# AdBoard AI / AdVantage — Master Context Restore

> **Snapshot Date:** February 2026 (Current)
> **System Status:** STABLE - Agentverse Deployed, Full Pipeline with Research + VEO 3
> **Product Name:** AdVantage (Devpost), AdBoard AI (codebase)

---

## 0. Quick Reference

### Critical Files
| Category | File | Purpose |
|----------|------|---------|
| **Entry Point** | `agents/orchestrator.py` | ASI:One/Agentverse, Chat Protocol, pipeline runner, preview logic |
| **Pipeline Runner** | `core/pipeline.py` | Agent sequences, progress callbacks, dummy research injection |
| **LLM Client** | `core/gemini_client.py` | Google Gemini API (Vertex AI), fallback chain |
| **Intent Parser** | `core/intent_extractor.py` | Parses user messages → structured intent (product, industry, output_type, etc.) |
| **Drive Upload** | `utils/gdrive_upload.py` | Uploads videos/PDFs/images to Google Drive; direct embed URLs for images |
| **Marky Workflow** | `orchestrator/workflow.py` | Research sub-agent orchestration |
| **Map Generator** | `utils/map_generator.py` | Competitor map with title, legend, border (Google Static Maps + Pillow) |
| **Flowchart** | `docs/AGENT_FLOWCHART.md` | Agent orchestration diagram (Mermaid) |
| **Orchestration ref** | `docs/AGENT_ORCHESTRATION.md` | Full data-flow: inputs, outputs, order |
| **Agentverse readiness** | `docs/AGENTVERSE_READINESS.md` | Checklist for deployment |

### Run Commands
| Command | Purpose |
|---------|---------|
| `python agents/orchestrator.py` | Start agent for Agentverse (keep running) |
| `python run_example.py "Create ad for my coffee shop"` | Full pipeline from CLI |
| `python run_example.py --quick "..."` | Quick mode (skip research, dummy data) |
| `python run_e2e_test.py` | Test Drive upload only (uses existing files in output/) |

---

## 1. Project Overview

**AdBoard AI / AdVantage** is a multi-agent system for the Fetch.AI track at Hack@Brown 2026. It generates full ad campaigns for local businesses.

### Value Proposition
We create **three deliverables**:

1. **Storyboard video** — Concept video with TTS + music for development and pitching. Shows the visual flow so clients can hire a crew and film the real ad.
2. **Viral video** — Ready-to-post short clip (VEO 3 or placeholder) with music and voiceover for TikTok and Reels.
3. **Campaign PDF** — Full production brief with research, script, cost estimates, filming locations, competitor map, and hiring guide.

### Input / Output
- **Input:** Natural language (e.g. "Create an ad campaign for my plumbing business in New York City")
- **Output:** Storyboard video + Viral video + PDF — all three with public links (Drive or tmpfiles)

### Problem Solved
Small businesses can't afford $5K–50K for agency storyboarding and campaign planning. AdVantage delivers both a development package and a ready-to-post viral clip.

---

## 2. How Everything Works

### High-Level Flow
```
User (ASI:One / Agentverse chat)
    → orchestrator.py (Chat Protocol)
    → intent_extractor.py (Gemini: product, industry, output_type, duration, tone, city)
    → pipeline.py (runs agent sequence with progress callbacks)
    → format_results() uploads storyboard + viral + PDF to Drive (or tmpfiles)
    → extract_video_thumbnail() → compress_thumbnail() → upload (Agentverse or Drive/tmpfiles fallback)
    → create_preview_response() with ResourceContent (thumbnail) + TextContent (links)
    → Response: preview image + "View Storyboard Video Here" + "View Viral Video Here" + "View Full Analysis PDF"
```

### Messaging (Natural Language, No Emojis)
- **Kick-off:** "Got it. I'm putting together your ad campaign for {product}—a storyboard video for development, a ready-to-post viral video, and the full campaign PDF. This takes several minutes. I'll check in as I go."
- **Progress:** Sent after each pipeline step (e.g. "Research done. Writing your script.", "Storyboard video ready. Generating viral video.")
- **Final:** Thumbnail image + "View Storyboard Video Here: {url}" + "View Viral Video Here: {url}" + "View Full Analysis PDF: {url}"

### File Upload
- **Primary:** Google Drive when `GDRIVE_DEFAULT_FOLDER_ID` is set + OAuth complete (credentials.json, oauth_tokens.json)
- **Fallback:** tmpfiles.org (1hr expiry) if Drive not configured or fails
- **Logic:** `upload_file()` in orchestrator tries Drive first, then `upload_file_to_tmpfiles()`
- **Images:** Drive uploads images with `permissions().create(type="anyone", role="reader")` and returns direct embed URL (`https://drive.google.com/uc?export=view&id=...`)

### Orchestrator Modes
| Mode | Env | Behavior |
|------|-----|----------|
| Production | (default) | Full pipeline, Drive upload, progress messages |
| TEST_MODE | `true` | Echo response, no pipeline |
| MOCK_MODE | `true` | Instant mock data, no pipeline |

### Pipeline Override (QUICK_FULL)
- **QUICK_FULL=true** → Forces `quick_full` pipeline (skips research, uses dummy data)
- **QUICK_FULL=false** → Uses intent's output_type (typically `full_campaign` with real research)
- User message "quick test" or "test without research" also forces quick_full

### Default Output Type
**full_campaign** — all three deliverables. User says "video", "full", or "viral" → full_campaign.

---

## 3. Pipelines (core/pipeline.py)

| Pipeline | Use Case |
|----------|----------|
| **full_campaign** | **DEFAULT** — Research → script → images → lyria + voiceover + audio_mixer → storyboard video (with audio) → VEO 3 → viral video → cost → social → PDF |
| **quick_full** | Skips research (dummy data), same as full_campaign otherwise. Triggered by QUICK_FULL=true or "quick test" |
| **storyboard_video** | Storyboard (silent, from images) + PDF only (no viral) |
| **quick_test** | Dummy research → script → images → video → PDF (no viral, no lyria/voiceover) |
| **script** | Script only |
| **storyboard** | Script + images, no video |
| **pdf** | PDF package (no video) |
| **viral_video** | VEO 3 + Lyria + TTS only |
| **viral_video_test** | Viral pipeline without research |
| **audio_package** | Voiceover + music, no video |
| **preproduction** | Research + script + cost + social |
| **full_no_visual** | Full minus images/video |

### full_campaign Pipeline Order
1. research (Marky workflow)
2. location_scout
3. trend_analyzer
4. script_writer
5. image_generator (or skipped if STORYBOARD_VIDEO_PATH / VEO_PLACEHOLDER_PATH set)
6. lyria_music
7. voiceover (Google TTS)
8. audio_mixer (voiceover + music)
9. video_assembly (storyboard video with audio)
10. veo3_generator (VEO 3 or placeholder)
11. viral_video_assembler (viral video with audio)
12. cost_estimator
13. social_media
14. pdf_builder

### Conditional Skipping
- **image_generator:** Skipped when `STORYBOARD_VIDEO_PATH` or `VEO_PLACEHOLDER_PATH` is set and file exists → uses sample video for storyboard
- **research/location_scout/trend_analyzer:** Replaced with dummy data when output_type is `quick_test` or `quick_full`

---

## 4. Agent Roster

| Agent | File | Purpose |
|-------|------|---------|
| Research | `enhanced_research.py` | Marky workflow: competitors (SerpAPI), reviews, Yelp, Google Trends; competitor map |
| Location Scout | `location_scout.py` | Google Places filming locations |
| Trend Analyzer | `trend_analyzer.py` | Viral patterns, hooks (Gemini) |
| Script Writer | `script_writer.py` | Ad script for storyboard + viral (Gemini) |
| Image Generator | `image_generator.py` | Imagen 3 storyboard frames (30s delay between calls) |
| Lyria | `lyria_agent.py` | AI music (mock/silent placeholder) |
| Voiceover | `voiceover_agent.py` | **Google Cloud TTS** (Studio voices, SSML) |
| Audio Mixer | `audio_mixer.py` | Mix voiceover + Lyria music |
| Video Assembly | `video_assembly_agent.py` | Ken Burns from images, or copy sample; adds mixed audio to storyboard |
| VEO 3 | `veo3_agent.py` | Photorealistic video via google-genai; placeholder when VEO_USE_PLACEHOLDER=true |
| Viral Assembler | `viral_video_assembler.py` | Combines VEO video + Lyria + Google TTS |
| Cost Estimator | `cost_estimator.py` | Budget breakdown (Gemini) |
| Social Media | `social_media_agent.py` | Hashtags, captions (Gemini) |
| PDF Builder | `pdf_builder.py` | Campaign PDF with map, script, budget, hiring guide, agent_architecture_diagram.png |

**Marky sub-agents** (enhanced_research): LocalIntel (SerpAPI), ReviewIntel (Google), YelpIntel, GoogleTrendsAgent, RelatedQuestions

---

## 5. Key Features & Implementation

### ASI:One Preview Image (Critical)
- **extract_video_thumbnail()** — Tries frames 0, 1, 2, 3, ~1s; skips black frames (brightness < 15); uses OpenCV
- **compress_thumbnail()** — Resizes to max 640px, JPEG 85% quality (Agentverse may reject large files)
- **upload_to_agentverse_storage()** — Primary; often returns 500 Internal Server Error
- **upload_thumbnail_fallback()** — When Agentverse fails: save to temp file → upload_file() → Drive or tmpfiles → returns https URL
- **create_preview_response()** — ResourceContent (thumbnail_uri) + TextContent (links). Supports both agent-storage:// and https:// URIs
- **Fallback to frame:** If no video thumbnail, uses first storyboard frame from image_generator.frames

### VEO 3 Placeholder Logic (FIXED)
- **Previously:** Used `output/final` (storyboard) as placeholder → viral looked identical to storyboard
- **Now:** (1) VEO_PLACEHOLDER_PATH if set, (2) video_testing/YTDowncom_*.mp4, (3) existing _placeholder_ files in veo3_videos/
- **Never** uses output/final for viral placeholder

### Competitor Map
- **utils/map_generator.py** — Google Static Maps API; Pillow post-process adds title bar, legend, border
- **CompetitorInsight.address** — Workflow passes address from local_intel for map markers
- **Static Maps error handling** — Detects error images; prints guidance for Maps Static API, billing

### Image Generation
- **IMAGEN_DELAY_SECONDS** — 30s between each Imagen call (configurable)
- Prevents quota/rate-limit failures

### format_results
- Returns `{text, video_url, viral_url, pdf_url, video_path}`
- Links: "View Storyboard Video Here", "View Viral Video Here", "View Full Analysis PDF"

### PDF Builder
- Embeds `docs/agent_architecture_diagram.png` in "Agent Orchestration" section
- Falls back to `docs/pipeline_diagram.png` if architecture diagram missing
- "Your Campaign Deliverables" section when viral present: storyboard, viral, PDF

### Voiceover & TTS
- **ElevenLabs removed** — Google Cloud Text-to-Speech everywhere
- Uses same GOOGLE_APPLICATION_CREDENTIALS as Imagen/Vertex
- Studio voices (en-US-Studio-Q, etc.), SSML with rate only (no pitch for Studio)

---

## 6. File Structure

```
Brown/
├── agents/
│   ├── orchestrator.py          # Main entry, Chat Protocol, preview, compress_thumbnail, upload_thumbnail_fallback
│   ├── enhanced_research.py
│   ├── script_writer.py
│   ├── image_generator.py
│   ├── video_assembly_agent.py  # sample mode (STORYBOARD_VIDEO_PATH), storyboard mode (Ken Burns)
│   ├── pdf_builder.py
│   ├── cost_estimator.py
│   ├── location_scout.py
│   ├── social_media_agent.py
│   ├── voiceover_agent.py       # Google TTS
│   ├── music_agent.py
│   ├── audio_mixer.py
│   ├── veo3_agent.py
│   ├── lyria_agent.py
│   ├── viral_video_assembler.py
│   ├── campaign_strategy_content.py
│   ├── mock_response.py
│   └── models.py
├── core/
│   ├── pipeline.py
│   ├── intent_extractor.py
│   ├── gemini_client.py
│   ├── groq_client.py
│   └── dummy_research.py
├── orchestrator/
│   ├── workflow.py
│   ├── agent.py
│   └── models.py
├── utils/
│   ├── gdrive_upload.py         # Direct embed URL for images; permissions for public view
│   ├── map_generator.py
│   └── generate_pipeline_diagram.py
├── docs/
│   ├── agent_architecture_diagram.png
│   ├── pipeline_diagram.png
│   ├── AGENT_FLOWCHART.md
│   ├── AGENT_ORCHESTRATION.md
│   ├── AGENTVERSE_READINESS.md
│   └── ...
├── video_testing/
│   └── YTDowncom_*.mp4          # Default VEO placeholder when no VEO_PLACEHOLDER_PATH
├── mcp-agents/gdrive-pdf-upload-mcp-agent/
├── run_example.py
├── run_e2e_test.py
└── output/
```

---

## 7. Environment Variables

### Required for Agentverse
```bash
AGENT_SEED_PHRASE=your-seed
AGENTVERSE_API_KEY=your-key
```

### Required for Pipeline
```bash
GCP_PROJECT_ID=...
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Google Drive
```bash
GDRIVE_DEFAULT_FOLDER_ID=your_folder_id
GDRIVE_CREDENTIALS_PATH=.../credentials.json
GDRIVE_TOKENS_PATH=.../oauth_tokens.json
```

### Image Generation
```bash
IMAGEN_DELAY_SECONDS=30
```

### VEO 3
```bash
VEO_USE_PLACEHOLDER=false   # true = placeholder, false = real VEO 3 (~$1.50/video)
VEO_PLACEHOLDER_PATH=       # Optional: path to custom placeholder video
VEO_GCS_OUTPUT_URI=         # Optional: gs://bucket/prefix
```

### Storyboard from Sample
```bash
STORYBOARD_VIDEO_PATH=/path/to/video.mp4   # Use as storyboard, skip image_generator
# When set: pipeline skips image_generator, video_assembly uses sample
```

### Research / Quick Mode
```bash
QUICK_FULL=false            # true = skip research (quick_full), false = full research
SERPAPI_KEY=...
YOUTUBE_API_KEY=...
GOOGLE_PLACES_API_KEY=...
```

### Optional
```bash
GROQ_API_KEY=
REPLICATE_API_TOKEN=
GEMINI_MODELS=              # Override default Gemini model list
USE_PROXY=false             # Mailbox vs Proxy for Agentverse
AGENT_PORT=8000
```

### GCP APIs to Enable
- Vertex AI API
- Cloud Text-to-Speech API
- Maps Static API (competitor map)
- Places API (location scout)

---

## 8. What's Been Done (Complete)

### UX & Messaging
- Natural language, no emojis
- Kick-off describes storyboard + viral + PDF
- Progress check-ins during pipeline
- Minimal final output: thumbnail + 3 links

### ASI:One Preview
- Video thumbnail extraction (non-black frame)
- Thumbnail compression (resize, JPEG) before upload
- Agentverse External Storage (primary)
- **Drive/tmpfiles fallback** when Agentverse returns 500
- ResourceContent with https:// URI support

### Dual Deliverables
- Storyboard video (with TTS + music)
- Viral video (VEO 3 or placeholder, with TTS + music)
- Both use shared Lyria + voiceover

### VEO Placeholder Fix
- No longer reuses output/final (storyboard)
- Uses video_testing sample or VEO_PLACEHOLDER_PATH

### ElevenLabs Removed
- Google TTS everywhere (voiceover_agent, viral_video_assembler)

### Competitor Map
- Title bar, legend, border
- CompetitorInsight.address from workflow

### Technical
- Drive as primary upload; tmpfiles fallback
- Drive images: public permission + direct embed URL
- PDF embeds agent_architecture_diagram.png

---

## 9. What's Next

### Hackathon
1. Demo video (3–5 min)
2. Deploy to cloud for 24/7 uptime
3. README with agent address, badges

### Optional
- Real Lyria music generation
- Payment Protocol

---

## 10. Known Issues

- **Agentverse External Storage** — Often returns 500; we fall back to Drive/tmpfiles
- **Moviepy v2** — Use `subclipped()`, `with_volume_scaled()`, `with_audio()`
- **Agent must stay running** — Local orchestrator stops when terminal closes
- **Drive OAuth** — Token refreshes on 401; first run may show "Refreshing credentials"

---

## 11. Agent Address

Search "AdBoard AI" on [agentverse.ai](https://agentverse.ai). Run `python agents/orchestrator.py` to start. Address printed on startup.

---

*Last Updated: February 2026*
*Hack@Brown 2026 - AdVantage - Fetch.AI Track*
