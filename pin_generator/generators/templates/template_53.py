#!/usr/bin/env python3
"""Template 53: Editorial Stripe — full background, bold vertical accent bar, magazine-style typography.
Distinct layout: left-edge stripe + bottom overlay panel, clean editorial feel."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_53"

STYLE_SLOTS = {
    "accent_stripe": {"background_color": "primary"},
    "overlay_panel": {"background_color": "primary"},
    "badge": {"color": "on_primary"},
    "title": {"color": "on_primary"},
    "website": {"color": "text_secondary"},
}

FONT_SLOTS = {
    "badge": "body",
    "title": "heading",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Editorial Stripe Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t53.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2–3 words, title case, max 18 characters, and it must fit this exact recipe (e.g. 'Quick & Easy', 'Best Ever'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3–8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, editorial style, bright natural light",
        },
    },
    "elements": {
        "accent_stripe": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 16,
            "height": 1308,
            "background_color": "#E85D04",
            "z_index": 12,
        },
        "overlay_panel": {
            "type": "div",
            "position": {"top": 880, "left": 0},
            "width": 736,
            "height": 428,
            "background_color": "#1A1A1A",
            "z_index": 10,
            "box_shadow": "0 -8px 32px rgba(0,0,0,0.35)",
        },
        "badge": {
            "type": "text",
            "text": "Quick & Easy",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2–3 words, title case, max 18 characters, and it must fit this exact recipe (e.g. 'Quick & Easy', 'Best Ever'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 920, "left": 48},
            "width": 640,
            "height": 32,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 14,
            "font_weight": "700",
            "color": "#FBBF24",
            "text_align": "left",
            "letter_spacing": "3px",
            "text_transform": "uppercase",
            "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "{{title}}",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: use the same recipe title {{title}} (or a very close short variant), title case, 3–8 words, max 42 characters. Do not change to a different dish. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 958, "left": 48},
            "width": 640,
            "height": 120,
            "font_family": "Playfair Display, Georgia, serif",
            "font_size": 48,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "left",
            "line_height": 1.12,
            "text_shadow": "0 2px 8px rgba(0,0,0,0.4)",
            "z_index": 20,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1258, "left": 0},
            "width": 736,
            "height": 40,
            "font_family": "Lato, Arial, sans-serif",
            "font_size": 18,
            "font_weight": "600",
            "color": "#9CA3AF",
            "text_align": "center",
            "letter_spacing": "0.5px",
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
