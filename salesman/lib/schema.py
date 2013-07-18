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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Float, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship , backref
import sqlalchemy
import datetime
import unittest

Base = declarative_base()
EPSILON=0.01
def has_equal_attrs(obj1, obj2, attrs=[]):
    try:
        return all(getattr(obj1,a)==getattr(obj2,a) for a in attrs)
    except AttributeError:
        return False

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
        return has_equal_attrs(self, obj, ['name','category','qty']) \
            and (self.price-obj.price) < EPSILON

    def __repr__(self):
        return '<Item(id={id},name={name},category={category},\
price={price}, qty={qty})>'.format(**{a:getattr(self,a)
            for a in ['id','name','category','price','qty']})

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    info = Column(String)
    type = Column(String)

    def __repr__(self):
        return '<Transaction(id={id}, date={date}, units={units}>'\
                .format(**{a:getattr(self,a) for a in ['id','date','units']})

    def __eq__(self, obj):
        return has_equal_attrs(self, obj, ['date','units','type'])

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

    def __eq__(self, obj):
        return has_equal_attrs(self, obj,
                                ['qty','discount','type','item'])

    def __repr__(self):
        return '<Unit(type={type},qty={qty},item={item},discount={discount})>'.\
                    format(**{a:getattr(self,a) for a in ['type','qty','discount','item']})
