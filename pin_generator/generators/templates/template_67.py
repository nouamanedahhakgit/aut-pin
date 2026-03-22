"""
Template 54: Split Image with Elegant Typography Panel
A sophisticated split layout with two image sections sandwiching a central
typography panel featuring mixed script and serif fonts.
"""

from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_54"

STYLE_SLOTS = {
    "center_panel": {"background_color": "surface"},
    "number_prefix": {"color": "on_dark"},
    "script_text": {"color": "on_dark"},
    "title_text": {"color": "primary"},
    "subtitle_text": {"color": "on_dark"},
    "bottom_bar": {"background_color": "secondary"},
    "website_text": {"color": "on_primary"},
    "accent_line": {"background_color": "accent"}
}

FONT_SLOTS = {
    "number_prefix": "heading",
    "script_text": "script",
    "title_text": "heading",
    "subtitle_text": "body",
    "website_text": "body"
}

TEMPLATE_DATA = {
    "name": "Split Image with Elegant Typography Panel",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t54.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},

    "top_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
    "bottom_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",

    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",

    "field_prompts": {
        "number_prefix": "Generate content for number_prefix for recipe {{title}}. You are writing the NUMBER prefix for a Pinterest food pin emphasizing simplicity. Format: Number followed by hyphen (e.g. '2-', '3-', '5-'). Output ONLY the replacement text for number_prefix, no quotes. Given the user's recipe title {{title}}, return only the number_prefix text.",
        "script_word": "Generate content for script_word for recipe {{title}}. You are writing the DESCRIPTOR in script font for a Pinterest food pin. Format: 1-2 words describing the recipe type, title case (e.g. 'Ingredient', 'Step', 'Minute'). Max 12 characters. Output ONLY the replacement text for script_word, no quotes. Given the user's recipe title {{title}}, return only the script_word text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: 1-2 words, title case, large serif display (e.g. 'Cheesecake', 'Brownies', 'Pasta'). Max 15 characters. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing the SUBTITLE for a Pinterest food pin. Format: uppercase descriptor, 4-6 words with ampersand (e.g. 'EASY & HIGH PROTEIN RECIPE', 'QUICK & HEALTHY MEAL'). Max 35 characters. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text."
    },

    "images": {
        "top_image": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 580,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Close-up food photography, bright lighting, detail shot"
        },
        "bottom_image": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 728, "left": 0},
            "width": 736,
            "height": 580,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Hero food photography, serving suggestion, appetizing presentation"
        }
    },

    "elements": {
        "center_panel": {
            "type": "div",
            "position": {"top": 540, "left": 28},
            "width": 680,
            "height": 228,
            "background_color": "#FFFFFF",
            "box_shadow": "0 8px 32px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08)",
            "z_index": 5
        },

        "number_prefix": {
            "type": "text",
            "text_prompt": "Generate content for number_prefix for recipe {{title}}. You are writing the NUMBER prefix for a Pinterest food pin emphasizing simplicity. Format: Number followed by hyphen (e.g. '2-', '3-', '5-'). Output ONLY the replacement text for number_prefix, no quotes. Given the user's recipe title {{title}}, return only the number_prefix text.",
            "position": {"top": 560, "left": 140},
            "width": 80,
            "height": 80,
            "font_family": "Playfair Display",
            "font_size": 72,
            "font_weight": 700,
            "color": "#1A1A1A",
            "text_align": "right",
            "z_index": 6
        },

        "script_text": {
            "type": "text",
            "text_prompt": "Generate content for script_word for recipe {{title}}. You are writing the DESCRIPTOR in script font for a Pinterest food pin. Format: 1-2 words describing the recipe type, title case (e.g. 'Ingredient', 'Step', 'Minute'). Max 12 characters. Output ONLY the replacement text for script_word, no quotes. Given the user's recipe title {{title}}, return only the script_word text.",
            "position": {"top": 575, "left": 220},
            "width": 300,
            "height": 60,
            "font_family": "Dancing Script",
            "font_size": 56,
            "font_weight": 700,
            "color": "#1A1A1A",
            "text_align": "left",
            "z_index": 6
        },

        "title_text": {
            "type": "text",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: 1-2 words, title case, large serif display (e.g. 'Cheesecake', 'Brownies', 'Pasta'). Max 15 characters. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 630, "left": 48},
            "width": 640,
            "height": 90,
            "font_family": "Playfair Display",
            "font_size": 78,
            "font_weight": 900,
            "color": "#D4854F",
            "text_align": "center",
            "line_height": 1.0,
            "z_index": 6
        },

        "subtitle_text": {
            "type": "text",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing the SUBTITLE for a Pinterest food pin. Format: uppercase descriptor, 4-6 words with ampersand (e.g. 'EASY & HIGH PROTEIN RECIPE', 'QUICK & HEALTHY MEAL'). Max 35 characters. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 720, "left": 48},
            "width": 640,
            "height": 40,
            "font_family": "Montserrat",
            "font_size": 20,
            "font_weight": 600,
            "color": "#1A1A1A",
            "text_align": "center",
            "letter_spacing": 3,
            "z_index": 6
        },

        "accent_line_left": {
            "type": "div",
            "position": {"top": 655, "left": 48},
            "width": 80,
            "height": 3,
            "background_color": "#D4854F",
            "z_index": 6
        },

        "accent_line_right": {
            "type": "div",
            "position": {"top": 655, "left": 608},
            "width": 80,
            "height": 3,
            "background_color": "#D4854F",
            "z_index": 6
        },

        "bottom_bar": {
            "type": "div",
            "position": {"top": 1238, "left": 0},
            "width": 736,
            "height": 70,
            "background_color": "#1A1A1A",
            "z_index": 7
        },

        "website_text": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1253, "left": 0},
            "width": 736,
            "height": 40,
            "font_family": "Montserrat",
            "font_size": 18,
            "font_weight": 600,
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": 3,
            "text_transform": "uppercase",
            "z_index": 8
        },

        "decorative_circle_1": {
            "type": "div",
            "position": {"top": 850, "left": 650},
            "width": 60,
            "height": 60,
            "background_color": "rgba(212, 133, 79, 0.2)",
            "border_radius": "50%",
            "z_index": 4
        },

        "decorative_circle_2": {
            "type": "div",
            "position": {"top": 400, "left": 30},
            "width": 40,
            "height": 40,
            "background_color": "rgba(212, 133, 79, 0.15)",
            "border_radius": "50%",
            "z_index": 4
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
