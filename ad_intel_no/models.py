"""
Data models for Ad Intelligence Agent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AdData:
    """Single Facebook ad."""

    ad_id: str
    page_name: str
    page_id: Optional[str] = None

    # Ad content
    ad_text: str = ""
    headline: Optional[str] = None
    description: Optional[str] = None
    call_to_action: Optional[str] = None
    link_url: Optional[str] = None

    # Creative
    media_type: str = "unknown"  # image, video, carousel
    image_urls: List[str] = field(default_factory=list)
    video_url: Optional[str] = None

    # Status
    is_active: bool = True
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # Extracted insights
    hooks: List[str] = field(default_factory=list)
    offers: List[str] = field(default_factory=list)
    trust_signals: List[str] = field(default_factory=list)
    emotional_appeals: List[str] = field(default_factory=list)


@dataclass
class CompetitorAds:
    """All ads for a single competitor."""

    page_name: str
    page_id: Optional[str] = None
    total_ads: int = 0
    active_ads: int = 0
    ads: List[AdData] = field(default_factory=list)

    # Aggregated patterns
    common_ctas: List[str] = field(default_factory=list)
    common_hooks: List[str] = field(default_factory=list)
    media_mix: Dict[str, int] = field(default_factory=dict)  # {image: 5, video: 3}


@dataclass
class AdPatterns:
    """Extracted patterns from competitor ads."""

    # Hook patterns
    hook_types: List[Dict[str, Any]] = field(
        default_factory=list
    )  # {type, examples, frequency}

    # CTA patterns
    cta_types: List[Dict[str, Any]] = field(default_factory=list)

    # Offer patterns
    offer_types: List[Dict[str, Any]] = field(default_factory=list)

    # Creative patterns
    media_distribution: Dict[str, float] = field(default_factory=dict)

    # Messaging themes
    themes: List[str] = field(default_factory=list)

    # Trust signals used
    trust_signals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hook_types": self.hook_types,
            "cta_types": self.cta_types,
            "offer_types": self.offer_types,
            "media_distribution": self.media_distribution,
            "themes": self.themes,
            "trust_signals": self.trust_signals,
        }


@dataclass
class AdAnalysis:
    """Complete ad analysis output."""

    business_type: str
    location: str
    search_query: str
    competitors_found: int
    total_ads_analyzed: int

    # Per-competitor data
    competitor_ads: List[CompetitorAds] = field(default_factory=list)

    # Aggregated patterns
    patterns: Optional[AdPatterns] = None

    # Generated suggestions
    hook_suggestions: List[str] = field(default_factory=list)
    headline_suggestions: List[str] = field(default_factory=list)
    cta_suggestions: List[str] = field(default_factory=list)
    creative_suggestions: List[str] = field(default_factory=list)

    # Gaps/opportunities
    messaging_gaps: List[str] = field(default_factory=list)

    # TOP vs BOTTOM competitor analysis
    top_competitors: List[str] = field(default_factory=list)  # Names of best performers
    what_top_competitors_do: List[str] = field(default_factory=list)  # Learn from these
    bottom_competitors: List[str] = field(
        default_factory=list
    )  # Names of weak performers
    what_to_avoid: List[str] = field(default_factory=list)  # Don't do these things

    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "business_type": self.business_type,
            "location": self.location,
            "search_query": self.search_query,
            "competitors_found": self.competitors_found,
            "total_ads_analyzed": self.total_ads_analyzed,
            "competitor_ads": [
                {
                    "page_name": ca.page_name,
                    "total_ads": ca.total_ads,
                    "active_ads": ca.active_ads,
                    "common_ctas": ca.common_ctas,
                    "common_hooks": ca.common_hooks,
                    "media_mix": ca.media_mix,
                    "sample_ads": [
                        {
                            "ad_text": ad.ad_text[:300] if ad.ad_text else "",
                            "headline": ad.headline,
                            "call_to_action": ad.call_to_action,
                            "media_type": ad.media_type,
                        }
                        for ad in ca.ads[:5]
                    ],
                }
                for ca in self.competitor_ads
            ],
            "patterns": self.patterns.to_dict() if self.patterns else None,
            "hook_suggestions": self.hook_suggestions,
            "headline_suggestions": self.headline_suggestions,
            "cta_suggestions": self.cta_suggestions,
            "creative_suggestions": self.creative_suggestions,
            "messaging_gaps": self.messaging_gaps,
            "top_competitors": self.top_competitors,
            "what_top_competitors_do": self.what_top_competitors_do,
            "bottom_competitors": self.bottom_competitors,
            "what_to_avoid": self.what_to_avoid,
            "generated_at": self.generated_at,
        }
