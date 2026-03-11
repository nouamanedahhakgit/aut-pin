#!/usr/bin/env python3
"""Template 15: The "Save This" Badge. Central focus on a large sticker/badge for high engagement."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_15"

STYLE_SLOTS = {
    "badge_bg": {"background_color": "secondary"},
    "badge_text": {"color": "on_secondary"},
    "title_box": {"background_color": "primary_glass"},
    "title": {"color": "on_primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "badge_text": "body",
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "The 'Save This' Badge",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/save_badge.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate a title and a FOMO badge for {{title}}.",
    "field_prompts": {
        "title": "Main title for {{title}}. Bold, 2-4 words.",
        "badge_text": "A CTA like 'SAVE THIS!', 'MUST TRY', 'TOP RATED'. 2 words max."
    },
    "images": {
        "hero": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": 1
        }
    },
    "elements": {
        "badge_bg": {
            "type": "div",
            "position": {"top": 80, "left": 80}, "width": 180, "height": 180,
            "background_color": "#FFCC00", "border_radius": 90, "z_index": 10,
            "box_shadow": "0 10px 20px rgba(0,0,0,0.3)", "transform": "rotate(-15deg)"
        },
        "badge_text": {
            "type": "text",
            "text": "SAVE<br>THIS!",
            "position": {"top": 120, "left": 80}, "width": 180, "height": 100,
            "font_family": "'Bebas Neue', sans-serif", "font_size": 40, "font_weight": "900",
            "color": "#000000", "text_align": "center", "line_height": 0.9, "z_index": 20, "transform": "rotate(-15deg)"
        },
        "title_box": {
            "type": "div",
            "position": {"top": 700, "left": 30}, "width": 540, "height": 200,
            "background_color": "rgba(255,255,255,0.9)", "border_radius": 15, "z_index": 5
        },
        "title": {
            "type": "text",
            "text": "THE ONLY COOKIE RECIPE YOU NEED",
            "position": {"top": 740, "left": 60}, "width": 480, "height": 120,
            "font_family": "'Inter', sans-serif", "font_size": 42, "font_weight": "900",
            "color": "#1A1A1A", "text_align": "center", "line_height": 1.1, "z_index": 20, "text_transform": "uppercase"
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1000, "left": 0}, "width": 600, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "text_transform": "uppercase", "text_shadow": "0 2px 4px rgba(0,0,0,0.5)", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
