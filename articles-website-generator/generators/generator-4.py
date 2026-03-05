# generator.py
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO ANALYSIS RESULTS - EMBEDDED CONFIG (Zero Runtime Analysis)
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG = {
    "title": "White Chocolate Cranberry Blondies",
    "categories_list": [{"id": 1, "categorie": "Dessert"}, {"id": 2, "categorie": "Baking"}],
    "colors": {
        "primary": "#FF6B35",
        "secondary": "#F7C59F",
        "accent": "#E85D04",
        "background": "#FFFCFA",
        "container_bg": "#FFFFFF",
        "border": "#FFE5D9",
        "text_primary": "#2D2D2D",
        "text_secondary": "#5A5A5A",
        "button_print": "#2D2D2D",
        "button_pin": "#E60023",
        "button_hover_print": "#000000",
        "button_hover_pin": "#BD081C",
        "link": "#FF6B35",
        "list_marker": "#FF6B35"
    },
    "fonts": {
        "heading": {
            "family": "'Playfair Display', Georgia, serif",
            "weights": [400, 700],
            "sizes": {"h1": "2.5rem", "h2": "1.8rem", "h3": "1.4rem"}
        },
        "body": {
            "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            "weight": 400,
            "size": "1rem",
            "line_height": 1.7
        }
    },
    "layout": {
        "max_width": "800px",
        "section_spacing": "2.5rem",
        "paragraph_spacing": "1.2rem",
        "list_spacing": "0.8rem",
        "container_padding": "2rem",
        "border_radius": "12px",
        "box_shadow": "0 4px 20px rgba(0,0,0,0.08)"
    },
    "components": {
        "numbered_list": {
            "style": "circle",
            "circle_bg": "#FF6B35",
            "circle_color": "#FFFFFF",
            "circle_size": "28px"
        },
        "bullet_list": {
            "style": "disc",
            "color": "#FF6B35"
        },
        "pro_tips_box": {
            "bg_color": "#FFF5F0",
            "border_color": "#FF6B35",
            "border_left": "4px",
            "padding": "1.5rem"
        },
        "recipe_card": {
            "bg": "#FFFFFF",
            "border": "2px solid #FFE5D9",
            "border_radius": "16px",
            "padding": "2rem",
            "meta_icon_color": "#FF6B35"
        }
    },
    "images": {
        "main_article_image": "hero-blondies.jpg",
        "ingredient_image": "ingredients-flatlay.jpg",
        "recipe_card_image": "hero-blondies.jpg"
    },
    "structure_template": {
        "word_counts": {
            "intro": 50,
            "why_i_love_this_recipe": 30,
            "ingredients_list": 40,
            "optional_variations": 25,
            "ingredient_quality_notes": 40,
            "step_by_step_instructions": 200,
            "tips_tricks": 100,
            "pro_tips": 60,
            "variations": 120,
            "storage_info": 100,
            "faqs": 150,
            "conclusion": 50
        }
    },
    "dark_mode": False
}

# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURE TEMPLATE (Extracted from Video)
# ═══════════════════════════════════════════════════════════════════════════════

STRUCTURE_TEMPLATE = {
    "sections": [
        {"type": "image", "key": "main_article_image", "alt": "White Chocolate Cranberry Blondies"},
        {"type": "intro", "key": "intro"},
        {"type": "h2", "text": "Why I Love This Recipe"},
        {"type": "numbered_list", "key": "why_i_love_this_recipe", "count": 4},
        {"type": "h2", "text": "Ingredients"},
        {"type": "h3", "text": "List of Required Ingredients"},
        {"type": "paragraph", "key": "ingredients_intro"},
        {"type": "bullet_list", "key": "ingredients_list", "count": 10},
        {"type": "paragraph", "key": "ingredients_outro"},
        {"type": "h3", "text": "Optional Ingredient Variations"},
        {"type": "paragraph", "key": "variations_intro"},
        {"type": "bullet_list", "key": "optional_variations", "count": 3},
        {"type": "paragraph", "key": "variations_outro"},
        {"type": "h3", "text": "Notes on Ingredient Quality"},
        {"type": "paragraph", "key": "ingredient_quality_notes"},
        {"type": "image", "key": "ingredient_image", "alt": "Ingredients for White Chocolate Cranberry Blondies"},
        {"type": "h2", "text": "Step-by-Step Instructions"},
        {"type": "h3", "text": "Prepping the Baking Pan"},
        {"type": "paragraph", "key": "prep_pan"},
        {"type": "h3", "text": "Mixing the Wet Ingredients"},
        {"type": "paragraph", "key": "mix_wet"},
        {"type": "h3", "text": "Combining the Dry Ingredients"},
        {"type": "paragraph", "key": "combine_dry"},
        {"type": "h3", "text": "Folding in the White Chocolate and Cranberries"},
        {"type": "paragraph", "key": "fold_mixins"},
        {"type": "h3", "text": "Baking and Cooling Process"},
        {"type": "paragraph", "key": "bake_cool"},
        {"type": "h2", "text": "Tips & Tricks"},
        {"type": "h3", "text": "How to Ensure Perfect Texture"},
        {"type": "paragraph", "key": "texture_intro"},
        {"type": "bullet_list", "key": "texture_tips", "count": 3},
        {"type": "h3", "text": "Common Mistakes to Avoid"},
        {"type": "paragraph", "key": "mistakes_intro"},
        {"type": "bullet_list", "key": "mistakes_list", "count": 3},
        {"type": "h3", "text": "Suggestions for Serving and Pairing"},
        {"type": "paragraph", "key": "serving_intro"},
        {"type": "bullet_list", "key": "serving_suggestions", "count": 3},
        {"type": "paragraph", "key": "serving_outro"},
        {"type": "pro_tips_box", "key": "pro_tips", "count": 4},
        {"type": "h2", "text": "Variations"},
        {"type": "h3", "text": "Nutty White Chocolate Cranberry Blondies"},
        {"type": "paragraph", "key": "variation_nutty"},
        {"type": "h3", "text": "Gluten-Free Version"},
        {"type": "paragraph", "key": "variation_gluten_free"},
        {"type": "h3", "text": "Alternative Flavor Combinations"},
        {"type": "paragraph", "key": "variation_flavors"},
        {"type": "h2", "text": "Storage Info"},
        {"type": "h3", "text": "Best Practices for Storing Blondies"},
        {"type": "paragraph", "key": "storage_best_practices"},
        {"type": "h3", "text": "How Long Do They Last?"},
        {"type": "paragraph", "key": "storage_duration"},
        {"type": "h3", "text": "Freezing Instructions"},
        {"type": "paragraph", "key": "storage_freezing"},
        {"type": "h2", "text": "FAQs"},
        {"type": "faq", "key": "faq_chocolate", "question": "Can I use regular chocolate instead of white chocolate?"},
        {"type": "faq", "key": "faq_cranberries", "question": "What can I substitute for cranberries?"},
        {"type": "faq", "key": "faq_chewy", "question": "How do I make blondies more chewy?"},
        {"type": "faq", "key": "faq_double", "question": "Can I double the recipe?"},
        {"type": "conclusion", "key": "conclusion"},
        {"type": "recipe_card", "key": "recipe"}
    ]
}

class ArticleGenerator:
    def __init__(self, config=None):
        self.config = config or CONFIG
        self.validate_config()
        from ai_client import create_ai_client
        self.client, self.model = create_ai_client(self.config)
        self.sections_content = {}
        
    def validate_config(self):
        """Validate CONFIG structure to prevent KeyError exceptions"""
        required_keys = ["title", "colors", "fonts", "layout", "components"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        # Validate colors
        color_keys = ["primary", "secondary", "background", "text_primary", "button_print", "button_pin"]
        for key in color_keys:
            if key not in self.config["colors"]:
                raise ValueError(f"Missing required color: {key}")
                
    def generate_content(self):
        """Generate all content using OpenAI API"""
        word_counts = self.config["structure_template"]["word_counts"]
        title = self.config["title"]
        
        schema = {
            "intro": f"string ~{word_counts['intro']} words",
            "why_i_love_this_recipe": f"array of 4 strings (BoldTitle: explanation) ~{word_counts['why_i_love_this_recipe']} total words",
            "ingredients_intro": "string ~15 words",
            "ingredients_list": "array of 10 strings",
            "ingredients_outro": "string ~15 words",
            "variations_intro": "string ~15 words",
            "optional_variations": "array of 3 strings",
            "variations_outro": "string ~10 words",
            "ingredient_quality_notes": f"string ~{word_counts['ingredient_quality_notes']} words",
            "prep_pan": "string ~40 words",
            "mix_wet": "string ~40 words",
            "combine_dry": "string ~40 words",
            "fold_mixins": "string ~30 words",
            "bake_cool": "string ~50 words",
            "texture_intro": "string ~10 words",
            "texture_tips": "array of 3 strings",
            "mistakes_intro": "string ~10 words",
            "mistakes_list": "array of 3 strings",
            "serving_intro": "string ~10 words",
            "serving_suggestions": "array of 3 strings",
            "serving_outro": "string ~15 words",
            "pro_tips": f"array of 4 strings (Title: description) ~{word_counts['pro_tips']} total words",
            "variation_nutty": "string ~50 words",
            "variation_gluten_free": "string ~40 words",
            "variation_flavors": "string ~50 words",
            "storage_best_practices": "string ~40 words",
            "storage_duration": "string ~30 words",
            "storage_freezing": "string ~40 words",
            "faq_chocolate": "string ~40 words",
            "faq_cranberries": "string ~40 words",
            "faq_chewy": "string ~40 words",
            "faq_double": "string ~40 words",
            "conclusion": f"string ~{word_counts['conclusion']} words"
        }

        system = (
            "You are a professional food blogger. Write engaging, SEO-friendly content. Be concise but warm. "
            "Output the full article as ONE JSON. Plain text only: no markdown (no ##, ###, ####, no ** or * for bold/italic, no - for bullets). "
            f"All content must be only about this recipe: {title}. Do not mention or use ingredients, steps, baking times, or dish names from any other recipe."
        )
        user = f"Generate the complete food blog article for '{title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        
        print("[*] Generating content with OpenAI (single JSON)...")
        from ai_client import ai_chat
        raw = ai_chat(self, user, max_tokens=5000, system=system)
        
        # Extract json
        text = (raw or "").strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m:
            text = m.group(1).strip()
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                data = json.loads(m.group())
            except Exception:
                data = {}
        else:
            try:
                data = json.loads(text)
            except Exception:
                data = {}

        if not data:
            print("[WARN] Failed to parse JSON, falling back to sequential generation...")
            return self._generate_content_sequential()
            
        print("[*] Generated content via single JSON.")
        
        for k in schema.keys():
            val = data.get(k)
            if isinstance(val, list):
                self.sections_content[k] = "\n".join(str(x) for x in val)
            else:
                self.sections_content[k] = str(val or "")
                
        return self.sections_content

    def _generate_content_sequential(self):
        word_counts = self.config["structure_template"]["word_counts"]
        title = self.config["title"]
        
        prompts = {
            "intro": f"Write an engaging intro paragraph for '{title}'. Approx {word_counts['intro']} words. SEO-friendly, enthusiastic tone.",
            "why_i_love_this_recipe": f"Generate 4 compelling reasons why someone would love this {title} recipe. Each reason should have a bold title and 1-2 sentences explanation. Total ~{word_counts['why_i_love_this_recipe']} words.",
            "ingredients_intro": f"Write a brief intro sentence about gathering ingredients for {title}. ~15 words.",
            "ingredients_list": f"List 10 ingredients for {title} with specific measurements (e.g., '1 cup unsalted butter, melted'). Format as simple list.",
            "ingredients_outro": f"Write one sentence about how these ingredients create a delicious treat. ~15 words.",
            "variations_intro": f"Write a sentence about optional add-ins for {title}. ~15 words.",
            "optional_variations": f"Generate 3 optional ingredient variations (Nuts, Coconut, Spices) with brief descriptions for {title}.",
            "variations_outro": f"Write an encouraging sentence about experimenting. ~10 words.",
            "ingredient_quality_notes": f"Write a paragraph about ingredient quality tips for {title}. ~{word_counts['ingredient_quality_notes']} words. Mention butter, chocolate, eggs.",
            "prep_pan": f"Write instructions for prepping the baking pan for {title}. Include oven temp 350°F (175°C), greasing 9x13 pan, parchment paper. ~40 words.",
            "mix_wet": f"Write instructions for mixing wet ingredients for {title}. Include melted butter, brown sugar, granulated sugar, eggs, vanilla. ~40 words.",
            "combine_dry": f"Write instructions for combining dry ingredients for {title}. Include flour, baking powder, salt. Mention not to overmix. ~40 words.",
            "fold_mixins": f"Write instructions for folding in white chocolate chips and dried cranberries for {title}. ~30 words.",
            "bake_cool": f"Write baking and cooling instructions for {title}. Include 25-30 minutes bake time, cooling 15 mins in pan. ~50 words.",
            "texture_intro": f"Write a sentence introducing texture tips. ~10 words.",
            "texture_tips": f"Generate 3 bullet points about ensuring perfect texture for {title} (melted butter, don't overmix, cool completely).",
            "mistakes_intro": f"Write a sentence introducing common mistakes. ~10 words.",
            "mistakes_list": f"Generate 3 bullet points about common mistakes to avoid when making {title} (cold eggs, overbaking, forgetting parchment).",
            "serving_intro": f"Write a sentence about serving suggestions. ~10 words.",
            "serving_suggestions": f"Generate 3 bullet points for serving {title} (vanilla ice cream, caramel drizzle, fresh fruit).",
            "serving_outro": f"Write a concluding sentence for the tips section. ~15 words.",
            "pro_tips": f"Generate 4 pro tips for perfect {title}. Include: Use High-Quality White Chocolate, Chill the Batter, Customize Mix-ins, Check for Doneness. Each with explanation. Total ~{word_counts['pro_tips']} words. Plain text only: no markdown (no ###, no **). Write each tip as 'Title: One or two sentences.'",
            "variation_nutty": f"Write instructions for making nutty version of {title}. Include walnuts or pecans. ~50 words.",
            "variation_gluten_free": f"Write instructions for gluten-free {title}. Mention gluten-free flour blend with xanthan gum. ~40 words.",
            "variation_flavors": f"Write about alternative flavors for {title}. Include orange zest, cinnamon, nutmeg. ~50 words.",
            "storage_best_practices": f"Write best practices for storing {title}. Include airtight container, room temperature, parchment between layers. ~40 words.",
            "storage_duration": f"Write how long {title} last. Include 1 week room temp, 2 weeks refrigerated. ~30 words.",
            "storage_freezing": f"Write freezing instructions for {title}. Include wrap individually, freezer bag, up to 3 months. ~40 words.",
            "faq_chocolate": f"Answer: Can I use regular chocolate instead of white chocolate for {title}? ~40 words. Mention dark/milk chocolate options.",
            "faq_cranberries": f"Answer: What can I substitute for cranberries in {title}? ~40 words. Mention cherries, raisins, dried apples.",
            "faq_chewy": f"Answer: How do I make {title} more chewy? ~40 words. Mention more brown sugar, don't overmix, slightly underbake.",
            "faq_double": f"Answer: Can I double the {title} recipe? ~40 words. Mention using 12x18 inch pan, longer baking time.",
            "conclusion": f"Write a warm conclusion paragraph for {title} blog post. ~{word_counts['conclusion']} words. Mention happy baking."
        }
        
        print("[*] Generating content sequentially with OpenAI...")
        
        from ai_client import ai_chat
        system = (
            "You are a professional food blogger. Write engaging, SEO-friendly content. Be concise but warm. "
            "Output plain text only: never use Markdown (no ##, ###, ####, no ** or * for bold/italic, no - for bullets). "
            f"All content must be only about this recipe: {title}. Do not mention or use ingredients, steps, baking times, or dish names from any other recipe."
        )
        for key, prompt in prompts.items():
            try:
                result = ai_chat(self, prompt, max_tokens=500, system=system)
                self.sections_content[key] = result or f"[Content for {key}]"
                print(f"  [OK] Generated: {key}")
            except Exception as e:
                print(f"  [WARN] Error generating {key}: {e}")
                self.sections_content[key] = f"[Content for {key}]"
                
        return self.sections_content
    
    def generate_recipe_data(self):
        """Generate structured recipe data. Use config.recipe when provided (e.g. from Domain A for B/C/D)."""
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": self.config["title"],
                "summary": "",
                "ingredients": [],
                "instructions": [],
                "prep_time": "15 min",
                "cook_time": "30 min",
                "total_time": "45 min",
                "servings": "16",
                "calories": "200",
                "course": "Dessert",
                "cuisine": "American",
                "chef_notes": ""
            }
            return {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        return {
            "name": self.config["title"],
            "summary": "Deliciously sweet blondies with white chocolate and tart cranberries.",
            "ingredients": [
                "1 cup unsalted butter, melted",
                "1 cup brown sugar, packed",
                "1/2 cup granulated sugar",
                "2 large eggs",
                "2 teaspoons vanilla extract",
                "2 cups all-purpose flour",
                "1 teaspoon baking powder",
                "1/2 teaspoon salt",
                "1 cup white chocolate chips",
                "1 cup dried cranberries"
            ],
            "instructions": [
                "Preheat your oven to 350°F (175°C). Grease and line a 9x13 inch baking pan with parchment paper, leaving some overhang for easy removal.",
                "In a large mixing bowl, combine the melted butter, brown sugar, and granulated sugar. Whisk until well blended.",
                "Add the eggs and vanilla extract to the sugar mixture and whisk until smooth and combined.",
                "In a separate bowl, sift together the flour, baking powder, and salt. Gradually add the dry ingredients to the wet ingredients, stirring until just combined - be careful not to overmix.",
                "Gently fold in the white chocolate chips and dried cranberries until evenly distributed throughout the batter.",
                "Pour the batter into the prepared baking pan, spreading it out evenly.",
                "Bake for approximately 25-30 minutes, or until the edges are golden brown and a toothpick inserted into the center comes out with a few moist crumbs (not wet batter).",
                "Remove from the oven and let cool in the pan for about 15 minutes before using the parchment paper to lift the blondies out onto a wire rack to cool completely.",
                "Once fully cooled, cut into squares or rectangles and enjoy!"
            ],
            "prep_time": "15 min",
            "cook_time": "30 min",
            "total_time": "45 min",
            "servings": "16",
            "calories": "200",
            "course": "Dessert",
            "cuisine": "American",
            "chef_notes": "Let cool completely before cutting for best texture."
        }
    
    def generate_seo_data(self):
        """Generate SEO and Pinterest metadata"""
        title = self.config["title"]
        return {
            "recipe_title_pin": f"Easy {title} Recipe - Perfect for Holidays!",
            "pinterest_title": f"Best {title} | Soft & Chewy",
            "pinterest_description": f"These irresistible {title} are the perfect blend of sweet and tart. Easy to make and perfect for any occasion!",
            "pinterest_keywords": "blondies, white chocolate, cranberry, dessert, baking, holiday treats, easy recipes, dessert bars",
            "focus_keyphrase": "white chocolate cranberry blondies",
            "meta_description": f"Make these irresistible {title}! Perfect blend of sweet white chocolate and tart cranberries. Easy recipe with simple ingredients.",
            "keyphrase_synonyms": "cranberry white chocolate bars, white chocolate blondies, cranberry dessert bars",
            "prompt_midjourney_main": f"Food photography of white chocolate cranberry blondies cut into squares on a white plate, golden brown edges, visible white chocolate chunks and red cranberries, soft natural lighting, shallow depth of field, rustic kitchen background --ar 16:9 --v 6.1",
            "prompt_midjourney_ingredients": f"Flat lay food photography of ingredients for white chocolate cranberry blondies on white marble: butter block, brown sugar in bowl, white chocolate chips, dried cranberries, eggs, flour, vanilla extract bottle, baking powder --ar 16:9 --v 6.1"
        }
    
    def generate_css(self):
        """Generate complete CSS based on config"""
        from generators.font_utils import font_family_css, build_font_import_url

        c = self.config["colors"]
        f = self.config["fonts"]
        l = self.config["layout"]
        comp = self.config["components"]
        import_url = build_font_import_url(f)
        body_font = font_family_css(f["body"]["family"], "sans-serif")
        heading_font = font_family_css(f["heading"]["family"], "serif")

        css = f'''/* Auto-generated CSS for {self.config["title"]} */
@import url('{import_url}');

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {body_font};
    font-size: {f["body"]["size"]};
    font-weight: {f["body"].get("weight", 400)};
    line-height: {f["body"]["line_height"]};
    color: {c["text_primary"]};
    background-color: {c["background"]};
}}

.article-container {{
    max-width: {l["max_width"]};
    margin: 0 auto;
    padding: {l["container_padding"]};
    background-color: {c["container_bg"]};
}}

.article-header.g4-header {{
    margin-bottom: {l["section_spacing"]};
}}
.article-header.g4-header .article-title {{
    font-family: {heading_font};
    font-size: {f["heading"]["sizes"]["h1"]};
    font-weight: 700;
    color: {c["text_primary"]};
    margin: 0 0 0.5rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 3px solid {c["primary"]};
    line-height: 1.2;
}}
.article-header.g4-header .article-byline-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
}}
.article-header.g4-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g4-header .byline-author {{ font-weight: 600; color: {c["text_primary"]}; }}
.article-header.g4-header .byline-date {{ font-size: 0.875rem; color: {c["text_secondary"]}; }}
.article-header.g4-header .byline-disclaimer {{ font-size: 0.8rem; color: {c["text_secondary"]}; font-style: italic; margin-top: 0.2rem; }}
.article-header.g4-header .byline-right {{ display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }}
.article-header.g4-header .recipe-meta-pills {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
.article-header.g4-header .recipe-meta-pills span {{
    background: {c["secondary"]};
    color: {c["text_primary"]};
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
    font-size: 0.85rem;
}}

/* Typography */
h1 {{
    font-family: {heading_font};
    font-size: {f["heading"]["sizes"]["h1"]};
    font-weight: 700;
    color: {c["text_primary"]};
    margin-bottom: 1.5rem;
    line-height: 1.2;
}}

h2 {{
    font-family: {heading_font};
    font-size: {f["heading"]["sizes"]["h2"]};
    font-weight: 700;
    color: {c["primary"]};
    margin-top: {l["section_spacing"]};
    margin-bottom: 1rem;
    line-height: 1.3;
}}

h3 {{
    font-family: {body_font};
    font-size: {f["heading"]["sizes"]["h3"]};
    font-weight: 600;
    color: {c["text_primary"]};
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    line-height: 1.4;
}}

p {{
    margin-bottom: {l["paragraph_spacing"]};
    color: {c["text_secondary"]};
}}

/* Lists */
.numbered-list {{
    list-style: none;
    padding: 0;
    margin: 1rem 0;
}}

.numbered-list li {{
    display: flex;
    align-items: flex-start;
    margin-bottom: {l["list_spacing"]};
    padding-left: 0;
}}

.numbered-list .number-circle {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: {comp["numbered_list"]["circle_size"]};
    height: {comp["numbered_list"]["circle_size"]};
    background-color: {comp["numbered_list"]["circle_bg"]};
    color: {comp["numbered_list"]["circle_color"]};
    border-radius: 50%;
    font-weight: 600;
    font-size: 0.9rem;
    margin-right: 1rem;
    flex-shrink: 0;
}}

.numbered-list .item-content {{
    flex: 1;
    padding-top: 0.2rem;
}}

.numbered-list .item-title {{
    font-weight: 600;
    color: {c["text_primary"]};
}}

.bullet-list {{
    list-style: none;
    padding-left: 0;
    margin: 1rem 0;
}}

.bullet-list li {{
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: {l["list_spacing"]};
    color: {c["text_secondary"]};
}}

.bullet-list li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0.6rem;
    width: 6px;
    height: 6px;
    background-color: {c["list_marker"]};
    border-radius: 50%;
}}

/* Images */
.article-image {{
    width: 100%;
    height: auto;
    border-radius: {l["border_radius"]};
    margin: 1.5rem 0;
    box-shadow: {l["box_shadow"]};
    display: block;
}}

/* Pro Tips Box */
.pro-tips-box {{
    background-color: {comp["pro_tips_box"]["bg_color"]};
    border-left: {comp["pro_tips_box"]["border_left"]} solid {comp["pro_tips_box"]["border_color"]};
    padding: {comp["pro_tips_box"]["padding"]};
    margin: 2rem 0;
    border-radius: 0 {l["border_radius"]} {l["border_radius"]} 0;
}}

.pro-tips-box h2 {{
    margin-top: 0;
    color: {c["primary"]};
    font-size: 1.5rem;
}}

.pro-tips-box .tip-item {{
    display: flex;
    align-items: flex-start;
    margin-bottom: 1rem;
}}

.pro-tips-box .tip-number {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background-color: {c["primary"]};
    color: white;
    border-radius: 50%;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 0.75rem;
    flex-shrink: 0;
}}

.pro-tips-box .tip-content {{
    flex: 1;
}}

.pro-tips-box .tip-title {{
    font-weight: 600;
    color: {c["text_primary"]};
    display: inline;
}}

/* FAQs */
.faq-section {{
    margin: 1.5rem 0;
}}

.faq-item {{
    margin-bottom: 1.5rem;
}}

.faq-question {{
    font-weight: 600;
    color: {c["text_primary"]};
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}}

.faq-answer {{
    color: {c["text_secondary"]};
    padding-left: 0;
}}

/* Recipe Card */
.recipe-card {{
    background-color: {comp["recipe_card"]["bg"]};
    border: {comp["recipe_card"]["border"]};
    border-radius: {comp["recipe_card"]["border_radius"]};
    padding: {comp["recipe_card"]["padding"]};
    margin-top: 2rem;
    box-shadow: {l["box_shadow"]};
}}

.recipe-card-header {{
    display: flex;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}}

.recipe-card-image {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid {c["border"]};
}}

.recipe-card-title {{
    flex: 1;
    min-width: 200px;
}}

.recipe-card-title h2 {{
    margin: 0;
    font-size: 1.5rem;
    color: {c["text_primary"]};
    font-family: {heading_font};
}}

.recipe-card-title p {{
    margin: 0.25rem 0 0 0;
    font-size: 0.9rem;
    color: {c["text_secondary"]};
}}

.recipe-meta {{
    display: flex;
    gap: 1.5rem;
    margin: 1rem 0;
    flex-wrap: wrap;
}}

.recipe-meta-item {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    color: {c["text_secondary"]};
}}

.recipe-meta-item .icon {{
    color: {comp["recipe_card"]["meta_icon_color"]};
    font-size: 1.1rem;
}}

.recipe-buttons {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin: 1.5rem 0;
}}

.btn {{
    padding: 0.875rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: all 0.2s;
    font-family: {body_font};
    font-size: 0.95rem;
}}

.btn-print {{
    background-color: {c["button_print"]};
    color: white;
}}

.btn-print:hover {{
    background-color: {c["button_hover_print"]};
}}

.btn-pin {{
    background-color: {c["button_pin"]};
    color: white;
}}

.btn-pin:hover {{
    background-color: {c["button_hover_pin"]};
}}

.recipe-columns {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-top: 1.5rem;
}}

@media (max-width: 600px) {{
    .recipe-columns {{
        grid-template-columns: 1fr;
    }}
}}

.recipe-ingredients h3,
.recipe-instructions h3 {{
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.ingredient-checklist {{
    list-style: none;
    padding: 0;
}}

.ingredient-checklist li {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid {c["border"]};
}}

.ingredient-checklist li:last-child {{
    border-bottom: none;
}}

.ingredient-checklist input[type="checkbox"] {{
    width: 18px;
    height: 18px;
    accent-color: {c["primary"]};
    cursor: pointer;
}}

.instruction-list {{
    list-style: none;
    counter-reset: instruction;
    padding: 0;
}}

.instruction-list li {{
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    align-items: flex-start;
}}

.instruction-list li::before {{
    counter-increment: instruction;
    content: counter(instruction);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background-color: {c["primary"]};
    color: white;
    border-radius: 50%;
    font-weight: 600;
    font-size: 0.85rem;
    flex-shrink: 0;
    margin-top: 0.1rem;
}}

.chef-notes {{
    background-color: {c["background"]};
    padding: 1rem;
    border-radius: 8px;
    margin-top: 1.5rem;
    border-left: 4px solid {c["primary"]};
}}

.chef-notes h4 {{
    margin: 0 0 0.5rem 0;
    color: {c["text_primary"]};
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.chef-notes p {{
    margin: 0;
    font-size: 0.95rem;
}}

.recipe-footer {{
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid {c["border"]};
    display: flex;
    justify-content: center;
    gap: 2rem;
    font-size: 0.9rem;
    color: {c["text_secondary"]};
}}

.recipe-footer strong {{
    color: {c["text_primary"]};
}}

/* Utility */
.intro-text {{
    font-size: 1.05rem;
    line-height: 1.8;
    color: {c["text_secondary"]};
    margin-bottom: 2rem;
}}
'''
        return css

    def _strip_markdown(self, text):
        """Remove ###, **, * so content is safe for HTML."""
        if not text or not isinstance(text, str):
            return text
        s = text.strip()
        s = re.sub(r'^#{1,6}\s*', '', s)
        s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'\*([^*]+)\*', r'\1', s)
        s = re.sub(r'^\s*-\s+', '', s, flags=re.MULTILINE)
        return s.strip()

    def _parse_pro_tips(self, content):
        """Split pro tips by ### or numbered lines; strip markdown. Returns list of {title, desc}."""
        if not content or not isinstance(content, str):
            return []
        raw = content.strip()
        tips = []
        # Split by ### (markdown headings)
        blocks = re.split(r'(?:^|\n)###\s*', raw)
        # If one block but it contains ### in the middle (e.g. no leading ###), split again
        if len(blocks) == 1 and '###' in blocks[0]:
            blocks = re.split(r'\n###\s*', blocks[0])
        if len(blocks) > 1:
            for block in blocks:
                block = block.strip()
                if not block:
                    continue
                lines = block.split('\n')
                title = self._strip_markdown(lines[0].strip())
                desc = self._strip_markdown('\n'.join(lines[1:]).strip()) if len(lines) > 1 else ""
                if title or desc:
                    tips.append({"title": title or "Pro Tip", "desc": desc})
        else:
            # Numbered lines: 1. **Title** desc or 1. Title: desc
            tips_parsed = re.findall(r'(\d+)[.:-]\s*\*\*(.*?)\*\*[:.-]?\s*(.*?)(?=\d+[.:-]\s*\*\*|\Z)', raw, re.DOTALL)
            if tips_parsed:
                for num, t, d in tips_parsed:
                    tips.append({"title": self._strip_markdown(t.strip()), "desc": self._strip_markdown(d.strip())})
            else:
                lines = [ln.strip() for ln in raw.split('\n') if ln.strip()]
                for i, line in enumerate(lines[:4], 1):
                    line = self._strip_markdown(line)
                    if ':' in line:
                        t, d = line.split(':', 1)
                        tips.append({"title": t.strip(), "desc": d.strip()})
                    else:
                        tips.append({"title": line[:60] + ("..." if len(line) > 60 else ""), "desc": ""})
        return tips[:8]

    def generate_html(self):
        """Generate complete HTML article"""
        c = self.config["colors"]
        s = self.sections_content
        r = self.generate_recipe_data()
        
        def get_content(key, default=""):
            raw = s.get(key, default)
            return self._strip_markdown(str(raw)) if raw else ""
        
        html_parts = []
        
        # Article header (title at top, byline, Pin, recipe meta)
        title = self.config["title"]
        html_parts.append(f'''<header class="article-header g4-header">
            <h1 class="article-title">{title}</h1>
            <div class="article-byline-row">
                <div class="byline-left">
                    <span class="byline-author">By <span class="article-author"></span></span>
                    <span class="byline-date">Published <span class="article-date"></span></span>
                    <p class="byline-disclaimer">This post may contain affiliate links.</p>
                </div>
                <div class="byline-right">
                    <button class="btn btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
                    <div class="recipe-meta-pills"><span>{r.get("prep_time", "")} prep</span><span>{r.get("cook_time", "")} cook</span><span>{r.get("servings", "")} servings</span></div>
                </div>
            </div>
        </header>''')
        
        # Hero Image
        html_parts.append(f'<img src="{self.config["images"]["main_article_image"]}" alt="White Chocolate Cranberry Blondies" class="article-image">')
        
        # Intro
        html_parts.append(f'<div class="intro-text">{get_content("intro")}</div>')
        
        # Why I Love This Recipe
        html_parts.append('<h2>Why I Love This Recipe</h2>')
        html_parts.append('<ol class="numbered-list">')
        reasons = get_content("why_i_love_this_recipe", "").split('\n')
        for i, reason in enumerate(reasons, 1):
            if reason.strip():
                # Extract bold title if present
                clean_reason = re.sub(r'\*\*|\*', '', reason).strip()
                if ':' in clean_reason:
                    title, desc = clean_reason.split(':', 1)
                    html_parts.append(f'<li><span class="number-circle">{i}</span><div class="item-content"><span class="item-title">{title.strip()}:</span>{desc.strip()}</div></li>')
                else:
                    html_parts.append(f'<li><span class="number-circle">{i}</span><div class="item-content">{clean_reason}</div></li>')
        html_parts.append('</ol>')
        
        # Ingredients
        html_parts.append('<h2>Ingredients</h2>')
        html_parts.append('<h3>List of Required Ingredients</h3>')
        html_parts.append(f'<p>{get_content("ingredients_intro")}</p>')
        
        html_parts.append('<ul class="bullet-list">')
        ingredients = get_content("ingredients_list", "").split('\n')
        for ing in ingredients:
            clean_ing = re.sub(r'^[-•]\s*', '', ing).strip()
            if clean_ing:
                html_parts.append(f'<li>{clean_ing}</li>')
        html_parts.append('</ul>')
        html_parts.append(f'<p>{get_content("ingredients_outro")}</p>')
        
        # Optional Variations
        html_parts.append('<h3>Optional Ingredient Variations</h3>')
        html_parts.append(f'<p>{get_content("variations_intro")}</p>')
        html_parts.append('<ul class="bullet-list">')
        variations = get_content("optional_variations", "").split('\n')
        for var in variations:
            clean_var = re.sub(r'^[-•]\s*', '', var).strip()
            if clean_var:
                html_parts.append(f'<li>{clean_var}</li>')
        html_parts.append('</ul>')
        html_parts.append(f'<p>{get_content("variations_outro")}</p>')
        
        # Ingredient Quality
        html_parts.append('<h3>Notes on Ingredient Quality</h3>')
        html_parts.append(f'<p>{get_content("ingredient_quality_notes")}</p>')
        html_parts.append(f'<img src="{self.config["images"]["ingredient_image"]}" alt="Ingredients for White Chocolate Cranberry Blondies" class="article-image">')
        
        # Instructions
        html_parts.append('<h2>Step-by-Step Instructions</h2>')
        
        sections = [
            ("Prepping the Baking Pan", "prep_pan"),
            ("Mixing the Wet Ingredients", "mix_wet"),
            ("Combining the Dry Ingredients", "combine_dry"),
            ("Folding in the White Chocolate and Cranberries", "fold_mixins"),
            ("Baking and Cooling Process", "bake_cool")
        ]
        
        for title, key in sections:
            html_parts.append(f'<h3>{title}</h3>')
            html_parts.append(f'<p>{get_content(key)}</p>')
        
        # Tips & Tricks
        html_parts.append('<h2>Tips & Tricks</h2>')
        
        html_parts.append('<h3>How to Ensure Perfect Texture</h3>')
        html_parts.append(f'<p>{get_content("texture_intro")}</p>')
        html_parts.append('<ul class="bullet-list">')
        tips = get_content("texture_tips", "").split('\n')
        for tip in tips:
            clean_tip = re.sub(r'^[-•]\s*', '', tip).strip()
            if clean_tip:
                html_parts.append(f'<li>{clean_tip}</li>')
        html_parts.append('</ul>')
        
        html_parts.append('<h3>Common Mistakes to Avoid</h3>')
        html_parts.append(f'<p>{get_content("mistakes_intro")}</p>')
        html_parts.append('<ul class="bullet-list">')
        mistakes = get_content("mistakes_list", "").split('\n')
        for mistake in mistakes:
            clean_mist = re.sub(r'^[-•]\s*', '', mistake).strip()
            if clean_mist:
                html_parts.append(f'<li>{clean_mist}</li>')
        html_parts.append('</ul>')
        
        html_parts.append('<h3>Suggestions for Serving and Pairing</h3>')
        html_parts.append(f'<p>{get_content("serving_intro")}</p>')
        html_parts.append('<ul class="bullet-list">')
        servings = get_content("serving_suggestions", "").split('\n')
        for serve in servings:
            clean_serve = re.sub(r'^[-•]\s*', '', serve).strip()
            if clean_serve:
                html_parts.append(f'<li>{clean_serve}</li>')
        html_parts.append('</ul>')
        html_parts.append(f'<p>{get_content("serving_outro")}</p>')
        
        # Pro Tips Box — parse into separate items, strip markdown
        html_parts.append('<div class="pro-tips-box">')
        html_parts.append('<h2>Pro Tips</h2>')
        pro_tips_list = self._parse_pro_tips(get_content("pro_tips", ""))
        if not pro_tips_list:
            pro_tips_list = [{"title": "Pro Tip", "desc": ""}]
        for i, tip in enumerate(pro_tips_list, 1):
            t_title = tip.get("title", "")
            t_desc = tip.get("desc", "")
            html_parts.append(f'<div class="tip-item"><span class="tip-number">{i}</span><div class="tip-content"><span class="tip-title">{t_title}:</span> {t_desc}</div></div>')
        html_parts.append('</div>')
        
        # Variations
        html_parts.append('<h2>Variations</h2>')
        html_parts.append('<h3>Nutty White Chocolate Cranberry Blondies</h3>')
        html_parts.append(f'<p>{get_content("variation_nutty")}</p>')
        html_parts.append('<h3>Gluten-Free Version</h3>')
        html_parts.append(f'<p>{get_content("variation_gluten_free")}</p>')
        html_parts.append('<h3>Alternative Flavor Combinations</h3>')
        html_parts.append(f'<p>{get_content("variation_flavors")}</p>')
        
        # Storage
        html_parts.append('<h2>Storage Info</h2>')
        html_parts.append('<h3>Best Practices for Storing Blondies</h3>')
        html_parts.append(f'<p>{get_content("storage_best_practices")}</p>')
        html_parts.append('<h3>How Long Do They Last?</h3>')
        html_parts.append(f'<p>{get_content("storage_duration")}</p>')
        html_parts.append('<h3>Freezing Instructions</h3>')
        html_parts.append(f'<p>{get_content("storage_freezing")}</p>')
        
        # FAQs
        html_parts.append('<h2>FAQs</h2>')
        html_parts.append('<div class="faq-section">')
        
        faqs = [
            ("Can I use regular chocolate instead of white chocolate?", "faq_chocolate"),
            ("What can I substitute for cranberries?", "faq_cranberries"),
            ("How do I make blondies more chewy?", "faq_chewy"),
            ("Can I double the recipe?", "faq_double")
        ]
        
        for question, key in faqs:
            html_parts.append('<div class="faq-item">')
            html_parts.append(f'<div class="faq-question">{question}</div>')
            html_parts.append(f'<div class="faq-answer">{get_content(key)}</div>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        # Conclusion
        html_parts.append(f'<p>{get_content("conclusion")}</p>')
        
        # Recipe Card
        html_parts.append('<div class="recipe-card">')
        html_parts.append('<div class="recipe-card-header">')
        html_parts.append(f'<img src="{self.config["images"]["recipe_card_image"]}" alt="{r["name"]}" class="recipe-card-image">')
        html_parts.append('<div class="recipe-card-title">')
        html_parts.append(f'<h2>{r["name"]}</h2>')
        html_parts.append(f'<p>{r["summary"]}</p>')
        html_parts.append('</div></div>')
        
        html_parts.append('<div class="recipe-meta">')
        html_parts.append(f'<div class="recipe-meta-item"><span class="icon">⏱</span> {r["prep_time"]} prep</div>')
        html_parts.append(f'<div class="recipe-meta-item"><span class="icon">🍳</span> {r["cook_time"]} cook</div>')
        html_parts.append(f'<div class="recipe-meta-item"><span class="icon">🍽</span> {r["servings"]} servings</div>')
        html_parts.append(f'<div class="recipe-meta-item"><span class="icon">⚡</span> {r["calories"]} cal</div>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="recipe-buttons">')
        html_parts.append('<button class="btn btn-print">Print Recipe</button>')
        html_parts.append('<button class="btn btn-pin" onclick="window.open(\'https://www.pinterest.com/pin/create/button/?url=\'+encodeURIComponent(window.location.href)+\'&media=\'+encodeURIComponent((document.querySelector(\'[data-pin-image]\')||{}).dataset?.pinImage||document.querySelector(\'.main-article-image img,.recipe-card-image img,article img\')?.src||\'\')+\'&description=\'+encodeURIComponent(document.title),\'pinterest\',\'width=750,height=600\')">Pin Recipe</button>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="recipe-columns">')
        html_parts.append('<div class="recipe-ingredients">')
        html_parts.append('<h3>📝 Ingredients</h3>')
        html_parts.append('<ul class="ingredient-checklist">')
        for ing in r["ingredients"]:
            html_parts.append(f'<li><input type="checkbox"> {ing}</li>')
        html_parts.append('</ul></div>')
        
        html_parts.append('<div class="recipe-instructions">')
        html_parts.append('<h3>📋 Instructions</h3>')
        html_parts.append('<ol class="instruction-list">')
        for inst in r["instructions"]:
            html_parts.append(f'<li>{inst}</li>')
        html_parts.append('</ol></div></div>')
        
        html_parts.append('<div class="chef-notes">')
        html_parts.append('<h4>👨‍🍳 Chef\'s Notes</h4>')
        html_parts.append(f'<p>{r["chef_notes"]}</p>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="recipe-footer">')
        html_parts.append(f'<div><strong>Course:</strong> {r["course"]}</div>')
        html_parts.append(f'<div><strong>Cuisine:</strong> {r["cuisine"]}</div>')
        html_parts.append('</div>')
        
        html_parts.append('</div>')  # End recipe card
        
        full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config["title"]}</title>
    <meta name="description" content="{self.generate_seo_data()["meta_description"]}">
    <link rel="stylesheet" href="css.css">
</head>
<body>
    <article class="article-container">
        {''.join(html_parts)}
    </article>
</body>
</html>'''
        
        return full_html
    
    def save_files(self, content_data, html_content, css_content):
        """Save all generated files to disk"""
        os.makedirs("output", exist_ok=True)
        
        # Save structure.json
        with open("output/structure.json", "w", encoding="utf-8") as f:
            json.dump(STRUCTURE_TEMPLATE, f, indent=2, ensure_ascii=False)
        
        # Save content.json
        with open("output/content.json", "w", encoding="utf-8") as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        # Save article.html
        with open("output/article.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Save css.css
        with open("output/css.css", "w", encoding="utf-8") as f:
            f.write(css_content)
        
        # Create placeholder.jpg if not exists
        placeholder_path = "output/placeholder.jpg"
        if not os.path.exists(placeholder_path):
            with open(placeholder_path, "wb") as f:
                f.write(b"")
        
        print("[OK] Files saved to ./output/")
    
    def _get_preview_content(self):
        """Placeholder content for template preview (no AI calls)."""
        title = self.config["title"]
        return {
            "intro": f"This is a sample intro paragraph for {title}. When you generate a full article, AI will write engaging content here.",
            "why_i_love_this_recipe": "1. Delicious Flavor Combination: The perfect blend of sweet and tart.\n2. Easy to Make: Simple ingredients, straightforward steps.\n3. Perfect for Any Occasion: Great for parties and family gatherings.\n4. Great for Meal Prep: Stores well and makes excellent leftovers.",
            "ingredients_intro": "Gather these ingredients before you begin.",
            "ingredients_list": "1 cup unsalted butter, melted\n1 cup brown sugar, packed\n1/2 cup granulated sugar\n2 large eggs\n2 teaspoons vanilla extract\n2 cups all-purpose flour\n1 teaspoon baking powder\n1/2 teaspoon salt\n1 cup white chocolate chips\n1 cup dried cranberries",
            "ingredients_outro": "These ingredients create a soft, chewy treat that bursts with flavor.",
            "variations_intro": "You can switch things up with optional add-ins.",
            "optional_variations": "- Nuts: walnuts or pecans\n- Coconut: shredded\n- Spices: cinnamon or nutmeg",
            "variations_outro": "Feel free to experiment to find your favorite mix!",
            "ingredient_quality_notes": "Using high-quality white chocolate chips, plump dried cranberries, fresh eggs, and unsalted butter makes a noticeable difference.",
            "prep_pan": "Preheat oven to 350°F. Grease and line a 9x13 inch baking pan with parchment paper, leaving overhang for easy removal.",
            "mix_wet": "In a large bowl, combine melted butter, brown sugar, granulated sugar, eggs, and vanilla. Whisk until smooth.",
            "combine_dry": "In a separate bowl, sift flour, baking powder, and salt. Gradually add to wet ingredients. Do not overmix.",
            "fold_mixins": "Gently fold in white chocolate chips and dried cranberries until evenly distributed.",
            "bake_cool": "Pour batter into prepared pan. Bake 25-30 minutes. Cool 15 minutes in pan, then transfer to wire rack.",
            "texture_intro": "For the best texture:",
            "texture_tips": "- Use melted butter (not cold)\n- Do not overmix the batter\n- Cool completely before cutting",
            "mistakes_intro": "Watch out for these:",
            "mistakes_list": "- Using cold eggs (use room temperature)\n- Overbaking (check early)\n- Forgetting parchment paper",
            "serving_intro": "Serve warm or at room temperature.",
            "serving_suggestions": "- Vanilla ice cream\n- Caramel drizzle\n- Fresh berries",
            "serving_outro": "Enjoy every bite!",
            "pro_tips": "1. Use High-Quality White Chocolate\n2. Chill the Batter\n3. Customize Your Mix-ins\n4. Check for Doneness",
            "variation_nutty": f"Add chopped walnuts or pecans (about 1 cup) for extra crunch.",
            "variation_gluten_free": "Swap flour for gluten-free blend with 1 tsp xanthan gum.",
            "variation_flavors": "Try orange zest, cinnamon, or nutmeg for a flavor twist.",
            "storage_best_practices": "Store in an airtight container. Use parchment between layers.",
            "storage_duration": "About 1 week at room temp, 2 weeks refrigerated.",
            "storage_freezing": "Cool completely, wrap individually, freeze in bags. Keeps up to 3 months.",
            "faq_chocolate": "Yes, dark or milk chocolate can be used but will alter the flavor.",
            "faq_cranberries": "Dried cherries, raisins, or chopped nuts work well as substitutes.",
            "faq_chewy": "Use more brown sugar, avoid overmixing, check doneness early.",
            "faq_double": "Yes. Use a 12x18 inch pan and bake 5-10 minutes longer.",
            "conclusion": f"Enjoy your homemade {title}! Happy baking!",
        }

    def run_preview(self):
        """Generate article template with placeholder content (no AI). For config preview."""
        self.validate_config()
        self.sections_content = self._get_preview_content()
        css_content = self.generate_css()
        html_content = self.generate_html()
        title = self.config["title"]
        slug = title.lower().replace(" ", "-").replace("'", "").replace('"', "")[:50]
        return {
            "title": title,
            "slug": slug,
            "article_html": html_content,
            "article_css": css_content,
        }

    def run(self, return_content_only=False):
        """Main execution method - API compatible"""
        print(f"[*] Generating article: {self.config['title']}")
        
        # Generate content
        self.generate_content()
        
        # Generate recipe data
        recipe_data = self.generate_recipe_data()
        
        # Generate SEO data
        seo_data = self.generate_seo_data()
        
        # Generate CSS
        css_content = self.generate_css()
        
        # Generate HTML
        html_content = self.generate_html()
        
        # Build content_data
        from ai_client import get_first_category
        cat = get_first_category(self.config)
        
        content_data = {
            "title": self.config["title"],
            "slug": self.config["title"].lower().replace(" ", "-"),
            "categorieId": str(cat.get("id", 1)),
            "categorie": cat.get("categorie", "General"),
            "sections": STRUCTURE_TEMPLATE["sections"],
            "article_html": html_content,
            "article_css": css_content,
            "prompt_used": "Video analysis of White Chocolate Cranberry Blondies article",
            "prompt_base": "Recipe article structure clone",
            "recipe": recipe_data,
            "recipe_title_pin": seo_data["recipe_title_pin"],
            "pinterest_title": seo_data["pinterest_title"],
            "pinterest_description": seo_data["pinterest_description"],
            "pinterest_keywords": seo_data["pinterest_keywords"],
            "focus_keyphrase": seo_data["focus_keyphrase"],
            "meta_description": seo_data["meta_description"],
            "keyphrase_synonyms": seo_data["keyphrase_synonyms"],
            "main_image": self.config["images"]["main_article_image"],
            "ingredient_image": self.config["images"]["ingredient_image"],
            "prompt_midjourney_main": seo_data["prompt_midjourney_main"],
            "prompt_midjourney_ingredients": seo_data["prompt_midjourney_ingredients"]
        }
        
        if return_content_only:
            return content_data
        
        self.save_files(content_data, html_content, css_content)
        print("[OK] Complete!")
        return content_data


if __name__ == "__main__":
    generator = ArticleGenerator()
    generator.run()