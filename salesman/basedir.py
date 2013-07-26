import os
import sys

if getattr(sys, 'frozen', None):
     BASEDIR = sys._MEIPASS
else:
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
