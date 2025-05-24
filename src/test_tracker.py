import unittest
from unittest.mock import Mock, patch
import numpy as np
import cv2
from trackers import FaceTracker, HandTracker
from osc_sender import VRChatOSCSender, ParameterSmoother


class TestFaceTracker(unittest.TestCase):
    """Test class for FaceTracker"""

    def setUp(self):
        self.face_tracker = FaceTracker()

    def test_initialization(self):
        """Test initialization"""
        self.assertIsNotNone(self.face_tracker.face_cascade)
        self.assertIsNotNone(self.face_tracker.eye_cascade)
        self.assertIsNotNone(self.face_tracker.mouth_cascade)
        self.assertEqual(self.face_tracker.prev_mouth_open, 0.0)
        self.assertEqual(self.face_tracker.prev_eye_blink_left, 0.0)
        self.assertEqual(self.face_tracker.prev_eye_blink_right, 0.0)

    @patch("cv2.cvtColor")
    @patch.object(cv2.CascadeClassifier, "detectMultiScale")
    def test_detect_face_expression_no_face(self, mock_detectMultiScale, mock_cvtColor):
        """Test when no face is detected"""
        # Mock setup
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cvtColor.return_value = mock_image

        # Mock no face detection
        mock_detectMultiScale.return_value = np.array([])

        result = self.face_tracker.detect_face_expression(mock_image)

        # Verify all parameters are 0.0
        expected_keys = [
            "MouthOpen",
            "LeftEyeBlink",
            "RightEyeBlink",
            "LeftEyebrowRaise",
            "RightEyebrowRaise",
            "MouthSmile",
        ]

        for key in expected_keys:
            self.assertIn(key, result)
            self.assertEqual(result[key], 0.0)

    def test_detect_mouth_movement(self):
        """Test mouth movement detection"""
        # Create test ROI data
        roi_gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        roi_color = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = self.face_tracker._detect_mouth_movement(roi_gray, roi_color)

        # Verify result is within 0.0-1.0 range
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)


class TestHandTracker(unittest.TestCase):
    """Test class for HandTracker"""

    def setUp(self):
        self.hand_tracker = HandTracker()

    def test_initialization(self):
        """Test initialization"""
        self.assertIsNotNone(self.hand_tracker.bg_subtractor)
        self.assertEqual(self.hand_tracker.prev_left_arm, 0.0)
        self.assertEqual(self.hand_tracker.prev_right_arm, 0.0)

    def test_detect_hand_pose_no_detection(self):
        """Test when no hands or arms are detected"""
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)

        result = self.hand_tracker.detect_hand_pose(mock_image)

        # Verify all parameters are returned (values may not be 0.0 due to motion detection)
        expected_keys = [
            "LeftArmRaise",
            "RightArmRaise",
            "LeftHandOpen",
            "RightHandOpen",
            "LeftHandFist",
            "RightHandFist",
            "LeftHandPoint",
            "RightHandPoint",
        ]

        for key in expected_keys:
            self.assertIn(key, result)
            # Values are within valid range
            self.assertGreaterEqual(result[key], 0.0)
            self.assertLessEqual(result[key], 1.0)

    def test_motion_detection(self):
        """Test motion detection functionality"""
        # Create two different images to trigger motion detection
        image1 = np.zeros((480, 640, 3), dtype=np.uint8)
        image2 = np.ones((480, 640, 3), dtype=np.uint8) * 255

        # Process first image to initialize background subtractor
        self.hand_tracker.detect_hand_pose(image1)

        # Process second image to detect motion
        result = self.hand_tracker.detect_hand_pose(image2)

        # Verify that motion is detected
        self.assertGreater(result["LeftArmRaise"] + result["RightArmRaise"], 0.0)


class TestVRChatOSCSender(unittest.TestCase):
    """Test class for VRChatOSCSender"""

    def setUp(self):
        with patch("pythonosc.udp_client.SimpleUDPClient"):
            self.osc_sender = VRChatOSCSender("127.0.0.1", 9000)

    def test_initialization(self):
        """Test initialization"""
        self.assertEqual(self.osc_sender.ip, "127.0.0.1")
        self.assertEqual(self.osc_sender.port, 9000)
        self.assertIsNotNone(self.osc_sender.client)

    @patch("time.time")
    def test_send_face_tracking_data(self, mock_time):
        """Test face data transmission"""
        # Set up time sequence to ensure messages are sent
        mock_time.side_effect = [0.0, 1.0]  # First call returns 0.0, second returns 1.0

        test_data = {"MouthOpen": 0.5, "LeftEyeBlink": 0.2, "RightEyeBlink": 0.3}

        self.osc_sender.client.send_message = Mock()

        # Reset last_send_time to ensure message sending
        self.osc_sender.last_send_time = -1.0

        self.osc_sender.send_face_tracking_data(test_data)

        # Verify messages were sent
        self.assertEqual(self.osc_sender.client.send_message.call_count, 3)

    def test_send_custom_parameter(self):
        """Test custom parameter transmission"""
        self.osc_sender.client.send_message = Mock()

        self.osc_sender.send_custom_parameter("TestParam", 0.8)

        # Verify correct address and value were sent
        self.osc_sender.client.send_message.assert_called_once_with(
            "/avatar/parameters/TestParam", 0.8
        )


class TestParameterSmoother(unittest.TestCase):
    """Test class for ParameterSmoother"""

    def setUp(self):
        self.smoother = ParameterSmoother(smoothing_factor=0.8)

    def test_first_smooth(self):
        """Test first smoothing"""
        test_data = {"param1": 1.0, "param2": 0.5}
        result = self.smoother.smooth_parameters(test_data)

        # First time returns original values
        self.assertEqual(result, test_data)

    def test_subsequent_smooth(self):
        """Test second and subsequent smoothing"""
        # First time
        first_data = {"param1": 1.0}
        self.smoother.smooth_parameters(first_data)

        # Second time
        second_data = {"param1": 0.0}
        result = self.smoother.smooth_parameters(second_data)

        # Verify smoothing is applied
        expected = 0.8 * 1.0 + 0.2 * 0.0  # 0.8
        self.assertAlmostEqual(result["param1"], expected, places=5)

    def test_reset(self):
        """Test reset functionality"""
        test_data = {"param1": 1.0}
        self.smoother.smooth_parameters(test_data)

        # After reset, previous values should be cleared
        self.smoother.reset()
        self.assertEqual(len(self.smoother.previous_values), 0)


class TestIntegration(unittest.TestCase):
    """Integration test class"""

    @patch("cv2.VideoCapture")
    def test_camera_initialization(self, mock_video_capture):
        """Integration test for camera initialization"""
        try:
            from main import WebcamTracker
        except ImportError:
            # Skip test if main module is not available
            self.skipTest("WebcamTracker module not available")

        # Mock camera setup
        mock_camera = Mock()
        mock_camera.isOpened.return_value = True
        mock_video_capture.return_value = mock_camera

        tracker = WebcamTracker()
        result = tracker.initialize_camera()

        self.assertTrue(result)
        mock_camera.set.assert_called()
        mock_camera.isOpened.assert_called()


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
