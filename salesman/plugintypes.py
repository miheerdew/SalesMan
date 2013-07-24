from yapsy.IPlugin import IPlugin
class IStatementFormatter(IPlugin):
    def format(self, items, statement, startDate, endDate):
        raise NotImplementedError
