#!/usr/bin/env python3
"""
Test Client for Marky - Ad Research Agent

Use this to test Marky locally before deploying.

Usage:
    1. Start Marky in one terminal:  python run_marky.py
    2. Run this client in another:   python test_marky_client.py
    3. Or with custom query:         python test_marky_client.py -q "plumber in Boston, MA"

Set MARKY_AGENT_ADDRESS in .env if Marky runs with a different address.
"""

from datetime import datetime, timezone
from uuid import uuid4
import os
import sys
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    TextContent,
    ChatAcknowledgement,
)

# Marky's address - deterministic from seed "marky-ad-research-agent"
# Run "python run_marky.py" first and copy the address from output if different
MARKY_AGENT_ADDRESS = os.getenv(
    "MARKY_AGENT_ADDRESS",
    "agent1q06t0mhdhu4w23qv58l5sw7arq0398tqyxgazcumnvtx8px9vmfpzklty0w",
)

# Default test query
DEFAULT_QUERY = "plumber in Boston, MA"

# Test client agent
client = Agent(
    name="marky-test-client",
    seed=os.environ.get("CLIENT_SEED_PHRASE", "marky-test-client-seed"),
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
)


@client.on_event("startup")
async def send_test_message(ctx: Context):
    """Send a test message when client starts."""
    import asyncio

    # Allow passing query via env or use default
    query = os.environ.get("MARKY_TEST_QUERY", DEFAULT_QUERY)

    # Wait for agent registration
    await asyncio.sleep(3)

    ctx.logger.info(f"Test client started. Sending to Marky: {MARKY_AGENT_ADDRESS[:20]}...")
    ctx.logger.info(f"Query: {query}")

    try:
        await ctx.send(
            MARKY_AGENT_ADDRESS,
            ChatMessage(
                timestamp=datetime.now(timezone.utc),
                msg_id=uuid4(),
                content=[TextContent(type="text", text=query)],
            ),
        )
        ctx.logger.info("Message sent! Waiting for response (this may take 2-4 minutes with 4 agents)...")
    except Exception as e:
        ctx.logger.error(f"Failed to send message: {e}")
        ctx.logger.info("Make sure Marky is running: python run_marky.py")


@client.on_message(ChatMessage)
async def handle_response(ctx: Context, sender: str, msg: ChatMessage):
    """Handle response from Marky."""
    for item in msg.content:
        if isinstance(item, TextContent):
            ctx.logger.info("=" * 60)
            ctx.logger.info("Response from Marky:")
            ctx.logger.info("=" * 60)
            ctx.logger.info(item.text)
            ctx.logger.info("=" * 60)


@client.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgement."""
    ctx.logger.info("Received acknowledgement from Marky")


def main():
    parser = argparse.ArgumentParser(description="Test client for Marky agent")
    parser.add_argument(
        "-q", "--query",
        type=str,
        default=DEFAULT_QUERY,
        help=f"Query to send (default: '{DEFAULT_QUERY}')",
    )
    args = parser.parse_args()

    # Set query for the startup handler
    os.environ["MARKY_TEST_QUERY"] = args.query

    # Valid uAgents address is ~66 chars; block placeholders like "agent1q..."
    if "..." in MARKY_AGENT_ADDRESS or len(MARKY_AGENT_ADDRESS) < 60:
        print("ERROR: Please set MARKY_AGENT_ADDRESS in .env!")
        print("Run 'python run_marky.py' first and copy the agent address from the output.")
        sys.exit(1)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  Marky Test Client                                           ║
╠══════════════════════════════════════════════════════════════╣
║  Query: {args.query:<50} ║
║  Target: {MARKY_AGENT_ADDRESS[:30]}... ║
╚══════════════════════════════════════════════════════════════╝

Starting client... (Make sure Marky is running in another terminal)
""")
    client.run()


if __name__ == "__main__":
    main()
