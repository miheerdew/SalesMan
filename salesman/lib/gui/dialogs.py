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


from . import autogen as auto
import wx
import os
from ..utils import wxdate_to_pydate, get_save_path_from_dialog
from ..models import UserError
from ..constants import *
from yapsy.PluginManager import PluginManagerSingleton

class SettingsDialog(auto.SettingsDialog):
    def __init__(self, parent):
        super(SettingsDialog,self).__init__(parent)

        pluginPaths = wx.GetApp().GetPluginPlaces()

        self.pluginsHtml.SetPage(
        """
        <html>
        <body><h3 align="center">Select Plugins</h3>
        You can add customized plugins by placing them in the following
        directories <ul><li>{}<li>{}</ul>
        <body>
        </html>
        """.format(*pluginPaths))

        self.pluginCtrlMap = {
                        STATEMENT_WRITER:self.statementWriter,
                        REGISTRY_WRITER:self.registryWriter,
                        TRANSACTION_FORMATTER:self.transactionFormatter,
                        INIT_PARSER:self.initParser
                        }

        self.app = wx.GetApp()
        manager = PluginManagerSingleton.get()

        for category, ctrl in self.pluginCtrlMap.items():
            currentSel = self.app.getPluginNameFromConfig(category)
            choices = [ p.name for p in
                    manager.getPluginsOfCategory(category) ]
            ctrl.SetItems(choices)
            try:
                i = choices.index(currentSel)
                ctrl.SetSelection(i)
            except ValueError:
                pass

    def OnSaveButtonClick(self, evt):
        for category, ctrl in self.pluginCtrlMap.items():
            sel = ctrl.GetSelection()
            if sel == wx.NOT_FOUND:
                dlg = wx.MessageDialog(self,
                    "Please select plugin of category {}".format(category),
                    "Incomplete Entry", style=wx.ICON_ERROR|wx.OK)
                dlg.ShowModal()
                return
            pluginName = ctrl.GetString(sel)
            self.app.setPluginPreference(category, pluginName)
        self.app.saveUserConfig()
        self.EndModal(wx.ID_SAVE)

STATEMENT, REGISTRY = 0, 1

class StatementCreationWizard(auto.StatementCreationWizard):
    MESSAGE = """
    <html><body>
    <h3 align='center'>This wizard will guide you to generate your statement</h3>
    <p>Please select the dates between which you want to generate the
    statement.
    All tansactions that happened on and after <u>Start Date</u>
    and on and before <u>End Date</u> will be taken into account.
    Also fill in the file you want the statement to be saved as in the
    entry box below, you can click on the button besides it to open the
    file save dialog.
    </html></body>
    """

    #Plugin category
    PLUGIN_CAT=[STATEMENT_WRITER, REGISTRY_WRITER]
    STRINGS = ["Statement", "Register"]
    DEFAULT_FNAME = [ DEFAULT_STATEMENT_FILE_NAME, DEFAULT_REGISTRY_FILE_NAME ]

    def __init__(self, parent):
        super(StatementCreationWizard,self).__init__(parent)
        self.html.SetPage(self.MESSAGE)
        self.output_type = STATEMENT

    def OnPathButtonClick( self, event ):
        t = self.output_type
        ext_info = wx.GetApp().getPluginFromConfig(self.PLUGIN_CAT[t]).plugin_object.ext_info

        dlg = wx.FileDialog(self, message="Save {} File..".format(self.STRINGS[t]),
                wildcard=simple_wild_card_from_extension(*ext_info),
                defaultFile=self.DEFAULT_FNAME[t],
                style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        path = get_save_path_from_dialog(dlg, ext_info[0])
        if path is not None:
            self.pathCtrl.SetValue(path)

    def OnOKButtonClick(self, evt):
        try:
            self.startDate = \
                    wxdate_to_pydate(self.startDateCtrl.GetValue())

            self.endDate = \
                    wxdate_to_pydate(self.endDateCtrl.GetValue())

            self.path = self.pathCtrl.GetValue()

            if self.startDate is None:
                raise UserError('Cannot process statement form',
                                'Invalid Start Date')
            if self.endDate is None:
                raise UserError('Cannot process statement form',
                                'Invalid End Date')
        except:
            raise
        else:
            evt.Skip()

    def GetOutputType(self):
        return self.output_type

    def OnGenerateChoiceChanged(self, evt):
        self.output_type = evt.GetInt()

    def GetDates(self):
        return self.startDate, self.endDate

    def GetPath(self):
        return self.path

    def WantChangesOnly(self):
        return self.changesCheck.IsChecked()

class ExceptionDialog(wx.Dialog):
    def __init__(self, parent, message='', reason='', fulldetails='',
                                title='Error Occured'):
        super(ExceptionDialog,self).__init__(parent, title=title)
        panel = ExceptionPanel(self, message, reason, fulldetails)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizerAndFit(sizer)

class ExceptionPanel(wx.Panel):
    def __init__(self, parent, message, reason, fulldetails):
        self.message = message
        self.reason = reason
        self.fulldetails = fulldetails
        wx.Panel.__init__(self, parent)

        mainBox = self._createMainBox(message, reason)

        cp = wx.CollapsiblePane(self, label='Details')
        self._createDetailsBox(cp.GetPane(), fulldetails)

        buttonBox = self._createButtonBox()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(mainBox, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(cp, 0, wx.EXPAND|wx.ALL,5)
        sizer.Add(buttonBox, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        self.SetSizer(sizer)

    def _createButtonBox(self):
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        okBtn = wx.Button(self, id=wx.ID_OK)
        copyBtn = wx.Button(self, label='Copy', id=wx.ID_COPY)
        copyBtn.SetToolTipString('Copy the error details to the clipboard')
        self.Bind(wx.EVT_BUTTON, self.OnCopyToClipBoard, copyBtn)
        btnBox.Add(copyBtn, 0)
        btnBox.Add(okBtn, 0)
        return btnBox

    def _createDetailsBox(self, pane, fulldetails):
        sizer = wx.BoxSizer(wx.VERTICAL)
        txtBox = wx.TextCtrl(pane, value=fulldetails,
                            style=wx.TE_MULTILINE|wx.TE_READONLY, size=(-1,100))
        sizer.Add(txtBox, 1,wx.EXPAND|wx.ALL,5)
        pane.SetSizer(sizer)

    def _createMainBox(self, message, reason):
        box = wx.BoxSizer(wx.VERTICAL)
        labelFont = wx.Font(12,
                        family=wx.FONTFAMILY_SWISS,
                        style=wx.FONTSTYLE_NORMAL,
                        weight=wx.FONTWEIGHT_BOLD,
                        underline=True)
        valueFont = wx.Font(12,
                        family=wx.FONTFAMILY_ROMAN,
                        style=wx.FONTSTYLE_NORMAL,
                        weight=wx.FONTWEIGHT_NORMAL,
                        underline=False)

        max_msg_width=500

        fbs = wx.FlexGridSizer(cols=2, vgap=10, hgap=10)
        for label,value in [('Error :',message),('Reason :',reason)]:
            labelCtrl = wx.StaticText(self, label=label)
            valueCtrl = wx.StaticText(self, label=value)
            valueCtrl.Wrap(max_msg_width)

            labelCtrl.SetFont(labelFont)
            valueCtrl.SetFont(valueFont)

            fbs.Add(labelCtrl, 0, wx.ALIGN_TOP|wx.ALIGN_LEFT)
            fbs.Add(valueCtrl, 1, wx.EXPAND)

        for i in [0,1]:
            fbs.AddGrowableRow(i,1)
        for i in [1]:
            fbs.AddGrowableCol(i,1)
        return fbs

    def OnCopyToClipBoard(self, evt):
        msg = """
Error : {}
Reason : {}
Details :{}
            """.format(self.message, self.reason, self.fulldetails)
        clipdata = wx.TextDataObject()
        clipdata.SetText(msg)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()
