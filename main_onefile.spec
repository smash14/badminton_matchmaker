# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('tools/matchmaker_core/bin/onefile/matchmaker_core.exe', 'tools/matchmaker_core/bin/onefile')],
    datas=[
        ('data/', 'data/'),
        ('C:\\develop\\ligaman_gui\\data\\logo\\Favicons\\favicon.ico', '.')
        ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Badminton Matchmaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='C:\\develop\\ligaman_gui\\data\\logo\\Favicons\\favicon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
