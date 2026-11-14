# """
# Main skin analysis engine that orchestrates all analysis modules.
# """

# import cv2
# import numpy as np
# from typing import Dict, Optional
# import time

# from face_detector import FaceDetector
# from skin_detector import SkinDetector
# from blemish_detector import BlemishDetector
# from wrinkle_detector import WrinkleDetector
# from texture_analyzer import TextureAnalyzer
# from dark_circle_detector import DarkCircleDetector
# from pore_analyzer import PoreAnalyzer
# from skin_tone_classifier import SkinToneClassifier
# from utils import (
#     resize_image, calculate_image_quality,
#     put_text_with_background
# )
# import config


# class SkinAnalyzer:
#     """
#     Main skin analysis engine.
#     Combines all detection and analysis modules.
#     """

#     def __init__(self, use_mediapipe: bool = True):
#         print("[INFO] Initializing Skin Analysis Tool...")

#         self.face_detector = FaceDetector(use_mediapipe=use_mediapipe)
#         self.skin_detector = SkinDetector()
#         self.blemish_detector = BlemishDetector()
#         self.wrinkle_detector = WrinkleDetector()
#         self.texture_analyzer = TextureAnalyzer()
#         self.dark_circle_detector = DarkCircleDetector()
#         self.pore_analyzer = PoreAnalyzer()
#         self.skin_tone_classifier = SkinToneClassifier()

#         print("[INFO] All modules initialized successfully!")

#     def analyze(self, image: np.ndarray,
#                 detailed: bool = True) -> Dict:
#         """
#         Perform comprehensive skin analysis.

#         Args:
#             image: BGR input image
#             detailed: Whether to perform detailed analysis

#         Returns:
#             Complete analysis results dictionary
#         """
#         start_time = time.time()
#         results = {
#             "status": "processing",
#             "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
#         }

#         # ──── Step 1: Image Quality Check ────
#         print("[STEP 1/8] Checking image quality...")
#         quality = calculate_image_quality(image)
#         results["image_quality"] = quality

#         if not quality["is_good_quality"]:
#             print("[WARN] Image quality may affect analysis accuracy")

#         # ──── Step 2: Face Detection ────
#         print("[STEP 2/8] Detecting face...")
#         face_bbox = self.face_detector.detect_face(image)
#         if face_bbox is None:
#             results["status"] = "error"
#             results["error"] = "No face detected in the image"
#             return results

#         results["face_bbox"] = face_bbox
#         print(f"  → Face detected at {face_bbox}")

#         # ──── Step 3: Get Facial Regions ────
#         print("[STEP 3/8] Extracting facial regions...")
#         regions = self.face_detector.get_facial_regions(image)
#         face_mask = self.face_detector.get_face_mask(image)
#         results["regions"] = regions

#         # ──── Step 4: Skin Detection ────
#         print("[STEP 4/8] Detecting skin...")
#         skin_image, skin_mask = self.skin_detector.extract_skin(
#             image, face_mask
#         )
#         skin_stats = self.skin_detector.get_skin_color_stats(image, skin_mask)
#         skin_percentage = self.skin_detector.get_skin_percentage(
#             skin_mask, face_mask
#         )
#         results["skin_detection"] = {
#             "mask": skin_mask,
#             "stats": skin_stats,
#             "coverage_percentage": skin_percentage,
#         }
#         print(f"  → Skin coverage: {skin_percentage:.1f}%")

#         if cv2.countNonZero(skin_mask) < 1000:
#             results["status"] = "error"
#             results["error"] = "Insufficient skin area detected"
#             return results

#         # ──── Step 5: Skin Tone Classification ────
#         print("[STEP 5/8] Classifying skin tone...")
#         tone_results = self.skin_tone_classifier.classify_skin_tone(
#             image, skin_mask
#         )
#         results["skin_tone"] = tone_results
#         print(f"  → Skin tone: {tone_results.get('category', 'Unknown')}")
#         print(f"  → Fitzpatrick: {tone_results.get('fitzpatrick_name', 'Unknown')}")

#         # ──── Step 6: Blemish Detection ────
#         print("[STEP 6/8] Detecting blemishes...")
#         blemish_results = self.blemish_detector.detect_blemishes(
#             image, skin_mask
#         )
#         results["blemishes"] = blemish_results
#         print(f"  → Found {blemish_results['count']} blemishes "
#               f"({blemish_results['severity']})")

#         if detailed:
#             # ──── Step 7: Wrinkle Detection ────
#             print("[STEP 7/8] Detecting wrinkles...")
#             wrinkle_results = self.wrinkle_detector.detect_wrinkles(
#                 image, skin_mask, regions
#             )
#             results["wrinkles"] = wrinkle_results
#             print(f"  → Wrinkle severity: {wrinkle_results['severity']}")

#             # ──── Step 7b: Texture Analysis ────
#             print("  [7b] Analyzing texture...")
#             texture_results = self.texture_analyzer.analyze_texture(
#                 image, skin_mask, regions
#             )
#             results["texture"] = texture_results
#             print(f"  → Texture grade: {texture_results['grade']}")

#             # ──── Step 7c: Dark Circle Detection ────
#             print("  [7c] Detecting dark circles...")
#             dark_circle_results = self.dark_circle_detector.detect_dark_circles(
#                 image, regions
#             )
#             results["dark_circles"] = dark_circle_results
#             print(f"  → Dark circles: {dark_circle_results['severity']}")

#             # ──── Step 7d: Pore Analysis ────
#             print("  [7d] Analyzing pores...")
#             pore_results = self.pore_analyzer.analyze_pores(
#                 image, skin_mask, regions
#             )
#             results["pores"] = pore_results
#             print(f"  → Pore severity: {pore_results['severity']}")

#         # ──── Step 8: Calculate Overall Score ────
#         print("[STEP 8/8] Computing overall skin health score...")
#         overall_score = self._calculate_overall_score(results)
#         results["overall_score"] = overall_score
#         results["overall_grade"] = self._grade_score(overall_score)

#         elapsed = time.time() - start_time
#         results["processing_time"] = f"{elapsed:.2f}s"
#         results["status"] = "complete"

#         print(f"\n{'=' * 50}")
#         print(f"  OVERALL SKIN HEALTH SCORE: {overall_score:.1f}/100")
#         print(f"  GRADE: {results['overall_grade']}")
#         print(f"  Processing Time: {elapsed:.2f}s")
#         print(f"{'=' * 50}\n")

#         return results

#     def _calculate_overall_score(self, results: Dict) -> float:
#         """Calculate the overall skin health score."""
#         weights = config.SCORE_WEIGHTS
#         scores = {}

#         # Blemish score
#         if "blemishes" in results:
#             scores["blemish"] = results["blemishes"].get("score", 50)

#         # Wrinkle score
#         if "wrinkles" in results:
#             scores["wrinkle"] = results["wrinkles"].get("overall_score", 50)

#         # Texture score
#         if "texture" in results:
#             scores["texture"] = results["texture"].get("score", 50)

#         # Pore score
#         if "pores" in results:
#             scores["pore"] = results["pores"].get("score", 50)

#         # Dark circle score
#         if "dark_circles" in results:
#             scores["dark_circle"] = results["dark_circles"].get("score", 50)

#         # Skin evenness
#         if "skin_tone" in results:
#             scores["evenness"] = results["skin_tone"].get("evenness_score", 50)

#         # Weighted average
#         total_weight = 0
#         weighted_sum = 0

#         for category, score in scores.items():
#             weight = weights.get(category, 0.1)
#             weighted_sum += score * weight
#             total_weight += weight

#         if total_weight > 0:
#             overall = weighted_sum / total_weight
#         else:
#             overall = 50.0

#         return min(100, max(0, overall))

#     def _grade_score(self, score: float) -> str:
#         """Convert score to letter grade."""
#         if score >= 90:
#             return "A+ (Excellent)"
#         elif score >= 80:
#             return "A (Very Good)"
#         elif score >= 70:
#             return "B (Good)"
#         elif score >= 60:
#             return "C (Average)"
#         elif score >= 50:
#             return "D (Below Average)"
#         else:
#             return "F (Needs Attention)"

#     def create_visualization(self, image: np.ndarray,
#                              results: Dict) -> Dict[str, np.ndarray]:
#         """
#         Create all visualization images.

#         Returns:
#             Dictionary of visualization images.
#         """
#         visualizations = {}

#         # 1. Original with face regions
#         if results.get("regions"):
#             vis_regions = self.face_detector.draw_regions(
#                 image, results["regions"]
#             )
#             visualizations["face_regions"] = vis_regions

#         # 2. Skin detection
#         if "skin_detection" in results:
#             skin_mask = results["skin_detection"]["mask"]
#             vis_skin = self.skin_detector.visualize_skin(image, skin_mask)
#             visualizations["skin_detection"] = vis_skin

#         # 3. Blemish detection
#         if "blemishes" in results:
#             vis_blemish = self.blemish_detector.visualize_blemishes(
#                 image, results["blemishes"]["blemishes"]
#             )
#             visualizations["blemishes"] = vis_blemish

#         # 4. Wrinkle detection
#         if "wrinkles" in results:
#             vis_wrinkle = self.wrinkle_detector.visualize_wrinkles(
#                 image, results["wrinkles"]["wrinkle_map"]
#             )
#             visualizations["wrinkles"] = vis_wrinkle

#         # 5. Texture map
#         if "texture" in results:
#             vis_texture = self.texture_analyzer.visualize_texture(
#                 image, results["texture"]["texture_map"]
#             )
#             visualizations["texture"] = vis_texture

#         # 6. Dark circles
#         if "dark_circles" in results and results.get("regions"):
#             vis_dc = self.dark_circle_detector.visualize_dark_circles(
#                 image, results["regions"], results["dark_circles"]
#             )
#             visualizations["dark_circles"] = vis_dc

#         # 7. Pores
#         if "pores" in results:
#             vis_pore = self.pore_analyzer.visualize_pores(
#                 image,
#                 results["pores"]["pore_map"],
#                 results["pores"].get("pore_locations"),
#             )
#             visualizations["pores"] = vis_pore

#         # 8. Score summary overlay
#         vis_summary = self._create_summary_image(image, results)
#         visualizations["summary"] = vis_summary

#         return visualizations

#     def _create_summary_image(self, image: np.ndarray,
#                                results: Dict) -> np.ndarray:
#         """Create a summary image with scores overlaid."""
#         h, w = image.shape[:2]

#         # Create a wider canvas
#         canvas_w = w + 350
#         canvas = np.zeros((h, canvas_w, 3), dtype=np.uint8)
#         canvas[:, :w] = image

#         # Draw info panel on the right
#         panel_x = w + 10
#         y_offset = 30
#         line_height = 30

#         def draw_text(text, y, color=(255, 255, 255), scale=0.5):
#             cv2.putText(canvas, text, (panel_x, y),
#                        cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1)

#         def draw_bar(y, score, label):
#             # Label
#             draw_text(f"{label}:", y)
#             # Bar background
#             bar_x = panel_x
#             bar_y = y + 5
#             bar_w = 200
#             bar_h = 15
#             cv2.rectangle(canvas, (bar_x, bar_y),
#                          (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
#             # Bar fill
#             fill_w = int(bar_w * score / 100)
#             color = (
#                 (0, 255, 0) if score >= 70 else
#                 (0, 200, 255) if score >= 50 else
#                 (0, 0, 255)
#             )
#             cv2.rectangle(canvas, (bar_x, bar_y),
#                          (bar_x + fill_w, bar_y + bar_h), color, -1)
#             # Score text
#             draw_text(f"{score:.0f}", y + 18,
#                      color=(200, 200, 200), scale=0.4)

#         # Title
#         draw_text("SKIN ANALYSIS REPORT", y_offset, (0, 255, 255), 0.7)
#         y_offset += line_height + 10

#         # Overall score
#         overall = results.get("overall_score", 0)
#         grade = results.get("overall_grade", "N/A")
#         draw_text(f"Overall: {overall:.1f}/100", y_offset, (255, 255, 255), 0.6)
#         y_offset += line_height
#         draw_text(f"Grade: {grade}", y_offset, (0, 255, 0), 0.5)
#         y_offset += line_height + 10

#         # Divider
#         cv2.line(canvas, (panel_x, y_offset),
#                 (panel_x + 320, y_offset), (100, 100, 100), 1)
#         y_offset += 15

#         # Individual scores
#         if "skin_tone" in results:
#             tone = results["skin_tone"]
#             draw_text(f"Skin Tone: {tone.get('category', 'N/A')}", y_offset)
#             y_offset += line_height
#             draw_text(f"  {tone.get('fitzpatrick_name', '')}", y_offset,
#                      (180, 180, 180), 0.4)
#             y_offset += line_height

#         if "blemishes" in results:
#             b = results["blemishes"]
#             draw_bar(y_offset, b.get("score", 0), "Blemishes")
#             y_offset += line_height + 10
#             draw_text(
#                 f"  Count: {b['count']} | {b['severity']}",
#                 y_offset, (180, 180, 180), 0.4
#             )
#             y_offset += line_height

#         if "wrinkles" in results:
#             wr = results["wrinkles"]
#             draw_bar(y_offset, wr.get("overall_score", 0), "Wrinkles")
#             y_offset += line_height + 10

#         if "texture" in results:
#             tx = results["texture"]
#             draw_bar(y_offset, tx.get("score", 0), "Texture")
#             y_offset += line_height + 10

#         if "pores" in results:
#             po = results["pores"]
#             draw_bar(y_offset, po.get("score", 0), "Pores")
#             y_offset += line_height + 10

#         if "dark_circles" in results:
#             dc = results["dark_circles"]
#             draw_bar(y_offset, dc.get("score", 0), "Dark Circles")
#             y_offset += line_height + 10

#         if "skin_tone" in results:
#             ev = results["skin_tone"].get("evenness_score", 0)
#             draw_bar(y_offset, ev, "Evenness")
#             y_offset += line_height + 10

#         # Divider
#         y_offset += 5
#         cv2.line(canvas, (panel_x, y_offset),
#                 (panel_x + 320, y_offset), (100, 100, 100), 1)
#         y_offset += 15

#         # Processing time
#         draw_text(
#             f"Time: {results.get('processing_time', 'N/A')}",
#             y_offset, (150, 150, 150), 0.4
#         )

#         return canvas


"""
Main skin analysis engine — Rewritten for consistent scoring
and personalized results.
"""

import cv2
import numpy as np
from typing import Dict, Optional
import time

from face_detector import FaceDetector
from skin_detector import SkinDetector
from blemish_detector import BlemishDetector
from wrinkle_detector import WrinkleDetector
from texture_analyzer import TextureAnalyzer
from dark_circle_detector import DarkCircleDetector
from pore_analyzer import PoreAnalyzer
from skin_tone_classifier import SkinToneClassifier
from skin_type_detector import SkinTypeDetector
from pigmentation_detector import PigmentationDetector
from skin_age_estimator import SkinAgeEstimator
from recommendation_engine import RecommendationEngine
from routine_builder import RoutineBuilder
from utils import resize_image, calculate_image_quality
import config


class SkinAnalyzer:
    """Main skin analysis engine with consistent scoring."""

    def __init__(self, use_mediapipe: bool = False):
        print("[INFO] Initializing Skin Analysis Tool...")

        self.face_detector = FaceDetector(use_mediapipe=use_mediapipe)
        self.skin_detector = SkinDetector()
        self.blemish_detector = BlemishDetector()
        self.wrinkle_detector = WrinkleDetector()
        self.texture_analyzer = TextureAnalyzer()
        self.dark_circle_detector = DarkCircleDetector()
        self.pore_analyzer = PoreAnalyzer()
        self.skin_tone_classifier = SkinToneClassifier()
        self.skin_type_detector = SkinTypeDetector()
        self.pigmentation_detector = PigmentationDetector()
        self.skin_age_estimator = SkinAgeEstimator()
        self.recommendation_engine = RecommendationEngine()
        self.routine_builder = RoutineBuilder()

        # ── Cache to ensure consistent scores ──
        self._cache = {}

        print("[INFO] All modules initialized successfully!")

    def analyze(self, image: np.ndarray, detailed: bool = True) -> Dict:
        """Perform comprehensive skin analysis with consistent results."""
        start_time = time.time()

        # ── Create image hash for caching ──
        image_hash = hash(image.tobytes()[:10000])

        if image_hash in self._cache:
            print("[INFO] Returning cached results (consistent scores)")
            return self._cache[image_hash]

        results = {
            "status": "processing",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # ── Step 1: Quality Check ──
        print("[1/10] Checking image quality...")
        quality = calculate_image_quality(image)
        results["image_quality"] = quality

        # ── Step 2: Face Detection ──
        print("[2/10] Detecting face...")
        face_bbox = self.face_detector.detect_face(image)
        if face_bbox is None:
            results["status"] = "error"
            results["error"] = "No face detected. Please use a clear, front-facing photo."
            return results
        results["face_bbox"] = face_bbox

        # ── Step 3: Facial Regions ──
        print("[3/10] Mapping facial regions...")
        regions = self.face_detector.get_facial_regions(image)
        face_mask = self.face_detector.get_face_mask(image)
        results["regions"] = regions

        # ── Step 4: Skin Detection ──
        print("[4/10] Detecting skin...")
        skin_image, skin_mask = self.skin_detector.extract_skin(image, face_mask)
        skin_stats = self.skin_detector.get_skin_color_stats(image, skin_mask)
        results["skin_detection"] = {"mask": skin_mask, "stats": skin_stats}

        if cv2.countNonZero(skin_mask) < 500:
            results["status"] = "error"
            results["error"] = "Insufficient skin detected. Try better lighting."
            return results

        # ── Step 5: Skin Tone ──
        print("[5/10] Analyzing skin tone...")
        results["skin_tone"] = self.skin_tone_classifier.classify_skin_tone(image, skin_mask)

        # ── Step 6: Skin Type ──
        print("[6/10] Detecting skin type...")
        results["skin_type"] = self.skin_type_detector.detect_skin_type(image, skin_mask, regions)

        # ── Step 7: Detect Issues ──
        print("[7/10] Detecting skin concerns...")

        results["blemishes"] = self.blemish_detector.detect_blemishes(image, skin_mask)
        results["pigmentation"] = self.pigmentation_detector.detect_pigmentation(image, skin_mask, regions)

        if detailed:
            results["wrinkles"] = self.wrinkle_detector.detect_wrinkles(image, skin_mask, regions)
            results["texture"] = self.texture_analyzer.analyze_texture(image, skin_mask, regions)
            results["pores"] = self.pore_analyzer.analyze_pores(image, skin_mask, regions)
            results["dark_circles"] = self.dark_circle_detector.detect_dark_circles(image, regions)

        # ── Step 8: Overall Score ──
        print("[8/10] Computing overall score...")
        results["overall_score"] = self._calculate_overall_score(results)
        results["overall_grade"] = self._grade_score(results["overall_score"])

        # ── Step 9: Skin Age ──
        print("[9/10] Estimating skin age...")
        results["skin_age"] = self.skin_age_estimator.estimate_skin_age(results)

        # ── Step 10: Personalized Recommendations ──
        print("[10/10] Generating personalized recommendations...")
        results["recommendations"] = self.recommendation_engine.generate_recommendations(results)
        results["routine"] = self.routine_builder.build_routine(results, results["recommendations"])

        elapsed = time.time() - start_time
        results["processing_time"] = f"{elapsed:.2f}s"
        results["status"] = "complete"

        # ── Cache results ──
        self._cache[image_hash] = results

        self._print_summary(results)
        return results

    def _calculate_overall_score(self, results: Dict) -> float:
        """Calculate consistent overall score."""
        weights = config.SCORE_WEIGHTS
        scores = {}

        if "blemishes" in results:
            scores["acne"] = results["blemishes"].get("score", 75)
        if "pigmentation" in results:
            scores["pigmentation"] = results["pigmentation"].get("score", 75)
        if "wrinkles" in results:
            scores["wrinkles"] = results["wrinkles"].get("overall_score", 75)
        if "texture" in results:
            scores["texture"] = results["texture"].get("score", 75)
        if "pores" in results:
            scores["pores"] = results["pores"].get("score", 75)
        if "dark_circles" in results:
            scores["dark_circles"] = results["dark_circles"].get("score", 75)
        if "skin_type" in results:
            shine = results["skin_type"].get("shine_level", 50)
            dryness = results["skin_type"].get("dryness_level", 50)
            scores["hydration"] = max(0, 100 - abs(shine - 50) - abs(dryness - 50))
        if "skin_tone" in results:
            scores["evenness"] = results["skin_tone"].get("evenness_score", 75)

        total_weight = 0
        weighted_sum = 0
        for cat, score in scores.items():
            w = weights.get(cat, 0.1)
            weighted_sum += score * w
            total_weight += w

        return min(100, max(0, weighted_sum / total_weight)) if total_weight > 0 else 50

    def _grade_score(self, score: float) -> str:
        if score >= 90: return "Excellent ✨"
        elif score >= 80: return "Very Good 👍"
        elif score >= 70: return "Good 😊"
        elif score >= 60: return "Average 😐"
        elif score >= 50: return "Below Average 😕"
        else: return "Needs Attention ⚠️"

    def _print_summary(self, results: Dict):
        print(f"\n{'═' * 50}")
        print(f"  SKIN HEALTH SCORE: {results['overall_score']:.0f}/100")
        print(f"  GRADE: {results['overall_grade']}")
        print(f"  SKIN TYPE: {results.get('skin_type', {}).get('type', 'N/A')}")
        print(f"  SKIN AGE: {results.get('skin_age', {}).get('age_range', 'N/A')}")
        print(f"  TIME: {results['processing_time']}")

        concerns = results.get("recommendations", {}).get("priority_concerns", [])
        if concerns:
            print(f"  TOP CONCERNS: {', '.join(concerns)}")
        print(f"{'═' * 50}\n")

    def create_visualization(self, image: np.ndarray, results: Dict) -> Dict:
        """Create visualization images."""
        vis = {}

        if results.get("regions"):
            vis["face_regions"] = self.face_detector.draw_regions(image, results["regions"])

        if "skin_detection" in results:
            vis["skin_detection"] = self.skin_detector.visualize_skin(
                image, results["skin_detection"]["mask"]
            )

        if "blemishes" in results:
            vis["blemishes"] = self.blemish_detector.visualize_blemishes(
                image, results["blemishes"]["blemishes"]
            )

        if "wrinkles" in results:
            vis["wrinkles"] = self.wrinkle_detector.visualize_wrinkles(
                image, results["wrinkles"]["wrinkle_map"]
            )

        if "texture" in results:
            vis["texture"] = self.texture_analyzer.visualize_texture(
                image, results["texture"]["texture_map"]
            )

        if "pores" in results:
            vis["pores"] = self.pore_analyzer.visualize_pores(
                image, results["pores"]["pore_map"],
                results["pores"].get("pore_locations")
            )

        if "pigmentation" in results:
            vis["pigmentation"] = self.pigmentation_detector.visualize(
                image, results["pigmentation"]["dark_patch_map"]
            )

        return vis