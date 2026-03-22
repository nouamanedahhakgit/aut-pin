#!/usr/bin/env python3
"""Template 64: Orange Header Bold -- vibrant orange header block with ultra-bold
white title, black pill badge, food photo with large rounded top corners,
and dark footer bar with website URL.
Inspired by high-engagement Pinterest recipe pins."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_64"

STYLE_SLOTS = {
    "header_bg": {"background_color": "primary"},
    "badge_bg": {"background_color": "text_primary"},
    "badge": {"color": "on_dark"},
    "subtitle": {"color": "on_primary"},
    "title": {"color": "on_primary"},
    "footer_bar": {"background_color": "text_primary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "subtitle": "body",
    "title": "heading",
    "badge": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Orange Header Bold Pin",
    "preview_url": "",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16", "background_color": "#1A1A1A"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing the small SUBTITLE line displayed above the main title on a Pinterest food pin. Format: 1-2 words, all uppercase, max 16 characters (e.g. 'COTTAGE CHEESE', 'CREAMY GARLIC', 'CHOCOLATE'). This describes the key ingredient or qualifier. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: 1-3 words, all uppercase, ultra-bold impact style, max 20 characters (e.g. 'STUFFED PEPPERS', 'PASTA BAKE', 'BROWNIES'). This is the dish name without the qualifier. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin inside a dark pill shape. Format: 3-5 words, all uppercase, max 24 characters (e.g. 'EASY & HIGH PROTEIN', 'QUICK 30 MIN RECIPE', 'FAMILY FAVORITE'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
    },
    "images": {
        "food_image": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/28c59a81/f78e79c055d.png",
            "position": {"top": 340, "left": 38},
            "width": 660,
            "height": 880,
            "layer_order": 2,
            "object_fit": "cover",
            "border_radius": "40px 40px 0 0",
            "description_prompt": "Appetizing food photography, close-up, overhead angle, vibrant colors",
        },
    },
    "elements": {
        # ── Orange header background filling top portion ──
        "header_bg": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 420,
            "background_color": "#F29924",
            "z_index": 1,
        },
        # ── Small subtitle text above the bold title ──
        "subtitle": {
            "type": "text",
            "text": "COTTAGE CHEESE",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing the small SUBTITLE line displayed above the main title on a Pinterest food pin. Format: 1-2 words, all uppercase, max 16 characters (e.g. 'COTTAGE CHEESE', 'CREAMY GARLIC', 'CHOCOLATE'). This describes the key ingredient or qualifier. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 38, "left": 40},
            "width": 656,
            "height": 36,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 18,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "5px",
            "text_transform": "uppercase",
            "z_index": 10,
        },
        # ── Ultra-bold main title ──
        "title": {
            "type": "text",
            "text": "STUFFED\nPEPPERS",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: 1-3 words, all uppercase, ultra-bold impact style, max 20 characters (e.g. 'STUFFED PEPPERS', 'PASTA BAKE', 'BROWNIES'). This is the dish name without the qualifier. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 68, "left": 40},
            "width": 656,
            "height": 230,
            "font_family": "Epilogue, Impact, Arial Black, sans-serif",
            "font_size": 88,
            "font_weight": "900",
            "color": "#FFFFFF",
            "text_align": "center",
            "line_height": 1.0,
            "text_transform": "uppercase",
            "z_index": 10,
        },
        # ── Black pill-shaped badge ──
        "badge_bg": {
            "type": "div",
            "position": {"top": 302, "left": 208},
            "width": 320,
            "height": 44,
            "background_color": "#1A1A1A",
            "border_radius": "22px",
            "z_index": 12,
        },
        "badge": {
            "type": "text",
            "text": "EASY & HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin inside a dark pill shape. Format: 3-5 words, all uppercase, max 24 characters (e.g. 'EASY & HIGH PROTEIN', 'QUICK 30 MIN RECIPE', 'FAMILY FAVORITE'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 305, "left": 213},
            "width": 310,
            "height": 38,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 14,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "2px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        # ── Dark footer bar ──
        "footer_bar": {
            "type": "div",
            "position": {"top": 1248, "left": 0},
            "width": 736,
            "height": 60,
            "background_color": "#1A1A1A",
            "z_index": 10,
        },
        # ── Website URL in footer ──
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1256, "left": 0},
            "width": 736,
            "height": 44,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 13,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "3px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
    },
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
