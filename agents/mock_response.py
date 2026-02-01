"""
Mock response data for testing ASI:One output without running full pipeline.

Usage:
    from agents.mock_response import MOCK_PIPELINE_RESULT
"""

MOCK_PIPELINE_RESULT = {
    "success": True,
    "results": {
        "research": {
            "industry": "food",
            "product": "donut shop",
            "city": "Boston",
            "competitors_found": 8,
            "google_reviews": 64,
            "yelp_reviews": 27,
            "keywords_analyzed": 0,
            "insights": [
                "Top competitors emphasize fresh, handmade donuts",
                "Customers value unique flavors and Instagram-worthy presentation",
                "Long wait times are a common complaint - highlight fast service",
                "Local coffee quality matters as much as donut quality",
                "Customers want gluten-free and vegan options"
            ],
            "local_intel": {
                "competitors_found": 8,
                "top_competitors": [
                    "Kane's Donuts (4.8★)",
                    "Union Square Donuts (4.7★)",
                    "Blackbird Doughnuts (4.6★)"
                ],
                "differentiators": [
                    "Emphasize specialty flavors",
                    "Highlight fresh daily production",
                    "Showcase local ingredients",
                    "Focus on fast, friendly service",
                    "Promote vegan & gluten-free options"
                ],
                "headline_suggestions": [
                    "Boston's Freshest Handmade Donuts",
                    "Where Every Donut is a Work of Art",
                    "Your Morning Just Got Better"
                ]
            },
            "google_reviews": {
                "pain_points": [
                    "Long wait times during morning rush",
                    "Limited parking",
                    "Runs out of popular flavors"
                ],
                "desires": [
                    "Unique seasonal flavors",
                    "Fresh coffee & espresso",
                    "Instagram-worthy presentation"
                ],
                "praise_quotes": [
                    "Best donuts in Boston, hands down!",
                    "The maple bacon is life-changing",
                    "Fresh every morning, you can taste the difference"
                ]
            },
            "yelp_reviews": {
                "pain_points": [
                    "Inconsistent quality",
                    "High prices",
                    "Small seating area"
                ],
                "praise_points": [
                    "Amazing variety of flavors",
                    "Friendly staff",
                    "Perfect coffee pairing"
                ]
            },
            "ad_hooks": [
                "What if your morning donut was actually... incredible?",
                "Stop settling for stale, boring donuts",
                "The donut shop Boston can't stop talking about",
                "Handmade fresh every morning - taste the difference",
                "Your new favorite morning ritual awaits"
            ]
        },
        
        "script_writer": {
            "script": "Full 5-scene script...",
            "scenes": [
                {
                    "scene_number": 1,
                    "timing": "0-6s",
                    "title": "Hook",
                    "visual": "Close-up of a hand stretching fresh donut dough, sunlight streaming through a bakery window at dawn. Golden, pillowy texture fills the frame.",
                    "audio": "Soft, warm acoustic music with a morning vibe",
                    "voiceover": "What if your morning donut was actually... incredible?"
                },
                {
                    "scene_number": 2,
                    "timing": "6-12s",
                    "title": "Problem",
                    "visual": "Quick cuts of sad, packaged donuts on convenience store shelves. Disappointed faces biting into stale donuts.",
                    "audio": "Music briefly pauses, slight tension",
                    "voiceover": "Most donuts sit in boxes for days. Stale. Boring. Forgettable."
                },
                {
                    "scene_number": 3,
                    "timing": "12-18s",
                    "title": "Solution",
                    "visual": "Warm, inviting shots of the donut shop interior. Baker pulling fresh trays from the oven. Colorful array of unique flavors on display.",
                    "audio": "Music swells - upbeat and energetic",
                    "voiceover": "At [Your Donut Shop], we handmake every donut fresh each morning using local ingredients."
                },
                {
                    "scene_number": 4,
                    "timing": "18-24s",
                    "title": "Proof",
                    "visual": "Happy customers taking first bites, eyes widening with delight. Instagram-worthy close-ups of maple bacon, matcha glaze, and seasonal flavors.",
                    "audio": "Upbeat music continues",
                    "voiceover": "From classic glazed to our famous maple bacon - Bostonians can't stop raving about us."
                },
                {
                    "scene_number": 5,
                    "timing": "24-30s",
                    "title": "CTA",
                    "visual": "Shop exterior with the sunrise. Smiling barista handing donut & coffee through window. Logo and address appear on screen.",
                    "audio": "Music reaches friendly, inviting conclusion",
                    "voiceover": "Visit us tomorrow morning. Your new favorite ritual is waiting. [Shop Name] - Boston's freshest donuts."
                }
            ],
            "voiceover_text": "What if your morning donut was actually... incredible? Most donuts sit in boxes for days. Stale. Boring. Forgettable. At [Your Donut Shop], we handmake every donut fresh each morning using local ingredients. From classic glazed to our famous maple bacon - Bostonians can't stop raving about us. Visit us tomorrow morning. Your new favorite ritual is waiting. [Shop Name] - Boston's freshest donuts.",
            "scene_count": 5,
            "estimated_duration": 30,
            "model_used": "llama-3.3-70b-versatile"
        },
        
        "image_generator": {
            "frames": [
                {"scene": 1, "timing": "0-6s", "description": "Donut dough stretching", "url": "output/frames/frame_1.png"},
                {"scene": 2, "timing": "6-12s", "description": "Sad packaged donuts", "url": "output/frames/frame_2.png"},
                {"scene": 3, "timing": "12-18s", "description": "Bakery interior", "url": "output/frames/frame_3.png"},
                {"scene": 4, "timing": "18-24s", "description": "Happy customers", "url": "output/frames/frame_4.png"},
                {"scene": 5, "timing": "24-30s", "description": "Shop exterior sunrise", "url": "output/frames/frame_5.png"}
            ],
            "model_used": "imagen-3.0-generate-001",
            "total_cost": 0.15
        },
        
        "voiceover": {
            "audio_path": "output/voiceovers/voiceover_donut_30s.mp3",
            "voice_id": "ThT5KcBeYPX3keUQqHPh",
            "voice_name": "Dorothy",
            "duration": 28,
            "cost": 0.03
        },
        
        "music": {
            "suggestions": "Upbeat acoustic morning vibe, 100-120 BPM",
            "search_terms": ["morning acoustic", "upbeat ukulele", "cafe music"],
            "music_path": "output/music/background.mp3"
        },
        
        "audio_mixer": {
            "mixed_audio_path": "output/mixed_audio/final_audio_donut_30s.mp3",
            "duration": 30
        },
        
        "video_assembly": {
            "final_video_path": "output/final/final_donut_shop_30s.mp4",
            "duration": 30,
            "frames_used": 5,
            "resolution": "1920x1080",
            "fps": 30,
            # Mock URL for testing (in production, this gets uploaded to tmpfiles.org)
            "video_url": "https://tmpfiles.org/dl/mock123/donut_shop_ad_30s.mp4"
        },
        
        "pdf_export": {
            "pdf_path": "output/pdfs/Ad_Package_Donut_Shop_Boston.pdf",
            "pages": 8,
            "includes": ["Script", "Storyboard", "Research Summary", "Cost Breakdown", "Competitor Map"],
            # Mock URL for testing (in production, this gets uploaded to tmpfiles.org)
            "pdf_url": "https://tmpfiles.org/dl/mock456/Ad_Package_Donut_Shop_Boston.pdf"
        },
        
        "competitor_map": {
            "map_path": "output/maps/competitor_map.png",
            "competitors_shown": 5,
            "city": "Boston, MA",
            "map_url": None  # Gets populated if uploaded
        },
        
        "cost_estimator": {
            "total": 487.50,
            "breakdown": {
                "images": 0.15,
                "voiceover": 0.03,
                "music": 0.00,
                "crew": 250.00,
                "equipment": 100.00,
                "location": 50.00,
                "editing": 87.32
            },
            "line_items": [
                {"category": "AI Generation", "item": "Image generation (5 frames, Imagen 3)", "cost": 0.15},
                {"category": "AI Generation", "item": "Voiceover (ElevenLabs TTS)", "cost": 0.03},
                {"category": "AI Generation", "item": "Background music (free library)", "cost": 0.00},
                {"category": "Production", "item": "3-person crew (DP, sound, director) - 4 hours", "cost": 250.00},
                {"category": "Production", "item": "Basic camera & lighting package", "cost": 100.00},
                {"category": "Production", "item": "Location permit (bakery shoot)", "cost": 50.00},
                {"category": "Post-Production", "item": "Video editing & color grading", "cost": 87.32}
            ]
        },
        
        "social_media": {
            "hashtags": {
                "primary": ["#BostonDonuts", "#FreshBaked", "#DonutShop", "#BostonEats", "#HandmadeDonuts"],
                "secondary": ["#BreakfastGoals", "#DonutLovers", "#LocalBusiness", "#SupportLocal"]
            },
            "captions": {
                "instagram": "Your morning just got a serious upgrade 🍩☀️ Handmade fresh every day in Boston. What's your go-to flavor? #BostonDonuts #FreshBaked",
                "tiktok": "POV: You just discovered Boston's best kept donut secret 👀🍩 #BostonEats #DonutShop",
                "facebook": "Start your day right with Boston's freshest handmade donuts! ☕🍩 From classic glazed to unique seasonal flavors, we bake everything fresh each morning using local ingredients."
            }
        },
        
        "location_scout": {
            "locations": [
                {"name": "Boston Public Market", "address": "100 Hanover St", "notes": "Great for establishing shots"},
                {"name": "Faneuil Hall", "address": "Faneuil Hall Square", "notes": "Iconic Boston landmark"},
                {"name": "North End Bakery District", "address": "Hanover Street area", "notes": "Authentic bakery atmosphere"}
            ]
        },
        
        "trend_analyzer": {
            "analysis": {
                "recommended_hook": "Close-up of fresh donut being glazed with morning light",
                "visual_style": "Warm, appetizing close-ups with golden morning lighting",
                "cta": "Visit us tomorrow morning - your new favorite ritual awaits",
                "key_messages": [
                    "Handmade fresh daily",
                    "Local ingredients",
                    "Unique flavors",
                    "Perfect with coffee"
                ]
            }
        }
    }
}
