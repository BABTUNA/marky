"""
Dummy research data for testing agents while teammate builds the real Research Agent.

This simulates what the Research Agent would return after:
1. Searching YouTube for viral ads in the industry
2. Analyzing video metadata (views, likes, duration)
3. Extracting patterns from successful ads

Replace this with real Research Agent output once ready.
"""

# Simulated research output for a "taco truck" in the "food" industry
DUMMY_RESEARCH_DATA = {
    "industry": "food",
    "product": "taco truck",
    "query_terms": [
        "taco truck commercial",
        "food truck advertisement",
        "street food marketing video",
    ],
    "top_videos": [
        {
            "title": "Best Taco Truck in LA - Customer Reactions",
            "channel": "FoodieVibes",
            "views": 2_400_000,
            "likes": 89_000,
            "duration": "0:42",
            "description": "Watch customers try our authentic street tacos for the first time...",
            "url": "https://youtube.com/watch?v=example1",
        },
        {
            "title": "How We Grew Our Taco Business to $1M",
            "channel": "SmallBizSuccess",
            "views": 1_800_000,
            "likes": 67_000,
            "duration": "0:58",
            "description": "From a single truck to a taco empire - our journey...",
            "url": "https://youtube.com/watch?v=example2",
        },
        {
            "title": "Street Tacos That Will Change Your Life",
            "channel": "TasteExplorers",
            "views": 3_100_000,
            "likes": 124_000,
            "duration": "0:35",
            "description": "These aren't your average tacos. Experience authentic flavor...",
            "url": "https://youtube.com/watch?v=example3",
        },
        {
            "title": "Food Truck Marketing That Actually Works",
            "channel": "MarketingPros",
            "views": 890_000,
            "likes": 45_000,
            "duration": "0:51",
            "description": "Learn the secrets behind viral food truck campaigns...",
            "url": "https://youtube.com/watch?v=example4",
        },
        {
            "title": "Taco Tuesday Gone Viral - Our Story",
            "channel": "TacoLoco",
            "views": 1_200_000,
            "likes": 56_000,
            "duration": "0:39",
            "description": "How a simple idea turned into a movement...",
            "url": "https://youtube.com/watch?v=example5",
        },
    ],
    "patterns_identified": {
        "common_hooks": [
            "Question opener: 'Craving something different?'",
            "Bold claim: 'The best tacos you'll ever taste'",
            "Social proof: 'Over 10,000 customers can't be wrong'",
            "Scarcity: 'Only here until 3pm'",
            "Curiosity: 'What makes our salsa so addictive?'",
        ],
        "successful_structures": [
            "Hook (0-3s) → Problem (3-8s) → Solution/Product (8-25s) → Social Proof (25-35s) → CTA (35-45s)",
            "Customer testimonial montage with upbeat music",
            "Behind-the-scenes 'making of' with founder voiceover",
            "Before/after taste reaction format",
        ],
        "visual_styles": [
            "Close-up food shots with steam/sizzle",
            "Bright, warm color grading (oranges, yellows)",
            "Quick cuts (2-3 second shots)",
            "Hand-held camera for authenticity",
            "Text overlays for key points",
        ],
        "audio_patterns": [
            "Upbeat Latin/acoustic music",
            "Natural ambient sounds (sizzling, chopping)",
            "Enthusiastic but authentic voiceover",
            "Customer sound bites",
        ],
        "effective_ctas": [
            "Find us at [location]",
            "Follow us for daily specials",
            "Tag us in your taco pics",
            "Order now on [app]",
            "Visit us today - you won't regret it",
        ],
    },
    "avg_video_length_seconds": 43,
    "avg_views": 1_878_000,
    "avg_likes": 76_200,
    "recommended_approach": {
        "style": "testimonial_with_food_shots",
        "tone": "warm_authentic_enthusiastic",
        "duration": 45,
        "key_elements": [
            "Open with sizzling food close-up",
            "Include 2-3 quick customer reactions",
            "Show the truck and team briefly",
            "End with location and social handles",
        ],
    },
    "competitor_insights": [
        "Most successful ads feature real customers, not actors",
        "Authenticity beats production value",
        "Music choice strongly impacts engagement",
        "Location mention in first 10 seconds increases local engagement",
    ],
}


def get_dummy_research(industry: str = "food", product: str = "taco truck") -> dict:
    """
    Get dummy research data. In production, this would be replaced
    by the actual Research Agent's output.

    Args:
        industry: The industry category
        product: The specific product/business

    Returns:
        dict: Simulated research data
    """
    # For now, return the taco truck data regardless of input
    # Your teammate will replace this with real YouTube API calls
    data = DUMMY_RESEARCH_DATA.copy()
    data["industry"] = industry
    data["product"] = product
    return data


# Additional dummy data for other industries (for testing flexibility)
DUMMY_RESEARCH_FITNESS = {
    "industry": "fitness",
    "product": "fitness app",
    "top_videos": [
        {
            "title": "This App Changed My Life - 30 Day Transformation",
            "channel": "FitLife",
            "views": 5_200_000,
            "likes": 210_000,
            "duration": "0:52",
        }
    ],
    "patterns_identified": {
        "common_hooks": [
            "Transformation reveal",
            "Before/after comparison",
            "'I used to hate working out...'",
            "Celebrity/influencer endorsement",
        ],
        "visual_styles": [
            "High energy, fast cuts",
            "Split screen transformations",
            "Workout montages",
        ],
    },
    "recommended_approach": {
        "style": "transformation_story",
        "tone": "motivational_energetic",
        "duration": 45,
    },
}


DUMMY_RESEARCH_TECH = {
    "industry": "technology",
    "product": "saas product",
    "top_videos": [
        {
            "title": "How We 10x'd Productivity with One Tool",
            "channel": "TechReview",
            "views": 1_800_000,
            "likes": 78_000,
            "duration": "0:48",
        }
    ],
    "patterns_identified": {
        "common_hooks": [
            "Problem-focused opener",
            "Statistics/data point",
            "'What if I told you...'",
            "Demo teaser",
        ],
        "visual_styles": [
            "Clean, minimal UI recordings",
            "Animated graphics",
            "Professional studio lighting",
        ],
    },
    "recommended_approach": {
        "style": "problem_solution_demo",
        "tone": "professional_confident",
        "duration": 60,
    },
}
