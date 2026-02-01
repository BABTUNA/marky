"""
Enhanced Research Agent
Combines YouTube viral ad analysis with Google Ads competitor intelligence
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

from agents.research_agent import ResearchAgent as YouTubeResearch
from ad_intel_no.agent import AdIntelAgent

load_dotenv()


class EnhancedResearchAgent:
    """
    Enhanced research that combines:
    1. YouTube viral ad analysis (what works in viral content)
    2. Google Ads competitor intelligence (what competitors are doing)
    """
    
    def __init__(self):
        self.youtube_research = YouTubeResearch()
        
        # Google Ads research (optional - requires SERPAPI_KEY)
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        if self.serpapi_key:
            self.ad_intel = AdIntelAgent(api_key=self.serpapi_key)
        else:
            self.ad_intel = None
    
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
        Perform comprehensive research combining YouTube and Google Ads.
        
        Returns:
            Combined research insights with viral patterns and competitor strategies
        """
        print("\n" + "="*60)
        print("ENHANCED RESEARCH AGENT")
        print("="*60)
        
        # Part 1: YouTube Viral Research
        print("\n[1/2] YouTube Viral Ad Analysis...")
        youtube_data = await self.youtube_research.run(
            product=product,
            industry=industry,
            duration=duration,
            tone=tone,
            city=city,
            previous_results=previous_results
        )
        
        # Part 2: Google Ads Competitor Intelligence (if available)
        google_ads_data = None
        if self.ad_intel and city:
            print("\n[2/2] Google Ads Competitor Intelligence...")
            try:
                analysis = self.ad_intel.analyze_market(
                    business_type=f"{industry} {product}".strip(),
                    location=city,
                    max_ads=20  # Limit for speed
                )
                
                google_ads_data = {
                    "competitors_found": analysis.competitors_found,
                    "total_ads_analyzed": analysis.total_ads_analyzed,
                    "hook_suggestions": analysis.hook_suggestions,
                    "headline_suggestions": analysis.headline_suggestions,
                    "cta_suggestions": analysis.cta_suggestions,
                    "creative_suggestions": analysis.creative_suggestions,
                    "messaging_gaps": analysis.messaging_gaps,
                    "patterns": analysis.patterns.to_dict() if analysis.patterns else None
                }
                
                print(f"  ✅ Analyzed {analysis.total_ads_analyzed} competitor ads")
                print(f"  ✅ Found {analysis.competitors_found} competitors")
                
            except Exception as e:
                print(f"  ⚠️ Google Ads analysis failed: {e}")
        else:
            print("\n[2/2] Google Ads Competitor Intelligence...")
            if not self.ad_intel:
                print("  ⚠️ Skipped - no SERPAPI_KEY found")
            elif not city:
                print("  ⚠️ Skipped - no city location provided")
        
        # Combine insights
        print("\n" + "="*60)
        print("RESEARCH COMPLETE")
        print("="*60 + "\n")
        
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
            
            # Combined insights for script writer
            "insights": self._combine_insights(youtube_data, google_ads_data),
            "videos_analyzed": len(youtube_data.get("top_videos", [])),
        }
    
    def _combine_insights(self, youtube_data: dict, google_ads_data: Optional[dict]) -> List[str]:
        """Combine YouTube and Google Ads insights into actionable recommendations."""
        insights = []
        
        # From YouTube viral patterns
        viral_patterns = youtube_data.get("patterns_identified", {})
        if viral_patterns:
            hooks = viral_patterns.get("common_hooks", [])
            for hook in hooks[:3]:
                insights.append(f"Viral hook: {hook}")
        
        # From Google Ads competitor analysis
        if google_ads_data:
            # Add hook suggestions
            for hook in google_ads_data.get("hook_suggestions", [])[:3]:
                insights.append(f"Competitor hook: {hook}")
            
            # Add messaging gaps (opportunities)
            for gap in google_ads_data.get("messaging_gaps", [])[:2]:
                insights.append(f"Opportunity: {gap}")
        
        return insights if insights else ["Generic: Focus on clear value proposition"]


# Make it compatible with the pipeline's Agent class pattern
class ResearchAgent(EnhancedResearchAgent):
    """Alias for pipeline compatibility"""
    pass
