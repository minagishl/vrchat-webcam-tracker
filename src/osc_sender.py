from pythonosc import udp_client
import time
from typing import Dict, Optional
import config


class VRChatOSCSender:
    """Class for sending OSC messages to VRChat"""

    def __init__(self, ip: Optional[str] = None, port: Optional[int] = None):
        self.ip = ip or config.VRCHAT_OSC_IP
        self.port = port or config.VRCHAT_OSC_PORT
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        self.last_send_time = 0
        self.send_interval = 1.0 / 60.0  # Send at 60FPS

        print(f"VRChat OSC client initialized: {self.ip}:{self.port}")

    def send_face_tracking_data(self, face_data: Dict[str, float]):
        """Send facial expression tracking data to VRChat"""
        current_time = time.time()
        if current_time - self.last_send_time < self.send_interval:
            return

        try:
            # Send to VRChat's standard OSC addresses
            for param_name, value in face_data.items():
                address = f"/avatar/parameters/{param_name}"
                self.client.send_message(address, value)

            self.last_send_time = current_time

        except Exception as e:
            print(f"Facial expression data transmission error: {e}")

    def send_hand_tracking_data(self, hand_data: Dict[str, float]):
        """Send hand and arm tracking data to VRChat"""
        current_time = time.time()
        if current_time - self.last_send_time < self.send_interval:
            return

        try:
            # Send to VRChat's standard OSC addresses
            for param_name, value in hand_data.items():
                address = f"/avatar/parameters/{param_name}"
                self.client.send_message(address, value)

            self.last_send_time = current_time

        except Exception as e:
            print(f"Hand & arm data transmission error: {e}")

    def send_combined_data(
        self, face_data: Dict[str, float], hand_data: Dict[str, float]
    ):
        """Send combined facial expression and hand & arm data"""
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

        except Exception as e:
            print(f"Combined data transmission error: {e}")

    def send_custom_parameter(self, parameter_name: str, value: float):
        """Send custom parameter"""
        try:
            address = f"/avatar/parameters/{parameter_name}"
            self.client.send_message(address, value)
        except Exception as e:
            print(f"Custom parameter transmission error: {e}")

    def test_connection(self):
        """Execute connection test"""
        try:
            test_address = "/avatar/parameters/TestConnection"
            self.client.send_message(test_address, 1.0)
            print("VRChat OSC connection test transmission completed")
            return True
        except Exception as e:
            print(f"VRChat connection test failed: {e}")
            return False


class OSCDebugger:
    """Debug class for OSC messages"""

    def __init__(self):
        self.message_count = 0
        self.last_debug_time = 0
        self.debug_interval = 1.0  # Display debug info every 1 second

    def log_parameters(self, face_data: Dict[str, float], hand_data: Dict[str, float]):
        """Log parameter values"""
        current_time = time.time()
        if current_time - self.last_debug_time < self.debug_interval:
            return

        print("\n=== VRChat Parameter Values ===")
        print("【Facial Expressions】")
        for param, value in face_data.items():
            print(f"  {param}: {value:.3f}")

        print("【Hand & Arm】")
        for param, value in hand_data.items():
            print(f"  {param}: {value:.3f}")

        print(f"Message transmission count: {self.message_count}")
        print("=" * 30)

        self.last_debug_time = current_time
        self.message_count += 1


class ParameterSmoother:
    """Class for smoothing parameter values"""

    def __init__(self, smoothing_factor: float = 0.8):
        self.smoothing_factor = smoothing_factor
        self.previous_values = {}

    def smooth_parameters(self, new_data: Dict[str, float]) -> Dict[str, float]:
        """Smooth parameter values"""
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
        """Smooth a single value"""
        if param_name in self.previous_values:
            smoothed_value = (
                self.smoothing_factor * self.previous_values[param_name]
                + (1 - self.smoothing_factor) * value
            )
        else:
            smoothed_value = value

        self.previous_values[param_name] = smoothed_value
        return smoothed_value

    def reset(self):
        """Reset previous values"""
        self.previous_values.clear()
