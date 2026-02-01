# Image Preview Test Agent

Tests **displaying an image** in ASI:One / Agentverse chat using the Chat Protocol `ResourceContent`. Uses a sample image in this folder, or creates one on first run.

## What it does

1. Runs a uAgent with Chat Protocol and mailbox (Agentverse discovery).
2. On any chat message: acknowledges, then reads (or creates) `sample.png`, uploads it to **Agentverse External Storage**, and replies with a `ChatMessage` containing `ResourceContent` (image/png) so the chat UI can show the image inline.
3. Also sends a clickable HTTPS link so you can open the image if the UI doesn’t embed it.

## Requirements

- Python 3.10+
- `uagents`, `uagents-core`
- **AGENTVERSE_API_KEY** in `.env` (project root or here)
- **Pillow** (optional) — only needed if `sample.png` doesn’t exist; the agent will create it. Project root has `Pillow` in requirements.

## Setup

1. **AGENTVERSE_API_KEY** in `.env` (project root or `image_testing/.env`).
2. **Image** — Prefer **`image_testing/fetch.png`** (agent uses it if present). Otherwise the agent uses **`sample.png`**, creating it on first run with Pillow if missing.

## Run

From project root:

```bash
python image_testing/preview_agent.py
```

- Default port: **8011** (so it doesn’t clash with the video preview agent on 8010).
- Connect via Agentverse mailbox, then **Chat with Agent** (or find via ASI:One).
- Send any message; the agent replies with the sample image. Image display depends on the platform; you always get a clickable link as fallback.

## Optional env vars

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTVERSE_API_KEY` | — | Required for upload |
| `IMAGE_PREVIEW_AGENT_NAME` | `Image Preview Test Agent` | Agent name |
| `IMAGE_PREVIEW_AGENT_SEED` | `image-preview-test-agent-seed` | Agent seed |
| `IMAGE_PREVIEW_AGENT_PORT` | `8011` | Agent port |

## Reference

- [Image Generation Agent (ResourceContent)](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/image-generation-agent) — same pattern; Agentverse Chat supports image display; ASI:One may support it as well.
