# VRChat Webcam Tracker - macOS Setup Guide

## Camera Access Permission Setup

To use the camera on macOS, you need to grant camera access permissions to the application.

### 1. Allow Camera Access in System Preferences

1. Open **System Preferences**
2. Click **Security & Privacy**
3. Select **Camera** from the left menu
4. Check the box for **Terminal** or **Python**

### 2. Manually Request Camera Access Permission

Run the following command in Terminal to request camera access permission:

```bash
# Request camera access permission
tccutil reset Camera
```

### 3. Running the Application

After setting up camera access permissions, run the application with the following commands:

```bash
# Tracking with display
uv run python -m vrchat_webcam_tracker.cli

# Tracking without display (debug mode)
uv run python -m vrchat_webcam_tracker.cli --debug --no-display

# Test OSC functionality only (no camera)
uv run python -m vrchat_webcam_tracker.osc_test --duration 10 --debug
```

## Troubleshooting

### If Camera Cannot Be Opened

1. **Check if camera is not being used by other applications**
   - Close Zoom, Teams, FaceTime, etc.
2. **Try changing camera ID**

   ```bash
   uv run python -m vrchat_webcam_tracker.cli --camera 1
   ```

3. **Restart the system**
   - A restart may be required after changing camera access permissions

### Verifying OSC Connection

Check if OSC is enabled in VRChat:

1. Launch VRChat
2. Settings → OSC → Enable OSC
3. Verify that port 9000 is being used

## Performance Optimization

### CPU Performance

- Use `--no-display` option to disable screen display
- Adjust tracking frequency (TARGET_FPS in config.py)

### Network Optimization

- When using local network, specify IP address with `--ip` option

## Customizing Configuration Files

You can adjust the following in `src/vrchat_webcam_tracker/config.py`:

```python
# Camera settings
CAMERA_INDEX = 0  # Camera ID
FRAME_WIDTH = 640  # Frame width
FRAME_HEIGHT = 480  # Frame height
TARGET_FPS = 30  # Target FPS

# OSC settings
VRCHAT_OSC_IP = "127.0.0.1"  # VRChat IP
VRCHAT_OSC_PORT = 9000  # OSC port
```

## Usage Examples

### Basic Usage

```bash
# Launch with default settings
uv run python -m vrchat_webcam_tracker.cli
```

### Custom Settings

```bash
# Specify IP and port
uv run python -m vrchat_webcam_tracker.cli --ip 192.168.1.100 --port 9001

# Use camera 1, debug mode
uv run python -m vrchat_webcam_tracker.cli --camera 1 --debug
```

### OSC Test Only

```bash
# 30-second OSC test
uv run python -m vrchat_webcam_tracker.osc_test --duration 30 --debug
```
