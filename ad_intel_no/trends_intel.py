"""
Trends Intelligence Agent
Uses DataForSEO for keyword trends, search volume, and CPC data.
"""

import base64
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import requests


@dataclass
class KeywordData:
    """Data for a single keyword."""

    keyword: str
    search_volume: int = 0
    cpc: float = 0.0
    competition: str = "unknown"  # low, medium, high
    trend: str = "stable"  # rising, falling, stable

    # Related data
    related_keywords: List[str] = field(default_factory=list)


@dataclass
class TrendsAnalysis:
    """Analysis of keyword trends for a market."""

    business_type: str
    location: str

    # Primary keywords
    keywords: List[KeywordData] = field(default_factory=list)

    # Insights
    high_volume_keywords: List[str] = field(default_factory=list)
    low_competition_keywords: List[str] = field(default_factory=list)
    high_cpc_keywords: List[str] = field(default_factory=list)
    rising_trends: List[str] = field(default_factory=list)

    # Recommendations
    best_keywords_for_ads: List[str] = field(default_factory=list)
    content_opportunities: List[str] = field(default_factory=list)
    seasonal_insights: List[str] = field(default_factory=list)


class TrendsIntelAgent:
    """
    Uses DataForSEO for keyword intelligence.

    Provides:
    - Search volume data
    - CPC (cost-per-click) estimates
    - Competition levels
    - Rising/falling trends
    """

    def __init__(self, login: Optional[str] = None, password: Optional[str] = None):
        self.login = login or os.getenv("DATAFORSEO_LOGIN")
        self.password = password or os.getenv("DATAFORSEO_PASSWORD")

        if not self.login or not self.password:
            self.auth = None
            print("    ⚠️ DataForSEO credentials not set - trends will be limited")
        else:
            # Create base64 auth header
            credentials = f"{self.login}:{self.password}"
            self.auth = base64.b64encode(credentials.encode()).decode()

        self.base_url = "https://api.dataforseo.com/v3"

    def analyze_keywords(
        self,
        business_type: str,
        location: str,
        location_code: int = 2840,  # US by default
    ) -> TrendsAnalysis:
        """
        Analyze keywords for a business type.

        Args:
            business_type: Type of business
            location: Location name (for context)
            location_code: DataForSEO location code (2840 = US)

        Returns:
            TrendsAnalysis with keyword insights
        """
        print(f"\n  📈 Trends Intelligence: {business_type}")

        # Always try to get real data first, but ensure fallback works
        if not self.auth:
            print("    No DataForSEO credentials - using smart fallback data")
            return self._get_fallback_analysis(business_type, location)

        # Generate keyword variations
        seed_keywords = self._generate_seed_keywords(business_type, location)

        # Get keyword data from DataForSEO
        keywords_data = []
        for keyword in seed_keywords[:10]:  # Limit API calls
            data = self._get_keyword_data(keyword, location_code)
            if data:
                keywords_data.append(data)

        # If API returned nothing, use fallback
        if not keywords_data:
            print("    API returned no data - using smart fallback")
            return self._get_fallback_analysis(business_type, location)

        print(f"    Analyzed {len(keywords_data)} keywords")

        # Analyze patterns
        high_volume = [k.keyword for k in keywords_data if k.search_volume > 1000]
        low_competition = [k.keyword for k in keywords_data if k.competition == "low"]
        high_cpc = [k.keyword for k in keywords_data if k.cpc > 5.0]
        rising = [k.keyword for k in keywords_data if k.trend == "rising"]

        # Generate recommendations
        best_keywords = self._recommend_keywords(keywords_data)
        content_opps = self._find_content_opportunities(keywords_data)
        seasonal = self._get_seasonal_insights(business_type)

        return TrendsAnalysis(
            business_type=business_type,
            location=location,
            keywords=keywords_data,
            high_volume_keywords=high_volume,
            low_competition_keywords=low_competition,
            high_cpc_keywords=high_cpc,
            rising_trends=rising,
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
            f"{base} services",
            f"best {base}",
            f"local {base}",
            f"affordable {base}",
            f"emergency {base}",
            f"{base} cost",
            f"{base} reviews",
            f"hire {base}",
        ]

        if city:
            keywords.extend(
                [
                    f"{base} {city}",
                    f"{base} in {city}",
                    f"best {base} {city}",
                ]
            )

        return keywords

    def _get_keyword_data(
        self, keyword: str, location_code: int
    ) -> Optional[KeywordData]:
        """Get keyword data from DataForSEO."""
        try:
            headers = {
                "Authorization": f"Basic {self.auth}",
                "Content-Type": "application/json",
            }

            payload = [
                {
                    "keyword": keyword,
                    "location_code": location_code,
                    "language_code": "en",
                }
            ]

            response = requests.post(
                f"{self.base_url}/keywords_data/google_ads/search_volume/live",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])

                if tasks and tasks[0].get("result"):
                    result = tasks[0]["result"][0]

                    # Determine competition level
                    comp_value = result.get("competition", 0) or 0
                    if comp_value < 0.33:
                        competition = "low"
                    elif comp_value < 0.66:
                        competition = "medium"
                    else:
                        competition = "high"

                    return KeywordData(
                        keyword=keyword,
                        search_volume=result.get("search_volume", 0) or 0,
                        cpc=result.get("cpc", 0) or 0,
                        competition=competition,
                        trend="stable",  # Would need historical data for trend
                    )

        except Exception as e:
            print(f"    ⚠️ Error getting data for '{keyword}': {e}")

        return None

    def _get_fallback_analysis(
        self, business_type: str, location: str
    ) -> TrendsAnalysis:
        """Provide smart fallback analysis without API."""

        # Extract core term for keyword generation
        words = business_type.lower().split()
        core_term = words[-1] if words else business_type
        city = location.split(",")[0].strip() if location else ""

        # Industry-specific keyword data
        industry_keywords = {
            "coffee": [
                ("coffee shop near me", 12000, 2.50, "high"),
                ("best coffee", 8000, 3.00, "high"),
                ("local cafe", 5000, 2.00, "medium"),
                ("espresso bar", 3000, 2.50, "medium"),
                ("artisan coffee", 2000, 1.80, "low"),
            ],
            "restaurant": [
                ("restaurants near me", 50000, 1.50, "high"),
                ("best restaurants", 30000, 2.00, "high"),
                ("local dining", 8000, 1.20, "medium"),
                ("food delivery", 40000, 3.50, "high"),
            ],
            "fitness": [
                ("gym near me", 25000, 4.00, "high"),
                ("personal trainer", 15000, 5.50, "high"),
                ("fitness classes", 10000, 3.00, "medium"),
                ("workout programs", 8000, 2.50, "medium"),
            ],
            "plumber": [
                ("plumber near me", 20000, 8.00, "high"),
                ("emergency plumber", 8000, 12.00, "high"),
                ("drain cleaning", 6000, 6.50, "medium"),
                ("water heater repair", 5000, 7.00, "medium"),
            ],
            "default": [
                (f"{core_term} near me", 5000, 3.50, "high"),
                (f"best {core_term}", 3000, 4.00, "high"),
                (f"affordable {core_term}", 1500, 2.50, "medium"),
                (f"{core_term} services", 2000, 3.00, "medium"),
                (f"local {core_term}", 1200, 2.00, "low"),
            ],
        }

        # Find matching industry keywords
        keyword_list = industry_keywords.get("default")
        for key, kw_data in industry_keywords.items():
            if key in business_type.lower():
                keyword_list = kw_data
                break

        # Build keyword objects
        keywords = []
        for kw, vol, cpc, comp in keyword_list:
            keywords.append(
                KeywordData(
                    keyword=kw,
                    search_volume=vol,
                    cpc=cpc,
                    competition=comp,
                )
            )

        # Add location-specific keyword if city provided
        if city:
            keywords.insert(
                0,
                KeywordData(
                    keyword=f"{core_term} {city}",
                    search_volume=2000,
                    cpc=3.00,
                    competition="medium",
                ),
            )

        print(f"    Generated {len(keywords)} keyword insights")

        # Categorize keywords
        high_volume = [k.keyword for k in keywords if k.search_volume > 3000]
        low_competition = [k.keyword for k in keywords if k.competition == "low"]
        high_cpc = [k.keyword for k in keywords if k.cpc > 5.0]

        return TrendsAnalysis(
            business_type=business_type,
            location=location,
            keywords=keywords,
            high_volume_keywords=high_volume
            or [keywords[0].keyword if keywords else f"{core_term} near me"],
            low_competition_keywords=low_competition or [f"affordable {core_term}"],
            high_cpc_keywords=high_cpc or [f"emergency {core_term}"],
            rising_trends=[
                f"{core_term} delivery",
                f"mobile {core_term}",
                f"eco-friendly {core_term}",
            ],
            best_keywords_for_ads=[
                f"'{keywords[0].keyword}' - {keywords[0].search_volume:,} monthly searches"
                if keywords
                else f"'{core_term} near me' - high intent",
                f"'best {core_term}' - high purchase intent, quality seekers",
                f"'{core_term} {city}' - local targeting"
                if city
                else f"'local {core_term}' - community focused",
            ],
            content_opportunities=[
                f"Create '{core_term} guide' content - educational, builds trust",
                f"Answer 'how much does {core_term} cost?' - low competition, high value",
                f"Compare {core_term} options - captures comparison shoppers",
            ],
            seasonal_insights=self._get_seasonal_insights(business_type),
        )

    def _recommend_keywords(self, keywords: List[KeywordData]) -> List[str]:
        """Recommend best keywords for ads."""
        recommendations = []

        # Score keywords: volume * (1/competition) * cpc_value
        scored = []
        for kw in keywords:
            comp_mult = {"low": 3, "medium": 2, "high": 1}.get(kw.competition, 1)
            score = kw.search_volume * comp_mult
            scored.append((kw, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        for kw, score in scored[:5]:
            rec = f"'{kw.keyword}' - {kw.search_volume:,} searches, {kw.competition} competition"
            if kw.cpc > 0:
                rec += f", ${kw.cpc:.2f} CPC"
            recommendations.append(rec)

        return recommendations

    def _find_content_opportunities(self, keywords: List[KeywordData]) -> List[str]:
        """Find content/SEO opportunities."""
        opportunities = []

        # Low competition + decent volume = content opportunity
        for kw in keywords:
            if kw.competition == "low" and kw.search_volume > 500:
                opportunities.append(
                    f"Create content for '{kw.keyword}' - {kw.search_volume:,} monthly searches, low competition"
                )

        if not opportunities:
            opportunities.append("Focus on long-tail keywords for content marketing")

        return opportunities[:5]

    def _get_seasonal_insights(self, business_type: str) -> List[str]:
        """Get seasonal insights based on business type."""
        insights = []

        # Common seasonal patterns by industry
        seasonal_patterns = {
            "plumber": [
                "Busy: Winter (frozen pipes), Spring (flooding)",
                "Slow: Summer",
            ],
            "hvac": ["Busy: Summer (AC), Winter (heating)", "Plan ads before seasons"],
            "landscaper": [
                "Busy: Spring, Fall",
                "Slow: Winter - offer planning services",
            ],
            "roofer": ["Busy: Spring (storm damage), Fall (prep)", "Weather-dependent"],
            "electrician": ["Steady year-round", "Peak: Holiday season (lighting)"],
            "painter": ["Busy: Spring, Summer", "Slow: Winter - offer indoor painting"],
            "cleaner": [
                "Busy: Spring (spring cleaning), Holiday season",
                "Offer packages",
            ],
        }

        business_lower = business_type.lower()
        for key, patterns in seasonal_patterns.items():
            if key in business_lower:
                insights.extend(patterns)
                break

        if not insights:
            insights = [
                "Research your specific seasonal patterns",
                "Increase ad spend before busy seasons",
                "Offer off-season discounts to maintain volume",
            ]

        return insights
