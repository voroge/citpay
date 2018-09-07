# -*- mode: python -*-

block_cipher = None


a = Analysis(['uiconnect.py'],
             pathex=['C:\\Grunge\\ITC_FAS\\Python\\citpay'],
             binaries=[],
             datas=[],
             hiddenimports=['pandas._libs.tslibs.np_datetime', 'pandas._libs.tslibs.nattype', 'pandas._libs.skiplist'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='uiconnect',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='ico\\user32.ico')
