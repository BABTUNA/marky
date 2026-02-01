"""
Cost Estimator Agent

Estimates production costs for filming the ad based on script requirements.
"""

import json
import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.groq_client import chat_completion


class CostEstimatorAgent:
    """Estimates production costs for the ad."""

    # Standard rate references
    RATE_GUIDE = {
        "actor_half_day": {"low": 150, "medium": 300, "high": 500},
        "actor_full_day": {"low": 250, "medium": 500, "high": 800},
        "location_permit": {"low": 0, "medium": 200, "high": 500},
        "location_rental_hour": {"low": 50, "medium": 150, "high": 400},
        "equipment_basic": {"low": 200, "medium": 400, "high": 800},
        "equipment_premium": {"low": 500, "medium": 1000, "high": 2000},
        "food_person": {"low": 15, "medium": 25, "high": 40},
        "post_production": {"low": 300, "medium": 800, "high": 2000},
        "contingency_percent": 0.15,
    }

    def __init__(self):
        pass

    async def run(
        self,
        product: str,
        industry: str,
        duration: int,
        tone: str,
        city: str,
        previous_results: dict,
    ) -> dict:
        """
        Estimate production costs.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone
            city: City for cost adjustment
            previous_results: Results from previous agents

        Returns:
            dict with cost breakdown and tips
        """

        # Get script data
        script_data = previous_results.get("script_writer", {})
        scenes = script_data.get("scenes", [])

        try:
            # Build scene summary for analysis
            scene_summary = ""
            for scene in scenes:
                scene_summary += f"Scene {scene.get('scene_number', '?')}: {scene.get('visual', '')}\n"

            prompt = f"""You are a video production cost estimator. Analyze these scenes and provide a detailed budget.

PRODUCTION DETAILS:
Product: {product}
Duration: {duration} seconds
City: {city if city else "General US market"}
Scene Count: {len(scenes)}

SCENES TO ANALYZE:
{scene_summary}

Based on the scenes, estimate:
1. Number of actors needed
2. Number of locations
3. Equipment requirements
4. Special requirements (food props, vehicles, etc.)
5. Crew size needed
6. Estimated shoot duration

Then provide a budget in this EXACT JSON format:
{{
    "total": 0000,
    "breakdown": {{
        "talent": 0000,
        "locations": 0000,
        "equipment": 0000,
        "props_wardrobe": 0000,
        "food_craft": 0000,
        "post_production": 0000,
        "contingency": 0000
    }},
    "assumptions": [
        "assumption 1",
        "assumption 2",
        "assumption 3"
    ],
    "budget_level": "low/medium/high",
    "shoot_days": 0,
    "crew_size": 0,
    "actor_count": 0,
    "tips": [
        "money saving tip 1",
        "money saving tip 2"
    ]
}}

Use realistic rates for {city if city else "a mid-size US city"}.
Assume non-union talent and indie production level.
Return ONLY the JSON, no other text."""

            # Use the Groq client with automatic model fallback
            response = chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.2,
            )

            result_text = response["content"].strip()

            # Parse JSON
            try:
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]

                estimate = json.loads(result_text)
                return estimate

            except json.JSONDecodeError:
                # Return a default estimate
                return self._default_estimate(len(scenes), duration)

        except Exception as e:
            return {
                "error": str(e),
                "fallback": self._default_estimate(len(scenes), duration),
            }

    def _default_estimate(self, scene_count: int, duration: int) -> dict:
        """Provide a default estimate when LLM fails."""

        # Simple calculation
        base_talent = 400  # 2 actors
        base_location = 300
        base_equipment = 400
        base_props = 150
        base_food = 100
        base_post = 500

        subtotal = (
            base_talent
            + base_location
            + base_equipment
            + base_props
            + base_food
            + base_post
        )
        contingency = int(subtotal * 0.15)
        total = subtotal + contingency

        return {
            "total": total,
            "breakdown": {
                "talent": base_talent,
                "locations": base_location,
                "equipment": base_equipment,
                "props_wardrobe": base_props,
                "food_craft": base_food,
                "post_production": base_post,
                "contingency": contingency,
            },
            "assumptions": [
                "1-2 non-union actors",
                "1 location, half-day shoot",
                "Basic equipment package",
                "Simple post-production",
            ],
            "budget_level": "low",
            "shoot_days": 1,
            "crew_size": 4,
            "actor_count": 2,
            "tips": [
                "Use natural lighting to reduce equipment costs",
                "Film at your actual business location (free)",
                "Ask friends/family to appear as extras",
            ],
        }
