"""
AdBoard AI Orchestrator Agent

Main entry point for ASI:One and Agentverse. Implements Chat Protocol
for discoverability and routes user requests to the appropriate pipeline.

Deploy this agent to Agentverse for the hackathon.
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

import requests

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    Resource,
    ResourceContent,
    TextContent,
    chat_protocol_spec,
)
from uagents_core.utils.registration import (
    RegistrationRequestCredentials,
    register_chat_agent,
)

load_dotenv()

# Agentverse External Storage for image/video previews
AGENTVERSE_URL = (os.getenv("AGENTVERSE_URL") or "https://agentverse.ai").rstrip("/")
STORAGE_URL = f"{AGENTVERSE_URL}/v1/storage"

ExternalStorage = None
external_storage = None

try:
    from uagents_core.storage import ExternalStorage as _ES

    ExternalStorage = _ES
except ImportError:
    pass

# Configuration
AGENT_NAME = "AdBoardAI"
SEED_PHRASE = os.getenv("AGENT_SEED_PHRASE", "adboard-ai-hackathon-seed-2026")
AGENTVERSE_KEY = os.getenv("AGENTVERSE_API_KEY")
AGENT_PORT = int(os.getenv("AGENT_PORT", "8000"))

# Use proxy instead of mailbox - proxy handles real-time messages better for chat
USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"

# Initialize the agent - use testnet for Agentverse compatibility
if USE_PROXY:
    agent = Agent(
        name=AGENT_NAME,
        seed=SEED_PHRASE,
        port=AGENT_PORT,
        proxy=True,
        handle_messages_concurrently=True,
        network="testnet",
    )
else:
    agent = Agent(
        name=AGENT_NAME,
        seed=SEED_PHRASE,
        port=AGENT_PORT,
        mailbox=True,
        handle_messages_concurrently=True,
        network="testnet",
    )

# Chat protocol
protocol = Protocol(spec=chat_protocol_spec)

# README for Agentverse listing
README = """# AdBoard AI - Full Ad Campaign Generator for Small Businesses

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

I create three deliverables for you:

1. **Storyboard video** — A silent concept video for development and pitching. Shows the visual flow so you can hire a crew and film the real ad.

2. **Viral video** — A ready-to-post short clip with music and voiceover, optimized for TikTok and Reels. Post it while you develop the full production.

3. **Campaign PDF** — Full production brief with research, script, cost estimates, filming locations, and everything you need to brief actors and producers.

Tell me about your business and I'll research your competitors, write the script, generate both videos, and deliver the complete package.

## How to Use

- "Create an ad campaign for my taco truck"
- "I need ads for my coffee shop in Boston"
- "Make a viral video and storyboard for my fitness studio"

## What You Get

- Storyboard concept video (for development and client approval)
- Full PDF package (strategy, budget, locations, hiring guide)
- Viral-ready short-form video (TikTok/Reels)
- Cost estimates and filming recommendations

Built at Hack@Brown 2026 for the Fetch.AI track.
"""


def create_response(text: str, end_session: bool = False) -> ChatMessage:
    """Helper to create a ChatMessage response."""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(tz=None),  # Use local time, protocol handles conversion
        msg_id=uuid4(),
        content=content,
    )


# ASI:One relays messages from Agentverse chat - we need to process these
ASI_ONE_ADDRESS = "agent1qgdsv5ft53hjhte3z96ejzhjctjcgwzjkvjfkn8edvs6vev2y9ktw26d6tu"

# TEST MODE: Set to True to skip pipeline and just test Agentverse communication
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# MOCK MODE: Set to True to return realistic mock data instead of running pipeline
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# Phrases that indicate automated/intro messages (not real user requests)
AUTOMATED_PHRASES = [
    "hi! i'm asi:one",
    "i'm here to help",
    "what can i do for you",
    "how can i assist",
    "hello! i am",
    "i can help you with",
]


@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages."""

    # Send acknowledgement first (required by protocol)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    # Extract text from message
    user_text = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            user_text += item.text

    user_text = user_text.strip()
    ctx.logger.info(f"Received from {sender}: {user_text[:100]}")

    # Ignore empty messages
    if not user_text:
        ctx.logger.info("Ignoring empty message")
        return

    # Filter out automated intro/greeting messages (but not real relayed requests)
    text_lower = user_text.lower()
    if any(phrase in text_lower for phrase in AUTOMATED_PHRASES):
        ctx.logger.info(f"Ignoring automated intro message")
        return

    # Clean up ASI:One relayed messages - they often start with @agent_address
    # Strip the @mention prefix if present
    if user_text.startswith("@agent"):
        # Find the end of the @mention (space or end of string)
        space_idx = user_text.find(" ")
        if space_idx > 0:
            user_text = user_text[space_idx:].strip()
            ctx.logger.info(f"Cleaned message (removed @mention): {user_text[:100]}")

    # TEST MODE: Quick response without running pipeline
    # Using exact same pattern as test_asi_simple.py (which works)
    if TEST_MODE:
        ctx.logger.info("TEST MODE: Sending quick test response")
        response_text = f"✅ Echo: {user_text}\n\n🤖 AdBoard AI Test Mode\n📬 Sender: {sender[:20]}..."

        response_msg = ChatMessage(
            timestamp=datetime.now(),
            msg_id=uuid4(),
            content=[TextContent(type="text", text=response_text)],
        )

        ctx.logger.info(f"📤 Sending response to: {sender}")

        try:
            await ctx.send(sender, response_msg)
            ctx.logger.info("✅ Response sent successfully!")
        except Exception as e:
            ctx.logger.error(f"❌ Failed to send response: {e}")
            import traceback

            ctx.logger.error(traceback.format_exc())
        return

    # MOCK MODE: Return realistic mock data without running pipeline
    if MOCK_MODE:
        ctx.logger.info("MOCK MODE: Returning realistic mock response")
        from agents.mock_response import MOCK_PIPELINE_RESULT

        # Send initial message
        await ctx.send(
            sender,
            create_response(
                "Running in mock mode so this will be quick. Here are your results."
            ),
        )

        # Format and send mock results
        formatted = format_results(MOCK_PIPELINE_RESULT, "storyboard_video")
        response_text = formatted["text"]
        ctx.logger.info(f"Sending mock response ({len(response_text)} chars)")

        try:
            await ctx.send(sender, create_response(response_text, end_session=True))
            ctx.logger.info("✅ Mock response sent successfully!")
        except Exception as e:
            ctx.logger.error(f"❌ Failed to send mock response: {e}")
        return

    # Import here to avoid circular imports
    from core.intent_extractor import extract_intent
    from core.pipeline import AdBoardPipeline

    try:
        # Extract intent from user message
        intent = extract_intent(user_text)
        ctx.logger.info(f"Extracted intent: {intent}")

        # Check if this is an ad-related request
        if not intent.get("is_ad_request"):
            await ctx.send(
                sender,
                create_response(
                    "I create full ad campaigns for small businesses. You get three deliverables: "
                    "a storyboard video for development, a viral video for TikTok and Reels, and a campaign PDF "
                    "with research, costs, and hiring guide. Just tell me about your business—like "
                    "'Create an ad for my taco truck' or 'I need ads for my coffee shop in Boston.'"
                ),
            )
            return

        # Check if we have all required info
        if not intent.get("ready"):
            missing = intent.get("missing", ["some details"])
            await ctx.send(
                sender,
                create_response(
                    f"Almost there! I still need: {', '.join(missing)}\n\n"
                    "Please provide the missing info."
                ),
            )
            return

        # We have everything - run the pipeline
        output_type = intent.get("output_type", "full_campaign")

        # Quick mode: skip research for faster testing (via "quick test" or QUICK_FULL env)
        if os.getenv("QUICK_FULL", "").lower() == "true":
            output_type = "quick_full"
        elif (
            "quick test" in user_text.lower()
            or "test without research" in user_text.lower()
        ):
            output_type = "quick_full"

        # Normalize output type
        if output_type in ("video", "full"):
            output_type = "full_campaign"

        product = intent.get("product", "product")
        duration = intent.get("duration", 30)
        tone = intent.get("tone", "professional")

        # Natural-language kick-off (no emojis)
        city_part = f" in {intent.get('city')}" if intent.get("city") else ""
        has_viral = output_type == "full_campaign"
        if has_viral:
            kickoff = (
                f"Got it. I'm putting together your ad campaign for {product}{city_part}—"
                "a silent storyboard video for development, a ready-to-post viral video, and the full campaign PDF. "
                "This takes several minutes. I'll check in as I go."
            )
        else:
            kickoff = (
                f"Got it. I'm putting together your storyboard package for {product}{city_part}—"
                "the concept video and campaign PDF. This takes a few minutes. I'll check in as I go."
            )
        await ctx.send(sender, create_response(kickoff))

        # Progress callback for check-in messages
        async def on_progress(step_name: str, message: str):
            try:
                await ctx.send(sender, create_response(message))
            except Exception as e:
                ctx.logger.warning(f"Could not send progress: {e}")

        # Run the pipeline
        pipeline = AdBoardPipeline(
            product=product,
            industry=intent.get("industry", "general"),
            output_type=output_type,
            duration=duration,
            tone=intent.get("tone", "professional"),
            city=intent.get("city", ""),
        )

        result = await pipeline.run(progress_callback=on_progress)

        # Format and send results
        ctx.logger.info("Pipeline completed, sending results back to Agentverse...")

        if result.get("success"):
            formatted = format_results(result, output_type)
            response_text = formatted["text"]
            video_url = formatted.get("video_url")
            pdf_url = formatted.get("pdf_url")
            video_path = formatted.get("video_path")

            # Build ASI:One preview: thumbnail + links (critical for UX)
            thumbnail_uri = None
            ctx.logger.info(
                f"Preview check: video_path={video_path}, video_url={video_url is not None}, pdf_url={pdf_url is not None}"
            )

            thumb_bytes = None
            # Step 1: Extract thumbnail from storyboard video
            if video_path and os.path.exists(video_path):
                ctx.logger.info(f"Extracting thumbnail from: {video_path}")
                thumb_bytes = extract_video_thumbnail(video_path)
                if thumb_bytes:
                    ctx.logger.info(f"Thumbnail extracted ({len(thumb_bytes)} bytes)")
            elif video_path:
                ctx.logger.warning(f"Video path does not exist: {video_path}")

            # Step 2: Fallback to first storyboard frame if no video thumbnail
            pipeline_results = result.get("results", {})
            if not thumb_bytes and "image_generator" in pipeline_results:
                frames = pipeline_results["image_generator"].get("frames", [])
                for frame in frames:
                    frame_path = frame.get("path")
                    if frame_path and os.path.exists(frame_path):
                        try:
                            with open(frame_path, "rb") as f:
                                thumb_bytes = f.read()
                            ctx.logger.info(
                                f"Using storyboard frame as preview: {frame_path}"
                            )
                            break
                        except Exception as e:
                            ctx.logger.warning(f"Could not read frame: {e}")

            # Step 3: Upload thumbnail — Agentverse first, then Drive/tmpfiles fallback
            if thumb_bytes:
                thumb_bytes = compress_thumbnail(thumb_bytes)
                ctx.logger.info(f"Thumbnail compressed to {len(thumb_bytes)} bytes")
                thumbnail_uri, _ = upload_to_agentverse_storage(
                    thumb_bytes, "video_preview.jpg", "image/jpeg", sender
                )
                if not thumbnail_uri:
                    ctx.logger.warning(
                        "Agentverse storage failed, trying Drive/tmpfiles..."
                    )
                    thumbnail_uri = upload_thumbnail_fallback(
                        thumb_bytes, "preview.jpg"
                    )
                    if thumbnail_uri:
                        ctx.logger.info(
                            f"Preview uploaded to fallback: {thumbnail_uri[:60]}..."
                        )

            ctx.logger.info(
                f"Sending success response ({len(response_text)} chars), thumbnail_uri={thumbnail_uri is not None}"
            )
            try:
                if thumbnail_uri or (
                    video_url
                    and (
                        "View Storyboard" in response_text
                        or "View Viral" in response_text
                        or "View Full" in response_text
                    )
                ):
                    # Use image/jpeg when fallback URL (our compressed thumb is jpeg)
                    thumb_mime = (
                        "image/jpeg"
                        if (thumbnail_uri and thumbnail_uri.startswith("http"))
                        else "image/png"
                    )
                    msg = create_preview_response(
                        thumbnail_uri=thumbnail_uri,
                        video_url=video_url,
                        pdf_url=pdf_url,
                        text_summary=response_text,
                        end_session=True,
                        thumbnail_mime=thumb_mime,
                    )
                    await ctx.send(sender, msg)
                else:
                    await ctx.send(
                        sender, create_response(response_text, end_session=True)
                    )
                ctx.logger.info("Response sent successfully!")
            except Exception as send_err:
                ctx.logger.error(f"Failed to send response: {send_err}")
                try:
                    await ctx.send(
                        sender, create_response(response_text, end_session=True)
                    )
                except Exception as e2:
                    ctx.logger.error(f"Failed to send fallback: {e2}")
        else:
            ctx.logger.info(f"Pipeline failed: {result.get('error')}")
            await ctx.send(
                sender,
                create_response(
                    f"Sorry, something went wrong: {result.get('error', 'Unknown error')}\n\n"
                    "Please try again or simplify your request.",
                    end_session=True,
                ),
            )

    except Exception as e:
        ctx.logger.error(f"Error processing request: {e}")
        import traceback

        ctx.logger.error(traceback.format_exc())
        try:
            await ctx.send(
                sender,
                create_response(
                    f"Sorry, I encountered an error: {str(e)}\n\nPlease try again.",
                    end_session=True,
                ),
            )
        except Exception as send_err:
            ctx.logger.error(f"Failed to send error response: {send_err}")


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgements (required by protocol)."""
    ctx.logger.debug(f"Received ack from {sender} for {msg.acknowledged_msg_id}")


def compress_thumbnail(thumb_bytes: bytes, max_bytes: int = 500_000) -> bytes:
    """Compress thumbnail for Agentverse upload.
    Target: under 500 KB (500,000 bytes) by default.
    """
    try:
        import cv2
        import numpy as np

        arr = np.frombuffer(thumb_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return thumb_bytes

        h, w = img.shape[:2]

        # Progressively reduce size and quality until under max_bytes
        # Start with reasonable dimensions for a thumbnail
        target_widths = [640, 480, 320, 240, 160]
        qualities = [85, 70, 50, 30, 20]

        for target_w in target_widths:
            if w > target_w:
                scale = target_w / w
                new_w = int(w * scale)
                new_h = int(h * scale)
                resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            else:
                resized = img

            for quality in qualities:
                _, jpg = cv2.imencode(
                    ".jpg", resized, [cv2.IMWRITE_JPEG_QUALITY, quality]
                )
                out = jpg.tobytes()
                if len(out) < max_bytes:
                    print(
                        f"  Thumbnail: {resized.shape[1]}x{resized.shape[0]} q{quality} = {len(out)} bytes ({len(out) / 1000:.1f} KB)"
                    )
                    return out

        # Last resort: very small
        resized = cv2.resize(img, (160, int(160 * h / w)), interpolation=cv2.INTER_AREA)
        _, jpg = cv2.imencode(".jpg", resized, [cv2.IMWRITE_JPEG_QUALITY, 10])
        out = jpg.tobytes()
        print(
            f"  Thumbnail: {resized.shape[1]}x{resized.shape[0]} q10 = {len(out)} bytes ({len(out) / 1000:.1f} KB)"
        )
        return out
    except Exception as e:
        print(f"  ⚠️ Thumbnail compress failed: {e}")
    return thumb_bytes


def upload_thumbnail_fallback(
    thumb_bytes: bytes, name: str = "preview.jpg"
) -> str | None:
    """Upload thumbnail to Drive or tmpfiles when Agentverse fails. Returns public URL."""
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(thumb_bytes)
            tmp_path = f.name
        try:
            url = upload_file(tmp_path)
            return url
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    except Exception as e:
        print(f"  ⚠️ Thumbnail fallback upload failed: {e}")
    return None


def extract_video_thumbnail(video_path: str) -> bytes | None:
    """Extract a non-black frame from video as PNG bytes for preview.

    Tries multiple frames since the first frame is often black (fade-in).
    Skips frames that are mostly black (mean brightness < 15).

    Args:
        video_path: Path to video file

    Returns:
        PNG image bytes, or None if extraction fails
    """
    try:
        import cv2
        import numpy as np

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"⚠️ Could not open video for thumbnail: {video_path}")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1)
        frame_indices = [
            0,
            1,
            2,
            3,
            max(1, int(fps)),
        ]  # Try frame 0, 1, 2, 3, ~1 sec in

        best_frame = None
        best_brightness = 0

        for idx in frame_indices:
            if idx >= total_frames:
                continue
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            # Mean brightness (skip black frames)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = float(np.mean(gray))
            if brightness > best_brightness and brightness > 15:
                best_frame = frame
                best_brightness = brightness
            elif best_frame is None:
                best_frame = frame  # Fallback to first readable frame

        cap.release()
        if best_frame is None:
            print("⚠️ Could not read any frame from video")
            return None

        _, png = cv2.imencode(".png", best_frame)
        print("Extracted thumbnail from video")
        return png.tobytes()
    except ImportError:
        print("⚠️ opencv-python not installed, skipping thumbnail extraction")
        return None
    except Exception as e:
        print(f"⚠️ Thumbnail extraction failed: {e}")
        return None


def init_external_storage():
    """Initialize Agentverse External Storage if API key is available."""
    global external_storage
    if external_storage is not None:
        return external_storage
    if AGENTVERSE_KEY and ExternalStorage is not None:
        try:
            external_storage = ExternalStorage(
                api_token=AGENTVERSE_KEY, storage_url=STORAGE_URL
            )
            print(f"✅ Agentverse External Storage initialized")
            return external_storage
        except Exception as e:
            print(f"⚠️ Failed to init external storage: {e}")
    return None


def upload_to_agentverse_storage(
    content: bytes, name: str, mime_type: str, sender: str
) -> tuple[str | None, str | None]:
    """Upload content to Agentverse External Storage (max 10 attempts).

    Args:
        content: File bytes
        name: Asset name
        mime_type: MIME type (e.g., "image/png", "video/mp4")
        sender: Agent address to grant permissions

    Returns:
        Tuple of (asset_uri, watch_url) or (None, None) if failed
    """
    import time

    storage = init_external_storage()
    if storage is None:
        return None, None

    for attempt in range(1, 11):
        try:
            time.sleep(4)
            asset_id = storage.create_asset(
                name=name,
                content=content,
                mime_type=mime_type,
            )
            storage.set_permissions(asset_id=asset_id, agent_address=sender)
            asset_uri = f"agent-storage://{STORAGE_URL}/{asset_id}"
            watch_url = f"{AGENTVERSE_URL}/v1/storage/assets/{asset_id}"
            print(f"✅ Uploaded to Agentverse storage: {asset_id} (attempt {attempt})")
            return asset_uri, watch_url
        except Exception as e:
            print(f"⚠️ Agentverse upload attempt {attempt}/10 failed, retrying...")

    print("⚠️ Agentverse storage failed after 10 attempts, falling back to Google Drive")
    return None, None


def create_preview_response(
    thumbnail_uri: str | None,
    video_url: str | None,
    pdf_url: str | None,
    text_summary: str,
    end_session: bool = True,
    thumbnail_mime: str = "image/png",
) -> ChatMessage:
    """Create a ChatMessage with image preview and links.

    Args:
        thumbnail_uri: URI for thumbnail (agent-storage:// or https://)
        video_url: Public URL to storyboard video
        pdf_url: Public URL to download PDF
        text_summary: Text content (includes all three links)
        end_session: Whether to end the session
        thumbnail_mime: MIME type for thumbnail (image/png or image/jpeg)
    """
    from datetime import timezone

    content = []

    # Add thumbnail image as ResourceContent (displays inline in ASI:One)
    if thumbnail_uri:
        content.append(
            ResourceContent(
                type="resource",
                resource_id=uuid4(),
                resource=Resource(
                    uri=thumbnail_uri,
                    metadata={
                        "mime_type": thumbnail_mime,
                        "role": "Video Preview",
                    },
                ),
            )
        )

    # Add text with links
    content.append(TextContent(type="text", text=text_summary))

    if end_session:
        content.append(EndSessionContent(type="end-session"))

    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )


def upload_file(file_path: str) -> str | None:
    """Upload file to Google Drive (preferred) or tmpfiles.org fallback.

    Uses Google Drive when GDRIVE_DEFAULT_FOLDER_ID is set and OAuth is complete.
    Otherwise falls back to tmpfiles.org (1hr expiry).

    Args:
        file_path: Local path to file (video, PDF, etc.)

    Returns:
        Public URL to file, or None if upload failed
    """
    # Try Google Drive first (permanent hosting)
    if os.getenv("GDRIVE_DEFAULT_FOLDER_ID"):
        try:
            from utils.gdrive_upload import upload_file_to_drive

            url = upload_file_to_drive(file_path)
            if url:
                return url
        except Exception as e:
            print(f"⚠️ Drive upload failed, falling back to tmpfiles: {e}")

    # Fallback to tmpfiles.org
    return upload_file_to_tmpfiles(file_path)


def upload_file_to_tmpfiles(file_path: str) -> str | None:
    """Upload any file to tmpfiles.org and return public URL.

    tmpfiles.org is a free temporary file hosting service.
    Files are kept for ~1 hour (sufficient for demos).

    Args:
        file_path: Local path to file (video, PDF, image, etc.)

    Returns:
        Public URL to file, or None if upload failed
    """
    try:
        import json
        import subprocess

        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            return None

        filename = os.path.basename(file_path)
        print(f"📤 Uploading {filename} to tmpfiles.org...")

        # Use curl command - more reliable than requests for file uploads
        result = subprocess.run(
            ["curl", "-F", f"file=@{file_path}", "https://tmpfiles.org/api/v1/upload"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            # tmpfiles.org returns JSON like: {"status":"success","data":{"url":"https://tmpfiles.org/xyz/file.mp4"}}
            data = json.loads(result.stdout)
            if data.get("status") == "success":
                url = data["data"]["url"]
                # Convert to direct download URL: tmpfiles.org/ID/file → tmpfiles.org/dl/ID/file
                direct_url = url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                print(f"✅ File uploaded successfully: {direct_url}")
                return direct_url

        print(f"⚠️ Upload failed: {result.stderr}")
        return None

    except Exception as e:
        print(f"⚠️ Upload error: {e}")
        return None


def format_results(result: dict, output_type: str) -> dict:
    """Format pipeline results. Returns storyboard video, viral video, and PDF links."""

    results = result.get("results", {})
    output_lines = []
    storyboard_url = None
    viral_url = None
    pdf_url = None
    video_path = None  # For thumbnail (prefer storyboard)

    # === STORYBOARD VIDEO (silent concept video) ===
    if "video_assembly" in results:
        video_data = results["video_assembly"]
        video_path = video_data.get("final_video_path")
        if video_data.get("video_url"):
            storyboard_url = video_data["video_url"]
        elif video_path and os.path.exists(video_path):
            print("\nUploading storyboard video...")
            storyboard_url = upload_file(video_path)

    # === VIRAL VIDEO (ready-to-post with audio) ===
    if "viral_video_assembler" in results:
        viral_data = results["viral_video_assembler"]
        viral_path = viral_data.get("final_video_path")
        if viral_path and os.path.exists(viral_path):
            print("\nUploading viral video...")
            viral_url = upload_file(viral_path)

    # === PDF ===
    pdf_data = results.get("pdf_export") or results.get("pdf_builder")
    if pdf_data:
        if pdf_data.get("pdf_url"):
            pdf_url = pdf_data["pdf_url"]
        else:
            pdf_path = pdf_data.get("pdf_path")
            if pdf_path and os.path.exists(pdf_path):
                print("\nUploading PDF...")
                pdf_url = upload_file(pdf_path)

    # Build response text — all three deliverables with clear labels
    if storyboard_url:
        output_lines.append(f"View Storyboard Video Here: {storyboard_url}")
    if viral_url:
        output_lines.append(f"View Viral Video Here: {viral_url}")
    if pdf_url:
        output_lines.append(f"View Full Analysis PDF: {pdf_url}")

    output_text = (
        "\n\n".join(output_lines)
        if output_lines
        else "Your campaign package is ready. Check the output folder for files."
    )

    return {
        "text": output_text,
        "video_url": storyboard_url,
        "viral_url": viral_url,
        "pdf_url": pdf_url,
        "video_path": str(video_path) if video_path else None,
    }


# Include the chat protocol
agent.include(protocol, publish_manifest=True)


@agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Initialize agent and register with Agentverse on startup."""
    ctx.logger.info(f"AdBoard AI starting: {ctx.agent.name}")
    ctx.logger.info(f"Agent address: {ctx.agent.address}")

    # Print address prominently for easy copy/paste
    print("\n" + "=" * 60)
    print("  AdBoard AI - Agent Address")
    print("=" * 60)
    print(f"  {ctx.agent.address}")
    print("=" * 60)
    print("  To interact on Agentverse, search for this address")
    print("  or find 'AdBoard AI' in the agent directory.")
    print("=" * 60 + "\n")

    # Register with Agentverse
    if AGENTVERSE_KEY and SEED_PHRASE:
        try:
            # Get the endpoint URL
            endpoint_url = None
            if hasattr(agent, "_endpoints") and agent._endpoints:
                endpoint_url = agent._endpoints[0].url
            else:
                endpoint_url = f"http://localhost:{AGENT_PORT}"

            ctx.logger.info(f"Registering with Agentverse at endpoint: {endpoint_url}")

            register_chat_agent(
                AGENT_NAME,
                endpoint_url,
                active=True,
                credentials=RegistrationRequestCredentials(
                    agentverse_api_key=AGENTVERSE_KEY,
                    agent_seed_phrase=SEED_PHRASE,
                ),
                readme=README,
                description="Creates full ad campaigns for small businesses: (1) storyboard video for development, (2) viral video for TikTok/Reels, and (3) campaign PDF with research, costs, and hiring guide.",
            )
            ctx.logger.info("Successfully registered with Agentverse!")

        except Exception as e:
            ctx.logger.error(f"Failed to register with Agentverse: {e}")
    else:
        missing = []
        if not AGENTVERSE_KEY:
            missing.append("AGENTVERSE_API_KEY")
        if not SEED_PHRASE:
            missing.append("AGENT_SEED_PHRASE")
        ctx.logger.warning(
            f"Skipping Agentverse registration - missing: {', '.join(missing)}"
        )

    ctx.logger.info("AdBoard AI is ready!")


if __name__ == "__main__":
    agent.run()
