from salesman.lib.schema import Item
from salesman.lib.models import UserError
from salesman.lib.constants import CSV
from salesman.lib.utils import normalizeString, standardizeString
import csv

import salesman.plugintypes as pt

class InitParser(pt.IInitParser):
    def parse(self, type, fd):
        if type != CSV:
            raise UserError('Cannot Parse Init File','Only CSV file supported')
        dialect = csv.Sniffer().sniff(fd.read(1024))
        fd.seek(0)
        reader = csv.DictReader(fd, dialect=dialect)
        permitted = {'name','qty','price','description','category'}
        fnames=set(map(normalizeString, reader.fieldnames))
        if not ( fnames <=  permitted):
            e_msg = ('Cannot process init file ',
            'Cannot recognize fieldnames {}'.format(list(fnames - permitted)) +
            'The fieldnames should only be from {},'.format(list(permitted)))
            raise UserError(*e_msg)

        for i,row in enumerate(reader):
            line_num = i+2
            args = {normalizeString(k):standardizeString(v) for k,v in row.items()}
            try:
                args['qty']=int(args['qty'])
                args['price']=float(args['price'])
            except ValueError:
                e_msg = ('Cannot process file {} '.format(csvfile),
                    'Cannot convert string to numeric'
                    'value at line {}'.format(line_num))
                raise UserError(*e_msg)
            yield Item(**args)
