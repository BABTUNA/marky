# Google Drive PDF Upload MCP Agent

Uploads PDF files to Google Drive folders. Based on [Fetch.ai innovation-lab-examples MCP pattern](https://github.com/fetchai/innovation-lab-examples/tree/main/mcp-agents).

## Tools

| Tool | Description |
|------|-------------|
| `upload_pdf_to_drive` | Upload a PDF file by path to a Drive folder |
| `upload_latest_pdf_from_output` | Upload the most recent PDF from `output/pdfs` |
| `setup_oauth` | Get OAuth URL to authenticate with Google Drive |
| `complete_oauth` | Complete OAuth with auth code |
| `check_auth_status` | Verify authentication |

## Setup

### 1. Google Cloud Console

1. Create a project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Google Drive API**
3. Create OAuth 2.0 credentials (Desktop app)
4. Download JSON and save as `credentials.json` in this directory

### 2. OAuth Flow

```bash
# Run agent or server, then call setup_oauth to get URL
# Open URL in browser, authorize, copy the code
# Call complete_oauth with the code
```

### 3. Environment

```bash
cp env.sample .env
# Set OPENAI_API_KEY, GDRIVE_DEFAULT_FOLDER_ID (optional)
```

### 4. Install Dependencies

```bash
pip install mcp uagents uagents-adapter google-auth google-auth-oauthlib google-api-python-client python-dotenv
```

## Run

```bash
cd mcp-agents/gdrive-pdf-upload-mcp-agent
python agent.py
```

Deploy to Agentverse for ASI:One discovery (mailbox enabled).

## Test (without Marky)

```bash
cd mcp-agents/gdrive-pdf-upload-mcp-agent
python test_agent.py --check-auth
python test_agent.py --setup-oauth
python test_agent.py --complete-oauth <auth_code_from_browser>
python test_agent.py --upload path/to/file.pdf --folder-id YOUR_FOLDER_ID
python test_agent.py --upload-latest --folder-id YOUR_FOLDER_ID
```

## Integration with Marky

When Marky runs with `--drive-upload`, the workflow:

1. Exports the report to PDF via `orchestrator/report_to_pdf.py`
2. Imports and calls `upload_pdf_to_drive()` from this MCP server

```bash
python run_marky.py --cli -b "plumber" -l "Boston" --drive-upload --drive-folder-id "YOUR_FOLDER_ID"
```

**Chat:** Add "and upload to drive" to the query (requires GDRIVE_DEFAULT_FOLDER_ID in .env).

## Folder ID

Get from the folder URL: `https://drive.google.com/drive/folders/FOLDER_ID`
