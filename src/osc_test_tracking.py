"""Test script for new tracking data format.

This script tests the new OSC tracking data format that sends to:
/tracking/trackers/1/position through /tracking/trackers/8/position
/tracking/trackers/1/rotation through /tracking/trackers/8/rotation
/tracking/trackers/head/position
/tracking/trackers/head/rotation
"""

import math
import time

from click import echo

from osc_sender import VRChatOSCSender


def main() -> None:
    """Test the new tracking data format."""
    echo("Testing new tracking data format...")

    # Initialize OSC sender
    osc_sender = VRChatOSCSender()

    # Test body tracking data with sample landmark data
    sample_body_data = {}

    # Create sample landmark data (simulating MediaPipe pose landmarks)
    for i in range(13):  # Simulate 13 upper body landmarks
        # Create some movement patterns for testing
        t = time.time()
        x = 0.5 + 0.2 * math.sin(t + i * 0.5)  # X position (0-1 range)
        y = 0.5 + 0.2 * math.cos(t + i * 0.3)  # Y position (0-1 range)
        z = 0.1 * math.sin(t * 2 + i)  # Z depth (-0.1 to 0.1 range)

        sample_body_data[f"Landmark{i}"] = (x, y, z)

    echo(f"Sending test data for {len(sample_body_data)} landmarks...")
    echo("This will send data to:")
    echo("- /tracking/trackers/1/position through /tracking/trackers/8/position")
    echo("- /tracking/trackers/1/rotation through /tracking/trackers/8/rotation")
    echo("- /tracking/trackers/head/position")
    echo("- /tracking/trackers/head/rotation")
    echo()

    # Send test data for 10 seconds
    test_duration_seconds = 10
    start_time = time.time()
    frame_count = 0

    try:
        while time.time() - start_time < test_duration_seconds:
            # Update sample data with animation
            for i in range(13):
                t = time.time()
                x = 0.5 + 0.2 * math.sin(t + i * 0.5)
                y = 0.5 + 0.2 * math.cos(t + i * 0.3)
                z = 0.1 * math.sin(t * 2 + i)
                sample_body_data[f"Landmark{i}"] = (x, y, z)

            # Send the body tracking data
            osc_sender.send_body_tracking_data(sample_body_data)

            frame_count += 1
            if frame_count % 60 == 0:  # Print status every 60 frames (1 second at 60fps)
                echo(f"Sent {frame_count} frames ({frame_count // 60} seconds)")

            time.sleep(1.0 / 60.0)  # 60 FPS

    except KeyboardInterrupt:
        echo("\nTest interrupted by user")

    echo(f"\nTest completed. Sent {frame_count} frames total.")
    echo("Check your OSC receiver to verify the new tracking data format is working.")


if __name__ == "__main__":
    main()
