"""
Basic Test Agent for Fetch.ai Agentverse
A simple conversational AI agent that echoes messages back

This agent:
- Receives messages via Fetch.ai protocol
- Echoes them back with confirmation
- Sends intelligent responses back
- Maintains basic conversation context

EXACT COPY of basic_gemini_agent.py format but without Gemini API requirement
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

# Create agent
agent = Agent(
    name="test_echo_agent",
    seed="adboard-test-fresh-2026-echo",  # Unique seed phrase
    port=8000,
    mailbox=True  # Required for Agentverse deployment
)

# Initialize chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# System prompt - customize this for your use case!
SYSTEM_PROMPT = """You are a helpful test assistant running on Fetch.ai's decentralized agent network.

You should:
- Be friendly, helpful, and concise
- Confirm receipt of messages
- Echo back what you received
- Keep responses focused and relevant

Current capabilities:
- Message confirmation
- Echo responses
- General conversation

Conversation History (if any):
"""


# Helper function to create text chat messages
def create_text_chat(text: str) -> ChatMessage:
    """Create a ChatMessage with TextContent"""
    return ChatMessage(
        content=[TextContent(text=text, type="text")]
    )


@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize agent on startup"""
    ctx.logger.info("🤖 Starting Test Echo Agent...")
    ctx.logger.info(f"📍 Agent address: {agent.address}")
    
    ctx.logger.info("✅ Test agent configured (no API needed)")
    
    # Initialize conversation storage
    ctx.storage.set("total_messages", 0)
    ctx.storage.set("conversations", {})


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
        
        # Send acknowledgement
        await ctx.send(sender, ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id
        ))
        
        # Get conversation history for context
        conversations = ctx.storage.get("conversations") or {}
        history = conversations.get(sender, [])
        
        # Build chat contents with history context
        # For simplicity, we'll include recent history in the prompt
        conversation_context = ""
        if history:
            for h in history[-5:]:
                role = "User" if h['role'] == 'user' else "Assistant"
                conversation_context += f"{role}: {h['text']}\n"
        
        # Generate simple echo response (no API needed)
        ctx.logger.info("🤔 Generating response...")
        response_text = f"✅ Message confirmed! I received: '{user_text[:100]}'\n\nMessage count: {len(history) // 2 + 1}"
        
        ctx.logger.info(f"✅ Response generated: {response_text[:50]}...")
        
        # Update conversation history
        history.append({'role': 'user', 'text': user_text})
        history.append({'role': 'model', 'text': response_text})
        conversations[sender] = history[-10:]  # Keep last 10 messages
        ctx.storage.set("conversations", conversations)
        
        # Track stats
        total = ctx.storage.get("total_messages") or 0
        ctx.storage.set("total_messages", total + 1)
        
        # Send response back to user
        await ctx.send(sender, create_text_chat(response_text))
        
        ctx.logger.info(f"💬 Response sent to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing message: {e}")
        
        # Send error message to user
        error_msg = "I'm sorry, I encountered an error processing your message. Please try again."
        await ctx.send(sender, create_text_chat(error_msg))


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle message acknowledgements"""
    ctx.logger.debug(f"✓ Message {msg.acknowledged_msg_id} acknowledged by {sender}")


# Include the chat protocol
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    print("🤖 Starting Test Echo Agent...")
    print(f"📍 Agent address: {agent.address}")
    
    print("✅ Test agent configured (no API needed)")
    
    print("\n🎯 Agent Features:")
    print("   • Simple message echo/confirmation")
    print("   • Context-aware responses")
    print("   • Conversation history tracking")
    print("   • Ready for Agentverse deployment")
    
    print("\n✅ Agent is running! Connect via ASI One or send messages programmatically.")
    print("   Press Ctrl+C to stop.\n")
    
    agent.run()
