"""
Skin pore detection and analysis module.
"""

import cv2
import numpy as np
from typing import Dict, Optional, List
import config


class PoreAnalyzer:
    """Detects and analyzes skin pores."""

    def __init__(self):
        self.min_area = config.PORE_MIN_AREA
        self.max_area = config.PORE_MAX_AREA
        self.threshold = config.PORE_THRESHOLD

    def analyze_pores(self, image: np.ndarray,
                      skin_mask: np.ndarray,
                      regions: Optional[Dict] = None) -> Dict:
        """
        Detect and analyze skin pores.

        Returns:
            Dictionary with pore detection results and scores.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Enhance contrast for pore visibility
        from utils import apply_clahe
        enhanced = apply_clahe(gray, clip_limit=3.0, tile_grid_size=(4, 4))

        # Detect pores
        pore_map = self._detect_pores(enhanced, skin_mask)
        pore_locations = self._find_pore_locations(pore_map, skin_mask)

        # Regional analysis
        regional = {}
        if regions:
            focus_regions = ["nose", "left_cheek", "right_cheek", "forehead", "chin"]
            for name in focus_regions:
                if name in regions:
                    x, y, w, h = regions[name]
                    if w > 10 and h > 10:
                        roi_pores = pore_map[y:y + h, x:x + w]
                        roi_mask = skin_mask[y:y + h, x:x + w]
                        regional[name] = self._analyze_region_pores(
                            roi_pores, roi_mask
                        )

        # Overall metrics
        total_pores = len(pore_locations)
        density = self._calculate_density(pore_map, skin_mask)
        avg_size = self._calculate_avg_size(pore_locations)
        score = self._calculate_pore_score(density, avg_size)

        return {
            "pore_map": pore_map,
            "pore_count": total_pores,
            "pore_locations": pore_locations,
            "density": density,
            "average_size": avg_size,
            "regional_analysis": regional,
            "score": score,
            "severity": self._classify_severity(score),
        }

    def _detect_pores(self, gray: np.ndarray,
                      mask: np.ndarray) -> np.ndarray:
        """Detect pores using morphological operations."""
        # Apply skin mask
        masked = cv2.bitwise_and(gray, gray, mask=mask)

        # Smooth to get the base skin texture
        smoothed = cv2.GaussianBlur(masked, (15, 15), 3)

        # Pores are small dark spots - difference between original and smoothed
        diff = cv2.subtract(smoothed, masked)

        # Apply bilateral filter for noise reduction
        diff = cv2.bilateralFilter(diff, 5, 50, 50)

        # Threshold to get pore candidates
        _, pore_mask = cv2.threshold(
            diff, self.threshold, 255, cv2.THRESH_BINARY
        )

        # Morphological refinement
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        pore_mask = cv2.morphologyEx(pore_mask, cv2.MORPH_OPEN, kernel)

        # Apply skin mask
        pore_mask = cv2.bitwise_and(pore_mask, mask)

        # Additional: Top-hat transform
        tophat_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        tophat = cv2.morphologyEx(masked, cv2.MORPH_BLACKHAT, tophat_kernel)
        _, tophat_mask = cv2.threshold(tophat, 20, 255, cv2.THRESH_BINARY)
        tophat_mask = cv2.bitwise_and(tophat_mask, mask)

        # Combine methods
        combined = cv2.bitwise_or(pore_mask, tophat_mask)
        combined = cv2.bitwise_and(combined, mask)

        return combined

    def _find_pore_locations(self, pore_map: np.ndarray,
                              skin_mask: np.ndarray) -> List[Dict]:
        """Find individual pore locations and properties."""
        contours, _ = cv2.findContours(
            pore_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        pores = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area <= area <= self.max_area:
                x, y, w, h = cv2.boundingRect(contour)
                center = (x + w // 2, y + h // 2)

                # Check if in skin region
                if (0 <= center[1] < skin_mask.shape[0] and
                    0 <= center[0] < skin_mask.shape[1] and
                    skin_mask[center[1], center[0]] > 0):

                    pores.append({
                        "center": center,
                        "area": area,
                        "bbox": (x, y, w, h),
                        "size_category": self._categorize_size(area),
                    })

        return pores

    def _categorize_size(self, area: float) -> str:
        """Categorize pore size."""
        if area < 15:
            return "small"
        elif area < 40:
            return "medium"
        else:
            return "large"

    def _calculate_density(self, pore_map: np.ndarray,
                           skin_mask: np.ndarray) -> float:
        """Calculate pore density (pore pixels / skin pixels)."""
        skin_pixels = cv2.countNonZero(skin_mask)
        if skin_pixels == 0:
            return 0.0
        pore_pixels = cv2.countNonZero(
            cv2.bitwise_and(pore_map, skin_mask)
        )
        return (pore_pixels / skin_pixels) * 100

    def _calculate_avg_size(self, pores: List[Dict]) -> float:
        """Calculate average pore size."""
        if not pores:
            return 0.0
        return np.mean([p["area"] for p in pores])

    def _analyze_region_pores(self, pore_roi: np.ndarray,
                               mask_roi: np.ndarray) -> Dict:
        """Analyze pores in a specific facial region."""
        contours, _ = cv2.findContours(
            cv2.bitwise_and(pore_roi, mask_roi),
            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        count = sum(
            1 for c in contours
            if self.min_area <= cv2.contourArea(c) <= self.max_area
        )

        skin_area = cv2.countNonZero(mask_roi)
        density = (count / (skin_area / 1000)) if skin_area > 0 else 0

        return {
            "count": count,
            "density": float(density),
            "severity": (
                "low" if density < 1 else
                "moderate" if density < 3 else "high"
            ),
        }

    def _calculate_pore_score(self, density: float,
                               avg_size: float) -> float:
        """Calculate pore score (0-100, higher is better)."""
        density_penalty = density * 10
        size_penalty = max(0, (avg_size - 10) * 2)
        score = max(0, 100 - density_penalty - size_penalty)
        return min(100, score)

    def _classify_severity(self, score: float) -> str:
        """Classify pore severity."""
        if score >= 80:
            return "fine"
        elif score >= 60:
            return "normal"
        elif score >= 40:
            return "visible"
        else:
            return "enlarged"

    def visualize_pores(self, image: np.ndarray,
                        pore_map: np.ndarray,
                        pore_locations: Optional[List] = None) -> np.ndarray:
        """Visualize detected pores."""
        result = image.copy()

        # Overlay pore map
        overlay = np.zeros_like(image)
        overlay[pore_map > 0] = (255, 255, 0)  # Cyan for pores

        result = cv2.addWeighted(result, 0.8, overlay, 0.2, 0)

        # Draw individual pore markers
        if pore_locations:
            for pore in pore_locations[:200]:  # Limit for performance
                color = {
                    "small": (0, 255, 0),
                    "medium": (0, 255, 255),
                    "large": (0, 0, 255),
                }.get(pore.get("size_category", "small"), (255, 255, 255))

                cv2.circle(result, pore["center"], 2, color, -1)

        return result