"""
Google Maps competitor location visualizer.

Generates a static map image showing competitor locations in a city.
Uses Google Maps Static API. Adds legend, title, and border overlay.
"""

import os
import requests
from typing import List, Dict
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _add_legend_and_border(
    image_path: str,
    city: str,
    competitors: List[Dict[str, str]],
    border_px: int = 3,
    legend_height: int = 80,
) -> None:
    """
    Add title bar, legend, and border to the map image using Pillow.
    Modifies the file in place.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return  # Skip if Pillow not available

    img = Image.open(image_path).convert("RGB")
    w, h = img.size

    # New image: map + title bar + legend + border padding
    pad = border_px
    title_h = 36
    new_h = h + title_h + legend_height + 2 * pad
    new_w = w + 2 * pad

    out = Image.new("RGB", (new_w, new_h), color=(240, 240, 240))
    # Layout: top margin | title bar | map | legend | bottom margin
    out.paste(img, (pad, pad + title_h))

    draw = ImageDraw.Draw(out)

    # Try system font, fallback to default
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    font_lg = font_sm = ImageFont.load_default()
    for p in font_paths:
        if os.path.exists(p):
            try:
                font_lg = ImageFont.truetype(p, 16)
                font_sm = ImageFont.truetype(p, 12)
                break
            except Exception:
                continue

    # Title bar (below top margin)
    draw.rectangle(
        [pad, pad, new_w - pad, pad + title_h],
        fill=(50, 50, 55),
        outline=(80, 80, 90),
    )
    draw.text(
        (new_w // 2, pad + title_h // 2),
        f"Competitor Locations — {city}",
        fill="white",
        font=font_lg,
        anchor="mm",
    )

    # Legend box (below map)
    leg_y = pad + title_h + h + 8
    leg_box = [pad, leg_y, new_w - pad, new_h - pad]
    draw.rectangle(leg_box, fill="white", outline=(180, 180, 185), width=1)

    legend_text = f"Red markers (1–{min(len(competitors), 10)}) = competitor locations"
    draw.text((pad + 12, leg_y + 12), legend_text, fill=(60, 60, 65), font=font_sm)

    # Competitor list (truncated if many)
    names = [c.get("name", "")[:30] for c in competitors[:5]]
    if names:
        list_text = " • ".join(f"{i+1}: {n}" for i, n in enumerate(names))
        if len(competitors) > 5:
            list_text += f" ... +{len(competitors) - 5} more"
        draw.text((pad + 12, leg_y + 32), list_text, fill=(90, 90, 95), font=font_sm)

    # Border around entire image
    draw.rectangle([0, 0, new_w - 1, new_h - 1], outline=(160, 160, 165), width=border_px)

    out.save(image_path, "PNG", optimize=True)


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
            # Check if response is an error image (contains "staticmaperror" text)
            # Google returns 200 but with an error image when API is misconfigured
            content_type = response.headers.get("Content-Type", "")
            if len(response.content) < 5000 and b"error" in response.content.lower():
                print("⚠️ Static Maps API returned error image. Check:")
                print("   1. Enable 'Maps Static API' in Google Cloud Console")
                print("   2. Ensure billing is enabled on the project")
                print("   3. Check API key restrictions allow Static Maps")
                return None
            
            # Save raw map
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Check for error watermark in the saved image
            try:
                from PIL import Image
                img = Image.open(output_path)
                # Error images are typically smaller or have specific patterns
                # The "g.co/staticmaperror" watermark appears in the top-right
                # We can't easily detect this without OCR, so just warn
            except Exception:
                pass
            
            # Add legend, title, and border
            _add_legend_and_border(output_path, city, competitors[:10])
            print(f"✅ Competitor map saved to: {output_path}")
            print(f"   ⚠️ If you see 'g.co/staticmaperror', enable Static Maps API in GCP Console")
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
