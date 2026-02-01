"""
Voiceover Agent

Generates professional voiceover audio using ElevenLabs API.
"""

import os
from pathlib import Path

import requests


class VoiceoverAgent:
    """Generates voiceover audio using ElevenLabs."""

    # Free tier voice IDs
    VOICES = {
        "female": {
            "friendly": "EXAVITQu4vr4xnSDxMaL",  # Bella
            "energetic": "AZnzlk1XvdvUeBnXmlld",  # Domi
        },
        "male": {
            "professional": "ErXwobaYiN019PkySvjV",  # Antoni
            "friendly": "VR6AewLTigWG4xSOukaG",  # Arnold
            "energetic": "pNInz6obpgDQGcFmaJgB",  # Adam
        },
    }

    def __init__(self):
        self.base_url = "https://api.elevenlabs.io/v1"
        self.output_dir = Path("output/voiceovers")
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        Generate voiceover from script.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone (affects voice selection)
            city: City (unused)
            previous_results: Results from previous agents

        Returns:
            dict with audio URL/path and metadata
        """

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            return {"error": "ELEVENLABS_API_KEY not set", "skipped": True}

        # Get voiceover text from script
        script_data = previous_results.get("script_writer", {})
        voiceover_text = script_data.get("voiceover_text", "")

        if not voiceover_text:
            # Try to extract from scenes
            scenes = script_data.get("scenes", [])
            voiceover_parts = [s.get("voiceover", "") for s in scenes]
            voiceover_text = " ".join(voiceover_parts)

        if not voiceover_text:
            return {"error": "No voiceover text available"}

        # Clean the text
        voiceover_text = voiceover_text.strip()

        # Check character limit (free tier is 10k/month)
        if len(voiceover_text) > 2000:
            voiceover_text = voiceover_text[:2000]
            print(f"  Voiceover truncated to 2000 chars")

        try:
            # Intelligent voice selection based on product/industry
            voice_gender = self._select_voice_gender(product, industry)
            voice_style = self._select_voice_style(tone)

            # Get the appropriate voice ID
            voice_id = self.VOICES[voice_gender].get(
                voice_style,
                self.VOICES[voice_gender].get(
                    "friendly", list(self.VOICES[voice_gender].values())[0]
                ),
            )

            # Make API request
            # Using eleven_multilingual_v2 for more natural, human-like speech
            # Voice settings tuned for conversational, natural delivery:
            # - Lower stability (0.3) = more expressive, natural variation
            # - Higher similarity_boost (0.8) = maintains voice character
            # - style = 0.5 for balanced expressiveness
            # - use_speaker_boost = True for clearer, more present voice
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "text": voiceover_text,
                    "model_id": "eleven_multilingual_v2",  # More natural sounding model
                    "voice_settings": {
                        "stability": 0.3,  # Lower = more expressive/natural
                        "similarity_boost": 0.8,  # Keep voice character
                        "style": 0.5,  # Expressiveness
                        "use_speaker_boost": True,  # Clearer audio
                    },
                },
                timeout=60,
            )

            if response.status_code != 200:
                return {
                    "error": f"ElevenLabs API error: {response.status_code}",
                    "details": response.text[:200],
                }

            # Save audio file
            filename = f"voiceover_{product.replace(' ', '_')}_{duration}s.mp3"
            filepath = self.output_dir / filename

            with open(filepath, "wb") as f:
                f.write(response.content)

            # Estimate duration (rough: ~150 words per minute)
            word_count = len(voiceover_text.split())
            estimated_duration = (word_count / 150) * 60

            return {
                "audio_path": str(filepath),
                "audio_url": str(filepath),  # For local testing
                "duration": round(estimated_duration, 1),
                "character_count": len(voiceover_text),
                "voice_id": voice_id,
                "text_preview": voiceover_text[:100] + "...",
            }

        except Exception as e:
            return {"error": str(e)}

    def _select_voice_gender(self, product: str, industry: str) -> str:
        """Select voice gender based on product and industry context."""

        product_lower = product.lower()

        # Men's products - use male voice
        mens_keywords = [
            "cologne",
            "men's",
            "mens",
            "beard",
            "shaving",
            "razor",
            "male",
            "gentleman",
            "barber",
            "sir",
            "guy",
            "bro",
        ]

        # Women's products - use female voice
        womens_keywords = [
            "makeup",
            "cosmetic",
            "lipstick",
            "mascara",
            "nail",
            "beauty",
            "women's",
            "womens",
            "female",
            "lady",
            "ladies",
            "spa",
            "salon",
            "skincare",
            "facial",
            "manicure",
            "pedicure",
        ]

        # Check product name for gender indicators
        for keyword in mens_keywords:
            if keyword in product_lower:
                return "male"

        for keyword in womens_keywords:
            if keyword in product_lower:
                return "female"

        # Industry-based defaults
        industry_defaults = {
            "beauty": "female",
            "fashion": "female",
            "fitness": "male",  # Often male, but could vary
            "tech": "male",
            "construction": "male",
            "automotive": "male",
            "food": "female",  # Warmer, more inviting
            "services": "male",  # Professional
        }

        # Return industry default or female as fallback (more versatile)
        return industry_defaults.get(industry, "female")

    def _select_voice_style(self, tone: str) -> str:
        """Select voice style based on tone."""

        if tone in ["funny", "friendly", "casual"]:
            return "friendly"
        elif tone in ["energetic", "exciting", "upbeat"]:
            return "energetic"
        else:
            return "professional"


class MockVoiceoverAgent:
    """Mock voiceover agent for testing."""

    async def run(self, **kwargs) -> dict:
        previous_results = kwargs.get("previous_results", {})
        script_data = previous_results.get("script_writer", {})
        voiceover_text = script_data.get("voiceover_text", "Sample voiceover text")

        return {
            "audio_path": "output/voiceovers/mock_voiceover.mp3",
            "audio_url": "https://example.com/mock_voiceover.mp3",
            "duration": 45.0,
            "character_count": len(voiceover_text),
            "mock": True,
            "mock": True,
        }
