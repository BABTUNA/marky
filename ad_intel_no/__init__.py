"""
Ad Intelligence Agent.
Scrapes competitor Google Ads via SerpAPI to analyze their ad strategies.
Uses the same SERPAPI_KEY as local_intel - no additional API needed.
"""

from .agent import AdIntelAgent, run_ad_analysis
from .models import AdData, CompetitorAds, AdAnalysis

__all__ = [
    "AdIntelAgent",
    "run_ad_analysis",
    "AdData",
    "CompetitorAds",
    "AdAnalysis",
]
