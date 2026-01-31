"""
Website scraper module.
Scrapes competitor websites using Firecrawl or free Jina Reader.
"""

import time
import requests
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

from .config import AppConfig, FirecrawlConfig
from .models import Competitor, ScrapedPage, WebsiteData


class WebsiteScraper:
    """Scrapes competitor websites for content analysis."""
    
    # Common pages to scrape on business websites
    IMPORTANT_PAGES = [
        "",  # Homepage
        "/services",
        "/about",
        "/about-us", 
        "/pricing",
        "/prices",
        "/rates",
        "/contact",
        "/why-us",
        "/why-choose-us",
    ]
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.request_delay = config.request_delay
    
    def scrape_competitor(self, competitor: Competitor) -> Optional[WebsiteData]:
        """
        Scrape a competitor's website.
        
        Returns WebsiteData with scraped content, or None if no website.
        """
        if not competitor.website:
            return None
        
        website_url = self._normalize_url(competitor.website)
        
        pages: List[ScrapedPage] = []
        
        # Try to scrape homepage first
        homepage = self._scrape_page(website_url)
        if homepage and homepage.success:
            pages.append(homepage)
        else:
            # If homepage fails, website is likely inaccessible
            return WebsiteData(
                competitor_name=competitor.name,
                website_url=website_url,
                pages_scraped=[homepage] if homepage else [],
            )
        
        # Try to scrape additional important pages
        for page_path in self.IMPORTANT_PAGES[1:]:  # Skip homepage, already scraped
            if len(pages) >= self.config.max_pages_per_site:
                break
            
            page_url = urljoin(website_url, page_path)
            page = self._scrape_page(page_url)
            
            if page and page.success and page.content:
                # Only add if we got meaningful content
                if len(page.content) > 100:
                    pages.append(page)
            
            time.sleep(self.request_delay)
        
        # Combine all content
        full_text = "\n\n---\n\n".join([
            f"# {p.url}\n\n{p.content}" 
            for p in pages 
            if p.success and p.content
        ])
        
        return WebsiteData(
            competitor_name=competitor.name,
            website_url=website_url,
            pages_scraped=pages,
            full_text=full_text,
        )
    
    def scrape_competitors(
        self, 
        competitors: List[Competitor],
        progress_callback: Optional[callable] = None,
    ) -> List[WebsiteData]:
        """
        Scrape multiple competitors' websites.
        
        Args:
            competitors: List of competitors to scrape
            progress_callback: Optional callback(current, total, competitor_name)
        """
        results: List[WebsiteData] = []
        
        # Filter to only competitors with websites
        with_websites = [c for c in competitors if c.website]
        
        for i, competitor in enumerate(with_websites):
            if progress_callback:
                progress_callback(i + 1, len(with_websites), competitor.name)
            else:
                print(f"Scraping {i+1}/{len(with_websites)}: {competitor.name}...")
            
            website_data = self.scrape_competitor(competitor)
            if website_data:
                results.append(website_data)
            
            # Delay between competitors
            if i < len(with_websites) - 1:
                time.sleep(self.request_delay)
        
        return results
    
    def _scrape_page(self, url: str) -> Optional[ScrapedPage]:
        """
        Scrape a single page.
        
        Tries in order:
        1. Firecrawl (if configured)
        2. Jina Reader (free fallback)
        """
        # Try Firecrawl first
        if self.config.firecrawl:
            result = self._scrape_with_firecrawl(url)
            if result and result.success:
                return result
        
        # Fall back to Jina Reader (always free)
        return self._scrape_with_jina(url)
    
    def _scrape_with_firecrawl(self, url: str) -> Optional[ScrapedPage]:
        """Scrape using Firecrawl API."""
        if not self.config.firecrawl:
            return None
        
        try:
            response = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={
                    "Authorization": f"Bearer {self.config.firecrawl.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                    "timeout": 30000,
                },
                timeout=60,
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("data", {}).get("markdown", "")
                title = data.get("data", {}).get("metadata", {}).get("title", "")
                
                return ScrapedPage(
                    url=url,
                    title=title,
                    content=content,
                    scrape_method="firecrawl",
                    success=True,
                )
            else:
                return ScrapedPage(
                    url=url,
                    content="",
                    scrape_method="firecrawl",
                    success=False,
                    error=f"HTTP {response.status_code}",
                )
                
        except Exception as e:
            return ScrapedPage(
                url=url,
                content="",
                scrape_method="firecrawl",
                success=False,
                error=str(e),
            )
    
    def _scrape_with_jina(self, url: str) -> ScrapedPage:
        """
        Scrape using Jina Reader (free, no API key needed).
        
        Just prepend r.jina.ai/ to any URL.
        """
        try:
            jina_url = f"https://r.jina.ai/{url}"
            
            response = requests.get(
                jina_url,
                headers={
                    "Accept": "text/plain",
                    "User-Agent": "LocalIntelAgent/1.0",
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Extract title from content if present
                title = ""
                lines = content.split("\n")
                for line in lines[:10]:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                    elif line.startswith("Title:"):
                        title = line.replace("Title:", "").strip()
                        break
                
                return ScrapedPage(
                    url=url,
                    title=title,
                    content=content,
                    scrape_method="jina",
                    success=True,
                )
            else:
                return ScrapedPage(
                    url=url,
                    content="",
                    scrape_method="jina",
                    success=False,
                    error=f"HTTP {response.status_code}",
                )
                
        except Exception as e:
            return ScrapedPage(
                url=url,
                content="",
                scrape_method="jina",
                success=False,
                error=str(e),
            )
    
    def _normalize_url(self, url: str) -> str:
        """Ensure URL has scheme and is properly formatted."""
        url = url.strip()
        
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        # Ensure trailing slash for base URL
        parsed = urlparse(url)
        if not parsed.path:
            url = url + "/"
        
        return url
