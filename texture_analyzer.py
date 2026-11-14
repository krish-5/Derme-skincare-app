"""
Skin texture analysis module.
"""

import cv2
import numpy as np
from typing import Dict, Optional
import config
from utils import compute_glcm_features


class TextureAnalyzer:
    """Analyzes skin texture quality and uniformity."""

    def __init__(self):
        self.block_size = config.TEXTURE_BLOCK_SIZE

    def analyze_texture(self, image: np.ndarray,
                        skin_mask: np.ndarray,
                        regions: Optional[Dict] = None) -> Dict:
        """
        Perform comprehensive texture analysis.

        Returns:
            Dictionary with texture metrics and scores.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        masked_gray = cv2.bitwise_and(gray, gray, mask=skin_mask)

        # Overall texture analysis
        roughness = self._calculate_roughness(masked_gray, skin_mask)
        uniformity = self._calculate_uniformity(masked_gray, skin_mask)
        smoothness = self._calculate_smoothness(masked_gray, skin_mask)

        # GLCM features
        glcm = self._compute_glcm_analysis(masked_gray, skin_mask)

        # LBP (Local Binary Pattern) texture
        lbp_features = self._compute_lbp(masked_gray, skin_mask)

        # Texture map
        texture_map = self._create_texture_map(masked_gray, skin_mask)

        # Regional analysis
        regional = {}
        if regions:
            for name, (x, y, w, h) in regions.items():
                if w > 10 and h > 10:
                    roi = gray[y:y + h, x:x + w]
                    mask_roi = skin_mask[y:y + h, x:x + w]
                    if cv2.countNonZero(mask_roi) > 100:
                        regional[name] = {
                            "roughness": self._calculate_roughness(roi, mask_roi),
                            "uniformity": self._calculate_uniformity(roi, mask_roi),
                            "smoothness": self._calculate_smoothness(roi, mask_roi),
                        }

        # Overall score
        score = self._calculate_texture_score(roughness, uniformity, smoothness)

        return {
            "roughness": roughness,
            "uniformity": uniformity,
            "smoothness": smoothness,
            "glcm_features": glcm,
            "lbp_features": lbp_features,
            "texture_map": texture_map,
            "regional_analysis": regional,
            "score": score,
            "grade": self._grade_texture(score),
        }

    def _calculate_roughness(self, gray: np.ndarray,
                              mask: np.ndarray) -> float:
        """
        Calculate skin roughness using high-frequency content analysis.
        """
        if cv2.countNonZero(mask) == 0:
            return 0.0

        # Apply Laplacian to detect edges / roughness
        smoothed = cv2.GaussianBlur(gray, (5, 5), 1.5)
        laplacian = cv2.Laplacian(smoothed, cv2.CV_64F)
        laplacian = np.abs(laplacian)

        # Only consider skin pixels
        skin_pixels = laplacian[mask > 0]
        if len(skin_pixels) == 0:
            return 0.0

        roughness = np.mean(skin_pixels)
        return float(roughness)

    def _calculate_uniformity(self, gray: np.ndarray,
                               mask: np.ndarray) -> float:
        """Calculate skin color/texture uniformity."""
        if cv2.countNonZero(mask) == 0:
            return 0.0

        skin_pixels = gray[mask > 0].astype(np.float64)
        if len(skin_pixels) == 0:
            return 0.0

        # Coefficient of variation (lower = more uniform)
        mean_val = np.mean(skin_pixels)
        std_val = np.std(skin_pixels)

        if mean_val == 0:
            return 0.0

        cv_val = std_val / mean_val
        uniformity = max(0, 1 - cv_val) * 100
        return float(uniformity)

    def _calculate_smoothness(self, gray: np.ndarray,
                               mask: np.ndarray) -> float:
        """Calculate skin smoothness."""
        if cv2.countNonZero(mask) == 0:
            return 0.0

        # Compare original with smoothed version
        smoothed = cv2.bilateralFilter(gray, 15, 75, 75)
        diff = cv2.absdiff(gray, smoothed)

        skin_diff = diff[mask > 0].astype(np.float64)
        if len(skin_diff) == 0:
            return 0.0

        # Lower difference = smoother skin
        mean_diff = np.mean(skin_diff)
        smoothness = max(0, 100 - mean_diff * 5)
        return float(smoothness)

    def _compute_glcm_analysis(self, gray: np.ndarray,
                                mask: np.ndarray) -> Dict:
        """Compute GLCM-based texture features for skin analysis."""
        if cv2.countNonZero(mask) == 0:
            return {}

        # Get bounding box of skin region
        coords = cv2.findNonZero(mask)
        if coords is None:
            return {}

        x, y, w, h = cv2.boundingRect(coords)
        roi = gray[y:y + h, x:x + w]

        # Compute GLCM features
        features = compute_glcm_features(
            roi, distances=[1, 2], angles=[0, np.pi / 4]
        )

        return features

    def _compute_lbp(self, gray: np.ndarray,
                     mask: np.ndarray) -> Dict:
        """Compute Local Binary Pattern features."""
        if cv2.countNonZero(mask) == 0:
            return {}

        h, w = gray.shape
        lbp_image = np.zeros_like(gray, dtype=np.uint8)

        # 8-neighbor LBP
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if mask[i, j] == 0:
                    continue

                center = gray[i, j]
                code = 0
                code |= (1 << 7) if gray[i - 1, j - 1] >= center else 0
                code |= (1 << 6) if gray[i - 1, j] >= center else 0
                code |= (1 << 5) if gray[i - 1, j + 1] >= center else 0
                code |= (1 << 4) if gray[i, j + 1] >= center else 0
                code |= (1 << 3) if gray[i + 1, j + 1] >= center else 0
                code |= (1 << 2) if gray[i + 1, j] >= center else 0
                code |= (1 << 1) if gray[i + 1, j - 1] >= center else 0
                code |= (1 << 0) if gray[i, j - 1] >= center else 0

                lbp_image[i, j] = code

        # LBP histogram
        skin_lbp = lbp_image[mask > 0]
        if len(skin_lbp) == 0:
            return {}

        hist, _ = np.histogram(skin_lbp, bins=256, range=(0, 256))
        hist = hist.astype(np.float64)
        hist /= (hist.sum() + 1e-6)

        # Features from LBP histogram
        entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0]))
        energy = np.sum(hist ** 2)

        return {
            "lbp_entropy": float(entropy),
            "lbp_energy": float(energy),
            "lbp_mean": float(np.mean(skin_lbp)),
            "lbp_std": float(np.std(skin_lbp)),
            "lbp_image": lbp_image,
        }

    def _create_texture_map(self, gray: np.ndarray,
                            mask: np.ndarray) -> np.ndarray:
        """Create a texture quality heatmap."""
        h, w = gray.shape
        texture_map = np.zeros((h, w), dtype=np.float64)
        bs = self.block_size

        for y in range(0, h - bs, bs // 2):
            for x in range(0, w - bs, bs // 2):
                block = gray[y:y + bs, x:x + bs]
                block_mask = mask[y:y + bs, x:x + bs]

                if cv2.countNonZero(block_mask) < bs * bs * 0.3:
                    continue

                # Local texture quality = inverse of variance
                skin_vals = block[block_mask > 0].astype(np.float64)
                if len(skin_vals) > 10:
                    local_roughness = np.std(skin_vals)
                    texture_map[y:y + bs, x:x + bs] = local_roughness

        texture_map = cv2.normalize(
            texture_map, None, 0, 255, cv2.NORM_MINMAX
        ).astype(np.uint8)

        return texture_map

    def _calculate_texture_score(self, roughness: float,
                                  uniformity: float,
                                  smoothness: float) -> float:
        """Calculate overall texture score."""
        # Roughness: lower is better (invert)
        roughness_score = max(0, 100 - roughness * 3)

        # Weighted combination
        score = (
            roughness_score * 0.35 +
            uniformity * 0.30 +
            smoothness * 0.35
        )
        return min(100, max(0, score))

    def _grade_texture(self, score: float) -> str:
        """Grade the texture quality."""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Average"
        elif score >= 35:
            return "Below Average"
        else:
            return "Poor"

    def visualize_texture(self, image: np.ndarray,
                          texture_map: np.ndarray) -> np.ndarray:
        """Visualize texture map as heatmap overlay."""
        from utils import overlay_heatmap
        return overlay_heatmap(image, texture_map, alpha=0.4,
                              colormap=cv2.COLORMAP_INFERNO)