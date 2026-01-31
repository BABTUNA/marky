"""
Subreddit discovery module.
Finds relevant subreddits based on product, audience, and market keywords.
"""

import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass

from .models import ResearchInput, Subreddit
from .reddit_client import RedditClient
from .cache import Cache


@dataclass
class KeywordExpansion:
    """Expanded keywords for research."""
    product_keywords: List[str]
    pain_point_phrases: List[str]
    desire_phrases: List[str]
    comparison_phrases: List[str]
    competitor_terms: List[str]


class SubredditDiscovery:
    """Discovers relevant subreddits for VoC research."""
    
    # Pain point signal words
    PAIN_SIGNALS = [
        "hate", "annoying", "frustrating", "terrible", "worst",
        "problem", "issue", "broken", "doesn't work", "waste",
        "overpriced", "expensive", "rip off", "scam",
        "disappointed", "regret", "avoid", "never again",
    ]
    
    # Desire signal words
    DESIRE_SIGNALS = [
        "wish", "need", "looking for", "want", "best",
        "recommend", "suggestion", "alternative", "help",
        "how to", "tips", "advice", "worth it",
    ]
    
    # Comparison signals
    COMPARISON_SIGNALS = [
        "vs", "versus", "better than", "compared to",
        "instead of", "or", "switch from", "alternative to",
    ]
    
    def __init__(self, client: RedditClient, cache: Cache):
        self.client = client
        self.cache = cache
    
    def expand_keywords(self, research_input: ResearchInput) -> KeywordExpansion:
        """
        Expand input into comprehensive keyword lists.
        
        Takes product/audience/market and generates:
        - Product keywords (variations, synonyms)
        - Pain point phrases
        - Desire phrases
        - Comparison phrases
        - Competitor terms
        """
        product_words = self._tokenize(research_input.product)
        audience_words = self._tokenize(research_input.audience)
        market_words = self._tokenize(research_input.market)
        
        # Combine base keywords
        base_keywords = list(set(
            product_words + audience_words + market_words + research_input.keywords
        ))
        
        # Generate product keyword variations
        product_keywords = []
        for kw in base_keywords:
            product_keywords.append(kw)
            # Add common variations
            if len(kw) > 4:
                product_keywords.append(f"{kw}s")  # Plural
                product_keywords.append(f"{kw} app")
                product_keywords.append(f"{kw} service")
                product_keywords.append(f"{kw} subscription")
        
        # Add the full product name
        product_keywords.append(research_input.product.lower())
        product_keywords = list(set(product_keywords))
        
        # Generate pain point search phrases
        pain_phrases = []
        for kw in base_keywords[:5]:  # Top 5 keywords
            for signal in self.PAIN_SIGNALS[:5]:
                pain_phrases.append(f"{signal} {kw}")
                pain_phrases.append(f"{kw} {signal}")
        
        # Generate desire search phrases
        desire_phrases = []
        for kw in base_keywords[:5]:
            for signal in self.DESIRE_SIGNALS[:5]:
                desire_phrases.append(f"{signal} {kw}")
                desire_phrases.append(f"best {kw}")
        
        # Generate comparison phrases
        comparison_phrases = []
        for kw in base_keywords[:3]:
            for signal in self.COMPARISON_SIGNALS[:3]:
                comparison_phrases.append(f"{kw} {signal}")
        
        return KeywordExpansion(
            product_keywords=product_keywords,
            pain_point_phrases=pain_phrases[:20],
            desire_phrases=desire_phrases[:20],
            comparison_phrases=comparison_phrases[:10],
            competitor_terms=research_input.competitors,
        )
    
    def discover_subreddits(
        self,
        research_input: ResearchInput,
        max_subreddits: int = 20,
        min_subscribers: int = 1000,
    ) -> List[Subreddit]:
        """
        Discover relevant subreddits for the research topic.
        
        Args:
            research_input: The research specification
            max_subreddits: Maximum subreddits to return
            min_subscribers: Minimum subscriber count filter
        
        Returns:
            List of Subreddit objects, scored by relevance
        """
        keywords = self.expand_keywords(research_input)
        
        # Collect candidate subreddits from various searches
        candidates: Dict[str, Dict[str, Any]] = {}
        
        # Search using product keywords
        for kw in keywords.product_keywords[:10]:
            try:
                results = self.client.search_subreddits(kw, limit=10)
                for sub in results:
                    name = sub["name"].lower()
                    if name not in candidates:
                        candidates[name] = sub
                        candidates[name]["keyword_matches"] = set()
                    candidates[name]["keyword_matches"].add(kw)
            except Exception as e:
                print(f"Warning: Search failed for '{kw}': {e}")
                continue
        
        # Also try autocomplete for quick suggestions
        for kw in keywords.product_keywords[:5]:
            try:
                results = self.client.subreddit_autocomplete(kw, limit=5)
                for sub in results:
                    name = sub["name"].lower()
                    if name not in candidates:
                        # Autocomplete has less data, fetch full info
                        candidates[name] = {
                            "name": sub["name"],
                            "subscribers": sub.get("subscribers", 0),
                            "description": "",
                            "keyword_matches": set(),
                        }
                    candidates[name]["keyword_matches"].add(kw)
            except Exception:
                continue
        
        # Score and filter subreddits
        scored_subreddits = []
        
        for name, data in candidates.items():
            subscribers = data.get("subscribers", 0)
            
            # Skip small subreddits
            if subscribers < min_subscribers:
                continue
            
            # Calculate relevance score
            score = self._calculate_relevance_score(
                data,
                keywords,
                research_input,
            )
            
            subreddit = Subreddit(
                name=data["name"],
                display_name=data.get("display_name", f"r/{data['name']}"),
                subscribers=subscribers,
                description=data.get("description", ""),
                relevance_score=score,
            )
            
            scored_subreddits.append(subreddit)
            
            # Cache the subreddit
            self.cache.save_subreddit(
                name=subreddit.name,
                display_name=subreddit.display_name,
                subscribers=subreddit.subscribers,
                description=subreddit.description,
            )
        
        # Sort by relevance score and return top N
        scored_subreddits.sort(key=lambda s: s.relevance_score, reverse=True)
        
        return scored_subreddits[:max_subreddits]
    
    def _calculate_relevance_score(
        self,
        subreddit_data: Dict[str, Any],
        keywords: KeywordExpansion,
        research_input: ResearchInput,
    ) -> float:
        """
        Calculate a relevance score for a subreddit.
        
        Factors:
        - Keyword match count
        - Name/description keyword presence
        - Subscriber count (log scale)
        """
        score = 0.0
        
        name = subreddit_data.get("name", "").lower()
        description = subreddit_data.get("description", "").lower()
        subscribers = subreddit_data.get("subscribers", 0)
        keyword_matches = subreddit_data.get("keyword_matches", set())
        
        # Points for keyword matches in search
        score += len(keyword_matches) * 10
        
        # Points for keywords in name
        for kw in keywords.product_keywords:
            if kw.lower() in name:
                score += 25
        
        # Points for keywords in description
        for kw in keywords.product_keywords:
            if kw.lower() in description:
                score += 5
        
        # Points for product/audience/market in name or description
        product_lower = research_input.product.lower()
        audience_lower = research_input.audience.lower()
        
        if product_lower in name or product_lower in description:
            score += 30
        if audience_lower in name or audience_lower in description:
            score += 20
        
        # Subscriber bonus (log scale to not over-weight huge subs)
        if subscribers > 0:
            import math
            score += math.log10(subscribers) * 2
        
        return score
    
    def _tokenize(self, text: str) -> List[str]:
        """Split text into keyword tokens."""
        # Remove special characters, split on spaces
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = text.split()
        
        # Filter out very short or common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'it'}
        tokens = [t for t in tokens if len(t) > 2 and t not in stop_words]
        
        return tokens
    
    def get_search_queries(self, keywords: KeywordExpansion) -> List[str]:
        """
        Get a list of search queries to use within subreddits.
        
        Combines keywords with signal phrases for targeted searching.
        """
        queries = []
        
        # Product keywords alone
        queries.extend(keywords.product_keywords[:5])
        
        # Pain point queries
        queries.extend(keywords.pain_point_phrases[:10])
        
        # Desire queries
        queries.extend(keywords.desire_phrases[:10])
        
        # Comparison queries
        queries.extend(keywords.comparison_phrases[:5])
        
        # Competitor queries
        for comp in keywords.competitor_terms:
            queries.append(comp)
            queries.append(f"{comp} vs")
            queries.append(f"switch from {comp}")
        
        return list(set(queries))
