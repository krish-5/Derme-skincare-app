"""
Utility functions for image processing and helper operations.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List


def resize_image(image: np.ndarray, max_width: int = 800,
                 max_height: int = 800) -> np.ndarray:
    """Resize image while maintaining aspect ratio."""
    h, w = image.shape[:2]
    if w <= max_width and h <= max_height:
        return image.copy()

    scale = min(max_width / w, max_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image to 0-255 range."""
    normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    return normalized.astype(np.uint8)


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0,
                tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    if len(image.shape) == 3:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        clahe = cv2.createCLAHE(clipLimit=clip_limit,
                                tileGridSize=tile_grid_size)
        lab[:, :, 0] = clahe.apply(l_channel)
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    else:
        clahe = cv2.createCLAHE(clipLimit=clip_limit,
                                tileGridSize=tile_grid_size)
        return clahe.apply(image)


def get_luminance(image: np.ndarray) -> np.ndarray:
    """Extract luminance channel from image."""
    if len(image.shape) == 3:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        return lab[:, :, 0]
    return image


def get_color_histogram(image: np.ndarray, mask: Optional[np.ndarray] = None,
                        bins: int = 256) -> np.ndarray:
    """Calculate color histogram for the image."""
    if len(image.shape) == 3:
        histograms = []
        for i in range(3):
            hist = cv2.calcHist([image], [i], mask, [bins], [0, 256])
            histograms.append(hist.flatten())
        return np.array(histograms)
    else:
        hist = cv2.calcHist([image], [0], mask, [bins], [0, 256])
        return hist.flatten()


def create_mask_from_contours(shape: Tuple[int, int],
                              contours: list) -> np.ndarray:
    """Create binary mask from contours."""
    mask = np.zeros(shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, contours, -1, 255, -1)
    return mask


def bilateral_filter(image: np.ndarray, d: int = 9,
                     sigma_color: float = 75,
                     sigma_space: float = 75) -> np.ndarray:
    """Apply bilateral filter for edge-preserving smoothing."""
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)


def extract_roi(image: np.ndarray, rect: Tuple[int, int, int, int],
                padding: int = 0) -> np.ndarray:
    """Extract region of interest with optional padding."""
    x, y, w, h = rect
    h_img, w_img = image.shape[:2]

    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(w_img, x + w + padding)
    y2 = min(h_img, y + h + padding)

    return image[y1:y2, x1:x2].copy()


def overlay_heatmap(image: np.ndarray, heatmap: np.ndarray,
                    alpha: float = 0.5,
                    colormap: int = cv2.COLORMAP_JET) -> np.ndarray:
    """Overlay a heatmap on the original image."""
    if len(heatmap.shape) == 2:
        heatmap_colored = cv2.applyColorMap(
            normalize_image(heatmap), colormap
        )
    else:
        heatmap_colored = heatmap

    if heatmap_colored.shape[:2] != image.shape[:2]:
        heatmap_colored = cv2.resize(
            heatmap_colored,
            (image.shape[1], image.shape[0])
        )

    return cv2.addWeighted(image, 1 - alpha, heatmap_colored, alpha, 0)


def calculate_image_quality(image: np.ndarray) -> dict:
    """Assess basic image quality metrics."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(
        image.shape) == 3 else image

    # Brightness
    brightness = np.mean(gray)

    # Contrast
    contrast = np.std(gray)

    # Sharpness (Laplacian variance)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = laplacian.var()

    # Noise estimation
    noise = estimate_noise(gray)

    return {
        "brightness": float(brightness),
        "contrast": float(contrast),
        "sharpness": float(sharpness),
        "noise": float(noise),
        "is_good_quality": (
            40 < brightness < 220 and
            contrast > 20 and
            sharpness > 50
        )
    }


def estimate_noise(image: np.ndarray) -> float:
    """Estimate noise level in the image using Laplacian method."""
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    h, w = image.shape
    M = [[1, -2, 1],
         [-2, 4, -2],
         [1, -2, 1]]

    sigma = np.sum(np.sum(np.absolute(
        cv2.filter2D(image.astype(np.float64), -1, np.array(M))
    )))
    sigma = sigma * np.sqrt(0.5 * np.pi) / (6 * (w - 2) * (h - 2))
    return sigma


def put_text_with_background(image: np.ndarray, text: str,
                              position: Tuple[int, int],
                              font_scale: float = 0.6,
                              color: Tuple[int, int, int] = (255, 255, 255),
                              bg_color: Tuple[int, int, int] = (0, 0, 0),
                              thickness: int = 1) -> np.ndarray:
    """Put text with a background rectangle for better readability."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

    x, y = position
    cv2.rectangle(
        image,
        (x - 5, y - text_size[1] - 5),
        (x + text_size[0] + 5, y + 5),
        bg_color, -1
    )
    cv2.putText(image, text, (x, y), font, font_scale, color, thickness)
    return image


def compute_glcm_features(image: np.ndarray,
                          distances: List[int] = [1],
                          angles: List[float] = [0]) -> dict:
    """Compute GLCM texture features manually."""
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Quantize to fewer levels for efficiency
    levels = 32
    image_q = (image / (256 / levels)).astype(np.uint8)

    h, w = image_q.shape
    glcm = np.zeros((levels, levels), dtype=np.float64)

    for d in distances:
        for angle in angles:
            dx = int(round(d * np.cos(angle)))
            dy = int(round(d * np.sin(angle)))

            for y in range(max(0, -dy), min(h, h - dy)):
                for x in range(max(0, -dx), min(w, w - dx)):
                    i = image_q[y, x]
                    j = image_q[y + dy, x + dx]
                    glcm[i, j] += 1

    # Normalize
    glcm_sum = glcm.sum()
    if glcm_sum > 0:
        glcm = glcm / glcm_sum

    # Features
    contrast = 0.0
    dissimilarity = 0.0
    homogeneity = 0.0
    energy = 0.0
    correlation = 0.0

    mu_i = 0.0
    mu_j = 0.0
    sigma_i = 0.0
    sigma_j = 0.0

    for i in range(levels):
        for j in range(levels):
            contrast += (i - j) ** 2 * glcm[i, j]
            dissimilarity += abs(i - j) * glcm[i, j]
            homogeneity += glcm[i, j] / (1 + (i - j) ** 2)
            energy += glcm[i, j] ** 2
            mu_i += i * glcm[i, j]
            mu_j += j * glcm[i, j]

    for i in range(levels):
        for j in range(levels):
            sigma_i += (i - mu_i) ** 2 * glcm[i, j]
            sigma_j += (j - mu_j) ** 2 * glcm[i, j]

    sigma_i = np.sqrt(sigma_i)
    sigma_j = np.sqrt(sigma_j)

    if sigma_i > 0 and sigma_j > 0:
        for i in range(levels):
            for j in range(levels):
                correlation += (
                    (i - mu_i) * (j - mu_j) * glcm[i, j]
                ) / (sigma_i * sigma_j)

    entropy = 0.0
    for i in range(levels):
        for j in range(levels):
            if glcm[i, j] > 0:
                entropy -= glcm[i, j] * np.log2(glcm[i, j])

    return {
        "contrast": contrast,
        "dissimilarity": dissimilarity,
        "homogeneity": homogeneity,
        "energy": energy,
        "correlation": correlation,
        "entropy": entropy,
    }