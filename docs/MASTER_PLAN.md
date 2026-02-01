# AdBoard AI - Master Implementation Plan

## Overview

This document contains the complete technical plan for building the AdBoard AI multi-agent system for the Fetch.AI track at Hack@Brown 2026.

---

## 1. FREE APIs & Services Summary

### Tier 1: Definitely Free (Use These)

| Service | Free Tier | What We Use It For |
|---------|-----------|-------------------|
| **Groq** | 14,400 requests/day (Llama 3.3 70B) | Script writing, analysis, all LLM tasks |
| **YouTube Data API v3** | 10,000 units/day | Research viral ads (search = 100 units each) |
| **Replicate** | 50 free generations/month | Storyboard image generation (FLUX) |
| **ElevenLabs** | 10,000 characters/month (~10 min audio) | Voiceover generation |
| **Google Cloud** | $300 credit for 90 days | Places API for location scouting |

### Tier 2: Alternatives If Needed

| Service | Free Tier | Backup For |
|---------|-----------|------------|
| **Together AI** | $5 free credit | Image generation (FLUX) |
| **Hugging Face Inference** | Free tier available | Image generation fallback |
| **OpenRouter** | Some free models | LLM fallback |
| **Apify** | $5/month free | YouTube scraping if API quota exceeded |

### API Keys You Need to Get

1. **Groq**: https://console.groq.com/ (instant, no card)
2. **YouTube**: https://console.cloud.google.com/ (enable YouTube Data API v3)
3. **Replicate**: https://replicate.com/ (instant, no card for free tier)
4. **ElevenLabs**: https://elevenlabs.io/ (instant, no card)
5. **Google Places**: Same Google Cloud project as YouTube

---

## 2. Agent Architecture Deep Dive

### 2.1 Orchestrator Agent (MAIN - Deploy to Agentverse)

**Purpose**: User-facing agent, implements Chat Protocol for ASI:One discovery

**Responsibilities**:
- Parse user intent (business type, product, budget, audience)
- Coordinate all sub-agents
- Aggregate results into final deliverable
- Handle errors gracefully

**Implementation**:
```python
from uagents import Agent, Context
from uagents.experimental.chat_protocol import ChatProtocol, ChatMessage

orchestrator = Agent(
    name="adboard-orchestrator",
    seed="your-seed-phrase",
    endpoint=["http://your-server:8000/submit"],
)

chat_proto = ChatProtocol(orchestrator)

@chat_proto.on_message
async def handle_user_message(ctx: Context, msg: ChatMessage):
    # 1. Parse user intent
    # 2. Call Research Agent
    # 3. Call Creative Director
    # 4. Call Production Agent
    # 5. Compile and return results
    pass
```

**Key Files**:
- `agents/orchestrator.py`
- `agents/models.py` (shared message models)

---

### 2.2 Research Agent

**Purpose**: Find viral ads in the user's industry, extract patterns

**Input** (from Orchestrator):
```python
class ResearchRequest(Model):
    industry: str          # "food", "construction", "fitness"
    product_type: str      # "taco truck", "roofing service"
    target_audience: str   # "young professionals", "homeowners"
    num_results: int       # 10-20 videos to analyze
```

**Output**:
```python
class ResearchResponse(Model):
    viral_patterns: list[dict]  # Common hooks, CTAs, styles
    top_videos: list[dict]      # Title, views, channel, URL
    avg_video_length: int       # In seconds
    recommended_style: str      # "testimonial", "product-demo", "story"
    key_phrases: list[str]      # Successful phrases/hooks
```

**API Calls**:

1. **YouTube Data API v3 - Search**
   ```python
   # Cost: 100 quota units per search
   GET https://www.googleapis.com/youtube/v3/search
   ?part=snippet
   &q={industry}+ad+commercial
   &type=video
   &videoDuration=short
   &order=viewCount
   &maxResults=20
   &key={API_KEY}
   ```

2. **YouTube Data API v3 - Video Statistics**
   ```python
   # Cost: 1 quota unit per video
   GET https://www.googleapis.com/youtube/v3/videos
   ?part=statistics,contentDetails
   &id={video_id1},{video_id2},...
   &key={API_KEY}
   ```

3. **Groq - Pattern Analysis**
   ```python
   # Analyze video titles/descriptions for patterns
   POST https://api.groq.com/openai/v1/chat/completions
   {
       "model": "llama-3.3-70b-versatile",
       "messages": [
           {"role": "system", "content": "Analyze these ad titles..."},
           {"role": "user", "content": "{video_data}"}
       ]
   }
   ```

**Key Files**:
- `agents/research_agent.py`
- `utils/youtube_client.py`

---

### 2.3 Creative Director Agent

**Purpose**: Coordinate creative sub-tasks (script, storyboard, voiceover)

This agent manages three sub-processes (can be separate agents or functions):

#### 2.3.1 Script Writer

**Input**:
```python
class ScriptRequest(Model):
    research_data: dict       # From Research Agent
    product_name: str
    unique_selling_point: str
    target_duration: int      # 30 or 60 seconds
    tone: str                 # "funny", "professional", "emotional"
```

**Output**:
```python
class ScriptResponse(Model):
    script_text: str           # Full script with timing
    scenes: list[dict]         # Scene breakdown
    estimated_duration: int    # Seconds
    voiceover_text: str        # Clean text for TTS
```

**API Call - Groq**:
```python
POST https://api.groq.com/openai/v1/chat/completions
{
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "system",
            "content": """You are an expert advertising copywriter. 
            Write a {duration}-second ad script for a {product}.
            
            Based on research, successful ads in this industry use:
            - {patterns}
            
            Format your response as:
            SCENE 1 (0-10s): [Visual description]
            VOICEOVER: "..."
            
            SCENE 2 (10-20s): ...
            """
        },
        {"role": "user", "content": "{request_details}"}
    ]
}
```

#### 2.3.2 Storyboard Generator

**Input**:
```python
class StoryboardRequest(Model):
    scenes: list[dict]        # From Script Writer
    style: str                # "realistic", "illustrated", "cinematic"
    aspect_ratio: str         # "16:9", "9:16", "1:1"
```

**Output**:
```python
class StoryboardResponse(Model):
    frames: list[dict]        # {scene_num, image_url, description}
    style_notes: str
```

**API Call - Replicate (FLUX)**:
```python
import replicate

# For each scene, generate an image
output = replicate.run(
    "black-forest-labs/flux-schnell",  # Fast, free tier friendly
    input={
        "prompt": f"Commercial advertisement frame: {scene_description}, "
                  f"professional photography, {style} style, 16:9 aspect ratio",
        "num_outputs": 1,
        "aspect_ratio": "16:9"
    }
)
# Returns image URL
```

**Alternative - Together AI**:
```python
import together

response = together.Image.generate(
    model="black-forest-labs/FLUX.1-schnell",
    prompt=f"Advertisement storyboard frame: {scene_description}",
    width=1024,
    height=576,  # 16:9
    steps=4
)
```

#### 2.3.3 Voiceover Agent

**Input**:
```python
class VoiceoverRequest(Model):
    script_text: str          # Clean voiceover text
    voice_style: str          # "professional", "friendly", "energetic"
    gender: str               # "male", "female"
```

**Output**:
```python
class VoiceoverResponse(Model):
    audio_url: str            # URL or base64 audio
    duration_seconds: float
```

**API Call - ElevenLabs**:
```python
import requests

url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

# Free voices: "21m00Tcm4TlvDq8ikWAM" (Rachel - female)
#              "ErXwobaYiN019PkySvjV" (Antoni - male)

response = requests.post(
    url,
    headers={
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "text": script_text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
)
# Returns audio bytes
```

**Key Files**:
- `agents/creative_director.py`
- `agents/script_writer.py`
- `agents/storyboard_generator.py`
- `agents/voiceover_agent.py`

---

### 2.4 Production Agent

**Purpose**: Estimate costs, find locations, generate final PDF

#### 2.4.1 Cost Estimator

**Input**:
```python
class CostEstimateRequest(Model):
    scenes: list[dict]        # Scene descriptions
    location_type: str        # "indoor", "outdoor", "studio"
    num_actors: int
    props_needed: list[str]
    city: str                 # For location-specific pricing
```

**Output**:
```python
class CostEstimateResponse(Model):
    total_estimate: float
    breakdown: dict           # {actors: $X, location: $Y, ...}
    assumptions: list[str]
    budget_tips: list[str]
```

**API Call - Groq (for estimation logic)**:
```python
# Use LLM to analyze scenes and estimate costs
POST https://api.groq.com/openai/v1/chat/completions
{
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "system",
            "content": """You are a video production cost estimator.
            
            Standard rates:
            - Actor (non-union, 4hr): $200-400
            - Location permit: $100-500
            - Basic equipment rental: $200-500/day
            - Food/props: varies
            
            Analyze the scenes and provide a realistic budget."""
        },
        {"role": "user", "content": "{scenes_json}"}
    ]
}
```

#### 2.4.2 Location Scout

**Input**:
```python
class LocationRequest(Model):
    location_type: str        # "restaurant", "outdoor park", "office"
    city: str
    budget_range: str         # "low", "medium", "high"
```

**Output**:
```python
class LocationResponse(Model):
    locations: list[dict]     # {name, address, price_estimate, photos}
```

**API Call - Google Places API**:
```python
# Text Search (New)
POST https://places.googleapis.com/v1/places:searchText
Headers:
  X-Goog-Api-Key: {API_KEY}
  X-Goog-FieldMask: places.displayName,places.formattedAddress,places.photos,places.priceLevel

Body:
{
    "textQuery": "film location rental {city}",
    "maxResultCount": 5
}
```

**Alternative - Simpler Nearby Search**:
```python
GET https://maps.googleapis.com/maps/api/place/textsearch/json
?query=event+venue+{city}
&key={API_KEY}
```

#### 2.4.3 PDF Generator

**Input**: All previous outputs (script, storyboard, costs, locations)

**Output**: Professional PDF screenplay/pitch deck

**Library - ReportLab**:
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generate_pdf(script, storyboard_images, costs, locations, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Title page
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "Ad Storyboard Package")
    
    # Script section
    c.showPage()
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, "Script")
    # ... add script text
    
    # Storyboard section
    for i, frame in enumerate(storyboard_images):
        c.showPage()
        img = ImageReader(frame['url'])
        c.drawImage(img, 50, 400, width=500, height=280)
        c.drawString(50, 380, f"Scene {i+1}: {frame['description']}")
    
    # Budget section
    c.showPage()
    c.drawString(100, 750, "Production Budget Estimate")
    # ... add cost breakdown
    
    c.save()
    return output_path
```

**Key Files**:
- `agents/production_agent.py`
- `utils/cost_estimator.py`
- `utils/location_scout.py`
- `utils/pdf_generator.py`

---

## 3. Fetch.AI Integration Checklist

### Required for Judging

- [ ] **Deploy Orchestrator to Agentverse**
  - Register agent at https://agentverse.ai
  - Get agent address (agent1q...)
  
- [ ] **Implement Chat Protocol**
  ```python
  from uagents.experimental.chat_protocol import ChatProtocol
  chat_proto = ChatProtocol(agent)
  ```
  
- [ ] **Make discoverable on ASI:One**
  - Add keywords: "advertising", "storyboard", "marketing", "video production"
  - Write clear README description
  
- [ ] **Multi-agent communication**
  - Use `ctx.send(agent_address, message)` between agents
  - Define clear message models

### Optional (Bonus Points)

- [ ] **Payment Protocol** - Charge per storyboard generation
- [ ] **Deploy sub-agents to Agentverse** - Not just orchestrator

---

## 4. Project File Structure

```
Brown/
├── README.md                    # Required: agent addresses, badges
├── docs/
│   ├── MASTER_PLAN.md          # This file
│   └── API_REFERENCE.md        # Quick API reference
├── agents/
│   ├── __init__.py
│   ├── models.py               # Shared message models
│   ├── orchestrator.py         # Main agent (Chat Protocol)
│   ├── research_agent.py       # YouTube research
│   ├── creative_director.py    # Coordinates creative tasks
│   └── production_agent.py     # Costs, locations, PDF
├── utils/
│   ├── __init__.py
│   ├── groq_client.py          # LLM wrapper
│   ├── youtube_client.py       # YouTube API wrapper
│   ├── replicate_client.py     # Image generation wrapper
│   ├── elevenlabs_client.py    # TTS wrapper
│   ├── places_client.py        # Google Places wrapper
│   └── pdf_generator.py        # ReportLab PDF creation
├── config/
│   └── settings.py             # API keys, constants
├── requirements.txt
└── .env.example
```

---

## 5. Implementation Order (Recommended)

### Phase 1: Core Infrastructure (First 2-3 hours)
1. Set up project structure
2. Get all API keys
3. Create basic Orchestrator with Chat Protocol
4. Test deployment to Agentverse
5. Verify ASI:One discoverability

### Phase 2: Research Agent (1-2 hours)
1. Implement YouTube API client
2. Build Research Agent
3. Test agent-to-agent communication

### Phase 3: Creative Director (2-3 hours)
1. Script Writer (Groq)
2. Storyboard Generator (Replicate)
3. Voiceover Agent (ElevenLabs)

### Phase 4: Production Agent (1-2 hours)
1. Cost Estimator
2. Location Scout (Google Places)
3. PDF Generator

### Phase 5: Integration & Demo (1-2 hours)
1. End-to-end testing
2. Record demo video (3-5 min)
3. Polish README

---

## 6. Quota Management

### YouTube API (10,000 units/day)
- Search: 100 units each
- Video details: 1 unit each
- **Safe limit**: ~80 searches + 2000 video lookups per day

### Groq (14,400 requests/day)
- More than enough for hackathon
- Use `llama-3.3-70b-versatile` for quality

### Replicate (50 free generations)
- 6-12 frames per storyboard = ~8 frames average
- **Safe limit**: 5-6 complete storyboards during hackathon

### ElevenLabs (10,000 characters)
- 60-second script ≈ 150-200 words ≈ 900-1200 characters
- **Safe limit**: ~8-10 voiceovers

---

## 7. Error Handling Strategy

```python
async def safe_api_call(func, *args, fallback=None, **kwargs):
    """Wrapper for graceful degradation"""
    try:
        return await func(*args, **kwargs)
    except RateLimitError:
        logger.warning(f"Rate limited on {func.__name__}")
        return fallback
    except APIError as e:
        logger.error(f"API error: {e}")
        return fallback
```

**Fallbacks**:
- If Replicate fails → Use placeholder images with scene descriptions
- If ElevenLabs fails → Skip voiceover, include script text only
- If YouTube quota exceeded → Use cached/mock research data

---

## 8. Demo Script (3-5 minutes)

1. **Intro** (30s): Explain the problem for small businesses
2. **ASI:One Discovery** (30s): Show agent being found via natural language
3. **User Interaction** (1m): "Create an ad storyboard for my taco truck"
4. **Agent Reasoning** (1m): Show agents communicating, research happening
5. **Output Showcase** (1m): Display script, storyboard frames, voiceover
6. **PDF & Costs** (30s): Show final deliverable with budget estimate
7. **Wrap-up** (30s): Recap value proposition

---

## Quick Links

- [Fetch.AI uAgents Docs](https://uagents.fetch.ai/docs)
- [Agentverse](https://agentverse.ai)
- [ASI:One](https://asi1.ai)
- [Chat Protocol Docs](https://docs.asi1.ai/documentation/tutorials/agent-chat-protocol)
- [Groq Console](https://console.groq.com)
- [Replicate](https://replicate.com)
- [ElevenLabs](https://elevenlabs.io)
- [YouTube API](https://developers.google.com/youtube/v3)
- [Google Places API](https://developers.google.com/maps/documentation/places)
