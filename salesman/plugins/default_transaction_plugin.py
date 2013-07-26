from salesman.lib.core import SALE, unit_total
from salesman.lib.utils import text_to_html
import salesman.plugintypes as pt


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


