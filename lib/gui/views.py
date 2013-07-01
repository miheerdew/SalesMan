import wx
from wx import html
from wx.lib.mixins import listctrl as listmix
from ..images import SmallDnArrow, SmallUpArrow

class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kargs):
        wx.ListCtrl.__init__(self, *args, **kargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class ItemViewer(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent , wx.ID_ANY)

        self.headers = [('Id',50),('Name',50),('Category',100),('Price',75),('Qty',50)]
        self.attrs = ['id','name','category','price','qty']

        self.itemDataMap = {}

        self.SetupWidgets()
        #self.BindMethods()

        assert len(self.headers) == len(self.attrs)
        listmix.ColumnSorterMixin.__init__(self, len(self.headers))

        self.il = wx.ImageList(16, 16)

        self.sm_up = self.il.Add(SmallUpArrow.GetBitmap())
        self.sm_dn = self.il.Add(SmallDnArrow.GetBitmap())
        self.listCtrl.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


    def SetupWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.searchCtrl = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.searchCtrl.ShowCancelButton(1)
        self.searchCtrl.ShowSearchButton(1)
        self.searchCtrl.SetDescriptiveText('Search')

        self.listCtrl = ListCtrl(self, style=wx.LC_REPORT|wx.LC_EDIT_LABELS)

        sizer.Add(self.searchCtrl, 0, wx.CENTER)
        sizer.Add(self.listCtrl, 1, wx.EXPAND)

        self.SetSizer(sizer)

        for i,t in enumerate(self.headers):
            info = wx.ListItem()
            info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE
            info.m_image = -1
            info.m_text = t[0]
            self.listCtrl.InsertColumnInfo(i,info)
            self.listCtrl.SetColumnWidth(i,t[1])

        self.listCtrl.setResizeColumn(2)


    def GetListCtrl(self):
        return self.listCtrl

    def Update(self, items):
        self.itemDataMap = {}
        self.listCtrl.DeleteAllItems()
        for j,item in enumerate(items):
            data = [getattr(item,a) for a in self.attrs]
            self.listCtrl.Append(data)
            self.listCtrl.SetItemData(j,item.id)
            self.itemDataMap[item.id] = data

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

class InvoiceViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self , parent)
        self.html = html.HtmlWindow(self)
        self.printer = html.HtmlEasyPrinting()


        btn = wx.Button(self,label='Print')
        self.Bind(wx.EVT_BUTTON, self.OnPrint)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.html,1,wx.EXPAND)
        sizer.Add(btn, 0, wx.CENTER)

        self.SetSizer(sizer)

    def Update(self, id, type ,units):
        template = '''
        <HTML><BODY>
            Transaction Id:{}
            Transaction Type:{}
            Date:{%d,%B %Y}
            <TABLE>
                <tr>
                    <th>Id
                    <th>Description
                    <th>Category
                    <th>Unit Price
                    <th>Qty
                    <th>Discount
                    <th>Total
                </tr>
            </TABLE>
        </BODY></HTML>
'''

    def OnPrint(self, evt):
        self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintFile(self.html.GetOpenedPage())



