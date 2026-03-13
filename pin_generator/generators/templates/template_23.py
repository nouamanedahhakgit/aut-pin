#!/usr/bin/env python3
"""Template 23: Watercolor Dream. Soft, artistic, fluid shapes and elegant serif typography."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_23"

STYLE_SLOTS = {
    "blob": {"background_color": "primary_glass"},
    "title": {"color": "text_primary"},
    "website": {"color": "text_secondary"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Watercolor Dream",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/watercolor.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate a soft, elegant title for {{title}}.",
    "field_prompts": {
        "title": "A poetic, elegant title for {{title}}. e.g. 'Golden Glow', 'Soft Petals'."
    },
    "images": {
        "bg": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 736, "height": 1308, "layer_order": -1,
            "filter": "blur(5px) opacity(0.6)"
        },
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 184, "left": 123}, "width": 491, "height": 490, "layer_order": 5,
            "border_radius": "50% 30% 70% 40%", "box_shadow": "0 0 61px rgba(0,0,0,0.1)"
        }
    },
    "elements": {
        "blob": {
            "type": "div", "position": {"top": 674, "left": 61}, "width": 613, "height": 368,
            "background_color": "rgba(255,182,193,0.3)", "filter": "blur(40px)", "z_index": 2
        },
        "title": {
            "type": "text", "text": "Artisan<br>Infusions",
            "position": {"top": 736, "left": 61}, "width": 613, "height": 245,
            "font_family": "'Great Vibes', cursive", "font_size": 98, "font_weight": "400",
            "color": "#4A3B3B", "text_align": "center", "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1226, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 20, "font_weight": "400",
            "color": "#888888", "text_align": "center", "letter_spacing": 4, "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
