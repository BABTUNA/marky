"""
Reddit post and comment scraper.
Collects discussions for VoC analysis.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from .models import ResearchInput, Subreddit, Post, Comment
from .reddit_client import RedditClient
from .cache import Cache
from .discovery import SubredditDiscovery, KeywordExpansion


@dataclass
class ScrapingStats:
    """Statistics from a scraping session."""
    subreddits_searched: int
    posts_collected: int
    comments_collected: int
    posts_from_cache: int
    comments_from_cache: int
    
    def __str__(self) -> str:
        return (
            f"Scraped {self.subreddits_searched} subreddits, "
            f"{self.posts_collected} posts ({self.posts_from_cache} cached), "
            f"{self.comments_collected} comments ({self.comments_from_cache} cached)"
        )


class RedditScraper:
    """Scrapes posts and comments from Reddit."""
    
    def __init__(self, client: RedditClient, cache: Cache):
        self.client = client
        self.cache = cache
    
    def scrape_subreddit(
        self,
        subreddit: Subreddit,
        queries: Optional[List[str]] = None,
        posts_limit: int = 50,
        comments_per_post: int = 50,
        sort: str = "top",
        time_filter: str = "month",
    ) -> Tuple[List[Post], List[Comment]]:
        """
        Scrape posts and comments from a subreddit.
        
        Args:
            subreddit: The subreddit to scrape
            queries: Optional search queries (if None, just get top/new posts)
            posts_limit: Max posts to collect
            comments_per_post: Max comments per post
            sort: Post sort method
            time_filter: Time filter for 'top' sort
        
        Returns:
            Tuple of (posts, comments)
        """
        posts: List[Post] = []
        comments: List[Comment] = []
        seen_post_ids = set()
        
        # Method 1: Search with queries if provided
        if queries:
            for query in queries[:5]:  # Limit queries per subreddit
                try:
                    post_data_list = self.client.search_subreddit_posts(
                        subreddit=subreddit.name,
                        query=query,
                        sort="relevance",
                        limit=min(posts_limit // 3, 25),
                    )
                    
                    for post_data in post_data_list:
                        if post_data["id"] in seen_post_ids:
                            continue
                        seen_post_ids.add(post_data["id"])
                        
                        post = self._process_post(post_data)
                        posts.append(post)
                        
                        if len(posts) >= posts_limit:
                            break
                            
                except Exception as e:
                    print(f"Warning: Search failed for '{query}' in r/{subreddit.name}: {e}")
                    continue
                
                if len(posts) >= posts_limit:
                    break
        
        # Method 2: Get top/hot/new posts
        remaining = posts_limit - len(posts)
        if remaining > 0:
            try:
                # Get top posts
                post_data_list = self.client.get_subreddit_posts(
                    subreddit=subreddit.name,
                    sort=sort,
                    time_filter=time_filter,
                    limit=remaining,
                )
                
                for post_data in post_data_list:
                    if post_data["id"] in seen_post_ids:
                        continue
                    seen_post_ids.add(post_data["id"])
                    
                    post = self._process_post(post_data)
                    posts.append(post)
                    
            except Exception as e:
                print(f"Warning: Failed to get posts from r/{subreddit.name}: {e}")
        
        # Get new posts too for recent discussions
        remaining = posts_limit - len(posts)
        if remaining > 0:
            try:
                post_data_list = self.client.get_subreddit_posts(
                    subreddit=subreddit.name,
                    sort="new",
                    limit=min(remaining, 25),
                )
                
                for post_data in post_data_list:
                    if post_data["id"] in seen_post_ids:
                        continue
                    seen_post_ids.add(post_data["id"])
                    
                    post = self._process_post(post_data)
                    posts.append(post)
                    
            except Exception as e:
                print(f"Warning: Failed to get new posts from r/{subreddit.name}: {e}")
        
        # Collect comments for each post
        for post in posts:
            try:
                post_comments = self._get_post_comments(
                    post,
                    limit=comments_per_post,
                )
                comments.extend(post_comments)
            except Exception as e:
                print(f"Warning: Failed to get comments for post {post.id}: {e}")
                continue
        
        return posts, comments
    
    def _process_post(self, post_data: Dict[str, Any]) -> Post:
        """Process and cache a post."""
        post = Post(
            id=post_data["id"],
            subreddit=post_data["subreddit"],
            title=post_data["title"],
            selftext=post_data.get("selftext", ""),
            score=post_data.get("score", 0),
            num_comments=post_data.get("num_comments", 0),
            created_utc=post_data.get("created_utc", 0),
            url=post_data.get("url", ""),
            permalink=post_data.get("permalink", ""),
        )
        
        # Cache the post
        self.cache.save_post(post_data)
        
        return post
    
    def _get_post_comments(self, post: Post, limit: int = 50) -> List[Comment]:
        """Get comments for a post, using cache when possible."""
        # Check cache first
        cached_comments = self.cache.get_comments_by_post(post.id)
        if cached_comments and len(cached_comments) >= limit // 2:
            return [
                Comment(
                    id=c["id"],
                    post_id=c["post_id"],
                    subreddit=c["subreddit"],
                    body=c["body"],
                    score=c.get("score", 0),
                    created_utc=c.get("created_utc", 0),
                    parent_id=c.get("parent_id"),
                )
                for c in cached_comments[:limit]
            ]
        
        # Fetch from API
        comment_data_list = self.client.get_post_comments(
            post_id=post.id,
            subreddit=post.subreddit,
            sort="top",
            limit=limit,
        )
        
        comments = []
        for comment_data in comment_data_list:
            comment = Comment(
                id=comment_data["id"],
                post_id=comment_data["post_id"],
                subreddit=comment_data["subreddit"],
                body=comment_data["body"],
                score=comment_data.get("score", 0),
                created_utc=comment_data.get("created_utc", 0),
                parent_id=comment_data.get("parent_id"),
            )
            comments.append(comment)
            
            # Cache the comment
            self.cache.save_comment(comment_data)
        
        return comments
    
    def scrape_for_research(
        self,
        subreddits: List[Subreddit],
        keywords: KeywordExpansion,
        posts_per_subreddit: int = 50,
        comments_per_post: int = 50,
        max_posts_total: int = 500,
        max_comments_total: int = 2000,
    ) -> Tuple[List[Post], List[Comment], ScrapingStats]:
        """
        Comprehensive scraping for VoC research.
        
        Args:
            subreddits: List of subreddits to scrape
            keywords: Expanded keywords for searching
            posts_per_subreddit: Max posts per subreddit
            comments_per_post: Max comments per post
            max_posts_total: Global max posts
            max_comments_total: Global max comments
        
        Returns:
            Tuple of (all_posts, all_comments, stats)
        """
        all_posts: List[Post] = []
        all_comments: List[Comment] = []
        
        # Generate search queries from keywords
        search_queries = []
        search_queries.extend(keywords.product_keywords[:5])
        search_queries.extend(keywords.pain_point_phrases[:5])
        search_queries.extend(keywords.desire_phrases[:5])
        
        stats = ScrapingStats(
            subreddits_searched=0,
            posts_collected=0,
            comments_collected=0,
            posts_from_cache=0,
            comments_from_cache=0,
        )
        
        for subreddit in subreddits:
            if len(all_posts) >= max_posts_total:
                break
            
            print(f"Scraping r/{subreddit.name}...")
            
            # Adjust limits based on remaining budget
            remaining_posts = max_posts_total - len(all_posts)
            remaining_comments = max_comments_total - len(all_comments)
            
            posts_limit = min(posts_per_subreddit, remaining_posts)
            comments_limit = min(
                comments_per_post,
                remaining_comments // max(1, posts_limit),
            )
            
            posts, comments = self.scrape_subreddit(
                subreddit=subreddit,
                queries=search_queries,
                posts_limit=posts_limit,
                comments_per_post=comments_limit,
            )
            
            all_posts.extend(posts)
            all_comments.extend(comments)
            
            stats.subreddits_searched += 1
            stats.posts_collected += len(posts)
            stats.comments_collected += len(comments)
            
            print(f"  Collected {len(posts)} posts, {len(comments)} comments")
            
            if len(all_comments) >= max_comments_total:
                break
        
        return all_posts, all_comments, stats
