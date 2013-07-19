# -*- mode: python -*-
a = Analysis(['bin/salesman'],
             pathex=['/home/miheerdew/Programming/Projects/SalesMan', '/home/miheerdew/Programming/Projects/SalesMan'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'salesman'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
