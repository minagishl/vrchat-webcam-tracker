#!/usr/bin/env python3
"""
VRChat Webcam Tracker - CLI-only tracker
Version without tkinter dependency
"""

import cv2
import numpy as np
import time
from typing import Dict, Optional
import config
from trackers import FaceTracker, HandTracker
from osc_sender import VRChatOSCSender, ParameterSmoother


class CLIWebcamTracker:
    """CLI webcam tracker (without GUI dependencies)"""

    def __init__(
        self,
        ip: "Optional[str]" = None,
        port: "Optional[int]" = None,
        camera_index: "Optional[int]" = None,
        debug: bool = False,
    ):
        # Settings
        self.ip = ip or config.VRCHAT_OSC_IP
        self.port = port or config.VRCHAT_OSC_PORT
        self.camera_index = camera_index or config.CAMERA_INDEX
        self.debug = debug

        # Tracking related
        self.face_tracker = FaceTracker()
        self.hand_tracker = HandTracker()
        self.osc_sender = VRChatOSCSender(self.ip, self.port)
        self.smoothers = {}

        # State management
        self.running = False
        self.tracking_thread = None
        self.cap = None

        # Performance monitoring
        self.fps_counter = 0
        self.fps_start_time = time.time()

        if self.debug:
            print(f"VRChat OSC: {self.ip}:{self.port}")
            print(f"Camera: {self.camera_index}")

    def start_tracking(self, show_video: bool = True):
        """Start tracking"""
        if self.running:
            print("Already tracking")
            return

        # Initialize camera
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.TARGET_FPS)

        print("Tracking started...")
        print("Press Ctrl+C to quit")

        self.running = True
        self._tracking_loop(show_video)

    def stop_tracking(self):
        """Stop tracking"""
        if not self.running:
            return

        print("Stopping tracking...")
        self.running = False

        if self.cap:
            self.cap.release()

        cv2.destroyAllWindows()
        print("Tracking stopped")

    def _tracking_loop(self, show_video: bool):
        """Main tracking loop"""
        try:
            while self.running:
                if self.cap is None or not self.cap.isOpened():
                    print("Warning: Camera is not initialized or already released")
                    break
                ret, frame = self.cap.read()
                if not ret:
                    print("Warning: Could not read frame")
                    continue

                # Process frame
                self._process_frame(frame)

                # Display video (optional)
                if show_video:
                    self._display_frame(frame)

                    # Exit with ESC key
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                        break

                # FPS control
                time.sleep(1.0 / config.TARGET_FPS)

        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt")
        finally:
            self.stop_tracking()

    def _process_frame(self, frame):
        """Process frame and send OSC messages"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Face detection and analysis
        face_data = self.face_tracker.detect(frame_rgb)
        if face_data:
            self._send_face_data(face_data)

        # Hand detection (simplified version)
        hand_data = self.hand_tracker.detect(frame_rgb)
        if hand_data:
            self._send_hand_data(hand_data)

        # Performance monitoring
        self._update_fps()

    def _send_face_data(self, face_data: Dict):
        """Send face data to VRChat"""
        # Calculate expression parameters
        expressions = self._calculate_expressions(face_data)

        # Send OSC messages
        for param, value in expressions.items():
            # Smoothing
            if param not in self.smoothers:
                self.smoothers[param] = ParameterSmoother()

            smoothed_value = self.smoothers[param].smooth(value)
            self.osc_sender.send_custom_parameter(param, smoothed_value)

            if self.debug:
                print(f"{param}: {smoothed_value:.3f}")

    def _send_hand_data(self, hand_data: Dict):
        """Send hand data to VRChat"""
        # Normalize hand positions
        for hand_type, landmarks in hand_data.items():
            if landmarks:
                # Calculate simple hand open/close state
                finger_curl = self._calculate_finger_curl(landmarks)
                param_name = f"Hand{hand_type.capitalize()}Curl"

                if param_name not in self.smoothers:
                    self.smoothers[param_name] = ParameterSmoother()

                smoothed_value = self.smoothers[param_name].smooth(finger_curl)
                self.osc_sender.send_custom_parameter(param_name, smoothed_value)

                if self.debug:
                    print(f"{param_name}: {smoothed_value:.3f}")

    def _calculate_expressions(self, face_data: Dict) -> Dict[str, float]:
        """Calculate expression parameters from face data"""
        expressions = {}

        if "landmarks" in face_data:
            landmarks = face_data["landmarks"]

            # Mouth opening (simplified version)
            mouth_points = landmarks[48:68]  # Mouth region
            if len(mouth_points) > 0:
                mouth_height = np.max(mouth_points[:, 1]) - np.min(mouth_points[:, 1])
                mouth_width = np.max(mouth_points[:, 0]) - np.min(mouth_points[:, 0])
                if mouth_width > 0:
                    expressions["MouthOpen"] = min(
                        1.0, mouth_height / mouth_width * 2.0
                    )

            # Eyebrow movement (simplified version)
            if len(landmarks) >= 27:
                eyebrow_left = landmarks[17:22]
                eyebrow_right = landmarks[22:27]

                # Average eyebrow height
                avg_eyebrow_height = (
                    np.mean(eyebrow_left[:, 1]) + np.mean(eyebrow_right[:, 1])
                ) / 2
                expressions["BrowUp"] = max(
                    0.0, min(1.0, (200 - avg_eyebrow_height) / 50)
                )

        return expressions

    def _calculate_finger_curl(self, landmarks) -> float:
        """Calculate finger curl from hand landmarks"""
        # Simplified version: calculate overall hand "openness"
        if len(landmarks) < 21:
            return 0.0

        # Total distance from palm center to each fingertip
        palm_center = landmarks[0]  # Wrist
        fingertips = [
            landmarks[4],
            landmarks[8],
            landmarks[12],
            landmarks[16],
            landmarks[20],
        ]

        total_distance = 0
        for tip in fingertips:
            distance = np.linalg.norm(tip - palm_center)
            total_distance += distance

        # Normalize (with arbitrary value)
        normalized_curl = max(0.0, min(1.0, float(total_distance / 400.0)))
        return float(1.0 - normalized_curl)  # curl is inverse

    def _display_frame(self, frame):
        """Display frame"""
        # Overlay information
        info_text = f"FPS: {self.fps_counter:.1f} | IP: {self.ip}:{self.port}"
        cv2.putText(
            frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

        # Status display
        status_text = "Tracking Active - Press ESC to quit"
        cv2.putText(
            frame,
            status_text,
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )

        cv2.imshow("VRChat Webcam Tracker", frame)

    def _update_fps(self):
        """Update FPS calculation"""
        current_time = time.time()
        if current_time - self.fps_start_time >= 1.0:
            self.fps_counter = self.fps_counter if hasattr(self, "_frame_count") else 0
            self.fps_start_time = current_time
            if hasattr(self, "_frame_count"):
                self.fps_counter = self._frame_count
                self._frame_count = 0
            else:
                self._frame_count = 0

        if not hasattr(self, "_frame_count"):
            self._frame_count = 0
        self._frame_count += 1


def main():
    """Main function"""
    import argparse
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\nStopping tracking...")
        sys.exit(0)

    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="VRChat Webcam Tracker - CLI version")
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
        "--no-display", action="store_true", help="Disable video display"
    )

    args = parser.parse_args()

    # Create and start tracker
    tracker = CLIWebcamTracker(
        ip=args.ip, port=args.port, camera_index=args.camera, debug=args.debug
    )

    try:
        tracker.start_tracking(show_video=not args.no_display)
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    finally:
        tracker.stop_tracking()


if __name__ == "__main__":
    main()
