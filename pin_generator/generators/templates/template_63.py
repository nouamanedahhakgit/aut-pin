#!/usr/bin/env python3
"""Template 63: Dark Moody Overlay -- full food photo with dark semi-transparent overlay.
Gold accent elements, white serif title. Premium, luxurious, magazine-cover aesthetic."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_63"

STYLE_SLOTS = {
    "badge": {"color": "secondary"},
    "stars": {"color": "secondary"},
    "title": {"color": "on_dark"},
    "subtitle": {"color": "on_dark"},
    "accent_line": {"background_color": "secondary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "badge": "accent",
    "title": "heading",
    "subtitle": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Dark Moody Overlay Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t63.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters. Output ONLY the replacement text for badge, no quotes.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase italic style. Max 30 characters. Output ONLY the replacement text for subtitle, no quotes.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, moody lighting",
        },
    },
    "elements": {
        "dark_overlay": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "background_color": "rgba(0,0,0,0.55)",
            "z_index": 5,
        },
        "accent_line_top": {
            "type": "div",
            "position": {"top": 440, "left": 328},
            "width": 80,
            "height": 2,
            "background_color": "#D4A574",
            "z_index": 20,
        },
        "badge": {
            "type": "text",
            "text": "THE BEST EVER",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters. Output ONLY the replacement text for badge, no quotes.",
            "position": {"top": 465, "left": 100},
            "width": 536,
            "height": 28,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 13,
            "font_weight": "600",
            "color": "#D4A574",
            "text_align": "center",
            "letter_spacing": "5px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "stars": {
            "type": "stars",
            "count": 5,
            "position": {"top": 515, "left": 290},
            "star_size": 24,
            "color": "#FFD700",
            "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
            "position": {"top": 570, "left": 80},
            "width": 576,
            "height": 220,
            "font_family": "Playfair Display, Georgia, serif",
            "font_size": 52,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "line_height": 1.15,
            "z_index": 20,
        },
        "subtitle": {
            "type": "text",
            "text": "prep in 5 minutes",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase italic style. Max 30 characters. Output ONLY the replacement text for subtitle, no quotes.",
            "position": {"top": 810, "left": 100},
            "width": 536,
            "height": 28,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 15,
            "font_weight": "400",
            "color": "rgba(255,255,255,0.8)",
            "text_align": "center",
            "z_index": 20,
        },
        "accent_line_bottom": {
            "type": "div",
            "position": {"top": 860, "left": 338},
            "width": 60,
            "height": 2,
            "background_color": "#D4A574",
            "z_index": 20,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1250, "left": 0},
            "width": 736,
            "height": 36,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 12,
            "font_weight": "600",
            "color": "rgba(255,255,255,0.6)",
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
