"""
Marky - Ad Research Agent (uAgents Entry Point)

Single-entry-point uAgent that handles chat protocol
and orchestrates the internal workflow.

Compatible with Fetch.ai Agentverse and ASI:One.
"""

from __future__ import annotations

import os
import re
import asyncio
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

# uAgents imports
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    MetadataContent,
    StartSessionContent,
    EndSessionContent,
)

from .models import AdResearchRequest, AdResearchResponse
from .workflow import MarkyWorkflow


# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_NAME = "Marky"
AGENT_SEED = "marky-ad-research-agent"
AGENT_PORT = int(os.getenv("MARKY_PORT", "8000"))

# Initialize the uAgent
marky_agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    mailbox=True,  # Enable mailbox for Agentverse discovery
)

# Initialize chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# Global workflow instance
_workflow: Optional[MarkyWorkflow] = None

# Track processed messages to prevent duplicates
_processed_messages: set = set()


# =============================================================================
# Helper Functions
# =============================================================================

def get_workflow() -> MarkyWorkflow:
    """Get or create the workflow instance."""
    global _workflow
    if _workflow is None:
        _workflow = MarkyWorkflow()
    return _workflow


def create_chat_message(text: str, end_session: bool = False) -> ChatMessage:
    """Create a ChatMessage with text content."""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )


def parse_research_request(user_text: str) -> Optional[AdResearchRequest]:
    """
    Parse user input to extract business type and location.
    
    Expected formats:
    - "plumber in Boston, MA"
    - "research electrician Providence RI"
    - "analyze restaurant near San Francisco"
    """
    # Clean up input
    text = user_text.lower().strip()
    
    # Remove command prefixes
    prefixes = ["research", "analyze", "audit", "find", "search"]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Try to parse "X in Y" pattern
    in_pattern = r"(.+?)\s+(?:in|near|around)\s+(.+)"
    match = re.match(in_pattern, text, re.IGNORECASE)
    
    if match:
        business_type = match.group(1).strip()
        location = match.group(2).strip()
        return AdResearchRequest(
            business_type=business_type,
            location=location,
        )
    
    # Try to parse "X, Y" pattern (business, location)
    if "," in text:
        parts = text.split(",", 1)
        if len(parts) == 2:
            return AdResearchRequest(
                business_type=parts[0].strip(),
                location=parts[1].strip(),
            )
    
    return None


def is_help_request(text: str) -> bool:
    """Check if the user is asking for help."""
    text = text.lower().strip()
    help_keywords = ["help", "?", "how", "what can you do", "commands", "usage"]
    return any(kw in text for kw in help_keywords)


def get_help_message() -> str:
    """Return help message."""
    return """# 🎯 Marky - Ad Research Agent

I help you research local competitors and generate advertising strategies.

## How to Use

Just tell me what business type and location you want to research:

- `plumber in Boston, MA`
- `restaurant near San Francisco`
- `electrician Providence RI`
- `dentist, Chicago IL`

## What I Analyze

1. **Local Competitors** - Find and analyze competitor websites
2. **Customer Reviews** - Extract pain points and desires from Yelp
3. **Search Trends** - Seasonal timing and keyword data
4. **Ad Strategy** - Generate hooks, headlines, and differentiators

## Example

```
research plumber in Providence, RI
```

Just type your request and I'll start the analysis!
"""


# =============================================================================
# Event Handlers
# =============================================================================

@marky_agent.on_event("startup")
async def on_startup(ctx: Context):
    """Initialize workflow on agent startup."""
    ctx.logger.info(f"🚀 {AGENT_NAME} starting at {ctx.agent.address}")
    ctx.logger.info(f"📬 Mailbox enabled for Agentverse discovery")
    
    # Pre-initialize workflow
    try:
        get_workflow()
        ctx.logger.info("✅ Workflow initialized successfully")
    except Exception as e:
        ctx.logger.error(f"❌ Failed to initialize workflow: {e}")


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages."""
    global _processed_messages
    
    # Check for duplicate
    message_key = f"{sender}:{msg.msg_id}"
    if message_key in _processed_messages:
        ctx.logger.debug(f"Duplicate message ignored: {msg.msg_id}")
        return
    
    try:
        # Send acknowledgement immediately
        ack = ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        )
        await ctx.send(sender, ack)
        
        # Mark as processed
        _processed_messages.add(message_key)
        if len(_processed_messages) > 1000:
            _processed_messages.clear()
        
        # Handle different content types
        for item in msg.content:
            # Handle session start
            if isinstance(item, StartSessionContent):
                await ctx.send(
                    sender,
                    ChatMessage(
                        timestamp=datetime.now(timezone.utc),
                        msg_id=uuid4(),
                        content=[
                            MetadataContent(type="metadata", metadata={"attachments": "false"}),
                        ],
                    ),
                )
                await ctx.send(sender, create_chat_message(
                    "👋 Hi! I'm Marky, your ad research assistant.\n\n"
                    "Tell me a business type and location to analyze, like:\n"
                    "`plumber in Boston, MA`\n\n"
                    "Type `help` for more info."
                ))
                return
            
            # Handle text content
            if isinstance(item, TextContent):
                user_text = item.text.strip()
                
                if not user_text:
                    await ctx.send(sender, create_chat_message(
                        "Please enter a query like: `plumber in Boston, MA`"
                    ))
                    return
                
                ctx.logger.info(f"📩 Received from {sender}: {user_text}")
                
                # Handle help request
                if is_help_request(user_text):
                    await ctx.send(sender, create_chat_message(get_help_message()))
                    return
                
                # Parse research request
                request = parse_research_request(user_text)
                
                if not request:
                    await ctx.send(sender, create_chat_message(
                        "🤔 I couldn't understand that.\n\n"
                        "Try something like: `plumber in Boston, MA`\n\n"
                        "Type `help` for more examples."
                    ))
                    return
                
                # Send progress update
                await ctx.send(sender, create_chat_message(
                    f"🔍 Starting analysis for **{request.business_type}** in **{request.location}**...\n\n"
                    "This may take 1-2 minutes."
                ))
                
                # Run workflow
                try:
                    workflow = get_workflow()
                    
                    # Progress callback to send updates
                    async def send_progress(msg: str):
                        if msg.startswith("🔍") or msg.startswith("🗣️") or msg.startswith("📈") or msg.startswith("🧠"):
                            await ctx.send(sender, create_chat_message(msg))
                    
                    # Run in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        lambda: workflow.run(request),
                    )
                    
                    # Send result
                    result_markdown = response.to_markdown()
                    await ctx.send(sender, create_chat_message(result_markdown))
                    
                    ctx.logger.info(f"✅ Analysis complete for {sender}")
                    
                except Exception as e:
                    ctx.logger.error(f"❌ Workflow error: {e}")
                    await ctx.send(sender, create_chat_message(
                        f"❌ Error running analysis: {str(e)}\n\n"
                        "Please try again or check your API keys."
                    ))
                
                return
        
        # No supported content found
        await ctx.send(sender, create_chat_message(
            "I didn't understand that message type. Please send text."
        ))
        
    except Exception as e:
        ctx.logger.error(f"❌ Error handling message: {e}")
        _processed_messages.discard(message_key)
        await ctx.send(sender, create_chat_message(f"❌ Error: {str(e)}"))


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgement messages."""
    ctx.logger.debug(f"ACK from {sender} for {msg.acknowledged_msg_id}")


# Include protocol with manifest for discovery
marky_agent.include(chat_proto, publish_manifest=True)


# =============================================================================
# Entry Point
# =============================================================================

def run_marky():
    """Run the Marky agent."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎯 MARKY - Ad Research Agent                               ║
║                                                              ║
║   Powered by uAgents + Fetch.ai                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Starting agent on port {AGENT_PORT}...
""")
    marky_agent.run()


if __name__ == "__main__":
    run_marky()
