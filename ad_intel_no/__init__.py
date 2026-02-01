"""
Ad Intelligence Module - Full "Marky" Research Suite

Includes:
- GoogleAdsScraper: Competitor Google Ads via SerpAPI
- AdIntelAgent: Ad pattern analysis
- ReviewIntelAgent: Google Reviews analysis
- YelpIntelAgent: Yelp reviews and business data
- TrendsIntelAgent: Keyword trends via DataForSEO
- WebsiteIntelAgent: Competitor website scraping
"""

from .agent import AdIntelAgent, run_ad_analysis
from .models import AdAnalysis, AdData, AdPatterns, CompetitorAds
from .review_intel import ReviewAnalysis, ReviewIntelAgent
from .scraper import GoogleAdsScraper
from .trends_intel import TrendsAnalysis, TrendsIntelAgent
from .website_intel import WebsiteAnalysis, WebsiteIntelAgent
from .yelp_intel import YelpAnalysis, YelpIntelAgent

__all__ = [
    # Original
    "GoogleAdsScraper",
    "AdIntelAgent",
    "run_ad_analysis",
    "AdData",
    "CompetitorAds",
    "AdPatterns",
    "AdAnalysis",
    # New agents
    "ReviewIntelAgent",
    "ReviewAnalysis",
    "YelpIntelAgent",
    "YelpAnalysis",
    "TrendsIntelAgent",
    "TrendsAnalysis",
    "WebsiteIntelAgent",
    "WebsiteAnalysis",
]
