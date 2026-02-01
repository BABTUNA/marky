#!/usr/bin/env python3
"""
Image Preview Test Agent — ASI:One / Agentverse

Tests displaying an image in ASI:One chat using the Chat Protocol ResourceContent.
Uses a sample image in this folder (image_testing), or creates one if missing.

Usage:
  1. Set AGENTVERSE_API_KEY in .env (project root or this folder).
  2. Run: python preview_agent.py
  3. Connect via Agentverse mailbox, then Chat with Agent (or find via ASI:One).
  4. Send any message; the agent replies with the sample image as a resource.

Requires: uagents, uagents-core (pip install uagents uagents-core)
"""

import os
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

# Image file in this folder (prefer fetch.png if present)
IMAGE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = IMAGE_DIR / "fetch.png" if (IMAGE_DIR / "fetch.png").exists() else IMAGE_DIR / "sample.png"
IMAGE_FILENAME = IMAGE_PATH.name

# Agentverse External Storage
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


def ensure_sample_image() -> bool:
    """Create sample.png with PIL if missing (only used when fetch.png is not present)."""
    if IMAGE_PATH.exists():
        return True
    try:
        from PIL import Image, ImageDraw, ImageFont
        w, h = 400, 200
        img = Image.new("RGB", (w, h), color=(70, 130, 180))
        draw = ImageDraw.Draw(img)
        text = "ASI:One Image Test"
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((w - tw) // 2, (h - th) // 2), text, fill="white", font=font)
        img.save(IMAGE_PATH, "PNG")
        return True
    except Exception:
        return False


# -----------------------------------------------------------------------------
# Agent
# -----------------------------------------------------------------------------

AGENT_NAME = os.getenv("IMAGE_PREVIEW_AGENT_NAME", "Image Preview Test Agent")
AGENT_SEED = os.getenv("IMAGE_PREVIEW_AGENT_SEED", "image-preview-test-agent-seed")
AGENT_PORT = int(os.getenv("IMAGE_PREVIEW_AGENT_PORT", "8011"))

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


def create_image_resource_chat(asset_id: str, asset_uri: str) -> ChatMessage:
    watch_url = f"{AGENTVERSE_URL}/v1/storage/assets/{asset_id}"
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[
            ResourceContent(
                type="resource",
                resource_id=uuid4(),
                resource=Resource(
                    uri=asset_uri,
                    metadata={
                        "mime_type": "image/png",
                        "role": "View image",
                    },
                ),
            ),
            TextContent(
                type="text",
                text=f"Sample image (from image_testing folder). Click to open: {watch_url}",
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

    if not ensure_sample_image():
        await ctx.send(
            sender,
            create_text_chat(
                f"Could not create sample image. Add {IMAGE_FILENAME} to image_testing/ or install Pillow.",
                end_session=True,
            ),
        )
        return

    if not IMAGE_PATH.exists():
        await ctx.send(
            sender,
            create_text_chat(f"Image not found: {IMAGE_PATH}", end_session=True),
        )
        return

    if external_storage is None:
        await ctx.send(
            sender,
            create_text_chat(
                "AGENTVERSE_API_KEY not set or uagents_core.storage not available.",
                end_session=True,
            ),
        )
        return

    try:
        image_bytes = IMAGE_PATH.read_bytes()
    except Exception as e:
        await ctx.send(
            sender,
            create_text_chat(f"Failed to read image: {e}", end_session=True),
        )
        return

    try:
        asset_id = external_storage.create_asset(
            name=f"preview-{uuid4().hex[:8]}",
            content=image_bytes,
            mime_type="image/png",
        )
        external_storage.set_permissions(asset_id=asset_id, agent_address=sender)
        asset_uri = f"agent-storage://{external_storage.storage_url}/{asset_id}"

        await ctx.send(sender, create_image_resource_chat(asset_id, asset_uri))
        ctx.logger.info(f"Sent image resource to {sender} (asset_id={asset_id})")
    except Exception as e:
        ctx.logger.exception("Upload failed")
        await ctx.send(
            sender,
            create_text_chat(f"Failed to upload image: {e}", end_session=True),
        )


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Ack from {sender} for {msg.acknowledged_msg_id}")


agent.include(chat_proto, publish_manifest=True)


@agent.on_event("startup")
async def startup(ctx: Context):
    ensure_sample_image()
    ctx.logger.info(f"Image Preview Test Agent running on port {AGENT_PORT}")
    ctx.logger.info(f"Image file: {IMAGE_PATH} (exists={IMAGE_PATH.exists()})")
    ctx.logger.info(f"Storage: {'configured' if external_storage else 'NOT configured'}")


if __name__ == "__main__":
    agent.run()
