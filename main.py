from lib.gui import Application, ApplicationWithDebugger
import unittest
import sys

if __name__ == '__main__':

    args = set(sys.argv[1:])

    if set(('-t', '--test')) & args:
        unittest.main(module='lib.test', exit=True, argv=['SalesMan'])

    App = Application

    if set(('-d', '--debug')) & set(sys.argv[1:]):
        App = ApplicationWithDebugger



    App().MainLoop()
