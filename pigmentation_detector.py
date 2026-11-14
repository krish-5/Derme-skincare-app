"""
Pigmentation and dark spot detection module.
"""

import cv2
import numpy as np
from typing import Dict, List, Optional


class PigmentationDetector:
    """Detects hyperpigmentation, melasma, and uneven skin tone."""

    def detect_pigmentation(self, image: np.ndarray,
                            skin_mask: np.ndarray,
                            regions: Optional[Dict] = None) -> Dict:
        """Detect pigmentation issues."""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        b_channel = lab[:, :, 2]

        # ── Detect dark patches (hyperpigmentation) ──
        dark_patches = self._detect_dark_patches(l_channel, skin_mask)

        # ── Detect uneven areas ──
        unevenness_map = self._detect_unevenness(l_channel, skin_mask)

        # ── Detect brown spots (melanin) ──
        brown_spots = self._detect_brown_spots(lab, skin_mask)

        # ── Regional analysis ──
        regional = {}
        if regions:
            for name, (x, y, w, h) in regions.items():
                if w > 10 and h > 10:
                    roi_l = l_channel[y:y + h, x:x + w]
                    roi_mask = skin_mask[y:y + h, x:x + w]
                    if cv2.countNonZero(roi_mask) > 50:
                        regional[name] = self._analyze_region(roi_l, roi_mask)

        # ── Calculate score ──
        dark_ratio = cv2.countNonZero(dark_patches) / max(1, cv2.countNonZero(skin_mask))
        score = max(0, 100 - dark_ratio * 300)
        score = min(100, score)

        return {
            "score": score,
            "dark_patch_map": dark_patches,
            "unevenness_map": unevenness_map,
            "brown_spot_count": len(brown_spots),
            "brown_spots": brown_spots,
            "severity": self._classify(score),
            "regional": regional,
            "pigmentation_type": self._determine_type(dark_patches, brown_spots, skin_mask),
        }

    def _detect_dark_patches(self, l_channel: np.ndarray,
                              mask: np.ndarray) -> np.ndarray:
        """Detect areas significantly darker than surrounding skin."""
        masked = cv2.bitwise_and(l_channel, l_channel, mask=mask)

        # Local adaptive mean
        local_mean = cv2.GaussianBlur(masked.astype(np.float64), (51, 51), 0)

        # Areas darker than local mean by threshold
        diff = local_mean - masked.astype(np.float64)
        dark_mask = (diff > 20).astype(np.uint8) * 255
        dark_mask = cv2.bitwise_and(dark_mask, mask)

        # Clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel)

        return dark_mask

    def _detect_unevenness(self, l_channel: np.ndarray,
                           mask: np.ndarray) -> np.ndarray:
        """Create unevenness heatmap."""
        masked = cv2.bitwise_and(l_channel, l_channel, mask=mask)
        mean_val = cv2.mean(l_channel, mask=mask)[0]

        diff = np.abs(masked.astype(np.float64) - mean_val)
        diff = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        diff = cv2.bitwise_and(diff, diff, mask=mask)

        return diff

    def _detect_brown_spots(self, lab: np.ndarray,
                            mask: np.ndarray) -> List[Dict]:
        """Detect brown/melanin spots."""
        spots = []
        l_channel = lab[:, :, 0]
        b_channel = lab[:, :, 2]

        # Brown spots: low L + specific b range
        masked_l = cv2.bitwise_and(l_channel, l_channel, mask=mask)
        mean_l = cv2.mean(l_channel, mask=mask)[0]

        dark = (masked_l < mean_l - 15).astype(np.uint8) * 255
        brown = cv2.bitwise_and(dark, mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        brown = cv2.morphologyEx(brown, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(brown, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if 20 < area < 400:
                x, y, w, h = cv2.boundingRect(contour)
                spots.append({
                    "center": (x + w // 2, y + h // 2),
                    "area": area,
                    "bbox": (x, y, w, h),
                })

        return spots

    def _analyze_region(self, roi_l: np.ndarray,
                        roi_mask: np.ndarray) -> Dict:
        """Analyze pigmentation in a region."""
        skin_vals = roi_l[roi_mask > 0].astype(np.float64)
        if len(skin_vals) == 0:
            return {"evenness": 100, "severity": "none"}

        std_val = np.std(skin_vals)
        score = max(0, 100 - std_val * 4)

        return {
            "evenness": float(score),
            "std_deviation": float(std_val),
            "severity": "none" if score > 80 else "mild" if score > 60 else "moderate",
        }

    def _classify(self, score: float) -> str:
        if score >= 85:
            return "minimal"
        elif score >= 70:
            return "mild"
        elif score >= 50:
            return "moderate"
        else:
            return "significant"

    def _determine_type(self, dark_patches: np.ndarray,
                        brown_spots: List, mask: np.ndarray) -> str:
        total_skin = max(1, cv2.countNonZero(mask))
        dark_ratio = cv2.countNonZero(dark_patches) / total_skin

        if dark_ratio > 0.15 and len(brown_spots) < 5:
            return "Melasma (diffuse darkening)"
        elif len(brown_spots) > 10:
            return "Sun spots / Age spots"
        elif dark_ratio > 0.05:
            return "Post-inflammatory hyperpigmentation"
        else:
            return "Minimal pigmentation concerns"

    def visualize(self, image: np.ndarray,
                  dark_patches: np.ndarray) -> np.ndarray:
        result = image.copy()
        overlay = np.zeros_like(image)
        overlay[dark_patches > 0] = (0, 100, 200)
        return cv2.addWeighted(result, 0.7, overlay, 0.3, 0)