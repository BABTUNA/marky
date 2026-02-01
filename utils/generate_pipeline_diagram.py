#!/usr/bin/env python3
"""
Generate static pipeline architecture diagram for PDFs.

Run once to create docs/pipeline_diagram.png which is included in all PDFs.
Shows research agents running concurrently, then sequential production pipeline.
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


def generate_pipeline_diagram(output_path: str = "docs/pipeline_diagram.png") -> str:
    """Generate the AdBoard AI pipeline architecture diagram."""
    if not PILLOW_AVAILABLE:
        print("❌ Pillow required: pip install Pillow")
        return None

    # Canvas size
    width, height = 750, 420
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fonts
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font_lg = font_sm = font_title = ImageFont.load_default()
    for p in font_paths:
        if Path(p).exists():
            try:
                font_title = ImageFont.truetype(p, 16)
                font_lg = ImageFont.truetype(p, 11)
                font_sm = ImageFont.truetype(p, 9)
                break
            except Exception:
                continue

    # Colors
    colors = {
        "research": "#3498db",  # Blue
        "analysis": "#9b59b6",  # Purple
        "creative": "#2ecc71",  # Green
        "production": "#e67e22",  # Orange
        "output": "#e74c3c",    # Red
        "arrow": "#7f8c8d",
        "border": "#bdc3c7",
        "text": "#2c3e50",
    }

    def hex_to_rgb(hex_color):
        return tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    def draw_box(x, y, w, h, label, color_key, sublabel=None):
        color = hex_to_rgb(colors[color_key])
        draw.rounded_rectangle([x, y, x+w, y+h], radius=6, fill=color, outline=None)
        draw.text((x + w//2, y + h//2 - (6 if sublabel else 0)), label, fill="white", font=font_lg, anchor="mm")
        if sublabel:
            draw.text((x + w//2, y + h//2 + 10), sublabel, fill=(220, 220, 220), font=font_sm, anchor="mm")

    def draw_arrow(x1, y1, x2, y2, color_key="arrow"):
        color = hex_to_rgb(colors[color_key])
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        # Arrowhead
        if x2 > x1:  # Right
            draw.polygon([(x2, y2), (x2-8, y2-4), (x2-8, y2+4)], fill=color)
        elif y2 > y1:  # Down
            draw.polygon([(x2, y2), (x2-4, y2-8), (x2+4, y2-8)], fill=color)

    # Title
    draw.text((width//2, 20), "AdBoard AI Pipeline Architecture", fill=hex_to_rgb(colors["text"]), font=font_title, anchor="mm")

    # === ROW 1: User Input ===
    draw_box(20, 50, 100, 35, "User Prompt", "text")

    # Arrow to research
    draw_arrow(120, 67, 150, 67)

    # === RESEARCH (Concurrent) ===
    # Bracket/box around concurrent agents
    draw.rectangle([155, 45, 450, 140], outline=hex_to_rgb(colors["border"]), width=2)
    draw.text((302, 55), "Research (Concurrent)", fill=hex_to_rgb(colors["text"]), font=font_sm, anchor="mm")

    # Research agents (arranged in 2x3 grid within the box)
    research_agents = [
        ("Local Intel", 165, 70),
        ("Review Intel", 265, 70),
        ("Yelp Intel", 365, 70),
        ("Trends Intel", 165, 105),
        ("Related Qs", 265, 105),
        ("Map Gen", 365, 105),
    ]
    for label, x, y in research_agents:
        draw_box(x, y, 85, 28, label, "research")

    # Arrow from research block to analysis
    draw_arrow(450, 92, 480, 92)

    # === ANALYSIS ===
    draw_box(485, 70, 90, 45, "Trend", "analysis", "Analyzer")
    draw_arrow(575, 92, 605, 92)
    draw_box(610, 70, 90, 45, "Script", "analysis", "Writer")

    # Arrow down from script
    draw_arrow(655, 115, 655, 155)

    # === ROW 2: Creative ===
    draw_box(520, 160, 90, 45, "Image", "creative", "Generator")
    draw_arrow(520, 182, 490, 182)
    draw_box(395, 160, 90, 45, "Video", "creative", "Assembly")
    
    # Optional voiceover/music branch
    draw.text((655, 175), "(optional)", fill=hex_to_rgb(colors["border"]), font=font_sm, anchor="mm")
    draw_box(610, 160, 90, 45, "Voiceover", "creative", "+ Music")
    draw_arrow(610, 182, 580, 182)

    # Arrow down from video
    draw_arrow(440, 205, 440, 245)

    # === ROW 3: Production ===
    draw_box(275, 250, 90, 45, "Cost", "production", "Estimator")
    draw_arrow(365, 272, 395, 272)
    draw_box(400, 250, 90, 45, "Location", "production", "Scout")
    draw_arrow(490, 272, 520, 272)
    draw_box(525, 250, 90, 45, "Social", "production", "Media")

    # Arrow down
    draw_arrow(440, 295, 440, 325)

    # === ROW 4: Output ===
    draw_box(350, 330, 90, 45, "PDF", "output", "Builder")
    draw_arrow(440, 352, 470, 352)
    draw_box(475, 330, 100, 45, "Drive Upload", "output")

    # Final outputs
    draw_arrow(575, 352, 610, 352)
    draw.text((680, 340), "Storyboard Video", fill=hex_to_rgb(colors["text"]), font=font_lg, anchor="mm")
    draw.text((680, 358), "Campaign PDF", fill=hex_to_rgb(colors["text"]), font=font_lg, anchor="mm")
    draw.text((680, 376), "(+ Viral Video)", fill=hex_to_rgb(colors["border"]), font=font_sm, anchor="mm")

    # Legend
    legend_y = 400
    legend_items = [
        ("Research", "research"),
        ("Analysis", "analysis"),
        ("Creative", "creative"),
        ("Production", "production"),
        ("Output", "output"),
    ]
    x = 20
    for label, color_key in legend_items:
        draw.rectangle([x, legend_y, x+12, legend_y+12], fill=hex_to_rgb(colors[color_key]))
        draw.text((x+16, legend_y+6), label, fill=hex_to_rgb(colors["text"]), font=font_sm, anchor="lm")
        x += 90

    # Border
    draw.rectangle([0, 0, width-1, height-1], outline=hex_to_rgb(colors["border"]), width=1)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", optimize=True)
    print(f"Pipeline diagram saved: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_pipeline_diagram()
