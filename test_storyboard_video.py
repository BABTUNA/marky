"""
Storyboard Video Test Script

Tests the complete storyboard video pipeline:
1. Generate sketch-style storyboard frames (Imagen 3)
2. Create video with Ken Burns effects (FFmpeg)
3. Mix voiceover + music
4. Final video output

Cost: ~$0.15 for 5 sketch frames
"""

import asyncio
from core.pipeline import run_pipeline


async def test_storyboard_video():
    """Run a complete storyboard video generation test."""
    
    print("=" * 70)
    print("            STORYBOARD VIDEO GENERATION TEST")
    print("=" * 70)
    print()
    print("📋 THIS TEST WILL:")
    print("   1. Generate 5 pencil sketch storyboard frames ($0.03 each)")
    print("   2. Create video with Ken Burns effects (pan/zoom)")
    print("   3. Mix voiceover + background music")
    print("   4. Export final 30s video with audio")
    print()
    print("💰 ESTIMATED COST: $0.15 (images only, FFmpeg is free)")
    print()
    print("=" * 70)
    print()
    
    # Test configuration
    product = "artisan coffee shop"
    industry = "food"
    duration = 30
    tone = "friendly"
    city = "Providence, RI"
    
    print(f"🎬 Product: {product}")
    print(f"🏢 Industry: {industry}")
    print(f"⏱️  Duration: {duration}s")
    print(f"🎭 Tone: {tone}")
    print(f"📍 City: {city}")
    print()
    
    # Run the storyboard_video pipeline
    result = await run_pipeline(
        product=product,
        industry=industry,
        output_type="storyboard_video",
        duration=duration,
        tone=tone,
        city=city,
    )
    
    # Display results
    print()
    print("=" * 70)
    print("            RESULTS")
    print("=" * 70)
    print()
    
    if result.get("success"):
        results = result.get("results", {})
        
        # Image generation
        image_data = results.get("image_generator", {})
        frames = image_data.get("frames", [])
        image_cost = image_data.get("total_generated", 0) * 0.03
        
        print(f"✅ STORYBOARD FRAMES:")
        print(f"   Generated: {len(frames)} sketch frames")
        print(f"   Cost: ${image_cost:.2f}")
        if frames:
            for frame in frames[:3]:
                path = frame.get("path") or frame.get("image_path", "N/A")
                print(f"   - {path}")
        print()
        
        # Audio
        audio_mixer = results.get("audio_mixer", {})
        mixed_audio = audio_mixer.get("mixed_audio_path")
        
        print(f"🎵 AUDIO:")
        print(f"   Mixed Audio: {mixed_audio or 'N/A'}")
        print()
        
        # Video assembly
        video_assembly = results.get("video_assembly", {})
        final_video = video_assembly.get("final_video_path")
        mode = video_assembly.get("mode", "unknown")
        frames_used = video_assembly.get("frames_used", 0)
        
        print(f"🎬 FINAL VIDEO:")
        print(f"   Mode: {mode}")
        print(f"   Frames Used: {frames_used}")
        print(f"   Output: {final_video or 'N/A'}")
        print()
        
        if final_video:
            print("=" * 70)
            print("✨ SUCCESS! Storyboard video created!")
            print("=" * 70)
            print()
            print(f"📹 Final video: {final_video}")
            print(f"💰 Total cost: ${image_cost:.2f}")
            print()
            print("You can now:")
            print("  1. Watch the video with storyboard frames + Ken Burns effects")
            print("  2. Listen to the voiceover + background music")
            print("  3. Test with different products/industries")
            print()
        else:
            print("⚠️  Video assembly failed - check logs above")
    else:
        print(f"❌ Pipeline failed: {result.get('error')}")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_storyboard_video())
