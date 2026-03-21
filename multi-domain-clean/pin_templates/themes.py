"""
Pin template themes: listicle-style layouts for pin_template_pool.
Each item: template_id, template_name, template_data (canvas, images, elements), style_slots, font_slots.
Add new themes here and run: python scripts/insert_pin_templates.py
"""

# Listicle "50" design: top hero image, diagonal teal band, circular number badge, script + bold title, two bottom images, footer pill.
# Matches reference: WhatsApp Image 2026-03-10 at 14.40.22 (3).jpeg
LISTICLE_50 = {
    "template_id": "listicle_50",
    "template_name": "listicle_50",
    "style_slots": {
        "band": {"background_color": "primary"},
        "badge_circle": {"background": "white", "border": "accent"},
        "accent_text": {"color": "on_primary"},
        "title": {"color": "on_primary"},
        "website": {"color": "on_light"},
    },
    "font_slots": {"badge_number": "body", "accent_text": "accent", "title": "heading", "website": "body"},
    "template_data": {
        "name": "50 Listicle Pin",
        "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},
        "prompt": "Generate text for each field based on the recipe title. Return a JSON object only.",
        "field_prompts": {
            "badge_number": "Generate a number or short count for recipe list (e.g. 50, 30, 10). Output only the number or 2-3 words.",
            "accent_text": "Generate a 2-word catchy phrase for recipe {{title}}, e.g. Super Simple, So Easy.",
            "title": "Generate a short all-caps recipe category title for {{title}}, 2-4 words, e.g. GROUND BEEF RECIPES.",
        },
        "images": {
            "top_image": {"position": {"top": 0, "left": 0}, "width": 736, "height": 523, "layer_order": 1},
            "bottom_left": {"position": {"top": 850, "left": 0}, "width": 368, "height": 458, "layer_order": 2},
            "bottom_right": {"position": {"top": 850, "left": 368}, "width": 368, "height": 458, "layer_order": 2},
        },
        "elements": {
            "band": {
                "type": "div",
                "position": {"top": 490, "left": -30},
                "width": 796,
                "height": 300,
                "background_color": "#1a3c4a",
                "rotation": -2,
                "z_index": 5,
            },
            "badge_circle": {
                "type": "div",
                "position": {"top": 455, "left": 48},
                "width": 80,
                "height": 80,
                "background_color": "#ffffff",
                "border": {"width": 2, "style": "dotted", "color": "#000000"},
                "border_radius": 40,
                "z_index": 10,
            },
            "badge_number": {
                "type": "text",
                "text": "50",
                "position": {"top": 478, "left": 48},
                "width": 80,
                "height": 44,
                "font_family": "Arial Black, sans-serif",
                "font_size": 32,
                "font_weight": "bold",
                "color": "#000000",
                "text_align": "center",
                "z_index": 11,
            },
            "accent_text": {
                "type": "text",
                "text": "Super Simple",
                "position": {"top": 535, "left": 145},
                "width": 240,
                "height": 36,
                "font_family": "Great Vibes, Brush Script MT, cursive",
                "font_size": 26,
                "font_weight": "normal",
                "color": "#ffffff",
                "text_align": "left",
                "z_index": 12,
            },
            "title": {
                "type": "text",
                "text": "GROUND BEEF RECIPES",
                "position": {"top": 568, "left": 145},
                "width": 460,
                "height": 72,
                "font_family": "Arial Black, sans-serif",
                "font_size": 36,
                "font_weight": "bold",
                "color": "#ffffff",
                "text_align": "left",
                "rotation": -2,
                "z_index": 12,
            },
            "footer_pill": {
                "type": "div",
                "position": {"top": 1254, "left": 218},
                "width": 300,
                "height": 44,
                "background_color": "#ffffff",
                "border_radius": 22,
                "z_index": 15,
            },
            "website": {
                "type": "text",
                "text": "{{domain}}",
                "position": {"top": 1256, "left": 218},
                "width": 300,
                "height": 40,
                "font_family": "Roboto, Open Sans, sans-serif",
                "font_size": 15,
                "font_weight": "normal",
                "color": "#000000",
                "text_align": "center",
                "z_index": 20,
            },
        },
    },
}

# All themes to insert. Add new dicts here.
THEMES = [
    LISTICLE_50,
]
