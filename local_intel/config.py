"""
Configuration for Local Competitor Intelligence Agent.
"""

import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class SerpAPIConfig:
    """SerpAPI configuration for Google Maps searches."""
    api_key: str
    
    @classmethod
    def from_env(cls) -> Optional["SerpAPIConfig"]:
        """Load from environment. Returns None if not configured."""
        api_key = os.getenv("SERPAPI_KEY") or os.getenv("SERPAPI_API_KEY")
        if api_key:
            return cls(api_key=api_key)
        return None


@dataclass
class FirecrawlConfig:
    """Firecrawl configuration for website scraping."""
    api_key: str
    
    @classmethod
    def from_env(cls) -> Optional["FirecrawlConfig"]:
        """Load from environment. Returns None if not configured."""
        api_key = os.getenv("FIRECRAWL_API_KEY") or os.getenv("FIRECRAWL_KEY")
        if api_key:
            return cls(api_key=api_key)
        return None


@dataclass
class OutscraperConfig:
    """Outscraper configuration for Google Maps data."""
    api_key: str
    
    @classmethod
    def from_env(cls) -> Optional["OutscraperConfig"]:
        """Load from environment. Returns None if not configured."""
        api_key = os.getenv("OUTSCRAPER_API_KEY") or os.getenv("OUTSCRAPER_KEY")
        if api_key:
            return cls(api_key=api_key)
        return None


@dataclass
class AppConfig:
    """Main application configuration."""
    serpapi: Optional[SerpAPIConfig] = None
    firecrawl: Optional[FirecrawlConfig] = None
    outscraper: Optional[OutscraperConfig] = None
    
    # Scraping settings
    max_competitors: int = 20
    max_pages_per_site: int = 5
    request_delay: float = 1.0  # seconds between requests
    
    # Output
    output_dir: str = "output"
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment."""
        return cls(
            serpapi=SerpAPIConfig.from_env(),
            firecrawl=FirecrawlConfig.from_env(),
            outscraper=OutscraperConfig.from_env(),
        )
    
    def has_competitor_discovery(self) -> bool:
        """Check if we can discover competitors."""
        return self.serpapi is not None or self.outscraper is not None
    
    def has_website_scraping(self) -> bool:
        """Check if we have paid scraping. Jina Reader is always available as free fallback."""
        return self.firecrawl is not None
