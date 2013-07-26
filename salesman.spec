# -*- mode: python -*-
from glob import glob
a = Analysis(['bin/salesman'],
             pathex=['.', '/home/miheerdew/Programming/Projects/SalesMan'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build/pyi.linux2/salesman', 'salesman'),
          debug=False,
          strip=None,
          upx=True,
          console=True )

plugins = Tree('salesman/plugins','plugins')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               plugins,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'salesman'))
