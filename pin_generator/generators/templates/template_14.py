#!/usr/bin/env python3
"""Template 14: Scandinavian Minimalist. Thin borders, serif fonts, lots of margins, elegant."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_14"

STYLE_SLOTS = {
    "frame": {"border": "border"},
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
    "name": "Scandinavian Minimalist",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/scandi_minimal.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate a calm title and a short desc for {{title}}.",
    "field_prompts": {
        "title": "Title for {{title}}. Title Case, elegant.",
        "subtitle": "One sentence about the purity or simplicity of {{title}}."
    },
    "images": {
        "hero": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 123, "left": 123}, "width": 491, "height": 736, "layer_order": 5, "object_fit": "cover"
        }
    },
    "elements": {
        "bg_layer": {
            "type": "div", "position": {"top": 0, "left": 0}, "width": 736, "height": 1308,
            "background_color": "#F9F9F9", "z_index": 1
        },
        "frame": {
            "type": "div",
            "position": {"top": 49, "left": 49}, "width": 638, "height": 1210,
            "border": {"width": 1, "color": "#E5E5E5"}, "z_index": 2
        },
        "title": {
            "type": "text",
            "text": "Quiet Morning Coffee",
            "position": {"top": 907, "left": 74}, "width": 589, "height": 98,
            "font_family": "'Playfair Display', serif", "font_size": 44, "font_weight": "400",
            "color": "#2D2D2D", "text_align": "center", "z_index": 10
        },
        "subtitle": {
            "type": "text",
            "text": "A minimal approach to the perfect brew",
            "position": {"top": 993, "left": 123}, "width": 491, "height": 74,
            "font_family": "'Inter', sans-serif", "font_size": 20, "font_weight": "300",
            "color": "#666666", "text_align": "center", "font_style": "italic", "z_index": 10
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1177, "left": 0}, "width": 736, "height": 37,
            "font_family": "'Inter', sans-serif", "font_size": 15, "font_weight": "400",
            "color": "#999999", "text_align": "center", "letter_spacing": 2, "z_index": 10
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
