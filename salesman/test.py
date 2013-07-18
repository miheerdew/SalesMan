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


from __future__ import unicode_literals
from StringIO import StringIO as BytesIO
import csv
import unittest
from collections import namedtuple
from datetime import date
from sqlalchemy import create_engine
from .lib.core import Core, TimeLineError, ItemNotAvailableError, TransactionTypeError
from .lib.models import Application
from .lib.utils import setter, FunctionDisabledError
from .lib.core import ADDITION, SALE, GIFT, TRANSFER, StatementRow
from .lib.schema import Base, Item, Transaction, Unit
from .lib.schema import ClearTable
from .lib.models import UserError
import sqlalchemy

BOOK = 'Books'
EBOOK = 'EBooks'
CD = 'CD/DVD'

class TestSchema(unittest.TestCase):
    def setUp(self):
        engine = sqlalchemy.create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        self.session = sqlalchemy.orm.sessionmaker(bind=engine)()

        self.b1 = Item(name='How stuff works', category='Book',
                        price=20, qty=10, description='Paperback')
        self.b2 = Item(name='Beethovens Symphony', category='CD/DVD',
                        price=40, qty=50)
        self.b3 = Item(name='Angels and Deamons', category='Ebook',
                        price=50,qty=20)

        self.session.add_all([self.b1,self.b2,self.b3])
        self.session.commit()

    def test_cascaded_deletion_of_transaction(self):
        t = Transaction(date=date(2011,1,1), info='To:ABC',
                        units=[ Unit(item_id=1, qty=3, type=ADDITION),
                                Unit(item_id=1, qty=4, type=SALE )
                                ])
        self.session.add(t)
        p=self.session.query(Transaction).get(1)
        assert t is p
        id=t.id
        id1 = p.units[0].id
        id2 = p.units[1].id
        self.assertNotEqual(id1,None)
        self.assertNotEqual(id2,None)
        self.session.delete(t)
        self.session.flush()
        self.assertEqual(self.session.query(Transaction).get(id), None)
        self.assertEqual(self.session.query(Unit).get(id1), None)
        self.assertEqual(self.session.query(Unit).get(id2), None)


class TestCore(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        self.core = Core(engine)

        l = [   ('Abc for kids', BOOK, 20, 30, 'For Kids'),
                ('Abc for kids', BOOK, 30, 20, 'For Smaller Kids'),
                ('abc in python', BOOK, 40, 10, 'For Developers'),
                ('abc in python', BOOK, 40, 10, 'For Developers'),
            ]

        items = [ Item(name=a,category=b,price=c,qty=d,description=e)
                    for a,b,c,d,e in l ]

        self.core.Initialize(items)

        for i,j in enumerate(self.core.QueryItems()):
            for k in ('id','name','category','price','qty','description'):
                self.assertEqual(getattr(items[i],k),getattr(j,k))

        self.assertEqual(self.core.QueryItems().count(),len(items))

    def test_batch_transaction(self):
        ids1= [self.core.AddTransaction(**i) for i in self.get_transaction_data()]
        state1 = self.get_state()
        self.core.Undo(1)
        ts = [Transaction(**i) for i in self.get_transaction_data()]
        ids2 = self.core.AddBatchTransactions(ts)
        state2 = self.get_state()

        self.assertEqual(state1, state2)
        self.assertEqual(ids1, ids2)

    def addSimpleTransaction(self, transaction):
        units = []
        for u in transaction[1]:
            item_id=None
            item=None
            discount=None if u[2] != SALE else u[3]

            if u[2] == ADDITION and isinstance(u[0],Item):
                item = u[0]
            else:
                item_id = u[0]

            units.append(Unit(item_id=item_id, item=item, qty=u[1],
                    type=u[2], discount=discount))

        return self.core.AddTransaction(date=transaction[0],units=units,
                                type=transaction[2])


    def test_statement_generation(self):
        transactions =(
            (
                date(2012,1,1),
                ((1,1,SALE,4),(2,2,GIFT),(3,3,TRANSFER),(4,4,ADDITION)),
                None
            ),
            (
                date(2012,1,2),
                (  (Item(name='Mathematical Circles',
                        price=120, category=BOOK),
                    2,
                    ADDITION),
                ),
                ADDITION
            ),
            (
                date(2012,1,3),
                ((5,1,SALE,10),(1,1,SALE,4)),
                SALE
            )
        )


        ids = [ self.addSimpleTransaction(t) for t in transactions]

        statement=self.core.GenerateStatement()
        expected = dict(opening=  [30,20,10,10, 0],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 4, 2],
                        sales=    [ 2, 0, 0, 0, 1],
                        discount= [ 8, 0, 0, 0,10],
                        gifts=    [ 0, 2, 0, 0, 0],
                        transfers=[ 0, 0, 3, 0, 0])

        self.check_for_statement(statement, expected)


        statement = self.core.GenerateStatement(ids[1],ids[2])
        expected = dict(opening=  [29,18, 7,14, 0],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 0, 2],
                        sales=    [ 1, 0, 0, 0, 1],
                        discount= [ 4, 0, 0, 0,10],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])

        self.check_for_statement(statement, expected)


        statement = self.core.GenerateStatement(ids[2],ids[2])
        expected = dict(opening=  [29,18, 7,14, 2],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 0, 0],
                        sales=    [ 1, 0, 0, 0, 1],
                        discount= [ 4, 0, 0, 0,10],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])


        statement = self.core.GenerateStatement(4,4)
        expected = dict(opening=  [28,18, 7,14, 1],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 0, 0],
                        sales=    [ 0, 0, 0, 0, 0],
                        discount= [ 0, 0, 0, 0, 0],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])

        self.check_for_statement(statement, expected)

        statement = self.core.GenerateStatement(5,5)
        expected = dict(opening=  [28,18, 7,14, 1],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 0, 0],
                        sales=    [ 0, 0, 0, 0, 0],
                        discount= [ 0, 0, 0, 0, 0],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])

        self.check_for_statement(statement, expected)


        statement = self.core.GenerateStatement(3,2)
        expected = dict(opening=  [29,18, 7,14, 2],
                        closing=  [29,18, 7,14, 2],
                        additions=[ 0, 0, 0, 0, 0],
                        sales=    [ 0, 0, 0, 0, 0],
                        discount= [ 0, 0, 0, 0, 0],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])
        self.check_for_statement(statement, expected)


    def check_for_statement(self, statement, expected):
        for k,v in statement.items():
            for a in v.attrs:
                self.assertEqual(getattr(v,a), expected[a][k-1])

    def test_different_kinds_of_units(self):
        units = [Unit(item_id=1,qty=1,type=SALE),
                 Unit(item_id=1,qty=1,type=GIFT),
                 Unit(item_id=1,qty=1,type=TRANSFER),
                 Unit(item_id=2,qty=1,type=ADDITION)
                ]
        self.core.AddTransaction(date=date(2013,1,1),units=units)
        self.assertEqual(self.core.QueryItems().get(1).qty,27)
        self.assertEqual(self.core.QueryItems().get(2).qty,21)

    def test_add_transaction_with_type(self):
        with self.assertRaises(TransactionTypeError):
            self.core.AddTransaction(type=ADDITION,
                date=date(2012,12,12),
                units=[Unit(item_id=1, qty=1,
                            type=ADDITION),
                        Unit(item_id=2, qty=1,
                                type=SALE)])

        self.assertEqual(30, self.core.QueryItems().get(1).qty)
        self.assertEqual(20, self.core.QueryItems().get(2).qty)

    def test_get_history(self):
        initial_state = self.get_item_state()
        id1 = self.core.AddTransaction( date=date(2013,1,1),
                info='Happy New Year',
                units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]
                    )
        mid_state1 = self.get_item_state()

        id2 = self.core.AddTransaction( date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)]
                            )
        mid_state2 = self.get_item_state()

        id3 = self.core.AddTransaction( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)]
                            )

        end_state = self.get_item_state()

        self.assertEqual(self.core.GetHistory(id3), mid_state2)

        self.assertEqual(self.core.GetHistory(id2), mid_state1)

        self.assertEqual(self.core.GetHistory(1), initial_state)

        self.assertEqual(self.core.GetHistory(0), self.get_item_state())

    def get_item_state(self):
        return { i.id:i.qty for i in self.core.QI() }

    def test_add_transaction_without_id(self):
        d = date(2012,12,12)
        info = "A test transaction"
        u = [
            Unit( qty=1, type=ADDITION,
                item=Item(name='Abc for kids',
                        category=BOOK, price=20) ),

            Unit(qty=1, type=ADDITION,
                item=Item(name='Abc for kids',
                        category=BOOK, price=120) )
                    ]

        t = self.core.AddTransaction(date=d, units=u)

        self.assertEqual( 31,
            self.core.QueryItems().get(1).qty)

        self.assertEqual( 1, self.core.QueryTransactions().get(t).units[1].item.qty)


    def test_add_transaction(self):
        d = date(2012,12,12)
        info = 'A test transaction'

        subtractions = [Unit(item_id=3,qty=10,discount=20,type=SALE)]
        additions = [
                    Unit(item_id=2,qty=5,type=ADDITION),
                    Unit(
                        qty=10,
                        item=Item(name='Learn English', category=BOOK,
                                price=30, qty=10, description='None'),
                        type=ADDITION
                    )
                    ]

        transaction_id = self.core.AddTransaction(date=d,
                            info='A test transaction',
                            units=(additions + subtractions))

        transaction = self.core.QueryTransactions().get(transaction_id)

        for a,b in (('id',transaction_id),('info',info),('date',d)):
            self.assertEqual(getattr(transaction,a),b)

        self.assertEqual(self.core.QueryItems().get(3).qty,0)
        self.assertEqual(self.core.QueryItems().get(2).qty,25)
        new_item = self.core.QueryItems().get(5)
        self.assertEqual(new_item.name, 'Learn English')


    def test_raises_Item_not_available_error(self):
        with self.assertRaises(ItemNotAvailableError):
            self.core.AddTransaction(date=date(2013,1,1),
            info='', units=[Unit(item_id=1,qty=40,type=SALE)])
        self.assertEqual(self.core.QueryItems().get(1).qty, 30)

    def test_raises_time_line_error(self):
        self.core.AddTransaction(date=date(2013,2,1), units=[])
        with self.assertRaises(TimeLineError):
            self.core.AddTransaction(date=date(2013,1,1),
                    units=[Unit(item_id=1,qty=5,type=SALE)])
        self.assertEqual(self.core.QueryItems().get(1).qty,30)

    def test_relative_reverts(self):
        initial_state = self.get_state()

        self.core.AddTransaction( date=date(2013,1,1),
                    info='Happy New Year',
                    units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]
                        )
        self.core.AddTransaction( date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20, type=ADDITION)]
                            )

        self.core.Undo(-2)

        self.assertEqual(initial_state, self.get_state())

    def test_positional_undo(self):
        initial_state = self.get_state()
        id1 = self.core.AddTransaction( date=date(2013,1,1),
                info='Happy New Year',
                units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]
                    )
        mid_state1 = self.get_state()

        id2 = self.core.AddTransaction( date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)]
                            )
        mid_state2 = self.get_state()

        id3 = self.core.AddTransaction( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)]
                            )

        end_state = self.get_state()

        self.core.Undo(id3)
        self.assertEqual(self.get_state(), mid_state2)

        self.core.Undo(id2)
        self.assertEqual(self.get_state(), mid_state1)

        self.core.Undo(0)
        self.assertEqual(self.get_state(), initial_state)

        self.core.Undo(0)
        self.assertEqual(self.get_state(), initial_state)

    def get_state(self):
        return ( self.core.QueryItems().all(),
                self.core.QueryTransactions().all() )

    def get_transaction_data(self):
        return [dict(date=date(2013,1,1),
                    info='Happy New Year',
                    units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]),
                dict(date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)]),
                dict( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)]
                    )
                ]



class TestApp(unittest.TestCase):

    def setUp(self):
        self.core = Application()
        self.core.OpenDatabase(':memory:')

        l = [   ('Abc for kids', BOOK, 20, 30, 'For Kids'),
                ('Abc for kids', BOOK, 30, 20, 'For Smaller Kids'),
                ('abc in python', BOOK, 40, 10, 'For Developers'),
                ('abc in python', BOOK, 40, 10, 'For Developers'),
            ]

        items = [ Item(name=a,category=b,price=c,qty=d,description=e)
                    for a,b,c,d,e in l ]

        fd = BytesIO()
        reader = csv.writer(fd)
        reader.writerow(['name','category','price','qty','description'])
        reader.writerows(l)
        fd.seek(0)

        self.core.InitDatabase(fd)

        for i,j in enumerate(self.core.QueryItems()):
            for k in ('name','category','price','qty','description'):
                self.assertEqual(getattr(items[i],k),getattr(j,k))

        self.assertEqual(self.core.QueryItems().count(),len(items))

    def test_initial_disables(self):
        app = Application()
        app.Initialize()
        for i in (('AddTransaction',''),('GenerateStatement',''),('GetCategories',),
                ('GetHistory',1),('InitDatabase',''), ('QueryItems',),
                ('QueryTransactions',),('Undo',1),('Redo',)):
            assert hasattr(app,i[0])
            assert callable(getattr(app,i[0]))
            with self.assertRaises(FunctionDisabledError):
                getattr(app,i[0])(*i[1:])


    def addSimpleTransaction(self, transaction):
        units = []
        for u in transaction[1]:
            item_id=None
            item=None
            discount=None if u[2] != SALE else u[3]

            if u[2] == ADDITION and isinstance(u[0],Item):
                item = u[0]
            else:
                item_id = u[0]

            units.append(Unit(item_id=item_id, item=item, qty=u[1],
                    type=u[2], discount=discount))

        return self.core.AddTransaction(date=transaction[0],units=units,
                                type=transaction[2])

    @unittest.skip('Need to be modified')
    def test_statement_generation(self):
        fd = BytesIO
        transactions =(
            (
                date(2012,1,1),
                ((1,1,SALE,4),(2,2,GIFT),(3,3,TRANSFER),(4,4,ADDITION)),
                None
            ),
            (
                date(2012,1,2),
                (  (Item(name='Mathematical Circles',
                        price=120, category=BOOK),
                    2,
                    ADDITION),
                ),
                ADDITION
            ),
            (
                date(2012,1,3),
                ((5,1,SALE,10),(1,1,SALE,4)),
                SALE
            )
        )


        ids = [ self.addSimpleTransaction(t) for t in transactions]

        statement=self.core.GenerateStatement()
        expected = dict(opening=  [30,20,10,10, 0],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 4, 2],
                        sales=    [ 2, 0, 0, 0, 1],
                        discount= [ 8, 0, 0, 0,10],
                        gifts=    [ 0, 2, 0, 0, 0],
                        transfers=[ 0, 0, 3, 0, 0])

        self.check_for_statement(statement, expected)


        statement = self.core.GenerateStatement(ids[1],ids[2])
        expected = dict(opening=  [29,18, 7,14, 0],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 0, 2],
                        sales=    [ 1, 0, 0, 0, 1],
                        discount= [ 4, 0, 0, 0,10],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])

        self.check_for_statement(statement, expected)


        statement = self.core.GenerateStatement(ids[2],ids[2])
        expected = dict(opening=  [29,18, 7,14, 2],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 0, 0],
                        sales=    [ 1, 0, 0, 0, 1],
                        discount= [ 4, 0, 0, 0,10],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])


        statement = self.core.GenerateStatement(4,4)
        expected = dict(opening=  [28,18, 7,14, 1],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 0, 0],
                        sales=    [ 0, 0, 0, 0, 0],
                        discount= [ 0, 0, 0, 0, 0],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])

        self.check_for_statement(statement, expected)

        statement = self.core.GenerateStatement(5,5)
        expected = dict(opening=  [28,18, 7,14, 1],
                        closing=  [28,18, 7,14, 1],
                        additions=[ 0, 0, 0, 0, 0],
                        sales=    [ 0, 0, 0, 0, 0],
                        discount= [ 0, 0, 0, 0, 0],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])

        self.check_for_statement(statement, expected)


        statement = self.core.GenerateStatement(3,2)
        expected = dict(opening=  [29,18, 7,14, 2],
                        closing=  [29,18, 7,14, 2],
                        additions=[ 0, 0, 0, 0, 0],
                        sales=    [ 0, 0, 0, 0, 0],
                        discount= [ 0, 0, 0, 0, 0],
                        gifts=    [ 0, 0, 0, 0, 0],
                        transfers=[ 0, 0, 0, 0, 0])
        self.check_for_statement(statement, expected)


    def check_for_statement(self, statement, expected):
        for k,v in statement.items():
            for a in v.attrs:
                self.assertEqual(getattr(v,a), expected[a][k-1])

    def test_different_kinds_of_units(self):
        units = [Unit(item_id=1,qty=1,type=SALE),
                 Unit(item_id=1,qty=1,type=GIFT),
                 Unit(item_id=1,qty=1,type=TRANSFER),
                 Unit(item_id=2,qty=1,type=ADDITION)
                ]
        self.core.AddTransaction(date=date(2013,1,1),units=units)
        self.assertEqual(self.core.QueryItems().get(1).qty,27)
        self.assertEqual(self.core.QueryItems().get(2).qty,21)

    def test_add_transaction_with_type(self):
        with self.assertRaises(TransactionTypeError):
            self.core.AddTransaction(type=ADDITION,
                date=date(2012,12,12),
                units=[Unit(item_id=1, qty=1,
                                    type=ADDITION),
                            Unit(item_id=2, qty=1,
                                    type=SALE)])

        self.assertEqual(30, self.core.QueryItems().get(1).qty)
        self.assertEqual(20, self.core.QueryItems().get(2).qty)

    def test_get_history(self):
        initial_state = self.get_item_state()
        id1 = self.core.AddTransaction( date=date(2013,1,1),
                info='Happy New Year',
                units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]
                    )
        mid_state1 = self.get_item_state()

        id2 = self.core.AddTransaction( date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)]
                            )
        mid_state2 = self.get_item_state()

        id3 = self.core.AddTransaction( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)]
                            )

        end_state = self.get_item_state()

        self.assertEqual(self.core.GetHistory(id3).all(), mid_state2)

        self.assertEqual(self.core.GetHistory(id2).all(), mid_state1)

        self.assertEqual(self.core.GetHistory(1).all(), initial_state)

        self.assertEqual(self.core.GetHistory(0).all(), self.get_item_state())

    def get_item_state(self):
        return self.get_state()[0]

    def test_add_transaction_without_id(self):
        d = date(2012,12,12)
        info = "A test transaction"
        u = [
            Unit( qty=1, type=ADDITION,
                item=Item(name='Abc for kids',
                        category=BOOK, price=20) ),

            Unit(qty=1, type=ADDITION,
                item=Item(name='Abc for kids',
                        category=BOOK, price=120) )
                    ]

        t = self.core.AddTransaction(date=d, units=u)

        self.assertEqual( 31,
            self.core.QueryItems().get(1).qty)

        self.assertEqual( 1, self.core.QueryTransactions().get(t).units[1].item.qty)


    def test_add_transaction(self):
        d = date(2012,12,12)
        info = 'A test transaction'

        subtractions = [Unit(item_id=3,qty=10,discount=20,type=SALE)]
        additions = [
                    Unit(item_id=2,qty=5,type=ADDITION),
                    Unit(
                        qty=10,
                        item=Item(name='Learn English', category=BOOK,
                                price=30, qty=10, description='None'),
                        type=ADDITION
                    )
                    ]

        transaction_id = self.core.AddTransaction(date=d,
                            info='A test transaction',
                            units=(additions + subtractions))

        transaction = self.core.QueryTransactions().get(transaction_id)

        for a,b in (('id',transaction_id),('info',info),('date',d)):
            self.assertEqual(getattr(transaction,a),b)

        self.assertEqual(self.core.QueryItems().get(3).qty,0)
        self.assertEqual(self.core.QueryItems().get(2).qty,25)
        new_item = self.core.QueryItems().get(5)
        self.assertEqual(new_item.name, 'Learn English')

    def test_raises_Item_not_available_error(self):
        with self.assertRaises(UserError):
            try:
                self.core.AddTransaction(date=date(2013,1,1),
                    info='', units=[Unit(item_id=1,qty=40,type=SALE)])
            except UserError as e:
                self.assertTrue(isinstance(e.exception, ItemNotAvailableError))
                raise
        self.assertEqual(self.core.QueryItems().get(1).qty, 30)

    def test_raises_time_line_error(self):
        self.core.AddTransaction(date=date(2013,2,1), units=[])
        with self.assertRaises(UserError):
            try:
                self.core.AddTransaction(date=date(2013,1,1),
                    units=[Unit(item_id=1,qty=5,type=SALE)])
            except UserError as e:
                self.assertTrue(isinstance(e.exception,TimeLineError))
                raise
        self.assertEqual(self.core.QueryItems().get(1).qty,30)

    def get_transaction_data(self):
        return [dict(date=date(2013,1,1),
                    info='Happy New Year',
                    units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]),
                dict(date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)]),
                dict( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)]
                    )
                ]


    def test_undo(self):
        initial_state = self.get_state()
        id1 = self.core.AddTransaction( date=date(2013,1,1),
                info='Happy New Year',
                units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]
                    )
        mid_state1 = self.get_state()

        id2 = self.core.AddTransaction(date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)]
                            )
        mid_state2 = self.get_state()

        id3 = self.core.AddTransaction( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)]
                            )

        end_state = self.get_state()

        self.core.Undo(id3)
        self.assertEqual(self.get_state(), mid_state2)

        self.core.Undo(id2)
        self.assertEqual(self.get_state(), mid_state1)

        self.core.Undo(0)
        self.assertEqual(self.get_state(), initial_state)

        self.core.Undo(0)
        self.assertEqual(self.get_state(), initial_state)

    def test_multiple_redo(self):
        ids, states = [], []
        for t in self.get_transaction_data():
            ids.append(self.core.AddTransaction(**t))
            states.append(self.get_state())

        for i in reversed(ids):
            self.core.Undo(i)

        for s in states:
            self.core.Redo()
            self.assertEqual(self.get_state(),s)

    def test_single_redo(self):
        for t in self.get_transaction_data():
            start1 = self.get_state()
            self.core.AddTransaction(**t)
            state2 = self.get_state()
            self.core.Undo(-1)
            self.assertEqual(start1, self.get_state())
            self.core.Redo()
            self.assertEqual(state2, self.get_state())

        state = self.get_state()
        self.core.Undo(1)
        self.core.Redo()
        self.assertEqual(self.get_state(),state)

    def get_transaction_data(self):
        return [dict(date=date(2013,1,1),
                    info='Happy New Year',
                    units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]),
                dict(date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)]),
                dict( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)]
                    )
                ]


    def get_state(self):
        return ( self.core.QueryItems().all(),
                self.core.QueryTransactions().all() )

class SetterDecoratorTester(unittest.TestCase):
    def test_basic_functionality(self):
        class A:
            @setter('a1','b1','c1')
            def func1(self, a1, b1, c1):
                return (self.a1, self.b1, self.c1)

            @setter('b2','c2')
            def func2(self, a2, b2=None, c2=None):
                return (self.b2, self.c2)

        self.assertSequenceEqual(A().func1(1,2,3),(1,2,3))
        self.assertSequenceEqual(A().func2(1,2),(2,None))



if __name__ == '__main__':
    unittest.main()
