# VRChat Webcam Tracker - macOS Setup Guide

## Prerequisites

- macOS 10.15 (Catalina) or later
- Python 3.8 or higher (will be installed automatically with uv)
- Webcam
- VRChat (with OSC functionality enabled)

## Installation

### Using Terminal

1. Open **Terminal**
2. Navigate to the project directory
3. Run the setup script:

```bash
scripts/setup.sh
```

## Running the Application

### Quick Start

Double-click `scripts/run.sh` to start the tracker with default settings, or run in Terminal:

```bash
./scripts/run.sh
```

### Command Line Usage

```bash
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

```bash
# Test OSC functionality without camera
uv run python src/osc_test.py
```

## Camera Access

### macOS Camera Privacy Settings

1. Open **System Preferences** (or **System Settings** on macOS Ventura+)
2. Click **Security & Privacy** → **Privacy** → **Camera**
3. Check the box for **Terminal** or **Python**
4. If the app isn't listed, you may need to manually add it or run the application first

### Manually Request Camera Access Permission

Run the following command in Terminal to reset camera permissions:

```bash
# Reset camera access permission
tccutil reset Camera
```

### Multiple Cameras

If you have multiple cameras, you can specify which one to use:

```bash
# Try different camera indices
uv run python src/main.py --camera 0  # Default
uv run python src/main.py --camera 1  # Second camera
uv run python src/main.py --camera 2  # Third camera
```

## Troubleshooting

### Setup Issues

**uv not found error:**

- The setup script will provide installation instructions
- Install uv manually: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or download from: https://github.com/astral-sh/uv/releases

**Dependencies installation failed:**

- Ensure you have a stable internet connection
- Try running `uv sync` manually
- Check if you have proper permissions

### Camera Issues

**Camera cannot be opened:**

1. **Check if camera is in use by other applications**

   - Close FaceTime, Zoom, Teams, browsers with camera access, etc.
   - Use Activity Monitor to check for applications using the camera

2. **Try different camera indices**

   ```bash
   uv run python src/main.py --camera 1
   uv run python src/main.py --camera 2
   ```

3. **Check macOS Camera Privacy Settings** (see Camera Access section above)

4. **Restart your computer** - Sometimes required after camera permission changes

**Camera detected but no video:**

- Check camera permissions in System Preferences
- Test camera with Photo Booth or FaceTime
- Restart the Terminal application

### OSC Connection Issues

**VRChat not receiving data:**

1. **Enable OSC in VRChat:**

   - Launch VRChat
   - Settings → OSC → Enable OSC
   - Verify port is set to 9000

2. **Check macOS Firewall:**

   - System Preferences → Security & Privacy → Firewall
   - If enabled, add exception for Python or the application

3. **Network connectivity:**
   ```bash
   # Test if port is accessible
   nc -zv 127.0.0.1 9000
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

```bash
uv run python src/main.py --no-display
```

### Custom Scripts

Create your own shell scripts for different configurations:

**gaming.sh:**

```bash
#!/bin/bash
uv run python src/main.py --no-display --ip 127.0.0.1
```

**debug.sh:**

```bash
#!/bin/bash
uv run python src/main.py --debug --camera 1
```

Make scripts executable:

```bash
chmod +x gaming.sh debug.sh
```

### Startup on Login

1. Open **System Preferences** → **Users & Groups**
2. Select your user account
3. Click **Login Items**
4. Click **+** and add your script or the `scripts/run.sh` file

Alternatively, create a LaunchAgent:

```bash
# Create a launch agent file
~/Library/LaunchAgents/com.vrchat-webcam-tracker.plist
```

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Run with `--debug` flag to see detailed output
3. Check camera and OSC connectivity separately
4. Verify VRChat OSC settings
5. Test with Photo Booth or FaceTime to ensure camera works
