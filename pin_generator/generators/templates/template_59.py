#!/usr/bin/env python3
"""Template 59: Sandwich Divider -- food photo top, text band middle, food photo bottom.
Outlined display font + solid font contrast. Orange badge. Modern graphic style."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_59"

STYLE_SLOTS = {
    "band_bg": {"background_color": "surface"},
    "badge_bg": {"background_color": "primary"},
    "badge": {"color": "on_primary"},
    "title": {"color": "text_primary"},
    "subtitle": {"color": "text_primary"},
    "line_top": {"background_color": "text_primary"},
    "line_bottom": {"background_color": "text_primary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "badge": "body",
    "title": "heading",
    "subtitle": "heading",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Sandwich Divider Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t59.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters. Output ONLY the replacement text for badge, no quotes.",
        "title": "Generate content for title for recipe {{title}}. You are writing the first word or key ingredient of the recipe, all uppercase, 1-2 words max. Output ONLY the replacement text for title, no quotes.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing the rest of the recipe name, 1-3 words, title case. Output ONLY the replacement text for subtitle, no quotes.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 520,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, overhead shot",
        },
        "background_bottom": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 850, "left": 0},
            "width": 736,
            "height": 458,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, side angle",
        },
    },
    "elements": {
        "band_bg": {
            "type": "div",
            "position": {"top": 520, "left": 0},
            "width": 736,
            "height": 330,
            "background_color": "#FAFAFA",
            "z_index": 10,
        },
        "line_top": {
            "type": "div",
            "position": {"top": 520, "left": 0},
            "width": 736,
            "height": 3,
            "background_color": "#1A1A1A",
            "z_index": 15,
        },
        "line_bottom": {
            "type": "div",
            "position": {"top": 847, "left": 0},
            "width": 736,
            "height": 3,
            "background_color": "#1A1A1A",
            "z_index": 15,
        },
        "badge_bg": {
            "type": "div",
            "position": {"top": 550, "left": 278},
            "width": 180,
            "height": 30,
            "background_color": "#E07A5F",
            "z_index": 18,
        },
        "badge": {
            "type": "text",
            "text": "HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters. Output ONLY the replacement text for badge, no quotes.",
            "position": {"top": 553, "left": 283},
            "width": 170,
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
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the first word or key ingredient of the recipe, all uppercase, 1-2 words max. Output ONLY the replacement text for title, no quotes.",
            "position": {"top": 610, "left": 40},
            "width": 656,
            "height": 90,
            "font_family": "Epilogue, Arial Black, sans-serif",
            "font_size": 64,
            "font_weight": "900",
            "color": "#1A1A1A",
            "text_align": "center",
            "line_height": 1.0,
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "subtitle": {
            "type": "text",
            "text": "Fried Eggs",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing the rest of the recipe name, 1-3 words, title case. Output ONLY the replacement text for subtitle, no quotes.",
            "position": {"top": 710, "left": 40},
            "width": 656,
            "height": 60,
            "font_family": "Epilogue, Arial Black, sans-serif",
            "font_size": 48,
            "font_weight": "900",
            "color": "#1A1A1A",
            "text_align": "center",
            "line_height": 1.0,
            "z_index": 20,
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
