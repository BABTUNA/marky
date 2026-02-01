#!/usr/bin/env python3
"""
Marky - Ad Research Orchestrator Agent

A single-entry-point uAgent for comprehensive ad research.
Uses Fetch.ai's uAgents framework with chat protocol.

Usage:
    # Run as uAgent (for Agentverse/ASI:One)
    python run_marky.py
    
    # Run CLI mode (direct analysis without uAgent)
    python run_marky.py --cli --business "plumber" --location "Boston, MA"
    
    # Check configuration
    python run_marky.py --check-config
"""

import argparse
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


def check_config():
    """Check API configuration status."""
    print("\n" + "="*60)
    print("API Configuration Status")
    print("="*60)
    
    configs = [
        ("SERPAPI_KEY", "SerpAPI (local_intel, yelp_intel, related_questions)", True),
        ("FIRECRAWL_API_KEY", "Firecrawl (website scraping)", False),
        ("ANTHROPIC_API_KEY", "Anthropic/Claude (AI analysis)", False),
        ("DATAFORSEO_LOGIN", "DataForSEO (trends_intel)", False),
        ("DATAFORSEO_PASSWORD", "DataForSEO (trends_intel)", False),
        ("GDRIVE_DEFAULT_FOLDER_ID", "Google Drive folder for --drive-upload", False),
    ]
    
    all_required = True
    
    for key, description, required in configs:
        value = os.getenv(key)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            status = "✓"
        else:
            masked = "NOT SET"
            status = "✗" if required else "○"
            if required:
                all_required = False
        
        req_str = "(required)" if required else "(optional)"
        print(f"  {status} {key}: {masked} {req_str}")
        print(f"      → {description}")
    
    print("="*60)
    
    if not all_required:
        print("\n⚠️  Some required API keys are missing.")
        print("   Set them in your .env file.")
        return False
    
    print("\n✅ Configuration OK - ready to run!")
    return True


def run_cli_mode(args):
    """Run analysis in CLI mode without uAgent."""
    from orchestrator.workflow import MarkyWorkflow
    from orchestrator.models import AdResearchRequest
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🎯 MARKY - CLI Mode                                         ║
╠══════════════════════════════════════════════════════════════╣
║  Business: {args.business:<47} ║
║  Location: {args.location:<47} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    workflow = MarkyWorkflow()
    request = AdResearchRequest(
        business_type=args.business,
        location=args.location,
        max_competitors=args.max_competitors,
        include_trends=not args.no_trends,
        include_pdf_export=not args.no_pdf,
        include_drive_upload=args.drive_upload,
        drive_folder_id=args.drive_folder_id or None,
    )
    
    response = workflow.run(request)
    
    if args.json:
        print(json.dumps(response.result.to_dict(), indent=2))
    else:
        print(response.to_markdown())
    
    # Save output
    if not args.no_save:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"marky_{timestamp}.json"
        
        with open(output_file, "w") as f:
            json.dump(response.result.to_dict(), indent=2, fp=f)
        
        print(f"\n📁 Report saved: {output_file}")
    
    return 0 if response.success else 1


def run_agent_mode():
    """Run as uAgent for Agentverse."""
    try:
        from orchestrator.agent import run_marky
        run_marky()
    except ImportError as e:
        print(f"❌ Error importing uAgents: {e}")
        print("\nMake sure uagents is installed:")
        print("  pip install uagents uagents-core")
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Marky - Ad Research Orchestrator Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run as uAgent (for Fetch.ai Agentverse)
  python run_marky.py
  
  # Run CLI analysis
  python run_marky.py --cli -b "plumber" -l "Boston, MA"
  
  # With PDF + Google Drive upload
  python run_marky.py --cli -b "plumber" -l "Boston" --drive-upload --drive-folder-id "YOUR_FOLDER_ID"
  
  # Check configuration
  python run_marky.py --check-config
        """,
    )
    
    # Mode selection
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode (direct analysis, no uAgent)",
    )
    
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check API configuration and exit",
    )
    
    # CLI mode arguments
    parser.add_argument(
        "-b", "--business",
        type=str,
        help="Business type to analyze (CLI mode)",
    )
    
    parser.add_argument(
        "-l", "--location",
        type=str,
        help="Location to analyze (CLI mode)",
    )
    
    parser.add_argument(
        "--max-competitors",
        type=int,
        default=5,
        help="Maximum competitors to analyze (default: 5)",
    )
    
    parser.add_argument(
        "--no-trends",
        action="store_true",
        help="Skip trends analysis (faster)",
    )
    
    parser.add_argument(
        "--drive-upload",
        action="store_true",
        help="Upload PDF report to Google Drive",
    )
    
    parser.add_argument(
        "--drive-folder-id",
        type=str,
        default=os.getenv("GDRIVE_DEFAULT_FOLDER_ID"),
        help="Google Drive folder ID for upload (or set GDRIVE_DEFAULT_FOLDER_ID)",
    )
    
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF export",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save output file",
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory (default: output)",
    )
    
    args = parser.parse_args()
    
    # Check config
    if args.check_config:
        sys.exit(0 if check_config() else 1)
    
    # CLI mode
    if args.cli:
        if not args.business or not args.location:
            print("❌ CLI mode requires --business and --location")
            print("   Example: python run_marky.py --cli -b 'plumber' -l 'Boston, MA'")
            sys.exit(1)
        sys.exit(run_cli_mode(args))
    
    # Agent mode (default)
    sys.exit(run_agent_mode())


if __name__ == "__main__":
    main()
