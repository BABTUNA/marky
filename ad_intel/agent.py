"""
Ad Intelligence Agent.
Analyzes competitor Facebook ads to extract strategies and patterns.
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from collections import Counter

from .models import AdData, CompetitorAds, AdPatterns, AdAnalysis
from .scraper import FacebookAdsScraper


class AdIntelAgent:
    """
    Ad Intelligence Agent.
    
    Scrapes and analyzes competitor Facebook ads to extract:
    - Hook patterns
    - CTA strategies
    - Creative formats
    - Messaging themes
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.scraper = FacebookAdsScraper(api_key)
    
    def analyze_market(
        self,
        business_type: str,
        location: str,
        max_ads: int = 50,
        additional_terms: Optional[List[str]] = None,
    ) -> AdAnalysis:
        """
        Analyze competitor ads in a market.
        
        Args:
            business_type: Type of business (e.g., "plumber")
            location: Location (e.g., "Providence RI")
            max_ads: Maximum ads to analyze
            additional_terms: Extra search terms
        
        Returns:
            Complete AdAnalysis
        """
        print(f"\n{'='*60}")
        print("Ad Intelligence Agent")
        print(f"{'='*60}")
        print(f"Business Type: {business_type}")
        print(f"Location: {location}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # Build search queries
        search_terms = [
            f"{business_type} {location}",
            f"{business_type} near me",
        ]
        if additional_terms:
            search_terms.extend(additional_terms)
        
        # Step 1: Scrape ads
        print("Step 1: Scraping Facebook Ads Library...")
        all_ads: List[AdData] = []
        
        for term in search_terms:
            print(f"  Searching: '{term}'...")
            ads = self.scraper.search_ads(
                search_term=term,
                max_ads=max_ads // len(search_terms),
            )
            print(f"    Found {len(ads)} ads")
            all_ads.extend(ads)
            time.sleep(1)  # Rate limiting
        
        print(f"\n  Total ads found: {len(all_ads)}")
        
        if not all_ads:
            print("\n  No ads found. This could mean:")
            print("  - No active ads in this market")
            print("  - Apify credits exhausted")
            print("  - Search terms too specific")
        
        # Step 2: Group by advertiser
        print("\nStep 2: Grouping by advertiser...")
        competitor_ads = self._group_by_advertiser(all_ads)
        print(f"  Found {len(competitor_ads)} unique advertisers")
        
        for ca in competitor_ads[:5]:
            print(f"    - {ca.page_name}: {ca.total_ads} ads")
        
        # Step 3: Analyze patterns
        print("\nStep 3: Analyzing ad patterns...")
        patterns = self._analyze_patterns(all_ads)
        
        print(f"  Hook types: {len(patterns.hook_types)}")
        print(f"  CTA types: {len(patterns.cta_types)}")
        print(f"  Themes: {len(patterns.themes)}")
        
        # Step 4: Generate suggestions
        print("\nStep 4: Generating suggestions...")
        hook_suggestions = self._generate_hook_suggestions(patterns, business_type)
        headline_suggestions = self._generate_headlines(patterns, business_type)
        cta_suggestions = self._generate_cta_suggestions(patterns)
        creative_suggestions = self._generate_creative_suggestions(patterns)
        messaging_gaps = self._find_messaging_gaps(patterns, business_type)
        
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Complete! ({elapsed:.1f}s)")
        print(f"{'='*60}\n")
        
        return AdAnalysis(
            business_type=business_type,
            location=location,
            search_query=search_terms[0],
            competitors_found=len(competitor_ads),
            total_ads_analyzed=len(all_ads),
            competitor_ads=competitor_ads,
            patterns=patterns,
            hook_suggestions=hook_suggestions,
            headline_suggestions=headline_suggestions,
            cta_suggestions=cta_suggestions,
            creative_suggestions=creative_suggestions,
            messaging_gaps=messaging_gaps,
        )
    
    def _group_by_advertiser(self, ads: List[AdData]) -> List[CompetitorAds]:
        """Group ads by advertiser/page."""
        by_page: Dict[str, List[AdData]] = {}
        
        for ad in ads:
            key = ad.page_name
            if key not in by_page:
                by_page[key] = []
            by_page[key].append(ad)
        
        competitor_ads = []
        
        for page_name, page_ads in by_page.items():
            # Aggregate patterns
            all_ctas = [ad.call_to_action for ad in page_ads if ad.call_to_action]
            all_hooks = [hook for ad in page_ads for hook in ad.hooks]
            
            media_mix = Counter(ad.media_type for ad in page_ads)
            
            competitor_ads.append(CompetitorAds(
                page_name=page_name,
                page_id=page_ads[0].page_id if page_ads else None,
                total_ads=len(page_ads),
                active_ads=sum(1 for ad in page_ads if ad.is_active),
                ads=page_ads,
                common_ctas=self._get_top_items(all_ctas, 3),
                common_hooks=self._get_top_items(all_hooks, 3),
                media_mix=dict(media_mix),
            ))
        
        # Sort by number of ads
        competitor_ads.sort(key=lambda x: x.total_ads, reverse=True)
        
        return competitor_ads
    
    def _analyze_patterns(self, ads: List[AdData]) -> AdPatterns:
        """Analyze patterns across all ads."""
        
        # Collect all patterns
        all_hooks = []
        all_ctas = []
        all_offers = []
        all_trust_signals = []
        all_emotions = []
        media_types = []
        
        for ad in ads:
            all_hooks.extend(ad.hooks)
            if ad.call_to_action:
                all_ctas.append(ad.call_to_action)
            all_offers.extend(ad.offers)
            all_trust_signals.extend(ad.trust_signals)
            all_emotions.extend(ad.emotional_appeals)
            media_types.append(ad.media_type)
        
        # Build pattern objects
        hook_counter = Counter(all_hooks)
        hook_types = [
            {"type": hook, "frequency": count, "percentage": count / len(ads) * 100 if ads else 0}
            for hook, count in hook_counter.most_common(10)
        ]
        
        cta_counter = Counter(all_ctas)
        cta_types = [
            {"type": cta, "frequency": count, "percentage": count / len(ads) * 100 if ads else 0}
            for cta, count in cta_counter.most_common(10)
        ]
        
        offer_counter = Counter(all_offers)
        offer_types = [
            {"type": offer, "frequency": count}
            for offer, count in offer_counter.most_common(10)
        ]
        
        # Media distribution
        media_counter = Counter(media_types)
        total_media = len(media_types)
        media_distribution = {
            media: count / total_media * 100 if total_media else 0
            for media, count in media_counter.items()
        }
        
        # Themes from emotions and trust signals
        themes = list(set(all_emotions + all_trust_signals))[:15]
        
        trust_signals = self._get_top_items(all_trust_signals, 10)
        
        return AdPatterns(
            hook_types=hook_types,
            cta_types=cta_types,
            offer_types=offer_types,
            media_distribution=media_distribution,
            themes=themes,
            trust_signals=trust_signals,
        )
    
    def _generate_hook_suggestions(
        self,
        patterns: AdPatterns,
        business_type: str,
    ) -> List[str]:
        """Generate hook suggestions based on patterns."""
        hooks = []
        
        # Based on common hook types
        hook_templates = {
            "[pain point]": f"Tired of unreliable {business_type}s?",
            "[desire]": f"Looking for a {business_type} you can trust?",
            "[need]": f"Need a {business_type} today?",
            "[command]": f"Stop calling {business_type}s who don't show up",
            "[warning]": f"Don't hire a {business_type} without reading this",
            "[relief]": f"Finally, a {business_type} who shows up on time",
            "[announcement]": f"Your local {business_type} is now accepting new customers",
            "[statistic]": f"Join 500+ satisfied customers this year",
        }
        
        for hook_type in patterns.hook_types[:5]:
            hook_name = hook_type.get("type", "")
            if hook_name in hook_templates:
                hooks.append(hook_templates[hook_name])
        
        # Add question hooks
        hooks.extend([
            f"Still searching for a reliable {business_type}?",
            f"What if your {business_type} actually showed up on time?",
            f"Ready to stop dealing with overpriced {business_type}s?",
        ])
        
        return hooks[:10]
    
    def _generate_headlines(
        self,
        patterns: AdPatterns,
        business_type: str,
    ) -> List[str]:
        """Generate headline suggestions."""
        headlines = []
        
        # From trust signals
        trust_to_headline = {
            "licensed": f"Licensed {business_type.title()}s You Can Trust",
            "insured": "Fully Insured for Your Protection",
            "experience": f"20+ Years of {business_type.title()} Experience",
            "local": f"Your Local {business_type.title()} Experts",
            "guarantee": "100% Satisfaction Guaranteed",
            "family owned": f"Family-Owned {business_type.title()} Service",
        }
        
        for signal in patterns.trust_signals[:5]:
            if signal in trust_to_headline:
                headlines.append(trust_to_headline[signal])
        
        # From themes
        theme_to_headline = {
            "speed": "Same-Day Service Available",
            "safety": "Safe & Reliable Service",
            "trust": "Trusted by Your Neighbors",
            "peace of mind": "Peace of Mind Guaranteed",
        }
        
        for theme in patterns.themes[:5]:
            if theme in theme_to_headline:
                headlines.append(theme_to_headline[theme])
        
        return headlines[:10]
    
    def _generate_cta_suggestions(self, patterns: AdPatterns) -> List[str]:
        """Generate CTA suggestions based on what's working."""
        ctas = []
        
        # Most common CTAs
        for cta_type in patterns.cta_types[:5]:
            ctas.append(cta_type.get("type", ""))
        
        # Standard high-performing CTAs
        standard_ctas = [
            "Call Now",
            "Get Free Quote",
            "Book Online",
            "Schedule Today",
            "Learn More",
            "Get Started",
        ]
        
        ctas.extend(standard_ctas)
        
        return list(dict.fromkeys(ctas))[:10]  # Unique, preserve order
    
    def _generate_creative_suggestions(self, patterns: AdPatterns) -> List[str]:
        """Generate creative format suggestions."""
        suggestions = []
        
        media_dist = patterns.media_distribution
        
        if media_dist.get("video", 0) > 40:
            suggestions.append("Video ads dominate this market - prioritize video content")
        else:
            suggestions.append("Image ads are common - video could stand out")
        
        if media_dist.get("carousel", 0) > 20:
            suggestions.append("Carousel ads are popular - show before/after or multiple services")
        
        # General recommendations
        suggestions.extend([
            "Show real team members for trust",
            "Include before/after photos if applicable",
            "Add customer testimonial overlay",
            "Show your branded vehicle/uniform",
        ])
        
        return suggestions[:8]
    
    def _find_messaging_gaps(
        self,
        patterns: AdPatterns,
        business_type: str,
    ) -> List[str]:
        """Find messaging opportunities competitors aren't using."""
        gaps = []
        
        # What's NOT in the patterns that could work
        potential_angles = [
            "emergency/24-7 service",
            "eco-friendly",
            "senior discounts",
            "financing available",
            "same-day service",
            "upfront pricing",
            "background-checked",
            "women-owned",
            "veteran-owned",
            "community involvement",
        ]
        
        used_themes = set(t.lower() for t in patterns.themes)
        used_signals = set(s.lower() for s in patterns.trust_signals)
        used = used_themes | used_signals
        
        for angle in potential_angles:
            if not any(word in used for word in angle.split()):
                gaps.append(f"No one emphasizes: {angle}")
        
        if len(gaps) < 3:
            gaps.extend([
                "Consider highlighting unique certifications",
                "Showcase community involvement",
                "Emphasize response time guarantees",
            ])
        
        return gaps[:8]
    
    def _get_top_items(self, items: List[str], n: int) -> List[str]:
        """Get most common items."""
        counter = Counter(items)
        return [item for item, _ in counter.most_common(n)]
    
    def save_report(
        self,
        analysis: AdAnalysis,
        output_dir: str = "output",
        filename: Optional[str] = None,
    ) -> str:
        """Save analysis to JSON file."""
        Path(output_dir).mkdir(exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ad_intel_{timestamp}.json"
        
        filepath = Path(output_dir) / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"Report saved: {filepath}")
        return str(filepath)
    
    def print_summary(self, analysis: AdAnalysis):
        """Print summary of analysis."""
        print("\n" + "="*60)
        print("AD INTELLIGENCE SUMMARY")
        print("="*60)
        
        print(f"\nAnalyzed: {analysis.total_ads_analyzed} ads from {analysis.competitors_found} competitors")
        
        if analysis.patterns:
            patterns = analysis.patterns
            
            print("\n### Media Mix")
            for media, pct in patterns.media_distribution.items():
                print(f"  - {media}: {pct:.0f}%")
            
            print("\n### Common CTAs")
            for cta in patterns.cta_types[:5]:
                print(f"  - {cta['type']} ({cta['frequency']} ads)")
            
            print("\n### Trust Signals Used")
            print(f"  {', '.join(patterns.trust_signals[:8])}")
            
            print("\n### Themes/Emotions")
            print(f"  {', '.join(patterns.themes[:8])}")
        
        print("\n### Hook Suggestions")
        for hook in analysis.hook_suggestions[:5]:
            print(f"  * {hook}")
        
        print("\n### Headline Suggestions")
        for headline in analysis.headline_suggestions[:5]:
            print(f"  * {headline}")
        
        print("\n### CTA Suggestions")
        for cta in analysis.cta_suggestions[:5]:
            print(f"  * {cta}")
        
        print("\n### Messaging Gaps (Opportunities)")
        for gap in analysis.messaging_gaps[:5]:
            print(f"  -> {gap}")
        
        print("\n" + "="*60)


def run_ad_analysis(
    business_type: str,
    location: str,
    max_ads: int = 50,
    save: bool = True,
    output_dir: str = "output",
) -> AdAnalysis:
    """
    Convenience function to run ad analysis.
    """
    agent = AdIntelAgent()
    
    analysis = agent.analyze_market(
        business_type=business_type,
        location=location,
        max_ads=max_ads,
    )
    
    agent.print_summary(analysis)
    
    if save:
        agent.save_report(analysis, output_dir)
    
    return analysis
