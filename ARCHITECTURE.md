# AdBoard AI - System Architecture

## Overview

AdBoard AI is a multi-agent advertising platform that generates complete ad production packages from natural language prompts. It combines **teammate's Marky research suite** (competitor intelligence, customer voice, trends) with **production agents** (script, images, video, audio, PDF).

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ADBOARD PIPELINE                                   │
│                                                                              │
│  User Prompt: "Create a 30 second ad for my pizza restaurant in Boston"    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    INTENT EXTRACTOR                                    │   │
│  │  core/intent_extractor.py                                             │   │
│  │  Extracts: product, industry, city, duration, tone, output_type      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    ADBOARD PIPELINE                                    │   │
│  │  core/pipeline.py - Orchestrates all agents sequentially             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│         ┌────────────────────────┼────────────────────────┐                │
│         │                        │                        │                │
│         ▼                        ▼                        ▼                │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐          │
│  │  RESEARCH   │────────▶│LOCATION_SCOUT│───────▶│TREND_ANALYZER│         │
│  └─────────────┘         └─────────────┘         └─────────────┘          │
│       │                                                  │                │
│       │          ┌───────────────────────────────────────┘                │
│       │          │                                                      │
│       │          ▼                                                      │
│       │   ┌─────────────────────────────────────────────────────────┐    │
│       │   │              MARKY WORKFLOW (5 sub-agents)              │    │
│       │   │           orchestrator/workflow.py                       │    │
│       │   │                                                          │    │
│       │   │  [1] Local Intel  ───▶ [2] Review Intel ──▶ [3] Yelp   │    │
│       │   │       │                    │                   │          │    │
│       │   │       ▼                    ▼                   ▼          │    │
│       │   │  Competitor          Google Reviews         Yelp         │    │
│       │   │  Discovery           Analysis               Reviews      │    │
│       │   │       │                    │                   │          │    │
│       │   │       └────────────────────┼───────────────────┘          │    │
│       │   │                            ▼                              │    │
│       │   │                   [4] Trends Intel                       │    │
│       │   │                        │                                 │    │
│       │   │                        ▼                                 │    │
│       │   │               [5] Related Questions                     │    │
│       │   │                        │                                 │    │
│       │   └────────────────────────┼───────────────────────────────┘    │
│       │                            │                                      │
│       └────────────────────────────┼────────────────────────────────────┘
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     SCRIPT WRITER                                    │  │
│  │  agents/script_writer.py - Generates scene-by-scene script         │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    IMAGE GENERATOR                                   │  │
│  │  agents/image_generator.py - Creates storyboard frames (Imagen)    │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      VOICEOVER                                       │  │
│  │  agents/voiceover_agent.py - Generates TTS audio (ElevenLabs)      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        MUSIC                                         │  │
│  │  agents/music_agent.py - Selects/generates background music        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     AUDIO MIXER                                      │  │
│  │  agents/audio_mixer.py - Combines voiceover + music (FFmpeg)       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                   VIDEO ASSEMBLY                                     │  │
│  │  agents/video_assembly_agent.py - Creates final MP4 (FFmpeg)       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                   COST ESTIMATOR                                     │  │
│  │  agents/cost_estimator.py - Calculates production budget           │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    SOCIAL MEDIA                                      │  │
│  │  agents/social_media_agent.py - Generates captions for platforms   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      PDF BUILDER                                     │  │
│  │  agents/pdf_builder.py - Creates production package PDF            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                      │
│                                    ▼                                      │
│  Final Outputs: Script, Images, Voiceover, Video, PDF, Budget     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Entry Points

| File | Purpose |
|------|---------|
| `run_example.py` | Interactive CLI runner |
| `core/pipeline.py` | Main pipeline orchestrator |
| `core/intent_extractor.py` | Natural language parsing |

---

## Pipeline Modes

The pipeline supports multiple output modes defined in `core/pipeline.py:PIPELINES`:

| Mode | Agents Run | Output |
|------|-----------|--------|
| `script` | research → location_scout → trend_analyzer → script_writer | Script only |
| `storyboard` | script + image_generator | Script + images |
| `storyboard_video` | all production agents | Final MP4 video |
| `video` | full pipeline without video_assembly | Assets for manual editing |
| `pdf` | research → trend_analyzer → script_writer → image_generator → cost_estimator → location_scout → pdf_builder | PDF package |
| `full` | all agents including PDF | Complete package |
| `audio_package` | research → location_scout → trend_analyzer → script_writer → voiceover → music → audio_mixer → social_media | Audio-focused |
| `preproduction` | research → location_scout → trend_analyzer → script_writer → cost_estimator → social_media | Planning documents |
| `full_no_visual` | audio_package + cost_estimator | No image/video generation |

---

## Agent Details

### 1. RESEARCH Agent

**File:** `agents/enhanced_research.py`

**Class:** `EnhancedResearchAgent` (alias: `ResearchAgent`)

**Purpose:** Runs the complete Marky research workflow and converts results to AdBoard format

**Inputs:**
```python
await agent.run(
    product="pizza",           # Product/business name
    industry="food",           # Industry category  
    duration=30,               # Ad duration
    tone="professional",       # Desired tone
    city="Boston",             # Location for research
    previous_results={},       # Empty for first agent
)
```

**Outputs:**
```python
{
    "industry": "food",
    "product": "pizza", 
    "city": "Boston",
    "local_intel": {           # From LocalIntelAgent
        "competitors_found": 8,
        "top_competitors": [...],
        "differentiators": [...],
        "headline_suggestions": [...],
        "trust_signals_to_use": [...],
    },
    "google_reviews": {        # From ReviewIntelAgent + YelpIntelAgent
        "pain_points": [...],
        "desires": [...],
        "praise_quotes": [...],
        "complaint_quotes": [...],
        "common_themes": [...],
    },
    "yelp_reviews": {...},     # Same structure as google_reviews
    "keyword_trends": {        # From TrendsIntelAgent
        "keywords_analyzed": 3,
        "keyword_data": [...],
        "timing_recommendations": [...],
        "ad_recommendations": [...],
    },
    "related_questions": [...], # From RelatedQuestionsIntelAgent
    "viral_videos": [],         # Not used in current version
    "viral_patterns": {},        # Not used in current version
    "insights": [...],          # Combined actionable insights
    "research_summary": {
        "competitors_found": 8,
        "google_reviews": 64,
        "yelp_reviews": 50,
        "keywords_analyzed": 0,
    },
    "marky_result": {...},      # Full Marky response for reference
}
```

---

### 1.1 MARKY WORKFLOW (Sub-agents)

**File:** `orchestrator/workflow.py`

**Class:** `MarkyWorkflow`

**Purpose:** Orchestrates 5 research sub-agents sequentially

#### 1.1.1 Local Intel Agent

**File:** `local_intel/agent.py`

**Class:** `LocalIntelAgent`

**Inputs:**
```python
agent.analyze(
    business_type="food pizza",
    location="Boston",
    radius_miles=10.0,
    top_count=8,          # Number of top competitors
    worst_count=2,        # Number of low-rated competitors
    include_worst_rated=True,
)
```

**Process:**
1. **Competitor Discovery** (`local_intel/competitor_discovery.py`)
   - Uses SerpAPI to search for top-rated + worst-rated competitors
   - Two-pass search: first for top-rated, then wider area for low-rated
2. **Website Scraping** (`local_intel/website_scraper.py`)
   - Scrapes competitor websites for content
   - Extracts services, trust signals, messaging
3. **Content Extraction** (`local_intel/content_extractor.py`)
   - Parses HTML to extract services, taglines, unique selling points
4. **Market Analysis** (`local_intel/content_extractor.py:MarketAnalyzer`)
   - Identifies common services, service gaps, messaging opportunities
5. **Ad Differentiation** (`local_intel/ad_generator.py`)
   - Generates differentiators, headlines, taglines, trust signals
6. **Claude Analysis** (`local_intel/agent.py:ClaudeAnalysisAgent`)
   - Analyzes success vs failure patterns using Claude

**Outputs:**
```python
IntelligenceReport {
    competitors: [Competitor, ...],
    market_analysis: MarketAnalysis {
        common_services: [...],
        service_gaps: [...],
        messaging_opportunities: [...],
    },
    differentiators: [AdDifferentiator, ...],
    headline_suggestions: [...],
    tagline_suggestions: [...],
    trust_signals_to_use: [...],
}
```

#### 1.1.2 Review Intel Agent (Google Reviews)

**File:** `review_intel/agent.py`

**Class:** `ReviewIntelAgent`

**Inputs:**
```python
agent.analyze_competitors(
    competitors=[
        {"name": "Descendant Detroit Style Pizza", "place_id": "...", "rating": 4.9},
        ...
    ],
    business_type="food pizza",
    location="Boston",
    reviews_per_competitor=8,
)
```

**Process:**
1. **Scraper** (`review_intel/scraper.py`) - Uses SerpAPI to fetch Google Reviews
2. **Analysis** - Extracts pain points, desires, praise, complaints
3. **Hook Generation** - Creates ad hooks from customer language

**Outputs:**
```python
ReviewAnalysis {
    total_reviews_analyzed: 64,
    voice_of_customer: VoiceOfCustomer {
        pain_points: [{"point": "...", "frequency": n}, ...],
        desires: [{"desire": "...", "frequency": n}, ...],
        praise_quotes: [...],
        complaint_quotes: [...],
    },
    ad_hooks: [...],
    headline_suggestions: [...],
    top_competitor_themes: [...],
}
```

#### 1.1.3 Yelp Intel Agent

**File:** `yelp_intel/agent.py`

**Class:** `YelpIntelAgent`

**Inputs:**
```python
agent.analyze_market(
    business_type="food pizza",
    location="Boston",
    max_businesses=5,
    reviews_per_business=10,
)
```

**Process:**
1. **Scraper** (`yelp_intel/scraper.py`) - Searches Yelp and fetches reviews
2. **Analysis** - Sentiment analysis, pain/praise extraction
3. **Suggestions** - Generates hooks and headlines

**Outputs:**
```python
YelpAnalysis {
    total_reviews_analyzed: 50,
    insights: YelpInsights {
        pain_points: [...],
        praise_points: [...],
        pain_point_quotes: [...],
        praise_quotes: [...],
        themes: [...],
        customer_phrases: [...],
    },
    ad_suggestions: AdSuggestions {
        hooks: [...],
        headlines: [...],
    },
}
```

#### 1.1.4 Trends Intel Agent

**File:** `trends_intel/agent.py`

**Class:** `TrendsIntelAgent`

**Inputs:**
```python
agent.analyze(
    keywords=["food pizza", "food pizza near me", "best food pizza"],
    location="United States",
    include_related=True,
)
```

**Process:**
1. **Scraper** (`trends_intel/scraper.py`) - Uses DataForSEO API
2. **Keyword Data** - Search volume, CPC, competition
3. **Related Queries** - "People also search for"
4. **Seasonal Analysis** - Peak/low months, recommendations

**Outputs:**
```python
TrendsAnalysis {
    keyword_data: [KeywordData {
        keyword: "food pizza",
        search_volume: 550000,
        cpc: 2.50,
        competition: 0.95,
    }, ...],
    related_queries: [...],
    seasonal_insights: [SeasonalInsight {
        keyword: "food pizza",
        peak_months: [6, 7, 8],  # Summer
        low_months: [1, 2],
        recommendation: "Best months for ads: June, July, August",
    }, ...],
}
```

#### 1.1.5 Related Questions Intel Agent

**File:** `related_questions_intel/agent.py`

**Class:** `RelatedQuestionsIntelAgent`

**Inputs:**
```python
agent.analyze(
    business_type="food pizza",
    location="Boston",
    seed_queries=None,        # Auto-generated if None
    max_questions_per_query=15,
)
```

**Process:**
1. **Scraper** (`related_questions_intel/scraper.py`) - Uses SerpAPI
2. **Queries** - Fetches "People also ask" questions
3. **Deduplication** - Returns unique questions

**Outputs:**
```python
RelatedQuestionsAnalysis {
    query_results: [QueryQuestions {
        query: "food pizza Boston",
        questions: [RelatedQuestion {
            question: "What makes Boston pizza unique?",
            snippet: "...",
            link: "...",
        }, ...],
    }, ...],
    all_questions(): [...],  # Flat list of unique questions
}
```

---

### 2. LOCATION SCOUT Agent

**File:** `agents/location_scout.py`

**Class:** `LocationScoutAgent`

**Purpose:** Finds potential filming locations using Google Places

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={"research": research_data},
)
```

**Outputs:**
```python
{
    "locations": [
        {
            "name": "Boston Public Garden",
            "address": "4 Charles St, Boston, MA 02116",
            "rating": 4.8,
            "types": ["park", "point_of_interest"],
            "price_level": "$$",
            "filming_notes": "Requires permit, beautiful for establishing shots",
        },
        ...
    ],
 [
    "tips":        "Best lighting: 2 hours before sunset",
        "Permit required for commercial filming",
    ],
}
```

---

### 3. TREND ANALYZER Agent

**File:** `agents/trend_analyzer.py`

**Class:** `TrendAnalyzerAgent`

**Purpose:** Analyzes research data and extracts actionable patterns for ad creation

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "research": {...},  # Full research data
    },
)
```

**Process:**
- Uses Groq LLM to analyze research and extract patterns
- Generates recommendations for hooks, visual style, structure, CTA

**Outputs:**
```python
{
    "analysis": {
        "recommended_hook": "Close-up of melted cheese pull with Boston skyline",
        "visual_style": "Warm, appetizing close-ups mixed with city establishing shots",
        "cta": "Order now at example.com and get 20% off",
        "key_messages": [
            "Quality ingredients",
            "Affordable prices",
            "Trusted by locals",
        ],
        "ad_structure": [
            {"time": "0-5s", "element": "Hook", "description": "Visual hook with tagline"},
            {"time": "5-10s", "element": "Problem", "description": "Show pain point"},
            {"time": "10-15s", "element": "Solution", "description": "Introduce product"},
            {"time": "15-22s", "element": "Proof", "description": "Social proof"},
            {"time": "22-30s", "element": "CTA", "description": "Call to action"},
        ],
    },
    "model_used": "llama-3.3-70b-versatile",
}
```

---

### 4. SCRIPT WRITER Agent

**File:** `agents/script_writer.py`

**Class:** `ScriptWriterAgent`

**Purpose:** Writes scene-by-scene ad script with visual and audio details

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "research": {...},         # Research data with insights
        "trend_analyzer": {...},   # Pattern analysis
        "location_scout": {...},   # Location suggestions
    },
)
```

**Process:**
- Builds comprehensive prompt with all research insights
- Uses Groq LLM to generate script
- Parses into structured scene format

**Outputs:**
```python
{
    "script": "--- SCENE 1 (0-5s): [HOOK] ...",
    "scenes": [
        {
            "scene_number": 1,
            "timing": "0-5s",
            "title": "Hook",
            "visual": "Close-up shot of a juicy, melted cheese pull...",
            "audio": "Upbeat, mouth-watering music...",
            "voiceover": "You know what's better than a slice...",
        },
        ...
    ],
    "voiceover_text": "You know what's better than a slice of pizza...",
    "scene_count": 5,
    "estimated_duration": 30,
    "model_used": "llama-3.3-70b-versatile",
}
```

---

### 5. IMAGE GENERATOR Agent

**File:** `agents/image_generator.py`

**Class:** `ImageGeneratorAgent`

**Purpose:** Generates storyboard frames using Google Cloud Vertex AI Imagen

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "script_writer": {
            "scenes": [...],  # 5 scenes
        },
    },
)
```

**Process:**
1. Extracts visual descriptions from each scene
2. Generates image prompts optimized for Imagen
3. Calls Vertex AI Imagen API (~$0.02-0.04/image)
4. Applies 30s delay between requests for quota limits
5. Saves images to `output/frames/`

**Outputs:**
```python
{
    "frames": [
        {
            "scene": 1,
            "timing": "0-5s",
            "description": "Close-up shot of melted cheese...",
            "prompt": "Cinematic close-up of pizza with stretching mozzarella cheese...",
            "url": "/Users/.../output/frames/frame_1.png",
        },
        ...
    ],
    "model_used": "imagen-3.0-generate-001",
}
```

---

### 6. VOICEOVER Agent

**File:** `agents/voiceover_agent.py`

**Class:** `VoiceoverAgent`

**Purpose:** Generates professional voiceover using ElevenLabs API

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",  # Affects voice selection
    city="Boston",
    previous_results={
        "script_writer": {
            "voiceover_text": "You know what's better than...",
        },
    },
)
```

**Process:**
1. Selects voice based on tone (female/male × friendly/professional/energetic)
2. Calls ElevenLabs API
3. Saves audio to `output/voiceovers/`

**Voice Selection:**
| Tone | Female Voice | Male Voice |
|------|--------------|------------|
| friendly | Rachel (21m00...) | Antoni (ErXw...) |
| professional | Dorothy (ThT5K...) | Drew (29vD3...) |
| energetic | Domi (AZnzlk...) | Adam (pNInz6...) |

**Outputs:**
```python
{
    "audio_path": "output/voiceovers/voiceover_pizza_30s.mp3",
    "voice_id": "ThT5KcBeYPX3keUQqHPh",
    "voice_name": "Dorothy",
    "settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
    },
    "duration": 28,
}
```

---

### 7. MUSIC Agent

**File:** `agents/music_agent.py`

**Class:** `MusicAgent`

**Purpose:** Provides music recommendations for ads (optional - no downloading)

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "script_writer": {"scenes": [...]},
    },
)
```

**Process:**
- Uses Groq LLM to generate music recommendations based on ad content
- Provides search terms for royalty-free music libraries (Pixabay, Mixkit, Epidemic Sound)
- Falls back to quick recommendations based on tone/industry

**Outputs:**
```python
{
    "suggestions": "1. PRIMARY RECOMMENDATION:\n- Genre: Acoustic / Light Jazz...",
    "tone": "professional",
    "duration": 30,
    "quick_recommendation": {
        "genre": "Acoustic / Light Jazz",
        "search_terms": ["upbeat acoustic", "happy ukulele", "cafe jazz"],
        "bpm": "100-120",
    },
    "note": "Music is optional - audio mixer works with voiceover only",
}
```

---

### 8. AUDIO MIXER Agent

**File:** `agents/audio_mixer.py`

**Class:** `AudioMixerAgent`

**Purpose:** Creates final audio track from voiceover with optional background music

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "voiceover": {"audio_path": "output/voiceovers/voiceover.mp3"},
        "music": {"music_path": "output/music/music.mp3"},  # Optional
    },
)
```

**Process:**
1. Loads voiceover audio
2. If music is provided and exists, mixes it with voiceover (ducking, fading)
3. If no music, processes voiceover with fade in/out
4. Saves to `output/mixed_audio/`

**Outputs:**
```python
{
    "mixed_audio_path": "output/mixed_audio/final_audio_pizza_30s.mp3",
    "voiceover_path": "output/voiceovers/voiceover_pizza_30s.mp3",
    "music_path": "output/music/music.mp3",  # or null
    "duration": 30,
    "music_genre": "Upbeat",  # or "None"
    "note": "Voiceover only - no background music",
}
```

---

### 9. VIDEO ASSEMBLY Agent

**File:** `agents/video_assembly_agent.py`

**Class:** `VideoAssemblyAgent`

**Purpose:** Creates final MP4 video using FFmpeg

**Supports two modes:**
1. **Storyboard Mode:** Images + Ken Burns effects + audio
2. **Video Mode:** Video clips (from Veo agent) + audio

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "image_generator": {"frames": [...]},
        "voiceover": {"audio_path": "output/voiceovers/voiceover.mp3"},
        "audio_mixer": {"mixed_audio_path": "output/audio/mixed.mp3"},
    },
)
```

**Process:**
1. Converts each image to video clip (6s each with Ken Burns)
2. Concatenates clips
3. Adds audio track
4. Saves to `output/final/`

**Outputs:**
```python
{
    "video_path": "output/final/final_pizza_30s.mp4",
    "file_size": "7.4MB",
    "duration": 30,
    "resolution": "1920x1080",
    "mode": "storyboard",
}
```

---

### 10. COST ESTIMATOR Agent

**File:** `agents/cost_estimator.py`

**Class:** `CostEstimatorAgent`

**Purpose:** Calculates detailed production budget

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "script_writer": {"scene_count": 5},
        "location_scout": {"locations": [...]},
    },
)
```

**Outputs:**
```python
{
    "total": 12500,
    "budget_level": "mid",
    "breakdown": {
        "talent": {"actors": 500, "voiceover": 200},
        "crew": {"director": 1000, "cinematographer": 800},
        "equipment": {"camera": 600, "lighting": 400},
        "locations": {"permits": 200, "rental": 800},
        "post_production": {"editing": 1500, "color": 500},
    },
    "schedule": [
        {"day": 1, "activity": "Pre-production", "hours": 8},
        {"day": 2, "activity": "Filming", "hours": 10},
        {"day": 3, "activity": "Post-production", "hours": 8},
    ],
    "tips": [
        "Consider shooting multiple versions simultaneously",
        "Use natural lighting when possible",
    ],
}
```

---

### 11. SOCIAL MEDIA Agent

**File:** `agents/social_media_agent.py`

**Class:** `SocialMediaAgent`

**Purpose:** Generates platform-specific captions and hashtags

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "script_writer": {...},
    },
)
```

**Outputs:**
```python
{
    "captions": {
        "instagram": "🍕 Slice into perfection! Our Boston pizzeria brings you...",
        "tiktok": "POV: You just discovered the best pizza in Boston...",
        "youtube": "Looking for the best pizza in Boston? We visited...",
    },
    "hashtags": ["#BostonPizza", "#PizzaLovers", "#Foodie"],
    "shortlinks": {
        "tracking": "https://track.example.com/ad-pizza",
    },
}
```

---

### 12. PDF BUILDER Agent

**File:** `agents/pdf_builder.py`

**Class:** `PDFBuilderAgent`

**Purpose:** Creates comprehensive production package PDF

**Inputs:**
```python
await agent.run(
    product="pizza",
    industry="food",
    duration=30,
    tone="professional",
    city="Boston",
    previous_results={
        "research": {...},
        "script_writer": {...},
        "image_generator": {...},
        "cost_estimator": {...},
        "location_scout": {...},
        "trend_analyzer": {...},
        "voiceover": {...},
        "music": {...},
        "video_assembly": {...},
        "social_media": {...},
    },
)
```

**PDF Sections:**
1. Cover Page
2. Executive Summary
3. Pipeline Overview
4. Market Research (Competitors, Customer Voice, Trends, Related Questions)
5. Complete Script
6. Storyboard & Visual Concepts
7. Production Budget & Resources
8. Filming Locations
9. Strategic Recommendations
10. Generated Assets
11. Next Steps & Action Items

**Outputs:**
```python
{
    "pdf_path": "output/pdfs/AdBoard_pizza_20260131_230220.pdf",
    "filename": "AdBoard_pizza_20260131_230220.pdf",
    "pages": 12,
    "sections": ["Cover", "Executive Summary", "Pipeline", "Market Research", ...],
}
```

---

## Data Flow Summary

```
User Input
    │
    ▼
Intent Extractor → {product, industry, city, duration, tone, output_type}
    │
    ▼
AdBoardPipeline.run()
    │
    ▼
RESEARCH → MarkyWorkflow → [Local → Review → Yelp → Trends → Related Questions]
    │
    ▼
location_scout → {locations: [...]}
    │
    ▼
trend_analyzer → {analysis: {hook, visual_style, cta, key_messages, ad_structure}}
    │
    ▼
script_writer → {script, scenes, voiceover_text}
    │
    ▼
[Conditional branches based on output_type]
    │
    ├─▶ image_generator → {frames: [{description, prompt, url}, ...]}
    │
    ├─▶ voiceover → {audio_path, duration}
    │
    ├─▶ music → {music_path}
    │
    ├─▶ audio_mixer → {mixed_audio_path}
    │
    ├─▶ video_assembly → {video_path, file_size}
    │
    ├─▶ cost_estimator → {total, breakdown, schedule}
    │
    ├─▶ social_media → {captions, hashtags}
    │
    └─▶ pdf_builder → {pdf_path, pages}
    │
    ▼
Final Output
```

---

## Output Directory Structure

```
output/
├── frames/                    # Generated storyboard images
│   ├── frame_1.png
│   ├── frame_2.png
│   └── ...
├── voiceovers/               # Generated voiceover audio
│   └── voiceover_pizza_30s.mp3
├── music/                    # Selected/generated music
│   └── background_*.mp3
├── audio/                    # Mixed audio tracks
│   └── mixed_*.mp3
├── final/                    # Final video outputs
│   ├── storyboard_pizza.mp4
│   └── final_pizza_30s.mp4
├── pdfs/                     # Production package PDFs
│   └── AdBoard_pizza_20260131_230220.pdf
└── related_questions/        # Related questions data (optional)
```

---

## API Keys Required

| Service | Environment Variable | Purpose |
|---------|---------------------|---------|
| SerpAPI | `SERPAPI_KEY` | Local Intel, Reviews, Yelp, Related Questions |
| Anthropic | `ANTHROPIC_API_KEY` | Claude analysis in Local Intel |
| DataForSEO | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` | Trends Intel |
| Google Cloud | `GCP_PROJECT_ID`, `GOOGLE_CLOUD_PROJECT` | Image generation (Vertex AI) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Voiceover |
| Groq | `GROQ_API_KEY` | Script, trend analysis, cost estimation |
| Firecrawl | `FIRECRAWL_API_KEY` | Website scraping (optional) |

---

## Key Design Patterns

1. **Sequential Pipeline:** Each agent runs after the previous one completes, passing results via `previous_results`

2. **Graceful Degradation:** Pipeline continues even if individual agents fail (errors stored in results)

3. **Dual Data Paths:** 
   - Marky workflow collects raw data (competitors, reviews, trends)
   - EnhancedResearchAgent converts to AdBoard format

4. **Async/Sync Bridge:** `run_in_executor` used to run synchronous Marky workflow in async pipeline

5. **Multi-Mode Output:** Same core pipeline generates different outputs based on `output_type`

---

## File Reference Index

### Core Pipeline
- `core/pipeline.py` - Main orchestrator, PIPELINES dict
- `core/intent_extractor.py` - NLP parsing
- `run_example.py` - CLI entry point

### Research (Marky)
- `agents/enhanced_research.py` - Adapter to Marky workflow
- `orchestrator/workflow.py` - Marky orchestration
- `orchestrator/models.py` - Marky data models

### Marky Sub-agents
- `local_intel/agent.py` - Local Intel orchestrator
- `local_intel/competitor_discovery.py` - Competitor search
- `local_intel/website_scraper.py` - Website scraping
- `local_intel/content_extractor.py` - Content parsing
- `local_intel/ad_generator.py` - Differentiation generation
- `review_intel/agent.py` - Google Reviews
- `yelp_intel/agent.py` - Yelp reviews
- `trends_intel/agent.py` - Keyword trends
- `related_questions_intel/agent.py` - "People also ask"

### Production Agents
- `agents/location_scout.py` - Location discovery
- `agents/trend_analyzer.py` - Pattern analysis
- `agents/script_writer.py` - Script generation
- `agents/image_generator.py` - Image generation (Imagen)
- `agents/voiceover_agent.py` - Voiceover (ElevenLabs)
- `agents/music_agent.py` - Music recommendations (optional)
- `agents/audio_mixer.py` - Audio mixing (FFmpeg)
- `agents/video_assembly_agent.py` - Video creation (FFmpeg)
- `agents/cost_estimator.py` - Budget calculation
- `agents/social_media_agent.py` - Caption generation
- `agents/pdf_builder.py` - PDF generation (ReportLab)
