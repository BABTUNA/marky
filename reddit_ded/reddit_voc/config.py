"""
Configuration management for Reddit VoC Agent.
Loads settings from environment variables.
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
class RedditConfig:
    """Reddit API configuration."""
    client_id: str
    client_secret: str
    username: str
    password: str
    user_agent: str
    
    # Rate limiting
    requests_per_second: float = 1.0  # Conservative default
    max_retries: int = 3
    
    # Caching
    cache_ttl_hours: int = 12
    
    @classmethod
    def from_env(cls) -> "RedditConfig":
        """Load configuration from environment variables."""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        username = os.getenv("REDDIT_USERNAME")
        password = os.getenv("REDDIT_PASSWORD")
        user_agent = os.getenv("REDDIT_USER_AGENT", f"VoCResearchAgent/1.0 by /u/{username}")
        
        if not all([client_id, client_secret, username, password]):
            raise ValueError(
                "Missing Reddit credentials. Set environment variables:\n"
                "  REDDIT_CLIENT_ID\n"
                "  REDDIT_CLIENT_SECRET\n"
                "  REDDIT_USERNAME\n"
                "  REDDIT_PASSWORD\n"
                "  REDDIT_USER_AGENT (optional)"
            )
        
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent,
        )


@dataclass
class ResearchConfig:
    """Research parameters configuration."""
    # Subreddit discovery
    max_subreddits: int = 20
    min_subscribers: int = 1000
    
    # Post collection
    posts_per_subreddit: int = 50
    max_posts_total: int = 500
    
    # Comment collection
    comments_per_post: int = 50
    max_comments_total: int = 2000
    
    # Analysis
    min_comment_length: int = 20
    max_themes: int = 12
    min_theme_examples: int = 3


@dataclass
class AppConfig:
    """Main application configuration."""
    reddit: RedditConfig
    research: ResearchConfig
    
    # Database
    db_path: str = "voc_cache.db"
    
    # Output
    output_dir: str = "output"
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load full configuration."""
        return cls(
            reddit=RedditConfig.from_env(),
            research=ResearchConfig(),
        )
