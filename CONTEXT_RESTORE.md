# AdBoard AI - Project Context & Status
**Last Updated:** January 31, 2026, ~8:50 PM EST
**Event:** Hack@Brown 2026 - Fetch.AI Track

---

## 🚀 Project Overview
AdBoard AI is a multi-agent storyboard video advertising system. Users requests (e.g., "coffee shop in Toronto") trigger a pipeline of 11+ agents that research, write, and produce a complete 30-second video advertisement with professional voiceover and music.

## ⚡️ Current Status: "It Works, But..."
The system is **fully functional end-to-end**.
- ✅ **Orchestrator** is running and handling ASI:One requests.
- ✅ **Pipeline** successfully generates videos from text prompts.
- ✅ **Delivery** uploads videos to `tmpfiles.org` and returns direct playback links.
- ✅ **Integration** of teammate's research code is "complete" (code-wise).

**HOWEVER:**
> **⚠️ Critical Partner Feedback:** "The research isn't being done properly."

This is the current priority. We have integrated the code, but we need to verify its quality, ensuring it's not just running but actually producing valuable, accurate intelligence.

---

## 🛠 Recent Major Changes & Integrations

### 1. Enhanced Research Intelligence (Current Integration Status)
We integrated the **`ad_intel_no`** package (from teammate) into the main pipeline. 
**Current State:** We have only partially integrated the "Marky" workflow.
1.  ✅ **`local_intel` (Partial):** We integrated `GoogleAdsScraper` (SerpAPI).
2.  ❌ **`local_intel` (Missing):** Website scraping via Firecrawl/Jina (API keys added, but code not wired).
3.  ❌ **`review_intel` (Missing):** Google Reviews analysis (needs place_ids).
4.  ❌ **`yelp_intel` (Missing):** Yelp reviews and customer voice.
5.  ❌ **`trends_intel` (Missing):** Keyword data and CPC via DataForSEO.

**Teammate's Vision ("Marky"):**
The full research suite uses 4 specific agents:
- **`local_intel`**: Competitor discovery (SerpAPI) + Website scraping (Firecrawl/Jina).
- **`review_intel`**: Google Reviews for competitors.
- **`yelp_intel`**: Yelp reviews/customer voice.
- **`trends_intel`**: Keyword data, CPC, seasonal timing (DataForSEO).

### 2. Smart Script Writing
The `ScriptWriterAgent` was upgraded to utilize the new intelligence.
- **Location Awareness:** Now uses actual location data (from `LocationScout`) to suggest filming scenes (e.g., "Filming at [Real Location Name]").
- **Competitor differentiation:** Uses gathered competitor hooks to write scripts that stand out ("They say X, we say Y").

### 3. Video Delivery
- **Direct Playback:** Videos are now uploaded to `tmpfiles.org` via `curl`.
- **User Experience:** The chat response provides a **direct download link** that plays immediately in the browser, bypassing landing pages.
- **Natural Language Response:** The agent now replies with a clean summary, research insights, and the video link, rather than raw JSON or file paths.

### 4. Git & Security Hygiene
- **`.gitignore`**: Created to exclude `output/`, `__pycache__`, and `.env`.
- **Secrets Management**: Removed `.env` from git history. Added `.env.example`.
- **API Keys**: Added keys for missing agents (`FIRECRAWL_API_KEY`, `DATAFORSEO_PASSWORD`, etc.) to `.env`.

---

## 📂 Project Structure (Key Components)

### **Core Agents (AdBoard)**
- **`agents/orchestrator.py`**: The brain. Handles Agentverse communication and routing.
- **`agents/enhanced_research.py`**: Currently combines YouTube + partial `local_intel` (Google Ads).
- **`agents/script_writer.py`**: Writes the ad script using available research.
- **`agents/image_generator.py`**: Creates storyboard frames (Vertex AI Imagen 3).
- **`agents/voiceover_agent.py`**: Generates audio (ElevenLabs).
- **`agents/video_assembly_agent.py`**: Stitches images/audio with Ken Burns effects (FFmpeg).

### **Teammate's Research Module (`ad_intel_no/`)**
- **`ad_intel_no/scraper.py`**: Currently contains `GoogleAdsScraper` (SerpAPI).
- **`ad_intel_no/agent.py`**: Logic for analyzing scraped ad data.
- **`ad_intel_no/models.py`**: Data structures for ad analysis.
*Note: We need to pull `review_intel`, `yelp_intel`, and `trends_intel` code from the repo.*

### **Core Utilities**
- **`core/pipeline.py`**: Manages the sequential flow of data between agents.
- **`core/intent_extractor.py`**: Parses user prompts.
- **`core/groq_client.py`**: Handles LLM requests with fallback.

---

## 📝 Next Steps (The "Marky" Integration Plan)

1.  **Full "Marky" Audit & Pull (Priority #1)**
    -   **Problem:** "Research isn't being done properly."
    -   **Root Cause:** We are missing 3 out of 4 agents (`review_intel`, `yelp_intel`, `trends_intel`) and the website scraping part of `local_intel`.
    -   **Action:** Pull the missing code for these agents from the main repo.
    -   **Action:** Wire up `Firecrawl` (for website text), `DataForSEO` (for trends), and the review scrapers.

2.  **Verify Agent Integration**
    -   Ensure `EnhancedResearchAgent` orchestrates ALL 4 research sub-agents, not just YouTube/Google Ads.
    -   Aggregate insights from Reviews and Trends into the Script Writer prompt.

3.  **Refine "Context" Usage**
    -   Ensure the `ScriptWriter` isn't ignoring the new data due to context window limits or prompt formatting.

4.  **Platform Stability**
    -   Monitor ASI:One chat. If UI issues persist, ensure the fallback (terminal logs/direct links) is robust.

---

## 🔑 Environment Variables
(Check `.env` to verify these are set)
- `GROQ_API_KEY`
- `SERPAPI_KEY` (Critical for new research)
- `ELEVENLABS_API_KEY`
- `GCP_PROJECT_ID` / `GOOGLE_APPLICATION_CREDENTIALS`
- `AGENT_SEED_PHRASE` / `AGENTVERSE_API_KEY`
