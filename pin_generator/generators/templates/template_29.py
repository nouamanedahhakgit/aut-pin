#!/usr/bin/env python3
"""Template 29: Organic Texture. Tactile, paper-like background with natural tones and soft serif font."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_29"

STYLE_SLOTS = {
    "paper_bg": {"background_color": "background"},
    "title": {"color": "text_primary"},
    "website": {"color": "text_secondary"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Organic Texture",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/organic_texture.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a natural, grounded title for {{title}}.",
    "field_prompts": {
        "title": "A natural title for {{title}}. e.g. 'EARTHEN BAKE', 'SIMPLE ROOTS'."
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 50, "left": 50}, "width": 500, "height": 600, "layer_order": -1,
            "border_radius": 15, "box_shadow": "0 15px 40px rgba(0,0,0,0.1)"
        }
    },
    "elements": {
        "paper_bg": {
            "type": "div", "position": {"top": 550, "left": 0}, "width": 600, "height": 517,
            "background_color": "#FDF5E6", "z_index": 1,
            "background": "url('https://www.transparenttextures.com/patterns/natural-paper.png')"
        },
        "title": {
            "type": "text", "text": "THE BEAUTY OF<br>SLO-COOKED",
            "position": {"top": 680, "left": 50}, "width": 500, "height": 180,
            "font_family": "'Playfair Display', serif", "font_size": 48, "font_weight": "700",
            "color": "#5D4037", "text_align": "center", "line_height": 1.1, "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "600",
            "color": "#8D6E63", "text_align": "center", "letter_spacing": 2, "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
