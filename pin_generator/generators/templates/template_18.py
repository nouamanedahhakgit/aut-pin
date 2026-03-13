#!/usr/bin/env python3
"""Template 18: Retro Pop Art. Vibrant colors, comic-style speech bubble, half-tone feel."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_18"

STYLE_SLOTS = {
    "bubble_bg": {"background_color": "secondary"},
    "bubble_text": {"color": "on_secondary"},
    "title": {"color": "primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "bubble_text": "body",
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Retro Pop Art",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/pop_art.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate a fun, high-energy title for {{title}}.",
    "field_prompts": {
        "title": "A fun, comic-style title for {{title}}. e.g. 'WOW! TASTY!', 'BOOM! FLAVOR!'",
        "bubble_text": "A quick CTA like 'EASY STEP!' or 'TRY NOW!'"
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 736, "height": 981, "layer_order": 1,
            "filter": "contrast(1.4) saturate(1.5)"
        }
    },
    "elements": {
        "yellow_strip": {
            "type": "div", "position": {"top": 919, "left": 0}, "width": 736, "height": 389,
            "background_color": "#FFD700", "z_index": 5
        },
        "bubble_bg": {
            "type": "div", "position": {"top": 61, "left": 61}, "width": 245, "height": 123,
            "background_color": "#FFFFFF", "border": "5px solid #000", "border_radius": 61, "z_index": 10
        },
        "bubble_text": {
            "type": "text", "text": "BOOM!", "position": {"top": 92, "left": 61}, "width": 245, "height": 61,
            "font_family": "'Bebas Neue', sans-serif", "font_size": 39, "font_weight": "900",
            "color": "#000000", "text_align": "center", "z_index": 20
        },
        "title": {
            "type": "text", "text": "THE BEST<br>CHICKEN!",
            "position": {"top": 981, "left": 49}, "width": 638, "height": 196,
            "font_family": "'Oswald', sans-serif", "font_size": 86, "font_weight": "900",
            "color": "#1A1A1A", "text_align": "center", "line_height": 0.9, "z_index": 10,
            "text_shadow": "5px 5px 0 #FFFFFF"
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1226, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 25, "font_weight": "800",
            "color": "#000000", "text_align": "center", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
