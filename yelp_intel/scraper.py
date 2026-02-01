"""
Yelp scraper using SerpAPI.
Scrapes business listings and reviews from Yelp.
"""

import os
import requests
from typing import List, Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .models import YelpBusiness, YelpReview

# SerpAPI can be slow; use longer timeout and retries
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3


class YelpScraper:
    """
    Scrapes Yelp data using SerpAPI.
    
    APIs used:
    - Yelp Search API (engine=yelp) - Find businesses
    - Yelp Reviews API (engine=yelp_reviews) - Get reviews
    
    Uses the same SERPAPI_KEY as other agents.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not set. Get one at https://serpapi.com")
        
        self.base_url = "https://serpapi.com/search"
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
        reraise=True,
    )
    def _request_with_retry(self, params: dict) -> dict:
        """Make SerpAPI request with retries on timeout/connection errors."""
        response = requests.get(
            self.base_url, params=params, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def search_businesses(
        self,
        query: str,
        location: str,
        max_results: int = 10,
        sort_by: str = "recommended",  # recommended, rating, review_count
    ) -> List[YelpBusiness]:
        """
        Search for businesses on Yelp.
        
        Args:
            query: Search query (e.g., "plumber", "pizza")
            location: Location (e.g., "Providence, RI")
            max_results: Maximum businesses to return
            sort_by: Sort order (recommended, rating, review_count)
        
        Returns:
            List of YelpBusiness objects
        """
        businesses: List[YelpBusiness] = []
        
        print(f"    Searching Yelp for '{query}' in '{location}'...")
        
        try:
            params = {
                "engine": "yelp",
                "find_desc": query,
                "find_loc": location,
                "sortby": sort_by,
                "api_key": self.api_key,
            }
            
            data = self._request_with_retry(params)
            
            # Parse organic results
            organic = data.get("organic_results", [])
            
            if organic:
                print(f"    Found {len(organic)} businesses")
                
                for item in organic[:max_results]:
                    business = self._parse_business(item)
                    if business:
                        businesses.append(business)
            else:
                print("    No businesses found")
            
            # Also check ads (sponsored results)
            ads = data.get("ads_results", [])
            if ads:
                print(f"    Found {len(ads)} sponsored listings")
                
        except requests.RequestException as e:
            print(f"    Request error: {e}")
        except Exception as e:
            print(f"    Error: {e}")
        
        return businesses
    
    def get_reviews(
        self,
        place_id: str,
        max_reviews: int = 20,
        sort_by: str = "relevance_desc",  # relevance_desc, date_desc, rating_desc, rating_asc
    ) -> List[YelpReview]:
        """
        Get reviews for a specific business.
        
        Args:
            place_id: Yelp place ID (e.g., "ED7A7vDdg8yLNKJTSVHHmg")
            max_reviews: Maximum reviews to return
            sort_by: Sort order
        
        Returns:
            List of YelpReview objects
        """
        reviews: List[YelpReview] = []
        
        try:
            params = {
                "engine": "yelp_reviews",
                "place_id": place_id,
                "sortby": sort_by,
                "num": min(max_reviews, 49),  # API max is 49
                "api_key": self.api_key,
            }
            
            data = self._request_with_retry(params)
            
            # Parse reviews
            reviews_data = data.get("reviews", [])
            
            for item in reviews_data[:max_reviews]:
                review = self._parse_review(item)
                if review:
                    reviews.append(review)
                    
        except requests.RequestException as e:
            print(f"      Review fetch error: {e}")
        except Exception as e:
            print(f"      Error: {e}")
        
        return reviews
    
    def get_negative_reviews(
        self,
        place_id: str,
        max_reviews: int = 10,
    ) -> List[YelpReview]:
        """
        Get low-rated reviews (1-2 stars) for pain point analysis.
        """
        reviews: List[YelpReview] = []
        
        try:
            params = {
                "engine": "yelp_reviews",
                "place_id": place_id,
                "sortby": "rating_asc",  # Lowest rated first
                "rating": "1,2",  # Only 1-2 star reviews
                "num": min(max_reviews, 49),
                "api_key": self.api_key,
            }
            
            data = self._request_with_retry(params)
            
            reviews_data = data.get("reviews", [])
            
            for item in reviews_data[:max_reviews]:
                review = self._parse_review(item)
                if review:
                    reviews.append(review)
                    
        except Exception as e:
            print(f"      Error fetching negative reviews: {e}")
        
        return reviews
    
    def get_positive_reviews(
        self,
        place_id: str,
        max_reviews: int = 10,
    ) -> List[YelpReview]:
        """
        Get high-rated reviews (4-5 stars) for praise analysis.
        """
        reviews: List[YelpReview] = []
        
        try:
            params = {
                "engine": "yelp_reviews",
                "place_id": place_id,
                "sortby": "rating_desc",  # Highest rated first
                "rating": "4,5",  # Only 4-5 star reviews
                "num": min(max_reviews, 49),
                "api_key": self.api_key,
            }
            
            data = self._request_with_retry(params)
            
            reviews_data = data.get("reviews", [])
            
            for item in reviews_data[:max_reviews]:
                review = self._parse_review(item)
                if review:
                    reviews.append(review)
                    
        except Exception as e:
            print(f"      Error fetching positive reviews: {e}")
        
        return reviews
    
    def _parse_business(self, item: Dict[str, Any]) -> Optional[YelpBusiness]:
        """Parse business from Yelp search results."""
        try:
            # Get place_id - Yelp returns array of IDs
            place_ids = item.get("place_ids", [])
            place_id = place_ids[0] if place_ids else ""
            
            # Get categories
            categories = []
            for cat in item.get("categories", []):
                if isinstance(cat, dict):
                    categories.append(cat.get("title", ""))
                elif isinstance(cat, str):
                    categories.append(cat)
            
            business = YelpBusiness(
                place_id=place_id,
                name=item.get("title", "Unknown"),
                link=item.get("link", ""),
                rating=float(item.get("rating", 0)),
                review_count=int(item.get("reviews", 0)),
                categories=categories,
                price=item.get("price"),
                neighborhood=item.get("neighborhoods"),
                phone=item.get("phone"),
                snippet=item.get("snippet"),
                thumbnail=item.get("thumbnail"),
                service_options=item.get("service_options", {}),
            )
            
            return business
            
        except Exception as e:
            print(f"    Error parsing business: {e}")
            return None
    
    def _parse_review(self, item: Dict[str, Any]) -> Optional[YelpReview]:
        """Parse review from Yelp reviews API."""
        try:
            # Get user info
            user = item.get("user", {})
            user_name = user.get("name", "Anonymous")
            user_location = user.get("address")
            
            # Get comment
            comment = item.get("comment", {})
            text = comment.get("text", "") if isinstance(comment, dict) else str(comment)
            
            # Get photos
            photos = []
            for photo in item.get("photos", []):
                if isinstance(photo, dict):
                    photos.append(photo.get("link", ""))
                elif isinstance(photo, str):
                    photos.append(photo)
            
            # Get owner reply
            owner_reply = None
            owner_replies = item.get("owner_replies", [])
            if owner_replies:
                owner_reply = owner_replies[0].get("comment", "")
            
            review = YelpReview(
                user_name=user_name,
                rating=int(item.get("rating", 0)),
                text=text,
                date=item.get("date", ""),
                user_location=user_location,
                photos=photos,
                owner_reply=owner_reply,
            )
            
            return review
            
        except Exception as e:
            print(f"      Error parsing review: {e}")
            return None
