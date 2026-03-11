#!/usr/bin/env python3
"""Template 13: Neon Night Fever. Dark mode, neon accents, floating brutalist title."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_13"

STYLE_SLOTS = {
    "neon_border": {"background_color": "accent"},
    "title_card": {"background_color": "background"},
    "title": {"color": "text_primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Neon Night Fever",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/neon_night.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a punchy, 2-word title for {{title}}.",
    "field_prompts": {
        "title": "Generate a 2-word, ALL CAPS energetic title for {{title}}. e.g. 'PURE FIRE', 'ULTIMATE BITE'."
    },
    "images": {
        "bg": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": 1,
            "filter": "grayscale(0.5) contrast(1.2) brightness(0.7)"
        }
    },
    "elements": {
        "neon_border": {
            "type": "div",
            "position": {"top": 50, "left": 50}, "width": 500, "height": 967,
            "border": {"width": 10, "color": "#E1306C"}, "border_radius": 20, "z_index": 5
        },
        "title_card": {
            "type": "div",
            "position": {"top": 400, "left": -20}, "width": 640, "height": 200,
            "background_color": "#000000", "transform": "rotate(-5deg)", "z_index": 10,
            "box_shadow": "0 0 30px #E1306C"
        },
        "title": {
            "type": "text",
            "text": "INSANE<br>FLAVOR",
            "position": {"top": 420, "left": 0}, "width": 600, "height": 160,
            "font_family": "'Inter', sans-serif", "font_size": 100, "font_weight": "900",
            "color": "#E1306C", "text_align": "center", "line_height": 0.8, "z_index": 20,
            "text_shadow": "0 0 20px #E1306C", "transform": "rotate(-5deg)"
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 980, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 20, "font_weight": "700",
            "color": "#E1306C", "text_align": "center", "text_transform": "uppercase", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
