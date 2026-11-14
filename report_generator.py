# """
# Report generation module for skin analysis results.
# """

# import cv2
# import numpy as np
# from typing import Dict, Optional
# import time
# import os


# class ReportGenerator:
#     """Generates detailed skin analysis reports."""

#     def generate_text_report(self, results: Dict) -> str:
#         """Generate a text-based analysis report."""
#         lines = []
#         lines.append("=" * 60)
#         lines.append("         SKIN ANALYSIS REPORT")
#         lines.append("=" * 60)
#         lines.append(f"Date: {results.get('timestamp', 'N/A')}")
#         lines.append(f"Processing Time: {results.get('processing_time', 'N/A')}")
#         lines.append("")

#         # ── Overall Score ──
#         lines.append("─" * 40)
#         lines.append("  OVERALL SKIN HEALTH")
#         lines.append("─" * 40)
#         lines.append(f"  Score: {results.get('overall_score', 0):.1f} / 100")
#         lines.append(f"  Grade: {results.get('overall_grade', 'N/A')}")
#         lines.append("")

#         # ── Skin Tone ──
#         if "skin_tone" in results:
#             tone = results["skin_tone"]
#             lines.append("─" * 40)
#             lines.append("  SKIN TONE ANALYSIS")
#             lines.append("─" * 40)
#             lines.append(f"  Category: {tone.get('category', 'N/A')}")
#             lines.append(f"  Fitzpatrick Type: {tone.get('fitzpatrick_name', 'N/A')}")
#             lines.append(f"    → {tone.get('fitzpatrick_description', '')}")

#             undertone = tone.get("undertone", {})
#             lines.append(f"  Undertone: {undertone.get('type', 'N/A')}")
#             lines.append(f"    → {undertone.get('description', '')}")

#             lines.append(f"  ITA Angle: {tone.get('ita_angle', 0):.1f}°")
#             lines.append(f"  ITA Category: {tone.get('ita_category', 'N/A')}")
#             lines.append(f"  Hex Color: {tone.get('hex_color', 'N/A')}")
#             lines.append(f"  Evenness Score: {tone.get('evenness_score', 0):.1f}/100")
#             lines.append("")

#         # ── Blemishes ──
#         if "blemishes" in results:
#             b = results["blemishes"]
#             lines.append("─" * 40)
#             lines.append("  BLEMISH ANALYSIS")
#             lines.append("─" * 40)
#             lines.append(f"  Score: {b.get('score', 0):.1f} / 100")
#             lines.append(f"  Total Count: {b.get('count', 0)}")
#             lines.append(f"  Severity: {b.get('severity', 'N/A')}")
#             types = b.get("types", {})
#             if types:
#                 lines.append("  Types Detected:")
#                 for btype, count in types.items():
#                     lines.append(f"    - {btype}: {count}")
#             lines.append("")

#         # ── Wrinkles ──
#         if "wrinkles" in results:
#             w = results["wrinkles"]
#             lines.append("─" * 40)
#             lines.append("  WRINKLE ANALYSIS")
#             lines.append("─" * 40)
#             lines.append(f"  Score: {w.get('overall_score', 0):.1f} / 100")
#             lines.append(f"  Severity: {w.get('severity', 'N/A')}")
#             lines.append(f"  Density: {w.get('wrinkle_density', 0):.2f}%")

#             regional = w.get("regional_scores", {})
#             if regional:
#                 lines.append("  Regional Scores:")
#                 for region, score in regional.items():
#                     lines.append(f"    - {region}: {score:.1f}/100")
#             lines.append("")

#         # ── Texture ──
#         if "texture" in results:
#             t = results["texture"]
#             lines.append("─" * 40)
#             lines.append("  TEXTURE ANALYSIS")
#             lines.append("─" * 40)
#             lines.append(f"  Score: {t.get('score', 0):.1f} / 100")
#             lines.append(f"  Grade: {t.get('grade', 'N/A')}")
#             lines.append(f"  Roughness: {t.get('roughness', 0):.2f}")
#             lines.append(f"  Uniformity: {t.get('uniformity', 0):.1f}%")
#             lines.append(f"  Smoothness: {t.get('smoothness', 0):.1f}%")

#             glcm = t.get("glcm_features", {})
#             if glcm:
#                 lines.append("  GLCM Features:")
#                 for feat, val in glcm.items():
#                     lines.append(f"    - {feat}: {val:.4f}")
#             lines.append("")

#         # ── Pores ──
#         if "pores" in results:
#             p = results["pores"]
#             lines.append("─" * 40)
#             lines.append("  PORE ANALYSIS")
#             lines.append("─" * 40)
#             lines.append(f"  Score: {p.get('score', 0):.1f} / 100")
#             lines.append(f"  Pore Count: {p.get('pore_count', 0)}")
#             lines.append(f"  Density: {p.get('density', 0):.2f}%")
#             lines.append(f"  Average Size: {p.get('average_size', 0):.1f} px")
#             lines.append(f"  Severity: {p.get('severity', 'N/A')}")

#             regional_p = p.get("regional_analysis", {})
#             if regional_p:
#                 lines.append("  Regional Analysis:")
#                 for region, data in regional_p.items():
#                     lines.append(
#                         f"    - {region}: {data.get('count', 0)} pores "
#                         f"({data.get('severity', 'N/A')})"
#                     )
#             lines.append("")

#         # ── Dark Circles ──
#         if "dark_circles" in results:
#             dc = results["dark_circles"]
#             lines.append("─" * 40)
#             lines.append("  DARK CIRCLE ANALYSIS")
#             lines.append("─" * 40)
#             lines.append(f"  Score: {dc.get('score', 0):.1f} / 100")
#             lines.append(f"  Severity: {dc.get('severity', 'N/A')}")
#             lines.append(f"  Darkness Level: {dc.get('darkness_level', 0):.1f}%")

#             color_analysis = dc.get("color_analysis", {})
#             if color_analysis:
#                 lines.append(f"  Type: {color_analysis.get('type', 'N/A')}")
#                 lines.append(f"    → {color_analysis.get('description', '')}")
#             lines.append("")

#         # ── Recommendations ──
#         lines.append("─" * 40)
#         lines.append("  RECOMMENDATIONS")
#         lines.append("─" * 40)
#         recommendations = self._generate_recommendations(results)
#         for i, rec in enumerate(recommendations, 1):
#             lines.append(f"  {i}. {rec}")

#         lines.append("")
#         lines.append("=" * 60)
#         lines.append("  Report generated by Skin Analysis Tool")
#         lines.append("  Note: This is for informational purposes only.")
#         lines.append("  Consult a dermatologist for professional advice.")
#         lines.append("=" * 60)

#         return "\n".join(lines)

#     def _generate_recommendations(self, results: Dict) -> list:
#         """Generate skin care recommendations based on analysis."""
#         recs = []

#         overall = results.get("overall_score", 50)

#         # Blemish recommendations
#         if "blemishes" in results:
#             severity = results["blemishes"].get("severity", "clear")
#             if severity in ["moderate", "severe"]:
#                 recs.append(
#                     "Consider using a gentle cleanser with salicylic acid "
#                     "or benzoyl peroxide for blemish control."
#                 )
#                 recs.append(
#                     "Avoid touching your face and change pillowcases regularly."
#                 )
#             elif severity == "mild":
#                 recs.append(
#                     "Maintain a consistent skincare routine with "
#                     "non-comedogenic products."
#                 )

#         # Wrinkle recommendations
#         if "wrinkles" in results:
#             severity = results["wrinkles"].get("severity", "minimal")
#             if severity in ["moderate", "severe"]:
#                 recs.append(
#                     "Use products with retinol or peptides to help "
#                     "reduce fine lines and wrinkles."
#                 )
#                 recs.append("Always apply broad-spectrum SPF 30+ sunscreen.")
#             elif severity == "mild":
#                 recs.append(
#                     "Start incorporating anti-aging ingredients like "
#                     "vitamin C and hyaluronic acid."
#                 )

#         # Texture recommendations
#         if "texture" in results:
#             grade = results["texture"].get("grade", "Average")
#             if grade in ["Below Average", "Poor"]:
#                 recs.append(
#                     "Exfoliate 1-2 times per week with a gentle "
#                     "chemical exfoliant (AHA/BHA)."
#                 )

#         # Pore recommendations
#         if "pores" in results:
#             severity = results["pores"].get("severity", "normal")
#             if severity in ["visible", "enlarged"]:
#                 recs.append(
#                     "Use a clay mask weekly and niacinamide serum "
#                     "to help minimize pore appearance."
#                 )

#         # Dark circle recommendations
#         if "dark_circles" in results:
#             severity = results["dark_circles"].get("severity", "none")
#             if severity in ["moderate", "severe"]:
#                 recs.append(
#                     "Get adequate sleep (7-9 hours), stay hydrated, and "
#                     "use an eye cream with vitamin K or caffeine."
#                 )

#         # General recommendations
#         recs.append("Drink at least 8 glasses of water daily for hydration.")
#         recs.append("Maintain a balanced diet rich in antioxidants.")

#         if overall < 50:
#             recs.append(
#                 "Consider consulting a dermatologist for a personalized "
#                 "skincare routine."
#             )

#         return recs

#     def save_report(self, report_text: str,
#                     filepath: Optional[str] = None) -> str:
#         """Save report to file."""
#         if filepath is None:
#             timestamp = time.strftime("%Y%m%d_%H%M%S")
#             filepath = f"skin_analysis_report_{timestamp}.txt"

#         with open(filepath, "w") as f:
#             f.write(report_text)

#         print(f"[INFO] Report saved to: {filepath}")
#         return filepath

#     def create_visual_report(self, image: np.ndarray,
#                              visualizations: Dict,
#                              results: Dict) -> np.ndarray:
#         """Create a comprehensive visual report as a single image."""
#         thumb_h, thumb_w = 300, 300
#         padding = 10

#         # Determine grid layout
#         vis_items = list(visualizations.items())
#         n_items = len(vis_items)
#         cols = 3
#         rows = (n_items + cols - 1) // cols

#         # Canvas size
#         canvas_w = cols * (thumb_w + padding) + padding
#         canvas_h = 80 + rows * (thumb_h + 30 + padding) + padding

#         canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
#         canvas[:] = (30, 30, 30)

#         # Title
#         cv2.putText(
#             canvas,
#             f"Skin Analysis Report - Score: "
#             f"{results.get('overall_score', 0):.0f}/100 "
#             f"({results.get('overall_grade', 'N/A')})",
#             (padding, 35),
#             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2
#         )
#         cv2.putText(
#             canvas,
#             results.get("timestamp", ""),
#             (padding, 60),
#             cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1
#         )

#         # Place thumbnails
#         for idx, (name, vis_img) in enumerate(vis_items):
#             row = idx // cols
#             col = idx % cols

#             x = padding + col * (thumb_w + padding)
#             y = 80 + row * (thumb_h + 30 + padding)

#             # Resize visualization
#             thumb = cv2.resize(vis_img, (thumb_w, thumb_h))
#             canvas[y:y + thumb_h, x:x + thumb_w] = thumb

#             # Label
#             label = name.replace("_", " ").title()
#             cv2.putText(
#                 canvas, label,
#                 (x, y + thumb_h + 20),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1
#             )

#         return canvas


"""
Report generation module — Fixed Unicode handling
"""

import cv2
import numpy as np
from typing import Dict, Optional
import time
import os


class ReportGenerator:
    """Generates detailed skin analysis reports."""

    def generate_text_report(self, results: Dict) -> str:
        """Generate a text-based analysis report (ASCII safe)."""
        lines = []
        lines.append("=" * 60)
        lines.append("         SKIN INSIGHTS - ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Date: {results.get('timestamp', 'N/A')}")
        lines.append(f"Processing Time: {results.get('processing_time', 'N/A')}")
        lines.append("")

        # Overall Score
        lines.append("-" * 40)
        lines.append("  OVERALL SKIN HEALTH")
        lines.append("-" * 40)
        score = results.get("overall_score", 0)
        lines.append(f"  Score: {score:.1f} / 100")
        lines.append(f"  Grade: {results.get('overall_grade', 'N/A')}")
        lines.append("")

        # Skin Type
        skin_type = results.get("skin_type", {})
        if skin_type:
            lines.append("-" * 40)
            lines.append("  SKIN TYPE")
            lines.append("-" * 40)
            lines.append(f"  Type: {skin_type.get('type', 'N/A')}")
            lines.append(f"  Description: {skin_type.get('description', '')}")
            chars = skin_type.get("characteristics", [])
            for c in chars:
                lines.append(f"    - {c}")
            lines.append("")

        # Skin Tone
        tone = results.get("skin_tone", {})
        if tone:
            lines.append("-" * 40)
            lines.append("  SKIN TONE")
            lines.append("-" * 40)
            lines.append(f"  Category: {tone.get('category', 'N/A')}")
            lines.append(f"  Fitzpatrick: {tone.get('fitzpatrick_name', 'N/A')}")
            undertone = tone.get("undertone", {})
            lines.append(f"  Undertone: {undertone.get('type', 'N/A')}")
            lines.append(f"  Hex Color: {tone.get('hex_color', 'N/A')}")
            lines.append("")

        # Skin Age
        skin_age = results.get("skin_age", {})
        if skin_age:
            lines.append("-" * 40)
            lines.append("  SKIN AGE ESTIMATION")
            lines.append("-" * 40)
            lines.append(f"  Estimated Skin Age: {skin_age.get('age_range', 'N/A')}")
            lines.append(f"  Status: {skin_age.get('status', 'N/A')}")
            lines.append("")

        # Score Breakdown
        lines.append("-" * 40)
        lines.append("  SCORE BREAKDOWN")
        lines.append("-" * 40)

        score_items = [
            ("Acne/Blemishes", results.get("blemishes", {}).get("score")),
            ("Pigmentation", results.get("pigmentation", {}).get("score")),
            ("Wrinkles", results.get("wrinkles", {}).get("overall_score")),
            ("Texture", results.get("texture", {}).get("score")),
            ("Pores", results.get("pores", {}).get("score")),
            ("Dark Circles", results.get("dark_circles", {}).get("score")),
        ]

        for name, sc in score_items:
            if sc is not None:
                bar_filled = int(sc / 5)
                bar_empty = 20 - bar_filled
                bar = "#" * bar_filled + "." * bar_empty
                lines.append(f"  {name:18s} [{bar}] {sc:.0f}/100")

        lines.append("")

        # Concerns
        concerns = results.get("recommendations", {}).get("concerns", [])
        if concerns:
            lines.append("-" * 40)
            lines.append("  YOUR SKIN CONCERNS")
            lines.append("-" * 40)
            for i, c in enumerate(concerns, 1):
                lines.append(f"  {i}. {c['name']} ({c['severity']})")
                lines.append(f"     {c.get('details', '')}")
            lines.append("")

        # Tips
        tips = results.get("recommendations", {}).get("specific_tips", [])
        if tips:
            lines.append("-" * 40)
            lines.append("  PERSONALIZED TIPS")
            lines.append("-" * 40)
            for tip in tips:
                lines.append(f"  [{tip.get('urgency', 'low').upper()}] {tip['title']}")
                lines.append(f"    {tip['tip']}")
                lines.append("")

        # Ingredients
        ingredients = results.get("recommendations", {}).get("recommended_ingredients", [])
        if ingredients:
            lines.append("-" * 40)
            lines.append("  RECOMMENDED INGREDIENTS")
            lines.append("-" * 40)
            for ing in ingredients:
                lines.append(f"  * {ing['name']} ({ing.get('concentration', '')})")
                lines.append(f"    {ing.get('benefits', '')}")
                lines.append(f"    Why: {ing.get('reason', '')}")
                lines.append("")

        # Routine
        routine = results.get("routine", {})
        if routine:
            lines.append("-" * 40)
            lines.append("  MORNING ROUTINE")
            lines.append("-" * 40)
            for step in routine.get("morning_routine", []):
                lines.append(f"  Step {step['step']}: {step['product']}")
                lines.append(f"    Product: {step.get('ingredient', '')}")
                lines.append(f"    How: {step.get('how_to', '')}")
                lines.append("")

            lines.append("-" * 40)
            lines.append("  NIGHT ROUTINE")
            lines.append("-" * 40)
            for step in routine.get("night_routine", []):
                lines.append(f"  Step {step['step']}: {step['product']}")
                lines.append(f"    Product: {step.get('ingredient', '')}")
                lines.append(f"    How: {step.get('how_to', '')}")
                lines.append("")

        # Lifestyle
        lifestyle = results.get("recommendations", {}).get("lifestyle_tips", [])
        if lifestyle:
            lines.append("-" * 40)
            lines.append("  LIFESTYLE TIPS")
            lines.append("-" * 40)
            for tip in lifestyle:
                # Remove emojis for safe encoding
                clean_tip = self._remove_emojis(tip)
                lines.append(f"  - {clean_tip}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("  This is for informational purposes only.")
        lines.append("  Consult a dermatologist for professional advice.")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _remove_emojis(self, text: str) -> str:
        """Remove emoji characters for safe file encoding."""
        clean = ""
        for char in text:
            if ord(char) < 0x10000 and char.isprintable():
                clean += char
            elif ord(char) >= 0x10000:
                clean += ""  # Skip emojis
        return clean.strip()

    def save_report(self, report_text: str,
                    filepath: Optional[str] = None) -> str:
        """Save report to file with proper encoding."""
        if filepath is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filepath = f"skin_analysis_report_{timestamp}.txt"

        # Remove any remaining emojis
        safe_text = self._remove_emojis(report_text)

        # Use UTF-8 encoding to handle special characters
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(safe_text)

        print(f"[INFO] Report saved to: {filepath}")
        return filepath

    def create_visual_report(self, image, visualizations, results):
        """Create visual report image."""
        thumb_h, thumb_w = 300, 300
        padding = 10

        vis_items = list(visualizations.items())
        n_items = len(vis_items)
        cols = 3
        rows = max(1, (n_items + cols - 1) // cols)

        canvas_w = cols * (thumb_w + padding) + padding
        canvas_h = 80 + rows * (thumb_h + 30 + padding) + padding

        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        canvas[:] = (30, 30, 30)

        score = results.get("overall_score", 0)
        grade = results.get("overall_grade", "N/A")

        cv2.putText(canvas,
                    f"Skin Analysis - Score: {score:.0f}/100 ({grade})",
                    (padding, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 255), 2)

        for idx, (name, vis_img) in enumerate(vis_items):
            row = idx // cols
            col = idx % cols
            x = padding + col * (thumb_w + padding)
            y = 80 + row * (thumb_h + 30 + padding)

            thumb = cv2.resize(vis_img, (thumb_w, thumb_h))
            canvas[y:y + thumb_h, x:x + thumb_w] = thumb

            label = name.replace("_", " ").title()
            cv2.putText(canvas, label, (x, y + thumb_h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        return canvas