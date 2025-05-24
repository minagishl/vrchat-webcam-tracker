"""VRChat Webcam Tracker - Command Line Version.

This tool tracks facial expressions and hand movements using your webcam
and sends the data to VRChat via OSC protocol.
"""

import signal
import sys
import time

import click
import cv2
import numpy as np

import config
from osc_sender import ParameterSmoother, VRChatOSCSender
from trackers import FaceTracker, HandTracker

ESC_KEY_CODE = 27  # ESC key code


def signal_handler(_sig: int, _frame: object) -> None:
    """Ctrl+C handler."""
    click.echo("\nStopping tracking...")
    sys.exit(0)


class SimpleTracker:
    """Simple CLI tracker."""

    def __init__(self, ip: str, port: int, camera_index: int, *, debug: bool = False) -> None:
        """Initialize SimpleTracker.

        Args:
            ip: VRChat OSC IP address.
            port: VRChat OSC port.
            camera_index: Camera index to use.
            debug: Enable debug mode.

        """
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

    def start(self, *, show_video: bool = True) -> bool:
        """Start tracking."""
        # Open camera
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            click.echo(f"Error: Could not open camera {self.camera_index}", err=True)
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        click.echo("Starting tracking...")
        if show_video:
            click.echo("Press ESC to exit, or Ctrl+C")
        else:
            click.echo("Press Ctrl+C to exit")

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

                    if cv2.waitKey(1) & 0xFF == ESC_KEY_CODE:  # ESC
                        break

                time.sleep(1.0 / config.TARGET_FPS)

        except KeyboardInterrupt:
            click.echo("\nKeyboard interrupt")
        finally:
            self.stop()

        return True

    def stop(self) -> None:
        """Stop tracking."""
        self.running = False
        if self.cap:
            self.cap.release()
        click.echo("Tracking stopped")

    def process_frame(self, frame: np.ndarray) -> None:
        """Frame processing."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Face detection
        face_data = self.face_tracker.detect(frame_rgb)
        if face_data and self.debug:
            click.echo(f"Face detection: {list(face_data.keys())}")

        # Hand detection
        hand_data = self.hand_tracker.detect(frame_rgb)
        if hand_data and self.debug:
            click.echo(f"Hand detection: {list(hand_data.keys())}")

        # OSC transmission (simplified version)
        if face_data:
            self.send_test_osc()

    def send_test_osc(self) -> None:
        """Test OSC transmission."""
        # Send simple test parameters
        test_value = (time.time() % 2.0) / 2.0  # Oscillate between 0-1

        if "MouthOpen" not in self.smoothers:
            self.smoothers["MouthOpen"] = ParameterSmoother()

        smoothed = self.smoothers["MouthOpen"].smooth(test_value, "MouthOpen")
        self.osc_sender.send_custom_parameter("MouthOpen", smoothed)

        if self.debug:
            click.echo(f"MouthOpen: {smoothed:.3f}")


@click.command()
@click.option(
    "--ip",
    default=config.VRCHAT_OSC_IP,
    help="VRChat IP address",
    show_default=True,
)
@click.option(
    "--port",
    type=int,
    default=config.VRCHAT_OSC_PORT,
    help="OSC port",
    show_default=True,
)
@click.option(
    "--camera",
    type=int,
    default=config.CAMERA_INDEX,
    help="Camera ID",
    show_default=True,
)
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--no-display", is_flag=True, help="Disable screen display")
def main(ip: str, port: int, camera: int, *, debug: bool, no_display: bool) -> None:
    """VRChat Webcam Tracker - Command Line Version.

    This tool tracks facial expressions and hand movements using your webcam
    and sends the data to VRChat via OSC protocol.
    """
    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    click.echo("VRChat Webcam Tracker (Command Line Version)")
    click.echo(f"VRChat OSC: {ip}:{port}")
    click.echo(f"Camera ID: {camera}")
    click.echo("-" * 50)

    # Create and start tracker
    tracker = SimpleTracker(ip=ip, port=port, camera_index=camera, debug=debug)

    try:
        tracker.start(show_video=not no_display)
    except (OSError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
