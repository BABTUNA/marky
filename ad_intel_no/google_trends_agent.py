"""
Google Trends Intelligence Agent
Uses pytrends (unofficial Google Trends API) - free, no API key needed!
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta


@dataclass
class KeywordData:
    """Data for a single keyword."""
    keyword: str
    search_volume: int = 0
    interest: int = 0  # 0-100 interest score from Google Trends
    trend: str = "stable"  # rising, falling, stable
    related_keywords: List[str] = field(default_factory=list)


@dataclass
class TrendsAnalysis:
    """Analysis of keyword trends for a market."""
    business_type: str
    location: str
    keywords: List[KeywordData] = field(default_factory=list)
    high_interest_keywords: List[str] = field(default_factory=list)
    rising_trends: List[str] = field(default_factory=list)
    best_keywords_for_ads: List[str] = field(default_factory=list)
    content_opportunities: List[str] = field(default_factory=list)
    seasonal_insights: List[str] = field(default_factory=list)


class GoogleTrendsAgent:
    """
    Uses pytrends (Google Trends) for keyword intelligence - completely FREE!
    
    No API key needed, uses Google Cloud infrastructure.
    Better for trend data than DataForSEO.
    """
    
    def __init__(self):
        """Initialize Google Trends client."""
        try:
            from pytrends.request import TrendReq
            self.pytrends = TrendReq(hl='en-US', tz=360)
            self.available = True
        except ImportError:
            print("⚠️ pytrends not installed - install with: pip install pytrends")
            self.pytrends = None
            self.available = False
    
    def analyze_keywords(
        self,
        business_type: str,
        location: str,
    ) -> TrendsAnalysis:
        """
        Analyze keywords using Google Trends.
        
        Args:
            business_type: Type of business
            location: Location name (e.g., "Boston")
            
        Returns:
            TrendsAnalysis with keyword insights
        """
        print(f"\n📈 Trends Intelligence (Google Trends)")
        print(f"   Business: {business_type}, Location: {location}")
        
        if not self.available:
            print("   Using fallback data (pytrends not available)")
            return self._get_fallback_analysis(business_type, location)
        
        # Generate seed keywords
        seed_keywords = self._generate_seed_keywords(business_type, location)
        
        # Get trends data
        keywords_data = []
        rising_keywords = []
        
        try:
            # Get interest over time for keywords (5 at a time max)
            for i in range(0, min(len(seed_keywords), 10), 5):
                batch = seed_keywords[i:i+5]
                
                self.pytrends.build_payload(
                    batch,
                    cat=0,
                    timeframe='today 12-m',
                    geo='US'
                )
                
                # Get interest over time
                interest_df = self.pytrends.interest_over_time()
                
                if not interest_df.empty:
                    for kw in batch:
                        if kw in interest_df.columns:
                            avg_interest = int(interest_df[kw].mean())
                            
                            # Determine trend
                            recent = interest_df[kw].tail(4).mean()
                            older = interest_df[kw].head(4).mean()
                            if recent > older * 1.2:
                                trend = "rising"
                                rising_keywords.append(kw)
                            elif recent < older * 0.8:
                                trend = "falling"
                            else:
                                trend = "stable"
                            
                            keywords_data.append(KeywordData(
                                keyword=kw,
                                search_volume=avg_interest * 100,  # Scale to estimate
                                interest=avg_interest,
                                trend=trend
                            ))
                
                # Get related queries (rising topics)
                try:
                    related = self.pytrends.related_queries()
                    for kw in batch:
                        if kw in related and related[kw]['rising'] is not None:
                            rising_df = related[kw]['rising']
                            if not rising_df.empty:
                                for query in rising_df['query'].head(3):
                                    if query not in rising_keywords:
                                        rising_keywords.append(str(query))
                except:
                    pass  # Related queries sometimes fail
            
            print(f"   ✓ Analyzed {len(keywords_data)} keywords from Google Trends")
            print(f"   ✓ Found {len(rising_keywords)} rising trends")
            
        except Exception as e:
            print(f"   ⚠️ Google Trends error: {e}")
            print("   Using fallback data")
            return self._get_fallback_analysis(business_type, location)
        
        if not keywords_data:
            return self._get_fallback_analysis(business_type, location)
        
        # Sort by interest
        keywords_data.sort(key=lambda x: x.interest, reverse=True)
        high_interest = [k.keyword for k in keywords_data[:3]]
        
        # Generate recommendations
        best_keywords = self._recommend_keywords(keywords_data)
        content_opps = [f"Create content around: {k}" for k in rising_keywords[:3]]
        seasonal = self._get_seasonal_insights(business_type)
        
        return TrendsAnalysis(
            business_type=business_type,
            location=location,
            keywords=keywords_data,
            high_interest_keywords=high_interest,
            rising_trends=rising_keywords[:5],
            best_keywords_for_ads=best_keywords,
            content_opportunities=content_opps,
            seasonal_insights=seasonal,
        )
    
    def _generate_seed_keywords(self, business_type: str, location: str) -> List[str]:
        """Generate seed keywords to research."""
        base = business_type.lower()
        city = location.split(",")[0].strip() if location else ""
        
        keywords = [
            base,
            f"{base} near me",
            f"best {base}",
            f"local {base}",
            f"affordable {base}",
        ]
        
        if city:
            keywords.extend([
                f"{base} {city}",
                f"best {base} {city}",
            ])
        
        return keywords
    
    def _recommend_keywords(self, keywords: List[KeywordData]) -> List[str]:
        """Recommend best keywords for ads."""
        recommendations = []
        
        for kw in keywords[:5]:
            trend_emoji = "📈" if kw.trend == "rising" else "📊"
            recommendations.append(
                f"{trend_emoji} '{kw.keyword}' - {kw.interest}/100 interest, {kw.trend}"
            )
        
        return recommendations
    
    def _get_seasonal_insights(self, business_type: str) -> List[str]:
        """Get seasonal insights based on business type."""
        seasonal_patterns = {
            "coffee": ["Peak: Fall/Winter (PSL season)", "Slow: Summer (iced drinks trend)"],
            "donut": ["Peak: Morning hours, weekends", "Valentine's Day & holidays boost"],
            "pizza": ["Peak: Fridays, Super Bowl, holidays", "Steady year-round"],
            "gym": ["Peak: January (resolutions)", "Slow: Summer"],
            "plumber": ["Peak: Winter (frozen pipes)", "Spring flooding"],
        }
        
        business_lower = business_type.lower()
        for key, patterns in seasonal_patterns.items():
            if key in business_lower:
                return patterns
        
        return ["Year-round demand", "Monitor local events for ad opportunities"]
    
    def _get_fallback_analysis(self, business_type: str, location: str) -> TrendsAnalysis:
        """Fallback when Google Trends unavailable."""
        core_term = business_type.lower().split()[-1]
        
        keywords = [
            KeywordData(keyword=f"{core_term} near me", interest=85, trend="rising"),
            KeywordData(keyword=f"best {core_term}", interest=75, trend="stable"),
            KeywordData(keyword=f"local {core_term}", interest=60, trend="rising"),
        ]
        
        return TrendsAnalysis(
            business_type=business_type,
            location=location,
            keywords=keywords,
            high_interest_keywords=[k.keyword for k in keywords],
            rising_trends=[f"{core_term} delivery", f"mobile {core_term}"],
            best_keywords_for_ads=[
                f"'{k.keyword}' - High search interest" for k in keywords
            ],
            content_opportunities=[
                f"Blog: 'Best {core_term} in {location}'",
                f"Guide: 'How to choose a {core_term}'"
            ],
            seasonal_insights=self._get_seasonal_insights(business_type),
        )
