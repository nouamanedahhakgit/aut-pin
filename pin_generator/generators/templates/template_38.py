from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_38"

STYLE_SLOTS = {
    "bottom_panel": {"background_color": "surface"},
    "title_text": {"color": "text_primary"},
    "circle_badge": {"background_color": "primary"},
    "badge_text": {"color": "on_primary"},
    "website_text": {"color": "text_secondary"}
}

FONT_SLOTS = {
    "title_text": "heading",
    "website_text": "body",
    "badge_text": "body"
}

TEMPLATE_DATA = {
    "name": "Geometric Split Circle",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16", "background_color": "#F4F4F4"},
    "prompt": "You are a playful food blogger. Write a fun, inviting title for this recipe.",
    "field_prompts": {
        "title_text": "Fun, inviting title (e.g. 'You Will Love This').",
        "badge_text": "Very short badge text like 'NEW', 'YUM', or 'EASY'."
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 736, "height": 850, "layer_order": 1
        }
    },
    "elements": {
        "bottom_panel": {
            "type": "div",
            "position": {"top": 850, "left": 0}, "width": 736, "height": 458,
            "background": "#FFFFFF",
            "z_index": 2
        },
        "circle_badge": {
            "type": "div",
            "position": {"top": 780, "left": 298}, "width": 140, "height": 140,
            "background": "#FF4B4B",
            "border_radius": "70px",
            "z_index": 10,
            "box_shadow": "0 10px 20px rgba(0,0,0,0.15)"
        },
        "badge_text": {
            "type": "text", "text": "HOT",
            "position": {"top": 835, "left": 298}, "width": 140, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 28, "font_weight": "800",
            "color": "#FFFFFF", "text_align": "center", "letter_spacing": "2px",
            "z_index": 15
        },
        "title_text": {
            "type": "text", "text": "Crispy Baked Parmesan Zucchini Fries",
            "position": {"top": 970, "left": 68}, "width": 600, "height": 220,
            "font_family": "'Playfair Display', serif", "font_size": 65, "font_weight": "800",
            "line_height": 1.1, "color": "#1A1A1A", "text_align": "center",
            "z_index": 10
        },
        "website_text": {
            "type": "text", "text": "{{domain}}",
            "position": {"top": 1220, "left": 0}, "width": 736, "height": 60,
            "font_family": "'Inter', sans-serif", "font_size": 24, "font_weight": "600",
            "color": "#888888", "text_align": "center", "letter_spacing": "1.5px",
            "text_transform": "uppercase",
            "z_index": 10
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
