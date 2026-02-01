"""
Google Drive File Upload

Uploads PDFs, videos, and other files to Google Drive.
Used by the orchestrator to host generated content (replacing tmpfiles.org).
Can also be used by the MCP agent for tool exposure.

Setup:
1. Create OAuth 2.0 credentials (Desktop app) in Google Cloud Console
2. Enable Google Drive API
3. Save credentials.json, run OAuth flow (setup_oauth + complete_oauth)
4. Set GDRIVE_DEFAULT_FOLDER_ID in .env
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

# Silence noisy Google API client logs
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

# MIME type mapping for common file types
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


def _get_mime_type(file_path: str) -> str:
    """Get MIME type from file extension."""
    ext = Path(file_path).suffix.lower()
    return MIME_TYPES.get(ext, "application/octet-stream")


def upload_file_to_drive(
    file_path: str,
    folder_id: Optional[str] = None,
    file_name: Optional[str] = None,
) -> Optional[str]:
    """
    Upload any file to Google Drive and return the shareable URL.

    Args:
        file_path: Full path to the file (PDF, MP4, etc.)
        folder_id: Google Drive folder ID. Defaults to GDRIVE_DEFAULT_FOLDER_ID.
        file_name: Optional custom name for the file in Drive.

    Returns:
        web_view_link (shareable URL) on success, None on failure.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import Flow
        from google.auth.transport.requests import Request as GoogleRequest
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print("⚠️ Google Drive API not installed. pip install google-auth-oauthlib google-api-python-client")
        return None

    path = Path(file_path)
    if not path.exists():
        print(f"⚠️ File not found: {file_path}")
        return None

    target_folder = folder_id or os.getenv("GDRIVE_DEFAULT_FOLDER_ID")
    if not target_folder:
        print("⚠️ No GDRIVE_DEFAULT_FOLDER_ID set. Skipping Drive upload.")
        return None

    credentials_path = os.getenv(
        "GDRIVE_CREDENTIALS_PATH",
        str(Path(__file__).resolve().parent.parent / "mcp-agents" / "gdrive-pdf-upload-mcp-agent" / "credentials.json"),
    )
    tokens_path = os.getenv(
        "GDRIVE_TOKENS_PATH",
        str(Path(__file__).resolve().parent.parent / "mcp-agents" / "gdrive-pdf-upload-mcp-agent" / "oauth_tokens.json"),
    )

    if not os.path.exists(tokens_path):
        print(f"⚠️ Google Drive not authenticated. Run OAuth flow first (see docs/MCP_AGENT.md)")
        return None

    try:
        with open(tokens_path, "r") as f:
            token_info = json.load(f)

        creds = Credentials(
            token_info["token"],
            refresh_token=token_info.get("refresh_token"),
            token_uri=token_info["token_uri"],
            client_id=token_info["client_id"],
            client_secret=token_info["client_secret"],
            scopes=token_info.get("scopes", ["https://www.googleapis.com/auth/drive.file"]),
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
            token_info["token"] = creds.token
            with open(tokens_path, "w") as f:
                json.dump(token_info, f, indent=2)

        service = build("drive", "v3", credentials=creds)

        name = file_name or path.name
        mime_type = _get_mime_type(str(path))
        metadata = {"name": name, "mimeType": mime_type, "parents": [target_folder]}
        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=True)

        file = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, name, webViewLink, webContentLink",
        ).execute()

        link = file.get("webViewLink") or file.get("webContentLink")
        if link:
            print(f"✅ Uploaded to Drive: {name} -> {link[:60]}...")
        return link

    except Exception as e:
        print(f"⚠️ Drive upload failed: {e}")
        return None
