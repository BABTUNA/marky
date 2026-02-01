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

from core.gemini_client import chat_completion  # Using Google Gemini (Cloud credits!)


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
                product,
                industry,
                duration,
                tone,
                city,
                trend_data,
                research_data,
                previous_results,
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
        """Build the script writing prompt with ALL research data."""

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

        # =============================================
        # ENHANCED: Get ALL research insights
        # =============================================

        # Combined insights (already processed by EnhancedResearchAgent)
        research_insights = research_data.get("insights", [])
        insights_text = (
            "\n".join(f"- {insight}" for insight in research_insights[:10])
            if research_insights
            else "- Focus on clear value proposition"
        )

        # Competitor hooks and insights from Google Ads
        competitor_ads = research_data.get("competitor_ads", {})
        competitor_hooks = ""
        if competitor_ads:
            hooks = competitor_ads.get("hook_suggestions", [])[:3]
            if hooks:
                competitor_hooks = (
                    "\n\nCOMPETITOR HOOKS (differentiate from these):\n"
                    + "\n".join(f"- {hook}" for hook in hooks)
                )

            # Add top competitor insights
            what_top_do = competitor_ads.get("what_top_competitors_do", [])[:3]
            if what_top_do:
                competitor_hooks += "\n\nLEARN FROM TOP COMPETITORS:\n"
                competitor_hooks += "\n".join(f"✓ {tip}" for tip in what_top_do)

            # Add what to avoid
            what_to_avoid = competitor_ads.get("what_to_avoid", [])[:3]
            if what_to_avoid:
                competitor_hooks += "\n\nAVOID THESE MISTAKES:\n"
                competitor_hooks += "\n".join(
                    f"✗ {mistake}" for mistake in what_to_avoid
                )

        # =============================================
        # NEW: Customer Voice from Reviews
        # =============================================
        customer_voice_section = ""

        # Google Reviews insights
        google_reviews = research_data.get("google_reviews", {})
        if google_reviews:
            complaints = google_reviews.get("common_complaints", [])[:3]
            praises = google_reviews.get("common_praises", [])[:3]

            if complaints or praises:
                customer_voice_section += "\n\nCUSTOMER VOICE (from real reviews):"
                if complaints:
                    customer_voice_section += "\nPain points to ADDRESS in the ad:"
                    for c in complaints:
                        customer_voice_section += f"\n  - Customers complain about: {c}"
                if praises:
                    customer_voice_section += "\nBenefits to HIGHLIGHT:"
                    for p in praises:
                        customer_voice_section += f"\n  - Customers love: {p}"

        # Yelp insights
        yelp_reviews = research_data.get("yelp_reviews", {})
        if yelp_reviews:
            loves = yelp_reviews.get("what_customers_love", [])[:2]
            phrases = yelp_reviews.get("customer_phrases", [])[:2]

            if loves:
                customer_voice_section += "\n\nYelp customers especially value:"
                for l in loves:
                    customer_voice_section += f"\n  - {l}"
            if phrases:
                customer_voice_section += (
                    "\nActual phrases customers use (incorporate naturally):"
                )
                for p in phrases:
                    customer_voice_section += f'\n  - "{p}"'

        # =============================================
        # NEW: Keyword Trends
        # =============================================
        trends_section = ""
        keyword_trends = research_data.get("keyword_trends", {})
        if keyword_trends:
            best_keywords = keyword_trends.get("best_keywords_for_ads", [])[:2]
            seasonal = keyword_trends.get("seasonal_insights", [])[:1]

            if best_keywords or seasonal:
                trends_section = "\n\nKEYWORD TARGETING:"
                if best_keywords:
                    for kw in best_keywords:
                        trends_section += f"\n  - {kw}"
                if seasonal:
                    trends_section += f"\n  - Seasonal insight: {seasonal[0]}"

        # =============================================
        # NEW: Related Questions (Content Intent)
        # =============================================
        related_questions_section = ""
        related_questions = research_data.get("related_questions", [])
        if related_questions:
            related_questions_section = "\n\nCUSTOMER QUESTIONS (Address these in your script):\n"
            for q in related_questions[:5]:
                related_questions_section += f"\n  - {q}"

        # Get location data for setting
        location_data = previous_results.get("location_scout", {})
        locations = location_data.get("locations", [])
        location_setting = ""
        if locations:
            loc = locations[0]
            loc_name = loc.get("name", "")
            loc_type = loc.get("types", [""])[0] if loc.get("types") else ""
            if loc_name:
                location_setting = f"\n\nFILMING LOCATION:\nShoot at or near: {loc_name} ({loc_type})\nIncorporate this or similar setting into the visuals."

        return f"""You are an award-winning advertising copywriter. Write a {duration}-second {tone} ad script for a {product}{location_ref}.

RESEARCH INSIGHTS (USE THESE - they're based on real competitor analysis and customer reviews):
{insights_text}
- Recommended Hook: {recommended_hook}
- Visual Style: {visual_style}
- Key Messages: {", ".join(key_messages) if key_messages else "Highlight unique value"}
- Call-to-Action: {cta}
{competitor_hooks}
{customer_voice_section}
{trends_section}
{related_questions_section}
{location_setting}

STRUCTURE GUIDANCE:
{structure_text if structure_text else "Standard: Hook -> Problem -> Solution -> Social Proof -> CTA"}

IMPORTANT: The script MUST:
1. Address at least ONE customer pain point identified in the research
2. Highlight at least ONE thing customers love (from reviews)
3. Use natural, conversational language that matches how real customers talk
4. Differentiate from competitor hooks listed above

Write the script in this EXACT format:

---
SCENE 1 (0-{duration // 6}s): [HOOK]
Visual: [Describe exactly what we see - be specific about shots, angles, subjects. Use the filming location if relevant.]
Audio: [Music/sound description]
Voiceover: "[Exact words spoken]"

SCENE 2 ({duration // 6}-{duration // 3}s): [SETUP/PROBLEM]
Visual: [Description - show the pain point customers complain about]
Audio: [Description]
Voiceover: "[Words - acknowledge the problem]"

SCENE 3 ({duration // 3}-{duration // 2}s): [SOLUTION/PRODUCT]
Visual: [Description]
Audio: [Description]
Voiceover: "[Words]"

SCENE 4 ({duration // 2}-{int(duration * 0.75)}s): [PROOF/BENEFITS]
Visual: [Description - show what customers love]
Audio: [Description]
Voiceover: "[Words - use customer language]"

SCENE 5 ({int(duration * 0.75)}-{duration}s): [CTA]
Visual: [Description]
Audio: [Description]
Voiceover: "[Words]"
---

Requirements:
1. The {tone} tone must come through clearly
2. Visual descriptions must be specific enough for a storyboard artist
3. Total voiceover should fit within {duration} seconds (about {duration * 2.5} words max)
4. Include at least one moment that creates emotional connection
5. End with a clear, memorable call-to-action
6. If location data is provided, incorporate that setting naturally into the visuals

CRITICAL - VOICEOVER MUST SOUND NATURAL AND HUMAN:
- Write like people actually talk, not like a commercial script
- Use contractions (don't, we're, you'll, it's) - NEVER use formal "do not", "we are"
- Include natural pauses with "..." or commas where someone would breathe
- Vary sentence length - mix short punchy lines with longer flowing ones
- Use conversational phrases like "you know what?", "here's the thing", "honestly"
- For funny tones: add playful exaggeration and unexpected twists
- Avoid clichés like "but wait, there's more" or "call now"
- Read it out loud in your head - if it sounds stilted, rewrite it
- Example GOOD: "Look, we get it... finding a good pizza place? It's basically impossible."
- Example BAD: "Are you searching for a quality pizza restaurant in your area?"

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
