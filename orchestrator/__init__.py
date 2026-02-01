"""
Marky - Ad Research Orchestrator Agent.

A single-entry-point uAgent that orchestrates multiple intelligence agents
to generate comprehensive ad research and differentiation strategies.

Uses uAgents chat protocol for Fetch.ai/ASI compatibility.
"""

from .agent import marky_agent, run_marky
from .workflow import MarkyWorkflow, AdResearchResult
from .models import AdResearchRequest, AdResearchResponse

__all__ = [
    "marky_agent",
    "run_marky",
    "MarkyWorkflow",
    "AdResearchRequest",
    "AdResearchResponse",
    "AdResearchResult",
]
