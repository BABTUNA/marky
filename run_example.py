#!/usr/bin/env python3
"""
AdBoard AI - Interactive Runner

Usage:
    python run_example.py                    # Interactive mode - enter your prompt
    python run_example.py "your prompt"      # Direct mode - pass prompt as argument

Examples:
    python run_example.py "Create a 30 second ad for my taco truck in Austin"
    python run_example.py "I need a storyboard video for my new coffee shop in Providence"
    python run_example.py "Make a funny commercial for my gym in Boston"
"""

import asyncio
import sys

from core.intent_extractor import extract_intent
from core.pipeline import run_pipeline


def print_banner():
    """Print the AdBoard AI banner."""
    print("\n" + "=" * 60)
    print("  🎬 AdBoard AI - Multi-Agent Storyboard Video Generator")
    print("=" * 60)
    print("\nDescribe the ad you want to create. Include:")
    print("  • What business/product (required)")
    print("  • Location/city (for local research)")
    print("  • Duration (30s, 45s, or 60s)")
    print("  • Tone (professional, funny, emotional, energetic)")
    print("  • Output type (script, storyboard, storyboard_video, pdf)")
    print("\nExamples:")
    print('  "Create a 30 second ad for my taco truck in Austin"')
    print('  "I need a funny storyboard video for my coffee shop in Providence"')
    print('  "Make an emotional 60 second commercial for my gym in Boston"')
    print("=" * 60 + "\n")


def get_user_input() -> str:
    """Get prompt from user interactively."""
    print_banner()

    try:
        prompt = input("Your prompt: ").strip()
        if not prompt:
            print("No prompt entered. Exiting.")
            sys.exit(0)
        return prompt
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting.")
        sys.exit(0)


def display_intent(intent: dict):
    """Display the extracted intent for confirmation."""
    print("\n" + "-" * 40)
    print("📋 Extracted Intent:")
    print("-" * 40)
    print(f"  Product:     {intent.get('product', 'Not specified')}")
    print(f"  Industry:    {intent.get('industry', 'general')}")
    print(f"  Location:    {intent.get('city', 'Not specified')}")
    print(f"  Duration:    {intent.get('duration', 30)} seconds")
    print(f"  Tone:        {intent.get('tone', 'professional')}")
    print(f"  Output Type: {intent.get('output_type', 'storyboard_video')}")
    print("-" * 40)

    if not intent.get("ready"):
        missing = intent.get("missing", [])
        print(f"\n⚠️  Missing required info: {', '.join(missing)}")
        return False

    return True


async def main():
    # Get prompt from command line arg or interactive input
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        print(f"\n🎬 AdBoard AI")
        print(f"Prompt: {user_prompt}\n")
    else:
        user_prompt = get_user_input()

    # Extract intent from natural language
    print("\n🔍 Analyzing your request...")
    intent = extract_intent(user_prompt)

    # Display what we understood
    if not display_intent(intent):
        print("\nPlease provide more details and try again.")
        return

    # Confirm before running (interactive mode only)
    if len(sys.argv) <= 1:
        try:
            confirm = input("\nProceed with generation? [Y/n]: ").strip().lower()
            if confirm and confirm not in ("y", "yes", ""):
                print("Cancelled.")
                return
        except (KeyboardInterrupt, EOFError):
            print("\n\nCancelled.")
            return

    print("\n🚀 Starting pipeline...\n")

    # Run the pipeline
    result = await run_pipeline(
        product=intent.get("product", "business"),
        industry=intent.get("industry", "general"),
        output_type=intent.get("output_type", "storyboard_video"),
        duration=intent.get("duration", 30),
        tone=intent.get("tone", "professional"),
        city=intent.get("city", ""),
    )

    # Display results
    if result["success"]:
        print("\n" + "=" * 60)
        print("✅ GENERATION COMPLETE")
        print("=" * 60)

        # Show script
        script_result = result["results"].get("script_writer", {})
        script = script_result.get("script", "No script generated")
        print("\n📜 GENERATED SCRIPT:")
        print("-" * 40)
        print(script)

        # Show research summary
        print("\n" + "-" * 40)
        print("📊 RESEARCH SUMMARY:")
        print("-" * 40)
        research = result["results"].get("research", {})
        summary = research.get("research_summary", {})
        print(f"  YouTube videos analyzed: {summary.get('youtube_videos', 0)}")
        print(f"  Google Ads analyzed:     {summary.get('google_ads', 0)}")
        print(f"  Reviews analyzed:        {summary.get('reviews_analyzed', 0)}")
        print(f"  Yelp businesses:         {summary.get('yelp_businesses', 0)}")
        print(f"  Keywords analyzed:       {summary.get('keywords_analyzed', 0)}")

        # Show generated assets if available
        print("\n" + "-" * 40)
        print("🎨 GENERATED ASSETS:")
        print("-" * 40)

        # Images
        image_result = result["results"].get("image_generator", {})
        if image_result and not image_result.get("error"):
            images = image_result.get("images", [])
            print(f"  Images generated: {len(images)}")
            for img in images[:3]:
                if isinstance(img, dict):
                    print(f"    - {img.get('path', 'N/A')}")

        # Audio
        voiceover_result = result["results"].get("voiceover", {})
        if voiceover_result and not voiceover_result.get("error"):
            print(f"  Voiceover: {voiceover_result.get('audio_path', 'N/A')}")

        music_result = result["results"].get("music", {})
        if music_result and not music_result.get("error"):
            print(f"  Music: {music_result.get('music_path', 'N/A')}")

        # Video
        video_result = result["results"].get("video_assembly", {})
        if video_result and not video_result.get("error"):
            print(f"  Final Video: {video_result.get('video_path', 'N/A')}")

        # PDF
        pdf_result = result["results"].get("pdf_builder", {})
        if pdf_result and not pdf_result.get("error"):
            print(f"  PDF Package: {pdf_result.get('pdf_path', 'N/A')}")

        print("\n" + "=" * 60)

    else:
        print(f"\n❌ Pipeline failed: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())
