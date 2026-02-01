"""
Viral Video Assembly Agent

Combines VEO 3 video + Lyria music + Google TTS voiceover into
one complete viral-ready video.

Pipeline:
1. VEO 3 generates silent video (15s)
2. Lyria generates background music (15s)
3. Google TTS generates voiceover narration (15s)
4. Mix music + voiceover into single audio track
5. Merge video + audio → Final viral video

Output: Ready-to-upload TikTok/Reels video with complete audio

TESTING MODE:
- Set ASSEMBLER_USE_MOCK=true to skip actual assembly and return mock paths
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Movie editing library - supports both moviepy v1 and v2
try:
    # Try moviepy v2 imports first
    from moviepy import AudioFileClip, VideoFileClip
    from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips

    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        # Fall back to moviepy v1 imports
        from moviepy.editor import (
            AudioFileClip,
            CompositeAudioClip,
            VideoFileClip,
            concatenate_audioclips,
        )

        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False

# Google TTS
try:
    from google.cloud import texttospeech

    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Testing flags
ASSEMBLER_USE_MOCK = os.getenv("ASSEMBLER_USE_MOCK", "false").lower() == "true"


class ViralVideoAssembler:
    """
    Assembles complete viral video with VEO 3 + Lyria + TTS.

    This is the final step that combines:
    - VEO 3 photorealistic video (silent)
    - Lyria background music
    - Google TTS voiceover

    Into one ready-to-post viral video.
    """

    def __init__(self):
        self.output_dir = Path("output/viral_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.project_id = os.getenv("GCP_PROJECT_ID")

    async def run(
        self,
        product: str,
        duration: int,
        previous_results: dict,
        industry: str = "",  # Accept but not used
        tone: str = "",  # Accept but not used
        city: str = "",  # Accept but not used
        **kwargs,  # Accept any other params
    ) -> Dict[str, Any]:
        """
        Assemble complete viral video with audio.

        Args:
            product: Product name
            duration: Video duration (15s recommended)
            previous_results: Contains veo3_video, lyria_music paths

        Returns:
            Dict with final_video_path and metadata
        """

        print("\n🎬 Viral Video Assembly Agent")
        print("=" * 60)
        print("   Combining: VEO 3 video + Lyria music + TTS voiceover")
        print("=" * 60)

        # Extract component paths from previous agents
        veo3_data = previous_results.get("veo3_generator", {})
        lyria_data = previous_results.get("lyria_music", {})
        script_data = previous_results.get("script_writer", {})

        video_path = veo3_data.get("video_path")
        music_path = lyria_data.get("audio_path")

        # Check if we have the components we need
        print(f"\n   📹 Video path: {video_path}")
        print(f"   🎵 Music path: {music_path}")

        if not video_path:
            print("   ⚠️  No video available - cannot assemble")
            return {
                "status": "missing_video",
                "enabled": False,
                "final_video_path": None,
                "error": "VEO 3 video not available",
            }

        # Generate voiceover from script
        # Priority: 1) Existing voiceover from voiceover agent, 2) Google TTS
        voiceover_path = None

        existing_voiceover = previous_results.get("voiceover", {})
        if existing_voiceover.get("audio_path"):
            voiceover_path = existing_voiceover.get("audio_path")
            print(f"   🎤 Using existing voiceover: {voiceover_path}")
        else:
            narration_text = self._extract_narration(script_data, product)
            if TTS_AVAILABLE:
                voiceover_path = await self._google_tts_generate(
                    text=narration_text,
                    product=product,
                    tone=tone,
                )

        print(f"   🎤 Voiceover path: {voiceover_path}")

        # Merge everything
        final_video = await self._assemble_video(
            video_path=video_path,
            music_path=music_path,
            voiceover_path=voiceover_path,
            product=product,
            duration=duration,
        )

        if final_video:
            return {
                "status": "assembled",
                "enabled": True,
                "final_video_path": final_video,
                "duration": duration,
                "format": "mp4",
                "has_audio": bool(music_path or voiceover_path),
                "audio_components": [
                    c
                    for c in [
                        "lyria_music" if music_path else None,
                        "google_tts_voiceover" if voiceover_path else None,
                    ]
                    if c
                ],
                "note": "Viral video assembled successfully!",
            }
        else:
            return {
                "status": "assembly_failed",
                "enabled": False,
                "final_video_path": None,
                "duration": duration,
                "format": "mp4",
                "has_audio": False,
                "error": "Video assembly failed - check moviepy installation",
            }

    def _extract_narration(self, script_data: dict, product: str) -> str:
        """
        Extract narration text from script data.

        Args:
            script_data: Script from script_writer agent
            product: Product name for fallback text

        Returns:
            Narration text string
        """
        # Use voiceover_text if available, otherwise build from scenes
        narration_text = script_data.get("voiceover_text", "")

        if not narration_text:
            scenes = script_data.get("scenes", [])
            narration_parts = []
            for scene in scenes:
                voiceover = scene.get("voiceover", "") or scene.get("narration", "")
                if voiceover and voiceover not in [
                    "[Background music only]",
                    "[Music only]",
                ]:
                    narration_parts.append(voiceover)
            narration_text = " ".join(narration_parts)

        if not narration_text:
            narration_text = f"Discover {product}. Experience the difference today."

        # Clean up text for TTS
        import re

        narration_text = re.sub(
            r"\[.*?\]", "", narration_text
        )  # Remove [stage directions]
        narration_text = re.sub(
            r"\(.*?\)", "", narration_text
        )  # Remove (parentheticals)
        narration_text = re.sub(
            r"\*+", "", narration_text
        )  # Remove asterisks (TTS reads them)
        narration_text = re.sub(
            r"\s+", " ", narration_text
        ).strip()  # Normalize whitespace

        # Truncate if too long (Google TTS has limits)
        if len(narration_text) > 5000:
            narration_text = narration_text[:5000]

        return narration_text

    def _prepare_ssml(self, text: str, tone: str) -> str:
        """
        Convert plain text to SSML for more natural speech.

        Adds pauses, emphasis, and pacing adjustments.
        """
        import re

        # Clean up text
        text = text.strip()

        # Add pauses after sentences
        text = re.sub(r"\.(\s+)", r'.<break time="300ms"/>\1', text)

        # Add shorter pauses after commas
        text = re.sub(r",(\s+)", r',<break time="150ms"/>\1', text)

        # Add pauses after ellipses for dramatic effect
        text = re.sub(r"\.\.\.", r'<break time="400ms"/>', text)

        # Add emphasis to questions
        text = re.sub(r"\?(\s+)", r'?<break time="250ms"/>\1', text)

        # Wrap in SSML with prosody (rate only - Studio voices don't support pitch)
        prosody_settings = {
            "professional": 'rate="95%"',
            "friendly": 'rate="100%"',
            "energetic": 'rate="105%"',
            "calm": 'rate="90%"',
            "funny": 'rate="102%"',
        }

        prosody = prosody_settings.get(tone.lower(), 'rate="97%"')

        ssml = f"<speak><prosody {prosody}>{text}</prosody></speak>"
        return ssml

    async def _google_tts_generate(
        self,
        text: str,
        product: str,
        tone: str = "professional",
    ) -> str:
        """
        Generate speech using Google Cloud Text-to-Speech.

        Uses Studio voices (highest quality) with SSML for natural pacing.
        Falls back to Wavenet if Studio unavailable.

        Returns:
            Path to generated audio file
        """

        if not TTS_AVAILABLE:
            print("   ⚠️  google-cloud-texttospeech not installed")
            print("   💡 Install with: pip install google-cloud-texttospeech")
            return None

        try:
            print("\n   🎤 Generating voiceover with Google TTS...")

            client = texttospeech.TextToSpeechClient()

            # Convert text to SSML for more natural speech
            ssml_text = self._prepare_ssml(text, tone)
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

            # Voice priority: Studio > Wavenet > Neural2
            # Studio voices are the most natural sounding
            # Casual-K is very conversational
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

            # Audio configuration
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.05,  # Slightly faster for engaging content
                pitch=0.0,
            )

            print(f"   📝 Text: {text[:80]}...")
            print(f"   🎙️ Voice: {voice_name}")

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            # Save audio
            safe_product = product.replace(" ", "_").replace("/", "_")[:20]
            output_path = self.output_dir / f"{safe_product}_voiceover.mp3"

            with open(output_path, "wb") as f:
                f.write(response.audio_content)

            print(f"   ✅ Voiceover saved: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"   ❌ Google TTS generation failed: {e}")
            return None

    async def _assemble_video(
        self,
        video_path: Optional[str],
        music_path: Optional[str],
        voiceover_path: Optional[str],
        product: str,
        duration: int = 15,
    ) -> Optional[str]:
        """
        Merge video + music + voiceover into final viral video.

        Steps:
        1. Load VEO 3 video (silent)
        2. Load Lyria music
        3. Load TTS voiceover
        4. Mix music + voiceover (music at 30% volume when voiceover plays)
        5. Add mixed audio to video
        6. Export final video

        Args:
            video_path: Path to VEO 3 video
            music_path: Path to Lyria music
            voiceover_path: Path to TTS voiceover
            product: Product name for filename
            duration: Target duration in seconds

        Returns:
            Path to final video with complete audio
        """

        print("\n   🎬 Assembling final viral video...")

        if not MOVIEPY_AVAILABLE:
            print("   ⚠️  moviepy not installed - cannot merge video/audio")
            print("   💡 Install with: pip install moviepy")
            return None

        if not video_path:
            print("   ⚠️  No video path provided - cannot assemble")
            return None

        if not os.path.exists(video_path):
            print(f"   ⚠️  Video file not found: {video_path}")
            return None

        try:
            # Load video
            print(f"   📹 Loading video: {video_path}")
            video = VideoFileClip(video_path)

            # Track audio clips to mix
            audio_clips = []

            # Helper for moviepy v1/v2 compatibility
            def clip_subclip(clip, start, end):
                """Handle subclip for both moviepy v1 and v2."""
                if hasattr(clip, "subclipped"):
                    return clip.subclipped(start, end)  # moviepy v2
                return clip.subclip(start, end)  # moviepy v1

            def clip_volume(clip, vol):
                """Handle volume for both moviepy v1 and v2."""
                if hasattr(clip, "with_volume_scaled"):
                    return clip.with_volume_scaled(vol)  # moviepy v2
                return clip.volumex(vol)  # moviepy v1

            # Load music if available
            if music_path and os.path.exists(music_path):
                print(f"   🎵 Loading music: {music_path}")
                music = AudioFileClip(music_path)

                # Trim/loop music to match video duration
                if music.duration > video.duration:
                    music = clip_subclip(music, 0, video.duration)
                elif music.duration < video.duration:
                    # Loop music to fill duration
                    loops_needed = int(video.duration / music.duration) + 1
                    music = clip_subclip(
                        concatenate_audioclips([music] * loops_needed),
                        0,
                        video.duration,
                    )

                # Reduce music volume if voiceover present (ducking)
                if voiceover_path:
                    music = clip_volume(
                        music, 0.25
                    )  # 25% volume when voiceover present
                else:
                    music = clip_volume(music, 0.7)  # 70% volume when music only

                audio_clips.append(music)

            # Load voiceover if available
            if voiceover_path and os.path.exists(voiceover_path):
                print(f"   🎤 Loading voiceover: {voiceover_path}")
                voiceover = AudioFileClip(voiceover_path)

                # Trim voiceover if longer than video
                if voiceover.duration > video.duration:
                    voiceover = clip_subclip(voiceover, 0, video.duration)

                audio_clips.append(voiceover)

            # Combine audio if we have any
            if audio_clips:
                print(f"   🔊 Mixing {len(audio_clips)} audio track(s)...")
                if len(audio_clips) == 1:
                    final_audio = audio_clips[0]
                else:
                    final_audio = CompositeAudioClip(audio_clips)

                # Set audio on video (moviepy v1/v2 compatible)
                if hasattr(video, "with_audio"):
                    video_with_audio = video.with_audio(final_audio)  # moviepy v2
                else:
                    video_with_audio = video.set_audio(final_audio)  # moviepy v1
            else:
                print("   ⚠️  No audio available - video will be silent")
                video_with_audio = video

            # Export final video
            safe_product = product.replace(" ", "_").replace("/", "_")[:20]
            output_path = self.output_dir / f"{safe_product}_viral_{duration}s.mp4"

            print(f"   💾 Exporting to: {output_path}")
            print(f"   ⏱️  This may take a moment...")

            # Write video file (moviepy v1/v2 compatible)
            write_kwargs = {
                "codec": "libx264",
                "audio_codec": "aac",
                "fps": 30,
            }
            # moviepy v1 uses verbose/logger, v2 doesn't
            try:
                video_with_audio.write_videofile(
                    str(output_path),
                    **write_kwargs,
                    verbose=False,
                    logger=None,
                )
            except TypeError:
                # moviepy v2 - simpler interface
                video_with_audio.write_videofile(
                    str(output_path),
                    **write_kwargs,
                )

            # Clean up
            video.close()
            for clip in audio_clips:
                clip.close()

            print(f"   ✅ Final video saved: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"   ❌ Video assembly failed: {e}")
            import traceback

            traceback.print_exc()
            return None


# ============================================================
# AUDIO MIXING UTILITIES
# ============================================================


def mix_audio_tracks(
    music_path: str,
    voiceover_path: str,
    output_path: str,
    music_volume: float = 0.3,
) -> str:
    """
    Mix Lyria music + TTS voiceover into single audio track.

    Args:
        music_path: Path to Lyria music (WAV)
        voiceover_path: Path to TTS voiceover (MP3)
        output_path: Where to save mixed audio
        music_volume: Music volume level (0.0-1.0) when voiceover plays

    Returns:
        Path to mixed audio file
    """
    # TODO: Implement audio mixing
    # Can use pydub or moviepy
    pass


def duck_music_for_voiceover(
    music_clip: "AudioFileClip",
    voiceover_clip: "AudioFileClip",
    duck_amount: float = 0.3,
) -> "AudioFileClip":
    """
    Apply audio ducking - lower music volume when voiceover is speaking.

    This creates professional-sounding audio where the music
    doesn't compete with the narration.

    Args:
        music_clip: Background music clip
        voiceover_clip: Voiceover clip
        duck_amount: How much to reduce music (0.3 = 70% reduction)

    Returns:
        Music clip with ducking applied
    """
    # TODO: Implement ducking algorithm
    # Detect when voiceover has audio
    # Lower music volume during those sections
    pass
