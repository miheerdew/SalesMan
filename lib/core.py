from schema import Item, Transaction, ClearTable, Unit
from sqlalchemy.orm import sessionmaker
from  sqlalchemy import and_

ADDITION = 'ADDITION'
SALE = 'SALE'
GIFT = 'GIFT'
TRANSFER = 'TRANSFER'

class ItemNotAvailableError(Exception):
    pass

class TimeLineError(Exception):
    pass

class Core:
    def __init__(self, engine):
        self.session = sessionmaker(bind=engine)()

    def Initialize(self, items):
        try:
            ClearTable(Item, self.session)
            ClearTable(Transaction, self.session)
            self.session.add_all(items)
        except:
            self.session.rollback()
            raise
        else:
            self.session.commit()

    def AddTransaction(self, date, units=[], info='', type=None):

        last_transaction = self.session.query(Transaction).\
                            order_by(Transaction.id.desc()).first()

        if last_transaction and (last_transaction.date > date):
            raise TimeLineError

        try:
            t = Transaction(date=date,info=info, type=type)
            for u in units:
                if type :
                    assert u.type == type

                assert isinstance(u,Unit)
                if u.item_id is None and u.type==ADDITION:
                    assert isinstance(u.item,Item)
                    if u.item.id is None:
                        i =  self.session.query(Item).\
                        filter(_and(Item.name == u.item.name,
                                    Item.category == u.item.category)).\
                                    first()
                        if i is None:
                            u.item.qty = 0
                            self.session.add(u.item)
                            self.session.flush()
                            u.item_id = u.item.id
                        else:
                            u.item_id = i.id
                assert u.item_id is not None
                item = self.session.query(Item).get(u.item_id)
                if u.type == ADDITION:
                    item.qty += u.qty
                else:
                    if item.qty < u.qty:
                        raise ItemNotAvailableError
                    item.qty -= u.qty


            t.units = units
            self.session.add(t)

        except:
            self.session.rollback()
            raise
        else:
            self.session.commit()

        return t.id

    def RevertTo(self,id):
        assert isinstance(id, int)
        if id < 0:
            assert self.session.query(Transaction).count() is not None
            if self.session.query(Transaction).count() <= -id:
                id = 0
            else:
                id = self.session.query(Transaction)[id-1].id

        assert id >= 0

        try:
            for t in self.session.query(Transaction).\
                            filter(Transaction.id > id).\
                            order_by(Transaction.id.desc()):

                for u in t.units:
                    if u.type == ADDITION:
                        u.item.qty -= u.qty
                        assert u.item.qty >= 0
                    else:
                        u.item.qty += u.qty

                self.session.delete(t)

        except:
            self.session.rollback()
            raise

        else:
            self.session.commit()


    def QueryItems(self):
        return self.session.query(Item)

    def QueryTransactions(self):
        return self.session.query(Transaction)

