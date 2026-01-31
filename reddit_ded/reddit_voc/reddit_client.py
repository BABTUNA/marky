"""
Reddit API client with OAuth authentication and rate limiting.
"""

import time
import requests
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import RedditConfig
from .cache import Cache


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
    
    def wait(self):
        """Wait if necessary to respect rate limit."""
        now = time.time()
        elapsed = now - self.last_request_time
        
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


class RedditAPIError(Exception):
    """Custom exception for Reddit API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class RedditClient:
    """Reddit API client with OAuth and rate limiting."""
    
    BASE_URL = "https://oauth.reddit.com"
    AUTH_URL = "https://www.reddit.com/api/v1/access_token"
    
    def __init__(self, config: RedditConfig, cache: Optional[Cache] = None):
        self.config = config
        self.cache = cache
        self.rate_limiter = RateLimiter(config.requests_per_second)
        
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.user_agent,
        })
    
    def _authenticate(self):
        """Get OAuth access token using password grant (script flow)."""
        auth = (self.config.client_id, self.config.client_secret)
        data = {
            "grant_type": "password",
            "username": self.config.username,
            "password": self.config.password,
        }
        headers = {"User-Agent": self.config.user_agent}
        
        response = requests.post(
            self.AUTH_URL,
            auth=auth,
            data=data,
            headers=headers,
        )
        
        if response.status_code != 200:
            raise RedditAPIError(
                f"Authentication failed: {response.text}",
                response.status_code
            )
        
        token_data = response.json()
        
        if "error" in token_data:
            raise RedditAPIError(f"Auth error: {token_data['error']}")
        
        self._access_token = token_data["access_token"]
        # Token expires in ~1 hour, refresh a bit early
        self._token_expires_at = time.time() + token_data.get("expires_in", 3600) - 60
        
        self.session.headers.update({
            "Authorization": f"Bearer {self._access_token}",
        })
    
    def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        if not self._access_token or time.time() >= self._token_expires_at:
            self._authenticate()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((requests.exceptions.RequestException, RedditAPIError)),
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Make an authenticated request to Reddit API."""
        
        # Check cache first
        if use_cache and self.cache and method.upper() == "GET":
            cached = self.cache.get_cached_request(endpoint, params or {})
            if cached is not None:
                return cached
        
        self._ensure_authenticated()
        self.rate_limiter.wait()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            time.sleep(retry_after)
            raise RedditAPIError("Rate limited", 429)
        
        if response.status_code != 200:
            raise RedditAPIError(
                f"API error: {response.status_code} - {response.text}",
                response.status_code
            )
        
        data = response.json()
        
        # Cache the response
        if use_cache and self.cache and method.upper() == "GET":
            self.cache.set_cached_request(endpoint, params or {}, data)
        
        return data
    
    def get(self, endpoint: str, params: Optional[Dict] = None, use_cache: bool = True) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint, params, use_cache)
    
    # =========================================================================
    # Subreddit Discovery
    # =========================================================================
    
    def search_subreddits(
        self,
        query: str,
        limit: int = 25,
        sort: str = "relevance",
    ) -> List[Dict[str, Any]]:
        """
        Search for subreddits matching a query.
        
        Args:
            query: Search term
            limit: Max results (up to 100)
            sort: 'relevance' or 'activity'
        
        Returns:
            List of subreddit data dicts
        """
        params = {
            "q": query,
            "limit": min(limit, 100),
            "sort": sort,
        }
        
        response = self.get("/subreddits/search", params)
        
        subreddits = []
        for child in response.get("data", {}).get("children", []):
            sub_data = child.get("data", {})
            subreddits.append({
                "name": sub_data.get("display_name", ""),
                "display_name": sub_data.get("display_name_prefixed", ""),
                "subscribers": sub_data.get("subscribers", 0),
                "description": sub_data.get("public_description", ""),
                "title": sub_data.get("title", ""),
                "url": sub_data.get("url", ""),
            })
        
        return subreddits
    
    def subreddit_autocomplete(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get subreddit suggestions via autocomplete.
        
        Faster but less detailed than search_subreddits.
        """
        params = {
            "query": query,
            "limit": limit,
            "include_over_18": False,
        }
        
        response = self.get("/api/subreddit_autocomplete_v2", params)
        
        subreddits = []
        for child in response.get("data", {}).get("children", []):
            sub_data = child.get("data", {})
            subreddits.append({
                "name": sub_data.get("display_name", ""),
                "subscribers": sub_data.get("subscribers", 0),
            })
        
        return subreddits
    
    # =========================================================================
    # Post Collection
    # =========================================================================
    
    def get_subreddit_posts(
        self,
        subreddit: str,
        sort: str = "top",
        time_filter: str = "month",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get posts from a subreddit.
        
        Args:
            subreddit: Subreddit name (without r/)
            sort: 'hot', 'new', 'top', 'rising'
            time_filter: For 'top' sort: 'hour', 'day', 'week', 'month', 'year', 'all'
            limit: Max posts (up to 100)
        
        Returns:
            List of post data dicts
        """
        endpoint = f"/r/{subreddit}/{sort}"
        params = {"limit": min(limit, 100)}
        
        if sort == "top":
            params["t"] = time_filter
        
        response = self.get(endpoint, params)
        
        posts = []
        for child in response.get("data", {}).get("children", []):
            post_data = child.get("data", {})
            posts.append({
                "id": post_data.get("id", ""),
                "subreddit": post_data.get("subreddit", ""),
                "title": post_data.get("title", ""),
                "selftext": post_data.get("selftext", ""),
                "score": post_data.get("score", 0),
                "num_comments": post_data.get("num_comments", 0),
                "created_utc": post_data.get("created_utc", 0),
                "url": post_data.get("url", ""),
                "permalink": post_data.get("permalink", ""),
            })
        
        return posts
    
    def search_subreddit_posts(
        self,
        subreddit: str,
        query: str,
        sort: str = "relevance",
        time_filter: str = "all",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search for posts within a specific subreddit.
        
        Args:
            subreddit: Subreddit name
            query: Search query
            sort: 'relevance', 'hot', 'top', 'new', 'comments'
            time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
            limit: Max results
        
        Returns:
            List of post data dicts
        """
        endpoint = f"/r/{subreddit}/search"
        params = {
            "q": query,
            "restrict_sr": 1,  # Restrict to subreddit
            "sort": sort,
            "t": time_filter,
            "limit": min(limit, 100),
        }
        
        response = self.get(endpoint, params)
        
        posts = []
        for child in response.get("data", {}).get("children", []):
            post_data = child.get("data", {})
            posts.append({
                "id": post_data.get("id", ""),
                "subreddit": post_data.get("subreddit", ""),
                "title": post_data.get("title", ""),
                "selftext": post_data.get("selftext", ""),
                "score": post_data.get("score", 0),
                "num_comments": post_data.get("num_comments", 0),
                "created_utc": post_data.get("created_utc", 0),
                "url": post_data.get("url", ""),
                "permalink": post_data.get("permalink", ""),
            })
        
        return posts
    
    # =========================================================================
    # Comment Collection
    # =========================================================================
    
    def get_post_comments(
        self,
        post_id: str,
        subreddit: str,
        sort: str = "top",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get comments for a post.
        
        Args:
            post_id: The post ID
            subreddit: Subreddit name
            sort: 'top', 'best', 'new', 'controversial', 'old', 'qa'
            limit: Max comments
        
        Returns:
            List of comment data dicts
        """
        endpoint = f"/r/{subreddit}/comments/{post_id}"
        params = {
            "sort": sort,
            "limit": limit,
        }
        
        response = self.get(endpoint, params)
        
        comments = []
        
        # Response is [post_data, comments_data]
        if len(response) >= 2:
            comments_data = response[1].get("data", {}).get("children", [])
            comments = self._flatten_comments(comments_data, post_id, subreddit)
        
        return comments[:limit]
    
    def _flatten_comments(
        self,
        comments_data: List[Dict],
        post_id: str,
        subreddit: str,
        parent_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Recursively flatten nested comments."""
        comments = []
        
        for child in comments_data:
            if child.get("kind") != "t1":  # Not a comment
                continue
            
            comment_data = child.get("data", {})
            
            # Skip deleted/removed
            body = comment_data.get("body", "")
            if body in ["[deleted]", "[removed]", ""]:
                continue
            
            comment = {
                "id": comment_data.get("id", ""),
                "post_id": post_id,
                "subreddit": subreddit,
                "body": body,
                "score": comment_data.get("score", 0),
                "created_utc": comment_data.get("created_utc", 0),
                "parent_id": parent_id,
            }
            comments.append(comment)
            
            # Recursively get replies
            replies = comment_data.get("replies")
            if replies and isinstance(replies, dict):
                reply_children = replies.get("data", {}).get("children", [])
                comments.extend(
                    self._flatten_comments(
                        reply_children,
                        post_id,
                        subreddit,
                        comment["id"],
                    )
                )
        
        return comments
