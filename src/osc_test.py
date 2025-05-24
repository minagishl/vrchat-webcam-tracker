#!/usr/bin/env python3
"""
VRChat Webcam Tracker - Test & Demo Version
Test OSC functionality without camera access
"""

import argparse
import signal
import sys
import time
import math
import config
from osc_sender import VRChatOSCSender, ParameterSmoother


def signal_handler(sig, frame):
    """Ctrl+C handler"""
    print("\nStopping test...")
    sys.exit(0)


class OSCTestRunner:
    """OSC functionality test runner"""

    def __init__(self, ip, port, debug=False):
        self.ip = ip
        self.port = port
        self.debug = debug

        # Initialize OSC sender and smoothers
        self.osc_sender = VRChatOSCSender(ip, port)
        self.smoothers = {}

        self.running = False

    def start_test(self, duration=30):
        """Start OSC test"""
        print(f"Starting OSC test - running for {duration} seconds")
        print("Sending various facial expression parameters to VRChat...")

        self.running = True
        start_time = time.time()

        try:
            while self.running and (time.time() - start_time) < duration:
                self.send_test_parameters()
                time.sleep(0.1)  # 10Hz

        except KeyboardInterrupt:
            print("\nKeyboard interrupt")
        finally:
            self.stop()

        return True

    def stop(self):
        """Stop test"""
        self.running = False
        if self.debug:
            print()  # Add newline to clear the debug line
        print("OSC test stopped")

    def send_test_parameters(self):
        """Send test parameters"""
        current_time = time.time()

        # Generate test parameters with various waveforms
        test_params = {
            "MouthOpen": (math.sin(current_time * 2) + 1) / 2,  # 0-1 sine wave
            "MouthSmile": (math.sin(current_time * 1.5 + 1) + 1) / 2,
            "EyeBlinkLeft": max(0, math.sin(current_time * 3)),
            "EyeBlinkRight": max(0, math.sin(current_time * 3 + 0.1)),
            "BrowUp": (math.sin(current_time * 0.8) + 1) / 2,
            "BrowDown": (math.sin(current_time * 0.6 + 2) + 1) / 2,
        }

        for param, value in test_params.items():
            # Smoothing
            if param not in self.smoothers:
                self.smoothers[param] = ParameterSmoother()

            smoothed_value = self.smoothers[param].smooth(value, param)
            self.osc_sender.send_custom_parameter(param, smoothed_value)

        if self.debug:
            # Create a single line output that overwrites the previous one
            debug_output = " | ".join(
                [
                    f"{param}: {self.smoothers[param].previous_values.get(param, 0.0):.3f}"
                    for param in test_params.keys()
                    if param in self.smoothers
                ]
            )
            print(f"\r{debug_output}", end="", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="VRChat OSC functionality test - camera-free version"
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
        "--duration",
        type=int,
        default=30,
        help="Test duration in seconds (default: 30)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    print("VRChat OSC Functionality Test")
    print(f"VRChat OSC: {args.ip}:{args.port}")
    print(f"Test duration: {args.duration} seconds")
    print("-" * 50)

    # Create and start test runner
    tester = OSCTestRunner(ip=args.ip, port=args.port, debug=args.debug)

    try:
        tester.start_test(duration=args.duration)
        print("Test completed!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
