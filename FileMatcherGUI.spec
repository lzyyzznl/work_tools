# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\file_matcher\\gui.py'],
    pathex=['D:\\workspace\\work_tools\\.venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('src/resource', 'resource'), ('src/file_matcher', 'file_matcher')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'pandas'],
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
    name='FileMatcherGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\resource\\icon.png'],
)
