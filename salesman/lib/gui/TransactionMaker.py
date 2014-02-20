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
from wx.lib import masked
from ..models import TransactionMaker as TransactionMakerModel
from ..topics import TRANSACTION_MAKER, TYPE_CHANGED, UNITS_CHANGED,\
                        TRANSACTION_CHANGED, MAKE_TRANSACTION
from ..utils import pub, wxdate_to_pydate
from ..core import ADDITION, SALE, GIFT, TRANSFER, unit_total
from .common import ListCtrl
from .auto_complete_controls import \
                            TextCtrlAutoComplete as TextCtrlAC,\
                            NameCtrlWithItemAutoComplete as NameCtrlAC
from .events import EVT_ITEM_SELECTED, PostItemSelectedEvent
from . import images
from ..utils import standardizeString

TYPE_LIST = ADDITION, SALE, GIFT, TRANSFER
DEFAULT_TYPE = SALE

class TransactionMaker(wx.Panel):
    def __init__(self, backend, parent):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.backend = backend
        self.CreateControls()
        self.PlaceControls()
        self.SetTabOrder()
        pub.subscribe(self.OnUnitsChanged,UNITS_CHANGED)
        pub.subscribe(self.OnTransactionsChanged,TRANSACTION_CHANGED)
        pub.subscribe(self.OnMakeTransactionToggle,MAKE_TRANSACTION)
        self.model = TransactionMakerModel(backend)

    def SetTabOrder(self):
        order = self.TabOrderData()
        for i in range(len(order) - 1):
            order[i+1].MoveAfterInTabOrder(order[i])

    def Toggle(self, enable=True):
        for x in self.GetChildren():
            if x is not self.confirmBtn:
                    x.Enable(enable)
                    x.Refresh()

    def OnMakeTransactionToggle(self, enabled):
        self.confirmBtn.Enable(enabled)
        self.confirmBtn.Refresh()

    def ItemAutoFill(self, item):
        #Automatically fill data from item
        self.nameCtrl.SetValueWithoutDropdown(item.name)
        self.categoryCtrl.SetValueWithoutDropdown(item.category)
        self.priceCtrl.SetValue(item.price)

    def OnItemSelectFromViewer(self, evt):
        self.ItemAutoFill(evt.item)
        self.qtyCtrl.SetValue(evt.qty)
        self.togglePercentageCheck(False)
        self.discountCtrl.SetValue(evt.discount)

    def PlacementData(self):
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.addBtn)
        hbox1.Add(self.removeBtn)

        hbox2=self.discount_box=wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.discountLabel,0,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        hbox2.Add(self.discountCtrl, 0,wx.ALIGN_LEFT|wx.LEFT,10)
        hbox2.Add(self.percentageCheck,0,wx.ALIGN_LEFT)

        return [(self.typeLabel,(0,0),(1,1),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL),
                (self.typeCtrl,(0,1),(1,1),wx.EXPAND),
                (self.dateLabel,(0,5),(1,1),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL),
                (self.dateCtrl, (0,6),(1,1)),
                (self.infoLabel, (1,0),(1,1),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL),
                (self.infoCtrl, (1,1), (2,4), wx.EXPAND),
                (self.nameLabel, (3,0),(1,3),wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL),
                (self.nameCtrl, (4,0), (1,3),wx.EXPAND),
                (self.categoryLabel, (3,3),(1,2),wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL),
                (self.categoryCtrl, (4,3),(1,2),wx.EXPAND),
                (self.priceLabel, (3,5),(1,1),wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL),
                (self.priceCtrl, (4,5), (1,1),wx.ALIGN_CENTER),
                (self.qtyLabel, (3,6),(1,1),wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL),
                (self.qtyCtrl, (4,6), (1,1),wx.ALIGN_CENTER),
                (hbox2, (5,4),(1,3),wx.ALIGN_RIGHT),
                (hbox1,(5,0),(1,1), wx.ALIGN_LEFT),
                (self.confirmBtn,(5,1),(1,1),wx.EXPAND),
                (self.resetBtn,(5,2),(1,1),wx.EXPAND),
                (self.unit_viewer, (6,0),(1,7),wx.EXPAND),
                ]

    def TabOrderData(self):
        return [self.typeCtrl, self.dateCtrl,self.infoCtrl,
                self.nameCtrl, self.categoryCtrl,
                self.priceCtrl,self.qtyCtrl, self.discountCtrl,
                self.addBtn, self.removeBtn, self.confirmBtn]

    def OnUnitsChanged(self, units, type):
        self.unit_viewer.DisplayUnits(units,type)

    def GetItems(self):
        return [[str(getattr(i,a)) for a in AC_ATTRS_NAMES] for i in self.backend.QueryItems()]

    def GetCategories(self):
        return self.backend.GetCategories()

    def OnTransactionsChanged(self,transactions):
        self.nameCtrl.UpdateDisplay()
        self.categoryCtrl.SetChoices(self.GetCategories())

    def PlaceControls(self):
        self.sizer = wx.GridBagSizer(vgap=10, hgap=10)
        self.sizer.AddMany(self.PlacementData())
        for i in range(1,5):
            self.sizer.AddGrowableCol(i)
        self.sizer.AddGrowableRow(6,10)
        self.sizer.AddGrowableRow(2,1)
        self.SetSizer(self.sizer)

    def OnAddItem(self, evt):
        self.addItem(remove=False)

    def OnRemoveItem(self, evt):
        self.addItem(remove=True)

    def addItem(self, remove=False):
        name = standardizeString(self.nameCtrl.GetValue())
        category = standardizeString(self.categoryCtrl.GetValue().strip())
        price = float(self.priceCtrl.GetValue())
        qty = 0
        if not remove:
            qty=int(self.qtyCtrl.GetValue())

        discount=0
        if self.typeCtrl.GetValue() == SALE:
            discount = self.discountCtrl.GetValue()
            if self.percentageCheck.GetValue():
                    discount = discount*price*qty/100

        self.model.AddItem(name,category,price,qty,discount)
        self.ClearItemEntryForm()
        self.nameCtrl.SetFocus()

    def ClearItemEntryForm(self):
        self.nameCtrl.SetValue('')
        self.categoryCtrl.SetValue('')
        self.priceCtrl.SetValue(0.0)
        self.qtyCtrl.SetValue(1)

    def ResetItemEntryForm(self):
        self.nameCtrl.SetValue('')
        self.categoryCtrl.SetValue('')
        self.priceCtrl.SetValue(0.0)
        self.qtyCtrl.SetValue(1)
        self.discountCtrl.SetValue(0.0)
        self.togglePercentageCheck(True)

    def OnConfirm(self, evt):
        date = wxdate_to_pydate(self.dateCtrl.GetValue())
        info = self.infoCtrl.GetValue()
        self.model.MakeTransaction(date, info)
        self.infoCtrl.SetValue('')
        self.ResetItemEntryForm()

    def CreateControls(self):
        self.typeLabel = wx.StaticText(self, label='Type')
        self.typeCtrl = wx.ComboBox(self,value=DEFAULT_TYPE, choices=TYPE_LIST,
                                    style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnTypeChanged, self.typeCtrl)

        self.dateLabel = wx.StaticText(self, label='Date')
        self.dateCtrl = wx.DatePickerCtrl(self, style=wx.DP_DROPDOWN
                                      | wx.DP_SHOWCENTURY, size=(200,-1))

        self.infoLabel = wx.StaticText(self, label='Info')
        self.infoCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        self.addBtn = wx.BitmapButton(self, bitmap=images.getPlusBitmap())
        self.Bind(wx.EVT_BUTTON, self.OnAddItem, self.addBtn)

        self.removeBtn = wx.BitmapButton(self, bitmap=images.getMinusBitmap())
        self.Bind(wx.EVT_BUTTON, self.OnRemoveItem, self.removeBtn)

        self.confirmBtn = wx.Button(self, label='Confirm')
        self.Bind(wx.EVT_BUTTON, self.OnConfirm, self.confirmBtn)

        self.resetBtn = wx.Button(self, label='Reset')
        self.Bind(wx.EVT_BUTTON, self.OnReset, self.resetBtn)

        self.nameLabel = wx.StaticText(self, label='Name')
        self.nameCtrl = NameCtrlAC(self, self.backend,
                        selectCallback=self.OnItemSelect)

        self.categoryLabel = wx.StaticText(self, label='Category')
        self.categoryCtrl = TextCtrlAC(self, choices=[''])

        self.priceLabel = wx.StaticText(self, label='Price')
        self.priceCtrl = masked.NumCtrl(self, value=0, fractionWidth=2,
                                        allowNegative=False)

        self.qtyLabel = wx.StaticText(self, label='Qty')
        self.qtyCtrl = masked.NumCtrl(self,value=1,
                                    allowNone=True,
                                    allowNegative=False)

        self.discountLabel = wx.StaticText(self, label='Discount')
        self.discountCtrl = masked.NumCtrl(self,value=0, fractionWidth=2,
                                            allowNegative=False)

        self.percentageCheck = wx.CheckBox(self, label="%", style=wx.ALIGN_RIGHT)
        self.percentageCheck.SetValue(1)
        self.Bind(wx.EVT_CHECKBOX, self.OnPercentageToggled, self.percentageCheck)

        self.unit_viewer = UnitViewer(self)
        self.Bind(EVT_ITEM_SELECTED, self.OnItemSelectFromViewer, self.unit_viewer)


    def togglePercentageCheck(self, enabled=True):
        if enabled:
            self.discountCtrl.SetMax(100)
            self.percentageCheck.SetLabel('%')
            self.percentageCheck.SetValue(1)
        else:
            self.discountCtrl.SetMax(None)
            self.percentageCheck.SetLabel('')
            self.percentageCheck.SetValue(0)

    def OnPercentageToggled(self, evt):
        self.togglePercentageCheck(evt.IsChecked())

    def OnDateChange(self, evt):
        self.date = wxdate_to_pydate(self.dateCtrl.GetValue())

    def OnTypeChanged(self, evt):
        type = evt.GetString()
        self.model.ChangeType(type)
        if type != SALE:
            self.sizer.Hide(self.discount_box)
        else:
            self.sizer.Show(self.discount_box)

    def OnReset(self, evt):
        self.model.Reset()
        self.ResetItemEntryForm()

    def OnItemSelect(self,item):
        self.ItemAutoFill(item)

class UnitViewer(ListCtrl):
    def __init__(self, parent):
        ListCtrl.__init__(self,parent, style=wx.LC_REPORT|wx.LC_VIRTUAL)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)
        self.headers = [('Sr.No',50),('Name',50),('Category',100),('Price',100),('Qty',50),('Discount',100),('Total',100)]
        self.discount_index = 5
        self.discount_shown = True
        self.attr = wx.ListItemAttr()
        self.attr.SetBackgroundColour("Yellow")

        self.count = 0

        self.grand_total=dict(discount=0, total=0, qty=0)

        for i,t in enumerate(self.headers):
            self.InsertColumn(i,t[0])
            self.SetColumnWidth(i,t[1])

        self.setResizeColumn(2)
        self.SetItemCount(2)

    def OnSelect(self, evt):
        i = evt.m_itemIndex
        if i < self.count:
            u = self.units[i]
            PostItemSelectedEvent(self,u.item, u.qty, u.discount)
        else:
            self.Select(i,on=False)
        evt.Skip()

    def DisplayUnits(self, units, type):
        di = self.discount_index
        if type == SALE and (not self.discount_shown):
            self.SetColumnWidth(di,self.headers[di][1])
            self.SetColumnWidth(di+1, self.headers[di+1][1])
            self.discount_shown = True
        elif type != SALE and self.discount_shown:
            self.SetColumnWidth(di,0)
            self.SetColumnWidth(di+1, self.headers[di+1][1]+self.headers[di][1])
            self.discount_shown = False

        self.units = units
        self.count = len(units)

        for a in ('discount','qty'):
            self.grand_total[a] = sum(getattr(u,a) for u in units)
        self.grand_total['total'] = sum(unit_total(u) for u in units)

        count=self.count+2
        self.SetItemCount(count)
        self.RefreshItems(0,count-1)

    def OnGetItemAttr(self, row):
        if row == self.count+1:
            return self.attr
        else:
            return None

    def OnGetItemText(self, row, col):
        if row >= self.count:
            if row == self.count:
                return '' #Seperator
            if col == 0:
                return ''
            elif col == 1:
                return 'Grand Total'
            elif col in (2,3):
                return ''
            elif col == 4:
                return '{:.2f}'.format(self.grand_total['qty'])
            elif col == 5:
                return '{:.2f}'.format(self.grand_total['discount'])
            elif col == 6:
                return '{:.2f}'.format(self.grand_total['total'])
            return

        unit = self.units[row]
        if col == 0:
            return (row+1)
        elif col <= 3:
            return getattr(unit.item,self.headers[col][0].lower())
        elif col == 4:
            return unit.qty
        elif col == 5:
                return '{:.2f}'.format(unit.discount)
        elif col == 6:
            return '{:.2f}'.format(unit_total(unit))

#class TransactionForm(wx.Panel):
