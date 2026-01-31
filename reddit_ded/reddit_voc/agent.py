"""
Main VoC Research Agent.
Orchestrates the full research pipeline.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .config import AppConfig, RedditConfig, ResearchConfig
from .models import ResearchInput, ResearchOutput
from .cache import Cache
from .reddit_client import RedditClient
from .discovery import SubredditDiscovery
from .scraper import RedditScraper
from .voc_extractor import VoCAnalyzer
from .output_generator import OutputGenerator


class VoCResearchAgent:
    """
    Voice of Customer Research Agent.
    
    Orchestrates the full pipeline:
    1. Discover relevant subreddits
    2. Scrape posts and comments
    3. Extract VoC signals
    4. Cluster into themes
    5. Generate ad research outputs
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize the research agent.
        
        Args:
            config: Application configuration. If None, loads from environment.
        """
        self.config = config or AppConfig.load()
        
        # Initialize components
        self.cache = Cache(
            db_path=self.config.db_path,
            ttl_hours=self.config.reddit.cache_ttl_hours,
        )
        
        self.client = RedditClient(self.config.reddit, self.cache)
        self.discovery = SubredditDiscovery(self.client, self.cache)
        self.scraper = RedditScraper(self.client, self.cache)
        self.analyzer = VoCAnalyzer(max_themes=self.config.research.max_themes)
        self.output_generator = OutputGenerator()
    
    def research(
        self,
        product: str,
        audience: str,
        market: str,
        keywords: Optional[list] = None,
        competitors: Optional[list] = None,
    ) -> ResearchOutput:
        """
        Run full VoC research for a product.
        
        Args:
            product: Product or service name/description
            audience: Target audience description
            market: Market or industry
            keywords: Additional keywords to search
            competitors: Competitor names to track
        
        Returns:
            Complete ResearchOutput with all artifacts
        """
        research_input = ResearchInput(
            product=product,
            audience=audience,
            market=market,
            keywords=keywords or [],
            competitors=competitors or [],
        )
        
        print(f"\n{'='*60}")
        print(f"VoC Research Agent")
        print(f"{'='*60}")
        print(f"Product: {product}")
        print(f"Audience: {audience}")
        print(f"Market: {market}")
        print(f"{'='*60}\n")
        
        # Step 1: Discover subreddits
        print("Step 1: Discovering relevant subreddits...")
        subreddits = self.discovery.discover_subreddits(
            research_input,
            max_subreddits=self.config.research.max_subreddits,
            min_subscribers=self.config.research.min_subscribers,
        )
        print(f"  Found {len(subreddits)} relevant subreddits")
        for sub in subreddits[:5]:
            print(f"    - r/{sub.name} ({sub.subscribers:,} subscribers, score: {sub.relevance_score:.1f})")
        
        # Step 2: Expand keywords for searching
        print("\nStep 2: Expanding search keywords...")
        keywords_expanded = self.discovery.expand_keywords(research_input)
        print(f"  Generated {len(keywords_expanded.product_keywords)} product keywords")
        print(f"  Generated {len(keywords_expanded.pain_point_phrases)} pain point phrases")
        
        # Step 3: Scrape posts and comments
        print("\nStep 3: Scraping posts and comments...")
        posts, comments, stats = self.scraper.scrape_for_research(
            subreddits=subreddits,
            keywords=keywords_expanded,
            posts_per_subreddit=self.config.research.posts_per_subreddit,
            comments_per_post=self.config.research.comments_per_post,
            max_posts_total=self.config.research.max_posts_total,
            max_comments_total=self.config.research.max_comments_total,
        )
        print(f"  {stats}")
        
        # Step 4: Analyze VoC signals
        print("\nStep 4: Analyzing Voice of Customer signals...")
        signals, themes = self.analyzer.analyze(comments, posts, research_input)
        print(f"  Extracted {len(signals)} VoC signals")
        print(f"  Clustered into {len(themes)} themes:")
        for theme in themes[:5]:
            print(f"    - {theme.name} ({theme.weight*100:.1f}% of signals)")
        
        # Extract language bank
        language_bank = self.analyzer.get_language_bank(signals, max_phrases=50)
        print(f"  Collected {len(language_bank)} reusable phrases")
        
        # Step 5: Generate outputs
        print("\nStep 5: Generating ad research outputs...")
        output = self.output_generator.generate_all(
            themes=themes,
            signals=signals,
            posts=posts,
            research_input=research_input,
            language_bank=language_bank,
        )
        
        print(f"  Generated:")
        print(f"    - VoC Brief with {len(output.voc_brief.top_themes)} themes")
        print(f"    - {len(output.angle_playbook.angles)} advertising angles")
        print(f"    - {len(output.hook_bank.hooks)} hooks")
        print(f"    - {len(output.objection_handling.objections)} objection handlers")
        print(f"    - Source map with {len(output.source_map.sources)} subreddits")
        
        print(f"\n{'='*60}")
        print("Research complete!")
        print(f"{'='*60}\n")
        
        return output
    
    def save_output(
        self,
        output: ResearchOutput,
        output_dir: Optional[str] = None,
        prefix: str = "voc_research",
    ) -> str:
        """
        Save research output to JSON files.
        
        Args:
            output: The research output to save
            output_dir: Directory to save to (default: config.output_dir)
            prefix: Filename prefix
        
        Returns:
            Path to the main output file
        """
        output_dir = output_dir or self.config.output_dir
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save combined output
        combined_file = output_path / f"{prefix}_{timestamp}.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(output.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Also save individual components
        components = {
            "voc_brief": output.voc_brief.to_dict(),
            "angle_playbook": output.angle_playbook.to_dict(),
            "hook_bank": output.hook_bank.to_dict(),
            "objection_handling": output.objection_handling.to_dict(),
            "source_map": output.source_map.to_dict(),
        }
        
        for name, data in components.items():
            component_file = output_path / f"{prefix}_{timestamp}_{name}.json"
            with open(component_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Output saved to: {combined_file}")
        return str(combined_file)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()


def run_research(
    product: str,
    audience: str,
    market: str,
    keywords: Optional[list] = None,
    competitors: Optional[list] = None,
    save: bool = True,
    output_dir: str = "output",
) -> ResearchOutput:
    """
    Convenience function to run research.
    
    Args:
        product: Product/service name
        audience: Target audience
        market: Market/industry
        keywords: Additional keywords
        competitors: Competitor names
        save: Whether to save output files
        output_dir: Where to save outputs
    
    Returns:
        ResearchOutput with all artifacts
    """
    agent = VoCResearchAgent()
    
    output = agent.research(
        product=product,
        audience=audience,
        market=market,
        keywords=keywords,
        competitors=competitors,
    )
    
    if save:
        agent.save_output(output, output_dir)
    
    return output
