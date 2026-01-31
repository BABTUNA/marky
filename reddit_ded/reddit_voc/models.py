"""
Data models for Reddit VoC Agent.
Defines the structure for scraped data and output artifacts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


# ============================================================================
# Input Models
# ============================================================================

@dataclass
class ResearchInput:
    """Input specification for VoC research."""
    product: str
    audience: str
    market: str
    keywords: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    language: str = "en"


# ============================================================================
# Reddit Data Models
# ============================================================================

@dataclass
class Subreddit:
    """Represents a discovered subreddit."""
    name: str
    display_name: str
    subscribers: int
    description: str
    relevance_score: float = 0.0
    url: str = ""
    
    def __post_init__(self):
        if not self.url:
            self.url = f"https://reddit.com/r/{self.name}"


@dataclass
class Post:
    """Represents a Reddit post."""
    id: str
    subreddit: str
    title: str
    selftext: str
    score: int
    num_comments: int
    created_utc: float
    url: str
    permalink: str
    
    @property
    def full_url(self) -> str:
        return f"https://reddit.com{self.permalink}"
    
    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created_utc)


@dataclass
class Comment:
    """Represents a Reddit comment."""
    id: str
    post_id: str
    subreddit: str
    body: str
    score: int
    created_utc: float
    parent_id: Optional[str] = None
    
    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created_utc)


# ============================================================================
# VoC Analysis Models
# ============================================================================

class SignalType(Enum):
    """Types of VoC signals in text."""
    PAIN_POINT = "pain_point"
    DESIRE = "desire"
    OBJECTION = "objection"
    COMPARISON = "comparison"
    PURCHASE_INTENT = "purchase_intent"
    RECOMMENDATION = "recommendation"


@dataclass
class VoCSignal:
    """A detected VoC signal from text."""
    text: str
    signal_type: SignalType
    source_comment_id: str
    source_subreddit: str
    confidence: float = 0.0
    keywords_matched: List[str] = field(default_factory=list)


@dataclass
class Theme:
    """A clustered theme from VoC signals."""
    name: str
    weight: float  # 0.0 to 1.0, proportion of mentions
    example_quotes: List[str] = field(default_factory=list)
    common_objections: List[str] = field(default_factory=list)
    desired_outcomes: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


# ============================================================================
# Output Models (for downstream creative agents)
# ============================================================================

@dataclass
class VoiceOfCustomerBrief:
    """Main VoC output document."""
    product: str
    audience: str
    market: str
    
    top_themes: List[Theme] = field(default_factory=list)
    language_bank: List[str] = field(default_factory=list)  # Phrases to reuse
    
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product": self.product,
            "audience": self.audience,
            "market": self.market,
            "top_themes": [
                {
                    "theme": t.name,
                    "weight": t.weight,
                    "example_quotes": t.example_quotes,
                    "common_objections": t.common_objections,
                    "desired_outcomes": t.desired_outcomes,
                }
                for t in self.top_themes
            ],
            "language_bank": self.language_bank,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class Angle:
    """An advertising angle derived from themes."""
    name: str
    promise: str
    target_emotion: str
    best_for_audience: str
    supporting_points: List[str] = field(default_factory=list)


@dataclass
class AnglePlaybook:
    """Collection of advertising angles."""
    angles: List[Angle] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "angles": [
                {
                    "angle_name": a.name,
                    "promise": a.promise,
                    "target_emotion": a.target_emotion,
                    "best_for_audience": a.best_for_audience,
                    "supporting_points": a.supporting_points,
                }
                for a in self.angles
            ]
        }


@dataclass
class Hook:
    """An ad hook line."""
    text: str
    mapped_theme: str
    tone: str  # e.g., "urgent", "curious", "empathetic"
    recommended_opening_visual: str = ""


@dataclass
class HookBank:
    """Collection of hook lines."""
    hooks: List[Hook] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hooks": [
                {
                    "hook_text": h.text,
                    "mapped_theme": h.mapped_theme,
                    "tone": h.tone,
                    "recommended_opening_visual": h.recommended_opening_visual,
                }
                for h in self.hooks
            ]
        }


@dataclass
class Objection:
    """An objection with rebuttals."""
    objection: str
    rebuttal_lines: List[str] = field(default_factory=list)
    proof_visuals: List[str] = field(default_factory=list)


@dataclass
class ObjectionHandling:
    """Collection of objection handlers."""
    objections: List[Objection] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "objections": [
                {
                    "objection": o.objection,
                    "rebuttal_lines": o.rebuttal_lines,
                    "proof_visuals": o.proof_visuals,
                }
                for o in self.objections
            ]
        }


@dataclass
class Source:
    """Source tracking for research."""
    subreddit: str
    post_url: str
    comment_count_used: int
    date_range: str  # e.g., "2024-01-15 to 2024-01-31"


@dataclass
class SourceMap:
    """Collection of sources used."""
    sources: List[Source] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sources": [
                {
                    "subreddit": s.subreddit,
                    "post_url": s.post_url,
                    "comment_count_used": s.comment_count_used,
                    "date_range": s.date_range,
                }
                for s in self.sources
            ]
        }


@dataclass
class ResearchOutput:
    """Complete research output package."""
    voc_brief: VoiceOfCustomerBrief
    angle_playbook: AnglePlaybook
    hook_bank: HookBank
    objection_handling: ObjectionHandling
    source_map: SourceMap
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "voice_of_customer_brief": self.voc_brief.to_dict(),
            "angle_playbook": self.angle_playbook.to_dict(),
            "hook_bank": self.hook_bank.to_dict(),
            "objection_handling": self.objection_handling.to_dict(),
            "source_map": self.source_map.to_dict(),
        }
