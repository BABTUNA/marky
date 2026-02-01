"""
Script Writer Agent

Writes compelling ad scripts based on research analysis.
Outputs scene-by-scene breakdown with visual descriptions and voiceover.
"""

import json
import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.groq_client import chat_completion


class ScriptWriterAgent:
    """Writes ad scripts based on trend analysis."""

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
        Write the ad script.

        Args:
            product: The product/business
            industry: Industry category
            duration: Target ad duration in seconds
            tone: Desired tone
            city: City (for location references)
            previous_results: Results from previous agents

        Returns:
            dict with script, scenes, and voiceover text
        """

        # Get trend analysis from previous step
        trend_data = previous_results.get("trend_analyzer", {})
        research_data = previous_results.get("research", {})

        try:
            prompt = self._build_prompt(
                product, industry, duration, tone, city, trend_data, research_data, previous_results
            )

            # Use the Groq client with automatic model fallback
            response = chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7,
            )

            result_text = response["content"].strip()

            # Parse the script
            script_data = self._parse_script(result_text, duration)
            script_data["model_used"] = response["model"]

            return script_data

        except Exception as e:
            return {"error": str(e)}

    def _build_prompt(
        self,
        product: str,
        industry: str,
        duration: int,
        tone: str,
        city: str,
        trend_data: dict,
        research_data: dict,
        previous_results: dict,
    ) -> str:
        """Build the script writing prompt with research and location data.\"""

        analysis = trend_data.get("analysis", {})

        # Extract recommendations if available
        recommended_hook = analysis.get("recommended_hook", "Attention-grabbing visual")
        ad_structure = analysis.get("ad_structure", [])
        visual_style = analysis.get("visual_style", "Professional and engaging")
        cta = analysis.get("cta", "Visit us today")
        key_messages = analysis.get("key_messages", [])

        structure_text = ""
        if ad_structure:
            for item in ad_structure:
                structure_text += f"- {item.get('time', '')}: {item.get('element', '')} - {item.get('description', '')}\n"

        location_ref = f" in {city}" if city else ""
        
        # Get enhanced research insights (YouTube + Google Ads)
        research_insights = research_data.get("insights", [])
        insights_text = "\n".join(f"- {insight}" for insight in research_insights[:5]) if research_insights else "- Focus on clear value proposition"
        
        # Get competitor hooks if available
        competitor_ads = research_data.get("competitor_ads", {})
        competitor_hooks = ""
        if competitor_ads:
            hooks = competitor_ads.get("hook_suggestions", [])[:3]
            if hooks:
                competitor_hooks = "\nCOMPETITOR HOOKS (differentiate from these):\n" + "\n".join(f"- {hook}" for hook in hooks)
        
        # Get location data for setting
        location_data = previous_results.get("location_scout", {})
        locations = location_data.get("locations", [])
        location_setting = ""
        if locations:
            # Use first location as primary setting
            loc = locations[0]
            loc_name = loc.get("name", "")
            loc_type = loc.get("types", [""])[0] if loc.get("types") else ""
            if loc_name:
                location_setting = f"\n\nFILMING LOCATION:\nShoot at or near: {loc_name} ({loc_type})\nIncorporate this or similar setting into the visuals."

        return f"""You are an award-winning advertising copywriter. Write a {duration}-second {tone} ad script for a {product}{location_ref}.

RESEARCH INSIGHTS:
{insights_text}
- Recommended Hook: {recommended_hook}
- Visual Style: {visual_style}
- Key Messages: {", ".join(key_messages) if key_messages else "Highlight unique value"}
- Call-to-Action: {cta}
{competitor_hooks}
{location_setting}

STRUCTURE GUIDANCE:
{structure_text if structure_text else "Standard: Hook -> Problem -> Solution -> Social Proof -> CTA"}

Write the script in this EXACT format:

---
SCENE 1 (0-{duration // 6}s): [HOOK]
Visual: [Describe exactly what we see - be specific about shots, angles, subjects. Use the filming location if relevant.]
Audio: [Music/sound description]
Voiceover: "[Exact words spoken]"

SCENE 2 ({duration // 6}-{duration // 3}s): [SETUP]
Visual: [Description]
Audio: [Description]
Voiceover: "[Words]"

SCENE 3 ({duration // 3}-{duration // 2}s): [SOLUTION/PRODUCT]
Visual: [Description]
Audio: [Description]
Voiceover: "[Words]"

SCENE 4 ({duration // 2}-{int(duration * 0.75)}s): [PROOF/BENEFITS]
Visual: [Description]
Audio: [Description]
Voiceover: "[Words]"

SCENE 5 ({int(duration * 0.75)}-{duration}s): [CTA]
Visual: [Description]
Audio: [Description]
Voiceover: "[Words]"
---

Requirements:
1. The {tone} tone must come through clearly
2. Voiceover should be natural and conversational
3. Visual descriptions must be specific enough for a storyboard artist
4. Total voiceover should fit within {duration} seconds (about {duration * 2.5} words max)
5. Include at least one moment that creates emotional connection
6. End with a clear, memorable call-to-action
7. If location data is provided, incorporate that setting naturally into the visuals

Write the complete script now:"""

    def _parse_script(self, script_text: str, duration: int) -> dict:
        """Parse the raw script into structured data."""

        scenes = []
        voiceover_parts = []

        # Split by SCENE markers
        scene_blocks = script_text.split("SCENE ")

        for block in scene_blocks[1:]:  # Skip first empty block
            lines = block.strip().split("\n")

            scene = {
                "scene_number": len(scenes) + 1,
                "timing": "",
                "title": "",
                "visual": "",
                "audio": "",
                "voiceover": "",
            }

            # Parse first line for timing and title
            if lines:
                first_line = lines[0]
                if "(" in first_line and ")" in first_line:
                    timing = first_line[first_line.find("(") + 1 : first_line.find(")")]
                    scene["timing"] = timing
                if ":" in first_line:
                    title_part = first_line.split(":")[-1].strip()
                    scene["title"] = title_part.strip("[]")

            # Parse remaining lines
            current_field = None
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("Visual:"):
                    current_field = "visual"
                    scene["visual"] = line.replace("Visual:", "").strip()
                elif line.startswith("Audio:"):
                    current_field = "audio"
                    scene["audio"] = line.replace("Audio:", "").strip()
                elif line.startswith("Voiceover:"):
                    current_field = "voiceover"
                    vo_text = line.replace("Voiceover:", "").strip().strip('"')
                    scene["voiceover"] = vo_text
                    voiceover_parts.append(vo_text)
                elif current_field and line:
                    # Continue previous field
                    if current_field == "voiceover":
                        scene["voiceover"] += " " + line.strip('"')
                    else:
                        scene[current_field] += " " + line

            if scene["visual"] or scene["voiceover"]:
                scenes.append(scene)

        # If parsing failed, create a simpler structure
        if not scenes:
            scenes = [
                {
                    "scene_number": 1,
                    "timing": f"0-{duration}s",
                    "title": "Full Ad",
                    "visual": "See full script",
                    "audio": "Background music",
                    "voiceover": "",
                }
            ]

        # Combine voiceover for TTS
        full_voiceover = " ".join(voiceover_parts)

        return {
            "script": script_text,
            "scenes": scenes,
            "voiceover_text": full_voiceover,
            "scene_count": len(scenes),
            "estimated_duration": duration,
        }
