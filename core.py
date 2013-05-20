from schema import Item, Transaction, ClearTable, Addition, Subtraction
from sqlalchemy.orm import sessionmaker

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

    def AddTransaction(self,
                        date,
                        additions=[],
                        subtractions=[],
                        info=''):

        last_transaction = self.session.query(Transaction).\
                            order_by(Transaction.id.desc()).first()

        if last_transaction and (last_transaction.date > date):
            raise TimeLineError

        try:
            t = Transaction(date=date,info=info)
            for a in additions:
                assert isinstance(a,Addition)
                if a.item_id is None:
                    assert isinstance(a.item,Item)
                    if a.item.id is None:
                        a.item.qty = 0
                        self.session.add(a.item)
                        self.session.flush()
                    a.item_id = a.item.id
                assert a.item_id is not None
                item = self.session.query(Item).get(a.item_id)
                item.qty += a.qty

            for s in subtractions:
                item = self.session.query(Item).get(s.item_id)
                if item.qty < s.qty:
                    raise ItemNotAvailableError
                item.qty -= s.qty

            t.additions = additions
            t.subtractions = subtractions

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

                for a in t.additions:
                    a.item.qty -= a.qty
                    assert a.item.qty >= 0

                for s in t.subtractions:
                    s.item.qty += s.qty

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

