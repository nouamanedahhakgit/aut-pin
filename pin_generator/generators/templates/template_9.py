#!/usr/bin/env python3
"""Template 9: Minimalist Editorial. High-end magazine layout with white header and clean serif title."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_9"

# Theme: Minimalist Clean
STYLE_SLOTS = {
    "header": {"background_color": "background"},
    "title": {"color": "text_primary"},
    "subtitle": {"color": "primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "subtitle": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Minimalist Editorial Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/70b230415f9.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}.",
    "field_prompts": {
        "title": "Refined title for recipe {{title}}. 3–5 words, mixed case.",
        "subtitle": "Short, elegant tagline for recipe {{title}}. 4–6 words, all caps, muted tone."
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "description_prompt": "Clean, minimalist food photography of {{title}}, soft shadows, bright natural light, top-down or slight angle.",
            "position": {"top": 441, "left": 0}, "width": 736, "height": 867, "layer_order": 1
        }
    },
    "elements": {
        "header": {
            "type": "div",
            "position": {"top": 0, "left": 0}, "width": 736, "height": 441,
            "background_color": "#FFFFFF", "z_index": 5
        },
        "title": {
            "type": "text",
            "text": "Artisan Garlic Herb Focaccia",
            "position": {"top": 98, "left": 74}, "width": 589, "height": 196,
            "font_family": "'Playfair Display', serif", "font_size": 51, "font_weight": "900",
            "color": "#1A1A1A", "text_align": "center", "line_height": 1.2, "z_index": 10
        },
        "subtitle": {
            "type": "text",
            "text": "THE PERFECT GOLDEN CRUST",
            "position": {"top": 294, "left": 123}, "width": 491, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 20, "font_weight": "700",
            "color": "#D27D56", "text_align": "center", "text_transform": "uppercase",
            "letter_spacing": 4, "z_index": 10
        },
        "line": {
            "type": "div",
            "position": {"top": 270, "left": 307}, "width": 123, "height": 2,
            "background_color": "#E5E7EB", "z_index": 10
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1226, "left": 0}, "width": 736, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 20, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "text_transform": "uppercase",
            "text_shadow": "0 2px 5px rgba(0,0,0,0.5)", "z_index": 10
        }
    },
    "background": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png"
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
