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

import threading

from collections import namedtuple
from sqlalchemy.orm import sessionmaker
from  sqlalchemy import and_

from .schema import Item, Transaction, ClearTable, Unit, Base
from .utils import setter, Record, threadsafe

EPSILON=0.1

ADDITION = 'additions'
SALE = 'sales'
OTHER_TYPES = ['gifts', 'transfers', 'library']
TYPES=[ADDITION, SALE] + OTHER_TYPES


def unit_total(unit):
    discount = 0
    if unit.type == SALE:
        discount = unit.discount

    return unit.item.price*unit.qty-discount


class ItemNotFoundError(Exception):
    @setter('name','price','category')
    def __init__(self, name, price, category):
        """Raised when item is not availabe in sufficent qty"""

    def __str__(self):
        return "Name:{}, Price:{}, Category:{}".format(self.name,self.price,self.category)

class TransactionTypeError(Exception):
    pass
class ItemNotAvailableError(Exception):
    @setter('item_id','available','requested')
    def __init__(self, item_id, available, requested):
        """Raised when item is not availabe in sufficent qty"""

class TimeLineError(Exception):
    @setter('last_date','new_date')
    def __init__(self, last_date, new_date):
        """Raised when the dat for the last transaction is greater than
        the requested transaction"""

#Decorator for wrapping session
def wrap_session(orig_method):
    def new_method(self, *args, **kargs):
        try:
            rt_val = orig_method(self, *args, **kargs)
        except:
            self.session.rollback()
            raise
        else:
            self.session.commit()
            return rt_val
    return new_method

class Core:
    def __init__(self, engine):
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()
        self.lock = threading.Lock()

    def GetLock(self):
        return self.lock

    @threadsafe
    @wrap_session
    def Initialize(self, items):
        """(Re) Initialize the database with items.
        The transaction will be washed off"""
        ClearTable(Item, self.session)
        ClearTable(Transaction, self.session)
        self.session.add_all(items)

    def GetHistory(self, transaction_id):
        return self.getHistory(transaction_id, true_history=True)

    def getHistory(self, transaction_id, true_history=False):
        """Returns the items of the system just before
        `transaction_id` was registered.

        Returns {id:qty}
        if transaction_id ==0 then , transaction_id=infinity
        
        if true_history is True then those Items that where first
        added after transaction_id are not shown.
        """

        transaction_id = self.getAbsoluteTransactionId(transaction_id)
        if transaction_id == 0:
            last_row = self.getLastRow(Transaction)
            if last_row is not None:
                transaction_id = last_row.id + 1

        quantities = {}
        for i in self.QI():
            quantities[i.id] = i.qty

        for t in self.descendTransactions(transaction_id):
            for u in t.units:
                if u.type == ADDITION:
                    quantities[u.item_id] -= u.qty
                    assert quantities[u.item_id] >= 0, repr(quantities[u.item_id])
                else:
                    quantities[u.item_id] += u.qty

                if u.item_first_seen and true_history:
                    del quantities[u.item_id]
        return quantities

    @threadsafe
    def GenerateStatement(self, start=1, end=-1, relative=False):
        """Returns a dictionary with item_ids as keys and dict as values.
        Each value dict has the following keys
        (opening,closing,discount,additions,sales,*OTHER_TYPES).
        
        If relative is True then the entries in the statement corresponding
        to those items that are not invoved in any transactions are absent.
        """
        
        start = self.getAbsoluteTransactionId(start)
        end = self.getAbsoluteTransactionId(end)

        statement = {}

        for item_id, qty in self.getHistory(start).items():
            statement[item_id] = dict(opening=qty,
                closing=qty, discount=0, additions=0, sales=0,
                **{t:0 for t in OTHER_TYPES})

        for t in self.QT().\
          filter(and_(Transaction.id >= start, Transaction.id <= end)).\
          order_by(Transaction.id):

            for u in t.units:
                row = statement[u.item_id]

                #The keys have been named appropriately for this
                row[u.type] = row[u.type] + u.qty

                if u.type == ADDITION:
                    row['closing'] += u.qty
                else:
                    row['closing'] -= u.qty

                if u.type == SALE:
                    row['discount'] += u.discount
        
        if relative:
            #Remove the items for which there are no transactions
            for item in statement.keys():
                if not [1 for k in TYPES if statement[item][k] != 0]:
                   del statement[item]
                    
        return statement


    def getItemByProperties(self, item):
        """Get an item resembing the properies
        of item that is required for equality"""
        for i in self.QI().filter(and_(Item.name == item.name,
                                Item.category == item.category)):
            if abs(i.price - item.price) <= EPSILON:
                return i

    @threadsafe
    @wrap_session
    def EditItem(self, item):
        """Edit the non-qty attributes of the item"""
        i = self.QI().get(item.id)
        for a in ('name', 'category','price','description'):
            setattr(i, a, getattr(item, a))

    @threadsafe
    @wrap_session
    def EditQty(self, item_id, qty):
        i = self.QI().get(item_id)
        i.qty = qty

    @threadsafe
    @wrap_session
    def AddBatchTransactions(self, transactions):
        return [self._addTransaction(
                *[getattr(t,a) for a in ('date','units','info','type')]
                                    )
                for t in transactions]


    @threadsafe
    @wrap_session
    def AddTransaction(self, date, units , info='', type=None):
        return self._addTransaction(date, units, info, type)

    def _addTransaction(self, date, units, info, type):
        #Check if date is greater than that of last transaction
        last_transaction = self.getLastRow(Transaction)
        if last_transaction and (last_transaction.date > date):
            raise TimeLineError(last_transaction.date, date)


        t = Transaction(date=date,info=info, type=type)

        #Prepare units so that each unit has item_id set
        for u in units:

            #Also check if types agree (if any)
            if type and type != u.type:
                raise TransactionTypeError

            assert isinstance(u,Unit), type(u)

            new_item_created = False
            if u.item_id is None:
                #In case of Addition add new Item
                assert isinstance(u.item,Item), type(u.item)
                if u.item.id is None:
                    i =  self.getItemByProperties(u.item)
                    if i is None:
                        if u.type == ADDITION:
                            u.item.qty = 0
                            self.session.add(u.item)
                            self.session.flush() #to get item.id
                            u.item_id = u.item.id
                            new_item_created = True
                        else:
                            raise ItemNotFoundError(u.item.name,
                                        u.item.price, u.item.category)

                    else:
                        u.item_id = i.id
                        u.item = i

            u.item_id = self.getAbsoluteItemId(u.item_id)
            u.item_first_seen = new_item_created

        t.units = units
        self.doTransaction(t)# Do the actual math

        self.session.add(t) #Add to transaction table
        self.session.flush() # to get the transaction id

        return t.id

    def getLastRow(self,Table):
        return self.session.query(Table).order_by(Table.id.desc()).first()

    def doTransaction(self, transaction):
        """Actually perform the addition/subtraction
        in the transaction, assuming that all the units
        have their item_id set properly
        """
        for u in transaction.units:
            assert isinstance(u.item_id, int)
            item = self.QI().get(u.item_id)
            if u.type == ADDITION:
                item.qty += u.qty
            else:
                if item.qty < u.qty:
                  raise ItemNotAvailableError(item.id, item.qty, u.qty)
                item.qty -= u.qty

    def undoTransaction(self, transaction):
        """Actually perform the work of undoing
        transaction, this does not delete the transaction,
        but does delete any items that were generated by the transaction
        """
        for u in reversed(transaction.units):
                if u.type == ADDITION:
                    u.item.qty -= u.qty
                    assert u.item.qty >= 0
                else:
                    u.item.qty += u.qty

                if u.item_first_seen:
                    assert u.item.qty == 0
                    self.session.delete(u.item)

    def getAbsoluteItemId(self, id):
        assert isinstance(id, int), type(id)
        if id < 0:
            assert self.QI().count() is not None
            if self.QI().count() <= -id:
                id = 0
            else:
                id = self.QI().order_by(Item.id)[id].id
        assert id >= 0, str(id)
        return id

    def getAbsoluteTransactionId(self, id):
        """Get the absolute transaction id,
        if id < 0 then resove it as python does
        """
        assert isinstance(id, int), type(id)
        if id < 0:
            assert self.QT().count() is not None
            if self.QT().count() <= -id:
                id = 0
            else:
                id = self.QT().order_by(Transaction.id)[id].id
        assert id >= 0, str(id)
        return id

    def descendTransactions(self, transaction_id):
        """Enumerates transaction in descending order starting
        from the last transaction till the transaction with id
        equal to transaction id"""
        return self.QT().filter(Transaction.id >= transaction_id).\
                            order_by(Transaction.id.desc())

    @threadsafe
    @wrap_session
    def Undo(self,transaction_id):
        """Undo everything after (and including)
        the transaction with transaction_id: id. Here
        negetive id is used for access from back. A transaction_id of zero,
        will definitely clear all the transactions"""

        transaction_id = self.getAbsoluteTransactionId(transaction_id)
        for t in self.descendTransactions(transaction_id):

                self.undoTransaction(t) #Do the actual math
                self.session.delete(t)

    def QI(self):
        return self.QueryItems()

    def QT(self):
        return self.QueryTransactions()

    def QueryItems(self):
        return self.session.query(Item)

    def QueryTransactions(self):
        return self.session.query(Transaction)

