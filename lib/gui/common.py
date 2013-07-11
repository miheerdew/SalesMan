import wx
from wx.lib.mixins import listctrl as listmix

class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self,*args, **kargs):
        wx.ListCtrl.__init__(self, *args, **kargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


