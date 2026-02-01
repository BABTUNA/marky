"""
VEO 3 Viral Video Generator Agent

Google's VEO 3 generates photorealistic video from text prompts.
Perfect for TikTok/Instagram Reels viral content.

IMPORTANT: We set generate_audio=False — audio is added by Lyria + TTS in viral_video_assembler.

Cost: ~$0.50-2.00 per 8s video (depends on resolution)

TESTING MODE:
- Set VEO_USE_PLACEHOLDER=true to use a placeholder video instead of VEO 3
- This allows testing the full pipeline without incurring costs
"""

import asyncio
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, Optional

# google-genai SDK for VEO 3 (Vertex AI)
GOOGLE_GENAI_AVAILABLE = False
genai_client = None
genai_types = None
try:
    from google import genai
    from google.genai import types

    genai_client = genai
    genai_types = types
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    pass

# TESTING: Set to "true" to use placeholder video instead of VEO 3
USE_PLACEHOLDER = os.getenv("VEO_USE_PLACEHOLDER", "true").lower() == "true"
PLACEHOLDER_VIDEO_PATH = os.getenv("VEO_PLACEHOLDER_PATH", "")
# Optional GCS bucket for output (if not set, video_bytes returned — smaller videos only)
VEO_GCS_OUTPUT_URI = os.getenv("VEO_GCS_OUTPUT_URI", "")


class VEO3Agent:
    """
    Generates short-form viral videos using Google VEO 3.

    VEO 3 creates photorealistic video perfect for:
    - TikTok (9:16 vertical)
    - Instagram Reels (9:16 vertical)
    """

    def __init__(self):
        self.output_dir = Path("output/veo3_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GCP_REGION") or os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

        # VEO 3 supports 4, 6, or 8 seconds
        self.veo_duration = 8
        self.model_name = "veo-3.1-generate-001"
        self.model_fast = "veo-3.1-fast-generate-001"
        self.default_aspect_ratio = "9:16"
        self.default_resolution = "1080p"

    def _get_client(self):
        """Create google-genai client for Vertex AI."""
        if not GOOGLE_GENAI_AVAILABLE or not genai_client:
            return None
        if not self.project_id:
            return None
        try:
            return genai_client.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
            )
        except Exception as e:
            print(f"  ⚠️ VEO client init failed: {e}")
            return None

    async def run(
        self,
        product: str,
        industry: str,
        tone: str,
        duration: int,
        previous_results: dict,
        city: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate viral short-form video using VEO 3.

        Returns:
            Dict with video_path, duration, format info
        """
        print("\n🎬 VEO 3 Viral Video Generator")
        print("=" * 60)
        print(f"   Product: {product}")
        print(f"   Format: Vertical 9:16 (TikTok/Reels)")
        print("=" * 60)

        script_data = previous_results.get("script_writer", {})
        research_data = previous_results.get("research", {})

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

        # PLACEHOLDER MODE
        if USE_PLACEHOLDER:
            video_path = await self._use_placeholder_video(product, duration)
            if video_path:
                print(f"\n✅ Using PLACEHOLDER video: {video_path}")
                return {
                    "status": "placeholder_mode",
                    "enabled": True,
                    "video_path": video_path,
                    "duration": self.veo_duration,
                    "format": "9:16 vertical",
                    "resolution": self.default_resolution,
                    "cost_estimate": 0.00,
                    "note": "PLACEHOLDER - set VEO_USE_PLACEHOLDER=false for real VEO 3",
                    "prompt": veo_prompt,
                }
            print("\n⚠️ No placeholder video found")

        # REAL VEO 3
        video_path = await self._generate_video(veo_prompt, product)
        if video_path:
            return {
                "status": "generated",
                "enabled": True,
                "video_path": video_path,
                "duration": self.veo_duration,
                "format": "9:16 vertical",
                "resolution": self.default_resolution,
                "cost_estimate": 1.50,
                "note": "VEO 3 generated",
                "prompt": veo_prompt,
            }

        return {
            "status": "failed",
            "enabled": False,
            "video_path": None,
            "duration": self.veo_duration,
            "error": "VEO 3 generation failed",
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
        scenes = script_data.get("scenes", [])
        first_scene = scenes[0] if scenes else {}
        hook_visual = first_scene.get("visual", f"{product} showcase")
        hooks = research_data.get("insights", {}).get("recommended_hooks", []) or research_data.get("hooks", [])
        top_hook = hooks[0] if hooks else f"Experience {product}"

        return f"""8-second vertical video (9:16) for {product} - {industry}

Opening Hook: {top_hook}
Visual: {hook_visual}

Style: Photorealistic, cinematic, trendy TikTok/Instagram Reels aesthetic
Mood: {tone}, engaging, scroll-stopping

Camera: Dynamic movement - slow zoom, smooth pan, professional gimbal feel
Lighting: Bright, vibrant, optimized for mobile viewing

Key elements: Show product/service in action, vibrant colors, clear focal point.
Reference: High-performing TikTok/Reels ads - authentic, engaging."""

    async def _use_placeholder_video(self, product: str, duration: int) -> Optional[str]:
        # 1) Explicit placeholder path (user-provided)
        if PLACEHOLDER_VIDEO_PATH and Path(PLACEHOLDER_VIDEO_PATH).exists():
            dest = self.output_dir / f"{product.replace(' ', '_')}_placeholder_{duration}s.mp4"
            shutil.copy(PLACEHOLDER_VIDEO_PATH, dest)
            return str(dest)

        # 2) Project default (video_testing sample) — do NOT use output/final (that's the storyboard)
        default_path = Path(__file__).resolve().parent.parent / "video_testing" / "YTDowncom_YouTube_3-Second-Video_Media_1O0yazhqaxs_001_1080p.mp4"
        if default_path.exists():
            dest = self.output_dir / f"{product.replace(' ', '_')}_placeholder_{duration}s.mp4"
            shutil.copy(default_path, dest)
            return str(dest)

        # 3) Existing placeholder in veo3 output from a prior run (not from current storyboard)
        if self.output_dir.exists():
            videos = [p for p in self.output_dir.glob("*.mp4") if "_placeholder_" in p.name]
            if videos:
                videos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                dest = self.output_dir / f"{product.replace(' ', '_')}_placeholder_{duration}s.mp4"
                shutil.copy(videos[0], dest)
                return str(dest)

        return None

    async def _generate_video(self, prompt: str, product: str) -> Optional[str]:
        """Generate video via VEO 3 API. Runs sync client in executor."""
        client = self._get_client()
        if not client or not genai_types:
            print("  ⚠️ VEO 3 not available (google-genai or GCP_PROJECT_ID)")
            return None

        def _run_sync():
            config_kw = {
                "aspect_ratio": self.default_aspect_ratio,
                "number_of_videos": 1,
                "duration_seconds": self.veo_duration,
                "resolution": self.default_resolution,
                "person_generation": "allow_adult",
                "enhance_prompt": True,
                "generate_audio": False,  # We add Lyria + TTS in assembler
            }
            if VEO_GCS_OUTPUT_URI:
                config_kw["output_gcs_uri"] = VEO_GCS_OUTPUT_URI.rstrip("/") + "/"

            config = genai_types.GenerateVideosConfig(**config_kw)
            operation = client.models.generate_videos(
                model=self.model_fast,
                prompt=prompt,
                config=config,
            )
            while not operation.done:
                time.sleep(15)
                operation = client.operations.get(operation)
                print("   ⏳ VEO 3 generating...")

            result = getattr(operation, "result", None) or getattr(operation, "response", None)
            if not result or not getattr(result, "generated_videos", None):
                return None
            gen = result.generated_videos[0]
            video = getattr(gen, "video", None)
            if not video:
                return None
            video_bytes = getattr(video, "video_bytes", None)
            if video_bytes:
                out_path = self.output_dir / f"{product.replace(' ', '_')}_viral_{self.veo_duration}s.mp4"
                with open(out_path, "wb") as f:
                    f.write(video_bytes)
                return str(out_path)
            if getattr(video, "uri", None):
                # GCS output — would need gsutil/gcloud to download
                print(f"   Video at GCS: {video.uri}")
                # TODO: Implement GCS download to local path
                return None
            return None

        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _run_sync)
        except Exception as e:
            print(f"   ❌ VEO 3 generation failed: {e}")
            return None
