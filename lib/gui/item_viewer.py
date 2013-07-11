import wx
from .common import ListCtrl

class ItemViewer(ListCtrl):
    def __init__(self, parent, **kargs):
        self.items = []
        self.headers = [('Id',50),('Name',50),('Category',100),('Price',75),('Qty',50)]
        self.attrs = ['id','name','category','price','qty']

        kargs['style'] = wx.LC_REPORT|wx.LC_VIRTUAL|kargs.get('style',0)
        ListCtrl.__init__(self, parent, **kargs)

        for i,t in enumerate(self.headers):
            self.InsertColumn(i,t[0])
            self.SetColumnWidth(i,t[1])
            self.setResizeColumn(2)
            self.SetItemCount(0)

    def GetItemAt(self, index):
        return self.items[index]

    def UpdateDisplay(self, items):
        count = items.count()
        self.SetItemCount(count)
        self.items = items
        self.RefreshItems(0,count)

    def OnGetItemText(self ,row, col):
        return getattr(self.items[row],self.attrs[col])

