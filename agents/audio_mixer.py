"""
Audio Mixer Agent

Creates final audio track from voiceover. Background music is optional -
if no music is provided, voiceover is used as-is with fade effects.
"""

import os
import re
from pathlib import Path

from pydub import AudioSegment


class AudioMixerAgent:
    """Creates final audio track from voiceover with optional background music."""

    def __init__(self):
        self.output_dir = Path("output/mixed_audio")
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
        Create final audio track from voiceover.

        Args:
            product: Product name
            industry: Industry
            duration: Target duration
            tone: Ad tone
            city: City
            previous_results: Results from previous agents

        Returns:
            dict with mixed audio file path and metadata
        """

        try:
            # Get voiceover data
            voiceover_data = previous_results.get("voiceover", {})
            music_data = previous_results.get("music", {}) or previous_results.get(
                "lyria_music", {}
            )

            voiceover_path = voiceover_data.get("audio_path")
            if not voiceover_path or not os.path.exists(voiceover_path):
                return {
                    "error": "No voiceover file found",
                    "skipped": True,
                }

            # Check for music (music agent uses music_path, lyria_music uses audio_path)
            music_path = music_data.get("music_path") or music_data.get("audio_path")
            has_music = music_path and os.path.exists(music_path)

            if has_music:
                print(f"\n  🎵 Mixing voiceover with background music...")
                mixed_audio_path = self._mix_with_music(
                    voiceover_path, music_path, product, duration
                )
                music_note = "Voiceover mixed with background music"
            else:
                print(f"\n  🎵 Creating voiceover track (no background music)...")
                mixed_audio_path = self._voiceover_only(
                    voiceover_path, product, duration
                )
                music_note = "Voiceover only - no background music"

            # Get music recommendations for context
            music_rec = music_data.get("quick_recommendation", {})

            return {
                "mixed_audio_path": str(mixed_audio_path),
                "voiceover_path": voiceover_path,
                "music_path": music_path if has_music else None,
                "duration": duration,
                "music_genre": music_rec.get("genre", "None") if has_music else "None",
                "music_bpm": music_rec.get("bpm", "N/A") if has_music else "N/A",
                "note": music_note,
            }

        except Exception as e:
            return {
                "error": str(e),
                "voiceover_path": previous_results.get("voiceover", {}).get(
                    "audio_path"
                ),
            }

    def _voiceover_only(
        self, voiceover_path: str, product: str, target_duration: int
    ) -> Path:
        """Process voiceover with fade effects, no music."""

        voiceover = AudioSegment.from_file(voiceover_path)
        voiceover_duration = len(voiceover)
        target_duration_ms = target_duration * 1000

        # Add fade in/out
        voiceover = voiceover.fade_in(500).fade_out(1000)

        # Trim or pad to match target duration
        if len(voiceover) < target_duration_ms:
            # Add silence padding at end
            silence = AudioSegment.silent(duration=target_duration_ms - len(voiceover))
            voiceover = voiceover + silence
        else:
            # Trim to target duration
            voiceover = voiceover[:target_duration_ms]

        # Export
        safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")
        output_filename = f"final_audio_{safe_product}_{target_duration}s.mp3"
        output_path = self.output_dir / output_filename

        voiceover.export(str(output_path), format="mp3", bitrate="192k")

        print(f"  ✅ Voiceover track created: {output_path}")
        print(f"     - Duration: {len(voiceover) / 1000:.1f}s")

        return output_path

    def _mix_with_music(
        self, voiceover_path: str, music_path: str, product: str, target_duration: int
    ) -> Path:
        """Mix voiceover with background music."""

        voiceover = AudioSegment.from_file(voiceover_path)
        music = AudioSegment.from_file(music_path)

        voiceover_duration = len(voiceover)
        target_duration_ms = target_duration * 1000

        # Loop or trim music to match target duration
        if len(music) < target_duration_ms:
            loops_needed = (target_duration_ms // len(music)) + 1
            music = music * loops_needed

        music = music[:target_duration_ms]

        # Reduce music volume for background (-20dB)
        music = music - 20

        # Add fade in/out to music
        music = music.fade_in(2000).fade_out(2000)

        # Overlay voiceover on music (500ms delay)
        mixed = music.overlay(voiceover, position=500)

        # Ensure final length matches target
        if len(mixed) > target_duration_ms:
            mixed = mixed[:target_duration_ms]

        # Export
        safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")
        output_filename = f"final_audio_{safe_product}_{target_duration}s.mp3"
        output_path = self.output_dir / output_filename

        mixed.export(str(output_path), format="mp3", bitrate="192k")

        print(f"  ✅ Mixed audio created: {output_path}")
        print(f"     - Voiceover: {voiceover_duration / 1000:.1f}s")
        print(f"     - Music (background): {target_duration}s")

        return output_path
