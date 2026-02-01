"""
AdBoard AI - Fresh Start
Simple test agent for ASI:One chat

Based on working Gemini quickstart format.
"""

import os
from datetime import datetime, timezone
from dotenv import load_dotenv

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    chat_protocol_spec
)

load_dotenv()

# Brand new random seed for fresh agent
SEED_PHRASE = "adboard-hackbrown-2026-final-test-x9z4k8"

# Create agent with testnet for better routing
agent = Agent(
    name="adboard_ai_agent",
    seed=SEED_PHRASE,
    port=8000,
    mailbox=True,
    network="testnet"  # May help resolve personal wallet endpoints
)

# Initialize chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)


def create_text_chat(text: str) -> ChatMessage:
    """Create a ChatMessage with TextContent"""
    return ChatMessage(
        content=[TextContent(text=text, type="text")]
    )


@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize agent on startup"""
    ctx.logger.info("🤖 Starting AdBoard AI Agent...")
    ctx.logger.info(f"📍 Agent address: {agent.address}")
    
    ctx.storage.set("total_messages", 0)
    ctx.storage.set("conversations", {})


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages"""
    
    try:
        # Extract text
        user_text = ""
        for item in msg.content:
            if isinstance(item, TextContent):
                user_text = item.text
                break
        
        if not user_text:
            ctx.logger.warning("No text content in message")
            return
        
        ctx.logger.info(f"📨 Message from {sender}: {user_text[:50]}...")
        
        # Send acknowledgement
        await ctx.send(sender, ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id
        ))
        
        # Get conversation history
        conversations = ctx.storage.get("conversations") or {}
        history = conversations.get(sender, [])
        
        # Generate response
        ctx.logger.info("🤔 Generating response...")
        response_text = f"✅ AdBoard AI received your message: '{user_text[:80]}'"
        
        ctx.logger.info(f"✅ Response: {response_text[:50]}...")
        
        # Update history
        history.append({'role': 'user', 'text': user_text})
        history.append({'role': 'model', 'text': response_text})
        conversations[sender] = history[-10:]
        ctx.storage.set("conversations", conversations)
        
        # Track stats
        total = ctx.storage.get("total_messages") or 0
        ctx.storage.set("total_messages", total + 1)
        
        # Send response
        await ctx.send(sender, create_text_chat(response_text))
        
        ctx.logger.info(f"💬 Response sent to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error: {e}")
        error_msg = "Sorry, I encountered an error. Please try again."
        await ctx.send(sender, create_text_chat(error_msg))


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle message acknowledgements"""
    ctx.logger.debug(f"✓ Message {msg.acknowledged_msg_id} acknowledged by {sender}")


# Include chat protocol
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 ADBOARD AI - FRESH START")
    print("=" * 70)
    print(f"📍 Agent address: {agent.address}")
    print(f"🔑 Seed: {SEED_PHRASE}")
    print()
    print("🎯 Ready for ASI:One chat testing")
    print()
    print("📋 Next Steps:")
    print("   1. Copy the agent address above")
    print("   2. Go to Agentverse inspector to create mailbox")
    print("   3. Test chat from ASI:One")
    print()
    print("✅ Agent running! Press Ctrl+C to stop.")
    print("=" * 70)
    print()
    
    agent.run()
