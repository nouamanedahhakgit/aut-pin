#!/usr/bin/env python3
"""Template 57: Top White Header -- white header top 30% with bold text, food photo bottom 70%.
Clean, structured, highly legible. Professional food blog style."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_57"

STYLE_SLOTS = {
    "header_bg": {"background_color": "surface"},
    "badge_bg": {"background_color": "primary"},
    "badge": {"color": "on_primary"},
    "label": {"color": "primary"},
    "title": {"color": "text_primary"},
    "divider": {"background_color": "primary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "badge": "body",
    "label": "accent",
    "title": "heading",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Top White Header Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t57.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'EASY RECIPE'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 400, "left": 0},
            "width": 736,
            "height": 908,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, bright natural light",
        },
    },
    "elements": {
        "header_bg": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 400,
            "background_color": "#FFFFFF",
            "z_index": 10,
        },
        "label": {
            "type": "text",
            "text": "EASY RECIPE",
            "position": {"top": 80, "left": 40},
            "width": 656,
            "height": 24,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 13,
            "font_weight": "600",
            "color": "#E07A5F",
            "text_align": "center",
            "letter_spacing": "4px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 120, "left": 30},
            "width": 676,
            "height": 200,
            "font_family": "Epilogue, Arial Black, sans-serif",
            "font_size": 54,
            "font_weight": "900",
            "color": "#1A1A1A",
            "text_align": "center",
            "line_height": 1.05,
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "badge_bg": {
            "type": "div",
            "position": {"top": 340, "left": 268},
            "width": 200,
            "height": 32,
            "background_color": "#1A1A1A",
            "z_index": 18,
        },
        "badge": {
            "type": "text",
            "text": "HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'EASY RECIPE'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 342, "left": 273},
            "width": 190,
            "height": 28,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 11,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "2px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "divider": {
            "type": "div",
            "position": {"top": 396, "left": 0},
            "width": 736,
            "height": 4,
            "background_color": "#1A1A1A",
            "z_index": 15,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1256, "left": 0},
            "width": 736,
            "height": 36,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 12,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "2px",
            "text_shadow": "0 1px 6px rgba(0,0,0,0.6)",
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
