"""
Lyria Music Generation Agent

Google's Lyria generates high-quality music from text prompts.
Perfect for background music in viral videos.

Lyria Features:
- Real-time music generation
- Various genres and moods
- 30s duration (configurable)
- Stereo 48kHz output
- WAV format

Cost: Covered by Google Cloud credits (pricing TBD by Google)

TESTING MODE:
- Set LYRIA_USE_MOCK=true to use mock/royalty-free music instead
- This allows testing the full pipeline without Lyria API access
"""

import asyncio
import os
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

# Lyria will be available via Vertex AI (same as VEO/Imagen)
try:
    import vertexai

    # from vertexai.preview.audio_models import MusicGenerationModel
    LYRIA_AVAILABLE = True
except ImportError:
    LYRIA_AVAILABLE = False

# TESTING: Set to True to use mock/royalty-free music
LYRIA_USE_MOCK = os.getenv("LYRIA_USE_MOCK", "true").lower() == "true"


class LyriaAgent:
    """
    Generates background music using Google Lyria.

    Perfect for viral video soundtracks - creates engaging,
    professional music that matches the video mood.
    """

    def __init__(self):
        self.output_dir = Path("output/lyria_music")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_REGION", "us-central1")

        # Lyria configuration
        self.model_name = "lyria-realtime"  # Google Lyria model
        self.default_duration = 30  # seconds
        self.sample_rate = 48000  # 48kHz stereo
        self.format = "wav"

        self.model = None

    def _initialize_lyria(self):
        """Initialize Lyria model (lazy loading)."""
        if not LYRIA_AVAILABLE:
            print("  ⚠️  Lyria not available - vertexai package required")
            return False

        if not self.project_id:
            print("  ⚠️  GCP_PROJECT_ID not set")
            return False

        try:
            vertexai.init(project=self.project_id, location=self.location)
            # Placeholder - actual model initialization depends on Google's API
            # self.model = MusicGenerationModel.from_pretrained("lyria-realtime")
            print(f"  ✅ Lyria model ready: {self.model_name}")
            return True
        except Exception as e:
            print(f"  ❌ Lyria initialization failed: {e}")
            return False

    async def run(
        self,
        product: str,
        industry: str,
        tone: str,
        duration: int,
        previous_results: dict,
        city: str = "",  # Accept but not used
        **kwargs,  # Accept any other params
    ) -> Dict[str, Any]:
        """
        Generate background music using Lyria.

        Args:
            product: Product/business name
            industry: Industry type
            tone: Music mood (energetic, calm, upbeat, etc.)
            duration: Target duration in seconds
            previous_results: Research and script data for context

        Returns:
            Dict with audio_path, duration, format info
        """

        print("\n🎵 Lyria Music Generation Agent")
        print("=" * 60)
        print(f"   Product: {product}")
        print(f"   Mood: {tone}")
        print(f"   Duration: {duration}s")
        print(f"   Format: Stereo 48kHz WAV")
        print("=" * 60)

        # Extract context from previous results
        research_data = previous_results.get("research", {})
        script_data = previous_results.get("script_writer", {})

        # Build Lyria music prompt
        music_prompt = self._build_music_prompt(
            product=product,
            industry=industry,
            tone=tone,
            duration=duration,
            research_data=research_data,
        )

        print(f"\n🎼 Lyria Prompt:")
        print(f"   {music_prompt[:150]}...")

        # MOCK MODE: Use placeholder/royalty-free music for testing
        if LYRIA_USE_MOCK:
            audio_path = await self._use_mock_music(product, tone, duration)
            if audio_path:
                print(f"\n✅ Using MOCK music for testing: {audio_path}")
                return {
                    "status": "mock_mode",
                    "enabled": True,
                    "audio_path": audio_path,
                    "duration": duration,
                    "format": "mp3",
                    "sample_rate": self.sample_rate,
                    "channels": "stereo",
                    "cost_estimate": 0.00,  # No cost for mock
                    "note": "MOCK MODE - using placeholder music for pipeline testing",
                    "prompt": music_prompt,
                }
            else:
                print(
                    "\n⚠️  Mock music generation failed, falling back to disabled mode"
                )

        # TODO: Uncomment when ready to actually generate
        # audio_path = await self._generate_music(music_prompt, product, duration)

        # For now, return placeholder
        print("\n⏸️  Lyria generation DISABLED (groundwork only)")
        print("   To enable: Uncomment generation code in lyria_agent.py")

        return {
            "status": "groundwork_ready",
            "enabled": False,
            "audio_path": None,
            "duration": duration,
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": "stereo",
            "cost_estimate": 0.50,  # Estimated
            "note": "Lyria infrastructure ready - enable when needed",
            "prompt": music_prompt,
        }

    def _build_music_prompt(
        self,
        product: str,
        industry: str,
        tone: str,
        duration: int,
        research_data: dict,
    ) -> str:
        """
        Build optimized prompt for Lyria music generation.

        Lyria best practices:
        - Specify genre and mood clearly
        - Describe tempo and energy level
        - Mention target audience
        - Keep it concise (under 200 tokens)
        """

        # Map tone to music characteristics
        music_style_map = {
            "energetic": {
                "genre": "upbeat pop",
                "tempo": "fast-paced",
                "energy": "high energy",
                "instruments": "electronic synths, driving drums",
            },
            "professional": {
                "genre": "corporate background",
                "tempo": "moderate tempo",
                "energy": "confident and polished",
                "instruments": "piano, strings, subtle percussion",
            },
            "playful": {
                "genre": "fun and bright",
                "tempo": "bouncy and upbeat",
                "energy": "cheerful and optimistic",
                "instruments": "ukulele, whistling, hand claps",
            },
            "calm": {
                "genre": "ambient chill",
                "tempo": "slow and relaxed",
                "energy": "peaceful and soothing",
                "instruments": "soft piano, gentle pads, light guitar",
            },
            "inspiring": {
                "genre": "motivational",
                "tempo": "building crescendo",
                "energy": "uplifting and powerful",
                "instruments": "orchestral strings, epic drums, brass",
            },
        }

        music_style = music_style_map.get(
            tone.lower(),
            {
                "genre": "modern commercial",
                "tempo": "moderate",
                "energy": "engaging",
                "instruments": "mixed instrumentation",
            },
        )

        # Industry-specific adjustments
        if industry in ["restaurant", "food", "cafe"]:
            music_style["genre"] = "modern acoustic"
            music_style["instruments"] = "acoustic guitar, light percussion"
        elif industry in ["tech", "software", "startup"]:
            music_style["genre"] = "modern electronic"
            music_style["instruments"] = "synths, electronic beats"
        elif industry in ["fitness", "sports", "wellness"]:
            music_style["genre"] = "energetic electronic"
            music_style["tempo"] = "fast and pumping"

        # Build prompt
        prompt = f"""{duration}-second background music for {product} advertisement

Genre: {music_style["genre"]}
Mood: {tone}, {music_style["energy"]}
Tempo: {music_style["tempo"]}
Instrumentation: {music_style["instruments"]}

Style: Modern, professional, viral video soundtrack
Target: Social media (TikTok/Instagram Reels)
No vocals, instrumental only
Optimized for background music that doesn't overpower narration"""

        return prompt

    async def _use_mock_music(
        self,
        product: str,
        tone: str,
        duration: int,
    ) -> Optional[str]:
        """
        Download royalty-free music from Pixabay for the pipeline.

        Pixabay offers free music for commercial use (no attribution required).

        Returns:
            Path to downloaded audio file
        """
        try:
            # Check for existing MUSIC files in the output directory
            existing_music = [
                f
                for f in (
                    list(self.output_dir.glob("*.mp3"))
                    + list(self.output_dir.glob("*.wav"))
                )
                if "music" in f.name.lower() and "voiceover" not in f.name.lower()
            ]
            if existing_music:
                print(f"   🎵 Using existing music file: {existing_music[0].name}")
                return str(existing_music[0])

            # Download royalty-free music from Pixabay based on tone
            print(f"   🎵 Downloading royalty-free music for tone: {tone}...")

            # Curated Pixabay tracks (direct download URLs) - all royalty-free
            # These are popular tracks that work well for ads
            tone_tracks = {
                "energetic": {
                    "url": "https://cdn.pixabay.com/download/audio/2022/10/25/audio_946b0939c8.mp3",
                    "name": "energetic_upbeat_music.mp3",
                },
                "professional": {
                    "url": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
                    "name": "corporate_professional_music.mp3",
                },
                "friendly": {
                    "url": "https://cdn.pixabay.com/download/audio/2023/07/17/audio_6d0c5c5f9a.mp3",
                    "name": "friendly_uplifting_music.mp3",
                },
                "calm": {
                    "url": "https://cdn.pixabay.com/download/audio/2022/02/22/audio_d1718ab41b.mp3",
                    "name": "calm_ambient_music.mp3",
                },
                "playful": {
                    "url": "https://cdn.pixabay.com/download/audio/2024/11/04/audio_4956b4edd1.mp3",
                    "name": "playful_fun_music.mp3",
                },
                "inspiring": {
                    "url": "https://cdn.pixabay.com/download/audio/2023/09/27/audio_3eebc83054.mp3",
                    "name": "inspiring_motivational_music.mp3",
                },
            }

            # Get track for tone, default to professional
            track = tone_tracks.get(tone.lower(), tone_tracks["professional"])

            safe_product = product.replace(" ", "_").replace("/", "_")[:20]
            output_path = self.output_dir / f"{safe_product}_music_{duration}s.mp3"

            # Download the track using curl (more reliable than urllib with SSL)
            print(f"   📥 Downloading: {track['name']}")
            import subprocess

            result = subprocess.run(
                ["curl", "-L", "-s", "-o", str(output_path), track["url"]],
                capture_output=True,
                timeout=60,
            )

            if result.returncode == 0 and output_path.exists():
                print(f"   ✅ Music downloaded: {output_path}")
                return str(output_path)
            else:
                raise Exception(f"curl failed: {result.stderr.decode()}")

        except Exception as e:
            print(f"   ⚠️ Music download failed: {e}")
            print(f"   🎵 Falling back to silent placeholder...")

            # Fallback to silent audio
            silent_path = (
                self.output_dir / f"{product.replace(' ', '_')}_silent_{duration}s.wav"
            )

            import struct
            import wave

            sample_rate = 44100
            num_samples = sample_rate * duration

            with wave.open(str(silent_path), "w") as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                for _ in range(num_samples):
                    wav_file.writeframes(struct.pack("<hh", 0, 0))

            return str(silent_path)

    async def _generate_music(
        self,
        prompt: str,
        product: str,
        duration: int,
    ) -> Optional[str]:
        """
        Generate music using Lyria (PLACEHOLDER - implement when ready).

        This method will:
        1. Initialize Lyria model
        2. Send generation request
        3. Wait for completion (~10-30 seconds)
        4. Download audio file
        5. Save as WAV

        Returns:
            Path to generated audio file
        """

        # Initialize model if needed
        if not self.model and not self._initialize_lyria():
            raise Exception("Lyria not available")

        try:
            print(f"\n   🎵 Generating {duration}s music with Lyria...")
            print(f"   ⏱️  This may take 10-30 seconds...")

            # TODO: Replace with actual Lyria API call
            # Example structure (API not finalized):
            # response = await self.model.generate_music(
            #     prompt=prompt,
            #     duration_seconds=duration,
            #     sample_rate=48000,
            #     output_format="wav",
            # )
            #
            # audio_data = response.audio_data
            #
            # # Save audio
            # safe_product = product.replace(" ", "_")[:20]
            # filename = f"{safe_product}_music_{duration}s.wav"
            # audio_path = self.output_dir / filename
            #
            # with open(audio_path, "wb") as f:
            #     f.write(audio_data)
            #
            # print(f"   ✅ Music saved: {audio_path}")
            # return str(audio_path)

            # Placeholder
            raise NotImplementedError("Lyria API calls not yet implemented")

        except Exception as e:
            print(f"   ❌ Lyria generation failed: {e}")
            return None


# ============================================================
# MUSIC STYLE PRESETS
# ============================================================

# Pre-defined music styles for common use cases
MUSIC_PRESETS = {
    "viral_tiktok": {
        "genre": "upbeat electronic pop",
        "tempo": "fast 130-140 BPM",
        "energy": "high energy, attention-grabbing",
        "description": "Trendy TikTok-style background music",
    },
    "product_showcase": {
        "genre": "modern commercial",
        "tempo": "moderate 110-120 BPM",
        "energy": "confident and polished",
        "description": "Professional product demonstration music",
    },
    "food_lifestyle": {
        "genre": "bright acoustic",
        "tempo": "upbeat 115-125 BPM",
        "energy": "warm and inviting",
        "description": "Perfect for food and lifestyle content",
    },
    "tech_startup": {
        "genre": "minimal electronic",
        "tempo": "medium 100-110 BPM",
        "energy": "modern and innovative",
        "description": "Clean, futuristic tech vibes",
    },
    "inspirational": {
        "genre": "cinematic motivational",
        "tempo": "building 80-120 BPM",
        "energy": "emotional and uplifting",
        "description": "Inspiring, feel-good soundtrack",
    },
}
