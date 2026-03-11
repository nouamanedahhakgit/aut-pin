#!/usr/bin/env python3
"""Template 27: Geometric Flat. Modern, structured, using vibrant overlapping shapes."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_27"

STYLE_SLOTS = {
    "circle": {"background_color": "secondary"},
    "rect": {"background_color": "primary"},
    "title": {"color": "on_primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Geometric Flat",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/geometric_flat.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a geometric-style title for {{title}}.",
    "field_prompts": {
        "title": "A modern, bold title for {{title}}. e.g. 'SHARP FLAVOR', 'PURE DESIGN'."
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 700, "layer_order": -1
        }
    },
    "elements": {
        "circle": {
            "type": "div", "position": {"top": 600, "left": -100}, "width": 400, "height": 400,
            "background_color": "#FFC107", "border_radius": 200, "z_index": 5, "opacity": 0.9
        },
        "rect": {
            "type": "div", "position": {"top": 700, "left": 100}, "width": 550, "height": 250,
            "background_color": "#1A1A1A", "z_index": 6
        },
        "title": {
            "type": "text", "text": "BOLD<br>MOVES",
            "position": {"top": 740, "left": 140}, "width": 420, "height": 160,
            "font_family": "'Inter', sans-serif", "font_size": 70, "font_weight": "900",
            "color": "#FFFFFF", "text_align": "left", "line_height": 0.9, "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 20, "font_weight": "700",
            "color": "#1A1A1A", "text_align": "center", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
