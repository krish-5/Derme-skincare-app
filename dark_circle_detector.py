"""
Under-eye dark circle detection module.
"""

import cv2
import numpy as np
from typing import Dict, Optional, Tuple
import config


class DarkCircleDetector:
    """Detects and analyzes under-eye dark circles."""

    def __init__(self):
        self.threshold = config.DARK_CIRCLE_THRESHOLD

    def detect_dark_circles(self, image: np.ndarray,
                            regions: Optional[Dict] = None) -> Dict:
        """
        Detect under-eye dark circles.

        Args:
            image: BGR input image
            regions: Facial regions dictionary

        Returns:
            Dictionary with dark circle analysis
        """
        if regions is None:
            return {"score": 50.0, "severity": "unknown",
                    "details": "No facial regions provided"}

        results = {}

        # Analyze both under-eye regions
        for eye_region in ["under_left_eye", "under_right_eye"]:
            if eye_region in regions:
                x, y, w, h = regions[eye_region]
                if w > 5 and h > 5:
                    roi = image[y:y + h, x:x + w]
                    analysis = self._analyze_under_eye(roi, image, regions)
                    results[eye_region] = analysis

        # Get reference skin (cheek or forehead)
        ref_luminance = self._get_reference_luminance(image, regions)

        # Calculate overall dark circle score
        overall = self._calculate_overall(results, ref_luminance)

        return {
            "eye_regions": results,
            "reference_luminance": ref_luminance,
            "score": overall["score"],
            "severity": overall["severity"],
            "darkness_level": overall["darkness_level"],
            "color_analysis": overall.get("color_analysis", {}),
        }

    def _analyze_under_eye(self, roi: np.ndarray,
                           full_image: np.ndarray,
                           regions: Dict) -> Dict:
        """Analyze a single under-eye region."""
        if roi.size == 0:
            return {"luminance": 0, "darkness": 0}

        # Convert to LAB
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        a_channel = lab[:, :, 1]
        b_channel = lab[:, :, 2]

        # Luminance analysis
        mean_l = np.mean(l_channel)
        std_l = np.std(l_channel)

        # Color analysis (bluish/purplish tones indicate dark circles)
        mean_a = np.mean(a_channel)
        mean_b = np.mean(b_channel)

        # HSV analysis
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mean_s = np.mean(hsv[:, :, 1])
        mean_v = np.mean(hsv[:, :, 2])

        return {
            "luminance": float(mean_l),
            "luminance_std": float(std_l),
            "mean_a": float(mean_a),
            "mean_b": float(mean_b),
            "saturation": float(mean_s),
            "value": float(mean_v),
        }

    def _get_reference_luminance(self, image: np.ndarray,
                                  regions: Dict) -> float:
        """Get reference luminance from cheek or forehead."""
        ref_regions = ["left_cheek", "right_cheek", "forehead"]

        luminances = []
        for region_name in ref_regions:
            if region_name in regions:
                x, y, w, h = regions[region_name]
                if w > 5 and h > 5:
                    roi = image[y:y + h, x:x + w]
                    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
                    luminances.append(np.mean(lab[:, :, 0]))

        return float(np.mean(luminances)) if luminances else 128.0

    def _calculate_overall(self, eye_results: Dict,
                           ref_luminance: float) -> Dict:
        """Calculate overall dark circle metrics."""
        if not eye_results:
            return {
                "score": 50.0,
                "severity": "unknown",
                "darkness_level": 0.0,
            }

        darkness_values = []
        color_shifts = []

        for eye_name, analysis in eye_results.items():
            if "luminance" in analysis:
                # Darkness = how much darker than reference
                darkness = ref_luminance - analysis["luminance"]
                darkness_values.append(max(0, darkness))

                # Blue shift (lower b value = more blue/purple)
                if "mean_b" in analysis:
                    color_shifts.append(128 - analysis["mean_b"])

        avg_darkness = np.mean(darkness_values) if darkness_values else 0
        avg_color_shift = np.mean(color_shifts) if color_shifts else 0

        # Normalize darkness to 0-100 scale
        darkness_normalized = min(100, avg_darkness * 2)

        # Score (higher is better, meaning less dark circles)
        score = max(0, 100 - darkness_normalized)

        # Severity classification
        if darkness_normalized < 15:
            severity = "none"
        elif darkness_normalized < 30:
            severity = "mild"
        elif darkness_normalized < 50:
            severity = "moderate"
        else:
            severity = "severe"

        # Determine the type of dark circle
        color_analysis = {}
        if avg_color_shift > 5:
            color_analysis["type"] = "vascular"  # Blue/purple tone
            color_analysis["description"] = "Blue/purple tones - vascular type"
        elif avg_darkness > 20:
            color_analysis["type"] = "pigmented"
            color_analysis["description"] = "Brown tones - pigmentation type"
        else:
            color_analysis["type"] = "mild_shadow"
            color_analysis["description"] = "Mild shadowing"

        return {
            "score": score,
            "severity": severity,
            "darkness_level": darkness_normalized,
            "color_analysis": color_analysis,
        }

    def visualize_dark_circles(self, image: np.ndarray,
                               regions: Dict,
                               dark_circle_data: Dict) -> np.ndarray:
        """Visualize dark circle detection results."""
        result = image.copy()

        severity_colors = {
            "none": (0, 255, 0),
            "mild": (0, 255, 255),
            "moderate": (0, 165, 255),
            "severe": (0, 0, 255),
            "unknown": (128, 128, 128),
        }

        color = severity_colors.get(
            dark_circle_data.get("severity", "unknown"),
            (128, 128, 128)
        )

        for eye_region in ["under_left_eye", "under_right_eye"]:
            if eye_region in regions:
                x, y, w, h = regions[eye_region]
                cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
                cv2.putText(
                    result,
                    f"DC: {dark_circle_data.get('severity', 'N/A')}",
                    (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1
                )

        return result