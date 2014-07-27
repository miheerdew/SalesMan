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
from .common import ListCtrl
from .events import PostEditItemEvent, PostEditQtyEvent
from wx.lib.mixins import listctrl as listmix


class TextEditMixin(listmix.TextEditMixin):
    def __init__(self):
        self.__item_columns = set(range(1,len(self.headers)-1))
        self.__qty_editing_enabled = False
        self.__item_editing_enabled = False
        listmix.TextEditMixin.__init__(self)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.__OnLabelEditBegin)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.__OnLabelEditEnd)

    def __is_enabled(self, col):
        if col in self.__item_columns:
            return self.__item_editing_enabled
        else:
            return self.__qty_editing_enabled

    def __OnLabelEditBegin(self, evt):
        if self.__is_enabled(evt.m_col):
            return evt.Skip()
        else:
            return evt.Veto()

    def __OnLabelEditEnd(self, evt):
        if not self.__is_enabled(evt.m_col):
            evt.Veto()
            return
        if evt.m_col in self.__item_columns:
            self.OnItemEdit(evt.m_itemIndex, evt.m_col, evt.m_item.GetText())
        else:
            self.OnQtyEdit(evt.m_itemIndex, evt.m_col, evt.m_item.GetText())
        evt.Skip()

    def OnItemEdit(self, row, col, txt):
        pass

    def OnQtyEdit(self, row, col, txt):
        pass

    def EnableItemEditing(self, enable):
        self.__item_editing_enabled = enable
        if not enable and self.curCol in self.__item_columns:
            #Close the editor if it is shown
            self.CloseEditor()

    def EnableQtyEditing(self, enable):
        self.__qty_editing_enabled = enable
        if not enable and self.curCol not in self.__item_columns:
            self.CloseEditor()

class ItemViewer(ListCtrl, TextEditMixin):
    def __init__(self, parent, **kargs):
        self.items = []
        self.headers = [('Id',50),('Name',50),('Category',100),('Price',75),('Qty',50)]
        self.attrs = ['id','name','category','price','qty']

        kargs['style'] = wx.LC_REPORT|wx.LC_VIRTUAL|kargs.get('style',0)
        ListCtrl.__init__(self, parent, **kargs)
        TextEditMixin.__init__(self)

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
        self.items = list(items) # to allow assignment in SetVirtualData()
        self.RefreshItems(0,count-1)

    def OnGetItemText(self, row, col):
        return getattr(self.items[row],self.attrs[col])

    def SetVirtualData(self, row, col, text):
        item = self.items[row]
        val = text
        if col == 3: #price
            val = float(val)
        if col == 4: #Qty
            val = int(val)
        setattr(item, self.attrs[col], val)
        if col == 4: #Qty
            PostEditQtyEvent(self, item.id, item.qty)
        else:
            PostEditItemEvent(self, item)
