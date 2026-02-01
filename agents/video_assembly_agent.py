"""
Video Assembly Agent

Combines video or images with audio (voiceover + optional music) into final MP4 using FFmpeg.

Supports three modes:
1. Image frames → Ken Burns storyboard
2. Video clips → concatenate
3. Sample video → use STORYBOARD_VIDEO_PATH or VEO_PLACEHOLDER_PATH as storyboard (when no frames)
"""

import os
import re
import shutil
from pathlib import Path
import subprocess

STORYBOARD_VIDEO_PATH = os.getenv("STORYBOARD_VIDEO_PATH", "")
VEO_PLACEHOLDER_PATH = os.getenv("VEO_PLACEHOLDER_PATH", "")


class VideoAssemblyAgent:
    """Assembles final video using FFmpeg."""

    def __init__(self):
        """Initialize video assembly agent."""
        self.output_dir = Path("output/final")
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
        Assemble final video from components.
        
        Supports two modes:
        1. Video clips from Veo agent
        2. Image frames from image_generator (storyboard mode)
        
        Args:
            product: Product name
            industry: Industry
            duration: Target duration
            tone: Ad tone
            city: City
            previous_results: Results from previous agents
        
        Returns:
            dict with final video path and metadata
        """
        
        # Get component paths
        veo_data = previous_results.get("veo", {})
        image_data = previous_results.get("image_generator", {})
        voiceover_data = previous_results.get("voiceover", {})
        audio_mixer_data = previous_results.get("audio_mixer", {})
        music_data = previous_results.get("music", {}) or previous_results.get("lyria_music", {})
        
        video_clips = veo_data.get("video_clips", [])
        image_frames = image_data.get("frames", [])
        voiceover_path = voiceover_data.get("audio_path")
        mixed_audio_path = audio_mixer_data.get("mixed_audio_path")
        music_path = music_data.get("music_path") or music_data.get("audio_path")
        
        # Determine mode: sample (when env set), video, or storyboard (from images)
        mode = None
        sample_video_path = None
        if STORYBOARD_VIDEO_PATH and Path(STORYBOARD_VIDEO_PATH).exists():
            mode = "sample"
            sample_video_path = STORYBOARD_VIDEO_PATH
        elif VEO_PLACEHOLDER_PATH and Path(VEO_PLACEHOLDER_PATH).exists():
            mode = "sample"
            sample_video_path = VEO_PLACEHOLDER_PATH
        elif video_clips:
            mode = "video"
        elif image_frames:
            mode = "storyboard"

        if not mode:
            return {
                "error": "No video clips, image frames, or STORYBOARD_VIDEO_PATH available",
                "skipped": True,
            }
        
        # Determine audio source (prioritize mixed, then voiceover, then music-only)
        audio_path = mixed_audio_path or voiceover_path or music_path
        audio_type = "mixed" if mixed_audio_path else ("voiceover" if voiceover_path else ("music-only" if music_path else "silent"))
        
        print(f"\n🎬 Video Assembly Agent - {mode.upper()} Mode")
        if mode == "sample":
            print(f"   Source: sample video ({sample_video_path})")
        else:
            print(f"   {'Video Clips' if mode == 'video' else 'Image Frames'}: {len(video_clips) if mode == 'video' else len(image_frames)}")
        print(f"   Audio: {audio_type}")

        try:
            if mode == "sample":
                # Use sample video as storyboard (will add audio if available)
                safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")
                video_path = self.output_dir / f"{safe_product}_storyboard_{duration}s.mp4"
                shutil.copy(sample_video_path, video_path)
                print(f"\n   📹 Using sample video as storyboard: {video_path.name}")
            elif mode == "storyboard":
                # Convert images to video with Ken Burns effects
                print(f"\n   🖼️  Step 1: Converting {len(image_frames)} images to video with Ken Burns effects...")
                video_path = await self._create_video_from_images(image_frames, product, duration)
            elif mode == "video":
                # Concatenate video clips
                print(f"\n   📹 Step 1: Concatenating {len(video_clips)} video clips...")
                video_path = await self._concatenate_videos(video_clips, product)

            # Step 2: Add audio if available (storyboard gets TTS + music)
            if audio_path:
                print(f"   🎵 Step 2: Adding audio track...")
                final_video = await self._add_audio_to_video(
                    video_path, audio_path, product, duration
                )
            else:
                print(f"   🔇 Step 2: Creating silent video (no audio)")
                final_video = video_path
            
            print(f"\n   ✅ Final video created: {final_video}")
            
            return {
                "final_video_path": str(final_video),
                "duration": duration,
                "mode": mode,
                "frames_used": len(image_frames) if mode == "storyboard" else len(video_clips),
                "audio_source": audio_type,
                "note": f"Complete {mode} video with {audio_type} audio ready for distribution",
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "note": "Video assembly failed - check FFmpeg installation",
            }


    async def _concatenate_videos(
        self, video_clips: list, product: str
    ) -> Path:
        """
        Concatenate multiple video clips into one.
        
        Args:
            video_clips: List of video clip dicts with paths
            product: Product name for filename
        
        Returns:
            Path to concatenated video
        """
        
        # Create concat list file for FFmpeg
        concat_list_path = self.output_dir / "concat_list.txt"
        with open(concat_list_path, "w") as f:
            for clip in video_clips:
                video_path = clip["video_path"]
                f.write(f"file '{os.path.abspath(video_path)}'\n")
        
        # Output path
        safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")
        output_path = self.output_dir / f"concatenated_{safe_product}.mp4"
        
        # FFmpeg command to concatenate
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_path),
            "-c", "copy",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"      ✓ Concatenated video: {output_path}")
        
        return output_path

    async def _create_video_from_images(
        self, image_frames: list, product: str, total_duration: int
    ) -> Path:
        """
        Create video from storyboard images with Ken Burns effects.
        
        Args:
            image_frames: List of image frame dicts with paths
            product: Product name for filename
            total_duration: Total duration to aim for
        
        Returns:
            Path to assembled video
        """
        
        # Create temp directory for clips
        temp_dir = self.output_dir / "temp_clips"
        temp_dir.mkdir(exist_ok=True)
        
        video_clips = []
        
        # Calculate duration per frame
        duration_per_frame = total_duration / len(image_frames)
        
        for i, frame in enumerate(image_frames, 1):
            image_path = frame.get("path") or frame.get("image_path")
            
            if not image_path or not os.path.exists(image_path):
                print(f"      ⚠️  Skipping frame {i} - image not found: {image_path}")
                continue
            
            frame_duration = duration_per_frame
            
            # Create video clip with Ken Burns effect
            clip_path = temp_dir / f"clip_{i:02d}.mp4"
            
            # Ken Burns parameters (vary by scene for visual interest)
            if i % 3 == 1:
                # Zoom in
                zoom_effect = "zoompan=z='min(zoom+0.002,1.3)':d={}:s=1920x1080".format(
                    int(frame_duration * 25)  # 25 fps
                )
            elif i % 3 == 2:
                # Zoom out
                zoom_effect = "zoompan=z='if(lte(zoom,1.0),1.3,max(1.0,zoom-0.002))':d={}:s=1920x1080".format(
                    int(frame_duration * 25)
                )
            else:
                # Pan left to right
                zoom_effect = "zoompan=z='1.2':x='iw/2-(iw/zoom/2)+((iw-iw/zoom)/{})*on':d={}:s=1920x1080".format(
                    int(frame_duration * 25),
                    int(frame_duration * 25)
                )
            
            
            # FFmpeg command to create video from image
            # Use scale with padding to avoid gray bars
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(image_path),
                "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,{zoom_effect},fade=t=in:st=0:d=0.5,fade=t=out:st={frame_duration-0.5}:d=0.5",
                "-t", str(frame_duration),
                "-r", "25",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(clip_path)
            ]

            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                video_clips.append({"video_path": str(clip_path)})
                print(f"      ✓ Created clip {i}/{len(image_frames)} ({frame_duration:.1f}s)")
            except subprocess.CalledProcessError as e:
                print(f"      ⚠️  Failed to create clip {i}: {e}")
        
        if not video_clips:
            raise Exception("Failed to create any video clips from images")
        
        # Concatenate all clips
        concat_list_path = temp_dir / "concat_list.txt"
        with open(concat_list_path, "w") as f:
            for clip in video_clips:
                f.write(f"file '{os.path.abspath(clip['video_path'])}'\n")
        
        # Output path
        safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")
        output_path = self.output_dir / f"storyboard_{safe_product}.mp4"
        
        # FFmpeg command to concatenate
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_path),
            "-c", "copy",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"      ✓ Assembled storyboard video: {output_path}")
        
        return output_path

    async def _add_audio_to_video(
        self, video_path: Path, audio_path: str, product: str, duration: int
    ) -> Path:
        """
        Add audio track to video.
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file (voiceover or mixed)
            product: Product name for filename
            duration: Target duration in seconds
        
        Returns:
            Path to final video with audio
        """
        
        # Output path
        safe_product = re.sub(r"[^\w\s-]", "", product).strip().replace(" ", "_")
        output_path = self.output_dir / f"final_{safe_product}_{duration}s.mp4"
        
        # FFmpeg command to add audio
        # Replace video's audio with our audio, trim to exact duration
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", audio_path,
            "-c:v", "copy",  # Copy video stream as-is
            "-c:a", "aac",   # Encode audio to AAC
            "-b:a", "192k",  # Audio bitrate
            "-map", "0:v:0", # Use video from first input
            "-map", "1:a:0", # Use audio from second input
            "-t", str(duration),  # Trim to exact duration
            "-shortest",  # End when shortest stream ends
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"      ✓ Final video with audio: {output_path}")
        
        # Get file size
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"      📦 File size: {file_size:.1f}MB")
        
        return output_path
