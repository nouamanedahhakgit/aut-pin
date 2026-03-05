#!/usr/bin/env python3
"""Template 5: Top + bottom images + white band + cursive subtitle + bold title."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_5"

STYLE_SLOTS = {
    "white_band": {"background_color": "background"},
    "subtitle": {"color": "primary"},
    "title": {"color": "text_primary"},
}

FONT_SLOTS = {
    "subtitle": "heading",
    "title": "heading",
}

TEMPLATE_DATA = {
    "name": "Street Corn Chicken Bowl",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' in your output; the domain is provided separately.",
    "field_prompts": {
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing the SUBTITLE for a Pinterest food pin. Format: one short cursive-style tagline, 2–4 words only (e.g. 'Street Corn', 'Easy Homemade'). Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the TITLE for a Pinterest food pin. Format: one line, ALL CAPS, 2–4 words (e.g. 'CHICKEN BOWL', 'STREET CORN BOWL'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text in ALL CAPS.",
    },
    "images": {
        "top_image": {"description_prompt": "Close-up, overhead shot of a Street Corn Chicken Bowl with white rice, grilled chicken, creamy white sauce, fresh cilantro, yellow corn kernels, red onion, and a lime wedge. Food photography style.", "position": {"top": 0, "left": 0}, "width": 600, "height": 478, "layer_order": 1},
        "bottom_image": {"description_prompt": "Close-up, overhead shot of a Street Corn Chicken Bowl. Identical to the top image.", "position": {"top": 589, "left": 0}, "width": 600, "height": 478, "layer_order": 1},
    },
    "elements": {
        "white_band": {"type": "div", "position": {"top": 478, "left": 0}, "width": 600, "height": 111, "background_color": "#FFFFFF", "z_index": 5},
        "subtitle": {
            "type": "text",
            "text": "Street Corn",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing the SUBTITLE for a Pinterest food pin. Format: one short cursive-style tagline, 2–4 words only (e.g. 'Street Corn', 'Easy Homemade'). Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 485, "left": 0}, "width": 600, "height": 48, "font_family": "'Dancing Script', cursive", "font_size": 48, "font_weight": "400", "color": "#000000", "text_align": "center", "line_height": 1, "z_index": 10,
        },
        "title": {
            "type": "text",
            "text": "CHICKEN BOWL",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the TITLE for a Pinterest food pin. Format: one line, ALL CAPS, 2–4 words (e.g. 'CHICKEN BOWL', 'STREET CORN BOWL'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text in ALL CAPS.",
            "position": {"top": 532, "left": 20}, "width": 560, "height": 55, "font_family": "'Bebas Neue', sans-serif", "font_size": 50, "font_weight": "400", "color": "#000000", "text_align": "center", "text_transform": "uppercase", "line_height": 1.0, "z_index": 10,
        },
    },
    "top_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/midjourney_splits/main/476/25bfa9d3f71.png",
    "bottom_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/midjourney_splits/main/476/25bfa9d3f71.png",
}


def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
