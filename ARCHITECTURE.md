# Marky Architecture

This document describes the architecture of the Marky ad research system—a single-entry-point uAgent that orchestrates four intelligence agents to produce ad research reports for local businesses.

---

## Overview

**Marky** accepts a business type and location (e.g., *"electrician in Providence, RI"*), runs four specialized agents in sequence, and synthesizes the results into an ad research report. The system uses the **uAgents framework** (Fetch.ai) for Agentverse/ASI:One compatibility.

### Goals

- **Single entry point** – One agent to chat with; internal orchestration is hidden
- **Modular agents** – Each intelligence agent has a clear responsibility and can run standalone
- **Sequential workflow** – Stages run in order because later stages depend on earlier outputs
- **Raw data collection** – No filtering or synthesis; all collected data is passed through for downstream agents (e.g., filter agent, ad generator)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTRY POINTS                                       │
├─────────────────────────────────┬───────────────────────────────────────────┤
│  uAgent (run_marky.py)          │  CLI (run_marky.py --cli)                  │
│  • Chat protocol                │  • Direct workflow execution               │
│  • Agentverse/ASI:One           │  • JSON output option                      │
│  • Mailbox for discovery        │                                            │
└─────────────────────────────────┴───────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR (orchestrator/)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  agent.py          – uAgent setup, chat protocol, request parsing            │
│  workflow.py       – MarkyWorkflow: runs 5 stages, synthesis                 │
│  models.py         – AdResearchRequest, AdResearchResult, data structures    │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW PIPELINE (5 Stages)                         │
│                                                                              │
│  Stage 1: Local Intel      → Competitors, websites, differentiators          │
│  Stage 2: Review Intel     → Google Reviews voice-of-customer (needs place_ids)
│  Stage 3: Yelp Intel       → Yelp reviews, pain/praise, ad suggestions       │
│  Stage 4: Trends Intel     → Keywords, CPC, seasonal timing                  │
│  Stage 5: Output           → Raw data combined (no filtering)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Entry Points

### 1. uAgent Mode (Agentverse)

```
python run_marky.py
```

- Starts Marky as a uAgent with `mailbox=True` for Agentverse discovery
- Uses the **chat protocol** (`chat_protocol_spec`) for compatibility
- User sends messages like *"electrician in Providence, RI"*
- Marky parses the request, runs the workflow, and streams back the report as chat messages

**Flow:** User message → `parse_research_request()` → `MarkyWorkflow.run()` → `AdResearchResponse.to_markdown()` → Chat reply

### 2. CLI Mode

```
python run_marky.py --cli -b "electrician" -l "Providence, RI"
```

- Bypasses the uAgent; calls `MarkyWorkflow.run()` directly
- Useful for local testing and CI
- Supports `--no-trends` and `--json` flags

### 3. Test Client

```
python test_marky_client.py -q "electrician in Providence, RI"
```

- Connects to a running Marky uAgent and sends a query
- Simulates an Agentverse client

---

## Orchestrator

### agent.py – uAgent Entry Point

| Component | Purpose |
|-----------|---------|
| `marky_agent` | uAgents `Agent` instance (name, seed, port, mailbox) |
| `chat_proto` | Protocol wrapping `chat_protocol_spec` |
| `parse_research_request()` | Extracts `(business_type, location)` from natural language |
| Message handler | On incoming chat message: parse → run workflow → send response |

### workflow.py – MarkyWorkflow

The workflow instantiates all four agents and runs them **sequentially**:

```
MarkyWorkflow.__init__()
  ├── self.local_intel   = LocalIntelAgent()
  ├── self.review_intel  = ReviewIntelAgent()
  ├── self.yelp_intel    = YelpIntelAgent()
  └── self.trends_intel  = TrendsIntelAgent()
```

**Dependencies between stages:**

| Stage | Depends On | Output Used By |
|-------|------------|----------------|
| 1. Local Intel | — | Stage 2 (place_ids), Synthesis |
| 2. Review Intel | Local Intel (place_ids) | Synthesis (customer_voice) |
| 3. Yelp Intel | — | Synthesis (merged with Review Intel) |
| 4. Trends Intel | — | Synthesis (timing) |
| 5. Synthesis | All above | Final report |

---

## Intelligence Agents

### 1. Local Intel (`local_intel/`)

**Purpose:** Discover local competitors and analyze their websites.

| Step | What It Does | API |
|------|--------------|-----|
| 1 | Search Google Maps for top-rated (and worst-rated) businesses in the area | SerpAPI |
| 2 | Scrape competitor websites (HTML content) | Firecrawl, Jina (fallback) |
| 3 | Extract services, trust signals, USPs, pricing patterns | Regex / content_extractor |
| 4 | Derive market analysis (common services, gaps) | — |
| 5 | Generate differentiators and headlines | — |
| 6 | Compare high vs low-rated competitors (success/failure patterns) | Anthropic Claude |

**Outputs:** Competitors (name, rating, place_id, website, services, trust_signals), differentiators, headline_suggestions, market_analysis

**Key files:** `agent.py`, `competitor_discovery.py`, `website_scraper.py`, `content_extractor.py`, `ad_generator.py`

---

### 2. Review Intel (`review_intel/`)

**Purpose:** Extract voice-of-customer from **Google Reviews** of the competitors found by Local Intel.

| Step | What It Does | API |
|------|--------------|-----|
| 1 | Fetch Google Reviews for each competitor using `place_id` | SerpAPI (Google Maps Reviews) |
| 2 | Extract pain points, desires, praise/complaint quotes | Keyword matching, theme extraction |
| 3 | Generate ad hooks and headlines from customer language | — |

**Input:** List of competitors with `place_id` from Local Intel  
**Outputs:** VoiceOfCustomer (pain_points, desires, praise_quotes, complaint_quotes), ad_hooks, headlines, top_competitor_themes

**Key files:** `agent.py`, `scraper.py`, `models.py`

---

### 3. Yelp Intel (`yelp_intel/`)

**Purpose:** Extract voice-of-customer from **Yelp** reviews (independent search, not tied to Local Intel competitors).

| Step | What It Does | API |
|------|--------------|-----|
| 1 | Search Yelp for businesses matching business type + location | SerpAPI (Yelp) |
| 2 | Fetch positive and negative reviews per business | SerpAPI |
| 3 | Extract pain points, praise points, themes, full phrases | Keyword + sentence extraction |
| 4 | Generate ad suggestions (hooks, headlines, pain_point_hooks) | — |

**Outputs:** Insights (pain_points, praise_points, themes, quotes), ad_suggestions (hooks, headlines, trust_signals)

**Note:** Results are **merged** with Review Intel in Synthesis (deduplicated pain points, desires, quotes).

**Key files:** `agent.py`, `scraper.py`, `models.py`

---

### 4. Trends Intel (`trends_intel/`)

**Purpose:** Provide keyword search volume, CPC, and seasonal timing for ad planning.

| Step | What It Does | API |
|------|--------------|-----|
| 1 | Fetch search volume, CPC, competition for target keywords | DataForSEO |
| 2 | Identify peak and low months from trends data | DataForSEO |
| 3 | Produce timing recommendations | — |

**Input:** Keywords derived from business type (e.g., "electrician", "electrician near me", "best electrician")  
**Outputs:** Keyword data (search_volume, cpc), seasonal_insights (peak_months, low_months, recommendation)

**Key files:** `agent.py`, `scraper.py`, `models.py`

---

## Output Stage (Raw Data, No Filtering)

After all four agents run, the workflow **combines** results without any filtering or synthesis:

| Data | Sources | Treatment |
|------|---------|-----------|
| Competitors | Local Intel | Raw: name, rating, strengths, services (no limits) |
| Pain points & desires | Review Intel + Yelp Intel | Raw merge (no dedup, no normalization) |
| Hooks | Review Intel + Yelp Intel | Raw (no filtering of quotes or testimonials) |
| Headlines | Local Intel + Review Intel + Yelp Intel | Raw (no dedup) |
| Trust signals | Local Intel + Yelp Intel | Raw (no normalization) |
| Seasonal timing | Trends Intel | Raw peak months, CPC, volume |

**No quality passes applied.** Output is intended for downstream agents (filter agent, ad generator) to process.

---

## Data Flow

```
AdResearchRequest (business_type, location)
        │
        ▼
┌───────────────────┐
│ Local Intel       │ → Competitors (place_id, trust_signals, services)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Review Intel      │ → CustomerVoice (pain_points, desires, quotes)
│ (needs place_ids) │   Ad hooks, headlines
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Yelp Intel        │ → Merges into CustomerVoice
│ (parallel source) │   Adds hooks, headlines, trust_signals
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Trends Intel      │ → SeasonalTiming (peak_months, CPC, volume)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Synthesis         │ → AdResearchResult
│                   │   • Executive summary
│                   │   • Key insights
│                   │   • Emotional angles
│                   │   • Recommended hooks
│                   │   • Headlines, trust signals
└─────────┬─────────┘
          │
          ▼
AdResearchResponse.to_markdown() → Final report (Markdown)
```

---

## Project Structure

```
hackbrown_testing/
├── run_marky.py              # Main entry (uAgent + CLI)
├── test_marky_client.py      # Test client for uAgent
│
├── orchestrator/
│   ├── agent.py              # uAgent, chat protocol, request parsing
│   ├── workflow.py           # MarkyWorkflow, 5-stage pipeline, synthesis
│   └── models.py             # AdResearchRequest, AdResearchResult, etc.
│
├── local_intel/
│   ├── agent.py              # LocalIntelAgent
│   ├── competitor_discovery.py  # SerpAPI Google Maps
│   ├── website_scraper.py    # Firecrawl / Jina
│   ├── content_extractor.py  # Services, trust signals, USPs
│   ├── ad_generator.py       # Differentiators, headlines
│   └── models.py             # IntelligenceReport, Competitor, etc.
│
├── review_intel/
│   ├── agent.py              # ReviewIntelAgent
│   ├── scraper.py            # SerpAPI Google Maps Reviews
│   └── models.py             # ReviewAnalysis, VoiceOfCustomer
│
├── yelp_intel/
│   ├── agent.py              # YelpIntelAgent
│   ├── scraper.py            # SerpAPI Yelp (retry logic)
│   └── models.py             # YelpAnalysis, CustomerInsights
│
├── trends_intel/
│   ├── agent.py              # TrendsIntelAgent
│   ├── scraper.py            # DataForSEO
│   └── models.py             # TrendsAnalysis, SeasonalInsight
│
├── output/                   # Generated reports (local_intel_*.json, etc.)
├── ARCHITECTURE.md           # This file
├── AGENTS.md                 # Agent reference (standalone commands)
└── README.md                 # User-facing quick start
```

---

## APIs Used

| Agent | API | Purpose |
|-------|-----|---------|
| local_intel | SerpAPI | Google Maps competitor search |
| local_intel | Firecrawl | Website scraping (primary) |
| local_intel | Jina Reader | Fallback scraping |
| local_intel | Anthropic (Claude) | Success/failure analysis |
| review_intel | SerpAPI | Google Maps Reviews |
| yelp_intel | SerpAPI | Yelp search and reviews |
| trends_intel | DataForSEO | Keyword volume, CPC, trends |

---

## Running Individual Agents

Each agent can run standalone for debugging or modular use:

```bash
python run_local_intel.py -b "electrician" -l "Providence, RI" --max-competitors 5
python run_review_intel.py --from-local-intel latest
python run_yelp_intel.py -b "electrician" -l "Providence, RI" -m 5
python run_trends_intel.py -k "electrician" "electrician near me"
```

See `AGENTS.md` for full agent reference and outputs.
