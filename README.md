# AdBoard AI

Multi-agent ad campaign generator built on Fetch.ai uAgents. Generates storyboard videos, viral videos, and campaign PDFs for small businesses.

**Built at Hack@Brown 2026 for the Fetch.AI track.**

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Add your API keys (see Environment Variables below)

# 3. Run the agent
python agents/orchestrator.py
```

The agent registers on Agentverse automatically. Chat with it on [ASI:One](https://asi1.ai) by searching "AdBoard AI".

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ASI:One Chat                            │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (uAgent)                        │
│  agents/orchestrator.py                                         │
│  • Chat Protocol (uagents_core.contrib.protocols.chat)          │
│  • Mailbox/Proxy for Agentverse discovery                       │
│  • Intent extraction → Pipeline execution → Response formatting │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PIPELINE (core/pipeline.py)                │
│  Sequential agent execution with accumulated results            │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
        ┌─────────────┬───────────┼───────────┬─────────────┐
        ▼             ▼           ▼           ▼             ▼
┌─────────────┐ ┌───────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  Research   │ │  Script   │ │  Image  │ │  Video  │ │   PDF   │
│  Agents     │ │  Writer   │ │  Gen    │ │  Gen    │ │ Builder │
└─────────────┘ └───────────┘ └─────────┘ └─────────┘ └─────────┘
```

### uAgents Integration

The orchestrator (`agents/orchestrator.py`) is the backbone:

```python
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage, ChatAcknowledgement, TextContent, ResourceContent
)

# Agent with mailbox for Agentverse discovery
agent = Agent(
    name="AdBoardAI",
    seed=SEED_PHRASE,
    mailbox=True,
    network="testnet",
)

# Chat protocol for ASI:One compatibility
protocol = Protocol(spec=chat_protocol_spec)

@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    # 1. Send acknowledgement
    await ctx.send(sender, ChatAcknowledgement(...))
    
    # 2. Extract intent from message
    intent = extract_intent(user_text)
    
    # 3. Run pipeline
    pipeline = AdBoardPipeline(product=..., industry=..., ...)
    result = await pipeline.run(progress_callback=on_progress)
    
    # 4. Upload outputs and send response
    await ctx.send(sender, create_preview_response(...))

agent.include(protocol, publish_manifest=True)
```

### Pipeline Agents

Each agent in `agents/` follows the same interface:

```python
class SomeAgent:
    async def run(self, product, industry, duration, tone, city, previous_results) -> dict:
        # Access previous agent outputs via previous_results
        # Return dict with results (stored in previous_results for next agent)
```

**Full Campaign Pipeline** (`full_campaign`):
1. `research` - Market research via Marky (5 parallel intel agents)
2. `location_scout` - Filming locations via Google Places
3. `trend_analyzer` - Viral patterns from trends
4. `script_writer` - Script via Gemini
5. `image_generator` - Storyboard frames via Imagen 3
6. `lyria_music` - Background music via Lyria
7. `voiceover` - TTS via Google Cloud TTS
8. `audio_mixer` - Mix voiceover + music
9. `video_assembly` - Storyboard video (FFmpeg)
10. `veo3_generator` - Viral video via VEO 3
11. `viral_video_assembler` - Viral video + audio
12. `cost_estimator` - Production budget
13. `social_media` - Platform strategy
14. `pdf_builder` - Campaign PDF via ReportLab

---

## API Reference

### External APIs

| API | Agent | Purpose | Env Variable |
|-----|-------|---------|--------------|
| **Google Gemini** | intent_extractor, script_writer | Intent parsing, script generation | `GOOGLE_API_KEY` |
| **Google Imagen 3** | image_generator | Storyboard frame generation | `GCP_PROJECT_ID` |
| **Google VEO 3** | veo3_generator | Photorealistic viral video | `GCP_PROJECT_ID` |
| **Google Lyria** | lyria_agent | Background music generation | `GCP_PROJECT_ID` |
| **Google Cloud TTS** | voiceover_agent | Text-to-speech narration | `GCP_PROJECT_ID` |
| **Google Places** | location_scout | Filming location discovery | `GOOGLE_PLACES_API_KEY` |
| **SerpAPI** | research (via Marky) | Google/Yelp reviews, trends | `SERPAPI_KEY` |
| **DataForSEO** | trends_intel | Keyword volume, CPC data | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` |
| **Agentverse** | orchestrator | Agent registration, storage | `AGENTVERSE_API_KEY` |

### Agentverse Storage

Thumbnails are uploaded to Agentverse External Storage for inline preview in ASI:One:

```python
from uagents_core.storage import ExternalStorage

storage = ExternalStorage(api_token=AGENTVERSE_KEY, storage_url=STORAGE_URL)
asset_id = storage.create_asset(name="preview.jpg", content=thumb_bytes, mime_type="image/jpeg")
storage.set_permissions(asset_id=asset_id, agent_address=sender)
# Returns: agent-storage://agentverse.ai/v1/storage/{asset_id}
```

Falls back to Google Drive or tmpfiles.org if Agentverse storage fails.

### Response Format

ASI:One responses use `ResourceContent` for inline images:

```python
ChatMessage(
    content=[
        ResourceContent(
            type="resource",
            resource=Resource(uri="agent-storage://...", metadata={"mime_type": "image/jpeg"})
        ),
        TextContent(type="text", text="View Storyboard: https://..."),
        EndSessionContent(type="end-session")
    ]
)
```

---

## Environment Variables

```bash
# Required
AGENTVERSE_API_KEY=         # Fetch.ai Agentverse API key
AGENT_SEED_PHRASE=          # Deterministic agent address

# Google Cloud (for Imagen/VEO/Lyria/TTS)
GCP_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=  # Path to service account JSON

# Google APIs
GOOGLE_API_KEY=             # For Gemini
GOOGLE_PLACES_API_KEY=      # For location scout

# Research APIs
SERPAPI_KEY=                # For Google/Yelp scraping
DATAFORSEO_LOGIN=           # For keyword data
DATAFORSEO_PASSWORD=

# Optional
GDRIVE_DEFAULT_FOLDER_ID=   # Google Drive folder for uploads
TEST_MODE=false             # Echo mode for testing
MOCK_MODE=false             # Return mock data without pipeline
QUICK_FULL=false            # Skip research for faster runs
```

---

## Deliverables

The agent produces three outputs:

1. **Storyboard Video** - Silent B&W sketch animation for concept validation
2. **Viral Video** - Ready-to-post short-form video with music and voiceover
3. **Campaign PDF** - Full brief with research, script, costs, locations, social strategy

---

## Testing

```bash
# Test mode (echo messages, no pipeline)
TEST_MODE=true python agents/orchestrator.py

# Mock mode (return sample data)
MOCK_MODE=true python agents/orchestrator.py

# Quick mode (skip research)
QUICK_FULL=true python agents/orchestrator.py

# CLI test
python run_example.py --product "coffee shop" --city "Providence"
```

---

## Project Structure

```
├── agents/
│   ├── orchestrator.py      # Main uAgent (Chat Protocol, Agentverse)
│   ├── script_writer.py     # Gemini script generation
│   ├── image_generator.py   # Imagen 3 storyboard frames
│   ├── veo3_agent.py        # VEO 3 viral video
│   ├── lyria_agent.py       # Lyria music generation
│   ├── voiceover_agent.py   # Google Cloud TTS
│   ├── video_assembly_agent.py    # FFmpeg storyboard video
│   ├── viral_video_assembler.py   # FFmpeg viral video
│   ├── pdf_builder.py       # ReportLab PDF generation
│   └── ...
├── core/
│   ├── pipeline.py          # Sequential agent orchestration
│   ├── intent_extractor.py  # Gemini intent parsing
│   └── gemini_client.py     # Gemini API wrapper
├── orchestrator/            # Marky research system
│   ├── workflow.py          # 5-agent research pipeline
│   └── ...
├── local_intel/             # Competitor discovery
├── review_intel/            # Google Reviews analysis
├── yelp_intel/              # Yelp sentiment analysis
├── trends_intel/            # Keyword/trend data
└── related_questions_intel/ # "People also ask" data
```

---

## License

MIT
