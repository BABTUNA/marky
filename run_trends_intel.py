#!/usr/bin/env python3
"""
Runner script for Trends Intelligence Agent.
Uses DataForSEO API for keyword trends and seasonal insights.

Usage:
    python run_trends_intel.py -k "plumber" "plumbing services" "emergency plumber"
    python run_trends_intel.py --keywords "HVAC repair" --location "United States"
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

from trends_intel import run_trends_analysis


def parse_args():
    parser = argparse.ArgumentParser(
        description="Trends Intelligence Agent - Seasonal keyword analysis using DataForSEO"
    )
    
    parser.add_argument(
        "-k", "--keywords",
        nargs="+",
        required=True,
        help="Keywords to analyze (space-separated, use quotes for phrases)"
    )
    
    parser.add_argument(
        "-l", "--location",
        default="United States",
        help="Location for search data (default: United States)"
    )
    
    parser.add_argument(
        "--no-related",
        action="store_true",
        help="Skip fetching related/rising queries"
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
    
    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    
    if login and password:
        print("[OK] DATAFORSEO_LOGIN: Configured")
        print("[OK] DATAFORSEO_PASSWORD: Configured")
        print("     -> Keyword search volume enabled")
        print("     -> Google Trends data enabled")
        print("     -> Related queries enabled")
    else:
        if not login:
            print("[X] DATAFORSEO_LOGIN: Not configured")
        if not password:
            print("[X] DATAFORSEO_PASSWORD: Not configured")
        print("")
        print("To configure:")
        print("1. Create account at https://app.dataforseo.com/register")
        print("2. Get API credentials at https://app.dataforseo.com/api-access")
        print("3. Add to .env file:")
        print("   DATAFORSEO_LOGIN=your_login")
        print("   DATAFORSEO_PASSWORD=your_api_password")
    
    print("="*50 + "\n")


def main():
    args = parse_args()
    
    if args.check_config:
        check_config()
        return 0
    
    # Check for API credentials
    if not os.getenv("DATAFORSEO_LOGIN") or not os.getenv("DATAFORSEO_PASSWORD"):
        print("Error: DataForSEO credentials not set")
        print("Get credentials at: https://app.dataforseo.com/api-access")
        print("\nRun with --check-config to see configuration status")
        return 1
    
    try:
        analysis = run_trends_analysis(
            keywords=args.keywords,
            location=args.location,
            include_related=not args.no_related,
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
