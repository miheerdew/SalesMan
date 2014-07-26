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
from wx.lib.mixins import listctrl as listmix

class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self,*args, **kargs):
        wx.ListCtrl.__init__(self, *args, **kargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class TextEditMixin(listmix.TextEditMixin):
    def __init__(self, editable_columns=None, enabled=False):
        self.__enabled = enabled
        self.__editable_columns = set(editable_columns)
        listmix.TextEditMixin.__init__(self)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.__OnLabelEditBegin)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.__OnLabelEditEnd)

    def __OnLabelEditBegin(self, evt):
        if not (self.__enabled and evt.m_col in self.__editable_columns):
            evt.Veto()
            return
        evt.Skip()

    def __OnLabelEditEnd(self, evt):
        if not self.__enabled:
            evt.Veto()
            return
        self.OnItemEdit(evt.m_itemIndex, evt.m_col, evt.m_item.GetText())
        evt.Skip()

    def OnItemEdit(self, row, col, txt):
        pass

    def EnableEditing(self, enable):
        self.__enabled = enable
        if not enable:
            #Close the editor if it is shown
            self.CloseEditor()
