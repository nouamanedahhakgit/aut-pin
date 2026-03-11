#!/usr/bin/env python3
"""Template 17: Magazine Cover style. Masthead at top, multi-headlines, editorial feel."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_17"

STYLE_SLOTS = {
    "masthead": {"color": "primary"},
    "headline": {"color": "text_primary"},
    "tagline": {"color": "secondary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "masthead": "heading",
    "headline": "heading",
    "tagline": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Magazine Editorial",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/magazine_editorial.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a magazine title and 2 headlines for {{title}}.",
    "field_prompts": {
        "masthead": "A magazine name related to the niche of {{title}}. 1 word.",
        "headline": "Main article headline for {{title}}. 3-5 words.",
        "tagline_1": "Supporting headline 1. 4-6 words.",
        "tagline_2": "Supporting headline 2. 4-6 words."
    },
    "images": {
        "cover_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": 1
        }
    },
    "elements": {
        "masthead": {
            "type": "text",
            "text": "SAVOR",
            "position": {"top": 40, "left": 0}, "width": 600, "height": 120,
            "font_family": "'Playfair Display', serif", "font_size": 120, "font_weight": "900",
            "color": "#1A1A1A", "text_align": "center", "letter_spacing": 10, "opacity": 0.8, "z_index": 10
        },
        "headline_box": {
            "type": "div",
            "position": {"top": 600, "left": 0}, "width": 450, "height": 300,
            "background": "linear-gradient(to right, rgba(0,0,0,0.7), transparent)", "z_index": 5
        },
        "headline": {
            "type": "text",
            "text": "THE ART OF THE<br>PERFECT CRUST",
            "position": {"top": 640, "left": 40}, "width": 400, "height": 120,
            "font_family": "'Inter', sans-serif", "font_size": 40, "font_weight": "900",
            "color": "#FFFFFF", "text_align": "left", "line_height": 1.1, "z_index": 10, "text_transform": "uppercase"
        },
        "tagline_1": {
            "type": "text",
            "text": "→ Secret ingredients unveiled",
            "position": {"top": 780, "left": 40}, "width": 350, "height": 30,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "600",
            "color": "#FFD700", "text_align": "left", "z_index": 10
        },
        "tagline_2": {
            "type": "text",
            "text": "→ From kitchen to masterpiece",
            "position": {"top": 815, "left": 40}, "width": 350, "height": 30,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "600",
            "color": "#FFD700", "text_align": "left", "z_index": 10
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "text_transform": "uppercase", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
