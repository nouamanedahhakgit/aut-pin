#!/usr/bin/env python3
"""Template 50: Creative Hook — full background, gradient overlay, bold hook line + title + stars.
Designed for high-engagement pins with an attention-grabbing hook above the recipe title."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_50"

STYLE_SLOTS = {
    "overlay_gradient": {"background_color": "primary"},
    "hook_text": {"color": "secondary"},
    "title": {"color": "on_primary"},
    "stars": {"color": "secondary"},
    "website": {"color": "on_dark"},
}

FONT_SLOTS = {
    "hook_text": "script",
    "title": "heading",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Creative Hook Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t50.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "hook_text": "Generate content for hook_text for recipe {{title}}. You are writing a short HOOK or attention-grabbing phrase for a Pinterest food pin. Format: 4-8 words that create curiosity or urgency (e.g. 'Everyone Asks Me for This Recipe', 'The Recipe That Broke the Internet', 'So Good It Went Viral', 'Ready in 15 Minutes', 'The Only Recipe You Need'). Output ONLY the replacement text for hook_text, no quotes. Given the user's recipe title {{title}}, return only the hook text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3-8 words (e.g. 'Million Dollar Chicken Salad'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 1308,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Stunning food photography, overhead shot, appetizing, bright natural light",
        },
    },
    "elements": {
        "overlay_gradient": {
            "type": "div",
            "position": {"top": 480, "left": 0},
            "width": 736,
            "height": 420,
            "background_color": "#1A1A1A",
            "z_index": 10,
        },
        "hook_text": {
            "type": "text",
            "text": "Everyone Asks Me for This Recipe",
            "text_prompt": "Generate content for hook_text for recipe {{title}}. You are writing a short HOOK or attention-grabbing phrase for a Pinterest food pin. Format: 4-8 words that create curiosity or urgency (e.g. 'Everyone Asks Me for This Recipe', 'The Recipe That Broke the Internet', 'So Good It Went Viral', 'Ready in 15 Minutes', 'The Only Recipe You Need'). Output ONLY the replacement text for hook_text, no quotes. Given the user's recipe title {{title}}, return only the hook text.",
            "position": {"top": 520, "left": 40},
            "width": 656,
            "height": 70,
            "font_family": "Dancing Script, Pacifico, cursive",
            "font_size": 38,
            "font_weight": "700",
            "color": "#FBBF24",
            "text_align": "center",
            "line_height": 1.2,
            "z_index": 20,
        },
        "title": {
            "type": "text",
            "text": "Your Recipe Title Here",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: one short recipe title, title case, 3-8 words (e.g. 'Million Dollar Chicken Salad'). Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 595, "left": 40},
            "width": 656,
            "height": 120,
            "font_family": "Playfair Display, Georgia, serif",
            "font_size": 52,
            "font_weight": "900",
            "color": "#FFFFFF",
            "text_align": "center",
            "line_height": 1.1,
            "text_shadow": "0 2px 8px rgba(0,0,0,0.5)",
            "z_index": 20,
        },
        "stars": {
            "type": "stars",
            "count": 5,
            "position": {"top": 730, "left": 268},
            "star_size": 32,
            "color": "#FBBF24",
            "z_index": 20,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1240, "left": 0},
            "width": 736,
            "height": 48,
            "font_family": "Arial, sans-serif",
            "font_size": 20,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "center",
            "text_shadow": "0 0 10px rgba(0,0,0,0.6)",
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
