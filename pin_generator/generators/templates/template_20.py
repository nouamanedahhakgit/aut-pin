#!/usr/bin/env python3
"""Template 20: Industrial Loft. Dark, textured, metallic accents, bold typography."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_20"

STYLE_SLOTS = {
    "accent_line": {"background_color": "primary"},
    "title": {"color": "on_dark"},
    "label": {"color": "secondary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "label": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Industrial Loft",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/industrial_loft.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a bold, gritty title for {{title}}.",
    "field_prompts": {
        "title": "A bold title for {{title}}. e.g. 'CHEF'S CHOICE', 'KITCHEN LAB'.",
        "label": "Short label like 'EST. 2024' or 'HANDCRAFTED'."
    },
    "images": {
        "bg": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": -1,
            "filter": "contrast(1.2) brightness(0.4) grayscale(0.5)"
        }
    },
    "elements": {
        "accent_line": {
            "type": "div", "position": {"top": 400, "left": 50}, "width": 5, "height": 300,
            "background_color": "#CD7F32", "z_index": 5
        },
        "title": {
            "type": "text", "text": "THE<br>IRON<br>PANS",
            "position": {"top": 400, "left": 80}, "width": 470, "height": 300,
            "font_family": "'Bebas Neue', sans-serif", "font_size": 100, "font_weight": "400",
            "color": "#FFFFFF", "text_align": "left", "line_height": 0.8, "z_index": 10
        },
        "label": {
            "type": "text", "text": "HANDCRAFTED",
            "position": {"top": 720, "left": 80}, "width": 200, "height": 30,
            "font_family": "'Inter', sans-serif", "font_size": 14, "font_weight": "800",
            "color": "#CD7F32", "text_align": "left", "letter_spacing": 3, "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "700",
            "color": "#CD7F32", "text_align": "center", "text_transform": "uppercase", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
