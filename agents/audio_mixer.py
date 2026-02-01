"""
Audio Mixer Agent

Downloads royalty-free music and combines it with voiceover to create final audio track.
"""

import os
import re
from pathlib import Path

import requests
from pydub import AudioSegment


class AudioMixerAgent:
    """Downloads music and mixes it with voiceover."""

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
        Download music and mix with voiceover.

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
            # Get voiceover and music data
            voiceover_data = previous_results.get("voiceover", {})
            music_data = previous_results.get("music", {})

            voiceover_path = voiceover_data.get("audio_path")
            if not voiceover_path or not os.path.exists(voiceover_path):
                return {
                    "error": "No voiceover file found",
                    "skipped": True,
                }

            print(f"\n  🎵 Downloading background music...")
            
            # Get music URL and attribution
            music_url, attribution = self._get_music_url(music_data)
            
            # Download music
            music_path = self._download_music(music_url, product)
            
            if not music_path:
                return {
                    "error": "Failed to download music",
                    "voiceover_path": voiceover_path,
                }
            
            print(f"  🎛️  Mixing audio (voiceover + background music)...")
            
            # Mix voiceover and music
            mixed_audio_path = self._mix_audio(
                voiceover_path, music_path, product, duration
            )
            
            # Get music recommendations for context
            music_rec = music_data.get("quick_recommendation", {})
            
            return {
                "mixed_audio_path": str(mixed_audio_path),
                "voiceover_path": voiceover_path,
                "music_path": music_path,
                "duration": duration,
                "music_genre": music_rec.get("genre", "Upbeat"),
                "music_bpm": music_rec.get("bpm", "100-120"),
                "music_attribution": attribution,
                "note": "Full audio track ready with voiceover and royalty-free music (CC-BY Kevin MacLeod)",
            }

        except Exception as e:
            return {
                "error": str(e),
                "voiceover_path": previous_results.get("voiceover", {}).get(
                    "audio_path"
                ),
            }

    def _get_music_url(self, music_data: dict) -> tuple[str, str]:
        """
        Get royalty-free music URL from Incompetech (Kevin MacLeod).
        
        Returns: (url, attribution_text)
        """

        # Curated royalty-free music tracks from Incompetech
        # All tracks are CC-BY 4.0 licensed by Kevin MacLeod
        music_library = {
            "upbeat": [
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3", 
                 "Carefree by Kevin MacLeod"),
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Wallpaper.mp3",
                 "Wallpaper by Kevin MacLeod"),
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Inspiring.mp3",
                 "Inspiring by Kevin MacLeod"),
            ],
            "calm": [
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Bliss.mp3",
                 "Bliss by Kevin MacLeod"),
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Calming%20Fires.mp3",
                 "Calming Fires by Kevin MacLeod"),
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Peaceful.mp3",
                 "Peaceful by Kevin MacLeod"),
            ],
            "energetic": [
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Upbeat%20Forever.mp3",
                 "Upbeat Forever by Kevin MacLeod"),
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Breaktime.mp3",
                 "Breaktime by Kevin MacLeod"),
                ("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Happy%20Alley.mp3",
                 "Happy Alley by Kevin MacLeod"),
            ],
        }

        # Get music style from recommendation  
        rec = music_data.get("quick_recommendation", {})
        genre = rec.get("genre", "").lower()

        # Select music based on genre keywords
        if any(word in genre for word in ["upbeat", "energetic", "commercial", "corporate"]):
            url, attribution = music_library["upbeat"][0]
        elif any(word in genre for word in ["calm", "peaceful", "acoustic"]):
            url, attribution = music_library["calm"][0]
        else:
            url, attribution = music_library["upbeat"][0]  # Default
        
        return url, attribution

    def _download_music(self, url: str, product: str) -> str:
        """Download music file from URL."""

        try:
            # Sanitize product name for filename
            safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")
            music_filename = f"music_{safe_product}.mp3"
            music_path = self.output_dir / music_filename

            # Download
            print(f"  📥 Downloading from Incompetech...")
            response = requests.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()

            # Save
            with open(music_path, "wb") as f:
                f.write(response.content)

            file_size = len(response.content) / (1024 * 1024)  # MB
            print(f"  ✅ Downloaded music: {music_path} ({file_size:.1f}MB)")
            return str(music_path)

        except Exception as e:
            print(f"  ⚠️  Failed to download music: {e}")
            return None

    def _mix_audio(
        self, voiceover_path: str, music_path: str, product: str, target_duration: int
    ) -> Path:
        """Mix voiceover and background music."""

        # Load audio files
        voiceover = AudioSegment.from_mp3(voiceover_path)
        music = AudioSegment.from_mp3(music_path)

        # Calculate durations
        voiceover_duration = len(voiceover)  # milliseconds
        target_duration_ms = target_duration * 1000

        # Trim or loop music to match target duration
        if len(music) < target_duration_ms:
            # Loop music if too short
            loops_needed = (target_duration_ms // len(music)) + 1
            music = music * loops_needed

        # Trim music to target duration
        music = music[:target_duration_ms]

        # Reduce music volume to -20dB for background
        music = music - 20  # dB reduction

        # Add fade in/out to music
        music = music.fade_in(2000).fade_out(2000)  # 2 second fades

        # Overlay voiceover on top of music
        # Position voiceover slightly after start (500ms delay)
        mixed = music.overlay(voiceover, position=500)

        # Ensure mixed audio matches target duration
        if len(mixed) > target_duration_ms:
            mixed = mixed[:target_duration_ms]

        # Export mixed audio
        safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")
        output_filename = f"final_audio_{safe_product}_{target_duration}s.mp3"
        output_path = self.output_dir / output_filename

        mixed.export(str(output_path), format="mp3", bitrate="192k")

        print(f"  ✅ Mixed audio created: {output_path}")
        print(f"     - Voiceover: {voiceover_duration / 1000:.1f}s")
        print(f"     - Music (background): {target_duration}s")
        print(f"     - Final: {len(mixed) / 1000:.1f}s")

        return output_path
