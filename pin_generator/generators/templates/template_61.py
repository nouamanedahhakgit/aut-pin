#!/usr/bin/env python3
"""Template 61: Bold Direct Text -- text placed directly on full-bleed food photo with
heavy shadows. NO cards, NO panels. Minimalist food-forward. The image is the hero."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_61"

STYLE_SLOTS = {
    "badge": {"color": "on_dark"},
    "title": {"color": "on_dark"},
    "subtitle": {"color": "on_dark"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "badge": "body",
    "title": "heading",
    "subtitle": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Bold Direct Text Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t61.png",
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
            "height": 1308,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, vibrant, close-up",
        },
    },
    "elements": {
        "gradient_overlay": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "background": "linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.55) 100%)",
            "z_index": 5,
        },
        "badge": {
            "type": "text",
            "text": "HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters. Output ONLY the replacement text for badge, no quotes.",
            "position": {"top": 860, "left": 40},
            "width": 656,
            "height": 28,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 13,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "left",
            "letter_spacing": "5px",
            "text_transform": "uppercase",
            "text_shadow": "0 2px 8px rgba(0,0,0,0.7)",
            "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
            "position": {"top": 910, "left": 40},
            "width": 656,
            "height": 240,
            "font_family": "Epilogue, Impact, Arial Black, sans-serif",
            "font_size": 64,
            "font_weight": "900",
            "color": "#FFFFFF",
            "text_align": "left",
            "line_height": 1.0,
            "text_transform": "uppercase",
            "text_shadow": "0 3px 12px rgba(0,0,0,0.6)",
            "z_index": 20,
        },
        "subtitle": {
            "type": "text",
            "text": "loaded with 30g protein",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase. Max 30 characters. Output ONLY the replacement text for subtitle, no quotes.",
            "position": {"top": 1170, "left": 40},
            "width": 656,
            "height": 30,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 15,
            "font_weight": "400",
            "color": "rgba(255,255,255,0.85)",
            "text_align": "left",
            "text_shadow": "0 1px 6px rgba(0,0,0,0.6)",
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
            "color": "rgba(255,255,255,0.7)",
            "text_align": "center",
            "letter_spacing": "3px",
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
