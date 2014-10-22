import csv
import sys

from salesman.lib.schema import Item
from salesman.lib.core import SALE, OTHER_TYPES as OTHERS, unit_total
from salesman.lib.models import UserError
from salesman.lib.utils import text_to_html
import salesman.plugintypes as pt

class StatementWriter(pt.IStatementWriter):
    ext_info = ('csv','Comma Separated Value')

    def write(self, path, statement, items, startDate, endDate):
        opened = False
        try:
            fd = open(path,'wb')
            opened = True
        except IOError as e:
            raise UserError('Cannot write statement to file "{}"'
                            .format(path), str(e),e)

        writer = csv.writer(fd, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

        try:
            for row in self.format(items, statement, startDate, endDate):
                writer.writerow(row)
        except:
            e_type, e_value, e_trace = sys.exc_info()
            e_msg = "Cannot Generate Statement"
            e_reason = ("An error occured in the formatter function : {}"
                            .format(e_value))
            raise UserError(e_msg, e_reason, e_value), None, e_trace
        finally:
            if opened:
                fd.close()


    DATE_FORMAT='%d/%m/%Y'

    def format(self, items, statement, startDate, endDate):
        header1 = ['Statement : {1:{0}} - {2:{0}}'.\
                    format(self.DATE_FORMAT, startDate, endDate),
                    None,None,None,
                    'Opening',None,
                    'Additions',None,
                    'Sales',None,None,
                ] + [ j for i in OTHERS for j in (i.title(),None) ] + [
                    'Closing',None,
                    ]

        header2 = [ 'Sr.No','Name','Category','Price',      #Item info
                    'Qty','Total',                          #Opening
                    'Qty','Total',                          #Additions
                    'Qty','Discount','Total',               #Sales
                  ] + ['Qty','Total']*len(OTHERS) + [
                    'Qty','Total',                          #Closing
                ]

        summable_entries = [ None, None, None, None,   #Item info
                            0, 0,                    #Opening
                            0, 0,                    #Additions
                            0, 0, 0,                 #Sales
                         ] + [0,0]*len(OTHERS) + [
                            0, 0,                    #Closing
                        ]

        last_row = ['Total',None, None, None,          #Item info
                    0, 0,                              #Opening
                    0, 0,                              #Additions
                    0, 0, 0,                           #Sales
                   ] + [0,0]*len(OTHERS) + [
                    0, 0,                              #Closing

                ]
        yield header1
        yield header2

        for i,item in enumerate(items.order_by(Item.category)):
                if item.id not in statement:
                    continue
                r = statement[item.id]
                p = item.price

                row = [i+1, item.name, item.category, p ,               #Item info
                r['opening'], r['opening']*p,                            #Opening
                r['additions'], r['additions']*p,                        #Additions
                r['sales'], r['discount'], r['sales']*p - r['discount'], #Sales
                    ] + [j for i in OTHERS for j in (r[i],r[i]*p)] + [
                r['closing'], r['closing']*p,                           #Closing

                ]

                yield row

                for i in range(len(summable_entries)):
                    if summable_entries[i] is not None:
                        summable_entries[i] += row[i]

        for i in range(len(last_row)):
                if last_row[i] == 0:
                    last_row[i] = summable_entries[i]
                    assert last_row[i] is not None
        yield last_row
