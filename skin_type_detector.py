"""
Skin type detection module — Oily, Dry, Combination, Normal
"""

import cv2
import numpy as np
from typing import Dict, Optional


class SkinTypeDetector:
    """Detects skin type based on shine, texture, and pore analysis."""

    def detect_skin_type(self, image: np.ndarray,
                         skin_mask: np.ndarray,
                         regions: Optional[Dict] = None) -> Dict:
        """
        Determine skin type: Oily, Dry, Combination, Normal

        Analysis based on:
        - Shine/specular highlights (oiliness indicator)
        - Texture roughness (dryness indicator)
        - T-zone vs cheek comparison (combination indicator)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]

        # ── Measure overall shine (oiliness) ──
        shine_score = self._measure_shine(l_channel, skin_mask)

        # ── Measure texture roughness (dryness) ──
        roughness_score = self._measure_dryness(gray, skin_mask)

        # ── T-zone analysis (combination skin) ──
        tzone_oiliness = 0.0
        cheek_oiliness = 0.0

        if regions:
            tzone_oiliness = self._measure_tzone(l_channel, regions)
            cheek_oiliness = self._measure_cheeks(l_channel, regions)

        # ── Determine skin type ──
        skin_type = self._classify_type(
            shine_score, roughness_score,
            tzone_oiliness, cheek_oiliness
        )

        return {
            "type": skin_type["type"],
            "description": skin_type["description"],
            "characteristics": skin_type["characteristics"],
            "shine_level": shine_score,
            "dryness_level": roughness_score,
            "tzone_oiliness": tzone_oiliness,
            "cheek_condition": cheek_oiliness,
            "confidence": skin_type["confidence"],
        }

    def _measure_shine(self, l_channel: np.ndarray,
                       mask: np.ndarray) -> float:
        """Measure specular highlights indicating oiliness."""
        masked = cv2.bitwise_and(l_channel, l_channel, mask=mask)
        skin_pixels = masked[mask > 0].astype(np.float64)

        if len(skin_pixels) == 0:
            return 0.0

        mean_l = np.mean(skin_pixels)
        # Count pixels significantly brighter than mean (shine spots)
        shine_threshold = mean_l + 40
        shine_pixels = np.sum(skin_pixels > shine_threshold)
        shine_ratio = shine_pixels / len(skin_pixels) * 100

        return min(100, shine_ratio * 10)

    def _measure_dryness(self, gray: np.ndarray,
                         mask: np.ndarray) -> float:
        """Measure texture roughness indicating dryness."""
        masked = cv2.bitwise_and(gray, gray, mask=mask)

        # High frequency content = rough/dry texture
        smoothed = cv2.GaussianBlur(masked, (11, 11), 3)
        diff = cv2.absdiff(masked, smoothed)

        skin_diff = diff[mask > 0].astype(np.float64)
        if len(skin_diff) == 0:
            return 0.0

        roughness = np.mean(skin_diff)
        return min(100, roughness * 8)

    def _measure_tzone(self, l_channel: np.ndarray,
                       regions: Dict) -> float:
        """Measure oiliness in T-zone (forehead + nose)."""
        shine_values = []

        for region_name in ["forehead", "nose"]:
            if region_name in regions:
                x, y, w, h = regions[region_name]
                if w > 5 and h > 5:
                    roi = l_channel[y:y + h, x:x + w]
                    if roi.size > 0:
                        mean_l = np.mean(roi)
                        bright = np.sum(roi > mean_l + 30)
                        ratio = bright / roi.size * 100
                        shine_values.append(ratio)

        return float(np.mean(shine_values) * 8) if shine_values else 0.0

    def _measure_cheeks(self, l_channel: np.ndarray,
                        regions: Dict) -> float:
        """Measure cheek condition."""
        values = []

        for region_name in ["left_cheek", "right_cheek"]:
            if region_name in regions:
                x, y, w, h = regions[region_name]
                if w > 5 and h > 5:
                    roi = l_channel[y:y + h, x:x + w]
                    if roi.size > 0:
                        mean_l = np.mean(roi)
                        bright = np.sum(roi > mean_l + 30)
                        ratio = bright / roi.size * 100
                        values.append(ratio)

        return float(np.mean(values) * 8) if values else 0.0

    def _classify_type(self, shine: float, roughness: float,
                       tzone: float, cheeks: float) -> Dict:
        """Classify skin type based on measurements."""

        # Combination: oily T-zone but dry/normal cheeks
        if tzone > 40 and cheeks < 25 and abs(tzone - cheeks) > 20:
            return {
                "type": "Combination",
                "description": "Oily in T-zone, normal to dry on cheeks",
                "characteristics": [
                    "Oily forehead and nose",
                    "Normal to dry cheeks",
                    "May have enlarged pores in T-zone",
                    "Prone to occasional breakouts in oily areas",
                ],
                "confidence": min(95, 60 + abs(tzone - cheeks)),
            }

        # Oily: high shine, low roughness
        if shine > 45:
            return {
                "type": "Oily",
                "description": "Excess sebum production across the face",
                "characteristics": [
                    "Visible shine, especially in T-zone",
                    "Enlarged or visible pores",
                    "Prone to acne and blackheads",
                    "Makeup tends to slide off",
                ],
                "confidence": min(95, 50 + shine * 0.5),
            }

        # Dry: high roughness, low shine
        if roughness > 45 and shine < 25:
            return {
                "type": "Dry",
                "description": "Insufficient moisture and oil production",
                "characteristics": [
                    "Tight or flaky feeling",
                    "Fine lines more visible",
                    "Dull complexion",
                    "May feel rough to touch",
                ],
                "confidence": min(95, 50 + roughness * 0.5),
            }

        # Normal
        return {
            "type": "Normal",
            "description": "Well-balanced skin with adequate moisture",
            "characteristics": [
                "Balanced oil production",
                "Small, barely visible pores",
                "Even skin tone",
                "Few imperfections",
            ],
            "confidence": min(90, 70),
        }