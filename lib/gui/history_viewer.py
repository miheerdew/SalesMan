import wx
from wx import html
from datetime import date
from .common import ListCtrl
from .item_viewer import ItemViewer
from ..core import ADDITION, SALE, GIFT, TRANSFER, unit_total
from .events import EVT_TRANSACTION_SELECTED, PostTransactionSelectedEvent,\
                     EVT_TRANSACTION_UNDO, PostTransactionUndoEvent
from ..utils import pub
from ..topics import TRANSACTION_CHANGED
from ..constants import NULL_TRANSACTION

class TransactionViewer(ListCtrl):
    def __init__(self, parent):
        self.current_selection=None
        self.transactions = []
        self.headers = [('Id',50),('Date',100),('Type',100),('Info',75)]
        self.attrs = ['id','date','type','info']
        ListCtrl.__init__(self, parent, style=wx.LC_REPORT|
                                        wx.LC_VIRTUAL|
                                        wx.LC_SINGLE_SEL)

        for i,t in enumerate(self.headers):
            self.InsertColumn(i,t[0])
            self.SetColumnWidth(i,t[1])

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)


    def OnRightDown(self, evt):
        x = evt.GetX()
        y = evt.GetY()
        item, flags = self.HitTest((x, y))
        if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
            self.Select(item)

        evt.Skip()

    def OnRightClick(self, evt):
        if not hasattr(self, "popupID"):
            self.popupID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnUndo, id=self.popupID)

        if self.current_selection not in [None,self.count-1]:
            menu = wx.Menu()
            menu.Append(self.popupID, "Undo selected transaction")
            self.PopupMenu(menu)
            menu.Destroy()

        evt.Skip()

    def OnUndo(self, event):
        PostTransactionUndoEvent(self,self.getSelectedTransaction())

    def getTransactionAt(self, i):
        if i == self.count -1:
            return NULL_TRANSACTION
        else:
            return self.transactions[i]

    def getSelectedTransaction(self):
        return self.getTransactionAt(self.current_selection)

    def OnSelect(self, evt):
        self.current_selection = evt.m_itemIndex
        PostTransactionSelectedEvent(self,self.getSelectedTransaction())
        evt.Skip()

    def UpdateDisplay(self, transactions):
        self.count = transactions.count() + 1
        self.SetItemCount(self.count)
        self.transactions = transactions
        self.RefreshItems(0,self.count)
        self.Select(self.count-1)

    def OnGetItemText(self ,row, col):
        val = getattr(self.getTransactionAt(row),self.attrs[col])
        if isinstance(val,date):
            val = '{:%x}'.format(val)
        return val

class TransactionDisplay(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.printer = html.HtmlEasyPrinting()

        self.SetupWidgets()
        self.PositionWidgets()
        self.BindWidgets()

    def SetupWidgets(self):
        self.html = html.HtmlWindow(self)
        self.printBtn = wx.Button(self, label='Print')

    def PositionWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.html, 1, wx.EXPAND)
        sizer.Add(self.printBtn, 0, wx.CENTER)
        self.SetSizer(sizer)

    def BindWidgets(self):
        self.printBtn.Bind(wx.EVT_BUTTON, self.OnPrint)

    def OnPrint(self, evt):
        #self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintText(self.html.GetParser().GetSource())

    def Blank(self):
        self.html.SetPage('')

    def UpdateDisplay(self, transaction):

        vals ={ a:getattr(transaction,a)
                for a in ('id','date','type','info','units') }

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
                    <td><b>{u.item_id}</b>-{u.item.name}</td>
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
        self.html.SetPage(html)


class HistoryViewer(wx.Frame):
    def __init__(self, backend, parent):
        wx.Frame.__init__(self, parent, size=(1000,600), title='History Viewer')
        self.backend = backend
        self.panel = wx.Panel(self)
        self.CreateControls(self.panel)
        self.PlaceControls(self.panel)
        pub.subscribe(self.OnTransactionsChange, TRANSACTION_CHANGED)
        self.Bind(wx.EVT_CLOSE, self.OnWindowClose)

    def OnWindowClose(self, evt):
        self.Show(False)

    def OnTransactionsChange(self, transactions):
        self.transaction_viewer.UpdateDisplay(transactions)

    def OnTransactionUndo(self, event):
        transaction = event.transaction
        #dlg = wx.MessageDialog(self, "Undoing this transaction will not just"\
        #" delete this transaction but also all the transactions have occured"\
        #" after this transaction. This change is irreversible and "\
        #"will result in loss of data of all deleted transactions."\
        #"Are you sure you want to continue?", 'Confirm Undo',
        # wx.YES_NO|wx.ICON_INFORMATION)

        #if dlg.ShowModal() == wx.ID_YES:
        #    self.backend.Undo(transaction)
        self.backend.Undo(transaction)

    def CreateControls(self, parent):
        self.item_viewer = ItemViewer(parent)

        self.transaction_viewer = TransactionViewer(parent)
        self.Bind(EVT_TRANSACTION_SELECTED, self.OnTransactionSelect,
                    self.transaction_viewer)
        self.Bind(EVT_TRANSACTION_UNDO, self.OnTransactionUndo,
                    self.transaction_viewer)

        self.transaction_display = TransactionDisplay(parent)

    def PlaceControls(self, parent):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(self.transaction_viewer, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        vbox.Add(self.transaction_display, 1, wx.EXPAND, 5)

        hbox.Add(self.item_viewer, 1, wx.EXPAND|wx.ALL, 5)
        hbox.Add(vbox, 1, wx.EXPAND)

        parent.SetSizerAndFit(hbox)

    def OnTransactionSelect(self, evt):
        transaction = evt.transaction
        self.item_viewer.UpdateDisplay(self.backend.GetHistory(transaction.id))
        self.transaction_display.UpdateDisplay(transaction)


