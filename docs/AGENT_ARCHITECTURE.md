# AdBoard AI - Final Agent Architecture

## Core Concept

The user decides what output they want:
- **Just a script** → Research → Script Writer → Done
- **Storyboard images** → Research → Script → Image Generation → Done  
- **Full video** → Research → Script → Images → Voiceover → Music → Video Assembly → Done
- **PDF package** → Research → Script → Images → Cost Estimate → Locations → PDF → Done
- **Everything** → All of the above

The **Orchestrator Agent** determines the pipeline based on user intent.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (ASI:One)                                  │
│         "Create a 30-second video ad for my taco truck"                     │
│         "Just give me a script for a fitness app"                           │
│         "Full storyboard package with cost estimates"                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR AGENT                                    │
│                    (Chat Protocol - Agentverse)                             │
│                                                                             │
│  1. Extract user intent:                                                    │
│     - What product/business?                                                │
│     - What output type? (script/images/video/pdf/all)                       │
│     - What duration? (30s/45s/60s)                                          │
│     - What tone? (funny/professional/emotional)                             │
│     - What city? (for locations)                                            │
│                                                                             │
│  2. Build pipeline based on output type                                     │
│  3. Execute pipeline sequentially                                           │
│  4. Return results                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ (determines which pipeline to run)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE BUILDER                                   │
│                                                                             │
│  Output Type → Pipeline Steps                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  "script"     → [Research, TrendAnalysis, ScriptWriter]                     │
│  "storyboard" → [Research, TrendAnalysis, ScriptWriter, ImageGen]           │
│  "video"      → [Research, TrendAnalysis, ScriptWriter, ImageGen,           │
│                  Voiceover, Music, VideoAssembly]                           │
│  "pdf"        → [Research, TrendAnalysis, ScriptWriter, ImageGen,           │
│                  CostEstimate, LocationScout, PDFBuilder]                   │
│  "full"       → [ALL AGENTS]                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │      SEQUENTIAL PIPELINE      │
                    │   (runs agents one by one)    │
                    └───────────────┬───────────────┘
                                    │
        ════════════════════════════╪════════════════════════════
                              AGENT POOL
        ════════════════════════════╪════════════════════════════
                                    │
┌───────────────────────────────────┴───────────────────────────────────────┐
│                                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  RESEARCH   │  │   TREND     │  │   SCRIPT    │  │   IMAGE     │      │
│  │   AGENT     │──▶│  ANALYZER   │──▶│   WRITER    │──▶│ GENERATOR   │      │
│  │             │  │             │  │             │  │             │      │
│  │ YouTube API │  │ Groq LLM    │  │ Groq LLM    │  │ Replicate   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│         │                │                │                │              │
│         ▼                ▼                ▼                ▼              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  VOICEOVER  │  │   MUSIC     │  │   VIDEO     │  │    COST     │      │
│  │   AGENT     │  │   AGENT     │  │  ASSEMBLER  │  │  ESTIMATOR  │      │
│  │             │  │             │  │             │  │             │      │
│  │ ElevenLabs  │  │ Groq/Free   │  │ MoviePy     │  │ Groq LLM    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│         │                │                │                │              │
│         ▼                ▼                ▼                ▼              │
│  ┌─────────────┐  ┌─────────────┐                                        │
│  │  LOCATION   │  │    PDF      │                                        │
│  │   SCOUT     │  │   BUILDER   │                                        │
│  │             │  │             │                                        │
│  │ Google      │  │ ReportLab   │                                        │
│  │ Places API  │  │             │                                        │
│  └─────────────┘  └─────────────┘                                        │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Agent List (10 Agents)

| # | Agent | Purpose | API | Required For |
|---|-------|---------|-----|--------------|
| 1 | **Orchestrator** | Chat Protocol, intent extraction, pipeline routing | uAgents | ALL |
| 2 | **Research Agent** | Search YouTube for viral ads | YouTube Data API | ALL |
| 3 | **Trend Analyzer** | Extract patterns, hooks, styles | Groq | ALL |
| 4 | **Script Writer** | Write ad script with scenes | Groq | ALL |
| 5 | **Image Generator** | Create storyboard frames | Replicate FLUX | storyboard, video, pdf, full |
| 6 | **Voiceover Agent** | Generate narration audio | ElevenLabs | video, full |
| 7 | **Music Agent** | Suggest background music | Groq | video, full |
| 8 | **Video Assembler** | Combine into preview video | MoviePy | video, full |
| 9 | **Cost Estimator** | Calculate production budget | Groq | pdf, full |
| 10 | **Location Scout** | Find filming locations | Google Places | pdf, full |
| 11 | **PDF Builder** | Create final deliverable | ReportLab | pdf, full |

---

## Output Type → Pipeline Mapping

```python
PIPELINES = {
    "script": [
        "research",
        "trend_analyzer", 
        "script_writer"
    ],
    
    "storyboard": [
        "research",
        "trend_analyzer",
        "script_writer",
        "image_generator"
    ],
    
    "video": [
        "research",
        "trend_analyzer",
        "script_writer",
        "image_generator",
        "voiceover",
        "music",
        "video_assembler"
    ],
    
    "pdf": [
        "research",
        "trend_analyzer",
        "script_writer",
        "image_generator",
        "cost_estimator",
        "location_scout",
        "pdf_builder"
    ],
    
    "full": [
        "research",
        "trend_analyzer",
        "script_writer",
        "image_generator",
        "voiceover",
        "music",
        "video_assembler",
        "cost_estimator",
        "location_scout",
        "pdf_builder"
    ]
}
```

---

## Orchestrator Agent (Main Entry Point)

```python
# agents/orchestrator.py

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage, ChatAcknowledgement, TextContent, 
    EndSessionContent, chat_protocol_spec
)
from datetime import datetime
from uuid import uuid4

from core.pipeline import AdBoardPipeline
from core.intent_extractor import extract_intent

agent = Agent(
    name="AdBoardOrchestrator",
    seed="your-seed-phrase-here",
    port=8000,
    mailbox=True
)

chat_proto = Protocol(spec=chat_protocol_spec)


def create_response(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content
    )


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    # Acknowledge receipt
    await ctx.send(sender, ChatAcknowledgement(
        timestamp=datetime.utcnow(),
        acknowledged_msg_id=msg.msg_id
    ))
    
    for item in msg.content:
        if isinstance(item, TextContent):
            user_input = item.text.strip()
            ctx.logger.info(f"User: {user_input}")
            
            # Extract intent from user message
            intent = extract_intent(user_input)
            
            if not intent.get("is_ad_request"):
                # Not an ad request, send help message
                await ctx.send(sender, create_response(
                    "Hi! I'm AdBoard AI. I create ad storyboards for small businesses.\n\n"
                    "Tell me:\n"
                    "- What's your product/business?\n"
                    "- What output do you want? (script/storyboard/video/pdf/full package)\n"
                    "- How long? (30s/45s/60s)\n\n"
                    "Example: 'Create a 30-second storyboard for my taco truck in Providence'"
                ))
                return
            
            # Check if we have all required info
            if not intent.get("ready"):
                missing = intent.get("missing", [])
                await ctx.send(sender, create_response(
                    f"Almost there! I still need: {', '.join(missing)}"
                ))
                return
            
            # We have everything - run the pipeline
            await ctx.send(sender, create_response(
                f"Creating your {intent['output_type']}...\n"
                f"Product: {intent['product']}\n"
                f"Duration: {intent['duration']}s\n"
                f"This may take a minute..."
            ))
            
            # Run the pipeline
            pipeline = AdBoardPipeline(
                product=intent["product"],
                industry=intent["industry"],
                output_type=intent["output_type"],
                duration=intent["duration"],
                tone=intent.get("tone", "professional"),
                city=intent.get("city", "")
            )
            
            result = await pipeline.run()
            
            # Send results
            if result.get("success"):
                response_text = format_results(result, intent["output_type"])
                await ctx.send(sender, create_response(response_text, end_session=True))
            else:
                await ctx.send(sender, create_response(
                    f"Sorry, something went wrong: {result.get('error')}"
                ))


agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
```

---

## Intent Extractor

```python
# core/intent_extractor.py

from groq import Groq
import json
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_intent(user_input: str) -> dict:
    """Extract structured intent from user message using LLM."""
    
    prompt = f"""Analyze this message and extract ad creation intent.

Message: "{user_input}"

Return JSON with these fields:
- is_ad_request: boolean (is this asking for ad/storyboard/video creation?)
- product: string (what product/business, e.g., "taco truck", "fitness app")
- industry: string (category: "food", "fitness", "tech", "retail", etc.)
- output_type: string (what they want: "script", "storyboard", "video", "pdf", "full")
- duration: integer (ad length in seconds: 30, 45, or 60)
- tone: string ("professional", "funny", "emotional", "energetic")
- city: string (city for locations, if mentioned)
- ready: boolean (do we have enough info to proceed?)
- missing: list of strings (what info is still needed)

Default output_type to "storyboard" if not specified.
Default duration to 45 if not specified.
Default tone to "professional" if not specified.

Return ONLY valid JSON, no other text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {"is_ad_request": False, "ready": False}
```

---

## Pipeline Runner

```python
# core/pipeline.py

from agents.research_agent import ResearchAgent
from agents.trend_analyzer import TrendAnalyzerAgent
from agents.script_writer import ScriptWriterAgent
from agents.image_generator import ImageGeneratorAgent
from agents.voiceover_agent import VoiceoverAgent
from agents.music_agent import MusicAgent
from agents.video_assembler import VideoAssemblerAgent
from agents.cost_estimator import CostEstimatorAgent
from agents.location_scout import LocationScoutAgent
from agents.pdf_builder import PDFBuilderAgent

PIPELINES = {
    "script": ["research", "trend_analyzer", "script_writer"],
    "storyboard": ["research", "trend_analyzer", "script_writer", "image_generator"],
    "video": ["research", "trend_analyzer", "script_writer", "image_generator", 
              "voiceover", "music", "video_assembler"],
    "pdf": ["research", "trend_analyzer", "script_writer", "image_generator",
            "cost_estimator", "location_scout", "pdf_builder"],
    "full": ["research", "trend_analyzer", "script_writer", "image_generator",
             "voiceover", "music", "video_assembler", "cost_estimator", 
             "location_scout", "pdf_builder"]
}


class AdBoardPipeline:
    def __init__(self, product, industry, output_type, duration, tone, city):
        self.product = product
        self.industry = industry
        self.output_type = output_type
        self.duration = duration
        self.tone = tone
        self.city = city
        
        # Initialize agents
        self.agents = {
            "research": ResearchAgent(),
            "trend_analyzer": TrendAnalyzerAgent(),
            "script_writer": ScriptWriterAgent(),
            "image_generator": ImageGeneratorAgent(),
            "voiceover": VoiceoverAgent(),
            "music": MusicAgent(),
            "video_assembler": VideoAssemblerAgent(),
            "cost_estimator": CostEstimatorAgent(),
            "location_scout": LocationScoutAgent(),
            "pdf_builder": PDFBuilderAgent()
        }
        
        # Results accumulator
        self.results = {}
    
    async def run(self):
        """Execute the pipeline based on output type."""
        
        pipeline_steps = PIPELINES.get(self.output_type, PIPELINES["storyboard"])
        
        try:
            for step in pipeline_steps:
                print(f"Running: {step}...")
                agent = self.agents[step]
                
                # Each agent takes previous results and adds its own
                result = await agent.run(
                    product=self.product,
                    industry=self.industry,
                    duration=self.duration,
                    tone=self.tone,
                    city=self.city,
                    previous_results=self.results
                )
                
                self.results[step] = result
                
                if result.get("error"):
                    return {"success": False, "error": result["error"]}
            
            return {"success": True, "results": self.results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
```

---

## Example Agent Implementation

```python
# agents/research_agent.py

import requests
import os

class ResearchAgent:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def run(self, product, industry, duration, tone, city, previous_results):
        """Search YouTube for viral ads in this industry."""
        
        try:
            # Build search queries
            queries = [
                f"{industry} commercial ad viral",
                f"{product} advertisement",
                f"{industry} marketing video successful"
            ]
            
            all_videos = []
            for query in queries:
                response = requests.get(
                    f"{self.base_url}/search",
                    params={
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "videoDuration": "short",
                        "order": "viewCount",
                        "maxResults": 10,
                        "key": self.api_key
                    }
                )
                data = response.json()
                all_videos.extend(data.get("items", []))
            
            # Get video statistics
            video_ids = list(set([v["id"]["videoId"] for v in all_videos[:20]]))
            stats = self._get_video_stats(video_ids)
            
            return {
                "videos": stats,
                "total_found": len(stats),
                "queries_used": queries
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_video_stats(self, video_ids):
        """Get detailed stats for videos."""
        if not video_ids:
            return []
            
        response = requests.get(
            f"{self.base_url}/videos",
            params={
                "part": "statistics,contentDetails,snippet",
                "id": ",".join(video_ids),
                "key": self.api_key
            }
        )
        
        videos = []
        for item in response.json().get("items", []):
            videos.append({
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "duration": item["contentDetails"]["duration"],
                "description": item["snippet"]["description"][:200]
            })
        
        # Sort by views
        return sorted(videos, key=lambda x: x["views"], reverse=True)
```

---

## File Structure (Final)

```
Brown/
├── README.md                      # Hackathon submission
├── requirements.txt
├── .env.example
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py            # Main agent (Agentverse)
│   ├── research_agent.py          # YouTube search
│   ├── trend_analyzer.py          # Pattern extraction (Groq)
│   ├── script_writer.py           # Script generation (Groq)
│   ├── image_generator.py         # Storyboard frames (Replicate)
│   ├── voiceover_agent.py         # Audio narration (ElevenLabs)
│   ├── music_agent.py             # Music suggestions (Groq)
│   ├── video_assembler.py         # Combine into video (MoviePy)
│   ├── cost_estimator.py          # Budget calc (Groq)
│   ├── location_scout.py          # Find locations (Google Places)
│   └── pdf_builder.py             # Final PDF (ReportLab)
│
├── core/
│   ├── __init__.py
│   ├── pipeline.py                # Pipeline orchestration
│   ├── intent_extractor.py        # Parse user intent (Groq)
│   └── prompts.py                 # All LLM prompts
│
├── utils/
│   ├── __init__.py
│   ├── groq_client.py
│   ├── youtube_client.py
│   ├── replicate_client.py
│   ├── elevenlabs_client.py
│   └── places_client.py
│
├── config/
│   └── settings.py
│
├── output/                        # Generated files
│   ├── storyboards/
│   ├── voiceovers/
│   ├── videos/
│   └── pdfs/
│
└── docs/
    ├── MASTER_PLAN.md
    ├── API_REFERENCE.md
    └── AGENT_ARCHITECTURE.md      # This file
```

---

## MVP Priority (What to Build First)

### Phase 1: Core Loop (Must Have)
1. **Orchestrator** - Chat Protocol, intent extraction
2. **Research Agent** - YouTube API
3. **Trend Analyzer** - Groq analysis
4. **Script Writer** - Groq script generation

### Phase 2: Visual Output
5. **Image Generator** - Replicate FLUX (storyboard frames)

### Phase 3: Full Package
6. **PDF Builder** - ReportLab (final deliverable)

### Phase 4: Nice to Have
7. Voiceover Agent (ElevenLabs)
8. Cost Estimator (Groq)
9. Location Scout (Google Places)

### Phase 5: Stretch
10. Music Agent
11. Video Assembler

---

## Example User Flows

**Flow 1: Quick Script**
```
User: "Write me a script for a fitness app ad"
→ Orchestrator extracts: output_type="script", industry="fitness", product="fitness app"
→ Pipeline: Research → Trend Analyzer → Script Writer
→ Returns: 45-second script with scenes
```

**Flow 2: Full Storyboard**
```
User: "Create a storyboard for my taco truck, 30 seconds, funny tone"
→ Orchestrator extracts: output_type="storyboard", product="taco truck", duration=30, tone="funny"
→ Pipeline: Research → Trends → Script → Image Generator
→ Returns: Script + 6-8 storyboard images
```

**Flow 3: Production Package**
```
User: "Full PDF package for a roofing company ad in Boston, need budget estimates"
→ Orchestrator extracts: output_type="pdf", product="roofing", city="Boston"
→ Pipeline: Research → Trends → Script → Images → Cost → Locations → PDF
→ Returns: Complete PDF with storyboard, budget breakdown, location suggestions
```
