# Quick Start - Get Running in 30 Minutes

## Step 1: Get Your API Keys (15 min)

Open these in browser tabs and sign up:

| Service | URL | Time | Notes |
|---------|-----|------|-------|
| Groq | https://console.groq.com | 2 min | Instant approval, no card |
| YouTube | https://console.cloud.google.com | 5 min | Enable "YouTube Data API v3" |
| Replicate | https://replicate.com | 2 min | Instant, no card for free tier |
| ElevenLabs | https://elevenlabs.io | 2 min | Instant, no card |
| Google Places | Same as YouTube | 0 min | Already done if you did YouTube |

## Step 2: Setup Project (5 min)

```bash
cd /Users/tomalmog/programming/Febuary\ 2026/Brown

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in keys
cp .env.example .env
# Edit .env with your keys
```

## Step 3: Test APIs (5 min)

Create `test_apis.py` in project root:

```python
import os
from dotenv import load_dotenv
load_dotenv()

def test_groq():
    from groq import Groq
    client = Groq()
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'works'"}],
        max_tokens=5
    )
    print(f"✓ Groq: {r.choices[0].message.content}")

def test_youtube():
    import requests
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={"part": "snippet", "q": "test", "maxResults": 1, 
                "key": os.environ["YOUTUBE_API_KEY"]}
    )
    print(f"✓ YouTube: {r.status_code == 200}")

def test_elevenlabs():
    import requests
    r = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}
    )
    print(f"✓ ElevenLabs: {r.status_code == 200}")

if __name__ == "__main__":
    test_groq()
    test_youtube()
    test_elevenlabs()
    print("\n🎉 All APIs working!")
```

Run: `python test_apis.py`

## Step 4: Run Your First Agent (5 min)

```python
# test_agent.py
from uagents import Agent, Context

agent = Agent(name="test", seed="test-seed-12345")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Agent started! Address: {agent.address}")

if __name__ == "__main__":
    agent.run()
```

Run: `python test_agent.py`

You should see your agent address printed. That's the address you'll register on Agentverse!

---

## Priority Order for Building

### Must Have (MVP for Demo)
1. ✅ Orchestrator with Chat Protocol (ASI:One compatible)
2. ✅ Research Agent (YouTube search)
3. ✅ Script Writer (Groq)
4. ✅ Storyboard Generator (Replicate)

### Nice to Have
5. Voiceover (ElevenLabs)
6. Cost Estimator (Groq)
7. Location Scout (Google Places)
8. PDF Generator

### Stretch Goals
9. Payment Protocol integration
10. Deploy all agents to Agentverse (not just orchestrator)

---

## Files Already Created

```
Brown/
├── README.md                 ✅ Done (with badges!)
├── requirements.txt          ✅ Done
├── .env.example              ✅ Done
├── docs/
│   ├── MASTER_PLAN.md        ✅ Full technical plan
│   ├── API_REFERENCE.md      ✅ Copy-paste API examples
│   └── QUICK_START.md        ✅ This file
├── agents/
│   ├── __init__.py           ✅ Done
│   └── models.py             ✅ All message models defined
├── utils/
│   └── __init__.py           ✅ Done
└── config/
    ├── __init__.py           ✅ Done
    └── settings.py           ✅ All config + prompts
```

---

## What to Build Next

Start with the Orchestrator - it's the most important for the Fetch.AI track:

```
agents/orchestrator.py  ← START HERE
```

Then build in this order:
```
utils/groq_client.py
utils/youtube_client.py
agents/research_agent.py
agents/creative_director.py
utils/replicate_client.py
```

---

## Judging Criteria Reminder

| Criteria | Weight | How We Hit It |
|----------|--------|---------------|
| Functionality | 25% | Working end-to-end demo |
| Fetch.AI Tech | 20% | Agentverse + Chat Protocol + Multi-agent |
| Innovation | 20% | Novel use case (ad storyboarding) |
| Real-World Impact | 20% | Solves real SMB problem |
| UX & Presentation | 15% | Clean demo video |

**Target Prize**: Best Multi-Agent Workflow ($500)
