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

APP_NAME = 'SalesMan'
LAST_SESSION_SECTION_NAME='Last Session'
PLUGINS_SECTION_NAME='Plugins'
TRANSACTION_FORMATTER='Transaction Formatter'
STATEMENT_FORMATTER='Statement Formatter'
NAME='name'
PATH='path'
APP_CONFIG_FILE=APP_NAME+".conf"
PLUGINS_DIR_NAME='plugins'
DEFAULT_PLUGIN_MAP={
        STATEMENT_FORMATTER:'Default Statement Formatter',
        TRANSACTION_FORMATTER: 'Default Transaction Formatter'
        }

