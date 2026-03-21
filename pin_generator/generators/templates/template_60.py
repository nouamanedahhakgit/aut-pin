#!/usr/bin/env python3
"""Template 60: 70/30 White Header -- 70% white area with massive green text, 30% food photo bottom.
Fresh healthy vibe with forest green typography. Extremely mobile-friendly."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_60"

STYLE_SLOTS = {
    "header_bg": {"background_color": "surface"},
    "badge_bg": {"background_color": "primary"},
    "badge": {"color": "on_primary"},
    "title": {"color": "primary"},
    "divider": {"background_color": "text_secondary"},
    "website": {"color": "text_secondary"},
}

FONT_SLOTS = {
    "badge": "body",
    "title": "heading",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "70/30 White Header Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t60.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-4 words, all uppercase, max 22 characters (e.g. 'EASY HIGH PROTEIN'). Output ONLY the replacement text for badge, no quotes.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), all uppercase, 2-4 words, max 30 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 900, "left": 0},
            "width": 736,
            "height": 408,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, bright, close-up",
        },
    },
    "elements": {
        "header_bg": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 900,
            "background_color": "#FFFFFF",
            "z_index": 2,
        },
        "badge_bg": {
            "type": "div",
            "position": {"top": 200, "left": 228},
            "width": 280,
            "height": 36,
            "background_color": "#E07A5F",
            "border_radius": "18px",
            "z_index": 18,
        },
        "badge": {
            "type": "text",
            "text": "EASY HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-4 words, all uppercase, max 22 characters (e.g. 'EASY HIGH PROTEIN'). Output ONLY the replacement text for badge, no quotes.",
            "position": {"top": 204, "left": 233},
            "width": 270,
            "height": 28,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 12,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "2px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), all uppercase, 2-4 words, max 30 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
            "position": {"top": 300, "left": 40},
            "width": 656,
            "height": 400,
            "font_family": "Epilogue, Arial Black, sans-serif",
            "font_size": 86,
            "font_weight": "900",
            "color": "#065F46",
            "text_align": "center",
            "line_height": 1.0,
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "divider": {
            "type": "div",
            "position": {"top": 780, "left": 230},
            "width": 276,
            "height": 1,
            "background_color": "#9CA3AF",
            "z_index": 15,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 800, "left": 0},
            "width": 736,
            "height": 30,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 12,
            "font_weight": "500",
            "color": "#9CA3AF",
            "text_align": "center",
            "letter_spacing": "3px",
            "text_transform": "uppercase",
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
