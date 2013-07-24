# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Oct  8 2012)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.html

###########################################################################
## Class StatementCreationWizard
###########################################################################

class StatementCreationWizard ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Statement Creation Wizard", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.Size( 500,500 ), wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.html = wx.html.HtmlWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
		bSizer1.Add( self.html, 1, wx.ALL|wx.EXPAND, 5 )
		
		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Set Dates" ), wx.VERTICAL )
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Start Date", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.m_staticText1.Wrap( -1 )
		bSizer2.Add( self.m_staticText1, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.startDateCtrl = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
		bSizer2.Add( self.startDateCtrl, 1, wx.ALL, 5 )
		
		
		sbSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )
		
		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"End Date", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		bSizer21.Add( self.m_staticText11, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.endDateCtrl = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
		bSizer21.Add( self.endDateCtrl, 1, wx.ALL, 5 )
		
		
		sbSizer1.Add( bSizer21, 0, wx.EXPAND, 5 )
		
		
		bSizer1.Add( sbSizer1, 0, wx.ALL|wx.EXPAND, 5 )
		
		sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Save file as" ), wx.HORIZONTAL )
		
		self.pathCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer4.Add( self.pathCtrl, 1, wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer4.Add( self.m_button1, 0, wx.ALL, 5 )
		
		
		bSizer1.Add( sbSizer4, 0, wx.ALL|wx.EXPAND, 5 )
		
		m_sdbSizer2 = wx.StdDialogButtonSizer()
		self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
		self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
		m_sdbSizer2.Realize();
		
		bSizer1.Add( m_sdbSizer2, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		bSizer1.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnPathButtonClick )
		self.m_sdbSizer2OK.Bind( wx.EVT_BUTTON, self.OnOKButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnPathButtonClick( self, event ):
		event.Skip()
	
	def OnOKButtonClick( self, event ):
		event.Skip()
	

###########################################################################
## Class SettingsDialog
###########################################################################

class SettingsDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Settings Dialog", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.Size( 500,500 ), wx.DefaultSize )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		self.html = wx.html.HtmlWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
		bSizer4.Add( self.html, 1, wx.ALL|wx.EXPAND, 5 )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Statement Formatter Plugin" ), wx.VERTICAL )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"select plugin ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		bSizer5.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		statementFormatterChoiceChoices = []
		self.statementFormatterChoice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, statementFormatterChoiceChoices, 0 )
		self.statementFormatterChoice.SetSelection( 0 )
		self.statementFormatterChoice.SetMinSize( wx.Size( 250,-1 ) )
		
		bSizer5.Add( self.statementFormatterChoice, 1, wx.ALL, 5 )
		
		
		sbSizer3.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		
		bSizer4.Add( sbSizer3, 0, wx.ALL|wx.EXPAND, 10 )
		
		m_sdbSizer2 = wx.StdDialogButtonSizer()
		self.m_sdbSizer2Save = wx.Button( self, wx.ID_SAVE )
		m_sdbSizer2.AddButton( self.m_sdbSizer2Save )
		self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
		m_sdbSizer2.Realize();
		
		bSizer4.Add( m_sdbSizer2, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer4 )
		self.Layout()
		bSizer4.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer2Save.Bind( wx.EVT_BUTTON, self.OnSaveButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnSaveButtonClick( self, event ):
		event.Skip()
	

