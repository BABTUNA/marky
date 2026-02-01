# AdVantage — Agent Orchestration (Complete Reference)

This document describes exactly what goes into each agent, in what order, and what each one produces.

---

## 1. Entry Point (Before Pipeline)

**Orchestrator** (`agents/orchestrator.py`) receives a ChatMessage from ASI:One.

1. **Intent Extractor** (`core/intent_extractor.py`) — called with `user_text`
   - **Input:** Raw user message (e.g. "Create an ad for my sushi shop in New York")
   - **Uses:** Gemini LLM to parse structured intent
   - **Output:** `{product, industry, output_type, duration, tone, city, ready, missing}`
   - **Output type** defaults to `storyboard_video` if user says "video" or "storyboard video"

2. **Pipeline selection** — `PIPELINES[output_type]` determines the agent sequence
3. **Pipeline instantiation** — `AdBoardPipeline(product, industry, output_type, duration, tone, city)`

---

## 2. Pipeline Execution (Sequential)

Agents run **one after another**. Each agent receives:
- `product`, `industry`, `duration`, `tone`, `city` (from intent)
- `previous_results` — a dict of **all prior agents' outputs** (accumulated so far)

Results are stored in `self.results` and passed forward. There is **no parallel execution** at the pipeline level — it's strictly sequential.

---

## 3. full_campaign Pipeline (Default — All Three Deliverables)

This is the main pipeline when user wants the complete package. Order:

| Step | Agent | Inputs (from previous_results) | Output |
|------|-------|-------------------------------|--------|
| 1 | **Research** | (none) | `research` |
| 2 | **Location Scout** | (optional: research) | `location_scout` |
| 3 | **Trend Analyzer** | `research` | `trend_analyzer` |
| 4 | **Script Writer** | `research`, `trend_analyzer`, `location_scout` | `script_writer` |
| 5 | **Image Generator** | `script_writer` | `image_generator` |
| 6 | **Video Assembly** | `image_generator` | `video_assembly` (SILENT storyboard) |
| 7 | **VEO 3 Generator** | `script_writer`, `research` | `veo3_generator` |
| 8 | **Lyria Music** | `script_writer`, `research` | `lyria_music` |
| 9 | **Viral Assembler** | `veo3_generator`, `lyria_music`, `script_writer` | `viral_video_assembler` |
| 10 | **Cost Estimator** | `script_writer`, `location_scout` | `cost_estimator` |
| 11 | **Social Media** | `script_writer` | `social_media` |
| 12 | **PDF Builder** | all above + `viral_video_assembler` | `pdf_builder` |

**Output:** Storyboard video (silent), Viral video (with audio), Campaign PDF.

## 3b. storyboard_video Pipeline (Storyboard + PDF only, no viral)

Same as full_campaign but stops after step 6; no VEO 3, Lyria, or viral assembler.

---

## 4. Agent Details (Inputs → Outputs)

### 4.1 Research (`enhanced_research.py`)

**Inputs:** `product`, `industry`, `city` (from intent). No previous_results.

**Internal flow (Marky workflow — runs sequentially; architecture diagrams often show as parallel for clarity):**
1. **Local Intel** — SerpAPI + competitor discovery → competitors, differentiators, headlines
2. **Review Intel** — Google Reviews (needs place_ids from Local Intel) → customer voice, pain points, desires
3. **Yelp Intel** — Yelp reviews → merged into customer voice
4. **Google Trends** — Keyword trends, seasonal data
5. **Related Questions** — "People also ask" queries
6. **Competitor Map** — `generate_competitor_map_from_research()` if city + competitor_details → PNG path

**Output:** Dict with `local_intel`, `google_reviews`, `yelp_reviews`, `keyword_trends`, `insights`, `competitor_map_path`, `research_summary`, etc.

---

### 4.2 Location Scout (`location_scout.py`)

**Inputs:** `product`, `industry`, `city`. Optionally uses `research` (but typically runs on city + product).

**Output:** `{locations: [{name, address, types, ...}], ...}`

---

### 4.3 Trend Analyzer (`trend_analyzer.py`)

**Inputs:** `previous_results["research"]`

**Output:** `{analysis: {recommended_hook, ad_structure, visual_style, cta, key_messages}, viral_patterns, recommended_hooks, ...}`

---

### 4.4 Script Writer (`script_writer.py`)

**Inputs:**
- `previous_results["trend_analyzer"]` — recommended hook, ad structure, visual style, CTA
- `previous_results["research"]` — insights, competitor hooks, customer voice, keyword trends, related questions
- `previous_results["location_scout"]` — filming location for setting

**Output:** `{scenes: [{scene_number, timing, title, visual, audio, voiceover}], voiceover_text, model_used}`

---

### 4.5 Image Generator (`image_generator.py`)

**Inputs:** `previous_results["script_writer"]["scenes"]`

- For each scene: `scene["visual"]` → fed into `_build_image_prompt()` → Imagen 3
- 30s delay between each image call (rate limit)

**Output:** `{frames: [{scene_number, timing, path, image_base64, prompt_used, description}], total_generated, model}`

---

### 4.6 Video Assembly (`video_assembly_agent.py`)

**Inputs:**
- `previous_results["image_generator"]["frames"]` — list of image paths
- (Optional) `voiceover`, `audio_mixer`, `music` — for audio track

**Mode:** "storyboard" (no VEO clips) — converts images to video with Ken Burns effects via FFmpeg. Silent if no audio.

**Output:** `{final_video_path, duration, resolution, frames_used}`

---

### 4.7 Cost Estimator (`cost_estimator.py`)

**Inputs:**
- `previous_results["script_writer"]["scenes"]` — number of scenes, complexity
- `previous_results["location_scout"]["locations"]` — for location costs

**Output:** `{total, line_items: [{category, item, cost}], breakdown}`

---

### 4.8 Social Media (`social_media_agent.py`)

**Inputs:** `previous_results["script_writer"]["scenes"]` — scene summary for captions

**Output:** `{hashtags: {primary, secondary}, captions: {platform: caption}, ...}`

---

### 4.9 PDF Builder (`pdf_builder.py`)

**Inputs:** (all of the above)
- `research` — competitor map path, insights, local_intel
- `script_writer` — scenes, voiceover
- `image_generator` — frame paths for embedding
- `cost_estimator` — line items, total
- `location_scout` — filming locations
- `video_assembly` — metadata
- `social_media` — hashtags, captions

**Output:** `{pdf_path, pages, includes}` — writes PDF to disk

---

## 5. Post-Pipeline (Orchestrator)

After `pipeline.run()` returns:

1. **format_results()** — Collects `video_assembly.final_video_path`, `pdf_builder.pdf_path`
2. **Upload** — `upload_file()` → Google Drive (or tmpfiles.org fallback)
3. **Thumbnail** — `extract_video_thumbnail(video_path)` → first non-black frame, uploaded to Agentverse External Storage
4. **Response** — `create_preview_response(thumbnail_uri, video_url, pdf_url, text)` or `create_response(text)` → sent to user via ASI:One

---

## 6. viral_video Pipeline (Separate)

Runs when `output_type == "viral_video"`:

| Step | Agent | Inputs | Output |
|------|-------|--------|--------|
| 1 | Research | — | research |
| 2 | Trend Analyzer | research | trend_analyzer |
| 3 | Script Writer | research, trend_analyzer | script_writer |
| 4 | VEO 3 Generator | script_writer, research | veo3_generator |
| 5 | Lyria Music | research, script_writer | lyria_music |
| 6 | Viral Assembler | veo3_generator, lyria_music, script_writer | viral_video_assembler |

No location_scout, image_generator, video_assembly, cost_estimator, social_media, or pdf_builder in this pipeline.

---

## 7. quick_test Pipeline (No Research)

Injects dummy data and skips Research, Location Scout, Trend Analyzer:

- `research` ← `get_dummy_research(industry, product)`
- `trend_analyzer` ← synthetic viral_patterns, recommended_hooks
- `location_scout` ← `[{name: "Downtown", address: "Providence, RI"}]`

Then runs: script_writer → image_generator → video_assembly → cost_estimator → social_media → pdf_builder

---

## 8. Data Flow Summary

```
Intent (product, industry, duration, tone, city, output_type)
    │
    ▼
Research (Marky: Local → Review → Yelp → Trends → Related → Map)
    │
    ▼
Location Scout (Google Places, city)
    │
    ▼
Trend Analyzer (research → Gemini)
    │
    ▼
Script Writer (research + trend_analyzer + location_scout → Gemini)
    │
    ▼
Image Generator (script_writer.scenes → Imagen 3, one frame per scene)
    │
    ▼
Video Assembly (image_generator.frames → FFmpeg Ken Burns → MP4)
    │
    ▼
Cost Estimator (script_writer + location_scout → Gemini)
    │
    ▼
Social Media (script_writer → Gemini)
    │
    ▼
PDF Builder (research, script, images, cost, location, video meta, social → ReportLab)
    │
    ▼
Upload (Drive) → Thumbnail (OpenCV) → Response (ASI:One)
```

---

*Last updated: February 2026*
