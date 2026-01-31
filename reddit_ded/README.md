# Reddit VoC Research Agent

A Voice of Customer (VoC) research agent that scrapes Reddit to extract pain points, desires, objections, and language patterns for ad creative generation.

## What It Does

Given a **product**, **audience**, and **market**, this agent:

1. **Discovers relevant subreddits** automatically (no prior knowledge needed)
2. **Scrapes posts and comments** with smart rate limiting and caching
3. **Extracts VoC signals**: pain points, desires, objections, comparisons
4. **Clusters into themes**: price, quality, convenience, trust, etc.
5. **Generates ad research outputs** ready for creative teams:
   - `VoiceOfCustomerBrief` - themes, quotes, language bank
   - `AnglePlaybook` - advertising angles with promises
   - `HookBank` - hook lines with tones and visuals
   - `ObjectionHandling` - objections with rebuttals
   - `SourceMap` - where the data came from

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Reddit API Credentials

Create a Reddit app at: https://www.reddit.com/prefs/apps

1. Log into Reddit
2. Go to **User Settings → Privacy & Security → Developed Applications**
3. Click **Create App** → Choose **script**
4. Note your `client_id` (under app name) and `client_secret`

Set environment variables:

```bash
# Windows (PowerShell)
$env:REDDIT_CLIENT_ID = "your_client_id"
$env:REDDIT_CLIENT_SECRET = "your_client_secret"
$env:REDDIT_USERNAME = "your_reddit_username"
$env:REDDIT_PASSWORD = "your_reddit_password"
$env:REDDIT_USER_AGENT = "VoCResearchAgent/1.0 by /u/your_username"

# Linux/Mac
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USERNAME="your_reddit_username"
export REDDIT_PASSWORD="your_reddit_password"
export REDDIT_USER_AGENT="VoCResearchAgent/1.0 by /u/your_username"
```

Or create a `.env` file:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=VoCResearchAgent/1.0 by /u/your_username
```

### 3. Run Research

```bash
# Basic usage
python main.py --product "Coffee Subscription" --audience "Coffee lovers" --market "Beverages"

# With keywords and competitors
python main.py \
    --product "Oat Milk" \
    --audience "Health-conscious consumers" \
    --market "Plant-based beverages" \
    --keywords "dairy free" "vegan" "barista" \
    --competitors "Oatly" "Califia"

# Interactive mode
python main.py --interactive

# Output as JSON
python main.py -p "Product" -a "Audience" -m "Market" --json
```

## Output Structure

Results are saved to `output/` directory:

```
output/
├── voc_research_20260131_120000.json          # Combined output
├── voc_research_20260131_120000_voc_brief.json
├── voc_research_20260131_120000_angle_playbook.json
├── voc_research_20260131_120000_hook_bank.json
├── voc_research_20260131_120000_objection_handling.json
└── voc_research_20260131_120000_source_map.json
```

### Sample Output

```json
{
  "voice_of_customer_brief": {
    "product": "Coffee Subscription",
    "audience": "Coffee lovers",
    "market": "Beverages",
    "top_themes": [
      {
        "theme": "Price",
        "weight": 0.25,
        "example_quotes": ["Way too expensive for what you get..."],
        "common_objections": ["Not worth the premium price"],
        "desired_outcomes": ["Good value for money"]
      }
    ],
    "language_bank": ["stale beans", "fresh roasted", "worth every penny"]
  },
  "hook_bank": {
    "hooks": [
      {
        "hook_text": "Tired of stale grocery store coffee? You're not alone.",
        "mapped_theme": "Quality",
        "tone": "empathetic",
        "recommended_opening_visual": "Relatable everyday situation"
      }
    ]
  }
}
```

## Python API

```python
from reddit_voc.agent import VoCResearchAgent

# Initialize agent
agent = VoCResearchAgent()

# Run research
output = agent.research(
    product="Coffee Subscription",
    audience="Coffee lovers who want fresh beans",
    market="Beverages",
    keywords=["specialty coffee", "fresh roasted"],
    competitors=["Trade Coffee", "Blue Bottle"],
)

# Access results
for theme in output.voc_brief.top_themes:
    print(f"{theme.name}: {theme.weight:.1%}")
    for quote in theme.example_quotes:
        print(f"  - {quote}")

for hook in output.hook_bank.hooks:
    print(f"[{hook.tone}] {hook.text}")

# Save to files
agent.save_output(output, output_dir="my_output")
```

## Architecture

```
reddit_voc/
├── __init__.py
├── config.py           # Configuration management
├── models.py           # Data models (Subreddit, Post, Comment, Theme, etc.)
├── cache.py            # SQLite caching layer
├── reddit_client.py    # Reddit API client with OAuth & rate limiting
├── discovery.py        # Subreddit discovery from keywords
├── scraper.py          # Post and comment scraper
├── voc_extractor.py    # VoC signal extraction and theme clustering
├── output_generator.py # Generate hooks, angles, objections
└── agent.py            # Main orchestrator
```

## Configuration

Edit `reddit_voc/config.py` to adjust:

```python
@dataclass
class ResearchConfig:
    max_subreddits: int = 20          # Max subreddits to discover
    min_subscribers: int = 1000       # Min subscriber filter
    posts_per_subreddit: int = 50     # Posts to scrape per sub
    comments_per_post: int = 50       # Comments per post
    max_posts_total: int = 500        # Global post limit
    max_comments_total: int = 2000    # Global comment limit
    max_themes: int = 12              # Max themes to extract
```

## Rate Limiting & Caching

- **Rate limiting**: 1 request/second by default (configurable)
- **Automatic retries**: Exponential backoff on 429/5xx errors
- **SQLite cache**: Responses cached for 12 hours
- **Deduplication**: Posts and comments are deduplicated

## Hackathon Tips

### Day 1 MVP
- Get OAuth working
- Discover 5-10 subreddits
- Pull 200-500 comments
- Basic keyword-based theme extraction
- Output HookBank + top pain points

### Day 2 Upgrade
- Add embeddings for better clustering
- Quote extraction per theme
- Objection→Rebuttal generation
- Polish output formatting

## Troubleshooting

### "Authentication failed"
- Double-check `client_id` and `client_secret`
- Make sure your Reddit account has no 2FA (or use app password)
- Verify `user_agent` follows Reddit's format: `platform:appname:version (by /u/username)`

### "Rate limited"
- Reduce `requests_per_second` in config
- The agent auto-retries with backoff

### No results found
- Try broader keywords
- Check if subreddits exist for your niche
- Lower `min_subscribers` threshold

## License

MIT - Use freely for hackathons and beyond!
