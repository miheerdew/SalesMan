import threading

from schema import *
from core import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wx.lib.pubsub import Publisher as pub
#from collection import defaultdict

ITEMS='ITEMS'
TRANSACTIONS='TRANSACTIONS'
UNITS='UNITS'

def nowait(func):
    def f(*args,**kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
    return f


class Backend:
    def __init__(self):
        self.lock = threading.Lock()
        self.ivm = ItemViewerModel(self)
        self.tvm = TransactionViewerModel(self)

    def SetListeners(self, ivm, tvm):
        self.ivm = ivm
        self.tvm = tvm

    def Update(self):
        self.ivm.Update()
        self.tvm.Update()

    #@nowait
    def OpenDatabase(self, dbfile):
        with self.lock:
            engine  = create_engine('sqlite://%s'%dbfile)
            Base.metadata.create_all(bind=engine)
            self.core = Core(engine=engine)
            self.Update()

    #@nowait
    def Initialize(self, items):
        with self.lock:
            self.core.Initialize(items)
            self.Update()

    #@nowait
    def AddTransaction(self,**kargs):
        with self.lock:
            self.core.AddTransaction(self,**kargs)
            self.Update()

    #@nowait
    def RevertTo(self,id)
        with self.lock:
            self.core.RevertTo(id)
            self.Update()

    def QueryItems(self):
        return self.core.QueryItems()

    def QueryTransactions(self):
        return self.core.QueryTransactions()

class ItemViewerModel:

    def __init__(self, backend):
        self.backend = backend
        self.query = ''

    def Update(self):
        pub.sendMessage(ITEMS, self.backend.QueryItems().\
                filter(Item.name.like('%{}%'.format(self.query)))
                )

    def Query(self, query):
        self.query = query
        self.Update()

class TransactionViewerModel:

    def __init__(self, backend):
        self.backend = backend

    def Update(self):
        pub.sendMessage(TRANSACTIONS, self.backend.QueryTransactions())

    def RevertTo(self, transaction):
        self.backend.RevertTo(transaction.id)

    def Undo(self)
        self.backend.RevertTo(-1)

class TransactionMakerModel:
    def __init__(self, backend):
        self.backend = backend

    def Initialize(self, type):
        assert type in [ADDITION, SALE, GIFT, TRANSFER]
        self.type = type
        self.id = self.backend.QueryTransactions().\
                order_by(Transaction.id.rev()).first() + 1
        self.units = {}
        self.commited = False
        self.Update()

    def Update(self):
        pub.sendMessage(UNITS,(self.id, self.type, self.units.values())

    def AddItem(self, item, qty, discount=0):
        assert isinstance(item, Item)
        if self.type != ADDITION:
            assert isinstance(item.id,int)

        if self.type != SALE:
            assert discount == 0

        discount = (discount*item.price/100)

        if item in self.units:
            discount += self.units[item].discount
            qty += self.units[item].qty

        self.items[item] = Unit(item=item, type=self.type, qty=qty,
                                    discount=discount)

        self.Update()

    def Commit(self, date, info):
        if not self.commited:
                #TODO Check for exceptions in the next thread
                try:
                    self.backend.AddTransaction(date=date, info=info,
                                            units=self.units.values())
                else:
                    self.commited = True
