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

