"""
Related Questions Intelligence Agent.
Fetches Google "People also ask" questions for content and intent insights.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from .models import RelatedQuestionsAnalysis, QueryQuestions
from .scraper import RelatedQuestionsScraper


class RelatedQuestionsIntelAgent:
    """
    Related Questions Intelligence Agent.
    Uses SerpAPI (Google search) to get "People also ask" questions for
    business type + location. Output is raw questions for content/FAQ and intent.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.scraper = RelatedQuestionsScraper(api_key=api_key)

    def analyze(
        self,
        business_type: str,
        location: str,
        seed_queries: Optional[List[str]] = None,
        max_questions_per_query: int = 15,
    ) -> RelatedQuestionsAnalysis:
        """
        Fetch related questions for the given business type and location.

        Args:
            business_type: Type of business (e.g., "plumber")
            location: Location (e.g., "Providence, RI")
            seed_queries: Optional list of queries; default built from business_type + location
            max_questions_per_query: Max questions to keep per seed query

        Returns:
            RelatedQuestionsAnalysis with query_results and flat question list
        """
        if seed_queries is None:
            seed_queries = [
                f"{business_type} {location}",
                f"best {business_type} {location}",
                f"{business_type} near me",
            ]

        print(f"\n{'='*60}")
        print("Related Questions Intelligence Agent (SerpAPI Google)")
        print(f"{'='*60}")
        print(f"Business: {business_type}, Location: {location}")
        print(f"Queries: {', '.join(seed_queries)}")
        print(f"{'='*60}\n")

        start_time = time.time()
        analysis = RelatedQuestionsAnalysis(
            business_type=business_type,
            location=location,
        )

        for query in seed_queries:
            print(f"  Fetching related questions for: {query}")
            qr = self.scraper.get_related_questions(
                query=query,
                location=location,
                max_questions=max_questions_per_query,
            )
            analysis.query_results.append(qr)
            if qr.questions:
                print(f"    -> {len(qr.questions)} questions")

        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Complete! ({elapsed:.1f}s) — {len(analysis.all_questions())} unique questions")
        print(f"{'='*60}")

        return analysis


def run_related_questions_analysis(
    business_type: str,
    location: str,
    seed_queries: Optional[List[str]] = None,
    save: bool = True,
    output_dir: str = "output",
) -> RelatedQuestionsAnalysis:
    """
    Run related questions analysis and optionally save results.
    """
    agent = RelatedQuestionsIntelAgent()
    analysis = agent.analyze(
        business_type=business_type,
        location=location,
        seed_queries=seed_queries,
    )

    if save:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_path / f"related_questions_intel_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"\nReport saved: {filename}")

    return analysis
