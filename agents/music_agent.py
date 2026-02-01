"""
Music Agent

Provides music recommendations for ads. Background music is optional -
the audio mixer will work with voiceover only if no music is provided.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.groq_client import chat_completion


class MusicAgent:
    """Provides music recommendations for ads. Music is optional."""

    def __init__(self):
        self.output_dir = Path("output/music") if False else None  # No download needed

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
        Provide music recommendations for the ad.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone
            city: City (unused)
            previous_results: Results from previous agents

        Returns:
            dict with music recommendations (no actual download)
        """

        try:
            script_data = previous_results.get("script_writer", {})
            scenes = script_data.get("scenes", [])

            scene_summary = ""
            for scene in scenes[:3]:
                scene_summary += (
                    f"- {scene.get('title', '')}: {scene.get('visual', '')[:50]}\n"
                )

            prompt = f"""You are a music supervisor for commercials. Suggest background music for this ad:

Product: {product}
Industry: {industry}
Duration: {duration} seconds
Tone: {tone}

Scene Overview:
{scene_summary}

Provide music recommendations in this format:

1. PRIMARY RECOMMENDATION:
- Genre: [specific genre]
- Tempo: [BPM range]
- Mood: [2-3 mood descriptors]
- Instruments: [key instruments]
- Search terms: [what to search on royalty-free sites]
- Example track style: [describe the ideal track]

2. ALTERNATIVE OPTIONS:
- Option A: [genre] - [brief description]
- Option B: [genre] - [brief description]

3. MUSIC STRUCTURE:
- Intro (0-{duration // 6}s): [energy level, what happens musically]
- Build ({duration // 6}-{duration // 2}s): [description]
- Peak ({duration // 2}-{int(duration * 0.75)}s): [description]
- Outro ({int(duration * 0.75)}-{duration}s): [description]

4. SPECIFIC TRACK SUGGESTIONS:
Search these terms on Pixabay Music, Mixkit, or Epidemic Sound:
- "[search term 1]"
- "[search term 2]"
- "[search term 3]"

Keep suggestions appropriate for commercial use (royalty-free)."""

            response = chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7,
            )

            suggestions = response["content"].strip()

            return {
                "suggestions": suggestions,
                "tone": tone,
                "duration": duration,
                "quick_recommendation": self._get_quick_recommendation(tone, industry),
                "note": "Music is optional - audio mixer works with voiceover only",
            }

        except Exception as e:
            return {
                "error": str(e),
                "fallback_suggestion": self._get_quick_recommendation(tone, industry),
                "note": "Music is optional - audio mixer works with voiceover only",
            }

    def _get_quick_recommendation(self, tone: str, industry: str) -> dict:
        """Provide a quick recommendation without API call."""

        recommendations = {
            ("professional", "food"): {
                "genre": "Acoustic / Light Jazz",
                "search_terms": ["upbeat acoustic", "happy ukulele", "cafe jazz"],
                "bpm": "100-120",
            },
            ("funny", "food"): {
                "genre": "Quirky / Playful",
                "search_terms": ["quirky comedy", "fun ukulele", "playful pizzicato"],
                "bpm": "120-140",
            },
            ("professional", "tech"): {
                "genre": "Corporate / Inspiring",
                "search_terms": [
                    "corporate inspiring",
                    "technology background",
                    "innovation",
                ],
                "bpm": "90-110",
            },
            ("energetic", "fitness"): {
                "genre": "Electronic / Workout",
                "search_terms": [
                    "workout motivation",
                    "energetic electronic",
                    "gym music",
                ],
                "bpm": "128-140",
            },
            ("emotional", "services"): {
                "genre": "Cinematic / Inspirational",
                "search_terms": [
                    "emotional piano",
                    "inspirational cinematic",
                    "heartfelt",
                ],
                "bpm": "70-90",
            },
        }

        key = (tone, industry)
        if key in recommendations:
            return recommendations[key]

        return {
            "genre": "Upbeat Corporate",
            "search_terms": [
                "upbeat background",
                "commercial music",
                "positive energy",
            ],
            "bpm": "100-120",
        }


# Required for Path import
from pathlib import Path
