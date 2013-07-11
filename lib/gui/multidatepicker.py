import wx
from textwrap import fill
from ..utils import wxdate2pydate

class MultiDatePickerDialog(wx.Dialog):
    def __init__(self, parent, title, labels):
        wx.Dialog.__init__(self, parent)
        self.labels = labels
        self.title = fill(title,25)
        self.CreateAndPlaceControls()

    def CreateAndPlaceControls(self):
        parent = self
        self.datepickers = []
        vbox = wx.BoxSizer(wx.VERTICAL)
        titleText=wx.StaticText(parent, label=self.title)
        font = wx.Font(14, wx.NORMAL, wx.NORMAL, wx.NORMAL)
        titleText.SetFont(font)
        titleText.SetBackgroundColour(wx.WHITE)

        vbox.Add(titleText, 1, wx.EXPAND, 5)
        vbox.Add((10,10),1,wx.EXPAND)

        gridsizer = wx.GridSizer(rows=len(self.labels), cols=2, hgap=5, vgap=10)
        for label in self.labels:
            gridsizer.Add(wx.StaticText(parent, label=label), 1, wx.EXPAND)
            dpc = wx.DatePickerCtrl(parent,style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
            self.datepickers.append(dpc)
            gridsizer.Add(dpc, 1, wx.EXPAND|wx.CENTER)
        vbox.Add(gridsizer, 0, wx.EXPAND, 5)
        vbox.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL), 0, wx.ALIGN_RIGHT, 5)
        self.SetSizerAndFit(vbox)

    def GetDates(self):
        return (wxdate2pydate(dpc.GetValue()) for dpc in self.datepickers)

