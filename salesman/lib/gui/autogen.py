# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.html
from .ItemViewer import ItemViewer
from .TransactionViewer import TransactionViewer
from .TransactionDisplay import TransactionDisplay

###########################################################################
## Class StatementCreationWizard
###########################################################################

class StatementCreationWizard ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Statement Creation Wizard", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHintsSz( wx.Size( 500,500 ), wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.html = wx.html.HtmlWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
		self.html.SetMinSize( wx.Size( 500,250 ) )

		bSizer1.Add( self.html, 1, wx.ALL|wx.EXPAND, 5 )

		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

		m_radioBox1Choices = [ u"Statement", u"Register" ]
		self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, u"What do you wish to generate?", wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
		self.m_radioBox1.SetSelection( 0 )
		bSizer9.Add( self.m_radioBox1, 1, wx.ALL, 5 )

		self.changesCheck = wx.CheckBox( self, wx.ID_ANY, u"Show changes only", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.changesCheck, 0, wx.ALIGN_BOTTOM|wx.ALL, 5 )


		bSizer1.Add( bSizer9, 0, wx.EXPAND, 5 )

		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Set Dates" ), wx.VERTICAL )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Start Date", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_staticText1.Wrap( -1 )
		bSizer2.Add( self.m_staticText1, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.startDateCtrl = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
		bSizer2.Add( self.startDateCtrl, 1, wx.ALL, 5 )


		sbSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )

		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"End Date", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
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
		self.m_radioBox1.Bind( wx.EVT_RADIOBOX, self.OnGenerateChoiceChanged )
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnPathButtonClick )
		self.m_sdbSizer2OK.Bind( wx.EVT_BUTTON, self.OnOKButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnGenerateChoiceChanged( self, event ):
		event.Skip()

	def OnPathButtonClick( self, event ):
		event.Skip()

	def OnOKButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class SettingsDialog
###########################################################################

class SettingsDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Settings", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHintsSz( wx.Size( 500,250 ), wx.DefaultSize )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_LEFT )
		self.m_panel1 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		gbSizer1 = wx.GridBagSizer( 10, 10 )
		gbSizer1.SetFlexibleDirection( wx.BOTH )
		gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.pluginsHtml = wx.html.HtmlWindow( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
		self.pluginsHtml.SetMinSize( wx.Size( 500,250 ) )

		gbSizer1.Add( self.pluginsHtml, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 10 )

		self.m_staticText5 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Statement Writer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		gbSizer1.Add( self.m_staticText5, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 10 )

		self.m_staticText6 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Transaction Formatter", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		gbSizer1.Add( self.m_staticText6, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 10 )

		transactionFormatterChoices = []
		self.transactionFormatter = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, transactionFormatterChoices, 0 )
		self.transactionFormatter.SetSelection( 0 )
		gbSizer1.Add( self.transactionFormatter, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		statementWriterChoices = []
		self.statementWriter = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, statementWriterChoices, 0 )
		self.statementWriter.SetSelection( 0 )
		gbSizer1.Add( self.statementWriter, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		self.m_staticText51 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Init File Parser", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText51.Wrap( -1 )
		gbSizer1.Add( self.m_staticText51, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 10 )

		initParserChoices = []
		self.initParser = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, initParserChoices, 0 )
		self.initParser.SetSelection( 0 )
		gbSizer1.Add( self.initParser, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		self.m_staticText511 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Registry Writer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText511.Wrap( -1 )
		gbSizer1.Add( self.m_staticText511, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		registryWriterChoices = []
		self.registryWriter = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, registryWriterChoices, 0 )
		self.registryWriter.SetSelection( 0 )
		gbSizer1.Add( self.registryWriter, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )


		gbSizer1.AddGrowableCol( 1 )
		gbSizer1.AddGrowableRow( 0 )

		self.m_panel1.SetSizer( gbSizer1 )
		self.m_panel1.Layout()
		gbSizer1.Fit( self.m_panel1 )
		self.m_notebook1.AddPage( self.m_panel1, u"Plugins", False )

		bSizer6.Add( self.m_notebook1, 1, wx.EXPAND |wx.ALL, 5 )

		m_sdbSizer3 = wx.StdDialogButtonSizer()
		self.m_sdbSizer3Save = wx.Button( self, wx.ID_SAVE )
		m_sdbSizer3.AddButton( self.m_sdbSizer3Save )
		self.m_sdbSizer3Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer3.AddButton( self.m_sdbSizer3Cancel )
		m_sdbSizer3.Realize();

		bSizer6.Add( m_sdbSizer3, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer6 )
		self.Layout()
		bSizer6.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_sdbSizer3Save.Bind( wx.EVT_BUTTON, self.OnSaveButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnSaveButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class HistoryViewer
###########################################################################

class HistoryViewer ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"History Viewer", pos = wx.DefaultPosition, size = wx.Size( 700,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_splitter1 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter1.SetSashGravity( 0.6 )
		self.m_splitter1.Bind( wx.EVT_IDLE, self.m_splitter1OnIdle )

		self.m_panel1 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel1, wx.ID_ANY, u"Item Viewer" ), wx.VERTICAL )

		self.item_viewer=ItemViewer(self.m_panel1)
		sbSizer1.Add( self.item_viewer, 1, wx.ALL|wx.EXPAND, 5 )


		self.m_panel1.SetSizer( sbSizer1 )
		self.m_panel1.Layout()
		sbSizer1.Fit( self.m_panel1 )
		self.m_panel2 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		self.m_splitter2 = wx.SplitterWindow( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter2.SetSashGravity( 0.3 )
		self.m_splitter2.Bind( wx.EVT_IDLE, self.m_splitter2OnIdle )

		self.m_panel4 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel4, wx.ID_ANY, u"Transaction Viewer" ), wx.VERTICAL )

		self.transaction_viewer = TransactionViewer(self.m_panel4)
		sbSizer3.Add( self.transaction_viewer, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer3.Add( sbSizer3, 1, wx.EXPAND, 5 )


		self.m_panel4.SetSizer( bSizer3 )
		self.m_panel4.Layout()
		bSizer3.Fit( self.m_panel4 )
		self.m_panel5 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.VERTICAL )

		sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel5, wx.ID_ANY, u"Transaction Display" ), wx.VERTICAL )

		self.transaction_display=TransactionDisplay(self.m_panel5)
		sbSizer4.Add( self.transaction_display, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer8.Add( sbSizer4, 1, wx.EXPAND, 5 )


		self.m_panel5.SetSizer( bSizer8 )
		self.m_panel5.Layout()
		bSizer8.Fit( self.m_panel5 )
		self.m_splitter2.SplitHorizontally( self.m_panel4, self.m_panel5, 0 )
		bSizer2.Add( self.m_splitter2, 1, wx.EXPAND, 5 )


		self.m_panel2.SetSizer( bSizer2 )
		self.m_panel2.Layout()
		bSizer2.Fit( self.m_panel2 )
		self.m_splitter1.SplitVertically( self.m_panel1, self.m_panel2, 0 )
		bSizer1.Add( self.m_splitter1, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass

	def m_splitter1OnIdle( self, event ):
		self.m_splitter1.SetSashPosition( 0 )
		self.m_splitter1.Unbind( wx.EVT_IDLE )

	def m_splitter2OnIdle( self, event ):
		self.m_splitter2.SetSashPosition( 0 )
		self.m_splitter2.Unbind( wx.EVT_IDLE )


