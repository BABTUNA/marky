"""
Marky Workflow - Sequential agent orchestration.

Runs the intelligence agents in sequence and synthesizes results.
"""

import os
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from dotenv import load_dotenv
load_dotenv()

from .models import (
    AdResearchRequest,
    AdResearchResult,
    AdResearchResponse,
    CompetitorInsight,
    CustomerVoice,
    SeasonalTiming,
    AdDifferentiator,
)

# Import our agents
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from local_intel.agent import LocalIntelAgent
from review_intel.agent import ReviewIntelAgent
from yelp_intel.agent import YelpIntelAgent
from trends_intel.agent import TrendsIntelAgent


class MarkyWorkflow:
    """
    Sequential workflow that orchestrates all intelligence agents.
    
    Pipeline:
    1. Local Intel - Find competitors, scrape websites
    2. Review Intel - Google Reviews from competitors (needs place_ids from Local)
    3. Yelp Intel - Extract customer voice from Yelp reviews
    4. Trends Intel - Get seasonal timing data
    5. Synthesis - Combine insights into ad recommendations
    """
    
    def __init__(self):
        """Initialize the workflow with agent instances."""
        self.local_intel = LocalIntelAgent()
        self.review_intel = ReviewIntelAgent()
        self.yelp_intel = YelpIntelAgent()
        self.trends_intel = TrendsIntelAgent()
        
    def run(
        self,
        request: AdResearchRequest,
        progress_callback: Optional[callable] = None,
    ) -> AdResearchResponse:
        """
        Run the complete ad research workflow.
        
        Args:
            request: The research request
            progress_callback: Optional callback for progress updates
            
        Returns:
            Complete AdResearchResponse
        """
        start_time = time.time()
        
        result = AdResearchResult(
            business_type=request.business_type,
            location=request.location,
        )
        
        def log(msg: str):
            print(msg)
            if progress_callback:
                progress_callback(msg)
        
        try:
            # ================================================================
            # Stage 1: Local Intelligence
            # ================================================================
            log("🔍 Stage 1/5: Running Local Intelligence...")
            
            local_report = None
            try:
                local_report = self.local_intel.analyze(
                    business_type=request.business_type,
                    location=request.location,
                    radius_miles=10.0,
                    top_count=request.max_competitors,
                    worst_count=2,
                    include_worst_rated=True,
                )
                
                result.agents_used.append("local_intel")
                
                # Extract competitor insights
                for comp in local_report.competitors[:request.max_competitors]:
                    insight = CompetitorInsight(
                        name=comp.name,
                        rating=comp.rating or 0.0,
                        review_count=comp.review_count or 0,
                        website=comp.website,
                        strengths=comp.trust_signals[:5] if comp.trust_signals else [],
                        weaknesses=[],  # Not available in source model
                        services=comp.services[:10] if comp.services else [],
                    )
                    result.competitors.append(insight)
                
                # Extract differentiators
                if local_report.differentiators:
                    for diff in local_report.differentiators[:5]:
                        ad_diff = AdDifferentiator(
                            angle_name=diff.angle_name,
                            hook=diff.hook,
                            headline=diff.hook,  # Use hook as headline
                            description=", ".join(diff.supporting_points[:3]) if diff.supporting_points else "",
                            best_for=diff.best_for,
                            trust_signals=[],  # Not available in source model
                        )
                        result.differentiators.append(ad_diff)
                
                # Headlines and trust signals
                result.headline_suggestions = local_report.headline_suggestions[:10]
                result.trust_signals = local_report.trust_signals_to_use[:10]
                
                # Market summary from analysis
                if local_report.market_analysis:
                    ma = local_report.market_analysis
                    # Build summary from available fields
                    parts = []
                    if ma.common_services:
                        parts.append(f"Common services: {', '.join(ma.common_services[:5])}")
                    if ma.service_gaps:
                        parts.append(f"Gaps: {', '.join(ma.service_gaps[:3])}")
                    result.market_summary = ". ".join(parts) if parts else ""
                    
                log(f"  ✓ Found {len(result.competitors)} competitors")
                
            except Exception as e:
                result.errors.append(f"local_intel: {str(e)}")
                log(f"  ⚠ Local Intel error: {e}")
            
            # ================================================================
            # Stage 2: Review Intelligence (Google Reviews - needs place_ids)
            # ================================================================
            log("📋 Stage 2/5: Running Review Intelligence (Google Reviews)...")
            
            try:
                if local_report and local_report.competitors:
                    competitors_with_place_id = [
                        {"name": c.name, "place_id": c.place_id, "rating": c.rating}
                        for c in local_report.competitors[:request.max_competitors]
                        if c.place_id
                    ]
                    if competitors_with_place_id:
                        review_analysis = self.review_intel.analyze_competitors(
                            competitors=competitors_with_place_id,
                            business_type=request.business_type,
                            location=request.location,
                            reviews_per_competitor=min(request.reviews_per_competitor, 10),
                        )
                        result.agents_used.append("review_intel")
                        
                        # Add Review Intel voice-of-customer (Yelp will merge later)
                        if review_analysis.voice_of_customer:
                            voc = review_analysis.voice_of_customer
                            pain_strs = [p["point"] for p in voc.pain_points[:8] if isinstance(p, dict) and p.get("point")]
                            desire_strs = [d["desire"] for d in voc.desires[:8] if isinstance(d, dict) and d.get("desire")]
                            
                            result.customer_voice = CustomerVoice(
                                pain_points=pain_strs,
                                desires=desire_strs,
                                praise_quotes=voc.praise_quotes[:5],
                                complaint_quotes=voc.complaint_quotes[:5],
                                common_themes=review_analysis.top_competitor_themes[:5],
                            )
                        
                        result.recommended_hooks.extend(review_analysis.ad_hooks[:5])
                        result.headline_suggestions.extend(review_analysis.headline_suggestions[:5])
                        
                        log(f"  ✓ Analyzed {review_analysis.total_reviews_analyzed} Google Reviews")
                    else:
                        log("  ⚠ No competitors with place_ids for Google Reviews")
                else:
                    log("  ⚠ Skipped (no local_intel competitors)")
                    
            except Exception as e:
                result.errors.append(f"review_intel: {str(e)}")
                log(f"  ⚠ Review Intel error: {e}")
            
            # ================================================================
            # Stage 3: Yelp Intelligence
            # ================================================================
            log("🗣️ Stage 3/5: Running Yelp Intelligence...")
            
            try:
                yelp_analysis = self.yelp_intel.analyze_market(
                    business_type=request.business_type,
                    location=request.location,
                    max_businesses=min(5, request.max_competitors),
                    reviews_per_business=request.reviews_per_competitor,
                )
                
                result.agents_used.append("yelp_intel")
                
                # Extract and merge customer voice (Review Intel may have run first)
                if yelp_analysis.insights:
                    insights = yelp_analysis.insights
                    yelp_voice = CustomerVoice(
                        pain_points=insights.pain_points[:10],
                        desires=insights.praise_points[:10],
                        praise_quotes=insights.praise_quotes[:5],
                        complaint_quotes=insights.pain_point_quotes[:5],
                        common_themes=insights.themes[:10] if insights.themes else [],
                    )
                    # Merge with Review Intel if present
                    if result.customer_voice:
                        result.customer_voice.pain_points = list(dict.fromkeys(
                            result.customer_voice.pain_points + yelp_voice.pain_points
                        ))[:12]
                        result.customer_voice.desires = list(dict.fromkeys(
                            result.customer_voice.desires + yelp_voice.desires
                        ))[:12]
                        result.customer_voice.praise_quotes = (result.customer_voice.praise_quotes + yelp_voice.praise_quotes)[:8]
                        result.customer_voice.complaint_quotes = (result.customer_voice.complaint_quotes + yelp_voice.complaint_quotes)[:8]
                        result.customer_voice.common_themes = list(dict.fromkeys(
                            result.customer_voice.common_themes + yelp_voice.common_themes
                        ))[:10]
                    else:
                        result.customer_voice = yelp_voice
                    
                    # Add Yelp-generated hooks to recommendations
                    if yelp_analysis.ad_suggestions:
                        result.recommended_hooks.extend(
                            yelp_analysis.ad_suggestions.hooks[:5]
                        )
                        result.headline_suggestions.extend(
                            yelp_analysis.ad_suggestions.headlines[:5]
                        )
                
                log(f"  ✓ Analyzed {yelp_analysis.total_reviews_analyzed} reviews")
                
            except Exception as e:
                result.errors.append(f"yelp_intel: {str(e)}")
                log(f"  ⚠ Yelp Intel error: {e}")
            
            # ================================================================
            # Stage 3: Trends Intelligence
            # ================================================================
            if request.include_trends:
                log("📈 Stage 4/5: Running Trends Intelligence...")
                
                try:
                    # Build keywords from business type
                    keywords = [
                        request.business_type,
                        f"{request.business_type} near me",
                        f"best {request.business_type}",
                    ]
                    
                    trends_analysis = self.trends_intel.analyze(
                        keywords=keywords,
                        location="United States",
                        include_related=True,
                    )
                    
                    result.agents_used.append("trends_intel")
                    
                    # Month number to name mapping
                    month_names = {
                        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
                        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
                        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
                    }
                    
                    # Extract timing recommendations
                    for kw_data in trends_analysis.keyword_data[:3]:
                        seasonal = None
                        for s in trends_analysis.seasonal_insights:
                            if s.keyword == kw_data.keyword:
                                seasonal = s
                                break
                        
                        # Convert month ints to strings
                        peak_strs = [month_names.get(m, str(m)) for m in (seasonal.peak_months if seasonal else [])]
                        low_strs = [month_names.get(m, str(m)) for m in (seasonal.low_months if seasonal else [])]
                        
                        timing = SeasonalTiming(
                            keyword=kw_data.keyword,
                            peak_months=peak_strs,
                            low_months=low_strs,
                            avg_cpc=kw_data.cpc or 0.0,
                            monthly_volume=kw_data.search_volume or 0,
                            recommendation=seasonal.recommendation if seasonal else "",
                        )
                        result.timing.append(timing)
                    
                    log(f"  ✓ Analyzed {len(keywords)} keywords")
                    
                except Exception as e:
                    result.errors.append(f"trends_intel: {str(e)}")
                    log(f"  ⚠ Trends Intel error: {e}")
            else:
                log("📈 Stage 4/5: Trends Intelligence (skipped)")
            
            # ================================================================
            # Stage 5: Synthesis
            # ================================================================
            log("🧠 Stage 5/5: Synthesizing insights...")
            
            result.key_insights = self._generate_key_insights(result)
            result.executive_summary = self._generate_executive_summary(result)
            
            # Deduplicate and prioritize hooks
            all_hooks = list(dict.fromkeys(result.recommended_hooks))  # preserve order
            result.recommended_hooks = all_hooks[:10]
            
            # Deduplicate headlines and trust signals
            result.headline_suggestions = list(dict.fromkeys(result.headline_suggestions))[:15]
            result.trust_signals = list(dict.fromkeys(result.trust_signals))[:10]
            
            log("  ✓ Synthesis complete")
            
            # ================================================================
            # Finalize
            # ================================================================
            result.total_time_seconds = time.time() - start_time
            
            log(f"\n✅ Complete! ({result.total_time_seconds:.1f}s)")
            
            return AdResearchResponse(success=True, result=result)
            
        except Exception as e:
            result.total_time_seconds = time.time() - start_time
            result.errors.append(f"workflow: {str(e)}")
            return AdResearchResponse(
                success=False,
                result=result,
                error=str(e),
            )
    
    def _generate_key_insights(self, result: AdResearchResult) -> List[str]:
        """Generate key insights from the collected data."""
        insights = []
        
        # Competitor insights
        if result.competitors:
            avg_rating = sum(c.rating for c in result.competitors) / len(result.competitors)
            insights.append(
                f"Market has {len(result.competitors)} competitors with avg rating {avg_rating:.1f}⭐"
            )
            
            top_comp = max(result.competitors, key=lambda c: c.rating)
            insights.append(
                f"Top competitor: {top_comp.name} ({top_comp.rating}⭐, {top_comp.review_count} reviews)"
            )
        
        # Customer voice insights
        if result.customer_voice:
            if result.customer_voice.pain_points:
                pt = result.customer_voice.pain_points[0]
                pt = pt[:80] + "..." if len(pt) > 80 else pt
                insights.append(f"Top customer pain point: {pt}")
            if result.customer_voice.desires:
                d = result.customer_voice.desires[0]
                d = d[:80] + "..." if len(d) > 80 else d
                insights.append(f"What customers want most: {d}")
        
        # Timing insights
        if result.timing:
            best_timing = result.timing[0]
            if best_timing.peak_months:
                insights.append(
                    f"Best months to advertise: {', '.join(best_timing.peak_months[:3])}"
                )
            if best_timing.avg_cpc > 0:
                insights.append(
                    f"Average CPC for '{best_timing.keyword}': ${best_timing.avg_cpc:.2f}"
                )
        
        return insights[:7]
    
    def _generate_executive_summary(self, result: AdResearchResult) -> str:
        """Generate an executive summary from the results."""
        parts = []
        
        parts.append(
            f"Analysis of {result.business_type} market in {result.location}."
        )
        
        if result.competitors:
            parts.append(
                f"Identified {len(result.competitors)} competitors in the area."
            )
        
        if result.customer_voice and result.customer_voice.pain_points:
            pts = [p[:60] + "..." if len(p) > 60 else p for p in result.customer_voice.pain_points[:3]]
            parts.append(
                f"Key customer pain points include: {'; '.join(pts)}."
            )
        
        if result.timing and result.timing[0].peak_months:
            parts.append(
                f"Best time to run ads: {', '.join(result.timing[0].peak_months[:2])}."
            )
        
        if result.differentiators:
            parts.append(
                f"Top differentiation angle: {result.differentiators[0].angle_name}."
            )
        
        return " ".join(parts)


def run_workflow(
    business_type: str,
    location: str,
    max_competitors: int = 5,
    include_trends: bool = True,
) -> AdResearchResponse:
    """
    Convenience function to run the Marky workflow.
    
    Args:
        business_type: Type of business (e.g., "plumber")
        location: Location (e.g., "Providence, RI")
        max_competitors: Maximum competitors to analyze
        include_trends: Whether to include trends analysis
        
    Returns:
        AdResearchResponse with results
    """
    workflow = MarkyWorkflow()
    request = AdResearchRequest(
        business_type=business_type,
        location=location,
        max_competitors=max_competitors,
        include_trends=include_trends,
    )
    return workflow.run(request)
