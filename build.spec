# -*- mode: python ; coding: utf-8 -*-
import cv2
from pathlib import Path
import mediapipe

# Get OpenCV data directory for Haar cascades
opencv_data_path = Path(cv2.data.haarcascades)

# Get MediaPipe installation path
mediapipe_path = Path(mediapipe.__file__).parent

a = Analysis(
    ['src/main.py'],
    pathex=['.', 'src'],
    binaries=[],
    datas=[
        # Include OpenCV Haar cascade files
        (str(opencv_data_path / 'haarcascade_frontalface_default.xml'), 'cv2/data'),
        (str(opencv_data_path / 'haarcascade_eye.xml'), 'cv2/data'),
        (str(opencv_data_path / 'haarcascade_smile.xml'), 'cv2/data'),
        # Include MediaPipe modules and data files
        (str(mediapipe_path / 'modules'), 'mediapipe/modules'),
        (str(mediapipe_path / 'python'), 'mediapipe/python'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'click',
        'pythonosc',
        'config',
        'osc_sender',
        'trackers',
        'mediapipe',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.pose',
        'mediapipe.python.solution_base',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
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
