# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['C:\\Temp\\Credenciais_API_local'], 
    binaries=[],
    datas=[
        ('instance','var\\project-instance'),
        ('project\\core', 'project\\core'),
        ('project\\envio', 'project\\envio'),
        ('project\\error_pages', 'project\\error_pages'),
        ('project\\static','project\\static'),
        ('project\\templates', 'project\\templates'),
        ('credentials.json','.'),
        ('token.json','.')
        ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='CredenciaisAPI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True
)
