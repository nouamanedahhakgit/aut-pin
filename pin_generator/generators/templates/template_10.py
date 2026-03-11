#!/usr/bin/env python3
"""Template 10: Midnight Slate. Premium dark theme with slanted blade overlay and gold accents."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_10"

# Theme: Midnight Luxe
STYLE_SLOTS = {
    "blade": {"background_color": "text_primary"},
    "title": {"color": "on_dark"},
    "accent_line": {"background_color": "primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "badge": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Midnight Slate Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/a05ea757750.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text.",
    "field_prompts": {
        "title": "Powerful title for recipe {{title}}. 2–4 words, ALL CAPS.",
        "badge": "Short promotional tag. 1 word, ALL CAPS."
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "description_prompt": "Moody, dark-themed food photography of {{title}}, cinematic lighting, rich textures, deep shadows.",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": 1
        }
    },
    "elements": {
        "blade": {
            "type": "div",
            "position": {"top": 600, "left": -50}, "width": 700, "height": 500,
            "background_color": "#111827", "rotation": -5, "z_index": 5, "opacity": 0.95
        },
        "accent_line": {
            "type": "div",
            "position": {"top": 595, "left": -50}, "width": 700, "height": 8,
            "background_color": "#FACC15", "rotation": -5, "z_index": 10
        },
        "title": {
            "type": "text",
            "text": "SMOKED BBQ<br>BRISKET",
            "position": {"top": 680, "left": 40}, "width": 520, "height": 200,
            "font_family": "'Bebas Neue', sans-serif", "font_size": 80, "font_weight": "400",
            "color": "#FFFFFF", "text_align": "left", "text_transform": "uppercase",
            "line_height": 1.0, "z_index": 15
        },
        "badge": {
            "type": "text",
            "text": "PREMIUM",
            "position": {"top": 860, "left": 40}, "width": 140, "height": 50,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "900",
            "color": "#FACC15", "text_align": "left", "text_transform": "uppercase",
            "letter_spacing": 3, "z_index": 15
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "700",
            "color": "#94A3B8", "text_align": "center", "text_transform": "uppercase",
            "z_index": 20
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
