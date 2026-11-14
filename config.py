"""
Configuration constants for the Skin Analysis Tool.
"""

# ──────────────── Face Detection ────────────────
FACE_CASCADE_PATH = "haarcascade_frontalface_default.xml"
EYE_CASCADE_PATH = "haarcascade_eye.xml"
USE_MEDIAPIPE = False  # Use MediaPipe for face mesh (more accurate)

# ──────────────── Skin Detection ────────────────
# HSV range for skin detection
SKIN_HSV_LOWER = (0, 20, 70)
SKIN_HSV_UPPER = (20, 255, 255)

# YCrCb range for skin detection
SKIN_YCRCB_LOWER = (0, 133, 77)
SKIN_YCRCB_UPPER = (255, 173, 127)

# ──────────────── Analysis Parameters ────────────────
# Blemish detection
BLEMISH_MIN_AREA = 20
BLEMISH_MAX_AREA = 500
BLEMISH_CIRCULARITY_THRESHOLD = 0.4

# Wrinkle detection
WRINKLE_GABOR_KSIZE = 31
WRINKLE_GABOR_SIGMA = 4.0
WRINKLE_GABOR_THETA_COUNT = 4
WRINKLE_GABOR_LAMBD = 10.0
WRINKLE_GABOR_GAMMA = 0.5
WRINKLE_THRESHOLD = 30

# Pore detection
PORE_MIN_AREA = 3
PORE_MAX_AREA = 80
PORE_THRESHOLD = 15

# Dark circle detection
DARK_CIRCLE_THRESHOLD = 0.7

# Texture analysis
TEXTURE_BLOCK_SIZE = 32

# ──────────────── Skin Tone Categories ────────────────
SKIN_TONE_CATEGORIES = {
    "Very Fair": (220, 255),
    "Fair": (190, 220),
    "Medium": (160, 190),
    "Olive": (130, 160),
    "Brown": (90, 130),
    "Dark Brown": (60, 90),
    "Dark": (0, 60),
}

# ──────────────── Scoring Weights ────────────────
SCORE_WEIGHTS = {
    "blemish": 0.25,
    "wrinkle": 0.20,
    "texture": 0.20,
    "pore": 0.15,
    "dark_circle": 0.10,
    "evenness": 0.10,
}

# ──────────────── GUI Settings ────────────────
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
THUMBNAIL_SIZE = (400, 400)

# ──────────────── Report ────────────────
REPORT_TEMPLATE = "skin_analysis_report_{timestamp}.pdf"






# 
"""
Configuration for Skin Analysis Tool — Minimalist Style
"""

# ──────────────── Face Detection ────────────────
USE_MEDIAPIPE = False

# ──────────────── Skin Detection ────────────────
SKIN_HSV_LOWER = (0, 20, 70)
SKIN_HSV_UPPER = (20, 255, 255)
SKIN_YCRCB_LOWER = (0, 133, 77)
SKIN_YCRCB_UPPER = (255, 173, 127)

# ──────────────── Analysis Parameters ────────────────
BLEMISH_MIN_AREA = 25
BLEMISH_MAX_AREA = 500
BLEMISH_CIRCULARITY_THRESHOLD = 0.4

WRINKLE_GABOR_KSIZE = 31
WRINKLE_GABOR_SIGMA = 4.0
WRINKLE_GABOR_THETA_COUNT = 4
WRINKLE_GABOR_LAMBD = 10.0
WRINKLE_GABOR_GAMMA = 0.5
WRINKLE_THRESHOLD = 50

PORE_MIN_AREA = 5
PORE_MAX_AREA = 80
PORE_THRESHOLD = 18

DARK_CIRCLE_THRESHOLD = 0.7

TEXTURE_BLOCK_SIZE = 32

# ──────────────── Skin Tone ────────────────
SKIN_TONE_CATEGORIES = {
    "Very Fair": (220, 255),
    "Fair": (190, 220),
    "Medium": (160, 190),
    "Olive": (130, 160),
    "Brown": (90, 130),
    "Dark Brown": (60, 90),
    "Dark": (0, 60),
}

# ──────────────── Scoring Weights ────────────────
SCORE_WEIGHTS = {
    "acne": 0.20,
    "pigmentation": 0.15,
    "wrinkles": 0.15,
    "texture": 0.15,
    "pores": 0.10,
    "dark_circles": 0.10,
    "hydration": 0.10,
    "evenness": 0.05,
}

# ──────────────── Skin Concerns ────────────────
CONCERN_CATEGORIES = [
    "Acne & Breakouts",
    "Pigmentation & Dark Spots",
    "Fine Lines & Wrinkles",
    "Enlarged Pores",
    "Dark Circles",
    "Uneven Texture",
    "Dullness",
    "Oiliness",
    "Dryness",
    "Redness & Sensitivity",
]

# ──────────────── GUI ────────────────
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# ──────────────── Colors (Minimalist Brand Style) ────────────────
COLORS = {
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F5F5F5",
    "bg_dark": "#1A1A1A",
    "bg_card": "#FAFAFA",
    "accent": "#E85D3A",
    "accent_light": "#FF7F5C",
    "text_primary": "#1A1A1A",
    "text_secondary": "#666666",
    "text_light": "#999999",
    "green": "#2ECC71",
    "yellow": "#F39C12",
    "red": "#E74C3C",
    "blue": "#3498DB",
    "border": "#E0E0E0",
    "score_excellent": "#2ECC71",
    "score_good": "#27AE60",
    "score_average": "#F39C12",
    "score_poor": "#E74C3C",
}