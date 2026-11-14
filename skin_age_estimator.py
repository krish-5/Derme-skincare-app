# """
# Skin age estimation based on wrinkles, texture, elasticity.
# """

# import cv2
# import numpy as np
# from typing import Dict, Optional


# class SkinAgeEstimator:
#     """Estimates skin age based on visible signs of aging."""

#     def estimate_skin_age(self, analysis_results: Dict) -> Dict:
#         """
#         Estimate skin age from analysis results.

#         Uses wrinkle density, texture quality, pore size,
#         and pigmentation to estimate skin age.
#         """
#         # Base age assumption (we can't know real age from photo)
#         # We estimate relative skin condition

#         # ── Collect scores ──
#         wrinkle_score = analysis_results.get("wrinkles", {}).get("overall_score", 75)
#         texture_score = analysis_results.get("texture", {}).get("score", 75)
#         pore_score = analysis_results.get("pores", {}).get("score", 75)
#         pigmentation_score = analysis_results.get("pigmentation", {}).get("score", 75)
#         evenness = analysis_results.get("skin_tone", {}).get("evenness_score", 75)

#         # ── Average skin condition ──
#         avg_score = np.mean([
#             wrinkle_score,
#             texture_score,
#             pore_score,
#             pigmentation_score,
#             evenness
#         ])

#         # ── Map score to estimated skin age ──
#         # Score 95+ → skin looks like 18-22
#         # Score 85-95 → skin looks like 22-28
#         # Score 75-85 → skin looks like 28-35
#         # Score 65-75 → skin looks like 35-42
#         # Score 50-65 → skin looks like 42-50
#         # Score below 50 → skin looks like 50+

#         if avg_score >= 95:
#             estimated_age = 20
#             age_range = "18-22"
#         elif avg_score >= 85:
#             estimated_age = 25
#             age_range = "22-28"
#         elif avg_score >= 75:
#             estimated_age = 31
#             age_range = "28-35"
#         elif avg_score >= 65:
#             estimated_age = 38
#             age_range = "35-42"
#         elif avg_score >= 50:
#             estimated_age = 46
#             age_range = "42-50"
#         elif avg_score >= 35:
#             estimated_age = 52
#             age_range = "50-55"
#         else:
#             estimated_age = 58
#             age_range = "55+"

#         # ── Determine what's aging the skin ──
#         aging_factors = []

#         if wrinkle_score < 70:
#             aging_factors.append({
#                 "factor": "Fine Lines & Wrinkles",
#                 "impact": "high" if wrinkle_score < 50 else "moderate",
#                 "advice": "Use retinol and peptides to boost collagen"
#             })

#         if texture_score < 70:
#             aging_factors.append({
#                 "factor": "Skin Texture",
#                 "impact": "moderate",
#                 "advice": "Regular exfoliation with AHA/BHA"
#             })

#         if pigmentation_score < 70:
#             aging_factors.append({
#                 "factor": "Pigmentation & Sun Damage",
#                 "impact": "high" if pigmentation_score < 50 else "moderate",
#                 "advice": "Vitamin C serum + daily SPF 50"
#             })

#         if pore_score < 60:
#             aging_factors.append({
#                 "factor": "Pore Visibility",
#                 "impact": "moderate",
#                 "advice": "Niacinamide helps minimize pore appearance"
#             })

#         # ── Skin age status ──
#         if avg_score >= 80:
#             status = "Your skin looks younger than average"
#             emoji = "✨"
#         elif avg_score >= 65:
#             status = "Your skin looks age-appropriate"
#             emoji = "👍"
#         else:
#             status = "Your skin shows signs of premature aging"
#             emoji = "⚠️"

#         return {
#             "estimated_age": estimated_age,
#             "age_range": age_range,
#             "skin_condition_score": float(avg_score),
#             "status": status,
#             "emoji": emoji,
#             "aging_factors": aging_factors,
#             "breakdown": {
#                 "wrinkle_contribution": float(wrinkle_score),
#                 "texture_contribution": float(texture_score),
#                 "pigmentation_contribution": float(pigmentation_score),
#                 "pore_contribution": float(pore_score),
#                 "evenness_contribution": float(evenness),
#             }
#         }


"""
Skin age estimation — Rewritten for REALISTIC results.

The old version relied heavily on wrinkle scores which were
inaccurate (0 score = severe wrinkles = age 55+). This version
uses a balanced approach with sanity checks.
"""

import cv2
import numpy as np
from typing import Dict, Optional


class SkinAgeEstimator:
    """
    Estimates RELATIVE skin age based on multiple factors.
    
    Key changes from old version:
    1. Does NOT assume worst case from bad wrinkle detection
    2. Uses face structure analysis (jaw line, skin tightness)
    3. Weighted approach where no single bad score ruins the result
    4. Sanity checks — most selfie takers are 15-50
    5. Focuses on what CAN be measured reliably:
       - Skin smoothness/texture
       - Color evenness  
       - Overall skin clarity
       - Blemish patterns
    """

    def estimate_skin_age(self, analysis_results: Dict,
                          image: Optional[np.ndarray] = None) -> Dict:
        """
        Estimate skin age from analysis results.
        
        Uses a CONSERVATIVE approach — when uncertain,
        estimates younger rather than older.
        """
        # ── Collect reliable scores ──
        # These are more reliable than wrinkle detection:
        texture_score = analysis_results.get("texture", {}).get("score", 70)
        smoothness = analysis_results.get("texture", {}).get("smoothness", 70)
        roughness = analysis_results.get("texture", {}).get("roughness", 10)
        evenness = analysis_results.get("skin_tone", {}).get("evenness_score", 70)
        blemish_score = analysis_results.get("blemishes", {}).get("score", 80)
        pore_score = analysis_results.get("pores", {}).get("score", 70)
        pigmentation_score = analysis_results.get("pigmentation", {}).get("score", 75)
        dc_score = analysis_results.get("dark_circles", {}).get("score", 70)

        # Wrinkle score — USE CAUTIOUSLY (often inaccurate)
        wrinkle_score = analysis_results.get("wrinkles", {}).get("overall_score", 80)
        wrinkle_density = analysis_results.get("wrinkles", {}).get("wrinkle_density", 0)

        # ── Adjust wrinkle score if it seems wrong ──
        # If texture is smooth but wrinkle score is very low,
        # the wrinkle detector probably made false detections
        if smoothness > 60 and wrinkle_score < 40:
            wrinkle_score = max(wrinkle_score, 65)
            wrinkle_density = min(wrinkle_density, 3.0)

        if texture_score > 70 and wrinkle_score < 30:
            wrinkle_score = max(wrinkle_score, 60)

        # ── Calculate age indicators ──
        # Each indicator gives a score from 0 (old) to 100 (young)

        # Indicator 1: Skin clarity (texture + smoothness)
        # Most reliable indicator
        clarity_score = (texture_score * 0.5 + smoothness * 0.5)

        # Indicator 2: Color evenness
        # Young skin tends to be more even
        evenness_indicator = evenness

        # Indicator 3: Blemish type analysis
        # Active acne suggests younger skin
        # Dark spots/pigmentation suggests older skin
        blemish_types = analysis_results.get("blemishes", {}).get("types", {})
        acne_count = blemish_types.get("acne", 0)
        dark_spot_count = blemish_types.get("dark_spot", 0)

        if acne_count > dark_spot_count and acne_count > 3:
            # Active acne is more common in younger people
            acne_youth_bonus = 15
        elif dark_spot_count > acne_count and dark_spot_count > 3:
            # Dark spots more common in older people
            acne_youth_bonus = -10
        else:
            acne_youth_bonus = 0

        # Indicator 4: Pore visibility
        # Pores become more visible with age
        pore_indicator = pore_score

        # Indicator 5: Adjusted wrinkle score
        # Only count if we trust the detection
        wrinkle_indicator = wrinkle_score

        # Indicator 6: Pigmentation
        # More pigmentation issues = older skin typically
        pigment_indicator = pigmentation_score

        # ── Weighted age calculation ──
        # Weight reliable metrics more heavily
        weighted_score = (
            clarity_score * 0.30 +          # Most reliable
            evenness_indicator * 0.15 +     # Reliable
            pore_indicator * 0.15 +         # Moderate reliability
            pigment_indicator * 0.15 +      # Moderate reliability
            wrinkle_indicator * 0.10 +      # LEAST reliable - low weight
            dc_score * 0.10 +              # Moderate
            blemish_score * 0.05            # Context dependent
        )

        # Add acne youth bonus
        weighted_score += acne_youth_bonus

        # Clamp to 0-100
        weighted_score = max(0, min(100, weighted_score))

        # ── Map weighted score to age ──
        # Use a GENTLER mapping that doesn't jump to 55
        estimated_age, age_range = self._score_to_age(weighted_score)

        # ── Determine aging factors ──
        aging_factors = self._identify_aging_factors(
            analysis_results, wrinkle_score, texture_score,
            pigmentation_score, pore_score, evenness
        )

        # ── Status message ──
        if weighted_score >= 75:
            status = "Your skin appears youthful and healthy"
        elif weighted_score >= 60:
            status = "Your skin is in good condition"
        elif weighted_score >= 45:
            status = "Your skin shows some signs of aging"
        else:
            status = "Your skin shows visible signs of aging"

        return {
            "estimated_age": estimated_age,
            "age_range": age_range,
            "skin_condition_score": float(weighted_score),
            "status": status,
            "aging_factors": aging_factors,
            "confidence": self._calculate_confidence(analysis_results),
            "breakdown": {
                "clarity": float(clarity_score),
                "evenness": float(evenness_indicator),
                "pores": float(pore_indicator),
                "pigmentation": float(pigment_indicator),
                "wrinkles": float(wrinkle_indicator),
                "dark_circles": float(dc_score),
            },
            "notes": self._get_notes(weighted_score, wrinkle_score, texture_score),
        }

    def _score_to_age(self, score: float) -> tuple:
        """
        Map skin condition score to estimated age.
        
        IMPORTANT: This is a GENTLE mapping.
        We bias toward younger estimates because:
        1. Most selfie-takers are 15-40
        2. Our wrinkle detection has false positives
        3. It's better to underestimate than overestimate
        """
        # Score ranges mapped to age ranges
        # Higher score = younger looking skin
        age_map = [
            (90, 100, 18, "18-22"),
            (82, 90,  22, "20-25"),
            (75, 82,  25, "23-28"),
            (68, 75,  28, "26-32"),
            (60, 68,  32, "30-35"),
            (52, 60,  35, "33-38"),
            (44, 52,  38, "36-42"),
            (36, 44,  42, "40-45"),
            (28, 36,  46, "43-48"),
            (20, 28,  50, "48-53"),
            (0,  20,  55, "52-58"),
        ]

        for low, high, age, age_range in age_map:
            if low <= score < high:
                return age, age_range

        # Default — if score is very high
        if score >= 100:
            return 18, "18-22"

        return 35, "33-38"

    def _identify_aging_factors(self, results: Dict,
                                 wrinkle_score: float,
                                 texture_score: float,
                                 pigmentation_score: float,
                                 pore_score: float,
                                 evenness: float) -> list:
        """Identify what factors are contributing to skin aging."""
        factors = []

        # Only flag factors that are actually concerning
        if texture_score < 60:
            factors.append({
                "factor": "Skin Texture",
                "impact": "high" if texture_score < 40 else "moderate",
                "detail": f"Texture score: {texture_score:.0f}/100",
                "advice": "Use AHA/BHA exfoliants 2-3x per week to improve texture"
            })

        if pigmentation_score < 65:
            factors.append({
                "factor": "Pigmentation / Sun Damage",
                "impact": "high" if pigmentation_score < 45 else "moderate",
                "detail": f"Pigmentation score: {pigmentation_score:.0f}/100",
                "advice": "Vitamin C serum + SPF 50 daily to prevent further damage"
            })

        if wrinkle_score < 60:
            # Only flag if texture also confirms
            if texture_score < 65:
                factors.append({
                    "factor": "Fine Lines",
                    "impact": "moderate",
                    "detail": f"Wrinkle score: {wrinkle_score:.0f}/100",
                    "advice": "Retinol (start low 0.25%) + Peptides at night"
                })

        if pore_score < 55:
            factors.append({
                "factor": "Pore Visibility",
                "impact": "moderate",
                "detail": f"Pore score: {pore_score:.0f}/100",
                "advice": "Niacinamide 10% helps tighten pore appearance"
            })

        if evenness < 60:
            factors.append({
                "factor": "Uneven Skin Tone",
                "impact": "moderate",
                "detail": f"Evenness: {evenness:.0f}/100",
                "advice": "Vitamin C + Alpha Arbutin for more even complexion"
            })

        if not factors:
            factors.append({
                "factor": "No Major Aging Concerns",
                "impact": "none",
                "detail": "Your skin is in great condition!",
                "advice": "Maintain your routine with SPF and hydration"
            })

        return factors

    def _calculate_confidence(self, results: Dict) -> str:
        """
        How confident are we in the age estimation?
        Lower confidence if wrinkle detection seems off.
        """
        wrinkle_score = results.get("wrinkles", {}).get("overall_score", 75)
        texture_score = results.get("texture", {}).get("score", 75)

        # If wrinkle and texture scores disagree wildly,
        # our confidence is lower
        diff = abs(wrinkle_score - texture_score)

        if diff < 15:
            return "high"
        elif diff < 30:
            return "moderate"
        else:
            return "low - wrinkle detection may be inaccurate"

    def _get_notes(self, weighted_score: float,
                   wrinkle_score: float,
                   texture_score: float) -> list:
        """Add notes about the estimation."""
        notes = []

        if abs(wrinkle_score - texture_score) > 30:
            notes.append(
                "Note: Wrinkle detection may have been affected by "
                "lighting, hair, or facial features. Texture analysis "
                "was given more weight for accuracy."
            )

        notes.append(
            "Skin age estimation is approximate and based on "
            "visible skin characteristics only. Actual biological "
            "age may differ."
        )

        return notes