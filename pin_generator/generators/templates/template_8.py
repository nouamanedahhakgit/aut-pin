#!/usr/bin/env python3
"""Template 8: Full background + light parchment card overlay + decorative badge + serif title."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_8"

# Theme: Warm Organic Kitchen
STYLE_SLOTS = {
    "overlay": {"background_color": "background"},
    "title": {"color": "text_primary"},
    "subtitle": {"color": "primary"},
    "badge": {"background_color": "secondary"},
    "stars": {"color": "secondary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "subtitle": "body",
    "badge": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Organic Earthy Recipe Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/b5c216ae305.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate a short promotional tag for {{title}} (e.g., 'FRESH', 'EASY'). 1 word, ALL CAPS.",
        "title": "Main title for {{title}}. 3–6 words, mixed case (Title Case).",
        "subtitle": "A warm, descriptive subtitle for {{title}}. 6–10 words, describing the texture, flavor, or vibe."
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "description_prompt": "Warm, beautifully lit food photography of {{title}} on a rustic wooden table with fresh ingredients around. Earthy tones, high quality.",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": 1
        }
    },
    "elements": {
        "overlay": {
            "type": "div",
            "position": {"top": 580, "left": 40}, "width": 520, "height": 340,
            "background_color": "#FCF8F3", "border_radius": 15, "opacity": 0.95,
            "box_shadow": "0 10px 30px rgba(0,0,0,0.15)", "z_index": 5
        },
        "badge": {
            "type": "text",
            "text": "FRESH",
            "position": {"top": 555, "left": 230}, "width": 140, "height": 50,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "900",
            "color": "#FFFFFF", "background_color": "#D27D56", "text_align": "center",
            "text_transform": "uppercase", "letter_spacing": 2, "border_radius": 25, "z_index": 15
        },
        "title": {
            "type": "text",
            "text": "Creamy Tuscan Chicken Pasta",
            "position": {"top": 620, "left": 70}, "width": 460, "height": 160,
            "font_family": "'Playfair Display', serif", "font_size": 44, "font_weight": "900",
            "color": "#4A3728", "text_align": "center", "line_height": 1.1, "z_index": 10
        },
        "stars": {"type": "stars", "count": 5, "position": {"top": 785, "left": 200}, "star_size": 28, "color": "#D27D56", "z_index": 10},
        "subtitle": {
            "type": "text",
            "text": "Rich, velvety sauce with sun-dried tomatoes and fresh spinach leaves",
            "position": {"top": 825, "left": 70}, "width": 460, "height": 90,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "400",
            "color": "#7D6B5D", "text_align": "center", "line_height": 1.2, "z_index": 10
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "text_transform": "uppercase",
            "text_shadow": "0 2px 4px rgba(0,0,0,0.5)", "z_index": 10
        }
    },
    "background": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png"
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
