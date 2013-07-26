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
from ..utils import ensure_dir_exists, pub
from .MainFrame import MainFrame
from ...plugintypes import IStatementFormatter, ITransactionFormatter
from ..constants import *
from ...basedir import BASEDIR

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

class Application(wx.App):
    def OnInit(self):
        self.SetAppName(APP_NAME)
        sys.excepthook = guiExceptionHandler
        self.sp = wx.StandardPaths.Get()

        self.pluginDirs = [
                self.sp.GetPluginsDir(),
                os.path.join(self.sp.GetUserDataDir(),PLUGINS_DIR_NAME),
                os.path.join(BASEDIR,PLUGINS_DIR_NAME)]

        self.userConfigDir = self.sp.GetUserConfigDir()
        self.globalConfigDir = self.sp.GetConfigDir()

        self.configFiles = [
                os.path.join(d,APP_CONFIG_FILE) for d in
                (self.userConfigDir, self.globalConfigDir)]

        self._readConfig()
        self._loadPlugins()
        self._setupBackendAndMainFrame()
        self._tryToOpenLastSession()
        return True

    def OnExit(self):
        self._addCurrentSessionToConfig()
        self.saveUserConfig()

    def setPluginPreference(self, category, name):
        previous = self.getPluginNameFromConfig(category)
        self.setConfig(PLUGINS_SECTION_NAME, category, name)
        try:
            pub.sendMessage(category,
                formatterPlugin=self.getPluginFromConfig(category))
        except:
            #Rollback
            self.setConfig(PLUGINS_SECTION_NAME, category, previous)
            raise


    def getPluginNameFromConfig(self, category):
        name = self.getConfig(PLUGINS_SECTION_NAME, category)
        if not name:
            self.setConfig( PLUGINS_SECTION_NAME, category,
                            DEFAULT_PLUGIN_NAME)
            name = DEFAULT_PLUGIN_NAME
        return name

    def getPluginFromConfig(self, category):
        name = self.getPluginNameFromConfig(category)
        manager = PluginManagerSingleton.get()
        plugin = manager.getPluginByName(name, category)
        if plugin is None:
            raise UserError("Cannot find plugin of category : "
                            "{} , name : {}".format(category, name))
        return plugin

    def _loadPlugins(self):
        manager = PluginManagerSingleton.get()
        manager.setPluginPlaces(self.pluginDirs)
        manager.setCategoriesFilter({STATEMENT_FORMATTER:IStatementFormatter,
                                    TRANSACTION_FORMATTER:ITransactionFormatter})
        manager.collectPlugins()

    def _readConfig(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(self.configFiles)

    def _addCurrentSessionToConfig(self):
        dbpath = self.backend.GetDBFilePath()
        if dbpath:
            self.setConfig(LAST_SESSION_SECTION_NAME, PATH, dbpath)

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
        if (self.config.has_section(section) and
            self.config.has_option(section, name)):
            return self.config.get(section, name)

    def setConfig(self, section, name, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, name, value)


class ApplicationWithDebugger(Application):
    def __init__(self, redirect=True):
        super(ApplicationWithDebugger,self).__init__(redirect)
    def OnInit(self):
        Application.OnInit(self)
        wx.lib.inspection.InspectionTool().Show()
        return True

