#!/usr/bin/env python3
"""Template 25: Classic Cookbook. Traditional, elegant, trustworthy editorial style."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_25"

STYLE_SLOTS = {
    "page_bg": {"background_color": "background"},
    "title": {"color": "text_primary"},
    "rule_line": {"background_color": "border"},
    "website": {"color": "text_secondary"}
}

FONT_SLOTS = {
    "title": "heading",
    "chapter": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Classic Cookbook",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/classic_cookbook.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate a classic recipe title for {{title}}.",
    "field_prompts": {
        "title": "A full, classic title for {{title}}. e.g. 'Traditional Beef Roast', 'Heritage Apple Pie'.",
        "chapter": "A category name like 'ENTREES', 'DESSERTS', or 'FAVORITES'."
    },
    "images": {
        "main_img": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 98, "left": 98}, "width": 540, "height": 539, "layer_order": 5,
            "border": "1px solid #CCC", "padding": "12px", "background": "#FFF"
        }
    },
    "elements": {
        "page_bg": {
            "type": "div", "position": {"top": 0, "left": 0}, "width": 736, "height": 1308,
            "background_color": "#FCFAF2", "z_index": 1
        },
        "rule_line": {
            "type": "div", "position": {"top": 736, "left": 184}, "width": 368, "height": 2,
            "background_color": "#D4AF37", "z_index": 5
        },
        "chapter": {
            "type": "text", "text": "CHEF'S SPECIALS",
            "position": {"top": 686, "left": 0}, "width": 736, "height": 37,
            "font_family": "'Inter', sans-serif", "font_size": 17, "font_weight": "600",
            "color": "#D4AF37", "text_align": "center", "letter_spacing": 4, "z_index": 10
        },
        "title": {
            "type": "text", "text": "Mastering the<br>Roasting Arts",
            "position": {"top": 797, "left": 61}, "width": 613, "height": 147,
            "font_family": "'Playfair Display', serif", "font_size": 51, "font_weight": "700",
            "color": "#2C2C2C", "text_align": "center", "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}", "position": {"top": 1201, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Lora', serif", "font_size": 20, "font_weight": "400",
            "color": "#888888", "text_align": "center", "font_style": "italic", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
