"""
Simple Test Agent for ASI:One
Tests basic chat communication with Fetch.ai Agentverse

This agent:
- Receives messages via Fetch.ai protocol
- Echoes them back
- Tests ASI:One chat UI integration
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

# Load environment variables
load_dotenv()

# Get seed phrase from environment
SEED_PHRASE = os.getenv("AGENT_SEED_PHRASE", "adboard-ai-hackathon-seed-2026589023745098423y")

# Create agent
agent = Agent(
    name="AdBoardAI",
    seed=SEED_PHRASE,
    port=8000,
    mailbox=True  # Required for Agentverse deployment
)

# Initialize chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)


# Helper function to create text chat messages
def create_text_chat(text: str) -> ChatMessage:
    """Create a ChatMessage with TextContent"""
    return ChatMessage(
        content=[TextContent(text=text, type="text")]
    )


@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize agent on startup"""
    ctx.logger.info("🤖 Starting AdBoard AI Test Agent...")
    ctx.logger.info(f"📍 Agent address: {agent.address}")
    
    # Initialize conversation storage
    ctx.storage.set("total_messages", 0)


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages"""
    
    try:
        # Extract text from message content
        user_text = ""
        for item in msg.content:
            if isinstance(item, TextContent):
                user_text = item.text
                break
        
        if not user_text:
            ctx.logger.warning("No text content in message")
            return
        
        # Log incoming message
        ctx.logger.info(f"📨 Message from {sender}: {user_text[:50]}...")
        print(f"\n{'=' * 60}")
        print(f"INCOMING MESSAGE:")
        print(f"  Sender: {sender}")
        print(f"  Text: '{user_text}'")
        print(f"  Msg ID: {msg.msg_id}")
        print(f"{'=' * 60}\n")
        
        # Send acknowledgement
        await ctx.send(sender, ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id
        ))
        print("✓ ACK sent")
        
        # Create simple echo response
        response_text = f"Hello! AdBoard AI received: '{user_text[:80]}'"
        
        ctx.logger.info(f"✅ Sending response: {response_text[:50]}...")
        print(f"📤 Sending response: {response_text}")
        
        # Track stats
        total = ctx.storage.get("total_messages") or 0
        ctx.storage.set("total_messages", total + 1)
        
        # Send response back to user (using helper function like working example)
        await ctx.send(sender, create_text_chat(response_text))
        
        ctx.logger.info(f"💬 Response sent to {sender}")
        print("✓ RESPONSE SENT SUCCESSFULLY")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing message: {e}")
        
        # Send error message to user
        error_msg = "I'm sorry, I encountered an error. Please try again."
        await ctx.send(sender, create_text_chat(error_msg))


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle message acknowledgements"""
    ctx.logger.debug(f"✓ Message {msg.acknowledged_msg_id} acknowledged by {sender}")


# Include the chat protocol
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    print("🤖 Starting AdBoard AI Test Agent...")
    print(f"📍 Agent address: {agent.address}")
    
    print("\n🎯 Agent Features:")
    print("   • Simple echo test agent")
    print("   • Tests ASI:One chat UI")
    print("   • Ready for Agentverse deployment")
    
    print("\n✅ Agent is running! Connect via ASI One or send messages programmatically.")
    print("   Press Ctrl+C to stop.\n")
    
    agent.run()
