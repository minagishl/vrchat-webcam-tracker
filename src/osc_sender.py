"""VRChat Webcam Tracker - OSC Sender Module.

This module handles sending OSC messages to VRChat for facial expression and hand tracking data.
It includes classes for sending data, smoothing parameters, and debugging OSC messages.
"""

from __future__ import annotations

import time

import click
from pythonosc import udp_client

import config


class VRChatOSCSender:
    """Class for sending OSC messages to VRChat."""

    def __init__(self, ip: str | None = None, port: int | None = None) -> None:
        """Initialize VRChat OSC sender.

        Args:
            ip: VRChat OSC IP address.
            port: VRChat OSC port.

        """
        self.ip = ip or config.VRCHAT_OSC_IP
        self.port = port or config.VRCHAT_OSC_PORT
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        self.last_send_time = 0
        self.send_interval = 1.0 / 60.0  # Send at 60FPS

        click.echo(
            f"VRChat OSC client initialized: {self.ip}:{self.port}",
        )

    def send_hand_tracking_data(self, hand_data: dict[str, float]) -> None:
        """Send hand and arm tracking data to VRChat."""
        current_time = time.time()
        if current_time - self.last_send_time < self.send_interval:
            return

        try:
            # Send to VRChat's standard OSC addresses
            for param_name, value in hand_data.items():
                address = f"/avatar/parameters/{param_name}"
                self.client.send_message(address, value)

            self.last_send_time = current_time

        except (OSError, RuntimeError) as e:
            click.echo(
                f"Hand & arm data transmission error: {e}",
            )

    def send_combined_data(
        self,
        face_data: dict[str, float],
        hand_data: dict[str, float],
    ) -> None:
        """Send combined facial expression and hand & arm data."""
        current_time = time.time()
        if current_time - self.last_send_time < self.send_interval:
            return

        try:
            # Send all parameters
            all_data = {**face_data, **hand_data}

            for param_name, value in all_data.items():
                address = f"/avatar/parameters/{param_name}"
                self.client.send_message(address, value)

            self.last_send_time = current_time

        except (OSError, RuntimeError) as e:
            click.echo(
                f"Combined data transmission error: {e}",
            )

    def send_body_tracking_data(self, body_data: dict[str, tuple[float, float, float]]) -> None:
        """Send body tracking data to VRChat via OSC.

        Args:
            body_data: Dictionary with landmark data in format {"Landmark{index}": (x, y, z)}.

        """
        current_time = time.time()
        if current_time - self.last_send_time < self.send_interval:
            return

        try:
            # Map landmark data to specific tracker IDs (1-8) and head tracker
            landmark_list = list(body_data.items())

            # Send data for trackers 1-8
            for tracker_id in range(1, 9):
                if tracker_id - 1 < len(landmark_list):
                    # Use landmark data for this tracker
                    _landmark_name, (x, y, z) = landmark_list[tracker_id - 1]
                    position_data = [x, y, z]
                    rotation_data = [0.0, 0.0, 0.0, 1.0]  # Quaternion (x, y, z, w)
                else:
                    # Use default values if no landmark data available
                    position_data = [0.0, 0.0, 0.0]
                    rotation_data = [0.0, 0.0, 0.0, 1.0]

                # Send position and rotation for each tracker
                position_address = f"/tracking/trackers/{tracker_id}/position"
                rotation_address = f"/tracking/trackers/{tracker_id}/rotation"

                self.client.send_message(position_address, position_data)
                self.client.send_message(rotation_address, rotation_data)

            # Send head tracker data (use first landmark or nose if available)
            if landmark_list:
                # Use the first landmark (usually nose/head) for head tracking
                _landmark_name, (x, y, z) = landmark_list[0]
                head_position = [x, y, z]
                head_rotation = [0.0, 0.0, 0.0, 1.0]
            else:
                head_position = [0.0, 0.0, 0.0]
                head_rotation = [0.0, 0.0, 0.0, 1.0]

            # Send head tracker data
            head_position_address = "/tracking/trackers/head/position"
            head_rotation_address = "/tracking/trackers/head/rotation"

            self.client.send_message(head_position_address, head_position)
            self.client.send_message(head_rotation_address, head_rotation)

            self.last_send_time = current_time

        except (OSError, RuntimeError) as e:
            click.echo(
                f"Body tracking data transmission error: {e}",
            )

    def send_tracking_data(
        self,
        face_data: dict[str, float],
        body_data: dict[str, tuple[float, float, float]] | None = None,
    ) -> None:
        """Send all tracking data using the new tracking format."""
        current_time = time.time()
        if current_time - self.last_send_time < self.send_interval:
            return

        try:
            # Create synthetic body tracking data from face/hand data if no body data available
            if body_data is None or len(body_data) == 0:
                body_data = {}
                # Use face data to create head tracking
                if face_data:
                    # Convert head pose data to position/rotation
                    head_x = face_data.get("HeadTurnLeft", 0.0) - face_data.get(
                        "HeadTurnRight",
                        0.0,
                    )
                    head_y = face_data.get("HeadTiltUp", 0.0) - face_data.get("HeadTiltDown", 0.0)
                    head_z = face_data.get("HeadTiltLeft", 0.0) - face_data.get(
                        "HeadTiltRight",
                        0.0,
                    )
                    body_data["Head"] = (head_x, head_y, head_z)

                # Create placeholder data for other trackers
                for i in range(8):
                    if f"Tracker{i}" not in body_data:
                        body_data[f"Tracker{i}"] = (0.0, 0.0, 0.0)

            # Send body tracking data using the new format
            self.send_body_tracking_data(body_data)

            self.last_send_time = current_time

        except (OSError, RuntimeError) as e:
            click.echo(
                f"Tracking data transmission error: {e}",
            )

    def send_custom_parameter(self, parameter_name: str, value: float) -> None:
        """Send custom parameter."""
        try:
            address = f"/avatar/parameters/{parameter_name}"
            self.client.send_message(address, value)
        except (OSError, RuntimeError) as e:
            click.echo(
                f"Custom parameter transmission error: {e}",
            )

    def test_connection(self) -> bool:
        """Execute connection test."""
        try:
            test_address = "/avatar/parameters/TestConnection"
            self.client.send_message(test_address, 1.0)
            click.echo(
                "VRChat OSC connection test transmission completed",
            )
        except (OSError, RuntimeError) as e:
            click.echo(
                f"VRChat connection test failed: {e}",
            )
            return False
        else:
            return True


class OSCDebugger:
    """Debug class for OSC messages."""

    def __init__(self) -> None:
        """Initialize OSC debugger."""
        self.message_count = 0
        self.last_debug_time = 0
        self.debug_interval = 1.0  # Display debug info every 1 second

    def log_parameters(self, face_data: dict[str, float], hand_data: dict[str, float]) -> None:
        """Log parameter values."""
        current_time = time.time()
        if current_time - self.last_debug_time < self.debug_interval:
            return

        click.echo("\n=== VRChat Parameter Values ===")
        click.echo("【Facial Expressions】")
        for param, value in face_data.items():
            click.echo(f"  {param}: {value:.3f}")

        click.echo("【Hand & Arm】")
        for param, value in hand_data.items():
            click.echo(f"  {param}: {value:.3f}")

        click.echo(f"Message transmission count: {self.message_count}")
        click.echo("=" * 30)

        self.last_debug_time = current_time
        self.message_count += 1


class ParameterSmoother:
    """Class for smoothing parameter values."""

    def __init__(self, smoothing_factor: float = 0.8) -> None:
        """Initialize parameter smoother.

        Args:
            smoothing_factor: Smoothing factor (0-1). Higher values mean more smoothing.

        """
        self.smoothing_factor = smoothing_factor
        self.previous_values = {}

    def smooth_parameters(self, new_data: dict[str, float]) -> dict[str, float]:
        """Smooth parameter values."""
        smoothed_data = {}

        for param_name, new_value in new_data.items():
            if param_name in self.previous_values:
                # Use exponential moving average for smoothing
                smoothed_value = (
                    self.smoothing_factor * self.previous_values[param_name]
                    + (1 - self.smoothing_factor) * new_value
                )
            else:
                smoothed_value = new_value

            self.previous_values[param_name] = smoothed_value
            smoothed_data[param_name] = smoothed_value

        return smoothed_data

    def smooth(self, value: float, param_name: str = "default") -> float:
        """Smooth a single value."""
        if param_name in self.previous_values:
            smoothed_value = (
                self.smoothing_factor * self.previous_values[param_name]
                + (1 - self.smoothing_factor) * value
            )
        else:
            smoothed_value = value

        self.previous_values[param_name] = smoothed_value
        return smoothed_value

    def reset(self) -> None:
        """Reset previous values."""
        self.previous_values.clear()
