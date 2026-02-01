#!/usr/bin/env python3
"""
Sample Video Preview Agent — ASI:One / Agentverse

Purely tests uploading a video preview to ASI:One using the Chat Protocol
ResourceContent. Uses the video in this folder (video_testing).

Usage:
  1. Set AGENTVERSE_API_KEY in .env (project root or this folder).
  2. Run: python preview_agent.py
  3. Connect via Agentverse mailbox, then Chat with Agent (or find via ASI:One).
  4. Send any message; the agent replies with the sample video as a resource.

Requires: uagents, uagents-core (pip install uagents uagents-core)
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

# Load .env from project root
_root = Path(__file__).resolve().parent.parent
_dotenv = _root / ".env"
if _dotenv.exists():
    from dotenv import load_dotenv
    load_dotenv(_dotenv)

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    ResourceContent,
    Resource,
    StartSessionContent,
    EndSessionContent,
)

# Video file in this folder
VIDEO_DIR = Path(__file__).resolve().parent
VIDEO_FILENAME = "YTDowncom_YouTube_3-Second-Video_Media_1O0yazhqaxs_001_1080p.mp4"
VIDEO_PATH = VIDEO_DIR / VIDEO_FILENAME

# Agentverse External Storage (for upload so ASI:One can fetch the video)
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")
AGENTVERSE_URL = (os.getenv("AGENTVERSE_URL") or "https://agentverse.ai").rstrip("/")
STORAGE_URL = f"{AGENTVERSE_URL}/v1/storage"

ExternalStorage = None
if AGENTVERSE_API_KEY:
    try:
        from uagents_core.storage import ExternalStorage as _ES
        ExternalStorage = _ES
    except ImportError:
        pass

if ExternalStorage is not None:
    external_storage = ExternalStorage(api_token=AGENTVERSE_API_KEY, storage_url=STORAGE_URL)
else:
    external_storage = None


# -----------------------------------------------------------------------------
# Agent
# -----------------------------------------------------------------------------

AGENT_NAME = os.getenv("VIDEO_PREVIEW_AGENT_NAME", "Video Preview Test Agent")
AGENT_SEED = os.getenv("VIDEO_PREVIEW_AGENT_SEED", "video-preview-test-agent-seed")
AGENT_PORT = int(os.getenv("VIDEO_PREVIEW_AGENT_PORT", "8010"))

agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    mailbox=True,
)

chat_proto = Protocol(spec=chat_protocol_spec)


def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )


def create_video_resource_chat(asset_id: str, asset_uri: str) -> ChatMessage:
    # Direct HTTPS link so ASI:One can show a clickable link (platform may not resolve agent-storage://)
    watch_url = f"{AGENTVERSE_URL.rstrip('/')}/v1/storage/assets/{asset_id}"
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[
            # Resource first so clients that support it can show inline preview
            ResourceContent(
                type="resource",
                resource_id=uuid4(),
                resource=Resource(
                    uri=asset_uri,
                    metadata={
                        "mime_type": "video/mp4",
                        "role": "Watch video",  # Friendlier link text on ASI:One
                    },
                ),
            ),
            # Explicit HTTPS link so there's always a clickable "Watch video" on the platform
            TextContent(
                type="text",
                text=f"Sample video (from video_testing folder). Click to watch: {watch_url}",
            ),
            EndSessionContent(type="end-session"),
        ],
    )


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        ),
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Start session from {sender}")
            continue
        if isinstance(item, TextContent):
            ctx.logger.info(f"Message from {sender}: {item.text}")
            break

    if not VIDEO_PATH.exists():
        await ctx.send(
            sender,
            create_text_chat(
                f"Video file not found: {VIDEO_PATH}. Add the sample MP4 to video_testing/.",
                end_session=True,
            ),
        )
        return

    if external_storage is None:
        await ctx.send(
            sender,
            create_text_chat(
                "AGENTVERSE_API_KEY not set or uagents_core.storage not available. "
                "Set AGENTVERSE_API_KEY in .env to upload video for preview.",
                end_session=True,
            ),
        )
        return

    try:
        video_bytes = VIDEO_PATH.read_bytes()
    except Exception as e:
        await ctx.send(
            sender,
            create_text_chat(f"Failed to read video file: {e}", end_session=True),
        )
        return

    try:
        asset_id = external_storage.create_asset(
            name=f"preview-{uuid4().hex[:8]}",
            content=video_bytes,
            mime_type="video/mp4",
        )
        external_storage.set_permissions(asset_id=asset_id, agent_address=sender)
        asset_uri = f"agent-storage://{external_storage.storage_url}/{asset_id}"

        await ctx.send(sender, create_video_resource_chat(asset_id, asset_uri))
        ctx.logger.info(f"Sent video resource to {sender} (asset_id={asset_id})")
    except Exception as e:
        ctx.logger.exception("Upload failed")
        await ctx.send(
            sender,
            create_text_chat(f"Failed to upload video to storage: {e}", end_session=True),
        )


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Ack from {sender} for {msg.acknowledged_msg_id}")


agent.include(chat_proto, publish_manifest=True)


@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Video Preview Test Agent running on port {AGENT_PORT}")
    ctx.logger.info(f"Video file: {VIDEO_PATH} (exists={VIDEO_PATH.exists()})")
    ctx.logger.info(f"Storage: {'configured' if external_storage else 'NOT configured (set AGENTVERSE_API_KEY)'}")


if __name__ == "__main__":
    agent.run()
