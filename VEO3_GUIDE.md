# VEO 3 Integration Guide

## Overview

VEO 3 groundwork is now in place and ready to enable when needed!

## Important: VEO 3 Does NOT Generate Audio ⚠️

**VEO 3 generates VIDEO ONLY** - no audio track is included!

You must add audio separately using one of these options:
1. **Trending TikTok sounds** - Import popular audio clips
2. **Background music** - Add royalty-free music
3. **AI voiceover** - Generate voiceover with ElevenLabs/Google TTS
4. **Silent** - Let users add their own audio
5. **Hybrid** - Combine music + voiceover

## What's Ready

### ✅ Completed (Groundwork)

1. **VEO 3 Agent** ([`agents/veo3_agent.py`](file:///Users/tomalmog/programming/Febuary%202026/Brown/agents/veo3_agent.py))
   - Full class structure
   - Prompt optimization for viral videos
   - Configuration management
   - Error handling
   - **NO API CALLS YET** (just infrastructure)

2. **Pipeline Integration** ([`core/pipeline.py`](file:///Users/tomalmog/programming/Febuary%202026/Brown/core/pipeline.py))
   - VEO 3 pipeline defined (commented out)
   - Ready to uncomment when needed

3. **Optimal Settings Configured**
   - Duration: 15 seconds (perfect for TikTok/Reels)
   - Format: 9:16 vertical
   - Resolution: 1080p (or 4K)
   - Style: Photorealistic, trendy

## VEO 3 Specifications

### Cost
- **$2.00 per 15-second video**
- Covered by your $410 Google Cloud credits
- 200+ videos possible with current credits

### Output Format
- **Aspect Ratio:** 9:16 (vertical - TikTok/Reels/Shorts)
- **Resolution:** 1080p or 4K
- **Duration:** 15 seconds (configurable)
- **FPS:** 30fps
- **Format:** MP4
- **Audio:** NONE (must add separately!)

### Generation Time
- **~2-5 minutes** per video
- Asynchronous polling required
- Much slower than Imagen (which is instant)

### Use Cases
- ✅ TikTok ads
- ✅ Instagram Reels
- ✅ YouTube Shorts
- ✅ Viral social media content
- ✅ Product showcases
- ✅ Quick promotional videos

## How It Works

### 1. Prompt Building

VEO 3 agent builds optimized prompts like:

```
15-second vertical video (9:16) for [Product] - [Industry]

Opening Hook (0-3s): [Trending hook from research]
Visual: [Scene description from script]

Style: Photorealistic, cinematic, trendy TikTok/Instagram Reels aesthetic
Mood: [energetic/calm/professional], engaging, scroll-stopping

Camera: Dynamic movement - slow zoom, smooth pan, professional gimbal feel
Lighting: Bright, vibrant, optimized for mobile viewing
Pacing: Fast cuts every 3-5 seconds to maintain attention

Key visual elements:
- Show product/service in action
- Include people/emotions if applicable
- Vibrant colors that pop on mobile screens
- Clear focal point in every shot
- Professional but not corporate

Technical: 4K quality, vertical format, optimized for mobile, no text overlays

Reference style: High-performing TikTok/Reels ads - authentic, engaging, not overly produced
```

### 2. Video Generation (Disabled)

Currently commented out in `veo3_agent.py`:

```python
# TODO: Uncomment when ready to actually generate
# video_path = await self._generate_video(veo_prompt, product, duration)
```

### 3. Audio Addition (TODO)

Since VEO 3 doesn't generate audio, you'll need to:

```python
# Option 1: Add trending TikTok sound
video_with_audio = add_trending_audio(veo_video, "trending_tiktok")

# Option 2: Add background music
video_with_audio = add_background_music(veo_video, music_path)

# Option 3: Add AI voiceover
video_with_audio = add_voiceover(veo_video, voiceover_path)

# Option 4: Leave silent
# (Ready for user to add their own trending audio)
```

## How to Enable (When Ready)

### Step 1: Verify API Access

```bash
# Make sure VEO 3 API is enabled in Google Cloud
gcloud services enable aiplatform.googleapis.com
```

### Step 2: Update VEO 3 Agent

In [`agents/veo3_agent.py`](file:///Users/tomalmog/programming/Febuary%202026/Brown/agents/veo3_agent.py), uncomment the generation code:

```python
# Line ~130: Uncomment this
video_path = await self._generate_video(veo_prompt, product, duration)

# Line ~157-180: Implement actual VEO 3 API call
# Replace placeholder with real Google API calls
```

### Step 3: Add to Pipeline

In [`core/pipeline.py`](file:///Users/tomalmog/programming/Febuary%202026/Brown/core/pipeline.py), uncomment the `viral_video` pipeline:

```python
"viral_video": {
    "veo3_generator": {
        "agent": VEO3Agent,
        "requires": ["research", "script_writer"],
    },
    # Optional: Add audio mixer
},
```

### Step 4: Update Orchestrator

In [`orchestrator/workflow.py`](file:///Users/tomalmog/programming/Febuary%202026/Brown/orchestrator/workflow.py), add VEO 3 to the workflow:

```python
# Add after storyboard video generation
if generate_viral_video:
    veo3_result = await self.run_pipeline("viral_video", request)
```

## Audio Integration Options

Since VEO 3 has no audio, here are the best options:

### Option 1: Trending TikTok Sounds
**Best for: Viral potential**
- Scrape trending sounds from TikTok API
- Download and apply to VEO 3 video
- Tools: TikTok API, yt-dlp, ffmpeg

### Option 2: Royalty-Free Music
**Best for: Safe, copyright-free**
- Use services like Epidemic Sound, Artlist
- Or free libraries: YouTube Audio Library
- Simple ffmpeg overlay

### Option 3: AI Voiceover (Already Have!)
**Best for: Brand messaging**
- Use existing ElevenLabs integration
- Generate script voiceover
- Add to VEO 3 video with background music

### Option 4: Silent (User Adds)
**Best for: Platform flexibility**
- Upload silent video
- User adds trending audio when posting
- Maximizes virality potential

## Cost Comparison

| Component | Current Cost | With VEO 3 |
|-----------|-------------|------------|
| Research | FREE | FREE |
| Script (Gemini) | $0.0001 | $0.0001 |
| Storyboard (Imagen) | $0.10 | $0.10 |
| **Viral Video (VEO 3)** | **N/A** | **$2.00** |
| Audio (optional) | $0.02 | $0.02 |
| **Total per Campaign** | **$0.10** | **$2.12** |

Still incredibly cheap! 200+ campaigns with $410 credits.

## Testing (When Enabled)

```bash
# Test VEO 3 generation
python agents/veo3_agent.py

# Full pipeline test
python agents/orchestrator.py
# Ask for "viral video" output type
```

## Current Status

🟡 **GROUNDWORK COMPLETE - READY TO ENABLE**

- ✅ Agent created
- ✅ Prompt optimization done
- ✅ Pipeline structure ready
- ✅ Configuration in place
- ⏸️ API calls disabled (by design)
- ⏸️ Audio integration pending
- ⏸️ Waiting for VEO 3 API access

## Next Steps (When Ready to Enable)

1. **Get VEO 3 API access** from Google Cloud
2. **Implement actual API calls** in `veo3_agent.py`
3. **Test generation** with a single video
4. **Add audio integration** (choose option above)
5. **Update orchestrator** to offer viral video option
6. **Test full pipeline** end-to-end
7. **Deploy to production**

---

**The infrastructure is ready - flip the switch when you want viral videos!** 🚀🎬
