"""
Trends Intelligence Agent.
Analyzes keyword trends for seasonal advertising insights.
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from collections import Counter

from .models import (
    KeywordData,
    TrendData,
    SeasonalInsight,
    AdTimingRecommendation,
    TrendsAnalysis,
)
from .scraper import DataForSEOClient


# Month names for display
MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}

SHORT_MONTHS = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

# Season definitions
SEASONS = {
    "Winter": [12, 1, 2],
    "Spring": [3, 4, 5],
    "Summer": [6, 7, 8],
    "Fall": [9, 10, 11],
}


class TrendsIntelAgent:
    """
    Trends Intelligence Agent.
    
    Uses DataForSEO to analyze:
    - Keyword search volume over time
    - Google Trends interest data
    - Seasonal patterns
    - Rising/related queries
    
    Provides recommendations for ad timing.
    """
    
    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.client = DataForSEOClient(login, password)
    
    def analyze(
        self,
        keywords: List[str],
        location: str = "United States",
        include_related: bool = True,
    ) -> TrendsAnalysis:
        """
        Analyze keyword trends.
        
        Args:
            keywords: Keywords to analyze
            location: Location for search data
            include_related: Include related/rising queries
        
        Returns:
            Complete TrendsAnalysis
        """
        print(f"\n{'='*60}")
        print("Trends Intelligence Agent (DataForSEO)")
        print(f"{'='*60}")
        print(f"Keywords: {', '.join(keywords)}")
        print(f"Location: {location}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        analysis = TrendsAnalysis(
            keywords=keywords,
            location=location,
        )
        
        # Step 1: Get search volume data
        print("Step 1: Fetching keyword search volume...")
        keyword_data = self.client.get_search_volume(keywords, location)
        analysis.keyword_data = keyword_data
        
        if keyword_data:
            for kd in keyword_data:
                print(f"  - {kd.keyword}: {kd.search_volume:,}/month, CPC: ${kd.cpc:.2f}")
        
        # Step 2: Get Google Trends data
        print("\nStep 2: Fetching Google Trends...")
        trend_data = self.client.get_trends(keywords[:5], location)
        analysis.trend_data = trend_data
        
        # Step 3: Get related queries
        if include_related and keywords:
            print("\nStep 3: Fetching related queries...")
            related = self.client.get_related_queries(keywords[0], location)
            analysis.related_queries = related.get("top", [])[:10]
            analysis.rising_queries = related.get("rising", [])[:10]
            
            if analysis.rising_queries:
                print(f"  Rising queries: {', '.join(analysis.rising_queries[:5])}")
        
        # Step 4: Analyze seasonality
        print("\nStep 4: Analyzing seasonal patterns...")
        for kd in keyword_data:
            insight = self._analyze_seasonality(kd)
            if insight:
                analysis.seasonal_insights.append(insight)
                print(f"  - {kd.keyword}: Peak in {insight.peak_season}")
        
        # Step 5: Generate timing recommendations
        print("\nStep 5: Generating ad timing recommendations...")
        for kd in keyword_data:
            rec = self._generate_timing_recommendation(kd)
            if rec:
                analysis.timing_recommendations.append(rec)
        
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Complete! ({elapsed:.1f}s)")
        print(f"{'='*60}")
        
        return analysis
    
    def _analyze_seasonality(self, kd: KeywordData) -> Optional[SeasonalInsight]:
        """Analyze seasonal patterns for a keyword."""
        if not kd.monthly_searches:
            return None
        
        # Group by month and average across years
        month_volumes: Dict[int, List[int]] = {m: [] for m in range(1, 13)}
        for ms in kd.monthly_searches:
            if 1 <= ms.month <= 12 and ms.search_volume:
                month_volumes[ms.month].append(ms.search_volume)
        
        # Calculate monthly averages
        month_avgs = {}
        for month, volumes in month_volumes.items():
            if volumes:
                month_avgs[month] = sum(volumes) / len(volumes)
        
        if not month_avgs:
            return None
        
        # Find peak and low months
        overall_avg = sum(month_avgs.values()) / len(month_avgs)
        peak_months = [m for m, v in month_avgs.items() if v > overall_avg * 1.15]
        low_months = [m for m, v in month_avgs.items() if v < overall_avg * 0.85]
        
        # Determine peak season
        peak_season = self._determine_season(peak_months)
        low_season = self._determine_season(low_months)
        
        # Calculate seasonality score (variance)
        if month_avgs:
            max_vol = max(month_avgs.values())
            min_vol = min(month_avgs.values())
            if max_vol > 0:
                seasonality = ((max_vol - min_vol) / max_vol) * 100
            else:
                seasonality = 0
        else:
            seasonality = 0
        
        # Generate recommendation
        if seasonality > 30:
            rec = f"Increase ad spend in {peak_season}. Consider reducing budget in {low_season}."
        elif seasonality > 15:
            rec = f"Slight seasonal pattern. Peak interest in {peak_season}."
        else:
            rec = "Stable demand year-round. Consistent ad spend recommended."
        
        return SeasonalInsight(
            keyword=kd.keyword,
            peak_season=peak_season,
            peak_months=peak_months,
            low_season=low_season,
            low_months=low_months,
            seasonality_score=round(seasonality, 1),
            recommendation=rec,
        )
    
    def _determine_season(self, months: List[int]) -> str:
        """Determine which season best matches the given months."""
        if not months:
            return "Year-round"
        
        season_scores = {}
        for season, season_months in SEASONS.items():
            overlap = len(set(months) & set(season_months))
            season_scores[season] = overlap
        
        best_season = max(season_scores, key=season_scores.get)
        month_names = [SHORT_MONTHS[m] for m in sorted(months)]
        
        if season_scores[best_season] >= 2:
            return f"{best_season} ({', '.join(month_names)})"
        else:
            return f"{', '.join(month_names)}"
    
    def _generate_timing_recommendation(
        self,
        kd: KeywordData,
    ) -> Optional[AdTimingRecommendation]:
        """Generate ad timing recommendation."""
        if not kd.monthly_searches:
            return None
        
        # Get peak and low months
        peak_months = kd.get_peak_months()
        low_months = kd.get_low_months()
        
        # Determine current trend (compare recent to older)
        recent = kd.monthly_searches[:3]  # Last 3 months
        older = kd.monthly_searches[6:9]  # 6-9 months ago
        
        if recent and older:
            recent_avg = sum(m.search_volume for m in recent) / len(recent)
            older_avg = sum(m.search_volume for m in older) / len(older)
            
            if older_avg > 0:
                change = (recent_avg - older_avg) / older_avg
                if change > 0.1:
                    trend = "rising"
                elif change < -0.1:
                    trend = "falling"
                else:
                    trend = "stable"
            else:
                trend = "stable"
        else:
            trend = "unknown"
        
        # Budget advice based on CPC and competition
        if kd.competition == "HIGH" and kd.cpc > 5:
            budget = "High competition and CPC. Consider long-tail keywords to reduce costs."
        elif kd.competition == "HIGH":
            budget = "Competitive market. Focus on quality score to lower CPC."
        elif kd.cpc > 10:
            budget = "High CPC. Test different ad copy to improve CTR."
        else:
            budget = "Reasonable CPC. Good opportunity for testing."
        
        return AdTimingRecommendation(
            keyword=kd.keyword,
            best_months=[SHORT_MONTHS[m] for m in sorted(peak_months)] if peak_months else ["Year-round"],
            avoid_months=[SHORT_MONTHS[m] for m in sorted(low_months)] if low_months else [],
            current_trend=trend,
            budget_advice=budget,
        )


def run_trends_analysis(
    keywords: List[str],
    location: str = "United States",
    include_related: bool = True,
    save: bool = True,
    output_dir: str = "output",
) -> TrendsAnalysis:
    """
    Run trends analysis and optionally save results.
    
    Args:
        keywords: Keywords to analyze
        location: Location for search data
        include_related: Include related queries
        save: Whether to save results
        output_dir: Output directory
    
    Returns:
        TrendsAnalysis results
    """
    agent = TrendsIntelAgent()
    analysis = agent.analyze(
        keywords=keywords,
        location=location,
        include_related=include_related,
    )
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("TRENDS INTELLIGENCE SUMMARY")
    print(f"{'='*60}\n")
    
    print("### Keyword Search Volume")
    for kd in analysis.keyword_data:
        print(f"  - {kd.keyword}")
        print(f"      Monthly volume: {kd.search_volume:,}")
        print(f"      Competition: {kd.competition} ({kd.competition_index}/100)")
        print(f"      CPC: ${kd.cpc:.2f} (bid range: ${kd.low_bid:.2f} - ${kd.high_bid:.2f})")
    
    print("\n### Seasonal Patterns")
    for insight in analysis.seasonal_insights:
        print(f"  - {insight.keyword}")
        print(f"      Seasonality: {insight.seasonality_score}%")
        print(f"      Peak: {insight.peak_season}")
        print(f"      Low: {insight.low_season}")
        print(f"      -> {insight.recommendation}")
    
    print("\n### Ad Timing Recommendations")
    for rec in analysis.timing_recommendations:
        print(f"  - {rec.keyword}")
        print(f"      Best months: {', '.join(rec.best_months)}")
        if rec.avoid_months:
            print(f"      Avoid: {', '.join(rec.avoid_months)}")
        print(f"      Trend: {rec.current_trend}")
        print(f"      -> {rec.budget_advice}")
    
    if analysis.rising_queries:
        print("\n### Rising Queries (Opportunities)")
        for q in analysis.rising_queries[:8]:
            print(f"  * {q}")
    
    if analysis.related_queries:
        print("\n### Related Queries")
        for q in analysis.related_queries[:8]:
            print(f"  - {q}")
    
    # Save results
    if save:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_path / f"trends_intel_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"Report saved: {filename}")
    
    return analysis
