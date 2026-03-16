from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_37"

# Slots link template elements to domain-specific colors and fonts
STYLE_SLOTS = {
    "card": {"background_color": "surface"},
    "title_text": {"color": "text_primary"},
    "subtitle_text": {"color": "primary"},
    "accent_line": {"background_color": "primary"},
    "website_pill": {"background_color": "primary"},
    "website_text": {"color": "on_primary"}
}

FONT_SLOTS = {
    "title_text": "heading",
    "website_text": "body",
    "subtitle_text": "body"
}

TEMPLATE_DATA = {
    "name": "Creative Floating Card",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16", "background_color": "#FDFDFD"},
    "prompt": "You are a creative designer. Write an engaging, modern title for this recipe. Keep it punchy, around 5-7 words.",
    "field_prompts": {
        "title_text": "Punchy, modern title.",
        "subtitle_text": "A short, engaging subtitle (2-3 words)."
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 40, "left": 40}, "width": 656, "height": 1100, "layer_order": 1,
            "border_radius": "30px",
            "box_shadow": "0 20px 40px rgba(0,0,0,0.15)"
        }
    },
    "elements": {
        "card": {
            "type": "div",
            "position": {"top": 700, "left": 68}, "width": 600, "height": 450,
            "background": "#FFFFFF",
            "border_radius": "24px",
            "box_shadow": "0 25px 50px rgba(0,0,0,0.12)",
            "z_index": 5
        },
        "subtitle_text": {
            "type": "text", "text": "MUST TRY RECIPE",
            "position": {"top": 760, "left": 118}, "width": 500, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 22, "font_weight": "700",
            "color": "#FF7849", "text_align": "left", "letter_spacing": "3px",
            "text_transform": "uppercase",
            "z_index": 10
        },
        "title_text": {
            "type": "text", "text": "The Ultimate Garlic Butter Steak Bites",
            "position": {"top": 810, "left": 118}, "width": 500, "height": 220,
            "font_family": "'Playfair Display', serif", "font_size": 75, "font_weight": "800",
            "line_height": 1.05, "color": "#2A2A2A", "text_align": "left",
            "z_index": 10
        },
        "accent_line": {
            "type": "div",
            "position": {"top": 1050, "left": 118}, "width": 100, "height": 6,
            "background": "#FF7849", "z_index": 10,
            "border_radius": "3px"
        },
        "website_pill": {
            "type": "div",
            "position": {"top": 1200, "left": 218}, "width": 300, "height": 60,
            "background": "#FF7849", "border_radius": "30px",
            "z_index": 10
        },
        "website_text": {
            "type": "text", "text": "{{domain}}",
            "position": {"top": 1215, "left": 218}, "width": 300, "height": 60,
            "font_family": "'Inter', sans-serif", "font_size": 22, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "letter_spacing": "1.5px",
            "text_transform": "uppercase",
            "z_index": 15
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
