@echo off
chcp 65001 >nul
echo Starting VRChat Webcam Tracker...
echo.
cd /d "%~dp0.."
REM The app now includes UpperBodyTracker with MediaPipe Pose for body tracking
REM Body tracking data is automatically sent via OSC when --no-display is used
uv run python src/main.py %*
echo.
pause
