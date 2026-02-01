# AdBoard AI - Agent Architecture

## 🤖 Multi-Agent System Overview

**12 Autonomous Agents** working in concert to generate complete ad campaigns via ASI:One.

AdBoard AI is a sophisticated multi-agent orchestration system that leverages specialized AI agents for research, content generation, and campaign delivery. Each agent operates independently, communicating through the Fetch.AI Agentverse platform to create professional advertising campaigns automatically.

> **Key Feature:** Parallel agent execution enables 3-5 second research phase with 5 concurrent intelligence agents.

## Architecture Diagram

![AdBoard AI Multi-Agent Pipeline](agent_architecture_diagram.png)

> **Multi-Agent Orchestration:** This system coordinates **12 autonomous agents** across 7 layers, with parallel execution in research (5 agents) and video generation (2 agents) phases.

---

## 🤖 Complete Agent Roster (12 Agents)

### Layer 1: User Interface (1 Agent)
**Agent #1 - ASI:One Chat Interface Agent**
- Receives user requests via Fetch.AI Agentverse
- Extracts business intent using Groq LLaMA
- Routes to orchestrator agent

### Layer 2: Intelligence Gathering (5 Agents - Parallel Execution)
**Agent #2 - Google Trends Intelligence Agent**
- Analyzes keyword trends and search volume
- Identifies rising search terms
- Provides seasonal timing recommendations

**Agent #3 - Google Places Discovery Agent**
- Finds local competitors using Google Places API
- Extracts ratings, reviews, services
- Maps competitor locations

**Agent #4 - Google Reviews Analysis Agent**
- Scrapes and analyzes Google Maps reviews
- Identifies customer pain points and desires
- Extracts common themes and sentiments

**Agent #5 - Yelp Intelligence Agent**
- Analyzes Yelp reviews for voice of customer
- Identifies praise patterns and complaints
- Generates ad hooks based on real feedback

**Agent #6 - Related Questions Agent**
- Scrapes "People Also Ask" queries
- Identifies content intent and FAQ topics
- Provides messaging opportunities

### Layer 3: Research Synthesis (1 Agent)
**Agent #7 - Research Synthesis Agent**
- Aggregates data from all 5 intelligence agents
- Identifies competitive differentiators
- Creates unified market analysis
- Generates strategic recommendations

### Layer 4: Content Creation (1 Agent)
**Agent #8 - Script Writer AI Agent**
- Uses Groq LLaMA 3.3 70B for script generation
- Creates scene-by-scene breakdown
- Tailors to business type and tone
- Optimizes timing and pacing

### Layer 5: Visual Production (2 Agents - Parallel Execution)
**Agent #9 - Storyboard Generator Agent**
- Generates black & white pencil sketches using Imagen 3
- Creates 30-60s concept video with Ken Burns effects
- Produces 5-7 frames at ~$0.02/frame

**Agent #10 - Viral Video Generator Agent**
- Creates 15s photorealistic video using VEO 3
- TikTok/Instagram-optimized format
- 4K quality, cinematic production value
- Cost: ~$2.00 per video

### Layer 6: Campaign Assembly (1 Agent)
**Agent #11 - Campaign Package Builder Agent**
- Compiles research, scripts, and visuals into PDF
- Adds Google Maps competitor visualization
- Includes cost breakdown and social strategy
- Uploads files to tmpfiles.org

### Layer 7: Response Delivery (1 Agent)
**Agent #12 - Response Formatter Agent**
- Formats complete response for ASI:One
- Provides download links and previews
- Delivers campaign summary
- Ensures optimal chat display

---

## Pipeline Flow

### 1️⃣ Input Layer
**ASI:One Chat Interface**
- User describes their business and ad needs
- Natural language → structured intent extraction
- Example: "Create an ad campaign for my sushi shop in LA"

### 2️⃣ Parallel Research Layer (Concurrent Execution)

All research agents run simultaneously for maximum speed:

| Agent | API/Service | Purpose |
|-------|------------|---------|
| 🔍 **Google Trends** | Google Trends API (Free) | Keyword trends, search volume, rising topics |
| 📍 **Google Places** | Google Places API | Competitor discovery, ratings, locations |
| ⭐ **Google Reviews** | Google Maps Reviews | Customer sentiment, pain points |
| 🗣️ **Yelp Intelligence** | SerpAPI + Yelp | Voice of customer, desires, complaints |
| ❓ **Related Questions** | Google "People Also Ask" | Content intent, FAQ insights |

**Runtime:** ~3-5 seconds (parallel execution)

### 3️⃣ Research Synthesis
**Purpose:** Combine insights from all research agents  
**Output:**
- Competitor landscape analysis
- Customer pain points & desires
- Trending hooks and angles
- Ad differentiation strategies
- Seasonal/timing recommendations

### 4️⃣ Script Generation
**AI Script Writer (Groq LLaMA 3.3 70B)**
- Generates professional ad script based on research
- Multiple scenes with timing, visuals, and voiceover
- Tailored to business type, tone, and target audience
- Typically 5-7 scenes for 30-60s video

### 5️⃣ Parallel Content Creation

Two videos generated simultaneously:

#### 🎨 Long-Form Storyboard Video (Imagen 3)
- **Duration:** 30-60 seconds
- **Style:** Black & white pencil sketches
- **Purpose:** Concept visualization, client presentation
- **Tech:** Google Vertex AI Imagen 3
- **Cost:** ~$0.02/frame (~$0.10 total)
- **Output:** Silent video with Ken Burns effects

#### 🎬 Short-Form Viral Video (VEO 3)
- **Duration:** 15 seconds
- **Style:** Photorealistic, TikTok-optimized
- **Purpose:** Social media ready, high engagement
- **Tech:** Google Veo 3 (4K video generation)
- **Cost:** ~$2.00 per video
- **Output:** Professional viral marketing content

### 6️⃣ Campaign Package Assembly

**PDF Builder** creates comprehensive ad package:
- ✅ Complete script with all scenes
- ✅ Storyboard frames (B&W sketches)
- ✅ Research insights & competitor analysis
- ✅ Cost breakdown & production estimates
- ✅ Social media strategy (hashtags, captions)
- ✅ Filming location recommendations
- ✅ Google Maps with competitor locations
- ✅ Campaign distribution timeline

**File Hosting:** Videos & PDF uploaded to tmpfiles.org

### 7️⃣ Output Delivery

**ASI:One Response** provides:
- 📹 Video preview (inline viewing)
- 🔗 Download links (video + PDF)
- 📊 Campaign summary
- 💰 Cost estimates
- 📱 Social media strategy

Links valid for ~1 hour (sufficient for demo/review)

---

## Technology Stack

### AI Models
| Component | Technology | Cost |
|-----------|-----------|------|
| Script Writing | Groq LLaMA 3.3 70B | Free tier |
| Storyboard Images | Google Imagen 3 | $0.02/image |
| Viral Videos | Google Veo 3 | $2.00/video |
| Intent Extraction | Groq LLaMA | Free tier |

### Google Cloud APIs (Using $410 Credits)
- ✅ Google Trends API (Free)
- ✅ Google Places API
- ✅ Google Maps Static API
- ✅ Google Vertex AI (Imagen 3, Veo 3)

### Third-Party Services
- SerpAPI (Yelp, Google searches)
- tmpfiles.org (Temporary file hosting)
- Fetch.AI Agentverse (Agent orchestration)

---

## Key Features

### 🚀 Speed
- Parallel research execution (3-5 seconds)
- Concurrent video generation
- End-to-end: ~2-3 minutes per campaign

### 💰 Cost Efficiency
- Leverages $410 Google Cloud credits
- Free APIs where possible (Trends, Groq)
- ~$2.50 per complete campaign

### 🎯 Quality
- Research-backed scripts
- Professional storyboards
- Viral-ready short videos
- Complete campaign strategy

### 📦 Deliverables
- 2 videos (long-form + short-form)
- Professional PDF package
- Social media assets
- Production cost estimates

---

## Future Enhancements

- [ ] Real-time video rendering preview
- [ ] A/B test variant generation
- [ ] Multi-language support
- [ ] Brand voice customization
- [ ] Campaign analytics dashboard

---

**Built at Hack@Brown 2026 for Fetch.AI**  
*Leveraging Google Cloud's $410 credits for maximum value*
