"""
Export AdResearchResult to PDF.
Uses ReportLab to create a simple text-based report.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from .models import AdResearchResult


def result_to_pdf(
    result: AdResearchResult,
    output_dir: str = "output/pdfs",
    filename_prefix: str = "Marky_Report",
) -> Optional[str]:
    """
    Export AdResearchResult to a PDF file.
    
    Returns:
        Path to the created PDF, or None if ReportLab unavailable or on error.
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    safe_bt = result.business_type.replace(" ", "_").replace("/", "-")[:20]
    safe_loc = result.location.replace(" ", "_").replace(",", "")[:15]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{safe_bt}_{safe_loc}_{timestamp}.pdf"
    filepath = out_path / filename
    
    try:
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(
            f"Ad Research Report: {result.business_type} in {result.location}",
            styles["Heading1"],
        ))
        story.append(Spacer(1, 0.25 * inch))
        
        def add_section(title: str, items: list):
            if not items:
                return
            story.append(Paragraph(title, styles["Heading2"]))
            for item in items[:20]:  # Limit per section
                text = item if isinstance(item, str) else f"{getattr(item, 'angle_name', item)}: {getattr(item, 'hook', item)}"
                story.append(Paragraph(f"• {text}", styles["Normal"]))
            story.append(Spacer(1, 0.15 * inch))
        
        # Competitors
        if result.competitors:
            story.append(Paragraph("Competitors", styles["Heading2"]))
            for c in result.competitors[:10]:
                story.append(Paragraph(
                    f"• <b>{c.name}</b> ({c.rating}⭐, {c.review_count} reviews) — {', '.join(c.services[:5])}",
                    styles["Normal"],
                ))
            story.append(Spacer(1, 0.15 * inch))
        
        # Customer Voice
        if result.customer_voice:
            voc = result.customer_voice
            add_section("Pain Points", voc.pain_points)
            add_section("Desires", voc.desires)
            add_section("Praise Quotes", voc.praise_quotes[:5])
        
        # Differentiators
        if result.differentiators:
            story.append(Paragraph("Differentiators", styles["Heading2"]))
            for d in result.differentiators:
                story.append(Paragraph(f"• <b>{d.angle_name}</b>: {d.hook}", styles["Normal"]))
            story.append(Spacer(1, 0.15 * inch))
        
        # Timing
        if result.timing:
            story.append(Paragraph("Seasonal Timing", styles["Heading2"]))
            for t in result.timing:
                story.append(Paragraph(
                    f"• {t.keyword}: Peak {', '.join(t.peak_months)} | CPC ${t.avg_cpc:.2f} | {t.monthly_volume:,}/mo",
                    styles["Normal"],
                ))
            story.append(Spacer(1, 0.15 * inch))
        
        # Related Questions
        add_section("Related Questions", result.related_questions)
        
        # Ad Hooks
        add_section("Ad Hooks", result.recommended_hooks)
        
        # Headlines
        add_section("Headlines", result.headline_suggestions)
        
        # Trust Signals
        add_section("Trust Signals", result.trust_signals)
        
        # Market Summary
        if result.market_summary:
            story.append(Paragraph("Market Summary", styles["Heading2"]))
            story.append(Paragraph(result.market_summary, styles["Normal"]))
        
        doc.build(story)
        return str(filepath)
        
    except Exception as e:
        print(f"  PDF export error: {e}")
        return None
