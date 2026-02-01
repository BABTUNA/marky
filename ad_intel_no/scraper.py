"""
Google Ads scraper using SerpAPI.
Scrapes paid search ads from Google search results.
"""

import os
import re
import requests
from typing import List, Optional, Dict, Any
from .models import AdData, CompetitorAds


class GoogleAdsScraper:
    """
    Scrapes Google Ads (paid search) using SerpAPI.
    
    Based on: https://serpapi.com/google-ads
    Uses your existing SERPAPI_KEY - no additional API needed.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not set. Get one at https://serpapi.com")
        
        self.base_url = "https://serpapi.com/search"
    
    def search_ads(
        self,
        search_term: str,
        location: str = "United States",
        max_ads: int = 50,
        **kwargs,
    ) -> List[AdData]:
        """
        Search Google for paid ads on a search term.
        
        Args:
            search_term: Search query (e.g., "plumber Providence RI")
            location: Location for search (e.g., "Providence, Rhode Island")
            max_ads: Maximum ads to return
        
        Returns:
            List of AdData from Google paid ads
        """
        ads: List[AdData] = []
        
        print(f"    Searching Google Ads via SerpAPI...")
        print(f"    Query: '{search_term}' in '{location}'")
        
        try:
            params = {
                "engine": "google",
                "q": search_term,
                "location": location,
                "google_domain": "google.com",
                "gl": "us",
                "hl": "en",
                "api_key": self.api_key,
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Parse ads from response
            # Google ads appear in "ads" array
            ads_data = data.get("ads", [])
            
            if ads_data:
                print(f"    Found {len(ads_data)} paid ads")
                
                for item in ads_data[:max_ads]:
                    ad = self._parse_google_ad(item)
                    if ad:
                        ads.append(ad)
            else:
                print("    No paid ads found for this search")
                
                # Also check shopping ads
                shopping = data.get("shopping_results", [])
                if shopping:
                    print(f"    Found {len(shopping)} shopping ads")
            
            # Also check local ads if available
            # Note: local_ads is an object with an "ads" array inside
            local_ads_obj = data.get("local_ads", {})
            if local_ads_obj and isinstance(local_ads_obj, dict):
                local_ads_list = local_ads_obj.get("ads", [])
                if local_ads_list:
                    print(f"    Found {len(local_ads_list)} local service ads")
                    # Parse local service ads
                    count = 0
                    for item in local_ads_list:
                        if count >= max_ads:
                            break
                        ad = self._parse_local_ad(item)
                        if ad:
                            ads.append(ad)
                            count += 1
                        
        except requests.RequestException as e:
            print(f"    Request error: {e}")
        except Exception as e:
            print(f"    Error: {e}")
        
        return ads
    
    def search_multiple_queries(
        self,
        queries: List[str],
        location: str = "United States",
        max_ads_per_query: int = 20,
    ) -> List[AdData]:
        """
        Search multiple queries and combine results.
        
        Args:
            queries: List of search queries
            location: Location for search
            max_ads_per_query: Max ads per query
        
        Returns:
            Combined list of AdData (deduplicated)
        """
        all_ads: List[AdData] = []
        seen_urls = set()
        
        for query in queries:
            ads = self.search_ads(query, location, max_ads_per_query)
            
            for ad in ads:
                # Deduplicate by link URL
                if ad.link_url and ad.link_url not in seen_urls:
                    all_ads.append(ad)
                    seen_urls.add(ad.link_url)
                elif not ad.link_url:
                    all_ads.append(ad)
        
        return all_ads
    
    def _parse_google_ad(self, item: Dict[str, Any]) -> Optional[AdData]:
        """
        Parse Google paid ad from SerpAPI response.
        
        Fields available:
        - position, block_position (top, bottom)
        - title, link, displayed_link
        - description, source
        - sitelinks, extensions
        - tracking_link
        """
        try:
            ad_id = item.get("tracking_link", "")[:50] or str(hash(item.get("link", "")))
            
            # Get advertiser name from displayed_link or source
            page_name = item.get("source") or ""
            if not page_name and item.get("displayed_link"):
                # Extract domain as page name
                displayed = item.get("displayed_link", "")
                page_name = displayed.split("/")[0] if "/" in displayed else displayed
            
            # Ad text is the description
            ad_text = item.get("description", "")
            
            # Headline is the title
            headline = item.get("title", "")
            
            # Get sitelinks as additional info
            sitelinks = item.get("sitelinks", [])
            sitelink_text = ""
            if sitelinks:
                sitelink_titles = [s.get("title", "") for s in sitelinks if s.get("title")]
                sitelink_text = " | ".join(sitelink_titles)
            
            # Get extensions (callouts, snippets)
            extensions = item.get("extensions", [])
            
            ad = AdData(
                ad_id=str(ad_id)[:20],
                page_name=page_name,
                page_id=None,
                ad_text=ad_text,
                headline=headline,
                description=sitelink_text if sitelink_text else None,
                call_to_action=None,  # Google ads don't have explicit CTA
                link_url=item.get("link"),
                media_type="text",  # Google search ads are text
                image_urls=[],
                video_url=None,
                is_active=True,
                start_date=None,
                end_date=None,
            )
            
            # Extract patterns
            full_text = f"{headline} {ad_text}"
            ad.hooks = self._extract_hooks(full_text)
            ad.offers = self._extract_offers(full_text)
            ad.trust_signals = self._extract_trust_signals(full_text)
            ad.emotional_appeals = self._extract_emotional_appeals(full_text)
            
            return ad
            
        except Exception as e:
            print(f"    Error parsing ad: {e}")
            return None
    
    def _parse_local_ad(self, item: Dict[str, Any]) -> Optional[AdData]:
        """
        Parse local service ad from SerpAPI.
        
        Fields per docs: title, rating, rating_count, type, service_area,
        hours, years_in_business, phone, link, thumbnail, highlighted_details
        """
        try:
            title = item.get("title") or "Unknown"
            
            # Build description from available fields
            description_parts = []
            if item.get("type"):
                description_parts.append(item["type"])
            if item.get("service_area"):
                description_parts.append(item["service_area"])
            if item.get("hours"):
                description_parts.append(item["hours"])
            if item.get("years_in_business"):
                description_parts.append(item["years_in_business"])
            if item.get("highlighted_details"):
                description_parts.extend(item["highlighted_details"])
            
            description = " | ".join(description_parts)
            
            ad = AdData(
                ad_id=str(hash(title))[:10],
                page_name=title,
                page_id=None,
                ad_text=description,
                headline=title,
                description=description,
                call_to_action="Call Now" if item.get("phone") else "Learn More",
                link_url=item.get("link"),
                media_type="local",
                image_urls=[item["thumbnail"]] if item.get("thumbnail") else [],
                is_active=True,
            )
            
            # Extract trust signals from description
            trust_signals = []
            if item.get("rating"):
                trust_signals.append(f"{item['rating']} stars")
            if item.get("rating_count"):
                trust_signals.append(f"{item['rating_count']} reviews")
            if item.get("years_in_business"):
                trust_signals.append(item["years_in_business"])
            ad.trust_signals = trust_signals
            
            # Extract patterns from description
            if description:
                ad.hooks = self._extract_hooks(description)
                ad.offers = self._extract_offers(description)
            
            return ad
            
        except Exception as e:
            print(f"      Error parsing local ad: {e}")
            return None
    
    
    def _extract_hooks(self, text: str) -> List[str]:
        """Extract hook patterns from ad text."""
        hooks = []
        text_lower = text.lower()
        
        # Question hooks
        if "?" in text:
            sentences = text.split("?")
            for s in sentences[:-1]:  # All but last (which is after the ?)
                hook = s.strip().split("\n")[-1] + "?"
                if len(hook) < 100:
                    hooks.append(hook)
        
        # Pattern hooks
        hook_patterns = [
            (r"tired of", "pain point"),
            (r"looking for", "desire"),
            (r"need a", "need"),
            (r"want to", "desire"),
            (r"stop", "command"),
            (r"don't", "warning"),
            (r"finally", "relief"),
            (r"introducing", "announcement"),
            (r"new:", "announcement"),
            (r"\d+%", "statistic"),
        ]
        
        for pattern, hook_type in hook_patterns:
            if re.search(pattern, text_lower):
                hooks.append(f"[{hook_type}]")
        
        return hooks[:5]
    
    def _extract_offers(self, text: str) -> List[str]:
        """Extract offer patterns from ad text."""
        offers = []
        text_lower = text.lower()
        
        offer_patterns = [
            (r"free\s+\w+", "free offer"),
            (r"\d+%\s+off", "percentage discount"),
            (r"\$\d+\s+off", "dollar discount"),
            (r"limited time", "urgency"),
            (r"today only", "urgency"),
            (r"special offer", "special"),
            (r"no obligation", "low risk"),
            (r"free estimate", "free estimate"),
            (r"free quote", "free quote"),
            (r"satisfaction guaranteed", "guarantee"),
        ]
        
        for pattern, offer_type in offer_patterns:
            if re.search(pattern, text_lower):
                offers.append(offer_type)
        
        return list(set(offers))
    
    def _extract_trust_signals(self, text: str) -> List[str]:
        """Extract trust signals from ad text."""
        signals = []
        text_lower = text.lower()
        
        trust_patterns = [
            (r"licensed", "licensed"),
            (r"insured", "insured"),
            (r"certified", "certified"),
            (r"\d+\s*years", "experience"),
            (r"family.?owned", "family owned"),
            (r"local", "local"),
            (r"trusted", "trusted"),
            (r"rated", "rated"),
            (r"reviews?", "reviews"),
            (r"guarantee", "guarantee"),
            (r"warranty", "warranty"),
            (r"bbb", "BBB"),
            (r"award", "award"),
        ]
        
        for pattern, signal in trust_patterns:
            if re.search(pattern, text_lower):
                signals.append(signal)
        
        return list(set(signals))
    
    def _extract_emotional_appeals(self, text: str) -> List[str]:
        """Extract emotional appeals from ad text."""
        appeals = []
        text_lower = text.lower()
        
        emotion_patterns = [
            (r"peace of mind", "peace of mind"),
            (r"worry.?free", "worry-free"),
            (r"stress.?free", "stress-free"),
            (r"relax", "relaxation"),
            (r"trust", "trust"),
            (r"safe", "safety"),
            (r"protect", "protection"),
            (r"family", "family"),
            (r"home", "home"),
            (r"emergency", "urgency"),
            (r"fast|quick|same.?day", "speed"),
        ]
        
        for pattern, appeal in emotion_patterns:
            if re.search(pattern, text_lower):
                appeals.append(appeal)
        
        return list(set(appeals))
    
    def search_by_domain(
        self,
        domain: str,
        location: str = "United States",
        max_ads: int = 20,
    ) -> List[AdData]:
        """
        Search for ads by a specific domain/competitor.
        
        Args:
            domain: Domain to search for (e.g., "rotorooter.com")
            location: Location for search
            max_ads: Maximum ads to return
        """
        # Search for the domain name
        return self.search_ads(
            search_term=domain.replace(".com", "").replace("-", " "),
            location=location,
            max_ads=max_ads,
        )
