"""
Campaign Strategy Section for PDF Builder

This module contains enhanced campaign-focused sections to add to the PDF:
- Campaign Strategy & Distribution
- A/B Testing Recommendations  
- Multi-Platform Distribution Timeline
"""

def get_campaign_strategy_section(product, industry, city, duration, research, social):
    """Generate campaign strategy content for PDF."""
    
    sections = []
    
    # Campaign Overview
    sections.append({
        "title": "📊 CAMPAIGN STRATEGY",
        "content": [
            f"This is a complete multi-format advertising campaign for {product}, not just a single ad. "
            f"The campaign includes multiple video assets optimized for different platforms and audience segments.",
            "",
            "<b>Campaign Assets:</b>",
            f"• Long-form Concept Video ({duration}s) - Black & white storyboard for client approval and concept validation",
            "• Short-form Viral Video (15s) - Photorealistic TikTok/Instagram Reels optimized content",
            "• Complete PDF Package - Research, strategy, scripts, and production details",
            "• Social Media Assets - Platform-specific captions and hashtags",
        ]
    })
    
    # Multi-Platform Distribution
    sections.append({
        "title": "📱 MULTI-PLATFORM DISTRIBUTION STRATEGY",
        "content": [
            "<b>Storyboard Video (30-60s) - B&W Concept:</b>",
            "• Platform: Client presentations, internal review, pitch decks",
            "• Purpose: Concept validation before full production",
            "• Format: Silent black & white pencil sketch animation",
            "",
            "<b>Viral Short (15s) - Photorealistic:</b>",
            "• Platforms: TikTok, Instagram Reels, YouTube Shorts",
            "• Purpose: High-engagement social media marketing",
            "• Format: Vertical 9:16, photorealistic, trending audio",
            "• Target: Gen Z and Millennial audiences",
            "",
            "<b>Distribution Priorities:</b>",
            "1. <b>Week 1-2:</b> TikTok + Instagram Reels (organic + paid)",
            "2. <b>Week 2-3:</b> YouTube Shorts + Facebook Stories",
            "3. <b>Week 3-4:</b> Retargeting campaigns based on top performers",
            "4. <b>Ongoing:</b> A/B testing and optimization",
        ]
    })
    
    # A/B Testing Recommendations
    sections.append({
        "title": "🧪 A/B TESTING RECOMMENDATIONS",
        "content": [
            "Test multiple variations to optimize campaign performance:",
            "",
            "<b>Hook Variations (Test First 3 Seconds):</b>",
            "• Version A: Problem-focused ('Tired of X?')",
            "• Version B: Benefit-focused ('Get X in Y seconds')",
            "• Version C: Curiosity-based ('The secret to X')",
            "",
            "<b>Call-to-Action Variations:</b>",
            "• Direct: 'Visit us today at [location]'",
            "• Offer-based: 'Get 20% off your first order'",
            "• Social proof: 'Join 10,000+ happy customers'",
            "",
            "<b>Visual Style Tests:</b>",
            "• Fast-paced cuts vs. smooth transitions",
            "• With text overlays vs. clean visuals only",
            "• Different music/sound styles",
            "",
            "<b>Targeting Segments:</b>",
            "• Age groups: 18-24, 25-34, 35-44, 45+",
            "• Interests: Food lovers, health-conscious, convenience-seekers",
            f"• Geographic: {city} metro area, surrounding suburbs, tourists",
            "",
            "<b>Success Metrics to Track:</b>",
            "• View-through rate (target: >50% for 15s video)",
            "• Click-through rate (target: >2%)", 
            "• Cost per click (benchmark against industry avg)",
            "• Conversion rate (track to purchase/visit)",
            "• Engagement rate (likes, comments, shares)",
        ]
    })
    
    # Budget Allocation
    sections.append({
        "title": "💰 CAMPAIGN BUDGET ALLOCATION",
        "content": [
            "<b>Recommended Spend Distribution:</b>",
            "",
            "Platform Testing Phase (Week 1-2): $500-1,000",
            "• TikTok Ads: 40% ($200-400)",
            "• Instagram Reels: 40% ($200-400)",
            "• YouTube Shorts: 20% ($100-200)",
            "",
            "Scale Phase (Week 3-4): $1,500-3,000",
            "• Top performer: 60%",
            "• Second best: 30%",
            "• Experimental: 10%",
            "",
            "<b>Total Recommended Campaign Budget: $2,000-4,000</b>",
            "Expected reach: 50,000-150,000 impressions",
            "Expected engagement: 2,000-8,000 interactions",
        ]
    })
    
    # Timeline
    sections.append({
        "title": "📅 4-WEEK CAMPAIGN TIMELINE",
        "content": [
            "<b>Week 1: Launch & Test</b>",
            "• Day 1-2: Deploy all video assets to platforms",
            "• Day 3-5: Monitor initial performance, adjust targeting",
            "• Day 6-7: Analyze data, identify top performers",
            "",
            "<b>Week 2: Optimize</b>",
            "• Day 8-10: Launch A/B tests on top platforms",
            "• Day 11-12: Scale budget to winning variations",
            "• Day 13-14: Create retargeting audiences",
            "",
            "<b>Week 3: Scale</b>",
            "• Day 15-17: Increase spend on proven winners",
            "• Day 18-19: Launch lookalike audiences",
            "• Day 20-21: Test new geographic markets",
            "",
            "<b>Week 4: Maximize & Analyze</b>",
            "• Day 22-25: Push for maximum reach",
            "• Day 26-27: Collect final performance data",
            "• Day 28: Complete campaign analysis report",
        ]
    })
    
    return sections


def get_enhanced_next_steps():
    """Get enhanced next steps with campaign focus."""
    return [
        "<b>Immediate Actions (This Week):</b>",
        "1. Review and approve campaign strategy and creative direction",
        "2. Set up platform advertising accounts (TikTok Ads, Meta Business)",
        "3. Define campaign budget and duration",
        "4. Prepare tracking pixels and conversion events",
        "",
        "<b>Production Phase (Week 1-2):</b>",
        "5. Generate VEO 3 short-form viral video (15s)",
        "6. Create platform-specific variations if needed",
        "7. Set up A/B test framework and tracking",
        "8. Prepare social media calendar",
        "",
        "<b>Launch Phase (Week 2-3):</b>",
        "9. Deploy campaign across all platforms",
        "10. Monitor performance in real-time",
        "11. Adjust targeting and budget allocation",
        "12. Engage with comments and audience",
        "",
        "<b>Optimization Phase (Week 3-4):</b>",
        "13. Scale successful variations",
        "14. Test new audiences and creatives",
        "15. Prepare performance report",
        "16. Plan follow-up campaigns",
    ]
