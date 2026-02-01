# API Quick Reference

Fast copy-paste reference for all API calls in AdBoard AI.

---

## 1. Groq (LLM)

**Base URL**: `https://api.groq.com/openai/v1`

**Get Key**: https://console.groq.com/keys

### Chat Completion
```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a 30-second ad script for a taco truck."}
    ],
    temperature=0.7,
    max_tokens=1024
)

print(response.choices[0].message.content)
```

**Available Models**:
- `llama-3.3-70b-versatile` (best quality, use this)
- `llama-3.1-8b-instant` (faster, lower quality)
- `mixtral-8x7b-32768` (good alternative)

**Rate Limits (Free Tier)**:
- 30 requests/minute
- 14,400 requests/day
- 6,000 tokens/minute

---

## 2. YouTube Data API v3

**Base URL**: `https://www.googleapis.com/youtube/v3`

**Get Key**: https://console.cloud.google.com/ → Enable YouTube Data API v3

### Search Videos
```python
import requests

API_KEY = os.environ.get("YOUTUBE_API_KEY")

# Search for ads in an industry (100 quota units)
response = requests.get(
    "https://www.googleapis.com/youtube/v3/search",
    params={
        "part": "snippet",
        "q": "taco truck commercial advertisement",
        "type": "video",
        "videoDuration": "short",  # < 4 minutes
        "order": "viewCount",
        "maxResults": 20,
        "key": API_KEY
    }
)

videos = response.json()["items"]
for video in videos:
    print(f"{video['snippet']['title']} - {video['id']['videoId']}")
```

### Get Video Statistics
```python
# Get view counts, likes (1 quota unit per video)
video_ids = ",".join([v["id"]["videoId"] for v in videos])

response = requests.get(
    "https://www.googleapis.com/youtube/v3/videos",
    params={
        "part": "statistics,contentDetails",
        "id": video_ids,
        "key": API_KEY
    }
)

for video in response.json()["items"]:
    stats = video["statistics"]
    print(f"Views: {stats['viewCount']}, Likes: {stats.get('likeCount', 'N/A')}")
```

**Quota Costs**:
| Operation | Cost |
|-----------|------|
| search.list | 100 |
| videos.list | 1 |
| channels.list | 1 |
| commentThreads.list | 1 |

**Daily Limit**: 10,000 units

---

## 3. Replicate (Image Generation)

**Get Token**: https://replicate.com/account/api-tokens

### Generate Storyboard Frame
```python
import replicate
import os

os.environ["REPLICATE_API_TOKEN"] = "your-token"

# Using FLUX Schnell (fast, good for storyboards)
output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": "Commercial advertisement frame: A happy customer eating a taco at a food truck, golden hour lighting, professional photography, 16:9 aspect ratio",
        "num_outputs": 1,
        "aspect_ratio": "16:9",
        "output_format": "webp",
        "output_quality": 80
    }
)

image_url = output[0]
print(f"Generated image: {image_url}")
```

### Alternative: FLUX Dev (higher quality, slower)
```python
output = replicate.run(
    "black-forest-labs/flux-dev",
    input={
        "prompt": "...",
        "guidance": 3.5,
        "num_outputs": 1,
        "aspect_ratio": "16:9",
        "output_format": "webp"
    }
)
```

**Free Tier**: ~50 generations/month

**Prompt Tips for Storyboards**:
```
"Commercial advertisement frame: [scene description], 
professional cinematography, [style] style, 
16:9 aspect ratio, high production value"
```

---

## 4. ElevenLabs (Text-to-Speech)

**Get Key**: https://elevenlabs.io/app/settings/api-keys

### Generate Voiceover
```python
import requests

API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# Free voice IDs:
# Rachel (female): 21m00Tcm4TlvDq8ikWAM
# Antoni (male): ErXwobaYiN019PkySvjV
# Domi (female): AZnzlk1XvdvUeBnXmlld
# Bella (female): EXAVITQu4vr4xnSDxMaL

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "text": "Craving authentic street tacos? Visit Taco Loco, where every bite is a fiesta!",
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
)

# Save audio file
with open("voiceover.mp3", "wb") as f:
    f.write(response.content)
```

### Get Available Voices
```python
response = requests.get(
    "https://api.elevenlabs.io/v1/voices",
    headers={"xi-api-key": API_KEY}
)

for voice in response.json()["voices"]:
    print(f"{voice['name']}: {voice['voice_id']}")
```

**Free Tier**: 10,000 characters/month (~10 minutes of audio)

---

## 5. Google Places API

**Get Key**: Same Google Cloud project as YouTube

### Text Search for Locations
```python
import requests

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")

# New Places API (Text Search)
response = requests.post(
    "https://places.googleapis.com/v1/places:searchText",
    headers={
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.photos,places.rating,places.priceLevel"
    },
    json={
        "textQuery": "event venue filming location Providence RI",
        "maxResultCount": 5
    }
)

for place in response.json().get("places", []):
    print(f"{place['displayName']['text']} - {place['formattedAddress']}")
```

### Legacy Places API (simpler)
```python
response = requests.get(
    "https://maps.googleapis.com/maps/api/place/textsearch/json",
    params={
        "query": "restaurant filming location Providence",
        "key": API_KEY
    }
)

for result in response.json()["results"][:5]:
    print(f"{result['name']} - {result['formatted_address']}")
```

**Free Tier**: Part of $300 Google Cloud credit (90 days)

---

## 6. uAgents (Fetch.AI)

### Basic Agent Setup
```python
from uagents import Agent, Context, Model

class MyRequest(Model):
    message: str

class MyResponse(Model):
    reply: str

agent = Agent(
    name="my-agent",
    seed="my-secret-seed-phrase",
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

@agent.on_message(model=MyRequest)
async def handle_request(ctx: Context, sender: str, msg: MyRequest):
    ctx.logger.info(f"Received: {msg.message}")
    await ctx.send(sender, MyResponse(reply="Got it!"))

if __name__ == "__main__":
    agent.run()
```

### Chat Protocol (Required for ASI:One)
```python
from uagents import Agent, Context
from uagents.experimental.chat_protocol import ChatProtocol, ChatMessage, TextContent

agent = Agent(
    name="adboard-orchestrator",
    seed="your-seed-phrase",
    port=8000,
    endpoint=["http://your-server:8000/submit"]
)

chat_proto = ChatProtocol(agent)

@chat_proto.on_message
async def handle_chat(ctx: Context, msg: ChatMessage):
    # Extract text from message
    user_text = ""
    for content in msg.content:
        if isinstance(content, TextContent):
            user_text = content.text
            break
    
    ctx.logger.info(f"User said: {user_text}")
    
    # Process and respond
    response = await process_request(user_text)
    
    # Send response back
    await ctx.send(
        msg.sender,
        ChatMessage(content=[TextContent(text=response)])
    )

agent.include(chat_proto)

if __name__ == "__main__":
    agent.run()
```

### Agent-to-Agent Communication
```python
# Orchestrator sending to Research Agent
RESEARCH_AGENT_ADDRESS = "agent1qxxxxxxxxx..."

@chat_proto.on_message
async def handle_chat(ctx: Context, msg: ChatMessage):
    # Send request to Research Agent
    await ctx.send(
        RESEARCH_AGENT_ADDRESS,
        ResearchRequest(industry="food", product_type="taco truck")
    )

# Research Agent receiving and responding
@agent.on_message(model=ResearchRequest)
async def handle_research(ctx: Context, sender: str, msg: ResearchRequest):
    # Do research...
    results = await do_youtube_research(msg.industry)
    
    # Send back to orchestrator
    await ctx.send(sender, ResearchResponse(results=results))
```

### Deploy to Agentverse
1. Go to https://agentverse.ai
2. Click "Launch an Agent" → "Chat Protocol"
3. Enter agent name and endpoint URL
4. Add keywords for discoverability
5. Run the registration script they provide

---

## Environment Variables Template

```bash
# .env file
GROQ_API_KEY=gsk_xxxxxxxxxxxx
YOUTUBE_API_KEY=AIzaxxxxxxxxxxxxxxx
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxx
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_PLACES_API_KEY=AIzaxxxxxxxxxxxxxxx

# Fetch.AI
AGENT_SEED_PHRASE="your twelve word seed phrase here for agent"
AGENTVERSE_API_KEY=xxxxxxxx
```

---

## Quick Test Script

```python
"""Test all APIs are working"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    from groq import Groq
    client = Groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'Groq works!'"}],
        max_tokens=10
    )
    print(f"Groq: {response.choices[0].message.content}")

def test_youtube():
    import requests
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={"part": "snippet", "q": "test", "maxResults": 1, 
                "key": os.environ["YOUTUBE_API_KEY"]}
    )
    print(f"YouTube: {r.status_code == 200}")

def test_replicate():
    import replicate
    # Just test auth
    models = replicate.models.list()
    print(f"Replicate: Connected")

def test_elevenlabs():
    import requests
    r = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}
    )
    print(f"ElevenLabs: {r.status_code == 200}")

if __name__ == "__main__":
    test_groq()
    test_youtube()
    test_replicate()
    test_elevenlabs()
    print("\nAll APIs tested!")
```
