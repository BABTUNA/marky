#!/usr/bin/env python3
"""
Runner script for Related Questions Intelligence Agent.
Fetches Google "People also ask" questions via SerpAPI.

Usage:
    python run_related_questions_intel.py -b "plumber" -l "Providence, RI"
    python run_related_questions_intel.py -b "electrician" -l "Boston, MA" --queries "emergency electrician Boston"
"""

import argparse
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from related_questions_intel import run_related_questions_analysis


def parse_args():
    parser = argparse.ArgumentParser(
        description="Related Questions Intelligence Agent - People also ask via SerpAPI"
    )
    parser.add_argument("-b", "--business-type", required=True, help="Business type (e.g., plumber)")
    parser.add_argument("-l", "--location", required=True, help="Location (e.g., Providence, RI)")
    parser.add_argument(
        "--queries",
        nargs="+",
        default=None,
        help="Optional seed queries (default: business_type location, best ..., near me)",
    )
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to file")
    parser.add_argument("--json", action="store_true", help="Print full JSON")
    parser.add_argument("--check-config", action="store_true", help="Check API config and exit")
    return parser.parse_args()


def check_config():
    print("\n" + "=" * 50)
    print("API Configuration Status")
    print("=" * 50)
    key = os.getenv("SERPAPI_KEY")
    if key:
        print("[OK] SERPAPI_KEY: Configured")
        print("     -> Related questions (People also ask) enabled")
    else:
        print("[X] SERPAPI_KEY: Not configured")
        print("    -> Get key: https://serpapi.com (100 free/month)")
    print("=" * 50 + "\n")


def main():
    args = parse_args()
    if args.check_config:
        check_config()
        return 0
    if not os.getenv("SERPAPI_KEY"):
        print("Error: SERPAPI_KEY not set. Get one at https://serpapi.com")
        return 1
    try:
        analysis = run_related_questions_analysis(
            business_type=args.business_type,
            location=args.location,
            seed_queries=args.queries,
            save=not args.no_save,
            output_dir=args.output_dir,
        )
        if args.json:
            print("\n" + "=" * 60)
            print("JSON OUTPUT")
            print("=" * 60)
            print(json.dumps(analysis.to_dict(), indent=2))
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
