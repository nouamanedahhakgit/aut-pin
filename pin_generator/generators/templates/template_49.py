#!/usr/bin/env python3
"""Template 49: Listicle Header + Image Grid — top hero image, overlay band with number circle + subtitle + title, two bottom images, footer."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_49"

STYLE_SLOTS = {
    "overlay_band":      {"background_color": "primary"},
    "number_circle":     {"border": "border_accent", "color": "on_primary"},
    "number_text":       {"color": "on_primary"},
    "subtitle_text":     {"color": "on_primary"},
    "main_title_line1":  {"color": "on_primary"},
    "main_title_line2":  {"color": "on_primary"},
    "footer_bar":        {"background_color": "surface"},
    "website":           {"color": "text_primary"},
}

FONT_SLOTS = {
    "number_text":      "display",
    "subtitle_text":    "script",
    "main_title_line1": "heading",
    "main_title_line2": "heading",
    "website":          "body",
}

TEMPLATE_DATA = {
    "name": "Listicle Header Grid",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t49.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "number_text": "Generate content for number_text for recipe {{title}}. You are writing the LISTICLE COUNT for a Pinterest food pin (e.g. 20, 25, 30, 50). Output ONLY the number, no quotes. Given the user's recipe title {{title}}, return only the number.",
        "subtitle_text": "Generate content for subtitle_text for recipe {{title}}. You are writing a short SCRIPT SUBTITLE for a Pinterest food pin. Format: 2–4 words, title case (e.g. 'Super Simple', 'Quick & Easy'). Output ONLY the replacement text for subtitle_text, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
        "main_title_line1": "Generate content for main_title_line1 for recipe {{title}}. You are writing the FIRST LINE of a two-line category title for a Pinterest food pin. Format: 1–3 words, ALL CAPS. Output ONLY the replacement text for main_title_line1, no quotes. Given the user's recipe title {{title}}, return only those words.",
        "main_title_line2": "Generate content for main_title_line2 for recipe {{title}}. You are writing the SECOND LINE of a two-line category title for a Pinterest food pin. Format: 1–2 words, ALL CAPS (e.g. 'RECIPES', 'DINNERS'). Output ONLY the replacement text for main_title_line2, no quotes. Given the user's recipe title {{title}}, return only that word.",
    },
    "images": {
        # Top hero image (full width, upper ~37% of canvas)
        "top_image": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 490,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Overhead hero shot of the finished recipe dish, bright natural light",
        },
        # Bottom-left grid image
        "bottom_left": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 718, "left": 0},
            "width": 368,
            "height": 548,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Close-up of recipe variation or ingredient, appetizing food photography",
        },
        # Bottom-right grid image
        "bottom_right": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 718, "left": 368},
            "width": 368,
            "height": 548,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Plated serving of the recipe with garnish, warm food styling",
        },
    },

    # ------------------------------------------------------------------ #
    # ELEMENTS
    # ------------------------------------------------------------------ #
    "elements": {

        # --- Diagonal teal overlay band ---
        "overlay_band": {
            "type": "div",
            "position": {"top": 430, "left": 0},
            "width": 736,
            "height": 290,
            "background_color": "#1a5068",
            "z_index": 10,
            # Slight skew effect approximated by oversizing; renderer may clip
        },

        # --- White circle badge (number) ---
        "number_circle": {
            "type": "div",
            "position": {"top": 448, "left": 28},
            "width": 140,
            "height": 140,
            "background_color": "#ffffff",
            "border": "3px dashed #1a5068",
            "border_radius": "50%",
            "z_index": 20,
        },

        # --- Number inside circle ---
        "number_text": {
            "type": "text",
            "text": "50",
            "text_prompt": "Generate content for number_text for recipe {{title}}. You are writing the LISTICLE COUNT for a Pinterest food pin (e.g. 20, 25, 30, 50). Output ONLY the number, no quotes. Given the user's recipe title {{title}}, return only the number.",
            "position": {"top": 460, "left": 28},
            "width": 140,
            "height": 116,
            "font_family": "Arial Black, Impact, sans-serif",
            "font_size": 74,
            "font_weight": "900",
            "color": "#1a5068",
            "text_align": "center",
            "line_height": 1.0,
            "z_index": 21,
        },
        "subtitle_text": {
            "type": "text",
            "text": "Super Simple",
            "text_prompt": "Generate content for subtitle_text for recipe {{title}}. You are writing a short SCRIPT SUBTITLE for a Pinterest food pin. Format: 2–4 words, title case (e.g. 'Super Simple', 'Quick & Easy'). Output ONLY the replacement text for subtitle_text, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 444, "left": 175},
            "width": 540,
            "height": 70,
            "font_family": "Dancing Script, Pacifico, cursive",
            "font_size": 52,
            "font_weight": "700",
            "color": "#ffffff",
            "text_align": "left",
            "line_height": 1.1,
            "z_index": 20,
        },
        "main_title_line1": {
            "type": "text",
            "text": "GROUND BEEF",
            "text_prompt": "Generate content for main_title_line1 for recipe {{title}}. You are writing the FIRST LINE of a two-line category title for a Pinterest food pin. Format: 1–3 words, ALL CAPS. Output ONLY the replacement text for main_title_line1, no quotes. Given the user's recipe title {{title}}, return only those words.",
            "position": {"top": 512, "left": 20},
            "width": 696,
            "height": 100,
            "font_family": "Arial Black, Impact, sans-serif",
            "font_size": 88,
            "font_weight": "900",
            "color": "#ffffff",
            "text_align": "center",
            "line_height": 1.0,
            "letter_spacing": "1px",
            "z_index": 20,
        },
        "main_title_line2": {
            "type": "text",
            "text": "RECIPES",
            "text_prompt": "Generate content for main_title_line2 for recipe {{title}}. You are writing the SECOND LINE of a two-line category title for a Pinterest food pin. Format: 1–2 words, ALL CAPS (e.g. 'RECIPES', 'DINNERS'). Output ONLY the replacement text for main_title_line2, no quotes. Given the user's recipe title {{title}}, return only that word.",
            "position": {"top": 606, "left": 20},
            "width": 696,
            "height": 100,
            "font_family": "Arial Black, Impact, sans-serif",
            "font_size": 88,
            "font_weight": "900",
            "color": "#ffffff",
            "text_align": "center",
            "line_height": 1.0,
            "letter_spacing": "1px",
            "z_index": 20,
        },

        # --- Thin white divider between grid images ---
        "grid_divider": {
            "type": "div",
            "position": {"top": 718, "left": 364},
            "width": 4,
            "height": 548,
            "background_color": "#ffffff",
            "z_index": 5,
        },

        # --- Footer white bar ---
        "footer_bar": {
            "type": "div",
            "position": {"top": 1262, "left": 0},
            "width": 736,
            "height": 46,
            "background_color": "#ffffff",
            "z_index": 15,
        },

        # --- Domain / website ---
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1266, "left": 0},
            "width": 736,
            "height": 38,
            "font_family": "Arial, sans-serif",
            "font_size": 22,
            "font_weight": "400",
            "color": "#333333",
            "text_align": "center",
            "line_height": 1.2,
            "z_index": 20,
        },
    },
    "top_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
    "bottom_left": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
    "bottom_right": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
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