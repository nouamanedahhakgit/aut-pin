#!/usr/bin/env python3
"""Template 19: Zen Garden. Minimal, soft pastels, plenty of white space, peaceful."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_19"

STYLE_SLOTS = {
    "center_card": {"background_color": "background"},
    "title": {"color": "text_primary"},
    "subtitle": {"color": "text_secondary"},
    "website": {"color": "text_secondary"}
}

FONT_SLOTS = {
    "title": "heading",
    "subtitle": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Zen Garden",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/zen_garden.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a short, peaceful title for {{title}}.",
    "field_prompts": {
        "title": "A serene title for {{title}}. e.g. 'Simple Joys', 'Pure Flavor'.",
        "subtitle": "One word about the essence of {{title}}."
    },
    "images": {
        "hero": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": -1,
            "filter": "brightness(1.1) saturate(0.8) blur(2px)"
        }
    },
    "elements": {
        "center_card": {
            "type": "div", "position": {"top": 333, "left": 50}, "width": 500, "height": 400,
            "background_color": "rgba(255,255,255,0.8)", "border_radius": 30, "z_index": 5
        },
        "title": {
            "type": "text", "text": "NATURAL<br>HARMONY",
            "position": {"top": 440, "left": 100}, "width": 400, "height": 120,
            "font_family": "'Inter', sans-serif", "font_size": 36, "font_weight": "300",
            "color": "#333333", "text_align": "center", "letter_spacing": 5, "z_index": 10
        },
        "subtitle": {
            "type": "text", "text": "PURE",
            "position": {"top": 550, "left": 100}, "width": 400, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 14, "font_weight": "600",
            "color": "#666666", "text_align": "center", "letter_spacing": 10, "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "400",
            "color": "#666666", "text_align": "center", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
