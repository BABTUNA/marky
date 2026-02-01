#!/usr/bin/env python3
"""
Test script for new non-visual pipeline modes.

Tests audio_package, preproduction, and full_no_visual pipelines.
"""

import asyncio
import os

from dotenv import load_dotenv

from core.pipeline import AdBoardPipeline

load_dotenv()


async def test_audio_package():
    """Test audio generation pipeline (voiceover + music)."""
    print("\n" + "=" * 60)
    print("TESTING: Audio Package Pipeline")
    print("=" * 60)

    pipeline = AdBoardPipeline(
        product="coffee shop",
        industry="food",
        output_type="audio_package",
        duration=30,
        tone="professional",
        city="Providence",
    )

    result = await pipeline.run()

    print("\n" + "-" * 60)
    print("RESULTS")
    print("-" * 60)
    print(f"Success: {result.get('success')}")

    if result.get("success"):
        results = result.get("results", {})

        # Voiceover
        print("\n📢 VOICEOVER:")
        voiceover = results.get("voiceover", {})
        if "error" in voiceover:
            print(f"   ⚠️  {voiceover['error']}")
            if "skipped" in voiceover:
                print("   (ElevenLabs API key not set - this is expected)")
        else:
            print(f"   ✅ Audio file: {voiceover.get('audio_path', 'N/A')}")
            print(f"   Duration: {voiceover.get('duration', 'N/A')}s")
            print(f"   Characters: {voiceover.get('character_count', 'N/A')}")
            print(f"   Text preview: {voiceover.get('text_preview', 'N/A')[:80]}...")

        # Music
        print("\n🎵 MUSIC RECOMMENDATIONS:")
        music = results.get("music", {})
        if "error" in music:
            print(f"   ⚠️  {music['error']}")
        else:
            rec = music.get("quick_recommendation", {})
            print(f"   ✅ Genre: {rec.get('genre', 'N/A')}")
            print(f"   BPM: {rec.get('bpm', 'N/A')}")
            print(f"   Search terms: {', '.join(rec.get('search_terms', [])[:3])}")
            
            sources = music.get("free_music_sources", [])
            if sources:
                print(f"   Free sources: {sources[0].get('name', 'N/A')}")


async def test_preproduction():
    """Test preproduction pipeline (location scout + cost estimator)."""
    print("\n" + "=" * 60)
    print("TESTING: Preproduction Pipeline")
    print("=" * 60)

    pipeline = AdBoardPipeline(
        product="yoga studio",
        industry="fitness",
        output_type="preproduction",
        duration=45,
        tone="emotional",
        city="Providence, RI",
    )

    result = await pipeline.run()

    print("\n" + "-" * 60)
    print("RESULTS")
    print("-" * 60)
    print(f"Success: {result.get('success')}")

    if result.get("success"):
        results = result.get("results", {})

        # Location Scout
        print("\n📍 LOCATIONS:")
        locations = results.get("location_scout", {})
        if "error" in locations:
            print(f"   ⚠️  {locations['error']}")
            fallback = locations.get("fallback_suggestions", [])
            if fallback:
                print(f"   Fallback suggestions: {len(fallback)} options")
                print(f"   Example: {fallback[0].get('type', 'N/A')}")
        else:
            locs = locations.get("locations", [])
            print(f"   ✅ Found {len(locs)} locations")
            for i, loc in enumerate(locs[:3], 1):
                print(f"   {i}. {loc.get('name', 'N/A')}")
                print(f"      {loc.get('address', 'N/A')[:50]}...")

        # Cost Estimator
        print("\n💰 COST ESTIMATE:")
        cost = results.get("cost_estimator", {})
        if "error" in cost:
            print(f"   ⚠️  {cost['error']}")
            fallback = cost.get("fallback", {})
            if fallback:
                print(f"   Fallback estimate: ${fallback.get('total', 0)}")
        else:
            print(f"   ✅ Total Budget: ${cost.get('total', 0)}")
            print(f"   Budget Level: {cost.get('budget_level', 'N/A')}")
            print(f"   Shoot Days: {cost.get('shoot_days', 'N/A')}")
            
            breakdown = cost.get("breakdown", {})
            print("\n   Breakdown:")
            for category, amount in list(breakdown.items())[:5]:
                print(f"   - {category}: ${amount}")
            
            tips = cost.get("tips", [])
            if tips:
                print(f"\n   💡 Tip: {tips[0]}")


async def test_full_no_visual():
    """Test full pipeline without images (all agents except image generation)."""
    print("\n" + "=" * 60)
    print("TESTING: Full Non-Visual Pipeline")
    print("=" * 60)

    pipeline = AdBoardPipeline(
        product="local bakery",
        industry="food",
        output_type="full_no_visual",
        duration=45,
        tone="funny",
        city="Providence, RI",
    )

    result = await pipeline.run()

    print("\n" + "-" * 60)
    print("RESULTS")
    print("-" * 60)
    print(f"Success: {result.get('success')}")

    if result.get("success"):
        results = result.get("results", {})
        
        print("\nAgents that ran:")
        for agent_name in results.keys():
            status = "✅" if "error" not in results[agent_name] else "⚠️"
            print(f"  {status} {agent_name}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NON-VISUAL PIPELINE TESTS")
    print("=" * 60)
    print("\nTesting new pipeline modes:")
    print("- audio_package: voice + music")
    print("- preproduction: locations + costs")
    print("- full_no_visual: everything except images")

    # Test 1: Audio Package
    asyncio.run(test_audio_package())

    # Test 2: Preproduction
    asyncio.run(test_preproduction())

    # Test 3: Full No Visual
    asyncio.run(test_full_no_visual())

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE!")
    print("=" * 60)
    
    # Check for missing API keys
    print("\n📋 API Key Status:")
    print(f"   GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Missing'}")
    print(f"   ELEVENLABS_API_KEY: {'✅ Set' if os.getenv('ELEVENLABS_API_KEY') else '⚠️  Missing (optional)'}")
    print(f"   GOOGLE_PLACES_API_KEY: {'✅ Set' if os.getenv('GOOGLE_PLACES_API_KEY') else '⚠️  Missing (optional)'}")
    print(f"   YOUTUBE_API_KEY: {'✅ Set' if os.getenv('YOUTUBE_API_KEY') else '❌ Missing'}")


if __name__ == "__main__":
    main()
