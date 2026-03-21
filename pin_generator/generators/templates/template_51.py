#!/usr/bin/env python3
"""Template 51: Bento Grid — 4-image collage with center title strip. Modern, magazine-style layout.
Each quadrant shows a different angle; center band holds bold title. Highly visual, Pinterest-trending."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_51"

STYLE_SLOTS = {
    "center_band": {"background_color": "surface"},
    "accent_line": {"background_color": "primary"},
    "title": {"color": "text_primary"},
    "tagline": {"color": "text_secondary"},
    "website": {"color": "text_secondary"},
}

FONT_SLOTS = {
    "title": "heading",
    "tagline": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Bento Grid",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t51.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3-8 words (e.g. 'Million Dollar Chicken Salad'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "tagline": "Generate content for tagline for recipe {{title}}. You are writing a short TAGLINE for a Pinterest food pin. Format: 3-6 words, lowercase or title case, evocative (e.g. 'Crispy. Golden. Irresistible.', 'Simple. Delicious. Perfect.'). Output ONLY the replacement text for tagline, no quotes. Given the user's recipe title {{title}}, return only the tagline text.",
    },
    "images": {
        "top_left": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 368,
            "height": 420,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Close-up detail of dish, appetizing food photography",
        },
        "top_right": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 368},
            "width": 368,
            "height": 420,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Overhead shot of ingredients or plating, bright styling",
        },
        "bottom_left": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 528, "left": 0},
            "width": 368,
            "height": 420,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Serving suggestion or finished plate, warm tones",
        },
        "bottom_right": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 528, "left": 368},
            "width": 368,
            "height": 420,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Texture or garnish detail, appetizing close-up",
        },
    },
    "elements": {
        "center_band": {
            "type": "div",
            "position": {"top": 420, "left": 0},
            "width": 736,
            "height": 108,
            "background_color": "#FAFAFA",
            "z_index": 15,
        },
        "accent_line": {
            "type": "div",
            "position": {"top": 420, "left": 0},
            "width": 6,
            "height": 108,
            "background_color": "#E07C5E",
            "z_index": 16,
        },
        "title": {
            "type": "text",
            "text": "Your Recipe Title Here",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3-8 words (e.g. 'Million Dollar Chicken Salad'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 432, "left": 24},
            "width": 688,
            "height": 52,
            "font_family": "Playfair Display, Georgia, serif",
            "font_size": 36,
            "font_weight": "700",
            "color": "#1A1A1A",
            "text_align": "center",
            "line_height": 1.1,
            "z_index": 20,
        },
        "tagline": {
            "type": "text",
            "text": "Crispy. Golden. Irresistible.",
            "text_prompt": "Generate content for tagline for recipe {{title}}. You are writing a short TAGLINE for a Pinterest food pin. Format: 3-6 words, lowercase or title case, evocative (e.g. 'Crispy. Golden. Irresistible.', 'Simple. Delicious. Perfect.'). Output ONLY the replacement text for tagline, no quotes. Given the user's recipe title {{title}}, return only the tagline text.",
            "position": {"top": 478, "left": 24},
            "width": 688,
            "height": 36,
            "font_family": "Lato, Arial, sans-serif",
            "font_size": 18,
            "font_weight": "400",
            "color": "#6B7280",
            "text_align": "center",
            "letter_spacing": "1px",
            "z_index": 20,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1260, "left": 0},
            "width": 736,
            "height": 40,
            "font_family": "Lato, Arial, sans-serif",
            "font_size": 16,
            "font_weight": "600",
            "color": "#9CA3AF",
            "text_align": "center",
            "letter_spacing": "0.5px",
            "z_index": 20,
        },
    },
    "top_left": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
    "top_right": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
    "bottom_left": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
    "bottom_right": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
}


def run(output_dir=None):
    apply_domain_style(
        TEMPLATE_DATA,
        STYLE_SLOTS,
        FONT_SLOTS,
        TEMPLATE_DATA.get("domain_colors"),
        TEMPLATE_DATA.get("domain_fonts"),
    )
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
