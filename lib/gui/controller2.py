import wx
from .models import *
from .views2 import *
from datetime import date
from wx.lib.pubsub import Publisher as pub

class MainFrame(wx.Frame):
    def __init__(self, parent, iv):
        wx.Frame.__init__(self, parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.iv = ItemViewer(self, *iv)
        self.tv = TransactionViewer(self)

        sub_sizer.Add(self.iv, 1, wx.EXPAND|wx.ALL , 5)
        sub_sizer.Add(self.tv, 1, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(sub_sizer,1 ,wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Show(True)

class Controller:
    def __init__(self, app):
        self.backend = Backend()
        self.ivm = ItemViewerModel(self.backend)
        self.tvm = TransactionViewerModel(self.backend)
        self.backend.SetListeners(self.ivm, self.tvm)
        self.mainFrame = MainFrame(None, iv=[self.SearchCallback, self.SelectionCallback])

        pub.subscribe(self.ItemsChanged, ITEMS)
        pub.subscribe(self.TransactionsChanged, TRANSACTIONS)

        self.test()

    def SearchCallback(self, query):
        self.ivm.Query(query if (query is not None) else '')

    def SelectionCallback(self, item):
        print item.id, item.name

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
        self.backend.AddTransaction

        self.backend.AddTransaction( date=date(2013,1,1),
                info='Happy New Year',
                units=[Unit(item_id=1,qty=3,discount=20,type=SALE)],
                type=SALE
                    )
        self.backend.AddTransaction( date=date(2013,2,1),
                        units=[Unit(item_id=1,qty=20,type=ADDITION)],
                        type=ADDITION
                            )

        self.backend.AddTransaction( date=date(2013,3,1),
                        units=[Unit(item_id=1,qty=30,type=ADDITION)],
                        type=ADDITION
                            )



    def ItemsChanged(self, message):
        self.mainFrame.iv.UpdateValues(message.data)

    def TransactionsChanged(self, message):
        self.mainFrame.tv.UpdateValues(message.data)



