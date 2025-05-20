# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\file_prefix_adder\\gui_qt.py'],
    pathex=['d:\\workspace\\WorkTools\\.venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('src/file_prefix_adder', 'file_prefix_adder')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
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
    name='FilePrefixAdderGUI',
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
)
