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
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a calm title and a short desc for {{title}}.",
    "field_prompts": {
        "title": "Title for {{title}}. Title Case, elegant.",
        "subtitle": "One sentence about the purity or simplicity of {{title}}."
    },
    "images": {
        "hero": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 100, "left": 100}, "width": 400, "height": 600, "layer_order": 5, "object_fit": "cover"
        }
    },
    "elements": {
        "bg_layer": {
            "type": "div", "position": {"top": 0, "left": 0}, "width": 600, "height": 1067,
            "background_color": "#F9F9F9", "z_index": 1
        },
        "frame": {
            "type": "div",
            "position": {"top": 40, "left": 40}, "width": 520, "height": 987,
            "border": {"width": 1, "color": "#E5E5E5"}, "z_index": 2
        },
        "title": {
            "type": "text",
            "text": "Quiet Morning Coffee",
            "position": {"top": 740, "left": 60}, "width": 480, "height": 80,
            "font_family": "'Playfair Display', serif", "font_size": 36, "font_weight": "400",
            "color": "#2D2D2D", "text_align": "center", "z_index": 10
        },
        "subtitle": {
            "type": "text",
            "text": "A minimal approach to the perfect brew",
            "position": {"top": 810, "left": 100}, "width": 400, "height": 60,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "300",
            "color": "#666666", "text_align": "center", "font_style": "italic", "z_index": 10
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 960, "left": 0}, "width": 600, "height": 30,
            "font_family": "'Inter', sans-serif", "font_size": 12, "font_weight": "400",
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
