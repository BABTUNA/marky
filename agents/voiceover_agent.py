"""
Voiceover Agent

Generates professional voiceover audio using Google Cloud Text-to-Speech.
Uses Studio voices for natural, high-quality speech.
"""

import os
import re
from pathlib import Path

try:
    from google.cloud import texttospeech

    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class VoiceoverAgent:
    """Generates voiceover audio using Google Cloud Text-to-Speech."""

    def __init__(self):
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
        Generate voiceover from script using Google TTS.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone (affects voice selection)
            city: City (unused)
            previous_results: Results from previous agents

        Returns:
            dict with audio_path and metadata
        """
        if not TTS_AVAILABLE:
            return {
                "error": "google-cloud-texttospeech not installed. pip install google-cloud-texttospeech",
                "skipped": True,
            }

        # Get voiceover text from script
        script_data = previous_results.get("script_writer", {})
        voiceover_text = script_data.get("voiceover_text", "")

        if not voiceover_text:
            scenes = script_data.get("scenes", [])
            voiceover_parts = []
            for s in scenes:
                v = s.get("voiceover", "") or s.get("narration", "")
                if v and v not in ["[Background music only]", "[Music only]"]:
                    voiceover_parts.append(v)
            voiceover_text = " ".join(voiceover_parts)

        if not voiceover_text:
            return {"error": "No voiceover text available in script"}

        # Preprocess text
        voiceover_text = self._preprocess_text(voiceover_text)

        # Truncate (Google TTS limit ~5000 chars)
        if len(voiceover_text) > 5000:
            voiceover_text = voiceover_text[:5000]

        try:
            audio_path = await self._google_tts_generate(
                text=voiceover_text, product=product, tone=tone
            )
            if not audio_path:
                return {"error": "Google TTS generation failed", "skipped": True}

            word_count = len(voiceover_text.split())
            estimated_duration = (word_count / 150) * 60

            return {
                "audio_path": str(audio_path),
                "duration": round(estimated_duration, 1),
                "character_count": len(voiceover_text),
                "provider": "google_tts",
            }
        except Exception as e:
            return {"error": str(e)}

    def _preprocess_text(self, text: str) -> str:
        """Clean text for TTS - remove stage directions, normalize whitespace."""
        text = text.strip()
        text = re.sub(r"\[.*?\]", "", text)
        text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _prepare_ssml(self, text: str, tone: str) -> str:
        """Convert text to SSML. Studio voices use rate only (no pitch)."""
        text = text.strip()
        text = re.sub(r"\.(\s+)", r'.<break time="300ms"/>\1', text)
        text = re.sub(r",(\s+)", r',<break time="150ms"/>\1', text)
        text = re.sub(r"\.\.\.", r'<break time="400ms"/>', text)
        text = re.sub(r"\?(\s+)", r'?<break time="250ms"/>\1', text)
        prosody_map = {
            "professional": 'rate="95%"',
            "friendly": 'rate="100%"',
            "energetic": 'rate="105%"',
            "calm": 'rate="90%"',
            "funny": 'rate="102%"',
        }
        prosody = prosody_map.get(tone.lower(), 'rate="97%"')
        return f"<speak><prosody {prosody}>{text}</prosody></speak>"

    async def _google_tts_generate(
        self, text: str, product: str, tone: str = "professional"
    ) -> str | None:
        """Generate speech using Google Cloud Text-to-Speech."""
        try:
            client = texttospeech.TextToSpeechClient()
            ssml_text = self._prepare_ssml(text, tone)
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

            voice_map = {
                "professional": ("en-US-Studio-Q", texttospeech.SsmlVoiceGender.MALE),
                "friendly": ("en-US-Studio-O", texttospeech.SsmlVoiceGender.FEMALE),
                "energetic": ("en-US-Casual-K", texttospeech.SsmlVoiceGender.MALE),
                "calm": ("en-US-Wavenet-C", texttospeech.SsmlVoiceGender.FEMALE),
                "funny": ("en-US-Casual-K", texttospeech.SsmlVoiceGender.MALE),
            }
            voice_name, voice_gender = voice_map.get(
                tone.lower(), ("en-US-Studio-Q", texttospeech.SsmlVoiceGender.MALE)
            )

            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", name=voice_name, ssml_gender=voice_gender
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.05,
                pitch=0.0,
            )

            print(f"  Using Google TTS voice: {voice_name}")

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")[:20]
            filepath = self.output_dir / f"voiceover_{safe_product}.mp3"
            with open(filepath, "wb") as f:
                f.write(response.audio_content)

            return str(filepath)
        except Exception as e:
            print(f"  Google TTS error: {e}")
            return None


class MockVoiceoverAgent:
    """Mock voiceover agent for testing."""

    async def run(self, **kwargs) -> dict:
        previous_results = kwargs.get("previous_results", {})
        script_data = previous_results.get("script_writer", {})
        voiceover_text = script_data.get("voiceover_text", "Sample voiceover text")

        return {
            "audio_path": "output/voiceovers/mock_voiceover.mp3",
            "duration": 45.0,
            "character_count": len(voiceover_text),
            "provider": "mock",
        }
