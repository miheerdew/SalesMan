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

    def __init__( self, parent, title=wx.EmptyString ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = title, pos = wx.DefaultPosition, size = wx.Size( 500,500 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.html = wx.html.HtmlWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
        bSizer1.Add( self.html, 1, wx.ALL|wx.EXPAND, 5 )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Set Dates" ), wx.VERTICAL )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Start Date", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
        self.m_staticText3.Wrap( -1 )
        bSizer2.Add( self.m_staticText3, 1, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.startDateCtrl = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
        bSizer2.Add( self.startDateCtrl, 1, wx.ALL, 5 )


        sbSizer1.Add( bSizer2, 0, wx.ALL|wx.EXPAND, 5 )

        bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText31 = wx.StaticText( self, wx.ID_ANY, u"End Date", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
        self.m_staticText31.Wrap( -1 )
        bSizer21.Add( self.m_staticText31, 1, wx.ALL|wx.EXPAND, 5 )

        self.endDateCtrl = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
        bSizer21.Add( self.endDateCtrl, 1, wx.ALL, 5 )


        sbSizer1.Add( bSizer21, 0, wx.ALL|wx.EXPAND, 5 )


        bSizer1.Add( sbSizer1, 0, wx.ALL|wx.EXPAND, 10 )

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Set path to statement file" ), wx.VERTICAL )

        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

        self.pathCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.pathCtrl, 1, wx.ALL, 5 )

        self.pathBtn = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.pathBtn, 0, wx.ALL, 5 )


        sbSizer2.Add( bSizer6, 1, wx.EXPAND, 5 )


        bSizer1.Add( sbSizer2, 0, wx.ALL|wx.EXPAND, 10 )

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();

        bSizer1.Add( m_sdbSizer1, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.pathBtn.Bind( wx.EVT_BUTTON, self.OnPathButtonClick )
        self.m_sdbSizer1OK.Bind( wx.EVT_BUTTON, self.OnOKButtonClick )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def OnPathButtonClick( self, event ):
        event.Skip()

    def OnOKButtonClick( self, event ):
        event.Skip()


