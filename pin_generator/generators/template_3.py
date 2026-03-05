#!/usr/bin/env python3
"""Template 3: Background + avatar + overlay box + title + stars + website."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_3"

STYLE_SLOTS = {
    "overlay_box": {"background_color": "primary"},
    "title": {"color": "on_primary"},
    "stars": {"color": "secondary"},
    "website": {"color": "on_dark", "background_color": "text_primary"},
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Salted Caramel Cheesecake Cookies",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' in your output; the domain is provided separately.",
    "field_prompts": {
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3–8 words (e.g. 'Salted Caramel Cheesecake Cookies'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
    },
    "images": {
        "background": {"description_prompt": "Salted caramel cheesecake cookies, food photography", "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": 1},
        "avatar": {"description_prompt": "Food blogger portrait, circular", "position": {"top": 380, "left": 240}, "width": 120, "height": 120, "border_radius": "50%", "border": "4px solid white", "layer_order": 30},
    },
    "elements": {
        "overlay_box": {"type": "div", "position": {"top": 440, "left": 20}, "width": 560, "height": 200, "background_color": "#1A1A1A", "border_radius": 15, "z_index": 10},
        "title": {
            "type": "text",
            "text": "Your Recipe Title Here",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3–8 words (e.g. 'Salted Caramel Cheesecake Cookies'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 480, "left": 40}, "width": 520, "height": 100, "font_family": "Georgia, serif", "font_size": 38, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "line_height": 1.2, "z_index": 20,
        },
        "stars": {"type": "stars", "count": 5, "position": {"top": 590, "left": 200}, "star_size": 28, "color": "#FFD700", "z_index": 20},
        "website": {
            "type": "text",
            "text": "yourdomain.com",
            "position": {"top": 980, "left": 150}, "width": 300, "height": 40, "font_family": "Arial, sans-serif", "font_size": 18, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "background_color": "#1A1A1A", "border_radius": 20, "padding": "10px 20px", "z_index": 20,
        },
    },
    "background": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/midjourney_splits/main/476/25bfa9d3f71.png",
    "avatar": "https://static.vecteezy.com/system/resources/previews/024/183/525/non_2x/avatar-of-a-man-portrait-of-a-young-guy-illustration-of-male-character-in-modern-color-style-vector.jpg",
}


def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
