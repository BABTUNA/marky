# AdVantage — Research-Backed Ad Campaigns in Minutes

---

## Inspiration

Small businesses can't afford the typical \(\$5\text{K}\)–\(\$50\text{K}\) agencies charge for storyboards and strategy. They skip research, guess at messaging, and hope their ads perform. We wanted a tool that does the research first—then turns it into both a concept package and a ready-to-post viral video.

AdVantage gives small businesses that edge: market intelligence plus two deliverables in one flow.

---

## What We Built

AdVantage is a multi-agent system that:

1. **Researches** your market—competitors, reviews, trends
2. **Generates** a script, storyboard, and viral video
3. **Delivers** two packages: a storyboard package (script, budget, locations, hiring guide) and a photorealistic viral video for TikTok and Reels

You describe your business in plain language. We analyze the market, then produce both the development brief and the viral clip.

---

## How We Built It

We built AdVantage as a multi-agent pipeline orchestrated on Fetch.AI's Agentverse:

- **Research** — Marky workflow pulls competitor and review data via SerpAPI, Google Places, and Google Trends
- **Intent & Script** — Gemini parses user input and writes the ad script
- **Storyboard** — Vertex AI Imagen generates pencil-sketch frames (with 30s delay between calls for rate limits)
- **Viral Video** — VEO 3 for photorealistic video, Lyria for AI music, Google TTS for voiceover
- **Assembly** — FFmpeg for Ken Burns storyboard video and final viral clip assembly
- **Output** — ReportLab for PDFs, Google Drive for hosting, orchestrator sends thumbnail + links via ASI:One chat

Stack: Python, Fetch Chat Protocol, Vertex AI (Imagen, VEO 3, Lyria), ReportLab, FFmpeg. The pipeline is modular so each agent can be swapped or upgraded independently.

---

## Challenges We Faced

**Rate limits** — Imagen throttling caused failures. We fixed it by adding configurable delays (\(t = 30\)s default) between image requests via `IMAGEN_DELAY_SECONDS`.

**Black thumbnails** — The first video frame was often black. We switched to sampling multiple frames and using the first non-black frame (mean brightness \(\mu > 15\)) instead of always using frame 0.

**VEO + Lyria integration** — Coordinating VEO 3 video generation with Lyria music and TTS required careful pipeline orchestration and timing.

**Agentverse storage** — External Storage uses async webhooks; we added fallbacks so the flow still works when storage fails.

**Competitor map** — Marky's CompetitorInsight lacked address data; we added the `address` field to the model and wired it through so the map generator could plot locations.

**UX** — Early responses felt robotic; we rewrote to natural language, added progress check-ins, and simplified the final output to thumbnail + links.

---

## What We Learned

Market research and creative generation work well as separate agent stages. Fetch's Chat Protocol made it straightforward to add image previews. Progress callbacks matter for long-running pipelines. VEO 3 and Lyria deliver strong results when orchestrated correctly. Graceful fallbacks (map, storage, rate limits) make the product more robust. Users prefer concise, human-sounding messages over dense, robotic output.

---

## What's Next for AdVantage

- Cloud deployment for 24/7 availability
- Payment Protocol for monetization
- A/B test variant generation
- Multi-language support
- Direct TikTok/Instagram API integration for publishing

---

## Built With

**Languages & Frameworks**
- Python
- Fetch.AI uAgents / Agentverse
- ReportLab (PDF generation)
- Pydantic (data validation)

**Cloud & APIs**
- Google Cloud Vertex AI (Imagen, Gemini, VEO 3, Lyria)
- Google Cloud Text-to-Speech
- Google Places API
- Google Maps Static API
- SerpAPI (competitor research)
- ElevenLabs (voiceover)
- Groq (LLM fallback)

**Tools & Libraries**
- FFmpeg (video assembly, Ken Burns effects)
- OpenCV (video thumbnail extraction)
- Pillow (image processing, competitor map)
- httpx / requests / aiohttp (HTTP clients)
- python-dotenv (config)

**Platforms**
- Fetch.AI Agentverse (agent hosting, ASI:One chat)
- Google Drive (file hosting)
- MCP (Model Context Protocol) for Drive uploads

---

*Built at Hack@Brown 2026 for the Fetch.AI track.*
