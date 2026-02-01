"""
Enhanced Research Agent - Full "Marky" Research Suite

Combines ALL research sources:
1. YouTube viral ad analysis (what works in viral content)
2. Google Ads competitor intelligence (what competitors are doing)
3. Google Reviews analysis (customer voice - complaints & praises)
4. Yelp reviews analysis (customer language & expectations)
5. Keyword trends (search volume, CPC, competition)
6. Website scraping (competitor messaging & positioning)
"""

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

from ad_intel_no.agent import AdIntelAgent
from ad_intel_no.review_intel import ReviewIntelAgent
from ad_intel_no.trends_intel import TrendsIntelAgent
from ad_intel_no.website_intel import WebsiteIntelAgent
from ad_intel_no.yelp_intel import YelpIntelAgent
from agents.research_agent import ResearchAgent as YouTubeResearch

load_dotenv()


class EnhancedResearchAgent:
    """
    Full "Marky" research suite that combines:
    1. YouTube viral ad analysis
    2. Google Ads competitor intelligence
    3. Google Reviews (customer pain points & praises)
    4. Yelp reviews (customer voice)
    5. Keyword trends (DataForSEO)
    6. Website scraping (competitor messaging)
    """

    def __init__(self):
        self.youtube_research = YouTubeResearch()

        # All research agents (optional - require API keys)
        self.serpapi_key = os.getenv("SERPAPI_KEY")

        # Initialize agents that need SERPAPI
        if self.serpapi_key:
            self.ad_intel = AdIntelAgent(api_key=self.serpapi_key)
            self.review_intel = ReviewIntelAgent(api_key=self.serpapi_key)
            self.yelp_intel = YelpIntelAgent(api_key=self.serpapi_key)
        else:
            self.ad_intel = None
            self.review_intel = None
            self.yelp_intel = None

        # Trends agent (uses DataForSEO)
        self.trends_intel = TrendsIntelAgent()

        # Website scraper (uses Firecrawl/Jina)
        self.website_intel = WebsiteIntelAgent()

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
        Perform comprehensive research using ALL available sources.

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
        google_ads_data = None
        review_data = None
        yelp_data = None
        trends_data = None
        website_data = None

        # ============================================
        # Part 1: YouTube Viral Research
        # ============================================
        print("\n[1/6] YouTube Viral Ad Analysis...")
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
        # Part 2: Google Ads Competitor Intelligence
        # ============================================
        print("\n[2/6] Google Ads Competitor Intelligence...")
        if self.ad_intel and city:
            try:
                analysis = self.ad_intel.analyze_market(
                    business_type=business_type, location=city, max_ads=20
                )

                google_ads_data = {
                    "competitors_found": analysis.competitors_found,
                    "total_ads_analyzed": analysis.total_ads_analyzed,
                    "hook_suggestions": analysis.hook_suggestions,
                    "headline_suggestions": analysis.headline_suggestions,
                    "cta_suggestions": analysis.cta_suggestions,
                    "creative_suggestions": analysis.creative_suggestions,
                    "messaging_gaps": analysis.messaging_gaps,
                    "patterns": analysis.patterns.to_dict()
                    if analysis.patterns
                    else None,
                }

                print(f"  ✅ Analyzed {analysis.total_ads_analyzed} competitor ads")

            except Exception as e:
                print(f"  ⚠️ Google Ads analysis failed: {e}")
        else:
            print("  ⚠️ Skipped - no SERPAPI_KEY or city")

        # ============================================
        # Part 3: Google Reviews Analysis
        # ============================================
        print("\n[3/6] Google Reviews Analysis...")
        if self.review_intel and city:
            try:
                review_analysis = self.review_intel.analyze_market_reviews(
                    business_type=business_type,
                    location=city,
                    max_businesses=5,
                    reviews_per_business=10,
                )

                review_data = {
                    "total_reviews": review_analysis.total_reviews,
                    "avg_rating": review_analysis.average_rating,
                    "common_complaints": review_analysis.common_complaints,
                    "common_praises": review_analysis.common_praises,
                    "customer_language": review_analysis.customer_language,
                    "opportunities": review_analysis.opportunities,
                }

                print(f"  ✅ Analyzed {review_analysis.total_reviews} reviews")

            except Exception as e:
                print(f"  ⚠️ Reviews analysis failed: {e}")
        else:
            print("  ⚠️ Skipped - no SERPAPI_KEY or city")

        # ============================================
        # Part 4: Yelp Reviews Analysis
        # ============================================
        print("\n[4/6] Yelp Reviews Analysis...")
        if self.yelp_intel and city:
            try:
                yelp_analysis = self.yelp_intel.analyze_market(
                    business_type=business_type, location=city, max_businesses=10
                )

                yelp_data = {
                    "businesses_analyzed": yelp_analysis.businesses_analyzed,
                    "avg_market_rating": yelp_analysis.avg_market_rating,
                    "what_customers_love": yelp_analysis.what_customers_love,
                    "what_customers_hate": yelp_analysis.what_customers_hate,
                    "customer_phrases": yelp_analysis.customer_phrases,
                    "top_rated_traits": yelp_analysis.top_rated_traits,
                }

                print(
                    f"  ✅ Analyzed {yelp_analysis.businesses_analyzed} Yelp listings"
                )

            except Exception as e:
                print(f"  ⚠️ Yelp analysis failed: {e}")
        else:
            print("  ⚠️ Skipped - no SERPAPI_KEY or city")

        # ============================================
        # Part 5: Keyword Trends Analysis
        # ============================================
        print("\n[5/6] Keyword Trends Analysis...")
        try:
            trends_analysis = self.trends_intel.analyze_keywords(
                business_type=business_type, location=city or "United States"
            )

            trends_data = {
                "high_volume_keywords": trends_analysis.high_volume_keywords,
                "low_competition_keywords": trends_analysis.low_competition_keywords,
                "best_keywords_for_ads": trends_analysis.best_keywords_for_ads,
                "seasonal_insights": trends_analysis.seasonal_insights,
            }

            print(f"  ✅ Analyzed {len(trends_analysis.keywords)} keywords")

        except Exception as e:
            print(f"  ⚠️ Trends analysis failed: {e}")

        # ============================================
        # Part 6: Website Intelligence (if we have competitor URLs)
        # ============================================
        print("\n[6/6] Website Intelligence...")
        competitor_urls = []

        # Extract URLs from Google Ads results
        if google_ads_data and google_ads_data.get("patterns"):
            patterns = google_ads_data.get("patterns", {})
            # URLs would be in competitor ads - but we'd need to store them

        if competitor_urls:
            try:
                website_analysis = self.website_intel.analyze_competitor_websites(
                    urls=competitor_urls,
                    business_type=business_type,
                    location=city or "",
                )

                website_data = {
                    "websites_analyzed": website_analysis.websites_analyzed,
                    "common_headlines": website_analysis.common_headlines,
                    "common_offers": website_analysis.common_offers,
                    "common_trust_signals": website_analysis.common_trust_signals,
                    "differentiation_opportunities": website_analysis.differentiation_opportunities,
                }

                print(f"  ✅ Analyzed {website_analysis.websites_analyzed} websites")

            except Exception as e:
                print(f"  ⚠️ Website analysis failed: {e}")
        else:
            print("  ⚠️ Skipped - no competitor URLs found")

        # ============================================
        # Combine All Insights
        # ============================================
        print("\n" + "=" * 60)
        print("RESEARCH COMPLETE - Combining Insights")
        print("=" * 60 + "\n")

        combined_insights = self._combine_all_insights(
            youtube_data=youtube_data,
            google_ads_data=google_ads_data,
            review_data=review_data,
            yelp_data=yelp_data,
            trends_data=trends_data,
            website_data=website_data,
        )

        return {
            "industry": industry,
            "product": product,
            "city": city,
            # YouTube data
            "viral_videos": youtube_data.get("top_videos", []),
            "viral_patterns": youtube_data.get("patterns_identified", {}),
            "youtube_source": youtube_data.get("source", "none"),
            # Google Ads data
            "competitor_ads": google_ads_data,
            # NEW: Reviews data
            "google_reviews": review_data,
            "yelp_reviews": yelp_data,
            # NEW: Trends data
            "keyword_trends": trends_data,
            # NEW: Website data
            "competitor_websites": website_data,
            # Combined insights for script writer
            "insights": combined_insights,
            "videos_analyzed": len(youtube_data.get("top_videos", [])),
            # Summary stats
            "research_summary": {
                "youtube_videos": len(youtube_data.get("top_videos", [])),
                "google_ads": google_ads_data.get("total_ads_analyzed", 0)
                if google_ads_data
                else 0,
                "reviews_analyzed": (
                    review_data.get("total_reviews", 0) if review_data else 0
                ),
                "yelp_businesses": (
                    yelp_data.get("businesses_analyzed", 0) if yelp_data else 0
                ),
                "keywords_analyzed": len(trends_data.get("high_volume_keywords", []))
                if trends_data
                else 0,
            },
        }

    def _combine_all_insights(
        self,
        youtube_data: dict,
        google_ads_data: Optional[dict],
        review_data: Optional[dict],
        yelp_data: Optional[dict],
        trends_data: Optional[dict],
        website_data: Optional[dict],
    ) -> List[str]:
        """Combine ALL research into actionable insights for the script writer."""
        insights = []

        # From YouTube viral patterns
        viral_patterns = youtube_data.get("patterns_identified", {})
        if viral_patterns:
            hooks = viral_patterns.get("common_hooks", [])
            for hook in hooks[:2]:
                insights.append(f"🎬 Viral hook: {hook}")

        # From Google Ads competitor analysis
        if google_ads_data:
            for hook in google_ads_data.get("hook_suggestions", [])[:2]:
                insights.append(f"📢 Competitor hook: {hook}")
            for gap in google_ads_data.get("messaging_gaps", [])[:1]:
                insights.append(f"💡 Opportunity: {gap}")

        # From Google Reviews - CUSTOMER VOICE
        if review_data:
            # Pain points to address
            for complaint in review_data.get("common_complaints", [])[:2]:
                insights.append(
                    f"😤 Customers complain about: {complaint} - ADDRESS THIS"
                )
            # What they love
            for praise in review_data.get("common_praises", [])[:2]:
                insights.append(f"😊 Customers love: {praise} - HIGHLIGHT THIS")
            # Customer language
            for phrase in review_data.get("customer_language", [])[:1]:
                insights.append(f"💬 Use customer language: '{phrase}'")

        # From Yelp
        if yelp_data:
            for love in yelp_data.get("what_customers_love", [])[:1]:
                insights.append(f"⭐ Yelp customers value: {love}")
            for trait in yelp_data.get("top_rated_traits", [])[:1]:
                insights.append(f"🏆 Top-rated businesses have: {trait}")

        # From Trends
        if trends_data:
            for kw in trends_data.get("best_keywords_for_ads", [])[:1]:
                insights.append(f"🔍 Target keyword: {kw}")
            for seasonal in trends_data.get("seasonal_insights", [])[:1]:
                insights.append(f"📅 Seasonal: {seasonal}")

        # From Website analysis
        if website_data:
            for opp in website_data.get("differentiation_opportunities", [])[:1]:
                insights.append(f"🎯 Differentiation: {opp}")

        if not insights:
            insights = ["Focus on clear value proposition and customer trust signals"]

        return insights


# Make it compatible with the pipeline's Agent class pattern
class ResearchAgent(EnhancedResearchAgent):
    """Alias for pipeline compatibility"""

    pass
