#!/usr/bin/env python3
"""Template 56: Framed Center Card -- white card with sharp 2px black border centered
over full-bleed food photo. Bold blocky sans-serif title. Clean editorial style."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_56"

STYLE_SLOTS = {
    "card_bg": {"background_color": "surface"},
    "badge_bg": {"background_color": "primary"},
    "badge": {"color": "on_primary"},
    "title": {"color": "text_primary"},
    "subtitle": {"color": "text_secondary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "badge": "body",
    "title": "heading",
    "subtitle": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Framed Center Card Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t56.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'BEST EVER'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase (e.g. 'fluffy and delicious', 'so easy to make'). Max 30 characters. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, close-up, bright light",
        },
    },
    "elements": {
        "dim_overlay": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "background_color": "rgba(0,0,0,0.12)",
            "z_index": 5,
        },
        "card_bg": {
            "type": "div",
            "position": {"top": 380, "left": 100},
            "width": 536,
            "height": 440,
            "background_color": "#FFFFFF",
            "border": "2px solid #000000",
            "z_index": 10,
        },
        "badge_bg": {
            "type": "div",
            "position": {"top": 420, "left": 248},
            "width": 240,
            "height": 30,
            "background_color": "#000000",
            "z_index": 18,
        },
        "badge": {
            "type": "text",
            "text": "HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'BEST EVER'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 422, "left": 253},
            "width": 230,
            "height": 26,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 11,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "3px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 490, "left": 130},
            "width": 476,
            "height": 220,
            "font_family": "Epilogue, Arial Black, sans-serif",
            "font_size": 52,
            "font_weight": "900",
            "color": "#000000",
            "text_align": "center",
            "line_height": 1.1,
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "subtitle": {
            "type": "text",
            "text": "fluffy and delicious",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase (e.g. 'fluffy and delicious', 'so easy to make'). Max 30 characters. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 740, "left": 130},
            "width": 476,
            "height": 28,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 14,
            "font_weight": "400",
            "color": "#6B7280",
            "text_align": "center",
            "z_index": 20,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1250, "left": 0},
            "width": 736,
            "height": 36,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 13,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "2px",
            "text_shadow": "0 1px 6px rgba(0,0,0,0.7)",
            "z_index": 20,
        },
    },
    "background": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
}


def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
