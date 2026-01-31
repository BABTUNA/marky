"""
Data models for Review Intelligence Agent.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ReviewData:
    """Single review from Google Maps."""
    reviewer_name: str
    rating: int  # 1-5 stars
    text: str
    date: Optional[str] = None
    
    # Extracted insights
    sentiment: Optional[str] = None  # positive, negative, neutral
    pain_points: List[str] = field(default_factory=list)
    praise_points: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # Owner response
    owner_response: Optional[str] = None
    owner_response_date: Optional[str] = None


@dataclass
class CompetitorReviews:
    """Reviews for a single competitor."""
    business_name: str
    place_id: str
    overall_rating: float
    total_reviews: int
    reviews: List[ReviewData] = field(default_factory=list)
    
    # Aggregated insights
    common_praise: List[str] = field(default_factory=list)
    common_complaints: List[str] = field(default_factory=list)
    response_rate: float = 0.0  # % of reviews with owner response


@dataclass
class VoiceOfCustomer:
    """Extracted customer voice patterns for ad copy."""
    # Direct quotes (actual customer language)
    praise_quotes: List[str] = field(default_factory=list)
    complaint_quotes: List[str] = field(default_factory=list)
    
    # Patterns
    pain_points: List[Dict[str, Any]] = field(default_factory=list)  # {point, frequency, examples}
    desires: List[Dict[str, Any]] = field(default_factory=list)  # {desire, frequency, examples}
    objections: List[Dict[str, Any]] = field(default_factory=list)  # {objection, frequency, examples}
    
    # Language bank
    power_words: List[str] = field(default_factory=list)
    emotional_triggers: List[str] = field(default_factory=list)
    trust_phrases: List[str] = field(default_factory=list)
    
    # For ad hooks
    hook_templates: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "praise_quotes": self.praise_quotes,
            "complaint_quotes": self.complaint_quotes,
            "pain_points": self.pain_points,
            "desires": self.desires,
            "objections": self.objections,
            "power_words": self.power_words,
            "emotional_triggers": self.emotional_triggers,
            "trust_phrases": self.trust_phrases,
            "hook_templates": self.hook_templates,
        }


@dataclass
class ReviewAnalysis:
    """Complete review analysis output."""
    business_type: str
    location: str
    competitors_analyzed: int
    total_reviews_analyzed: int
    
    # Per-competitor data
    competitor_reviews: List[CompetitorReviews] = field(default_factory=list)
    
    # Aggregated voice of customer
    voice_of_customer: Optional[VoiceOfCustomer] = None
    
    # Top/worst comparison
    top_competitor_themes: List[str] = field(default_factory=list)
    worst_competitor_themes: List[str] = field(default_factory=list)
    
    # Generated insights
    ad_hooks: List[str] = field(default_factory=list)
    headline_suggestions: List[str] = field(default_factory=list)
    
    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "business_type": self.business_type,
            "location": self.location,
            "competitors_analyzed": self.competitors_analyzed,
            "total_reviews_analyzed": self.total_reviews_analyzed,
            "competitor_reviews": [
                {
                    "business_name": cr.business_name,
                    "overall_rating": cr.overall_rating,
                    "total_reviews": cr.total_reviews,
                    "reviews_scraped": len(cr.reviews),
                    "common_praise": cr.common_praise,
                    "common_complaints": cr.common_complaints,
                    "response_rate": cr.response_rate,
                    "sample_reviews": [
                        {"rating": r.rating, "text": r.text[:200], "sentiment": r.sentiment}
                        for r in cr.reviews[:5]
                    ],
                }
                for cr in self.competitor_reviews
            ],
            "voice_of_customer": self.voice_of_customer.to_dict() if self.voice_of_customer else None,
            "top_competitor_themes": self.top_competitor_themes,
            "worst_competitor_themes": self.worst_competitor_themes,
            "ad_hooks": self.ad_hooks,
            "headline_suggestions": self.headline_suggestions,
            "generated_at": self.generated_at,
        }
