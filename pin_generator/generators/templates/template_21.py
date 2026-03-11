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
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a cozy title for {{title}}.",
    "field_prompts": {
        "title": "A handwritten-style title for {{title}}. e.g. 'Our Favorite Bites', 'Sweet Memories'."
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 100, "left": 50}, "width": 400, "height": 400, "layer_order": 5,
            "border": "15px solid #FFF", "box_shadow": "0 10px 20px rgba(0,0,0,0.1)", "transform": "rotate(-5deg)"
        },
        "side_img_1": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 450, "left": 250}, "width": 300, "height": 300, "layer_order": 4,
            "border": "12px solid #FFF", "box_shadow": "0 10px 20px rgba(0,0,0,0.1)", "transform": "rotate(8deg)"
        },
        "side_img_2": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 600, "left": 50}, "width": 250, "height": 250, "layer_order": 3,
            "border": "10px solid #FFF", "box_shadow": "0 10px 20px rgba(0,0,0,0.1)", "transform": "rotate(-12deg)"
        }
    },
    "elements": {
        "bg": {
            "type": "div", "position": {"top": 0, "left": 0}, "width": 600, "height": 1067,
            "background_color": "#F3F1ED", "z_index": 1
        },
        "title": {
            "type": "text", "text": "Weekend<br>Brunch Highlights",
            "position": {"top": 850, "left": 0}, "width": 600, "height": 150,
            "font_family": "'Dancing Script', cursive", "font_size": 48, "font_weight": "700",
            "color": "#4A4A4A", "text_align": "center", "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "400",
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
