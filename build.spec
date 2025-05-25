# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/config.py', 'src'),
        ('src/osc_sender.py', 'src'),
        ('src/trackers.py', 'src'),
        ('src/__init__.py', 'src'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'click',
        'pythonosc',
        'src.config',
        'src.osc_sender',
        'src.trackers',
        'config',
        'osc_sender',
        'trackers',
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

# Collect all cv2 dependencies
from PyInstaller.utils.hooks import collect_all
cv2_datas, cv2_binaries, cv2_hiddenimports = collect_all('cv2')
a.datas += cv2_datas
a.binaries += cv2_binaries
a.hiddenimports += cv2_hiddenimports

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='vrchat-webcam-tracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
