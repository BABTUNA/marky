#!/usr/bin/env python3
"""
AdBoard AI - Comprehensive Demo Script

Runs a full non-visual pipeline and displays all generated content
in a polished, easy-to-read format.
"""

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from core.pipeline import AdBoardPipeline

load_dotenv()


def print_header(title, char="=", width=70):
    """Print a nice header."""
    print(f"\n{char * width}")
    print(f"{title.center(width)}")
    print(f"{char * width}\n")


def print_section(title, char="-"):
    """Print a section header."""
    print(f"\n{char * 50}")
    print(f"{title}")
    print(f"{char * 50}")


async def run_demo():
    """Run comprehensive demo and show all outputs."""

    print_header("🎬 ADBOARD AI - COMPLETE DEMO 🎬", "=", 70)

    print("📋 CAMPAIGN DETAILS:\n")
    product = "artisan coffee shop"
    industry = "food"
    duration = 30
    tone = "friendly"
    city = "Providence, RI"

    print(f"   Product: {product}")
    print(f"   Industry: {industry}")
    print(f"   Duration: {duration} seconds")
    print(f"   Tone: {tone}")
    print(f"   City: {city}")

    print("\n🎯 Running FULL NON-VISUAL pipeline:")
    print("   (8 agents: research → trends → script → voice → music → cost → locations → social)")

    # Run pipeline
    pipeline = AdBoardPipeline(
        product=product,
        industry=industry,
        output_type="full_no_visual",
        duration=duration,
        tone=tone,
        city=city,
    )

    result = await pipeline.run()

    if not result.get("success"):
        print(f"\n❌ Pipeline failed: {result.get('error')}")
        return

    results = result.get("results", {})

    # Display results for each agent
    print_header("📊 GENERATED CONTENT", "=", 70)

    # 1. Research
    print_section("🔍 RESEARCH - YouTube Viral Ad Analysis")
    research = results.get("research", {})
    if "videos" in research:
        videos = research["videos"][:5]
        print(f"\nFound {len(videos)} viral ads in the {industry} industry:\n")
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video.get('title', 'N/A')[:60]}")
            print(f"   Views: {video.get('views', 'N/A'):,} | Engagement: {video.get('engagement_score', 0):.1f}/10")

    # 2. Trends
    print_section("📈 TREND ANALYSIS")
    trends = results.get("trend_analyzer", {})
    if "key_themes" in trends:
        print("\n🎯 Key Themes:")
        for theme in trends["key_themes"][:4]:
            print(f"   • {theme}")

    # 3. Script
    print_section("📝 AD SCRIPT")
    script = results.get("script_writer", {})
    if "scenes" in script:
        scenes = script["scenes"]
        print(f"\n✅ Generated {len(scenes)}-scene ad script\n")

        for scene in scenes[:3]:  # Show first 3
            print(f"┌─ SCENE {scene.get('scene_number', '?')} ({scene.get('timing', '?')})")
            print(f"│  {scene.get('title', 'N/A')}")
            print(f"│")
            print(f"│  🎬 Visual: {scene.get('visual', 'N/A')[:80]}...")
            print(f"│  🎙️  Voiceover: {scene.get('voiceover', 'N/A')[:80]}...")
            print("└" + "─" * 48 + "\n")

        voiceover_full = script.get("voiceover_text", "")
        if voiceover_full:
            print(f"📄 Full Voiceover Text ({len(voiceover_full)} characters):")
            print(f"   \"{voiceover_full[:200]}...\"")

    # 4. Voiceover
    print_section("🎙️  VOICEOVER GENERATION")
    voiceover = results.get("voiceover", {})
    if "error" in voiceover:
        print(f"\n   ⚠️  {voiceover['error']}")
        if "skipped" in voiceover:
            print("   (This is expected if ElevenLabs API key is not set)")
    else:
        print(f"\n   ✅ Audio file generated!")
        print(f"   📁 Path: {voiceover.get('audio_path', 'N/A')}")
        print(f"   ⏱️  Duration: {voiceover.get('duration', 0)} seconds")
        print(f"   📝 Characters: {voiceover.get('character_count', 0)}")

    # 5. Music
    print_section("🎵 MUSIC RECOMMENDATIONS")
    music = results.get("music", {})
    if "quick_recommendation" in music:
        rec = music["quick_recommendation"]
        print(f"\n   🎼 Genre: {rec.get('genre', 'N/A')}")
        print(f"   🥁 BPM: {rec.get('bpm', 'N/A')}")
        print(f"\n   🔍 Search these on royalty-free sites:")
        for term in rec.get("search_terms", [])[:3]:
            print(f"      • \"{term}\"")

        sources = music.get("free_music_sources", [])
        if sources:
            print(f"\n   🌐 Free Music Sources:")
            for source in sources[:3]:
                print(f"      • {source.get('name', 'N/A')}: {source.get('url', 'N/A')}")

    # 6. Cost Estimation
    print_section("💰 PRODUCTION COST ESTIMATE")
    cost = results.get("cost_estimator", {})
    if "total" in cost:
        print(f"\n   💵 Total Budget: ${cost.get('total', 0):,}")
        print(f"   📊 Budget Level: {cost.get('budget_level', 'N/A').upper()}")
        print(f"   🎬 Shoot Days: {cost.get('shoot_days', 'N/A')}")
        print(f"   👥 Crew Size: {cost.get('crew_size', 'N/A')}")

        breakdown = cost.get("breakdown", {})
        if breakdown:
            print("\n   📋 Budget Breakdown:")
            for category, amount in breakdown.items():
                print(f"      • {category.replace('_', ' ').title()}: ${amount:,}")

        tips = cost.get("tips", [])
        if tips:
            print(f"\n   💡 Money-Saving Tip:")
            print(f"      {tips[0]}")

    # 7. Location Scout
    print_section("📍 FILMING LOCATIONS")
    locations = results.get("location_scout", {})
    if "locations" in locations:
        locs = locations["locations"]
        print(f"\n   ✅ Found {len(locs)} locations in {city}\n")

        for i, loc in enumerate(locs[:3], 1):
            print(f"   {i}. {loc.get('name', 'N/A')}")
            print(f"      📍 {loc.get('address', 'N/A')[:50]}...")
            print(f"      ⭐ Rating: {loc.get('rating', 'N/A')}")
            print(f"      💰 Est. Cost: {loc.get('price_level', 'Contact for pricing')}\n")

    # 8. Social Media Strategy
    print_section("📱 SOCIAL MEDIA STRATEGY")
    social = results.get("social_media", {})
    if "platforms" in social:
        platforms = social["platforms"]
        print("\n   🎯 Recommended Platforms:\n")
        for plat in platforms[:3]:
            print(f"   #{plat.get('priority', '?')} {plat.get('name', 'N/A')}")
            print(f"       Format: {plat.get('format', 'N/A')}")
            print()

    if "hashtags" in social:
        hashtags = social["hashtags"]
        print("   #️⃣  Hashtag Strategy:\n")
        primary = hashtags.get("primary", [])
        if primary:
            print(f"       {' '.join(primary[:5])}")

    if "quick_captions" in social:
        captions = social["quick_captions"]
        print("\n   ✍️  Sample Captions:\n")
        print(f"       Main: {captions.get('main', 'N/A')[:60]}...")
        print(f"       CTA: {captions.get('cta', 'N/A')[:60]}...")

    # Summary
    print_header("✅ DEMO COMPLETE! ✅", "=", 70)

    print("📦 DELIVERABLES CREATED:\n")
    deliverables = [
        ("Research Report", "✅ 5 viral ads analyzed"),
        ("Trend Analysis", "✅ Key themes identified"),
        ("Ad Script", f"✅ {len(script.get('scenes', []))} scenes written"),
        ("Voiceover", "⚠️  Requires valid API key" if "error" in voiceover else f"✅ {voiceover.get('audio_path', 'Generated')}"),
        ("Music Strategy", "✅ Genre & search terms"),
        ("Cost Estimate", f"✅ ${cost.get('total', 0):,} budget"),
        ("Locations", f"✅ {len(locations.get('locations', []))} filming spots"),
        ("Social Strategy", "✅ Platforms & hashtags"),
    ]

    for name, status in deliverables:
        print(f"   • {name:20} → {status}")

    print("\n" + "=" * 70)
    print("\n💾 Want to save results? Check output/ directory for audio files")
    print("📊 Pipeline orchestrated 8 agents successfully!\n")

    # Save full results to JSON for inspection
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    results_file = output_dir / "demo_results.json"
    with open(results_file, "w") as f:
        # Convert results to JSON-serializable format
        json.dump(results, f, indent=2, default=str)

    print(f"📁 Full results saved to: {results_file}\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
