"""
SQLite-based caching for Reddit API responses.
Reduces API calls and respects rate limits.
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any, List
from contextlib import contextmanager
from pathlib import Path


class Cache:
    """SQLite cache for Reddit API responses."""
    
    def __init__(self, db_path: str = "voc_cache.db", ttl_hours: int = 12):
        self.db_path = db_path
        self.ttl_hours = ttl_hours
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS subreddits (
                    name TEXT PRIMARY KEY,
                    display_name TEXT,
                    subscribers INTEGER,
                    description TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    subreddit TEXT,
                    title TEXT,
                    selftext TEXT,
                    score INTEGER,
                    num_comments INTEGER,
                    created_utc REAL,
                    url TEXT,
                    permalink TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    post_id TEXT,
                    subreddit TEXT,
                    body TEXT,
                    score INTEGER,
                    created_utc REAL,
                    parent_id TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit);
                CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);
                CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at);
            """)
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def _make_key(self, prefix: str, *args) -> str:
        """Create a cache key from prefix and arguments."""
        data = f"{prefix}:{':'.join(str(a) for a in args)}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if not expired."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
                (key, datetime.now())
            ).fetchone()
            
            if row:
                return json.loads(row["value"])
        return None
    
    def set(self, key: str, value: Any, ttl_hours: Optional[int] = None):
        """Set a cached value with expiration."""
        ttl = ttl_hours or self.ttl_hours
        expires_at = datetime.now() + timedelta(hours=ttl)
        
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO cache (key, value, expires_at) 
                   VALUES (?, ?, ?)""",
                (key, json.dumps(value), expires_at)
            )
    
    def get_cached_request(self, endpoint: str, params: dict) -> Optional[Any]:
        """Get cached API response."""
        key = self._make_key("api", endpoint, json.dumps(params, sort_keys=True))
        return self.get(key)
    
    def set_cached_request(self, endpoint: str, params: dict, response: Any):
        """Cache an API response."""
        key = self._make_key("api", endpoint, json.dumps(params, sort_keys=True))
        self.set(key, response)
    
    # Subreddit caching
    def save_subreddit(self, name: str, display_name: str, subscribers: int, description: str):
        """Save a discovered subreddit."""
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO subreddits 
                   (name, display_name, subscribers, description) VALUES (?, ?, ?, ?)""",
                (name, display_name, subscribers, description)
            )
    
    def get_subreddits(self) -> List[dict]:
        """Get all cached subreddits."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM subreddits ORDER BY subscribers DESC").fetchall()
            return [dict(row) for row in rows]
    
    # Post caching
    def save_post(self, post_data: dict):
        """Save a scraped post."""
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO posts 
                   (id, subreddit, title, selftext, score, num_comments, created_utc, url, permalink)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    post_data["id"],
                    post_data["subreddit"],
                    post_data["title"],
                    post_data.get("selftext", ""),
                    post_data.get("score", 0),
                    post_data.get("num_comments", 0),
                    post_data.get("created_utc", 0),
                    post_data.get("url", ""),
                    post_data.get("permalink", ""),
                )
            )
    
    def get_posts_by_subreddit(self, subreddit: str) -> List[dict]:
        """Get cached posts for a subreddit."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM posts WHERE subreddit = ? ORDER BY score DESC",
                (subreddit,)
            ).fetchall()
            return [dict(row) for row in rows]
    
    def post_exists(self, post_id: str) -> bool:
        """Check if a post is already cached."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT 1 FROM posts WHERE id = ?", (post_id,)).fetchone()
            return row is not None
    
    # Comment caching
    def save_comment(self, comment_data: dict):
        """Save a scraped comment."""
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO comments 
                   (id, post_id, subreddit, body, score, created_utc, parent_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    comment_data["id"],
                    comment_data["post_id"],
                    comment_data["subreddit"],
                    comment_data["body"],
                    comment_data.get("score", 0),
                    comment_data.get("created_utc", 0),
                    comment_data.get("parent_id"),
                )
            )
    
    def get_comments_by_post(self, post_id: str) -> List[dict]:
        """Get cached comments for a post."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM comments WHERE post_id = ? ORDER BY score DESC",
                (post_id,)
            ).fetchall()
            return [dict(row) for row in rows]
    
    def get_all_comments(self) -> List[dict]:
        """Get all cached comments."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM comments ORDER BY score DESC"
            ).fetchall()
            return [dict(row) for row in rows]
    
    def comment_exists(self, comment_id: str) -> bool:
        """Check if a comment is already cached."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT 1 FROM comments WHERE id = ?", (comment_id,)).fetchone()
            return row is not None
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._get_connection() as conn:
            subreddit_count = conn.execute("SELECT COUNT(*) FROM subreddits").fetchone()[0]
            post_count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
            comment_count = conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
            
            return {
                "subreddits": subreddit_count,
                "posts": post_count,
                "comments": comment_count,
            }
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache WHERE expires_at < ?", (datetime.now(),))
