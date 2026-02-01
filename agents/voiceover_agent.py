"""
Voiceover Agent

Generates professional voiceover audio using ElevenLabs API.
Optimized for natural, human-sounding speech.
"""

import os
import re
from pathlib import Path

import requests


class VoiceoverAgent:
    """Generates voiceover audio using ElevenLabs with natural speech settings."""

    # Voice IDs - prioritizing the most natural-sounding voices
    # These voices are known for their human-like quality
    VOICES = {
        "female": {
            "friendly": "21m00Tcm4TlvDq8ikWAM",  # Rachel - very natural, warm
            "professional": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - clear, professional
            "energetic": "AZnzlk1XvdvUeBnXmlld",  # Domi - upbeat
            "conversational": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        },
        "male": {
            "professional": "29vD33N1CtxCmqQRPOHJ",  # Drew - natural, clear
            "friendly": "ErXwobaYiN019PkySvjV",  # Antoni - warm, friendly
            "energetic": "pNInz6obpgDQGcFmaJgB",  # Adam - dynamic
            "conversational": "29vD33N1CtxCmqQRPOHJ",  # Drew
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

        # Preprocess text for more natural speech
        voiceover_text = self._preprocess_for_natural_speech(voiceover_text, tone)

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
                    "conversational", list(self.VOICES[voice_gender].values())[0]
                ),
            )

            print(
                f"  Using voice: {voice_gender}/{voice_style} (ID: {voice_id[:8]}...)"
            )

            # Get optimal voice settings based on tone
            voice_settings = self._get_voice_settings(tone)

            # Make API request
            # Using eleven_turbo_v2_5 for most natural speech (or eleven_multilingual_v2)
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "text": voiceover_text,
                    "model_id": "eleven_turbo_v2_5",  # Latest, most natural model
                    "voice_settings": voice_settings,
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

        if tone in ["funny", "friendly", "casual", "warm"]:
            return "friendly"
        elif tone in ["energetic", "exciting", "upbeat"]:
            return "energetic"
        elif tone in ["conversational", "natural"]:
            return "conversational"
        else:
            return "professional"

    def _preprocess_for_natural_speech(self, text: str, tone: str) -> str:
        """
        Preprocess text to make TTS sound more natural and human.

        Techniques:
        1. Add natural pauses with commas and ellipses
        2. Add emphasis markers for key words
        3. Break up long sentences
        4. Add conversational fillers for casual tones
        5. Use SSML-like hints that ElevenLabs understands
        """
        # Clean up the text first
        text = text.strip()

        # Remove any existing stage directions or brackets
        text = re.sub(r"\[.*?\]", "", text)
        text = re.sub(r"\(.*?\)", "", text)

        # Add natural pauses after certain phrases
        pause_after = [
            "you know what",
            "here's the thing",
            "let me tell you",
            "the truth is",
            "believe it or not",
            "and honestly",
            "but wait",
            "get this",
        ]
        for phrase in pause_after:
            text = re.sub(rf"({phrase})", r"\1...", text, flags=re.IGNORECASE)

        # Break up very long sentences (over 20 words) with natural pauses
        sentences = text.split(". ")
        processed_sentences = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 25:
                # Find a natural break point (after conjunctions, commas)
                mid = len(words) // 2
                # Look for a good break point near the middle
                for i in range(mid - 3, mid + 4):
                    if i < len(words) and words[i].lower() in [
                        "and",
                        "but",
                        "or",
                        "so",
                        "because",
                        "when",
                        "while",
                        "that",
                    ]:
                        words[i] = f"... {words[i]}"
                        break
                sentence = " ".join(words)
            processed_sentences.append(sentence)
        text = ". ".join(processed_sentences)

        # For funny/casual tones, add slight hesitations that feel natural
        if tone in ["funny", "casual", "friendly"]:
            # Add subtle emphasis to questions
            text = re.sub(r"\?", "?...", text)

        # Clean up multiple spaces and periods
        text = re.sub(r"\.{4,}", "...", text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s+([.,!?])", r"\1", text)

        return text.strip()

    def _get_voice_settings(self, tone: str) -> dict:
        """
        Get optimal voice settings based on tone.

        Key settings for natural speech:
        - stability: Lower (0.3-0.5) = more expressive, natural variation
        - similarity_boost: Higher (0.7-0.9) = maintains voice character
        - style: Controls expressiveness (0 = neutral, 1 = very expressive)
        - use_speaker_boost: True = clearer, more present audio
        """

        # Base settings for natural speech
        base_settings = {
            "stability": 0.4,  # Some variation for naturalness
            "similarity_boost": 0.75,  # Good voice character
            "style": 0.5,  # Moderate expressiveness
            "use_speaker_boost": True,
        }

        # Adjust based on tone
        if tone in ["funny", "casual", "friendly"]:
            return {
                "stability": 0.35,  # More variation = more natural/playful
                "similarity_boost": 0.7,
                "style": 0.7,  # More expressive
                "use_speaker_boost": True,
            }
        elif tone in ["energetic", "exciting", "upbeat"]:
            return {
                "stability": 0.3,  # High variation for energy
                "similarity_boost": 0.65,
                "style": 0.85,  # Very expressive
                "use_speaker_boost": True,
            }
        elif tone in ["professional", "serious"]:
            return {
                "stability": 0.5,  # More stable for authority
                "similarity_boost": 0.8,
                "style": 0.3,  # Less expressive, more measured
                "use_speaker_boost": True,
            }
        elif tone in ["emotional", "heartfelt", "warm"]:
            return {
                "stability": 0.4,
                "similarity_boost": 0.75,
                "style": 0.6,  # Expressive but not over the top
                "use_speaker_boost": True,
            }
        else:
            return base_settings


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
