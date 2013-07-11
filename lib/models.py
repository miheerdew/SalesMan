import csv
import datetime
from copy import copy
from threading import Lock
from sqlalchemy import create_engine
from .core import Core, SALE, ADDITION, GIFT, TRANSFER
from .schema import Transaction, Item, Unit
from .utils import threadsafe, ToggleableMethods, run_if_enabled, pub
from .topics import *

DATE_FORMAT='%d/%m/%Y'

class WrapItems:
    def __init__(self, items, changes={}, strict=False):
        if strict:
            self.items = items.filter(Item.id.in_(changes))
        else:
            self.items = items
        self.changes = changes

    def first(self):
        i = self.items.first()
        if i is not None:
            return self.modify(i)

    def all(self):
        return [self.modify(i) for i in self.items.all()]

    def get(self, i):
        return self.modify(self.items.get(i))

    def filter(self, *args, **kargs):
        return WrapItems(self.items.filter(*args, **kargs),self.changes)

    def count(self):
        return self.items.count()

    def modify(self, item):
        item = copy(item)
        if item is not None and item.id in self.changes:
            item.qty = self.changes[item.id]
        return item

    def __getitem__(self, index):
        return self.modify(self.items[index])

    def __iter__(self):
        for item in self.items:
            yield self.modify(item)

class Application(ToggleableMethods):
    def __init__(self):
        ToggleableMethods.__init__(self)
        self.core = None
        self.engine = None
        self.lock = Lock()

    def Initialize(self):
        self.batchDisable([INIT_DATABASE,UNDO,GENERATE_STATEMENT,QUERY_ITEMS,GET_HISTORY,GET_CATEGORY,ADD_TRANSACTION])

    def closeEngine(self):
        self.engine.dispose()
        self.engine = None
        self.core = None

    @run_if_enabled
    def GetCategories(self):
        return self.categories

    @run_if_enabled
    @threadsafe
    def OpenDatabase(self, dbfile):
        if self.engine is not None:
            self.closeEngine()

        self.engine = create_engine('sqlite:///{}'.format(dbfile))
        self.core = Core(self.engine)
        self.categories = set(i.category for i in self.core.QI())
        self.batchDisable([])
        self.batchEnable([INIT_DATABASE, UNDO,GENERATE_STATEMENT,GET_HISTORY, QUERY_ITEMS, GET_CATEGORY, ADD_TRANSACTION])
        self.notifyChange()

    @run_if_enabled
    @threadsafe
    def InitDatabase(self, csvfile):
        items = []
        opened = False
        if isinstance(csvfile, basestring):
            fd = open(csvfile, 'rb')
            opened = True
        else:
            fd = csvfile

        try:
            dialect = csv.Sniffer().sniff(fd.read(1024))
            fd.seek(0)
            for row in csv.DictReader(fd, dialect=dialect):
                row['qty']=int(row['qty'])
                row['price']=float(row['price'])
                items.append(Item(**row))
        finally:
            if opened: fd.close()

        self.core.Initialize(items)
        self.notifyChange()
        self.batchDisable([])
        self.batchEnable([])

    @run_if_enabled
    def GetHistory(self, transaction=0):
        if isinstance(transaction,Transaction):
            id = transaction.id
        else:
            id = int(transaction)
        return WrapItems(self.core.QI(),self.core.GetHistory(id),strict=True)

    @run_if_enabled
    def GenerateStatement(self, filepath, startDate, endDate):
        assert startDate >= endDate
        first_transaction = self.core.QT().\
                            filter(Transaction.date >= startDate).\
                            order_by(Transaction.id).first()
        last_transaction =  self.core.QT().\
                            filter(Transaction.date <= endDate).\
                            order_by(Transaction.id.desc()).first()

        end = last_transaction.id if last_transaction else 0
        start = first_transaction.id if first_transaction else end+1

        statement = self.core.GenerateStatement(start, end)

        header1 = ['Statement : {1:{0}} - {2:{0}}'.\
                    format(DATE_FORMAT, startDate, endDate),None,None,None,
                    'Opening',None,
                    'Closing',None,
                    'Additions',None,
                    'Sales',None,None,
                    'Transfers',None,
                    'Gifts',None]

        header2 = [ 'Sr.No','Name','Category','Price',      #Item info
                    'Qty','Total',                          #Opening
                    'Qty','Total',                          #Closing
                    'Qty','Total',                          #Additions
                    'Qty','Discount','Total',               #Sales
                    'Qty','Total',                          #Transfers
                    'Qty','Total'                           #Gifts
                ]

        summable_entries = [ None, None, None, None,   #Item info
                            None, 0,                    #Opening
                            None, 0,                    #Closing
                            None, 0,                    #Additions
                            None, 0, 0,                 #Sales
                            None, 0,                    #Transfers
                            None, 0                     #Gifts
                        ]

        last_row = ['Total',None, None, None,          #Item info
                    '', 0,                              #Opening
                    '', 0,                              #Closing
                    '', 0,                              #Additions
                    '', 0, 0,                           #Sales
                    '', 0,                              #Transfers
                    '', 0                               #Gifts
                ]
        with open(filepath, 'wb') as fd:
            writer = csv.writer(fd, delimiter=',',
                    quotechar="'", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header1)
            writer.writerow(header2)

            for i,item in enumerate(self.core.QI().order_by(Item.category)):
                r = statement[item.id]
                p = item.price

                row = [ i, item.name, item.category, p ,    #Item info
                r.opening, r.opening*p,                     #Opening
                r.closing, r.closing*p,                     #Closing
                r.additions, r.additions*p,                 #Additions
                r.sales, r.discount, r.sales*p - r.discount,#Sales
                r.transfers, r.transfers*p,                 #Transfers
                r.gifts, r.gifts*p                          #Gifts
                ]

                writer.writerow(row)

                for i in range(len(summable_entries)):
                    if summable_entries[i] is not None:
                        summable_entries[i] += row[i]

            for i in range(len(last_row)):
                if last_row[i] == 0:
                    last_row[i] = summable_entries[i]
                    assert last_row[i] is not None
            writer.writerow(last_row)


    @run_if_enabled
    @threadsafe
    def Undo(self, transaction):
        if isinstance(transaction,Transaction):
            i = transaction.id
        else:
            i = int(transaction)
        self.core.Undo(i)
        self.notifyChange()

    @run_if_enabled
    @threadsafe
    def AddTransaction(self, date, units=[], info='', type=None):
        for u in units:
            if u.item_id is not None:
                u.item = self.core.QI().get(u.item_id)

        if type == ADDITION:
            self.categories |= set(u.item.category for u in units)
        id = self.core.AddTransaction(date,units,info,type)
        self.notifyChange()
        return id

    @run_if_enabled
    def QueryItems(self):
        return WrapItems(self.core.QI())

    def QI(self):
        return self.QueryItems()

    def QueryTransactions(self):
        return self.core.QueryTransactions()

    def notifyChange(self):
        self.notifyItemChange()
        self.notifyTransactionChange()

    def notifyTransactionChange(self):
        pub.sendMessage(TRANSACTION_CHANGED, transactions=self.core.QT())

    def notifyItemChange(self):
        pub.sendMessage(ITEM_CHANGED, items=WrapItems(self.core.QI()))

class TransactionMaker:
    def __init__(self, backend):
        self.backend = backend
        self.type = SALE
        self.units = {}
        self.NotifyChanges()

    def NotifyChanges(self):
        pub.sendMessage((TRANSACTION_MAKER,UNITS_CHANGED), units=self.units.values(), type=self.type)

    def Reset(self):
        self.units = {}
        self.NotifyChanges()

    def ChangeType(self, type):
        self.type = type
        for i in self.units.keys():
            self.units[i].type=type
        self.NotifyChanges()

    def AddItem(self, name, category, price, qty=0, discount=0):
        item_sig = (name,category,price)
        if qty <= 0 and (item_sig in self.units):
            del self.units[item_sig]

        elif qty > 0:
            self.units[item_sig] = Unit(item=Item(name=name,
                                        category=category, price=price),
                            type=self.type, qty=qty, discount=discount)
        self.NotifyChanges()

    def MakeTransaction(self, date, info):
        self.backend.AddTransaction(date, self.units.values(), info, self.type)
        self.Reset()
