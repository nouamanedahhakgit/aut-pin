#!/usr/bin/env python3
"""Template 2: Top + bottom images + colored banner + subtitle + title + website bar."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_2"

STYLE_SLOTS = {
    "purple_banner": {"background_color": "primary"},
    "subtitle": {"color": "secondary"},
    "title": {"color": "on_primary"},
    "website_bar": {"background_color": "text_primary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "subtitle": "heading",
    "title": "heading",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Oreo Cinnamon Rolls",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t2.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing the SUBTITLE for a Pinterest food pin. Format: short tagline in ALL CAPS, 2–5 words (e.g. 'Delicious in Minutes', 'Quick & Easy'). Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title in ALL CAPS, 1–4 words (e.g. 'Couscous', 'OREO CINNAMON ROLLS'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
    },
    "images": {
        "top_image": {"description_prompt": "Close-up Oreo cinnamon rolls, food photography", "position": {"top": 0, "left": 0}, "width": 736, "height": 552, "layer_order": 1},
        "bottom_image": {"description_prompt": "Oreo cinnamon rolls on tray, food photography", "position": {"top": 756, "left": 0}, "width": 736, "height": 552, "layer_order": 1},
    },
    "elements": {
        "purple_banner": {"type": "div", "position": {"top": 552, "left": 0}, "width": 736, "height": 205, "background_color": "#3D2B4F", "z_index": 10},
        "subtitle": {
            "type": "text",
            "text": "Delicious in Minutes",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing the SUBTITLE for a Pinterest food pin. Format: short tagline in ALL CAPS, 2–5 words (e.g. 'Delicious in Minutes', 'Quick & Easy'). Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 570, "left": 25}, "width": 687, "height": 49, "font_family": "Arial Black, sans-serif", "font_size": 39, "font_weight": "900", "color": "#FBBF24", "text_align": "center", "text_transform": "uppercase", "letter_spacing": 2, "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "Couscous",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title in ALL CAPS, 1–4 words (e.g. 'Couscous', 'OREO CINNAMON ROLLS'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 625, "left": 25}, "width": 687, "height": 110, "font_family": "Arial Black, sans-serif", "font_size": 51, "font_weight": "900", "color": "#F9FAFB", "text_align": "center", "text_transform": "uppercase", "line_height": 1.1, "z_index": 20,
        },
        "website_bar": {"type": "div", "position": {"top": 715, "left": 0}, "width": 736, "height": 42, "background_color": "#111827", "z_index": 10},
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 721, "left": 25}, "width": 687, "height": 29, "font_family": "Georgia, serif", "font_size": 27, "font_weight": "normal", "color": "#FFFFFF", "text_align": "center", "font_style": "italic", "z_index": 20,
        },
    },
    "top_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/midjourney_splits/main/476/25bfa9d3f71.png",
    "bottom_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/midjourney_splits/main/476/ccbfc53a614.png",
}


def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
