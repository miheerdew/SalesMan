from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Float, Integer, String, Date
from sqlalchemy.orm import relationship , backref
import sqlalchemy
import datetime
import unittest

Base = declarative_base()

def ClearTable(mapper_class, session):
    for r in session.query(mapper_class):
        session.delete(r)

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    price = Column(Float, nullable=False)
    qty = Column(Integer, default=0)
    description = Column(String)

    def __init__(self, name, category, price, qty, description=''):
        self.name = name
        self.category = category
        self.price = price
        self.qty = qty
        self.description = description

    def __repr__(self):
        return '<Item(id=%(id)d,name=%(name)s,category=%(category)s,\
price=%(price).2f, qty=%(qty)d)>' % self.__dict__

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    info = Column(String)

    def __repr__(self):
        return '<Transaction(id=%(id)d, date=%(date)s>'%self.__dict__

class Addition(Base):
    __tablename__ = 'additions'

    id = Column(Integer, primary_key=True)
    qty = Column(Integer)
    discount = Column(Float)
    item_id = Column(Integer, ForeignKey('items.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    item = relationship('Item')
    transaction = relationship('Transaction',
                    backref=backref('additions',cascade='all,delete-orphan'))


class Subtraction(Base):
    __tablename__ = 'subtractions'

    id = Column(Integer, primary_key=True)
    qty = Column(Integer)
    discount = Column(Float)
    item = relationship('Item')
    item_id = Column(Integer, ForeignKey('items.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    transaction = relationship('Transaction',
                    backref=backref('subtractions',cascade='all,delete-orphan'))


