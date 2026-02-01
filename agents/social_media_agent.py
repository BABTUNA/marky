"""
Social Media Strategy Agent

Creates a comprehensive social media distribution strategy for the ad.
"""

import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.gemini_client import chat_completion  # Using Google Gemini (Cloud credits!)


class SocialMediaAgent:
    """Generates social media posting strategy and content recommendations."""

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
        Generate social media strategy.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone
            city: City (for local targeting)
            previous_results: Results from previous agents

        Returns:
            dict with social media strategy
        """

        try:
            # Get context from previous results
            script_data = previous_results.get("script_writer", {})
            scenes = script_data.get("scenes", [])

            # Get target audience if available
            target_audience = previous_results.get("target_audience", {})

            scene_summary = ""
            for scene in scenes[:3]:
                scene_summary += f"- {scene.get('title', '')}\n"

            prompt = f"""You are a social media marketing expert. Create a distribution strategy for this ad campaign:

CAMPAIGN DETAILS:
Product: {product}
Industry: {industry}
Duration: {duration} seconds
Tone: {tone}
Location: {city if city else "General market"}

AD CONTENT OVERVIEW:
{scene_summary}

Create a comprehensive social media strategy with:

1. PLATFORM RECOMMENDATIONS (prioritize top 3):
   For each platform include:
   - Why this platform?
   - Target audience on this platform
   - Posting format (Reels, Story, Feed post, etc.)
   - Optimal posting times

2. CONTENT VARIATIONS:
   - Main post caption (60-100 words)
   - Short teaser caption (20 words)
   - Story/Reels caption (10 words)

3. HASHTAG STRATEGY:
   - 5 industry-specific hashtags
   - 3 location-based hashtags (if city provided)
   - 2 trending/viral hashtags

4. POSTING SCHEDULE:
   - Best days of week
   - Best times of day
   - Posting frequency

5. ENGAGEMENT TACTICS:
   - Call-to-action recommendations
   - Comment engagement strategy
   - Cross-promotion ideas

6. BUDGET RECOMMENDATIONS:
   - Organic vs paid strategy
   - Suggested ad spend (if any)
   - Expected reach estimates

Format your response in clear sections with emoji for visual appeal.
Be specific and actionable."""

            # Use the Groq client with automatic model fallback
            response = chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7,
            )

            strategy = response["content"].strip()

            # Generate quick hashtags
            hashtags = self._generate_hashtags(industry, city, tone)

            return {
                "strategy": strategy,
                "hashtags": hashtags,
                "platforms": self._get_platform_priorities(industry, tone),
                "quick_captions": self._generate_quick_captions(
                    product, tone, script_data
                ),
            }

        except Exception as e:
            return {
                "error": str(e),
                "fallback": self._get_fallback_strategy(product, industry, city),
            }

    def _generate_hashtags(self, industry: str, city: str, tone: str) -> dict:
        """Generate hashtag suggestions quickly."""

        industry_tags = {
            "food": [
                "#FoodPorn",
                "#Foodie",
                "#FoodLover",
                "#InstaFood",
                "#Delicious",
            ],
            "fitness": [
                "#Fitness",
                "#FitLife",
                "#Workout",
                "#HealthyLiving",
                "#FitnessMotivation",
            ],
            "tech": ["#Tech", "#Innovation", "#TechNews", "#Startup", "#Digital"],
            "beauty": [
                "#Beauty",
                "#BeautyTips",
                "#Skincare",
                "#MakeupLover",
                "#SelfCare",
            ],
        }

        tags = industry_tags.get(
            industry, ["#SmallBusiness", "#LocalBusiness", "#ShopLocal"]
        )

        if city:
            city_name = city.split(",")[0].strip().replace(" ", "")
            tags.extend([f"#{city_name}", f"#{city_name}Business"])

        # Add tone-based tags
        if tone == "funny":
            tags.append("#Humor")
        elif tone == "professional":
            tags.append("#Professional")

        return {
            "primary": tags[:5],
            "location": tags[5:7] if city else [],
            "tone": tags[7:],
        }

    def _get_platform_priorities(self, industry: str, tone: str) -> list:
        """Get recommended platforms based on industry and tone."""

        platforms = {
            "food": [
                {"name": "Instagram", "priority": 1, "format": "Reels + Stories"},
                {"name": "TikTok", "priority": 2, "format": "Short-form video"},
                {"name": "Facebook", "priority": 3, "format": "Feed post + story"},
            ],
            "fitness": [
                {"name": "Instagram", "priority": 1, "format": "Reels + IGTV"},
                {"name": "TikTok", "priority": 2, "format": "Workout videos"},
                {"name": "YouTube", "priority": 3, "format": "Shorts"},
            ],
            "tech": [
                {"name": "LinkedIn", "priority": 1, "format": "Feed post + article"},
                {"name": "Twitter/X", "priority": 2, "format": "Thread + video"},
                {"name": "Instagram", "priority": 3, "format": "Reels"},
            ],
        }

        return platforms.get(
            industry,
            [
                {"name": "Instagram", "priority": 1, "format": "Reels"},
                {"name": "Facebook", "priority": 2, "format": "Feed post"},
                {"name": "TikTok", "priority": 3, "format": "Video"},
            ],
        )

    def _generate_quick_captions(
        self, product: str, tone: str, script_data: dict
    ) -> dict:
        """Generate quick caption variations."""

        voiceover = script_data.get("voiceover_text", "")
        hook = voiceover[:100] if voiceover else f"Check out {product}!"

        return {
            "main": f"{hook}... Visit us today! 🎯",
            "short": f"You NEED to see this! 👀 #{product.replace(' ', '')}",
            "cta": f"Ready to experience {product}? Click the link in bio! 🔗",
        }

    def _get_fallback_strategy(self, product: str, industry: str, city: str) -> dict:
        """Provide basic strategy when API fails."""

        return {
            "platforms": ["Instagram", "Facebook", "TikTok"],
            "posting_times": ["Mon-Fri 12pm-2pm", "Wed-Thu 6pm-8pm"],
            "hashtags": ["#SmallBusiness", "#LocalBusiness", f"#{industry}"],
            "caption": f"Discover {product}! Visit us today.",
            "tip": "Post during peak engagement hours and use location tags",
        }
