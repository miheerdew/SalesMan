# -*- mode: python -*-
import os.path as op
import platform
import wxversion;wxversion.select("2.8");import sys 
block_cipher = None

plugins_dir = op.join('salesman','plugins') 
plugins = Tree(plugins_dir, 'plugins', excludes=['*.pyc', '*~'])

exe_name = 'salesman'

if platform.system() == 'Windows':
    exe_name += '.exe'

a = Analysis(['main.py'],
             pathex=[sys.path[0]],
             hiddenimports=['xlsxwriter'],
             hookspath=None,
             runtime_hooks=None,
             cipher=block_cipher)
pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas + plugins,
          plugins,
          name=exe_name,
          debug=False,
          strip=None,
          upx=True,
          console=False , icon=op.join('data','AppIcon32x32.ico'))
