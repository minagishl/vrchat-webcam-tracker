"""VRChat Webcam Tracker - Command Line Version.

This tool tracks facial expressions and hand movements using your webcam
and sends the data to VRChat via OSC protocol.
"""

from __future__ import annotations

import signal
import sys
import time
from typing import TYPE_CHECKING

import click
import cv2

# Handle both direct execution and PyInstaller packaging
try:
    from . import config
except ImportError:
    import config

if TYPE_CHECKING:
    import numpy as np

try:
    from .osc_sender import ParameterSmoother, VRChatOSCSender
    from .trackers import FaceTracker, HandTracker
except ImportError:
    from osc_sender import ParameterSmoother, VRChatOSCSender
    from trackers import FaceTracker, HandTracker

ESC_KEY_CODE = 27  # ESC key code
MIN_DISPLAY_THRESHOLD = 0.1  # Minimum parameter value to display in debug mode


def signal_handler(_sig: int, _frame: object) -> None:
    """Ctrl+C handler."""
    click.echo("\nStopping tracking...")
    sys.exit(0)


def get_camera_input() -> int:
    """Get camera ID from user input with interactive selection.

    Returns:
        int: Selected camera ID.

    """
    click.echo("Camera ID Selection")
    click.echo("-" * 50)

    try:
        while True:
            camera_id = click.prompt("Enter camera ID", type=int, default=config.CAMERA_INDEX)

            # Test if camera can be opened
            test_cap = cv2.VideoCapture(camera_id)
            if test_cap.isOpened():
                test_cap.release()

                # Clear the camera selection lines
                click.echo("\033[A\033[K" * 3, nl=False)  # Move up 3 lines and clear them

                click.echo(f"Selected > {camera_id}")

                return camera_id
            click.echo(f"Error: Cannot open camera {camera_id}. Please try another ID.", err=True)

    except click.Abort:
        click.echo("\nCamera selection cancelled.")
        sys.exit(0)
    except (ValueError, TypeError) as e:
        click.echo(f"Error: {e}. Please enter a valid camera ID.", err=True)
        return get_camera_input()  # Retry on error


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

        # Face detection
        face_data = self.face_tracker.detect(frame_rgb)
        if face_data and self.debug:
            click.echo(f"Face detection: {list(face_data.keys())}")

        # Hand detection
        hand_data = self.hand_tracker.detect(frame_rgb)
        if hand_data and self.debug:
            click.echo(f"Hand detection: {list(hand_data.keys())}")

        # OSC transmission - send actual tracking data
        self.send_tracking_data(face_data, hand_data)

    def send_tracking_data(self, face_data: dict[str, float], hand_data: dict[str, float]) -> None:
        """Send actual tracking data to VRChat via OSC."""
        # Initialize smoothers for all parameters if they don't exist
        all_params = {**face_data, **hand_data}

        for param_name in all_params:
            if param_name not in self.smoothers:
                self.smoothers[param_name] = ParameterSmoother()

        # Smooth and send face data
        smoothed_face_data = {}
        for param_name, value in face_data.items():
            smoothed_value = self.smoothers[param_name].smooth(value, param_name)
            smoothed_face_data[param_name] = smoothed_value

        # Smooth and send hand data
        smoothed_hand_data = {}
        for param_name, value in hand_data.items():
            smoothed_value = self.smoothers[param_name].smooth(value, param_name)
            smoothed_hand_data[param_name] = smoothed_value

        # Send combined data to VRChat
        self.osc_sender.send_combined_data(smoothed_face_data, smoothed_hand_data)
        if self.debug:
            # Display all parameters being sent
            for param_name, value in {**smoothed_face_data, **smoothed_hand_data}.items():
                if value > MIN_DISPLAY_THRESHOLD:  # Only show parameters with significant values
                    click.echo(f"{param_name}: {value:.3f}")

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
    help="Camera ID (if not specified, interactive selection will be prompted)",
)
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--no-display", is_flag=True, help="Disable screen display")
def main(ip: str, port: int, camera: int | None, *, debug: bool, no_display: bool) -> None:
    """VRChat Webcam Tracker - Command Line Version.

    This tool tracks facial expressions and hand movements using your webcam
    and sends the data to VRChat via OSC protocol.
    """
    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    click.echo("VRChat Webcam Tracker (Command Line Version)")
    click.echo(f"VRChat OSC: {ip}:{port}")

    # Camera ID selection - interactive if not specified via --camera
    if camera is None:
        camera = get_camera_input()
    else:
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
