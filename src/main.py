#!/usr/bin/env python3
"""
VRChat Webcam Tracker

Basic usage:
    python -m vrchat_webcam_tracker.cli

Options:
    --ip IP_ADDRESS        VRChat IP address (default: 127.0.0.1)
    --port PORT            OSC port (default: 9000)
    --camera CAMERA_ID     Camera ID (default: 0)
    --debug                Enable debug mode
    --no-display           Disable screen display
"""

import argparse
import signal
import sys
import cv2
import time
import config
from trackers import FaceTracker, HandTracker
from osc_sender import VRChatOSCSender, ParameterSmoother


def signal_handler(sig, frame):
    """Ctrl+C handler"""
    print("\nStopping tracking...")
    sys.exit(0)


class SimpleTracker:
    """Simple CLI tracker"""

    def __init__(self, ip, port, camera_index, debug=False):
        self.ip = ip
        self.port = port
        self.camera_index = camera_index
        self.debug = debug

        # Initialize trackers and OSC sender
        self.face_tracker = FaceTracker()
        self.hand_tracker = HandTracker()
        self.osc_sender = VRChatOSCSender(ip, port)
        self.smoothers = {}

        self.running = False
        self.cap = None

    def start(self, show_video=True):
        """Start tracking"""
        # Open camera
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        print("Starting tracking...")
        if show_video:
            print("Press ESC to exit, or Ctrl+C")
        else:
            print("Press Ctrl+C to exit")

        self.running = True

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                # Frame processing
                self.process_frame(frame)

                # Screen display
                if show_video:
                    cv2.putText(
                        frame,
                        f"OSC: {self.ip}:{self.port}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )
                    cv2.imshow("VRChat Tracker", frame)

                    if cv2.waitKey(1) & 0xFF == 27:  # ESC
                        break

                time.sleep(1.0 / config.TARGET_FPS)

        except KeyboardInterrupt:
            print("\nKeyboard interrupt")
        finally:
            self.stop()

        return True

    def stop(self):
        """Stop tracking"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Tracking stopped")

    def process_frame(self, frame):
        """Frame processing"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Face detection
        face_data = self.face_tracker.detect(frame_rgb)
        if face_data and self.debug:
            print(f"Face detection: {list(face_data.keys())}")

        # Hand detection
        hand_data = self.hand_tracker.detect(frame_rgb)
        if hand_data and self.debug:
            print(f"Hand detection: {list(hand_data.keys())}")

        # OSC transmission (simplified version)
        if face_data:
            self.send_test_osc()

    def send_test_osc(self):
        """Test OSC transmission"""
        # Send simple test parameters
        test_value = (time.time() % 2.0) / 2.0  # Oscillate between 0-1

        if "MouthOpen" not in self.smoothers:
            self.smoothers["MouthOpen"] = ParameterSmoother()

        smoothed = self.smoothers["MouthOpen"].smooth(test_value, "MouthOpen")
        self.osc_sender.send_custom_parameter("MouthOpen", smoothed)

        if self.debug:
            print(f"MouthOpen: {smoothed:.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="VRChat Webcam Tracker - Command Line Version"
    )
    parser.add_argument(
        "--ip",
        default=config.VRCHAT_OSC_IP,
        help="VRChat IP address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.VRCHAT_OSC_PORT,
        help="OSC port (default: 9000)",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=config.CAMERA_INDEX,
        help="Camera ID (default: 0)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--no-display", action="store_true", help="Disable screen display"
    )

    args = parser.parse_args()

    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    print("VRChat Webcam Tracker (Command Line Version)")
    print(f"VRChat OSC: {args.ip}:{args.port}")
    print(f"Camera ID: {args.camera}")
    print("-" * 50)

    # Create and start tracker
    tracker = SimpleTracker(
        ip=args.ip, port=args.port, camera_index=args.camera, debug=args.debug
    )

    try:
        tracker.start(show_video=not args.no_display)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
