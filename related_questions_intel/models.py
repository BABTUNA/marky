"""
Data models for Related Questions Intelligence Agent.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class RelatedQuestion:
    """A single "People also ask" question from Google SERP."""
    question: str
    snippet: Optional[str] = None
    link: Optional[str] = None
    title: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "snippet": self.snippet,
            "link": self.link,
            "title": self.title,
        }


@dataclass
class QueryQuestions:
    """Related questions for one seed query."""
    query: str
    questions: List[RelatedQuestion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "questions": [q.to_dict() for q in self.questions],
        }


@dataclass
class RelatedQuestionsAnalysis:
    """Complete related questions analysis (People also ask)."""
    business_type: str
    location: str
    query_results: List[QueryQuestions] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "business_type": self.business_type,
            "location": self.location,
            "query_results": [qr.to_dict() for qr in self.query_results],
        }

    def all_questions(self) -> List[str]:
        """Flat list of unique question strings across all queries."""
        seen = set()
        out = []
        for qr in self.query_results:
            for q in qr.questions:
                if q.question and q.question not in seen:
                    seen.add(q.question)
                    out.append(q.question)
        return out
