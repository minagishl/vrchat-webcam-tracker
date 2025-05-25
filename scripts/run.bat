@echo off
chcp 65001 >nul
echo Starting VRChat Webcam Tracker...
echo.
cd /d "%~dp0.."
uv run python src/main.py %*
echo.
pause
