# VRChat Webcam Tracker

A Python application that detects facial expressions and arm movements using a webcam and sends them to VRChat in real time.

## Features

- **Facial Expression Tracking**: Detects mouth opening/closing, eyebrow movements, eye blinking, etc.
- **Arm & Hand Tracking**: Detects arm positions and hand gestures
- **VRChat OSC Integration**: Sends data to VRChat using Open Sound Control protocol
- **Real-time Processing**: Low-latency tracking and transmission

## Requirements

- Python 3.8 or higher
- Webcam
- VRChat (with OSC functionality enabled)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd vrchat-webcam-tracker
```

2. Install dependencies using uv:

```bash
uv sync
```

3. For macOS, configure camera access permissions (see [macOS Setup Guide](docs/MACOS_SETUP.md) for details)

## Usage

### Basic Usage

```bash
# Run the tracker (recommended)
uv run python src/main.py

# Debug mode
uv run python src/main.py --debug

# No display mode
uv run python src/main.py --no-display
```

### Testing OSC Functionality

```bash
# Test OSC functionality without camera
uv run python -m vrchat_webcam_tracker.osc_test --duration 10 --debug
```

### Detailed Options

```bash
python src/main.py [options]

Options:
  --ip IP          VRChat IP address (default: 127.0.0.1)
  --port PORT      OSC port (default: 9000)
  --camera ID      Camera ID (default: 0)
  --debug          Enable debug mode
  --no-display     Disable video display window
```

## Configuration

You can adjust OSC destination IP address, port, tracking sensitivity, etc. in `config.py`.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
