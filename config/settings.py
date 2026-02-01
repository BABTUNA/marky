"""
Configuration settings for AdBoard AI.
Load environment variables and define constants.
"""

import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()


# ============================================
# API KEYS
# ============================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Fetch.AI
AGENT_SEED_PHRASE = os.getenv(
    "AGENT_SEED_PHRASE", "default seed phrase for testing only"
)
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")


# ============================================
# API ENDPOINTS
# ============================================

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"
GOOGLE_PLACES_BASE_URL = "https://places.googleapis.com/v1"


# ============================================
# MODEL SETTINGS
# ============================================

# Groq
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 2048
GROQ_TEMPERATURE = 0.7

# Replicate
REPLICATE_IMAGE_MODEL = "black-forest-labs/flux-schnell"  # Fast, good for hackathon
REPLICATE_IMAGE_MODEL_HQ = "black-forest-labs/flux-dev"  # Higher quality, slower

# Voiceover uses Google Cloud Text-to-Speech (same GOOGLE_APPLICATION_CREDENTIALS)


# ============================================
# AGENT CONFIGURATION
# ============================================

# Agent names and ports
ORCHESTRATOR_NAME = "adboard-orchestrator"
ORCHESTRATOR_PORT = 8000

RESEARCH_AGENT_NAME = "adboard-research"
RESEARCH_AGENT_PORT = 8001

CREATIVE_AGENT_NAME = "adboard-creative"
CREATIVE_AGENT_PORT = 8002

PRODUCTION_AGENT_NAME = "adboard-production"
PRODUCTION_AGENT_PORT = 8003

# For local testing, use localhost endpoints
# For production, replace with your deployed URLs
LOCAL_ENDPOINT_BASE = "http://localhost"


# ============================================
# DEFAULTS
# ============================================

DEFAULT_NUM_SEARCH_RESULTS = 15
DEFAULT_AD_DURATION = 45  # seconds
DEFAULT_STORYBOARD_FRAMES = 8
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_CITY = "Providence, RI"


# ============================================
# OUTPUT PATHS
# ============================================

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
STORYBOARD_DIR = os.path.join(OUTPUT_DIR, "storyboards")
VOICEOVER_DIR = os.path.join(OUTPUT_DIR, "voiceovers")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")

# Create directories if they don't exist
for dir_path in [OUTPUT_DIR, STORYBOARD_DIR, VOICEOVER_DIR, PDF_DIR]:
    os.makedirs(dir_path, exist_ok=True)


# ============================================
# PROMPTS
# ============================================

RESEARCH_ANALYSIS_PROMPT = """You are an expert advertising analyst. Analyze these YouTube ad videos and identify patterns that make them successful.

Videos to analyze:
{video_data}

Industry: {industry}
Product Type: {product_type}

Provide your analysis in this exact JSON format:
{{
    "viral_patterns": ["pattern1", "pattern2", ...],
    "recommended_style": "testimonial|product-demo|story|humor|emotional",
    "key_phrases": ["phrase1", "phrase2", ...],
    "avg_hook_length": 5,
    "common_ctas": ["cta1", "cta2", ...],
    "insights": "Brief summary of what works"
}}
"""

SCRIPT_WRITING_PROMPT = """You are an expert advertising copywriter. Write a {duration}-second ad script for {product_name}.

Unique Selling Point: {usp}
Tone: {tone}
Target Audience: {audience}

Based on research, successful ads in this industry use:
{patterns}

Write the script in this format:

SCENE 1 (0-{scene1_end}s):
[Visual: Description of what we see]
VOICEOVER: "The spoken words"

SCENE 2 ({scene1_end}-{scene2_end}s):
[Visual: Description]
VOICEOVER: "Words"

... continue for all scenes ...

FINAL SCENE:
[Visual: Logo and CTA]
VOICEOVER: "Call to action"

Make it compelling, memorable, and true to the brand voice. The hook should grab attention in the first 3 seconds.
"""

COST_ESTIMATION_PROMPT = """You are a video production cost estimator. Analyze these scenes and provide a realistic budget estimate.

Scenes:
{scenes}

City: {city}
Budget Level: {budget_level}

Standard rates to consider:
- Actor (non-union, 4hr half-day): $200-400
- Location permit (basic): $100-500
- Equipment rental (basic kit): $200-500/day
- Food/craft services: $15-25/person
- Props (varies widely)
- Post-production (basic edit): $300-800

Provide your estimate in this JSON format:
{{
    "total": 0000,
    "breakdown": {{
        "actors": 0000,
        "location": 0000,
        "equipment": 0000,
        "props": 0000,
        "food": 0000,
        "post_production": 0000,
        "contingency": 0000
    }},
    "assumptions": ["assumption1", "assumption2"],
    "budget_tips": ["tip1", "tip2", "tip3"]
}}
"""
