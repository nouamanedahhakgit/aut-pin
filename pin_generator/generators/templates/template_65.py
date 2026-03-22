#!/usr/bin/env python3
"""Template 65: Full-Bleed Overlay Card -- full-bleed food photo background with
centered white rectangular text overlay card. Script-style top line, large bold
serif title in burnt orange, small uppercase sans-serif subtitle, and dark
footer bar with website URL. Clean, readable, high-engagement Pinterest style."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_65"

STYLE_SLOTS = {
    "card_bg": {"background_color": "surface"},
    "script_text": {"color": "text_primary"},
    "title": {"color": "primary"},
    "subtitle": {"color": "text_primary"},
    "footer_bar": {"background_color": "text_primary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "script_text": "accent",
    "title": "heading",
    "subtitle": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Full-Bleed Overlay Card Pin",
    "preview_url": "",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "script_text": "Generate content for script_text for recipe {{title}}. You are writing an elegant script-style descriptor displayed above the main title on a Pinterest food pin. Format: 1-3 words, title case, cursive style, max 18 characters (e.g. '2-Ingredient', 'One-Pot', 'No-Bake', 'Grandma's'). This describes a key qualifier or attribute. Output ONLY the replacement text for script_text, no quotes. Given the user's recipe title {{title}}, return only the script_text text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main large TITLE for a Pinterest food pin. Format: 1-2 words, title case, bold serif style, max 14 characters (e.g. 'Cheesecake', 'Brownies', 'Pasta Bake'). This is the dish name. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE below the title on a Pinterest food pin. Format: 3-6 words, all uppercase, max 30 characters (e.g. 'EASY & HIGH PROTEIN RECIPE', 'QUICK 30 MINUTE DINNER', 'FAMILY FAVORITE DESSERT'). Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/28c59a81/f78e79c055d.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, bright natural light, close-up shot",
        },
    },
    "elements": {
        # ── White text overlay card ──
        "card_bg": {
            "type": "div",
            "position": {"top": 530, "left": 68},
            "width": 600,
            "height": 250,
            "background_color": "rgba(255, 255, 255, 0.95)",
            "box_shadow": "0 4px 20px rgba(0,0,0,0.12)",
            "z_index": 10,
        },
        # ── Script/cursive text on top of card ──
        "script_text": {
            "type": "text",
            "text": "2-Ingredient",
            "text_prompt": "Generate content for script_text for recipe {{title}}. You are writing an elegant script-style descriptor displayed above the main title on a Pinterest food pin. Format: 1-3 words, title case, cursive style, max 18 characters (e.g. '2-Ingredient', 'One-Pot', 'No-Bake', 'Grandma's'). This describes a key qualifier or attribute. Output ONLY the replacement text for script_text, no quotes. Given the user's recipe title {{title}}, return only the script_text text.",
            "position": {"top": 552, "left": 88},
            "width": 560,
            "height": 52,
            "font_family": "Dancing Script, cursive",
            "font_size": 36,
            "font_weight": "700",
            "color": "#1A1A1A",
            "text_align": "center",
            "z_index": 20,
        },
        # ── Large bold serif title ──
        "title": {
            "type": "text",
            "text": "Cheesecake",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main large TITLE for a Pinterest food pin. Format: 1-2 words, title case, bold serif style, max 14 characters (e.g. 'Cheesecake', 'Brownies', 'Pasta Bake'). This is the dish name. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 604, "left": 88},
            "width": 560,
            "height": 90,
            "font_family": "Playfair Display, Georgia, serif",
            "font_size": 64,
            "font_weight": "900",
            "color": "#B85C20",
            "text_align": "center",
            "line_height": 1.1,
            "z_index": 20,
        },
        # ── Small uppercase subtitle ──
        "subtitle": {
            "type": "text",
            "text": "EASY & HIGH PROTEIN RECIPE",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE below the title on a Pinterest food pin. Format: 3-6 words, all uppercase, max 30 characters (e.g. 'EASY & HIGH PROTEIN RECIPE', 'QUICK 30 MINUTE DINNER', 'FAMILY FAVORITE DESSERT'). Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 710, "left": 88},
            "width": 560,
            "height": 36,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 14,
            "font_weight": "500",
            "color": "#1A1A1A",
            "text_align": "center",
            "letter_spacing": "3px",
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
    "background": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/28c59a81/f78e79c055d.png",
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
