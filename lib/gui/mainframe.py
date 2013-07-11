import wx
import os
from .multidatepicker import MultiDatePickerDialog
from ..utils import pub, silentremove, get_save_path_from_dialog
from ..topics import *
from ..constants import *
from .history_viewer import HistoryViewer
from .transaction_maker import TransactionMaker

class MenuItemToggleListener:
    def __init__(self, menuItem):
        self.menuItem = menuItem

    def __call__(self, enabled):
        self.menuItem.Enable(enabled)

class MainFrame(wx.Frame):
    def __init__(self, backend, parent, title=MAIN_FRAME_TITLE,
                    style= wx.DEFAULT_FRAME_STYLE
                          |wx.MAXIMIZE ):
        wx.Frame.__init__(self, parent, style=style, title=title)
        self.backend = backend
        self.setupMenuBar()
        self.history_viewer = HistoryViewer(backend, self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.transaction_maker = TransactionMaker(backend, self)
        pub.subscribe(self.OnAddTransactionToggle, (TOGGLE,ADD_TRANSACTION))
        sizer.Add(self.transaction_maker,1,wx.EXPAND|wx.ALL,100)


    def OnAddTransactionToggle(self,enabled):
        self.transaction_maker.Toggle(enabled)

    def menuData(self):
        return (('&File',
                    (
                        ('New Database', wx.ID_NEW,  self.OnCreateDatabase, (TOGGLE,OPEN_DATABSE)),
                        ('Open Database',wx.ID_OPEN, self.OnOpenDatabase, (TOGGLE,OPEN_DATABSE)),
                        ('Exit', wx.ID_EXIT, self.OnExit)
                    )
                ),
                ('&Database',
                    (
                        ('Initialize Database\tCTRL+I', wx.NewId(), self.OnInitDatabase, (TOGGLE,INIT_DATABASE)),
                        ('Generate Statement\tCTRL+S', wx.NewId(), self.OnGenerateStatement ,(TOGGLE,GENERATE_STATEMENT)),
                        (),
                        ('View History \tCTRL+H', wx.NewId(), self.OnViewHistory, (TOGGLE, GET_HISTORY))
                    )
                )
        )

    def setupMenuBar(self):
        self.togglers = {}
        menubar = wx.MenuBar()
        for menuLabel, menuItems in self.menuData():
            menu = wx.Menu()
            for mi in menuItems:
                if len(mi) == 0:
                    menu.AppendSeparator()
                    continue
                item = menu.Append(mi[1], mi[0])
                self.Bind(wx.EVT_MENU, mi[2], id=mi[1])
                if len(mi) >= 4:
                    self.togglers[item] = MenuItemToggleListener(item)
                    pub.subscribe(self.togglers[item], mi[3])
            menubar.Append(menu, menuLabel)
        self.SetMenuBar(menubar)

    def OnExit(self, evt):
        self.Close()

    def OnOpenDatabase(self, evt):
        dlg = wx.FileDialog(None, message="Open Database File ..",
                wildcard=DB_FILE_WILD_CARD,
                style= wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)

        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        self.backend.OpenDatabase(path)
        self.SetTitle('{} :{}'.format(MAIN_FRAME_TITLE,path))

    def OnCreateDatabase(self, evt):
        dlg = wx.FileDialog(None, message="Create Database file..",
                wildcard=DB_FILE_WILD_CARD,
                defaultFile=DEFAULT_DB_FILE_NAME,
                style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        path = get_save_path_from_dialog(dlg, DB_FILE_EXTENSION)

        if path is None:
            return

        silentremove(path)
        self.backend.OpenDatabase(path)

    def OnInitDatabase(self, evt):
        dlg = wx.FileDialog(None, message="Open file to init database ..",
                wildcard=INIT_FILE_WILD_CARD,
                style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)

        if dlg.ShowModal() != wx.ID_OK:
            return


        self.backend.InitDatabase(dlg.GetPath())

    def OnGenerateStatement(self, evt):

        dlg = MultiDatePickerDialog(self, labels=['Start Date', 'End Date'],
                    title='Enter the transaction dates')

        if dlg.ShowModal() != wx.ID_OK:
            return
        startDate, endDate = dlg.GetDates()

        dlg = wx.FileDialog(self, message="Save Statement File..",
                wildcard=STATEMENT_FILE_WILD_CARD,
                defaultFile=DEFAULT_STATEMENT_FILE_NAME,
                style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        path = get_save_path_from_dialog(dlg, STATEMENT_FILE_EXTENSION)

        if path is None:
            return
        self.backend.GenerateStatement(path, startDate, endDate)

    def OnViewHistory(self, evt):
        self.history_viewer.Show(True)


