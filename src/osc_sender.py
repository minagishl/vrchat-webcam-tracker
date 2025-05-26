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

    def send_face_tracking_data(self, face_data: dict[str, float]) -> None:
        """Send facial expression tracking data to VRChat."""
        current_time = time.time()
        if current_time - self.last_send_time < self.send_interval:
            return

        try:
            # Send to VRChat's standard OSC addresses
            for param_name, value in face_data.items():
                address = f"/avatar/parameters/{param_name}"
                self.client.send_message(address, value)

            self.last_send_time = current_time

        except (OSError, RuntimeError) as e:
            click.echo(
                f"Facial expression data transmission error: {e}",
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
            # Send body tracking data to VRChat's tracking system
            for i, (_landmark_name, (x, y, z)) in enumerate(body_data.items()):
                # Send position data
                position_address = f"/tracking/trackers/{i}/position"
                self.client.send_message(position_address, [x, y, z])

                # Send rotation data (fixed values as requested)
                rotation_address = f"/tracking/trackers/{i}/rotation"
                self.client.send_message(rotation_address, [0.0, 0.0, 0.0])

            self.last_send_time = current_time

        except (OSError, RuntimeError) as e:
            click.echo(
                f"Body tracking data transmission error: {e}",
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
