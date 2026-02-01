#!/usr/bin/env python3
"""
Runner script for Review Intelligence Agent.
Analyzes Google Reviews to extract customer voice for ad copy.

Usage:
    # Standalone (with manual competitor list):
    python run_review_intel.py --business "plumber" --location "Providence, RI"
    
    # With JSON file of competitors:
    python run_review_intel.py --competitors competitors.json
    
    # From local_intel output:
    python run_review_intel.py --from-local-intel output/local_intel_20260131_133128.json
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from review_intel import ReviewIntelAgent, run_review_analysis


def parse_args():
    parser = argparse.ArgumentParser(
        description="Review Intelligence Agent - Extract customer voice from Google Reviews"
    )
    
    parser.add_argument(
        "--business", "-b",
        type=str,
        help="Business type (e.g., 'plumber', 'restaurant')",
    )
    
    parser.add_argument(
        "--location", "-l",
        type=str,
        help="Location (e.g., 'Providence, RI')",
    )
    
    parser.add_argument(
        "--competitors", "-c",
        type=str,
        help="JSON file with competitor list",
    )
    
    parser.add_argument(
        "--from-local-intel", "-f",
        type=str,
        help="Use competitors from a local_intel output JSON file (use 'latest' for most recent)",
    )
    
    parser.add_argument(
        "--reviews-per",
        type=int,
        default=20,
        help="Reviews to fetch per competitor (default: 20)",
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="output",
        help="Output directory (default: output)",
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save output file",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON to stdout",
    )
    
    return parser.parse_args()


def find_latest_local_intel(output_dir: str = "output") -> str:
    """Find the most recent local_intel JSON file."""
    output_path = Path(output_dir)
    if not output_path.exists():
        return None
    
    files = list(output_path.glob("local_intel_*.json"))
    if not files:
        return None
    
    # Sort by modification time, most recent first
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return str(files[0])


def load_competitors_from_local_intel(filepath: str) -> tuple:
    """Load competitors from local_intel output."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    search = data.get("search", {}) or data.get("search_input", {})
    business_type = search.get("business_type", "business")
    location = search.get("location", "Unknown")
    
    competitors = []
    
    # Get from competitor data
    for comp in data.get("competitors", []):
        if comp.get("place_id"):
            competitors.append({
                "name": comp.get("name", "Unknown"),
                "place_id": comp.get("place_id"),
                "rating": comp.get("rating"),
            })
    
    return competitors, business_type, location


def load_competitors_from_json(filepath: str) -> list:
    """Load competitors from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    args = parse_args()
    
    # Check for API key
    if not os.getenv("SERPAPI_KEY"):
        print("Error: SERPAPI_KEY not set in environment")
        print("Get one at: https://serpapi.com")
        return 1
    
    # Determine source of competitors
    competitors = []
    business_type = args.business or "business"
    location = args.location or "Unknown"
    
    if args.from_local_intel:
        filepath = args.from_local_intel
        
        # Support "latest" or auto-find if file doesn't exist
        if filepath.lower() == "latest" or not Path(filepath).exists():
            latest = find_latest_local_intel(args.output_dir)
            if latest:
                print(f"Using latest local_intel file: {latest}")
                filepath = latest
            else:
                print(f"Error: No local_intel files found in {args.output_dir}/")
                print("Run local_intel first: python run_local_intel.py -b 'plumber' -l 'Providence, RI'")
                return 1
        
        print(f"Loading competitors from: {filepath}")
        competitors, business_type, location = load_competitors_from_local_intel(filepath)
        print(f"Found {len(competitors)} competitors with place_ids")
        
    elif args.competitors:
        print(f"Loading competitors from: {args.competitors}")
        competitors = load_competitors_from_json(args.competitors)
        
    else:
        print("Error: Provide --from-local-intel or --competitors")
        print("\nExample usage:")
        print("  python run_review_intel.py --from-local-intel latest")
        print("  python run_review_intel.py --from-local-intel output/local_intel_20260131_194058.json")
        print("  python run_review_intel.py --competitors my_competitors.json -b plumber -l 'Providence, RI'")
        return 1
    
    if not competitors:
        print("Error: No competitors with place_ids found")
        return 1
    
    # Override business/location if provided
    if args.business:
        business_type = args.business
    if args.location:
        location = args.location
    
    try:
        analysis = run_review_analysis(
            competitors=competitors,
            business_type=business_type,
            location=location,
            reviews_per_competitor=args.reviews_per,
            save=not args.no_save,
            output_dir=args.output_dir,
        )
        
        if args.json:
            print("\n" + "="*60)
            print("JSON OUTPUT")
            print("="*60)
            print(json.dumps(analysis.to_dict(), indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
