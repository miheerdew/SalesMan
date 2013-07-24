from salesman.lib.schema import Item
import salesman.plugintypes as pt

DATE_FORMAT='%d/%m/%Y'

class StatementFormatter(pt.IStatementFormatter):

    def format(self, items, statement, startDate, endDate):
        header1 = ['Statement : {1:{0}} - {2:{0}}'.\
                    format(DATE_FORMAT, startDate, endDate),
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


