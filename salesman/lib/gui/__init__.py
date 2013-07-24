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
import ConfigParser
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

from .dialogs import ExceptionDialog
from ..models import Application as AppBackend
from ..models import UserError
from ..utils import ensure_dir_exists
from .MainFrame import MainFrame
from ...plugintypes import IStatementFormatter
from ..constants import *


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
    dlg.Destroy()

def safelyGet(config, section, name):
    if config.has_section(section) and config.has_option(section, name):
        return config.get(section, name)
    return None

def easilySet(config, section, name, value):
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, name, value)

class Application(wx.App):
    def OnInit(self):
        self.SetAppName(APP_NAME)
        sys.excepthook = guiExceptionHandler
        self.sp = wx.StandardPaths.Get()
        self.pluginDirs = [self.sp.GetPluginsDir(),
                os.path.join(self.sp.GetUserDataDir(),PLUGINS_DIR_NAME)]
        self.configFiles = [
                    os.path.join(d,APP_CONFIG_FILE) for d in
                        (self.sp.GetConfigDir(), self.sp.GetUserConfigDir())]
        self.userConfigDir = self.sp.GetUserConfigDir()
        self._readConfig()
        self._loadPlugins()
        self._setupBackendAndMainFrame()
        self._tryToOpenLastSession()
        return True

    def OnExit(self):
        self._addCurrentSessionToConfig()
        self.saveUserConfig()

    def getStatementFormatterPluginName(self):
        name = self.getConfig(STATEMENT_FORMATTER_SECTION_NAME, NAME)
        if not name:
            self.setConfig( STATEMENT_FORMATTER_SECTION_NAME, NAME,
                            DEFAULT_STATEMENT_FORMATTER_NAME)
            name = DEFAULT_STATEMENT_FORMATTER_NAME
        return name

    def getStatementFormatterPlugin(self):
        name = self.getStatementFormatterPluginName()
        manager = PluginManagerSingleton.get()
        plugin = manager.getPluginByName(name, STATEMENT_FORMATTER)
        if plugin is None:
            raise UserError("Cannot find plugin with name {}".format(name))
        return plugin


    def _loadPlugins(self):
        manager = PluginManagerSingleton.get()
        manager.setPluginPlaces(self.pluginDirs)
        manager.setCategoriesFilter({STATEMENT_FORMATTER:IStatementFormatter})
        manager.collectPlugins()

    def _readConfig(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(self.configFiles)

    def _addCurrentSessionToConfig(self):
        dbpath = self.backend.GetDBFilePath()
        if dbpath:
            easilySet(self.config, LAST_SESSION_SECTION_NAME, PATH, dbpath)

    def saveUserConfig(self):
        ensure_dir_exists(self.userConfigDir)
        with open(os.path.join(self.userConfigDir,APP_CONFIG_FILE),'w') as fd:
            self.config.write(fd)

    def _setupBackendAndMainFrame(self):
        self.backend=AppBackend()
        mainFrame = MainFrame(self.backend,None)
        self.backend.Initialize()
        mainFrame.Show(True)
        mainFrame.Maximize() #For working with pyinstaller on windows

    def _tryToOpenLastSession(self):
        try:
            self._openLastSession()
        except:
            pass

    def _openLastSession(self):
            dbpath=self.getConfig(LAST_SESSION_SECTION_NAME, PATH)
            if dbpath and os.path.isfile(dbpath):
                self.backend.OpenDatabase(dbpath)

    def getConfig(self, section, name):
        return safelyGet(self.config, section, name)

    def setConfig(self, section, name, value):
        return easilySet(self.config, section, name, value)

class ApplicationWithDebugger(Application):
    def __init__(self, redirect=True):
        super(ApplicationWithDebugger,self).__init__(redirect)
    def OnInit(self):
        Application.OnInit(self)
        wx.lib.inspection.InspectionTool().Show()
        return True

