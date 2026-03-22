"""
Template 53: Bold Typography Hero + Organic Edge
A high-impact vertical layout with massive display typography on a bold warm background,
organic curved image reveal, and decorative arrow accent.
"""

from _base import render_pin, apply_domain_style

TEMPLATE_ID = "template_53"

STYLE_SLOTS = {
    "top_panel": {"background_color": "primary"},
    "bottom_bar": {"background_color": "secondary"},
    "badge_pill": {"background_color": "on_dark", "color": "surface"},
    "category_text": {"color": "on_primary"},
    "title_text": {"color": "on_primary"},
    "subtitle_text": {"color": "on_primary"},
    "website_text": {"color": "on_primary"},
    "arrow_accent": {"color": "surface"},
    "star_accent": {"color": "accent"}
}

FONT_SLOTS = {
    "category_text": "body",
    "title_text": "display",
    "subtitle_text": "body",
    "badge_pill": "body",
    "website_text": "body"
}

TEMPLATE_DATA = {
    "name": "Bold Typography Hero with Organic Edge",
    "preview_url": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/template_preview/t53.png",
    "canvas": {"width": 736, "height": 1308, "aspect_ratio": "9:16"},

    "background": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",

    "prompt": "Generate text for each field based on the recipe title provided. Use the field_prompts JSON below: for each key, generate content using the corresponding prompt (replace {{title}} with the user's recipe title). Your response MUST be a single JSON object only, with one key per field and the value being the generated text. Format: {\"field_name\": \"text\", ...}. Do not include 'website' or 'domain' in your output; the domain name is injected automatically.",

    "field_prompts": {
        "category_text": "Generate content for category_text for recipe {{title}}. You are writing the CATEGORY label for a Pinterest food pin. Format: 2-3 words uppercase, describing the main ingredient or dish type (e.g. 'COTTAGE CHEESE', 'HIGH PROTEIN', 'EASY DINNER'). Max 20 characters. Output ONLY the replacement text for category_text, no quotes. Given the user's recipe title {{title}}, return only the category_text text.",
        "title": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: 2-4 words, title case, massive impact font style, short and punchy (e.g. 'STUFFED PEPPERS', 'CHICKEN SALAD', 'BEEF STEW'). Max 25 characters. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
        "badge": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: uppercase descriptor with ampersand, 3-5 words (e.g. 'EASY & HIGH PROTEIN', 'QUICK & HEALTHY', 'LOW CARB & TASTY'). Max 30 characters. Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text."
    },

    "images": {
        "background": {
            "src": "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/ba00aa85/58c84a65007.png",
            "position": {"top": 520, "left": 0},
            "width": 736,
            "height": 788,
            "layer_order": 1,
            "object_fit": "cover",
            "description_prompt": "Appetizing food photography, warm lighting, top-down or 45-degree angle"
        }
    },

    "elements": {
        "top_panel": {
            "type": "div",
            "position": {"top": 0, "left": 0},
            "width": 736,
            "height": 580,
            "background_color": "#E89B35",
            "z_index": 2
        },

        "category_text": {
            "type": "text",
            "text_prompt": "Generate content for category_text for recipe {{title}}. You are writing the CATEGORY label for a Pinterest food pin. Format: 2-3 words uppercase, describing the main ingredient or dish type (e.g. 'COTTAGE CHEESE', 'HIGH PROTEIN', 'EASY DINNER'). Max 20 characters. Output ONLY the replacement text for category_text, no quotes. Given the user's recipe title {{title}}, return only the category_text text.",
            "position": {"top": 50, "left": 40},
            "width": 656,
            "height": 50,
            "font_family": "Montserrat",
            "font_size": 28,
            "font_weight": 700,
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": 6,
            "z_index": 3
        },

        "title_text": {
            "type": "text",
            "text_prompt": "Generate content for title for recipe {{title}}. You are writing the main TITLE for a Pinterest food pin. Format: 2-4 words, title case, massive impact font style, short and punchy (e.g. 'STUFFED PEPPERS', 'CHICKEN SALAD', 'BEEF STEW'). Max 25 characters. Output ONLY the replacement text for title, no quotes. Given the user's recipe title {{title}}, return only the title text.",
            "position": {"top": 110, "left": 30},
            "width": 676,
            "height": 200,
            "font_family": "Anton",
            "font_size": 88,
            "font_weight": 400,
            "color": "#FFFFFF",
            "text_align": "center",
            "line_height": 1.05,
            "z_index": 3
        },

        "badge_pill": {
            "type": "text",
            "text_prompt": "Generate content for badge for recipe {{title}}. You are writing the BADGE label for a Pinterest food pin. Format: uppercase descriptor with ampersand, 3-5 words (e.g. 'EASY & HIGH PROTEIN', 'QUICK & HEALTHY', 'LOW CARB & TASTY'). Max 30 characters. Output ONLY the replacement text for badge, no quotes. Given the user's recipe title {{title}}, return only the badge text.",
            "position": {"top": 320, "left": 118},
            "width": 500,
            "height": 60,
            "font_family": "Montserrat",
            "font_size": 24,
            "font_weight": 800,
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": 2,
            "background_color": "#1A1A1A",
            "border_radius": 30,
            "padding": "15px 30px",
            "z_index": 4
        },

        "image_overlay_shape": {
            "type": "div",
            "position": {"top": 480, "left": -20},
            "width": 776,
            "height": 80,
            "background_color": "#E89B35",
            "border_radius": "0 0 50% 50%",
            "z_index": 5
        },

        "arrow_accent": {
            "type": "text",
            "text": "\u21B2",
            "position": {"top": 400, "left": 30},
            "width": 100,
            "height": 100,
            "font_family": "Georgia",
            "font_size": 120,
            "font_weight": 400,
            "color": "#FFFFFF",
            "text_align": "center",
            "rotation": -15,
            "z_index": 6
        },

        "bottom_bar": {
            "type": "div",
            "position": {"top": 1238, "left": 0},
            "width": 736,
            "height": 70,
            "background_color": "#8B5A2B",
            "z_index": 7
        },

        "website_text": {
            "type": "text",
            "text": "{{domain}}",
            "position": {"top": 1253, "left": 0},
            "width": 736,
            "height": 40,
            "font_family": "Montserrat",
            "font_size": 18,
            "font_weight": 600,
            "color": "#FFFFFF",
            "text_align": "center",
            "letter_spacing": 3,
            "text_transform": "uppercase",
            "z_index": 8
        },

        "star_accent_1": {
            "type": "stars",
            "count": 5,
            "star_size": 20,
            "color": "#FFD700",
            "position": {"top": 1180, "left": 568},
            "z_index": 6
        }
    }
}

def run(output_dir=None):
    apply_domain_style(TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS, 
                       TEMPLATE_DATA.get("domain_colors"), TEMPLATE_DATA.get("domain_fonts"))
    render_pin(TEMPLATE_ID, TEMPLATE_DATA, output_dir)

if __name__ == "__main__":
    run()
