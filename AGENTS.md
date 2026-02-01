# Agent Reference

Description of each intelligence agent in the Marky ad research system.

---

## 1. Local Intel (`local_intel`)

**Purpose:** Discover and analyze local competitors by scraping their websites.

**Used by Marky:** ✅ Yes

### Steps

1. **Competitor discovery** – SerpAPI (Google Maps) finds top-rated and low-rated local businesses in the target area.
2. **Website scraping** – Firecrawl (with Jina fallback) scrapes competitor sites.
3. **Content extraction** – Extracts services, pricing, trust signals, taglines, and unique selling points.
4. **Market analysis** – Derives common services, service gaps, and messaging angles.
5. **Ad differentiation** – Generates competitive insights, differentiators, and headline suggestions.
6. **AI analysis** – Uses Claude to compare high-rated vs low-rated competitors and surface success/failure patterns.

### APIs

| API | Purpose |
|-----|---------|
| SerpAPI | Google Maps competitor search |
| Firecrawl | Website scraping |
| Jina Reader | Fallback scraping |
| Anthropic (Claude) | Success/failure analysis |

### Outputs

- Competitors (name, rating, review count, website, services, trust signals)
- Market analysis (common services, gaps, opportunities)
- Differentiators (angle, hook, supporting points, best channel)
- Headline suggestions, taglines, trust signals to use

### Run standalone

```bash
python run_local_intel.py -b "electrician" -l "Providence, RI" --max-competitors 5
```

---

## 2. Yelp Intel (`yelp_intel`)

**Purpose:** Extract voice-of-customer from Yelp reviews (pain points, praise, themes).

**Used by Marky:** ✅ Yes

### Steps

1. **Business search** – SerpAPI (Yelp) finds local businesses.
2. **Review collection** – Collects positive and negative reviews per business.
3. **Insight extraction** – Keyword-based extraction of pain points, praise points, themes, and customer phrases.
4. **Ad suggestions** – Generates hooks, headlines, pain-point hooks, and trust signals from insights.

### APIs

| API | Purpose |
|-----|---------|
| SerpAPI | Yelp business search and review scraping |

### Outputs

- Customer insights (pain_points, praise_points, themes, customer_phrases, quotes)
- Ad suggestions (hooks, headlines, pain_point_hooks, trust_signals, differentiators)

### Note

Pain points and praise points are keyword matches (single words/phrases from predefined lists). For richer themes, consider using the full `pain_point_quotes` and `praise_quotes`.

### Run standalone

```bash
python run_yelp_intel.py -b "electrician" -l "Providence, RI" --max-businesses 5
```

---

## 3. Trends Intel (`trends_intel`)

**Purpose:** Provide keyword search volume, CPC, and seasonal timing for ad planning.

**Used by Marky:** ✅ Yes

### Steps

1. **Search volume** – DataForSEO fetches monthly volume, CPC, and competition for target keywords.
2. **Google Trends** – Fetches interest-over-time data (when available).
3. **Related queries** – Extracts related and rising queries.
4. **Seasonal analysis** – Identifies peak and low months from search volume.
5. **Timing recommendations** – Produces best/avoid months and budget advice.

### APIs

| API | Purpose |
|-----|---------|
| DataForSEO | Keyword volume, CPC, related queries, trends |

### Outputs

- Keyword data (search_volume, cpc, competition)
- Seasonal insights (peak_season, peak_months, low_season, recommendation)
- Related queries, rising queries
- Ad timing recommendations

### Run standalone

```bash
python run_trends_intel.py -k "electrician" "electrician near me" "best electrician"
```

---

## 4. Review Intel (`review_intel`)

**Purpose:** Analyze Google Reviews to extract customer voice (similar to Yelp Intel, different source).

**Used by Marky:** ✅ Yes (Stage 2, after Local Intel)

### Steps

1. **Review scraping** – SerpAPI (Google Maps Reviews) fetches reviews for given competitors.
2. **Insight extraction** – Keyword-based extraction of pain points, praise points, and themes.
3. **Ad suggestions** – Generates hooks and headlines from customer language.

### APIs

| API | Purpose |
|-----|---------|
| SerpAPI | Google Maps Reviews |

### Outputs

- VoiceOfCustomer (pain_points, desires, praise_quotes, complaint_quotes)
- Ad suggestions (hooks, headlines)

### Run standalone

```bash
python run_review_intel.py -b "electrician" -l "Providence, RI"
```

### Note

Uses competitor place IDs from Local Intel. Could be integrated into Marky to add Google Reviews alongside Yelp.

---

## Summary

| Agent | Used by Marky | Primary API | Main Output |
|-------|---------------|-------------|-------------|
| local_intel | ✅ | SerpAPI + Firecrawl | Competitors, differentiators, trust signals |
| review_intel | ✅ | SerpAPI | Google Reviews voice-of-customer |
| yelp_intel | ✅ | SerpAPI | Yelp pain points, praise, ad hooks |
| trends_intel | ✅ | DataForSEO | CPC, seasonal timing, keywords |
