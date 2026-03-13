#!/usr/bin/env python3
"""Template 1: Full background + dark overlay band + badge + stars + title."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_1"

STYLE_SLOTS = {
    "overlay_band": {"background_color": "primary"},
    "badge": {"color": "on_primary", "border": "border_accent"},
    "title": {"color": "on_primary"},
    "stars": {"color": "secondary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "badge": "body",
    "title": "heading",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Million Dollar Chicken Salad",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t1.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2–3 words, title case (e.g. 'Top Recipe', 'Best Ever'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3–8 words (e.g. 'Million Dollar Chicken Salad'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
    },
    "images": {
        "background": {"description_prompt": "Close-up overhead shot of creamy chicken salad, food photography", "position": {"top": 0, "left": 0}, "width": 736, "height": 1308, "layer_order": 1},
    },
    "elements": {
        "overlay_band": {"type": "div", "position": {"top": 515, "left": 0}, "width": 736, "height": 278, "background_color": "#1A1A1A", "z_index": 10},
        "badge": {
            "type": "text",
            "text": "Top Recipe",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2–3 words, title case (e.g. 'Top Recipe', 'Best Ever'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 533, "left": 184}, "width": 368, "height": 49, "font_family": "Georgia, serif", "font_size": 27, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "background": "transparent", "border": "2px solid #D4AF37", "border_radius": 25, "padding": "10px 25px", "z_index": 20,
        },
        "stars": {"type": "stars", "count": 5, "position": {"top": 601, "left": 276}, "star_size": 29, "color": "#FFD700", "z_index": 20},
        "title": {
            "type": "text",
            "text": "Your Recipe Title Here",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3–8 words (e.g. 'Million Dollar Chicken Salad'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 650, "left": 37}, "width": 662, "height": 98, "font_family": "Georgia, serif", "font_size": 44, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "line_height": 1.2, "z_index": 20,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1226, "left": 0}, "width": 736, "height": 49, "font_family": "Arial, sans-serif", "font_size": 22, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "text_shadow": "0 0 12px rgba(0,0,0,0.5)", "z_index": 20,
        },
    },
    "background": "https://californiagrown.org/wp-content/uploads/2024/12/CAG-Loaded-Baked-Potato-17.jpg",
}


def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
