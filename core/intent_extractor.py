"""
Intent Extractor

Parses user messages to extract structured intent for ad creation.
Uses Groq LLM to understand natural language requests.
"""

import json
import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.gemini_client import chat_completion  # Using Google Gemini (Cloud credits!)


def extract_intent(user_input: str) -> dict:
    """
    Extract structured intent from user message using Groq LLM.

    Args:
        user_input: The user's message

    Returns:
        dict with keys:
            - is_ad_request: bool - Is this asking for ad/storyboard creation?
            - product: str - What product/business (e.g., "taco truck")
            - industry: str - Category (e.g., "food", "fitness", "tech")
            - output_type: str - What they want ("script", "storyboard", "video", "pdf", "full")
            - duration: int - Ad length in seconds (30, 45, or 60)
            - tone: str - Style ("professional", "funny", "emotional", "energetic")
            - city: str - City for locations if mentioned
            - ready: bool - Do we have enough info to proceed?
            - missing: list[str] - What info is still needed
    """

    prompt = f"""Analyze this message and extract ad creation intent.

Message: "{user_input}"

We create three deliverables: (1) storyboard video (silent, for development), (2) viral video (ready-to-post with audio), and (3) campaign PDF. The default is to create all three (full_campaign).

Return a JSON object with these exact fields:
{{
    "is_ad_request": true/false,
    "product": "string or null",
    "industry": "string or null (food/fitness/tech/retail/services/construction/beauty/automotive/general)",
    "output_type": "script/storyboard/storyboard_video/full_campaign/video/pdf/full (default: full_campaign)",
    "duration": 30/45/60 (default: 45),
    "tone": "professional/funny/emotional/energetic (default: professional)",
    "city": "string or null",
    "ready": true/false,
    "missing": ["list", "of", "missing", "required", "fields"]
}}

Rules:
1. is_ad_request = true if they want any kind of ad, commercial, storyboard, viral video, marketing, or script
2. product is REQUIRED - if not provided, add "product" to missing
3. output_type defaults to "full_campaign" (storyboard video + viral video + PDF — all three)
4. "full" or "full package" or "everything" or "viral" means output_type = "full_campaign"
5. "pdf" or "production package" or "budget" means output_type = "pdf"
6. "video" or "storyboard video" or "animated" means output_type = "full_campaign" (all three)
7. "script only" or "just script" means output_type = "script"
8. "storyboard" without "video" means output_type = "storyboard" (images only, no video)
9. "storyboard only" or "no viral" means output_type = "storyboard_video" (storyboard + PDF, no viral)
9. duration defaults to 30 if not specified
10. tone defaults to "professional" if not specified
11. ready = true only if we have at least the product
12. Infer industry from product if possible (taco truck -> food, gym -> fitness)

Return ONLY valid JSON, no other text or explanation."""

    try:
        # Use Groq client with automatic model fallback
        response = chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1,
        )

        result_text = response["content"].strip()

        # Try to parse JSON, handling potential markdown code blocks
        if result_text.startswith("```"):
            # Remove markdown code block
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1])

        return json.loads(result_text)

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}, falling back to rule-based intent")
        return extract_intent_simple(user_input)
    except Exception as e:
        print(f"Intent extraction error: {e}, falling back to rule-based intent")
        simple = extract_intent_simple(user_input)
        simple["_fallback"] = True
        return simple


def extract_intent_simple(user_input: str) -> dict:
    """
    Simple rule-based intent extraction (fallback if Groq fails).

    This is less accurate but works without API calls.
    """

    user_lower = user_input.lower()

    result = {
        "is_ad_request": False,
        "product": None,
        "industry": "general",
        "output_type": "full_campaign",
        "duration": 45,
        "tone": "professional",
        "city": None,
        "ready": False,
        "missing": [],
    }

    # Check if it's an ad request
    ad_keywords = [
        "ad",
        "advertisement",
        "commercial",
        "storyboard",
        "script",
        "video",
        "marketing",
        "promo",
        "promotional",
    ]
    if any(kw in user_lower for kw in ad_keywords):
        result["is_ad_request"] = True

    # Output type detection
    if "full package" in user_lower or "everything" in user_lower or "viral" in user_lower:
        result["output_type"] = "full_campaign"
    elif "storyboard only" in user_lower or "no viral" in user_lower:
        result["output_type"] = "storyboard_video"
    elif (
        "pdf" in user_lower
        or "budget" in user_lower
        or "production package" in user_lower
    ):
        result["output_type"] = "pdf"
    elif "video" in user_lower:
        result["output_type"] = "full_campaign"
    elif "script" in user_lower and "storyboard" not in user_lower:
        result["output_type"] = "script"

    # Duration detection
    if "30 second" in user_lower or "30s" in user_lower or "30-second" in user_lower:
        result["duration"] = 30
    elif (
        "60 second" in user_lower
        or "60s" in user_lower
        or "60-second" in user_lower
        or "1 minute" in user_lower
    ):
        result["duration"] = 60

    # Tone detection
    if "funny" in user_lower or "humor" in user_lower or "comedic" in user_lower:
        result["tone"] = "funny"
    elif "emotional" in user_lower or "heartfelt" in user_lower:
        result["tone"] = "emotional"
    elif (
        "energetic" in user_lower or "exciting" in user_lower or "dynamic" in user_lower
    ):
        result["tone"] = "energetic"

    # Common products and industries
    product_industry_map = {
        "taco": ("taco truck", "food"),
        "food truck": ("food truck", "food"),
        "restaurant": ("restaurant", "food"),
        "coffee": ("coffee shop", "food"),
        "gym": ("gym", "fitness"),
        "fitness": ("fitness app", "fitness"),
        "app": ("app", "tech"),
        "software": ("software", "tech"),
        "roofing": ("roofing company", "construction"),
        "plumber": ("plumbing service", "services"),
        "salon": ("salon", "beauty"),
        "car": ("car dealership", "automotive"),
    }

    for keyword, (product, industry) in product_industry_map.items():
        if keyword in user_lower:
            result["product"] = product
            result["industry"] = industry
            break

    # Check if ready
    if result["product"]:
        result["ready"] = True
    else:
        result["missing"] = ["product"]

    return result
