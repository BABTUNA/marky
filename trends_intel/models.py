"""
Data models for Trends Intelligence Agent.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class MonthlyVolume:
    """Monthly search volume data point."""
    year: int
    month: int
    search_volume: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "search_volume": self.search_volume,
        }


@dataclass
class KeywordData:
    """Keyword search volume and competition data."""
    keyword: str
    search_volume: int  # Monthly average
    competition: str  # HIGH, MEDIUM, LOW
    competition_index: int  # 0-100
    cpc: float  # Cost per click in USD
    low_bid: float  # Low top of page bid
    high_bid: float  # High top of page bid
    monthly_searches: List[MonthlyVolume] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyword": self.keyword,
            "search_volume": self.search_volume,
            "competition": self.competition,
            "competition_index": self.competition_index,
            "cpc": self.cpc,
            "low_bid": self.low_bid,
            "high_bid": self.high_bid,
            "monthly_searches": [m.to_dict() for m in self.monthly_searches],
        }
    
    def get_peak_months(self) -> List[int]:
        """Get months with highest search volume."""
        if not self.monthly_searches:
            return []
        
        avg = sum(m.search_volume for m in self.monthly_searches) / len(self.monthly_searches)
        peak_months = [m.month for m in self.monthly_searches if m.search_volume > avg * 1.2]
        return list(set(peak_months))
    
    def get_low_months(self) -> List[int]:
        """Get months with lowest search volume."""
        if not self.monthly_searches:
            return []
        
        avg = sum(m.search_volume for m in self.monthly_searches) / len(self.monthly_searches)
        low_months = [m.month for m in self.monthly_searches if m.search_volume < avg * 0.8]
        return list(set(low_months))


@dataclass
class TrendData:
    """Google Trends interest over time data."""
    keyword: str
    data_points: List[Dict[str, Any]] = field(default_factory=list)  # date, value
    average: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyword": self.keyword,
            "data_points": self.data_points,
            "average": self.average,
        }


@dataclass
class SeasonalInsight:
    """Seasonal insight for a keyword."""
    keyword: str
    peak_season: str  # e.g., "Winter (Dec-Feb)"
    peak_months: List[int]
    low_season: str  # e.g., "Summer (Jun-Aug)"
    low_months: List[int]
    seasonality_score: float  # 0-100, higher = more seasonal
    recommendation: str  # When to run ads
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyword": self.keyword,
            "peak_season": self.peak_season,
            "peak_months": self.peak_months,
            "low_season": self.low_season,
            "low_months": self.low_months,
            "seasonality_score": self.seasonality_score,
            "recommendation": self.recommendation,
        }


@dataclass
class AdTimingRecommendation:
    """Recommendation for ad timing based on trends."""
    keyword: str
    best_months: List[str]
    avoid_months: List[str]
    current_trend: str  # "rising", "falling", "stable"
    budget_advice: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyword": self.keyword,
            "best_months": self.best_months,
            "avoid_months": self.avoid_months,
            "current_trend": self.current_trend,
            "budget_advice": self.budget_advice,
        }


@dataclass
class TrendsAnalysis:
    """Complete trends analysis results."""
    keywords: List[str]
    location: str
    keyword_data: List[KeywordData] = field(default_factory=list)
    trend_data: List[TrendData] = field(default_factory=list)
    seasonal_insights: List[SeasonalInsight] = field(default_factory=list)
    timing_recommendations: List[AdTimingRecommendation] = field(default_factory=list)
    related_queries: List[str] = field(default_factory=list)
    rising_queries: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "keywords": self.keywords,
            "location": self.location,
            "keyword_data": [k.to_dict() for k in self.keyword_data],
            "trend_data": [t.to_dict() for t in self.trend_data],
            "seasonal_insights": [s.to_dict() for s in self.seasonal_insights],
            "timing_recommendations": [r.to_dict() for r in self.timing_recommendations],
            "related_queries": self.related_queries,
            "rising_queries": self.rising_queries,
        }
