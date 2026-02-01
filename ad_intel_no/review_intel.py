"""
Review Intelligence Agent
Scrapes and analyzes Google Reviews for competitors to extract customer voice.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests


@dataclass
class ReviewData:
    """Single review data."""

    text: str
    rating: int
    author: str = ""
    date: str = ""
    business_name: str = ""

    # Extracted insights
    pain_points: List[str] = field(default_factory=list)
    praises: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass
class ReviewAnalysis:
    """Analysis of reviews for a business/market."""

    business_type: str
    location: str
    total_reviews: int
    average_rating: float
    reviews: List[ReviewData]

    # Aggregated insights
    common_complaints: List[str] = field(default_factory=list)
    common_praises: List[str] = field(default_factory=list)
    customer_language: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)


class ReviewIntelAgent:
    """
    Scrapes Google Reviews via SerpAPI to understand customer voice.

    Extracts:
    - Common complaints (pain points to address in ads)
    - Common praises (benefits to highlight)
    - Customer language (words real customers use)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not set")
        self.base_url = "https://serpapi.com/search"

    def analyze_market_reviews(
        self,
        business_type: str,
        location: str,
        max_businesses: int = 5,
        reviews_per_business: int = 10,
    ) -> ReviewAnalysis:
        """
        Analyze reviews for businesses in a market.

        Args:
            business_type: Type of business (e.g., "plumber")
            location: Location (e.g., "Providence RI")
            max_businesses: Max businesses to analyze
            reviews_per_business: Reviews to fetch per business

        Returns:
            ReviewAnalysis with aggregated insights
        """
        print(f"\n  📝 Review Intelligence: {business_type} in {location}")

        all_reviews = []
        all_ratings = []

        # Step 1: Find businesses via Google Maps
        businesses = self._find_businesses(business_type, location, max_businesses)
        print(f"    Found {len(businesses)} businesses to analyze")

        # Step 2: Get reviews for each business
        for biz in businesses:
            place_id = biz.get("place_id")
            name = biz.get("title", "Unknown")

            if place_id:
                reviews = self._get_reviews(place_id, name, reviews_per_business)
                all_reviews.extend(reviews)

                rating = biz.get("rating", 0)
                if rating:
                    all_ratings.append(rating)

        print(f"    Collected {len(all_reviews)} total reviews")

        # Step 3: Analyze patterns
        avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0

        complaints = self._extract_complaints(all_reviews)
        praises = self._extract_praises(all_reviews)
        language = self._extract_customer_language(all_reviews)
        opportunities = self._find_opportunities(complaints, praises)

        return ReviewAnalysis(
            business_type=business_type,
            location=location,
            total_reviews=len(all_reviews),
            average_rating=avg_rating,
            reviews=all_reviews,
            common_complaints=complaints,
            common_praises=praises,
            customer_language=language,
            opportunities=opportunities,
        )

    def _find_businesses(
        self, business_type: str, location: str, max_results: int
    ) -> List[Dict]:
        """Find businesses via Google Maps search."""
        try:
            params = {
                "engine": "google_maps",
                "q": f"{business_type} {location}",
                "type": "search",
                "api_key": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = data.get("local_results", [])
            return results[:max_results]

        except Exception as e:
            print(f"    ⚠️ Error finding businesses: {e}")
            return []

    def _get_reviews(
        self, place_id: str, business_name: str, max_reviews: int
    ) -> List[ReviewData]:
        """Get reviews for a specific business."""
        reviews = []

        try:
            params = {
                "engine": "google_maps_reviews",
                "place_id": place_id,
                "api_key": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            for item in data.get("reviews", [])[:max_reviews]:
                review = ReviewData(
                    text=item.get("snippet", ""),
                    rating=item.get("rating", 0),
                    author=item.get("user", {}).get("name", ""),
                    date=item.get("date", ""),
                    business_name=business_name,
                )

                # Extract insights from review text
                if review.text:
                    review.pain_points = self._find_pain_points(review.text)
                    review.praises = self._find_praises(review.text)
                    review.keywords = self._extract_keywords(review.text)

                reviews.append(review)

        except Exception as e:
            print(f"    ⚠️ Error getting reviews for {business_name}: {e}")

        return reviews

    def _find_pain_points(self, text: str) -> List[str]:
        """Find pain points mentioned in review."""
        pain_points = []
        text_lower = text.lower()

        # Negative indicators
        negative_patterns = [
            ("late", "showed up late"),
            ("didn't show", "no-show"),
            ("overcharged", "overpriced"),
            ("expensive", "too expensive"),
            ("rude", "rude service"),
            ("unprofessional", "unprofessional"),
            ("messy", "left a mess"),
            ("didn't fix", "problem not fixed"),
            ("still broken", "issue persists"),
            ("no response", "unresponsive"),
            ("waiting", "long wait"),
            ("disappointed", "disappointment"),
        ]

        for pattern, label in negative_patterns:
            if pattern in text_lower:
                pain_points.append(label)

        return pain_points

    def _find_praises(self, text: str) -> List[str]:
        """Find praises mentioned in review."""
        praises = []
        text_lower = text.lower()

        positive_patterns = [
            ("on time", "punctual"),
            ("professional", "professional"),
            ("friendly", "friendly"),
            ("quick", "fast service"),
            ("fair price", "fair pricing"),
            ("affordable", "affordable"),
            ("clean", "clean work"),
            ("explained", "good communication"),
            ("recommend", "recommended"),
            ("honest", "honest"),
            ("knowledgeable", "knowledgeable"),
            ("thorough", "thorough"),
        ]

        for pattern, label in positive_patterns:
            if pattern in text_lower:
                praises.append(label)

        return praises

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key phrases customers use."""
        keywords = []
        text_lower = text.lower()

        # Common service-related phrases
        phrases = [
            "same day",
            "next day",
            "emergency",
            "free estimate",
            "free quote",
            "warranty",
            "guarantee",
            "family owned",
            "local",
            "years of experience",
        ]

        for phrase in phrases:
            if phrase in text_lower:
                keywords.append(phrase)

        return keywords

    def _extract_complaints(self, reviews: List[ReviewData]) -> List[str]:
        """Aggregate common complaints."""
        from collections import Counter

        all_complaints = []
        for review in reviews:
            if review.rating <= 3:  # Focus on negative reviews
                all_complaints.extend(review.pain_points)

        counter = Counter(all_complaints)
        return [complaint for complaint, _ in counter.most_common(10)]

    def _extract_praises(self, reviews: List[ReviewData]) -> List[str]:
        """Aggregate common praises."""
        from collections import Counter

        all_praises = []
        for review in reviews:
            if review.rating >= 4:  # Focus on positive reviews
                all_praises.extend(review.praises)

        counter = Counter(all_praises)
        return [praise for praise, _ in counter.most_common(10)]

    def _extract_customer_language(self, reviews: List[ReviewData]) -> List[str]:
        """Extract phrases customers actually use."""
        from collections import Counter

        all_keywords = []
        for review in reviews:
            all_keywords.extend(review.keywords)

        counter = Counter(all_keywords)
        return [kw for kw, _ in counter.most_common(10)]

    def _find_opportunities(
        self, complaints: List[str], praises: List[str]
    ) -> List[str]:
        """Find advertising opportunities from review analysis."""
        opportunities = []

        # Turn complaints into ad opportunities
        complaint_to_opportunity = {
            "showed up late": "Highlight: 'Always on time - or it's free'",
            "overpriced": "Emphasize: 'Upfront pricing, no surprises'",
            "unresponsive": "Promote: '24/7 availability, fast response'",
            "problem not fixed": "Guarantee: 'Fixed right the first time'",
            "unprofessional": "Show: 'Licensed, uniformed professionals'",
        }

        for complaint in complaints:
            if complaint in complaint_to_opportunity:
                opportunities.append(complaint_to_opportunity[complaint])

        # Add general opportunities
        if "punctual" in praises:
            opportunities.append("Customers value punctuality - make it a headline")
        if "professional" in praises:
            opportunities.append("Professionalism stands out - show uniforms/trucks")

        return opportunities[:8]
