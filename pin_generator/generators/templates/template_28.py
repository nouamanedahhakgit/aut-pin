#!/usr/bin/env python3
"""Template 28: Moody Cinematic. Cinematic widescreen feel with caption-style typography."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_28"

STYLE_SLOTS = {
    "title": {"color": "on_dark"},
    "caption": {"color": "secondary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "caption": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Moody Cinematic",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/cinematic.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16", "background_color": "#000"},
    "prompt": "Generate a dramatic movie-like title for {{title}}.",
    "field_prompts": {
        "title": "A dramatic title for {{title}}. e.g. 'THE CHOSEN CRUMB', 'NIGHT FEAST'.",
        "caption": "A subtitle like '[Crispness Intenuifies]' or '[The Perfect Flavor]'."
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 245, "left": 0}, "width": 736, "height": 736, "layer_order": 1,
            "filter": "contrast(1.3) brightness(0.8) saturate(0.7)"
        }
    },
    "elements": {
        "black_top": {
            "type": "div", "position": {"top": 0, "left": 0}, "width": 736, "height": 245,
            "background_color": "#000000", "z_index": 5
        },
        "black_bottom": {
            "type": "div", "position": {"top": 981, "left": 0}, "width": 736, "height": 327,
            "background_color": "#000000", "z_index": 5
        },
        "title": {
            "type": "text", "text": "THE CRUST",
            "position": {"top": 61, "left": 0}, "width": 736, "height": 123,
            "font_family": "'Inter', sans-serif", "font_size": 49, "font_weight": "300",
            "color": "#FFFFFF", "text_align": "center", "letter_spacing": 15, "z_index": 10,
            "text_transform": "uppercase"
        },
        "caption": {
            "type": "text", "text": "[ SIZZLING INTENSIFIES ]",
            "position": {"top": 1042, "left": 0}, "width": 736, "height": 61,
            "font_family": "'Inter', sans-serif", "font_size": 22, "font_weight": "400",
            "color": "#CCFF00", "text_align": "center", "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1226, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 17, "font_weight": "700",
            "color": "#666666", "text_align": "center", "text_transform": "uppercase", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
