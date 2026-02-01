# AdBoard AI - Master Context Restore

> **Snapshot Date:** February 2026 (Current)
> **System Status:** STABLE - Agentverse Deployed, Google Drive Upload Working
> **Latest:** Dual-package messaging, natural language UX, ASI:One preview, competitor map, rate-limited image gen

---

## 0. Quick Reference

### Critical Files
| Category | File | Purpose |
|----------|------|---------|
| **Entry Point** | `agents/orchestrator.py` | ASI:One/Agentverse, Chat Protocol, pipeline runner |
| **Pipeline Runner** | `core/pipeline.py` | Agent sequences, progress callbacks |
| **LLM Client** | `core/gemini_client.py` | Google Gemini API (Vertex AI) |
| **Intent Parser** | `core/intent_extractor.py` | Parses user messages → structured intent |
| **Drive Upload** | `utils/gdrive_upload.py` | Uploads videos/PDFs to Google Drive |
| **Marky Workflow** | `orchestrator/workflow.py` | Research sub-agent orchestration |
| **Map Generator** | `utils/map_generator.py` | Competitor map with legend/border |
| **Flowchart** | `docs/AGENT_FLOWCHART.md` | Agent orchestration diagram (Mermaid) |

### Run Commands
| Command | Purpose |
|---------|---------|
| `python agents/orchestrator.py` | Start agent for Agentverse (keep running) |
| `python run_example.py "Create ad for my coffee shop"` | Full pipeline from CLI |
| `python run_e2e_test.py` | Test Drive upload only (uses existing files in output/) |

---

## 1. Project Overview

**AdBoard AI** is a multi-agent system for the Fetch.AI track at Hack@Brown 2026. It generates full ad campaigns for local businesses.

### Value Proposition
We create **two packages**:

1. **Storyboard package** — Concept video + full production brief (script, costs, locations, hiring guide) so clients can develop and film the real ad.
2. **Viral video** — Ready-to-post short clip for TikTok and Reels while they develop the full production.

### Input / Output
- **Input:** Natural language (e.g. "Create an ad campaign for my taco truck in Providence")
- **Output:** Storyboard video + PDF (storyboard_video pipeline) + optionally viral video (viral_video pipeline)

### Problem Solved
Small businesses can't afford $5K–50K for agency storyboarding and campaign planning. AdBoard delivers both a development package and a ready-to-post viral clip.

---

## 2. How Everything Works

### High-Level Flow
```
User (ASI:One / Agentverse chat)
    → orchestrator.py (Chat Protocol)
    → intent_extractor.py (Gemini: product, industry, output_type, duration, tone, city)
    → pipeline.py (runs agent sequence with progress callbacks)
    → format_results() uploads video + PDF to Drive (or tmpfiles fallback)
    → extract_video_thumbnail() for ASI:One preview
    → create_preview_response() or create_response()
    → Response sent back: thumbnail + "View Full Video Here" + "View Full Analysis PDF"
```

### Messaging (Natural Language, No Emojis)
- **Kick-off:** "Got it. I'm putting together your ad campaign for {product}—a storyboard package with everything you need to hire and produce the real ad, plus a viral video you can post. This takes a few minutes. I'll check in as I go."
- **Progress:** Sent after each pipeline step (e.g. "Research done. Writing your script.", "Storyboard frames are done. Assembling the concept video.")
- **Final:** Minimal — thumbnail image + "View Full Video Here: {url}" + "View Full Analysis PDF: {url}" (+ "View Viral Video Here" when present)

### File Upload
- **Primary:** Google Drive when `GDRIVE_DEFAULT_FOLDER_ID` is set + OAuth complete
- **Fallback:** tmpfiles.org (1hr expiry) if Drive not configured or fails
- **Logic:** `upload_file()` in orchestrator tries Drive first, then `upload_file_to_tmpfiles()`
- **Setup:** See `docs/MCP_AGENT.md` — credentials.json, oauth_tokens.json, folder ID in .env

### Orchestrator Modes
| Mode | Env | Behavior |
|------|-----|----------|
| Production | (default) | Full pipeline, Drive upload, progress messages |
| TEST_MODE | `true` | Echo response, no pipeline |
| MOCK_MODE | `true` | Instant mock data, no pipeline |

### Default Output Type
User says "video" or "storyboard video" → `storyboard_video` pipeline.

---

## 3. Pipelines (core/pipeline.py)

| Pipeline | Use Case |
|----------|----------|
| **storyboard_video** | **DEFAULT** — research → script → images → video → cost → social → PDF |
| script | Script only |
| storyboard | Script + images, no video |
| pdf | PDF package (no video) |
| full | Everything (voiceover, music, PDF) |
| viral_video | VEO 3 + Lyria + TTS (placeholder/mock) |
| viral_video_test | Viral pipeline without research |
| quick_test | Dummy research → script → images → video → PDF (no Marky, faster) |
| audio_package | Voiceover + music, no video |
| preproduction | Research + script + cost + social |
| full_no_visual | Full minus images/video |

**quick_test** injects dummy research/trends/location — skips slow Marky workflow. Use for fast iteration.

### Progress Messages (PROGRESS_MESSAGES)
Sent after each step: research, location_scout, trend_analyzer, script_writer, image_generator, video_assembly, cost_estimator, social_media, pdf_builder. Viral pipeline: veo3_generator, lyria_music, viral_video_assembler.

---

## 4. Agent Roster

| Agent | File | Purpose |
|-------|------|---------|
| Research | `enhanced_research.py` | Marky workflow: competitors, reviews, trends, competitor map |
| Location Scout | `location_scout.py` | Google Places filming locations |
| Trend Analyzer | `trend_analyzer.py` | Viral patterns, hooks (Gemini) |
| Script Writer | `script_writer.py` | Ad script for storyboard + viral (Gemini) |
| Image Generator | `image_generator.py` | Imagen 3 storyboard frames (30s delay between calls) |
| Video Assembly | `video_assembly_agent.py` | Ken Burns from frames (FFmpeg) |
| Voiceover | `voiceover_agent.py` | ElevenLabs |
| Music | `music_agent.py` | Background music (Gemini) |
| Audio Mixer | `audio_mixer.py` | Mix voiceover + music |
| Cost Estimator | `cost_estimator.py` | Budget breakdown (Gemini) |
| Social Media | `social_media_agent.py` | Hashtags, captions (Gemini) |
| PDF Builder | `pdf_builder.py` | Campaign PDF with map, script, budget, hiring guide |
| VEO 3 | `veo3_agent.py` | Photorealistic video (placeholder) |
| Lyria | `lyria_agent.py` | AI music (mock) |
| Viral Assembler | `viral_video_assembler.py` | Video + music + Google TTS |

**Marky sub-agents** (enhanced_research): LocalIntel (SerpAPI), ReviewIntel (Google), YelpIntel, GoogleTrendsAgent, RelatedQuestions

---

## 5. Key Features & Implementation

### ASI:One Image Preview
- **extract_video_thumbnail()** — Tries frames 0, 1, 2, 3, ~1s; skips black frames (brightness < 15); uses OpenCV
- **upload_to_agentverse_storage()** — Uploads thumbnail to Agentverse External Storage
- **create_preview_response()** — ChatMessage with ResourceContent (thumbnail) + TextContent (links)

### Competitor Map
- **utils/map_generator.py** — Google Static Maps API; Pillow post-process adds title bar, legend, border
- **competitor_map_path** in research → passed to pdf_builder
- **CompetitorInsight.address** — Workflow passes address from local_intel for map markers

### Image Generation Rate Limits
- **IMAGE_DELAY_SECONDS** — 30s between each Imagen call (configurable via `IMAGEN_DELAY_SECONDS` in .env)
- Prevents quota/rate-limit failures

### format_results
- Returns `{text, video_url, pdf_url, video_path}` (minimal text; details in PDF)
- Links: "View Full Video Here", "View Full Analysis PDF", "View Viral Video Here" (when present)

---

## 6. File Structure

```
Brown/
├── agents/
│   ├── orchestrator.py          # Main entry, Chat Protocol, preview
│   ├── enhanced_research.py     # Research (Marky) + competitor map
│   ├── script_writer.py
│   ├── image_generator.py       # Imagen 3, 30s delay
│   ├── video_assembly_agent.py
│   ├── pdf_builder.py
│   ├── cost_estimator.py
│   ├── location_scout.py
│   ├── social_media_agent.py
│   ├── voiceover_agent.py
│   ├── music_agent.py
│   ├── audio_mixer.py
│   ├── veo3_agent.py
│   ├── lyria_agent.py
│   ├── viral_video_assembler.py
│   ├── campaign_strategy_content.py
│   ├── mock_response.py
│   └── models.py
├── core/
│   ├── pipeline.py              # Pipelines, progress callbacks
│   ├── intent_extractor.py      # Dual-package framing
│   ├── gemini_client.py
│   ├── groq_client.py
│   └── dummy_research.py
├── orchestrator/
│   ├── workflow.py              # Marky workflow
│   ├── agent.py
│   └── models.py                # CompetitorInsight has address
├── utils/
│   ├── gdrive_upload.py
│   └── map_generator.py         # Title, legend, border
├── docs/
│   ├── AGENT_FLOWCHART.md
│   ├── agent_flowchart.mmd
│   ├── MCP_AGENT.md
│   ├── ASI_ONE_VIDEO_PREVIEW.md
│   └── ...
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
# credentials.json + oauth_tokens.json in mcp-agents/gdrive-pdf-upload-mcp-agent/
```

### Image Generation
```bash
IMAGEN_DELAY_SECONDS=30   # Seconds between Imagen API calls (default 30)
```

### Research
SERPAPI_KEY, YOUTUBE_API_KEY, GOOGLE_PLACES_API_KEY (or GOOGLE_MAPS_API_KEY)

### Optional
ELEVENLABS_API_KEY, GROQ_API_KEY, REPLICATE_API_TOKEN, TOGETHER_API_KEY

---

## 8. What's Been Done (Complete)

### UX & Messaging
- Natural language, no emojis in user-facing text
- Kick-off: describes storyboard + viral packages
- Progress check-ins during pipeline
- Minimal final output: thumbnail + 2–3 links

### ASI:One Preview
- Video thumbnail extracted (non-black frame)
- Uploaded to Agentverse External Storage
- ResourceContent displays inline
- create_preview_response() for thumbnail + links

### Dual-Package Framing
- README, intro, kick-off, progress, intent extractor
- Script writer knows it feeds storyboard + viral
- Campaign strategy PDF describes both packages
- format_results labels: storyboard video, PDF, viral video

### Competitor Map
- Title bar, legend, border (Pillow post-process)
- CompetitorInsight.address from workflow
- Map included in PDF

### Technical
- Google Drive as primary upload; tmpfiles fallback
- 30s delay between Imagen calls (IMAGEN_DELAY_SECONDS)
- Pipeline progress_callback for check-in messages
- Agent flowchart (docs/AGENT_FLOWCHART.md)

---

## 9. What's Next

### Hackathon
1. Demo video (3–5 min) — ASI:One discovery, full request, Drive links
2. Deploy to cloud — 24/7 uptime
3. README — Agent address, badges, demo link

### Optional
- Real VEO 3 + Lyria (placeholders now)
- Payment Protocol
- TTS quality (Studio/WaveNet)

---

## 10. Known Issues

- **Moviepy v2** — Use `subclipped()`, `with_volume_scaled()`, `with_audio()`
- **Agent must stay running** — Local orchestrator stops when terminal closes
- **Drive OAuth** — Token refreshes on 401; first run may show "Refreshing credentials"
- **Black thumbnails** — Fixed by trying multiple frames, skipping black (brightness < 15)

---

## 11. Agent Address

Search "AdBoard AI" on [agentverse.ai](https://agentverse.ai). Run `python agents/orchestrator.py` to start. Address printed on startup.

---

*Last Updated: February 2026*
*Hack@Brown 2026 - AdBoard AI - Fetch.AI Track*
