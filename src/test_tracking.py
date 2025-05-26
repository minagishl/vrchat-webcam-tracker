"""Test script to verify main application sends tracking data in new format."""

import time

from click import echo

from osc_sender import VRChatOSCSender


def test_main_tracking_format() -> None:
    """Test that main application sends data in the new tracking format."""
    echo("Testing main application tracking format...")

    # Create OSC sender
    osc_sender = VRChatOSCSender()

    # Simulate face data that would come from face tracker
    face_data = {
        "HeadTurnLeft": 0.3,
        "HeadTurnRight": 0.0,
        "HeadTiltUp": 0.2,
        "HeadTiltDown": 0.0,
        "HeadTiltLeft": 0.1,
        "HeadTiltRight": 0.0,
        "MouthOpen": 0.5,
        "LeftEyeBlink": 0.0,
        "RightEyeBlink": 0.0,
    }

    # No body tracking data (simulating the case where MediaPipe is not available)
    body_data = None

    echo("Sending face and hand data using new tracking format...")
    echo("Expected outputs:")
    echo("- /tracking/trackers/head/position (from face data)")
    echo("- /tracking/trackers/head/rotation")
    echo("- /tracking/trackers/1/position through /tracking/trackers/8/position")
    echo("- /tracking/trackers/1/rotation through /tracking/trackers/8/rotation")
    echo()

    # Send data using the new tracking method
    for i in range(5):
        osc_sender.send_tracking_data(face_data, body_data)
        echo(f"Sent frame {i + 1}")
        time.sleep(0.1)

    echo("\nTest completed. The main application should now send tracking data to:")
    echo("- /tracking/trackers/head/position")
    echo("- /tracking/trackers/head/rotation")
    echo("- /tracking/trackers/1-8/position")
    echo("- /tracking/trackers/1-8/rotation")
    echo("instead of /avatar/parameters/HeadTiltLeft etc.")


if __name__ == "__main__":
    test_main_tracking_format()
