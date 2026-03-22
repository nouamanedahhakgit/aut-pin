#!/usr/bin/env python3
"""Template 68: Badge & Card Title (Cottage Cheese Bread style).

Layout (736 x 1472px, warm beige #F9F5EB background):
  - Brown rounded badge pill at top-left            top:50  left:50
  - White rounded title card                         top:142 left:40  w:656 h:355
      · Giant bold title text inside                top:192 left:80  w:576
      · Warm URL bar inside card                     top:480 left:80  w:576 h:62
  - Full-width food photo (no border-radius)         top:537 left:0   w:736 h:700
      · Pink heart icon (rounded square) overlay     bottom:180 left:40 (top:957)
      · Curly arrow SVG                              bottom:200 right:20 (top:892)
      · Bold white text with black stroke            bottom:80  right:40 (top:1032)
"""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_68"

STYLE_SLOTS = {
    "badge_bg":     {"background_color": "primary"},
    "badge":        {"color": "on_primary"},
    "title_card":   {"background_color": "on_dark"},
    "title":        {"color": "text_primary"},
    "url_bar_bg":   {"background_color": "surface"},
    "url_text":     {"color": "primary"},
    "heart_bg":     {"background_color": "accent"},
    "overlay_text": {"color": "on_dark"},
}

FONT_SLOTS = {
    "badge":        "body",
    "title":        "heading",
    "url_text":     "body",
    "overlay_text": "heading",
}

TEMPLATE_DATA = {
    "name": "Badge & Card Title Pin",
    "preview_url": "",
    "canvas": {"width": 736, "height": 1472, "background_color": "#F9F5EB"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "badge":        "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'QUICK & EASY', 'BEST EVER'). Output ONLY the replacement text for badge, no quotes.",
        "title":        "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Use the recipe name words, each on its own line separated by newline, all uppercase, max 12 characters per line, 2-4 lines. Output ONLY the title text with newlines, no quotes.",
        "overlay_text": "Generate content for overlay_text for recipe {{title}}. You are writing a catchy 3-5 word overlay phrase (e.g. 'For Healthy Breakfast!', 'So Good & Easy!', 'Try This Tonight!'). Title case. Max 22 chars. Output ONLY the text, no quotes.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            # image-section: margin-top:40px from end of title card (top:142 + h:355 + 40 = 537)
            "position": {"top": 537, "left": 0},
            "width": 736,
            "height": 700,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing close-up food photography, warm natural light",
        },
    },
    "elements": {
        # ── Canvas background ──────────────────────────────────────────────
        "canvas_bg": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736, "height": 1472,
            "background_color": "#F9F5EB",
            "z_index": 0,
        },

        # ── Top badge pill ─────────────────────────────────────────────────
        # margin: 50px 50px 30px  → top=50, left=50
        # padding: 20px 50px → inner height ~62px; auto-width ~340px for "HIGH PROTEIN"
        "badge_bg": {
            "type": "div",
            "position": {"top": 50, "left": 50},
            "width": 340, "height": 82,
            "background_color": "#5D4037",
            "border_radius": "50px",
            "box_shadow": "0 4px 10px rgba(0,0,0,0.15)",
            "z_index": 10,
        },
        "badge": {
            "type": "text",
            "text": "HIGH PROTEIN",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: 2-3 words, all uppercase, max 18 characters (e.g. 'HIGH PROTEIN', 'QUICK & EASY', 'BEST EVER'). Output ONLY the replacement text for badge, no quotes.",
            "position": {"top": 50, "left": 50},
            "width": 340, "height": 82,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 28,
            "font_weight": "800",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "3px",
            "text_transform": "uppercase",
            "z_index": 15,
        },

        # ── White title card ────────────────────────────────────────────────
        # top-badge ends at 50+82+30(margin-bottom) = 162 → card top ≈ 162
        # margin: 0 40px → left=40, width=656
        # padding: 50px 40px
        "title_card": {
            "type": "div",
            "position": {"top": 162, "left": 40},
            "width": 656, "height": 355,
            "background_color": "#FFFFFF",
            "border_radius": "20px",
            "box_shadow": "0 4px 20px rgba(0,0,0,0.08)",
            "z_index": 5,
        },

        # title text inside card: card top(162) + card-padding-top(50) = 212
        # left: card_left(40) + padding(40) = 80; width: 656 - 2*40 = 576
        # font-size:100px, line-height:0.95, 3 lines ≈ 285px
        "title": {
            "type": "text",
            "text": "Cottage\nCheese\nBread",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Use the recipe name words, each on its own line separated by newline, all uppercase, max 12 characters per line, 2-4 lines. Output ONLY the title text with newlines, no quotes.",
            "position": {"top": 212, "left": 80},
            "width": 576, "height": 290,
            "font_family": "Montserrat, Arial Black, sans-serif",
            "font_size": 100,
            "font_weight": "900",
            "color": "#000000",
            "text_align": "center",
            "line_height": 0.95,
            "text_transform": "uppercase",
            "letter_spacing": "-3px",
            "white_space": "pre-line",
            "z_index": 8,
        },

        # url bar: card_top(162) + card_padding_top(50) + title_h(285) + margin-top(30) = 527
        # left: card_left(40) + padding(40) = 80; width: 576; height ~62px
        "url_bar_bg": {
            "type": "div",
            "position": {"top": 457, "left": 80},
            "width": 576, "height": 60,
            "background_color": "#F5E6C8",
            "border_radius": "10px",
            "border": {"width": "3px", "style": "solid", "color": "#E8D5B5"},
            "z_index": 8,
        },
        "url_text": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 457, "left": 80},
            "width": 576, "height": 60,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 20,
            "font_weight": "700",
            "color": "#5D4037",
            "text_align": "center",
            "letter_spacing": "2px",
            "text_transform": "uppercase",
            "z_index": 12,
        },

        # ── Overlays on the food photo ─────────────────────────────────────
        # image section starts at top:537, height:700 → ends at 1237

        # curly arrow svg: bottom:200px from image-end → top = 1237-200-150 = 887
        # right:20 → left = 736-20-120 = 596; 120×150px
        "curly_arrow": {
            "type": "icon",
            "position": {"top": 887, "left": 596},
            "width": 120, "height": 150,
            "z_index": 10,
        },

        # heart/instagram icon: bottom:180 → top = 1237-180-100 = 957; left=40; 100×100
        "heart_bg": {
            "type": "div",
            "position": {"top": 957, "left": 40},
            "width": 100, "height": 100,
            "background_color": "#E4405F",
            "border_radius": "25px",
            "box_shadow": "0 6px 20px rgba(228,64,95,0.4)",
            "z_index": 20,
        },

        # bottom-text: bottom:80 → top = 1237-80-160 = 997; right:40 → left=736-40-420=276
        # font-size:72px, line-height:0.9, 2 lines ≈ 130px; width≈420px
        "overlay_text": {
            "type": "text",
            "text": "For Healthy\nBreakfast!",
            "text_prompt": "Generate content for overlay_text for recipe {{title}}. You are writing a catchy 3-5 word overlay phrase (e.g. 'For Healthy Breakfast!', 'So Good & Easy!', 'Try This Tonight!'). Title case. Max 22 chars. Output ONLY the text, no quotes.",
            "position": {"top": 997, "left": 276},
            "width": 420, "height": 160,
            "font_family": "Montserrat, Arial Black, sans-serif",
            "font_size": 72,
            "font_weight": "900",
            "color": "#FFFFFF",
            "text_align": "right",
            "line_height": 0.9,
            "text_transform": "uppercase",
            "letter_spacing": "-2px",
            "white_space": "pre-line",
            "text_shadow": "-4px -4px 0 #000, 4px -4px 0 #000, -4px 4px 0 #000, 4px 4px 0 #000, -4px 0 0 #000, 4px 0 0 #000, 0 -4px 0 #000, 0 4px 0 #000",
            "z_index": 25,
        },
    },
    "background": "#F9F5EB",
}


def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
