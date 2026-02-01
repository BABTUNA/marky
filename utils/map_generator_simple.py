"""
Simple competitor location map generator using matplotlib.

Creates a visual map showing competitor locations without needing Maps API.
Uses a scatter plot overlay on city coordinates.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Dict
import requests


def geocode_address(address: str, api_key: str) -> tuple:
    """Get lat/long from address using Google Geocoding API."""
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        response = requests.get(url, params={"address": address, "key": api_key}, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return (location['lat'], location['lng'])
    except Exception as e:
        print(f"⚠️ Geocoding error for {address}: {e}")
    
    return None


def generate_simple_competitor_map(
    city: str,
    competitors: List[Dict[str, str]],
    output_path: str = "output/maps/competitor_map.png"
) -> str:
    """
    Generate a simple competitor map using matplotlib.
    
    Args:
        city: City name
        competitors: List with 'name' and 'address' 
        output_path: Where to save
        
    Returns:
        Path to map image or None
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"🗺️ Generating competitor map for {city}...")
    print(f"   Analyzing {len(competitors)} competitors...")
    
    # Get coordinates for each competitor
    locations = []
    names = []
    
    for comp in competitors[:10]:  # Limit to 10
        address = comp.get("address", "")
        name = comp.get("name", "Competitor")
        
        if address and api_key:
            coords = geocode_address(address, api_key)
            if coords:
                locations.append(coords)
                names.append(name)
    
    if not locations:
        print("⚠️ No valid coordinates found")
        return None
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Extract lat/long
    lats = [loc[0] for loc in locations]
    longs = [loc[1] for loc in locations]
    
    # Plot competitors
    ax.scatter(longs, lats, c='red', s=200, alpha=0.7, edgecolors='darkred', linewidth=2, zorder=5)
    
    # Add labels
    for i, (lat, long, name) in enumerate(zip(lats, longs, names), 1):
        ax.annotate(f'{i}', xy=(long, lat), xytext=(0, 0),
                   textcoords='offset points', ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white', zorder=6)
        
        # Add name below marker
        ax.annotate(name, xy=(long, lat), xytext=(0, -25),
                   textcoords='offset points', ha='center', va='top',
                   fontsize=8, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Style the plot
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title(f'Competitor Locations in {city}', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#f0f0f0')
    
    # Add legend
    red_patch = mpatches.Patch(color='red', label=f'{len(locations)} Competitors')
    ax.legend(handles=[red_patch], loc='upper right', fontsize=10)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Competitor map saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test
    test_competitors = [
        {"name": "Kane's Donuts", "address": "120 Lincoln Ave, Saugus, MA 01906"},
        {"name": "Union Square Donuts", "address": "10 Bow St, Somerville, MA 02143"},
        {"name": "Blackbird Doughnuts", "address": "492 Tremont St, Boston, MA 02116"},
        {"name": "Donut Villa Diner", "address": "2 Constitution Rd, Boston, MA 02129"},
        {"name": "Twin Donuts", "address": "1414 Beacon St, Brookline, MA 02446"}
    ]
    
    result = generate_simple_competitor_map(
        "Boston, MA",
        test_competitors,
        "output/maps/competitor_map.png"
    )
    
    if result:
        print(f"\n✅ Test map generated!")
        print(f"View: {result}")
