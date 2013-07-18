#Copyright (C) 2013  Miheer Dewaskar <miheerdew@gmail.com>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>


"""This module provides the Application class, the model for
the application"""

import sys
import csv
import datetime
import copy
import threading
import sqlalchemy

from .core import Core, SALE, ADDITION, GIFT, TRANSFER
from .core import TimeLineError, ItemNotFoundError, ItemNotAvailableError
from .schema import Transaction, Item, Unit
from .utils import threadsafe, ToggleableMethods, run_if_enabled, pub
from .topics import *

DATE_FORMAT='%d/%m/%Y'

class UserError(Exception):
    """A class to catch User Exception
    """
    def __init__(self, message='', reason=None, exception=None):
        self.message = message
        self.reason = reason
        self.exception = exception

    def __str__(self):
        return "<UserError: msg={}, reason={}>"\
                .format(self.message, self.reason)

    def __repr__(self):
        return "<UserError:Exception:{!r}>".format(self.exception)

    def GetMessage(self):
        return self.message

class WrapItems:
    """A wrapper around session.query(Item) object.

    It implements a minimal api, of the query object. It has provision
    to provide different attributes via supplied dictionaries
    """
    def __init__(self, items, quantities={}, strict=False):
        """Create the wrapped query object.

        The :param quantities: dictionary is of the form {item_key:qty}.
        If :param strict: is true , then all items not in :param quantities:
        will not be included in the query object
        """
        if strict:
            self._items = items.filter(Item.id.in_(quantities))
        else:
            self._items = items
        self._qty = quantities

    def first(self):
        i = self._items.first()
        if i is not None:
            return self.modify(i)

    def all(self):
        return [self.modify(i) for i in self._items.all()]

    def get(self, i):
        return self.modify(self._items.get(i))

    def filter(self, *args, **kargs):
        return WrapItems(self._items.filter(*args, **kargs),
                          self._qty)

    def count(self):
        return self._items.count()

    def modify(self, item):
        item = copy.copy(item)
        if item is not None and item.id in self._qty:
            item.qty = self._qty[item.id]
        return item

    def __getitem__(self, index):
        return self.modify(self._items[index])

    def __iter__(self):
        for item in self._items:
            yield self.modify(item)

class Application(ToggleableMethods):
    methods_to_disable_on_startup = (INIT_DATABASE,
                                    UNDO,
                                    REDO,
                                    GENERATE_STATEMENT,
                                    GET_HISTORY,
                                    GET_CATEGORIES,
                                    ADD_TRANSACTION,
                                    QUERY_ITEMS,
                                    QUERY_TRANSACTIONS)
    methods_to_enable_on_open_database = (INIT_DATABASE,
                                    UNDO,
                                    GENERATE_STATEMENT,
                                    GET_HISTORY,
                                    GET_CATEGORIES,
                                    ADD_TRANSACTION,
                                    QUERY_ITEMS,
                                    QUERY_TRANSACTIONS)
    def __init__(self):
        ToggleableMethods.__init__(self)
        self.core = None
        self.engine = None
        self.dbfile = None
        self.undo_stack = []
        self.lock = threading.Lock()

    def GetDBFilePath(self):
        return self.dbfile

    def Initialize(self):
        self.batchDisable(self.methods_to_disable_on_startup)

    def closeEngine(self):
        self.engine.dispose()
        self.engine = None
        self.core = None

    def GetLock(self):
        return self.lock

    @run_if_enabled
    def GetCategories(self):
        return self.categories

    @run_if_enabled
    @threadsafe
    def OpenDatabase(self, dbfile):

        try:
            self.dbfile = dbfile
            if self.engine is not None:
                self.closeEngine()
            self.engine = sqlalchemy\
                        .create_engine('sqlite:///{}'.format(dbfile))
            self.core = Core(self.engine)
            self.categories = set(i.category for i in self.core.QI())
            self.batchDisable([])
            self.batchEnable(self.methods_to_enable_on_open_database)
            self.notifyChange()

        except sqlalchemy.exc.DBAPIError:
            e_type, e_value, e_trace = sys.exc_info()
            e_msg = ('Cannot open dbfile {} .').format(dbfile)
            raise UserError(e_msg, str(e_value), e_value), None, e_trace

    @run_if_enabled
    @threadsafe
    def InitDatabase(self, csvfile):
        try:
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
                reader = csv.DictReader(fd, dialect=dialect)

                permitted = {'name','qty','price','description','category'}
                if not (set(reader.fieldnames) == permitted):
                    e_msg = ('Cannot process file {} '.format(csvfile),
                    'The fieldnames should only be {} '.format(permitted))
                    raise UserError(*e_msg)

                for i,row in enumerate(reader):
                    line_num = i+2
                    try:
                        row['qty']=int(row['qty'])
                        row['price']=float(row['price'])
                    except ValueError:
                        e_msg = ('Cannot process file {} '.format(csvfile),
                            'Cannot convert string to numeric'
                            'value at line {}'.format(line_num))
                        raise UserError(*e_msg)

                    items.append(Item(**row))
            finally:
                if opened: fd.close()

            self.core.Initialize(items)
            self.notifyChange()
            self.batchDisable([])
            self.batchEnable([])

        except:
            e_type, e_value, e_trace = sys.exc_info()
            if e_type == IOError:
                e_msg = ('Cannot open the file {} to initialize database'\
                        .format(csvfile),
                        str(e_value))
            elif e_type in (ValueError,csv.Error):
                e_msg = ('Error while parsing file {}'.format(csvfile),
                        str(e_value))
            else:
                raise
            raise UserError(*e_msg, exception=e_value),None, e_trace

    @run_if_enabled
    def GetHistory(self, transaction=0):
        if isinstance(transaction,Transaction):
            id = transaction.id
        else:
            id = int(transaction)
        return WrapItems(self.core.QI(),self.core.GetHistory(id),strict=True)

    @run_if_enabled
    def GenerateStatement(self, statementFile, startDate, endDate):
        e_reason = None
        if not isinstance(startDate, datetime.date):
            e_reason = 'start date is Invalid'

        if not isinstance(endDate, datetime.date):
            e_reason = 'end date is Invalid'

        if e_reason is not None:
            raise UserError('Cannot generate statement',e_reason)

        if startDate > endDate:
            e_reason = ('Start date : {} is greater than End date : {}'
                        .format(startDate, endDate))
            raise UserError('Cannot generate statement',e_reason)

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

        opened = False
        if isinstance(statementFile,basestring):
            try:
                fd = open(statementFile,'wb')
                opened = True
            except IOError as e:
                raise UserError('Cannot write statement to file "{}"'
                                .format(statementFile),
                                str(e),e)
        else:
            fd = statementFile

        try:
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

        finally:
            if opened:
                fd.close()

    @run_if_enabled
    @threadsafe
    def Redo(self):
        last = self.undo_stack[-1]
        self.core.AddBatchTransactions(last)
        #Pop the last transaction if not errors are raised
        self.undo_stack.pop()
        if len(self.undo_stack) == 0:
            self.disable(REDO)
        self.notifyChange()

    def _copyTransaction(self, transaction):
        """Make a sufficiently deep copy of transaction so that it can
        be used even after deletion by the database"""
        new_units = []
        for unit in transaction.units:
            new_item = Item(**{a:getattr(unit.item,a)
                        for a in ('name','price','category')})
            new_unit = Unit(item=new_item, **{a:getattr(unit,a)
                        for a in ('qty','discount','type')})
            new_unit.item = new_item
            new_units.append(new_unit)

        return Transaction(units=new_units,**{a:getattr(transaction,a)
                    for a in ('date','info','type')})

    @run_if_enabled
    @threadsafe
    def Undo(self, transaction):
        if isinstance(transaction,Transaction):
            i = transaction.id
        else:
            i = int(transaction)
        i = self.core.getAbsoluteTransactionId(i)
        transactions_to_be_undone = [self._copyTransaction(t) for t in
                    self.core.QT().filter(Transaction.id >=i)]
        self.core.Undo(i)
        #Put it into the undo stack if no errors are raised
        self.undo_stack.append(transactions_to_be_undone)
        if not self.isEnabled(REDO):
            self.enable(REDO)
        self.notifyChange()

    @run_if_enabled
    @threadsafe
    def AddTransaction(self, date, units=[], info='', type=None):
        for u in units:
            if u.item_id is not None:
                if u.item is None:
                    u.item = self.core.QI().get(u.item_id)
        try:
            id = self.core.AddTransaction(date,units,info,type)
        except:
            e_type, e_val, e_trace = sys.exc_info()
            e_msg='Cannot register transaction'

            if e_type == ItemNotFoundError:
                e_reason = ('Item with (Name:{name},Category:{category}'
                            ',Price:{price}) was not found').\
                            format(**{a:getattr(e_val,a)
                                for a in ['name','category','price']})

            elif e_type == TimeLineError:
                e_reason = ('The last transaction is dated {}'
                    'while the current transaction has date {}.'
                    'The transactions must be entered in ascending order'
                    'of date').format(e_val.last_date, e_val.new_date)

            elif e_type == ItemNotAvailableError:
                item = self.core.QI().get(e_val.item_id)
                e_reason = ('The item (Name:{name},Category:{category}'
                ',Price:{price}) has only {available} items available'
                'but you have requested for {requested}')\
                        .format(available=e_val.available,
                                requested=e_val.requested,
                            **{a:getattr(item,a)
                                for a in ['name','category','price']})
            else:
                raise

            raise UserError(e_msg, e_reason, e_val)

        if type == ADDITION:
            self.categories |= set(u.item.category for u in units)
        self.notifyChange()
        return id

    @run_if_enabled
    def QueryItems(self):
        return WrapItems(self.core.QI())

    def QI(self):
        return self.QueryItems()

    @run_if_enabled
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
        pub.sendMessage(UNITS_CHANGED, units=self.units.values(), type=self.type)

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
        print item_sig
        if qty <= 0 and (item_sig in self.units):
            del self.units[item_sig]

        elif qty > 0:
            self.units[item_sig] = Unit(item=Item(name=name,
                                        category=category, price=price),
                            type=self.type, qty=qty, discount=discount)
        self.NotifyChanges()

    def MakeTransaction(self, date, info):
        id = self.backend.AddTransaction(date, self.units.values(), info, self.type)
        pub.sendMessage(TRANSACTION_ADDED, id=id)
        self.Reset()
