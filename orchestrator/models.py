"""
Pydantic models for Marky orchestrator.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class AdResearchRequest:
    """Request to run ad research for a business."""
    business_type: str
    location: str
    
    # Optional parameters
    max_competitors: int = 5
    reviews_per_competitor: int = 10
    include_trends: bool = True


@dataclass
class CompetitorInsight:
    """Insight about a competitor."""
    name: str
    rating: float
    review_count: int
    website: Optional[str] = None
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)


@dataclass
class CustomerVoice:
    """Voice of customer data from reviews."""
    pain_points: List[str] = field(default_factory=list)
    desires: List[str] = field(default_factory=list)
    praise_quotes: List[str] = field(default_factory=list)
    complaint_quotes: List[str] = field(default_factory=list)
    common_themes: List[str] = field(default_factory=list)


@dataclass
class SeasonalTiming:
    """Seasonal timing recommendations."""
    keyword: str
    peak_months: List[str] = field(default_factory=list)
    low_months: List[str] = field(default_factory=list)
    avg_cpc: float = 0.0
    monthly_volume: int = 0
    recommendation: str = ""


@dataclass
class AdDifferentiator:
    """Ad differentiation angle."""
    angle_name: str
    hook: str
    headline: str
    description: str
    best_for: str
    trust_signals: List[str] = field(default_factory=list)


@dataclass
class AdResearchResult:
    """Complete ad research result from all agents."""
    business_type: str
    location: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Competitor data
    competitors: List[CompetitorInsight] = field(default_factory=list)
    market_summary: str = ""
    
    # Voice of customer
    customer_voice: Optional[CustomerVoice] = None
    
    # Seasonal timing
    timing: List[SeasonalTiming] = field(default_factory=list)
    
    # Generated ad strategies
    differentiators: List[AdDifferentiator] = field(default_factory=list)
    headline_suggestions: List[str] = field(default_factory=list)
    trust_signals: List[str] = field(default_factory=list)
    
    # Synthesis
    executive_summary: str = ""
    key_insights: List[str] = field(default_factory=list)
    recommended_hooks: List[str] = field(default_factory=list)
    
    # Metadata
    agents_used: List[str] = field(default_factory=list)
    total_time_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "business_type": self.business_type,
            "location": self.location,
            "timestamp": self.timestamp,
            "competitors": [
                {
                    "name": c.name,
                    "rating": c.rating,
                    "review_count": c.review_count,
                    "website": c.website,
                    "strengths": c.strengths,
                    "weaknesses": c.weaknesses,
                    "services": c.services,
                }
                for c in self.competitors
            ],
            "market_summary": self.market_summary,
            "customer_voice": {
                "pain_points": self.customer_voice.pain_points,
                "desires": self.customer_voice.desires,
                "praise_quotes": self.customer_voice.praise_quotes,
                "complaint_quotes": self.customer_voice.complaint_quotes,
                "common_themes": self.customer_voice.common_themes,
            } if self.customer_voice else None,
            "timing": [
                {
                    "keyword": t.keyword,
                    "peak_months": t.peak_months,
                    "low_months": t.low_months,
                    "avg_cpc": t.avg_cpc,
                    "monthly_volume": t.monthly_volume,
                    "recommendation": t.recommendation,
                }
                for t in self.timing
            ],
            "differentiators": [
                {
                    "angle_name": d.angle_name,
                    "hook": d.hook,
                    "headline": d.headline,
                    "description": d.description,
                    "best_for": d.best_for,
                    "trust_signals": d.trust_signals,
                }
                for d in self.differentiators
            ],
            "headline_suggestions": self.headline_suggestions,
            "trust_signals": self.trust_signals,
            "executive_summary": self.executive_summary,
            "key_insights": self.key_insights,
            "recommended_hooks": self.recommended_hooks,
            "agents_used": self.agents_used,
            "total_time_seconds": self.total_time_seconds,
            "errors": self.errors,
        }


@dataclass
class AdResearchResponse:
    """Response from the Marky agent."""
    success: bool
    result: Optional[AdResearchResult] = None
    error: Optional[str] = None
    
    def to_markdown(self) -> str:
        """Convert result to markdown for chat display."""
        if not self.success or not self.result:
            return f"❌ Error: {self.error or 'Unknown error'}"
        
        r = self.result
        lines = [
            f"# 📊 Ad Research Report: {r.business_type} in {r.location}",
            "",
            "## Executive Summary",
            r.executive_summary or "_No summary available_",
            "",
        ]
        
        # Key Insights
        if r.key_insights:
            lines.append("## 💡 Key Insights")
            for insight in r.key_insights[:5]:
                lines.append(f"- {insight}")
            lines.append("")
        
        # Competitor Overview
        if r.competitors:
            lines.append("## 🏢 Competitor Overview")
            for c in r.competitors[:5]:
                lines.append(f"- **{c.name}** ({c.rating}⭐, {c.review_count} reviews)")
                if c.strengths:
                    lines.append(f"  - Strengths: {', '.join(c.strengths[:3])}")
                if c.weaknesses:
                    lines.append(f"  - Weaknesses: {', '.join(c.weaknesses[:3])}")
            lines.append("")
        
        # Customer Voice
        if r.customer_voice:
            lines.append("## 🗣️ Customer Voice")
            if r.customer_voice.pain_points:
                lines.append("**Pain Points:**")
                for p in r.customer_voice.pain_points[:5]:
                    lines.append(f"- {p}")
            if r.customer_voice.desires:
                lines.append("\n**What Customers Want:**")
                for d in r.customer_voice.desires[:5]:
                    lines.append(f"- {d}")
            lines.append("")
        
        # Timing
        if r.timing:
            lines.append("## 📅 Seasonal Timing")
            for t in r.timing[:3]:
                lines.append(f"- **{t.keyword}**: Peak in {', '.join(t.peak_months[:3])}")
                lines.append(f"  - CPC: ${t.avg_cpc:.2f}, Volume: {t.monthly_volume:,}/mo")
            lines.append("")
        
        # Recommended Hooks
        if r.recommended_hooks:
            lines.append("## 🎯 Recommended Ad Hooks")
            for i, hook in enumerate(r.recommended_hooks[:5], 1):
                lines.append(f"{i}. \"{hook}\"")
            lines.append("")
        
        # Headlines
        if r.headline_suggestions:
            lines.append("## ✍️ Headline Suggestions")
            for h in r.headline_suggestions[:5]:
                lines.append(f"- {h}")
            lines.append("")
        
        # Trust Signals
        if r.trust_signals:
            lines.append("## ✅ Trust Signals to Emphasize")
            for s in r.trust_signals[:5]:
                lines.append(f"- {s}")
            lines.append("")
        
        # Metadata
        lines.append("---")
        lines.append(f"*Agents used: {', '.join(r.agents_used)}*")
        lines.append(f"*Analysis time: {r.total_time_seconds:.1f}s*")
        
        return "\n".join(lines)
