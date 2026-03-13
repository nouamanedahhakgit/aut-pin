#!/usr/bin/env python3
"""Template 21: Polaroid Collage. Multiple overlapping frames for a casual, personal feel."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_21"

STYLE_SLOTS = {
    "bg": {"background_color": "background"},
    "title": {"color": "text_primary"},
    "website": {"color": "text_secondary"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Polaroid Collage",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/polaroid_collage.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate a cozy title for {{title}}.",
    "field_prompts": {
        "title": "A handwritten-style title for {{title}}. e.g. 'Our Favorite Bites', 'Sweet Memories'."
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 123, "left": 61}, "width": 491, "height": 490, "layer_order": 5,
            "border": "18px solid #FFF", "box_shadow": "0 12px 25px rgba(0,0,0,0.1)", "transform": "rotate(-5deg)"
        },
        "side_img_1": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 552, "left": 307}, "width": 368, "height": 368, "layer_order": 4,
            "border": "15px solid #FFF", "box_shadow": "0 12px 25px rgba(0,0,0,0.1)", "transform": "rotate(8deg)"
        },
        "side_img_2": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 736, "left": 61}, "width": 307, "height": 306, "layer_order": 3,
            "border": "12px solid #FFF", "box_shadow": "0 12px 25px rgba(0,0,0,0.1)", "transform": "rotate(-12deg)"
        }
    },
    "elements": {
        "bg": {
            "type": "div", "position": {"top": 0, "left": 0}, "width": 736, "height": 1308,
            "background_color": "#F3F1ED", "z_index": 1
        },
        "title": {
            "type": "text", "text": "Weekend<br>Brunch Highlights",
            "position": {"top": 1042, "left": 0}, "width": 736, "height": 184,
            "font_family": "'Dancing Script', cursive", "font_size": 59, "font_weight": "700",
            "color": "#4A4A4A", "text_align": "center", "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1226, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 22, "font_weight": "400",
            "color": "#999999", "text_align": "center", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
