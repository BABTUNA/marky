"""
AdBoard Pipeline Runner

Orchestrates sequential execution of agents based on output type.
Each agent runs after the previous one completes, passing results forward.
"""

import asyncio
from typing import Any, Dict, List

# Human-friendly progress messages (no emojis)
PROGRESS_MESSAGES = {
    "research": "Research done. Writing your script.",
    "location_scout": "Found filming locations. Writing your script.",
    "trend_analyzer": "Analyzed what works in ads like yours. Writing the script.",
    "script_writer": "Script is ready. Generating storyboard frames for both packages.",
    "image_generator": "Storyboard frames are done. Assembling the concept video.",
    "video_assembly": "Concept video is ready. Building your full campaign package.",
    "cost_estimator": "Budget estimated. Building your PDF with hiring and cost details.",
    "social_media": "Social strategy ready. Building your campaign PDF.",
    "pdf_builder": "Almost done. Finalizing your storyboard and viral packages.",
    "veo3_generator": "Generating viral video. Adding music next.",
    "lyria_music": "Music added. Assembling viral clip.",
    "viral_video_assembler": "Viral video is ready. Finalizing your packages.",
}

# Pipeline definitions - which agents to run for each output type
PIPELINES = {
    "script": ["research", "location_scout", "trend_analyzer", "script_writer"],
    "storyboard": [
        "research",
        "location_scout",
        "trend_analyzer",
        "script_writer",
        "image_generator",
    ],
    "video": [
        "research",
        "location_scout",
        "trend_analyzer",
        "script_writer",
        "image_generator",
        "voiceover",
        "music",
        # "video_assembler"  # Stretch goal
    ],
    "pdf": [
        "research",
        "trend_analyzer",
        "script_writer",
        "image_generator",
        "cost_estimator",
        "location_scout",
        "pdf_builder",
    ],
    "full": [
        "research",
        "trend_analyzer",
        "script_writer",
        "image_generator",
        "voiceover",
        "music",
        "cost_estimator",
        "location_scout",
        "pdf_builder",
    ],
    # NEW: Non-visual pipeline modes (no image/video generation)
    "audio_package": [
        "research",
        "location_scout",
        "trend_analyzer",
        "script_writer",
        "voiceover",
        "music",
        "audio_mixer",
        "social_media",
    ],
    "preproduction": [
        "research",
        "location_scout",
        "trend_analyzer",
        "script_writer",
        "cost_estimator",
        "social_media",
    ],
    "full_no_visual": [
        "research",
        "location_scout",
        "trend_analyzer",
        "script_writer",
        "voiceover",
        "music",
        "audio_mixer",
        "cost_estimator",
        "social_media",
    ],
    # NEW: Storyboard video - sketch frames + Ken Burns (SILENT - no audio) + PDF package
    "storyboard_video": [
        "research",
        "location_scout",
        "trend_analyzer",
        "script_writer",
        "image_generator",  # Generate sketch frames
        "video_assembly",  # Create silent video from images
        "cost_estimator",
        "social_media",
        "pdf_builder",  # Complete campaign PDF package
    ],
    # Complete Viral Video Pipeline (VEO 3 + Lyria + TTS)
    # Now enabled for testing with placeholders!
    "viral_video": [
        "research",
        "trend_analyzer",
        "script_writer",
        "veo3_generator",  # Generates silent video (or uses placeholder)
        "lyria_music",  # Generates music (or uses mock)
        "viral_video_assembler",  # Combines Video + Music + TTS
    ],
    # Minimal viral video test (skip research for faster iteration)
    "viral_video_test": [
        "script_writer",
        "veo3_generator",
        "lyria_music",
        "viral_video_assembler",
    ],
    # Quick E2E test - skips research, produces video + PDF (no VEO 3)
    "quick_test": [
        "script_writer",
        "image_generator",
        "video_assembly",
        "cost_estimator",
        "social_media",
        "pdf_builder",
    ],
}


class AdBoardPipeline:
    """
    Sequential pipeline runner for AdBoard AI.

    Executes agents in order, passing accumulated results to each agent.
    """

    def __init__(
        self,
        product: str,
        industry: str,
        output_type: str,
        duration: int,
        tone: str,
        city: str = "",
    ):
        self.product = product
        self.industry = industry
        self.output_type = output_type
        self.duration = duration
        self.tone = tone
        self.city = city

        # Results accumulator - each agent adds its output here
        self.results: Dict[str, Any] = {}

        # Lazy-load agents to avoid import issues
        self._agents = None

    def _init_agents(self):
        """Initialize all agent instances."""
        if self._agents is not None:
            return

        from agents.audio_mixer import AudioMixerAgent
        from agents.cost_estimator import CostEstimatorAgent
        from agents.enhanced_research import (
            ResearchAgent,  # Now includes YouTube + Google Ads
        )
        from agents.image_generator import ImageGeneratorAgent
        from agents.location_scout import LocationScoutAgent
        from agents.lyria_agent import LyriaAgent
        from agents.music_agent import MusicAgent
        from agents.pdf_builder import PDFBuilderAgent
        from agents.script_writer import ScriptWriterAgent
        from agents.social_media_agent import SocialMediaAgent
        from agents.trend_analyzer import TrendAnalyzerAgent
        from agents.veo3_agent import VEO3Agent
        from agents.video_assembly_agent import VideoAssemblyAgent
        from agents.viral_video_assembler import ViralVideoAssembler
        from agents.voiceover_agent import VoiceoverAgent

        self._agents = {
            "research": ResearchAgent(),
            "trend_analyzer": TrendAnalyzerAgent(),
            "script_writer": ScriptWriterAgent(),
            "image_generator": ImageGeneratorAgent(),
            "voiceover": VoiceoverAgent(),
            "music": MusicAgent(),
            "audio_mixer": AudioMixerAgent(),
            "cost_estimator": CostEstimatorAgent(),
            "location_scout": LocationScoutAgent(),
            "social_media": SocialMediaAgent(),
            "veo3_generator": VEO3Agent(),
            "lyria_music": LyriaAgent(),
            "viral_video_assembler": ViralVideoAssembler(),
            "pdf_builder": PDFBuilderAgent(),
            "video_assembly": VideoAssemblyAgent(),
        }

    async def run(self, progress_callback=None) -> Dict[str, Any]:
        """
        Execute the pipeline based on output type.

        Args:
            progress_callback: Optional async callable(step_name, message) for check-in messages.

        Returns:
            dict with keys:
                - success: bool
                - results: dict of agent outputs
                - error: str (if failed)
        """

        # Initialize agents
        self._init_agents()

        # Get pipeline steps for this output type
        pipeline_steps = PIPELINES.get(self.output_type, PIPELINES["storyboard"])

        # Quick test: inject dummy research + trend data (skips slow Marky workflow)
        if self.output_type == "quick_test":
            from core.dummy_research import get_dummy_research
            self.results["research"] = get_dummy_research(
                industry=self.industry, product=self.product
            )
            self.results["trend_analyzer"] = {
                "viral_patterns": self.results["research"].get("patterns_identified", {}).get("common_hooks", [])[:3],
                "recommended_hooks": ["Authenticity wins", "Show the product", "Clear CTA"],
            }
            self.results["location_scout"] = {"locations": [{"name": "Downtown", "address": "Providence, RI"}]}
            print("  [quick_test] Using dummy research (skipping Marky workflow)")

        print(f"\n{'=' * 50}")
        print(f"AdBoard Pipeline: {self.output_type}")
        print(f"Steps: {' -> '.join(pipeline_steps)}")
        print(f"{'=' * 50}\n")

        try:
            for step in pipeline_steps:
                print(f"[{step}] Starting...")

                agent = self._agents.get(step)
                if agent is None:
                    print(f"[{step}] Agent not found, skipping")
                    continue

                # Run the agent with context
                try:
                    result = await agent.run(
                        product=self.product,
                        industry=self.industry,
                        duration=self.duration,
                        tone=self.tone,
                        city=self.city,
                        previous_results=self.results,
                    )

                    # Store result
                    self.results[step] = result

                    # Progress check-in (human-friendly message)
                    if progress_callback and step in PROGRESS_MESSAGES:
                        try:
                            await progress_callback(step, PROGRESS_MESSAGES[step])
                        except Exception:
                            pass

                    # Check for errors
                    if isinstance(result, dict) and result.get("error"):
                        print(f"[{step}] Error: {result['error']}")
                        # Continue anyway - graceful degradation
                    else:
                        print(f"[{step}] Completed successfully")

                except Exception as e:
                    print(f"[{step}] Exception: {e}")
                    self.results[step] = {"error": str(e)}
                    # Continue with pipeline - don't fail completely

            print(f"\n{'=' * 50}")
            print("Pipeline completed!")
            print(f"{'=' * 50}\n")

            return {"success": True, "results": self.results}

        except Exception as e:
            print(f"Pipeline failed: {e}")
            return {"success": False, "error": str(e), "results": self.results}

    def run_sync(self) -> Dict[str, Any]:
        """Synchronous wrapper for running the pipeline."""
        return asyncio.run(self.run())


# Convenience function
async def run_pipeline(
    product: str,
    industry: str,
    output_type: str = "storyboard",
    duration: int = 45,
    tone: str = "professional",
    city: str = "",
) -> Dict[str, Any]:
    """
    Run the AdBoard pipeline with given parameters.

    Args:
        product: What product/business
        industry: Industry category
        output_type: What to generate (script/storyboard/video/pdf/full)
        duration: Ad length in seconds
        tone: Style (professional/funny/emotional/energetic)
        city: City for location scouting

    Returns:
        Pipeline results
    """
    pipeline = AdBoardPipeline(
        product=product,
        industry=industry,
        output_type=output_type,
        duration=duration,
        tone=tone,
        city=city,
    )
    return await pipeline.run()
