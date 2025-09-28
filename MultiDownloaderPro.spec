# -*- mode: python ; coding: utf-8 -*-
# NOTA: Este SPEC asume que has creado un script de entrada (ej: main_runner.py)
# que contiene 'import multi' para cargar el módulo .pyd.

block_cipher = None

# *******************************************************************
# ** AJUSTA ESTA RUTA DE ARCHIVO .PYD AQUÍ **
# Reemplaza 'RUTA_A_TU_MULTI.PYD' con la ubicación real de tu archivo compilado.
# Ejemplo: 'build/lib.win-amd64-3.13/multi.cpython-313-x86_64-win.pyd'
# *******************************************************************
PYD_PATH_COMPLETA = 'C:\\Users\\nates\\Documents\\MultiDowloaderProV2.0\\MultiDowloaderV2.0'

a = Analysis(
    ['MultiDownloaderv2.0.py'], # Usamos el script principal
    
    # 1. CORRECCIÓN DE SINTAXIS: Las rutas deben ser strings (cadenas entre comillas)
    # Recomendación: Usar la ruta del directorio del proyecto (path actual)
    pathex=['C:\\Users\\nates\\Documents\\MultiDowloaderProV2.0\\MultiDowloaderV2.0'],
    
    # 2. INCLUSIÓN CORRECTA DEL .PYD EN LA LISTA DE BINARIOS
    # Formato: [(ruta_completa_al_archivo, nombre_del_módulo_en_runtime)]
    binaries=[
        (PYD_PATH_COMPLETA, 'multi.pyd')
    ],
    
    # Incluir la carpeta de assets para el logo (si existe)
    datas=[('assets', 'assets')], 
    
    # Hidden Imports (Cruciales para yt-dlp, browser-cookie3 y GUI)
    hiddenimports=[
        'yt_dlp.extractor.all', 
        'browser_cookie3', # Asegura que la librería de cookies se incluya
        'PIL._tkinter_finder', # Para asegurar que PIL (Pillow) funcione con tkinter
        'customtkinter', # Si usas customtkinter (el diseño lo sugiere)
        'multi' # Aseguramos la importación del módulo Cython
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Excluir módulos grandes que no usas
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
    console=False, # Mantiene la ventana de consola oculta (Correcto para GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
