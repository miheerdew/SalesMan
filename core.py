from __future__ import unicode_literals

import datetime
import unittest
from threading import Lock

import sqlalchemy
from sqlalchemy.exc import NoReferenceError

import schema

class ItemNotFoundError(Exception):
    def __init__(self, item_id):
        self.item_id = item_id

    def __str__(self):
        return "Item with item_id:'%d' was not found"%(self.item_id)

class ItemtNotAvailableError(Exception):
    def __init__(self, item, requested_qty):
        self.item = item
        self.requested_qty = requested_qty

        if item.qty > 0:
            self.msg = "Only %d items of %s available,while you have asked for %d" % (self.item.qty, self.item, self.requested_qty)
        else:
            self.msg = "The item %s is out of stock" % (self.item)

    def __str__(self):
        return self.msg

class Core:
    def __init__(self, session):
        self.session = session
        self.lock = Lock()

    def ensureItemIsCreated(self, name, category,
                                price, description=''):
        with self.lock:

            product = self.session.query(schema.Product).filter_by(name=name, category=category).first()
            if product is None:
                product = schema.Product(name=name, category=category)
                self.session.add(product)

            assert product
            item = self.session.query(schema.Item).filter_by(product_id=product.id, price=price).first()

            if item is None:
                item = schema.Item(price=price, qty=0,
                        description=description, product_id=product.id)
                self.session.add(item)
                self.session.commit()
                return True

            return False

    def registerTransaction(self,transaction):
        with self.lock:

            for addition in transaction.additions:
                item_id = addition.item_id
                item = self.session.query(schema.Item).filter_by(id=item_id).first()
                if not item:
                    self.session.rollback()
                    raise ItemNotFoundError(item_id)
                item.qty += addition.qty

            for subtraction in transaction.subtractions:
                item_id = subtraction.item_id
                item = self.session.query(schema.Item).filter_by(id=item_id).first()
                if not item:
                    self.session.rollback()
                    raise ItemNotFoundError(item_id)
                if item.qty < subtraction.qty:
                    self.session.rollback()
                    raise ItemNotFoundError(item, substraction.qty)
                item.qty -= subtraction.qty

            self.session.add(transaction)
            self.session.commit()

class TestCore(schema.DBTestBase):
    def setUp(self):
        schema.DBTestBase.setUp(self)
        self.core = Core(self.session)

    def runTest(self):
        self.createItems()
        self.registerTransaction()

    def createItems(self):
        self.core.ensureItemIsCreated('Sherlock Holmes','Book',400,'Paper Back')
        self.core.ensureItemIsCreated('Sherlock Holmes','Book',400,'No Back')
        self.core.ensureItemIsCreated('Sherlock Holmes','Book',1000,'Hard Bound')
        products = self.session.query(schema.Product).all()
        self.assertEqual(len(products),1)
        items = self.session.query(schema.Item).all()
        self.assertEqual(len(items),2)
        self.assertEqual(items[0].product_id,items[1].product_id)
        self.assertEqual(items[0].price,400)
        self.assertEqual(items[1].price,1000)
        self.assertEqual(items[0].description,'Paper Back')


    def registerTransaction(self):
        t = schema.Transaction(date=datetime.date(2012,12,12))
        t.additions = [schema.Addition(qty=10,item_id=1),
                        schema.Addition(qty=100, item_id=2)]
        self.core.registerTransaction(t)
        self.assertSequenceEqual(self.session.query(schema.Transaction).all(),[t])
        self.assertSequenceEqual(self.session.query(schema.Addition).all(),t.additions)
        self.assertEqual(self.session.query(schema.Item).filter_by(id=1).first().qty,10)
        self.assertEqual(self.session.query(schema.Item).filter_by(id=2).first().qty,100)

        t1 = schema.Transaction(date=datetime.date(2012,12,12))
        t1.subtractions = [schema.Subtraction(qty=5,item_id=1, discount=10),
                         schema.Subtraction(qty=5, item_id=2)]
        self.core.registerTransaction(t1)
        self.assertSequenceEqual(self.session.query(schema.Transaction).all(),[t,t1])
        self.assertSequenceEqual(self.session.query(schema.Addition).all(),t.additions)
        self.assertSequenceEqual(self.session.query(schema.Subtraction).all(),t1.subtractions)
        self.assertEqual(self.session.query(schema.Item).filter_by(id=1).first().qty,5)
        self.assertEqual(self.session.query(schema.Item).filter_by(id=2).first().qty,95)


if __name__ == '__main__':
    unittest.main()
