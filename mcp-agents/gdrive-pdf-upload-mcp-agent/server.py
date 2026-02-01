#!/usr/bin/env python3
"""
FastMCP Google Drive File Upload Server

Exposes tools to upload PDF, video, and other files to a Google Drive folder.
Used by AdBoard AI for hosting generated storyboard videos and PDF packages.

Based on: https://github.com/fetchai/innovation-lab-examples/tree/main/mcp-agents
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional

# Add project root for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from fastmcp import FastMCP
    except ImportError:
        FastMCP = None

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

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
DEFAULT_FOLDER_ID = os.getenv("GDRIVE_DEFAULT_FOLDER_ID", "")
DEFAULT_OUTPUT_DIR = os.getenv("GDRIVE_OUTPUT_DIR", str(PROJECT_ROOT / "output" / "pdfs"))

# Supported file extensions for upload
SUPPORTED_EXTENSIONS = {".pdf", ".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg", ".gif", ".mp3", ".wav"}
MIME_TYPES = {
    ".pdf": "application/pdf",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

mcp = FastMCP("Google Drive File Upload") if FastMCP else None


class DriveAuth:
    """Handles OAuth for Google Drive and provides authenticated service."""

    def __init__(self, credentials_path: str = CREDENTIALS_PATH, tokens_path: str = TOKENS_PATH):
        self.credentials_path = credentials_path
        self.tokens_path = tokens_path
        self._service = None

    def get_oauth_url(self) -> str:
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Google OAuth credentials not found at {self.credentials_path}. "
                "Download from Google Cloud Console and save as credentials.json"
            )
        flow = Flow.from_client_secrets_file(
            self.credentials_path, scopes=SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        return auth_url

    def exchange_code_for_token(self, auth_code: str) -> bool:
        flow = Flow.from_client_secrets_file(
            self.credentials_path, scopes=SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
        )
        flow.fetch_token(code=auth_code.strip())
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
        if self._service:
            return self._service
        if not os.path.exists(self.tokens_path):
            raise RuntimeError("Not authenticated. Run setup_oauth then complete_oauth with the auth code.")
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


def _do_upload(file_path: str, folder_id: str, file_name: Optional[str] = None) -> dict:
    """Perform the actual upload. Returns dict with success, file_id, web_view_link."""
    path = Path(file_path)
    name = file_name or path.name
    ext = path.suffix.lower()
    mime_type = MIME_TYPES.get(ext, "application/octet-stream")
    metadata = {"name": name, "mimeType": mime_type, "parents": [folder_id]}
    media = MediaFileUpload(str(path), mimetype=mime_type, resumable=True)
    service = drive_auth.get_service()
    file = service.files().create(
        body=metadata, media_body=media, fields="id, name, webViewLink, webContentLink"
    ).execute()
    return {
        "success": True,
        "file_id": file.get("id"),
        "file_name": file.get("name"),
        "web_view_link": file.get("webViewLink", "") or file.get("webContentLink", ""),
    }


# ---------------------------------------------------------------------------
# MCP Tools (only if FastMCP available)
# ---------------------------------------------------------------------------

if mcp:

    @mcp.tool()
    def setup_oauth() -> str:
        """Get the OAuth authorization URL to authenticate with Google Drive."""
        if not DRIVE_AVAILABLE:
            return json.dumps({"success": False, "error": "Google Drive API not installed"})
        try:
            url = drive_auth.get_oauth_url()
            return json.dumps({"success": True, "auth_url": url}, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    def complete_oauth(auth_code: str) -> str:
        """Complete OAuth by exchanging the authorization code."""
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

    @mcp.tool()
    def upload_file_to_drive(
        file_path: str,
        folder_id: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> str:
        """
        Upload a file (PDF, MP4, etc.) to a Google Drive folder.
        Supported: .pdf, .mp4, .mov, .webm, .png, .jpg, .gif, .mp3, .wav
        """
        if not DRIVE_AVAILABLE:
            return json.dumps({"success": False, "error": "Google Drive API not installed"})
        path = Path(file_path)
        if not path.exists():
            return json.dumps({"success": False, "error": f"File not found: {file_path}"})
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return json.dumps({
                "success": False,
                "error": f"Unsupported file type. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
            })
        target_folder = folder_id or DEFAULT_FOLDER_ID
        if not target_folder:
            return json.dumps({
                "success": False,
                "error": "No folder_id. Pass folder_id or set GDRIVE_DEFAULT_FOLDER_ID",
            })
        try:
            result = _do_upload(str(path), target_folder, file_name)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    def upload_pdf_to_drive(
        file_path: str,
        folder_id: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> str:
        """Upload a PDF file to a Google Drive folder."""
        return upload_file_to_drive(file_path, folder_id, file_name)

    @mcp.tool()
    def upload_latest_pdf_from_output(
        folder_id: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> str:
        """Upload the most recently created PDF from the output directory."""
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
            result = _do_upload(str(latest), target_folder, latest.name)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)


def main():
    """Run as standalone FastMCP server."""
    if not mcp:
        print("FastMCP not installed. pip install fastmcp")
        return
    port = int(os.getenv("GDRIVE_MCP_PORT", "8082"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
