"""
Music Agent

Suggests royalty-free background music based on ad tone and industry.
Does NOT generate music - provides recommendations from free libraries.
"""

import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.groq_client import chat_completion


class MusicAgent:
    """Suggests appropriate background music for the ad."""

    # Royalty-free music libraries
    FREE_MUSIC_SOURCES = [
        {"name": "Pixabay Music", "url": "https://pixabay.com/music/"},
        {"name": "Free Music Archive", "url": "https://freemusicarchive.org/"},
        {"name": "Mixkit", "url": "https://mixkit.co/free-stock-music/"},
        {
            "name": "YouTube Audio Library",
            "url": "https://studio.youtube.com/channel/audio",
        },
    ]

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
        Suggest music for the ad.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone
            city: City (unused)
            previous_results: Results from previous agents

        Returns:
            dict with music suggestions
        """

        try:
            # Get script context for better suggestions
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
Search these terms on Pixabay Music or Mixkit:
- "[search term 1]"
- "[search term 2]"
- "[search term 3]"

Keep suggestions appropriate for commercial use (royalty-free)."""

            # Use the Groq client with automatic model fallback
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
                "free_music_sources": self.FREE_MUSIC_SOURCES,
                "quick_recommendation": self._get_quick_recommendation(tone, industry),
            }

        except Exception as e:
            return {
                "error": str(e),
                "fallback_suggestion": self._get_quick_recommendation(tone, industry),
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

        # Default
        return {
            "genre": "Upbeat Corporate",
            "search_terms": [
                "upbeat background",
                "commercial music",
                "positive energy",
            ],
            "bpm": "100-120",
            "bpm": "100-120",
        }
