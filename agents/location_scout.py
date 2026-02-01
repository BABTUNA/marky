"""
Location Scout Agent

Finds potential filming locations using Google Places API.
"""

import os

import requests


class LocationScoutAgent:
    """Finds filming locations using Google Places API."""

    def __init__(self):
        self.base_url = "https://maps.googleapis.com/maps/api/place"

    async def run(
        self,
        product: str,
        industry: str,
        duration: int,
        tone: str,
        city: str,
        previous_results: dict,
    ) -> dict:
        """
        Find potential filming locations.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration (unused)
            tone: Desired tone (unused)
            city: City to search in
            previous_results: Results from previous agents

        Returns:
            dict with location suggestions
        """

        api_key = os.getenv("GOOGLE_PLACES_API_KEY")

        if not api_key:
            return {
                "error": "GOOGLE_PLACES_API_KEY not set",
                "fallback_suggestions": self._get_fallback_suggestions(industry, city),
            }

        if not city:
            return {
                "error": "No city specified",
                "fallback_suggestions": self._get_fallback_suggestions(
                    industry, "your area"
                ),
            }

        # Determine what locations to search for based on industry
        search_queries = self._get_search_queries(industry, product, city)

        try:
            all_locations = []

            for query in search_queries[:3]:  # Limit API calls
                response = requests.get(
                    f"{self.base_url}/textsearch/json",
                    params={"query": query, "key": api_key},
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])[:3]

                    for place in results:
                        location = {
                            "name": place.get("name", "Unknown"),
                            "address": place.get("formatted_address", ""),
                            "rating": place.get("rating", "N/A"),
                            "type": query.split(" in ")[0]
                            if " in " in query
                            else "location",
                            "price_level": self._price_level_to_estimate(
                                place.get("price_level")
                            ),
                            "place_id": place.get("place_id", ""),
                        }

                        # Avoid duplicates
                        if location["name"] not in [l["name"] for l in all_locations]:
                            all_locations.append(location)

            return {
                "locations": all_locations[:6],
                "city": city,
                "search_queries": search_queries,
                "tips": self._get_location_tips(industry),
            }

        except Exception as e:
            return {
                "error": str(e),
                "fallback_suggestions": self._get_fallback_suggestions(industry, city),
            }

    def _get_search_queries(self, industry: str, product: str, city: str) -> list:
        """Generate search queries based on industry."""

        industry_queries = {
            "food": [
                f"outdoor dining area {city}",
                f"food market {city}",
                f"park with food trucks {city}",
            ],
            "fitness": [
                f"gym with natural light {city}",
                f"outdoor fitness area {city}",
                f"park running trail {city}",
            ],
            "tech": [
                f"modern office space {city}",
                f"coworking space {city}",
                f"coffee shop with wifi {city}",
            ],
            "services": [
                f"professional office {city}",
                f"business center {city}",
                f"residential neighborhood {city}",
            ],
            "construction": [
                f"residential area {city}",
                f"construction supply store {city}",
                f"home improvement store {city}",
            ],
            "beauty": [f"salon {city}", f"spa {city}", f"photo studio {city}"],
            "retail": [
                f"shopping area {city}",
                f"boutique store {city}",
                f"downtown shopping {city}",
            ],
        }

        base_queries = industry_queries.get(
            industry,
            [f"event venue {city}", f"photo studio {city}", f"outdoor location {city}"],
        )

        # Add product-specific query
        base_queries.insert(0, f"{product} location {city}")

        return base_queries

    def _price_level_to_estimate(self, price_level) -> str:
        """Convert Google price level to rental estimate."""
        if price_level is None:
            return "Contact for pricing"

        estimates = {
            0: "Free/Low cost ($0-50/hr)",
            1: "Budget ($50-100/hr)",
            2: "Moderate ($100-200/hr)",
            3: "Premium ($200-400/hr)",
            4: "Luxury ($400+/hr)",
        }

        return estimates.get(price_level, "Contact for pricing")

    def _get_location_tips(self, industry: str) -> list:
        """Get filming location tips."""

        general_tips = [
            "Always get written permission before filming",
            "Check if location requires permits or insurance",
            "Scout locations at the same time of day you plan to film",
            "Consider parking and power outlet availability",
        ]

        industry_tips = {
            "food": [
                "Ensure kitchen access for food shots",
                "Check health permit requirements",
            ],
            "fitness": [
                "Verify if gym allows filming",
                "Consider outdoor locations for free",
            ],
            "tech": [
                "Look for clean, modern backgrounds",
                "Avoid branded items in frame",
            ],
        }

        return general_tips + industry_tips.get(industry, [])

    def _get_fallback_suggestions(self, industry: str, city: str) -> list:
        """Provide suggestions without API."""

        suggestions = {
            "food": [
                {"type": "Your own kitchen/restaurant", "note": "Free, authentic"},
                {
                    "type": "Local farmer's market",
                    "note": "Great atmosphere, may need permit",
                },
                {"type": "Public park", "note": "Free, natural lighting"},
            ],
            "fitness": [
                {"type": "Local gym", "note": "Ask about off-hours filming"},
                {"type": "Public park", "note": "Free, natural setting"},
                {"type": "Beach/trail", "note": "Free, cinematic"},
            ],
            "tech": [
                {"type": "Coworking space", "note": "$50-200/hr typically"},
                {"type": "Modern coffee shop", "note": "May allow during slow hours"},
                {"type": "Home office", "note": "Free, controlled environment"},
            ],
        }

        return suggestions.get(
            industry,
            [
                {"type": "Your business location", "note": "Free, authentic"},
                {"type": "Public spaces", "note": "Free, may need permit"},
                {
                    "type": "Local studio rental",
                    "note": "Search 'photo studio rental' + your city",
                },
            ],
        )
