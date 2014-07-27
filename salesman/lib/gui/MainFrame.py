#Copyright (C) 2013  Miheer Dewaskar <miheerdew@gmail.com>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>

import wx
from wx.lib.wordwrap import wordwrap

import os
from functools import partial
from .dialogs import StatementCreationWizard, SettingsDialog
from ..utils import pub, silent_remove, get_save_path_from_dialog
from ..topics import *
from ..constants import *
from .HistoryViewer import HistoryViewer
from .TransactionMaker import TransactionMaker
from . import images
from yapsy.PluginManager import PluginManagerSingleton
from ..models import UserError
from ... import about
from .events import EVT_TRANSACTION_EDIT

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
        self.statusbar = self.CreateStatusBar()
        self.history_viewer = HistoryViewer(backend, self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.transaction_maker = TransactionMaker(backend, self)
        pub.subscribe(self.OnAddTransactionToggle, ADD_TRANSACTION)
        pub.subscribe(self.OnTransactionAdded, TRANSACTION_ADDED)
        sizer.Add(self.transaction_maker,1,wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.SetIcons(images.GetIconBundleFromImage(images.getAppIconImage()))

        self.Bind(EVT_TRANSACTION_EDIT, self.OnEditTransaction)

    def OnEditTransaction(self, evt):
        self.transaction_maker.FromTransaction(evt.transaction)

    def OnTransactionAdded(self, id):
        self.statusbar.PushStatusText('New transaction added with '
                'transaction id {}'.format(id))
    def OnAddTransactionToggle(self,enabled):
        self.transaction_maker.Toggle(enabled)

    def menuData(self):
        return (('&File',
                    (
                        ('New Database', wx.ID_NEW,  self.OnCreateDatabase, OPEN_DATABSE),
                        ('Open Database',wx.ID_OPEN, self.OnOpenDatabase, OPEN_DATABSE),
                        ('Exit', wx.ID_EXIT, self.OnExit)
                    )
                ),
                ('&Database',
                    (
                        ('Initialize Database\tCTRL+I', wx.NewId(), self.OnInitDatabase, INIT_DATABASE),
                        ('Generate Statement\tCTRL+S', wx.NewId(), self.OnGenerateStatement ,GENERATE_STATEMENT),
                        (),
                        ('View History \tCTRL+H', wx.NewId(), self.OnViewHistory, GET_HISTORY)
                    )
                ),
                ('Preferences',
                    (
                        ('Settings\tCTRL+T', wx.NewId(), self.OnSettings ),
                    )
                ),
                ('Help',
                    (
                        ('About',wx.ID_ABOUT,self.OnAbout),
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

    def OnAbout(self, evt):
        info = wx.AboutDialogInfo()
        for a in ('Name','Version','Copyright','WebSite','Developers'):
            setattr(info,a,getattr(about,a))

        for b,w  in (('License',700),('Description',500)):
            setattr(info,b,wordwrap(getattr(about,b),w,
                    wx.ClientDC(self)))
        wx.AboutBox(info)

    def OnExit(self, evt):
        self.Close()

    def OnSettings(self, evt):
        dlg = SettingsDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnOpenDatabase(self, evt):
        dlg = wx.FileDialog(self, message="Open Database File ..",
                wildcard=DB_FILE_WILD_CARD,
                style= wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.OpenDatabase(path)

        dlg.Destroy()

    def OpenDatabase(self, path):
            self.backend.OpenDatabase(path)
            self.statusbar.PushStatusText('Opened database file "{}"'\
                    .format(path))
            self.SetTitle('{} :{}'.format(MAIN_FRAME_TITLE,path))

    
    def OnCreateDatabase(self, evt):
        dlg = wx.FileDialog(self, message="Create Database file..",
                wildcard=DB_FILE_WILD_CARD,
                defaultFile=DEFAULT_DB_FILE_NAME,
                style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        path = get_save_path_from_dialog(dlg, DB_FILE_EXTENSION)

        dlg.Destroy()

        if path is None:
            return

        silent_remove(path)
        self.backend.OpenDatabase(path)

        self.statusbar.PushStatusText('Created new database file "{}"'\
                .format(path))


    def OnInitDatabase(self, evt):
        dlg = wx.FileDialog(self, message="Open file to init database ..",
                wildcard=INIT_FILE_WILD_CARD,
                style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            plugin = wx.GetApp().getPluginFromConfig(INIT_PARSER)
            parser = partial(plugin.plugin_object.parse,CSV)
            self.backend.InitDatabase(dlg.GetPath(),parser=parser)
            self.statusbar.PushStatusText('Initialized database from file "{}"'\
                    .format(dlg.GetPath()))

        dlg.Destroy()


    def OnGenerateStatement(self, evt):
        dlg = StatementCreationWizard(self)
        if dlg.ShowModal() == wx.ID_OK:

            startDate, endDate = dlg.GetDates()
            path = dlg.GetPath()
            plugin = wx.GetApp().getPluginFromConfig(STATEMENT_FORMATTER)
            self.backend.GenerateStatement(path, startDate, endDate,
                plugin.plugin_object.format, changes_only=dlg.WantChangesOnly())
            self.statusbar.PushStatusText('Generated statement file "{}"'
                                            .format(path))

        dlg.Destroy()

    def OnViewHistory(self, evt):
        self.history_viewer.Show(True)
        self.history_viewer.Raise()


