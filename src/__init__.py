"""
VRChat Webcam Tracker

A Python package that detects facial expressions and arm movements
using a webcam and sends them to VRChat in real time.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from trackers import FaceTracker, HandTracker
from osc_sender import VRChatOSCSender, OSCDebugger, ParameterSmoother

__all__ = [
    "FaceTracker",
    "HandTracker",
    "VRChatOSCSender",
    "OSCDebugger",
    "ParameterSmoother",
]
