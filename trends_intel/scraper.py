"""
DataForSEO scraper for keyword and trends data.
Uses Basic Auth with login:password.
"""

import os
import base64
import requests
from typing import List, Optional, Dict, Any
from .models import KeywordData, MonthlyVolume, TrendData


# Common location codes
LOCATION_CODES = {
    "US": 2840,
    "United States": 2840,
    "UK": 2826,
    "United Kingdom": 2826,
    "Canada": 2124,
    "Australia": 2036,
    "Germany": 2276,
    "France": 2250,
}


class DataForSEOClient:
    """
    DataForSEO API client.
    
    Uses Basic Authentication with login:password from:
    https://app.dataforseo.com/api-access
    
    Environment variables:
    - DATAFORSEO_LOGIN: Your API login
    - DATAFORSEO_PASSWORD: Your API password
    """
    
    BASE_URL = "https://api.dataforseo.com/v3"
    
    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.login = login or os.getenv("DATAFORSEO_LOGIN")
        self.password = password or os.getenv("DATAFORSEO_PASSWORD")
        
        if not self.login or not self.password:
            raise ValueError(
                "DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD not set. "
                "Get credentials at https://app.dataforseo.com/api-access"
            )
        
        # Create auth header
        credentials = f"{self.login}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }
    
    def get_search_volume(
        self,
        keywords: List[str],
        location: str = "United States",
        language: str = "en",
    ) -> List[KeywordData]:
        """
        Get search volume data for keywords.
        
        Args:
            keywords: List of keywords (max 1000)
            location: Location name or code
            language: Language code (e.g., "en")
        
        Returns:
            List of KeywordData with search volumes
        """
        results: List[KeywordData] = []
        
        # Get location code
        location_code = LOCATION_CODES.get(location, 2840)
        if isinstance(location, int):
            location_code = location
        
        print(f"    Fetching search volume for {len(keywords)} keywords...")
        
        try:
            payload = [{
                "keywords": keywords[:1000],  # API limit
                "location_code": location_code,
                "language_code": language,
            }]
            
            response = requests.post(
                f"{self.BASE_URL}/keywords_data/google_ads/search_volume/live",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            
            if response.status_code == 401:
                print("    Error: Invalid credentials")
                return results
            
            if response.status_code != 200:
                print(f"    Error {response.status_code}: {response.text[:200]}")
                return results
            
            data = response.json()
            
            # Check for errors
            if data.get("status_code") != 20000:
                print(f"    API error: {data.get('status_message')}")
                return results
            
            # Parse results
            tasks = data.get("tasks", [])
            if tasks and tasks[0].get("result"):
                for item in tasks[0]["result"]:
                    kw_data = self._parse_keyword_data(item)
                    if kw_data:
                        results.append(kw_data)
                
                print(f"    Got data for {len(results)} keywords")
                cost = data.get("cost", 0)
                print(f"    Cost: ${cost:.4f}")
            else:
                print("    No results returned")
                
        except requests.RequestException as e:
            print(f"    Request error: {e}")
        except Exception as e:
            print(f"    Error: {e}")
        
        return results
    
    def get_trends(
        self,
        keywords: List[str],
        location: str = "United States",
        time_range: str = "past_12_months",
    ) -> List[TrendData]:
        """
        Get Google Trends data for keywords.
        
        Args:
            keywords: List of keywords (max 5)
            location: Location name
            time_range: Time range (past_12_months, past_5_years, etc.)
        
        Returns:
            List of TrendData with interest over time
        """
        results: List[TrendData] = []
        
        print(f"    Fetching Google Trends for {len(keywords[:5])} keywords...")
        
        try:
            payload = [{
                "keywords": keywords[:5],  # API limit is 5
                "location_name": location,
                "time_range": time_range,
                "item_types": ["google_trends_graph", "google_trends_queries_list"],
            }]
            
            response = requests.post(
                f"{self.BASE_URL}/keywords_data/google_trends/explore/live",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            
            if response.status_code != 200:
                print(f"    Error {response.status_code}: {response.text[:200]}")
                return results
            
            data = response.json()
            
            if data.get("status_code") != 20000:
                print(f"    API error: {data.get('status_message')}")
                return results
            
            # Parse results
            tasks = data.get("tasks", [])
            if tasks and tasks[0].get("result"):
                result = tasks[0]["result"][0]
                items = result.get("items", [])
                
                # Find graph data
                for item in items:
                    if item.get("type") == "google_trends_graph":
                        trend = self._parse_trend_data(item, keywords)
                        if trend:
                            results.append(trend)
                
                print(f"    Got trends data")
                cost = data.get("cost", 0)
                print(f"    Cost: ${cost:.4f}")
            else:
                print("    No trends data returned")
                
        except requests.RequestException as e:
            print(f"    Request error: {e}")
        except Exception as e:
            print(f"    Error: {e}")
        
        return results
    
    def get_related_queries(
        self,
        keyword: str,
        location: str = "United States",
    ) -> Dict[str, List[str]]:
        """
        Get related and rising queries for a keyword.
        
        Returns:
            Dict with "top" and "rising" query lists
        """
        result = {"top": [], "rising": []}
        
        try:
            payload = [{
                "keywords": [keyword],
                "location_name": location,
                "time_range": "past_12_months",
                "item_types": ["google_trends_queries_list"],
            }]
            
            response = requests.post(
                f"{self.BASE_URL}/keywords_data/google_trends/explore/live",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            
            if response.status_code != 200:
                return result
            
            data = response.json()
            
            if data.get("status_code") != 20000:
                return result
            
            tasks = data.get("tasks", [])
            if tasks and tasks[0].get("result"):
                items = tasks[0]["result"][0].get("items", [])
                
                for item in items:
                    if item.get("type") == "google_trends_queries_list":
                        queries_data = item.get("data", {})
                        
                        # Top queries
                        for q in queries_data.get("top", []):
                            if q.get("query"):
                                result["top"].append(q["query"])
                        
                        # Rising queries
                        for q in queries_data.get("rising", []):
                            if q.get("query"):
                                result["rising"].append(q["query"])
                
        except Exception:
            pass
        
        return result
    
    def _parse_keyword_data(self, item: Dict[str, Any]) -> Optional[KeywordData]:
        """Parse keyword data from API response."""
        try:
            monthly = []
            for m in item.get("monthly_searches", []):
                if m.get("search_volume") is not None:
                    monthly.append(MonthlyVolume(
                        year=m.get("year", 0),
                        month=m.get("month", 0),
                        search_volume=m.get("search_volume", 0),
                    ))
            
            return KeywordData(
                keyword=item.get("keyword", ""),
                search_volume=item.get("search_volume") or 0,
                competition=item.get("competition") or "UNKNOWN",
                competition_index=item.get("competition_index") or 0,
                cpc=item.get("cpc") or 0.0,
                low_bid=item.get("low_top_of_page_bid") or 0.0,
                high_bid=item.get("high_top_of_page_bid") or 0.0,
                monthly_searches=monthly,
            )
            
        except Exception as e:
            print(f"      Error parsing keyword data: {e}")
            return None
    
    def _parse_trend_data(
        self,
        item: Dict[str, Any],
        keywords: List[str],
    ) -> Optional[TrendData]:
        """Parse trend data from API response."""
        try:
            data_points = []
            for point in item.get("data", []):
                values = point.get("values", [])
                value = values[0] if values else 0
                
                data_points.append({
                    "date_from": point.get("date_from"),
                    "date_to": point.get("date_to"),
                    "value": value if value is not None else 0,
                })
            
            # Calculate average
            values = [p["value"] for p in data_points if p["value"]]
            avg = sum(values) / len(values) if values else 0
            
            # Use first keyword as label
            keyword = keywords[0] if keywords else "unknown"
            
            return TrendData(
                keyword=keyword,
                data_points=data_points,
                average=round(avg, 2),
            )
            
        except Exception as e:
            print(f"      Error parsing trend data: {e}")
            return None
