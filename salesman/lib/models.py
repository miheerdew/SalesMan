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

from .core import Core, SALE, ADDITION
from .core import TimeLineError, ItemNotFoundError, ItemNotAvailableError
from .schema import Transaction, Item, Unit
from .utils import threadsafe, ToggleableMethods, run_if_enabled, pub
from .topics import *

DATE_FORMAT='%d/%m/%Y'


class UserError(Exception):
    """A class to catch User Exception
    """
    def __init__(self, message='', reason='', exception=None):
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

class WrapQuery(object):
    """A wrapper around session.query(TableMapper) object.

    It implements a minimal api, of the query object.
    """
    def __init__(self, query):
        """Create the wrapped query object."""
        self._query = query

    def first(self):
        i = self._query.first()
        if i is not None:
            return self.modify(i)

    def all(self):
        return [self.modify(i) for i in self._query.all()]

    def get(self, i):
        return self.modify(self._query.get(i))

    def filter(self, *args, **kargs):
        return self.wrap(self._query.filter(*args, **kargs))

    def order_by(self, *args, **kargs):
        return self.wrap(self._query.order_by(*args, **kargs))

    def count(self):
        return self._query.count()

    def __getitem__(self, index):
        return self.modify(self._query[index])

    def __iter__(self):
        for entry in self._query:
            yield self.modify(entry)

    #Methods that can be overwridden
    def wrap(self, query):
        """Return a wrapped object from query"""
        return type(self)(query)

    def modify(self, entry):
        """A modification hook, which can decide what to return when
        entry should be returned."""
        raise entry

def copyTransaction(transaction):
        """Make a copy of transaction"""
        new_units = []
        for unit in transaction.units:
            new_item = Item(**{a:getattr(unit.item,a)
                        for a in ('id','name','price','category','qty')})
            new_unit = Unit(item=new_item, **{a:getattr(unit,a)
                        for a in ('qty','discount','type')})
            new_unit.item = new_item
            new_units.append(new_unit)

        return Transaction(units=new_units,**{a:getattr(transaction,a)
                    for a in ('id','date','info','type')})

class WrapTransactions(WrapQuery):
    """A custom wrapper around session.query(Transaction) object.
    """
    def modify(self, transaction):
        return copyTransaction(transaction)


class WrapItems(WrapQuery):
    """A custom wrapper around session.query(Item) object.
    """
    def __init__(self, items, quantities={}, strict=False):
        if strict:
            items = items.filter(Item.id.in_(quantities))
        self._qty = quantities
        super(WrapItems,self).__init__(items)

    def wrap(self, items):
        return WrapItems(items, self._qty)

    def modify(self, item):
        if item is None: return None
        item = Item(**{a:getattr(item,a) for a in ('id','qty','name','category','price','description')})
        if item.id in self._qty:
            item.qty = self._qty[item.id]
        return item

class Application(ToggleableMethods):
    methods_to_disable_on_startup = (INIT_DATABASE,
                                    UNDO,
                                    REDO,
                                    GENERATE_STATEMENT,
                                    GENERATE_REGISTRY,
                                    GET_HISTORY,
                                    GET_CATEGORIES,
                                    ADD_TRANSACTION,
                                    QUERY_ITEMS,
                                    QUERY_TRANSACTIONS,
                                    EDIT_ITEM,
                                    EDIT_QTY)
    def __init__(self):
        ToggleableMethods.__init__(self)
        self.core = None
        self.engine = None
        self.dbfile = None
        self.undo_stack = []
        self.edit_locked = True
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

    def _getMethodsToEnableOnOpenDatabase(self):
        l = [UNDO,
        GENERATE_STATEMENT,
        GENERATE_REGISTRY,
        GET_HISTORY,
        GET_CATEGORIES,
        ADD_TRANSACTION,
        QUERY_ITEMS,
        QUERY_TRANSACTIONS,
        ]

        if self.core.QT().count() == 0:
            l.append(INIT_DATABASE)
        if self.canEditItem():
            l.append(EDIT_ITEM)
        if self.canEditQty():
            l.append(EDIT_QTY)

        return l

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
            self.batchEnable(self._getMethodsToEnableOnOpenDatabase())
            self.notifyChange()

        except sqlalchemy.exc.DBAPIError:
            e_type, e_value, e_trace = sys.exc_info()
            e_msg = ('Cannot open dbfile {} .').format(dbfile)
            raise UserError(e_msg, str(e_value), e_value), None, e_trace

    @run_if_enabled
    @threadsafe
    def InitDatabase(self, initFile, parser):
        """Is enabled only when the trasaction count is zero."""
        try:
            items = []
            opened = False
            fileName = None
            if isinstance(initFile, basestring):
                fd = open(initFile, 'rb')
                fileName = initFile
                opened = True
            else:
                fd = initFile
            try:
                items=list(parser(fd))
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
    def GenerateRegistry(self,  startDate, endDate, changes_only=False):
        e_reason = None
        if not isinstance(startDate, datetime.date):
            e_reason = 'start date is Invalid'

        if not isinstance(endDate, datetime.date):
            e_reason = 'end date is Invalid'

        if e_reason is not None:
            raise UserError('Cannot generate registry',e_reason)

        if startDate > endDate:
            e_reason = ('Start date : {} is greater than End date : {}'
                        .format(startDate, endDate))
            raise UserError('Cannot generate registry',e_reason)

        first_transaction = self.core.QT().\
                            filter(Transaction.date >= startDate).\
                            order_by(Transaction.id).first()
        last_transaction =  self.core.QT().\
                            filter(Transaction.date <= endDate).\
                            order_by(Transaction.id.desc()).first()

        end = last_transaction.id if last_transaction else 0
        start = first_transaction.id if first_transaction else end+1

        return self.core.GenerateRegistry(start, end, relative=changes_only)


    @run_if_enabled
    def GenerateStatement(self,  startDate, endDate, changes_only=False):
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

        return self.core.GenerateStatement(start, end, relative=changes_only)


    @run_if_enabled
    @threadsafe
    def Redo(self):
        """
        Undo just pops the transactions in a stack. Redo just adds back the
        transactions in the last element of the stack.

        Undo-Redo can be used to insert a transaction at an old point.
        Just Undo the transaction you want to insert before. Add a new transaction,
        then just Redo.
        """
        last = self.undo_stack[-1]
        self.core.AddBatchTransactions(last)
        #Pop the last transaction if no errors are raised
        self.undo_stack.pop()
        if len(self.undo_stack) == 0:
            self.disable(REDO)
            if self.canEditItem():
                self.enable(EDIT_ITEM)
        if last:
            self.batchDisable([INIT_DATABASE, EDIT_QTY])
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
    def Undo(self, transaction, permanent=False):
        """
        Undo pops all the transactions after (including) transaction from the
        transaction stack.

        If permanent is False, it copies the undone transaction into
        a undo_stack. Redo can be then be used to add the last batch undone
        (with permanent=False) back.

        Undo-Redo can be used to insert and delete transactions at arbitrary
        points.
        """

        if isinstance(transaction,Transaction):
            i = transaction.id
        else:
            i = int(transaction)
        i = self.core.getAbsoluteTransactionId(i)
        transactions_to_be_undone = [self._copyTransaction(t) for t in
                    self.core.QT().filter(Transaction.id >=i)]
        self.core.Undo(i)
        if permanent is False:
            #Put it into the undo stack if no errors are raised
            self.undo_stack.append(transactions_to_be_undone)
            if not self.isEnabled(REDO):
                self.enable(REDO)
            #TODO: The test for edit_item fails when kept inside the if
            self.disable(EDIT_ITEM)

        if self.core.QT().count() == 0:
            self.batchEnable([INIT_DATABASE])
        if self.canEditQty():
           self.enable(EDIT_QTY)
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
        self.batchDisable([INIT_DATABASE, EDIT_QTY])
        self.notifyChange()
        return id

    #TODO: Edit self.categories on Edit. Make self.categories into a multiset?
    #      When item is removed, the corresponding category must also be removed
    @run_if_enabled
    @threadsafe
    def EditItem(self, item):
        if self.core.QI().get(item.id) is None:
            raise UserError('Invalid Item with item id {}'.format(item.id))
        self.core.EditItem(item)
        self.notifyItemChange()

    def canEditItem(self):
        return self.core and len(self.undo_stack) == 0 and (not self.edit_locked)
        
    @run_if_enabled
    @threadsafe
    def EditQty(self, item_id, qty):
        self.core.EditQty(item_id, qty)

    def canEditQty(self):
        return self.core and self.core.QT().count() == 0 and (not self.edit_locked)

    @threadsafe
    def LockEdit(self, locked=True):
        self.edit_locked = locked
        if locked:
            self.batchDisable([EDIT_QTY,EDIT_ITEM])
        else:
            if self.canEditQty():
                self.enable(EDIT_QTY)
            if self.canEditItem():
                self.enable(EDIT_ITEM)

    @run_if_enabled
    def QueryItems(self):
        return WrapItems(self.core.QI())

    def QI(self):
        return self.QueryItems()

    @run_if_enabled
    def QueryTransactions(self):
        return WrapTransactions(self.core.QueryTransactions())

    def notifyChange(self):
        self.notifyItemChange()
        self.notifyTransactionChange()

    def notifyTransactionChange(self):
        pub.sendMessage(TRANSACTION_CHANGED, transactions=self.core.QT())

    def notifyItemChange(self):
        pub.sendMessage(ITEM_CHANGED, items=WrapItems(self.core.QI()))


class TransactionMaker(ToggleableMethods):
    def __init__(self, backend):
        ToggleableMethods.__init__(self)
        self.backend = backend
        self.type = SALE
        self.units = {}
        self.NotifyChanges()
        self.disable(MAKE_TRANSACTION)

    def NotifyChanges(self):
        pub.sendMessage(UNITS_CHANGED, units=self.units.values(), type=self.type)

    def Reset(self):
        self.units = {}
        self.disable(MAKE_TRANSACTION)
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
            if not self.units:
                self.disable(MAKE_TRANSACTION)

        elif qty > 0:
            self.units[item_sig] = Unit(item=Item(name=name,
                                        category=category, price=price),
                            type=self.type, qty=qty, discount=discount)
            self.enable(MAKE_TRANSACTION)

        self.NotifyChanges()

    @run_if_enabled
    def MakeTransaction(self, date, info):
        id = self.backend.AddTransaction(date, self.units.values(), info, self.type)
        pub.sendMessage(TRANSACTION_ADDED, id=id)
        self.Reset()
