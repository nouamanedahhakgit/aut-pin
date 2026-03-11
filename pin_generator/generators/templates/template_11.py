#!/usr/bin/env python3
"""Template 11: Vibrant Bistro. High-energy layout with dual split image and central focus badge."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_11"

# Theme: Modern Brutalist Pop
STYLE_SLOTS = {
    "center_plate": {"background_color": "background"},
    "badge": {"background_color": "primary", "color": "on_primary"},
    "title": {"color": "text_primary"},
    "footer": {"background_color": "text_primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "badge": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Vibrant Bistro Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/690bc9326cf.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text.",
    "field_prompts": {
        "title": "Bold recipe name for {{title}}. 2–4 words, uppercase.",
        "badge": "Exciting promo word (e.g. 'TASTY', 'YUM!'). 1 word, ALL CAPS."
    },
    "images": {
        "top_image": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "description_prompt": "High-impact food photo of {{title}}, saturated colors, bistro style.",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 450, "layer_order": 1
        },
        "bottom_image": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "description_prompt": "Detail shot of fresh ingredients or serving suggestion for {{title}}.",
            "position": {"top": 617, "left": 0}, "width": 600, "height": 450, "layer_order": 1
        }
    },
    "elements": {
        "center_plate": {
            "type": "div",
            "position": {"top": 400, "left": 40}, "width": 520, "height": 267,
            "background_color": "#FFFFFF", "border": {"width": 6, "color": "#000000"},
            "z_index": 5
        },
        "badge": {
            "type": "text",
            "text": "YUM!",
            "position": {"top": 375, "left": 220}, "width": 160, "height": 60,
            "font_family": "'Inter', sans-serif", "font_size": 24, "font_weight": "900",
            "color": "#FFFFFF", "background_color": "#EF4444", "text_align": "center",
            "text_transform": "uppercase", "rotation": -5, "border": {"width": 4, "color": "#000000"},
            "z_index": 20
        },
        "title": {
            "type": "text",
            "text": "CRISPY FISH<br>TACOS",
            "position": {"top": 440, "left": 70}, "width": 460, "height": 160,
            "font_family": "'Bebas Neue', sans-serif", "font_size": 72, "font_weight": "400",
            "color": "#111827", "text_align": "center", "line_height": 1.0, "z_index": 10
        },
        "stars": {"type": "stars", "count": 5, "position": {"top": 590, "left": 200}, "star_size": 28, "color": "#F59E0B", "z_index": 10},
        "footer": {
            "type": "div",
            "position": {"top": 1027, "left": 0}, "width": 600, "height": 40,
            "background_color": "#000000", "z_index": 10
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1027, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "z_index": 20
        }
    },
    "top_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
    "bottom_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png"
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
