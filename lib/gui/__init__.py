import wx
from ..models import Application as AppBackend
from .mainframe import MainFrame

class Application(wx.App):
    def OnInit(self):
        backend=AppBackend()
        mainFrame = MainFrame(backend,None)
        backend.Initialize()
        mainFrame.Show(True)
        return True

class DebugApp(Application):
    def OnInit(self):
        import wx.lib.inspection
        Application.OnInit(self)
        wx.lib.inspection.InspectionTool().Show()
        return True

