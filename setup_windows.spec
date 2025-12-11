# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for The Apex Executive - Windows Build
"""

block_cipher = None

a = Analysis(
    ['modern_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('game_core.py', '.'),
        ('event_system.py', '.'),
        ('companies.py', '.'),
        ('assets/app_icon.png', 'assets'),
        ('assets/README.txt', 'assets'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'customtkinter',
        'darkdetect',
        'packaging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TheApexExecutive',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.png',  # Will be converted to .ico automatically
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TheApexExecutive',
)
