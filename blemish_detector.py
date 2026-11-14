"""
Blemish and acne detection module.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import config


class BlemishDetector:
    """Detects blemishes, acne, and dark spots on the skin."""

    def __init__(self):
        self.min_area = config.BLEMISH_MIN_AREA
        self.max_area = config.BLEMISH_MAX_AREA
        self.circularity_threshold = config.BLEMISH_CIRCULARITY_THRESHOLD

    def detect_blemishes(self, image: np.ndarray,
                         skin_mask: np.ndarray) -> Dict:
        """
        Detect blemishes in the skin region.

        Returns:
            Dictionary with blemish info, locations, severity
        """
        # Convert to different color spaces
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        a_channel = lab[:, :, 1]  # Red-green
        b_channel = lab[:, :, 2]  # Blue-yellow

        blemishes = []

        # Method 1: Dark spot detection using luminance
        dark_spots = self._detect_dark_spots(l_channel, skin_mask)
        blemishes.extend(dark_spots)

        # Method 2: Red spot detection (acne/inflammation)
        red_spots = self._detect_red_spots(image, a_channel, skin_mask)
        blemishes.extend(red_spots)

        # Method 3: Blob detection
        blobs = self._detect_blobs(gray, skin_mask)
        blemishes.extend(blobs)

        # Remove duplicates (overlapping detections)
        blemishes = self._remove_duplicates(blemishes)

        # Classify severity
        severity = self._classify_severity(len(blemishes), skin_mask)

        return {
            "blemishes": blemishes,
            "count": len(blemishes),
            "severity": severity,
            "score": self._calculate_score(len(blemishes), skin_mask),
            "types": self._categorize_blemishes(blemishes),
        }

    def _detect_dark_spots(self, l_channel: np.ndarray,
                           skin_mask: np.ndarray) -> List[Dict]:
        """Detect dark spots using luminance analysis."""
        spots = []

        # Apply skin mask
        masked_l = cv2.bitwise_and(l_channel, l_channel, mask=skin_mask)

        # Calculate local mean
        kernel_size = 31
        local_mean = cv2.GaussianBlur(masked_l.astype(np.float64),
                                       (kernel_size, kernel_size), 0)

        # Pixels significantly darker than local mean
        diff = local_mean - masked_l.astype(np.float64)
        dark_mask = (diff > 25).astype(np.uint8) * 255

        # Apply skin mask
        dark_mask = cv2.bitwise_and(dark_mask, skin_mask)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(
            dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area <= area <= self.max_area:
                perimeter = cv2.arcLength(contour, True)
                circularity = (
                    4 * np.pi * area / (perimeter ** 2)
                    if perimeter > 0 else 0
                )

                if circularity >= self.circularity_threshold:
                    x, y, w, h = cv2.boundingRect(contour)
                    center = (x + w // 2, y + h // 2)
                    radius = max(w, h) // 2

                    spots.append({
                        "type": "dark_spot",
                        "center": center,
                        "radius": radius,
                        "area": area,
                        "circularity": circularity,
                        "bbox": (x, y, w, h),
                        "contour": contour,
                        "severity": "mild" if area < 100 else "moderate"
                    })

        return spots

    def _detect_red_spots(self, image: np.ndarray,
                          a_channel: np.ndarray,
                          skin_mask: np.ndarray) -> List[Dict]:
        """Detect red/inflamed areas (acne)."""
        spots = []

        # Apply skin mask
        masked_a = cv2.bitwise_and(a_channel, a_channel, mask=skin_mask)

        # Red areas have higher 'a' values in LAB
        mean_a = cv2.mean(a_channel, mask=skin_mask)[0]
        std_a = np.std(a_channel[skin_mask > 0]) if cv2.countNonZero(skin_mask) > 0 else 0

        if std_a == 0:
            return spots

        threshold = mean_a + 1.5 * std_a
        red_mask = (masked_a > threshold).astype(np.uint8) * 255
        red_mask = cv2.bitwise_and(red_mask, skin_mask)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area <= area <= self.max_area:
                x, y, w, h = cv2.boundingRect(contour)
                center = (x + w // 2, y + h // 2)
                radius = max(w, h) // 2

                # Check redness intensity
                roi = image[y:y + h, x:x + w]
                if roi.size > 0:
                    mean_color = cv2.mean(roi)[:3]
                    redness = mean_color[2] - (mean_color[0] + mean_color[1]) / 2

                    if redness > 10:
                        spots.append({
                            "type": "acne",
                            "center": center,
                            "radius": radius,
                            "area": area,
                            "redness": redness,
                            "bbox": (x, y, w, h),
                            "contour": contour,
                            "severity": (
                                "severe" if redness > 40 else
                                "moderate" if redness > 20 else "mild"
                            )
                        })

        return spots

    def _detect_blobs(self, gray: np.ndarray,
                      skin_mask: np.ndarray) -> List[Dict]:
        """Detect blobs using SimpleBlobDetector."""
        spots = []

        masked = cv2.bitwise_and(gray, gray, mask=skin_mask)

        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = self.min_area
        params.maxArea = self.max_area
        params.filterByCircularity = True
        params.minCircularity = self.circularity_threshold
        params.filterByConvexity = True
        params.minConvexity = 0.5
        params.filterByInertia = True
        params.minInertiaRatio = 0.3
        params.filterByColor = True
        params.blobColor = 0  # Dark blobs

        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(masked)

        for kp in keypoints:
            center = (int(kp.pt[0]), int(kp.pt[1]))
            radius = int(kp.size / 2)
            area = np.pi * radius ** 2

            # Verify it's in skin region
            if (0 <= center[1] < skin_mask.shape[0] and
                0 <= center[0] < skin_mask.shape[1] and
                skin_mask[center[1], center[0]] > 0):
                spots.append({
                    "type": "blemish",
                    "center": center,
                    "radius": radius,
                    "area": area,
                    "bbox": (
                        center[0] - radius, center[1] - radius,
                        2 * radius, 2 * radius
                    ),
                    "severity": "mild"
                })

        return spots

    def _remove_duplicates(self, blemishes: List[Dict],
                           min_distance: int = 15) -> List[Dict]:
        """Remove overlapping blemish detections."""
        if not blemishes:
            return blemishes

        unique = []
        used = set()

        for i, b1 in enumerate(blemishes):
            if i in used:
                continue
            for j, b2 in enumerate(blemishes[i + 1:], i + 1):
                if j in used:
                    continue
                dist = np.sqrt(
                    (b1["center"][0] - b2["center"][0]) ** 2 +
                    (b1["center"][1] - b2["center"][1]) ** 2
                )
                if dist < min_distance:
                    used.add(j)
            unique.append(b1)

        return unique

    def _classify_severity(self, count: int,
                           skin_mask: np.ndarray) -> str:
        """Classify overall blemish severity."""
        skin_area = cv2.countNonZero(skin_mask)
        if skin_area == 0:
            return "unknown"

        density = count / (skin_area / 10000)  # per 10000 pixels

        if density < 0.5:
            return "clear"
        elif density < 2:
            return "mild"
        elif density < 5:
            return "moderate"
        else:
            return "severe"

    def _calculate_score(self, count: int,
                         skin_mask: np.ndarray) -> float:
        """Calculate blemish score (0-100, higher is better)."""
        skin_area = cv2.countNonZero(skin_mask)
        if skin_area == 0:
            return 50.0

        density = count / (skin_area / 10000)
        score = max(0, 100 - density * 15)
        return min(100, score)

    def _categorize_blemishes(self, blemishes: List[Dict]) -> Dict:
        """Categorize blemishes by type."""
        categories = {}
        for b in blemishes:
            btype = b.get("type", "unknown")
            if btype not in categories:
                categories[btype] = 0
            categories[btype] += 1
        return categories

    def visualize_blemishes(self, image: np.ndarray,
                            blemishes: List[Dict]) -> np.ndarray:
        """Draw detected blemishes on the image."""
        result = image.copy()

        colors = {
            "acne": (0, 0, 255),       # Red
            "dark_spot": (139, 0, 139), # Purple
            "blemish": (0, 165, 255),   # Orange
        }

        for b in blemishes:
            color = colors.get(b["type"], (0, 0, 255))
            center = b["center"]
            radius = max(b["radius"], 5)

            cv2.circle(result, center, radius + 3, color, 2)

            # Severity indicator
            severity_colors = {
                "mild": (0, 255, 0),
                "moderate": (0, 165, 255),
                "severe": (0, 0, 255),
            }
            sev_color = severity_colors.get(b.get("severity", "mild"), (255, 255, 255))
            cv2.circle(result, center, 3, sev_color, -1)

        return result