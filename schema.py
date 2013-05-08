from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Float, Integer, String, Date
from sqlalchemy.orm import relationship , backref
import sqlalchemy
import datetime
import unittest

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    price = Column(Float, nullable=False)
    qty = Column(Integer, default=0)
    description = Column(String)

    product_id = Column(Integer,ForeignKey('products.id'))

    product = relationship('Product',
                backref=backref('items', order_by=id))


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    info = Column(String)


class Addition(Base):
    __tablename__ = 'additions'

    id = Column(Integer, primary_key=True)
    qty = Column(Integer)
    discount = Column(Float)
    item_id = Column(Integer, ForeignKey('items.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    item = relationship('Item')
    transaction = relationship('Transaction',
                    backref=backref('additions'))


class Subtraction(Base):
    __tablename__ = 'subtractions'

    id = Column(Integer, primary_key=True)
    qty = Column(Integer)
    discount = Column(Float)
    item = relationship('Item')
    item_id = Column(Integer, ForeignKey('items.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    transaction = relationship('Transaction',
                    backref=backref('subtractions'))



def test():

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import datetime

    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine)()

    b1 = Product(name='How stuff works', category='Book')
    b2 = Product(name='Beethovens Symphony', category='CD/DVD')
    b3 = Product(name='Angels and Deamons', category='Ebook')

    b1.items = [Item(price=100, qty=10)]
    b2.items = [Item(price=500, qty=100)]
    b3.items = [Item(price=500, qty=10, description='Paperback'),
                Item(price=1500, qty=10, description='Hard Cover') ]

    session.add_all([b1,b2,b3])
    session.commit()

    t = Transaction(time=datetime.datetime.now(),
                    info="The first transaction of the store")

    assert t.additions == []
    assert t.subtractions == []

    t.additions = [Addition(qty=10, item_id=b1.items[0].id)]
    t.subtractions = [Subtraction(qty=2, item_id=b3.items[1].id)]

    expenditure = 0
    session.add(t)
    session.flush()

    for i in t.additions:
        j = i.item
        j.qty += i.qty
        expenditure += j.price*i.qty

    for i in t.subtractions:
        j = i.item
        #j = session.query(Item).filter_by(id=i.item_id).first()
        j.qty -= i.qty
        expenditure -= j.price*i.qty


    assert expenditure == (10*100) - (2*1500)
    assert session.query(Item).filter_by(price=1500).first().qty == 8
    assert session.query(Item).filter_by(price=100).first().qty == 20


class DBTestBase(unittest.TestCase):
    def setUp(self):
        engine = sqlalchemy.create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        self.session = sqlalchemy.orm.sessionmaker(bind=engine)()


class TestDB(DBTestBase):
    def setUp(self):
        DBTestBase.setUp(self)
        self.b1 = Product(name='How stuff works', category='Book')
        self.b2 = Product(name='Beethovens Symphony', category='CD/DVD')
        self.b3 = Product(name='Angels and Deamons', category='Ebook')

        self.b1.items = [Item(price=100, qty=10)]
        self.b2.items = [Item(price=500, qty=100)]
        self.b3.items = [Item(price=500, qty=10, description='Paperback'),
                Item(price=1500, qty=10, description='Hard Cover') ]

        self.session.add_all([self.b1,self.b2,self.b3])
        self.session.commit()

    def test_add_a_transaction_manually(self):
        t = Transaction(date=datetime.date(2012,12,12),
                    info="The first transaction of the store")

        self.assertEqual(t.additions,[])
        self.assertEqual(t.subtractions,[])

        t.additions = [Addition(qty=10, item_id=self.b1.items[0].id)]
        t.subtractions = [Subtraction(qty=2, item_id=self.b3.items[1].id)]

        expenditure = 0
        self.session.add(t)
        self.session.flush()

        for i in t.additions:
            j = i.item
            j.qty += i.qty
            expenditure += j.price*i.qty

        for i in t.subtractions:
            j = i.item
            #j = session.query(Item).filter_by(id=i.item_id).first()
            j.qty -= i.qty
            expenditure -= j.price*i.qty

        self.assertEqual(expenditure,(10*100) - (2*1500))
        self.assertEqual(self.session.query(Item).filter_by(price=1500).first().qty,8)
        self.assertEqual(self.session.query(Item).filter_by(price=100).first().qty,20)


if __name__ == '__main__':
    unittest.main()

