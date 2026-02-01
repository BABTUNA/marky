# AdBoard AI - Context Restore File
**Last Updated:** January 31, 2026 (Evening)
**Session Summary:** Integrated teammate's Marky research agents including new Related Questions Intel

---

## Current State

### What's Working
1. **Full Marky Research Suite** - All 6 research agents are integrated and working:
   - YouTube viral ad analysis (finds 5+ videos)
   - Local Intel (competitor discovery, website scraping, Claude success/failure analysis)
   - Google Reviews (40+ reviews analyzed via place_ids)
   - Yelp Reviews (65+ reviews with pain/praise extraction)
   - Trends Intel (keyword data from DataForSEO)
   - Related Questions Intel (People also ask questions for content intent)

2. **Video Generation Pipeline** - Complete storyboard_video pipeline works:
   - Research → Location Scout → Trend Analyzer → Script Writer → Image Generator → Voiceover → Music → Video Assembly

3. **Interactive Runner** - `run_example.py` accepts natural language prompts

### Key Files Modified This Session

#### `/agents/enhanced_research.py` (COMPLETELY REWRITTEN)
- Now imports and uses teammate's Marky agents:
  - `local_intel.agent.LocalIntelAgent`
  - `review_intel.agent.ReviewIntelAgent`
  - `yelp_intel.agent.YelpIntelAgent`
  - `trends_intel.agent.TrendsIntelAgent`
- Runs 5-stage research pipeline
- Extracts Claude's success/failure analysis from local_intel
- Combines all insights for script writer

#### `/run_example.py` (NEW)
- Interactive CLI for running the pipeline
- Accepts prompts like: `python run_example.py "Create a 30 second ad for my pizza restaurant in Boston"`
- Uses intent extraction to parse natural language
- Shows research summary and generated script

#### Files Pulled from Teammate's `main` Branch
- `local_intel/` - Full competitor intelligence suite
- `review_intel/` - Google Reviews agent
- `yelp_intel/` - Yelp reviews agent
- `trends_intel/` - DataForSEO trends agent
- `related_questions_intel/` - Google "People also ask" questions agent (NEW)
- `orchestrator/` - Marky workflow orchestrator
- `run_marky.py` - Standalone Marky runner

#### `/ad_intel_no/agent.py` (ENHANCED)
- Improved `_generate_search_queries()` to find national brand ads (Domino's, Pizza Hut, etc.)
- Added `_analyze_top_bottom_competitors()` for success/failure classification
- Added `_get_fallback_analysis()` with industry-specific insights
- Added `_get_industry_top_brands()` for known leaders

#### `/ad_intel_no/models.py` (UPDATED)
- Added fields to `AdAnalysis`:
  - `top_competitors: List[str]`
  - `what_top_competitors_do: List[str]`
  - `bottom_competitors: List[str]`
  - `what_to_avoid: List[str]`

#### `/ad_intel_no/trends_intel.py` (ENHANCED)
- Improved `_get_fallback_analysis()` with industry-specific keyword data
- Added fallback when API returns no data

#### `/agents/research_agent.py` (ENHANCED)
- Improved `_generate_search_queries()` for better YouTube video discovery
- Industry-specific search strategies
- Fallback queries that always return results

#### `/agents/script_writer.py` (ENHANCED)
- Now includes "LEARN FROM TOP COMPETITORS" section
- Now includes "AVOID THESE MISTAKES" section
- Uses customer voice from reviews

---

## Architecture Overview

```
User Prompt
    │
    ▼
Intent Extractor (core/intent_extractor.py)
    │
    ▼
Pipeline Runner (core/pipeline.py)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH STAGE                            │
│  EnhancedResearchAgent (agents/enhanced_research.py)         │
│                                                              │
│  [1/6] YouTube Research (agents/research_agent.py)           │
│        → Viral ad patterns, hooks, visual styles             │
│                                                              │
│  [2/6] Local Intel (local_intel/agent.py)                    │
│        → Competitor discovery via SerpAPI                    │
│        → Website scraping (services, trust signals)          │
│        → Claude analysis (success vs failure patterns)       │
│                                                              │
│  [3/6] Review Intel (review_intel/agent.py)                  │
│        → Google Reviews via place_ids                        │
│        → Pain points, desires, customer quotes               │
│        → Ad hooks and headlines                              │
│                                                              │
│  [4/6] Yelp Intel (yelp_intel/agent.py)                      │
│        → Yelp reviews with sentiment analysis                │
│        → Pain points and praise extraction                   │
│        → Customer themes and phrases                         │
│                                                              │
│  [5/6] Trends Intel (trends_intel/agent.py)                  │
│        → DataForSEO keyword data                             │
│        → Search volume, CPC, competition                     │
│        → Seasonal timing insights                            │
│                                                              │
│  [6/6] Related Questions Intel (related_questions_intel/)    │
│        → Google "People also ask" questions                  │
│        → Content intent and FAQ opportunities                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                  PRODUCTION STAGES                           │
│                                                              │
│  Location Scout → Trend Analyzer → Script Writer             │
│        ↓                                                     │
│  Image Generator (Vertex AI Imagen)                          │
│        ↓                                                     │
│  Voiceover (Google Cloud TTS)                                │
│        ↓                                                     │
│  Music (Lyria or stock)                                      │
│        ↓                                                     │
│  Video Assembly (FFmpeg with Ken Burns)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Sample Output

Running: `python run_example.py "Create a 30 second ad for my pizza restaurant in Boston"`

```
RESEARCH SUMMARY:
  youtube_videos: 5
  competitors_found: 8
  google_reviews: 40
  yelp_reviews: 65
  keywords_analyzed: 3

LOCAL INTEL:
  Top competitors: ['Descendant Detroit Style Pizza', 'Galleria Umberto', 'Pizzeria Rustico']
  What they do right:
    - Consistently high customer ratings (4.8+)
    - Emphasis on quality service and customer experience
  What to avoid:
    - Lack of consistent quality or customer service
    - Inability to establish strong brand identity
```

---

## Environment Variables Required

```bash
# SerpAPI (for Local Intel, Reviews, Yelp)
SERPAPI_KEY=your_key

# DataForSEO (for Trends Intel)
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password

# YouTube (for viral ad research)
YOUTUBE_API_KEY=your_key

# Anthropic (for Claude success/failure analysis in Local Intel)
ANTHROPIC_API_KEY=your_key

# Google Cloud (for image generation, TTS)
GOOGLE_CLOUD_PROJECT=your_project

# Groq (for fast LLM inference)
GROQ_API_KEY=your_key

# Optional
FIRECRAWL_API_KEY=your_key  # For website scraping
```

---

## How to Run

### Interactive Mode
```bash
cd "/Users/tomalmog/programming/Febuary 2026/Brown"
python run_example.py
```

### Direct Mode
```bash
python run_example.py "Create a 30 second funny ad for my pizza restaurant in Boston"
```

### Script Only (Fast)
Modify `run_example.py` or use:
```python
await run_pipeline(
    product='pizza restaurant',
    industry='food',
    output_type='script',  # Just script, no images/video
    duration=30,
    tone='funny',
    city='Boston',
)
```

### Full Video
```python
await run_pipeline(
    product='pizza restaurant',
    industry='food',
    output_type='storyboard_video',  # Full video with images, audio
    duration=30,
    tone='funny',
    city='Boston',
)
```

---

## Known Issues / TODOs

1. **Trends Intel** - DataForSEO sometimes returns empty data; fallback works but with limited insights

2. **Website Scraping** - Takes 2-3 minutes for 7 websites; could parallelize

3. **Image Generation** - 30s delay between requests due to Vertex AI quota limits

4. **ASI:One Chat UI** - Responses not displaying (noted in previous session, not addressed this session)

---

## Git Status

- **Branch:** `tom`
- **Remote:** `origin/main` (teammate's Marky code)
- Pulled teammate's agents from main without merge (used `git checkout origin/main -- <dirs>`)

---

## Next Steps (Suggestions)

1. Test full storyboard_video pipeline end-to-end
2. Fix ASI:One chat UI display issue
3. Add more industry-specific keyword data to trends fallback
4. Consider caching research results to speed up iteration
5. Add error recovery for failed research stages
