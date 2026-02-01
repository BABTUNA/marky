#!/usr/bin/env python3
"""
Dump raw output from each agent to a .txt file for debugging.
Run: python dump_agent_outputs.py

Produces: agent_outputs_debug.txt
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


def _format_section(name: str, data: dict) -> str:
    """Format a section as readable text."""
    lines = [f"\n{'='*70}", f"  {name}", f"{'='*70}\n"]
    lines.append(json.dumps(data, indent=2, default=str))
    return "\n".join(lines)


def main():
    business_type = "electrician"
    location = "providence, ri"
    output_path = Path(__file__).parent / "agent_outputs_debug.txt"

    lines = [
        "# Agent Raw Outputs Debug",
        f"# Generated: {datetime.now().isoformat()}",
        f"# Query: {business_type} in {location}",
        "#",
        "# MAPPING TO FINAL REPORT:",
        "#   Competitor Overview  <- local_intel.competitors",
        "#   Customer Voice      <- yelp_intel.insights (pain_points, praise_points)",
        "#   Seasonal Timing     <- trends_intel.seasonal_insights, keyword_data",
        "#   Ad Hooks/Headlines  <- local_intel + yelp_intel ad_suggestions",
        "#   Trust Signals       <- local_intel.trust_signals_to_use",
        "#",
        "# ISSUE: pain_points & praise_points are keyword matches (single words).",
        "#   They come from PAIN_KEYWORDS/PRAISE_KEYWORDS in yelp_intel/agent.py",
        "#",
    ]

    # -------------------------------------------------------------------------
    # LOCAL INTEL
    # -------------------------------------------------------------------------
    try:
        from local_intel import LocalIntelAgent
        agent = LocalIntelAgent()
        report = agent.analyze(
            business_type=business_type,
            location=location,
            radius_miles=10.0,
            top_count=2,
            worst_count=0,
            include_worst_rated=False,
        )
        d = {
            "search_input": {
                "business_type": report.search_input.business_type,
                "location": report.search_input.location,
                "radius_miles": report.search_input.radius_miles,
            },
            "competitors_count": len(report.competitors),
            "competitors": [
                {
                    "name": c.name,
                    "rating": c.rating,
                    "review_count": c.review_count,
                    "website": c.website,
                    "services": c.services[:8],
                    "trust_signals": c.trust_signals[:8],
                }
                for c in report.competitors
            ],
            "market_analysis": asdict(report.market_analysis) if report.market_analysis else None,
            "differentiators": [
                {"angle_name": d.angle_name, "hook": d.hook, "supporting_points": d.supporting_points[:3], "best_for": d.best_for}
                for d in report.differentiators[:5]
            ],
            "headline_suggestions": report.headline_suggestions[:8],
            "tagline_suggestions": report.tagline_suggestions[:5],
            "trust_signals_to_use": report.trust_signals_to_use[:8],
        }
        lines.append(_format_section("1. LOCAL INTEL (local_intel)", d))
    except Exception as e:
        lines.append(_format_section("1. LOCAL INTEL (local_intel)", {"error": str(e), "traceback": type(e).__name__}))

    # -------------------------------------------------------------------------
    # YELP INTEL
    # -------------------------------------------------------------------------
    try:
        from yelp_intel import YelpIntelAgent
        agent = YelpIntelAgent()
        analysis = agent.analyze_market(
            business_type=business_type,
            location=location,
            max_businesses=2,
            reviews_per_business=6,
        )
        d = {
            "business_type": analysis.business_type,
            "location": analysis.location,
            "businesses_count": len(analysis.businesses),
            "total_reviews_analyzed": analysis.total_reviews_analyzed,
            "businesses": [
                {"name": b.name, "rating": b.rating, "review_count": b.review_count}
                for b in analysis.businesses
            ],
            "insights": {
                "pain_points": analysis.insights.pain_points,
                "pain_point_quotes": analysis.insights.pain_point_quotes[:5],
                "praise_points": analysis.insights.praise_points,
                "praise_quotes": analysis.insights.praise_quotes[:5],
                "themes": analysis.insights.themes,
                "customer_phrases": analysis.insights.customer_phrases[:10],
            },
            "ad_suggestions": {
                "hooks": analysis.ad_suggestions.hooks,
                "headlines": analysis.ad_suggestions.headlines,
                "pain_point_hooks": analysis.ad_suggestions.pain_point_hooks,
                "trust_signals": analysis.ad_suggestions.trust_signals,
            },
        }
        lines.append(_format_section("2. YELP INTEL (yelp_intel)", d))
    except Exception as e:
        lines.append(_format_section("2. YELP INTEL (yelp_intel)", {"error": str(e)}))

    # -------------------------------------------------------------------------
    # TRENDS INTEL
    # -------------------------------------------------------------------------
    try:
        from trends_intel import TrendsIntelAgent
        agent = TrendsIntelAgent()
        analysis = agent.analyze(
            keywords=[business_type, f"{business_type} near me"],
            location="United States",
            include_related=False,
        )
        month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        d = {
            "keywords": analysis.keywords,
            "location": analysis.location,
            "keyword_data": [
                {
                    "keyword": k.keyword,
                    "search_volume": k.search_volume,
                    "cpc": k.cpc,
                    "competition": k.competition,
                }
                for k in analysis.keyword_data
            ],
            "seasonal_insights": [
                {
                    "keyword": s.keyword,
                    "peak_season": s.peak_season,
                    "peak_months": [month_names.get(m, m) for m in s.peak_months],
                    "low_season": s.low_season,
                    "recommendation": s.recommendation,
                }
                for s in analysis.seasonal_insights
            ],
            "related_queries": analysis.related_queries[:10],
            "rising_queries": analysis.rising_queries[:10],
        }
        lines.append(_format_section("3. TRENDS INTEL (trends_intel)", d))
    except Exception as e:
        lines.append(_format_section("3. TRENDS INTEL (trends_intel)", {"error": str(e)}))

    # -------------------------------------------------------------------------
    # WRITE
    # -------------------------------------------------------------------------
    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")
    print(f"Wrote: {output_path}")
    print(f"Open agent_outputs_debug.txt to inspect each agent's raw output.")


if __name__ == "__main__":
    main()
