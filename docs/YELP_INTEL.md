# Yelp Intel Agent

Scrapes **Yelp** reviews and extracts customer pain points, praise, themes, and ad suggestions. Works independently of Local Intel (searches Yelp directly).

---

## Example Input

```python
agent = YelpIntelAgent()
analysis = agent.analyze_market(
    business_type="electrician",
    location="Providence, RI",
    max_businesses=5,
    reviews_per_business=20,
)
```

**CLI:**
```bash
python run_yelp_intel.py -b "electrician" -l "Providence, RI" -m 5
```

---

## Example Output (abbreviated)

```json
{
  "business_type": "electrician",
  "location": "Providence, RI",
  "total_reviews_analyzed": 25,
  "avg_rating": 4.36,
  "businesses": [
    {"name": "ZH Electric", "rating": 4.2, "review_count": 21},
    {"name": "Naxos Electric", "rating": 5.0, "review_count": 45}
  ],
  "insights": {
    "pain_points": [
      "I called them about 10 times and sent several emails asking when would work to reschedule, but they didn't get back to me",
      "Why waste people's time as well as his to schedule an appointment, then no show",
      "The electrician came out and assessed my situation and never sent a quote or returned a call"
    ],
    "praise_points": [
      "Strongly recommended for efficiency and effective service, and all at the best prices in the market.",
      "Zach was easy to contact, the pricing was fair, the work was performed on time",
      "He was punctual, professional, and friendly"
    ],
    "themes": ["pricing", "quality", "timeliness", "communication", "professionalism"],
    "pain_point_quotes": [
      "ZH Electric gave me a quote, I accepted... The day of the service, they sent me an email saying they had to reschedule."
    ],
    "praise_quotes": [
      "Zach is wonderful. Always shows up when expected and on time, does great work."
    ]
  },
  "ad_suggestions": {
    "hooks": [
      "Fair, transparent pricing - no surprises",
      "On time, every time - we respect your schedule",
      "Quality work that lasts"
    ],
    "headlines": [
      "Top-Rated Electrician in Your Area",
      "Professional Electrician Services",
      "Fast, Reliable Electrician Service"
    ],
    "trust_signals": ["Licensed & Professional Service", "Fast, Efficient Service", "Honest, Upfront Pricing"]
  }
}
```

---

## Purpose

Extract voice-of-customer from Yelp (different source from Google Reviews):

1. Search Yelp for businesses matching business type + location
2. Fetch positive and negative reviews per business
3. Extract pain points (full phrases), praise points (full phrases), themes
4. Generate ad hooks, headlines, trust signals, differentiators

---

## How It Works

### 1. Business Search

**Code:** `yelp_intel/scraper.py` → `YelpScraper.search_businesses()`

- **API:** SerpAPI (`engine=yelp`)
- **Params:** `find_desc`, `find_loc`, `sortby` (recommended, rating, review_count)
- **Output:** List of `YelpBusiness` (name, rating, review_count, place_id, url)

```python
params = {
    "engine": "yelp",
    "find_desc": query,   # e.g., "electrician"
    "find_loc": location, # e.g., "Providence, RI"
    "sortby": "recommended",
}
data = self._request_with_retry(params)
```

**Reference:** `scraper.py:search_businesses()` (lines 49–100)

---

### 2. Review Collection

**Code:** `yelp_intel/scraper.py` → `get_positive_reviews()`, `get_negative_reviews()`

- **API:** SerpAPI (`engine=yelp_reviews`)
- **Logic:** Fetches positive (4–5 star) and negative (1–2 star) reviews per business; combines for balanced sample
- **Retry:** Uses `tenacity` for timeout/connection errors (60s timeout, 3 retries, exponential backoff)

**Reference:** `scraper.py:get_positive_reviews()`, `get_negative_reviews()`, `_request_with_retry()`

---

### 3. Review Analysis

**Code:** `yelp_intel/agent.py` → `_analyze_reviews()`

- **Pain keywords:** `PAIN_KEYWORDS` (e.g., terrible, overpriced, rude, no-show, slow)
- **Praise keywords:** `PRAISE_KEYWORDS` (e.g., amazing, friendly, fast, recommend, honest)
- **Phrase extraction:** `_extract_sentence_containing()` returns the full sentence containing a keyword (15–200 chars), not just the keyword
- **Themes:** `THEME_PATTERNS` (pricing, quality, timeliness, communication, professionalism, cleanliness, expertise, reliability)
- **Output:** `CustomerInsights` (pain_points, praise_points, themes, customer_phrases, praise_quotes, pain_point_quotes)

```python
# Full phrase extraction - not just keyword
phrase = self._extract_sentence_containing(review.text, keyword)
if phrase and phrase not in pain_phrases:
    pain_phrases.append(phrase)
```

**Reference:** `agent.py:_analyze_reviews()` (lines 220–292), `_extract_sentence_containing()` (lines 194–217)

---

### 4. Ad Suggestions Generation

**Code:** `yelp_intel/agent.py` → `_generate_suggestions()`

- **Pain-point hooks:** Maps pain keywords to templates (e.g., `late` → `Tired of {business_type}s who never show up on time?`)
- **Trust signals:** Maps praise keywords to trust phrases (e.g., `professional` → `Licensed & Professional Service`)
- **Theme-based hooks:** If "pricing" in themes → "Fair, transparent pricing - no surprises"; "timeliness" → "On time, every time"
- **Headlines:** Generic + business-type templates
- **Differentiators:** Suggestions based on what's missing (e.g., if "reliable" not in praise → "Emphasize reliability")

**Reference:** `agent.py:_generate_suggestions()` (lines 332–401)

---

## Main Entry Point

**Code:** `yelp_intel/agent.py` → `YelpIntelAgent`

```python
agent = YelpIntelAgent()
analysis = agent.analyze_market(
    business_type="electrician",
    location="Providence, RI",
    max_businesses=5,
    reviews_per_business=20,
)
```

**Reference:** `agent.py:YelpIntelAgent.analyze_market()` (lines 74–192)

---

## Output Model

**Code:** `yelp_intel/models.py`

| Field | Type | Description |
|-------|------|-------------|
| `insights` | CustomerInsights | pain_points, praise_points, themes, praise_quotes, pain_point_quotes, customer_phrases |
| `ad_suggestions` | AdSuggestions | hooks, headlines, pain_point_hooks, trust_signals, differentiators |
| `total_reviews_analyzed` | int | Total reviews collected |
| `rating_distribution` | Dict[int,int] | Count per star (1–5) |

---

## APIs Used

| API | Purpose | Env Var |
|-----|---------|---------|
| SerpAPI | Yelp search + Yelp reviews | `SERPAPI_KEY` |

---

## Standalone Run

```bash
python run_yelp_intel.py -b "electrician" -l "Providence, RI" -m 5
# -m is alias for --max-businesses
```
