@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo Starting VRChat Webcam Tracker setup...
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if !errorlevel! neq 0 (
    echo Error: uv is not installed.
    echo Please install uv before running again:
    echo.
    echo For Windows:
    echo powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    echo Or download from: https://github.com/astral-sh/uv/releases
    echo.
    pause
    exit /b 1
)

echo ✓ uv found
echo.

REM Install dependencies
echo Installing dependencies...
uv sync

if !errorlevel! neq 0 (
    echo Error: Dependencies installation failed
    pause
    exit /b 1
)

echo ✓ Dependencies installation completed
echo.

REM Test camera
echo Testing camera...
uv run python -c "import cv2; camera = cv2.VideoCapture(0); print('✓ Camera detected successfully') if camera.isOpened() else print('× Camera not detected. Please check if camera is connected.'); camera.release() if camera.isOpened() else None"
echo.

echo Setup completed!
echo.
echo To run the tracker:
echo   uv run python src/main.py
echo.
echo To test OSC connection:
echo   uv run python src/osc_test.py
echo.
pause
