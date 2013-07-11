from lib.gui import Application, DebugApp
import sys

if __name__ == '__main__':
    App = Application
    if set(('d','-d')) & set(sys.argv[1:]):
        App = DebugApp
    App().MainLoop()
