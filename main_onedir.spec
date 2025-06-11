# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('tools/matchmaker_core/bin/onedir/', 'tools/matchmaker_core/bin/onedir')],
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

splash = Splash('splashscreen.png',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(10, 50),
                text_size=12,
                text_color='black')

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    splash,
    a.scripts,
    [],
    exclude_binaries=False,
    name='Badminton Matchmaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='C:\\develop\\ligaman_gui\\data\\logo\\Favicons\\favicon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    splash.binaries,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
