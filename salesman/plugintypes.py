from yapsy.IPlugin import IPlugin

class IStatementFormatter(IPlugin):
    def format(self, items, statement, startDate, endDate):
        raise NotImplementedError

class ITransactionFormatter(IPlugin):
    def format(self, transaction):
        raise NotImplementedError
