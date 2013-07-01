from wx.lib.mixins import listctrl as listmix
import wx
from wx import html
from datetime import date
from ..core import ADDITION, SALE, GIFT, TRANSFER
import string
from wx.lib.masked import NumCtrl

def pydate2wxdate(date):
     import datetime
     assert isinstance(date, (datetime.datetime, datetime.date))
     tt = date.timetuple()
     dmy = (tt[2], tt[1]-1, tt[0])
     return wx.DateTimeFromDMY(*dmy)

def wxdate2pydate(date):
     import datetime
     assert isinstance(date, wx.DateTime)
     if date.IsValid():
         ymd = map(int, date.FormatISODate().split('-'))
         return datetime.date(*ymd)
     else:
         return None

class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self,*args, **kargs):
        wx.ListCtrl.__init__(self, *args, **kargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class IVListCtrl(ListCtrl):
    def __init__(self, parent):
        self.items = []
        self.headers = [('Id',50),('Name',50),('Category',100),('Price',75),('Qty',50)]
        self.attrs = ['id','name','category','price','qty']

        ListCtrl.__init__(self, parent, style=wx.LC_REPORT|wx.LC_VIRTUAL)

        for i,t in enumerate(self.headers):
            self.InsertColumn(i,t[0])
            self.SetColumnWidth(i,t[1])
            self.setResizeColumn(2)
            self.SetItemCount(0)

    def UpdateValues(self, items):
        count = items.count()
        self.SetItemCount(count)
        self.items = items
        self.RefreshItems(0,count)

    def OnGetItemText(self ,row, col):
        return getattr(self.items[row],self.attrs[col])

class ItemViewer(wx.Panel):
    def __init__(self, parent, searchCallback, selectionCallback):
        wx.Panel.__init__(self, parent , wx.ID_ANY)

        self.SetupWidgets()
        self.PositionWidgets()
        self.BindWidgets(searchCallback, selectionCallback)

    def SetupListCtrl(self):
        self.listCtrl = IVListCtrl(self)

    def SetupSearchCtrl(self):
        self.searchCtrl = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.searchCtrl.ShowCancelButton(1)
        self.searchCtrl.ShowSearchButton(1)

    def SetupWidgets(self):
        self.SetupListCtrl()
        self.SetupSearchCtrl()

    def PositionWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.searchCtrl, 0, wx.CENTER)
        sizer.Add(self.listCtrl, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def BindWidgets(self, searchCallback, selectionCallback):

        def do_search(evt):
            searchCallback(self.searchCtrl.GetValue())

        def cancel_search(evt):
            searchCallback(None)

        self.searchCtrl.Bind(wx.EVT_TEXT_ENTER, do_search)
        self.searchCtrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, do_search)
        self.searchCtrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, cancel_search)

        def on_select(evt):
            selectionCallback(self.listCtrl.items[evt.m_itemIndex])

        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, on_select)

    def UpdateValues(self, items):
        self.listCtrl.UpdateValues(items)


class TransactionView(wx.Panel):
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

    def UpdateValues(self, id, date, type, info, units):
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

        """.format(**locals())

        if type == SALE:
            html += """<table width="100%", border="1" cellpadding="5" cellspacing="0">
                <tr>
                <th>Sr No.</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Rate</th>
                <th>Discount %</th>
                <th>Total</th>
            </tr>"""

            rows = []
            grand = 0
            for i,u in enumerate(units):
                total = u.qty * u.item.price * (100-u.discount)/100
                grand += total
                row = """<tr>
                    <td>{index}</td>
                    <td><b>{u.item_id}</b>-{u.item.name}</td>
                    <td>{u.qty}</td>
                    <td>{u.item.price:0.2f}</td>
                    <td>{u.discount}</td>
                    <td>{total:0.2f}</td>
                    </tr>
                """.format(index=i+1, u=u, total=total)
                rows.append(row)

            html += '\n'.join(rows) + """
            <tr>
                <td colspan="5" align="center">Grand Total</td>
                <td>{:0.2f}</td>
            </tr>""".format(grand)

        else:
            html += """<table width="100%", border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Sr No.</th>
                <th>Description</th>
                <th>Category</th>
                <th>Qty</th>
                <th>Rate</th>
            </tr>
            """
            rows = []
            for i,u in enumerate(units):
                row = """<tr>
                    <td>{index}</td>
                    <td>{u.item.name}</td>
                    <td>{u.item.category}</td>
                    <td>{u.qty}</td>
                    <td>{u.item.price:0.2f}</td>
                    </tr>
                """.format(index=i+1, u=u)
                rows.append(row)
            html += '\n'.join(rows)
        html += """</table></body></html>"""
        self.html.SetPage(html)


class TVListCtrl(ListCtrl):
    def __init__(self, parent):
        self.transactions = []
        self.headers = [('Id',50),('Date',100),('Type',100),('Info',75)]
        self.attrs = ['id','date','type','info']
        ListCtrl.__init__(self, parent, style=wx.LC_REPORT|
                                        wx.LC_VIRTUAL|
                                        wx.LC_SINGLE_SEL)

        for i,t in enumerate(self.headers):
            self.InsertColumn(i,t[0])
            self.SetColumnWidth(i,t[1])

    def UpdateValues(self, transactions):
        count = transactions.count()
        self.SetItemCount(count)
        self.transactions = transactions
        self.RefreshItems(0,count)
        self.Select(count-1)

    def OnGetItemText(self ,row, col):
        val = getattr(self.transactions[row],self.attrs[col])

        if isinstance(val,date):
            val = '{:%x}'.format(val)

        return val

class TransactionViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetupWidgets()
        self.PositionWidgets()
        self.BindWidgets()

    def SetupWidgets(self):
        self.listCtrl = TVListCtrl(self)
        self.tv = TransactionView(self)

    def PositionWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listCtrl, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self.tv, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)

    def BindWidgets(self):
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)

    def OnSelect(self, evt):
        t = self.listCtrl.transactions[evt.m_itemIndex]
        self.tv.UpdateValues(id=t.id, date=t.date, type=t.type,
                                    info=t.info, units=t.units)

    def UpdateValues(self, transactions):
        self.listCtrl.UpdateValues(transactions)


class Page(wx.Panel):
    def __init__(self, parent, type, Entry, View):
        wx.Panel.__init__(self, OnItemAddCallback, OnCommitCallback)

        self.entry = Entry(self, OnItemAddCallback, OnCommitCallback)
        self.view = View(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.entry, 0, wx.ALL, 5)
        sizer.Add(self.view, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def UpdateValues(self , **kargs):
        self.view.UpdateValues(**kargs)


class IntValidator(wx.PyValidator):
    def __init__(self, flag=None, pyVar=None):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return IntValidator(self.flag)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
            for x in val:
                if x not in string.digits:
                    return False
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == ALPHA_ONLY and chr(key) in string.letters:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in string.digits:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

DATE, ALPHA_NUM, NUM, FLOAT = range(3)

class KeyValue(wx.Panel):
    def __init__(self, parent, label, type=ALPHA_NUM):
        wx.Panel.__init__(self)
        self.label = wx.StaticText(self, label=label)
        self.type = type

        if self.type == DATE:
            self.entry = wx.DatePickerCtrl(self, style=wx.DP_DROPDOWN
                                      | wx.DP_SHOWCENTURY
                                      | wx.DP_ALLOWNONE )
        else:
            if self.type == NUM:
                validator = IntValidator
            else:
                validator = wx.DefaultValidator

            self.entry = wx.TextCtr(self, validator=validator)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.label, 0)
        sizer.Add(self.entry, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def GetValue(self):
        if self.type == DATE:
            return wxdate2pydate(self.entry.GetValue())

        if self.type == NUM:
            return int(self.entry.GetValue())

        if self.type == ALPHA_NUM:
            return self.entry.GetValue()

class Entry(wx.Panel):
    def __init__(self, parent, OnItemAddCallback, OnCommitCallback
                askDiscount=True, askId=True ):
        wx.Panel.__init__(self, parent)

        self.OnItemAddCallback = OnItemAddCallback
        self.OnCommitCallback = OnCommitCallback

        self.SetupWidgets(askDiscount, askId)

    def SetupWidgets(self, askDiscount, askId):

        if askId:
            self.id = KeyValue(self, label = 'Id', type=NUM)
        else:
            self.id = None

        self.date = KeyValue(self, label='Date', type=DATE)

        self.name = KeyValue(self, label='Name')
        self.Qty =

        self.addBtn = wx.Button(self, label='Add Item')


class TransactionMaker(wx.Notebook):
    def __init__(self, parent, OnItemAddCallback,
                OnTypeChangedCallback, OnCommitCallback):
        wx.Notebook.__init__(self, parent)

        self.OnTypeChangedCallback = OnTypeChangedCallback

        self.pages = [(type,
            Page(self.note, type, OnItemAddCallback, OnCommitCallback)
            for type in (ADDITION, SALE, GIFT, TRANSFER)]

        for p in self.pages:
            self.note.AddPage(p[1],p[0])

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, evt):
        self.OnTypeChangedCallback(self.pages[evt.GetSelection()][0])

    def UpdateValues(self, **kargs):
        self.pages[self.GetSelection()].UpdateValues(**kargs)

    def SetItem(self, item):
        self.pages[self.GetSelection()].SetItem(item)


