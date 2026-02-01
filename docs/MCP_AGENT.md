# MCP Agent: Google Drive File Upload

Model Context Protocol (MCP) agent that uploads PDFs, videos, and other files to Google Drive. Integrated into the AdBoard AI pipeline for permanent file hosting (replacing tmpfiles.org).

---

## Quick Setup (Orchestrator Integration)

To use Google Drive instead of tmpfiles.org for uploads:

1. **Google Cloud Console**: Create OAuth 2.0 credentials (Desktop app), enable Drive API
2. **credentials.json**: Download from Google Cloud Console → save to `mcp-agents/gdrive-pdf-upload-mcp-agent/credentials.json`
3. **OAuth flow**: Run the setup script (see below) to authenticate
4. **.env**: Add `GDRIVE_DEFAULT_FOLDER_ID=your_folder_id` (get from folder URL: drive.google.com/drive/folders/FOLDER_ID)

---

## OAuth Setup

```bash
cd mcp-agents/gdrive-pdf-upload-mcp-agent
python -c "
from server import drive_auth
url = drive_auth.get_oauth_url()
print('Open this URL in a browser:', url)
code = input('Paste the authorization code: ')
drive_auth.exchange_code_for_token(code)
print('Done! You can now use Drive uploads.')
"
```

Or use the MCP tools if running the agent: `setup_oauth` → open URL → `complete_oauth` with code.

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GDRIVE_DEFAULT_FOLDER_ID` | Target folder for uploads (required for Drive) |
| `GDRIVE_CREDENTIALS_PATH` | Path to credentials.json |
| `GDRIVE_TOKENS_PATH` | Path to oauth_tokens.json |

---

## How It Works

- **Orchestrator**: When `GDRIVE_DEFAULT_FOLDER_ID` is set, `format_results()` uploads storyboard videos, viral videos, and PDFs to Google Drive instead of tmpfiles.org
- **Fallback**: If Drive fails or isn't configured, falls back to tmpfiles.org (1hr expiry)
- **Supported files**: PDF, MP4, MOV, WebM, PNG, JPG, GIF, MP3, WAV

---

## Standalone MCP Agent

To run as a standalone uAgent (optional):

```bash
cd mcp-agents/gdrive-pdf-upload-mcp-agent
pip install fastmcp uagents-adapter[mcp]
python agent.py
```

---

## Files

| File | Purpose |
|------|---------|
| `utils/gdrive_upload.py` | Core upload logic (used by orchestrator) |
| `mcp-agents/gdrive-pdf-upload-mcp-agent/server.py` | FastMCP server with tools |
| `mcp-agents/gdrive-pdf-upload-mcp-agent/agent.py` | uAgent wrapper (optional) |
