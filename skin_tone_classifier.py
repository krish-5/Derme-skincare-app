"""
Skin tone classification and analysis module.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional
import config


class SkinToneClassifier:
    """Classifies skin tone and analyzes skin color properties."""

    FITZPATRICK_SCALE = {
        1: {"name": "Type I - Very Fair", "l_range": (75, 100),
            "description": "Always burns, never tans"},
        2: {"name": "Type II - Fair", "l_range": (65, 75),
            "description": "Usually burns, tans minimally"},
        3: {"name": "Type III - Medium", "l_range": (55, 65),
            "description": "Sometimes burns, tans uniformly"},
        4: {"name": "Type IV - Olive", "l_range": (45, 55),
            "description": "Burns minimally, tans well"},
        5: {"name": "Type V - Brown", "l_range": (35, 45),
            "description": "Rarely burns, tans darkly"},
        6: {"name": "Type VI - Dark", "l_range": (0, 35),
            "description": "Never burns, deeply pigmented"},
    }

    def __init__(self):
        self.tone_categories = config.SKIN_TONE_CATEGORIES

    def classify_skin_tone(self, image: np.ndarray,
                           skin_mask: np.ndarray) -> Dict:
        """
        Classify skin tone from the image.

        Returns:
            Dictionary with tone classification, Fitzpatrick type, etc.
        """
        if cv2.countNonZero(skin_mask) == 0:
            return {"error": "No skin detected"}

        # Extract skin pixels
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Get mean values
        mean_lab = cv2.mean(lab, mask=skin_mask)[:3]
        mean_hsv = cv2.mean(hsv, mask=skin_mask)[:3]
        mean_bgr = cv2.mean(image, mask=skin_mask)[:3]

        # L channel for lightness
        l_value = mean_lab[0]
        l_normalized = (l_value / 255) * 100  # Normalize to 0-100

        # Classify by category
        category = self._classify_category(l_value)

        # Fitzpatrick scale
        fitzpatrick = self._classify_fitzpatrick(l_normalized)

        # Undertone analysis
        undertone = self._analyze_undertone(image, skin_mask)

        # ITA (Individual Typology Angle)
        ita = self._calculate_ita(mean_lab)

        # Color evenness
        evenness = self._analyze_evenness(lab, skin_mask)

        # Hex color
        hex_color = self._bgr_to_hex(mean_bgr)

        return {
            "category": category,
            "fitzpatrick_type": fitzpatrick["type"],
            "fitzpatrick_name": fitzpatrick["name"],
            "fitzpatrick_description": fitzpatrick["description"],
            "undertone": undertone,
            "ita_angle": ita,
            "ita_category": self._ita_category(ita),
            "mean_lab": {
                "L": float(mean_lab[0]),
                "a": float(mean_lab[1]),
                "b": float(mean_lab[2]),
            },
            "mean_hsv": {
                "H": float(mean_hsv[0]),
                "S": float(mean_hsv[1]),
                "V": float(mean_hsv[2]),
            },
            "hex_color": hex_color,
            "rgb_color": (
                int(mean_bgr[2]),
                int(mean_bgr[1]),
                int(mean_bgr[0]),
            ),
            "evenness_score": evenness,
        }

    def _classify_category(self, l_value: float) -> str:
        """Classify skin tone by luminance."""
        for category, (low, high) in self.tone_categories.items():
            if low <= l_value < high:
                return category
        return "Unknown"

    def _classify_fitzpatrick(self, l_normalized: float) -> Dict:
        """Classify according to Fitzpatrick scale."""
        for ftype, info in self.FITZPATRICK_SCALE.items():
            low, high = info["l_range"]
            if low <= l_normalized < high:
                return {
                    "type": ftype,
                    "name": info["name"],
                    "description": info["description"],
                }

        return {
            "type": 3,
            "name": "Type III - Medium",
            "description": "Sometimes burns, tans uniformly",
        }

    def _analyze_undertone(self, image: np.ndarray,
                           skin_mask: np.ndarray) -> Dict:
        """Analyze skin undertone (warm, cool, neutral)."""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # Get a and b channels for skin pixels
        a_values = lab[:, :, 1][skin_mask > 0].astype(np.float64)
        b_values = lab[:, :, 2][skin_mask > 0].astype(np.float64)

        mean_a = np.mean(a_values) - 128  # Center around 0
        mean_b = np.mean(b_values) - 128

        # Warm tones: higher b (yellow), higher a (red)
        # Cool tones: lower b (blue), lower a (green)
        warmth = mean_a + mean_b

        if warmth > 10:
            undertone_type = "warm"
            description = "Yellow/golden undertones"
        elif warmth < -10:
            undertone_type = "cool"
            description = "Pink/blue undertones"
        else:
            undertone_type = "neutral"
            description = "Balanced undertones"

        return {
            "type": undertone_type,
            "description": description,
            "warmth_score": float(warmth),
            "a_deviation": float(mean_a),
            "b_deviation": float(mean_b),
        }

    def _calculate_ita(self, mean_lab: Tuple) -> float:
        """
        Calculate Individual Typology Angle.
        ITA = arctan((L - 50) / b) * (180 / pi)
        """
        l_value = mean_lab[0] * (100 / 255)  # Normalize to 0-100
        b_value = mean_lab[2] - 128  # Center around 0

        if abs(b_value) < 0.001:
            b_value = 0.001

        ita = np.arctan2(l_value - 50, b_value) * (180 / np.pi)
        return float(ita)

    def _ita_category(self, ita: float) -> str:
        """Classify ITA angle into skin type category."""
        if ita > 55:
            return "Very Light"
        elif ita > 41:
            return "Light"
        elif ita > 28:
            return "Intermediate"
        elif ita > 10:
            return "Tan"
        elif ita > -30:
            return "Brown"
        else:
            return "Dark"

    def _analyze_evenness(self, lab: np.ndarray,
                          skin_mask: np.ndarray) -> float:
        """Analyze skin color evenness."""
        l_channel = lab[:, :, 0]
        skin_l = l_channel[skin_mask > 0].astype(np.float64)

        if len(skin_l) == 0:
            return 50.0

        # Lower std = more even
        std_l = np.std(skin_l)
        evenness = max(0, 100 - std_l * 3)
        return min(100, float(evenness))

    def _bgr_to_hex(self, bgr: Tuple) -> str:
        """Convert BGR to hex color string."""
        b, g, r = int(bgr[0]), int(bgr[1]), int(bgr[2])
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_skin_tone_swatch(self, hex_color: str,
                                 size: Tuple[int, int] = (100, 100)) -> np.ndarray:
        """Create a color swatch image."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        swatch = np.full((*size, 3), (b, g, r), dtype=np.uint8)
        return swatch