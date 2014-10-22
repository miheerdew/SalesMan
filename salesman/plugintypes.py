from yapsy.IPlugin import IPlugin
from .lib.constants import STATEMENT_WRITER, TRANSACTION_FORMATTER, INIT_PARSER
class IStatementWriter(IPlugin):
    @property
    def ext_info(self):
        """Should return (ext, description)"""
        raise NotImplementedError

    def write(self, path, items, statement, startDate, endDate):
        raise NotImplementedError

class ITransactionFormatter(IPlugin):
    def format(self, transaction):
        raise NotImplementedError

class IInitParser(IPlugin):
    def parse(self, type, fd):
        raise NotImplementedError

categories = {STATEMENT_WRITER:IStatementWriter,
             TRANSACTION_FORMATTER:ITransactionFormatter,
             INIT_PARSER:IInitParser}
