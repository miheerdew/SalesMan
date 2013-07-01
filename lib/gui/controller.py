import wx
from .models import *
from .views import *
from wx.lib.pubsub import Publisher as pub

class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ivv = ItemViewer(self)
        sub_sizer.Add(self.ivv, 1, wx.EXPAND|wx.ALL , 5)
        main_sizer.Add(sub_sizer,1 ,wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Show(True)

class Controller:
    def __init__(self, app):
        self.backend = Backend()
        self.ivm = ItemViewerModel(self.backend)
        self.tvm = TransactionViewerModel(self.backend)
        self.backend.SetListeners(self.ivm, self.tvm)
        self.mainFrame = MainFrame(None)

        self.mainFrame.ivv.searchCtrl.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.mainFrame.ivv.searchCtrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnDoSearch)
        self.mainFrame.ivv.searchCtrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelSearch)

        self.mainFrame.ivv.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

        pub.subscribe(self.ItemsChanged, ITEMS)
        #pub.subscribe(self.TransactionsChanged, TRANSACTIONS)

        self.test()

    def OnItemSelected(self, evt):
        index = evt.m_itemIndex
        id = self.mainFrame.ivv.listCtrl.GetItemData(index)
        print "id:%d seletcted" % id

    def OnCancelSearch(self, evt):
        self.ivm.Query('')

    def OnDoSearch(self, evt):
        query = self.mainFrame.ivv.searchCtrl.GetValue()
        self.ivm.Query(query)

    def test(self):
        self.backend.OpenDatabase('/:memory:')

        l = [   ('Abc for kids', 'BOOK', 20, 30, 'For Kids'),
                ('Abc for kids', 'BOOK', 30, 20, 'For Smaller Kids'),
                ('abc in python', 'BOOK', 40, 10, 'For Developers'),
                ('abc in python', 'BOOK', 40, 10, 'For Developers'),
            ]

        items = [ Item(name=a,category=b,price=c,qty=d,description=e)
                    for a,b,c,d,e in l ]

        self.backend.Initialize(items)


    def ItemsChanged(self, message):
        d = message.data
        self.mainFrame.ivv.Update(d)





