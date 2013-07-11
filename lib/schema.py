from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Float, Integer, String, Date, Boolean
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

    def __init__(self, name, category, price, id=None, qty=None, description=''):
        self.name = name
        self.id = id
        self.category = category
        self.price = price
        self.qty = qty
        self.description = description

    def __eq__(self, obj):
        return repr(self) == repr(obj)

    def __repr__(self):
        return '<Item(id={id},name={name},category={category}s,\
price={price}, qty={qty})>'.format(**self.__dict__)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    info = Column(String)
    type = Column(String)

    def __repr__(self):
        return '<Transaction(id=%(id)d, date=%(date)s>'%self.__dict__

class Unit(Base):
    __tablename__ = 'units'

    id = Column(Integer, primary_key=True)
    qty = Column(Integer)
    discount = Column(Float)
    item_id = Column(Integer, ForeignKey('items.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    item = relationship('Item')
    transaction = relationship('Transaction',
                    backref=backref('units',cascade='all,delete-orphan'))
    type = Column(String)
    item_first_seen = Column(Boolean)

    def __init__(self, qty, type, item_id=None, item=None, discount=0, item_first_seen=False):
        for a in ('qty','type','item_id','item','discount','item_first_seen'):
            setattr(self, a, locals()[a])
