from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_33"

# Slots link template elements to domain-specific colors and fonts
STYLE_SLOTS = {
    "overlay_band": {"background_color": "primary"},
    "title": {"color": "text_primary"},
    "website": {"color": "on_primary"}
}

FONT_SLOTS = {
    "title": "heading",
    "website": "body"
}

TEMPLATE_DATA = {
    "name": "The Editorial (Vogue Style)",
    "canvas": {"width": 600, "height": 1067, "aspect_ratio": "9:16", "background_color": "#000000"},
    "prompt": "You are a food magazine editor. Write a sophisticated, elegant title for this recipe. Use high-level vocabulary but keep it under 8 words. Website should be bottom center.",
    "field_prompts": {
        "title": "Elegant magazine-style title (e.g. 'A Summer Evening in Tuscany').",
        "author": "Short author name (e.g. 'BETH LARKINS')."
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 0, "left": 0}, "width": 600, "height": 1067, "layer_order": 1,
            "opacity": 0.9,
            "filter": "contrast(110%)"
        }
    },
    "elements": {
        "overlay_band": {
            "type": "div",
            "position": {"top": 867, "left": 0}, "width": 600, "height": 200,
            "background": "#FF7849",
            "z_index": 5,
            "box_shadow": "0 -10px 40px rgba(0,0,0,0.4)"
        },
        "title_box": {
            "type": "div",
            "position": {"top": 40, "left": 40}, "width": 520, "height": 600,
            "border": "12px solid #FFFFFF",
            "z_index": 4,
            "opacity": 0.3
        },
        "title": {
            "type": "text", "text": "THE ART OF THE PERFECT SOUFFLÉ",
            "position": {"top": 120, "left": 60}, "width": 480, "height": 500,
            "font_family": "'Playfair Display', serif", "font_size": 72, "font_weight": "900",
            "line_height": 0.95, "color": "#FFFFFF", "text_align": "center",
            "text_transform": "uppercase", "letter_spacing": -2,
            "text_shadow": "0 10px 30px rgba(0,0,0,0.8)",
            "z_index": 10
        },
        "author": {
            "type": "text", "text": "EXCLUSIVELY BY BETH LARKINS",
            "position": {"top": 620, "left": 60}, "width": 480, "height": 30,
            "font_family": "'Inter', sans-serif", "font_size": 16, "font_weight": "700",
            "color": "#FFFFFF", "text_align": "center", "letter_spacing": 4,
            "opacity": 0.9,
            "z_index": 10
        },
        "line": {
            "type": "div",
            "position": {"top": 660, "left": 250}, "width": 100, "height": 2,
            "background": "#FFFFFF", "z_index": 10
        },
        "website": {
            "type": "text", "text": "{{domain}}",
            "position": {"top": 930, "left": 0}, "width": 600, "height": 50,
            "font_family": "'Inter', sans-serif", "font_size": 22, "font_weight": "800",
            "color": "#FFFFFF", "text_align": "center", "letter_spacing": 2,
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
