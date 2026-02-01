"""
Direct test client for AdBoard AI agent.

This script sends a message directly to your agent without going through ASI:One,
which helps debug if the issue is with ASI:One's relay or with the agent itself.
"""

import asyncio
import os
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

load_dotenv()

# Your AdBoard AI agent address (from orchestrator startup)
ADBOARD_ADDRESS = "agent1q2xwg46kfvvrv05dez0ala9evfmwjnzhq8nsu3t8uly2vmt3245sk9v84tc"

# Create a test client agent - use testnet to match orchestrator
test_client = Agent(
    name="TestClient",
    seed="test-client-seed-12345",
    port=8001,
    mailbox=True,
    network="testnet",
)


@test_client.on_event("startup")
async def on_startup(ctx: Context):
    """Send a test message to AdBoard AI on startup."""
    ctx.logger.info(f"Test client started: {ctx.agent.address}")
    ctx.logger.info(f"Sending test message to AdBoard AI: {ADBOARD_ADDRESS}")

    # Create a test message
    test_msg = ChatMessage(
        timestamp=datetime.now(),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text="Create an ad for my pizza shop"),
        ],
    )

    try:
        await ctx.send(ADBOARD_ADDRESS, test_msg)
        ctx.logger.info("Test message sent!")
    except Exception as e:
        ctx.logger.error(f"Failed to send: {e}")


@test_client.on_message(ChatMessage)
async def handle_response(ctx: Context, sender: str, msg: ChatMessage):
    """Handle response from AdBoard AI."""
    ctx.logger.info(f"Received response from {sender}!")

    # Send acknowledgement
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    # Print the response
    for item in msg.content:
        if isinstance(item, TextContent):
            print("\n" + "=" * 60)
            print("RESPONSE FROM ADBOARD AI:")
            print("=" * 60)
            print(item.text)
            print("=" * 60 + "\n")


@test_client.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgement."""
    ctx.logger.info(f"Message {msg.acknowledged_msg_id} was acknowledged by {sender}")


if __name__ == "__main__":
    print("\nTest Client for AdBoard AI")
    print("=" * 40)
    print(f"Target agent: {ADBOARD_ADDRESS}")
    print("=" * 40 + "\n")
    test_client.run()
