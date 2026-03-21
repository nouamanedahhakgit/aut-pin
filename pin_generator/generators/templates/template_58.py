#!/usr/bin/env python3
"""Template 58: Black-Out Banner -- full-bleed food photo with a thick black horizontal
banner across the upper-middle. Huge white Impact-style text. Maximum contrast."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_58"

STYLE_SLOTS = {
    "banner": {"background_color": "primary"},
    "badge_bg": {"background_color": "surface"},
    "badge": {"color": "text_primary"},
    "title": {"color": "on_primary"},
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
    "name": "Black-Out Banner Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t58.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'MUST TRY'). Output ONLY the replacement text for badge, no quotes.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase (e.g. '6 ingredients only'). Max 30 characters. Output ONLY the replacement text for subtitle, no quotes.",
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
            "background_color": "rgba(0,0,0,0.08)",
            "z_index": 5,
        },
        "banner": {
            "type": "div",
            "position": {"top": 420, "left": 0},
            "width": 736,
            "height": 320,
            "background_color": "#000000",
            "z_index": 10,
        },
        "badge_bg": {
            "type": "div",
            "position": {"top": 390, "left": 268},
            "width": 200,
            "height": 34,
            "background_color": "#FFFFFF",
            "z_index": 18,
        },
        "badge": {
            "type": "text",
            "text": "HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'MUST TRY'). Output ONLY the replacement text for badge, no quotes.",
            "position": {"top": 392, "left": 273},
            "width": 190,
            "height": 30,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 12,
            "font_weight": "700",
            "color": "#000000",
            "text_align": "center",
            "letter_spacing": "3px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes.",
            "position": {"top": 460, "left": 40},
            "width": 656,
            "height": 220,
            "font_family": "Epilogue, Impact, Arial Black, sans-serif",
            "font_size": 60,
            "font_weight": "900",
            "color": "#FFFFFF",
            "text_align": "center",
            "line_height": 1.05,
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "subtitle": {
            "type": "text",
            "text": "6 ingredients only",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words, lowercase (e.g. '6 ingredients only'). Max 30 characters. Output ONLY the replacement text for subtitle, no quotes.",
            "position": {"top": 760, "left": 0},
            "width": 736,
            "height": 30,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 15,
            "font_weight": "400",
            "color": "#FFFFFF",
            "text_align": "center",
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
            "color": "#FFFFFF",
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
