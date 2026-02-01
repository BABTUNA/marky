# Local Intel Agent

Discovers local competitors via Google Maps, scrapes their websites, extracts competitive intelligence, and generates ad differentiation.

---

## Example Input

```python
agent = LocalIntelAgent()
report = agent.analyze(
    business_type="plumber",
    location="Providence, RI",
    radius_miles=10.0,
    top_count=5,
    worst_count=2,
)
```

**CLI:**
```bash
python run_local_intel.py -b "plumber" -l "Providence, RI" --max-competitors 5
```

---

## Example Output (abbreviated)

```json
{
  "search": {
    "business_type": "plumber",
    "location": "Providence, RI",
    "radius_miles": 10.0
  },
  "competitors": [
    {
      "name": "United Sewer And Drain",
      "website": "http://www.unitedsds.com/",
      "rating": 5,
      "review_count": 77,
      "services": ["Maintenance", "Service", "Sump Pump", "Repair", "Installation", "Hydro Jetting"],
      "trust_signals": ["Warranty", "Fully Insured", "Emergency Service", "Certified", "24/7"]
    },
    {
      "name": "Roto-Rooter Plumbing & Water Cleanup",
      "rating": 4.8,
      "review_count": 3052,
      "services": ["Drain Cleaning", "Emergency Plumbing", "Water Heater", "Sewer Line", "Leak Detection"],
      "trust_signals": ["Fully Licensed", "24/7", "Emergency Service"]
    }
  ],
  "market_analysis": {
    "common_services": ["Service", "Repair", "Drain Cleaning", "Emergency", "Inspection"],
    "service_gaps": ["Trenchless sewer repair"],
    "common_trust_signals": ["24/7", "Emergency Service", "Licensed"]
  },
  "differentiators": [
    {
      "angle_name": "Emergency Angle",
      "hook": "24/7 emergency service when you need us most",
      "supporting_points": ["Same-day service", "Licensed technicians"],
      "best_for": "Emergency/urgent scenarios"
    }
  ],
  "headline_suggestions": [
    "Licensed Plumbers You Can Trust",
    "24/7 Emergency Plumbing | Same-Day Service",
    "Drain Cleaning & Repair | Fair Pricing"
  ],
  "trust_signals_to_use": ["Licensed & Insured", "24/7 Emergency Service", "Satisfaction Guaranteed"]
}
```

---

## Purpose

Analyze the competitive landscape for a business type in a given location by:
1. Finding top-rated and worst-rated local competitors
2. Scraping competitor websites for content
3. Extracting services, trust signals, pricing, and USPs
4. Deriving market analysis (common services, gaps, opportunities)
5. Generating ad differentiators, headlines, and trust signals
6. Comparing success vs failure patterns (Claude or rule-based)

---

## How It Works

### 1. Competitor Discovery

**Code:** `local_intel/competitor_discovery.py`

- **API:** SerpAPI (Google Maps) or Outscraper
- **Two-pass strategy:** First pass finds top-rated; second pass uses expanded radius (3×) to find low-rated competitors
- **Output:** List of `Competitor` (name, rating, review_count, place_id, website)

```python
# Key logic: discover_with_worst()
# Pass 1: Search "business_type in location" → top N by rating
# Pass 2: Search same with larger radius → lowest N by rating
competitors, top_competitors, worst_competitors = self.discovery.discover_with_worst(
    search_input, discovery_config
)
```

**Reference:** `competitor_discovery.py:discover_with_worst()`, `_search_serpapi()`

---

### 2. Website Scraping

**Code:** `local_intel/website_scraper.py`

- **APIs:** Firecrawl (primary), Jina Reader (fallback)
- **Pages scraped:** Homepage, `/services`, `/about`, `/pricing`, `/contact`, etc. (up to `max_pages_per_site`)
- **Output:** `WebsiteData` with combined HTML/text content per competitor

```python
# Scrapes homepage first, then IMPORTANT_PAGES
IMPORTANT_PAGES = ["", "/services", "/about", "/about-us", "/pricing", "/contact", ...]
page = self._scrape_page(page_url)  # Firecrawl or Jina
```

**Reference:** `website_scraper.py:scrape_competitor()`, `_scrape_page()`

---

### 3. Content Extraction

**Code:** `local_intel/content_extractor.py`

- **Methods:** Regex patterns for services, trust signals, pricing, taglines, unique selling points
- **Trust signals:** `TRUST_PATTERNS` (e.g., `licensed insured`, `bbb a+`, `24/7`, `family owned`)
- **Output:** Enriches `WebsiteData` with `services`, `trust_signals`, `taglines`, `unique_points`

```python
# Extracts via regex from scraped content
def _extract_trust_signals(self, content: str) -> List[str]:
    for pattern, _ in self.TRUST_PATTERNS:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            signals.append(match.group(0).strip().title())
```

**Reference:** `content_extractor.py:_extract_trust_signals()`, `_extract_services()`, `_extract_unique_points()`

---

### 4. Market Analysis

**Code:** `local_intel/content_extractor.py` → `MarketAnalyzer`

- **Logic:** Aggregates services and trust signals across competitors; identifies gaps (services few offer) and messaging opportunities
- **Output:** `MarketAnalysis` (common_services, service_gaps, common_trust_signals, messaging_opportunities)

**Reference:** `content_extractor.py:MarketAnalyzer.analyze()`

---

### 5. Ad Differentiation Generation

**Code:** `local_intel/ad_generator.py`

- **Generates:** Competitive insights, ad differentiators (angle_name, hook, supporting_points), headlines, taglines, trust_signals_to_use
- **Logic:** Uses market analysis and website data to suggest angles (e.g., Safety, Trust, Price)

**Reference:** `ad_generator.py:AdDifferentiationGenerator.generate_differentiators()`, `generate_headlines()`

---

### 6. Success vs Failure Analysis

**Code:** `local_intel/agent.py` → `ClaudeAnalysisAgent`

- **If `ANTHROPIC_API_KEY` set:** Claude compares top vs worst competitors; returns success_factors, failure_patterns, recommendations, ad_angles_from_analysis
- **Fallback:** Rule-based analysis comparing services and trust signals unique to top vs worst

**Reference:** `agent.py:ClaudeAnalysisAgent.analyze_success_patterns()`, `_build_analysis_prompt()`

---

## Main Entry Point

**Code:** `local_intel/agent.py` → `LocalIntelAgent`

```python
agent = LocalIntelAgent()
report = agent.analyze(
    business_type="electrician",
    location="Providence, RI",
    radius_miles=10.0,
    top_count=5,
    worst_count=2,
    include_worst_rated=True,
)
```

**Reference:** `agent.py:LocalIntelAgent.analyze()` (lines 330–460)

---

## Output Model

**Code:** `local_intel/models.py`

| Field | Type | Description |
|-------|------|-------------|
| `competitors` | List[Competitor] | Name, rating, place_id, website, services, trust_signals |
| `market_analysis` | MarketAnalysis | common_services, service_gaps, messaging_opportunities |
| `differentiators` | List[AdDifferentiator] | angle_name, hook, supporting_points, best_for |
| `headline_suggestions` | List[str] | Generated headlines |
| `trust_signals_to_use` | List[str] | Trust signals to emphasize in ads |

---

## APIs Used

| API | Purpose | Env Var |
|-----|---------|---------|
| SerpAPI | Google Maps competitor search | `SERPAPI_KEY` |
| Firecrawl | Website scraping | `FIRECRAWL_API_KEY` |
| Jina Reader | Fallback scraping | — |
| Anthropic Claude | Success/failure analysis | `ANTHROPIC_API_KEY` |

---

## Standalone Run

```bash
python run_local_intel.py -b "electrician" -l "Providence, RI" --max-competitors 5
```
