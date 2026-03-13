#!/usr/bin/env python3
"""Template 24: Glitch Aesthetic. High-energy, digital, cyberpunk-inspired visual distortion."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_24"

STYLE_SLOTS = {
    "accent_bar": {"background_color": "primary"},
    "title": {"color": "on_dark"},
    "website": {"color": "secondary"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Glitch Aesthetic",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/glitch.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16", "background_color": "#000"},
    "prompt": "Generate a short, intense title for {{title}}.",
    "field_prompts": {
        "title": "A sharp, intense title for {{title}}. e.g. 'BREAKOUT', 'TASTE PROTOCOL'."
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 736, "height": 736, "layer_order": 1,
            "filter": "contrast(2) brightness(1.5) hue-rotate(180deg)"
        }
    },
    "elements": {
        "accent_bar": {
            "type": "div", "position": {"top": 711, "left": 0}, "width": 736, "height": 25,
            "background_color": "#00FFFF", "z_index": 10
        },
        "glitch_text_1": {
            "type": "text", "text": "SYSTEM ERROR",
            "position": {"top": 762, "left": 52}, "width": 638, "height": 123,
            "font_family": "'Inter', sans-serif", "font_size": 49, "font_weight": "900",
            "color": "#FF00FF", "text_align": "center", "opacity": 0.5, "z_index": 5
        },
        "glitch_text_2": {
            "type": "text", "text": "SYSTEM ERROR",
            "position": {"top": 758, "left": 47}, "width": 638, "height": 123,
            "font_family": "'Inter', sans-serif", "font_size": 49, "font_weight": "900",
            "color": "#00FFFF", "text_align": "center", "opacity": 0.5, "z_index": 5
        },
        "title": {
            "type": "text", "text": "THE TASTE<br>OF FUTURE",
            "position": {"top": 858, "left": 61}, "width": 613, "height": 245,
            "font_family": "'Bebas Neue', sans-serif", "font_size": 110, "font_weight": "400",
            "color": "#FFFFFF", "text_align": "center", "line_height": 0.9, "z_index": 15
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1226, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 22, "font_weight": "700",
            "color": "#00FFFF", "text_align": "center", "text_transform": "uppercase", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
