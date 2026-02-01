"""
AdBoard AI Orchestrator Agent

Main entry point for ASI:One and Agentverse. Implements Chat Protocol
for discoverability and routes user requests to the appropriate pipeline.

Deploy this agent to Agentverse for the hackathon.
"""

import os
import sys
import requests
from datetime import datetime
from uuid import uuid4

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
    TextContent,
    chat_protocol_spec,
)
from uagents_core.utils.registration import (
    RegistrationRequestCredentials,
    register_chat_agent,
)

load_dotenv()

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
README = """# AdBoard AI - AI Video Ad Generator for Small Businesses

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

An AI-powered multi-agent system that creates professional ad storyboard VIDEOS for small businesses. Tell me about your business and I'll generate a complete 30-second video ad with:
- Pencil-sketch storyboard frames (AI-generated)
- Professional voiceover narration
- Background music
- Ken Burns animation effects

## What I Can Create

- **Storyboard Video** (default): Complete video with sketch frames, voiceover, and music
- **Script**: Just the ad script with scene breakdowns
- **Storyboard**: Script + visual storyboard frames (no video)
- **PDF Package**: Complete production package with budget estimates and locations

## How to Use

Just tell me about your business! Examples:

- "Create an ad for my taco truck"
- "Make a 30-second funny video for my coffee shop"
- "I need a professional ad for my fitness studio in Boston"
- "Generate a storyboard video for my tech startup"

## Features

- 🔍 Researches viral ads in your industry
- ✍️ Writes compelling scripts based on what works
- 🎨 Generates pencil-sketch storyboard frames (Google Imagen 3)
- 🎤 Creates natural voiceover narration (ElevenLabs)
- 🎵 Adds royalty-free background music
- 🎬 Assembles video with Ken Burns pan/zoom effects
- 💰 Estimates production costs
- 📍 Finds filming locations

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
    if TEST_MODE:
        ctx.logger.info("TEST MODE: Sending quick test response")
        test_response = f"Hello! I received: {user_text[:50]}. AdBoard AI test mode."

        # Try without EndSessionContent - ASI:One might not relay it properly
        response_msg = ChatMessage(
            timestamp=datetime.now(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text=test_response),
            ],
        )

        ctx.logger.info(f"Sending to sender: {sender}")
        ctx.logger.info(f"Response msg_id: {response_msg.msg_id}")

        try:
            await ctx.send(sender, response_msg)
            ctx.logger.info("Test response sent successfully to ASI:One!")
        except Exception as e:
            ctx.logger.error(f"Failed to send: {e}")
            import traceback

            ctx.logger.error(traceback.format_exc())
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
                    "Hi! I'm AdBoard AI - I create VIDEO ADS for small businesses!\n\n"
                    "Just tell me about your business and I'll generate:\n"
                    "- A compelling script\n"
                    "- Pencil-sketch storyboard frames\n"
                    "- Professional voiceover\n"
                    "- Background music\n"
                    "- A complete 30-second video!\n\n"
                    "Example: 'Create an ad for my taco truck' or 'Make a funny video for my coffee shop in Providence'"
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
        output_type = intent.get("output_type", "storyboard_video")

        # Normalize output type - "video" should be "storyboard_video"
        if output_type == "video":
            output_type = "storyboard_video"

        product = intent.get("product", "product")
        duration = intent.get("duration", 30)
        tone = intent.get("tone", "professional")

        # Friendly output type names
        output_type_names = {
            "storyboard_video": "storyboard video",
            "storyboard": "storyboard images",
            "script": "script",
            "pdf": "PDF package",
            "full": "full package",
        }
        friendly_output = output_type_names.get(output_type, output_type)

        await ctx.send(
            sender,
            create_response(
                f"🎬 Creating your {friendly_output}!\n\n"
                f"📦 Product: {product}\n"
                f"⏱️ Duration: {duration}s\n"
                f"🎭 Tone: {tone}\n"
                f"📍 Location: {intent.get('city', 'General')}\n\n"
                "⏳ This takes 3-5 minutes (generating images, voiceover, video)...\n"
                "I'll send you the results when ready!"
            ),
        )

        # Run the pipeline
        pipeline = AdBoardPipeline(
            product=product,
            industry=intent.get("industry", "general"),
            output_type=output_type,
            duration=duration,
            tone=intent.get("tone", "professional"),
            city=intent.get("city", ""),
        )

        result = await pipeline.run()

        # Format and send results
        ctx.logger.info("Pipeline completed, sending results back to Agentverse...")

        if result.get("success"):
            response_text = format_results(result, output_type)
            ctx.logger.info(f"Sending success response ({len(response_text)} chars)")
            try:
                await ctx.send(sender, create_response(response_text, end_session=True))
                ctx.logger.info("Response sent successfully!")
            except Exception as send_err:
                ctx.logger.error(f"Failed to send response: {send_err}")
                # Try sending a shorter response
                try:
                    short_response = (
                        "Your ad is ready! Check the output folder for your video."
                    )
                    await ctx.send(
                        sender, create_response(short_response, end_session=True)
                    )
                except Exception as e2:
                    ctx.logger.error(f"Failed to send short response: {e2}")
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


def upload_video_to_fileio(video_path: str) -> str:
    """Upload video to tmpfiles.org and return public URL.
    
    tmpfiles.org is a free temporary file hosting service.
    Files are kept for ~1 hour (sufficient for demos).
    
    Args:
        video_path: Local path to video file
        
    Returns:
        Public URL to video, or None if upload failed
    """
    try:
        import subprocess
        import json
        
        filename = os.path.basename(video_path)
        print(f"📤 Uploading {filename} to tmpfiles.org...")
        
        # Use curl command - more reliable than requests for file uploads
        result = subprocess.run(
            ['curl', '-F', f'file=@{video_path}', 'https://tmpfiles.org/api/v1/upload'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # tmpfiles.org returns JSON like: {"status":"success","data":{"url":"https://tmpfiles.org/xyz/file.mp4"}}
            data = json.loads(result.stdout)
            if data.get('status') == 'success':
                url = data['data']['url']
                # Convert to direct download URL: tmpfiles.org/ID/file → tmpfiles.org/dl/ID/file
                direct_url = url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                print(f"✅ Video uploaded successfully: {direct_url}")
                return direct_url
        
        print(f"⚠️ Upload failed: {result.stderr}")
        return None
        
    except Exception as e:
        print(f"⚠️ Upload error: {e}")
        return None


def format_results(result: dict, output_type: str) -> str:
    """Format pipeline results as natural language descriptions."""

    results = result.get("results", {})
    output_lines = ["🎉 Your ad is ready!\n"]
    output_lines.append("=" * 40 + "\n")

    # Video - upload and return URL
    if "video_assembly" in results:
        video_data = results["video_assembly"]
        video_path = video_data.get("final_video_path")
        if video_path:
            output_lines.append("🎬 FINAL VIDEO")
            output_lines.append("-" * 20)
            output_lines.append(f"✅ {video_data.get('duration', 30)}-second storyboard video created")
            output_lines.append(f"📹 {video_data.get('frames_used', 5)} animated frames with Ken Burns effects")
            output_lines.append(f"🎵 Includes professional voiceover and background music")
            
            # Upload video and get URL
            print(f"\n📤 Uploading video to tmpfiles.org...")
            video_url = upload_video_to_fileio(video_path)
            if video_url:
                output_lines.append(f"\n🔗 **Watch your video:** {video_url}")
                output_lines.append("(Link valid for ~1 hour)")
            else:
                output_lines.append(f"\n⚠️ Video upload failed - file saved locally")
            output_lines.append("")

    # Script - natural language summary
    if "script_writer" in results:
        script_data = results["script_writer"]
        output_lines.append("\n📝 SCRIPT SUMMARY")
        output_lines.append("-" * 20)
        
        # Get voiceover text as the narrative
        voiceover = script_data.get("voiceover_text", "")
        if voiceover:
            # Summarize the voiceover naturally
            output_lines.append(f"'{voiceover[:400]}{'...' if len(voiceover) > 400 else ''}'")
        else:
            scenes = script_data.get("scenes", [])
            if scenes:
                output_lines.append(f"{len(scenes)}-scene commercial script created:")
                for i, scene in enumerate(scenes[:3], 1):
                    visual = scene.get("visual", "")
                    if visual:
                        output_lines.append(f"  Scene {i}: {visual[:80]}")
        output_lines.append("")

    # Storyboard - describe the scenes visually
    if "image_generator" in results:
        img_data = results["image_generator"]
        frames = img_data.get("frames", [])
        if frames:
            output_lines.append(f"\n🎨 STORYBOARD ({len(frames)} frames)")
            output_lines.append("-" * 20)
            
            # Describe each frame naturally based on script scenes
            script_scenes = results.get("script_writer", {}).get("scenes", [])
            for i, frame in enumerate(frames[:5], 1):
                if i <= len(script_scenes):
                    visual = script_scenes[i-1].get("visual", "Visual scene")
                    output_lines.append(f"Frame {i}: {visual}")
                else:
                    output_lines.append(f"Frame {i}: Generated sketch illustration")
            output_lines.append("")

    # Cost estimate - natural breakdown
    if "cost_estimator" in results:
        cost_data = results["cost_estimator"]
        total = cost_data.get("total", 0)
        if total:
            output_lines.append("\n💰 PRODUCTION COST ESTIMATE")
            output_lines.append("-" * 20)
            output_lines.append(f"Total Budget: ${total:.2f}")
            
            # Break down costs naturally
            breakdown = cost_data.get("breakdown", {})
            if breakdown:
                output_lines.append("\nBreakdown:")
                if breakdown.get("images"):
                    output_lines.append(f"  • Image generation: ${breakdown['images']:.2f}")
                if breakdown.get("voiceover"):
                    output_lines.append(f"  • Professional voiceover: ${breakdown['voiceover']:.2f}")
                if breakdown.get("music"):
                    music_cost = breakdown['music']
                    if music_cost == 0:
                        output_lines.append(f"  • Background music: Free")
                    else:
                        output_lines.append(f"  • Music licensing: ${music_cost:.2f}")
            output_lines.append("")

    # Trend Analysis
    if "trend_analyzer" in results:
        trend_data = results["trend_analyzer"]
        trends = trend_data.get("trends", [])
        if trends:
            output_lines.append("\n📈 TRENDING INSIGHTS")
            output_lines.append("-" * 20)
            for trend in trends[:3]:
                if isinstance(trend, dict):
                    trend_text = trend.get("insight", trend.get("trend", str(trend)))
                else:
                    trend_text = str(trend)
                output_lines.append(f"  • {trend_text}")
            output_lines.append("")
    
    # Research summary (if available)
    if "research" in results:
        research_data = results["research"]
        insights = research_data.get("insights", [])
        videos_analyzed = research_data.get("videos_analyzed", 0)
        if insights or videos_analyzed:
            output_lines.append("\n🔍 MARKET RESEARCH")
            output_lines.append("-" * 20)
            if videos_analyzed:
                output_lines.append(f"Analyzed {videos_analyzed} viral ads in your industry")
            for insight in insights[:3]:
                output_lines.append(f"  • {insight}")
            output_lines.append("")

    # Locations
    if "location_scout" in results:
        loc_data = results["location_scout"]
        locations = loc_data.get("locations", [])
        if locations:
            output_lines.append("\n📍 FILMING LOCATIONS")
            output_lines.append("-" * 20)
            for loc in locations[:3]:
                name = loc.get("name", "Location")
                output_lines.append(f"  • {name}")
            output_lines.append("")

    # Social media strategy
    if "social_media" in results:
        social_data = results["social_media"]
        if social_data.get("hashtags"):
            hashtags = social_data["hashtags"]
            primary = hashtags.get("primary", [])[:5]
            if primary:
                output_lines.append("\n📱 SOCIAL MEDIA STRATEGY")
                output_lines.append("-" * 20)
                output_lines.append(f"Recommended hashtags: {' '.join(primary)}")
                output_lines.append("")

    output_lines.append("\n" + "=" * 40)
    output_lines.append("Thanks for using AdBoard AI! 🚀")
    output_lines.append("Built at Hack@Brown 2026")

    return "\n".join(output_lines)


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
                description="AI-powered multi-agent system that creates professional ad storyboards for small businesses. Researches viral ads, writes scripts, generates visuals, and delivers production-ready packages.",
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
