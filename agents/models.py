"""
Shared message models for agent communication.
All agents import from here to ensure consistency.
"""

from typing import Optional

from uagents import Model

# ============================================
# ORCHESTRATOR <-> USER (via Chat Protocol)
# ============================================
# Note: Chat Protocol uses ChatMessage with TextContent
# These are handled by the chat_protocol module


# ============================================
# ORCHESTRATOR <-> RESEARCH AGENT
# ============================================


class ResearchRequest(Model):
    """Request from Orchestrator to Research Agent"""

    industry: str  # e.g., "food", "construction", "fitness"
    product_type: str  # e.g., "taco truck", "roofing service"
    target_audience: str  # e.g., "young professionals", "homeowners"
    num_results: int = 15  # Number of videos to analyze


class ResearchResponse(Model):
    """Response from Research Agent to Orchestrator"""

    viral_patterns: list  # Common hooks, CTAs, styles found
    top_videos: list  # [{title, views, channel, url, duration}]
    avg_video_length: int  # Average length in seconds
    recommended_style: str  # "testimonial", "product-demo", "story", etc.
    key_phrases: list  # Successful phrases/hooks found
    success: bool = True
    error: Optional[str] = None


# ============================================
# ORCHESTRATOR <-> CREATIVE DIRECTOR
# ============================================


class CreativeRequest(Model):
    """Request from Orchestrator to Creative Director"""

    research_data: dict  # Full research response as dict
    product_name: str  # Name of the product/business
    unique_selling_point: str  # What makes it special
    target_duration: int = 45  # Target ad length in seconds (30 or 60)
    tone: str = "friendly"  # "funny", "professional", "emotional", "energetic"
    voice_gender: str = "female"  # "male" or "female"


class CreativeResponse(Model):
    """Response from Creative Director to Orchestrator"""

    script_text: str  # Full script with timing markers
    scenes: list  # [{scene_num, start_time, end_time, visual, voiceover}]
    storyboard_frames: list  # [{scene_num, image_url, description}]
    voiceover_url: Optional[str] = None  # URL to audio file
    voiceover_duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


# ============================================
# CREATIVE DIRECTOR <-> SUB-AGENTS
# ============================================


class ScriptRequest(Model):
    """Request to Script Writer"""

    research_data: dict
    product_name: str
    unique_selling_point: str
    target_duration: int
    tone: str


class ScriptResponse(Model):
    """Response from Script Writer"""

    script_text: str
    scenes: list  # Parsed scene breakdown
    voiceover_text: str  # Clean text for TTS (no stage directions)
    estimated_duration: int
    success: bool = True
    error: Optional[str] = None


class StoryboardRequest(Model):
    """Request to Storyboard Generator"""

    scenes: list  # Scene descriptions from script
    style: str = "cinematic"  # "realistic", "illustrated", "cinematic"
    aspect_ratio: str = "16:9"


class StoryboardResponse(Model):
    """Response from Storyboard Generator"""

    frames: list  # [{scene_num, image_url, description}]
    success: bool = True
    error: Optional[str] = None


class VoiceoverRequest(Model):
    """Request to Voiceover Agent"""

    script_text: str  # Clean voiceover text
    voice_gender: str = "female"
    voice_style: str = "professional"  # "professional", "friendly", "energetic"


class VoiceoverResponse(Model):
    """Response from Voiceover Agent"""

    audio_url: str  # URL or local path to audio
    duration_seconds: float
    success: bool = True
    error: Optional[str] = None


# ============================================
# ORCHESTRATOR <-> PRODUCTION AGENT
# ============================================


class ProductionRequest(Model):
    """Request from Orchestrator to Production Agent"""

    scenes: list  # Scene descriptions with requirements
    city: str  # City for location search
    budget_level: str = "medium"  # "low", "medium", "high"


class ProductionResponse(Model):
    """Response from Production Agent to Orchestrator"""

    cost_estimate: dict  # {total, breakdown: {actors, location, equipment, etc}}
    locations: list  # [{name, address, price_estimate, rating}]
    budget_tips: list  # Money-saving suggestions
    pdf_path: Optional[str] = None  # Path to generated PDF
    success: bool = True
    error: Optional[str] = None


# ============================================
# FINAL OUTPUT MODEL
# ============================================


class AdBoardOutput(Model):
    """Complete output package from AdBoard AI"""

    # Research
    industry_insights: dict

    # Creative
    script: str
    scenes: list
    storyboard_frames: list
    voiceover_url: Optional[str]

    # Production
    cost_estimate: dict
    recommended_locations: list
    budget_tips: list

    # Deliverable
    pdf_path: Optional[str]

    success: bool = True
    error: Optional[str] = None
