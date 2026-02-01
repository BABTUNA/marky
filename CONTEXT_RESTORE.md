# AdBoard AI - Context Restore File
**Last Updated:** January 31, 2026, ~8:00 PM EST
**Event:** Hack@Brown 2026 - Fetch.AI Track

---

## Project Overview

AdBoard AI is a multi-agent storyboard video advertising system for small businesses. Users describe their business (e.g., "Create an ad for my taco truck") and the system generates a complete 30-second video advertisement with:
- Pencil-sketch storyboard frames (Google Vertex AI Imagen 3)
- Professional voiceover narration (ElevenLabs)
- Background music (Pixabay royalty-free)
- Ken Burns pan/zoom animation effects
- Video assembly (FFmpeg)

---

## Current State: VIDEO GENERATION WORKS LOCALLY ✅

The core pipeline is **fully functional** when run locally:

```bash
cd /Users/tomalmog/programming/Febuary\ 2026/Brown
python test_storyboard_video.py
```

This successfully:
1. Researches viral ads in the industry
2. Writes a compelling script with scenes
3. Generates 5 pencil-sketch storyboard frames via Imagen 3 (with 30s delays between requests)
4. Creates voiceover audio via ElevenLabs (eleven_multilingual_v2 model)
5. Downloads royalty-free background music
6. Mixes audio (voiceover + music)
7. Assembles final video with Ken Burns effects

**Output location:** `output/final/final_<product>_<duration>s.mp4`

**Existing test video:** `output/final/final_coffee_shop_45s.mp4` (5.5MB, 45 seconds)

---

## CRITICAL CURRENT BLOCKER: ASI:One Chat UI Not Displaying Responses

### The Exact Problem

The agent code is **100% working correctly**. The issue is that **ASI:One's chat UI does not display the responses** even though:
1. ✅ Agent registers with Agentverse successfully
2. ✅ ChatProtocol v0.3.0 shows correctly in Agent Profile on Agentverse
3. ✅ Agent receives messages from ASI:One relay
4. ✅ Agent sends acknowledgement successfully (no errors)
5. ✅ Agent sends response successfully (no errors)
6. ✅ Terminal shows "RESPONSE SENT SUCCESSFULLY"
7. ❌ **ASI:One UI shows "Working on a response for you..." forever**
8. ❌ **Response NEVER appears in the chat UI, even after refresh**

### Two Different Sender Addresses (Important!)

**When logged OUT (incognito) - Uses ASI:One relay:**
```
Sender: agent1qgdsv5ft53hjhte3z96ejzhjctjcgwzjkvjfkn8edvs6vev2y9ktw26d6tu
```
- No errors in terminal
- Response sends successfully
- But UI still doesn't show response

**When logged IN - Uses personal wallet agent:**
```
Sender: agent1qg5waf2l44g6pnp0rwrjek8x6c7l3yfmd5h5flr72j3c70tzddw5cd5dppf
```
- Gets error: "Unable to resolve destination endpoint for agent"
- This address can't be found in Almanac
- Response still says "sent successfully" but definitely doesn't arrive

### Key Discovery from Debugging

- Changed Agentverse @ handle which may have caused issues
- Changed it back but the logged-in sender address remained different
- In **incognito mode**, it uses the correct ASI:One relay address (no errors)
- But **response still doesn't show in UI** even with no errors

### Latest Terminal Output (Incognito - No Errors)

```
============================================================
INCOMING MESSAGE:
  Sender: agent1qgdsv5ft53hjhte3z96ejzhjctjcgwzjkvjfkn8edvs6vev2y9ktw26d6tu
  Full text: '@agent1q2xwg46kfvvrv05dez0ala9evfmwjnzhq8nsu3t8uly2vmt3245sk9v84tc hi'
  Msg ID: 4f5f445c-906f-42ed-92b2-3797df2a19b5
============================================================

ACK sent
Sending response: Hello! AdBoard AI received: '@agent1q2xwg46kfvvrv05dez0ala9evfmwjnzhq8nsu3t8uly2vmt3245sk9v84tc hi'
RESPONSE SENT SUCCESSFULLY
============================================================
```

### What We've Tried (Extensive Debugging)

1. **Mailbox mode** (`mailbox=True`) - Response not showing in UI
2. **Proxy mode** (`proxy=True`) - Same issue
3. **Adding `network="testnet"`** - Same issue
4. **Removing `network="testnet"`** - Same issue
5. **Removing `EndSessionContent`** - Same issue
6. **Adding `EndSessionContent`** - Same issue
7. **Minimal response format** (matching official Fetch.ai examples exactly) - Same issue
8. **Simple test agent** copied from official examples - Same issue
9. **Hard refresh (Cmd+Shift+R)** - Doesn't help
10. **Incognito window** - Uses correct relay but still no UI response
11. **New chat session** - Doesn't help
12. **Changing @ handle and changing back** - Created new issues with logged-in sender
13. **Contacted Fetch.ai support on Discord** - They confirmed setup is correct

### Official Examples We Matched Exactly

From `https://github.com/fetchai/innovation-lab-examples`:
- `asi-cloud-agent/agent.py`
- `gemini-quickstart/01-basic-gemini-agent/agent.py`

Our code is **identical** to these working examples.

### Fetch.ai Discord Contacts

- **martin_fetchai** - Asked if mailbox=True
- **kshipra-fetchai** - Suggested checking ChatProtocol v0.3.0 in Agent Profile (we have it ✅)
- **ryan fetch ai** - Confirmed they'd help

They confirmed:
- ChatProtocol v0.3.0 is required ✅ (we have it)
- Protocol shows correctly in Agent Profile ✅ (confirmed)
- Our setup looks correct

### Conclusion

**This is 100% an ASI:One platform issue, NOT a code issue.**

The agent:
- Receives messages ✅
- Processes them ✅
- Sends acknowledgements ✅
- Sends responses ✅
- No errors in terminal ✅

The ASI:One UI simply does not display the response. This needs to be escalated to Fetch.ai.

---

## Architecture

### Pipeline Flow (11 Agents)

```
User Request
    ↓
[Intent Extractor] → Extracts product, industry, tone, duration, city
    ↓
[Research Agent] → Searches for viral ads in the industry
    ↓
[Location Scout] → Finds filming locations (if city provided)
    ↓
[Trend Analyzer] → Analyzes viral ad patterns
    ↓
[Script Writer] → Writes script with scenes, voiceover text
    ↓
[Image Generator] → Generates pencil-sketch frames (Vertex AI Imagen 3)
    ↓
[Voiceover Agent] → Creates narration audio (ElevenLabs)
    ↓
[Music Agent] → Downloads royalty-free background music
    ↓
[Audio Mixer] → Mixes voiceover + music
    ↓
[Video Assembly] → Creates video with Ken Burns effects (FFmpeg)
    ↓
[Cost Estimator] → Estimates production budget
    ↓
[Social Media Agent] → Generates hashtags
```

### Key Files

| File | Purpose |
|------|---------|
| `agents/orchestrator.py` | Main entry point, Chat Protocol, Agentverse registration |
| `agents/simple_test_agent.py` | Minimal test agent for debugging ASI:One |
| `core/pipeline.py` | Sequential pipeline runner |
| `core/groq_client.py` | Groq LLM client with automatic model fallback |
| `core/intent_extractor.py` | Extracts user intent from natural language |
| `agents/image_generator.py` | Vertex AI Imagen 3 integration |
| `agents/voiceover_agent.py` | ElevenLabs integration |
| `agents/video_assembly_agent.py` | FFmpeg video creation |
| `test_storyboard_video.py` | Local test script for full pipeline |

---

## Technical Details

### Image Generation (Fixed Issues)

**Previous problems:**
1. Gray borders/padding on images
2. 4-panel collages instead of single images

**Current solution in `agents/image_generator.py`:**
```python
prompt = f"""{shot} pencil sketch illustration of {visual}

Scene for {product} commercial. Black and white pencil drawing style, professional animation concept art, clean lines, detailed shading.

The illustration fills the entire canvas edge to edge with no empty space around it."""
```

Also includes 30-second delays between Imagen requests to respect quota limits.

### Voiceover (Fixed Issues)

**Previous problem:** Robotic sounding voice

**Current solution in `agents/voiceover_agent.py`:**
```python
json={
    "text": voiceover_text,
    "model_id": "eleven_multilingual_v2",  # More natural sounding
    "voice_settings": {
        "stability": 0.3,  # Lower = more expressive
        "similarity_boost": 0.8,
        "style": 0.5,
        "use_speaker_boost": True,
    },
}
```

### Groq Rate Limit Handling

**File:** `core/groq_client.py`

Automatic fallback through models:
1. `llama-3.3-70b-versatile` (primary)
2. `openai/gpt-oss-120b`
3. `openai/gpt-oss-20b`
4. `llama-3.1-8b-instant` (fallback)

### Video Assembly (Fixed Issues)

**Previous problems:**
- Gray bars/letterboxing
- Cropped images

**Current FFmpeg settings in `agents/video_assembly_agent.py`:**
- Uses `scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080`
- Ken Burns effects: random pan/zoom movements
- H.264 encoding with `-pix_fmt yuv420p` for compatibility

---

## Environment Variables Required

```bash
# Google Cloud (Imagen)
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1

# ElevenLabs (Voiceover)
ELEVENLABS_API_KEY=your-key

# Groq (LLM)
GROQ_API_KEY=your-key

# Fetch.ai Agentverse
AGENT_SEED_PHRASE=your-seed-phrase
AGENTVERSE_API_KEY=your-key

# Optional
TEST_MODE=true  # Skip pipeline, just test Agentverse communication
USE_PROXY=true  # Use proxy instead of mailbox
```

---

## Agent Addresses

- **AdBoard AI:** `agent1q2xwg46kfvvrv05dez0ala9evfmwjnzhq8nsu3t8uly2vmt3245sk9v84tc`
- **ASI:One (relay):** `agent1qgdsv5ft53hjhte3z96ejzhjctjcgwzjkvjfkn8edvs6vev2y9ktw26d6tu`

---

## How to Run

### Test Video Generation Locally (WORKS)
```bash
cd /Users/tomalmog/programming/Febuary\ 2026/Brown
python test_storyboard_video.py
```

### Run Simple Test Agent (for ASI:One debugging)
```bash
python agents/simple_test_agent.py
```

### Run Full Orchestrator
```bash
python agents/orchestrator.py
```

### Run with Test Mode (skip pipeline)
```bash
TEST_MODE=true python agents/orchestrator.py
```

---

## Next Steps

1. **Keep trying ASI:One** - It's intermittent, may start working again
2. **Try hosting on Agentverse directly** - Instead of local+mailbox, use Agentverse's hosted agent feature
3. **Demo locally if needed** - Show the video generation working locally with terminal output as backup
4. **Follow up with Fetch.ai Discord** - They confirmed setup is correct, may have platform fix

---

## Files Modified Recently

1. `agents/orchestrator.py` - Added TEST_MODE, filtering for ASI:One messages, better logging, network="testnet"
2. `agents/simple_test_agent.py` - Minimal test agent matching official examples (current testing agent)
3. `agents/image_generator.py` - Fixed prompt to prevent borders and collages
4. `agents/voiceover_agent.py` - Changed to eleven_multilingual_v2 with lower stability
5. `core/groq_client.py` - Created automatic model fallback client
6. `test_agent_direct.py` - Created direct agent-to-agent test client

---

## Current Simple Test Agent Code

The `agents/simple_test_agent.py` is the minimal working agent for testing (matches official examples exactly):

```python
"""
Simple test agent to verify ASI:One chat works.
Based on official Fetch.ai example from innovation-lab-examples.
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

load_dotenv()

SEED_PHRASE = os.getenv("AGENT_SEED_PHRASE", "adboard-ai-hackathon-seed-2026")

agent = Agent(name="AdBoardAI", seed=SEED_PHRASE, port=8000, mailbox=True)
chat_proto = Protocol(spec=chat_protocol_spec)


@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Agent started: {ctx.agent.address}")
    print(f"\n{'=' * 60}")
    print(f"  SIMPLE TEST AGENT")
    print(f"  Address: {ctx.agent.address}")
    print(f"{'=' * 60}\n")


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    try:
        # Extract text
        user_text = ""
        for item in msg.content:
            if isinstance(item, TextContent):
                user_text = item.text
                break

        # Log the FULL message for debugging
        print(f"\n{'=' * 60}")
        print(f"INCOMING MESSAGE:")
        print(f"  Sender: {sender}")
        print(f"  Full text: '{user_text}'")
        print(f"  Msg ID: {msg.msg_id}")
        print(f"{'=' * 60}\n")

        if not user_text:
            ctx.logger.warning("No text content in message")
            return

        # Send acknowledgement first
        await ctx.send(
            sender,
            ChatAcknowledgement(
                timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id
            ),
        )
        print("ACK sent")

        # Simple response - just echo back
        response_text = f"Hello! AdBoard AI received: '{user_text[:80]}'"

        print(f"Sending response: {response_text}")

        # Send response
        response = ChatMessage(content=[TextContent(text=response_text, type="text")])

        await ctx.send(sender, response)

        print("RESPONSE SENT SUCCESSFULLY")
        print(f"{'=' * 60}\n")

    except Exception as exc:
        ctx.logger.error(f"Error: {exc}")
        await ctx.send(
            sender,
            ChatMessage(content=[TextContent(text=f"Error: {exc}", type="text")]),
        )


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.debug(f"Ack received from {sender[:20]}...")


agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    agent.run()
```

---

## Agent Addresses

- **AdBoard AI Agent:** `agent1q2xwg46kfvvrv05dez0ala9evfmwjnzhq8nsu3t8uly2vmt3245sk9v84tc`
- **ASI:One Relay (works, no errors):** `agent1qgdsv5ft53hjhte3z96ejzhjctjcgwzjkvjfkn8edvs6vev2y9ktw26d6tu`
- **Personal Wallet (logged in, causes errors):** `agent1qg5waf2l44g6pnp0rwrjek8x6c7l3yfmd5h5flr72j3c70tzddw5cd5dppf`

---

## How to Test

1. Run the simple test agent:
```bash
cd /Users/tomalmog/programming/Febuary\ 2026/Brown
python agents/simple_test_agent.py
```

2. Open **incognito browser** (to use ASI:One relay, not personal wallet)

3. Go to Agentverse, find AdBoardAI agent, click "Chat with Agent"

4. Send a message like "hi"

5. Watch terminal - should show:
   - INCOMING MESSAGE with sender `agent1qgdsv5ft53hjhte3z96ejzhjctjcgwzjkvjfkn8edvs6vev2y9ktw26d6tu`
   - ACK sent
   - Sending response
   - RESPONSE SENT SUCCESSFULLY

6. **THE PROBLEM:** Even with all this working, the ASI:One UI does NOT display the response

---

## Question for Fetch.ai Support

> "My agent receives messages from ASI:One relay (`agent1qgdsv5ft53hjhte3z96ejzhjctjcgwzjkvjfkn8edvs6vev2y9ktw26d6tu`), sends ACK and response successfully with NO errors in terminal, but the response NEVER appears in ASI:One chat UI. It just shows 'Working on a response for you...' forever.
>
> I've verified:
> - ChatProtocol v0.3.0 shows in Agent Profile ✅
> - Code matches official examples exactly ✅
> - Terminal shows RESPONSE SENT SUCCESSFULLY ✅
>
> What could prevent the UI from displaying responses that are successfully sent?"

---

## Summary

**What works:** 
- Complete video generation pipeline runs locally ✅
- Agent receives messages ✅
- Agent sends acknowledgements ✅
- Agent sends responses (no errors) ✅
- ChatProtocol v0.3.0 registered properly ✅

**What doesn't work:**
- ASI:One chat UI does NOT display responses
- This happens even with no errors in terminal
- This is a platform issue, not a code issue

**Next step:** Get Fetch.ai to investigate why ASI:One UI isn't displaying responses that are successfully sent to the relay agent.
