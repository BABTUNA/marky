"""
Cost Estimator Agent - Enhanced Version

Estimates detailed production costs including:
- Line-item breakdown (every expense category)
- Equipment rental list with specific items
- Crew breakdown with roles and rates
- Talent costs with character descriptions
- Location and permit costs
- Post-production detailed breakdown
- Day-by-day shoot schedule
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.gemini_client import chat_completion  # Using Google Gemini (Cloud credits!)


class CostEstimatorAgent:
    """Estimates detailed production costs for the ad."""

    RATE_GUIDE = {
        "talent": {
            "lead_actor_half_day": {"low": 200, "medium": 400, "high": 750},
            "lead_actor_full_day": {"low": 350, "medium": 700, "high": 1200},
            "extra_half_day": {"low": 75, "medium": 150, "high": 250},
            "extra_full_day": {"low": 125, "medium": 250, "high": 400},
            "voiceover_artist": {"low": 150, "medium": 350, "high": 600},
        },
        "crew": {
            "director_half_day": {"low": 250, "medium": 500, "high": 1000},
            "director_full_day": {"low": 400, "medium": 800, "high": 1500},
            "dp_half_day": {"low": 200, "medium": 400, "high": 800},
            "dp_full_day": {"low": 350, "medium": 700, "high": 1200},
            "sound_mixer": {"low": 150, "medium": 300, "high": 500},
            "gaffer": {"low": 150, "medium": 300, "high": 500},
            "pa": {"low": 75, "medium": 125, "high": 200},
        },
        "equipment": {
            "camera_package_basic": {"low": 300, "medium": 600, "high": 1200},
            "camera_package_pro": {"low": 800, "medium": 1500, "high": 3000},
            "lighting_package": {"low": 200, "medium": 400, "high": 800},
            "audio_package": {"low": 100, "medium": 200, "high": 400},
            "grip_package": {"low": 100, "medium": 200, "high": 400},
        },
        "post": {
            "editing_basic": {"low": 400, "medium": 1000, "high": 2000},
            "editing_premium": {"low": 800, "medium": 2000, "high": 4000},
            "color_grading": {"low": 200, "medium": 500, "high": 1000},
            "sound_design": {"low": 150, "medium": 400, "high": 800},
            "music_licensing": {"low": 100, "medium": 300, "high": 600},
            "rendering_export": {"low": 50, "medium": 100, "high": 200},
        },
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
        """Estimate detailed production costs."""

        script_data = previous_results.get("script_writer", {})
        scenes = script_data.get("scenes", [])
        location_data = previous_results.get("location_scout", {})
        locations = location_data.get("locations", [])

        try:
            scene_summary = ""
            for scene in scenes:
                scene_summary += f"Scene {scene.get('scene_number', '?')}: {scene.get('visual', '')}\n"

            locations_summary = ""
            for loc in locations[:3]:
                locations_summary += f"- {loc.get('name', 'Unknown')} ({loc.get('price_level', 'unknown')})\n"

            prompt = f"""You are a detailed video production cost estimator. Create a comprehensive line-item budget for this commercial.

PRODUCTION DETAILS:
Product: {product}
Industry: {industry}
Duration: {duration} seconds
Tone: {tone}
City: {city if city else "General US market"}
Scene Count: {len(scenes)}

SCENES TO ANALYZE:
{scene_summary}

LOCATIONS IDENTIFIED:
{locations_summary if locations_summary else "Location scouting pending - assume generic location"}

Based on the script and industry, provide a detailed budget in this EXACT JSON format:

{{
    "summary": {{
        "total": 0,
        "budget_level": "low/medium/high",
        "shoot_days": 1,
        "crew_size": 0,
        "actor_count": 0,
        "location_count": 0
    }},
    "talent": {{
        "total": 0,
        "line_items": [
            {{
                "item": "Lead Actor - [Character Description]",
                "quantity": 1,
                "unit": "day",
                "rate": 0,
                "total": 0,
                "notes": "Non-union, local casting"
            }}
        ]
    }},
    "crew": {{
        "total": 0,
        "line_items": [
            {{
                "role": "Director",
                "quantity": 1,
                "unit": "day",
                "rate": 0,
                "total": 0
            }}
        ]
    }},
    "equipment": {{
        "total": 0,
        "line_items": [
            {{
                "item": "Camera Package - [specs]",
                "quantity": 1,
                "unit": "day",
                "rate": 0,
                "total": 0
            }}
        ]
    }},
    "locations": {{
        "total": 0,
        "line_items": [
            {{
                "location": "Location name",
                "type": "permit/rental/自有",
                "cost": 0,
                "notes": "Details"
            }}
        ]
    }},
    "props_wardrobe": {{
        "total": 0,
        "line_items": [
            {{
                "item": "Description",
                "cost": 0,
                "notes": "Source/rental/购买"
            }}
        ]
    }},
    "food_craft": {{
        "total": 0,
        "per_person": 0,
        "total_persons": 0,
        "notes": "Crew meals for shoot day"
    }},
    "post_production": {{
        "total": 0,
        "line_items": [
            {{
                "task": "Editing",
                "hours": 0,
                "rate": 0,
                "total": 0
            }}
        ]
    }},
    "breakdown": {{
        "talent": 0,
        "crew": 0,
        "equipment": 0,
        "locations": 0,
        "props_wardrobe": 0,
        "food_craft": 0,
        "post_production": 0,
        "contingency": 0
    }},
    "assumptions": [
        "1-2 non-union actors, half-day shoot",
        "Basic 3-person crew (DP, sound, director)",
        "Single location, natural lighting",
        "1-day shoot, 8 hours"
    ],
    "schedule": [
        {{"day": 1, "activity": "Shoot day - setup, filming, wrap", "hours": "8-10"}},
        {{"day": 2, "activity": "Post-production editing", "hours": "4-6"}}
    ],
    "tips": [
        "Use natural lighting to reduce equipment costs",
        "Film at your actual business location (free)"
    ]
}}

Requirements:
- Determine appropriate budget level (low/medium/high) based on production value needed
- Realistic rates for {city if city else "a mid-size US city"}
- Non-union talent, indie production level
- Include specific equipment names (e.g., "Sony A7S III", "Aputure 300d")
- Include specific crew roles
- Calculate contingency at 15% of subtotal
- Return ONLY the JSON, no other text."""

            response = chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.2,
            )

            result_text = response["content"].strip()

            try:
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]

                estimate = json.loads(result_text)
                return estimate

            except json.JSONDecodeError:
                return self._default_detailed_estimate(len(scenes), duration)

        except Exception as e:
            return {
                "error": str(e),
                "fallback": self._default_detailed_estimate(len(scenes), duration),
            }

    def _default_detailed_estimate(self, scene_count: int, duration: int) -> dict:
        """Provide a detailed default estimate when LLM fails."""

        talent_total = 400
        crew_total = 600
        equipment_total = 400
        locations_total = 200
        props_total = 150
        food_total = 100
        post_total = 600

        subtotal = talent_total + crew_total + equipment_total + locations_total + props_total + food_total + post_total
        contingency = int(subtotal * 0.15)
        total = subtotal + contingency

        return {
            "summary": {
                "total": total,
                "budget_level": "low",
                "shoot_days": 1,
                "crew_size": 4,
                "actor_count": 2,
                "location_count": 1,
            },
            "talent": {
                "total": talent_total,
                "line_items": [
                    {"item": "Lead Actor (On-Camera)", "quantity": 1, "unit": "half day", "rate": 200, "total": 200, "notes": "Non-union, local"},
                    {"item": "Supporting Actor", "quantity": 1, "unit": "half day", "rate": 150, "total": 150, "notes": "Non-union, local"},
                    {"item": "Voiceover Artist", "quantity": 1, "unit": "session", "rate": 50, "total": 50, "notes": "Studio session"},
                ],
            },
            "crew": {
                "total": crew_total,
                "line_items": [
                    {"role": "Director", "quantity": 1, "unit": "half day", "rate": 200, "total": 200},
                    {"role": "Director of Photography", "quantity": 1, "unit": "half day", "rate": 175, "total": 175},
                    {"role": "Sound Mixer", "quantity": 1, "unit": "half day", "rate": 125, "total": 125},
                    {"role": "Production Assistant", "quantity": 1, "unit": "half day", "rate": 100, "total": 100},
                ],
            },
            "equipment": {
                "total": equipment_total,
                "line_items": [
                    {"item": "Camera Package (Sony A7S III or similar)", "quantity": 1, "unit": "day", "rate": 200, "total": 200},
                    {"item": "Lighting Package (Aputure LEDs)", "quantity": 1, "unit": "day", "rate": 100, "total": 100},
                    {"item": "Audio Package (Zoom recorder + mics)", "quantity": 1, "unit": "day", "rate": 75, "total": 75},
                    {"item": "Grip & Support", "quantity": 1, "unit": "day", "rate": 25, "total": 25},
                ],
            },
            "locations": {
                "total": locations_total,
                "line_items": [
                    {"location": "Your Business Location", "type": "自有 (Free)", "cost": 0, "notes": "Recommended - authentic and free"},
                    {"location": "Permit (if public location)", "type": "permit", "cost": 150, "notes": "City permit if needed"},
                    {"location": "Backup Indoor Location", "type": "rental", "cost": 50, "notes": "Photo studio backup"},
                ],
            },
            "props_wardrobe": {
                "total": props_total,
                "line_items": [
                    {"item": "Product/Service Props", "cost": 75, "notes": "Your actual products"},
                    {"item": "Wardrobe for Talent", "cost": 50, "notes": "Simple, matching brand aesthetic"},
                    {"item": "Miscellaneous Set Dressing", "cost": 25, "notes": "Small items to enhance scene"},
                ],
            },
            "food_craft": {
                "total": food_total,
                "per_person": 15,
                "total_persons": 6,
                "notes": "Lunch and snacks for crew",
            },
            "post_production": {
                "total": post_total,
                "line_items": [
                    {"task": "Video Editing", "hours": 8, "rate": 50, "total": 400},
                    {"task": "Color Grading", "hours": 2, "rate": 50, "total": 100},
                    {"task": "Sound Design & Mix", "hours": 2, "rate": 50, "total": 100},
                ],
            },
            "breakdown": {
                "talent": talent_total,
                "crew": crew_total,
                "equipment": equipment_total,
                "locations": locations_total,
                "props_wardrobe": props_total,
                "food_craft": food_total,
                "post_production": post_total,
                "contingency": contingency,
            },
            "assumptions": [
                "1-2 non-union actors",
                "Half-day shoot (4-5 hours)",
                "4-person crew",
                "Single location (your business)",
                "Basic equipment package",
                "Simple post-production",
            ],
            "schedule": [
                {"day": 1, "activity": "Shoot Day: Setup (1hr) + Filming (3hr) + Wrap (1hr)", "hours": "5"},
                {"day": 2, "activity": "Post-Production: Editing (4hr) + Color/Sound (2hr)", "hours": "6"},
                {"day": 3, "activity": "Final Review & Export", "hours": "1"},
            ],
            "tips": [
                "Use natural lighting to reduce equipment costs",
                "Film at your actual business location (free, authentic)",
                "Ask friends/family to appear as extras",
                "Use your own phone/camera if equipment budget is tight",
                "Record voiceover in a quiet room with free Audacity software",
            ],
        }
