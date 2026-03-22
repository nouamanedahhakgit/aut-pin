#!/usr/bin/env python3
"""Template 69: Gradient Header Bold (Stuffed Peppers style).

Layout (736 x 1472px, warm gradient #F5A623 → #F7B731):
  - Small uppercase descriptor line at top         top:60  centered
  - Giant bold title text                          top:125 centered w:696
  - Black pill badge                               top:389 centered w:380 h:74
  - Large rounded food photo                       top:503 left:40  w:656 h:839 r:40px
  - Solid dark footer bar                          top:1392 full-width h:80
      · Domain URL text inside footer
"""
from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_69"

STYLE_SLOTS = {
    "small_title":  {"color": "on_primary"},
    "title":        {"color": "on_primary"},
    "badge_bg":     {"background_color": "on_dark"},
    "badge":        {"color": "on_primary"},
    "footer_bg":    {"background_color": "secondary"},
    "website":      {"color": "on_primary"},
}

FONT_SLOTS = {
    "small_title": "body",
    "title":       "heading",
    "badge":       "body",
    "website":     "body",
}

TEMPLATE_DATA = {
    "name": "Gradient Header Bold Pin",
    "preview_url": "",
    "canvas": {"width": 736, "height": 1472, "background_color": "#F5A623"},
    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",
    "field_prompts": {
        "small_title": "Generate content for small_title for recipe {{title}}. You are writing a small DESCRIPTOR line that appears above the main title on a Pinterest pin. This is a key ingredient, modifier, or cooking style (e.g. 'Cottage Cheese', 'Grilled', 'One Pot'). 1-2 words, title case, max 16 characters. Output ONLY the text, no quotes.",
        "title":       "Generate content for title for recipe {{title}}. You are writing the MAIN GIANT TITLE for a Pinterest food pin. Use 1-2 of the key recipe words, ALL UPPERCASE, max 14 characters per line, put each word on its own line if 2 words (e.g. 'STUFFED\\nPEPPERS', 'BANANA\\nBREAD'). Output ONLY the text with newlines if needed, no quotes.",
        "badge":       "Generate content for badge for recipe {{title}}. You are writing a BADGE label for a Pinterest food pin. Format: 3-5 words, title case, max 24 characters (e.g. 'Easy & High Protein', 'Quick 15 Min Meal', 'Gluten Free & Healthy'). Output ONLY the text, no quotes.",
    },
    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            # image-section: padding:0 40px so left=40; margin-top:40px from badge bottom
            # badge bottom = 389+74 = 463; image top = 463+40 = 503
            "position": {"top": 503, "left": 40},
            "width": 656,
            "height": 839,
            "layer_order": 5,
            "object_fit": "cover",
            "border_radius": 40,
            "box_shadow": "0 10px 30px rgba(0,0,0,0.2)",
            "description_prompt": "Beautiful colorful food photography, appetizing plated dish",
        },
    },
    "elements": {
        # ── Full gradient background ────────────────────────────────────────
        "gradient_bg": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736, "height": 1472,
            "background_color": "#F5A623",
            "background": "linear-gradient(135deg, #F5A623 0%, #F7B731 100%)",
            "z_index": 0,
        },

        # ── Small descriptor title ─────────────────────────────────────────
        # padding-top:60px, font-size:42px, letter-spacing:4px, margin-bottom:10px → height≈55px
        "small_title": {
            "type": "text",
            "text": "Cottage Cheese",
            "text_prompt": "Generate content for small_title for recipe {{title}}. You are writing a small DESCRIPTOR line that appears above the main title on a Pinterest pin. This is a key ingredient, modifier, or cooking style (e.g. 'Cottage Cheese', 'Grilled', 'One Pot'). 1-2 words, title case, max 16 characters. Output ONLY the text, no quotes.",
            "position": {"top": 60, "left": 0},
            "width": 736, "height": 55,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 30,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "4px",
            "text_transform": "uppercase",
            "z_index": 10,
        },

        # ── Main giant title ───────────────────────────────────────────────
        # top = 60+55+10 = 125; font-size:130px, line-height:0.9, 2 lines → h≈234px
        # margin:0 20px → left=20, width=696
        "title": {
            "type": "text",
            "text": "STUFFED\nPEPPERS",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the MAIN GIANT TITLE for a Pinterest food pin. Use 1-2 of the key recipe words, ALL UPPERCASE, max 14 characters per line, put each word on its own line if 2 words (e.g. 'STUFFED\\nPEPPERS', 'BANANA\\nBREAD'). Output ONLY the text with newlines if needed, no quotes.",
            "position": {"top": 125, "left": 20},
            "width": 696, "height": 244,
            "font_family": "Montserrat, Arial Black, sans-serif",
            "font_size": 118,
            "font_weight": "900",
            "color": "#FFFFFF",
            "text_align": "center",
            "line_height": 0.9,
            "text_transform": "uppercase",
            "letter_spacing": "-2px",
            "text_shadow": "0 4px 8px rgba(0,0,0,0.1)",
            "white_space": "pre-line",
            "z_index": 10,
        },

        # ── Black pill badge ───────────────────────────────────────────────
        # top = 125+244+30(margin) = 399; centered on 736 → left=(736-380)/2=178
        # padding:18px 40px, font-size:38px → height≈74px
        "badge_bg": {
            "type": "div",
            "position": {"top": 399, "left": 178},
            "width": 380, "height": 64,
            "background_color": "#000000",
            "border_radius": "50px",
            "box_shadow": "0 4px 15px rgba(0,0,0,0.2)",
            "z_index": 10,
        },
        "badge": {
            "type": "text",
            "text": "Easy & High Protein",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing a BADGE label for a Pinterest food pin. Format: 3-5 words, title case, max 24 characters (e.g. 'Easy & High Protein', 'Quick 15 Min Meal', 'Gluten Free & Healthy'). Output ONLY the text, no quotes.",
            "position": {"top": 399, "left": 178},
            "width": 380, "height": 64,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 24,
            "font_weight": "700",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "2px",
            "text_transform": "uppercase",
            "z_index": 15,
        },

        # ── Footer bar ─────────────────────────────────────────────────────
        # position:absolute; bottom:0; padding:35px → height≈80px → top=1392
        "footer_bg": {
            "type": "div",
            "position": {"top": 1392, "left": 0},
            "width": 736, "height": 80,
            "background_color": "#8B5A2B",
            "z_index": 10,
        },
        "website": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1392, "left": 0},
            "width": 736, "height": 80,
            "font_family": "Montserrat, Arial, sans-serif",
            "font_size": 22,
            "font_weight": "600",
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": "3px",
            "text_transform": "uppercase",
            "z_index": 15,
        },
    },
    "background": "#F5A623",
}


def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS,
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)


if __name__ == "__main__":
    run()
