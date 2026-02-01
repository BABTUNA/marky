"""
Lyria Music Generation Agent (Google Vertex AI)

PLACEHOLDER - DO NOT RUN YET (OPTIONAL - Use Incompetech instead)

Generates music using Google's Lyria 2 model.
Alternative: Keep using Incompetech music downloads (free, CC-BY)
"""

import os
import base64
from pathlib import Path
from typing import Dict

# TODO: Uncomment when ready to test
# from google.cloud import aiplatform


class LyriaAgent:
    """Generates music using Google Lyria 2."""

    def __init__(self):
        """Initialize Lyria agent."""
        self.output_dir = Path("output/music")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # TODO: Initialize Vertex AI client when ready
        # self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        # self.location = "us-central1"

    async def run(
        self,
        product: str,
        industry: str,
        duration: int,
        tone: str,
        city: str,
        previous_results: dict,
    ) -> Dict:
        """
        Generate background music using Lyria 2.
        
        Args:
            product: Product name
            industry: Industry
            duration: Target duration (seconds)
            tone: Ad tone
            city: City
            previous_results: Results from previous agents
        
        Returns:
            dict with music file path and metadata
        """
        
        # Get music recommendations from music agent
        music_data = previous_results.get("music", {})
        music_rec = music_data.get("quick_recommendation", {})
        genre = music_rec.get("genre", "Upbeat")
        bpm = music_rec.get("bpm", "100-120")
        
        print(f"\n🎵 Lyria Agent")
        print(f"   Genre: {genre}")
        print(f"   BPM: {bpm}")
        print(f"   Duration: {duration}s")
        
        # PLACEHOLDER: Would generate music here
        # For now, return structure without actual generation
        
        print(f"   ⏳ [PLACEHOLDER] Would generate music with Lyria 2")
        print(f"   💡 Alternative: Using Incompetech (free, already working)")
        
        return {
            "music_path": str(self.output_dir / f"lyria_{product.replace(' ', '_')}.wav"),
            "genre": genre,
            "bpm": bpm,
            "duration": duration,
            "model": "lyria-2-realtime",
            "note": "PLACEHOLDER - Actual generation not implemented yet. Recommend using Incompetech instead (free).",
            "generated": False,
        }

    async def _generate_music(
        self, prompt: str, duration: int, product: str
    ) -> str:
        """
        Generate music using Lyria API.
        
        ⚠️ OPTIONAL - Consider using Incompetech instead (free)
        
        Args:
            prompt: Text description of music style
            duration: Duration in seconds (30-32s)
            product: Product name for filename
        
        Returns:
            Path to generated music file
        """
        
        # TODO: Implement when ready to test
        raise NotImplementedError("Lyria API calls not implemented yet - use Incompetech instead!")
        
        # EXAMPLE CODE (uncomment when ready):
        #
        # endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/lyria-realtime"
        #
        # request_payload = {
        #     "instances": [{
        #         "prompt": prompt,
        #         "negative_prompt": "vocals, lyrics, jarring, dissonant",
        #         "duration": duration,
        #     }],
        #     "parameters": {
        #         "seed": 12345
        #     }
        # }
        #
        # response = self.client.predict(endpoint=endpoint, instances=request_payload["instances"])
        # audio_base64 = response.predictions[0]["audio"]
        # audio_bytes = base64.b64decode(audio_base64)
        #
        # output_path = self.output_dir / f"lyria_{product.replace(' ', '_')}.wav"
        # with open(output_path, "wb") as f:
        #     f.write(audio_bytes)
        #
        # return str(output_path)
