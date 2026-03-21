#!/usr/bin/env python3
"""Template 55: Split Color Block -- food photo top 50%, solid coral block bottom 50%.
Bold chunky white text on the coral section. HIGH PROTEIN badge. Modern fitness blogger style."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_55"

STYLE_SLOTS = {
    "color_block": {"background_color": "primary"},
    "badge_bg": {"background_color": "surface"},
    "badge": {"color": "on_primary"},
    "title": {"color": "on_primary"},
    "subtitle": {"color": "on_primary"},
    "website": {"color": "on_primary"},
}

FONT_SLOTS = {
    "badge": "body",
    "title": "heading",
    "subtitle": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Split Color Block Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t55.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'QUICK & EASY', 'BEST EVER'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words describing a key benefit or feature, lowercase (e.g. 'ready in 20 minutes', 'so easy and delicious'). Max 30 characters. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 654,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, close-up overhead shot",
        },
    },
    "elements": {
        "color_block": {
            "type": "div",
            "position": {"top": 654, "left": 0},
            "width": 736,
            "height": 654,
            "background_color": "#C84B31",
            "z_index": 10,
        },
        "badge_bg": {
            "type": "div",
            "position": {"top": 690, "left": 40},
            "width": 160,
            "height": 32,
            "background_color": "#000000",
            "z_index": 18,
        },
        "badge": {
            "type": "text",
            "text": "HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'QUICK & EASY', 'BEST EVER'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 692, "left": 45},
            "width": 150,
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
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 770, "left": 40},
            "width": 656,
            "height": 240,
            "font_family": "Epilogue, Impact, Arial Black, sans-serif",
            "font_size": 62,
            "font_weight": "900",
            "color": "#FFFFFF",
            "text_align": "left",
            "line_height": 1.05,
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "subtitle": {
            "type": "text",
            "text": "ready in 20 minutes",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words describing a key benefit or feature, lowercase (e.g. 'ready in 20 minutes', 'so easy and delicious'). Max 30 characters. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 1050, "left": 40},
            "width": 656,
            "height": 30,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 15,
            "font_weight": "400",
            "color": "rgba(255,255,255,0.8)",
            "text_align": "left",
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
