"""
Facebook Ads Library scraper using Apify.
"""

import os
import re
import time
import requests
from typing import List, Optional, Dict, Any
from .models import AdData, CompetitorAds


class FacebookAdsScraper:
    """
    Scrapes Facebook Ads Library using official Apify actor.
    
    Based on: https://apify.com/apify/facebook-ads-scraper
    Pricing: $3.40 - $5.80 per 1,000 ads
    """
    
    # Official Apify Facebook Ads Scraper
    # Note: In API calls, "/" becomes "~"
    ACTOR_ID = "apify~facebook-ads-scraper"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("APIFY_API_KEY")
        if not self.api_key:
            raise ValueError("APIFY_API_KEY not set. Get one at https://apify.com")
        
        self.base_url = "https://api.apify.com/v2"
    
    def _build_ad_library_url(
        self,
        search_term: str,
        country: str = "US",
        active_only: bool = True,
        media_type: str = "all",
    ) -> str:
        """
        Build Facebook Ad Library URL from search parameters.
        
        Based on official docs format:
        https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=keyword&search_type=keyword_unordered
        """
        from urllib.parse import quote
        
        active_status = "active" if active_only else "all"
        query = quote(search_term)
        
        url = (
            f"https://www.facebook.com/ads/library/"
            f"?active_status={active_status}"
            f"&ad_type=all"
            f"&country={country}"
            f"&q={query}"
            f"&search_type=keyword_unordered"
        )
        
        if media_type != "all":
            url += f"&media_type={media_type}"
        
        return url
    
    def search_ads(
        self,
        search_term: str,
        country: str = "US",
        max_ads: int = 50,
        ad_type: str = "all",  # all, image, video
        active_only: bool = True,
    ) -> List[AdData]:
        """
        Search Facebook Ads Library for ads.
        
        Uses official apify/facebook-ads-scraper actor.
        Input: Facebook page URLs or Meta Ad Library URLs
        
        Args:
            search_term: Search query (e.g., "plumber Providence")
            country: Country code (US, GB, CA, etc.)
            max_ads: Maximum ads to fetch
            ad_type: Filter by ad type
            active_only: Only fetch active ads
        
        Returns:
            List of AdData
        """
        ads: List[AdData] = []
        
        # Build the Ad Library URL with search parameters
        ad_library_url = self._build_ad_library_url(
            search_term=search_term,
            country=country,
            active_only=active_only,
            media_type=ad_type,
        )
        
        print(f"    Using official apify/facebook-ads-scraper...")
        print(f"    URL: {ad_library_url[:80]}...")
        
        try:
            # Official input format: startUrls is required
            # Format: array of objects with "url" key
            run_input = {
                "startUrls": [{"url": ad_library_url}],
            }
            
            response = requests.post(
                f"{self.base_url}/acts/{self.ACTOR_ID}/run-sync-get-dataset-items",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=run_input,
                timeout=300,  # 5 minute timeout - scraper can be slow
            )
            
            if response.status_code == 402:
                print("    Insufficient Apify credits.")
                print("    Get credits at: https://apify.com")
                return ads
            
            if response.status_code == 401:
                print("    Invalid API key. Check APIFY_API_KEY in .env")
                return ads
            
            if response.status_code >= 400:
                print(f"    Error {response.status_code}: {response.text[:200]}")
                return ads
            
            results = response.json()
            
            if results:
                print(f"    Received {len(results)} results from API")
                
                for item in results:
                    ad = self._parse_official_ad(item)
                    if ad:
                        ads.append(ad)
                        if len(ads) >= max_ads:
                            break
                
                print(f"    Parsed {len(ads)} ads successfully")
            else:
                print("    No ads found for this search")
                
        except requests.exceptions.Timeout:
            print("    Request timed out. Try a more specific search.")
        except requests.exceptions.RequestException as e:
            print(f"    Request error: {e}")
        except Exception as e:
            print(f"    Error: {e}")
        
        return ads
    
    def _parse_official_ad(self, item: Dict[str, Any]) -> Optional[AdData]:
        """
        Parse ad from official apify/facebook-ads-scraper output.
        
        Output format from docs:
        - pageInfo: page details
        - snapshot: ad content (body, images, videos, ctaText, etc.)
        - pageName, pageId
        - publisherPlatform: ["FACEBOOK", "INSTAGRAM", etc.]
        - isActive, startDate, endDate
        """
        try:
            # Get basic info
            ad_id = item.get("adArchiveID") or item.get("adArchiveId") or ""
            page_name = item.get("pageName") or "Unknown"
            page_id = item.get("pageId") or item.get("pageID")
            
            # Get snapshot (ad content)
            snapshot = item.get("snapshot", {})
            
            # Ad text
            ad_text = ""
            if snapshot.get("body"):
                ad_text = snapshot["body"].get("text", "")
            
            # Headline/title
            headline = snapshot.get("title")
            
            # CTA
            cta_text = snapshot.get("ctaText")
            cta_type = snapshot.get("ctaType")
            call_to_action = cta_text or cta_type
            
            # Link URL
            link_url = snapshot.get("linkUrl")
            
            # Media type and content
            display_format = snapshot.get("displayFormat", "").lower()
            
            image_urls = []
            video_url = None
            
            if display_format == "video" or snapshot.get("videos"):
                media_type = "video"
                videos = snapshot.get("videos", [])
                if videos:
                    video_url = videos[0].get("videoHdUrl") or videos[0].get("videoSdUrl")
            elif display_format == "carousel" or len(snapshot.get("cards", [])) > 1:
                media_type = "carousel"
                for card in snapshot.get("cards", []):
                    if card.get("originalImageUrl"):
                        image_urls.append(card["originalImageUrl"])
            else:
                media_type = "image"
                images = snapshot.get("images", [])
                for img in images:
                    if img.get("originalImageUrl"):
                        image_urls.append(img["originalImageUrl"])
                    elif img.get("resizedImageUrl"):
                        image_urls.append(img["resizedImageUrl"])
            
            # Status and dates
            is_active = item.get("isActive", True)
            start_date = item.get("startDateFormatted")
            end_date = item.get("endDateFormatted")
            
            # Publisher platforms
            platforms = item.get("publisherPlatform", [])
            
            ad = AdData(
                ad_id=str(ad_id),
                page_name=page_name,
                page_id=str(page_id) if page_id else None,
                ad_text=ad_text,
                headline=headline,
                description=snapshot.get("linkDescription"),
                call_to_action=call_to_action,
                link_url=link_url,
                media_type=media_type,
                image_urls=image_urls,
                video_url=video_url,
                is_active=is_active,
                start_date=start_date,
                end_date=end_date,
            )
            
            # Extract patterns from ad text
            if ad_text:
                ad.hooks = self._extract_hooks(ad_text)
                ad.offers = self._extract_offers(ad_text)
                ad.trust_signals = self._extract_trust_signals(ad_text)
                ad.emotional_appeals = self._extract_emotional_appeals(ad_text)
            
            return ad
            
        except Exception as e:
            print(f"    Error parsing ad: {e}")
            return None
    
    def _parse_ad(self, item: Dict[str, Any]) -> Optional[AdData]:
        """Parse Apify result into AdData."""
        try:
            # Different actors have different output formats
            ad_id = item.get("id") or item.get("ad_id") or item.get("adArchiveID", "")
            page_name = item.get("page_name") or item.get("pageName") or item.get("advertiser_name", "Unknown")
            
            # Get ad text
            ad_text = ""
            if item.get("ad_creative_body"):
                ad_text = item["ad_creative_body"]
            elif item.get("body"):
                ad_text = item["body"]
            elif item.get("ad_text"):
                ad_text = item["ad_text"]
            elif item.get("snapshot", {}).get("body", {}).get("text"):
                ad_text = item["snapshot"]["body"]["text"]
            
            # Get headline
            headline = item.get("ad_creative_title") or item.get("title") or item.get("headline")
            
            # Get CTA
            cta = item.get("call_to_action_type") or item.get("cta") or item.get("callToActionType")
            
            # Get link
            link_url = item.get("ad_creative_link_url") or item.get("link_url") or item.get("landingPageUrl")
            
            # Determine media type
            media_type = "unknown"
            image_urls = []
            video_url = None
            
            if item.get("ad_creative_video") or item.get("video_url") or item.get("hasVideo"):
                media_type = "video"
                video_url = item.get("video_url") or item.get("ad_creative_video", {}).get("url")
            elif item.get("ad_creative_image") or item.get("image_url"):
                media_type = "image"
                img = item.get("image_url") or item.get("ad_creative_image", {}).get("url")
                if img:
                    image_urls = [img]
            elif item.get("images"):
                media_type = "carousel" if len(item["images"]) > 1 else "image"
                image_urls = item["images"]
            
            # Get dates
            start_date = item.get("ad_delivery_start_time") or item.get("startDate")
            is_active = item.get("is_active", True) or item.get("status") == "ACTIVE"
            
            ad = AdData(
                ad_id=str(ad_id),
                page_name=page_name,
                page_id=item.get("page_id") or item.get("pageId"),
                ad_text=ad_text,
                headline=headline,
                call_to_action=cta,
                link_url=link_url,
                media_type=media_type,
                image_urls=image_urls,
                video_url=video_url,
                is_active=is_active,
                start_date=start_date,
            )
            
            # Extract patterns from ad text
            if ad_text:
                ad.hooks = self._extract_hooks(ad_text)
                ad.offers = self._extract_offers(ad_text)
                ad.trust_signals = self._extract_trust_signals(ad_text)
                ad.emotional_appeals = self._extract_emotional_appeals(ad_text)
            
            return ad
            
        except Exception as e:
            print(f"    Error parsing ad: {e}")
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
    
    def search_by_page(
        self,
        page_url: str,
        max_ads: int = 20,
    ) -> List[AdData]:
        """
        Search ads for a specific Facebook page.
        
        Args:
            page_url: Facebook page URL (e.g., "https://www.facebook.com/nike/")
                      or page name (e.g., "nike")
        """
        # Build proper URL if just page name provided
        if not page_url.startswith("http"):
            page_url = f"https://www.facebook.com/{page_url}/"
        
        try:
            # Official actor accepts page URLs via startUrls
            response = requests.post(
                f"{self.base_url}/acts/{self.ACTOR_ID}/run-sync-get-dataset-items",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "startUrls": [{"url": page_url}],
                },
                timeout=300,
            )
            
            if response.status_code >= 400:
                print(f"    Error {response.status_code}")
                return []
            
            ads = []
            for item in response.json():
                ad = self._parse_official_ad(item)
                if ad:
                    ads.append(ad)
                    if len(ads) >= max_ads:
                        break
            
            return ads
            
        except Exception as e:
            print(f"    Error fetching ads for page {page_url}: {e}")
            return []
