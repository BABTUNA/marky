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
from related_questions_intel.agent import RelatedQuestionsIntelAgent


class MarkyWorkflow:
    """
    Sequential workflow that orchestrates all intelligence agents.
    
    Pipeline (raw data collection, no filtering):
    1. Local Intel - Find competitors, scrape websites
    2. Review Intel - Google Reviews from competitors (needs place_ids from Local)
    3. Yelp Intel - Extract customer voice from Yelp reviews
    4. Trends Intel - Get seasonal timing data
    5. Related Questions Intel - People also ask (content/intent)
    6. Output - All collected data combined, unfiltered
    """

    def __init__(self):
        """Initialize the workflow with agent instances."""
        self.local_intel = LocalIntelAgent()
        self.review_intel = ReviewIntelAgent()
        self.yelp_intel = YelpIntelAgent()
        self.trends_intel = TrendsIntelAgent()
        self.related_questions_intel = RelatedQuestionsIntelAgent()
        
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
            log("🔍 Stage 1/6: Running Local Intelligence...")
            
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
                
                # Extract competitor insights (raw, no limits)
                for comp in local_report.competitors[:request.max_competitors]:
                    insight = CompetitorInsight(
                        name=comp.name,
                        rating=comp.rating or 0.0,
                        review_count=comp.review_count or 0,
                        website=comp.website,
                        strengths=comp.trust_signals or [],
                        weaknesses=[],  # Not available in source model
                        services=comp.services or [],
                    )
                    result.competitors.append(insight)
                
                # Extract differentiators (raw, no limits)
                if local_report.differentiators:
                    for diff in local_report.differentiators:
                        ad_diff = AdDifferentiator(
                            angle_name=diff.angle_name,
                            hook=diff.hook,
                            headline=diff.hook,  # Use hook as headline
                            description=", ".join(diff.supporting_points) if diff.supporting_points else "",
                            best_for=diff.best_for,
                            trust_signals=[],  # Not available in source model
                        )
                        result.differentiators.append(ad_diff)
                
                # Headlines and trust signals (raw, no limits)
                result.headline_suggestions = local_report.headline_suggestions
                result.trust_signals = local_report.trust_signals_to_use
                
                # Market summary from analysis
                if local_report.market_analysis:
                    ma = local_report.market_analysis
                    # Build summary from available fields
                    parts = []
                    if ma.common_services:
                        parts.append(f"Common services: {', '.join(ma.common_services)}")
                    if ma.service_gaps:
                        parts.append(f"Gaps: {', '.join(ma.service_gaps)}")
                    result.market_summary = ". ".join(parts) if parts else ""
                    
                log(f"  ✓ Found {len(result.competitors)} competitors")
                
            except Exception as e:
                result.errors.append(f"local_intel: {str(e)}")
                log(f"  ⚠ Local Intel error: {e}")
            
            # ================================================================
            # Stage 2: Review Intelligence (Google Reviews - needs place_ids)
            # ================================================================
            log("📋 Stage 2/6: Running Review Intelligence (Google Reviews)...")
            
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
                            pain_strs = [p["point"] for p in voc.pain_points if isinstance(p, dict) and p.get("point")]
                            desire_strs = [d["desire"] for d in voc.desires if isinstance(d, dict) and d.get("desire")]
                            
                            result.customer_voice = CustomerVoice(
                                pain_points=pain_strs,
                                desires=desire_strs,
                                praise_quotes=voc.praise_quotes,
                                complaint_quotes=voc.complaint_quotes,
                                common_themes=review_analysis.top_competitor_themes,
                            )
                        
                        result.recommended_hooks.extend(review_analysis.ad_hooks)
                        result.headline_suggestions.extend(review_analysis.headline_suggestions)
                        
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
            log("🗣️ Stage 3/6: Running Yelp Intelligence...")
            
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
                    # Merge with Review Intel if present (raw merge, no dedup)
                    if result.customer_voice:
                        result.customer_voice.pain_points = result.customer_voice.pain_points + yelp_voice.pain_points
                        result.customer_voice.desires = result.customer_voice.desires + yelp_voice.desires
                        result.customer_voice.praise_quotes = result.customer_voice.praise_quotes + yelp_voice.praise_quotes
                        result.customer_voice.complaint_quotes = result.customer_voice.complaint_quotes + yelp_voice.complaint_quotes
                        result.customer_voice.common_themes = result.customer_voice.common_themes + yelp_voice.common_themes
                    else:
                        result.customer_voice = yelp_voice
                    
                    # Add Yelp-generated hooks (raw, no filter)
                    if yelp_analysis.ad_suggestions:
                        result.recommended_hooks.extend(yelp_analysis.ad_suggestions.hooks)
                        result.headline_suggestions.extend(yelp_analysis.ad_suggestions.headlines)
                
                log(f"  ✓ Analyzed {yelp_analysis.total_reviews_analyzed} reviews")
                
            except Exception as e:
                result.errors.append(f"yelp_intel: {str(e)}")
                log(f"  ⚠ Yelp Intel error: {e}")
            
            # ================================================================
            # Stage 4: Trends Intelligence
            # ================================================================
            if request.include_trends:
                log("📈 Stage 4/6: Running Trends Intelligence...")
                
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
                log("📈 Stage 4/6: Trends Intelligence (skipped)")

            # ================================================================
            # Stage 5: Related Questions Intelligence
            # ================================================================
            log("❓ Stage 5/6: Running Related Questions Intelligence...")
            try:
                rq_analysis = self.related_questions_intel.analyze(
                    business_type=request.business_type,
                    location=request.location,
                    seed_queries=None,
                    max_questions_per_query=15,
                )
                result.agents_used.append("related_questions_intel")
                result.related_questions = rq_analysis.all_questions()
                log(f"  ✓ Collected {len(result.related_questions)} related questions")
            except Exception as e:
                result.errors.append(f"related_questions_intel: {str(e)}")
                log(f"  ⚠ Related Questions Intel error: {e}")

            # ================================================================
            # Stage 6: Data Collection Complete (no filtering)
            # ================================================================
            log("📦 Stage 6/6: Raw data collection complete...")
            log("  ✓ All data collected (unfiltered)")
            
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
