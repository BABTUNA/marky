# Local Business Ad Research Agent

An intelligent agent that discovers local competitors, scrapes their websites, and generates advertising differentiation insights for small businesses like plumbers, restaurants, contractors, and more.

## What It Does

Given a **business type** and **location**, this agent:

1. **Discovers local competitors** via Google Maps (SerpAPI)
2. **Scrapes competitor websites** for services, pricing, and messaging
3. **Extracts competitive intelligence**: services offered, trust signals, unique selling points
4. **Analyzes the market**: finds gaps and opportunities
5. **Generates ad differentiation**:
   - Competitive insights
   - Ad hooks and headlines
   - Trust signals to emphasize
   - Tagline suggestions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys (Optional but Recommended)

```powershell
# Windows PowerShell
$env:SERPAPI_KEY = "your_serpapi_key"           # For competitor discovery
$env:FIRECRAWL_API_KEY = "your_firecrawl_key"   # For premium scraping (optional)
```

```bash
# Linux/Mac
export SERPAPI_KEY="your_serpapi_key"
export FIRECRAWL_API_KEY="your_firecrawl_key"
```

**Get API Keys:**
- **SerpAPI**: https://serpapi.com (100 free searches/month)
- **Firecrawl**: https://firecrawl.dev (500 free pages)

**Note:** Jina Reader is used as a free fallback for website scraping - no API key needed!

### 3. Run Analysis

```bash
# Analyze plumbers in Providence, RI
python run_local_intel.py --business "plumber" --location "Providence, RI"

# Analyze restaurants in a specific zip code
python run_local_intel.py --business "restaurant" --location "02903" --radius 5

# Interactive mode
python run_local_intel.py --interactive

# Check your API configuration
python run_local_intel.py --check-config
```

## Example Output

```
==============================================================
COMPETITIVE INTELLIGENCE SUMMARY
==============================================================

### Competitors Analyzed: 12
  - ABC Plumbing ★ 4.8
    Services: Drain Cleaning, Water Heater, Emergency Plumbing
  - XYZ Plumbers ★ 4.5
    Services: Pipe Repair, Leak Detection, Bathroom Remodel

### Market Insights
  Common services: Drain Cleaning, Water Heater, Pipe Repair
  Trust signals used: Licensed And Insured, Free Estimates

  Service gaps (opportunities):
    - Hydro Jetting
    - Tankless Water Heater
    - Trenchless Repair

### Top Ad Differentiators
  [Emergency Angle]
    Hook: "Burst pipe at 2 AM? We're there in 60 minutes or less."
    Best for: Google Ads (search intent)

  [Trust Angle]
    Hook: "The plumber your neighbors trust. 100+ 5-star reviews."
    Best for: Facebook/Instagram (social proof)

### Headline Suggestions
  • Fast. Reliable. Affordable.
  • Plumbing Problems? Solved.
  • Same-day service. Because leaks don't wait.

### Trust Signals to Emphasize
  ✓ Background Checked
  ✓ Same Day Service
  ✓ Upfront Pricing
  ✓ Satisfaction Guarantee
```

## Supported Business Types

The agent has industry-specific intelligence for:
- **Plumbers** - drain cleaning, water heaters, emergency service
- **Electricians** - panel upgrades, EV chargers, safety
- **HVAC** - AC repair, heating, maintenance plans
- **Restaurants** - dine-in, catering, online ordering
- **Contractors** - remodeling, new construction, permits

Other business types use generic service detection.

## API Options Summary

### Competitor Discovery

| Provider | Free Tier | Setup |
|----------|-----------|-------|
| **SerpAPI** | 100 searches/mo | `SERPAPI_KEY` |
| **Outscraper** | 500 results | `OUTSCRAPER_API_KEY` |
| Manual input | Unlimited | No key needed |

### Website Scraping

| Provider | Free Tier | Setup |
|----------|-----------|-------|
| **Jina Reader** | Unlimited | No key needed (default) |
| **Firecrawl** | 500 pages | `FIRECRAWL_API_KEY` |

## Project Structure

```
hackbrown_testing/
├── run_local_intel.py      # CLI entry point
├── requirements.txt
├── README.md
├── local_intel/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── models.py           # Data models
│   ├── competitor_discovery.py  # Find competitors
│   ├── website_scraper.py  # Scrape websites
│   ├── content_extractor.py    # Extract services/signals
│   ├── ad_generator.py     # Generate ad differentiation
│   └── agent.py            # Main orchestrator
└── output/                 # Generated reports (JSON)
```

## Python API

```python
from local_intel.agent import LocalIntelAgent

# Initialize
agent = LocalIntelAgent()

# Run analysis
report = agent.analyze(
    business_type="plumber",
    location="Providence, RI",
    radius_miles=10,
    max_competitors=15,
)

# Access results
for insight in report.insights:
    print(f"{insight.title}: {insight.description}")

for diff in report.differentiators:
    print(f"Hook: {diff.hook}")

# Save report
agent.save_report(report, output_dir="my_output")
```

### Manual Competitor Input

If you don't have API keys, you can manually specify competitors:

```python
from local_intel.agent import LocalIntelAgent

agent = LocalIntelAgent()

report = agent.analyze(
    business_type="plumber",
    location="Providence, RI",
    manual_competitors=[
        {"name": "ABC Plumbing", "website": "https://abcplumbing.com"},
        {"name": "XYZ Plumbers", "website": "https://xyzplumbers.com"},
        {"name": "Quick Fix Plumbing", "website": "https://quickfixplumbing.com"},
    ]
)
```

## How It Works

### 1. Competitor Discovery
Uses SerpAPI to search Google Maps for businesses matching your type and location. Extracts name, address, website, rating, and review count.

### 2. Website Scraping
Scrapes competitor homepages plus key pages (/services, /about, /pricing) using Jina Reader (free) or Firecrawl. Converts to clean markdown.

### 3. Content Extraction
Uses pattern matching to extract:
- **Services**: Industry-specific service detection
- **Trust signals**: "Licensed & Insured", "24/7", "Free Estimates"
- **Pricing**: Dollar amounts, "free estimate", "financing available"
- **Taglines**: Short, punchy messaging

### 4. Market Analysis
Aggregates data across competitors to find:
- Common services (table stakes)
- Rare services (differentiation opportunities)
- Trust signal gaps
- Pricing transparency opportunities

### 5. Ad Generation
Creates advertising angles based on:
- Industry-specific hooks
- Competitor gaps
- Trust signal opportunities
- Proven messaging patterns

## Troubleshooting

### "No competitors found"
- Check your API key: `python run_local_intel.py --check-config`
- Try a different location format (city vs zip vs coordinates)
- Use manual competitor input as fallback

### Website scraping fails
- Some sites block scrapers - this is expected
- The agent continues with sites that work
- Jina Reader handles most sites well

### Missing services in extraction
- The agent uses industry-specific keywords
- For uncommon business types, extraction may be limited
- Results still provide competitive overview

## License

MIT - Use freely for hackathons and beyond!
