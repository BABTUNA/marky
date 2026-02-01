"""
Local Competitor Intelligence Agent.
Main orchestrator for the competitive analysis pipeline.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from .config import AppConfig
from .models import (
    SearchInput, Competitor, DiscoveryResult, WebsiteData,
    MarketAnalysis, IntelligenceReport, CompetitiveInsight, AdDifferentiator,
)
from .competitor_discovery import CompetitorDiscovery, ManualCompetitorInput, DiscoveryConfig
from .website_scraper import WebsiteScraper
from .content_extractor import ContentExtractor, MarketAnalyzer
from .ad_generator import AdDifferentiationGenerator


# ============================================================================
# Timing/Logging Classes
# ============================================================================

@dataclass
class StepTiming:
    """Timing for a single step."""
    step_name: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration_seconds: float = 0.0


@dataclass
class ProcessLog:
    """Complete process timing log."""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    steps: List[StepTiming] = field(default_factory=list)
    
    def start_step(self, step_name: str) -> StepTiming:
        """Start timing a step."""
        step = StepTiming(step_name=step_name, start_time=time.time())
        self.steps.append(step)
        return step
    
    def end_step(self, step: StepTiming):
        """End timing a step."""
        step.end_time = time.time()
        step.duration_seconds = step.end_time - step.start_time
    
    def finish(self):
        """Finish the process log."""
        self.end_time = datetime.now()
        self.total_duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def print_summary(self):
        """Print timing summary."""
        print("\n" + "-"*60)
        print("PROCESS TIMING LOG")
        print("-"*60)
        for step in self.steps:
            print(f"  {step.step_name}: {step.duration_seconds:.2f}s")
        print("-"*60)
        print(f"  TOTAL TIME: {self.total_duration_seconds:.2f}s ({self.total_duration_seconds/60:.1f} min)")
        print("-"*60)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration_seconds": self.total_duration_seconds,
            "steps": [
                {"step": s.step_name, "duration_seconds": s.duration_seconds}
                for s in self.steps
            ]
        }


# ============================================================================
# Claude Analysis Agent
# ============================================================================

class ClaudeAnalysisAgent:
    """
    Uses Claude to analyze competitor success/failure patterns.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Anthropic API key."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.available = self.api_key is not None
    
    def analyze_success_patterns(
        self,
        top_competitors: List[Competitor],
        worst_competitors: List[Competitor],
        market_analysis: MarketAnalysis,
    ) -> Dict[str, Any]:
        """
        Analyze what makes competitors successful vs unsuccessful.
        
        Returns structured analysis with success factors and failure patterns.
        """
        if not self.available:
            return self._generate_rule_based_analysis(
                top_competitors, worst_competitors, market_analysis
            )
        
        try:
            import requests
            
            # Build prompt with competitor data
            prompt = self._build_analysis_prompt(
                top_competitors, worst_competitors, market_analysis
            )
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 2000,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60,
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result["content"][0]["text"]
                return self._parse_analysis(analysis_text, top_competitors, worst_competitors)
            else:
                print(f"  Claude API error: {response.status_code}")
                return self._generate_rule_based_analysis(
                    top_competitors, worst_competitors, market_analysis
                )
                
        except Exception as e:
            print(f"  Claude analysis error: {e}")
            return self._generate_rule_based_analysis(
                top_competitors, worst_competitors, market_analysis
            )
    
    def _build_analysis_prompt(
        self,
        top_competitors: List[Competitor],
        worst_competitors: List[Competitor],
        market_analysis: MarketAnalysis,
    ) -> str:
        """Build the analysis prompt for Claude."""
        
        top_data = "\n".join([
            f"- {c.name}: {c.rating} stars, {c.review_count} reviews, "
            f"Services: {', '.join(c.services[:5]) if c.services else 'N/A'}, "
            f"Trust signals: {', '.join(c.trust_signals[:3]) if c.trust_signals else 'N/A'}"
            for c in top_competitors[:5]
        ])
        
        worst_data = "\n".join([
            f"- {c.name}: {c.rating} stars, {c.review_count} reviews, "
            f"Services: {', '.join(c.services[:5]) if c.services else 'N/A'}, "
            f"Trust signals: {', '.join(c.trust_signals[:3]) if c.trust_signals else 'N/A'}"
            for c in worst_competitors[:5]
        ])
        
        return f"""Analyze these local {market_analysis.business_type} businesses in {market_analysis.location}.

TOP-RATED COMPETITORS (successful):
{top_data}

LOWEST-RATED COMPETITORS (struggling):
{worst_data}

MARKET CONTEXT:
- Common services: {', '.join(market_analysis.common_services[:5])}
- Common trust signals: {', '.join(market_analysis.common_trust_signals[:3])}

Provide a JSON analysis with:
1. "success_factors": List of 3-5 things that make top competitors successful
2. "failure_patterns": List of 3-5 things that struggling competitors lack or do wrong
3. "key_differentiators": What specifically separates winners from losers
4. "recommendations": 3-5 actionable recommendations for a new business entering this market
5. "ad_angles_from_analysis": 3 specific ad hooks based on this analysis

Respond ONLY with valid JSON, no other text."""
    
    def _parse_analysis(
        self,
        analysis_text: str,
        top_competitors: List[Competitor],
        worst_competitors: List[Competitor],
    ) -> Dict[str, Any]:
        """Parse Claude's analysis response."""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                analysis["source"] = "claude"
                analysis["top_competitors_analyzed"] = [c.name for c in top_competitors[:5]]
                analysis["worst_competitors_analyzed"] = [c.name for c in worst_competitors[:5]]
                return analysis
        except json.JSONDecodeError:
            pass
        
        # If parsing fails, return the raw text in a structured format
        return {
            "source": "claude",
            "raw_analysis": analysis_text,
            "success_factors": [],
            "failure_patterns": [],
            "recommendations": [],
        }
    
    def _generate_rule_based_analysis(
        self,
        top_competitors: List[Competitor],
        worst_competitors: List[Competitor],
        market_analysis: MarketAnalysis,
    ) -> Dict[str, Any]:
        """Generate analysis using rules when Claude is not available."""
        
        # Analyze differences between top and worst
        top_services = set()
        top_signals = set()
        worst_services = set()
        worst_signals = set()
        
        for c in top_competitors:
            top_services.update(c.services or [])
            top_signals.update(c.trust_signals or [])
        
        for c in worst_competitors:
            worst_services.update(c.services or [])
            worst_signals.update(c.trust_signals or [])
        
        # Services top have that worst don't
        unique_to_top = top_services - worst_services
        # Signals top have that worst don't
        signals_unique_to_top = top_signals - worst_signals
        
        # Calculate average ratings
        top_avg = sum(c.rating or 0 for c in top_competitors) / max(1, len(top_competitors))
        worst_avg = sum(c.rating or 0 for c in worst_competitors) / max(1, len(worst_competitors))
        
        success_factors = [
            "Higher review counts indicate active customer engagement",
            "Consistent service quality reflected in ratings",
        ]
        
        if unique_to_top:
            success_factors.append(f"Offer services competitors don't: {', '.join(list(unique_to_top)[:3])}")
        
        if signals_unique_to_top:
            success_factors.append(f"Display trust signals: {', '.join(list(signals_unique_to_top)[:3])}")
        
        failure_patterns = [
            "Lower review counts suggest less customer engagement",
            "May lack professional website or online presence",
            "Missing key trust signals that customers look for",
        ]
        
        recommendations = [
            "Focus on getting more reviews from satisfied customers",
            "Prominently display all certifications and guarantees",
            f"Offer services that competitors lack: {', '.join(list(unique_to_top)[:2]) if unique_to_top else 'specialized services'}",
            "Respond to all reviews, especially negative ones",
            "Ensure website clearly communicates trust signals",
        ]
        
        ad_angles = [
            f"Highlight your {list(signals_unique_to_top)[0] if signals_unique_to_top else 'quality guarantee'}",
            f"Emphasize your {list(unique_to_top)[0] if unique_to_top else 'specialized expertise'}",
            "Use social proof: 'Join hundreds of satisfied customers'",
        ]
        
        return {
            "source": "rule_based",
            "success_factors": success_factors,
            "failure_patterns": failure_patterns,
            "key_differentiators": [
                f"Top competitors average {top_avg:.1f} stars vs {worst_avg:.1f} for struggling ones",
                f"Top competitors have more services listed ({len(top_services)} vs {len(worst_services)})",
            ],
            "recommendations": recommendations,
            "ad_angles_from_analysis": ad_angles,
            "top_competitors_analyzed": [c.name for c in top_competitors[:5]],
            "worst_competitors_analyzed": [c.name for c in worst_competitors[:5]],
        }


# ============================================================================
# Main Agent Class
# ============================================================================

class LocalIntelAgent:
    """
    Local Competitor Intelligence Agent.
    
    Discovers local competitors, scrapes their websites,
    extracts competitive intelligence, and generates ad differentiation.
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize the agent.
        
        Args:
            config: Application configuration. If None, loads from environment.
        """
        self.config = config or AppConfig.load()
        
        # Initialize components
        self.discovery = CompetitorDiscovery(self.config)
        self.scraper = WebsiteScraper(self.config)
        self.claude_agent = ClaudeAnalysisAgent()
    
    def analyze(
        self,
        business_type: str,
        location: str,
        radius_miles: float = 10.0,
        manual_competitors: Optional[List[Dict[str, Any]]] = None,
        include_worst_rated: bool = True,
        worst_radius_multiplier: float = 3.0,
        top_count: int = 3,
        worst_count: int = 3,
    ) -> IntelligenceReport:
        """
        Run full competitive intelligence analysis.
        
        Args:
            business_type: Type of business (e.g., "plumber", "restaurant")
            location: Location to search (city, zip, or coordinates)
            radius_miles: Search radius
            manual_competitors: Optional list of manually specified competitors
            include_worst_rated: Whether to include worst-rated competitor analysis
            worst_radius_multiplier: How much larger to search for worst-rated (3.0 = 3x radius)
            top_count: Number of top-rated competitors to analyze
            worst_count: Number of worst-rated competitors to analyze
        
        Returns:
            Complete IntelligenceReport with all insights
        """
        # Initialize process log
        process_log = ProcessLog()
        
        # Total competitors to analyze
        max_competitors = top_count + worst_count
        
        search_input = SearchInput(
            business_type=business_type,
            location=location,
            radius_miles=radius_miles,
            max_competitors=max_competitors,
        )
        
        print(f"\n{'='*60}")
        print("Local Competitor Intelligence Agent")
        print(f"{'='*60}")
        print(f"Business Type: {business_type}")
        print(f"Location: {location}")
        print(f"Search Radius: {radius_miles} miles")
        print(f"Analyzing: {top_count} top-rated + {worst_count} worst-rated = {max_competitors} total")
        print(f"{'='*60}\n")
        
        # Step 1: Discover competitors (two-pass strategy for top + worst)
        step1 = process_log.start_step("1. Competitor Discovery")
        print("Step 1: Discovering local competitors...")
        
        top_competitors = []
        worst_competitors = []
        
        if manual_competitors:
            competitors = ManualCompetitorInput.from_manual_list(manual_competitors)
            discovery_source = "manual"
            print(f"  Using {len(competitors)} manually specified competitors")
            
            # Still separate top/worst from manual input
            rated = [c for c in competitors if c.rating is not None]
            if rated:
                rated.sort(key=lambda c: (c.rating or 0, c.review_count or 0), reverse=True)
                top_competitors = rated[:top_count]
                worst_competitors = rated[-worst_count:] if len(rated) > worst_count else []
        else:
            # Use two-pass discovery for top AND worst rated
            if include_worst_rated:
                print(f"  Using two-pass search ({top_count} top + {worst_count} worst, {worst_radius_multiplier}x radius for worst)...")
                discovery_config = DiscoveryConfig(
                    top_count=top_count,
                    find_worst=True,
                    worst_count=worst_count,
                    worst_radius_multiplier=worst_radius_multiplier,
                    worst_rating_threshold=4.0,
                )
                competitors, top_competitors, worst_competitors = self.discovery.discover_with_worst(
                    search_input, discovery_config
                )
                discovery_source = "serpapi (two-pass)"
            else:
                # Single-pass discovery
                discovery_result = self.discovery.discover(search_input)
                competitors = discovery_result.competitors
                discovery_source = discovery_result.source
            
            if competitors:
                print(f"  Total: {len(competitors)} competitors found via {discovery_source}")
                
                # Show top rated
                if top_competitors:
                    print(f"\n  TOP RATED ({len(top_competitors)}):")
                    for c in top_competitors[:5]:
                        website_status = "[has website]" if c.website else "[no website]"
                        rating_str = f"({c.rating} stars, {c.review_count} reviews)" if c.rating else ""
                        print(f"    [+] {c.name} {rating_str} {website_status}")
                
                # Show worst rated
                if worst_competitors:
                    print(f"\n  LOWEST RATED ({len(worst_competitors)}):")
                    for c in worst_competitors[:5]:
                        website_status = "[has website]" if c.website else "[no website]"
                        rating_str = f"({c.rating} stars, {c.review_count} reviews)" if c.rating else ""
                        print(f"    [-] {c.name} {rating_str} {website_status}")
            else:
                print("  No competitors found automatically.")
                print("  Tip: Set SERPAPI_KEY or provide manual_competitors")
        
        process_log.end_step(step1)
        
        # Step 2: Scrape competitor websites
        # Only scrape the competitors we care about (top + worst), not all discovered
        step2 = process_log.start_step("2. Website Scraping")
        print("\nStep 2: Scraping competitor websites...")
        
        # Combine top + worst, limiting to max_competitors
        competitors_to_scrape = []
        seen_names = set()
        
        # Add top competitors first
        for c in top_competitors:
            if c.name not in seen_names:
                competitors_to_scrape.append(c)
                seen_names.add(c.name)
        
        # Add worst competitors
        for c in worst_competitors:
            if c.name not in seen_names:
                competitors_to_scrape.append(c)
                seen_names.add(c.name)
        
        # If we still have room, add more from the general pool up to max_competitors
        if len(competitors_to_scrape) < max_competitors:
            for c in competitors:
                if c.name not in seen_names:
                    competitors_to_scrape.append(c)
                    seen_names.add(c.name)
                    if len(competitors_to_scrape) >= max_competitors:
                        break
        
        # Update competitors list to only the ones we're analyzing
        competitors = competitors_to_scrape
        
        websites_with_urls = [c for c in competitors if c.website]
        print(f"  {len(websites_with_urls)} competitors to scrape (of {len(competitors)} selected)")
        
        website_data: List[WebsiteData] = []
        if websites_with_urls:
            website_data = self.scraper.scrape_competitors(websites_with_urls)
            success_count = sum(1 for w in website_data if w.pages_scraped)
            print(f"  Successfully scraped {success_count} websites")
        
        process_log.end_step(step2)
        
        # Step 3: Extract content and signals
        step3 = process_log.start_step("3. Content Extraction")
        print("\nStep 3: Extracting services, trust signals, and messaging...")
        extractor = ContentExtractor(business_type)
        website_data = extractor.extract_all(website_data)
        
        total_services = sum(len(w.services) for w in website_data)
        total_signals = sum(len(w.trust_signals) for w in website_data)
        print(f"  Found {total_services} services, {total_signals} trust signals")
        
        # Update competitors with extracted data
        for website in website_data:
            for comp in competitors:
                if comp.name == website.competitor_name:
                    comp.services = website.services
                    comp.trust_signals = website.trust_signals
                    comp.taglines = website.taglines
                    comp.unique_selling_points = website.unique_points
                    break
        
        process_log.end_step(step3)
        
        # Step 4: Analyze market
        step4 = process_log.start_step("4. Market Analysis")
        print("\nStep 4: Analyzing competitive landscape...")
        market_analyzer = MarketAnalyzer()
        market_analysis = market_analyzer.analyze(
            business_type=business_type,
            location=location,
            competitors=competitors,
            websites=website_data,
        )
        
        print(f"  Common services: {', '.join(market_analysis.common_services[:5])}")
        print(f"  Service gaps identified: {len(market_analysis.service_gaps)}")
        print(f"  Messaging opportunities: {len(market_analysis.messaging_opportunities)}")
        
        process_log.end_step(step4)
        
        # Step 5: Generate ad differentiation
        step5 = process_log.start_step("5. Ad Differentiation Generation")
        print("\nStep 5: Generating advertising differentiation...")
        ad_generator = AdDifferentiationGenerator(business_type)
        
        insights = ad_generator.generate_insights(market_analysis, website_data)
        differentiators = ad_generator.generate_differentiators(insights, market_analysis)
        headlines = ad_generator.generate_headlines(market_analysis, differentiators)
        taglines = ad_generator.generate_taglines(market_analysis)
        trust_signals = ad_generator.generate_trust_signals_to_use(market_analysis)
        
        print(f"  Generated {len(insights)} competitive insights")
        print(f"  Generated {len(differentiators)} ad differentiators")
        print(f"  Generated {len(headlines)} headline suggestions")
        
        process_log.end_step(step5)
        
        # Step 6: Claude Analysis (success/failure patterns)
        step6 = process_log.start_step("6. AI Success/Failure Analysis")
        print("\nStep 6: Analyzing success vs failure patterns...")
        
        claude_analysis = None
        if top_competitors and (worst_competitors or len(top_competitors) >= 2):
            if self.claude_agent.available:
                print("  Using Claude for deep analysis...")
            else:
                print("  Using rule-based analysis (set ANTHROPIC_API_KEY for Claude)...")
            
            claude_analysis = self.claude_agent.analyze_success_patterns(
                top_competitors=top_competitors,
                worst_competitors=worst_competitors if worst_competitors else top_competitors[-3:],
                market_analysis=market_analysis,
            )
            
            if claude_analysis.get("success_factors"):
                print(f"  Found {len(claude_analysis.get('success_factors', []))} success factors")
                print(f"  Found {len(claude_analysis.get('failure_patterns', []))} failure patterns")
        else:
            print("  Not enough rated competitors for analysis")
        
        process_log.end_step(step6)
        
        # Finish timing
        process_log.finish()
        
        # Build final report
        report = IntelligenceReport(
            search_input=search_input,
            competitors=competitors,
            market_analysis=market_analysis,
            insights=insights,
            differentiators=differentiators,
            headline_suggestions=headlines,
            tagline_suggestions=taglines,
            trust_signals_to_use=trust_signals,
        )
        
        # Add extra data to report dict
        report._timing = process_log
        report._top_competitors = top_competitors
        report._worst_competitors = worst_competitors
        report._claude_analysis = claude_analysis
        report._website_data = website_data
        
        print(f"\n{'='*60}")
        print("Analysis complete!")
        print(f"{'='*60}")
        
        # Print timing summary
        process_log.print_summary()
        
        return report
    
    def save_report(
        self,
        report: IntelligenceReport,
        output_dir: Optional[str] = None,
        prefix: str = "local_intel",
    ) -> str:
        """
        Save intelligence report to JSON file.
        """
        output_dir = output_dir or self.config.output_dir
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        filepath = output_path / filename
        
        # Build extended report
        report_dict = report.to_dict()
        
        # Add timing if available
        if hasattr(report, '_timing') and report._timing:
            report_dict["timing"] = report._timing.to_dict()
        
        # Add top/worst competitors
        if hasattr(report, '_top_competitors') and report._top_competitors:
            report_dict["top_rated_competitors"] = [
                {"name": c.name, "rating": c.rating, "review_count": c.review_count}
                for c in report._top_competitors
            ]
        
        if hasattr(report, '_worst_competitors') and report._worst_competitors:
            report_dict["worst_rated_competitors"] = [
                {"name": c.name, "rating": c.rating, "review_count": c.review_count}
                for c in report._worst_competitors
            ]
        
        # Add Claude analysis
        if hasattr(report, '_claude_analysis') and report._claude_analysis:
            report_dict["success_failure_analysis"] = report._claude_analysis
        
        # Add raw website data (full_text, homepage_html) for downstream use
        if hasattr(report, '_website_data') and report._website_data:
            report_dict["website_data"] = [
                {
                    "competitor_name": w.competitor_name,
                    "website_url": w.website_url,
                    "full_text": w.full_text,
                    "homepage_html": getattr(w, "homepage_html", None),
                }
                for w in report._website_data
            ]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\nReport saved to: {filepath}")
        return str(filepath)
    
    def print_summary(self, report: IntelligenceReport):
        """Print a summary of the intelligence report."""
        print("\n" + "="*60)
        print("COMPETITIVE INTELLIGENCE SUMMARY")
        print("="*60)
        
        print(f"\n### Competitors Analyzed: {len(report.competitors)}")
        
        # Show top rated
        if hasattr(report, '_top_competitors') and report._top_competitors:
            print("\n  TOP RATED:")
            for comp in report._top_competitors[:3]:
                rating = f"({comp.rating} stars, {comp.review_count} reviews)" if comp.rating else ""
                print(f"    [+] {comp.name} {rating}")
        
        # Show worst rated
        if hasattr(report, '_worst_competitors') and report._worst_competitors:
            print("\n  LOWEST RATED:")
            for comp in report._worst_competitors[:3]:
                rating = f"({comp.rating} stars, {comp.review_count} reviews)" if comp.rating else ""
                print(f"    [-] {comp.name} {rating}")
        
        # Show Claude analysis
        if hasattr(report, '_claude_analysis') and report._claude_analysis:
            analysis = report._claude_analysis
            
            print("\n### Success vs Failure Analysis")
            
            if analysis.get("success_factors"):
                print("\n  What makes top competitors successful:")
                for factor in analysis["success_factors"][:3]:
                    print(f"    [+] {factor}")
            
            if analysis.get("failure_patterns"):
                print("\n  What struggling competitors lack:")
                for pattern in analysis["failure_patterns"][:3]:
                    print(f"    [-] {pattern}")
            
            if analysis.get("recommendations"):
                print("\n  Recommendations for your business:")
                for rec in analysis["recommendations"][:3]:
                    print(f"    -> {rec}")
        
        if report.market_analysis:
            print(f"\n### Market Insights")
            print(f"  Common services: {', '.join(report.market_analysis.common_services[:5])}")
            print(f"  Trust signals used: {', '.join(report.market_analysis.common_trust_signals[:3])}")
            
            if report.market_analysis.service_gaps:
                print(f"\n  Service gaps (opportunities):")
                for gap in report.market_analysis.service_gaps[:3]:
                    print(f"    - {gap}")
        
        print(f"\n### Top Ad Differentiators")
        for diff in report.differentiators[:3]:
            print(f"  [{diff.angle_name}]")
            print(f"    Hook: \"{diff.hook}\"")
            print(f"    Best for: {diff.best_for}")
        
        print(f"\n### Headline Suggestions")
        for headline in report.headline_suggestions[:5]:
            print(f"  * {headline}")
        
        print(f"\n### Trust Signals to Emphasize")
        for signal in report.trust_signals_to_use[:5]:
            print(f"  [+] {signal}")
        
        print("\n" + "="*60)


def run_analysis(
    business_type: str,
    location: str,
    radius_miles: float = 10.0,
    save: bool = True,
    output_dir: str = "output",
    include_worst_rated: bool = True,
    worst_radius_multiplier: float = 3.0,
    top_count: int = 3,
    worst_count: int = 3,
) -> IntelligenceReport:
    """
    Convenience function to run competitive analysis.
    
    Args:
        include_worst_rated: If True, do a second search to find low-rated competitors
        worst_radius_multiplier: How much larger to search for worst-rated (e.g., 3.0 = 3x radius)
        top_count: Number of top-rated competitors to analyze
        worst_count: Number of worst-rated competitors to analyze
    """
    agent = LocalIntelAgent()
    
    report = agent.analyze(
        business_type=business_type,
        location=location,
        radius_miles=radius_miles,
        include_worst_rated=include_worst_rated,
        worst_radius_multiplier=worst_radius_multiplier,
        top_count=top_count,
        worst_count=worst_count,
    )
    
    if save:
        agent.save_report(report, output_dir)
    
    agent.print_summary(report)
    
    return report
