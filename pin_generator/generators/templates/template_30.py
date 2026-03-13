#!/usr/bin/env python3
"""Template 30: Bold Borderless. High-impact, minimal elements, maximum image focus."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_30"

STYLE_SLOTS = {
    "title": {"color": "on_dark"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Bold Borderless",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/borderless.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate a short, high-impact title for {{title}}.",
    "field_prompts": {
        "title": "A short, 2-3 word high-impact title for {{title}}. e.g. 'CHICKEN REDEFINED', 'PURE CRISP'."
    },
    "images": {
        "bg": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 736, "height": 1308, "layer_order": -1,
            "filter": "brightness(0.7) contrast(1.2)"
        }
    },
    "elements": {
        "title": {
            "type": "text", "text": "CRISP<br>PERFECTION",
            "position": {"top": 490, "left": 0}, "width": 736, "height": 368,
            "font_family": "'Montserrat', sans-serif", "font_size": 135, "font_weight": "900",
            "color": "#FFFFFF", "text_align": "center", "line_height": 0.8, "z_index": 10,
            "text_transform": "uppercase"
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1226, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 27, "font_weight": "800",
            "color": "#FFFFFF", "text_align": "center", "letter_spacing": 2, "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
