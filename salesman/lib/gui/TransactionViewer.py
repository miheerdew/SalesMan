import wx
from datetime import date
from .common import ListCtrl
from .events import EVT_TRANSACTION_SELECTED, PostTransactionSelectedEvent,\
                     EVT_TRANSACTION_UNDO, PostTransactionUndoEvent
from ..topics import TRANSACTION_CHANGED, REDO
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

        self.attr = wx.ListItemAttr()
        self.attr.SetBackgroundColour("Yellow")
        #self.attr.SetTextColour("White")

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
        self.RefreshItems(0,self.count-1)
        self.doSelect(self.count-1)

    def doSelect(self, idx):
        self.Select(self.count-1)
        self.Focus(self.count-1)
        PostTransactionSelectedEvent(self,self.getSelectedTransaction())

    def OnGetItemAttr(self, row):
        if row == self.count-1:
            return self.attr
        else:
            return None

    def OnGetItemText(self ,row, col):
        if row == self.count-1:
            return '-' if col != 3 else 'State of Items now'
        val = getattr(self.getTransactionAt(row),self.attrs[col])
        if isinstance(val,date):
            val = '{:%x}'.format(val)
        return val
