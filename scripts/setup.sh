#!/bin/bash

# VRChat Webcam Tracker - Setup Script

echo "Starting VRChat Webcam Tracker setup..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed."
    echo "Please install uv before running again:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ uv found"

# Create Python virtual environment and install dependencies
echo "Installing dependencies..."
uv sync

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installation completed"
else
    echo "Error: Dependencies installation failed"
    exit 1
fi

# Test camera
echo "Testing camera..."
uv run python -c "
import cv2
camera = cv2.VideoCapture(0)
if camera.isOpened():
    print('✓ Camera detected successfully')
    camera.release()
else:
    print('× Camera not detected. Please check if camera is connected.')
"

echo ""
echo "Setup completed!"
echo ""