"""
Yelp Intelligence Agent
Scrapes Yelp reviews and business data for customer voice insights.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import requests


@dataclass
class YelpReview:
    """Single Yelp review."""

    text: str
    rating: int
    author: str = ""
    date: str = ""
    business_name: str = ""
    useful_count: int = 0

    # Extracted insights
    mentions: List[str] = field(default_factory=list)
    sentiment: str = "neutral"


@dataclass
class YelpBusiness:
    """Yelp business data."""

    name: str
    rating: float
    review_count: int
    categories: List[str] = field(default_factory=list)
    price: str = ""
    highlights: List[str] = field(default_factory=list)


@dataclass
class YelpAnalysis:
    """Analysis of Yelp data for a market."""

    business_type: str
    location: str
    businesses_analyzed: int
    total_reviews: int

    # Market insights
    avg_market_rating: float = 0.0
    price_distribution: Dict[str, int] = field(default_factory=dict)
    common_categories: List[str] = field(default_factory=list)

    # Customer voice
    what_customers_love: List[str] = field(default_factory=list)
    what_customers_hate: List[str] = field(default_factory=list)
    customer_phrases: List[str] = field(default_factory=list)

    # Competitive insights
    top_rated_traits: List[str] = field(default_factory=list)
    low_rated_issues: List[str] = field(default_factory=list)


class YelpIntelAgent:
    """
    Scrapes Yelp via SerpAPI for customer voice and competitive insights.

    Extracts:
    - What customers love (for ad messaging)
    - What customers hate (pain points to address)
    - How top-rated businesses position themselves
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not set")
        self.base_url = "https://serpapi.com/search"

    def analyze_market(
        self,
        business_type: str,
        location: str,
        max_businesses: int = 10,
    ) -> YelpAnalysis:
        """
        Analyze Yelp data for a market.

        Args:
            business_type: Type of business
            location: Location to search
            max_businesses: Max businesses to analyze

        Returns:
            YelpAnalysis with customer voice insights
        """
        print(f"\n  🍽️ Yelp Intelligence: {business_type} in {location}")

        # Search Yelp via SerpAPI
        businesses = self._search_yelp(business_type, location, max_businesses)
        print(f"    Found {len(businesses)} Yelp listings")

        if not businesses:
            return YelpAnalysis(
                business_type=business_type,
                location=location,
                businesses_analyzed=0,
                total_reviews=0,
            )

        # Analyze business data
        ratings = []
        review_counts = []
        all_categories = []
        price_dist = {"$": 0, "$$": 0, "$$$": 0, "$$$$": 0}
        all_highlights = []

        for biz in businesses:
            if biz.rating:
                ratings.append(biz.rating)
            if biz.review_count:
                review_counts.append(biz.review_count)
            all_categories.extend(biz.categories)
            if biz.price in price_dist:
                price_dist[biz.price] += 1
            all_highlights.extend(biz.highlights)

        # Get reviews from top businesses for customer voice
        reviews = self._get_sample_reviews(businesses[:5])

        # Analyze reviews
        loves, hates = self._analyze_sentiment(reviews)
        phrases = self._extract_phrases(reviews)

        # Get traits from top vs low rated
        top_traits = self._get_top_rated_traits(businesses)
        low_issues = self._get_low_rated_issues(businesses)

        # Common categories
        from collections import Counter

        cat_counter = Counter(all_categories)
        common_cats = [cat for cat, _ in cat_counter.most_common(5)]

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        total_reviews = sum(review_counts)

        return YelpAnalysis(
            business_type=business_type,
            location=location,
            businesses_analyzed=len(businesses),
            total_reviews=total_reviews,
            avg_market_rating=avg_rating,
            price_distribution=price_dist,
            common_categories=common_cats,
            what_customers_love=loves,
            what_customers_hate=hates,
            customer_phrases=phrases,
            top_rated_traits=top_traits,
            low_rated_issues=low_issues,
        )

    def _search_yelp(
        self, business_type: str, location: str, max_results: int
    ) -> List[YelpBusiness]:
        """Search Yelp via SerpAPI."""
        businesses = []

        try:
            params = {
                "engine": "yelp",
                "find_desc": business_type,
                "find_loc": location,
                "api_key": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            for item in data.get("organic_results", [])[:max_results]:
                biz = YelpBusiness(
                    name=item.get("title", ""),
                    rating=item.get("rating", 0),
                    review_count=item.get("reviews", 0),
                    categories=[c.get("title", "") for c in item.get("categories", [])],
                    price=item.get("price", ""),
                    highlights=item.get("highlights", []),
                )
                businesses.append(biz)

        except Exception as e:
            print(f"    ⚠️ Yelp search error: {e}")

        return businesses

    def _get_sample_reviews(self, businesses: List[YelpBusiness]) -> List[YelpReview]:
        """Get sample reviews from businesses (via Yelp reviews endpoint)."""
        reviews = []

        # Note: SerpAPI's Yelp reviews requires business alias/ID
        # For now, we'll extract what we can from highlights
        for biz in businesses:
            for highlight in biz.highlights:
                review = YelpReview(
                    text=highlight,
                    rating=int(biz.rating) if biz.rating else 0,
                    business_name=biz.name,
                )
                review.sentiment = (
                    "positive"
                    if biz.rating >= 4
                    else "negative"
                    if biz.rating <= 2
                    else "neutral"
                )
                reviews.append(review)

        return reviews

    def _analyze_sentiment(self, reviews: List[YelpReview]) -> tuple:
        """Analyze what customers love and hate."""
        loves = []
        hates = []

        love_indicators = [
            ("friendly", "friendly staff"),
            ("fast", "fast service"),
            ("clean", "cleanliness"),
            ("professional", "professionalism"),
            ("affordable", "good value"),
            ("quality", "quality work"),
            ("recommend", "highly recommended"),
            ("best", "best in area"),
            ("amazing", "amazing service"),
            ("helpful", "helpful staff"),
        ]

        hate_indicators = [
            ("slow", "slow service"),
            ("rude", "rude staff"),
            ("expensive", "overpriced"),
            ("dirty", "cleanliness issues"),
            ("wait", "long wait times"),
            ("disappointing", "disappointing"),
            ("worst", "poor experience"),
            ("avoid", "to be avoided"),
        ]

        for review in reviews:
            text_lower = review.text.lower()

            for pattern, label in love_indicators:
                if pattern in text_lower and label not in loves:
                    loves.append(label)

            for pattern, label in hate_indicators:
                if pattern in text_lower and label not in hates:
                    hates.append(label)

        return loves[:10], hates[:10]

    def _extract_phrases(self, reviews: List[YelpReview]) -> List[str]:
        """Extract common customer phrases."""
        phrases = []

        phrase_patterns = [
            "highly recommend",
            "will definitely",
            "came back",
            "go-to place",
            "best in town",
            "fair price",
            "great experience",
            "never disappointed",
            "always reliable",
            "top notch",
        ]

        for review in reviews:
            text_lower = review.text.lower()
            for phrase in phrase_patterns:
                if phrase in text_lower and phrase not in phrases:
                    phrases.append(phrase)

        return phrases

    def _get_top_rated_traits(self, businesses: List[YelpBusiness]) -> List[str]:
        """Get traits from top-rated businesses."""
        traits = []

        # Sort by rating
        sorted_biz = sorted(businesses, key=lambda x: x.rating or 0, reverse=True)
        top_biz = sorted_biz[:3]

        for biz in top_biz:
            # Categories as traits
            for cat in biz.categories[:2]:
                if cat and cat not in traits:
                    traits.append(f"Category: {cat}")

            # Price point
            if biz.price:
                trait = f"Price point: {biz.price}"
                if trait not in traits:
                    traits.append(trait)

            # Highlights
            for highlight in biz.highlights[:2]:
                if len(highlight) < 50:
                    traits.append(f"Highlight: {highlight}")

        return traits[:8]

    def _get_low_rated_issues(self, businesses: List[YelpBusiness]) -> List[str]:
        """Get issues from low-rated businesses."""
        issues = []

        # Sort by rating ascending
        sorted_biz = sorted(businesses, key=lambda x: x.rating or 5)
        low_biz = [b for b in sorted_biz if b.rating and b.rating < 3.5][:3]

        for biz in low_biz:
            if biz.rating:
                issues.append(f"{biz.name}: {biz.rating} stars - room for competitor")

        if not issues:
            issues.append(
                "Market has generally high ratings - focus on differentiation"
            )

        return issues[:5]
