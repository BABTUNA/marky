# Agentverse Readiness Checklist

Use this checklist before running on Agentverse / ASI:One.

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `AGENTVERSE_API_KEY` | Fetch.AI Agentverse API key ([agentverse.ai](https://agentverse.ai) → API Keys) |
| `AGENT_SEED_PHRASE` | Unique seed for agent identity (keeps address stable) |
| `GROQ_API_KEY` | LLM for script and analysis |
| `GCP_PROJECT_ID` | Google Cloud project (Imagen, TTS, VEO) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON |

## Pipeline Dependencies (for full campaigns)

| Variable | Purpose |
|----------|---------|
| `GCP_LOCATION` | e.g. `us-central1` |
| `YOUTUBE_API_KEY` | Research (optional, improves results) |
| `GOOGLE_PLACES_API_KEY` | Location scouting |
| `SERPAPI_KEY` | Competitor research |
| `GDRIVE_DEFAULT_FOLDER_ID` | Where to upload videos/PDFs (or tmpfiles.org fallback) |

## GCP APIs to Enable

- Vertex AI API
- Cloud Text-to-Speech API
- (Optional) Maps Static API (competitor map)
- (Optional) Places API

## Run Steps

1. **Set env vars** — Copy `.env.example` to `.env` and fill in keys.

2. **Start the agent:**
   ```bash
   python agents/orchestrator.py
   ```

3. **Verify startup output:**
   - Agent address printed
   - "Successfully registered with Agentverse!"
   - "Mailbox access token acquired" (if using mailbox)

4. **Connect via Agentverse:**
   - Open the **Agent Inspector** URL from the terminal
   - Click **Connect** → choose **Mailbox** (or **Proxy** if `USE_PROXY=true`)

5. **Test on ASI:One:**
   - Go to [asi1.ai](https://asi1.ai)
   - Search for "AdBoard AI" or your agent address
   - Send: "Create an ad campaign for my coffee shop in Providence"

## Optional: Proxy vs Mailbox

- **Mailbox** (default): Agent connects to Agentverse; works for local runs.
- **Proxy** (`USE_PROXY=true`): Alternative for real-time chat; may need different setup.

## Quick Test Mode

To test without slow research, say **"quick test"** or **"test without research"** in your message, or set `QUICK_FULL=true` in `.env`.

## Hackathon Submission

- Include agent **name** and **address** in your README
- Add badges: `![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)` and `![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)`
- Ensure Chat Protocol is implemented (✅ done)
