@echo off
chcp 65001 >nul
echo Starting VRChat Webcam Tracker...
echo.
uv run python src/main.py %*
echo.
pause
