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
import wx.lib.inspection
import os
import sys
import traceback

from .dialogs import ExceptionDialog
from ..models import Application as AppBackend
from ..models import UserError
from ..utils import ensure_dir_exists
from .MainFrame import MainFrame

APP_NAME = 'SalesMan'
LAST_SESSION_INFO_FILE='.last'

def guiExceptionHandler(type, value, tb):
    if type == UserError:
        e_msg = value.message
        e_reason = value.reason
    else:
        e_msg = 'An Unexpected error has occured'
        e_reason = str(value)

    e_details = ''.join(traceback.format_exception(type,value,tb))
    dlg = ExceptionDialog(None,e_msg,e_reason,e_details)
    dlg.ShowModal()

class Application(wx.App):
    def OnInit(self):
        self.SetAppName(APP_NAME)
        sys.excepthook = guiExceptionHandler
        self.dataDir = wx.StandardPaths.Get().GetUserLocalDataDir()
        ensure_dir_exists(self.dataDir)
        self._setupBackendAndMainFrame()
        self._tryToOpenLastSession()
        return True

    def OnExit(self):
        self._saveCurrentSession()

    def _saveCurrentSession(self):
        dbpath = self.backend.GetDBFilePath()
        infoFile=os.path.join(self.dataDir,LAST_SESSION_INFO_FILE)
        if dbpath is not None:
            try:
                with open(infoFile,'w') as fd:
                    fd.write(dbpath)
            except IOError:
                pass

    def _setupBackendAndMainFrame(self):
        self.backend=AppBackend()
        mainFrame = MainFrame(self.backend,None)
        self.backend.Initialize()
        mainFrame.Show(True)

    def _tryToOpenLastSession(self):
        try:
            self._openLastSession()
        except:
            pass

    def _openLastSession(self):
        infoFile = os.path.join(self.dataDir,LAST_SESSION_INFO_FILE)
        if os.path.isfile(infoFile):
            dbpath=open(infoFile,'r').read()
            if os.path.isfile(dbpath):
                self.backend.OpenDatabase(dbpath)

class ApplicationWithDebugger(Application):
    def __init__(self, redirect=True):
        super(ApplicationWithDebugger,self).__init__(redirect)
    def OnInit(self):
        Application.OnInit(self)
        wx.lib.inspection.InspectionTool().Show()
        return True

