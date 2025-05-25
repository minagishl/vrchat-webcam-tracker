"""VRChat Webcam Tracker - Face and Hand Tracking Module.

This module contains classes for tracking facial expressions and hand movements using OpenCV.
"""

import sys
from pathlib import Path
from typing import cast

import cv2
import numpy as np


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""

    def _raise_attribute_error() -> None:
        raise AttributeError

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, "_MEIPASS", None)
        if base_path is None:
            _raise_attribute_error()
    except AttributeError:
        base_path = Path(__file__).parent.parent

    # Ensure base_path is not None before using it
    if base_path is None:
        base_path = Path(__file__).parent.parent

    return str(Path(base_path) / relative_path)


class FaceTracker:
    """Class for tracking facial expressions (using OpenCV Haar cascades)."""

    # Head pose detection thresholds
    HEAD_MOVEMENT_THRESHOLD = 0.1
    FACE_ASPECT_RATIO_THRESHOLD = 1.2

    def __init__(self) -> None:
        """Initialize the FaceTracker with Haar cascades and smoothing variables."""
        # Initialize Haar cascade classifiers
        # Try to load from packaged resources first, fallback to cv2.data
        try:
            # For PyInstaller packaged application
            face_cascade_path = get_resource_path("cv2/data/haarcascade_frontalface_default.xml")
            eye_cascade_path = get_resource_path("cv2/data/haarcascade_eye.xml")
            mouth_cascade_path = get_resource_path("cv2/data/haarcascade_smile.xml")
        except (AttributeError, FileNotFoundError, OSError):
            # Fallback to original cv2.data paths
            haarcascades_path = cast("str", cv2.data.haarcascades)
            face_cascade_path = str(Path(haarcascades_path) / "haarcascade_frontalface_default.xml")
            eye_cascade_path = str(Path(haarcascades_path) / "haarcascade_eye.xml")
            mouth_cascade_path = str(Path(haarcascades_path) / "haarcascade_smile.xml")

        self.face_cascade = cv2.CascadeClassifier()
        if not self.face_cascade.load(face_cascade_path):
            error_msg = f"Failed to load Haar cascade from '{face_cascade_path}'"
            raise OSError(error_msg)

        self.eye_cascade = cv2.CascadeClassifier()
        if not self.eye_cascade.load(eye_cascade_path):
            error_msg = f"Failed to load Haar cascade from '{eye_cascade_path}'"
            raise OSError(error_msg)

        self.mouth_cascade = cv2.CascadeClassifier()
        if not self.mouth_cascade.load(mouth_cascade_path):
            error_msg = f"Failed to load Haar cascade from '{mouth_cascade_path}'"
            raise OSError(error_msg)

        # Save previous values (for smoothing)
        self.prev_mouth_open = 0.0
        self.prev_eye_blink_left = 0.0
        self.prev_eye_blink_right = 0.0

    def detect(self, image: np.ndarray) -> dict[str, float]:
        """Detect facial expressions using the main detection method.

        Args:
            image: Input image (BGR format).

        Returns:
            Dictionary with facial expression parameters.

        """
        return self.detect_face_expression(image)

    def detect_face_expression(self, image: np.ndarray) -> dict[str, float]:
        """Detect facial expressions and return VRChat parameters."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        expression_data = {
            "MouthOpen": 0.0,
            "LeftEyeBlink": 0.0,
            "RightEyeBlink": 0.0,
            "LeftEyebrowRaise": 0.0,
            "RightEyebrowRaise": 0.0,
            "MouthSmile": 0.0,
            # Head pose parameters
            "HeadTiltLeft": 0.0,
            "HeadTiltRight": 0.0,
            "HeadTiltUp": 0.0,
            "HeadTiltDown": 0.0,
            "HeadTurnLeft": 0.0,
            "HeadTurnRight": 0.0,
        }

        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            # Select the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face

            # Extract face region
            roi_gray = gray[y : y + h, x : x + w]
            roi_color = image[y : y + h, x : x + w]

            # Mouth detection
            mouth_open = self._detect_mouth_movement(roi_gray, roi_color)
            expression_data["MouthOpen"] = mouth_open

            # Eye detection
            eye_blink = self._detect_eye_blink(roi_gray, roi_color)
            expression_data["LeftEyeBlink"] = eye_blink
            expression_data["RightEyeBlink"] = eye_blink

            # Smile detection
            smile = self._detect_smile(roi_gray)
            expression_data["MouthSmile"] = smile

            # Head pose detection
            head_pose = self._detect_head_pose(face, image.shape)
            expression_data.update(head_pose)

            # Eyebrow movement is substituted with random values (difficult to implement)
            expression_data["LeftEyebrowRaise"] = 0.0
            expression_data["RightEyebrowRaise"] = 0.0

        return expression_data

    def _detect_mouth_movement(
        self,
        roi_gray: np.ndarray,
        _roi_color: np.ndarray,
    ) -> float:
        """Detect mouth movement."""
        # Mouth region (lower half of face)
        mouth_region_y = int(roi_gray.shape[0] * 0.6)
        mouth_roi = roi_gray[mouth_region_y:, :]

        # Detect mouth contour with edge detection
        edges = cv2.Canny(mouth_roi, 50, 150)
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        if contours:
            # Assume largest contour is the mouth
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            # Estimate mouth opening based on area
            mouth_open_ratio = min(1.0, area / 100.0)  # Normalize

            # Smoothing
            smoothed = 0.7 * self.prev_mouth_open + 0.3 * mouth_open_ratio
            self.prev_mouth_open = smoothed
            return smoothed

        return 0.0

    def _detect_eye_blink(self, roi_gray: np.ndarray, _roi_color: np.ndarray) -> float:
        """Detect eye blinking."""
        eyes = self.eye_cascade.detectMultiScale(roi_gray)

        # If no eyes detected, likely blinking; if eyes detected, they are open
        blink_value = 0.8 if len(eyes) == 0 else 0.0

        # Smoothing
        smoothed = 0.8 * self.prev_eye_blink_left + 0.2 * blink_value
        self.prev_eye_blink_left = smoothed
        return smoothed

    def _detect_smile(self, roi_gray: np.ndarray) -> float:
        """Detect smile."""
        smiles = self.mouth_cascade.detectMultiScale(roi_gray, 1.8, 20)

        if len(smiles) > 0:
            return 0.8  # If smile detected
        return 0.0

    def _detect_head_pose(
        self,
        face_rect: tuple[int, int, int, int],
        image_shape: tuple[int, ...],
    ) -> dict[str, float]:
        """Detect head pose based on face position and size."""
        x, y, w, h = face_rect
        image_height, image_width = image_shape[:2]

        # Center of the face
        face_center_x = x + w // 2
        face_center_y = y + h // 2

        # Image center
        image_center_x = image_width // 2
        image_center_y = image_height // 2

        # Calculate relative position (normalized to -1 to 1)
        horizontal_offset = (face_center_x - image_center_x) / (image_width // 2)
        vertical_offset = (face_center_y - image_center_y) / (image_height // 2)

        # Convert to VRChat parameters
        head_pose = {
            "HeadTiltLeft": 0.0,
            "HeadTiltRight": 0.0,
            "HeadTiltUp": 0.0,
            "HeadTiltDown": 0.0,
            "HeadTurnLeft": 0.0,
            "HeadTurnRight": 0.0,
        }

        # Horizontal turn (left/right)
        if (
            horizontal_offset > self.HEAD_MOVEMENT_THRESHOLD
        ):  # Face is to the right of center = head turned left
            head_pose["HeadTurnLeft"] = min(1.0, abs(horizontal_offset) * 2.0)
        elif (
            horizontal_offset < -self.HEAD_MOVEMENT_THRESHOLD
        ):  # Face is to the left of center = head turned right
            head_pose["HeadTurnRight"] = min(1.0, abs(horizontal_offset) * 2.0)

        # Vertical tilt (up/down)
        if (
            vertical_offset > self.HEAD_MOVEMENT_THRESHOLD
        ):  # Face is below center = head tilted down
            head_pose["HeadTiltDown"] = min(1.0, abs(vertical_offset) * 2.0)
        elif (
            vertical_offset < -self.HEAD_MOVEMENT_THRESHOLD
        ):  # Face is above center = head tilted up
            head_pose["HeadTiltUp"] = min(1.0, abs(vertical_offset) * 2.0)

        # Simple tilt detection based on face aspect ratio
        face_aspect_ratio = w / h if h > 0 else 1.0
        if face_aspect_ratio > self.FACE_ASPECT_RATIO_THRESHOLD:  # Face appears wider = head tilted
            # Determine tilt direction based on horizontal position
            if horizontal_offset > 0:
                head_pose["HeadTiltRight"] = min(1.0, (face_aspect_ratio - 1.0) * 2.0)
            else:
                head_pose["HeadTiltLeft"] = min(1.0, (face_aspect_ratio - 1.0) * 2.0)

        return head_pose


class HandTracker:
    """Class for tracking hand and arm movements (simplified version)."""

    def __init__(self) -> None:
        """Initialize the HandTracker with background subtraction and tracking variables."""
        # Background subtraction model for background difference method
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.prev_left_arm = 0.0
        self.prev_right_arm = 0.0

        # Movement threshold for hand gesture detection
        self.MOVEMENT_THRESHOLD = 0.01

    def detect(self, image: np.ndarray) -> dict[str, float]:
        """Detect hand pose using the main detection method."""
        return self.detect_hand_pose(image)

    def detect_hand_pose(self, image: np.ndarray) -> dict[str, float]:
        """Detect hand and arm posture and return VRChat parameters."""
        tracking_data = {
            "LeftArmRaise": 0.0,
            "RightArmRaise": 0.0,
            "LeftHandOpen": 0.0,
            "RightHandOpen": 0.0,
            "LeftHandFist": 0.0,
            "RightHandFist": 0.0,
            "LeftHandPoint": 0.0,
            "RightHandPoint": 0.0,
        }

        # Motion detection (simplified version)
        fg_mask = self.bg_subtractor.apply(image)

        # Divide image into left and right halves
        height, width = image.shape[:2]
        left_half = fg_mask[:, : width // 2]
        right_half = fg_mask[:, width // 2 :]

        # Calculate amount of movement in each half
        left_movement = np.sum(left_half > 0) / (left_half.size)
        right_movement = np.sum(right_half > 0) / (right_half.size)

        # Estimate arm elevation from amount of movement
        left_arm_raise = min(1.0, left_movement * 10.0)
        right_arm_raise = min(1.0, right_movement * 10.0)

        # Smoothing
        tracking_data["LeftArmRaise"] = float(
            0.7 * self.prev_left_arm + 0.3 * left_arm_raise,
        )
        tracking_data["RightArmRaise"] = float(
            0.7 * self.prev_right_arm + 0.3 * right_arm_raise,
        )

        # Hand gestures are set simplistically
        tracking_data["LeftHandOpen"] = 0.5 if left_movement > self.MOVEMENT_THRESHOLD else 0.0
        tracking_data["RightHandOpen"] = 0.5 if right_movement > self.MOVEMENT_THRESHOLD else 0.0

        return tracking_data
