# Google Drive File Upload MCP Agent

Uploads PDFs, videos, and other files to Google Drive. Used by AdBoard AI for permanent file hosting.

## Setup

1. Create OAuth 2.0 credentials (Desktop app) in Google Cloud Console
2. Enable Google Drive API
3. Save `credentials.json` in this directory
4. Run OAuth flow (see project `docs/MCP_AGENT.md`)
5. Set `GDRIVE_DEFAULT_FOLDER_ID` in `.env`

## Orchestrator Integration

The main AdBoard orchestrator uses `utils/gdrive_upload.py` directly. When `GDRIVE_DEFAULT_FOLDER_ID` is set, generated videos and PDFs are uploaded to Google Drive instead of tmpfiles.org.

## Standalone MCP Server

```bash
pip install fastmcp google-auth-oauthlib google-api-python-client
python server.py
```

Runs on port 8082 (or `GDRIVE_MCP_PORT`).
