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


from wx.lib.newevent import NewCommandEvent
import wx

TransactionSelectedEvent, EVT_TRANSACTION_SELECTED = NewCommandEvent()

def PostTransactionSelectedEvent(target,  transaction):
    evt = TransactionSelectedEvent(target.GetId(),transaction=transaction)
    wx.PostEvent(target, evt)


TransactionUndoEvent, EVT_TRANSACTION_UNDO = NewCommandEvent()

def PostTransactionUndoEvent(target,  transaction):
    evt = TransactionUndoEvent(target.GetId(),transaction=transaction)
    wx.PostEvent(target, evt)


ItemSelectedEvent, EVT_ITEM_SELECTED = NewCommandEvent()

def PostItemSelectedEvent(target,  item, qty=0, discount=0):
    evt = ItemSelectedEvent(target.GetId(),item=item, qty=qty, discount=discount)
    wx.PostEvent(target, evt)

TransactionDeleteEvent, EVT_TRANSACTION_DELETE = NewCommandEvent()

def PostTransactionDeleteEvent(target,  transaction):
    evt = TransactionDeleteEvent(target.GetId(),transaction=transaction)
    wx.PostEvent(target, evt)
