#!/usr/bin/env python3
"""
Runner script for Ad Intelligence Agent.
Analyzes competitor Facebook ads to extract strategies and patterns.

Usage:
    python run_ad_intel.py -b "plumber" -l "Providence, RI"
    python run_ad_intel.py --business "restaurant" --location "Boston, MA" --max-ads 100
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

from ad_intel import AdIntelAgent, run_ad_analysis


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ad Intelligence Agent - Analyze competitor Facebook ads"
    )
    
    parser.add_argument(
        "--business", "-b",
        type=str,
        required=True,
        help="Business type (e.g., 'plumber', 'restaurant')",
    )
    
    parser.add_argument(
        "--location", "-l",
        type=str,
        required=True,
        help="Location (e.g., 'Providence, RI')",
    )
    
    parser.add_argument(
        "--max-ads",
        type=int,
        default=50,
        help="Maximum ads to analyze (default: 50)",
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
    
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check API configuration and exit",
    )
    
    return parser.parse_args()


def check_config():
    """Check API configuration."""
    print("\n" + "="*50)
    print("API Configuration Status")
    print("="*50)
    
    api_key = os.getenv("APIFY_API_KEY")
    
    if api_key:
        print("[OK] APIFY_API_KEY: Configured")
        print("     -> Facebook Ads scraping enabled")
    else:
        print("[X] APIFY_API_KEY: Not configured")
        print("    -> Set APIFY_API_KEY for Facebook ad scraping")
        print("    -> Get key: https://apify.com (free $5/month)")
    
    print("="*50 + "\n")


def main():
    args = parse_args()
    
    if args.check_config:
        check_config()
        return 0
    
    # Check for API key
    if not os.getenv("APIFY_API_KEY"):
        print("Error: APIFY_API_KEY not set in environment")
        print("Get one at: https://apify.com (free $5/month credits)")
        print("\nRun with --check-config to see configuration status")
        return 1
    
    try:
        analysis = run_ad_analysis(
            business_type=args.business,
            location=args.location,
            max_ads=args.max_ads,
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
