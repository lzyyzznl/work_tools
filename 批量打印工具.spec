# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\batch_printer\\gui.py'],
    pathex=['d:\\workspace\\work_tools\\.venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('src/batch_printer', 'batch_printer'), ('src/resource', 'resource')],
    hiddenimports=['win32print', 'win32api', 'win32con', 'pywintypes', 'win32com.client', 'pythoncom', 'PyQt5.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'tkinter', 'sqlite3', 'distutils', 'email', 'http', 'urllib3', 'xml', 'PyQt5.Qt3DAnimation', 'PyQt5.Qt3DCore', 'PyQt5.Qt3DExtras', 'PyQt5.Qt3DInput', 'PyQt5.Qt3DLogic', 'PyQt5.Qt3DRender', 'PyQt5.QtWebEngine', 'PyQt5.QtWebEngineCore', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebKit', 'PyQt5.QtWebKitWidgets', 'PyQt5.QtQuick', 'PyQt5.QtQuick3D', 'PyQt5.QtQml', 'PyQt5.QtDesigner', 'PyQt5.QtHelp', 'PyQt5.QtMultimedia', 'PyQt5.QtLocation', 'PyQt5.QtPositioning'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='批量打印工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\resource\\打印机.ico'],
)
