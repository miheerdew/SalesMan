from .schema import Transaction
import datetime
def simple_wild_card_from_extension(ext, desc=None):
    if desc is None:
        desc = ext
    return '{0} (*.{1})|*.{1}|All Files (*.*)|*.*'.format(desc, ext)

DB_FILE_EXTENSION='sqlite'
INIT_FILE_EXTENSION='csv'
STATEMENT_FILE_EXTENSION='csv'
GET_CATEGORY='GetCategory'
DEFAULT_DB_FILE_NAME='dbfile.{}'.format(DB_FILE_EXTENSION)
DEFAULT_STATEMENT_FILE_NAME='statement.{}'.format(STATEMENT_FILE_EXTENSION)

DB_FILE_WILD_CARD=\
        simple_wild_card_from_extension(DB_FILE_EXTENSION)

INIT_FILE_WILD_CARD=\
        simple_wild_card_from_extension(INIT_FILE_EXTENSION, 'Comma Seperated Value')

STATEMENT_FILE_WILD_CARD=\
        simple_wild_card_from_extension(STATEMENT_FILE_EXTENSION, 'Comma Seperated Value')

NULL_TRANSACTION=Transaction(id=0,info='Null Transaction',date=datetime.date.max, units=[])

MAIN_FRAME_TITLE='Sales Manager'
