"""
Image Generator Agent

Generates storyboard frames for the concept video (part of the development package).
Uses Google Cloud Vertex AI Imagen. Frames are used for both the storyboard concept
video and inform the viral video production.
"""

import asyncio
import base64
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Google Cloud Project ID (required)
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Model options (pricing per image):
# - imagen-4.0-generate-preview-05-20: $0.04/image (high quality)
# - imagen-4.0-fast-generate-preview-05-20: $0.02/image (fast, good quality)
# - imagegeneration@006: Imagen 3 (older but stable)
IMAGEN_MODEL = "imagen-3.0-generate-001"  # Stable model

# Seconds to wait between each Imagen API call (rate limit)
IMAGE_DELAY_SECONDS = int(os.getenv("IMAGEN_DELAY_SECONDS", "45"))


class ImageGeneratorAgent:
    """
    Generates storyboard images using Google Cloud Vertex AI Imagen.

    Pricing: ~$0.02-0.04 per image
    With $410 credits = 10,000-20,000 images!
    """

    def __init__(self):
        self.project_id = GCP_PROJECT_ID
        self.location = GCP_LOCATION
        self.model_name = IMAGEN_MODEL
        self._model = None

    def _init_model(self):
        """Initialize the Imagen model (lazy loading)."""
        if self._model is not None:
            return

        try:
            import vertexai
            from vertexai.preview.vision_models import ImageGenerationModel

            vertexai.init(project=self.project_id, location=self.location)
            self._model = ImageGenerationModel.from_pretrained(self.model_name)
            print(f"  ✅ Initialized Vertex AI Imagen: {self.model_name}")
        except Exception as e:
            print(f"  ❌ Failed to initialize Vertex AI: {e}")
            self._model = None

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
        Generate storyboard frames for each scene.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone
            city: City for context
            previous_results: Results from previous agents (includes script)

        Returns:
            dict with generated frame URLs/paths
        """

        # Get script data
        script_data = previous_results.get("script_writer", {})
        scenes = script_data.get("scenes", [])

        if not scenes:
            return {"error": "No scenes available from script writer"}

        if not self.project_id:
            print("  ⚠️ No GCP_PROJECT_ID set - using placeholder images")
            return await self._generate_placeholders(scenes, product, industry, tone)

        # Initialize model
        self._init_model()

        if self._model is None:
            print("  ⚠️ Imagen model not available - using placeholders")
            return await self._generate_placeholders(scenes, product, industry, tone)

        delay_sec = IMAGE_DELAY_SECONDS
        print(f"  🎨 Using Google Vertex AI Imagen (~$0.02-0.04/image)")
        print(f"  ⏱️  {delay_sec}s between each image (rate limit)")

        frames = []
        for i, scene in enumerate(scenes):
            # Delay before each call after the first (30s between all Imagen requests)
            if i > 0:
                print(f"  ⏳ Waiting {delay_sec}s before next request...")
                await asyncio.sleep(delay_sec)

            print(f"  Generating frame {i + 1}/{len(scenes)} via Imagen...")

            # Build image prompt from scene
            prompt = self._build_image_prompt(
                scene, product, industry, tone, i + 1, len(scenes)
            )

            # Generate image
            image_path, image_b64 = await self._generate_image(prompt, i + 1)

            frames.append(
                {
                    "scene_number": scene.get("scene_number", i + 1),
                    "timing": scene.get("timing", ""),
                    "path": image_path,
                    "image_base64": image_b64[:100] + "..." if image_b64 else None,
                    "prompt_used": prompt[:200] + "..."
                    if len(prompt) > 200
                    else prompt,
                    "description": scene.get("visual", ""),
                    "source": "vertex-imagen" if image_path else "placeholder",
                }
            )

            if image_path:
                print(f"    ✅ Frame {i + 1} saved to: {image_path}")
            else:
                print(f"    ⚠️ Frame {i + 1} failed, using placeholder")

        successful_frames = [f for f in frames if f.get("source") == "vertex-imagen"]

        return {
            "frames": frames,
            "total_generated": len(successful_frames),
            "total_scenes": len(scenes),
            "model": self.model_name,
            "note": f"Generated {len(successful_frames)} images via Vertex AI Imagen",
        }

    async def _generate_image(
        self, prompt: str, frame_num: int
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Generate an image using Vertex AI Imagen.

        Returns:
            Tuple of (file_path, base64_data)
        """
        try:
            # Run in thread pool since vertexai is sync
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio="16:9",
                    safety_filter_level="block_few",
                ),
            )

            if result.images:
                image = result.images[0]

                # Save to output folder
                output_dir = os.path.join(
                    os.path.dirname(__file__), "..", "output", "frames"
                )
                os.makedirs(output_dir, exist_ok=True)

                filename = f"frame_{frame_num}.png"
                filepath = os.path.join(output_dir, filename)

                # Save the image
                image.save(filepath)

                # Also get base64 for PDF embedding
                with open(filepath, "rb") as f:
                    image_b64 = base64.b64encode(f.read()).decode()

                return filepath, image_b64

            return None, None

        except Exception as e:
            print(f"    ❌ Imagen error: {e}")
            return None, None

    async def _generate_placeholders(
        self, scenes: list, product: str, industry: str, tone: str
    ) -> dict:
        """Generate placeholder response when API is not available."""

        frames = []
        for i, scene in enumerate(scenes[:4]):
            prompt = self._build_image_prompt(
                scene, product, industry, tone, i + 1, len(scenes)
            )
            seed = abs(hash(prompt)) % 10000
            frames.append(
                {
                    "scene_number": scene.get("scene_number", i + 1),
                    "timing": scene.get("timing", ""),
                    "url": f"https://picsum.photos/seed/{seed}/1280/720",
                    "prompt_used": prompt[:200] + "...",
                    "description": scene.get("visual", ""),
                    "source": "placeholder",
                }
            )

        return {
            "frames": frames,
            "total_generated": 0,
            "total_scenes": len(scenes),
            "model": "placeholder",
            "note": "Using placeholder images - set GCP_PROJECT_ID for Vertex AI Imagen",
        }

    def _build_image_prompt(
        self,
        scene: dict,
        product: str,
        industry: str,
        tone: str,
        scene_num: int,
        total_scenes: int,
    ) -> str:
        """Build an optimized image generation prompt for storyboard sketches."""

        visual = scene.get("visual", "")

        # Shot type based on scene position
        if scene_num == 1:
            shot = "wide establishing shot"
        elif scene_num == total_scenes:
            shot = "close-up"
        else:
            shot = "medium shot"

        # AUTHENTIC HAND-DRAWN STORYBOARD - Simple, clean, single image
        prompt = f"""{visual}

Black and white pencil drawing. Traditional hand-drawn animation storyboard style.

IMPORTANT. EACH IMAGE GENERATED MUST FOLLOW THESE RULES:
- Single complete scene only (NOT a collage)
- Fill entire image edge to edge
- Rough pencil sketch with visible strokes
- Hand-drawn aesthetic like Disney/Pixar pre-production art
- NO frames, NO borders, NO panels
- NO text, NO labels, NO annotations
- Simple composition showing the scene clearly

Drawing style: Quick animator sketch on paper, authentic hand-made marks, loose confident linework."""

        return prompt


# ============================================================
# ALTERNATIVE: FALLBACK TO POLLINATIONS (FREE, NO API KEY)
# ============================================================


class PollinationsImageGenerator:
    """
    Fallback: Uses Pollinations.ai - completely free, no API key.
    URL-based generation - image is created when URL is accessed.
    """

    import urllib.parse

    def __init__(self):
        self.model = "flux-realism"
        self.width = 1280
        self.height = 720

    async def run(
        self,
        product: str,
        industry: str,
        duration: int,
        tone: str,
        city: str,
        previous_results: dict,
    ) -> dict:
        script_data = previous_results.get("script_writer", {})
        scenes = script_data.get("scenes", [])

        if not scenes:
            return {"error": "No scenes available"}

        frames = []
        for i, scene in enumerate(scenes[:4]):
            visual = scene.get("visual", "")
            prompt = f"Commercial ad for {product}: {visual}. Professional photography, 16:9."

            import urllib.parse

            encoded = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width={self.width}&height={self.height}&model={self.model}&nologo=true"

            frames.append(
                {
                    "scene_number": i + 1,
                    "url": url,
                    "description": visual,
                    "source": "pollinations",
                }
            )

        return {
            "frames": frames,
            "total_generated": len(frames),
            "model": "pollinations-flux",
        }


# ============================================================
# MOCK GENERATOR FOR TESTING
# ============================================================


class MockImageGeneratorAgent:
    """Mock image generator for testing without any API calls."""

    async def run(
        self,
        product: str,
        industry: str,
        duration: int,
        tone: str,
        city: str,
        previous_results: dict,
    ) -> dict:
        script_data = previous_results.get("script_writer", {})
        scenes = script_data.get("scenes", [])

        frames = []
        for i, scene in enumerate(scenes[:6]):
            frames.append(
                {
                    "scene_number": scene.get("scene_number", i + 1),
                    "timing": scene.get("timing", ""),
                    "url": f"https://picsum.photos/seed/{i * 100}/1280/720",
                    "prompt_used": "[MOCK] " + scene.get("visual", "")[:100],
                    "description": scene.get("visual", ""),
                    "source": "mock",
                }
            )

        return {
            "frames": frames,
            "total_generated": len(frames),
            "total_scenes": len(scenes),
            "mock": True,
        }
