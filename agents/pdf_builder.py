"""
PDF Builder Agent

Generates a professional PDF package with script, storyboard, budget, and locations.
"""

import os
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not installed - PDF generation will be limited")


class PDFBuilderAgent:
    """Builds professional PDF packages."""

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
        """
        Build the PDF package.

        Args:
            product: The product/business
            industry: Industry category
            duration: Ad duration
            tone: Desired tone
            city: City
            previous_results: Results from all previous agents

        Returns:
            dict with PDF path and metadata
        """

        if not REPORTLAB_AVAILABLE:
            return {
                "error": "ReportLab not installed",
                "text_summary": self._generate_text_summary(product, previous_results),
            }

        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_product = product.replace(" ", "_").replace("/", "-")[:20]
            filename = f"AdBoard_{safe_product}_{timestamp}.pdf"
            filepath = self.output_dir / filename

            # Build the PDF
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )

            # Build content
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=20,
                textColor=HexColor("#1a1a2e"),
            )

            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=10,
                textColor=HexColor("#16213e"),
            )

            subheading_style = ParagraphStyle(
                "SubHeading",
                parent=styles["Heading3"],
                fontSize=12,
                spaceBefore=10,
                spaceAfter=5,
            )

            body_style = styles["Normal"]

            # === COVER PAGE ===
            story.append(Spacer(1, 2 * inch))
            story.append(Paragraph("AD STORYBOARD PACKAGE", title_style))
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(f"<b>{product.upper()}</b>", heading_style))
            story.append(Spacer(1, 0.25 * inch))
            story.append(
                Paragraph(f"{duration}-Second {tone.title()} Advertisement", body_style)
            )
            story.append(Paragraph(f"Industry: {industry.title()}", body_style))
            if city:
                story.append(Paragraph(f"Location: {city}", body_style))
            story.append(Spacer(1, inch))
            story.append(
                Paragraph(
                    f"Generated: {datetime.now().strftime('%B %d, %Y')}", body_style
                )
            )
            story.append(Paragraph("Powered by AdBoard AI", body_style))
            story.append(PageBreak())

            # === SCRIPT SECTION ===
            script_data = previous_results.get("script_writer", {})
            if script_data and not script_data.get("error"):
                story.append(Paragraph("SCRIPT", title_style))
                story.append(Spacer(1, 0.25 * inch))

                scenes = script_data.get("scenes", [])
                for scene in scenes:
                    story.append(
                        Paragraph(
                            f"<b>SCENE {scene.get('scene_number', '?')} ({scene.get('timing', '')})</b>",
                            subheading_style,
                        )
                    )
                    story.append(
                        Paragraph(
                            f"<i>Visual:</i> {scene.get('visual', 'N/A')}", body_style
                        )
                    )
                    story.append(
                        Paragraph(
                            f'<i>Voiceover:</i> "{scene.get("voiceover", "N/A")}"',
                            body_style,
                        )
                    )
                    story.append(Spacer(1, 0.15 * inch))

                story.append(PageBreak())

            # === STORYBOARD SECTION ===
            image_data = previous_results.get("image_generator", {})
            frames = image_data.get("frames", [])
            if frames:
                story.append(Paragraph("STORYBOARD", title_style))
                story.append(Spacer(1, 0.25 * inch))

                for frame in frames:
                    story.append(
                        Paragraph(
                            f"<b>Frame {frame.get('scene_number', '?')} - {frame.get('timing', '')}</b>",
                            subheading_style,
                        )
                    )

                    # Add image URL (in production, could download and embed)
                    url = frame.get("url", "Not generated")
                    story.append(Paragraph(f"Image: {url}", body_style))
                    story.append(
                        Paragraph(
                            f"Description: {frame.get('description', 'N/A')[:200]}",
                            body_style,
                        )
                    )
                    story.append(Spacer(1, 0.2 * inch))

                story.append(PageBreak())

            # === BUDGET SECTION ===
            cost_data = previous_results.get("cost_estimator", {})
            if cost_data and not cost_data.get("error"):
                story.append(Paragraph("PRODUCTION BUDGET", title_style))
                story.append(Spacer(1, 0.25 * inch))

                total = cost_data.get("total", 0)
                story.append(
                    Paragraph(f"<b>Estimated Total: ${total:,}</b>", heading_style)
                )
                story.append(Spacer(1, 0.15 * inch))

                # Budget breakdown table
                breakdown = cost_data.get("breakdown", {})
                if breakdown:
                    table_data = [["Category", "Estimate"]]
                    for category, amount in breakdown.items():
                        table_data.append(
                            [category.replace("_", " ").title(), f"${amount:,}"]
                        )

                    table = Table(table_data, colWidths=[3 * inch, 1.5 * inch])
                    table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#16213e")),
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, -1), 10),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                            ]
                        )
                    )
                    story.append(table)

                # Assumptions
                assumptions = cost_data.get("assumptions", [])
                if assumptions:
                    story.append(Spacer(1, 0.25 * inch))
                    story.append(Paragraph("<b>Assumptions:</b>", subheading_style))
                    for assumption in assumptions:
                        story.append(Paragraph(f"• {assumption}", body_style))

                # Tips
                tips = cost_data.get("tips", [])
                if tips:
                    story.append(Spacer(1, 0.25 * inch))
                    story.append(
                        Paragraph("<b>Budget-Saving Tips:</b>", subheading_style)
                    )
                    for tip in tips:
                        story.append(Paragraph(f"• {tip}", body_style))

                story.append(PageBreak())

            # === LOCATIONS SECTION ===
            location_data = previous_results.get("location_scout", {})
            locations = location_data.get("locations", [])
            if locations:
                story.append(Paragraph("FILMING LOCATIONS", title_style))
                story.append(Spacer(1, 0.25 * inch))

                for loc in locations[:5]:
                    story.append(
                        Paragraph(
                            f"<b>{loc.get('name', 'Unknown')}</b>", subheading_style
                        )
                    )
                    story.append(
                        Paragraph(f"Address: {loc.get('address', 'N/A')}", body_style)
                    )
                    story.append(
                        Paragraph(
                            f"Rating: {loc.get('rating', 'N/A')} | {loc.get('price_level', 'Contact for pricing')}",
                            body_style,
                        )
                    )
                    story.append(Spacer(1, 0.15 * inch))

                # Location tips
                tips = location_data.get("tips", [])
                if tips:
                    story.append(Spacer(1, 0.25 * inch))
                    story.append(Paragraph("<b>Location Tips:</b>", subheading_style))
                    for tip in tips[:4]:
                        story.append(Paragraph(f"• {tip}", body_style))

            # Build PDF
            doc.build(story)

            return {
                "pdf_path": str(filepath),
                "filename": filename,
                "pages": "~" + str(4 + len(frames) // 2),
                "sections": ["Cover", "Script", "Storyboard", "Budget", "Locations"],
            }

        except Exception as e:
            return {
                "error": str(e),
                "text_summary": self._generate_text_summary(product, previous_results),
            }

    def _generate_text_summary(self, product: str, previous_results: dict) -> str:
        """Generate a text summary when PDF fails."""

        lines = [f"AD STORYBOARD PACKAGE: {product}", "=" * 50, ""]

        script_data = previous_results.get("script_writer", {})
        if script_data:
            lines.append("SCRIPT:")
            lines.append(script_data.get("script", "Not available")[:500])
            lines.append("")

        cost_data = previous_results.get("cost_estimator", {})
        if cost_data:
            lines.append(f"ESTIMATED BUDGET: ${cost_data.get('total', 'N/A')}")
            lines.append("")

        return "\n".join(lines)
