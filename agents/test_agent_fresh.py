"""
Fresh Test Agent for ASI:One
Brand new agent to test chat communication

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

# BRAND NEW RANDOM SEED - creates a completely new agent identity
SEED_PHRASE = "hackybrowntom26"
# Create agent
agent = Agent(
    name="FreshTestAgent",
    seed=SEED_PHRASE,
    port=8001,  # Different port to avoid conflicts
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
    ctx.logger.info("🤖 Starting Fresh Test Agent...")
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
        response_text = f"🎉 Fresh Agent says: I received '{user_text[:60]}'"
        
        ctx.logger.info(f"✅ Sending response: {response_text[:50]}...")
        print(f"📤 Sending response: {response_text}")
        
        # Track stats
        total = ctx.storage.get("total_messages") or 0
        ctx.storage.set("total_messages", total + 1)
        
        # Send response back to user
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
    print("=" * 70)
    print("🤖 FRESH TEST AGENT - Brand New Identity")
    print("=" * 70)
    print(f"📍 Agent address: {agent.address}")
    print(f"🔑 Seed: {SEED_PHRASE}")
    print(f"🌐 Port: 8001")
    
    print("\n🎯 Agent Features:")
    print("   • Brand new agent identity")
    print("   • Simple echo test")
    print("   • Tests ASI:One chat UI")
    print("   • Ready for Agentverse deployment")
    
    print("\n📋 Next Steps:")
    print("   1. Copy the agent address above")
    print("   2. Go to Agentverse and find this agent")
    print("   3. Click 'Chat with Agent'")
    print("   4. Send a message!")
    
    print("\n✅ Agent is running! Press Ctrl+C to stop.")
    print("=" * 70 + "\n")
    
    agent.run()
