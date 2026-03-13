#!/usr/bin/env python3
"""Template 12: Step-by-Step Storyteller. Main image + 3 side-step icons + large headline."""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_12"

STYLE_SLOTS = {
    "sidebar": {"background_color": "secondary"},
    "title_box": {"background_color": "primary"},
    "title": {"color": "on_primary"},
    "step_label": {"color": "secondary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "step_label": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Step-by-Step Storyteller",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/step_storyteller.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
    "prompt": "Generate text for a step-by-step recipe pin. Replace {{title}} with the recipe name.",
    "field_prompts": {
        "title": "Main title for {{title}}. 3–5 words, ALL CAPS.",
        "step_1": "Step 1: Prep phase.",
        "step_2": "Step 2: Cook phase.",
        "step_3": "Step 3: Serve phase."
    },
    "images": {
        "main_image": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 184}, "width": 552, "height": 1308, "layer_order": 1
        },
        "step1_img": {"src": "{{main_image}}", "position": {"top": 61, "left": 31}, "width": 123, "height": 123, "border_radius": 61, "z_index": 20},
        "step2_img": {"src": "{{main_image}}", "position": {"top": 245, "left": 31}, "width": 123, "height": 123, "border_radius": 61, "z_index": 20},
        "step3_img": {"src": "{{main_image}}", "position": {"top": 429, "left": 31}, "width": 123, "height": 123, "border_radius": 61, "z_index": 20}
    },
    "elements": {
        "sidebar": {
            "type": "div",
            "position": {"top": 0, "left": 0}, "width": 184, "height": 1308,
            "background_color": "#F3F3F3", "z_index": 10
        },
        "title_box": {
            "type": "div",
            "position": {"top": 736, "left": 184}, "width": 552, "height": 306,
            "background_color": "#E1306C", "z_index": 15, "opacity": 0.9
        },
        "title": {
            "type": "text",
            "text": "CRISPY LEMON<br>ROAST CHICKEN",
            "position": {"top": 785, "left": 221}, "width": 478, "height": 196,
            "font_family": "'Bebas Neue', sans-serif", "font_size": 74, "font_weight": "400",
            "color": "#FFFFFF", "text_align": "left", "line_height": 1.1, "z_index": 20
        },
        "step_1": {
            "type": "text", "text": "PREP", "position": {"top": 190, "left": 0}, "width": 184, "height": 37,
            "font_family": "'Inter', sans-serif", "font_size": 17, "font_weight": "800",
            "color": "#333333", "text_align": "center", "z_index": 20
        },
        "step_2": {
            "type": "text", "text": "COOK", "position": {"top": 374, "left": 0}, "width": 184, "height": 37,
            "font_family": "'Inter', sans-serif", "font_size": 17, "font_weight": "800",
            "color": "#333333", "text_align": "center", "z_index": 20
        },
        "step_3": {
            "type": "text", "text": "SERVE", "position": {"top": 558, "left": 0}, "width": 184, "height": 37,
            "font_family": "'Inter', sans-serif", "font_size": 17, "font_weight": "800",
            "color": "#333333", "text_align": "center", "z_index": 20
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1226, "left": 184}, "width": 552, "height": 49,
            "font_family": "'Inter', sans-serif", "font_size": 22, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "text_transform": "uppercase", "z_index": 20
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
