"""
Enhanced Research Agent - Full "Marky" Research Suite

Uses the proper Marky agents from teammate's implementation:
1. LocalIntelAgent - Competitor discovery, website scraping, success/failure analysis
2. ReviewIntelAgent - Google Reviews via place_ids
3. YelpIntelAgent - Yelp reviews with pain/praise extraction
4. TrendsIntelAgent - DataForSEO keyword trends
5. YouTube Research - Viral ad analysis (our addition)
"""

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

# Import teammate's Marky agents
# Our YouTube research (complements the Marky suite)
from agents.research_agent import ResearchAgent as YouTubeResearch
from local_intel.agent import LocalIntelAgent
from review_intel.agent import ReviewIntelAgent
from trends_intel.agent import TrendsIntelAgent
from yelp_intel.agent import YelpIntelAgent


class EnhancedResearchAgent:
    """
    Full "Marky" research suite that combines:
    1. Local Intel - Competitor discovery, websites, success/failure patterns
    2. Review Intel - Google Reviews (customer voice)
    3. Yelp Intel - Yelp reviews (pain points & praises)
    4. Trends Intel - Keyword trends and seasonal timing
    5. YouTube Research - Viral ad patterns (our addition)
    """

    def __init__(self):
        # YouTube research (our addition)
        self.youtube_research = YouTubeResearch()

        # Marky agents from teammate
        self.local_intel = LocalIntelAgent()
        self.review_intel = ReviewIntelAgent()
        self.yelp_intel = YelpIntelAgent()
        self.trends_intel = TrendsIntelAgent()

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
        Perform comprehensive research using ALL Marky agents.

        Returns:
            Combined research insights from all agents
        """
        print("\n" + "=" * 60)
        print("ENHANCED RESEARCH AGENT (Full Marky Suite)")
        print("=" * 60)
        print(f"Product: {product} | Industry: {industry} | Location: {city}")
        print("=" * 60)

        business_type = f"{industry} {product}".strip() if industry else product

        # Initialize result containers
        youtube_data = {}
        local_intel_data = None
        review_data = None
        yelp_data = None
        trends_data = None

        # ============================================
        # Part 1: YouTube Viral Research (our addition)
        # ============================================
        print("\n[1/5] YouTube Viral Ad Analysis...")
        try:
            youtube_data = await self.youtube_research.run(
                product=product,
                industry=industry,
                duration=duration,
                tone=tone,
                city=city,
                previous_results=previous_results,
            )
            print(f"  ✅ Found {len(youtube_data.get('top_videos', []))} viral videos")
        except Exception as e:
            print(f"  ⚠️ YouTube research failed: {e}")

        # ============================================
        # Part 2: Local Intel - Competitor Discovery & Analysis
        # ============================================
        print("\n[2/5] Local Competitor Intelligence...")
        competitors_for_reviews = []
        try:
            local_report = self.local_intel.analyze(
                business_type=business_type,
                location=city or "United States",
                radius_miles=10.0,
                top_count=5,
                worst_count=3,
                include_worst_rated=True,
            )

            # Extract data for downstream use
            local_intel_data = {
                "competitors_found": len(local_report.competitors),
                "top_competitors": [
                    c.name for c in getattr(local_report, "_top_competitors", [])[:5]
                ],
                "worst_competitors": [
                    c.name for c in getattr(local_report, "_worst_competitors", [])[:3]
                ],
                "headline_suggestions": local_report.headline_suggestions[:10],
                "trust_signals": local_report.trust_signals_to_use[:10],
                "differentiators": [
                    {
                        "angle": d.angle_name,
                        "hook": d.hook,
                        "best_for": d.best_for,
                    }
                    for d in local_report.differentiators[:5]
                ],
            }

            # Get Claude analysis if available
            if (
                hasattr(local_report, "_claude_analysis")
                and local_report._claude_analysis
            ):
                claude = local_report._claude_analysis
                local_intel_data["what_top_competitors_do"] = claude.get(
                    "success_factors", []
                )[:5]
                local_intel_data["what_to_avoid"] = claude.get("failure_patterns", [])[
                    :5
                ]
                local_intel_data["recommendations"] = claude.get("recommendations", [])[
                    :5
                ]

            # Extract competitors with place_ids for review_intel
            competitors_for_reviews = [
                {"name": c.name, "place_id": c.place_id, "rating": c.rating}
                for c in local_report.competitors
                if c.place_id
            ]

            print(f"  ✅ Found {len(local_report.competitors)} competitors")
            if local_intel_data.get("top_competitors"):
                print(
                    f"      Top rated: {', '.join(local_intel_data['top_competitors'][:3])}"
                )
            if local_intel_data.get("worst_competitors"):
                print(
                    f"      Worst rated: {', '.join(local_intel_data['worst_competitors'][:2])}"
                )

        except Exception as e:
            print(f"  ⚠️ Local Intel failed: {e}")
            import traceback

            traceback.print_exc()

        # ============================================
        # Part 3: Google Reviews Analysis (uses place_ids from Local Intel)
        # ============================================
        print("\n[3/5] Google Reviews Analysis...")
        if competitors_for_reviews:
            try:
                review_analysis = self.review_intel.analyze_competitors(
                    competitors=competitors_for_reviews[:5],
                    business_type=business_type,
                    location=city or "United States",
                    reviews_per_competitor=10,
                )

                # Extract voice of customer
                voc = review_analysis.voice_of_customer
                review_data = {
                    "total_reviews": review_analysis.total_reviews_analyzed,
                    "pain_points": [
                        p.get("point", p) if isinstance(p, dict) else p
                        for p in (voc.pain_points if voc else [])[:8]
                    ],
                    "desires": [
                        d.get("desire", d) if isinstance(d, dict) else d
                        for d in (voc.desires if voc else [])[:8]
                    ],
                    "praise_quotes": voc.praise_quotes[:5] if voc else [],
                    "complaint_quotes": voc.complaint_quotes[:5] if voc else [],
                    "ad_hooks": review_analysis.ad_hooks[:5],
                    "headline_suggestions": review_analysis.headline_suggestions[:5],
                }

                print(
                    f"  ✅ Analyzed {review_analysis.total_reviews_analyzed} Google Reviews"
                )

            except Exception as e:
                print(f"  ⚠️ Review Intel failed: {e}")
        else:
            print("  ⚠️ Skipped - no competitors with place_ids from Local Intel")

        # ============================================
        # Part 4: Yelp Reviews Analysis
        # ============================================
        print("\n[4/5] Yelp Reviews Analysis...")
        try:
            yelp_analysis = self.yelp_intel.analyze_market(
                business_type=business_type,
                location=city or "United States",
                max_businesses=5,
                reviews_per_business=15,
            )

            insights = yelp_analysis.insights
            yelp_data = {
                "total_reviews": yelp_analysis.total_reviews_analyzed,
                "businesses_analyzed": len(yelp_analysis.businesses),
                "pain_points": insights.pain_points[:10] if insights else [],
                "praise_points": insights.praise_points[:10] if insights else [],
                "pain_quotes": insights.pain_point_quotes[:5] if insights else [],
                "praise_quotes": insights.praise_quotes[:5] if insights else [],
                "themes": insights.themes[:10] if insights else [],
            }

            # Get ad suggestions
            if yelp_analysis.ad_suggestions:
                yelp_data["hooks"] = yelp_analysis.ad_suggestions.hooks[:5]
                yelp_data["headlines"] = yelp_analysis.ad_suggestions.headlines[:5]

            print(
                f"  ✅ Analyzed {yelp_analysis.total_reviews_analyzed} Yelp reviews from {len(yelp_analysis.businesses)} businesses"
            )

        except Exception as e:
            print(f"  ⚠️ Yelp Intel failed: {e}")

        # ============================================
        # Part 5: Keyword Trends Analysis
        # ============================================
        print("\n[5/5] Keyword Trends Analysis...")
        try:
            # Build keywords from business type
            keywords = [
                business_type,
                f"{business_type} near me",
                f"best {business_type}",
            ]

            trends_analysis = self.trends_intel.analyze(
                keywords=keywords,
                location="United States",
                include_related=True,
            )

            # Extract timing recommendations
            timing_recs = []
            for s in trends_analysis.seasonal_insights[:3]:
                if s.peak_months:
                    month_names = {
                        1: "Jan",
                        2: "Feb",
                        3: "Mar",
                        4: "Apr",
                        5: "May",
                        6: "Jun",
                        7: "Jul",
                        8: "Aug",
                        9: "Sep",
                        10: "Oct",
                        11: "Nov",
                        12: "Dec",
                    }
                    peaks = [month_names.get(m, str(m)) for m in s.peak_months[:3]]
                    timing_recs.append(
                        f"Peak months for '{s.keyword}': {', '.join(peaks)}"
                    )

            trends_data = {
                "keywords_analyzed": len(trends_analysis.keyword_data),
                "keyword_data": [
                    {
                        "keyword": kw.keyword,
                        "search_volume": kw.search_volume,
                        "cpc": kw.cpc,
                    }
                    for kw in trends_analysis.keyword_data[:5]
                ],
                "timing_recommendations": timing_recs,
                "ad_recommendations": getattr(
                    trends_analysis, "ad_recommendations", []
                )[:5]
                if hasattr(trends_analysis, "ad_recommendations")
                and getattr(trends_analysis, "ad_recommendations", None)
                else [],
            }

            print(f"  ✅ Analyzed {len(trends_analysis.keyword_data)} keywords")

        except Exception as e:
            print(f"  ⚠️ Trends Intel failed: {e}")

        # ============================================
        # Combine All Insights
        # ============================================
        print("\n" + "=" * 60)
        print("RESEARCH COMPLETE - Combining Insights")
        print("=" * 60 + "\n")

        combined_insights = self._combine_all_insights(
            youtube_data=youtube_data,
            local_intel_data=local_intel_data,
            review_data=review_data,
            yelp_data=yelp_data,
            trends_data=trends_data,
        )

        return {
            "industry": industry,
            "product": product,
            "city": city,
            # YouTube data
            "viral_videos": youtube_data.get("top_videos", []),
            "viral_patterns": youtube_data.get("patterns_identified", {}),
            "youtube_source": youtube_data.get("source", "none"),
            # Local Intel data (replaces old google_ads)
            "competitor_ads": local_intel_data,  # Keep this key for backward compat
            "local_intel": local_intel_data,
            # Reviews data
            "google_reviews": review_data,
            "yelp_reviews": yelp_data,
            # Trends data
            "keyword_trends": trends_data,
            # Combined insights for script writer
            "insights": combined_insights,
            "videos_analyzed": len(youtube_data.get("top_videos", [])),
            # Summary stats
            "research_summary": {
                "youtube_videos": len(youtube_data.get("top_videos", [])),
                "competitors_found": local_intel_data.get("competitors_found", 0)
                if local_intel_data
                else 0,
                "google_reviews": review_data.get("total_reviews", 0)
                if review_data
                else 0,
                "yelp_reviews": yelp_data.get("total_reviews", 0) if yelp_data else 0,
                "keywords_analyzed": trends_data.get("keywords_analyzed", 0)
                if trends_data
                else 0,
            },
        }

    def _combine_all_insights(
        self,
        youtube_data: dict,
        local_intel_data: Optional[dict],
        review_data: Optional[dict],
        yelp_data: Optional[dict],
        trends_data: Optional[dict],
    ) -> List[str]:
        """Combine ALL research into actionable insights for the script writer."""
        insights = []

        # From YouTube viral patterns
        viral_patterns = youtube_data.get("patterns_identified", {})
        if viral_patterns:
            hooks = viral_patterns.get("common_hooks", [])
            for hook in hooks[:2]:
                insights.append(f"🎬 Viral hook pattern: {hook}")

        # From Local Intel - competitor analysis
        if local_intel_data:
            # Success factors from Claude analysis
            for tip in local_intel_data.get("what_top_competitors_do", [])[:2]:
                insights.append(f"✅ Top competitors: {tip}")

            # Failure patterns to avoid
            for avoid in local_intel_data.get("what_to_avoid", [])[:2]:
                insights.append(f"❌ Avoid: {avoid}")

            # Differentiators
            for diff in local_intel_data.get("differentiators", [])[:2]:
                insights.append(
                    f"💡 Angle: {diff.get('angle', '')} - {diff.get('hook', '')}"
                )

        # From Google Reviews - Customer voice
        if review_data:
            for pain in review_data.get("pain_points", [])[:2]:
                insights.append(f"😤 Customer pain point: {pain} - ADDRESS THIS")
            for desire in review_data.get("desires", [])[:2]:
                insights.append(f"💭 Customers want: {desire}")
            for hook in review_data.get("ad_hooks", [])[:1]:
                insights.append(f"📢 Hook from reviews: {hook}")

        # From Yelp - Pain/praise
        if yelp_data:
            for pain in yelp_data.get("pain_points", [])[:2]:
                insights.append(f"⭐ Yelp complaint: {pain}")
            for praise in yelp_data.get("praise_points", [])[:2]:
                insights.append(f"🏆 Yelp praise: {praise}")

        # From Trends - Timing
        if trends_data:
            for timing in trends_data.get("timing_recommendations", [])[:1]:
                insights.append(f"📅 {timing}")
            for rec in trends_data.get("ad_recommendations", [])[:1]:
                insights.append(f"🎯 {rec}")

        if not insights:
            insights = ["Focus on clear value proposition and customer trust signals"]

        return insights


# Make it compatible with the pipeline's Agent class pattern
class ResearchAgent(EnhancedResearchAgent):
    """Alias for pipeline compatibility"""

    pass
