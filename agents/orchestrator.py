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
        
        # Send initial "working on it" message
        await ctx.send(
            sender,
            create_response(
               "🎬 Generating your ad package (MOCK MODE - instant results)...\n\n"
                "In production, this would take 3-5 minutes. Mock mode returns instantly!"
            ),
        )
        
        # Format and send mock results
        response_text = format_results(MOCK_PIPELINE_RESULT, "storyboard_video")
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


def upload_file_to_tmpfiles(file_path: str) -> str:
    """Upload any file to tmpfiles.org and return public URL.
    
    tmpfiles.org is a free temporary file hosting service.
    Files are kept for ~1 hour (sufficient for demos).
    
    Args:
        file_path: Local path to file (video, PDF, image, etc.)
        
    Returns:
        Public URL to file, or None if upload failed
    """
    try:
        import subprocess
        import json
        
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            return None
        
        filename = os.path.basename(file_path)
        print(f"📤 Uploading {filename} to tmpfiles.org...")
        
        # Use curl command - more reliable than requests for file uploads
        result = subprocess.run(
            ['curl', '-F', f'file=@{file_path}', 'https://tmpfiles.org/api/v1/upload'],
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
                print(f"✅ File uploaded successfully: {direct_url}")
                return direct_url
        
        print(f"⚠️ Upload failed: {result.stderr}")
        return None
        
    except Exception as e:
        print(f"⚠️ Upload error: {e}")
        return None


def format_results(result: dict, output_type: str) -> str:
    """Format pipeline results with COMPLETE details (like terminal logs)."""
    
    results = result.get("results", {})
    output_lines = []
    viral_video_url = None

    # === EXECUTIVE SUMMARY (Top of response for quick scanning) ===
    output_lines.append("=" * 50)
    output_lines.append("🎯 CAMPAIGN PACKAGE READY")
    output_lines.append("=" * 50)
    
    # Quick stats
    research_data = results.get("research", {})
    script_data = results.get("script_writer", {})
    scenes = script_data.get("scenes", [])
    
    if research_data:
        summary = research_data.get("research_summary", {})
        output_lines.append(f"✅ Analyzed {summary.get('competitors_found', 0)} competitors")
        output_lines.append(f"✅ Generated {len(scenes)} scene storyboard")
        output_lines.append(f"✅ Researched {summary.get('keywords_analyzed', 0)} keywords")
    
    output_lines.append("")
    output_lines.append("📦 Package Includes:")
    output_lines.append("   • Black & White Storyboard Video (concept validation)")
    output_lines.append("   • Complete PDF Package (strategy + research + budget)")
    output_lines.append("   • Multi-Platform Distribution Plan")
    output_lines.append("   • A/B Testing Recommendations")
    output_lines.append("")
    output_lines.append("⬇️ SCROLL DOWN FOR DETAILS & DOWNLOAD LINKS")
    output_lines.append("=" * 50)
    output_lines.append("")
    
    output_lines.append("=" * 50)
    output_lines.append("🎉 YOUR AD PRODUCTION PACKAGE IS READY!")
    output_lines.append("=" * 50)
    output_lines.append("")
    
    # === VIDEO & FILES ===
    video_url = None
    if "video_assembly" in results:
        video_data = results["video_assembly"]
        
        # Check if mock URL already provided (for MOCK_MODE)
        if video_data.get("video_url"):
            video_url = video_data["video_url"]
            output_lines.append("🎬 FINAL VIDEO")
            output_lines.append("-" * 50)
            output_lines.append(f"🔗 WATCH NOW: {video_url}")
            output_lines.append(f"   (Mock link - in production, this uploads to tmpfiles.org)")
            output_lines.append(f"   • Duration: {video_data.get('duration', 30)}s")
            output_lines.append(f"   • Resolution: {video_data.get('resolution', '1920x1080')}")
            output_lines.append(f"   • Frames: {video_data.get('frames_used', 5)} with Ken Burns effects")
            output_lines.append("")
        else:
            # Real mode: check if file exists and upload it
            video_path = video_data.get("final_video_path")
            if video_path and os.path.exists(video_path):
                output_lines.append("🎬 FINAL VIDEO")
                output_lines.append("-" * 50)
                # Upload video
                print(f"\n📤 Uploading video to tmpfiles.org...")
                video_url = upload_file_to_tmpfiles(video_path)
                if video_url:
                    output_lines.append(f"🔗 WATCH NOW: {video_url}")
                    output_lines.append(f"   (Link valid for ~1 hour)")
                output_lines.append(f"   • Duration: {video_data.get('duration', 30)}s")
                output_lines.append(f"   • Resolution: {video_data.get('resolution', '1920x1080')}")
                output_lines.append(f"   • Frames: {video_data.get('frames_used', 5)} with Ken Burns effects")
                output_lines.append("")
    

    # === VIRAL VIDEO (VEO 3 + LYRIA + TTS) ===
    if "viral_video_assembler" in results:
        viral_data = results["viral_video_assembler"]
        viral_path = viral_data.get("final_video_path")
        
        output_lines.append("📱 VIRAL VIDEO (TikTok/Reels)")
        output_lines.append("-" * 50)
        
        if viral_path and os.path.exists(viral_path):
            print(f"\n📤 Uploading viral video to tmpfiles.org...")
            viral_video_url = upload_file_to_tmpfiles(viral_path)
            
            if viral_video_url:
                output_lines.append(f"🔗 WATCH NOW: {viral_video_url}")
            
            output_lines.append(f"   • Format: 9:16 Vertical (15s)")
            output_lines.append(f"   • Music: Generated by Lyria")
            output_lines.append(f"   • Voice: Google TTS Neural2")
            output_lines.append("")
        elif viral_path: # Mock mode or error
             output_lines.append(f"🔗 WATCH NOW: {viral_path} (Mock)")

    # === PDF PACKAGE ===
    pdf_url = None
    if "pdf_export" in results:
        pdf_data = results["pdf_export"]
        
        # Check if mock URL already provided (for MOCK_MODE)
        if pdf_data.get("pdf_url"):
            pdf_url = pdf_data["pdf_url"]
            output_lines.append("📄 COMPLETE AD PACKAGE (PDF)")
            output_lines.append("-" * 50)
            output_lines.append(f"🔗 DOWNLOAD PDF: {pdf_url}")
            output_lines.append(f"   (Mock link - in production, this uploads to tmpfiles.org)")
            output_lines.append(f"   • Pages: {pdf_data.get('pages', 8)}")
            includes = pdf_data.get('includes', [])
            if includes:
                output_lines.append(f"   • Includes: {', '.join(includes)}")
            output_lines.append("")
        else:
            # Real mode: check if file exists and upload it
            pdf_path = pdf_data.get("pdf_path")
            if pdf_path and os.path.exists(pdf_path):
                output_lines.append("📄 COMPLETE AD PACKAGE (PDF)")
                output_lines.append("-" * 50)
                print(f"\n📤 Uploading PDF to tmpfiles.org...")
                pdf_url = upload_file_to_tmpfiles(pdf_path)
                if pdf_url:
                    output_lines.append(f"🔗 DOWNLOAD PDF: {pdf_url}")
                    output_lines.append(f"   (Link valid for ~1 hour)")
                output_lines.append(f"   • Pages: {pdf_data.get('pages', 8)}")
                includes = pdf_data.get('includes', [])
                if includes:
                    output_lines.append(f"   • Includes: {', '.join(includes)}")
                output_lines.append("")
    
    # === FULL SCRIPT ===
    if "script_writer" in results:
        script_data = results["script_writer"]
        scenes = script_data.get("scenes", [])
        output_lines.append("📝 COMPLETE SCRIPT")
        output_lines.append("-" * 50)
        
        if scenes:
            for scene in scenes:
                output_lines.append(f"\n🎬 SCENE {scene.get('scene_number')} ({scene.get('timing')}) - {scene.get('title', '').upper()}")
                output_lines.append(f"Visual: {scene.get('visual', '')}")
                if scene.get('voiceover'):
                    output_lines.append(f"Voiceover: \"{scene.get('voiceover')}\"")
                if scene.get('audio'):
                    output_lines.append(f"Audio: {scene.get('audio')}")
        
        voiceover = script_data.get("voiceover_text", "")
        if voiceover:
            output_lines.append(f"\n📢 FULL VOICEOVER TEXT:")
            output_lines.append(f'"{voiceover}"')
        output_lines.append("")
    
    # === RESEARCH INSIGHTS ===
    if "research" in results:
        research_data = results["research"]
        output_lines.append("🔍 MARKET RESEARCH SUMMARY")
        output_lines.append("-" * 50)
        
        # Stats
        output_lines.append(f"✓ Competitors analyzed: {research_data.get('competitors_found', 0)}")
        output_lines.append(f"✓ Google Reviews: {research_data.get('google_reviews', 0)}")
        output_lines.append(f"✓ Yelp Reviews: {research_data.get('yelp_reviews', 0)}")
        output_lines.append(f"✓ Keywords analyzed: {research_data.get('keywords_analyzed', 0)}")
        
        # Top Competitors
        local_intel = research_data.get("local_intel", {})
        if local_intel.get("top_competitors"):
            output_lines.append(f"\n🏆 Top Competitors:")
            for comp in local_intel["top_competitors"][:3]:
                output_lines.append(f"   • {comp}")
        
        # Ad Hooks
        hooks = research_data.get("ad_hooks", [])
        if hooks:
            output_lines.append(f"\n💡 Recommended Ad Hooks:")
            for hook in hooks[:3]:
                output_lines.append(f"   • {hook}")
        
        # Key Insights
        insights = research_data.get("insights", [])
        if insights:
            output_lines.append(f"\n📊 Key Insights:")
            for insight in insights[:5]:
                output_lines.append(f"   • {insight}")
        
        output_lines.append("")
    
    # === STORYBOARD FRAMES ===
    if "image_generator" in results:
        img_data = results["image_generator"]
        frames = img_data.get("frames", [])
        if frames:
            output_lines.append("🎨 STORYBOARD FRAMES")
            output_lines.append("-" * 50)
            script_scenes = results.get("script_writer", {}).get("scenes", [])
            for i, frame in enumerate(frames, 1):
                timing = frame.get("timing", "")
                if i <= len(script_scenes):
                    desc = script_scenes[i-1].get("visual", "")[:80]
                else:
                    desc = frame.get("description", "Generated scene")
                output_lines.append(f"Frame {i} ({timing}): {desc}")
            output_lines.append(f"\nTotal: {len(frames)} frames generated via {img_data.get('model_used', 'Imagen')}")
            output_lines.append("")
    
    # === COST BREAKDOWN ===
    if "cost_estimator" in results:
        cost_data = results["cost_estimator"]
        total = cost_data.get("total", 0)
        output_lines.append("💰 PRODUCTION COST ESTIMATE")
        output_lines.append("-" * 50)
        output_lines.append(f"TOTAL BUDGET: ${total:,.2f}")
        output_lines.append("")
        
        # Line items
        line_items = cost_data.get("line_items", [])
        if line_items:
            current_category = None
            for item in line_items:
                category = item.get("category", "")
                if category != current_category:
                    output_lines.append(f"\n{category}:")
                    current_category = category
                name = item.get("item", "")
                cost = item.get("cost", 0)
                output_lines.append(f"   • {name}: ${cost:,.2f}")
        else:
            # Fallback to breakdown
            breakdown = cost_data.get("breakdown", {})
            if breakdown:
                output_lines.append("Breakdown:")
                for key, value in breakdown.items():
                    output_lines.append(f"   • {key.replace('_', ' ').title()}: ${value:,.2f}")
        output_lines.append("")
    
    # === SOCIAL MEDIA ===
    if "social_media" in results:
        social_data = results["social_media"]
        hashtags = social_data.get("hashtags", {})
        captions = social_data.get("captions", {})
        
        if hashtags or captions:
            output_lines.append("📱 SOCIAL MEDIA STRATEGY")
            output_lines.append("-" * 50)
            
            primary = hashtags.get("primary", [])
            if primary:
                output_lines.append(f"Hashtags: {' '.join(primary[:5])}")
            
            if captions:
                for platform, caption in list(captions.items())[:2]:
                    output_lines.append(f"\n{platform.title()}: \"{caption[:100]}...\"")
            output_lines.append("")
    
    # === FILMING LOCATIONS ===
    if "location_scout" in results:
        loc_data = results["location_scout"]
        locations = loc_data.get("locations", [])
        if locations:
            output_lines.append("📍 RECOMMENDED FILMING LOCATIONS")
            output_lines.append("-" * 50)
            for loc in locations[:3]:
                name = loc.get("name", "")
                address = loc.get("address", "")
                notes = loc.get("notes", "")
                output_lines.append(f"   • {name}")
                if address:
                    output_lines.append(f"     {address}")
                if notes:
                    output_lines.append(f"     Note: {notes}")
            output_lines.append("")
    
    # === FOOTER ===
    output_lines.append("=" * 50)
    if video_url or pdf_url or viral_video_url:
        output_lines.append("🎯 YOUR CAMPAIGN PACKAGE:")
        if video_url:
            output_lines.append(f"   🎬 Video: {video_url}")
        if viral_video_url:
            output_lines.append(f"   📱 Viral Video: {viral_video_url}")
        if pdf_url:
            output_lines.append(f"   📄 PDF Package: {pdf_url}")
        output_lines.append("")
    output_lines.append("Your complete campaign package is ready! 🚀")
    output_lines.append("Built at Hack@Brown 2026 | 12-Agent Orchestration System")
    output_lines.append("=" * 50)
    
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
