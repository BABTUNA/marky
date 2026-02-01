"""
Related Questions (People also ask) scraper using SerpAPI.
Fetches Google SERP "related_questions" from engine=google.
"""

import os
import requests
from typing import List, Optional, Dict, Any
from .models import RelatedQuestion, QueryQuestions


REQUEST_TIMEOUT = 45


class RelatedQuestionsScraper:
    """
    Fetches Google "People also ask" / related questions via SerpAPI.
    Uses engine=google with q=query; response includes related_questions.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not set. Get one at https://serpapi.com")
        self.base_url = "https://serpapi.com/search"

    def get_related_questions(
        self,
        query: str,
        location: Optional[str] = None,
        gl: str = "us",
        hl: str = "en",
        max_questions: int = 20,
    ) -> QueryQuestions:
        """
        Fetch related questions (People also ask) for a search query.

        Args:
            query: Search query (e.g., "plumber Providence RI")
            location: Optional location string for local results
            gl: Country code (us, uk, etc.)
            hl: Language code (en, etc.)
            max_questions: Maximum questions to return per query

        Returns:
            QueryQuestions with question list
        """
        result = QueryQuestions(query=query, questions=[])

        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "gl": gl,
                "hl": hl,
            }
            if location:
                params["location"] = location

            response = requests.get(
                self.base_url, params=params, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("related_questions", [])[:max_questions]:
                q = RelatedQuestion(
                    question=item.get("question", "").strip(),
                    snippet=item.get("snippet") or item.get("answer"),
                    link=item.get("link"),
                    title=item.get("title"),
                )
                if q.question:
                    result.questions.append(q)

        except requests.RequestException as e:
            print(f"    SerpAPI request error: {e}")
        except Exception as e:
            print(f"    Error fetching related questions: {e}")

        return result
