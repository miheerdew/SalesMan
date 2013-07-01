from __future__ import unicode_literals
from __future__ import print_function

import unittest
from datetime import date
from sqlalchemy import create_engine

import core
from core import ADDITION, SALE, GIFT, TRANSFER
from schema import Base, Item, Transaction, Unit
from schema import ClearTable
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
        self.core = core.Core(engine)

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

    def test_different_kinds_of_units(self):
        units = [Unit(item_id=1,qty=1,type=SALE),
                 Unit(item_id=1,qty=1,type=GIFT),
                 Unit(item_id=1,qty=1,type=TRANSFER),
                 Unit(item_id=2,qty=1,type=ADDITION)
                ]
        self.core.AddTransaction(date=date(2013,1,1),units=units)
        self.assertEqual(self.core.QueryItems().get(1).qty,27)
        self.assertEqual(self.core.QueryItems().get(2).qty,21)
        self.core.RevertTo(-1)

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

        self.core.RevertTo(-1)

    def test_raises_Item_not_available_error(self):
        with self.assertRaises(core.ItemNotAvailableError):
            self.core.AddTransaction(date=date(2013,1,1),
            info='', units=[Unit(item_id=1,qty=40,type=SALE)])
        self.assertEqual(self.core.QueryItems().get(1).qty, 30)

    def test_raises_time_line_error(self):
        self.core.AddTransaction(date=date(2013,2,1))
        with self.assertRaises(core.TimeLineError):
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

        self.core.RevertTo(-2)

        self.assertEqual(initial_state, self.get_state())

    def test_positional_reverts(self):
        initial_state = self.get_state()
        id1 = self.core.AddTransaction( date=date(2013,1,1),
                info='Happy New Year',
                units=[Unit(item_id=1,qty=3,discount=20,type=SALE)]
                    )
        id2 = self.core.AddTransaction( date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)]
                            )
        mid_state = self.get_state()

        id3 = self.core.AddTransaction( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)]
                            )

        end_state = self.get_state()

        self.core.RevertTo(id3)
        self.assertEqual(self.get_state(), end_state)

        self.core.RevertTo(id2)
        self.assertEqual(self.get_state(), mid_state)

        self.core.RevertTo(0)
        self.assertEqual(self.get_state(), initial_state)

    def get_state(self):
        return ( self.core.QueryItems().filter(Item.qty > 0).all(),
                    self.core.QueryTransactions().all() )

if __name__ == '__main__':
    unittest.main()
