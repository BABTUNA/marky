"""
Voice of Customer extraction and analysis.
Filters, classifies, and clusters Reddit comments into VoC insights.
"""

import re
import hashlib
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field

from .models import (
    Comment, Post, VoCSignal, SignalType, Theme,
    ResearchInput,
)


@dataclass
class VoCFilters:
    """Configuration for VoC signal detection."""
    
    # Pain point indicators
    pain_keywords: List[str] = field(default_factory=lambda: [
        "hate", "hated", "hating",
        "annoying", "annoyed", "frustrating", "frustrated",
        "terrible", "horrible", "awful", "worst",
        "problem", "problems", "issue", "issues",
        "broken", "broke", "breaks",
        "doesn't work", "don't work", "didn't work", "not working",
        "waste", "wasted", "useless",
        "overpriced", "expensive", "too much", "rip off", "ripoff",
        "disappointed", "disappointing", "letdown",
        "regret", "regretted", "mistake",
        "avoid", "stay away", "never again", "don't buy",
        "sucks", "sucked", "garbage", "trash",
        "unreliable", "inconsistent", "poor quality",
    ])
    
    # Desire/want indicators
    desire_keywords: List[str] = field(default_factory=lambda: [
        "wish", "wished", "wishing",
        "need", "needed", "needs",
        "want", "wanted", "wanting",
        "looking for", "searching for", "trying to find",
        "best", "better", "ideal", "perfect",
        "recommend", "recommended", "recommendation", "suggestions",
        "should i", "should I", "worth it", "worth buying",
        "help me", "any tips", "any advice",
        "how do i", "how do I", "how to",
        "love", "loved", "amazing", "awesome", "great",
    ])
    
    # Objection indicators
    objection_keywords: List[str] = field(default_factory=lambda: [
        "but", "however", "although", "though",
        "concern", "concerned", "worried", "worry",
        "not sure", "unsure", "hesitant", "skeptical",
        "too expensive", "can't afford", "budget",
        "don't trust", "scam", "legit", "legitimate",
        "does it actually", "does it really",
        "heard bad things", "reviews say",
        "what about", "what if",
    ])
    
    # Comparison indicators
    comparison_keywords: List[str] = field(default_factory=lambda: [
        "vs", "versus", "vs.",
        "better than", "worse than",
        "compared to", "comparison",
        "instead of", "rather than",
        "switch from", "switched from", "switching",
        "alternative", "alternatives",
        "or", "which one", "which is better",
    ])
    
    # Purchase intent indicators
    purchase_keywords: List[str] = field(default_factory=lambda: [
        "buy", "buying", "bought", "purchase", "purchased",
        "order", "ordered", "ordering",
        "subscribe", "subscribed", "subscription",
        "sign up", "signed up", "signing up",
        "try", "tried", "trying",
        "get", "getting", "got",
        "worth", "worth it", "value",
        "deal", "discount", "sale", "coupon",
    ])
    
    min_comment_length: int = 20
    max_comment_length: int = 5000


class VoCExtractor:
    """Extracts VoC signals from Reddit comments."""
    
    def __init__(self, filters: Optional[VoCFilters] = None):
        self.filters = filters or VoCFilters()
        self._seen_hashes: Set[str] = set()
    
    def extract_signals(
        self,
        comments: List[Comment],
        posts: Optional[List[Post]] = None,
    ) -> List[VoCSignal]:
        """
        Extract VoC signals from comments and post titles/text.
        
        Args:
            comments: List of comments to analyze
            posts: Optional list of posts (titles are analyzed too)
        
        Returns:
            List of VoCSignal objects
        """
        signals: List[VoCSignal] = []
        
        # Process comments
        for comment in comments:
            comment_signals = self._extract_from_text(
                text=comment.body,
                source_id=comment.id,
                source_subreddit=comment.subreddit,
            )
            signals.extend(comment_signals)
        
        # Process post titles and selftext
        if posts:
            for post in posts:
                # Analyze title
                title_signals = self._extract_from_text(
                    text=post.title,
                    source_id=f"post_{post.id}_title",
                    source_subreddit=post.subreddit,
                )
                signals.extend(title_signals)
                
                # Analyze selftext if present
                if post.selftext and len(post.selftext) > self.filters.min_comment_length:
                    selftext_signals = self._extract_from_text(
                        text=post.selftext,
                        source_id=f"post_{post.id}_body",
                        source_subreddit=post.subreddit,
                    )
                    signals.extend(selftext_signals)
        
        return signals
    
    def _extract_from_text(
        self,
        text: str,
        source_id: str,
        source_subreddit: str,
    ) -> List[VoCSignal]:
        """Extract signals from a single piece of text."""
        signals: List[VoCSignal] = []
        
        # Skip if too short or too long
        if len(text) < self.filters.min_comment_length:
            return signals
        if len(text) > self.filters.max_comment_length:
            text = text[:self.filters.max_comment_length]
        
        # Deduplicate by text hash
        text_hash = self._hash_text(text)
        if text_hash in self._seen_hashes:
            return signals
        self._seen_hashes.add(text_hash)
        
        text_lower = text.lower()
        
        # Check for each signal type
        signal_checks = [
            (SignalType.PAIN_POINT, self.filters.pain_keywords),
            (SignalType.DESIRE, self.filters.desire_keywords),
            (SignalType.OBJECTION, self.filters.objection_keywords),
            (SignalType.COMPARISON, self.filters.comparison_keywords),
            (SignalType.PURCHASE_INTENT, self.filters.purchase_keywords),
        ]
        
        for signal_type, keywords in signal_checks:
            matched_keywords = []
            for kw in keywords:
                if kw.lower() in text_lower:
                    matched_keywords.append(kw)
            
            if matched_keywords:
                confidence = min(1.0, len(matched_keywords) * 0.2)
                
                signal = VoCSignal(
                    text=text,
                    signal_type=signal_type,
                    source_comment_id=source_id,
                    source_subreddit=source_subreddit,
                    confidence=confidence,
                    keywords_matched=matched_keywords,
                )
                signals.append(signal)
        
        return signals
    
    def _hash_text(self, text: str) -> str:
        """Create a normalized hash of text for deduplication."""
        # Normalize: lowercase, remove extra whitespace
        normalized = ' '.join(text.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def filter_high_quality(
        self,
        signals: List[VoCSignal],
        min_confidence: float = 0.2,
    ) -> List[VoCSignal]:
        """Filter to high-quality signals."""
        return [s for s in signals if s.confidence >= min_confidence]
    
    def group_by_type(
        self,
        signals: List[VoCSignal],
    ) -> Dict[SignalType, List[VoCSignal]]:
        """Group signals by their type."""
        grouped: Dict[SignalType, List[VoCSignal]] = defaultdict(list)
        for signal in signals:
            grouped[signal.signal_type].append(signal)
        return dict(grouped)


class ThemeClusterer:
    """Clusters VoC signals into themes."""
    
    # Predefined theme categories with associated keywords
    THEME_PATTERNS = {
        "price": ["price", "cost", "expensive", "cheap", "afford", "budget", "money", "pay", "value", "worth"],
        "quality": ["quality", "good", "bad", "great", "poor", "excellent", "terrible", "build", "durable"],
        "convenience": ["easy", "hard", "convenient", "hassle", "simple", "complicated", "quick", "fast", "slow"],
        "reliability": ["reliable", "unreliable", "consistent", "inconsistent", "always", "never", "sometimes", "breaks"],
        "customer_service": ["support", "service", "help", "response", "contact", "email", "phone", "chat", "refund"],
        "shipping": ["shipping", "delivery", "arrive", "arrived", "late", "fast", "slow", "package", "tracking"],
        "taste_flavor": ["taste", "flavor", "delicious", "gross", "bland", "sweet", "bitter", "fresh", "stale"],
        "health": ["health", "healthy", "organic", "natural", "ingredients", "nutrition", "diet", "calories"],
        "subscription": ["subscription", "subscribe", "cancel", "recurring", "monthly", "annual", "renew"],
        "comparison": ["better", "worse", "vs", "versus", "compared", "alternative", "switch", "instead"],
        "trust": ["trust", "scam", "legit", "legitimate", "honest", "fake", "real", "authentic"],
        "experience": ["experience", "tried", "using", "used", "love", "hate", "amazing", "terrible"],
    }
    
    def __init__(self, max_themes: int = 12):
        self.max_themes = max_themes
    
    def cluster_signals(
        self,
        signals: List[VoCSignal],
        research_input: Optional[ResearchInput] = None,
    ) -> List[Theme]:
        """
        Cluster signals into themes.
        
        Uses keyword-based clustering (simple but effective).
        For better results, integrate embeddings + k-means.
        """
        # Count theme occurrences
        theme_signals: Dict[str, List[VoCSignal]] = defaultdict(list)
        theme_quotes: Dict[str, List[str]] = defaultdict(list)
        theme_objections: Dict[str, List[str]] = defaultdict(list)
        theme_desires: Dict[str, List[str]] = defaultdict(list)
        
        for signal in signals:
            text_lower = signal.text.lower()
            
            # Find matching themes
            matched_themes = []
            for theme_name, theme_keywords in self.THEME_PATTERNS.items():
                for kw in theme_keywords:
                    if kw in text_lower:
                        matched_themes.append(theme_name)
                        break
            
            # If no theme matched, try to categorize as "general"
            if not matched_themes:
                matched_themes = ["general"]
            
            for theme_name in matched_themes:
                theme_signals[theme_name].append(signal)
                
                # Extract a short quote (first 200 chars)
                quote = self._extract_quote(signal.text)
                if quote:
                    theme_quotes[theme_name].append(quote)
                
                # Categorize by signal type
                if signal.signal_type == SignalType.OBJECTION:
                    theme_objections[theme_name].append(quote)
                elif signal.signal_type == SignalType.DESIRE:
                    theme_desires[theme_name].append(quote)
        
        # Build Theme objects
        total_signals = len(signals)
        themes: List[Theme] = []
        
        for theme_name, theme_signal_list in theme_signals.items():
            weight = len(theme_signal_list) / max(1, total_signals)
            
            # Get unique quotes (top by frequency/relevance)
            quotes = list(set(theme_quotes.get(theme_name, [])))[:5]
            objections = list(set(theme_objections.get(theme_name, [])))[:3]
            desires = list(set(theme_desires.get(theme_name, [])))[:3]
            
            # Extract keywords from signals
            keywords = self._extract_theme_keywords(theme_signal_list)
            
            theme = Theme(
                name=theme_name.replace("_", " ").title(),
                weight=weight,
                example_quotes=quotes,
                common_objections=objections,
                desired_outcomes=desires,
                keywords=keywords,
            )
            themes.append(theme)
        
        # Sort by weight and limit
        themes.sort(key=lambda t: t.weight, reverse=True)
        return themes[:self.max_themes]
    
    def _extract_quote(self, text: str, max_length: int = 200) -> str:
        """Extract a usable quote from text."""
        # Clean up the text
        text = text.strip()
        
        # Remove markdown formatting
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
        text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)  # Bold/italic
        text = re.sub(r'~~([^~]+)~~', r'\1', text)  # Strikethrough
        
        # Truncate intelligently
        if len(text) <= max_length:
            return text
        
        # Try to cut at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        last_question = truncated.rfind('?')
        last_exclaim = truncated.rfind('!')
        
        cut_point = max(last_period, last_question, last_exclaim)
        if cut_point > max_length // 2:
            return text[:cut_point + 1]
        
        # Cut at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length // 2:
            return text[:last_space] + "..."
        
        return truncated + "..."
    
    def _extract_theme_keywords(
        self,
        signals: List[VoCSignal],
        top_n: int = 10,
    ) -> List[str]:
        """Extract the most common keywords from signals."""
        keyword_counts: Dict[str, int] = defaultdict(int)
        
        for signal in signals:
            for kw in signal.keywords_matched:
                keyword_counts[kw.lower()] += 1
        
        # Sort by count and return top N
        sorted_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        
        return [kw for kw, _ in sorted_keywords[:top_n]]


class VoCAnalyzer:
    """Main analyzer that combines extraction and clustering."""
    
    def __init__(
        self,
        filters: Optional[VoCFilters] = None,
        max_themes: int = 12,
    ):
        self.extractor = VoCExtractor(filters)
        self.clusterer = ThemeClusterer(max_themes)
    
    def analyze(
        self,
        comments: List[Comment],
        posts: Optional[List[Post]] = None,
        research_input: Optional[ResearchInput] = None,
    ) -> Tuple[List[VoCSignal], List[Theme]]:
        """
        Full VoC analysis pipeline.
        
        Returns:
            Tuple of (signals, themes)
        """
        # Extract signals
        signals = self.extractor.extract_signals(comments, posts)
        
        # Filter to high quality
        signals = self.extractor.filter_high_quality(signals, min_confidence=0.2)
        
        # Cluster into themes
        themes = self.clusterer.cluster_signals(signals, research_input)
        
        return signals, themes
    
    def get_language_bank(
        self,
        signals: List[VoCSignal],
        max_phrases: int = 50,
    ) -> List[str]:
        """
        Extract reusable phrases and language from signals.
        
        These are short, punchy phrases good for ad copy.
        """
        phrases: List[str] = []
        
        for signal in signals:
            # Extract phrases between 3-10 words
            text = signal.text
            sentences = re.split(r'[.!?]', text)
            
            for sentence in sentences:
                words = sentence.strip().split()
                if 3 <= len(words) <= 12:
                    phrase = ' '.join(words)
                    # Clean up
                    phrase = re.sub(r'\s+', ' ', phrase).strip()
                    if phrase and len(phrase) > 10:
                        phrases.append(phrase)
        
        # Deduplicate and limit
        unique_phrases = list(set(phrases))
        return unique_phrases[:max_phrases]
