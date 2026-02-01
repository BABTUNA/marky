"""
Comprehensive PDF Builder Agent

Generates a complete production deliverable PDF with ALL research, analysis,
script, storyboard, budget, and production details.
"""

import os
from datetime import datetime
from pathlib import Path

from agents.campaign_strategy_content import (
    get_campaign_strategy_section,
    get_enhanced_next_steps,
)

try:
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Flowable,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus import Image as RLImage

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PipelineDiagram(Flowable):
    """Custom flowable for drawing the pipeline diagram with arrows."""

    def __init__(self, width, height, pipeline_steps):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.pipeline_steps = pipeline_steps

    def draw(self):
        canvas = self.canv
        x = 50
        y = self.height - 30
        box_width = 65
        box_height = 28
        arrow_size = 8

        colors_list = [
            "#e74c3c",
            "#3498db",
            "#9b59b6",
            "#2ecc71",
            "#f39c12",
            "#1abc9c",
            "#e67e22",
            "#34495e",
            "#8e44ad",
            "#16a085",
        ]

        for i, step in enumerate(self.pipeline_steps):
            color_hex = colors_list[i % len(colors_list)]
            color = HexColor(color_hex)

            canvas.setFillColor(color)
            canvas.roundRect(
                x, y - box_height, box_width, box_height, 4, fill=1, stroke=0
            )

            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 7)
            step_name = step.replace("_", " ").title()
            canvas.drawCentredString(
                x + box_width / 2, y - box_height / 2 - 3, step_name[:12]
            )

            if i < len(self.pipeline_steps) - 1:
                canvas.setStrokeColor(color)
                canvas.setLineWidth(2)
                canvas.line(
                    x + box_width,
                    y - box_height / 2,
                    x + box_width + 12,
                    y - box_height / 2,
                )
                canvas.setFillColor(color)
                canvas.line(
                    x + box_width + 12,
                    y - box_height / 2,
                    x + box_width + 6,
                    y - box_height / 2 - 4,
                )
                canvas.line(
                    x + box_width + 12,
                    y - box_height / 2,
                    x + box_width + 6,
                    y - box_height / 2 + 4,
                )

            x += box_width + 15


class PDFBuilderAgent:
    """Builds comprehensive production package PDFs."""

    def __init__(self):
        self.output_dir = Path("output/pdfs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def run(
        self,
        product: str,
        industry: str,
        duration: int,
        tone: str,
        city: str,
        previous_results: dict,
    ) -> dict:
        """Build comprehensive PDF package."""

        if not REPORTLAB_AVAILABLE:
            return {
                "error": "ReportLab not installed",
                "text_summary": self._generate_text_summary(product, previous_results),
            }

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_product = product.replace(" ", "_").replace("/", "-")[:20]
            filename = f"AdBoard_{safe_product}_{timestamp}.pdf"
            filepath = self.output_dir / filename

            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch,
            )

            story = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=26,
                spaceAfter=20,
                textColor=HexColor("#1a1a2e"),
                fontName="Helvetica-Bold",
            )

            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=14,
                spaceBefore=15,
                spaceAfter=10,
                textColor=HexColor("#16213e"),
                fontName="Helvetica-Bold",
            )

            subheading_style = ParagraphStyle(
                "SubHeading",
                parent=styles["Heading3"],
                fontSize=11,
                spaceBefore=8,
                spaceAfter=5,
                textColor=HexColor("#0f3460"),
                fontName="Helvetica-Bold",
            )

            body_style = ParagraphStyle(
                "Body", parent=styles["Normal"], fontSize=9, spaceBefore=3, spaceAfter=3
            )
            body_small = ParagraphStyle(
                "BodySmall",
                parent=styles["Normal"],
                fontSize=7,
                spaceBefore=2,
                spaceAfter=2,
            )
            quote_style = ParagraphStyle(
                "Quote", parent=body_style, alignment=1, leftIndent=20, rightIndent=20
            )

            research = previous_results.get("research", {})
            script_data = previous_results.get("script_writer", {})
            image_data = previous_results.get("image_generator", {})
            cost_data = previous_results.get("cost_estimator", {})
            location_data = previous_results.get("location_scout", {})
            trend_data = previous_results.get("trend_analyzer", {})
            voiceover = previous_results.get("voiceover", {})
            music = previous_results.get("music", {})
            video = previous_results.get("video_assembly", {})
            social = previous_results.get("social_media", {})

            # ==================== COVER PAGE ====================
            story.append(Spacer(1, 2 * inch))
            story.append(Paragraph("🎬 COMPLETE CAMPAIGN PACKAGE", title_style))
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph(f"<b>{product.upper()}</b>", title_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(
                Paragraph(f"{duration}-Second {tone.title()} Advertisement", body_style)
            )
            story.append(Paragraph(f"Industry: {industry.title()}", body_style))
            if city:
                story.append(Paragraph(f"Target Market: {city}", body_style))
            story.append(Spacer(1, 0.5 * inch))

            summary = research.get("research_summary", {})
            story.append(Paragraph("<b>Research Data Collected:</b>", subheading_style))
            story.append(
                Paragraph(
                    f"• YouTube Videos Analyzed: {summary.get('youtube_videos', 0)}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"• Competitors Researched: {summary.get('competitors_found', 0)}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"• Google Reviews Analyzed: {summary.get('google_reviews', 0)}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"• Yelp Reviews Analyzed: {summary.get('yelp_reviews', 0)}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"• Keywords Analyzed: {summary.get('keywords_analyzed', 0)}",
                    body_style,
                )
            )

            story.append(Spacer(1, 0.5 * inch))
            story.append(
                Paragraph(
                    f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                    body_small,
                )
            )
            story.append(
                Paragraph(
                    "Powered by AdBoard AI - 12-Agent Orchestration System", body_small
                )
            )
            story.append(PageBreak())

            # ==================== EXECUTIVE SUMMARY ====================
            story.append(Paragraph("EXECUTIVE SUMMARY", title_style))
            story.append(Spacer(1, 0.15 * inch))

            story.append(Paragraph("<b>Project Overview:</b>", subheading_style))
            story.append(
                Paragraph(
                    f"This production package contains comprehensive market research, creative strategy, and production "
                    f"planning for a {duration}-second {tone} advertisement promoting {product} in the {industry} industry.",
                    body_style,
                )
            )

            if cost_data and not cost_data.get("error"):
                total = cost_data.get("summary", {}).get("total", 0) or cost_data.get(
                    "total", 0
                )
                if total:
                    story.append(Spacer(1, 0.15 * inch))
                    story.append(
                        Paragraph(f"<b>Estimated Budget:</b> ${total:,}", body_style)
                    )
                    level = cost_data.get("summary", {}).get(
                        "budget_level", cost_data.get("budget_level", "")
                    )
                    if level:
                        story.append(
                            Paragraph(f"Budget Level: {level.title()}", body_style)
                        )

            if location_data and location_data.get("locations"):
                story.append(
                    Paragraph(
                        f"Potential Filming Locations: {len(location_data['locations'])}",
                        body_style,
                    )
                )

            if script_data:
                scenes = script_data.get("scenes", [])
                story.append(
                    Paragraph(f"Script Structure: {len(scenes)} scenes", body_style)
                )

            insights = research.get("insights", [])
            if insights:
                story.append(Spacer(1, 0.15 * inch))
                story.append(
                    Paragraph("<b>Key Strategic Insights:</b>", subheading_style)
                )
                for insight in insights[:6]:
                    clean = (
                        str(insight)
                        .replace("🎬", "")
                        .replace("✅", "")
                        .replace("❌", "")
                        .replace("💡", "")
                        .strip()
                    )
                    story.append(Paragraph(f"• {clean}", body_style))

            story.append(PageBreak())

            # ==================== PIPELINE OVERVIEW ====================
            story.append(Paragraph("RESEARCH & PRODUCTION PROCESS", title_style))
            story.append(Spacer(1, 0.15 * inch))
            story.append(
                Paragraph(
                    "This deliverable was created through our multi-agent AI pipeline, combining advanced research "
                    "with creative generation to produce a complete production package.",
                    body_style,
                )
            )
            story.append(Spacer(1, 0.15 * inch))

            pipeline_steps = [
                "research",
                "trend_analyzer",
                "script_writer",
                "image_generator",
                "voiceover",
                "music",
                "video_assembly",
                "cost_estimator",
                "location_scout",
                "pdf_builder",
            ]

            diagram = PipelineDiagram(7.5 * inch, 1.2 * inch, pipeline_steps)
            story.append(diagram)
            story.append(Spacer(1, 0.2 * inch))

            step_descriptions = {
                "research": "Collects YouTube trends, competitor data, reviews, and keyword insights",
                "trend_analyzer": "Extracts viral patterns, hooks, visual styles, and CTAs",
                "script_writer": "Writes scene-by-scene script with visual and voiceover details",
                "image_generator": "Creates storyboard frames for each scene",
                "voiceover": "Generates professional TTS voiceover from script",
                "music": "Selects or generates background music matching tone",
                "video_assembly": "Combines images, voiceover, and music into final video",
                "cost_estimator": "Calculates detailed production budget and requirements",
                "location_scout": "Finds filming locations with permits and pricing",
                "pdf_builder": "Compiles all data into this comprehensive package",
            }

            for i, step in enumerate(pipeline_steps):
                desc = step_descriptions.get(step, step)
                story.append(
                    Paragraph(
                        f"{i + 1}. <b>{step.replace('_', ' ').title()}</b>: {desc}",
                        body_style,
                    )
                )

            story.append(PageBreak())

            # ==================== MARKET RESEARCH ====================
            story.append(Paragraph("MARKET RESEARCH ANALYSIS", title_style))

            # Competitor Analysis
            local_intel = research.get("local_intel", {})
            if local_intel:
                story.append(Paragraph("Competitor Analysis", heading_style))

                top_comps = local_intel.get("top_competitors", [])
                if top_comps:
                    story.append(
                        Paragraph("Top Competitors in Target Market:", subheading_style)
                    )
                    for i, comp in enumerate(top_comps[:8], 1):
                        story.append(Paragraph(f"{i}. {comp}", body_style))

                what_top = local_intel.get("what_top_competitors_do", [])
                if what_top:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph("✅ What Top Competitors Do Right:", subheading_style)
                    )
                    for item in what_top[:6]:
                        story.append(Paragraph(f"• {item}", body_style))

                what_avoid = local_intel.get("what_to_avoid", [])
                if what_avoid:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph(
                            "❌ Common Failure Patterns to Avoid:", subheading_style
                        )
                    )
                    for item in what_avoid[:6]:
                        story.append(Paragraph(f"• {item}", body_style))

                differentiators = local_intel.get("differentiators", [])
                if differentiators:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph(
                            "💡 Recommended Differentiation Angles:", subheading_style
                        )
                    )
                    for diff in differentiators[:4]:
                        angle = diff.get("angle", "")
                        hook = diff.get("hook", "")
                        story.append(Paragraph(f"• <b>{angle}</b>: {hook}", body_style))

                story.append(Spacer(1, 0.15 * inch))

            # Competitor Map Image (if available)
            competitor_map_path = research.get("competitor_map_path")
            if competitor_map_path and os.path.exists(competitor_map_path):
                story.append(Paragraph("Competitor Location Map", heading_style))
                try:
                    # Add the map image, scaled to fit
                    map_img = RLImage(
                        competitor_map_path, width=6 * inch, height=4.5 * inch
                    )
                    story.append(map_img)
                    story.append(
                        Paragraph(
                            "<i>Red markers show competitor locations in the target market area</i>",
                            body_small,
                        )
                    )
                    story.append(Spacer(1, 0.15 * inch))
                except Exception as e:
                    story.append(
                        Paragraph(f"(Map image could not be loaded: {e})", body_small)
                    )

            # Customer Voice
            google_reviews = research.get("google_reviews", {})
            yelp_reviews = research.get("yelp_reviews", {})

            if google_reviews or yelp_reviews:
                story.append(Paragraph("Customer Voice Analysis", heading_style))

                all_pain = []
                if google_reviews:
                    all_pain.extend(google_reviews.get("pain_points", []))
                if yelp_reviews:
                    all_pain.extend(yelp_reviews.get("pain_points", []))

                if all_pain:
                    story.append(
                        Paragraph(
                            "😤 Customer Pain Points to Address in Ad:",
                            subheading_style,
                        )
                    )
                    for pain in all_pain[:8]:
                        clean = (
                            str(pain).get("point", pain)
                            if isinstance(pain, dict)
                            else pain
                        )
                        story.append(Paragraph(f"• {clean}", body_style))

                all_desires = google_reviews.get("desires", [])
                if all_desires:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph("💭 Customer Desires & Wants:", subheading_style)
                    )
                    for desire in all_desires[:6]:
                        clean = (
                            str(desire).get("desire", desire)
                            if isinstance(desire, dict)
                            else desire
                        )
                        story.append(Paragraph(f"• {clean}", body_style))

                all_praise = []
                if google_reviews:
                    all_praise.extend(google_reviews.get("praise_quotes", []))
                if yelp_reviews:
                    all_praise.extend(yelp_reviews.get("praise_points", []))

                if all_praise:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph(
                            "🏆 What Customers Love (Use as Proof):", subheading_style
                        )
                    )
                    for praise in all_praise[:6]:
                        clean = (
                            str(praise).get("praise", praise)
                            if isinstance(praise, dict)
                            else praise
                        )
                        story.append(Paragraph(f"• {clean}", body_style))

                all_quotes = google_reviews.get(
                    "praise_quotes", []
                ) + google_reviews.get("complaint_quotes", [])
                if all_quotes[:3]:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph("💬 Actual Customer Quotes:", subheading_style)
                    )
                    for quote in all_quotes[:4]:
                        story.append(Paragraph(f'"{quote}"', quote_style))

                story.append(Spacer(1, 0.15 * inch))

            # Keyword Trends
            trends = research.get("keyword_trends", {})
            if trends:
                story.append(Paragraph("Keyword & Trend Analysis", heading_style))

                kw_data = trends.get("keyword_data", [])
                if kw_data:
                    story.append(Paragraph("Target Keywords for Ad:", subheading_style))
                    table_data = [["Keyword", "Search Volume", "CPC ($)"]]
                    for kw in kw_data[:10]:
                        table_data.append(
                            [
                                kw.get("keyword", ""),
                                f"{kw.get('search_volume', 0):,}",
                                f"${kw.get('cpc', 0):.2f}",
                            ]
                        )
                    table = Table(
                        table_data, colWidths=[3 * inch, 1.5 * inch, 1 * inch]
                    )
                    table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#16213e")),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, -1), 9),
                                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ]
                        )
                    )
                    story.append(table)
                    story.append(Spacer(1, 0.15 * inch))

                timing = trends.get("timing_recommendations", [])
                if timing:
                    story.append(
                        Paragraph(
                            "📅 Seasonal Timing Recommendations:", subheading_style
                        )
                    )
                    for rec in timing:
                        story.append(Paragraph(f"• {rec}", body_style))

                ad_recs = trends.get("ad_recommendations", [])
                if ad_recs:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph("🎯 Ad Strategy Recommendations:", subheading_style)
                    )
                    for rec in ad_recs[:5]:
                        story.append(Paragraph(f"• {rec}", body_style))

                story.append(Spacer(1, 0.15 * inch))

            # Related Questions (People also ask)
            related_questions = research.get("related_questions", [])
            if related_questions:
                story.append(
                    Paragraph("Content Intent & FAQ Opportunities", heading_style)
                )
                story.append(
                    Paragraph(
                        "Questions customers are asking (from Google 'People also ask'):",
                        subheading_style,
                    )
                )
                for i, q in enumerate(related_questions[:12], 1):
                    story.append(Paragraph(f"{i}. {q}", body_style))
                story.append(Spacer(1, 0.15 * inch))

            # Viral Patterns
            viral_videos = research.get("viral_videos", [])
            if viral_videos:
                story.append(
                    Paragraph("Viral Ad Patterns & Reference Videos", heading_style)
                )

                patterns = research.get("viral_patterns", {})
                hooks = patterns.get("common_hooks", [])
                if hooks:
                    story.append(
                        Paragraph("🎬 Proven Hook Strategies:", subheading_style)
                    )
                    for hook in hooks[:6]:
                        story.append(Paragraph(f"• {hook}", body_style))

                styles = patterns.get("visual_styles", [])
                if styles:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph("🎨 Effective Visual Styles:", subheading_style)
                    )
                    for style in styles[:5]:
                        story.append(Paragraph(f"• {style}", body_style))

                ctas = patterns.get("effective_ctas", [])
                if ctas:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph("📢 Calls-to-Action That Convert:", subheading_style)
                    )
                    for cta in ctas[:5]:
                        story.append(Paragraph(f"• {cta}", body_style))

                story.append(Spacer(1, 0.1 * inch))
                story.append(
                    Paragraph("Top Performing Reference Videos:", subheading_style)
                )
                for i, video in enumerate(viral_videos[:5], 1):
                    title = video.get("title", "Unknown")
                    views = video.get("views", 0)
                    url = video.get("url", "")
                    story.append(
                        Paragraph(f"{i}. <b>{title}</b> ({views:,} views)", body_style)
                    )
                    if url:
                        story.append(Paragraph(f"   URL: {url}", body_small))

            story.append(PageBreak())

            # ==================== SCRIPT ====================
            story.append(Paragraph("COMPLETE SCRIPT", title_style))
            story.append(Spacer(1, 0.15 * inch))

            if script_data:
                script_text = script_data.get("script", "")
                if script_text:
                    story.append(
                        Paragraph(script_text.replace("---", "").strip(), body_style)
                    )
                    story.append(Spacer(1, 0.2 * inch))

                scenes = script_data.get("scenes", [])
                if scenes:
                    story.append(
                        Paragraph("<b>Scene-by-Scene Breakdown:</b>", subheading_style)
                    )
                    for scene in scenes:
                        story.append(
                            Paragraph(
                                f"<b>Scene {scene.get('scene_number', '?')}</b> ({scene.get('timing', '')}) - {scene.get('title', '')}",
                                body_style,
                            )
                        )
                        vo = scene.get("voiceover", "")
                        if vo:
                            story.append(Paragraph(f'   Voiceover: "{vo}"', body_small))
                        visual = scene.get("visual", "")
                        if visual:
                            story.append(
                                Paragraph(
                                    f"   Visual: {visual[:150]}{'...' if len(visual) > 150 else ''}",
                                    body_small,
                                )
                            )
                        audio = scene.get("audio", "")
                        if audio:
                            story.append(Paragraph(f"   Audio: {audio}", body_small))
                        story.append(Spacer(1, 0.05 * inch))

                voiceover_text = script_data.get("voiceover_text", "")
                if voiceover_text:
                    story.append(Spacer(1, 0.15 * inch))
                    story.append(
                        Paragraph("<b>Full Voiceover Script:</b>", subheading_style)
                    )
                    story.append(Paragraph(f'"{voiceover_text}"', quote_style))

            story.append(PageBreak())

            # ==================== CAMPAIGN STRATEGY ====================
            story.append(Paragraph("CAMPAIGN STRATEGY & DISTRIBUTION", title_style))
            story.append(Spacer(1, 0.15 * inch))

            campaign_sections = get_campaign_strategy_section(
                product, industry, city, duration, research, social
            )
            for section in campaign_sections:
                story.append(Paragraph(section["title"], heading_style))
                story.append(Spacer(1, 0.1 * inch))
                for line in section["content"]:
                    if line == "":
                        story.append(Spacer(1, 0.05 * inch))
                    else:
                        story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 0.15 * inch))

            story.append(PageBreak())

            # ==================== STORYBOARD ====================
            story.append(Paragraph("STORYBOARD & VISUAL CONCEPTS", title_style))
            story.append(Spacer(1, 0.15 * inch))

            frames = image_data.get("frames", [])
            if frames:
                story.append(
                    Paragraph(
                        f"<b>{len(frames)} Visual Frames Generated:</b>",
                        subheading_style,
                    )
                )
                story.append(Spacer(1, 0.1 * inch))

                for i, frame in enumerate(frames, 1):
                    story.append(
                        Paragraph(
                            f"<b>Frame {i}</b> - {frame.get('timing', '')}", body_style
                        )
                    )
                    desc = frame.get("description", "N/A")
                    story.append(Paragraph(f"<i>Concept:</i> {desc}", body_small))

                    prompt = frame.get("prompt", "")
                    if prompt:
                        story.append(
                            Paragraph(
                                f"<i>AI Prompt:</i> {prompt[:200]}{'...' if len(prompt) > 200 else ''}",
                                body_small,
                            )
                        )

                    url = frame.get("url", "")
                    if url and url != "Not generated":
                        story.append(
                            Paragraph(
                                f"<i>Image URL:</i> {url[:80]}{'...' if len(url) > 80 else ''}",
                                body_small,
                            )
                        )

                    story.append(Spacer(1, 0.1 * inch))

            story.append(PageBreak())

            # ==================== PRODUCTION BUDGET ====================
            if cost_data and not cost_data.get("error"):
                story.append(Paragraph("PRODUCTION BUDGET & RESOURCES", title_style))
                story.append(Spacer(1, 0.15 * inch))

                summary = cost_data.get("summary", {})
                total = summary.get("total", 0) or cost_data.get("total", 0)
                if total:
                    story.append(
                        Paragraph(
                            f"<b>Total Estimated Budget: ${total:,}</b>", heading_style
                        )
                    )
                    level = summary.get(
                        "budget_level", cost_data.get("budget_level", "")
                    )
                    if level:
                        story.append(
                            Paragraph(f"Budget Level: {level.upper()}", body_style)
                        )
                    story.append(Spacer(1, 0.15 * inch))

                breakdown = cost_data.get("breakdown", {})
                if breakdown:
                    table_data = [["Category", "Amount"]]
                    for category, amount in breakdown.items():
                        cat_name = category.replace("_", " ").title()
                        table_data.append([cat_name, f"${amount:,}"])

                    table = Table(table_data, colWidths=[4 * inch, 1.5 * inch])
                    table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#16213e")),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ]
                        )
                    )
                    story.append(table)
                    story.append(Spacer(1, 0.15 * inch))

                talent = cost_data.get("talent", {})
                if talent.get("line_items"):
                    story.append(Paragraph("Talent Costs:", subheading_style))
                    for item in talent["line_items"]:
                        story.append(
                            Paragraph(
                                f"• {item.get('item', '')}: ${item.get('total', 0):,} "
                                f"({item.get('quantity', 1)} {item.get('unit', 'day')})",
                                body_small,
                            )
                        )

                crew = cost_data.get("crew", {})
                if crew.get("line_items"):
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(Paragraph("Crew Costs:", subheading_style))
                    for item in crew["line_items"]:
                        story.append(
                            Paragraph(
                                f"• {item.get('role', '')}: ${item.get('total', 0):,} "
                                f"({item.get('quantity', 1)} {item.get('unit', 'day')})",
                                body_small,
                            )
                        )

                equipment = cost_data.get("equipment", {})
                if equipment.get("line_items"):
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(Paragraph("Equipment Rental:", subheading_style))
                    for item in equipment["line_items"]:
                        story.append(
                            Paragraph(
                                f"• {item.get('item', '')}: ${item.get('total', 0):,}",
                                body_small,
                            )
                        )

                locations = cost_data.get("locations", {})
                if locations.get("line_items"):
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph("Location & Permit Costs:", subheading_style)
                    )
                    for item in locations["line_items"]:
                        story.append(
                            Paragraph(
                                f"• {item.get('location', '')} ({item.get('type', '')}): ${item.get('cost', 0):,}",
                                body_small,
                            )
                        )

                post = cost_data.get("post_production", {})
                if post.get("line_items"):
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(Paragraph("Post-Production:", subheading_style))
                    for item in post["line_items"]:
                        story.append(
                            Paragraph(
                                f"• {item.get('task', '')}: ${item.get('total', 0):,} "
                                f"({item.get('hours', 0)} hrs @ ${item.get('rate', 0)}/hr)",
                                body_small,
                            )
                        )

                assumptions = cost_data.get("assumptions", [])
                if assumptions:
                    story.append(Spacer(1, 0.15 * inch))
                    story.append(
                        Paragraph("<b>Production Assumptions:</b>", subheading_style)
                    )
                    for assumption in assumptions:
                        story.append(Paragraph(f"• {assumption}", body_style))

                schedule = cost_data.get("schedule", [])
                if schedule:
                    story.append(Spacer(1, 0.15 * inch))
                    story.append(
                        Paragraph("<b>Production Schedule:</b>", subheading_style)
                    )
                    for day in schedule:
                        story.append(
                            Paragraph(
                                f"Day {day.get('day', '?')}: {day.get('activity', '')} ({day.get('hours', '')} hours)",
                                body_style,
                            )
                        )

                tips = cost_data.get("tips", [])
                if tips:
                    story.append(Spacer(1, 0.15 * inch))
                    story.append(
                        Paragraph(
                            "<b>💰 Budget Optimization Tips:</b>", subheading_style
                        )
                    )
                    for tip in tips:
                        story.append(Paragraph(f"• {tip}", body_style))

                story.append(PageBreak())

            # ==================== FILMING LOCATIONS ====================
            locations = location_data.get("locations", []) if location_data else []
            if locations:
                story.append(Paragraph("POTENTIAL FILMING LOCATIONS", title_style))
                story.append(Spacer(1, 0.15 * inch))

                for i, loc in enumerate(locations[:8], 1):
                    story.append(
                        Paragraph(
                            f"<b>{i}. {loc.get('name', 'Unknown')}</b>",
                            subheading_style,
                        )
                    )
                    story.append(
                        Paragraph(f"Address: {loc.get('address', 'N/A')}", body_style)
                    )
                    rating = loc.get("rating", "N/A")
                    price = loc.get("price_level", "Contact for pricing")
                    story.append(Paragraph(f"Rating: {rating} | {price}", body_style))
                    story.append(Spacer(1, 0.1 * inch))

                location_tips = location_data.get("tips", [])
                if location_tips:
                    story.append(
                        Paragraph("<b>📍 Location Scouting Tips:</b>", subheading_style)
                    )
                    for tip in location_tips[:6]:
                        story.append(Paragraph(f"• {tip}", body_style))

                story.append(PageBreak())

            # ==================== TREND ANALYSIS ====================
            if trend_data and not trend_data.get("error"):
                story.append(Paragraph("STRATEGIC RECOMMENDATIONS", title_style))
                story.append(Spacer(1, 0.15 * inch))

                analysis = trend_data.get("analysis", {})
                if analysis:
                    hook = analysis.get("recommended_hook", "")
                    if hook:
                        story.append(
                            Paragraph(f"<b>Recommended Hook:</b> {hook}", body_style)
                        )

                    visual = analysis.get("visual_style", "")
                    if visual:
                        story.append(Spacer(1, 0.1 * inch))
                        story.append(
                            Paragraph(f"<b>Visual Style:</b> {visual}", body_style)
                        )

                    cta = analysis.get("cta", "")
                    if cta:
                        story.append(Spacer(1, 0.1 * inch))
                        story.append(
                            Paragraph(f"<b>Call-to-Action:</b> {cta}", body_style)
                        )

                    key_msgs = analysis.get("key_messages", [])
                    if key_msgs:
                        story.append(Spacer(1, 0.1 * inch))
                        story.append(
                            Paragraph("<b>Key Messages:</b>", subheading_style)
                        )
                        for msg in key_msgs[:5]:
                            story.append(Paragraph(f"• {msg}", body_style))

                    structure = analysis.get("ad_structure", [])
                    if structure:
                        story.append(Spacer(1, 0.1 * inch))
                        story.append(
                            Paragraph("<b>Recommended Structure:</b>", subheading_style)
                        )
                        for item in structure[:6]:
                            story.append(
                                Paragraph(
                                    f"{item.get('time', '')}: {item.get('element', '')} - {item.get('description', '')}",
                                    body_small,
                                )
                            )

                story.append(PageBreak())

            # ==================== GENERATED ASSETS ====================
            story.append(Paragraph("GENERATED ASSETS & OUTPUTS", title_style))
            story.append(Spacer(1, 0.15 * inch))

            if voiceover and not voiceover.get("error"):
                story.append(Paragraph("🎙️ Voiceover:", subheading_style))
                story.append(
                    Paragraph(f"File: {voiceover.get('audio_path', 'N/A')}", body_style)
                )
                duration = voiceover.get("duration", "N/A")
                if duration != "N/A":
                    story.append(Paragraph(f"Duration: {duration} seconds", body_style))

            if music and not music.get("error"):
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph("🎵 Background Music:", subheading_style))
                story.append(
                    Paragraph(f"File: {music.get('music_path', 'N/A')}", body_style)
                )

            if video and not video.get("error"):
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph("🎬 Final Video Assembly:", subheading_style))
                story.append(
                    Paragraph(f"File: {video.get('video_path', 'N/A')}", body_style)
                )

            if social and not social.get("error"):
                captions = social.get("captions", {})
                if captions:
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(
                        Paragraph("📱 Social Media Captions:", subheading_style)
                    )
                    for platform, caption in captions.items():
                        story.append(
                            Paragraph(
                                f"<b>{platform.title()}:</b> {caption[:150]}...",
                                body_small,
                            )
                        )

            story.append(PageBreak())

            # ==================== NEXT STEPS ====================
            story.append(Paragraph("NEXT STEPS & ACTION ITEMS", title_style))
            story.append(Spacer(1, 0.15 * inch))

            # Get enhanced campaign-focused next steps
            enhanced_steps = get_enhanced_next_steps()
            for step in enhanced_steps:
                story.append(Paragraph(step, body_style))
                story.append(Spacer(1, 0.05 * inch))

            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("<b>⚡ Quick Wins:</b>", subheading_style))
            story.append(
                Paragraph(
                    "• Start with TikTok - highest ROI for short-form video", body_style
                )
            )
            story.append(
                Paragraph(
                    "• Use existing customer testimonials in retargeting ads",
                    body_style,
                )
            )
            story.append(
                Paragraph("• Leverage competitor hashtags for discovery", body_style)
            )
            story.append(
                Paragraph(
                    "• Post organically before running paid ads to build social proof",
                    body_style,
                )
            )

            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph("=" * 60, body_small))
            story.append(
                Paragraph(
                    "This document was generated by AdBoard AI - Multi-Agent Advertising Platform",
                    body_small,
                )
            )
            story.append(Paragraph(f"Document ID: {timestamp}", body_small))

            # Build PDF
            doc.build(story)

            return {
                "pdf_path": str(filepath),
                "filename": filename,
                "pages": len(story) // 3 + 5,
                "sections": [
                    "Cover",
                    "Executive Summary",
                    "Pipeline",
                    "Market Research",
                    "Script",
                    "Campaign Strategy",
                    "Storyboard",
                    "Budget",
                    "Locations",
                    "Strategic Recommendations",
                    "Assets",
                    "Campaign Roadmap",
                ],
            }

        except Exception as e:
            import traceback

            traceback.print_exc()
            return {
                "error": str(e),
                "text_summary": self._generate_text_summary(product, previous_results),
            }

    def _generate_text_summary(self, product: str, previous_results: dict) -> str:
        """Generate text summary when PDF fails."""
        lines = [f"AD PRODUCTION PACKAGE: {product}", "=" * 60, ""]

        research = previous_results.get("research", {})
        if research:
            summary = research.get("research_summary", {})
            lines.append("RESEARCH SUMMARY:")
            lines.append(f"  - YouTube Videos: {summary.get('youtube_videos', 0)}")
            lines.append(f"  - Competitors: {summary.get('competitors_found', 0)}")
            lines.append(f"  - Google Reviews: {summary.get('google_reviews', 0)}")
            lines.append(f"  - Yelp Reviews: {summary.get('yelp_reviews', 0)}")
            lines.append(f"  - Keywords: {summary.get('keywords_analyzed', 0)}")
            lines.append("")

        script = previous_results.get("script_writer", {})
        if script:
            lines.append("SCRIPT:")
            lines.append(script.get("script", "Not available")[:1000])
            lines.append("")

        cost = previous_results.get("cost_estimator", {})
        if cost:
            lines.append(f"BUDGET: ${cost.get('total', 'N/A')}")
            lines.append("")

        return "\n".join(lines)
