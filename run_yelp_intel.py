#!/usr/bin/env python3
"""
Runner script for Yelp Intelligence Agent.
Analyzes Yelp reviews to extract customer insights for advertising.

Usage:
    python run_yelp_intel.py -b "plumber" -l "Providence, RI"
    python run_yelp_intel.py --business "restaurant" --location "Boston, MA" --max-businesses 10
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

from yelp_intel import run_yelp_analysis


def parse_args():
    parser = argparse.ArgumentParser(
        description="Yelp Intelligence Agent - Extract customer insights from Yelp reviews"
    )
    
    parser.add_argument(
        "-b", "--business",
        required=True,
        help="Business type to analyze (e.g., 'plumber', 'restaurant', 'dentist')"
    )
    
    parser.add_argument(
        "-l", "--location",
        required=True,
        help="Location to search (e.g., 'Providence, RI', 'Boston, MA')"
    )
    
    parser.add_argument(
        "-m", "--max-businesses",
        type=int,
        default=5,
        help="Maximum number of businesses to analyze (default: 5)"
    )
    
    parser.add_argument(
        "--reviews-per-business",
        type=int,
        default=20,
        help="Reviews to fetch per business (default: 20)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for reports (default: output)"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full JSON results"
    )
    
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check API configuration and exit"
    )
    
    return parser.parse_args()


def check_config():
    """Check API configuration."""
    print("\n" + "="*50)
    print("API Configuration Status")
    print("="*50)
    
    api_key = os.getenv("SERPAPI_KEY")
    
    if api_key:
        print("[OK] SERPAPI_KEY: Configured")
        print("     -> Yelp Search and Reviews enabled")
        print("     -> Uses same key as local_intel and ad_intel")
    else:
        print("[X] SERPAPI_KEY: Not configured")
        print("    -> Set SERPAPI_KEY for Yelp scraping")
        print("    -> Get key: https://serpapi.com (100 free/month)")
    
    print("="*50 + "\n")


def main():
    args = parse_args()
    
    if args.check_config:
        check_config()
        return 0
    
    # Check for API key
    if not os.getenv("SERPAPI_KEY"):
        print("Error: SERPAPI_KEY not set in environment")
        print("Get one at: https://serpapi.com (100 free searches/month)")
        print("\nRun with --check-config to see configuration status")
        return 1
    
    try:
        analysis = run_yelp_analysis(
            business_type=args.business,
            location=args.location,
            max_businesses=args.max_businesses,
            reviews_per_business=args.reviews_per_business,
            save=not args.no_save,
            output_dir=args.output_dir,
        )
        
        if args.json:
            print("\n" + "="*60)
            print("JSON OUTPUT")
            print("="*60)
            print(json.dumps(analysis.to_dict(), indent=2))
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
