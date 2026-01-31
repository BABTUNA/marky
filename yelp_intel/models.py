"""
Data models for Yelp Intelligence Agent.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class YelpBusiness:
    """A business from Yelp search results."""
    place_id: str
    name: str
    link: str
    rating: float = 0.0
    review_count: int = 0
    categories: List[str] = field(default_factory=list)
    price: Optional[str] = None  # $, $$, $$$, $$$$
    neighborhood: Optional[str] = None
    phone: Optional[str] = None
    snippet: Optional[str] = None  # Preview review text
    thumbnail: Optional[str] = None
    service_options: Dict[str, bool] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "place_id": self.place_id,
            "name": self.name,
            "link": self.link,
            "rating": self.rating,
            "review_count": self.review_count,
            "categories": self.categories,
            "price": self.price,
            "neighborhood": self.neighborhood,
            "phone": self.phone,
            "snippet": self.snippet,
            "service_options": self.service_options,
        }


@dataclass
class YelpReview:
    """A review from Yelp."""
    user_name: str
    rating: int
    text: str
    date: str
    user_location: Optional[str] = None
    photos: List[str] = field(default_factory=list)
    owner_reply: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_name": self.user_name,
            "rating": self.rating,
            "text": self.text,
            "date": self.date,
            "user_location": self.user_location,
            "has_photos": len(self.photos) > 0,
            "owner_replied": self.owner_reply is not None,
        }


@dataclass
class CustomerInsights:
    """Aggregated customer insights from reviews."""
    # Pain points (complaints)
    pain_points: List[str] = field(default_factory=list)
    pain_point_quotes: List[str] = field(default_factory=list)
    
    # Praise points (what customers love)
    praise_points: List[str] = field(default_factory=list)
    praise_quotes: List[str] = field(default_factory=list)
    
    # Common themes/topics mentioned
    themes: List[str] = field(default_factory=list)
    
    # Customer language (phrases to use in ads)
    customer_phrases: List[str] = field(default_factory=list)
    
    # Questions customers ask
    questions: List[str] = field(default_factory=list)
    
    # Price sensitivity signals
    price_mentions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pain_points": self.pain_points,
            "pain_point_quotes": self.pain_point_quotes[:10],  # Top 10
            "praise_points": self.praise_points,
            "praise_quotes": self.praise_quotes[:10],
            "themes": self.themes,
            "customer_phrases": self.customer_phrases,
            "questions": self.questions,
            "price_mentions": self.price_mentions,
        }


@dataclass
class AdSuggestions:
    """Ad suggestions derived from customer insights."""
    hooks: List[str] = field(default_factory=list)
    headlines: List[str] = field(default_factory=list)
    pain_point_hooks: List[str] = field(default_factory=list)
    trust_signals: List[str] = field(default_factory=list)
    differentiators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hooks": self.hooks,
            "headlines": self.headlines,
            "pain_point_hooks": self.pain_point_hooks,
            "trust_signals": self.trust_signals,
            "differentiators": self.differentiators,
        }


@dataclass
class YelpAnalysis:
    """Complete Yelp analysis results."""
    business_type: str
    location: str
    businesses: List[YelpBusiness] = field(default_factory=list)
    total_reviews_analyzed: int = 0
    insights: CustomerInsights = field(default_factory=CustomerInsights)
    ad_suggestions: AdSuggestions = field(default_factory=AdSuggestions)
    
    # Rating distribution
    rating_distribution: Dict[int, int] = field(default_factory=dict)
    avg_rating: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "business_type": self.business_type,
            "location": self.location,
            "businesses_analyzed": len(self.businesses),
            "total_reviews_analyzed": self.total_reviews_analyzed,
            "avg_rating": self.avg_rating,
            "rating_distribution": self.rating_distribution,
            "businesses": [b.to_dict() for b in self.businesses],
            "insights": self.insights.to_dict(),
            "ad_suggestions": self.ad_suggestions.to_dict(),
        }
