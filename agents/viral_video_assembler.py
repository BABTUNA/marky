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
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Movie editing library
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

# Google TTS
try:
    from google.cloud import texttospeech
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


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
        
        # Generate voiceover from script
        voiceover_path = await self._generate_voiceover(
            script_data=script_data,
            duration=duration,
            product=product,
        )
        
        # Merge everything
        final_video = await self._assemble_video(
            video_path=video_path,
            music_path=music_path,
            voiceover_path=voiceover_path,
            product=product,
        )
        
        return {
            "status": "groundwork_ready",
            "enabled": False,
            "final_video_path": final_video,
            "duration": duration,
            "format": "mp4",
            "has_audio": True,
            "audio_components": ["lyria_music", "google_tts_voiceover"],
            "note": "Video assembly infrastructure ready",
        }
    
    async def _generate_voiceover(
        self,
        script_data: dict,
        duration: int,
        product: str,
    ) -> Optional[str]:
        """
        Generate voiceover narration using Google TTS.
        
        Extracts the script/hook text and converts to speech.
        Uses Google Cloud Text-to-Speech (free tier available).
        
        Args:
            script_data: Script from script_writer agent
            duration: Target duration
            product: Product name for filename
        
        Returns:
            Path to voiceover audio file
        """
        
        print("\n   🎤 Generating voiceover with Google TTS...")
        
        # Extract narration text from script
        scenes = script_data.get("scenes", [])
        
        # For 15s viral video, use first scene + hook
        narration_parts = []
        for scene in scenes[:2]:  # First 2 scenes for 15s
            narration = scene.get("narration", "")
            if narration and narration != "[Background music only]":
                narration_parts.append(narration)
        
        narration_text = " ".join(narration_parts)
        
        if not narration_text:
            print("   ⚠️  No narration found - using product name as voiceover")
            narration_text = f"Discover {product}. Experience the difference."
        
        print(f"   📝 Narration: {narration_text[:100]}...")
        
        # TODO: Uncomment when ready to generate
        # return await self._google_tts_generate(narration_text, product)
        
        # Placeholder
        print("   ⏸️  TTS generation DISABLED (groundwork only)")
        return None
    
    async def _google_tts_generate(
        self,
        text: str,
        product: str,
    ) -> str:
        """
        Generate speech using Google Cloud Text-to-Speech.
        
        PLACEHOLDER - Implement when ready.
        
        Google TTS Features:
        - Natural sounding voices
        - Multiple languages
        - Voice styles (news, conversational, etc.)
        - Free tier: 1M characters/month
        
        Returns:
            Path to generated audio file
        """
        
        if not TTS_AVAILABLE:
            raise ImportError("google-cloud-texttospeech not installed")
        
        try:
            # TODO: Replace with actual Google TTS API call
            # Example structure:
            # 
            # client = texttospeech.TextToSpeechClient()
            # 
            # synthesis_input = texttospeech.SynthesisInput(text=text)
            # 
            # # Voice configuration - use natural sounding voice
            # voice = texttospeech.VoiceSelectionParams(
            #     language_code="en-US",
            #     name="en-US-Neural2-J",  # Male voice, or Neural2-F for female
            #     ssml_gender=texttospeech.SsmlVoiceGender.MALE
            # )
            # 
            # audio_config = texttospeech.AudioConfig(
            #     audio_encoding=texttospeech.AudioEncoding.MP3,
            #     speaking_rate=1.1,  # Slightly faster for viral content
            #     pitch=0.0,
            # )
            # 
            # response = client.synthesize_speech(
            #     input=synthesis_input,
            #     voice=voice,
            #     audio_config=audio_config
            # )
            # 
            # # Save audio
            # safe_product = product.replace(" ", "_")[:20]
            # output_path = self.output_dir / f"{safe_product}_voiceover.mp3"
            # 
            # with open(output_path, "wb") as f:
            #     f.write(response.audio_content)
            # 
            # print(f"   ✅ Voiceover saved: {output_path}")
            # return str(output_path)
            
            raise NotImplementedError("Google TTS not yet implemented")
            
        except Exception as e:
            print(f"   ❌ TTS generation failed: {e}")
            return None
    
    async def _assemble_video(
        self,
        video_path: Optional[str],
        music_path: Optional[str],
        voiceover_path: Optional[str],
        product: str,
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
        
        PLACEHOLDER - Implement when ready.
        
        Args:
            video_path: Path to VEO 3 video
            music_path: Path to Lyria music
            voiceover_path: Path to TTS voiceover
            product: Product name for filename
        
        Returns:
            Path to final video with complete audio
        """
        
        print("\n   🎬 Assembling final viral video...")
        
        if not MOVIEPY_AVAILABLE:
            print("   ⚠️  moviepy not installed - cannot merge video/audio")
            return None
        
        if not video_path or not music_path or not voiceover_path:
            print("   ⚠️  Missing components - cannot assemble")
            return None
        
        try:
            # TODO: Replace with actual video assembly
            # Example structure:
            # 
            # # Load video (silent)
            # video = VideoFileClip(video_path)
            # 
            # # Load audio components
            # music = AudioFileClip(music_path)
            # voiceover = AudioFileClip(voiceover_path)
            # 
            # # Reduce music volume when voiceover is playing
            # music_reduced = music.volumex(0.3)  # 30% volume
            # 
            # # Combine audio tracks
            # final_audio = CompositeAudioClip([
            #     music_reduced,
            #     voiceover,
            # ])
            # 
            # # Add audio to video
            # video_with_audio = video.set_audio(final_audio)
            # 
            # # Export final video
            # safe_product = product.replace(" ", "_")[:20]
            # output_path = self.output_dir / f"{safe_product}_viral_15s.mp4"
            # 
            # video_with_audio.write_videofile(
            #     str(output_path),
            #     codec="libx264",
            #     audio_codec="aac",
            #     fps=30,
            #     preset="medium",
            # )
            # 
            # # Clean up
            # video.close()
            # music.close()
            # voiceover.close()
            # 
            # print(f"   ✅ Final video saved: {output_path}")
            # return str(output_path)
            
            print("   ⏸️  Video assembly DISABLED (groundwork only)")
            return None
            
        except Exception as e:
            print(f"   ❌ Video assembly failed: {e}")
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
    music_clip: 'AudioFileClip',
    voiceover_clip: 'AudioFileClip',
    duck_amount: float = 0.3,
) -> 'AudioFileClip':
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
