# Marky (Orchestrator Agent)

Single-entry-point **uAgent** that collects raw data from four intelligence agents and outputs an unfiltered report. Compatible with Fetch.ai Agentverse and ASI:One.

---

## Example Input

**Chat (natural language):**
```
electrician in Providence, RI
```
```
research plumber Boston MA
```
```
artisan coffee near San Francisco
```

**CLI:**
```bash
python run_marky.py --cli -b "electrician" -l "Providence, RI"
```

**Test client (to running uAgent):**
```bash
python test_marky_client.py -q "electrician in Providence, RI"
```

---

## Example Output (raw data, unfiltered)

```markdown
# Raw Data: electrician in providence, ri

_Unfiltered data from all agents. No synthesis or filtering applied._

## Competitors (raw)
- **M&M Electric, Inc.** (5, 273 reviews)
  - Website: https://www.mmelectric.com
  - Strengths: 30+ Years Of Experience, Family Owned, Licensed & Insured, Certified
  - Services: Service, Estimate, Installation, Panel Upgrade, Electrical Repair

- **Hartman Electrical Services** (5, 244 reviews)
  - Strengths: Free Estimate
  - Services: Residential, Commercial, Emergency

## Customer Voice (raw)
**Pain Points:**
- I called them about 10 times and sent several emails asking when would work to reschedule, but they didn't get back to me
- Why waste people's time as well as his to schedule an appointment, then no show

**Desires:**
- expertise
- speed
- fair pricing
- recommendation

**Praise Quotes:**
- David was super helpful. Easy to communicate with and had the job done in no time.
- Excellent service, provided a detailed explanation of what the problem was.

## Differentiators (raw)
- **Safety Angle**: Licensed electricians who put your family's safety first
- **Trust Angle**: Expert electrician your neighbors trust

## Seasonal Timing (raw)
- **electrician**: Peak Jan, Feb, Mar | CPC $16.41 | 368,000/mo
- **electrician near me**: Peak Feb, Mar | CPC $19.41 | 450,000/mo

## Ad Hooks (raw)
1. "Expert electrician your neighbors trust"
2. "Fair, transparent pricing - no surprises"
3. "On time, every time - we respect your schedule"

## Headlines (raw)
- Licensed electricians who put your family's safety first.
- Safe. Reliable. Professional.
- Need electrical inspection? We're the experts.

## Trust Signals (raw)
- Satisfaction Guaranteed
- Same-Day Service Available
- Background-Checked Technicians

---
*Agents used: local_intel, review_intel, yelp_intel, trends_intel*
*Analysis time: 200.1s*
```

---

## Purpose

- **Entry point:** Chat protocol for natural-language requests (e.g., "electrician in Providence, RI")
- **Orchestration:** Runs Local Intel → Review Intel → Yelp Intel → Trends Intel sequentially
- **Output:** Raw, unfiltered data (no synthesis, no filtering) for downstream agents (filter agent, ad generator)

---

## How It Works

### 1. uAgent Setup

**Code:** `orchestrator/agent.py`

- **Framework:** uAgents (Fetch.ai)
- **Protocol:** `chat_protocol_spec` for Agentverse compatibility
- **Mailbox:** Enabled for discovery on Agentverse (can disable for local-only)

```python
marky_agent = Agent(
    name="Marky",
    seed="marky-ad-research-agent",
    port=int(os.getenv("MARKY_PORT", "8000")),
    mailbox=True,
)
chat_proto = Protocol(spec=chat_protocol_spec)
```

**Reference:** `agent.py:marky_agent`, `chat_proto` (lines 47–54)

---

### 2. Request Parsing

**Code:** `orchestrator/agent.py` → `parse_research_request()`

- **Formats supported:**
  - `plumber in Boston, MA`
  - `research electrician Providence RI`
  - `analyze restaurant near San Francisco`
  - `business_type, location`
- **Output:** `AdResearchRequest(business_type, location)` or `None`

**Reference:** `agent.py:parse_research_request()` (lines 88–127)

---

### 3. Workflow Orchestration

**Code:** `orchestrator/workflow.py` → `MarkyWorkflow`

**Pipeline (5 stages):**

| Stage | Agent | Output |
|-------|-------|--------|
| 1 | Local Intel | Competitors (place_id, website, services, trust_signals), differentiators, headlines |
| 2 | Review Intel | Voice of customer (pain_points, desires, quotes), ad_hooks, headlines |
| 3 | Yelp Intel | Merged customer voice, ad_hooks, headlines (raw merge, no dedup) |
| 4 | Trends Intel | Seasonal timing, CPC, volume, related/rising queries |
| 5 | Output | Raw data combined (no synthesis) |

**Reference:** `workflow.py:MarkyWorkflow.run()` (lines 55–350)

---

### 4. Data Flow

**Stage 2 depends on Stage 1:** Review Intel needs `place_id` from Local Intel competitors.

**Stage 3 merges with Stage 2:** Yelp customer voice is concatenated with Review Intel (pain_points, desires, quotes, themes) — no deduplication.

**Stage 4 is independent:** Trends Intel uses keywords derived from `business_type` (e.g., "electrician", "electrician near me", "best electrician").

**Reference:** `workflow.py` lines 85–310

---

### 5. Report Output

**Code:** `orchestrator/models.py` → `AdResearchResponse.to_markdown()`

- **Format:** Markdown with sections: Competitors (raw), Customer Voice (raw), Differentiators (raw), Seasonal Timing (raw), Ad Hooks (raw), Headlines (raw), Trust Signals (raw), Market Summary (raw)
- **No synthesis:** No executive summary, key insights, or emotional angles
- **Full data:** No truncation or limits on displayed items

**Reference:** `models.py:AdResearchResponse.to_markdown()` (lines 164–258)

---

## Main Entry Points

### uAgent Mode (Agentverse)

```bash
python run_marky.py
```

- Starts Marky on port 8000
- Listens for chat messages
- On message: parse → run workflow → send markdown response

### CLI Mode (Local)

```bash
python run_marky.py --cli -b "electrician" -l "Providence, RI"
```

- Bypasses uAgent; runs workflow directly
- Supports `--no-trends`, `--json`

### Test Client

```bash
python test_marky_client.py -q "electrician in Providence, RI"
```

- Connects to running Marky uAgent
- Sends query and prints response

---

## Code Reference Summary

| Component | File | Key Functions |
|-----------|------|---------------|
| uAgent setup | `orchestrator/agent.py` | `marky_agent`, `chat_proto`, `handle_chat_message()` |
| Request parsing | `orchestrator/agent.py` | `parse_research_request()`, `get_help_message()` |
| Workflow | `orchestrator/workflow.py` | `MarkyWorkflow.run()`, `__init__()` (creates 4 agents) |
| Models | `orchestrator/models.py` | `AdResearchRequest`, `AdResearchResult`, `AdResearchResponse.to_markdown()` |

---

## Agents Used

| Agent | Purpose | Output Used |
|-------|---------|-------------|
| Local Intel | Competitors, websites, differentiators | place_ids for Review Intel; competitors, headlines, trust_signals |
| Review Intel | Google Reviews voice | customer_voice, ad_hooks, headlines |
| Yelp Intel | Yelp voice | Merged into customer_voice; ad_hooks, headlines |
| Trends Intel | Keywords, CPC, seasonality | timing (peak months, CPC, volume) |
