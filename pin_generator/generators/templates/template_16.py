#!/usr/bin/env python3
"""Template 16: Dynamic Diagonal. Slanted panels for a sense of motion and modernity."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_16"

STYLE_SLOTS = {
    "accent_panel": {"background_color": "primary"},
    "title": {"color": "on_primary"},
    "subtitle": {"color": "secondary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "subtitle": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Dynamic Diagonal",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/dynamic_diagonal.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a dynamic title for {{title}}.",
    "field_prompts": {
        "title": "Generate a high-energy title for {{title}}. e.g. 'POWER PACKED', 'TASTE BLAST'.",
        "subtitle": "Short descriptive text. 4-6 words."
    },
    "images": {
        "top_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": -100, "left": -50}, "width": 700, "height": 600, "layer_order": 1, "transform": "rotate(-5deg)"
        }
    },
    "elements": {
        "accent_panel": {
            "type": "div",
            "position": {"top": 450, "left": -100}, "width": 800, "height": 500,
            "background_color": "#1A1A1A", "transform": "rotate(-8deg)", "z_index": 5, "opacity": 0.95
        },
        "title": {
            "type": "text",
            "text": "UNLEASH THE<br>UMAMI BOMB",
            "position": {"top": 550, "left": 50}, "width": 500, "height": 180,
            "font_family": "'Bebas Neue', sans-serif", "font_size": 75, "font_weight": "400",
            "color": "#FFCC00", "text_align": "left", "line_height": 0.9, "z_index": 10, "transform": "rotate(-8deg)"
        },
        "subtitle": {
            "type": "text",
            "text": "The secret to bold flavors revealed",
            "position": {"top": 740, "left": 60}, "width": 400, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "600",
            "color": "#FFFFFF", "text_align": "left", "z_index": 10, "transform": "rotate(-8deg)"
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "700",
            "color": "#FFCC00", "text_align": "center", "text_transform": "uppercase", "z_index": 10
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
