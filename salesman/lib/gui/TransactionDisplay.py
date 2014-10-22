import wx
from wx import html
from ..utils import pub
from datetime import date
from ..constants import NULL_TRANSACTION, TRANSACTION_FORMATTER

class TransactionDisplay(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.printer = html.HtmlEasyPrinting()
        self.currentTransaction = None

        self.SetupWidgets()
        self.PositionWidgets()
        self.BindWidgets()

        self.transactionFormatterPlugin = wx.GetApp().\
                    getPluginFromConfig(TRANSACTION_FORMATTER)

        pub.subscribe(self.OnFormatterChanged, TRANSACTION_FORMATTER)


    def SetupWidgets(self):
        self.html = html.HtmlWindow(self)
        self.printBtn = wx.Button(self, label='Print')

    def PositionWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.html, 1, wx.EXPAND)
        sizer.Add(self.printBtn, 0, wx.CENTER)
        self.SetSizer(sizer)

    def BindWidgets(self):
        self.printBtn.Bind(wx.EVT_BUTTON, self.OnPrint)

    def OnFormatterChanged(self, plugin):
        self.transactionFormatterPlugin=plugin
        self.UpdateDisplay(self.currentTransaction)

    def OnPrint(self, evt):
        #self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintText(self.html.GetParser().GetSource())

    def Blank(self):
        self.html.SetPage('')

    def UpdateDisplay(self, transaction):
        self.currentTransaction = transaction

        if transaction is NULL_TRANSACTION:
            html="""<html><body>
            <p><u>Note</u> : <i>This is just a dummy transaction added to the transaction
            list,so that, the current item state can also be seen
            through history viewer.</i></p>
            <p>
            <h4><u>How to use History Viewer:</u></h4>
            When a transraction is selected in the <u>Transaction List</u> (above),
            The state of items just before the transaction was registerd is
            shown in the <u>Item Viewer</u> (on the left).
            The paritculars of the transaction are shown in <u>Transaction Details</u>
            (this section).You can print the transaction details using the print Button (below).
            To undo any transaction , right click on that transaction in the <u>Transaction List</u>
            and press "Undo Selected Transaction". But note that if a transaction is undone, all the
            transactions that have been registered after it will also be removed.In case you wish to redo your undo,
            you may click on the redo button on the toolbar.
            </body>
            </html>
            """
        else:
            html=self.transactionFormatterPlugin\
                    .plugin_object.format(transaction)

        self.html.SetPage(html)
