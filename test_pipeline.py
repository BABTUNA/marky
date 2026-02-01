#!/usr/bin/env python3
"""
Test script for AdBoard AI pipeline.

Run this to test the pipeline without Agentverse.
Make sure you have a .env file with at least GROQ_API_KEY set.

Usage:
    python test_pipeline.py
"""

import asyncio
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required API key
if not os.getenv("GROQ_API_KEY"):
    print("ERROR: GROQ_API_KEY not set in .env file")
    print("Get a free key at: https://console.groq.com/keys")
    exit(1)


async def test_intent_extraction():
    print("\n" + "=" * 50)
    print("Testing Intent Extractor")
    print("=" * 50)

    from core.intent_extractor import extract_intent

    test_messages = [
        "Create a 30-second storyboard for my taco truck",
        "Write a script for a fitness app ad, make it funny",
        "Full PDF package for a roofing company in Boston",
        "Hello, how are you?",  # Non-ad request
    ]

    for msg in test_messages:
        print(f"\nInput: '{msg}'")
        result = extract_intent(msg)
        print(f"Result: {result}")


async def test_pipeline_script_only():
    """Test pipeline with script-only output."""
    print("\n" + "=" * 50)
    print("Testing Pipeline (script only)")
    print("=" * 50)

    from core.pipeline import AdBoardPipeline

    pipeline = AdBoardPipeline(
        product="taco truck",
        industry="food",
        output_type="script",
        duration=30,
        tone="funny",
        city="Providence",
    )

    result = await pipeline.run()

    print("\nPipeline Result:")
    print(f"Success: {result.get('success')}")

    if result.get("success"):
        results = result.get("results", {})

        # Print script
        script_data = results.get("script_writer", {})
        if script_data:
            print("\n--- SCRIPT ---")
            print(script_data.get("script", "No script")[:1000])
            print("\nScenes:", len(script_data.get("scenes", [])))
    else:
        print(f"Error: {result.get('error')}")


async def test_pipeline_storyboard():
    """Test pipeline with storyboard output (includes images)."""
    print("\n" + "=" * 50)
    print("Testing Pipeline (storyboard - includes images)")
    print("=" * 50)

    # Check for Replicate key (Optional now - we use Vertex AI or Pollinations)
    # if not os.getenv("REPLICATE_API_TOKEN"):
    #     print("REPLICATE_API_TOKEN not set - skipping image generation test")
    #     return
    
    # We can proceed without Replicate since we have Vertex/Pollinations

    from core.pipeline import AdBoardPipeline

    pipeline = AdBoardPipeline(
        product="coffee shop",
        industry="food",
        output_type="storyboard",
        duration=45,
        tone="professional",
        city="",
    )

    result = await pipeline.run()

    print("\nPipeline Result:")
    print(f"Success: {result.get('success')}")

    if result.get("success"):
        results = result.get("results", {})

        # Print image results
        image_data = results.get("image_generator", {})
        if image_data:
            print("\n--- STORYBOARD FRAMES ---")
            frames = image_data.get("frames", [])
            for frame in frames:
                print(
                    f"Frame {frame.get('scene_number')}: {frame.get('url', 'No URL')}"
                )


async def test_full_pipeline():
    """Test full pipeline with all agents."""
    print("\n" + "=" * 50)
    print("Testing Full Pipeline")
    print("=" * 50)

    from core.pipeline import AdBoardPipeline

    pipeline = AdBoardPipeline(
        product="yoga studio",
        industry="fitness",
        output_type="pdf",  # Full package minus video
        duration=45,
        tone="emotional",
        city="Providence, RI",
    )

    result = await pipeline.run()

    print("\nPipeline Result:")
    print(f"Success: {result.get('success')}")

    if result.get("success"):
        results = result.get("results", {})

        for agent_name, agent_result in results.items():
            print(f"\n--- {agent_name.upper()} ---")
            if isinstance(agent_result, dict):
                if agent_result.get("error"):
                    print(f"Error: {agent_result['error']}")
                else:
                    # Print first few keys
                    for key in list(agent_result.keys())[:3]:
                        value = agent_result[key]
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"{key}: {value}")


def main():
    """Run tests."""
    print("AdBoard AI - Pipeline Test")
    print("=" * 50)
    print("Make sure you have a .env file with your API keys!")
    print("=" * 50)

    # Run tests
    asyncio.run(test_intent_extraction())
    asyncio.run(test_pipeline_script_only())

    # Optional tests (require more API keys)
    response = input("\nRun storyboard test (uses Replicate quota)? [y/N]: ")
    if response.lower() == "y":
        asyncio.run(test_pipeline_storyboard())

    response = input("\nRun full pipeline test? [y/N]: ")
    if response.lower() == "y":
        asyncio.run(test_full_pipeline())

    print("\n" + "=" * 50)
    print("Tests complete!")
    print("=" * 50)
    print("="*50)


if __name__ == "__main__":
    main()
