#!/usr/bin/env python3
"""Template 26: Travel Postcard. Nostalgic, full-bleed imagery with stamp and script accents."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_26"

STYLE_SLOTS = {
    "stamp_bg": {"background_color": "secondary"},
    "title": {"color": "on_dark"},
    "script": {"color": "primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "script": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Travel Postcard",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/postcard.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a 'Greetings from' style title for {{title}}.",
    "field_prompts": {
        "title": "A location or flavor-focused title for {{title}}. e.g. 'TASTE OF ITALY', 'SWEET RETREAT'.",
        "script_text": "A handwritten phrase like 'Wish you were here' or 'Simply Delicious'."
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": -1,
            "filter": "sepia(0.3) contrast(1.1)"
        },
        "stamp": {
            "src": "https://cdn-icons-png.flaticon.com/512/814/814421.png",
            "position": {"top": 50, "left": 450}, "width": 100, "height": 100, "layer_order": 10, "opacity": 0.8
        }
    },
    "elements": {
        "title_overlay": {
            "type": "div", "position": {"top": 700, "left": 0}, "width": 600, "height": 200,
            "background": "linear-gradient(to top, rgba(0,0,0,0.8), transparent)", "z_index": 5
        },
        "title": {
            "type": "text", "text": "GREETINGS FROM<br>THE PERFECT BITE",
            "position": {"top": 750, "left": 0}, "width": 600, "height": 120,
            "font_family": "'Oswald', sans-serif", "font_size": 50, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "letter_spacing": 2, "z_index": 10
        },
        "script_text": {
            "type": "text", "text": "Wish you were here",
            "position": {"top": 870, "left": 100}, "width": 400, "height": 60,
            "font_family": "'Dancing Script', cursive", "font_size": 32, "font_weight": "700",
            "color": "#FFD700", "text_align": "center", "transform": "rotate(-5deg)", "z_index": 15
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
