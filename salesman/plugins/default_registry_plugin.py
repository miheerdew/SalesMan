from __future__ import division
import xlsxwriter
import salesman.plugintypes as pt
from salesman.lib.schema import Item
from salesman.lib.core import ADDITION
from sqlalchemy.sql import collate

class Writer(pt.IRegistryWriter):
    ext_info = ('xlsx', 'Excel Workbook')

    def write(self, path, registry, items, startDate, endDate):

        self.wb = xlsxwriter.Workbook(path)
        self.title_format = self.wb.add_format({'bold':'True', 'align':'center', 'valign':'vcenter'})
        self.date_format = self.wb.add_format({'num_format':'dd-mm-yyyy', 'valign':'vcenter'})
        self.desc_format = self.wb.add_format({'align':'center','valign':'vjustify'})
        self.align_center= self.wb.add_format({'align':'center', 'valign':'vcenter'})
        self.vcenter_top = self.wb.add_format({'valign':'top'})
        self.align_right = self.wb.add_format({'align':'right', 'valign':'vcenter'})

        self.last_name = None
        self.repeat_count = 0
        for item in items.order_by(collate(Item.name, 'NOCASE')):
            if item.id in registry:
                self.write_entry(item, registry[item.id])
        try:
            self.wb.close()
        except IOError as e:
            raise UserError('Cannot write register to file "{}"'.format(path), str(e), e)

    def write_entry(self, item, entries):
        PREFIX_LEN = 4
        if item.name[:PREFIX_LEN] == self.last_name:
            self.repeat_count += 1
            name = '{}{}'.format(self.last_name, self.repeat_count)
        else:
            self.repeat_count = 0
            name = self.last_name = item.name[:PREFIX_LEN]

        ws = self.wb.add_worksheet(name)
        ws.freeze_panes(5, 1)

        ws.write('A1', 'Name', self.title_format)
        ws.set_column('A:A',8)

        ws.merge_range('B1:E1', item.name, self.desc_format)

        ws.write('A2', 'Category', self.title_format)
        ws.write('B2', item.category, self.align_center)

        ws.write('A3', 'Price', self.title_format)
        ws.write('B3', item.price, self.align_center)

        ws.write_row('A5', ('SrNo', 'Date', 'Type', 'Particulars', 'Qty'), self.title_format)
        ws.set_column('B:B', 12)
        ws.set_column('C:C', 10)
        DESC_WIDTH = 30
        ws.set_column('D:D', DESC_WIDTH)
        ws.set_column('E:E', 5)

        ws.set_row(0, 15*estimated_height([item.name], width=12+10+DESC_WIDTH+5))

        ws.write('D7', 'Opening Qty', self.title_format)
        ws.write('E7', entries['opening'], self.align_right)

        linenum = 9
        for i, u in enumerate(entries['units'], 1):
            t = u.transaction
            sign = 1 if u.type == ADDITION else -1
            ws.write(linenum-1, 0, i, self.align_center)
            ws.write(linenum-1, 1, t.date, self.date_format)
            ws.write(linenum-1, 2, u.type.upper(), self.align_center)

            l = lines(u.transaction.info)
            ws.write(linenum-1, 3, '\n'.join(l), self.desc_format)
            h = estimated_height(l, width=DESC_WIDTH) #in lines
            ws.set_row(linenum-1, 15*(max(h,1)))

            ws.write(linenum-1, 4, sign*u.qty, self.align_right)
            linenum += 1

        linenum += 1
        ws.write('D{}'.format(linenum), 'Closing Qty', self.title_format)
        ws.write('E{}'.format(linenum), entries['closing'], self.align_right)

        ws.repeat_rows(4)
        ws.set_margins(left=1.5, right=0.30)
        ws.hide_gridlines(0)
        ws.fit_to_pages(1,0)

def lines(string):
    return [l.strip() for l in string.split('\n') if l.strip()]

def estimated_height(lines, width):
    return sum(len(l)//width + 1 for l in lines)
