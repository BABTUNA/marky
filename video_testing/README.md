# Video Preview Test Agent

Sample uAgent that **only** tests uploading a video preview to ASI:One / Agentverse using the Chat Protocol `ResourceContent`. It uses the MP4 in this folder.

## What it does

1. Runs a uAgent with Chat Protocol and mailbox (Agentverse discovery).
2. On any chat message: acknowledges, then reads the sample video from this folder, uploads it to **Agentverse External Storage**, and replies with a `ChatMessage` containing `ResourceContent` (video/mp4) so the chat UI can show a preview.

## Requirements

- Python 3.10+
- `uagents`, `uagents-core` (from project root: `pip install -r requirements.txt` or `pip install uagents uagents-core`)
- **AGENTVERSE_API_KEY** in `.env` (project root or here) so the agent can upload the video to storage

## Setup

1. **Get an Agentverse API key**  
   [Agentverse](https://agentverse.ai/) → account / API keys.

2. **Add to `.env`** (project root or `video_testing/.env`):
   ```env
   AGENTVERSE_API_KEY=your_key_here
   ```

3. **Video file**  
   The agent expects this file in the same folder:
   - `YTDowncom_YouTube_3-Second-Video_Media_1O0yazhqaxs_001_1080p.mp4`

   If it’s missing, the agent will reply with a text error.

## Run

From project root:

```bash
python video_testing/preview_agent.py
```

Or from this folder:

```bash
cd video_testing
python preview_agent.py
```

- Default port: **8010** (override with `VIDEO_PREVIEW_AGENT_PORT`).
- Use the Agent Inspector link in the logs to connect via **Mailbox** to Agentverse.
- In Agentverse, open the agent and click **Chat with Agent** (or find it via ASI:One).
- Send any message; the agent replies with the video resource and a **clickable "Watch video" link** (HTTPS). If ASI:One doesn't show an inline player, use that link to open the video. The link text for the resource is set to "Watch video" so it appears as a clear clickable item on the platform.

## Optional env vars

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTVERSE_API_KEY` | — | Required for uploading video to storage |
| `AGENTVERSE_URL` | `https://agentverse.ai` | Agentverse base URL |
| `VIDEO_PREVIEW_AGENT_NAME` | `Video Preview Test Agent` | Agent name |
| `VIDEO_PREVIEW_AGENT_SEED` | `video-preview-test-agent-seed` | Agent seed |
| `VIDEO_PREVIEW_AGENT_PORT` | `8010` | Agent port |

## References

- [ASI:One Video Preview demo code](../docs/ASI_ONE_VIDEO_PREVIEW.md)
- [Image Generation Agent (same ResourceContent pattern)](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/image-generation-agent)
