#!/usr/bin/env python3
"""Test enhanced pipeline with audio mixing."""

import asyncio

from core.pipeline import AdBoardPipeline


async def test():
    print("🎬 Testing Enhanced Pipeline with Audio Mixing\n")

    pipeline = AdBoardPipeline(
        product="artisan coffee shop",
        industry="food",
        output_type="audio_package",
        duration=30,
        tone="friendly",
        city="Providence, RI",
    )

    result = await pipeline.run()

    if result["success"]:
        print("\n✅ Pipeline completed successfully!\n")
        results = result["results"]

        # Show location was used early
        if "location_scout" in results:
            locs = results["location_scout"].get("locations", [])
            print(f"📍 Locations found BEFORE script: {len(locs)} places")
            if locs:
                print(f'   First location: {locs[0].get("name", "N/A")}')

        # Show voiceover
        if "voiceover" in results:
            vo = results["voiceover"]
            print(f'\n🎙️  Voiceover: {vo.get("audio_path", "N/A")}')

        # Show mixed audio
        if "audio_mixer" in results:
            mixer = results["audio_mixer"]
            if "mixed_audio_path" in mixer:
                print(f'\n🎵 FINAL MIXED AUDIO: {mixer["mixed_audio_path"]}')
                print("   - Includes voiceover + background music")
                print("   - Ready to use with video!")
            else:
                print(f'\n⚠️  Audio mixer: {mixer.get("error", "Unknown error")}')
    else:
        print(f'❌ Failed: {result.get("error")}')


if __name__ == "__main__":
    asyncio.run(test())
