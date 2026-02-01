#!/usr/bin/env python3
"""
Google Drive PDF Upload MCP Agent

uAgent that wraps the FastMCP Google Drive server using MCPServerAdapter.
Deployable on Agentverse for ASI:One discovery.

Based on: https://github.com/fetchai/innovation-lab-examples/tree/main/mcp-agents
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root so relative paths (output/pdfs) work when run from mcp-agents
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# Set default output dir for PDFs (server reads GDRIVE_OUTPUT_DIR)
os.environ.setdefault("GDRIVE_OUTPUT_DIR", str(PROJECT_ROOT / "output" / "pdfs"))

load_dotenv(PROJECT_ROOT / ".env")

from uagents import Agent
from uagents_adapter import MCPServerAdapter
from server import mcp

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

mcp_adapter = MCPServerAdapter(
    mcp_server=mcp,
    llm_api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    llm_base_url="https://api.openai.com/v1",
    system_prompt="""
You help users upload PDF files to Google Drive folders.

=== UPLOAD OPTIONS ===
1. upload_pdf_to_drive: Upload a specific PDF by path. Use when user provides a file path.
2. upload_latest_pdf_from_output: Upload the most recent PDF from output/pdfs. Use when user says
   "upload the latest PDF", "upload my report", or after a PDF was just generated.

=== FOLDER ID ===
- Users must provide a Google Drive folder ID (from drive.google.com/drive/folders/FOLDER_ID)
- Or set GDRIVE_DEFAULT_FOLDER_ID in environment
- If folder_id is missing, ask the user for it

=== AUTH ===
- If check_auth_status fails, guide user through setup_oauth and complete_oauth
""",
)

agent = Agent(
    name="gdrive-pdf-upload-agent",
    seed="gdrive-pdf-upload-agent-seed",
    port=int(os.getenv("GDRIVE_AGENT_PORT", "8003")),
    mailbox=True,
)

for protocol in mcp_adapter.protocols:
    agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    mcp_adapter.run(agent)
