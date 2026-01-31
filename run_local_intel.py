#!/usr/bin/env python3
"""
Local Competitor Intelligence Agent - CLI Entry Point

Analyze local competitors and generate advertising differentiation.

Usage:
    python run_local_intel.py --business "plumber" --location "Providence, RI"
    python run_local_intel.py --interactive
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from local_intel.agent import LocalIntelAgent, run_analysis
from local_intel.config import AppConfig


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Local Competitor Intelligence Agent - Analyze competitors and generate ad differentiation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze plumbers in Providence
  python run_local_intel.py --business "plumber" --location "Providence, RI"
  
  # Analyze restaurants with larger radius
  python run_local_intel.py --business "restaurant" --location "02903" --radius 5
  
  # Interactive mode
  python run_local_intel.py --interactive
  
  # Output as JSON
  python run_local_intel.py -b "electrician" -l "Boston, MA" --json

API Keys (set as environment variables):
  SERPAPI_KEY          - For competitor discovery (100 free/month)
  FIRECRAWL_API_KEY    - For website scraping (500 free pages)
  
  Note: Jina Reader is used as free fallback for scraping (no key needed)
        """,
    )
    
    parser.add_argument(
        "--business", "-b",
        type=str,
        help="Type of business (e.g., plumber, electrician, restaurant, contractor)",
    )
    
    parser.add_argument(
        "--location", "-l",
        type=str,
        help="Location to search (city, zip code, or 'lat,lng' coordinates)",
    )
    
    parser.add_argument(
        "--radius", "-r",
        type=float,
        default=10.0,
        help="Search radius in miles (default: 10)",
    )
    
    parser.add_argument(
        "--max-competitors", "-m",
        type=int,
        default=15,
        help="Maximum competitors to analyze (default: 15)",
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="output",
        help="Output directory for results (default: output)",
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save output files",
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON to stdout",
    )
    
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check API configuration and exit",
    )
    
    parser.add_argument(
        "--skip-worst",
        action="store_true",
        help="Skip the second search for worst-rated competitors (faster)",
    )
    
    parser.add_argument(
        "--worst-radius",
        type=float,
        default=3.0,
        help="Radius multiplier for worst-rated search (default: 3.0 = 3x normal radius)",
    )
    
    parser.add_argument(
        "--top-count",
        type=int,
        default=3,
        help="Number of top-rated competitors to analyze (default: 3)",
    )
    
    parser.add_argument(
        "--worst-count",
        type=int,
        default=3,
        help="Number of worst-rated competitors to analyze (default: 3)",
    )
    
    return parser.parse_args()


def check_config():
    """Check and display API configuration status."""
    config = AppConfig.load()
    
    print("\n" + "="*50)
    print("API Configuration Status")
    print("="*50)
    
    # SerpAPI
    if config.serpapi:
        print("[OK] SerpAPI: Configured")
        print("     -> Competitor discovery enabled")
    else:
        print("[X] SerpAPI: Not configured")
        print("    -> Set SERPAPI_KEY for auto competitor discovery")
        print("    -> Get key: https://serpapi.com (100 free/month)")
    
    # Firecrawl
    if config.firecrawl:
        print("[OK] Firecrawl: Configured")
        print("     -> Premium website scraping enabled")
    else:
        print("[--] Firecrawl: Not configured (optional)")
        print("     -> Jina Reader will be used (free, no key needed)")
    
    # Outscraper
    if config.outscraper:
        print("[OK] Outscraper: Configured")
        print("     -> Backup competitor discovery enabled")
    else:
        print("[--] Outscraper: Not configured (optional)")
    
    print("\n" + "="*50)
    
    if not config.has_competitor_discovery():
        print("\n[!] No competitor discovery API configured!")
        print("   You can still use manual competitor input.")
        print("   Or set SERPAPI_KEY for automatic discovery.")
    
    print()


def interactive_mode():
    """Run in interactive mode."""
    print("\n" + "="*60)
    print("Local Competitor Intelligence Agent - Interactive Mode")
    print("="*60 + "\n")
    
    # Check config first
    config = AppConfig.load()
    if not config.has_competitor_discovery():
        print("⚠️  No competitor discovery API configured.")
        print("   Set SERPAPI_KEY for automatic discovery,")
        print("   or you'll need to provide competitors manually.\n")
    
    business_type = input("Business type (e.g., plumber, restaurant): ").strip()
    if not business_type:
        print("Error: Business type is required")
        return None
    
    location = input("Location (city, zip, or coordinates): ").strip()
    if not location:
        print("Error: Location is required")
        return None
    
    radius_input = input("Search radius in miles (Enter for 10): ").strip()
    radius = float(radius_input) if radius_input else 10.0
    
    max_input = input("Max competitors to analyze (Enter for 15): ").strip()
    max_competitors = int(max_input) if max_input else 15
    
    return {
        "business_type": business_type,
        "location": location,
        "radius_miles": radius,
        "max_competitors": max_competitors,
    }


def main():
    """Main entry point."""
    args = parse_args()
    
    # Check config
    if args.check_config:
        check_config()
        return 0
    
    # Get parameters
    if args.interactive:
        params = interactive_mode()
        if not params:
            return 1
    elif args.business and args.location:
        params = {
            "business_type": args.business,
            "location": args.location,
            "radius_miles": args.radius,
            "max_competitors": args.max_competitors,
        }
    else:
        print("Error: Please provide --business and --location, or use --interactive mode")
        print("Run with --help for usage information")
        print("Run with --check-config to verify API setup")
        return 1
    
    try:
        # Run analysis
        report = run_analysis(
            business_type=params["business_type"],
            location=params["location"],
            radius_miles=params["radius_miles"],
            save=not args.no_save,
            output_dir=args.output_dir,
            include_worst_rated=not args.skip_worst,
            worst_radius_multiplier=args.worst_radius,
            top_count=args.top_count,
            worst_count=args.worst_count,
        )
        
        # Output as JSON if requested
        if args.json:
            print("\n" + "="*60)
            print("JSON OUTPUT")
            print("="*60)
            print(json.dumps(report.to_dict(), indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
