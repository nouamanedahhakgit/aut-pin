from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_6"

STYLE_SLOTS = {
    "badge": {"background_color": "secondary", "color": "on_secondary"},
    "title_card": {"background_color": "primary"},
    "title": {"color": "on_primary"},
    "subtitle": {"color": "on_primary"},
    "website": {"color": "on_dark"}
}

FONT_SLOTS = {
    "title": "heading",
    "subtitle": "body",
    "badge": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Modern Brutalist Recipe Pin",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/1025609e4e2.png",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}.",
    "field_prompts": {
        "badge": "Generate a bold, high-impact badge for recipe {{title}}. Style: 1–2 words, uppercase, visually striking with playful energy. Return only the badge text.",
        "title": "Generate the main title for recipe {{title}}. Style: uppercase, 2–4 words, highly legible, modern brutalist feel. Return only the title text.",
        "subtitle": "Generate a subtitle for recipe {{title}}. Style: 8–12 words, all caps, bold, describe a quick or unique aspect of the recipe. Return only the subtitle text.",
        "website": "Generate the footer website name. Style: uppercase, short, bold, easy to read, suitable for branding. Return only the website text."
    },
    "images": {
        "top_image": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "description_prompt": "Close-up food photography of {{title}}, vibrant colors, dramatic lighting, highly appetizing plating, shallow depth of field, Pinterest food photography style.",
            "position": {"top": 0, "left": 0},
            "width": 600,
            "height": 600,
            "layer_order": 1
        }
    },
    "elements": {
        "title_card": {
            "type": "div",
            "position": {"top": 580, "left": 40},
            "width": 520,
            "height": 320,
            "background_color": "#000000",
            "border": {"width": 4, "color": "#000000"},
            "box_shadow": "10px 10px 0px 0px #FFD700",
            "z_index": 5
        },
        "badge": {
            "type": "text",
            "text": "NEW",
            "text_prompt": "Identify a promotional badge for {{title}}. Style: 1 word, ALL CAPS.",
            "position": {"top": 540, "left": 480},
            "width": 100,
            "height": 100,
            "font_family": "'Inter', sans-serif",
            "font_size": 24,
            "font_weight": "900",
            "color": "#000000",
            "background_color": "#FFD700",
            "text_align": "center",
            "text_transform": "uppercase",
            "line_height": 1.0,
            "border": {"width": 4, "color": "#000000"},
            "rotation": 5,
            "z_index": 15
        },
        "title": {
            "type": "text",
            "text": "SPICY VODKA PASTA",
            "text_prompt": "Main recipe title derived from {{title}}. Format: 2–4 words, ALL CAPS.",
            "position": {"top": 600, "left": 80},
            "width": 440,
            "height": 180,
            "font_family": "'Bebas Neue', sans-serif",
            "font_size": 70,
            "font_weight": "400",
            "color": "#FFD700",
            "text_align": "left",
            "text_transform": "uppercase",
            "line_height": 1.1,
            "z_index": 10
        },
        "subtitle": {
            "type": "text",
            "text": "THE ULTIMATE 20-MINUTE COMFORT",
            "text_prompt": "Short tagline for {{title}}. 4-6 words.",
            "position": {"top": 820, "left": 80},
            "width": 400,
            "height": 50,
            "font_family": "'Inter', sans-serif",
            "font_size": 22,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "left",
            "text_transform": "uppercase",
            "line_height": 1.2,
            "z_index": 10
        },
        "decor_box": {
            "type": "div",
            "position": {"top": 880, "left": -20},
            "width": 200,
            "height": 100,
            "background_color": "#FFD700",
            "border": {"width": 4, "color": "#000000"},
            "z_index": 1
        },
        "line1": {
            "type": "div",
            "position": {"top": 920, "left": 0},
            "width": 600,
            "height": 4,
            "background_color": "#000000",
            "z_index": 2
        },
        "line2": {
            "type": "div",
            "position": {"top": 940, "left": 40},
            "width": 520,
            "height": 4,
            "background_color": "#000000",
            "z_index": 2
        },
        "line3": {
            "type": "div",
            "position": {"top": 1020, "left": 200},
            "width": 200,
            "height": 4,
            "background_color": "#000000",
            "z_index": 2
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "text_prompt": "Website domain.",
            "position": {"top": 980, "left": 0},
            "width": 600,
            "height": 40,
            "font_family": "'Inter', sans-serif",
            "font_size": 20,
            "font_weight": "700",
            "color": "#000000",
            "text_align": "center",
            "text_transform": "uppercase",
            "line_height": 1.0,
            "z_index": 10
        }
    },
    "top_image": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png"
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
