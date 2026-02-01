# Review Intel Agent

Scrapes and analyzes **Google Reviews** to extract customer voice, pain points, desires, and ad hooks.

---

## Example Input

```python
agent = ReviewIntelAgent()
analysis = agent.analyze_competitors(
    competitors=[
        {"name": "United Sewer And Drain", "place_id": "ChIJ...", "rating": 5.0},
        {"name": "Mr. Sewer & Pipe LLC", "place_id": "ChIJ...", "rating": 5.0}
    ],
    business_type="plumber",
    location="Providence, RI",
    reviews_per_competitor=10,
)
```

**CLI (uses place_ids from latest Local Intel output):**
```bash
python run_review_intel.py --from-local-intel latest
```

---

## Example Output (abbreviated)

```json
{
  "business_type": "plumber",
  "location": "Providence, RI",
  "competitors_analyzed": 6,
  "total_reviews_analyzed": 12,
  "voice_of_customer": {
    "pain_points": [
      {"point": "poor communication", "frequency": 3, "percentage": 25.0},
      {"point": "unreliable timing", "frequency": 2, "percentage": 16.7}
    ],
    "desires": [
      {"desire": "fair pricing", "frequency": 5, "percentage": 35.7},
      {"desire": "expertise", "frequency": 4, "percentage": 28.6},
      {"desire": "speed", "frequency": 3, "percentage": 21.4}
    ],
    "praise_quotes": [
      "David was super helpful. Easy to communicate with and had the job done in no time.",
      "Excellent service, provided a detailed explanation of what the problem was."
    ],
    "complaint_quotes": []
  },
  "top_competitor_themes": ["fair pricing", "communication", "expertise", "speed"],
  "worst_competitor_themes": [],
  "ad_hooks": [
    "Fair pricing. No surprises.",
    "Expert plumber your neighbors trust",
    "We show up on time, every time"
  ],
  "headline_suggestions": [
    "Honest pricing with no surprises",
    "Trusted experts in your area",
    "Expertise Guaranteed"
  ]
}
```

---

## Purpose

Extract voice-of-customer from Google Reviews of **competitors** (identified by Local Intel via `place_id`):

1. Fetch reviews for each competitor using Google Maps place_id
2. Extract pain points, desires, praise quotes, complaint quotes
3. Generate ad hooks and headlines from customer language
4. Compare top vs worst rated competitors

---

## How It Works

### 1. Review Scraping

**Code:** `review_intel/scraper.py` → `GoogleReviewsScraper`

- **API:** SerpAPI (`engine=google_maps_reviews`)
- **Input:** Competitor list with `place_id` (from Local Intel)
- **Output:** `CompetitorReviews` per competitor with `ReviewData` (rating, text, sentiment, pain_points, praise_points, keywords)

```python
params = {
    "engine": "google_maps_reviews",
    "place_id": place_id,
    "sort_by": "qualityScore",  # or newestFirst, ratingHigh, ratingLow
}
response = requests.get(self.base_url, params=params)
```

**Reference:** `scraper.py:get_reviews()` (lines 22–90)

---

### 2. Keyword Extraction (Per Review)

**Code:** `review_intel/scraper.py` → `_extract_keywords()`, `_extract_complaints()`, `_extract_praise()`

- **Logic:** Maps review text to predefined pain/praise keywords (e.g., `unreliable timing`, `overpricing`, `punctuality`, `fair pricing`)
- **Sentiment:** Positive (4–5 stars), negative (1–2 stars), neutral (3 stars)

**Reference:** `scraper.py:_extract_complaints()`, `_extract_praise()`

---

### 3. Voice of Customer Aggregation

**Code:** `review_intel/agent.py` → `_extract_voice_of_customer()`

- **Pain points:** `Counter` over all negative-review pain points → top 10 with frequency/percentage
- **Desires:** `Counter` over praise points from positive reviews → top 10
- **Quotes:** First sentence or 150 chars from 5-star (praise) and ≤2-star (complaint) reviews
- **Emotional triggers:** Maps pain/desire keywords to emotions (e.g., `unreliable timing` → `frustration with waiting`)
- **Trust phrases:** Maps desires to phrases (e.g., `punctuality` → `We show up on time, every time`)
- **Hook templates:** Pain-point and desire-based hook templates

**Reference:** `agent.py:_extract_voice_of_customer()` (lines 143–213)

---

### 4. Ad Hooks and Headlines Generation

**Code:** `review_intel/agent.py` → `_generate_hooks()`, `_generate_headlines()`

- **Hooks:** From hook_templates, short praise quotes, and top pain point (e.g., `Stop dealing with {top_pain}`)
- **Headlines:** From trust_phrases, power words, and desires (e.g., `{desire} Guaranteed`)

**Reference:** `agent.py:_generate_hooks()` (lines 343–357), `_generate_headlines()` (lines 359–376)

---

### 5. Top vs Worst Comparison

**Code:** `review_intel/agent.py` → `analyze_competitors()` (Step 4)

- **Logic:** Splits competitors by rating; gets common themes from positive reviews (top half) vs negative reviews (bottom half)
- **Output:** `top_competitor_themes`, `worst_competitor_themes`

**Reference:** `agent.py:analyze_competitors()` (lines 108–124)

---

## Main Entry Point

**Code:** `review_intel/agent.py` → `ReviewIntelAgent`

```python
agent = ReviewIntelAgent()
analysis = agent.analyze_competitors(
    competitors=[{"name": "ABC Plumbing", "place_id": "ChIJ...", "rating": 4.8}],
    business_type="plumber",
    location="Providence, RI",
    reviews_per_competitor=10,
)
```

**Reference:** `agent.py:ReviewIntelAgent.analyze_competitors()` (lines 31–141)

---

## Output Model

**Code:** `review_intel/models.py`

| Field | Type | Description |
|-------|------|-------------|
| `voice_of_customer` | VoiceOfCustomer | pain_points, desires, praise_quotes, complaint_quotes, power_words, hook_templates |
| `ad_hooks` | List[str] | Generated ad hooks |
| `headline_suggestions` | List[str] | Generated headlines |
| `top_competitor_themes` | List[str] | Themes from top-rated competitors |
| `worst_competitor_themes` | List[str] | Issues from worst-rated competitors |
| `total_reviews_analyzed` | int | Total reviews scraped |

---

## Dependencies

**Requires `place_id` from Local Intel.** Competitors must have `place_id` (Google Maps identifier). Local Intel includes this in its competitor output.

---

## APIs Used

| API | Purpose | Env Var |
|-----|---------|---------|
| SerpAPI | Google Maps Reviews | `SERPAPI_KEY` |

---

## Standalone Run

```bash
# Requires local_intel output with place_ids
python run_review_intel.py --from-local-intel latest
# or
python run_review_intel.py --from-local-intel output/local_intel_20260131_120000.json
```
