# AdBoard AI - Master Context Restore

> **Snapshot Date:** February 1, 2026 (Evening Update)
> **System Status:** STABLE - Viral Video Pipeline TESTED
> **Latest Change:** Google TTS Integration + Viral Pipeline Testing

---

## 0. Quick Reference - Critical Files

| Category | File | Purpose |
|----------|------|---------|
| **Entry Point** | `agents/orchestrator.py` | ASI:One/Agentverse integration, Chat Protocol |
| **Pipeline Runner** | `core/pipeline.py` | Defines agent sequences for each output type |
| **LLM Client** | `core/gemini_client.py` | Google Gemini API wrapper |
| **Intent Parser** | `core/intent_extractor.py` | Parses user messages to structured intent |
| **Models** | `agents/models.py` | Shared message models (uAgents protocol) |
| **Marky Workflow** | `orchestrator/workflow.py` | Research sub-agent orchestration |

---

## 1. Project Overview & Mission

**AdBoard AI** is a multi-agent system that generates complete advertising campaigns for local businesses.

- **Input:** Business Name, Industry, City
- **Output:**
    1. **PDF Campaign Package:** Strategy, scripts, budget, distribution plan
    2. **Storyboard Video:** Black & white hand-drawn sketches (concept validation) - **SILENT, NO AUDIO**
    3. **Viral Video (Future):** Photorealistic VEO 3 video + Lyria music + Google TTS voiceover

---

## 2. IMPORTANT: Current vs Final System

### What We Just Built (Testing Only)
The viral video pipeline was tested to verify:
- Video + Audio assembly works (moviepy)
- Google TTS voiceover generation works
- Music overlay works

**This is NOT the final product flow.** The testing used:
- Placeholder video (existing storyboard video)
- Mock music (existing audio file)
- Google TTS voiceover

### Final Production System Will Be:
1. **Storyboard Pipeline (Current Default):** Hand-drawn sketches → Ken Burns video → **NO AUDIO**
2. **Viral Video Pipeline (Future):** VEO 3 photorealistic video → Lyria music → Google TTS → Combined viral video

The storyboard videos are meant for concept validation and should remain silent.

---

## 3. Recent Changes (This Session)

### Google TTS Integration
- **Status:** WORKING
- **File:** `agents/viral_video_assembler.py`
- **Voices:** Neural2 voices (most natural sounding)
  - `professional` → en-US-Neural2-J (male)
  - `friendly` → en-US-Neural2-F (female)
  - `energetic` → en-US-Neural2-D (male)
  - `calm` → en-US-Neural2-C (female)
  - `funny` → en-US-Neural2-A (male)

### Viral Video Pipeline Testing
- **Test Script:** `test_viral_pipeline.py`
- **Components Tested:**
  - VEO 3 Agent (placeholder mode) ✅
  - Lyria Agent (mock mode) ✅
  - Video Assembler (full assembly) ✅
  - Google TTS (working) ✅

### Environment Variables for Testing
```bash
VEO_USE_PLACEHOLDER=true    # Use existing video instead of VEO 3
LYRIA_USE_MOCK=true         # Use mock/silent audio instead of Lyria
ASSEMBLER_USE_ELEVENLABS=false  # Use Google TTS (default now)
```

---

## 4. Known Issue: Google TTS Voice Sounds Robotic

The current Google TTS Neural2 voices sound robotic. Options to improve:

### Option 1: Use Studio Voices (Higher Quality)
Google offers "Studio" voices that are more natural but cost more:
```python
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-O",  # Studio voice
)
```

### Option 2: Use Journey Voices (Most Natural)
Google's newest "Journey" voices are the most natural:
```python
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Journey-D",  # Journey voice (if available)
)
```

### Option 3: Adjust Speech Parameters
Add SSML for more natural pacing:
```python
synthesis_input = texttospeech.SynthesisInput(
    ssml='<speak><prosody rate="95%" pitch="-2st">Your text here</prosody></speak>'
)
```

### Option 4: Switch to WaveNet Voices
WaveNet voices are between Neural2 and Studio in quality:
```python
name="en-US-Wavenet-D"  # Instead of Neural2
```

---

## 5. File Manifest (Complete)

### Core Files
| File | Purpose | Status |
|------|---------|--------|
| `agents/orchestrator.py` | Main entry point, ASI:One/Agentverse Chat Protocol | ✅ Active |
| `core/pipeline.py` | Pipeline definitions & runner (11 pipelines) | ✅ Active |
| `core/gemini_client.py` | LLM Backend (Vertex AI Gemini) | ✅ Active |
| `core/intent_extractor.py` | Parses user messages → structured intent | ✅ Active |
| `agents/models.py` | Shared uAgents message models | ✅ Active |

### Research Agents
| File | Purpose | Status |
|------|---------|--------|
| `agents/enhanced_research.py` | Main research agent (calls Marky workflow) | ✅ Active |
| `orchestrator/workflow.py` | Marky multi-agent research orchestration | ✅ Active |
| `local_intel/agent.py` | SerpAPI competitor discovery | ✅ Active |
| `review_intel/agent.py` | Google Reviews fetcher | ✅ Active |
| `yelp_intel/agent.py` | Yelp reviews & insights | ✅ Active |
| `ad_intel_no/google_trends_agent.py` | Google Trends keyword analysis | ✅ Active |
| `related_questions_intel/agent.py` | "People also ask" scraper | ✅ Active |

### Creative Agents
| File | Purpose | Status |
|------|---------|--------|
| `agents/script_writer.py` | Gemini-powered script generation | ✅ Active |
| `agents/trend_analyzer.py` | Viral trend analysis | ✅ Active |
| `agents/image_generator.py` | Imagen 3 storyboard frames | ✅ Active |
| `agents/video_assembly_agent.py` | Ken Burns animation (silent) | ✅ Active |

### Audio/Video Agents
| File | Purpose | Status |
|------|---------|--------|
| `agents/voiceover_agent.py` | ElevenLabs voiceover | ✅ Active |
| `agents/music_agent.py` | Background music selection | ✅ Active |
| `agents/audio_mixer.py` | Mixes voiceover + music (pydub) | ✅ Active |
| `agents/veo3_agent.py` | VEO 3 video generation | ✅ Placeholder mode |
| `agents/lyria_agent.py` | Lyria AI music generation | ✅ Mock mode |
| `agents/viral_video_assembler.py` | Video + Music + Google TTS | ✅ **WORKING** |

### Production Agents
| File | Purpose | Status |
|------|---------|--------|
| `agents/cost_estimator.py` | Production budget estimation | ✅ Active |
| `agents/location_scout.py` | Google Places filming locations | ✅ Active |
| `agents/social_media_agent.py` | Hashtags & captions per platform | ✅ Active |
| `agents/pdf_builder.py` | Complete PDF campaign package | ✅ Active |

### Utilities
| File | Purpose | Status |
|------|---------|--------|
| `utils/map_generator.py` | Google Static Maps competitor visualization | ✅ Integrated |
| `utils/map_generator_simple.py` | Simplified map generator | ✅ Available |
| `test_viral_pipeline.py` | CLI test script for viral pipeline | ✅ Active |

### Legacy/Unused
| File | Purpose | Status |
|------|---------|--------|
| `agents/veo_agent.py` | Original VEO agent (pre-VEO 3) | ⚠️ Deprecated |
| `agents/research_agent.py` | Old research agent | ⚠️ Replaced by enhanced_research |
| `core/groq_client.py` | Groq LLM client | ⚠️ Backup only |
| `core/dummy_research.py` | Mock research data | ⚠️ Testing only |

---

## 6. How to Run

### Standard Storyboard (Production Default)
```bash
python agents/orchestrator.py
```
Result: Hand-drawn storyboard video (SILENT) + PDF Package

### Test Viral Video Pipeline
```bash
python test_viral_pipeline.py
python test_viral_pipeline.py --product "Pizza Shop" --tone "funny"
python test_viral_pipeline.py --full  # Include research agents
```
Result: Assembled video with placeholder video + mock music + Google TTS voiceover

### Enable Real VEO 3 + Lyria (Costs Money!)
```bash
export VEO_USE_PLACEHOLDER=false  # ~$2 per video
export LYRIA_USE_MOCK=false       # Uses Lyria API
python test_viral_pipeline.py
```

---

## 7. API Requirements & Environment Variables

**Enabled APIs (Google Cloud Console):**
- Vertex AI API ✅
- Cloud Text-to-Speech API ✅
- Imagen API ✅
- Google Static Maps API ✅ (competitor map)
- VEO 3 API (when ready)
- Lyria API (when ready)

**Required Environment Variables (.env):**
```bash
# Google Cloud (REQUIRED)
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Fetch.AI Agentverse (REQUIRED for ASI:One)
AGENT_SEED_PHRASE=your-unique-seed-phrase
AGENTVERSE_API_KEY=your-agentverse-key

# Research APIs (REQUIRED for full research)
SERPAPI_KEY=your-serpapi-key
YOUTUBE_API_KEY=your-youtube-key
GOOGLE_PLACES_API_KEY=your-places-key

# Optional
ELEVENLABS_API_KEY=your-elevenlabs-key  # Fallback TTS
REPLICATE_API_TOKEN=your-replicate-key   # Backup image gen
GROQ_API_KEY=your-groq-key               # Backup LLM
```

**Testing Mode Variables:**
```bash
VEO_USE_PLACEHOLDER=true     # Skip VEO 3 API (~$2/video)
LYRIA_USE_MOCK=true          # Skip Lyria API  
ASSEMBLER_USE_ELEVENLABS=false  # Use Google TTS (default)
TEST_MODE=true               # Quick echo response (no pipeline)
MOCK_MODE=true               # Return mock data instantly
```

---

## 8. Orchestrator Details

### Entry Point Flow
```
User Message (ASI:One/Agentverse)
       ↓
orchestrator.py (Chat Protocol)
       ↓
intent_extractor.py (Gemini parses intent)
       ↓
pipeline.py (Runs agent sequence)
       ↓
Results formatted & returned
       ↓
Files uploaded to Google Drive (or tmpfiles.org fallback)
```

### Orchestrator Modes
| Mode | Env Variable | Behavior |
|------|--------------|----------|
| **Production** | (default) | Full pipeline, uploads to Google Drive (or tmpfiles.org if not configured) |
| **Test Mode** | `TEST_MODE=true` | Quick echo response, no pipeline |
| **Mock Mode** | `MOCK_MODE=true` | Returns realistic mock data instantly |

### Output Types (intent_extractor.py)
| Keyword | Output Type | Description |
|---------|-------------|-------------|
| "storyboard video" | `storyboard_video` | Silent video with Ken Burns animation |
| "video" | `storyboard_video` | Same as above (normalized) |
| "full package" | `full` | Everything including PDF |
| "pdf", "budget" | `pdf` | PDF package only |
| "script only" | `script` | Just the script |
| "storyboard" | `storyboard` | Images only, no video |

### File Upload System
The orchestrator uploads final files to **Google Drive** (when `GDRIVE_DEFAULT_FOLDER_ID` is set) or **tmpfiles.org** (fallback, 1hr expiry):
- Videos (MP4) and PDFs
- Uses `utils/gdrive_upload.py` for Drive (permanent links)
- Falls back to tmpfiles.org via curl if Drive not configured
- See `docs/MCP_AGENT.md` for Drive setup

---

## 9. Stretch Goals (From Discord)

### Priority Tasks
1. **Integrate MCP Google Drive Upload** - Upload final videos/PDFs to Google Drive ✅ DONE
2. **Ensure Research → Script Context** - Research agent must know it's generating for storyboard + viral video + PDF ✅ DONE
3. **Test with Actual VEO 3** - Full pipeline with real video generation, music, TTS overlay, then Drive upload

### Stretch Goal
4. **ASI:One Preview Integration** - Figure out how to preview results in ASI:One interface

## 10. Completed Small Tasks

- ✅ Fixed voiceover label (was showing "elevenlabs" instead of "google_tts")
- ✅ Fixed mock music bug (was using old voiceover as music, causing voice overlap)
- ✅ Updated script writer to know output is used for storyboard + viral video + PDF
- ✅ Improved Google TTS with Studio/Casual voices + SSML for natural pacing
- ✅ Integrated competitor map generator into research pipeline
- ✅ Added competitor map image to PDF output

---

## 11. Full Agent Orchestration Chain

### Pipeline Definitions (from `core/pipeline.py`) - 11 Total

| Pipeline Name | Agents in Order | Use Case |
|--------------|-----------------|----------|
| `script` | research → location_scout → trend_analyzer → script_writer | Script only |
| `storyboard` | research → location_scout → trend_analyzer → script_writer → image_generator | Storyboard frames |
| `video` | research → location_scout → trend_analyzer → script_writer → image_generator → voiceover → music | Full video (legacy) |
| `pdf` | research → trend_analyzer → script_writer → image_generator → cost_estimator → location_scout → pdf_builder | PDF package |
| `full` | research → trend_analyzer → script_writer → image_generator → voiceover → music → cost_estimator → location_scout → pdf_builder | Everything |
| `audio_package` | research → location_scout → trend_analyzer → script_writer → voiceover → music → audio_mixer → social_media | Audio only (no video) |
| `preproduction` | research → location_scout → trend_analyzer → script_writer → cost_estimator → social_media | Planning only |
| `full_no_visual` | research → location_scout → trend_analyzer → script_writer → voiceover → music → audio_mixer → cost_estimator → social_media | Full minus images |
| `storyboard_video` | research → location_scout → trend_analyzer → script_writer → image_generator → video_assembly → cost_estimator → social_media | **DEFAULT** Ken Burns video (silent) |
| `viral_video` | research → trend_analyzer → script_writer → veo3_generator → lyria_music → viral_video_assembler | TikTok/Reels with audio |
| `viral_video_test` | script_writer → veo3_generator → lyria_music → viral_video_assembler | Quick test (no research) |

### Detailed Agent Descriptions

| Agent | File | Purpose | Input | Output |
|-------|------|---------|-------|--------|
| **Research** | `agents/enhanced_research.py` | Runs Marky workflow for competitor/review/trend research | product, industry, city | competitor_details, customer_voice, keyword_trends, competitor_map_path |
| **Location Scout** | `agents/location_scout.py` | Finds filming locations via Google Places | city | locations list with addresses |
| **Trend Analyzer** | `agents/trend_analyzer.py` | Analyzes viral trends and hooks | research data | viral_patterns, recommended_hooks |
| **Script Writer** | `agents/script_writer.py` | Writes ad script with scenes | research, trends | scenes[], voiceover_text |
| **Image Generator** | `agents/image_generator.py` | Generates storyboard frames via Imagen | script scenes | frame images (hand-drawn style) |
| **Voiceover** | `agents/voiceover_agent.py` | Generates voiceover via ElevenLabs | script | audio file |
| **Music** | `agents/music_agent.py` | Selects/generates background music | tone | audio file |
| **Video Assembly** | `agents/video_assembly_agent.py` | Ken Burns animation from frames | images, audio | silent video |
| **Cost Estimator** | `agents/cost_estimator.py` | Estimates production costs | all previous | budget breakdown |
| **Social Media** | `agents/social_media_agent.py` | Generates hashtags/captions | script, research | platform-specific content |
| **PDF Builder** | `agents/pdf_builder.py` | Builds campaign PDF package | all previous | PDF file with map, diagram |
| **VEO 3 Generator** | `agents/veo3_agent.py` | Generates photorealistic video | script | video file (or placeholder) |
| **Lyria Music** | `agents/lyria_agent.py` | Generates AI music | tone, duration | audio file (or mock) |
| **Viral Assembler** | `agents/viral_video_assembler.py` | Combines video + music + TTS | veo3, lyria, script | final viral video |

### Marky Research Sub-Agents (from `orchestrator/workflow.py`)

The Research agent internally runs these Marky sub-agents:

1. **LocalIntelAgent** (`local_intel/agent.py`) - Discovers competitors via SerpAPI, scrapes websites
2. **ReviewIntelAgent** (`review_intel/agent.py`) - Fetches Google Reviews for competitors
3. **YelpIntelAgent** (`yelp_intel/agent.py`) - Fetches Yelp reviews, extracts pain/praise
4. **TrendsIntelAgent** (`trends_intel/agent.py`) - Gets keyword trends from DataForSEO
5. **RelatedQuestionsAgent** (`related_questions_intel/agent.py`) - "People also ask" queries

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                     │
│              (Business Name, Industry, City, Tone, Duration)             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RESEARCH PHASE                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ LocalIntel  │ │ ReviewIntel │ │  YelpIntel  │ │ TrendsIntel │       │
│  │ (SerpAPI)   │ │ (Google)    │ │   (Yelp)    │ │ (DataForSEO)│       │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘       │
│         └───────────────┴───────────────┴───────────────┘               │
│                                 │                                        │
│                    ┌────────────▼────────────┐                          │
│                    │   Competitor Map Gen    │                          │
│                    │  (Google Static Maps)   │                          │
│                    └────────────┬────────────┘                          │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  SCRIPT WRITER  │    │ LOCATION SCOUT  │    │ TREND ANALYZER  │
│    (Gemini)     │    │ (Google Places) │    │    (Gemini)     │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ IMAGE GENERATOR │    │  VEO 3 AGENT    │    │  COST ESTIMATOR │
│    (Imagen 3)   │    │  (Placeholder)  │    │    (Gemini)     │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         ▼                      ▼                      │
┌─────────────────┐    ┌─────────────────┐             │
│ VIDEO ASSEMBLY  │    │  LYRIA MUSIC    │             │
│  (Ken Burns)    │    │    (Mock)       │             │
└────────┬────────┘    └────────┬────────┘             │
         │                      │                      │
         │              ┌───────▼───────┐              │
         │              │ VIRAL VIDEO   │              │
         │              │  ASSEMBLER    │              │
         │              │ (Google TTS)  │              │
         │              └───────┬───────┘              │
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          PDF BUILDER                                     │
│  • Pipeline Diagram (agent flow visualization)                          │
│  • Competitor Map (Google Static Maps image)                            │
│  • Research Summary (competitors, reviews, keywords)                    │
│  • Script & Storyboard Frames                                           │
│  • Cost Breakdown & Timeline                                            │
│  • Social Media Strategy                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           FINAL OUTPUT                                   │
│  • PDF Campaign Package (with map + diagram)                            │
│  • Storyboard Video (silent, Ken Burns)                                 │
│  • Viral Video (with music + TTS) [when VEO 3 enabled]                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Known Issues & Gotchas

### Moviepy v1 vs v2 Compatibility
The codebase uses moviepy v2 API. If you see errors like `subclip not found`, check:
- `subclip()` → `subclipped()` in v2
- `volumex()` → `with_volume_scaled()` in v2
- `set_audio()` → `with_audio()` in v2
- `write_videofile()` doesn't accept `verbose` or `logger` in v2

### Google TTS Voice Quality
- Neural2 voices sound robotic
- Studio voices (en-US-Studio-O, en-US-Studio-Q) are more natural but cost more
- Casual voices (en-US-Casual-K) good for energetic tones
- Use SSML with `<break>` tags for natural pacing

### Mock Music Bug (FIXED)
Previously, mock music was copying voiceover files causing voice overlap. Fixed by filtering:
```python
existing_music = [f for f in files if "music" in f.name.lower() and "voiceover" not in f.name.lower()]
```

### Agent Signature Requirements
All agents must accept these parameters (even if unused):
```python
async def run(self, product, industry, duration, tone, city, previous_results, **kwargs)
```

### File Upload (Google Drive / tmpfiles.org)
- **Google Drive**: Set `GDRIVE_DEFAULT_FOLDER_ID` + OAuth (see docs/MCP_AGENT.md). Permanent links.
- **tmpfiles.org fallback**: Files expire after ~1 hour. Use direct URL: `tmpfiles.org/dl/ID/file`
- May fail silently - check return value

---

*Last Updated: February 1, 2026 (Night)*
*Hack@Brown 2026 - AdBoard AI Team*
