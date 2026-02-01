# MCP Agent: Google Drive PDF Upload

Model Context Protocol (MCP) agent that uploads PDF reports to Google Drive. Integrated into the Marky end-to-end workflow.

---

## What is MCP?

**Model Context Protocol** is an open standard that lets AI agents and LLMs call external tools in a consistent way. Fetch.ai’s [innovation-lab-examples](https://github.com/fetchai/innovation-lab-examples/tree/main/mcp-agents) use MCP to expose tools (e.g., weather, Gmail, events) as uAgents on Agentverse.

This project adds a **Google Drive PDF Upload** MCP agent that:

1. Exposes upload tools via a FastMCP server
2. Can run as a standalone uAgent (MCPServerAdapter) on Agentverse
3. Is called directly by the Marky workflow when `--drive-upload` is used

---

## MCP Code Agent (Structure)

The **MCP code agent** lives under `mcp-agents/gdrive-pdf-upload-mcp-agent/`. It has two main pieces:

### 1. `server.py` — FastMCP server (the tools)

- Uses **FastMCP** to define tools that any MCP client (or Python code) can call.
- Each tool is a function decorated with `@mcp.tool()`:
  - **OAuth:** `setup_oauth()`, `complete_oauth(auth_code)`, `check_auth_status()`
  - **Upload:** `upload_pdf_to_drive(file_path, folder_id, file_name)`, `upload_latest_pdf_from_output(folder_id, output_dir)`
- No uAgent or network required: you can `from server import upload_pdf_to_drive` and call it from Marky.

### 2. `agent.py` — uAgent wrapper (optional)

- Wraps the same MCP server with **MCPServerAdapter** so it can run as a Fetch.ai uAgent (e.g. on Agentverse).
- Listens for chat; an LLM picks which tool to call from natural language.
- Used when you want “talk to an agent” instead of calling Marky CLI.

**Summary:** The *code* that does the work is in `server.py`. Marky integrates by importing and calling those functions. `agent.py` is for running the same tools as a standalone chat agent.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Marky Workflow (orchestrator/workflow.py)                       │
│                                                                  │
│  Stage 1–5: Intel agents (Local, Review, Yelp, Trends, Related)  │
│  Stage 6:   Raw data collection complete                         │
│  Stage 7:   PDF Export (orchestrator/report_to_pdf.py)           │
│  Stage 8:   Drive Upload ──────────────────────────────┐         │
└─────────────────────────────────────────────────────────│─────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  gdrive-pdf-upload-mcp-agent                                     │
│  mcp-agents/gdrive-pdf-upload-mcp-agent/                         │
│                                                                  │
│  server.py (FastMCP)                                             │
│    ├── setup_oauth()                                             │
│    ├── complete_oauth()                                          │
│    ├── check_auth_status()                                       │
│    ├── upload_pdf_to_drive(file_path, folder_id)                 │
│    └── upload_latest_pdf_from_output(folder_id)                  │
│                                                                  │
│  agent.py (uAgent)                                               │
│    └── MCPServerAdapter wraps server for Agentverse              │
└─────────────────────────────────────────────────────────────────┘
```

---

## How to Integrate into Marky

To wire the MCP Drive agent into the Marky pipeline:

### 1. Request parameters

In `orchestrator/models.py`, `AdResearchRequest` has:

- `include_pdf_export` — whether to export the report to PDF (default `True` when Drive upload is requested).
- `include_drive_upload` — whether to upload the PDF to Google Drive (default `False`).
- `drive_folder_id` — target folder ID (or use env `GDRIVE_DEFAULT_FOLDER_ID`).

### 2. Workflow steps (orchestrator/workflow.py)

After Stage 6 (raw data complete):

- **Stage 7 — PDF export:** If `include_pdf_export` or `include_drive_upload`, call `result_to_pdf(result)` from `orchestrator/report_to_pdf.py`. Result gets `result.pdf_path`.
- **Stage 8 — Drive upload:** If `include_drive_upload` and `result.pdf_path` and a folder ID:
  - Add `mcp-agents/gdrive-pdf-upload-mcp-agent` to `sys.path`.
  - `from server import upload_pdf_to_drive`.
  - Call `upload_pdf_to_drive(file_path=result.pdf_path, folder_id=folder_id)`.
  - Put the returned JSON (e.g. `file_id`, `web_view_link`) into `result.drive_upload_result`.

### 3. CLI (run_marky.py)

- `--drive-upload` sets `include_drive_upload=True`.
- `--drive-folder-id ID` sets `drive_folder_id` (overrides `GDRIVE_DEFAULT_FOLDER_ID`).
- `--no-pdf` sets `include_pdf_export=False` (no PDF, so no Drive upload).

### 4. Chat (orchestrator/agent.py)

- `parse_research_request()` looks for phrases like “upload to drive” / “save to drive” and sets `include_drive_upload=True`.
- Folder ID comes from `GDRIVE_DEFAULT_FOLDER_ID` in `.env` (chat has no `--drive-folder-id`).

### 5. Output

- `AdResearchResult` gets `pdf_path` and `drive_upload_result`.
- Markdown output (and JSON) includes PDF path and Drive link when present.

**Adding another MCP agent:** Follow the same pattern: implement tools in an MCP server, then in the workflow import and call the needed function(s) after the relevant stage, and add request/CLI/chat flags as needed.

---

## Integration Modes

### 1. Direct Call (Marky Workflow)

When Marky runs with `--drive-upload`, the workflow:

1. Generates a PDF from the report
2. Imports `upload_pdf_to_drive` from the MCP server
3. Calls it with the PDF path and folder ID

No separate MCP agent process is needed. The server’s tools are used as plain Python functions.

### 2. Standalone uAgent (Agentverse)

For chat-based access:

```bash
cd mcp-agents/gdrive-pdf-upload-mcp-agent
python agent.py
```

The agent runs on port 8003, uses MCPServerAdapter for tool selection, and can be discovered via Agentverse/ASI:One. Users can say things like “upload the latest PDF to my Drive folder.”

### 3. Direct Tool Testing

```bash
cd mcp-agents/gdrive-pdf-upload-mcp-agent
python test_agent.py --check-auth
python test_agent.py --upload-latest --folder-id "YOUR_FOLDER_ID"
```

---

## Tools

| Tool | Description |
|------|-------------|
| `setup_oauth` | Return OAuth URL for first-time Drive auth |
| `complete_oauth` | Exchange auth code for tokens |
| `check_auth_status` | Verify Drive authentication |
| `upload_pdf_to_drive` | Upload a specific PDF file |
| `upload_latest_pdf_from_output` | Upload the most recent PDF from `output/pdfs` |

---

## Setup

1. **Google Cloud:** Create OAuth 2.0 credentials (Desktop app), enable Drive API.
2. **credentials.json:** Download from Google Cloud Console → place in `mcp-agents/gdrive-pdf-upload-mcp-agent/`.
3. **OAuth flow:** Run `python test_agent.py --setup-oauth`, open URL, then `--complete-oauth <code>`.
4. **Folder ID:** Set `GDRIVE_DEFAULT_FOLDER_ID` in `.env` or pass `--folder-id` / `--drive-folder-id`.

---

## End-to-End Flow (Marky)

```bash
# CLI with Drive upload
python run_marky.py --cli -b "plumber" -l "Boston, MA" --drive-upload --drive-folder-id "13csILnYrm5vicf6x4kJI1nH9GdoF4Mn-"

# Or set GDRIVE_DEFAULT_FOLDER_ID in .env
python run_marky.py --cli -b "plumber" -l "Boston, MA" --drive-upload
```

**Chat (uAgent):**  
`electrician in Providence RI and upload to drive`

Requires `GDRIVE_DEFAULT_FOLDER_ID` in `.env`.

---

## Files

| File | Purpose |
|------|---------|
| `mcp-agents/gdrive-pdf-upload-mcp-agent/server.py` | FastMCP server with Drive tools |
| `mcp-agents/gdrive-pdf-upload-mcp-agent/agent.py` | uAgent wrapper for Agentverse |
| `mcp-agents/gdrive-pdf-upload-mcp-agent/test_agent.py` | Standalone test script |
| `orchestrator/report_to_pdf.py` | Converts AdResearchResult to PDF |
