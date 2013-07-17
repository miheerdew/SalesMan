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
