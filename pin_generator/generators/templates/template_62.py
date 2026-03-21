#!/usr/bin/env python3
"""Template 62: Bottom White Footer -- food photo fills top 75%, clean white footer 25%.
Coral badge, bold serif title, gray subtitle. Professional cookbook style."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_62"

STYLE_SLOTS = {
    "footer_bg": {"background_color": "surface"},
    "badge_bg": {"background_color": "primary"},
    "badge": {"color": "on_primary"},
    "title": {"color": "text_primary"},
    "subtitle": {"color": "text_secondary"},
    "website": {"color": "text_secondary"},
}

FONT_SLOTS = {
    "badge": "body",
    "title": "heading",
    "subtitle": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Bottom White Footer Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t62.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters. Output ONLY the replacement text for badge, no quotes.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase. Max 30 characters. Output ONLY the replacement text for subtitle, no quotes.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 960,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, close-up, bright light",
        },
    },
    "elements": {
        "footer_bg": {
            "type": "div",
            "position": {"top": 960, "left": 0},
            "width": 736,
            "height": 348,
            "background_color": "#FFFFFF",
            "z_index": 10,
        },
        "badge_bg": {
            "type": "div",
            "position": {"top": 990, "left": 40},
            "width": 170,
            "height": 30,
            "background_color": "#E07A5F",
            "border_radius": "4px",
            "z_index": 18,
        },
        "badge": {
            "type": "text",
            "text": "HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters. Output ONLY the replacement text for badge, no quotes.",
            "position": {"top": 993, "left": 45},
            "width": 160,
            "height": 24,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 11,
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
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
            "position": {"top": 1040, "left": 40},
            "width": 656,
            "height": 140,
            "font_family": "Playfair Display, Georgia, serif",
            "font_size": 44,
            "font_weight": "700",
            "color": "#1A1A1A",
            "text_align": "left",
            "line_height": 1.15,
            "z_index": 20,
        },
        "subtitle": {
            "type": "text",
            "text": "no flour needed",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase. Max 30 characters. Output ONLY the replacement text for subtitle, no quotes.",
            "position": {"top": 1200, "left": 40},
            "width": 400,
            "height": 28,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 14,
            "font_weight": "400",
            "color": "#6B7280",
            "text_align": "left",
            "z_index": 20,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1260, "left": 0},
            "width": 736,
            "height": 30,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 11,
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
