"""
Google Maps competitor location visualizer.

Generates a static map image showing competitor locations in a city.
Uses Google Maps Static API.
"""

import os
import requests
from typing import List, Dict
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_competitor_map(
    city: str,
    competitors: List[Dict[str, str]],
    output_path: str = "output/maps/competitor_map.png"
) -> str:
    """
    Generate a Google Maps image showing competitor locations.
    
    Args:
        city: City name (e.g., "Boston, MA")
        competitors: List of competitor data with 'name' and 'address' keys
        output_path: Where to save the map image
        
    Returns:
        Path to saved map image, or None if failed
    """
    # Try GOOGLE_PLACES_API_KEY (same key works for Static Maps API)
    api_key = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("⚠️ Google API key not found (need GOOGLE_PLACES_API_KEY or GOOGLE_MAPS_API_KEY)")
        return None
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Build Google Maps Static API URL
    base_url = "https://maps.googleapis.com/maps/api/staticmap"
    
    # Parameters
    params = {
        "center": city,
        "zoom": 12,
        "size": "800x600",
        "maptype": "roadmap",
        "key": api_key
    }
    
    # Add markers for each competitor
    markers = []
    for i, comp in enumerate(competitors[:10], 1):  # Limit to 10 for readability
        address = comp.get("address", "")
        name = comp.get("name", f"Competitor {i}")
        
        if address:
            # Use red markers with numbers
            marker = f"color:red|label:{i}|{quote(address)}"
            markers.append(marker)
    
    # Add markers to URL
    if markers:
        params["markers"] = markers
    
    try:
        print(f"🗺️ Generating competitor map for {city}...")
        print(f"   Plotting {len(markers)} competitor locations")
        
        # Make request - use POST if too many markers
        if len(str(params)) > 2000:  # URL too long
            response = requests.post(base_url, data=params, timeout=30)
        else:
            response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            # Save image
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Competitor map saved to: {output_path}")
            return output_path
        else:
            print(f"⚠️ Maps API error {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"⚠️ Map generation failed: {e}")
        return None


def generate_competitor_map_from_research(research_data: Dict, output_path: str = None) -> str:
    """
    Generate competitor map from research pipeline output.
    
    Args:
        research_data: Research results dict with 'city' and competitor info
        output_path: Optional custom output path
        
    Returns:
        Path to map image or None
    """
    if not output_path:
        output_path = "output/maps/competitor_map.png"
    
    city = research_data.get("city", "")
    
    # Extract competitor addresses from local_intel
    competitors = []
    local_intel = research_data.get("local_intel", {})
    
    # Try to get competitor details with addresses
    competitor_details = local_intel.get("competitor_details", [])
    if competitor_details:
        for comp in competitor_details:
            if comp.get("address"):
                competitors.append({
                    "name": comp.get("name", ""),
                    "address": comp.get("address", "")
                })
    
    if not competitors:
        print(f"⚠️ No competitor addresses found for map generation")
        return None
    
    if not city:
        print(f"⚠️ No city provided for map generation")
        return None
    
    return generate_competitor_map(city, competitors, output_path)


if __name__ == "__main__":
    # Test with Boston donut shops
    test_competitors = [
        {"name": "Kane's Donuts", "address": "120 Lincoln Ave, Saugus, MA 01906"},
        {"name": "Union Square Donuts", "address": "10 Bow St, Somerville, MA 02143"},
        {"name": "Blackbird Doughnuts", "address": "492 Tremont St, Boston, MA 02116"},
        {"name": "Donut Villa Diner", "address": "2 Constitution Rd, Boston, MA 02129"},
        {"name": "Twin Donuts", "address": "1414 Beacon St, Brookline, MA 02446"}
    ]
    
    result = generate_competitor_map(
        "Boston, MA",
        test_competitors,
        "output/maps/test_competitor_map.png"
    )
    
    if result:
        print(f"\n✅ Test map generated successfully!")
        print(f"View it at: {result}")
    else:
        print(f"\n❌ Test map generation failed")
