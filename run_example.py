#!/usr/bin/env python3
"""
AdBoard AI - Interactive Runner

Usage:
    python run_example.py                    # Interactive mode - enter your prompt
    python run_example.py "your prompt"      # Direct mode - pass prompt as argument
    python run_example.py --quick "prompt"   # Skip research (dummy data) - faster testing

Examples:
    python run_example.py "Create an ad campaign for my taco truck in Austin"
    python run_example.py "I need ads for my coffee shop in Providence"
    python run_example.py --quick "Create ad for my coffee shop"   # Fast test (no research)
"""

import asyncio
import os
import sys

from core.intent_extractor import extract_intent
from core.pipeline import run_pipeline


def print_banner():
    """Print the AdBoard AI banner."""
    print("\n" + "=" * 60)
    print("  AdBoard AI - Full Ad Campaign Generator")
    print("=" * 60)
    print("\nCreates: (1) storyboard package for development + (2) viral video ready to post.")
    print("\nDescribe the ad you want. Include:")
    print("  • What business/product (required)")
    print("  • Location/city (for local research)")
    print("  • Duration (30s, 45s, or 60s)")
    print("  • Tone (professional, funny, emotional, energetic)")
    print("\nExamples:")
    print('  "Create an ad campaign for my taco truck in Austin"')
    print('  "I need ads for my coffee shop in Providence"')
    print('  "Make a viral video and storyboard for my gym in Boston"')
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
    print(f"  Output Type: {intent.get('output_type', 'full_campaign')}")
    print("-" * 40)

    if not intent.get("ready"):
        missing = intent.get("missing", [])
        print(f"\n⚠️  Missing required info: {', '.join(missing)}")
        return False

    return True


async def main():
    # Check for --quick flag (skip research, use dummy data)
    use_quick = "--quick" in sys.argv or os.getenv("QUICK_FULL", "").lower() == "true"
    if "--quick" in sys.argv:
        sys.argv.remove("--quick")

    # Get prompt from command line arg or interactive input
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        print(f"\n🎬 AdBoard AI" + (" [QUICK MODE - no research]" if use_quick else ""))
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

    # Run the pipeline (override to quick_full if --quick)
    output_type = "quick_full" if use_quick else intent.get("output_type", "full_campaign")
    result = await run_pipeline(
        product=intent.get("product", "business"),
        industry=intent.get("industry", "general"),
        output_type=output_type,
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
        print("📊 RESEARCH SUMMARY (Marky Research Suite):")
        print("-" * 40)
        research = result["results"].get("research", {})
        summary = research.get("research_summary", {})
        
        # Marky research uses these keys
        competitors = research.get("local_intel", {}).get("competitors_found", summary.get('competitors_found', 0))
        google_reviews = summary.get('google_reviews', 0)
        yelp_reviews = summary.get('yelp_reviews', 0)
        keywords = summary.get('keywords_analyzed', 0)
        related_questions = len(research.get("related_questions", []))
        
        print(f"  Competitors found:       {competitors}")
        print(f"  Google Reviews analyzed: {google_reviews}")
        print(f"  Yelp reviews analyzed:   {yelp_reviews}")
        print(f"  Keywords analyzed:       {keywords}")
        print(f"  Related questions:       {related_questions}")
        
        # Show Marky differentiators if available
        differentiators = research.get("local_intel", {}).get("differentiators", [])
        if differentiators:
            print(f"  Differentiators:         {len(differentiators)}")
        
        # Show customer themes
        customer_voice = research.get("google_reviews", {})
        themes = customer_voice.get("common_themes", [])
        if themes:
            print(f"  Customer themes:         {len(themes)}")

        # Show generated assets if available
        print("\n" + "-" * 40)
        print("🎨 GENERATED ASSETS:")
        print("-" * 40)

        # Images
        image_result = result["results"].get("image_generator", {})
        if image_result and not image_result.get("error"):
            frames = image_result.get("frames", [])
            print(f"  Images generated: {len(frames)}")
            for img in frames[:3]:
                if isinstance(img, dict):
                    print(f"    - {img.get('url', img.get('path', 'N/A'))[:60]}...")

        # Audio
        voiceover_result = result["results"].get("voiceover", {})
        if voiceover_result and not voiceover_result.get("error"):
            vo_path = voiceover_result.get('audio_path', 'N/A')
            print(f"  Voiceover: {vo_path.split('/')[-1] if '/' in vo_path else vo_path}")

        # Lyria music (viral pipeline)
        lyria_result = result["results"].get("lyria_music", {})
        if lyria_result and lyria_result.get("audio_path"):
            print(f"  Lyria Music: {lyria_result['audio_path'].split('/')[-1]}")

        # Audio mixer (shows if music was included)
        audio_mixer_result = result["results"].get("audio_mixer", {})
        if audio_mixer_result and not audio_mixer_result.get("error"):
            note = audio_mixer_result.get("note", "")
            if "voiceover only" in note.lower():
                print(f"  Music: None (voiceover only)")
            else:
                mixed_path = audio_mixer_result.get('mixed_audio_path', 'N/A')
                print(f"  Audio: {mixed_path.split('/')[-1]}")

        # Storyboard video
        video_result = result["results"].get("video_assembly", {})
        if video_result and not video_result.get("error"):
            video_path = video_result.get('final_video_path') or video_result.get('video_path', 'N/A')
            print(f"  Storyboard Video: {video_path.split('/')[-1] if isinstance(video_path, str) else 'N/A'}")

        # Viral video (when quick_full or full_campaign)
        viral_result = result["results"].get("viral_video_assembler", {})
        if viral_result and viral_result.get("final_video_path"):
            print(f"  Viral Video: {viral_result['final_video_path'].split('/')[-1]}")

        # PDF
        pdf_result = result["results"].get("pdf_builder", {})
        if pdf_result and not pdf_result.get("error"):
            print(f"  PDF Package: {pdf_result.get('pdf_path', 'N/A')}")

        # Upload to Google Drive (or tmpfiles.org) if configured
        print("\n" + "-" * 40)
        print("📤 UPLOADING TO CLOUD...")
        print("-" * 40)
        try:
            from agents.orchestrator import upload_file
            uploaded = []
            if video_result and not video_result.get("error"):
                vpath = video_result.get("final_video_path") or video_result.get("video_path")
                if vpath and os.path.exists(vpath):
                    url = upload_file(vpath)
                    if url:
                        print(f"  🎬 Storyboard Video: {url}")
                        uploaded.append("storyboard")
            if viral_result and viral_result.get("final_video_path"):
                vpath = viral_result["final_video_path"]
                if os.path.exists(vpath):
                    url = upload_file(vpath)
                    if url:
                        print(f"  🎬 Viral Video: {url}")
                        uploaded.append("viral")
            if pdf_result and not pdf_result.get("error"):
                ppath = pdf_result.get("pdf_path")
                if ppath and os.path.exists(ppath):
                    url = upload_file(ppath)
                    if url:
                        print(f"  📄 PDF: {url}")
                        uploaded.append("pdf")
            if not uploaded:
                print("  (No files to upload or upload skipped - check GDRIVE_DEFAULT_FOLDER_ID)")
        except Exception as e:
            print(f"  ⚠️ Upload failed: {e}")

        print("\n" + "=" * 60)

    else:
        print(f"\n❌ Pipeline failed: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())
