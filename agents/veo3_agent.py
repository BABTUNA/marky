"""
VEO 3 Viral Video Generator Agent

Google's VEO 3 generates photorealistic 4K video from text prompts.
Perfect for 15s TikTok/Instagram Reels viral content.

IMPORTANT: VEO 3 generates VIDEO ONLY (no audio)
- Audio must be added separately
- Can use trending sounds, music, or voiceover
- Or leave silent for user to add their own audio

Cost: ~$2.00 per 15s video

TESTING MODE:
- Set USE_PLACEHOLDER=True to use a placeholder video instead of VEO 3
- This allows testing the full pipeline without incurring costs
"""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

# VEO 3 will be available via Vertex AI (same as Imagen)
try:
    import vertexai
    from vertexai.preview.vision_models import VideoGenerationModel

    VEO_AVAILABLE = True
except ImportError:
    VEO_AVAILABLE = False

# TESTING: Set to True to use placeholder video instead of VEO 3
USE_PLACEHOLDER = os.getenv("VEO_USE_PLACEHOLDER", "true").lower() == "true"
PLACEHOLDER_VIDEO_PATH = os.getenv("VEO_PLACEHOLDER_PATH", "")


class VEO3Agent:
    """
    Generates short-form viral videos using Google VEO 3.

    VEO 3 creates photorealistic 4K video perfect for:
    - TikTok (9:16 vertical)
    - Instagram Reels (9:16 vertical)
    - YouTube Shorts (9:16 vertical)

    Note: Video only - no audio generated!
    """

    def __init__(self):
        self.output_dir = Path("output/veo3_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_REGION", "us-central1")

        # VEO 3 configuration
        self.model_name = "veo-3"  # Actual model name TBD by Google
        self.default_duration = 15  # seconds (optimal for social media)
        self.default_aspect_ratio = "9:16"  # Vertical for TikTok/Reels
        self.default_resolution = "1080p"  # or "4k"

        self.model = None

    def _initialize_veo(self):
        """Initialize VEO 3 model (lazy loading)."""
        if not VEO_AVAILABLE:
            print("  ⚠️  VEO 3 not available - vertexai package required")
            return False

        if not self.project_id:
            print("  ⚠️  GCP_PROJECT_ID not set")
            return False

        try:
            vertexai.init(project=self.project_id, location=self.location)
            # This is a placeholder - actual model initialization will depend on Google's API
            # self.model = VideoGenerationModel.from_pretrained("veo-3")
            print(f"  ✅ VEO 3 model ready: {self.model_name}")
            return True
        except Exception as e:
            print(f"  ❌ VEO 3 initialization failed: {e}")
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
        Generate viral short-form video using VEO 3.

        Args:
            product: Product/business name
            industry: Industry type
            tone: Video tone (energetic, calm, professional, etc.)
            duration: Target duration (recommend 15s)
            previous_results: Script and research data

        Returns:
            Dict with video_path, duration, format info
        """

        print("\n🎬 VEO 3 Viral Video Generator")
        print("=" * 60)
        print(f"   Product: {product}")
        print(f"   Duration: {duration}s")
        print(f"   Format: Vertical 9:16 (TikTok/Reels)")
        print("=" * 60)

        # Extract script/hook from previous results
        script_data = previous_results.get("script_writer", {})
        research_data = previous_results.get("research", {})

        # Build VEO 3 prompt
        veo_prompt = self._build_veo_prompt(
            product=product,
            industry=industry,
            tone=tone,
            duration=duration,
            script_data=script_data,
            research_data=research_data,
        )

        print(f"\n📝 VEO 3 Prompt:")
        print(f"   {veo_prompt[:200]}...")

        # PLACEHOLDER MODE: Use existing video for testing pipeline
        if USE_PLACEHOLDER:
            video_path = await self._use_placeholder_video(product, duration)
            if video_path:
                print(f"\n✅ Using PLACEHOLDER video for testing: {video_path}")
                return {
                    "status": "placeholder_mode",
                    "enabled": True,
                    "video_path": video_path,
                    "duration": duration,
                    "format": "9:16 vertical",
                    "resolution": self.default_resolution,
                    "cost_estimate": 0.00,  # No cost for placeholder
                    "note": "PLACEHOLDER MODE - using existing video for pipeline testing",
                    "prompt": veo_prompt,
                }
            else:
                print("\n⚠️  No placeholder video found, falling back to disabled mode")

        # TODO: Uncomment when ready to actually generate
        # video_path = await self._generate_video(veo_prompt, product, duration)

        # For now, return placeholder
        print("\n⏸️  VEO 3 generation DISABLED (groundwork only)")
        print("   To enable: Uncomment generation code in veo3_agent.py")

        return {
            "status": "groundwork_ready",
            "enabled": False,
            "video_path": None,
            "duration": duration,
            "format": "9:16 vertical",
            "resolution": self.default_resolution,
            "cost_estimate": 2.00,
            "note": "VEO 3 infrastructure ready - enable when needed",
            "prompt": veo_prompt,
        }

    def _build_veo_prompt(
        self,
        product: str,
        industry: str,
        tone: str,
        duration: int,
        script_data: dict,
        research_data: dict,
    ) -> str:
        """
        Build optimized prompt for VEO 3 video generation.

        VEO 3 best practices:
        - Clear, concise visual descriptions
        - Specify camera movements
        - Describe lighting and mood
        - Include pacing information
        - Keep under 1000 tokens
        """

        # Get the hook/opening from script
        scenes = script_data.get("scenes", [])
        first_scene = scenes[0] if scenes else {}
        hook_visual = first_scene.get("visual", f"{product} showcase")

        # Get trending insights
        hooks = research_data.get("hooks", [])
        top_hook = hooks[0] if hooks else f"Experience {product}"

        # Build prompt optimized for viral social media
        prompt = f"""15-second vertical video (9:16) for {product} - {industry}

Opening Hook (0-3s): {top_hook}
Visual: {hook_visual}

Style: Photorealistic, cinematic, trendy TikTok/Instagram Reels aesthetic
Mood: {tone}, engaging, scroll-stopping

Camera: Dynamic movement - slow zoom, smooth pan, professional gimbal feel
Lighting: Bright, vibrant, optimized for mobile viewing
Pacing: Fast cuts every 3-5 seconds to maintain attention

Key visual elements:
- Show product/service in action
- Include people/emotions if applicable
- Vibrant colors that pop on mobile screens
- Clear focal point in every shot
- Professional but not corporate

Technical: 4K quality, vertical format, optimized for mobile, no text overlays

Reference style: High-performing TikTok/Reels ads - authentic, engaging, not overly produced"""

        return prompt

    async def _use_placeholder_video(
        self,
        product: str,
        duration: int,
    ) -> Optional[str]:
        """
        Use a placeholder video for testing the pipeline.

        This allows testing the full viral video pipeline (Lyria + TTS + assembly)
        without actually calling VEO 3 (which costs ~$2 per video).

        Will look for:
        1. Custom path specified in VEO_PLACEHOLDER_PATH env var
        2. Existing videos in output/final/ directory
        3. Any .mp4 file it can find

        Returns:
            Path to placeholder video file
        """

        # Option 1: Custom placeholder path from env
        if PLACEHOLDER_VIDEO_PATH and Path(PLACEHOLDER_VIDEO_PATH).exists():
            placeholder_dest = (
                self.output_dir
                / f"{product.replace(' ', '_')}_placeholder_{duration}s.mp4"
            )
            shutil.copy(PLACEHOLDER_VIDEO_PATH, placeholder_dest)
            print(f"   📹 Using custom placeholder: {PLACEHOLDER_VIDEO_PATH}")
            return str(placeholder_dest)

        # Option 2: Look for existing videos in output/final/
        final_dir = Path("output/final")
        if final_dir.exists():
            videos = list(final_dir.glob("*.mp4"))
            if videos:
                # Use the most recently modified one
                videos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                source_video = videos[0]
                placeholder_dest = (
                    self.output_dir
                    / f"{product.replace(' ', '_')}_placeholder_{duration}s.mp4"
                )
                shutil.copy(source_video, placeholder_dest)
                print(f"   📹 Using existing video as placeholder: {source_video.name}")
                return str(placeholder_dest)

        # Option 3: Look in veo3_videos directory for any previous output
        if self.output_dir.exists():
            videos = list(self.output_dir.glob("*.mp4"))
            if videos:
                return str(videos[0])

        print("   ⚠️  No placeholder video found!")
        print("   To fix: Set VEO_PLACEHOLDER_PATH=/path/to/video.mp4")
        print("   Or place a .mp4 file in output/final/")
        return None

    async def _generate_video(
        self,
        prompt: str,
        product: str,
        duration: int,
    ) -> Optional[str]:
        """
        Generate video using VEO 3 (PLACEHOLDER - implement when ready).

        This method will:
        1. Initialize VEO 3 model
        2. Send generation request
        3. Poll for completion (may take 2-5 minutes)
        4. Download generated video
        5. Save to output directory

        Returns:
            Path to generated video file
        """

        # Initialize model if needed
        if not self.model and not self._initialize_veo():
            raise Exception("VEO 3 not available")

        try:
            print(f"\n   🎬 Generating {duration}s video with VEO 3...")
            print(f"   ⏱️  This may take 2-5 minutes...")

            # TODO: Replace with actual VEO 3 API call
            # Example structure (API not finalized):
            # response = await self.model.generate_video(
            #     prompt=prompt,
            #     duration_seconds=duration,
            #     aspect_ratio="9:16",
            #     resolution="1080p",
            #     fps=30,
            # )
            #
            # # Poll for completion
            # video_data = await self._wait_for_completion(response.operation_id)
            #
            # # Save video
            # safe_product = product.replace(" ", "_")[:20]
            # filename = f"{safe_product}_viral_{duration}s.mp4"
            # video_path = self.output_dir / filename
            #
            # with open(video_path, "wb") as f:
            #     f.write(video_data)
            #
            # print(f"   ✅ Video saved: {video_path}")
            # return str(video_path)

            # Placeholder
            raise NotImplementedError("VEO 3 API calls not yet implemented")

        except Exception as e:
            print(f"   ❌ VEO 3 generation failed: {e}")
            return None

    async def _wait_for_completion(
        self, operation_id: str, timeout: int = 600
    ) -> bytes:
        """
        Poll VEO 3 for video completion (videos take time to generate).

        Args:
            operation_id: VEO 3 operation ID
            timeout: Max wait time in seconds (default 10 minutes)

        Returns:
            Video data bytes
        """
        # TODO: Implement polling logic
        # VEO 3 videos take 2-5 minutes to generate
        # Need to poll every 10-30 seconds
        pass


# ============================================================
# AUDIO INTEGRATION (VEO 3 has no audio!)
# ============================================================


async def add_trending_audio_to_veo_video(
    video_path: str,
    audio_choice: str = "trending_tiktok",
) -> str:
    """
    Add audio to VEO 3 generated video.

    Options:
    - "trending_tiktok" - Use popular TikTok sound
    - "background_music" - Generic background music
    - "voiceover" - AI-generated voiceover
    - "silent" - No audio

    Returns:
        Path to video with audio
    """
    # TODO: Implement audio mixing
    # Can use moviepy or ffmpeg to add audio track
    pass
