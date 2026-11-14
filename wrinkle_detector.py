"""
Wrinkle and fine line detection module.
"""

import cv2
import numpy as np
from typing import Dict, Optional
import config


class WrinkleDetector:
    """Detects wrinkles and fine lines in facial skin."""

    def __init__(self):
        self.ksize = config.WRINKLE_GABOR_KSIZE
        self.sigma = config.WRINKLE_GABOR_SIGMA
        self.theta_count = config.WRINKLE_GABOR_THETA_COUNT
        self.lambd = config.WRINKLE_GABOR_LAMBD
        self.gamma = config.WRINKLE_GABOR_GAMMA
        self.threshold = config.WRINKLE_THRESHOLD

    def detect_wrinkles(self, image: np.ndarray,
                        skin_mask: np.ndarray,
                        regions: Optional[Dict] = None) -> Dict:
        """
        Detect wrinkles in the image.

        Returns:
            Dictionary with wrinkle maps, scores, and analysis.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply skin mask
        masked_gray = cv2.bitwise_and(gray, gray, mask=skin_mask)

        # Method 1: Gabor filter based detection
        gabor_wrinkles = self._gabor_detection(masked_gray, skin_mask)

        # Method 2: Morphological detection
        morph_wrinkles = self._morphological_detection(masked_gray, skin_mask)

        # Method 3: Frangi filter (vessel-like structure detection)
        frangi_wrinkles = self._frangi_detection(masked_gray, skin_mask)

        # Combine methods
        combined = self._combine_methods(
            gabor_wrinkles, morph_wrinkles, frangi_wrinkles
        )

        # Regional analysis
        regional_scores = {}
        if regions:
            for region_name, (x, y, w, h) in regions.items():
                if w > 0 and h > 0:
                    roi = combined[y:y + h, x:x + w]
                    mask_roi = skin_mask[y:y + h, x:x + w]
                    regional_scores[region_name] = self._calculate_region_score(
                        roi, mask_roi
                    )

        # Overall score
        overall_score = self._calculate_overall_score(combined, skin_mask)

        return {
            "wrinkle_map": combined,
            "gabor_map": gabor_wrinkles,
            "morphological_map": morph_wrinkles,
            "overall_score": overall_score,
            "regional_scores": regional_scores,
            "severity": self._classify_severity(overall_score),
            "wrinkle_density": self._calculate_density(combined, skin_mask),
        }

    def _gabor_detection(self, gray: np.ndarray,
                         mask: np.ndarray) -> np.ndarray:
        """Detect wrinkles using Gabor filters at multiple orientations."""
        accumulator = np.zeros_like(gray, dtype=np.float64)

        thetas = np.linspace(0, np.pi, self.theta_count, endpoint=False)

        for theta in thetas:
            kernel = cv2.getGaborKernel(
                (self.ksize, self.ksize),
                self.sigma, theta, self.lambd, self.gamma, 0,
                ktype=cv2.CV_64F
            )
            filtered = cv2.filter2D(gray.astype(np.float64), cv2.CV_64F, kernel)
            accumulator = np.maximum(accumulator, np.abs(filtered))

        # Normalize
        accumulator = cv2.normalize(
            accumulator, None, 0, 255, cv2.NORM_MINMAX
        ).astype(np.uint8)

        # Apply threshold
        _, wrinkle_mask = cv2.threshold(
            accumulator, self.threshold, 255, cv2.THRESH_BINARY
        )

        # Apply skin mask
        wrinkle_mask = cv2.bitwise_and(wrinkle_mask, mask)

        return wrinkle_mask

    def _morphological_detection(self, gray: np.ndarray,
                                  mask: np.ndarray) -> np.ndarray:
        """Detect wrinkles using morphological operations."""
        # Apply bilateral filter to reduce noise while preserving edges
        smoothed = cv2.bilateralFilter(gray, 9, 75, 75)

        # Blackhat morphology to detect dark linear structures
        kernel_sizes = [(15, 1), (1, 15), (11, 11)]
        accumulator = np.zeros_like(gray, dtype=np.float64)

        for ks in kernel_sizes:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ks)
            blackhat = cv2.morphologyEx(smoothed, cv2.MORPH_BLACKHAT, kernel)
            accumulator += blackhat.astype(np.float64)

        # Additional: line detection with longer kernels at various angles
        for angle in [0, 45, 90, 135]:
            kernel = self._create_line_kernel(15, angle)
            blackhat = cv2.morphologyEx(smoothed, cv2.MORPH_BLACKHAT, kernel)
            accumulator += blackhat.astype(np.float64)

        # Normalize
        accumulator = cv2.normalize(
            accumulator, None, 0, 255, cv2.NORM_MINMAX
        ).astype(np.uint8)

        # Threshold
        _, wrinkle_mask = cv2.threshold(
            accumulator, 30, 255, cv2.THRESH_BINARY
        )

        # Thin the lines
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        wrinkle_mask = cv2.morphologyEx(wrinkle_mask, cv2.MORPH_OPEN, kernel)

        return cv2.bitwise_and(wrinkle_mask, mask)

    def _frangi_detection(self, gray: np.ndarray,
                          mask: np.ndarray) -> np.ndarray:
        """Simple Frangi-like filter for line detection using Hessian."""
        smoothed = cv2.GaussianBlur(gray.astype(np.float64), (5, 5), 1.5)

        # Compute Hessian matrix elements
        dxx = cv2.Sobel(smoothed, cv2.CV_64F, 2, 0, ksize=5)
        dyy = cv2.Sobel(smoothed, cv2.CV_64F, 0, 2, ksize=5)
        dxy = cv2.Sobel(smoothed, cv2.CV_64F, 1, 1, ksize=5)

        # Eigenvalues of Hessian
        trace = dxx + dyy
        det = dxx * dyy - dxy * dxy

        # Discriminant
        disc = np.sqrt(np.maximum(trace ** 2 - 4 * det, 0))

        lambda1 = (trace + disc) / 2
        lambda2 = (trace - disc) / 2

        # Frangi response: strong when one eigenvalue is large
        # and the other is small (line-like structure)
        response = np.zeros_like(gray, dtype=np.float64)
        valid = np.abs(lambda1) > 1e-6

        ratio = np.zeros_like(lambda1)
        ratio[valid] = (lambda2[valid] / lambda1[valid]) ** 2

        # Vesselness measure
        response = np.abs(lambda2) * np.exp(-ratio / 0.5)
        response[lambda2 > 0] = 0  # We want dark lines

        response = cv2.normalize(
            response, None, 0, 255, cv2.NORM_MINMAX
        ).astype(np.uint8)

        _, wrinkle_mask = cv2.threshold(response, 25, 255, cv2.THRESH_BINARY)
        return cv2.bitwise_and(wrinkle_mask, mask)

    def _create_line_kernel(self, length: int, angle: int) -> np.ndarray:
        """Create a line-shaped morphological kernel at a given angle."""
        kernel = np.zeros((length, length), dtype=np.uint8)
        center = length // 2

        rad = np.radians(angle)
        for i in range(length):
            x = int(center + (i - center) * np.cos(rad))
            y = int(center + (i - center) * np.sin(rad))
            if 0 <= x < length and 0 <= y < length:
                kernel[y, x] = 1

        return kernel

    def _combine_methods(self, *maps) -> np.ndarray:
        """Combine multiple wrinkle detection maps."""
        combined = np.zeros_like(maps[0], dtype=np.float64)

        weights = [0.4, 0.35, 0.25]

        for i, m in enumerate(maps):
            weight = weights[i] if i < len(weights) else 1.0 / len(maps)
            combined += m.astype(np.float64) * weight

        combined = cv2.normalize(
            combined, None, 0, 255, cv2.NORM_MINMAX
        ).astype(np.uint8)

        _, combined = cv2.threshold(combined, 40, 255, cv2.THRESH_BINARY)
        return combined

    def _calculate_region_score(self, wrinkle_roi: np.ndarray,
                                 mask_roi: np.ndarray) -> float:
        """Calculate wrinkle score for a specific region."""
        skin_pixels = cv2.countNonZero(mask_roi) if mask_roi is not None else wrinkle_roi.size
        if skin_pixels == 0:
            return 100.0

        wrinkle_pixels = cv2.countNonZero(
            cv2.bitwise_and(wrinkle_roi, mask_roi) if mask_roi is not None else wrinkle_roi
        )
        ratio = wrinkle_pixels / skin_pixels
        score = max(0, 100 - ratio * 500)
        return min(100, score)

    def _calculate_overall_score(self, wrinkle_map: np.ndarray,
                                  skin_mask: np.ndarray) -> float:
        """Calculate overall wrinkle score (0-100, higher is better)."""
        skin_pixels = cv2.countNonZero(skin_mask)
        if skin_pixels == 0:
            return 50.0

        wrinkle_pixels = cv2.countNonZero(
            cv2.bitwise_and(wrinkle_map, skin_mask)
        )
        ratio = wrinkle_pixels / skin_pixels
        score = max(0, 100 - ratio * 400)
        return min(100, score)

    def _calculate_density(self, wrinkle_map: np.ndarray,
                           skin_mask: np.ndarray) -> float:
        """Calculate wrinkle density."""
        skin_pixels = cv2.countNonZero(skin_mask)
        if skin_pixels == 0:
            return 0.0
        wrinkle_pixels = cv2.countNonZero(
            cv2.bitwise_and(wrinkle_map, skin_mask)
        )
        return (wrinkle_pixels / skin_pixels) * 100

    def _classify_severity(self, score: float) -> str:
        """Classify wrinkle severity based on score."""
        if score >= 85:
            return "minimal"
        elif score >= 70:
            return "mild"
        elif score >= 50:
            return "moderate"
        else:
            return "severe"

    def visualize_wrinkles(self, image: np.ndarray,
                           wrinkle_map: np.ndarray) -> np.ndarray:
        """Visualize wrinkles as overlay on image."""
        result = image.copy()
        overlay = np.zeros_like(image)
        overlay[wrinkle_map > 0] = (0, 0, 255)  # Red for wrinkles
        result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)
        return result