"""
Data models for Local Competitor Intelligence Agent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


# ============================================================================
# Input Models
# ============================================================================

@dataclass
class SearchInput:
    """Input for competitor search."""
    business_type: str  # e.g., "plumber", "restaurant", "electrician"
    location: str  # e.g., "Providence, RI" or "02912" or "41.8239,-71.4128"
    radius_miles: float = 10.0
    max_competitors: int = 20


# ============================================================================
# Competitor Discovery Models
# ============================================================================

@dataclass
class Competitor:
    """A discovered competitor business."""
    name: str
    address: str
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_level: Optional[str] = None  # "$", "$$", "$$$"
    hours: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    place_id: Optional[str] = None
    
    # Scraped data (filled later)
    website_content: Optional[str] = None
    services: List[str] = field(default_factory=list)
    pricing_info: List[str] = field(default_factory=list)
    taglines: List[str] = field(default_factory=list)
    trust_signals: List[str] = field(default_factory=list)
    unique_selling_points: List[str] = field(default_factory=list)


@dataclass
class DiscoveryResult:
    """Result of competitor discovery."""
    query: SearchInput
    competitors: List[Competitor]
    total_found: int
    source: str  # "serpapi", "outscraper", "google_places"
    searched_at: datetime = field(default_factory=datetime.now)


# ============================================================================
# Website Scraping Models
# ============================================================================

@dataclass
class ScrapedPage:
    """A scraped webpage."""
    url: str
    title: Optional[str] = None
    content: str = ""  # Markdown or plain text
    scrape_method: str = ""  # "firecrawl", "jina", etc.
    success: bool = True
    error: Optional[str] = None


@dataclass 
class WebsiteData:
    """Aggregated data from a competitor's website."""
    competitor_name: str
    website_url: str
    pages_scraped: List[ScrapedPage] = field(default_factory=list)
    
    # Extracted information
    services: List[str] = field(default_factory=list)
    pricing: List[str] = field(default_factory=list)
    taglines: List[str] = field(default_factory=list)
    trust_signals: List[str] = field(default_factory=list)
    unique_points: List[str] = field(default_factory=list)
    contact_info: Dict[str, str] = field(default_factory=dict)
    
    # Raw content for analysis
    full_text: str = ""


# ============================================================================
# Analysis & Output Models
# ============================================================================

class InsightType(Enum):
    """Types of competitive insights."""
    SERVICE_GAP = "service_gap"  # Service competitors don't offer
    PRICING_OPPORTUNITY = "pricing_opportunity"  # Pricing differentiation
    TRUST_DIFFERENTIATOR = "trust_differentiator"  # Trust signal to emphasize
    MESSAGING_ANGLE = "messaging_angle"  # Unique messaging opportunity
    WEAKNESS_EXPLOIT = "weakness_exploit"  # Competitor weakness to counter


@dataclass
class CompetitiveInsight:
    """A single competitive insight."""
    insight_type: InsightType
    title: str
    description: str
    evidence: List[str] = field(default_factory=list)  # Supporting data
    suggested_copy: List[str] = field(default_factory=list)  # Ad copy suggestions
    priority: int = 1  # 1 = highest


@dataclass
class MarketAnalysis:
    """Analysis of the local market."""
    business_type: str
    location: str
    competitors_analyzed: int
    
    # Common patterns
    common_services: List[str] = field(default_factory=list)
    common_trust_signals: List[str] = field(default_factory=list)
    price_range: Optional[str] = None
    
    # Gaps and opportunities
    service_gaps: List[str] = field(default_factory=list)
    messaging_opportunities: List[str] = field(default_factory=list)
    
    # Competitor weaknesses (from reviews if available)
    common_complaints: List[str] = field(default_factory=list)


@dataclass
class AdDifferentiator:
    """An advertising differentiation angle."""
    angle_name: str
    hook: str
    supporting_points: List[str] = field(default_factory=list)
    proof_needed: str = ""
    best_for: str = ""  # "Facebook ads", "Google ads", "Flyers", etc.


@dataclass
class IntelligenceReport:
    """Complete intelligence report output."""
    # Input
    search_input: SearchInput
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Competitors
    competitors: List[Competitor] = field(default_factory=list)
    
    # Market analysis
    market_analysis: Optional[MarketAnalysis] = None
    
    # Insights
    insights: List[CompetitiveInsight] = field(default_factory=list)
    
    # Ad angles
    differentiators: List[AdDifferentiator] = field(default_factory=list)
    
    # Quick-use outputs
    headline_suggestions: List[str] = field(default_factory=list)
    tagline_suggestions: List[str] = field(default_factory=list)
    trust_signals_to_use: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "search": {
                "business_type": self.search_input.business_type,
                "location": self.search_input.location,
                "radius_miles": self.search_input.radius_miles,
            },
            "generated_at": self.generated_at.isoformat(),
            "competitors_found": len(self.competitors),
            "competitors": [
                {
                    "name": c.name,
                    "address": c.address,
                    "website": c.website,
                    "rating": c.rating,
                    "review_count": c.review_count,
                    "services": c.services,
                    "trust_signals": c.trust_signals,
                    "unique_selling_points": c.unique_selling_points,
                }
                for c in self.competitors
            ],
            "market_analysis": {
                "common_services": self.market_analysis.common_services if self.market_analysis else [],
                "common_trust_signals": self.market_analysis.common_trust_signals if self.market_analysis else [],
                "service_gaps": self.market_analysis.service_gaps if self.market_analysis else [],
                "common_complaints": self.market_analysis.common_complaints if self.market_analysis else [],
            } if self.market_analysis else None,
            "insights": [
                {
                    "type": i.insight_type.value,
                    "title": i.title,
                    "description": i.description,
                    "suggested_copy": i.suggested_copy,
                    "priority": i.priority,
                }
                for i in self.insights
            ],
            "differentiators": [
                {
                    "angle": d.angle_name,
                    "hook": d.hook,
                    "supporting_points": d.supporting_points,
                    "best_for": d.best_for,
                }
                for d in self.differentiators
            ],
            "quick_use": {
                "headlines": self.headline_suggestions,
                "taglines": self.tagline_suggestions,
                "trust_signals": self.trust_signals_to_use,
            },
        }
