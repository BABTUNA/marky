# ASI:One / Agentverse Video (and Image) Preview — Demo Code

Demo code for sending **video** or **image** previews in chat using the Agent Chat Protocol `ResourceContent`. The same pattern works for Agentverse Chat; ASI:One UI support for rendering media may still be rolling out.

---

## 1. Imports and helpers

```python
from datetime import datetime, timezone
from uuid import uuid4

from uagents import Context
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    ResourceContent,
    Resource,
    EndSessionContent,
)
```

---

## 2. Reply with a **public video URL** (no storage upload)

Use this when the video is already hosted at a public HTTPS URL (e.g. S3, CDN, Google Drive share link).

```python
def create_video_resource_chat(public_video_url: str, caption: str = "Video") -> ChatMessage:
    """Build a ChatMessage that carries a video for preview (public URL)."""
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=caption),
            ResourceContent(
                type="resource",
                resource_id=uuid4(),
                resource=Resource(
                    uri=public_video_url,
                    metadata={
                        "mime_type": "video/mp4",
                        "role": "generated-video",
                    },
                ),
            ),
        ],
    )


# Example: after your pipeline produces a video URL
# await ctx.send(sender, create_video_resource_chat(
#     "https://your-cdn.com/output/final.mp4",
#     caption="Here’s your ad video.",
# ))
```

---

## 3. Reply with **Agentverse External Storage** (upload bytes, then send resource)

Use this when you have the video (or image) in memory or as bytes and want to store it on Agentverse so the chat UI can fetch it.

```python
import os
from uagents_core.storage import ExternalStorage

# One-time setup (e.g. in agent module or __main__)
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")
STORAGE_URL = os.getenv("AGENTVERSE_URL", "https://agentverse.ai").rstrip("/") + "/v1/storage"

if AGENTVERSE_API_KEY:
    external_storage = ExternalStorage(api_token=AGENTVERSE_API_KEY, storage_url=STORAGE_URL)
else:
    external_storage = None


def create_text_chat(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


async def send_video_via_storage(
    ctx: Context,
    sender: str,
    video_bytes: bytes,
    session_id: str,
    mime_type: str = "video/mp4",
) -> None:
    """
    Upload video to Agentverse External Storage and send a ChatMessage
    with ResourceContent so the chat UI can show a preview.
    """
    if not external_storage:
        await ctx.send(sender, create_text_chat("Video storage not configured."))
        return

    try:
        asset_id = external_storage.create_asset(
            name=f"{session_id}-video",
            content=video_bytes,
            mime_type=mime_type,
        )
        external_storage.set_permissions(asset_id=asset_id, agent_address=sender)
        asset_uri = f"agent-storage://{external_storage.storage_url}/{asset_id}"

        msg = ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[
                ResourceContent(
                    type="resource",
                    resource_id=uuid4(),
                    resource=Resource(
                        uri=asset_uri,
                        metadata={"mime_type": mime_type, "role": "generated-video"},
                    ),
                ),
            ],
        )
        await ctx.send(sender, msg)
    except Exception as e:
        await ctx.send(sender, create_text_chat(f"Failed to upload video: {e}"))
```

---

## 4. Image preview (same pattern)

```python
def create_image_resource_chat(public_image_url: str, caption: str = "Image") -> ChatMessage:
    """Build a ChatMessage that carries an image for preview (public URL)."""
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=caption),
            ResourceContent(
                type="resource",
                resource_id=uuid4(),
                resource=Resource(
                    uri=public_image_url,
                    metadata={
                        "mime_type": "image/png",
                        "role": "generated-image",
                    },
                ),
            ),
        ],
    )
```

For **uploaded** image bytes (e.g. generated image), use the same `external_storage.create_asset(..., mime_type="image/png")` and `ResourceContent` with `mime_type: "image/png"`, `role: "generated-image"`.

---

## 5. Minimal handler example (video URL in response)

```python
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
)
from uagents import Protocol

chat_proto = Protocol(spec=chat_protocol_spec)


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
            continue
        if isinstance(item, TextContent):
            # Example: your pipeline produces a video URL
            video_url = "https://example.com/demo.mp4"  # replace with real URL
            await ctx.send(
                sender,
                create_video_resource_chat(video_url, caption="Here’s your video."),
            )
            break
```

---

## 6. Requirements

- `uagents` / `uagents-core` with chat protocol support.
- For External Storage: `AGENTVERSE_API_KEY` and (optionally) `AGENTVERSE_URL`.

---

## 7. References

- [Agent Chat Protocol — ResourceContent](https://innovationlab.fetch.ai/resources/docs/agent-communication/agent-chat-protocol)
- [Image Generation Agent (same pattern for video)](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/image-generation-agent)
- [ASI:One Agent Chat Protocol](https://docs.asi1.ai/documentation/tutorials/agent-chat-protocol)

Image sharing (and thus video preview) in **ASI:One** may still be “coming soon”; **Agentverse Chat** already supports displaying images (and likely the same resource format for video).
