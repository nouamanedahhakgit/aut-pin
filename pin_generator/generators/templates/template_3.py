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
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t3.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3–8 words (e.g. 'Salted Caramel Cheesecake Cookies'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
    },
    "images": {
        "background": {"description_prompt": "Salted caramel cheesecake cookies, food photography", "position": {"top": 0, "left": 0}, "width": 736, "height": 1308, "layer_order": 1},
        "avatar": {"description_prompt": "Food blogger portrait, circular", "position": {"top": 466, "left": 294}, "width": 147, "height": 147, "border_radius": "50%", "border": "5px solid white", "layer_order": 30},
    },
    "elements": {
        "overlay_box": {"type": "div", "position": {"top": 539, "left": 25}, "width": 687, "height": 245, "background_color": "#1A1A1A", "border_radius": 18, "z_index": 10},
        "title": {
            "type": "text",
            "text": "Your Recipe Title Here",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3–8 words (e.g. 'Salted Caramel Cheesecake Cookies'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 588, "left": 49}, "width": 638, "height": 123, "font_family": "Georgia, serif", "font_size": 47, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "line_height": 1.2, "z_index": 20,
        },
        "stars": {"type": "stars", "count": 5, "position": {"top": 723, "left": 245}, "star_size": 34, "color": "#FFD700", "z_index": 20},
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1201, "left": 184}, "width": 368, "height": 49, "font_family": "Arial, sans-serif", "font_size": 22, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "background_color": "#1A1A1A", "border_radius": 25, "padding": "12px 25px", "z_index": 20,
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
