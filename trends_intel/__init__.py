"""
Trends Intelligence Agent.
Uses DataForSEO API for keyword search volume and Google Trends data.
Provides seasonal insights for advertising timing.
"""

from .agent import TrendsIntelAgent, run_trends_analysis
from .models import KeywordData, TrendData, SeasonalInsight, TrendsAnalysis

__all__ = [
    "TrendsIntelAgent",
    "run_trends_analysis",
    "KeywordData",
    "TrendData",
    "SeasonalInsight",
    "TrendsAnalysis",
]
