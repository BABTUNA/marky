# Trends Intel Agent

Uses **DataForSEO** to analyze keyword search volume, CPC, seasonal patterns, and related/rising queries for ad timing recommendations.

---

## Example Input

```python
agent = TrendsIntelAgent()
analysis = agent.analyze(
    keywords=["plumber", "emergency plumber", "plumbing services"],
    location="United States",
    include_related=True,
)
```

**CLI:**
```bash
python run_trends_intel.py -k "plumber" "emergency plumber" "plumbing services"
```

---

## Example Output (abbreviated)

```json
{
  "keywords": ["plumber", "emergency plumber", "plumbing services"],
  "location": "United States",
  "keyword_data": [
    {
      "keyword": "plumber",
      "search_volume": 673000,
      "competition": "LOW",
      "competition_index": 33,
      "cpc": 29.9,
      "monthly_searches": [
        {"year": 2025, "month": 3, "search_volume": 1000000},
        {"year": 2025, "month": 2, "search_volume": 1000000},
        {"year": 2025, "month": 1, "search_volume": 823000}
      ]
    },
    {
      "keyword": "emergency plumber",
      "search_volume": 74000,
      "cpc": 65.57,
      "competition": "LOW"
    }
  ],
  "seasonal_insights": [
    {
      "keyword": "plumber",
      "peak_season": "Winter (Jan, Feb, Mar)",
      "peak_months": [1, 2, 3],
      "low_season": "Summer (Jun, Jul, Aug)",
      "seasonality_score": 45.2,
      "recommendation": "Increase ad spend in Winter. Consider reducing budget in Summer."
    }
  ],
  "timing_recommendations": [
    {
      "keyword": "plumber",
      "best_months": ["Jan", "Feb", "Mar"],
      "avoid_months": ["Jun", "Jul", "Aug"],
      "current_trend": "stable",
      "budget_advice": "Reasonable CPC. Good opportunity for testing."
    }
  ],
  "rising_queries": ["24 7 plumber", "emergency plumber near me", "plumber seo"]
}
```

---

## Purpose

Provide keyword and seasonal data for ad planning:

1. Fetch search volume and CPC for target keywords
2. Fetch Google Trends interest data (when available)
3. Get related and rising queries
4. Analyze seasonal patterns (peak/low months)
5. Generate ad timing recommendations

---

## How It Works

### 1. Search Volume Data

**Code:** `trends_intel/scraper.py` → `DataForSEOClient.get_search_volume()`

- **API:** DataForSEO `keywords_data/google_ads/search_volume/live`
- **Auth:** Basic Auth (login:password from API dashboard)
- **Output:** `KeywordData` per keyword (search_volume, cpc, competition, competition_index, monthly_searches)

```python
payload = [{
    "keywords": keywords,
    "location_code": 2840,  # United States
    "language_code": "en",
}]
response = requests.post(
    f"{BASE_URL}/keywords_data/google_ads/search_volume/live",
    headers={"Authorization": f"Basic {encoded}"},
    json=payload,
)
```

**Reference:** `scraper.py:DataForSEOClient.get_search_volume()` (lines 63–130)

---

### 2. Google Trends Data

**Code:** `trends_intel/scraper.py` → `DataForSEOClient.get_trends()`

- **API:** DataForSEO Google Trends endpoint
- **Output:** `TrendData` with interest-over-time (may be empty for some keywords)

**Reference:** `scraper.py:get_trends()`

---

### 3. Related Queries

**Code:** `trends_intel/scraper.py` → `DataForSEOClient.get_related_queries()`

- **Output:** `top` (related queries), `rising` (trending queries)

**Reference:** `scraper.py:get_related_queries()`

---

### 4. Seasonal Analysis

**Code:** `trends_intel/agent.py` → `_analyze_seasonality()`

- **Input:** `KeywordData.monthly_searches` (list of {month, search_volume})
- **Logic:** Averages volume per month across years; identifies peak months (>115% of average) and low months (<85%)
- **Season mapping:** `SEASONS` (Winter: 12,1,2; Spring: 3,4,5; Summer: 6,7,8; Fall: 9,10,11)
- **Recommendation:** Based on seasonality score (>30% = strong seasonal; >15% = slight; else = stable)
- **Output:** `SeasonalInsight` (keyword, peak_season, peak_months, low_season, low_months, seasonality_score, recommendation)

**Reference:** `agent.py:_analyze_seasonality()` (lines 143–198), `_determine_season()` (lines 200–216)

---

### 5. Ad Timing Recommendations

**Code:** `trends_intel/agent.py` → `_generate_timing_recommendation()`

- **Best months:** Peak months from seasonal analysis
- **Avoid months:** Low months
- **Current trend:** Compares recent vs older monthly volume → rising/falling/stable
- **Budget advice:** Based on CPC and competition (e.g., high CPC + high competition → suggest long-tail keywords)

**Reference:** `agent.py:_generate_timing_recommendation()` (lines 218–268)

---

## Main Entry Point

**Code:** `trends_intel/agent.py` → `TrendsIntelAgent`

```python
agent = TrendsIntelAgent()
analysis = agent.analyze(
    keywords=["electrician", "electrician near me", "best electrician"],
    location="United States",
    include_related=True,
)
```

**Reference:** `agent.py:TrendsIntelAgent.analyze()` (lines 66–141)

---

## Output Model

**Code:** `trends_intel/models.py`

| Field | Type | Description |
|-------|------|-------------|
| `keyword_data` | List[KeywordData] | search_volume, cpc, competition, monthly_searches |
| `trend_data` | List[TrendData] | Interest over time (if available) |
| `seasonal_insights` | List[SeasonalInsight] | peak_months, low_months, seasonality_score, recommendation |
| `timing_recommendations` | List[AdTimingRecommendation] | best_months, avoid_months, current_trend, budget_advice |
| `related_queries` | List[str] | Top related queries |
| `rising_queries` | List[str] | Rising/trending queries |

---

## APIs Used

| API | Purpose | Env Var |
|-----|---------|---------|
| DataForSEO | Search volume, trends, related queries | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` |

**Note:** Use API credentials from https://app.dataforseo.com/api-access (not account email/password).

---

## Standalone Run

```bash
python run_trends_intel.py -k "electrician" "electrician near me" "best electrician"
```
