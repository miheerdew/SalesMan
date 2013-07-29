from yapsy.IPlugin import IPlugin
from .lib.constants import STATEMENT_FORMATTER, TRANSACTION_FORMATTER, INIT_PARSER
class IStatementFormatter(IPlugin):
    def format(self, items, statement, startDate, endDate):
        raise NotImplementedError

class ITransactionFormatter(IPlugin):
    def format(self, transaction):
        raise NotImplementedError

class IInitParser(IPlugin):
    def parse(self, type, fd):
        raise NotImplementedError

categories = {STATEMENT_FORMATTER:IStatementFormatter,
             TRANSACTION_FORMATTER:ITransactionFormatter,
             INIT_PARSER:IInitParser}
