"""
Enhanced Research Agent - Uses Teammate's Marky Research Suite

Uses the Marky workflow (teammate's implementation) for comprehensive ad research:
1. Local Intel - Competitor discovery, website scraping, success/failure analysis
2. Review Intel - Google Reviews via place_ids
3. Yelp Intel - Yelp reviews with pain/praise extraction
4. Trends Intel - DataForSEO keyword trends
5. Related Questions Intel - "People also ask" queries for content intent
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv

load_dotenv()

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.workflow import MarkyWorkflow, run_workflow
from orchestrator.models import AdResearchRequest, AdResearchResponse


class EnhancedResearchAgent:
    """
    Comprehensive research agent using Marky's multi-agent workflow.
    
    Runs the complete Marky pipeline:
    1. Local Intel - Competitor discovery and website analysis
    2. Review Intel - Google Reviews from competitors
    3. Yelp Intel - Yelp reviews analysis
    4. Trends Intel - Keyword and seasonal data
    5. Related Questions Intel - Content intent from "People also ask"
    """

    def __init__(self):
        self.workflow = MarkyWorkflow()

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
        Perform comprehensive research using Marky workflow.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone
            city: City for location
            previous_results: Results from previous agents

        Returns:
            Combined research insights compatible with AdBoard pipeline
        """
        print("\n" + "=" * 60)
        print("ENHANCED RESEARCH AGENT (Marky Workflow)")
        print("=" * 60)
        print(f"Product: {product} | Industry: {industry} | Location: {city}")
        print("=" * 60)

        # Build business type string
        business_type = f"{industry} {product}".strip() if industry else product
        location = city or "United States"

        # Run Marky workflow (synchronous, runs in thread pool)
        import asyncio

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: run_workflow(
                business_type=business_type,
                location=location,
                max_competitors=8,
                include_trends=True,
            )
        )

        # Convert Marky response to AdBoard format
        research_data = self._convert_marky_response(response, business_type, product, industry, city)

        return research_data

    def _convert_marky_response(
        self,
        response: AdResearchResponse,
        business_type: str,
        product: str,
        industry: str,
        city: str,
    ) -> dict:
        """Convert Marky response to AdBoard pipeline format."""

        if not response.success or not response.result:
            print(f"  ⚠️ Marky workflow failed: {response.error}")
            return {
                "industry": industry,
                "product": product,
                "city": city,
                "error": response.error or "Unknown error",
                "research_summary": {
                    "youtube_videos": 0,
                    "competitors_found": 0,
                    "google_reviews": 0,
                    "yelp_reviews": 0,
                    "keywords_analyzed": 0,
                },
            }

        result = response.result

        # Build competitor intel data
        local_intel_data = self._build_local_intel_data(result)
        review_data = self._build_review_data(result)
        trends_data = self._build_trends_data(result)

        # Combine insights
        combined_insights = self._combine_insights(result)

        # Calculate summary stats
        competitors_count = len(result.competitors)
        google_reviews_count = sum(
            len(voice.praise_quotes) + len(voice.complaint_quotes)
            for voice in [result.customer_voice] if voice
        )
        yelp_reviews_count = google_reviews_count  # Combined in customer_voice
        keywords_count = len(result.timing)

        print(f"\n✅ Research complete:")
        print(f"  • Competitors found: {competitors_count}")
        print(f"  • Customer themes: {len(result.customer_voice.common_themes) if result.customer_voice else 0}")
        print(f"  • Keywords analyzed: {keywords_count}")
        print(f"  • Ad hooks generated: {len(result.recommended_hooks)}")
        print(f"  • Headlines generated: {len(result.headline_suggestions)}")
        print(f"  • Differentiators: {len(result.differentiators)}")

        return {
            "industry": industry,
            "product": product,
            "city": city,
            # Local Intel (competitors, website analysis)
            "competitor_ads": local_intel_data,
            "local_intel": local_intel_data,
            # Customer voice from reviews
            "google_reviews": review_data,
            "yelp_reviews": review_data,  # Combined in Marky
            # Keyword trends
            "keyword_trends": trends_data,
            # Related questions for content intent
            "related_questions": result.related_questions,
            # Viral patterns (placeholder - YouTube research would be separate)
            "viral_videos": [],
            "viral_patterns": {},
            # Combined insights for script writer
            "insights": combined_insights,
            "videos_analyzed": 0,
            # Summary stats
            "research_summary": {
                "youtube_videos": 0,
                "competitors_found": competitors_count,
                "google_reviews": google_reviews_count,
                "yelp_reviews": yelp_reviews_count,
                "keywords_analyzed": keywords_count,
            },
            # Full Marky result for reference
            "marky_result": result.to_dict() if hasattr(result, "to_dict") else {},
        }

    def _build_local_intel_data(self, result) -> dict:
        """Build local intelligence data from Marky result."""
        data = {
            "competitors_found": len(result.competitors),
            "top_competitors": [c.name for c in result.competitors[:5]],
            "worst_competitors": [],
            "headline_suggestions": result.headline_suggestions[:10],
            "trust_signals_to_use": result.trust_signals[:10],
            "differentiators": [
                {
                    "angle": d.angle_name,
                    "hook": d.hook,
                    "best_for": d.best_for,
                }
                for d in result.differentiators[:5]
            ],
            "what_top_competitors_do": [],
            "what_to_avoid": [],
            "recommendations": [],
        }

        # Extract what top competitors do from differentiators and market summary
        for diff in result.differentiators[:3]:
            if "strength" in diff.angle_name.lower() or "quality" in diff.angle_name.lower():
                data["what_top_competitors_do"].append(f"Emphasize {diff.angle_name}")

        # Build market summary from differentiators
        if result.market_summary:
            data["market_summary"] = result.market_summary

        return data

    def _build_review_data(self, result) -> dict:
        """Build review/customer voice data from Marky result."""
        if not result.customer_voice:
            return {
                "total_reviews": 0,
                "pain_points": [],
                "desires": [],
                "praise_quotes": [],
                "complaint_quotes": [],
                "ad_hooks": result.recommended_hooks[:5],
                "headline_suggestions": result.headline_suggestions[:5],
            }

        voice = result.customer_voice

        return {
            "total_reviews": len(voice.praise_quotes) + len(voice.complaint_quotes),
            "pain_points": voice.pain_points[:10],
            "desires": voice.desires[:10],
            "praise_quotes": voice.praise_quotes[:5],
            "complaint_quotes": voice.complaint_quotes[:5],
            "ad_hooks": result.recommended_hooks[:5],
            "headline_suggestions": result.headline_suggestions[:5],
            "common_themes": voice.common_themes[:10],
        }

    def _build_trends_data(self, result) -> dict:
        """Build keyword trends data from Marky result."""
        keyword_data = []
        timing_recommendations = []
        ad_recommendations = []

        for timing in result.timing:
            keyword_data.append({
                "keyword": timing.keyword,
                "search_volume": timing.monthly_volume,
                "cpc": timing.avg_cpc,
            })
            if timing.recommendation:
                timing_recommendations.append(
                    f"Best months for '{timing.keyword}': {', '.join(timing.peak_months)}"
                )
                ad_recommendations.append(timing.recommendation)

        return {
            "keywords_analyzed": len(keyword_data),
            "keyword_data": keyword_data,
            "timing_recommendations": timing_recommendations,
            "ad_recommendations": ad_recommendations[:5],
        }

    def _combine_insights(self, result) -> List[str]:
        """Combine all research into actionable insights for the script writer."""
        insights = []

        # From customer voice - pain points to address
        if result.customer_voice:
            for pain in result.customer_voice.pain_points[:2]:
                insights.append(f"😤 Customer pain point: {pain} - ADDRESS THIS")
            for desire in result.customer_voice.desires[:2]:
                insights.append(f"💭 Customers want: {desire}")

        # From recommended hooks
        for hook in result.recommended_hooks[:2]:
            insights.append(f"📢 Hook from research: {hook}")

        # From differentiators
        for diff in result.differentiators[:2]:
            insights.append(f"💡 Angle: {diff.angle_name} - {diff.hook}")

        # From seasonal timing
        for timing in result.timing[:1]:
            if timing.peak_months:
                insights.append(f"📅 Best timing: {', '.join(timing.peak_months)}")

        if not insights:
            insights = ["Focus on clear value proposition and customer trust signals"]

        return insights


# Make it compatible with the pipeline's Agent class pattern
class ResearchAgent(EnhancedResearchAgent):
    """Alias for pipeline compatibility"""

    pass
