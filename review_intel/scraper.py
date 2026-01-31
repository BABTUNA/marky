"""
Google Reviews scraper using SerpAPI.
"""

import os
import re
import requests
from typing import List, Optional, Dict, Any
from .models import ReviewData, CompetitorReviews


class GoogleReviewsScraper:
    """Scrapes Google Reviews using SerpAPI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not set. Get one at https://serpapi.com")
        
        self.base_url = "https://serpapi.com/search"
    
    def get_reviews(
        self,
        place_id: str,
        business_name: str,
        max_reviews: int = 20,
        sort_by: str = "qualityScore",  # qualityScore, newestFirst, ratingHigh, ratingLow
    ) -> CompetitorReviews:
        """
        Fetch reviews for a business.
        
        Args:
            place_id: Google Maps place_id (or data_id)
            business_name: Name for reference
            max_reviews: Maximum reviews to fetch
            sort_by: Sort order for reviews
        
        Returns:
            CompetitorReviews with all review data
        """
        reviews: List[ReviewData] = []
        overall_rating = 0.0
        total_reviews = 0
        
        try:
            # Fetch reviews from SerpAPI
            params = {
                "engine": "google_maps_reviews",
                "place_id": place_id,
                "api_key": self.api_key,
                "sort_by": sort_by,
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Get place info
            place_info = data.get("place_info", {})
            overall_rating = place_info.get("rating", 0.0)
            total_reviews = place_info.get("reviews", 0)
            
            # Parse reviews
            for review_data in data.get("reviews", [])[:max_reviews]:
                review = ReviewData(
                    reviewer_name=review_data.get("user", {}).get("name", "Anonymous"),
                    rating=review_data.get("rating", 0),
                    text=review_data.get("snippet", "") or review_data.get("extracted_snippet", {}).get("original", ""),
                    date=review_data.get("date", ""),
                    owner_response=review_data.get("response", {}).get("snippet") if review_data.get("response") else None,
                    owner_response_date=review_data.get("response", {}).get("date") if review_data.get("response") else None,
                )
                
                # Basic sentiment from rating
                if review.rating >= 4:
                    review.sentiment = "positive"
                elif review.rating <= 2:
                    review.sentiment = "negative"
                else:
                    review.sentiment = "neutral"
                
                # Extract keywords and points
                review.keywords = self._extract_keywords(review.text)
                if review.sentiment == "positive":
                    review.praise_points = self._extract_praise(review.text)
                elif review.sentiment == "negative":
                    review.pain_points = self._extract_complaints(review.text)
                
                reviews.append(review)
            
            # If no reviews via place_id, try data_id format
            if not reviews and not place_id.startswith("0x"):
                # Try as data_id
                params["data_id"] = place_id
                del params["place_id"]
                
                response = requests.get(self.base_url, params=params, timeout=30)
                if response.ok:
                    data = response.json()
                    for review_data in data.get("reviews", [])[:max_reviews]:
                        review = ReviewData(
                            reviewer_name=review_data.get("user", {}).get("name", "Anonymous"),
                            rating=review_data.get("rating", 0),
                            text=review_data.get("snippet", "") or "",
                            date=review_data.get("date", ""),
                        )
                        if review.rating >= 4:
                            review.sentiment = "positive"
                        elif review.rating <= 2:
                            review.sentiment = "negative"
                        else:
                            review.sentiment = "neutral"
                        reviews.append(review)
                        
        except requests.RequestException as e:
            print(f"    Error fetching reviews for {business_name}: {e}")
        except Exception as e:
            print(f"    Error parsing reviews for {business_name}: {e}")
        
        # Calculate response rate
        response_count = sum(1 for r in reviews if r.owner_response)
        response_rate = response_count / len(reviews) if reviews else 0.0
        
        # Aggregate common themes
        all_praise = []
        all_complaints = []
        for r in reviews:
            all_praise.extend(r.praise_points)
            all_complaints.extend(r.pain_points)
        
        return CompetitorReviews(
            business_name=business_name,
            place_id=place_id,
            overall_rating=overall_rating,
            total_reviews=total_reviews,
            reviews=reviews,
            common_praise=self._get_top_items(all_praise, 5),
            common_complaints=self._get_top_items(all_complaints, 5),
            response_rate=response_rate,
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from review text."""
        # Common positive/negative keywords for service businesses
        keywords = []
        text_lower = text.lower()
        
        positive_keywords = [
            "professional", "quick", "fast", "friendly", "honest", "reliable",
            "clean", "punctual", "affordable", "knowledgeable", "helpful",
            "efficient", "courteous", "thorough", "responsive", "fair",
            "excellent", "amazing", "great", "recommend", "satisfied",
        ]
        
        negative_keywords = [
            "late", "rude", "expensive", "overpriced", "unprofessional",
            "slow", "messy", "dishonest", "unreliable", "poor",
            "terrible", "awful", "never", "worst", "avoid",
            "disappointed", "frustrating", "overcharged", "no-show",
        ]
        
        for kw in positive_keywords:
            if kw in text_lower:
                keywords.append(f"+{kw}")
        
        for kw in negative_keywords:
            if kw in text_lower:
                keywords.append(f"-{kw}")
        
        return keywords
    
    def _extract_praise(self, text: str) -> List[str]:
        """Extract praise points from positive review."""
        points = []
        text_lower = text.lower()
        
        praise_patterns = [
            (r"on time|punctual|arrived.*quickly|showed up.*fast", "punctuality"),
            (r"fair price|affordable|reasonable|good value|didn't overcharge", "fair pricing"),
            (r"professional|knowledgeable|knew what|expert", "expertise"),
            (r"friendly|nice|courteous|polite|pleasant", "friendly service"),
            (r"clean|cleaned up|neat|tidy", "cleanliness"),
            (r"fast|quick|efficient|same day|right away", "speed"),
            (r"honest|trustworthy|didn't try to upsell|straightforward", "honesty"),
            (r"explained|communicated|kept.*informed|called ahead", "communication"),
            (r"emergency|after hours|weekend|24.?7", "availability"),
            (r"recommend|definitely use again|will call again", "recommendation"),
        ]
        
        for pattern, label in praise_patterns:
            if re.search(pattern, text_lower):
                points.append(label)
        
        return points
    
    def _extract_complaints(self, text: str) -> List[str]:
        """Extract pain points from negative review."""
        points = []
        text_lower = text.lower()
        
        complaint_patterns = [
            (r"late|no.?show|didn't show|waited|never came", "unreliable timing"),
            (r"expensive|overpriced|overcharged|too much|rip.?off", "overpricing"),
            (r"rude|unprofessional|disrespectful|attitude", "poor attitude"),
            (r"messy|didn't clean|left.*mess", "left mess"),
            (r"didn't fix|still broken|came back|had to call again", "poor quality work"),
            (r"no response|didn't call back|ignored|ghosted", "poor communication"),
            (r"pushy|upsell|unnecessary|didn't need", "pushy sales"),
            (r"hidden|surprise|extra charge|not quoted", "hidden fees"),
            (r"damage|broke|scratched|ruined", "caused damage"),
            (r"license|insurance|permit", "licensing concerns"),
        ]
        
        for pattern, label in complaint_patterns:
            if re.search(pattern, text_lower):
                points.append(label)
        
        return points
    
    def _get_top_items(self, items: List[str], n: int) -> List[str]:
        """Get most common items."""
        from collections import Counter
        counts = Counter(items)
        return [item for item, _ in counts.most_common(n)]
