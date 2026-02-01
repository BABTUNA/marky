"""
Local Competitor Intelligence Agent

Discovers local competitors, scrapes their websites,
and generates advertising differentiation insights.
"""

__version__ = "1.0.0"

from .agent import LocalIntelAgent, run_analysis
from .models import IntelligenceReport, Competitor, MarketAnalysis

__all__ = [
    "LocalIntelAgent",
    "run_analysis",
    "IntelligenceReport",
    "Competitor",
    "MarketAnalysis",
]
