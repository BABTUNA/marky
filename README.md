# 🎯 Marky - Ad Research Orchestrator Agent

A single-entry-point uAgent that orchestrates multiple intelligence agents to generate comprehensive ad research and differentiation strategies for local businesses.

**Built for the Fetch.ai Track** using the uAgents framework with chat protocol for Agentverse/ASI:One compatibility.

## What It Does

Given a **business type** and **location**, Marky:

1. **Discovers local competitors** via Google Maps (SerpAPI)
2. **Scrapes competitor websites** for services, pricing, and messaging
3. **Extracts customer voice** from Google Reviews (competitor reviews)
4. **Extracts customer voice** from Yelp reviews (pain points, desires)
5. **Analyzes search trends** for seasonal timing (DataForSEO)
6. **Generates ad differentiation**:
   - Competitive insights
   - Ad hooks and headlines
   - Optimal timing recommendations
   - Trust signals to emphasize

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MARKY (uAgent Entry Point)                   │
│                  Chat Protocol / Agentverse Compatible          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SEQUENTIAL WORKFLOW                          │
│                                                                 │
│  Local Intel → Review Intel → Yelp Intel → Trends Intel         │
│  (SerpAPI +    (Google       (Yelp        (DataForSEO)          │
│   Firecrawl)    Reviews)      Reviews)                          │
│                              │                                  │
│                              ▼                                  │
│                    ┌──────────────┐                            │
│                    │  Synthesis   │                            │
│                    │  (Combine &  │                            │
│                    │   Report)    │                            │
│                    └──────────────┘                            │
│                              │                                  │
│                              ▼                                  │
│                    ┌──────────────┐                            │
│                    │  Synthesis   │                            │
│                    │  (Combine &  │                            │
│                    │   Report)    │                            │
│                    └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Copy `env.example` to `.env` and fill in your keys:

```bash
cp env.example .env
```

**Required:**
- `SERPAPI_KEY` - For competitor discovery & Yelp reviews ([serpapi.com](https://serpapi.com))

**Optional:**
- `FIRECRAWL_API_KEY` - Premium website scraping ([firecrawl.dev](https://firecrawl.dev))
- `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` - Keyword trends ([dataforseo.com](https://dataforseo.com))

### 3. Run Marky

**As a uAgent (for Fetch.ai Agentverse):**

```bash
python run_marky.py
```

**CLI mode (direct analysis):**

```bash
python run_marky.py --cli -b "plumber" -l "Boston, MA"
```

**Check configuration:**

```bash
python run_marky.py --check-config
```

## Usage Examples

### Chat Protocol (Agentverse/ASI:One)

Once running, send messages like:

```
plumber in Boston, MA
```
```
research electrician Providence RI
```
```
restaurant near San Francisco
```

### CLI Mode

```bash
# Full analysis
python run_marky.py --cli -b "plumber" -l "Providence, RI"

# Faster (skip trends)
python run_marky.py --cli -b "plumber" -l "Providence, RI" --no-trends

# Output as JSON
python run_marky.py --cli -b "plumber" -l "Providence, RI" --json
```

### Individual Agents

Each sub-agent can also be run standalone:

```bash
# Local competitor analysis
python run_local_intel.py -b "plumber" -l "Providence, RI" --max-competitors 5

# Yelp reviews
python run_yelp_intel.py -b "plumber" -l "Providence, RI" --max-businesses 5

# Keyword trends
python run_trends_intel.py -k "plumber" "emergency plumber" "plumbing services"
```

## Example Output

```
# 📊 Ad Research Report: plumber in Boston, MA

## Executive Summary
Analysis of plumber market in Boston, MA. Identified 5 competitors. 
Key customer pain points include: late arrivals, hidden fees, poor communication.
Best time to run ads: January, February, March.

## 💡 Key Insights
- Market has 5 competitors with avg rating 4.3⭐
- Top competitor: ABC Plumbing (4.8⭐, 234 reviews)
- Top customer pain point: Late arrivals and no-shows
- Best months to advertise: Jan, Feb, Mar

## 🎯 Recommended Ad Hooks
1. "Burst pipe at 2 AM? We're there in 60 minutes."
2. "No hidden fees. Upfront pricing before we start."
3. "The plumber your neighbors trust. 100+ 5-star reviews."

## ✍️ Headline Suggestions
- Fast. Reliable. Affordable.
- Plumbing Problems? Solved.
- Same-day service. Because leaks don't wait.
```

## Project Structure

```
marky/
├── run_marky.py              # Main entry point
├── orchestrator/
│   ├── __init__.py
│   ├── agent.py              # uAgent with chat protocol
│   ├── workflow.py           # Sequential orchestration
│   └── models.py             # Data models
├── local_intel/              # Competitor website analysis
├── review_intel/             # Google Reviews (not currently used)
├── yelp_intel/               # Yelp review analysis
├── trends_intel/             # DataForSEO keyword trends
├── requirements.txt
├── env.example
└── output/                   # Generated reports
```

## API Services Used

| Agent | API | Free Tier | Purpose |
|-------|-----|-----------|---------|
| local_intel | SerpAPI | 100/mo | Google Maps competitors |
| local_intel | Firecrawl | 500 pages | Website scraping |
| yelp_intel | SerpAPI | 100/mo | Yelp search & reviews |
| trends_intel | DataForSEO | $1 trial | Keyword volume & trends |

## Fetch.ai Integration

Marky uses the uAgents framework:

- **Chat Protocol** - Compatible with `chat_protocol_spec` for Agentverse
- **Mailbox Enabled** - Discoverable on the Fetch.ai network
- **Single Entry Point** - One agent, internal sub-agent orchestration
- **ASI:One Compatible** - Can be chatted with via ASI:One interface

## License

MIT - Built for HackBrown 2026
