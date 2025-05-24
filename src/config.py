"""VRChat Webcam Tracker - Configuration Module.

This module contains configuration settings for the VRChat Webcam Tracker.
It includes settings for OSC communication, camera parameters, and tracking thresholds.
"""

# VRChat OSC Configuration
VRCHAT_OSC_IP = "127.0.0.1"  # IP address of the PC running VRChat
VRCHAT_OSC_PORT = 9000  # VRChat OSC port

# Tracking Configuration
FACE_DETECTION_CONFIDENCE = 0.5  # Face detection confidence threshold
HAND_DETECTION_CONFIDENCE = 0.5  # Hand detection confidence threshold
TRACKING_CONFIDENCE = 0.5  # Tracking confidence threshold

# Camera Configuration
CAMERA_INDEX = 0  # Camera index to use
CAMERA_WIDTH = 640  # Camera resolution (width)
CAMERA_HEIGHT = 480  # Camera resolution (height)
FPS = 30  # Frame rate

# Facial Expression Parameter Adjustments
MOUTH_OPEN_THRESHOLD = 0.02  # Mouth opening/closing detection threshold
EYE_BLINK_THRESHOLD = 0.4  # Eye blink detection threshold
EYEBROW_RAISE_THRESHOLD = 0.01  # Eyebrow raise detection threshold

# Arm & Hand Movement Parameters
ARM_MOVEMENT_SENSITIVITY = 1.0  # Arm movement sensitivity
HAND_GESTURE_SENSITIVITY = 1.0  # Hand gesture sensitivity

# Additional frame configuration for CLI
FRAME_WIDTH = CAMERA_WIDTH  # Frame width (alias)
FRAME_HEIGHT = CAMERA_HEIGHT  # Frame height (alias)
TARGET_FPS = FPS  # Target FPS (alias)
