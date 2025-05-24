# VRChat Webcam Tracker - Windows Setup Guide

## Prerequisites

- Windows 10 or later
- Python 3.9 or higher (will be installed automatically with uv)
- Webcam
- VRChat (with OSC functionality enabled)

## Installation

### Option 1: Using Command Prompt (Recommended)

1. Open **Command Prompt** as Administrator (optional, but recommended)
2. Navigate to the project directory
3. Run the setup script:

```cmd
scripts\setup.bat
```

### Option 2: Using PowerShell

1. Open **PowerShell** as Administrator (optional, but recommended)
2. Navigate to the project directory
3. If you encounter execution policy issues, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4. Run the setup script:

```powershell
scripts\setup.ps1
```

## Running the Application

### Quick Start

Double-click `scripts\run.bat` to start the tracker with default settings.

### Command Line Usage

```cmd
# Basic usage
uv run python src/main.py

# With debug mode
uv run python src/main.py --debug

# Without display window
uv run python src/main.py --no-display

# Custom IP and port
uv run python src/main.py --ip 192.168.1.100 --port 9001

# Different camera
uv run python src/main.py --camera 1
```

### Testing OSC Connection

```cmd
# Test OSC functionality without camera
uv run python src/osc_test.py
```

## Camera Access

### Windows Camera Privacy Settings

1. Open **Settings** (Windows key + I)
2. Go to **Privacy & security** → **Camera**
3. Ensure **Camera access** is turned on
4. Ensure **Let apps access your camera** is turned on
5. Ensure **Let desktop apps access your camera** is turned on

### Multiple Cameras

If you have multiple cameras, you can specify which one to use:

```cmd
# Try different camera indices
uv run python src/main.py --camera 0  # Default
uv run python src/main.py --camera 1  # Second camera
uv run python src/main.py --camera 2  # Third camera
```

## Troubleshooting

### Setup Issues

**uv not found error:**

- The setup script will provide installation instructions
- Download uv from: https://github.com/astral-sh/uv/releases
- Or use the PowerShell installation command provided in the setup script

**Dependencies installation failed:**

- Run Command Prompt as Administrator
- Ensure you have a stable internet connection
- Try running `uv sync` manually

### Camera Issues

**Camera cannot be opened:**

1. **Check if camera is in use by other applications**

   - Close Skype, Teams, OBS, browsers with camera access, etc.
   - Use Task Manager to check for applications using the camera

2. **Try different camera indices**

   ```cmd
   uv run python src/main.py --camera 1
   uv run python src/main.py --camera 2
   ```

3. **Check Windows Camera Privacy Settings** (see Camera Access section above)

4. **Restart your computer** - Sometimes required after camera permission changes

**Camera detected but no video:**

- Check camera drivers in Device Manager
- Update camera drivers
- Test camera with Windows Camera app

### OSC Connection Issues

**VRChat not receiving data:**

1. **Enable OSC in VRChat:**

   - Launch VRChat
   - Settings → OSC → Enable OSC
   - Verify port is set to 9000

2. **Check Windows Firewall:**

   - Windows Defender Firewall might block the connection
   - Add exception for Python or the application

3. **Network connectivity:**
   ```cmd
   # Test if port is accessible (requires telnet)
   telnet 127.0.0.1 9000
   ```

### Performance Issues

**High CPU usage:**

- Use `--no-display` option to disable video window
- Lower the frame rate in config.py
- Close unnecessary background applications

**Lag or delay:**

- Ensure VRChat and the tracker are on the same machine
- Check network latency if using remote connection
- Reduce camera resolution in config.py

## Configuration

Edit `src/config.py` to customize settings:

```python
# Camera settings
CAMERA_INDEX = 0  # Camera ID
FRAME_WIDTH = 640  # Frame width
FRAME_HEIGHT = 480  # Frame height
TARGET_FPS = 30  # Target FPS

# OSC settings
VRCHAT_OSC_IP = "127.0.0.1"  # VRChat IP
VRCHAT_OSC_PORT = 9000  # OSC port

# Tracking sensitivity
MOUTH_THRESHOLD = 0.02  # Mouth open threshold
EYEBROW_THRESHOLD = 0.01  # Eyebrow raise threshold
```

## Advanced Usage

### Running in Background

To run the tracker in the background without a display window:

```cmd
uv run python src/main.py --no-display
```

### Custom Scripts

Create your own batch files for different configurations:

**gaming.bat:**

```cmd
@echo off
uv run python src/main.py --no-display --ip 127.0.0.1
```

**debug.bat:**

```cmd
@echo off
uv run python src/main.py --debug --camera 1
```

### Startup on Boot

1. Create a shortcut to `scripts\run.bat`
2. Place the shortcut in:
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
   ```

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Run with `--debug` flag to see detailed output
3. Check camera and OSC connectivity separately
4. Verify VRChat OSC settings
5. Test with Windows Camera app to ensure camera works
