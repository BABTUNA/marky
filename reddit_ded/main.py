#!/usr/bin/env python3
"""
Reddit VoC Research Agent - CLI Entry Point

Run Voice of Customer research to extract ad insights from Reddit.

Usage:
    python main.py --product "Coffee Subscription" --audience "Coffee lovers" --market "Beverages"
    python main.py --interactive
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from reddit_voc.agent import VoCResearchAgent, run_research
from reddit_voc.config import AppConfig


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Reddit VoC Research Agent - Extract ad insights from Reddit discussions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic research
  python main.py --product "Coffee Subscription" --audience "Coffee lovers" --market "Beverages"
  
  # With keywords and competitors
  python main.py --product "Oat Milk" --audience "Health-conscious consumers" --market "Plant-based beverages" \\
      --keywords "dairy free" "vegan" "barista" \\
      --competitors "Oatly" "Califia"
  
  # Interactive mode
  python main.py --interactive
  
  # Show cache stats
  python main.py --stats
        """,
    )
    
    parser.add_argument(
        "--product", "-p",
        type=str,
        help="Product or service to research",
    )
    
    parser.add_argument(
        "--audience", "-a",
        type=str,
        help="Target audience description",
    )
    
    parser.add_argument(
        "--market", "-m",
        type=str,
        help="Market or industry",
    )
    
    parser.add_argument(
        "--keywords", "-k",
        type=str,
        nargs="+",
        default=[],
        help="Additional keywords to search",
    )
    
    parser.add_argument(
        "--competitors", "-c",
        type=str,
        nargs="+",
        default=[],
        help="Competitor names to track",
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
        "--stats",
        action="store_true",
        help="Show cache statistics and exit",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON to stdout",
    )
    
    return parser.parse_args()


def interactive_mode():
    """Run in interactive mode, prompting for inputs."""
    print("\n" + "="*60)
    print("Reddit VoC Research Agent - Interactive Mode")
    print("="*60 + "\n")
    
    product = input("Product/Service to research: ").strip()
    if not product:
        print("Error: Product is required")
        return None
    
    audience = input("Target audience: ").strip()
    if not audience:
        audience = "general consumers"
    
    market = input("Market/Industry: ").strip()
    if not market:
        market = "general"
    
    keywords_input = input("Additional keywords (comma-separated, or Enter to skip): ").strip()
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()] if keywords_input else []
    
    competitors_input = input("Competitors (comma-separated, or Enter to skip): ").strip()
    competitors = [c.strip() for c in competitors_input.split(",") if c.strip()] if competitors_input else []
    
    return {
        "product": product,
        "audience": audience,
        "market": market,
        "keywords": keywords,
        "competitors": competitors,
    }


def show_stats():
    """Show cache statistics."""
    try:
        agent = VoCResearchAgent()
        stats = agent.get_cache_stats()
        print("\nCache Statistics:")
        print(f"  Subreddits cached: {stats['subreddits']}")
        print(f"  Posts cached: {stats['posts']}")
        print(f"  Comments cached: {stats['comments']}")
    except Exception as e:
        print(f"Could not load stats: {e}")


def print_summary(output):
    """Print a summary of the research output."""
    print("\n" + "="*60)
    print("RESEARCH SUMMARY")
    print("="*60)
    
    print("\n### Top Themes ###")
    for theme in output.voc_brief.top_themes[:5]:
        print(f"\n{theme.name} ({theme.weight*100:.1f}%)")
        if theme.example_quotes:
            print(f"  Quote: \"{theme.example_quotes[0][:100]}...\"" if len(theme.example_quotes[0]) > 100 else f"  Quote: \"{theme.example_quotes[0]}\"")
    
    print("\n### Sample Hooks ###")
    for hook in output.hook_bank.hooks[:5]:
        print(f"  [{hook.tone}] {hook.text}")
    
    print("\n### Advertising Angles ###")
    for angle in output.angle_playbook.angles[:3]:
        print(f"  - {angle.name}: {angle.promise}")
    
    print("\n### Key Objections ###")
    for obj in output.objection_handling.objections[:3]:
        print(f"  - {obj.objection[:80]}...")
        if obj.rebuttal_lines:
            print(f"    Rebuttal: {obj.rebuttal_lines[0]}")
    
    print("\n" + "="*60)


def main():
    """Main entry point."""
    args = parse_args()
    
    # Show stats and exit
    if args.stats:
        show_stats()
        return 0
    
    # Get research parameters
    if args.interactive:
        params = interactive_mode()
        if not params:
            return 1
    elif args.product and args.audience and args.market:
        params = {
            "product": args.product,
            "audience": args.audience,
            "market": args.market,
            "keywords": args.keywords,
            "competitors": args.competitors,
        }
    else:
        print("Error: Please provide --product, --audience, and --market, or use --interactive mode")
        print("Run with --help for usage information")
        return 1
    
    try:
        # Run research
        output = run_research(
            product=params["product"],
            audience=params["audience"],
            market=params["market"],
            keywords=params.get("keywords"),
            competitors=params.get("competitors"),
            save=not args.no_save,
            output_dir=args.output_dir,
        )
        
        # Output results
        if args.json:
            print(json.dumps(output.to_dict(), indent=2))
        else:
            print_summary(output)
        
        return 0
        
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("  REDDIT_CLIENT_ID")
        print("  REDDIT_CLIENT_SECRET")
        print("  REDDIT_USERNAME")
        print("  REDDIT_PASSWORD")
        print("  REDDIT_USER_AGENT (optional)")
        return 1
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
