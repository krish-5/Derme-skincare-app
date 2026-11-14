"""
Skin detection and segmentation module.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import config


class SkinDetector:
    """Detects and segments skin regions from images."""

    def __init__(self):
        self.hsv_lower = np.array(config.SKIN_HSV_LOWER)
        self.hsv_upper = np.array(config.SKIN_HSV_UPPER)
        self.ycrcb_lower = np.array(config.SKIN_YCRCB_LOWER)
        self.ycrcb_upper = np.array(config.SKIN_YCRCB_UPPER)

    def detect_skin(self, image: np.ndarray,
                    method: str = "combined") -> np.ndarray:
        """
        Detect skin pixels in the image.

        Args:
            image: BGR image
            method: 'hsv', 'ycrcb', or 'combined'

        Returns:
            Binary mask of skin regions
        """
        if method == "hsv":
            return self._detect_hsv(image)
        elif method == "ycrcb":
            return self._detect_ycrcb(image)
        elif method == "combined":
            return self._detect_combined(image)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _detect_hsv(self, image: np.ndarray) -> np.ndarray:
        """Detect skin using HSV color space."""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
        return self._refine_mask(mask)

    def _detect_ycrcb(self, image: np.ndarray) -> np.ndarray:
        """Detect skin using YCrCb color space."""
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        mask = cv2.inRange(ycrcb, self.ycrcb_lower, self.ycrcb_upper)
        return self._refine_mask(mask)

    def _detect_combined(self, image: np.ndarray) -> np.ndarray:
        """Combine HSV and YCrCb detection for better results."""
        hsv_mask = self._detect_hsv(image)
        ycrcb_mask = self._detect_ycrcb(image)

        # Combine using AND (more precise) or OR (more coverage)
        combined = cv2.bitwise_and(hsv_mask, ycrcb_mask)
        return self._refine_mask(combined)

    def _refine_mask(self, mask: np.ndarray) -> np.ndarray:
        """Refine skin mask using morphological operations."""
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))

        # Remove small noise
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open, iterations=2)
        # Fill small holes
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close, iterations=2)
        # Smooth the mask
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        return mask

    def extract_skin(self, image: np.ndarray,
                     face_mask: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract skin from the image.

        Returns:
            Tuple of (skin-only image, skin mask)
        """
        skin_mask = self.detect_skin(image)

        if face_mask is not None:
            skin_mask = cv2.bitwise_and(skin_mask, face_mask)

        skin_image = cv2.bitwise_and(image, image, mask=skin_mask)
        return skin_image, skin_mask

    def get_skin_percentage(self, mask: np.ndarray,
                            roi: Optional[np.ndarray] = None) -> float:
        """Calculate the percentage of skin in the image/ROI."""
        if roi is not None:
            total = cv2.countNonZero(roi)
            skin = cv2.countNonZero(cv2.bitwise_and(mask, roi))
        else:
            total = mask.shape[0] * mask.shape[1]
            skin = cv2.countNonZero(mask)

        if total == 0:
            return 0.0
        return (skin / total) * 100

    def get_skin_color_stats(self, image: np.ndarray,
                             mask: np.ndarray) -> dict:
        """Get statistical properties of the skin color."""
        if cv2.countNonZero(mask) == 0:
            return {}

        # BGR stats
        mean_bgr = cv2.mean(image, mask=mask)[:3]

        # LAB stats
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        mean_lab = cv2.mean(lab, mask=mask)[:3]

        # HSV stats
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mean_hsv = cv2.mean(hsv, mask=mask)[:3]

        # Standard deviation
        pixels = image[mask > 0]
        std_bgr = np.std(pixels, axis=0) if len(pixels) > 0 else (0, 0, 0)

        return {
            "mean_bgr": mean_bgr,
            "mean_lab": mean_lab,
            "mean_hsv": mean_hsv,
            "std_bgr": tuple(std_bgr),
            "luminance": mean_lab[0],
            "pixel_count": cv2.countNonZero(mask),
        }

    def visualize_skin(self, image: np.ndarray,
                       skin_mask: np.ndarray) -> np.ndarray:
        """Create a visualization of detected skin."""
        result = image.copy()

        # Create colored overlay
        overlay = np.zeros_like(image)
        overlay[skin_mask > 0] = (0, 255, 0)  # Green overlay for skin

        result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)
        return result