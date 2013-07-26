from salesman.lib.schema import Item
from salesman.lib.core import SALE, unit_total
from salesman.lib.utils import text_to_html
import salesman.plugintypes as pt


class StatementFormatter(pt.IStatementFormatter):

    DATE_FORMAT='%d/%m/%Y'

    def format(self, items, statement, startDate, endDate):
        header1 = ['Statement : {1:{0}} - {2:{0}}'.\
                    format(self.DATE_FORMAT, startDate, endDate),
                    None,None,None,
                    'Opening',None,
                    'Additions',None,
                    'Sales',None,None,
                    'Transfers',None,
                    'Gifts',None,
                    'Closing',None,
                    ]

        header2 = [ 'Sr.No','Name','Category','Price',      #Item info
                    'Qty','Total',                          #Opening
                    'Qty','Total',                          #Additions
                    'Qty','Discount','Total',               #Sales
                    'Qty','Total',                          #Transfers
                    'Qty','Total',                          #Gifts
                    'Qty','Total',                          #Closing
                ]

        summable_entries = [ None, None, None, None,   #Item info
                            None, 0,                    #Opening
                            None, 0,                    #Additions
                            None, 0, 0,                 #Sales
                            None, 0,                    #Transfers
                            None, 0,                    #Gifts
                            None, 0,                    #Closing
                        ]

        last_row = ['Total',None, None, None,          #Item info
                    '', 0,                              #Opening
                    '', 0,                              #Additions
                    '', 0, 0,                           #Sales
                    '', 0,                              #Transfers
                    '', 0,                              #Gifts
                    '', 0,                              #Closing

                ]
        yield header1
        yield header2

        for i,item in enumerate(items.order_by(Item.category)):
                r = statement[item.id]
                p = item.price

                row = [i+1, item.name, item.category, p ,    #Item info
                r.opening, r.opening*p,                     #Opening
                r.additions, r.additions*p,                 #Additions
                r.sales, r.discount, r.sales*p - r.discount,#Sales
                r.transfers, r.transfers*p,                 #Transfers
                r.gifts, r.gifts*p,                         #Gifts
                r.closing, r.closing*p,                     #Closing
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


class TransactionFormatter(pt.ITransactionFormatter):
    def format(self, transaction):
        vals ={ a:getattr(transaction,a)
                for a in ('id','date','type','info','units') }

        vals['info'] = text_to_html(vals['info'])

        html = """
        <html><body>
        <table width="100%" cellpadding="0" cellspacing="10" border="0">
            <tr>
                <td width="50%" valign="top">
                    <b>Id</b> : {id}
                </td>
                <td width="50%" valign="top">
                    <b> Date </b> : {date:%d, %b %Y}
                </td>
            </tr>
            <tr>
                <td columnspan=2>
                <b>Type</b> : {type}
                </td>
            </tr>
            <tr>
                <td columnspan="2">
                <b>Info</b> : {info}
                </td>
            </tr>

        </table>

        """.format(**vals)

        isSale = vals['type'] == SALE

        html += """<table width="100%", border="1" cellpadding="5" cellspacing="0">
                <tr>
                <th>Sr No.</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Rate</th>
                {}
                <th>Total</th>
            </tr>""".format("<th>Discount</th>" if isSale else "")

        rows = []
        grand_totals=dict(qty=0, discount=0, total=0)
        for i,u in enumerate(vals['units']):
            total = unit_total(u)
            grand_totals['qty'] += u.qty
            grand_totals['discount'] += u.discount
            grand_totals['total'] += total
            row = """<tr>
                    <td>{index}</td>
                    <td>{u.item.name}</td>
                    <td>{u.qty}</td>
                    <td>{u.item.price:0.2f}</td>
                    {discount_str}
                    <td>{total:0.2f}</td>
                    </tr>
                """.format(index=i+1, u=u, total=total,
                    discount_str="<td>{:0.2f}</td>".format(u.discount)
                            if isSale else '')
            rows.append(row)

        html += '\n'.join(rows) + """
            <tr>
            <td colspan="2" align="center">Grand Total</td>
            <td>{qty}</td>
            <td></td>
            {total_discount_str}
            <td>{total:0.2f}</td>
            </tr>""".format(
            total_discount_str="<td>{:0.2f}</td>".format(grand_totals['discount'])
                                if isSale else '',
                        **grand_totals)

        html += """</table></body></html>"""
        return html


