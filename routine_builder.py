"""
Personalized AM/PM skincare routine builder.
"""

from typing import Dict, List


class RoutineBuilder:
    """Builds personalized morning and night skincare routines."""

    def build_routine(self, results: Dict,
                      recommendations: Dict) -> Dict:
        """Build complete AM and PM routines."""
        skin_type = results.get("skin_type", {}).get("type", "Normal")
        concerns = [c["name"] for c in recommendations.get("concerns", [])]

        am_routine = self._build_am(skin_type, concerns)
        pm_routine = self._build_pm(skin_type, concerns)
        weekly = self._build_weekly(skin_type, concerns)

        return {
            "morning_routine": am_routine,
            "night_routine": pm_routine,
            "weekly_treatments": weekly,
            "skin_type": skin_type,
            "notes": self._routine_notes(skin_type),
        }

    def _build_am(self, skin_type: str,
                  concerns: List[str]) -> List[Dict]:
        """Build morning routine."""
        routine = []

        # Step 1: Cleanser
        if skin_type == "Oily":
            routine.append({
                "step": 1,
                "product": "Gel/Foam Cleanser",
                "ingredient": "Salicylic Acid 1%" if "Acne & Breakouts" in concerns else "Gentle gel cleanser",
                "how_to": "Massage onto wet face for 60 seconds, rinse with lukewarm water",
                "icon": "🧴",
            })
        elif skin_type == "Dry":
            routine.append({
                "step": 1,
                "product": "Cream Cleanser",
                "ingredient": "Ceramide-based gentle cleanser",
                "how_to": "Gently massage onto face, rinse without rubbing",
                "icon": "🧴",
            })
        else:
            routine.append({
                "step": 1,
                "product": "Gentle Cleanser",
                "ingredient": "pH-balanced face wash",
                "how_to": "Massage for 60 seconds, rinse with lukewarm water",
                "icon": "🧴",
            })

        # Step 2: Toner (optional)
        routine.append({
            "step": 2,
            "product": "Hydrating Toner",
            "ingredient": "Hyaluronic Acid toner" if skin_type == "Dry" else "Niacinamide toner",
            "how_to": "Pat onto damp skin with palms, don't rub",
            "icon": "💧",
        })

        # Step 3: Serum
        if "Pigmentation & Dark Spots" in concerns:
            routine.append({
                "step": 3,
                "product": "Brightening Serum",
                "ingredient": "Vitamin C 10-20%",
                "how_to": "Apply 4-5 drops to face and neck, let absorb for 2 minutes",
                "icon": "✨",
            })
        elif "Acne & Breakouts" in concerns:
            routine.append({
                "step": 3,
                "product": "Anti-Acne Serum",
                "ingredient": "Niacinamide 10% + Zinc",
                "how_to": "Apply to entire face, focusing on acne-prone areas",
                "icon": "💚",
            })
        elif "Enlarged Pores" in concerns:
            routine.append({
                "step": 3,
                "product": "Pore-Minimizing Serum",
                "ingredient": "Niacinamide 10%",
                "how_to": "Apply to entire face, especially T-zone",
                "icon": "🔬",
            })
        else:
            routine.append({
                "step": 3,
                "product": "Hydrating Serum",
                "ingredient": "Hyaluronic Acid 2%",
                "how_to": "Apply to damp skin for best absorption",
                "icon": "💧",
            })

        # Step 4: Eye Cream
        if "Dark Circles" in concerns:
            routine.append({
                "step": 4,
                "product": "Eye Cream",
                "ingredient": "Caffeine 5% eye serum",
                "how_to": "Dab gently with ring finger under eyes, don't rub",
                "icon": "👁️",
            })

        # Step 5: Moisturizer
        if skin_type == "Oily":
            routine.append({
                "step": len(routine) + 1,
                "product": "Lightweight Moisturizer",
                "ingredient": "Oil-free gel moisturizer",
                "how_to": "Apply thin layer to entire face",
                "icon": "🧊",
            })
        elif skin_type == "Dry":
            routine.append({
                "step": len(routine) + 1,
                "product": "Rich Moisturizer",
                "ingredient": "Ceramide + Hyaluronic Acid cream",
                "how_to": "Apply generously, lock in previous layers",
                "icon": "🧴",
            })
        else:
            routine.append({
                "step": len(routine) + 1,
                "product": "Moisturizer",
                "ingredient": "Lightweight cream with ceramides",
                "how_to": "Apply evenly to face and neck",
                "icon": "🧴",
            })

        # Step 6: SUNSCREEN (always last in AM)
        routine.append({
            "step": len(routine) + 1,
            "product": "Sunscreen ☀️",
            "ingredient": "Broad Spectrum SPF 50 PA++++",
            "how_to": "Apply 2 finger-lengths. Reapply every 2 hours outdoors. NON-NEGOTIABLE!",
            "icon": "☀️",
        })

        return routine

    def _build_pm(self, skin_type: str,
                  concerns: List[str]) -> List[Dict]:
        """Build night routine."""
        routine = []

        # Step 1: Double Cleanse (oil + water)
        routine.append({
            "step": 1,
            "product": "Oil Cleanser / Micellar Water",
            "ingredient": "Cleansing oil or micellar water",
            "how_to": "Remove sunscreen and makeup first",
            "icon": "🧴",
        })

        routine.append({
            "step": 2,
            "product": "Water-based Cleanser",
            "ingredient": "Same as morning cleanser",
            "how_to": "Second cleanse to clean skin thoroughly",
            "icon": "🫧",
        })

        # Step 3: Treatment
        if "Fine Lines & Wrinkles" in concerns:
            routine.append({
                "step": 3,
                "product": "Anti-Aging Treatment",
                "ingredient": "Retinol 0.3% (start low, build up)",
                "how_to": "Apply pea-sized amount to dry face. "
                          "Start 2x/week, increase gradually. "
                          "NOT with AHA/BHA on same night",
                "icon": "⭐",
            })
        elif "Acne & Breakouts" in concerns:
            routine.append({
                "step": 3,
                "product": "Acne Treatment",
                "ingredient": "Salicylic Acid 2% or Azelaic Acid 10%",
                "how_to": "Apply to affected areas after cleansing",
                "icon": "💚",
            })
        elif "Pigmentation & Dark Spots" in concerns:
            routine.append({
                "step": 3,
                "product": "Brightening Treatment",
                "ingredient": "Alpha Arbutin 2% + Tranexamic Acid 3%",
                "how_to": "Apply to dark spots and overall face",
                "icon": "✨",
            })
        elif "Uneven Texture" in concerns:
            routine.append({
                "step": 3,
                "product": "Exfoliating Treatment",
                "ingredient": "AHA 10% (use 2-3x/week only)",
                "how_to": "Apply to clean face, avoid eye area",
                "icon": "🔄",
            })

        # Step 4: Serum
        if "Dryness & Dehydration" in concerns or skin_type == "Dry":
            routine.append({
                "step": len(routine) + 1,
                "product": "Hydrating Serum",
                "ingredient": "Hyaluronic Acid 2% + B5",
                "how_to": "Apply to damp skin for maximum hydration",
                "icon": "💧",
            })

        # Step 5: Eye Cream
        if "Dark Circles" in concerns or "Fine Lines & Wrinkles" in concerns:
            routine.append({
                "step": len(routine) + 1,
                "product": "Night Eye Cream",
                "ingredient": "Peptide eye cream or Retinol eye cream (0.1%)",
                "how_to": "Gently pat around orbital bone with ring finger",
                "icon": "👁️",
            })

        # Step 6: Night Moisturizer
        routine.append({
            "step": len(routine) + 1,
            "product": "Night Moisturizer",
            "ingredient": "Rich repair cream with ceramides and peptides",
            "how_to": "Apply generous layer. Skin repairs itself at night!",
            "icon": "🌙",
        })

        return routine

    def _build_weekly(self, skin_type: str,
                      concerns: List[str]) -> List[Dict]:
        """Build weekly treatment schedule."""
        weekly = []

        if "Enlarged Pores" in concerns or skin_type == "Oily":
            weekly.append({
                "treatment": "Clay Mask",
                "frequency": "1-2x per week",
                "ingredient": "Kaolin / Bentonite clay",
                "benefit": "Deep cleans pores, absorbs excess oil",
            })

        if "Uneven Texture" in concerns or "Pigmentation & Dark Spots" in concerns:
            weekly.append({
                "treatment": "Chemical Exfoliation",
                "frequency": "2-3x per week",
                "ingredient": "AHA 10% (Glycolic/Lactic Acid)",
                "benefit": "Removes dead skin cells, brightens",
            })

        if skin_type == "Dry" or "Dryness & Dehydration" in concerns:
            weekly.append({
                "treatment": "Hydrating Sheet Mask",
                "frequency": "2-3x per week",
                "ingredient": "Hyaluronic Acid + Ceramide mask",
                "benefit": "Intense hydration boost",
            })

        if "Acne & Breakouts" in concerns:
            weekly.append({
                "treatment": "Spot Treatment Night",
                "frequency": "As needed",
                "ingredient": "Benzoyl Peroxide 2.5% (spot only)",
                "benefit": "Kills acne-causing bacteria on active spots",
            })

        return weekly

    def _routine_notes(self, skin_type: str) -> List[str]:
        return [
            "⏱️ Wait 1-2 minutes between each product layer",
            "🚫 Never use Retinol + AHA/BHA on the same night",
            "☀️ If using Retinol or AHA, sunscreen is MANDATORY",
            "📅 Give products 4-8 weeks to show results",
            "🧪 Patch test new products on jaw for 48 hours first",
            "💧 Apply serums on slightly damp skin for better absorption",
        ]