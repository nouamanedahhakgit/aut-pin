from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_32"

# Slots link template elements to domain-specific colors and fonts
STYLE_SLOTS = {
    "glass_card": {"background_color": "background", "border": "border_accent"},
    "title": {"color": "text_primary"},
    "badge_bg": {"background_color": "primary"},
    "badge_text": {"color": "on_primary"},
    "website": {"color": "text_secondary"}
}

FONT_SLOTS = {
    "title": "heading",
    "badge_text": "body",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "Frosted Elegance (Glassmorphism)",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16", "background_color": "#f0f2f5"},
    "prompt": "You are a luxury food stylist. Generate a punchy, click-worthy title for this recipe. Keep it under 6 words. For the badge, use 2-3 words like 'MUST TRY' or '5-MIN RECIPE'.",
    "field_prompts": {
        "title": "Main title of the recipe pin (e.g. 'The Only Lasagna You Need').",
        "badge": "Short 2-word highlight badge (e.g. 'BEST EVER')."
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": 1
        }
    },
    "elements": {
        "glass_card": {
            "type": "div",
            "position": {"top": 450, "left": 40}, "width": 520, "height": 450,
            "background": "rgba(255, 255, 255, 0.7)",
            "backdrop_filter": "blur(20px) saturate(180%)",
            "border_radius": 32,
            "border": "1px solid rgba(255, 255, 255, 0.3)",
            "box_shadow": "0 8px 32px 0 rgba(31, 38, 135, 0.15)",
            "z_index": 5
        },
        "badge_bg": {
            "type": "div",
            "position": {"top": 430, "left": 220}, "width": 160, "height": 40,
            "background": "#FF7849",
            "border_radius": 20,
            "z_index": 15,
            "box_shadow": "0 4px 15px rgba(0,0,0,0.1)"
        },
        "badge_text": {
            "type": "text", "text": "BEST EVER",
            "position": {"top": 430, "left": 220}, "width": 160, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 14, "font_weight": "800",
            "color": "#FFFFFF", "text_align": "center", "text_transform": "uppercase",
            "letter_spacing": 1.5, "z_index": 16
        },
        "title": {
            "type": "text", "text": "CREAMY GARLIC BUTTER PASTA",
            "position": {"top": 500, "left": 70}, "width": 460, "height": 280,
            "font_family": "'Playfair Display', serif", "font_size": 58, "font_weight": "900",
            "line_height": 1.1, "color": "#1a1a1a", "text_align": "center",
            "z_index": 10
        },
        "stars": {
            "type": "stars", "count": 5, "star_size": 24, "color": "#FFB800",
            "position": {"top": 780, "left": 230}, "z_index": 10, "spacing": 6
        },
        "website": {
            "type": "text", "text": "{{domain}}",
            "position": {"top": 840, "left": 40}, "width": 520, "height": 40,
            "font_family": "'Inter', sans-serif", "font_size": 18, "font_weight": "600",
            "color": "#666666", "text_align": "center", "opacity": 0.8,
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
