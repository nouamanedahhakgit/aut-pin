#!/usr/bin/env python3
"""Template 54: Glass Card -- Stitch-designed Pinterest food pin.
Full-bleed food photo with subtle dark overlay. Centered frosted glass card with
warm cream tint, soft blur shadow, and thin terracotta inner border. Mixed typography:
Montserrat uppercase badge + Playfair Display bold title + italic subtitle.
Thin terracotta accent lines frame the card content. Domain at bottom with drop shadow."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_54"

STYLE_SLOTS = {
    "card_bg": {"background_color": "surface"},
    "card_inner_border": {"border": "border_accent"},
    "accent_line_top": {"background_color": "primary"},
    "accent_line_bottom": {"background_color": "primary"},
    "badge": {"color": "primary"},
    "title": {"color": "text_primary"},
    "subtitle": {"color": "text_secondary"},
    "stars": {"color": "secondary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "badge": "accent",
    "title": "heading",
    "subtitle": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Glass Card Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t54.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'BEST EVER', 'MUST TRY', 'FAMILY FAVORITE'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words describing a key benefit or feature, lowercase italic style (e.g. 'ready in 30 minutes', 'one pan wonder', 'so easy and delicious'). Max 30 characters. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, close-up, bright natural light",
        },
    },
    "elements": {
        # Subtle dark overlay on the full image for better card contrast
        "dim_overlay": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "background_color": "rgba(0,0,0,0.10)",
            "z_index": 5,
        },
        # Glass card background -- warm cream with semi-transparency
        "card_bg": {
            "type": "div",
            "position": {"top": 390, "left": 80},
            "width": 576,
            "height": 500,
            "background_color": "rgba(255,252,248,0.92)",
            "border_radius": "2px",
            "border": "1px solid rgba(255,255,255,0.5)",
            "box_shadow": "0 10px 30px rgba(0,0,0,0.15)",
            "z_index": 10,
        },
        # Inner border with subtle terracotta tint
        "card_inner_border": {
            "type": "div",
            "position": {"top": 404, "left": 94},
            "width": 548,
            "height": 472,
            "background_color": "transparent",
            "border": "1px solid rgba(184,92,56,0.10)",
            "border_radius": "1px",
            "z_index": 11,
        },
        # Top accent line -- thin terracotta
        "accent_line_top": {
            "type": "div",
            "position": {"top": 440, "left": 344},
            "width": 48,
            "height": 2,
            "background_color": "#B85C38",
            "z_index": 20,
        },
        # Badge -- small uppercase Montserrat label
        "badge": {
            "type": "text",
            "text": "BEST EVER",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'BEST EVER', 'MUST TRY', 'FAMILY FAVORITE'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 462, "left": 130},
            "width": 476,
            "height": 24,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 11,
            "font_weight": "600",
            "color": "#B85C38",
            "text_align": "center",
            "letter_spacing": "4px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        # Stars row -- gold
        "stars": {
            "type": "stars",
            "count": 5,
            "position": {"top": 502, "left": 304},
            "star_size": 20,
            "color": "#EAB308",
            "z_index": 20,
        },
        # Title -- Playfair Display, large bold serif, dark gray
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3-8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 545, "left": 130},
            "width": 476,
            "height": 200,
            "font_family": "Playfair Display, Georgia, serif",
            "font_size": 48,
            "font_weight": "900",
            "color": "#1F2937",
            "text_align": "center",
            "line_height": 1.18,
            "z_index": 20,
        },
        # Subtitle -- italic Montserrat, gray
        "subtitle": {
            "type": "text",
            "text": "ready in 30 minutes",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing a short SUBTITLE for a Pinterest food pin. Format: 3-6 words describing a key benefit or feature, lowercase italic style (e.g. 'ready in 30 minutes', 'one pan wonder', 'so easy and delicious'). Max 30 characters. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 778, "left": 130},
            "width": 476,
            "height": 28,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 14,
            "font_weight": "400",
            "color": "#6B7280",
            "text_align": "center",
            "letter_spacing": "0.5px",
            "z_index": 20,
        },
        # Bottom accent line -- thin terracotta
        "accent_line_bottom": {
            "type": "div",
            "position": {"top": 834, "left": 344},
            "width": 48,
            "height": 2,
            "background_color": "#B85C38",
            "z_index": 20,
        },
        # Website at the bottom on the food image
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1240, "left": 0},
            "width": 736,
            "height": 36,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 12,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "3px",
            "text_transform": "uppercase",
            "text_shadow": "0 1px 4px rgba(0,0,0,0.5)",
            "z_index": 20,
        },
    },
    "background": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
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
