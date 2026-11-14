"""
Personalized skincare recommendation engine.
Generates specific advice based on detected skin concerns.
"""

from typing import Dict, List


class RecommendationEngine:
    """
    Generates personalized skincare recommendations
    based on actual analysis results — NOT generic advice.
    """

    # ── Ingredient Database ──
    INGREDIENTS = {
        "niacinamide": {
            "name": "Niacinamide (Vitamin B3)",
            "concentration": "5-10%",
            "benefits": "Reduces pores, controls oil, fades dark spots",
            "best_for": ["oily", "pores", "pigmentation", "acne"],
        },
        "retinol": {
            "name": "Retinol (Vitamin A)",
            "concentration": "0.25-1%",
            "benefits": "Anti-aging, reduces wrinkles, boosts cell turnover",
            "best_for": ["wrinkles", "texture", "aging"],
        },
        "vitamin_c": {
            "name": "Vitamin C (L-Ascorbic Acid)",
            "concentration": "10-20%",
            "benefits": "Brightens skin, fades dark spots, antioxidant protection",
            "best_for": ["pigmentation", "dullness", "dark_spots", "evenness"],
        },
        "salicylic_acid": {
            "name": "Salicylic Acid (BHA)",
            "concentration": "1-2%",
            "benefits": "Unclogs pores, reduces acne, exfoliates",
            "best_for": ["acne", "pores", "oily", "blackheads"],
        },
        "hyaluronic_acid": {
            "name": "Hyaluronic Acid",
            "concentration": "1-2%",
            "benefits": "Deep hydration, plumps skin, reduces fine lines",
            "best_for": ["dry", "wrinkles", "hydration", "texture"],
        },
        "alpha_arbutin": {
            "name": "Alpha Arbutin",
            "concentration": "2%",
            "benefits": "Fades dark spots without irritation",
            "best_for": ["pigmentation", "dark_spots", "dark_circles"],
        },
        "aha": {
            "name": "AHA (Glycolic/Lactic Acid)",
            "concentration": "5-10%",
            "benefits": "Surface exfoliation, improves texture, brightens",
            "best_for": ["texture", "dullness", "pigmentation"],
        },
        "spf": {
            "name": "Broad Spectrum SPF 50",
            "concentration": "PA++++",
            "benefits": "Prevents sun damage, aging, and pigmentation",
            "best_for": ["all", "pigmentation", "wrinkles", "aging"],
        },
        "peptides": {
            "name": "Peptide Complex",
            "concentration": "Multi-peptide",
            "benefits": "Firms skin, reduces wrinkles, boosts collagen",
            "best_for": ["wrinkles", "aging", "elasticity"],
        },
        "azelaic_acid": {
            "name": "Azelaic Acid",
            "concentration": "10%",
            "benefits": "Reduces acne, fades marks, calms redness",
            "best_for": ["acne", "pigmentation", "redness", "sensitivity"],
        },
        "caffeine": {
            "name": "Caffeine",
            "concentration": "3-5%",
            "benefits": "Reduces puffiness and dark circles under eyes",
            "best_for": ["dark_circles"],
        },
        "ceramides": {
            "name": "Ceramides",
            "concentration": "Complex",
            "benefits": "Repairs skin barrier, locks in moisture",
            "best_for": ["dry", "sensitivity", "hydration"],
        },
        "tranexamic_acid": {
            "name": "Tranexamic Acid",
            "concentration": "3%",
            "benefits": "Targets stubborn pigmentation and melasma",
            "best_for": ["pigmentation", "melasma", "dark_spots"],
        },
    }

    def generate_recommendations(self, results: Dict) -> Dict:
        """
        Generate PERSONALIZED recommendations based on analysis.
        NOT generic — each recommendation tied to a detected issue.
        """
        concerns = self._identify_concerns(results)
        ingredients = self._recommend_ingredients(concerns)
        tips = self._generate_specific_tips(results, concerns)
        priority_concerns = self._prioritize_concerns(concerns)

        return {
            "concerns": concerns,
            "priority_concerns": priority_concerns,
            "recommended_ingredients": ingredients,
            "specific_tips": tips,
            "lifestyle_tips": self._lifestyle_tips(results),
        }

    def _identify_concerns(self, results: Dict) -> List[Dict]:
        """Identify specific skin concerns from analysis results."""
        concerns = []

        # ── Acne / Blemishes ──
        blemish_data = results.get("blemishes", {})
        blemish_score = blemish_data.get("score", 100)
        blemish_count = blemish_data.get("count", 0)

        if blemish_score < 85:
            severity = blemish_data.get("severity", "mild")
            types = blemish_data.get("types", {})

            concern = {
                "name": "Acne & Breakouts",
                "severity": severity,
                "score": blemish_score,
                "icon": "🔴",
                "details": f"{blemish_count} blemishes detected",
            }

            if types.get("acne", 0) > 0:
                concern["details"] += f" ({types['acne']} active acne)"
            if types.get("dark_spot", 0) > 0:
                concern["details"] += f", {types['dark_spot']} post-acne marks"

            concerns.append(concern)

        # ── Pigmentation ──
        pigment_data = results.get("pigmentation", {})
        pigment_score = pigment_data.get("score", 100)

        if pigment_score < 85:
            concerns.append({
                "name": "Pigmentation & Dark Spots",
                "severity": pigment_data.get("severity", "mild"),
                "score": pigment_score,
                "icon": "🟤",
                "details": pigment_data.get("pigmentation_type",
                                            "Some uneven pigmentation detected"),
            })

        # ── Wrinkles ──
        wrinkle_data = results.get("wrinkles", {})
        wrinkle_score = wrinkle_data.get("overall_score", 100)

        if wrinkle_score < 85:
            density = wrinkle_data.get("wrinkle_density", 0)
            regional = wrinkle_data.get("regional_scores", {})

            worst_region = ""
            if regional:
                worst = min(regional.items(), key=lambda x: x[1])
                worst_region = f" Most visible on {worst[0]}"

            concerns.append({
                "name": "Fine Lines & Wrinkles",
                "severity": wrinkle_data.get("severity", "mild"),
                "score": wrinkle_score,
                "icon": "〰️",
                "details": f"Wrinkle density: {density:.1f}%.{worst_region}",
            })

        # ── Pores ──
        pore_data = results.get("pores", {})
        pore_score = pore_data.get("score", 100)

        if pore_score < 75:
            regional_p = pore_data.get("regional_analysis", {})
            worst_pore_region = ""
            if regional_p:
                worst_r = max(regional_p.items(),
                              key=lambda x: x[1].get("density", 0))
                worst_pore_region = f" Most visible on {worst_r[0]}"

            concerns.append({
                "name": "Enlarged Pores",
                "severity": pore_data.get("severity", "normal"),
                "score": pore_score,
                "icon": "⚫",
                "details": f"{pore_data.get('pore_count', 0)} visible pores.{worst_pore_region}",
            })

        # ── Dark Circles ──
        dc_data = results.get("dark_circles", {})
        dc_score = dc_data.get("score", 100)

        if dc_score < 80:
            color_info = dc_data.get("color_analysis", {})
            dc_type = color_info.get("description", "Under-eye darkness detected")

            concerns.append({
                "name": "Dark Circles",
                "severity": dc_data.get("severity", "mild"),
                "score": dc_score,
                "icon": "👁️",
                "details": dc_type,
            })

        # ── Texture ──
        texture_data = results.get("texture", {})
        texture_score = texture_data.get("score", 100)

        if texture_score < 70:
            concerns.append({
                "name": "Uneven Texture",
                "severity": "moderate" if texture_score < 50 else "mild",
                "score": texture_score,
                "icon": "🧱",
                "details": f"Roughness: {texture_data.get('roughness', 0):.1f}, "
                           f"Smoothness: {texture_data.get('smoothness', 0):.0f}%",
            })

        # ── Skin Type Specific ──
        skin_type = results.get("skin_type", {}).get("type", "Normal")

        if skin_type == "Oily":
            shine = results.get("skin_type", {}).get("shine_level", 0)
            if shine > 40:
                concerns.append({
                    "name": "Excess Oiliness",
                    "severity": "moderate" if shine > 60 else "mild",
                    "score": max(0, 100 - shine),
                    "icon": "💧",
                    "details": f"Shine level: {shine:.0f}%. T-zone especially oily.",
                })

        elif skin_type == "Dry":
            dryness = results.get("skin_type", {}).get("dryness_level", 0)
            if dryness > 40:
                concerns.append({
                    "name": "Dryness & Dehydration",
                    "severity": "moderate" if dryness > 60 else "mild",
                    "score": max(0, 100 - dryness),
                    "icon": "🏜️",
                    "details": "Skin appears dry. Needs better hydration.",
                })

        # ── If NO concerns found ──
        if not concerns:
            concerns.append({
                "name": "Great Skin! 🎉",
                "severity": "none",
                "score": 95,
                "icon": "✨",
                "details": "Your skin looks healthy! Keep up your current routine.",
            })

        return concerns

    def _prioritize_concerns(self, concerns: List[Dict]) -> List[str]:
        """Return top 3 concerns sorted by severity."""
        severity_order = {"severe": 0, "significant": 1,
                          "moderate": 2, "mild": 3, "none": 4, "normal": 3}

        sorted_concerns = sorted(
            concerns,
            key=lambda c: (severity_order.get(c["severity"], 5), c.get("score", 100))
        )

        return [c["name"] for c in sorted_concerns[:3]]

    def _recommend_ingredients(self, concerns: List[Dict]) -> List[Dict]:
        """Recommend specific ingredients based on concerns."""
        concern_to_tags = {
            "Acne & Breakouts": ["acne", "oily"],
            "Pigmentation & Dark Spots": ["pigmentation", "dark_spots"],
            "Fine Lines & Wrinkles": ["wrinkles", "aging"],
            "Enlarged Pores": ["pores", "oily"],
            "Dark Circles": ["dark_circles"],
            "Uneven Texture": ["texture", "dullness"],
            "Excess Oiliness": ["oily", "pores"],
            "Dryness & Dehydration": ["dry", "hydration"],
        }

        recommended = []
        added_names = set()

        for concern in concerns:
            tags = concern_to_tags.get(concern["name"], [])

            for ing_key, ing_data in self.INGREDIENTS.items():
                if ing_key in added_names:
                    continue

                # Check if this ingredient matches any concern tag
                match = any(tag in ing_data["best_for"] for tag in tags)

                if match:
                    recommended.append({
                        **ing_data,
                        "reason": f"Recommended for: {concern['name']}",
                        "priority": "high" if concern["severity"] in ["severe", "significant", "moderate"] else "medium",
                    })
                    added_names.add(ing_key)

        # Always recommend SPF
        if "spf" not in added_names:
            recommended.append({
                **self.INGREDIENTS["spf"],
                "reason": "Essential for all skin types",
                "priority": "high",
            })

        return recommended[:8]  # Top 8 recommendations

    def _generate_specific_tips(self, results: Dict,
                                 concerns: List[Dict]) -> List[Dict]:
        """Generate tips SPECIFIC to this person's results."""
        tips = []

        skin_type = results.get("skin_type", {}).get("type", "Normal")
        concern_names = [c["name"] for c in concerns]

        # ── Acne Tips ──
        if "Acne & Breakouts" in concern_names:
            blemish_data = results.get("blemishes", {})
            types = blemish_data.get("types", {})

            if types.get("acne", 0) > types.get("dark_spot", 0):
                tips.append({
                    "title": "Active Acne Management",
                    "tip": "Your skin shows active inflammation. Use a 2% "
                           "Salicylic Acid cleanser morning and night. "
                           "Avoid touching your face during the day.",
                    "urgency": "high",
                })
            else:
                tips.append({
                    "title": "Post-Acne Mark Fading",
                    "tip": "You have more post-acne marks than active acne. "
                           "Focus on Alpha Arbutin 2% + Vitamin C 10% to "
                           "fade these marks over 8-12 weeks.",
                    "urgency": "medium",
                })

        # ── Pigmentation Tips ──
        if "Pigmentation & Dark Spots" in concern_names:
            pig_type = results.get("pigmentation", {}).get("pigmentation_type", "")

            if "melasma" in pig_type.lower():
                tips.append({
                    "title": "Melasma Management",
                    "tip": "You show signs of melasma (diffuse darkening). "
                           "Use Tranexamic Acid 3% + Vitamin C. "
                           "SPF 50 is NON-NEGOTIABLE — reapply every 2 hours.",
                    "urgency": "high",
                })
            elif "sun" in pig_type.lower():
                tips.append({
                    "title": "Sun Spot Treatment",
                    "tip": "Your dark spots appear sun-related. Use Vitamin C "
                           "20% in the morning + Alpha Arbutin at night. "
                           "Always wear SPF 50.",
                    "urgency": "medium",
                })

        # ── Wrinkle Tips ──
        if "Fine Lines & Wrinkles" in concern_names:
            wrinkle_data = results.get("wrinkles", {})
            regional = wrinkle_data.get("regional_scores", {})

            if regional.get("forehead", 100) < 70:
                tips.append({
                    "title": "Forehead Lines",
                    "tip": "Your forehead shows the most wrinkle activity. "
                           "Start with Retinol 0.3% at night (3x/week), "
                           "gradually increasing. Always pair with SPF.",
                    "urgency": "medium",
                })

            if regional.get("under_left_eye", 100) < 70 or regional.get("under_right_eye", 100) < 70:
                tips.append({
                    "title": "Eye Area Concern",
                    "tip": "Fine lines around eyes detected. Use a "
                           "peptide-based eye cream. Avoid rubbing your eyes.",
                    "urgency": "medium",
                })

        # ── Pore Tips ──
        if "Enlarged Pores" in concern_names:
            regional_p = results.get("pores", {}).get("regional_analysis", {})
            nose_pores = regional_p.get("nose", {})

            if nose_pores.get("severity") in ["moderate", "high"]:
                tips.append({
                    "title": "Nose Pore Treatment",
                    "tip": "Your nose area shows the most visible pores. "
                           "Use Niacinamide 10% daily + Clay mask once weekly. "
                           "Don't use pore strips — they damage skin.",
                    "urgency": "medium",
                })

        # ── Dark Circle Tips ──
        if "Dark Circles" in concern_names:
            dc_type = results.get("dark_circles", {}).get("color_analysis", {}).get("type", "")

            if dc_type == "vascular":
                tips.append({
                    "title": "Vascular Dark Circles",
                    "tip": "Your dark circles have a blue/purple tone "
                           "(vascular type). Caffeine 5% eye serum helps "
                           "constrict blood vessels. Get 7-9 hours of sleep.",
                    "urgency": "medium",
                })
            elif dc_type == "pigmented":
                tips.append({
                    "title": "Pigmented Dark Circles",
                    "tip": "Your dark circles are brown-toned (pigmentation). "
                           "Use Vitamin C eye cream + Alpha Arbutin. "
                           "Wear SPF even around eyes.",
                    "urgency": "medium",
                })

        # ── Skin Type Tips ──
        if skin_type == "Oily":
            tips.append({
                "title": f"Managing {skin_type} Skin",
                "tip": "Use gel-based, oil-free products. "
                       "Don't skip moisturizer — dehydrated oily skin "
                       "produces MORE oil. Use Niacinamide 10% to control sebum.",
                "urgency": "low",
            })
        elif skin_type == "Dry":
            tips.append({
                "title": f"Managing {skin_type} Skin",
                "tip": "Layer hydrating products: Hyaluronic Acid on damp skin, "
                       "then a ceramide moisturizer. Avoid hot water on face. "
                       "Use a humidifier at night.",
                "urgency": "low",
            })
        elif skin_type == "Combination":
            tips.append({
                "title": f"Managing {skin_type} Skin",
                "tip": "Use lightweight products on T-zone, richer ones on cheeks. "
                       "Niacinamide works well for combination skin — balances oil "
                       "without drying.",
                "urgency": "low",
            })

        return tips

    def _lifestyle_tips(self, results: Dict) -> List[str]:
        """Generate lifestyle recommendations."""
        tips = []
        overall = results.get("overall_score", 50)

        if overall < 60:
            tips.append("🥤 Drink at least 3 liters of water daily")
            tips.append("😴 Get 7-9 hours of quality sleep every night")
            tips.append("🥗 Eat foods rich in Omega-3, Zinc, and Vitamin E")
            tips.append("🚭 Avoid smoking and limit alcohol intake")
            tips.append("☀️ Never skip sunscreen, even on cloudy days")
        elif overall < 80:
            tips.append("💧 Stay hydrated — aim for 2.5L water daily")
            tips.append("🧘 Manage stress — it directly affects skin health")
            tips.append("☀️ Apply SPF 50 every morning, reapply every 2 hours")
        else:
            tips.append("✨ Your skin is doing great! Maintain your current routine")
            tips.append("☀️ Continue using sunscreen daily to prevent future damage")
            tips.append("💤 Keep getting adequate sleep for skin regeneration")

        return tips
    