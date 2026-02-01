# Related Questions Intel Agent

Fetches Google **"People also ask"** (related questions) via SerpAPI for content ideas, FAQs, and search intent.

---

## Example Input

```python
agent = RelatedQuestionsIntelAgent()
analysis = agent.analyze(
    business_type="plumber",
    location="Providence, RI",
    seed_queries=None,  # default: "plumber Providence RI", "best plumber Providence RI", "plumber near me"
)
```

**CLI:**
```bash
python run_related_questions_intel.py -b "plumber" -l "Providence, RI"
python run_related_questions_intel.py -b "electrician" -l "Boston, MA" --queries "emergency electrician Boston"
```

---

## Example Output (abbreviated)

```json
{
  "business_type": "plumber",
  "location": "Providence, RI",
  "query_results": [
    {
      "query": "plumber Providence RI",
      "questions": [
        {
          "question": "How much does a plumber cost per hour?",
          "snippet": "The average cost for a plumber is $45–$200 per hour...",
          "link": "https://...",
          "title": "Plumber Cost Guide"
        },
        {
          "question": "What do plumbers charge for?",
          "snippet": "Plumbers typically charge for labor, parts...",
          "link": null,
          "title": null
        }
      ]
    },
    {
      "query": "best plumber Providence RI",
      "questions": [
        {
          "question": "How do I find a good plumber?",
          "snippet": "...",
          "link": "...",
          "title": "..."
        }
      ]
    }
  ]
}
```

---

## Purpose

Collect **People also ask** questions for:

1. **Content / SEO** – Questions to answer on site or in FAQs
2. **Intent** – What searchers care about in the niche and location
3. **Ad copy** – Question-based headlines and ad angles

---

## How It Works

### 1. Seed Queries

**Code:** `related_questions_intel/agent.py` → `RelatedQuestionsIntelAgent.analyze()`

- **Default queries:** `"{business_type} {location}"`, `"best {business_type} {location}"`, `"{business_type} near me"`
- **Optional:** Caller can pass `seed_queries` for custom queries

**Reference:** `agent.py:analyze()` (lines 35–45)

---

### 2. SerpAPI Google Search

**Code:** `related_questions_intel/scraper.py` → `RelatedQuestionsScraper.get_related_questions()`

- **API:** SerpAPI `engine=google`, `q=query`
- **Response key:** `related_questions` (People also ask block)
- **Per item:** `question`, `snippet`, `link`, `title`
- **Output:** `QueryQuestions` (query + list of `RelatedQuestion`)

```python
params = {
    "engine": "google",
    "q": query,
    "api_key": self.api_key,
    "gl": "us",
    "hl": "en",
}
if location:
    params["location"] = location
response = requests.get(self.base_url, params=params, timeout=45)
data = response.json()
for item in data.get("related_questions", [])[:max_questions]:
    result.questions.append(RelatedQuestion(question=..., snippet=..., link=..., title=...))
```

**Reference:** `scraper.py:get_related_questions()` (lines 28–75)

---

### 3. Aggregation

**Code:** `related_questions_intel/models.py` → `RelatedQuestionsAnalysis.all_questions()`

- **Input:** `query_results` (list of `QueryQuestions`)
- **Logic:** Flatten to unique question strings (deduplicated)
- **Output:** `List[str]` for Marky report and downstream agents

**Reference:** `models.py:RelatedQuestionsAnalysis.all_questions()` (lines 55–64)

---

## Main Entry Point

**Code:** `related_questions_intel/agent.py` → `RelatedQuestionsIntelAgent`

```python
agent = RelatedQuestionsIntelAgent()
analysis = agent.analyze(
    business_type="electrician",
    location="Providence, RI",
    seed_queries=None,
    max_questions_per_query=15,
)
# analysis.query_results  -> per-query questions
# analysis.all_questions() -> flat unique list for report
```

**Reference:** `agent.py:RelatedQuestionsIntelAgent.analyze()` (lines 28–75)

---

## Output Model

**Code:** `related_questions_intel/models.py`

| Field | Type | Description |
|-------|------|-------------|
| `business_type` | str | Business type (e.g., plumber) |
| `location` | str | Location (e.g., Providence, RI) |
| `query_results` | List[QueryQuestions] | Per-query questions (query + list of RelatedQuestion) |
| `RelatedQuestion` | question, snippet, link, title | One PAA item |
| `all_questions()` | List[str] | Flat unique question list |

---

## APIs Used

| API | Purpose | Env Var |
|-----|---------|---------|
| SerpAPI | Google search → related_questions (People also ask) | `SERPAPI_KEY` |

**Note:** Same `SERPAPI_KEY` as Local Intel, Yelp Intel, Review Intel. Get key at https://serpapi.com (100 free/month).

---

## Standalone Run

```bash
python run_related_questions_intel.py -b "electrician" -l "Providence, RI"
python run_related_questions_intel.py -b "plumber" -l "Boston, MA" --queries "emergency plumber" "plumber cost"
```

See `AGENTS.md` for full agent reference.
