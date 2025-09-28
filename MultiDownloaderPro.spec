# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# *******************************************************************
# CONFIGURACIÓN DE RUTAS
# *******************************************************************
PROJECT_ROOT = r'C:\Users\nates\Documents\MultiDowloaderProV2.0\MultiDowloaderV2.0'
PYD_DIR = PROJECT_ROOT  # Carpeta donde está el multi.pyd

a = Analysis(
    ['MultiDownloaderv2.0.py'],  # Script principal
    pathex=[PROJECT_ROOT],
    binaries=[
        (os.path.join(PYD_DIR, 'multi.pyd'), '.'),
    ],
    datas=[
        (os.path.join(PROJECT_ROOT, 'assets'), 'assets'),
    ],
    hiddenimports=[
        'yt_dlp.extractor.all',
        'browser_cookie3',
        'PIL._tkinter_finder',
        'customtkinter',
        'multi'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PySide6', 'matplotlib', 'numpy', 'scipy'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MultiDownloaderPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Oculta la consola (para GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(PROJECT_ROOT, 'assets', 'youtubemp4.ico')
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MultiDownloaderPro',
)
