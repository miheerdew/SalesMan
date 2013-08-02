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
from .events import EVT_TRANSACTION_SELECTED, EVT_TRANSACTION_UNDO
from ..utils import pub
from ..topics import TRANSACTION_CHANGED, REDO
from . import autogen as auto

class HistoryViewer(auto.HistoryViewer):
    def __init__(self, backend, parent):
        auto.HistoryViewer.__init__(self, parent)
        self.backend = backend
        self._createToolbar()
        self._makeBindings()

    def _createToolbar(self):
        items = [(wx.ID_REDO, wx.ART_REDO,'Redo',
                'Redo the last set of transaction undone',
                None)]
        self.toolbar = self.CreateToolBar()
        for i in items:
            self.toolbar.AddLabelTool(id=i[0],
                                    bitmap=wx.ArtProvider.GetBitmap(i[1]),
                                    label=i[2],
                                    shortHelp = i[3],
                        longHelp = i[4] if i[4] is not None else i[3]
                                    )
        self.toolbar.Realize()

    def _makeBindings(self):

        self.Bind(EVT_TRANSACTION_SELECTED, self.OnTransactionSelect,
                    self.transaction_viewer)
        self.Bind(EVT_TRANSACTION_UNDO, self.OnTransactionUndo,
                    self.transaction_viewer)

        pub.subscribe(self.OnTransactionsChange, TRANSACTION_CHANGED)
        pub.subscribe(self.OnRedoToggled, REDO)
        self.Bind(wx.EVT_CLOSE, self.OnWindowClose)
        self.Bind(wx.EVT_TOOL, self.OnRedo, id=wx.ID_REDO)

    def OnRedoToggled(self, enabled):
        self.toolbar.EnableTool(wx.ID_REDO, enabled)

    def OnRedo(self, evt):
        self.backend.Redo()

    def OnWindowClose(self, evt):
        self.Show(False)

    def OnTransactionsChange(self, transactions):
        self.transaction_viewer.UpdateDisplay(transactions)

    def OnTransactionUndo(self, event):
        transaction = event.transaction
        self.backend.Undo(transaction)

    def OnTransactionSelect(self, evt):
        transaction = evt.transaction
        self.item_viewer.UpdateDisplay(self.backend.GetHistory(transaction.id))
        self.transaction_display.UpdateDisplay(transaction)
