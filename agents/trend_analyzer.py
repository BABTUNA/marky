"""
Trend Analyzer Agent

Analyzes research data (from YouTube) to extract actionable patterns
for ad creation: hooks, structures, visual styles, CTAs.
"""

import json
import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.groq_client import chat_completion


class TrendAnalyzerAgent:
    """Analyzes viral ad patterns from research data."""

    def __init__(self):
        pass

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
        Analyze research data and extract patterns.

        Args:
            product: The product/business
            industry: Industry category
            duration: Target ad duration
            tone: Desired tone
            city: City (unused here)
            previous_results: Results from previous agents (includes research)

        Returns:
            dict with analyzed patterns and recommendations
        """

        # Get research data from previous step
        research_data = previous_results.get("research", {})

        if not research_data or research_data.get("error"):
            return {"error": "No research data available"}

        try:
            # Build the analysis prompt
            prompt = self._build_prompt(
                research_data, product, industry, duration, tone
            )

            # Use the Groq client with automatic model fallback
            response = chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3,
            )

            result_text = response["content"].strip()

            # Try to parse as JSON
            try:
                # Handle markdown code blocks
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]

                analysis = json.loads(result_text)
            except json.JSONDecodeError:
                # Return as structured text if JSON fails
                analysis = {"raw_analysis": result_text}

            return {
                "analysis": analysis,
                "product": product,
                "industry": industry,
                "target_duration": duration,
                "tone": tone,
            }

        except Exception as e:
            return {"error": str(e)}

    def _build_prompt(
        self, research_data: dict, product: str, industry: str, duration: int, tone: str
    ) -> str:
        """Build the analysis prompt."""

        # Extract key info from research
        top_videos = research_data.get("top_videos", [])
        patterns = research_data.get("patterns_identified", {})

        videos_summary = ""
        for i, video in enumerate(top_videos[:5], 1):
            videos_summary += f"{i}. {video.get('title', 'Unknown')} - {video.get('views', 0):,} views\n"

        return f"""You are an expert advertising strategist. Analyze this research data and provide actionable insights for creating a {duration}-second {tone} ad for a {product} in the {industry} industry.

RESEARCH DATA:
Top Performing Videos:
{videos_summary}

Patterns Already Identified:
- Common Hooks: {patterns.get("common_hooks", ["Not available"])}
- Visual Styles: {patterns.get("visual_styles", ["Not available"])}
- Effective CTAs: {patterns.get("effective_ctas", ["Not available"])}
- Effective CTAs: {patterns.get("effective_ctas", ["Not available"])}

Provide your analysis as a JSON object with these exact fields:
{{
    "recommended_hook": "The specific opening hook to use (first 3 seconds)",
    "ad_structure": [
        {{"time": "0-3s", "element": "Hook", "description": "What happens"}},
        {{"time": "3-10s", "element": "Problem/Setup", "description": "What happens"}},
        ...continue for full {duration} seconds...
    ],
    "visual_style": "Specific visual approach to use",
    "audio_approach": "Music and sound design recommendation",
    "key_messages": ["Message 1", "Message 2", "Message 3"],
    "cta": "Specific call-to-action",
    "unique_angle": "What will make this ad stand out",
    "warnings": ["Things to avoid based on research"]
}}

Be specific and actionable. This will be used to write the actual script."""
