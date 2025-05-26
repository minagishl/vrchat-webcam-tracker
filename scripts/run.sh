#!/bin/bash

# VRChat Webcam Tracker - Run Script

echo "Starting VRChat Webcam Tracker..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed."
    echo "Please install uv before running again:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Run the application
# The app now includes UpperBodyTracker with MediaPipe Pose for body tracking
# Body tracking data is automatically sent via OSC when --no-display is used
uv run python src/main.py "$@"

echo ""
