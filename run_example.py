#!/usr/bin/env python3
"""
Example script to run AdBoard AI pipeline.

Usage:
    python run_example.py
"""

import asyncio

from core.pipeline import run_pipeline


async def main():
    # Example prompt for a local coffee shop ad
    result = await run_pipeline(
        product="artisan coffee shop",
        industry="food and beverage",
        output_type="script",  # Just generate script (fastest for testing)
        duration=30,
        tone="warm and inviting",
        city="Providence, RI",
    )

    if result["success"]:
        print("\n" + "=" * 60)
        print("GENERATED SCRIPT")
        print("=" * 60)

        script_result = result["results"].get("script_writer", {})
        script = script_result.get("script", "No script generated")
        print(script)

        print("\n" + "=" * 60)
        print("RESEARCH SUMMARY")
        print("=" * 60)
        research = result["results"].get("research", {})
        summary = research.get("research_summary", {})
        print(f"  YouTube videos analyzed: {summary.get('youtube_videos', 0)}")
        print(f"  Google Ads analyzed: {summary.get('google_ads', 0)}")
        print(f"  Reviews analyzed: {summary.get('reviews_analyzed', 0)}")
        print(f"  Yelp businesses: {summary.get('yelp_businesses', 0)}")
        print(f"  Keywords analyzed: {summary.get('keywords_analyzed', 0)}")
    else:
        print(f"Pipeline failed: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())
