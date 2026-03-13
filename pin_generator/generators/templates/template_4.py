#!/usr/bin/env python3
"""Template 4: Top + bottom images + text band + subtitle + title + time badge."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_4"

STYLE_SLOTS = {
    "text_band": {"background_color": "primary"},
    "subtitle": {"color": "on_primary"},
    "title": {"color": "on_primary"},
    "time_badge": {"color": "on_primary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "subtitle": "heading",
    "title": "heading",
    "time_badge": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Chopped Chicken Bacon Ranch Sandwich",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t4.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing the SUBTITLE for a Pinterest food pin. Format: one short cursive-style tagline, 2–4 words only (e.g. 'Easy Homemade', 'Quick & Tasty'). Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the TITLE for a Pinterest food pin. Format: exactly 2 lines, ALL CAPS, with <br> between lines. Each line 2–4 words. Output ONLY the replacement text for title including <br> (e.g. 'STREET CORN<br>CHICKEN BOWL'). Given the user's recipe title {{title}}, return only the title text with <br>.",
        "time_badge": "Generate content for time_badge for recipe {{title}}. You are writing the TIME BADGE for a Pinterest food pin. Format: one short phrase for prep/cook time, lowercase, 3–6 words (e.g. 'in 10 minutes', 'ready in 20 min'). Output ONLY the replacement text for time_badge, no quotes. Given the user's recipe title {{title}}, return only the time phrase.",
    },
    "images": {
        "top_image": {"description_prompt": "Chicken bacon ranch sandwich, food photography", "position": {"top": 0, "left": 0}, "width": 736, "height": 490, "layer_order": 1},
        "bottom_image": {"description_prompt": "Cross-section chicken bacon ranch sandwich", "position": {"top": 736, "left": 0}, "width": 736, "height": 572, "layer_order": 1},
    },
    "elements": {
        "text_band": {"type": "div", "position": {"top": 490, "left": 0}, "width": 736, "height": 245, "background_color": "#6D4C41", "z_index": 5},
        "subtitle": {
            "type": "text",
            "text": "Easy Homemade",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing the SUBTITLE for a Pinterest food pin. Format: one short cursive-style tagline, 2–4 words only (e.g. 'Easy Homemade', 'Quick & Tasty'). Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 509, "left": 0}, "width": 736, "height": 74, "font_family": "'Dancing Script', cursive", "font_size": 64, "font_weight": "700", "color": "#FFFFFF", "text_align": "center", "text_shadow": "2px 2px 5px rgba(0,0,0,0.3)", "z_index": 10,
        },
        "title": {
            "type": "text",
            "text": "CHICKEN<br>SANDWICH",
            "position": {"top": 582, "left": 25}, "width": 687, "height": 135, "font_family": "'Bebas Neue', sans-serif", "font_size": 51, "font_weight": "400", "color": "#FFFFFF", "text_align": "center", "line_height": 1.1, "text_shadow": "2px 2px 5px rgba(0,0,0,0.4)", "z_index": 10,
        },
        "time_badge": {
            "type": "text",
            "text": "in 10 minutes",
            "text_prompt": "Generate content for time_badge for recipe {{title}}. You are writing the TIME BADGE for a Pinterest food pin. Format: one short phrase for prep/cook time, lowercase, 3–6 words (e.g. 'in 10 minutes', 'ready in 20 min'). Output ONLY the replacement text for time_badge, no quotes. Given the user's recipe title {{title}}, return only the time phrase.",
            "position": {"top": 693, "left": 245}, "width": 245, "height": 37, "font_family": "Arial, sans-serif", "font_size": 22, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "text_shadow": "1px 1px 2px rgba(0,0,0,0.3)", "z_index": 10,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1226, "left": 0}, "width": 736, "height": 49, "font_family": "Arial, sans-serif", "font_size": 22, "font_weight": "bold", "color": "#FFFFFF", "text_align": "center", "text_shadow": "0 0 12px rgba(0,0,0,0.5)", "z_index": 20,
        },
    },
    "top_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/midjourney_splits/main/476/25bfa9d3f71.png",
    "bottom_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/midjourney_splits/main/476/ccbfc53a614.png",
}


def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
