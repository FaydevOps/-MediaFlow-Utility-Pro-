block_cipher = None

a = Analysis(
    ['youtube.py'],
    pathex=['/Users/nates/Documents/MultiDowloader-MultiDownloader/MultiDowloader-MultiDownloader/macapply'],
    binaries=[
        ('youtube.so', '.'),  # En Mac, Cython genera .so
    ],
    datas=[
        ('assets/youtubemp3.png', 'assets'),  # Incluye tu imagen
        ('assets/youtubemp4.icns', 'assets'),        # Icono para Mac
    ],
    hiddenimports=[
        'yt_dlp',
        'PIL._tkinter_finder',
        'browser_cookie3',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MultiDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX no se recomienda en Mac
    console=False,
    icon='assets/youtubemp4.icns',  # Icono en formato .icns
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MultiDownloader'
)