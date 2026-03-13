#!/usr/bin/env python3
"""Template 31: The Listicle. Numbered steps or highlights for high engagement and readability."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_31"

STYLE_SLOTS = {
    "num_bg": {"background_color": "secondary"},
    "title_box": {"background_color": "primary"},
    "title": {"color": "on_primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "The Listicle",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/listicle.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate a listicle-style title for {{title}}.",
    "field_prompts": {
        "title": "A listicle title for {{title}}. e.g. '3 WAYS TO COOK...', '5 SECRETS OF...'."
    },
    "images": {
        "hero": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 736, "height": 1308, "layer_order": -1
        }
    },
    "elements": {
        "title_box": {
            "type": "div", "position": {"top": 98, "left": 0}, "width": 675, "height": 221,
            "background_color": "#E1306C", "z_index": 5
        },
        "title": {
            "type": "text", "text": "3 SECRETS TO<br>THE PERFECT BITE",
            "position": {"top": 135, "left": 37}, "width": 613, "height": 147,
            "font_family": "'Inter', sans-serif", "font_size": 51, "font_weight": "900",
            "color": "#FFFFFF", "text_align": "left", "line_height": 1.1, "z_index": 10
        },
        "n1": {
            "type": "div", "position": {"top": 429, "left": 61}, "width": 74, "height": 74,
            "background_color": "#FFD700", "border_radius": 37, "z_index": 5
        },
        "t1": {
            "type": "text", "text": "1", "position": {"top": 429, "left": 61}, "width": 74, "height": 74,
            "font_family": "'Inter', sans-serif", "font_size": 39, "font_weight": "900",
            "color": "#000", "text_align": "center", "z_index": 10
        },
        "n2": {
            "type": "div", "position": {"top": 552, "left": 61}, "width": 74, "height": 74,
            "background_color": "#FFD700", "border_radius": 37, "z_index": 5
        },
        "t2": {
            "type": "text", "text": "2", "position": {"top": 552, "left": 61}, "width": 74, "height": 74,
            "font_family": "'Inter', sans-serif", "font_size": 39, "font_weight": "900",
            "color": "#000", "text_align": "center", "z_index": 10
        },
        "n3": {
            "type": "div", "position": {"top": 674, "left": 61}, "width": 74, "height": 74,
            "background_color": "#FFD700", "border_radius": 37, "z_index": 5
        },
        "t3": {
            "type": "text", "text": "3", "position": {"top": 674, "left": 61}, "width": 74, "height": 74,
            "font_family": "'Inter', sans-serif", "font_size": 39, "font_weight": "900",
            "color": "#000", "text_align": "center", "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1226, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 25, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "text_shadow": "0 2px 5px rgba(0,0,0,0.5)", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
