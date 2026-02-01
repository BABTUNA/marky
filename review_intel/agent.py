"""
Review Intelligence Agent.
Analyzes Google Reviews to extract customer voice for ad copy.
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from collections import Counter

from .models import ReviewData, CompetitorReviews, VoiceOfCustomer, ReviewAnalysis
from .scraper import GoogleReviewsScraper


class ReviewIntelAgent:
    """
    Review Intelligence Agent.
    
    Scrapes and analyzes Google Reviews to extract:
    - Customer voice patterns
    - Pain points and desires
    - Ad hooks and headlines
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.scraper = GoogleReviewsScraper(api_key)
    
    def analyze_competitors(
        self,
        competitors: List[Dict[str, Any]],
        business_type: str,
        location: str,
        reviews_per_competitor: int = 20,
    ) -> ReviewAnalysis:
        """
        Analyze reviews for a list of competitors.
        
        Args:
            competitors: List of competitors with 'name', 'place_id', 'rating'
            business_type: Type of business
            location: Location string
            reviews_per_competitor: Max reviews to fetch per competitor
        
        Returns:
            Complete ReviewAnalysis
        """
        print(f"\n{'='*60}")
        print("Review Intelligence Agent")
        print(f"{'='*60}")
        print(f"Business Type: {business_type}")
        print(f"Location: {location}")
        print(f"Competitors: {len(competitors)}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # Step 1: Scrape reviews
        print("Step 1: Scraping Google Reviews...")
        competitor_reviews: List[CompetitorReviews] = []
        total_reviews = 0
        
        for i, comp in enumerate(competitors, 1):
            name = comp.get("name", "Unknown")
            place_id = comp.get("place_id", "")
            
            if not place_id:
                print(f"  [{i}/{len(competitors)}] {name} - No place_id, skipping")
                continue
            
            print(f"  [{i}/{len(competitors)}] {name}...")
            
            reviews = self.scraper.get_reviews(
                place_id=place_id,
                business_name=name,
                max_reviews=reviews_per_competitor,
            )
            
            if reviews.reviews:
                competitor_reviews.append(reviews)
                total_reviews += len(reviews.reviews)
                print(f"    -> {len(reviews.reviews)} reviews ({reviews.overall_rating} stars)")
            else:
                print(f"    -> No reviews found")
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"\n  Total: {total_reviews} reviews from {len(competitor_reviews)} competitors")
        
        # Step 2: Extract voice of customer
        print("\nStep 2: Extracting customer voice patterns...")
        voc = self._extract_voice_of_customer(competitor_reviews, business_type)
        
        print(f"  Pain points: {len(voc.pain_points)}")
        print(f"  Desires: {len(voc.desires)}")
        print(f"  Praise quotes: {len(voc.praise_quotes)}")
        print(f"  Complaint quotes: {len(voc.complaint_quotes)}")
        
        # Step 3: Generate ad hooks
        print("\nStep 3: Generating ad hooks and headlines...")
        ad_hooks = self._generate_hooks(voc, business_type)
        headlines = self._generate_headlines(voc, business_type)
        
        print(f"  Hooks: {len(ad_hooks)}")
        print(f"  Headlines: {len(headlines)}")
        
        # Step 4: Compare top vs worst
        print("\nStep 4: Comparing top vs worst rated...")
        sorted_by_rating = sorted(competitor_reviews, key=lambda x: x.overall_rating, reverse=True)
        
        top_themes = []
        worst_themes = []
        
        if len(sorted_by_rating) >= 2:
            top = sorted_by_rating[:len(sorted_by_rating)//2]
            worst = sorted_by_rating[len(sorted_by_rating)//2:]
            
            top_themes = self._get_common_themes([r for cr in top for r in cr.reviews if r.sentiment == "positive"])
            worst_themes = self._get_common_themes([r for cr in worst for r in cr.reviews if r.sentiment == "negative"])
            
            print(f"  Top competitor themes: {', '.join(top_themes[:3])}")
            print(f"  Worst competitor issues: {', '.join(worst_themes[:3])}")
        
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Complete! ({elapsed:.1f}s)")
        print(f"{'='*60}\n")
        
        return ReviewAnalysis(
            business_type=business_type,
            location=location,
            competitors_analyzed=len(competitor_reviews),
            total_reviews_analyzed=total_reviews,
            competitor_reviews=competitor_reviews,
            voice_of_customer=voc,
            top_competitor_themes=top_themes,
            worst_competitor_themes=worst_themes,
            ad_hooks=ad_hooks,
            headline_suggestions=headlines,
        )
    
    def _extract_voice_of_customer(
        self,
        competitor_reviews: List[CompetitorReviews],
        business_type: str,
    ) -> VoiceOfCustomer:
        """Extract voice of customer patterns from reviews."""
        
        praise_quotes = []
        complaint_quotes = []
        all_pain_points = []
        all_praise_points = []
        all_keywords = []
        
        for cr in competitor_reviews:
            for review in cr.reviews:
                # Collect quotes (short, impactful ones)
                if review.text and len(review.text) > 20:
                    if review.sentiment == "positive" and review.rating == 5:
                        # Get first sentence or first 150 chars
                        quote = self._extract_quote(review.text)
                        if quote:
                            praise_quotes.append(quote)
                    elif review.sentiment == "negative" and review.rating <= 2:
                        quote = self._extract_quote(review.text)
                        if quote:
                            complaint_quotes.append(quote)
                
                all_pain_points.extend(review.pain_points)
                all_praise_points.extend(review.praise_points)
                all_keywords.extend(review.keywords)
        
        # Aggregate pain points with frequency
        pain_counter = Counter(all_pain_points)
        pain_points = [
            {"point": point, "frequency": count, "percentage": count / len(all_pain_points) * 100 if all_pain_points else 0}
            for point, count in pain_counter.most_common(10)
        ]
        
        # Aggregate desires (inverse of pain points from positive reviews)
        desire_counter = Counter(all_praise_points)
        desires = [
            {"desire": desire, "frequency": count, "percentage": count / len(all_praise_points) * 100 if all_praise_points else 0}
            for desire, count in desire_counter.most_common(10)
        ]
        
        # Extract power words
        positive_keywords = [kw[1:] for kw in all_keywords if kw.startswith("+")]
        negative_keywords = [kw[1:] for kw in all_keywords if kw.startswith("-")]
        
        power_words = [word for word, _ in Counter(positive_keywords).most_common(15)]
        
        # Emotional triggers based on common themes
        emotional_triggers = self._get_emotional_triggers(pain_points, desires, business_type)
        
        # Trust phrases
        trust_phrases = self._get_trust_phrases(desires)
        
        # Hook templates
        hook_templates = self._create_hook_templates(pain_points, desires, business_type)
        
        return VoiceOfCustomer(
            praise_quotes=praise_quotes[:20],
            complaint_quotes=complaint_quotes[:20],
            pain_points=pain_points,
            desires=desires,
            objections=[],  # Could be extracted from negative reviews
            power_words=power_words,
            emotional_triggers=emotional_triggers,
            trust_phrases=trust_phrases,
            hook_templates=hook_templates,
        )
    
    def _extract_quote(self, text: str, max_length: int = 150) -> Optional[str]:
        """Extract a clean, usable quote from review text."""
        # Remove common filler
        text = text.strip()
        
        # Get first sentence
        sentences = text.split(".")
        if sentences:
            first = sentences[0].strip()
            if 20 <= len(first) <= max_length:
                return first + "."
        
        # Or truncate intelligently
        if len(text) > max_length:
            truncated = text[:max_length].rsplit(" ", 1)[0]
            return truncated + "..."
        
        return text if len(text) >= 20 else None
    
    def _get_common_themes(self, reviews: List[ReviewData]) -> List[str]:
        """Get common themes from a list of reviews."""
        all_points = []
        for r in reviews:
            all_points.extend(r.praise_points)
            all_points.extend(r.pain_points)
        
        counter = Counter(all_points)
        return [theme for theme, _ in counter.most_common(5)]
    
    def _get_emotional_triggers(
        self,
        pain_points: List[Dict],
        desires: List[Dict],
        business_type: str,
    ) -> List[str]:
        """Generate emotional triggers based on patterns."""
        triggers = []
        
        # Map pain points to emotions
        pain_to_emotion = {
            "unreliable timing": "frustration with waiting",
            "overpricing": "fear of being ripped off",
            "poor quality work": "anxiety about wasted money",
            "poor communication": "feeling ignored",
            "caused damage": "fear of making things worse",
        }
        
        for pp in pain_points[:5]:
            point = pp.get("point", "")
            if point in pain_to_emotion:
                triggers.append(pain_to_emotion[point])
        
        # Map desires to positive emotions
        desire_to_emotion = {
            "punctuality": "relief from stress",
            "fair pricing": "confidence in value",
            "expertise": "trust in quality",
            "friendly service": "feeling respected",
            "honesty": "peace of mind",
        }
        
        for d in desires[:5]:
            desire = d.get("desire", "")
            if desire in desire_to_emotion:
                triggers.append(desire_to_emotion[desire])
        
        return list(set(triggers))
    
    def _get_trust_phrases(self, desires: List[Dict]) -> List[str]:
        """Generate trust phrases from customer desires."""
        phrases = []
        
        desire_to_phrase = {
            "punctuality": "We show up on time, every time",
            "fair pricing": "Honest pricing with no surprises",
            "expertise": "Trusted experts in your area",
            "friendly service": "Friendly, respectful service",
            "honesty": "Straightforward, no-pressure approach",
            "communication": "We keep you informed every step",
            "speed": "Fast response when you need it",
            "cleanliness": "We leave your home cleaner than we found it",
            "availability": "Available when you need us most",
            "recommendation": "Recommended by your neighbors",
        }
        
        for d in desires:
            desire = d.get("desire", "")
            if desire in desire_to_phrase:
                phrases.append(desire_to_phrase[desire])
        
        return phrases[:10]
    
    def _create_hook_templates(
        self,
        pain_points: List[Dict],
        desires: List[Dict],
        business_type: str,
    ) -> List[str]:
        """Create hook templates from customer insights."""
        hooks = []
        
        # Pain point hooks
        pain_templates = {
            "unreliable timing": f"Tired of {business_type}s who don't show up?",
            "overpricing": f"Think all {business_type}s overcharge?",
            "poor quality work": f"Had a {business_type} who didn't fix it right?",
            "poor communication": f"Frustrated by {business_type}s who don't call back?",
        }
        
        for pp in pain_points[:3]:
            point = pp.get("point", "")
            if point in pain_templates:
                hooks.append(pain_templates[point])
        
        # Desire hooks
        desire_templates = {
            "punctuality": f"A {business_type} who actually shows up on time",
            "fair pricing": "Honest pricing. No surprises.",
            "expertise": f"Expert {business_type} your neighbors trust",
            "friendly service": "Friendly service from start to finish",
        }
        
        for d in desires[:3]:
            desire = d.get("desire", "")
            if desire in desire_templates:
                hooks.append(desire_templates[desire])
        
        return hooks
    
    def _generate_hooks(self, voc: VoiceOfCustomer, business_type: str) -> List[str]:
        """Generate ad hooks from voice of customer."""
        hooks = list(voc.hook_templates)
        
        # Add quote-based hooks
        for quote in voc.praise_quotes[:3]:
            if len(quote) < 80:
                hooks.append(f'"{quote}"')
        
        # Add pain-point hooks
        if voc.pain_points:
            top_pain = voc.pain_points[0].get("point", "")
            if top_pain:
                hooks.append(f"Stop dealing with {top_pain}")
        
        return hooks[:10]
    
    def _generate_headlines(self, voc: VoiceOfCustomer, business_type: str) -> List[str]:
        """Generate headline suggestions."""
        headlines = []
        
        # From trust phrases
        for phrase in voc.trust_phrases[:5]:
            headlines.append(phrase)
        
        # From power words
        if voc.power_words:
            pw = voc.power_words[:3]
            headlines.append(f"{pw[0].title()} & {pw[1].title() if len(pw) > 1 else 'Reliable'} Service")
        
        # From desires
        for d in voc.desires[:3]:
            desire = d.get("desire", "")
            if desire:
                headlines.append(f"{desire.title()} Guaranteed")
        
        return headlines[:10]
    
    def save_report(
        self,
        analysis: ReviewAnalysis,
        output_dir: str = "output",
        filename: Optional[str] = None,
    ) -> str:
        """Save analysis to JSON file."""
        Path(output_dir).mkdir(exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"review_intel_{timestamp}.json"
        
        filepath = Path(output_dir) / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"Report saved: {filepath}")
        return str(filepath)
    
    def print_summary(self, analysis: ReviewAnalysis):
        """Print summary of analysis."""
        print("\n" + "="*60)
        print("REVIEW INTELLIGENCE SUMMARY")
        print("="*60)
        
        print(f"\nAnalyzed: {analysis.total_reviews_analyzed} reviews from {analysis.competitors_analyzed} competitors")
        
        if analysis.voice_of_customer:
            voc = analysis.voice_of_customer
            
            print("\n### Top Customer Pain Points")
            for pp in voc.pain_points[:5]:
                print(f"  - {pp['point']} ({pp['frequency']} mentions)")
            
            print("\n### What Customers Want")
            for d in voc.desires[:5]:
                print(f"  + {d['desire']} ({d['frequency']} mentions)")
            
            print("\n### Power Words (from positive reviews)")
            print(f"  {', '.join(voc.power_words[:10])}")
            
            print("\n### Sample Praise Quotes")
            for quote in voc.praise_quotes[:3]:
                print(f'  "{quote}"')
            
            print("\n### Sample Complaint Quotes")
            for quote in voc.complaint_quotes[:3]:
                print(f'  "{quote}"')
        
        print("\n### Generated Ad Hooks")
        for hook in analysis.ad_hooks[:5]:
            print(f"  * {hook}")
        
        print("\n### Headline Suggestions")
        for headline in analysis.headline_suggestions[:5]:
            print(f"  * {headline}")
        
        print("\n" + "="*60)


def run_review_analysis(
    competitors: List[Dict[str, Any]],
    business_type: str,
    location: str,
    reviews_per_competitor: int = 20,
    save: bool = True,
    output_dir: str = "output",
) -> ReviewAnalysis:
    """
    Convenience function to run review analysis.
    
    Args:
        competitors: List with 'name', 'place_id', 'rating' keys
        business_type: Type of business
        location: Location string
        reviews_per_competitor: Reviews to fetch per competitor
        save: Whether to save report
        output_dir: Output directory
    
    Returns:
        ReviewAnalysis
    """
    agent = ReviewIntelAgent()
    
    analysis = agent.analyze_competitors(
        competitors=competitors,
        business_type=business_type,
        location=location,
        reviews_per_competitor=reviews_per_competitor,
    )
    
    agent.print_summary(analysis)
    
    if save:
        agent.save_report(analysis, output_dir)
    
    return analysis
