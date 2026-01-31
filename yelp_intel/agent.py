"""
Yelp Intelligence Agent.
Analyzes Yelp reviews to extract customer insights for advertising.
"""

import json
import os
import re
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from collections import Counter

from .models import (
    YelpBusiness,
    YelpReview,
    CustomerInsights,
    AdSuggestions,
    YelpAnalysis,
)
from .scraper import YelpScraper


class YelpIntelAgent:
    """
    Yelp Intelligence Agent.
    
    Scrapes Yelp reviews and extracts:
    - Customer pain points (from negative reviews)
    - What customers love (from positive reviews)
    - Common themes and language
    - Ad hooks and suggestions
    """
    
    # Pain point keywords
    PAIN_KEYWORDS = [
        "terrible", "awful", "horrible", "worst", "never", "don't", "didn't",
        "overpriced", "expensive", "rip off", "ripoff", "scam", "waste",
        "rude", "unprofessional", "late", "no-show", "noshow", "waited",
        "dirty", "filthy", "disgusting", "gross", "cold", "slow",
        "wrong", "mistake", "messed up", "broke", "damaged", "ruined",
        "disappointed", "disappointing", "frustrating", "annoying",
        "avoid", "stay away", "don't go", "wouldn't recommend",
        "overcharged", "hidden fees", "extra charge",
    ]
    
    # Praise keywords
    PRAISE_KEYWORDS = [
        "amazing", "excellent", "fantastic", "wonderful", "best", "love",
        "friendly", "professional", "helpful", "knowledgeable", "expert",
        "fast", "quick", "on time", "punctual", "prompt", "efficient",
        "clean", "spotless", "tidy", "organized",
        "fair", "reasonable", "affordable", "great value", "worth",
        "recommend", "highly recommend", "will be back", "come back",
        "exceeded", "above and beyond", "impressed",
        "honest", "trustworthy", "reliable", "dependable",
    ]
    
    # Theme categories
    THEME_PATTERNS = {
        "pricing": ["price", "cost", "expensive", "cheap", "affordable", "value", "worth", "charge", "fee", "quote"],
        "quality": ["quality", "work", "job", "result", "excellent", "poor", "good", "bad", "great"],
        "timeliness": ["time", "late", "early", "on time", "punctual", "wait", "quick", "fast", "slow", "schedule"],
        "communication": ["call", "called", "respond", "response", "answer", "contact", "reach", "phone", "text", "email"],
        "professionalism": ["professional", "rude", "friendly", "polite", "courteous", "respectful", "attitude"],
        "cleanliness": ["clean", "dirty", "mess", "tidy", "neat", "spotless"],
        "expertise": ["know", "expert", "experienced", "skilled", "trained", "knowledge", "explain"],
        "reliability": ["reliable", "dependable", "trust", "honest", "show up", "showed up"],
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.scraper = YelpScraper(api_key)
    
    def analyze_market(
        self,
        business_type: str,
        location: str,
        max_businesses: int = 5,
        reviews_per_business: int = 20,
    ) -> YelpAnalysis:
        """
        Analyze Yelp reviews for a market.
        
        Args:
            business_type: Type of business (e.g., "plumber")
            location: Location (e.g., "Providence, RI")
            max_businesses: Max businesses to analyze
            reviews_per_business: Reviews to fetch per business
        
        Returns:
            Complete YelpAnalysis
        """
        print(f"\n{'='*60}")
        print("Yelp Intelligence Agent")
        print(f"{'='*60}")
        print(f"Business Type: {business_type}")
        print(f"Location: {location}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # Step 1: Find businesses
        print("Step 1: Finding businesses on Yelp...")
        businesses = self.scraper.search_businesses(
            query=business_type,
            location=location,
            max_results=max_businesses,
        )
        print(f"  Found {len(businesses)} businesses\n")
        
        if not businesses:
            print("  No businesses found. Try a different search term or location.")
            return YelpAnalysis(
                business_type=business_type,
                location=location,
            )
        
        # Step 2: Collect reviews
        print("Step 2: Collecting reviews...")
        all_reviews: List[YelpReview] = []
        rating_counts: Dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for i, business in enumerate(businesses):
            print(f"  [{i+1}/{len(businesses)}] {business.name} ({business.rating} stars, {business.review_count} reviews)")
            
            if not business.place_id:
                print(f"    Skipping - no place ID")
                continue
            
            # Get mix of positive and negative reviews
            positive = self.scraper.get_positive_reviews(
                business.place_id,
                max_reviews=reviews_per_business // 2,
            )
            negative = self.scraper.get_negative_reviews(
                business.place_id,
                max_reviews=reviews_per_business // 2,
            )
            
            reviews = positive + negative
            all_reviews.extend(reviews)
            
            # Count ratings
            for review in reviews:
                if 1 <= review.rating <= 5:
                    rating_counts[review.rating] += 1
            
            print(f"    Got {len(positive)} positive, {len(negative)} negative reviews")
            time.sleep(0.3)  # Rate limiting
        
        print(f"\n  Total reviews collected: {len(all_reviews)}")
        
        # Step 3: Analyze reviews
        print("\nStep 3: Analyzing customer insights...")
        insights = self._analyze_reviews(all_reviews)
        print(f"  Pain points: {len(insights.pain_points)}")
        print(f"  Praise points: {len(insights.praise_points)}")
        print(f"  Themes: {len(insights.themes)}")
        print(f"  Customer phrases: {len(insights.customer_phrases)}")
        
        # Step 4: Generate ad suggestions
        print("\nStep 4: Generating ad suggestions...")
        ad_suggestions = self._generate_suggestions(insights, business_type)
        print(f"  Hooks: {len(ad_suggestions.hooks)}")
        print(f"  Headlines: {len(ad_suggestions.headlines)}")
        
        # Calculate average rating
        total_ratings = sum(rating_counts.values())
        avg_rating = 0.0
        if total_ratings > 0:
            avg_rating = sum(r * c for r, c in rating_counts.items()) / total_ratings
        
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Complete! ({elapsed:.1f}s)")
        print(f"{'='*60}")
        
        return YelpAnalysis(
            business_type=business_type,
            location=location,
            businesses=businesses,
            total_reviews_analyzed=len(all_reviews),
            insights=insights,
            ad_suggestions=ad_suggestions,
            rating_distribution=rating_counts,
            avg_rating=round(avg_rating, 2),
        )
    
    def _analyze_reviews(self, reviews: List[YelpReview]) -> CustomerInsights:
        """Analyze reviews to extract insights."""
        insights = CustomerInsights()
        
        pain_counter: Counter = Counter()
        praise_counter: Counter = Counter()
        theme_counter: Counter = Counter()
        phrase_counter: Counter = Counter()
        
        for review in reviews:
            text = review.text.lower()
            
            # Extract pain points from negative reviews
            if review.rating <= 2:
                for keyword in self.PAIN_KEYWORDS:
                    if keyword in text:
                        pain_counter[keyword] += 1
                
                # Add as quote if it's a good example
                if len(review.text) > 50 and len(review.text) < 500:
                    insights.pain_point_quotes.append(review.text[:200])
            
            # Extract praise from positive reviews
            if review.rating >= 4:
                for keyword in self.PRAISE_KEYWORDS:
                    if keyword in text:
                        praise_counter[keyword] += 1
                
                # Add as quote
                if len(review.text) > 50 and len(review.text) < 500:
                    insights.praise_quotes.append(review.text[:200])
            
            # Extract themes
            for theme, patterns in self.THEME_PATTERNS.items():
                for pattern in patterns:
                    if pattern in text:
                        theme_counter[theme] += 1
                        break
            
            # Extract customer phrases (short meaningful phrases)
            phrases = self._extract_phrases(review.text)
            for phrase in phrases:
                phrase_counter[phrase] += 1
            
            # Extract questions
            questions = self._extract_questions(review.text)
            insights.questions.extend(questions)
            
            # Extract price mentions
            if any(word in text for word in ["price", "cost", "charge", "paid", "expensive", "cheap", "afford"]):
                # Get the sentence containing price mention
                sentences = review.text.split(".")
                for sent in sentences:
                    if any(word in sent.lower() for word in ["price", "cost", "charge", "$"]):
                        if 20 < len(sent) < 150:
                            insights.price_mentions.append(sent.strip())
        
        # Convert counters to lists
        insights.pain_points = [item for item, _ in pain_counter.most_common(15)]
        insights.praise_points = [item for item, _ in praise_counter.most_common(15)]
        insights.themes = [item for item, _ in theme_counter.most_common(10)]
        insights.customer_phrases = [item for item, _ in phrase_counter.most_common(20)]
        
        # Dedupe
        insights.questions = list(set(insights.questions))[:10]
        insights.price_mentions = list(set(insights.price_mentions))[:10]
        
        return insights
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract meaningful short phrases from review text."""
        phrases = []
        
        # Common valuable phrases
        patterns = [
            r"(highly recommend\w*)",
            r"(would (?:definitely )?(?:use|recommend|come back))",
            r"(saved (?:me|us) \w+)",
            r"(best .{5,30} (?:ever|in town|around))",
            r"(worst .{5,30} (?:ever|experience))",
            r"(never (?:going|coming|using) (?:back|again))",
            r"(will (?:definitely )?(?:be back|return|use again))",
            r"((?:so|very|really|extremely) (?:professional|friendly|helpful|rude|slow|fast))",
            r"(on time|ahead of schedule|running late)",
            r"(fair price|great value|overpriced|rip ?off)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            phrases.extend(matches)
        
        return phrases
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from review text."""
        questions = []
        
        # Find sentences ending with ?
        sentences = text.split("?")
        for i, sent in enumerate(sentences[:-1]):  # All but last (after last ?)
            # Get the question part
            lines = sent.split(".")
            if lines:
                q = lines[-1].strip() + "?"
                if 10 < len(q) < 150:
                    questions.append(q)
        
        return questions
    
    def _generate_suggestions(
        self,
        insights: CustomerInsights,
        business_type: str,
    ) -> AdSuggestions:
        """Generate ad suggestions from insights."""
        suggestions = AdSuggestions()
        
        # Generate pain point hooks
        pain_hooks = {
            "late": f"Tired of {business_type}s who never show up on time?",
            "expensive": f"Looking for a {business_type} that won't break the bank?",
            "overpriced": f"Stop overpaying for {business_type} services",
            "rude": f"Want a {business_type} who treats you with respect?",
            "unprofessional": f"Tired of unprofessional {business_type}s?",
            "waited": f"No more waiting around - we show up when we say we will",
            "slow": f"Need a {business_type} who gets the job done fast?",
            "mistake": f"Looking for a {business_type} who gets it right the first time?",
            "hidden fees": f"Transparent pricing. No hidden fees. No surprises.",
            "no-show": f"We always show up - on time, every time",
        }
        
        for pain in insights.pain_points[:5]:
            if pain in pain_hooks:
                suggestions.pain_point_hooks.append(pain_hooks[pain])
        
        # Generate praise-based trust signals
        praise_signals = {
            "professional": "Licensed & Professional Service",
            "friendly": "Friendly, Courteous Team",
            "fast": "Fast, Efficient Service",
            "quick": "Quick Response Time",
            "on time": "Always On Time - Guaranteed",
            "punctual": "Punctual & Reliable",
            "clean": "Clean, Tidy Work",
            "honest": "Honest, Upfront Pricing",
            "recommend": "Highly Recommended by Customers",
            "expert": "Expert Technicians",
            "reliable": "Reliable Service You Can Trust",
        }
        
        for praise in insights.praise_points[:5]:
            if praise in praise_signals:
                suggestions.trust_signals.append(praise_signals[praise])
        
        # Generate hooks based on themes
        if "pricing" in insights.themes:
            suggestions.hooks.append("Fair, transparent pricing - no surprises")
        if "timeliness" in insights.themes:
            suggestions.hooks.append("On time, every time - we respect your schedule")
        if "quality" in insights.themes:
            suggestions.hooks.append("Quality work that lasts")
        if "communication" in insights.themes:
            suggestions.hooks.append("We answer your calls and keep you informed")
        if "professionalism" in insights.themes:
            suggestions.hooks.append("Professional service from start to finish")
        
        # Generate headlines
        suggestions.headlines = [
            f"Top-Rated {business_type.title()} in Your Area",
            f"Your Trusted Local {business_type.title()}",
            f"Professional {business_type.title()} Services",
            f"Fast, Reliable {business_type.title()} Service",
            f"Quality {business_type.title()} Work at Fair Prices",
        ]
        
        # Add differentiators based on what's missing
        if "reliable" not in insights.praise_points:
            suggestions.differentiators.append("Emphasize reliability - customers want dependable service")
        if "on time" not in insights.praise_points:
            suggestions.differentiators.append("Highlight punctuality - a common pain point")
        if "honest" not in insights.praise_points:
            suggestions.differentiators.append("Stress honesty and transparency in pricing")
        if "fast" not in insights.praise_points:
            suggestions.differentiators.append("Promote quick response and service times")
        
        return suggestions


def run_yelp_analysis(
    business_type: str,
    location: str,
    max_businesses: int = 5,
    reviews_per_business: int = 20,
    save: bool = True,
    output_dir: str = "output",
) -> YelpAnalysis:
    """
    Run Yelp analysis and optionally save results.
    
    Args:
        business_type: Type of business to analyze
        location: Location to search
        max_businesses: Number of businesses to analyze
        reviews_per_business: Reviews per business
        save: Whether to save results
        output_dir: Output directory
    
    Returns:
        YelpAnalysis results
    """
    agent = YelpIntelAgent()
    analysis = agent.analyze_market(
        business_type=business_type,
        location=location,
        max_businesses=max_businesses,
        reviews_per_business=reviews_per_business,
    )
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("YELP INTELLIGENCE SUMMARY")
    print(f"{'='*60}\n")
    
    print(f"Analyzed: {len(analysis.businesses)} businesses, {analysis.total_reviews_analyzed} reviews")
    print(f"Average Rating: {analysis.avg_rating} stars\n")
    
    print("### Rating Distribution")
    for rating in [5, 4, 3, 2, 1]:
        count = analysis.rating_distribution.get(rating, 0)
        bar = "*" * min(count, 20)
        print(f"  {rating} stars: {bar} ({count})")
    
    print("\n### Customer Pain Points (from negative reviews)")
    for pain in analysis.insights.pain_points[:8]:
        print(f"  - {pain}")
    
    print("\n### What Customers Love (from positive reviews)")
    for praise in analysis.insights.praise_points[:8]:
        print(f"  - {praise}")
    
    print("\n### Key Themes")
    for theme in analysis.insights.themes[:6]:
        print(f"  - {theme}")
    
    print("\n### Customer Quotes (Pain Points)")
    for quote in analysis.insights.pain_point_quotes[:3]:
        print(f'  "{quote[:100]}..."')
    
    print("\n### Customer Quotes (Praise)")
    for quote in analysis.insights.praise_quotes[:3]:
        print(f'  "{quote[:100]}..."')
    
    print("\n### Ad Hook Suggestions")
    for hook in analysis.ad_suggestions.pain_point_hooks[:5]:
        print(f"  * {hook}")
    for hook in analysis.ad_suggestions.hooks[:3]:
        print(f"  * {hook}")
    
    print("\n### Trust Signals to Emphasize")
    for signal in analysis.ad_suggestions.trust_signals[:5]:
        print(f"  - {signal}")
    
    print("\n### Differentiators (Opportunities)")
    for diff in analysis.ad_suggestions.differentiators[:4]:
        print(f"  -> {diff}")
    
    # Save results
    if save:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_path / f"yelp_intel_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"Report saved: {filename}")
    
    return analysis
