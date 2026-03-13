#!/usr/bin/env python3
"""Template 22: High-Contrast Noir. Black and white images with a singular vibrant accent color."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_22"

STYLE_SLOTS = {
    "accent_box": {"background_color": "primary"},
    "title": {"color": "on_primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "High-Contrast Noir",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/noir.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate a short, sharp title for {{title}}.",
    "field_prompts": {
        "title": "A sharp, 1-3 word title for {{title}}. e.g. 'PURE LUXE', 'THE EDGE'."
    },
    "images": {
        "bg": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 736, "height": 1308, "layer_order": 1,
            "filter": "grayscale(1) contrast(1.5)"
        }
    },
    "elements": {
        "accent_box": {
            "type": "div", "position": {"top": 858, "left": 0}, "width": 736, "height": 450,
            "background_color": "#E1306C", "z_index": 5
        },
        "title": {
            "type": "text", "text": "REDEFINE<br>YOUR TASTE",
            "position": {"top": 919, "left": 61}, "width": 613, "height": 221,
            "font_family": "'Oswald', sans-serif", "font_size": 98, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "left", "line_height": 0.85, "z_index": 10,
            "text_transform": "uppercase"
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1226, "left": 61}, "width": 613, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 25, "font_weight": "400",
            "color": "#FFFFFF", "text_align": "left", "letter_spacing": 2, "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
