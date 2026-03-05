#!/usr/bin/env python3
"""Template 1: Frosted Glass Card — Full background with floating glass overlay card."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_6"

STYLE_SLOTS = {
    "card_overlay": {"background_color": "primary"},
    "badge": {"background_color": "secondary", "color": "on_secondary"},
    "title": {"color": "on_primary"},
    "subtitle": {"color": "secondary"},
    "stars": {"color": "secondary"},
    "divider": {"background_color": "secondary"},
    "website": {"color": "on_dark", "background_color": "text_primary"},
}

FONT_SLOTS = {
    "title": "heading",
    "subtitle": "heading",
    "badge": "body",
    "website": "body",
}

TEMPLATE_DATA = {
    "name": "Frosted Glass Card",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. The style should be elegant and editorial, suitable for a premium food pin on Pinterest.",
    "field_prompts": {
        "title": "Generate content for title for recipe {{title}}. You are writing the title for a Pinterest food pin. Format: title case, 3-6 words, compelling and appetizing. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "subtitle": "Generate content for subtitle for recipe {{title}}. You are writing the subtitle tagline for a Pinterest food pin. Format: 2-4 words, lowercase cursive style, evocative and sensory. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
        "badge": "Generate content for badge for recipe {{title}}. You are writing a small badge label for a Pinterest food pin. Format: 2-3 words, ALL CAPS (e.g. 'TOP RECIPE', 'MUST TRY', 'BEST EVER'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
    },
    "images": {
        "background": {
            "description_prompt": "Close-up overhead food photography, beautifully plated dish, soft natural lighting, shallow depth of field, warm tones, editorial food magazine style",
            "position": {"top": 0, "left": 0},
            "width": 600,
            "height": 1067,
            "layer_order": 1,
        },
    },
    "elements": {
        # ── Dark gradient overlay at bottom ──
        "gradient_overlay": {
            "type": "div",
            "position": {"top": 400, "left": 0},
            "width": 600,
            "height": 667,
            "background_color": "linear-gradient(to bottom, rgba(0,0,0,0), rgba(30,15,20,0.85) 60%)",
            "z_index": 3,
        },
        # ── Floating card ──
        "card_overlay": {
            "type": "div",
            "position": {"top": 590, "left": 40},
            "width": 520,
            "height": 400,
            "background_color": "rgba(60, 20, 30, 0.75)",
            "border_radius": 24,
            "border": "1px solid rgba(255,255,255,0.12)",
            "z_index": 8,
            "opacity": 0.95,
        },
        # ── Badge pill ──
        "badge": {
            "type": "text",
            "text": "MUST TRY",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing a small badge label for a Pinterest food pin. Format: 2-3 words, ALL CAPS (e.g. 'TOP RECIPE', 'MUST TRY', 'BEST EVER'). Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 610, "left": 195},
            "width": 210,
            "height": 36,
            "font_family": "Arial, sans-serif",
            "font_size": 13,
            "font_weight": "bold",
            "color": "#FFFFFF",
            "text_align": "center",
            "text_transform": "uppercase",
            "letter_spacing": 3,
            "line_height": 1.0,
            "background_color": "#C4933F",
            "border_radius": 20,
            "padding": "8px 20px",
            "z_index": 20,
        },
        # ── Divider line ──
        "divider": {
            "type": "div",
            "position": {"top": 670, "left": 240},
            "width": 120,
            "height": 3,
            "background_color": "#C4933F",
            "border_radius": 2,
            "z_index": 20,
        },
        # ── Title ──
        "title": {
            "type": "text",
            "text": "Honey Glazed Salmon",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the title for a Pinterest food pin. Format: title case, 3-6 words, compelling and appetizing. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 695, "left": 70},
            "width": 460,
            "height": 120,
            "font_family": "Georgia, serif",
            "font_size": 42,
            "font_weight": "bold",
            "color": "#FFFFFF",
            "text_align": "center",
            "line_height": 1.2,
            "z_index": 20,
        },
        # ── Stars ──
        "stars": {
            "type": "stars",
            "count": 5,
            "position": {"top": 830, "left": 222},
            "star_size": 26,
            "color": "#C4933F",
            "z_index": 20,
        },
        # ── Subtitle ──
        "subtitle": {
            "type": "text",
            "text": "simply irresistible",
            "text_prompt": "Generate content for subtitle for recipe {{title}}. You are writing the subtitle tagline for a Pinterest food pin. Format: 2-4 words, lowercase cursive style, evocative and sensory. Output ONLY the replacement text for subtitle, no quotes. Given the user's recipe title {{title}}, return only the subtitle text.",
            "position": {"top": 870, "left": 130},
            "width": 340,
            "height": 50,
            "font_family": "'Georgia', serif",
            "font_size": 24,
            "font_weight": "normal",
            "font_style": "italic",
            "color": "#C4933F",
            "text_align": "center",
            "line_height": 1.3,
            "z_index": 20,
        },
        # ── Bottom accent line ──
        "bottom_accent": {
            "type": "div",
            "position": {"top": 940, "left": 200},
            "width": 200,
            "height": 2,
            "background_color": "rgba(196, 147, 63, 0.4)",
            "z_index": 20,
        },
        # ── Website pill ──
        "website": {
            "type": "text",
            "text": "yourdomain.com",
            "position": {"top": 960, "left": 175},
            "width": 250,
            "height": 38,
            "font_family": "Arial, sans-serif",
            "font_size": 14,
            "font_weight": "bold",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": 2,
            "text_transform": "uppercase",
            "background_color": "rgba(30, 15, 20, 0.7)",
            "border_radius": 20,
            "border": "1px solid rgba(196, 147, 63, 0.5)",
            "padding": "8px 20px",
            "z_index": 25,
        },
    },
    # Default test image (replaced at runtime):
    "background": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=600&h=1067&fit=crop",
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
