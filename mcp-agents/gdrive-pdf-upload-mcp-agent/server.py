#!/usr/bin/env python3
"""
FastMCP Google Drive PDF Upload Server

Exposes tools to upload PDF files to a Google Drive folder.
Follows the Fetch.ai innovation-lab-examples MCP pattern (see gmail_chat_uagent, events-finder-mcp-agent).

Requirements:
- Google Cloud project with Drive API enabled
- OAuth 2.0 credentials (Desktop app)
- credentials.json in this directory (or path via GOOGLE_APPLICATION_CREDENTIALS)
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Google Drive API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request as GoogleRequest
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = os.getenv(
    "GDRIVE_CREDENTIALS_PATH",
    str(CURRENT_DIR / "credentials.json"),
)
TOKENS_PATH = os.getenv(
    "GDRIVE_TOKENS_PATH",
    str(CURRENT_DIR / "oauth_tokens.json"),
)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Default folder for uploads (user can override via tool param)
DEFAULT_FOLDER_ID = os.getenv("GDRIVE_DEFAULT_FOLDER_ID", "")
# Default PDF output dir (relative to project root or absolute)
DEFAULT_OUTPUT_DIR = os.getenv("GDRIVE_OUTPUT_DIR", "output/pdfs")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP("Google Drive PDF Upload")

# ---------------------------------------------------------------------------
# Google Drive OAuth helper
# ---------------------------------------------------------------------------


class DriveAuth:
    """Handles OAuth for Google Drive and provides authenticated service."""

    def __init__(
        self,
        credentials_path: str = CREDENTIALS_PATH,
        tokens_path: str = TOKENS_PATH,
    ):
        self.credentials_path = credentials_path
        self.tokens_path = tokens_path
        self._service = None

    def get_oauth_url(self) -> str:
        """Generate OAuth authorization URL."""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Google OAuth credentials not found at {self.credentials_path}. "
                "Download from Google Cloud Console and save as credentials.json"
            )
        flow = Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=SCOPES,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        return auth_url

    def exchange_code_for_token(self, auth_code: str) -> bool:
        """Exchange authorization code for tokens."""
        flow = Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=SCOPES,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
        )
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes) if creds.scopes else SCOPES,
        }
        with open(self.tokens_path, "w") as f:
            json.dump(token_data, f, indent=2)
        self._service = None
        return True

    def get_service(self):
        """Get authenticated Drive API service."""
        if self._service:
            return self._service
        if not os.path.exists(self.tokens_path):
            raise RuntimeError(
                "Not authenticated. Run setup_oauth then complete_oauth with the auth code."
            )
        with open(self.tokens_path, "r") as f:
            token_info = json.load(f)
        creds = Credentials(
            token_info["token"],
            refresh_token=token_info.get("refresh_token"),
            token_uri=token_info["token_uri"],
            client_id=token_info["client_id"],
            client_secret=token_info["client_secret"],
            scopes=token_info.get("scopes", SCOPES),
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
            token_info["token"] = creds.token
            with open(self.tokens_path, "w") as f:
                json.dump(token_info, f, indent=2)
        self._service = build("drive", "v3", credentials=creds)
        return self._service


drive_auth = DriveAuth() if DRIVE_AVAILABLE else None

# ---------------------------------------------------------------------------
# OAuth tools
# ---------------------------------------------------------------------------


@mcp.tool()
def setup_oauth() -> str:
    """
    Get the OAuth authorization URL to authenticate with Google Drive.
    Open the returned URL in a browser, sign in, then use complete_oauth with the code.
    """
    if not DRIVE_AVAILABLE:
        return json.dumps({"success": False, "error": "Google Drive API not installed"})
    try:
        url = drive_auth.get_oauth_url()
        return json.dumps({"success": True, "auth_url": url}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
def complete_oauth(auth_code: str) -> str:
    """
    Complete OAuth by exchanging the authorization code from the OAuth URL.
    Paste the code you received after authorizing in the browser.
    """
    if not DRIVE_AVAILABLE:
        return json.dumps({"success": False, "error": "Google Drive API not installed"})
    try:
        drive_auth.exchange_code_for_token(auth_code.strip())
        return json.dumps({"success": True, "message": "Authentication complete"}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
def check_auth_status() -> str:
    """Check if Google Drive is authenticated and ready for uploads."""
    if not DRIVE_AVAILABLE:
        return json.dumps({"success": False, "error": "Google Drive API not installed"}, indent=2)
    try:
        drive_auth.get_service()
        return json.dumps({"success": True, "authenticated": True}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "authenticated": False, "error": str(e)}, indent=2)

# ---------------------------------------------------------------------------
# PDF Upload tool
# ---------------------------------------------------------------------------


@mcp.tool()
def upload_pdf_to_drive(
    file_path: str,
    folder_id: Optional[str] = None,
    file_name: Optional[str] = None,
) -> str:
    """
    Upload a PDF file to a Google Drive folder.

    Args:
        file_path: Full path to the PDF file on disk (e.g., output/pdfs/AdBoard_product_20260131.pdf).
        folder_id: Google Drive folder ID to upload to. Get from folder URL: drive.google.com/drive/folders/FOLDER_ID.
                   If not provided, uses GDRIVE_DEFAULT_FOLDER_ID from environment.
        file_name: Optional custom name for the file in Drive. Defaults to the original filename.

    Returns:
        JSON with success status, file_id, and web_view_link if successful.
    """
    if not DRIVE_AVAILABLE:
        return json.dumps({"success": False, "error": "Google Drive API not installed"})
    path = Path(file_path)
    if not path.exists():
        return json.dumps({"success": False, "error": f"File not found: {file_path}"})
    if path.suffix.lower() != ".pdf":
        return json.dumps({"success": False, "error": "File must be a PDF"})
    target_folder = folder_id or DEFAULT_FOLDER_ID
    if not target_folder:
        return json.dumps({
            "success": False,
            "error": "No folder_id provided. Pass folder_id or set GDRIVE_DEFAULT_FOLDER_ID",
        })
    try:
        return _do_upload(str(path), target_folder, file_name)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def _do_upload(file_path: str, folder_id: str, file_name: Optional[str] = None) -> str:
    """Internal: perform the actual upload. Assumes DRIVE_AVAILABLE and authenticated."""
    """Internal: perform the actual upload."""
    path = Path(file_path)
    name = file_name or path.name
    metadata = {"name": name, "mimeType": "application/pdf", "parents": [folder_id]}
    media = MediaFileUpload(str(path), mimetype="application/pdf", resumable=True)
    service = drive_auth.get_service()
    file = service.files().create(
        body=metadata, media_body=media, fields="id, name, webViewLink"
    ).execute()
    return json.dumps({
        "success": True,
        "file_id": file.get("id"),
        "file_name": file.get("name"),
        "web_view_link": file.get("webViewLink", ""),
    }, indent=2)


@mcp.tool()
def upload_latest_pdf_from_output(
    folder_id: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """
    Upload the most recently created PDF from the output directory.
    Useful after the PDF Builder agent produces a new PDF.

    Args:
        folder_id: Google Drive folder ID. Optional if GDRIVE_DEFAULT_FOLDER_ID is set.
        output_dir: Path to folder containing PDFs (default: GDRIVE_OUTPUT_DIR or output/pdfs).

    Returns:
        JSON with success status and file details.
    """
    if not DRIVE_AVAILABLE:
        return json.dumps({"success": False, "error": "Google Drive API not installed"}, indent=2)
    target_folder = folder_id or DEFAULT_FOLDER_ID
    if not target_folder:
        return json.dumps({
            "success": False,
            "error": "No folder_id. Pass folder_id or set GDRIVE_DEFAULT_FOLDER_ID",
        })
    out_dir = output_dir or DEFAULT_OUTPUT_DIR
    dir_path = Path(out_dir)
    if not dir_path.exists():
        return json.dumps({"success": False, "error": f"Directory not found: {out_dir}"})
    pdfs = list(dir_path.glob("*.pdf"))
    if not pdfs:
        return json.dumps({"success": False, "error": f"No PDF files in {out_dir}"})
    latest = max(pdfs, key=lambda p: p.stat().st_mtime)
    try:
        return _do_upload(str(latest), target_folder, latest.name)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main():
    """Run as standalone FastMCP server (stdio transport for Agentverse)."""
    port = int(os.getenv("GDRIVE_MCP_PORT", "8082"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
