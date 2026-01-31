"""
Competitor discovery module.
Finds local competitors using Google Maps via SerpAPI or Outscraper.
"""

import time
import requests
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import quote
from dataclasses import dataclass

from .config import AppConfig, SerpAPIConfig, OutscraperConfig
from .models import SearchInput, Competitor, DiscoveryResult


@dataclass
class DiscoveryConfig:
    """Configuration for competitor discovery."""
    # For top competitors
    top_count: int = 5
    
    # For worst competitors (separate search with expanded radius)
    find_worst: bool = True
    worst_count: int = 3
    worst_radius_multiplier: float = 3.0  # Search 3x larger area for worst
    worst_rating_threshold: float = 4.0   # Consider < 4.0 as "worst"


class CompetitorDiscovery:
    """Discovers local competitors from various sources."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.request_delay = config.request_delay
    
    def discover(self, search: SearchInput) -> DiscoveryResult:
        """
        Discover competitors based on search input.
        
        Tries sources in order:
        1. SerpAPI (if configured)
        2. Outscraper (if configured)
        3. Manual fallback instructions
        """
        competitors: List[Competitor] = []
        source = "none"
        
        # Try SerpAPI first
        if self.config.serpapi:
            try:
                competitors = self._search_serpapi(search, self.config.serpapi)
                source = "serpapi"
            except Exception as e:
                print(f"SerpAPI search failed: {e}")
        
        # Try Outscraper as fallback
        if not competitors and self.config.outscraper:
            try:
                competitors = self._search_outscraper(search, self.config.outscraper)
                source = "outscraper"
            except Exception as e:
                print(f"Outscraper search failed: {e}")
        
        # If no API configured, provide instructions
        if not competitors and not self.config.has_competitor_discovery():
            print("\n" + "="*60)
            print("No competitor discovery API configured!")
            print("="*60)
            print("\nTo enable automatic competitor discovery, set one of:")
            print("  SERPAPI_KEY=your_key  (100 free searches/month)")
            print("  OUTSCRAPER_API_KEY=your_key  (500 free results)")
            print("\nGet SerpAPI key: https://serpapi.com")
            print("Get Outscraper key: https://outscraper.com")
            print("="*60 + "\n")
        
        return DiscoveryResult(
            query=search,
            competitors=competitors[:search.max_competitors],
            total_found=len(competitors),
            source=source,
        )
    
    def discover_with_worst(
        self,
        search: SearchInput,
        discovery_config: Optional[DiscoveryConfig] = None,
    ) -> Tuple[List[Competitor], List[Competitor], List[Competitor]]:
        """
        Discover competitors with separate search for worst-rated.
        
        Strategy:
        1. Normal search -> get top-rated (Google's default)
        2. Expanded radius search -> filter for low-rated only
        
        Returns:
            Tuple of (all_competitors, top_competitors, worst_competitors)
        """
        config = discovery_config or DiscoveryConfig()
        
        all_competitors: List[Competitor] = []
        top_competitors: List[Competitor] = []
        worst_competitors: List[Competitor] = []
        
        if not self.config.serpapi:
            # Fall back to regular discover
            result = self.discover(search)
            return result.competitors, [], []
        
        # Pass 1: Normal search for top-rated
        print("    Pass 1: Searching for top-rated competitors...")
        try:
            top_results = self._search_serpapi(search, self.config.serpapi)
            all_competitors.extend(top_results)
            
            # Get top N by rating
            rated = [c for c in top_results if c.rating is not None]
            rated.sort(key=lambda c: (c.rating or 0, c.review_count or 0), reverse=True)
            top_competitors = rated[:config.top_count]
            
            print(f"    Found {len(top_results)} competitors, {len(top_competitors)} top-rated")
        except Exception as e:
            print(f"    Pass 1 failed: {e}")
        
        # Pass 2: Expanded search for worst-rated
        if config.find_worst:
            print(f"    Pass 2: Searching wider area for low-rated competitors...")
            try:
                # Create expanded search
                expanded_search = SearchInput(
                    business_type=search.business_type,
                    location=search.location,
                    radius_miles=search.radius_miles * config.worst_radius_multiplier,
                    max_competitors=50,  # Get more to find low-rated ones
                )
                
                # Add a start parameter to get different results (pagination)
                worst_results = self._search_serpapi_with_start(
                    expanded_search, 
                    self.config.serpapi,
                    start=20,  # Skip first 20 (likely high-rated)
                )
                
                # Filter for low-rated only
                low_rated = [
                    c for c in worst_results 
                    if c.rating is not None and c.rating < config.worst_rating_threshold
                ]
                
                # If no truly low-rated, get the lowest from what we have
                if not low_rated and worst_results:
                    all_rated = [c for c in worst_results if c.rating is not None]
                    all_rated.sort(key=lambda c: (c.rating or 5, c.review_count or 0))
                    low_rated = all_rated[:config.worst_count]
                
                # Deduplicate against what we already have
                existing_names = {c.name.lower() for c in all_competitors}
                new_worst = [c for c in low_rated if c.name.lower() not in existing_names]
                
                worst_competitors = new_worst[:config.worst_count]
                all_competitors.extend(worst_competitors)
                
                if worst_competitors:
                    print(f"    Found {len(worst_competitors)} lower-rated competitors:")
                    for c in worst_competitors:
                        print(f"      - {c.name} ({c.rating} stars)")
                else:
                    print(f"    No competitors below {config.worst_rating_threshold} stars found")
                    # Fall back to lowest from original search
                    if top_results:
                        rated = [c for c in top_results if c.rating is not None]
                        rated.sort(key=lambda c: (c.rating or 5, c.review_count or 0))
                        worst_competitors = rated[:config.worst_count]
                        print(f"    Using lowest from main search: {[c.name for c in worst_competitors]}")
                        
            except Exception as e:
                print(f"    Pass 2 failed: {e}")
        
        return all_competitors, top_competitors, worst_competitors
    
    def _search_serpapi(
        self, 
        search: SearchInput, 
        config: SerpAPIConfig
    ) -> List[Competitor]:
        """Search for competitors using SerpAPI Google Maps."""
        return self._search_serpapi_with_start(search, config, start=0)
    
    def _search_serpapi_with_start(
        self, 
        search: SearchInput, 
        config: SerpAPIConfig,
        start: int = 0,
    ) -> List[Competitor]:
        """Search for competitors using SerpAPI Google Maps with pagination."""
        
        # Build search query
        query = f"{search.business_type} in {search.location}"
        
        params = {
            "engine": "google_maps",
            "q": query,
            "type": "search",
            "api_key": config.api_key,
        }
        
        # Add pagination if needed
        if start > 0:
            params["start"] = start
        
        # If location looks like coordinates, use ll parameter
        if self._is_coordinates(search.location):
            lat, lng = search.location.split(",")
            params["ll"] = f"@{lat.strip()},{lng.strip()},14z"
            params["q"] = search.business_type
        
        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        
        competitors = []
        
        # Parse local results
        local_results = data.get("local_results", [])
        
        for result in local_results:
            competitor = Competitor(
                name=result.get("title", "Unknown"),
                address=result.get("address", ""),
                phone=result.get("phone"),
                website=result.get("website"),
                rating=result.get("rating"),
                review_count=result.get("reviews"),
                price_level=result.get("price"),
                hours=result.get("hours"),
                categories=result.get("type", "").split(", ") if result.get("type") else [],
                latitude=result.get("gps_coordinates", {}).get("latitude"),
                longitude=result.get("gps_coordinates", {}).get("longitude"),
                place_id=result.get("place_id"),
            )
            competitors.append(competitor)
        
        return competitors
    
    def _search_outscraper(
        self, 
        search: SearchInput, 
        config: OutscraperConfig
    ) -> List[Competitor]:
        """Search for competitors using Outscraper."""
        
        query = f"{search.business_type}, {search.location}"
        
        headers = {
            "X-API-KEY": config.api_key,
        }
        
        params = {
            "query": query,
            "limit": search.max_competitors,
            "language": "en",
            "region": "us",
        }
        
        response = requests.get(
            "https://api.outscraper.com/maps/search-v3",
            headers=headers,
            params=params,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        
        competitors = []
        
        # Parse results
        results = data.get("data", [[]])[0] if data.get("data") else []
        
        for result in results:
            competitor = Competitor(
                name=result.get("name", "Unknown"),
                address=result.get("full_address", ""),
                phone=result.get("phone"),
                website=result.get("site"),
                rating=result.get("rating"),
                review_count=result.get("reviews"),
                price_level=result.get("price_level"),
                hours=result.get("working_hours_old_format"),
                categories=result.get("type", "").split(", ") if result.get("type") else [],
                latitude=result.get("latitude"),
                longitude=result.get("longitude"),
                place_id=result.get("place_id"),
            )
            competitors.append(competitor)
        
        return competitors
    
    def _is_coordinates(self, location: str) -> bool:
        """Check if location string looks like coordinates."""
        try:
            parts = location.split(",")
            if len(parts) == 2:
                float(parts[0].strip())
                float(parts[1].strip())
                return True
        except ValueError:
            pass
        return False


class ManualCompetitorInput:
    """Helper for manually inputting competitors when no API is available."""
    
    @staticmethod
    def from_google_maps_urls(urls: List[str]) -> List[Competitor]:
        """
        Create competitors from Google Maps URLs.
        User can manually copy URLs from Google Maps.
        """
        competitors = []
        for url in urls:
            # Extract basic info from URL if possible
            competitor = Competitor(
                name="[Manual Entry]",
                address="",
                website=None,
            )
            # URL parsing could be enhanced
            competitors.append(competitor)
        return competitors
    
    @staticmethod
    def from_manual_list(businesses: List[Dict[str, Any]]) -> List[Competitor]:
        """
        Create competitors from manual list.
        
        Example:
            businesses = [
                {"name": "ABC Plumbing", "website": "https://abcplumbing.com"},
                {"name": "XYZ Plumbers", "website": "https://xyzplumbers.com"},
            ]
        """
        competitors = []
        for biz in businesses:
            competitor = Competitor(
                name=biz.get("name", "Unknown"),
                address=biz.get("address", ""),
                phone=biz.get("phone"),
                website=biz.get("website"),
                rating=biz.get("rating"),
                review_count=biz.get("review_count"),
            )
            competitors.append(competitor)
        return competitors
