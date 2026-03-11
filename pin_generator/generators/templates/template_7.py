from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_7"

STYLE_SLOTS = {
    "badge": {"background_color": "secondary", "color": "on_secondary"},
    "floating_card": {"background_color": "primary_glass"},
    "title": {"color": "on_primary"},
    "stars": {"color": "secondary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "badge": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Glassmorphism Luxe Recipe Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/fcb98647364.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}.",
    "field_prompts": {
        "badge": "Generate content for badge for recipe {{title}}. Style: 2–3 words, Title Case. Return only the badge text.",
        "title": "Generate content for title for recipe {{title}}. Format: ALL CAPS, 2–4 words. Return only the title text.",
        "website": "Generate website footer text like WWW.SITE.COM.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "description_prompt": "Pinterest-style food photography of {{title}}, vibrant and appetizing.",
            "position": {"top": 0, "left": 0}, 
            "width": 600, 
            "height": 1067, 
            "layer_order": 1
        },
    },
    "elements": {
        "badge": {
            "type": "text",
            "text": "Premium Recipe",
            "text_prompt": "Generate badge text. Style: uppercase, 2-3 words.",
            "position": {"top": 32, "left": 32},
            "width": 160,
            "height": 40,
            "font_family": "'Inter', sans-serif",
            "font_size": 12,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "background_color": "rgba(255, 255, 255, 0.2)",
            "backdrop_blur": 10,
            "border": {"width": 1, "color": "rgba(255, 255, 255, 0.4)"},
            "border_radius": 20,
            "z_index": 20,
            "text_shadow": "0 0 10px rgba(255, 255, 255, 0.5)"
        },
        "floating_card": {
            "type": "div",
            "position": {"top": 440, "left": 40},
            "width": 520,
            "height": 220,
            "background_color": "rgba(255, 255, 255, 0.15)",
            "backdrop_blur": 20,
            "border": {"width": 1, "color": "rgba(255, 255, 255, 0.3)"},
            "box_shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.3)",
            "border_radius": 20,
            "z_index": 10,
        },
        "title": {
            "type": "text",
            "text": "HOMEMADE ARTISAN PASTA",
            "text_prompt": "Recipe title. Format: ALL CAPS.",
            "position": {"top": 480, "left": 80},
            "width": 440,
            "height": 110,
            "font_family": "'Playfair Display', serif",
            "font_size": 48,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "line_height": 1.1,
            "z_index": 20,
            "text_shadow": "0 0 10px rgba(255, 255, 255, 0.5)"
        },
        "stars": {
            "type": "stars",
            "count": 5,
            "size": 24,
            "color": "#FACC15",
            "position": {"top": 600, "left": 232},
            "spacing": 4,
            "z_index": 20
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "text_prompt": "Website URL.",
            "position": {"top": 1000, "left": 0},
            "width": 600,
            "height": 30,
            "font_family": "'Inter', sans-serif",
            "font_size": 16,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "text_transform": "uppercase",
            "z_index": 20,
            "text_shadow": "0 0 10px rgba(255, 255, 255, 0.5)"
        }
    },
    "background": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png"
}

def run(output_dir=None):
    apply_domain_style(
        TEMPLATE_DATA,
        STYLE_SLOTS,
        FONT_SLOTS,
        TEMPLATE_DATA.get("domain_colors"),
        TEMPLATE_DATA.get("domain_fonts")
    )
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
