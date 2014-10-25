import xlsxwriter

import salesman.plugintypes as pt
from salesman.lib.models import UserError
from salesman.lib.schema import Item

class ExcelWriter(pt.IStatementWriter):
    ext_info = ('xlsx', 'Excel Workbook')

    DATE_FORMAT='%d/%m/%Y'
    NAME_WIDTH=30

    def write(self, path, statement, items, start_date, end_date):
        self.wb = xlsxwriter.Workbook(path)
        self.statement_date = '{1:{0}}-{2:{0}}'.format(self.DATE_FORMAT, start_date, end_date)
        self.ws = self.wb.add_worksheet()

        self.write_headers()
        count = self.write_items(items, statement)
        self.write_footer(count)
        self.write_print_settings()
        try:
            self.wb.close()
        except IOError as e:
            raise UserError('Cannot write statement to file "{}"'.format(path), str(e), e)


    def write_headers(self):
        ws = self.ws
        align_center = self.wb.add_format({'align':'center'})

        ws.write('A1', 'No')
        ws.set_column('A:A', 4) 

        ws.write('B1', 'Name of Publication')
        ws.set_column('B:B', self.NAME_WIDTH)
        ws.write('B2', self.statement_date, align_center)

        ws.write('C1', 'Type')
        ws.set_column('C:C', 6)

        ws.write('D1', 'Price')
        ws.set_column('D:D', 5)

        ws.merge_range('E1:F1', 'Opening')
        ws.write_row('E2', ('Qty', 'Total'))
        ws.set_column('E:E', 4)
        ws.set_column('F:F', 7)

        ws.merge_range('G1:H1', 'Addtions')
        ws.write_row('G2', ('Qty', 'Total'))
        ws.set_column('G:G', 4)
        ws.set_column('H:H', 6)

        ws.merge_range('I1:K1', 'Sales')
        ws.write_row('I2', ('Qty', 'Disc.', 'Total'))
        ws.set_column('I:I', 4)
        ws.set_column('J:J', 4)
        ws.set_column('K:K', 6)

        ws.merge_range('L1:M1', 'Gifts')
        ws.write_row('L2', ('Qty', 'Total'))
        ws.set_column('L:L', 4)
        ws.set_column('M:M', 6)

        ws.merge_range('N1:O1', 'Transfers')
        ws.write_row('N2', ('Qty', 'Total'))
        ws.set_column('N:N', 4)
        ws.set_column('O:O', 6)

        ws.merge_range('P1:Q1', 'Library')
        ws.write_row('P2', ('Qty', 'Total'))
        ws.set_column('P:P', 4)
        ws.set_column('Q:Q', 6)

        ws.merge_range('R1:S1', 'Closing')
        ws.write_row('R2', ('Qty', 'Total'))
        ws.set_column('R:R', 4)
        ws.set_column('S:S', 7)

        self.style = self.wb.add_format({'align': 'center', 'bold':True})

        ws.set_row(0, None, self.style)
        ws.set_row(1, None, self.style)
        ws.freeze_panes(2,1)

    def write_footer(self, count):
        def f(col):
            self.ws.write('{0}{1}'.format(col, count+3), '=SUM({0}3:{0}{1})'.format(col, count+2))  

        self.ws.write(count+2, 1, 'Total', self.style)
        for col in 'EFGHIJKLMNOPQRS':
            f(col)

    def write_items(self, items, statement):
        row_fmt = self.wb.add_format()
        row_fmt.set_align('vcenter')

        name_fmt = self.wb.add_format()
        name_fmt.set_text_wrap()
        name_fmt.set_align('vcenter')

        index_fmt = self.wb.add_format({'align':'center', 'valign':'vcenter'})

        count = 0

        def f(fmt_str):
            return fmt_str.replace('#','{0}').format(count+2)

        for item in items.order_by(Item.category, Item.name):
            if item.id not in statement:
                continue

            count += 1
            s = statement[item.id]
            self.ws.write_row(count + 1, 2,
                        ( item.category, item.price,
                                        s['opening'], f('=E#*D#'),
                                        s['additions'], f('=G#*D#'),
                                        s['sales'], s['discount'], f('=I#*D#-J#'),
                                        s['gifts'], f('=L#*D#'),
                                        s['transfers'], f('=N#*D#'),
                                        s['library'], f('=P#*D#'),
                                        f('=E#+G#-I#-L#-N#-P#'), f('=R#*D#')))
            self.ws.write(count+1, 0, count, index_fmt)
            self.ws.write(count+1, 1, item.name, name_fmt)
            self.ws.set_row(count+1, 15*(len(item.name)/self.NAME_WIDTH + 1), row_fmt)
        return count

    def write_print_settings(self):
        self.ws.set_landscape()
        self.ws.repeat_rows(0,1)
        self.ws.set_margins(left=0.30, right=0.30)
        self.ws.hide_gridlines(0)
        self.ws.fit_to_pages(1,0)
