import os
import re
import json
import random
import string
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError

# Load environment variables
load_dotenv()

# CONFIGURATION - EXTRACTED FROM VIDEO ANALYSIS
CONFIG = {
    "title": "White Chocolate Cranberry Blondies",
    "categories_list": [{"id": 1, "categorie": "dessert"}, {"id": 2, "categorie": "baking"}],
    "colors": {
        "primary": "#E8663F",
        "secondary": "#333333",
        "accent": "#E8663F",
        "background": "#FFFFFF",
        "container_bg": "#FFF8F5",
        "border": "#F0E0D8",
        "text_primary": "#2C2C2C",
        "text_secondary": "#666666",
        "button_print": "#2C3E50",
        "button_pin": "#BD081C",
        "button_hover_print": "#1A252F",
        "button_hover_pin": "#9B0718",
        "link": "#E8663F",
        "list_marker": "#E8663F"
    },
    "fonts": {
        "heading": {
            "family": "Playfair Display",
            "weights": [400, 600, 700],
            "sizes": {"h1": "2.5rem", "h2": "1.875rem", "h3": "1.5rem"}
        },
        "body": {
            "family": "Inter",
            "weight": 400,
            "size": "1.125rem",
            "line_height": 1.7
        }
    },
    "layout": {
        "max_width": "800px",
        "section_spacing": "40px",
        "paragraph_spacing": "20px",
        "list_spacing": "12px",
        "container_padding": "40px",
        "border_radius": "8px",
        "box_shadow": "0 4px 20px rgba(0,0,0,0.08)"
    },
    "components": {
        "numbered_list": {
            "style": "circles",
            "circle_bg": "#E8663F",
            "circle_color": "#FFFFFF",
            "circle_size": "28px"
        },
        "bullet_list": {
            "style": "disc",
            "color": "#E8663F"
        },
        "pro_tips_box": {
            "bg_color": "#FFF0EB",
            "border_color": "#E8663F",
            "border_left": "4px solid #E8663F",
            "padding": "24px"
        },
        "recipe_card": {
            "bg": "#FFF8F5",
            "border": "1px solid #F0E0D8",
            "border_radius": "12px",
            "padding": "40px",
            "meta_icon_color": "#E8663F"
        }
    },
    "images": {
        "main_article_image": "placeholder.jpg",
        "ingredient_image": "placeholder.jpg",
        "recipe_card_image": "placeholder.jpg"
    },
    "structure_template": {
        "word_counts": {
            "intro": 50,
            "why_i_love_this_recipe": 80,
            "list_of_required_ingredients": 20,
            "optional_ingredient_variations": 40,
            "notes_on_ingredient_quality": 50,
            "prepping_the_baking_pan": 60,
            "mixing_the_wet_ingredients": 70,
            "combining_the_dry_ingredients": 70,
            "folding_in_the_white_chocolate": 60,
            "baking_and_cooling_process": 80,
            "how_to_ensure_perfect_texture": 60,
            "common_mistakes_to_avoid": 60,
            "suggestions_for_serving": 70,
            "tips_conclusion": 40,
            "pro_tips": 120,
            "nutty_variation": 60,
            "gluten_free_variation": 50,
            "alternative_flavor": 50,
            "storage_best_practices": 50,
            "how_long_last": 40,
            "freezing_instructions": 50,
            "faq_chocolate": 40,
            "faq_cranberries": 40,
            "faq_chewy": 40,
            "faq_double": 40,
            "final_conclusion": 80
        }
    },
    "dark_mode": False
}

STRUCTURE = [
    {"type": "image", "subtype": "hero"},
    {"type": "intro", "key": "intro"},
    {"type": "h2", "text": "Why I Love This Recipe"},
    {"type": "numbered_list", "count": 4, "key": "why_i_love_this_recipe"},
    {"type": "h2", "text": "Ingredients"},
    {"type": "h3", "text": "List of Required Ingredients"},
    {"type": "bullet_list", "count": 10, "key": "list_of_required_ingredients", "intro": "To make these tasty white chocolate cranberry blondies, gather these key ingredients:"},
    {"type": "paragraph", "key": "ingredients_description"},
    {"type": "h3", "text": "Optional Ingredient Variations"},
    {"type": "bullet_list", "count": 3, "key": "optional_ingredient_variations", "intro": "You can switch things up by adding a few fun ingredients:"},
    {"type": "paragraph", "key": "optional_conclusion"},
    {"type": "h3", "text": "Notes on Ingredient Quality"},
    {"type": "paragraph", "key": "notes_on_ingredient_quality"},
    {"type": "image", "subtype": "ingredients"},
    {"type": "h2", "text": "Step-by-Step Instructions"},
    {"type": "h3", "text": "Prepping the Baking Pan"},
    {"type": "paragraph", "key": "prepping_the_baking_pan"},
    {"type": "h3", "text": "Mixing the Wet Ingredients"},
    {"type": "paragraph", "key": "mixing_the_wet_ingredients"},
    {"type": "h3", "text": "Combining the Dry Ingredients"},
    {"type": "paragraph", "key": "combining_the_dry_ingredients"},
    {"type": "h3", "text": "Folding in the White Chocolate and Cranberries"},
    {"type": "paragraph", "key": "folding_in_the_white_chocolate"},
    {"type": "h3", "text": "Baking and Cooling Process"},
    {"type": "paragraph", "key": "baking_and_cooling_process"},
    {"type": "h2", "text": "Tips & Tricks"},
    {"type": "h3", "text": "How to Ensure Perfect Texture"},
    {"type": "bullet_list", "count": 3, "key": "how_to_ensure_perfect_texture", "intro": "To get the best texture in your blondies, follow these steps:"},
    {"type": "h3", "text": "Common Mistakes to Avoid"},
    {"type": "bullet_list", "count": 3, "key": "common_mistakes_to_avoid", "intro": "Watch out for these common mistakes:"},
    {"type": "h3", "text": "Suggestions for Serving and Pairing"},
    {"type": "paragraph", "key": "suggestions_for_serving_intro"},
    {"type": "bullet_list", "count": 3, "key": "suggestions_for_serving", "intro": "Pair them with:"},
    {"type": "paragraph", "key": "tips_conclusion"},
    {"type": "pro_tips_box", "count": 4, "key": "pro_tips", "title": "Pro Tips"},
    {"type": "h2", "text": "Variations"},
    {"type": "h3", "text": "Nutty White Chocolate Cranberry Blondies"},
    {"type": "paragraph", "key": "nutty_variation"},
    {"type": "h3", "text": "Gluten-Free Version"},
    {"type": "paragraph", "key": "gluten_free_variation"},
    {"type": "h3", "text": "Alternative Flavor Combinations"},
    {"type": "paragraph", "key": "alternative_flavor"},
    {"type": "h2", "text": "Storage Info"},
    {"type": "h3", "text": "Best Practices for Storing Blondies"},
    {"type": "paragraph", "key": "storage_best_practices"},
    {"type": "h3", "text": "How Long Do They Last?"},
    {"type": "paragraph", "key": "how_long_last"},
    {"type": "h3", "text": "Freezing Instructions"},
    {"type": "paragraph", "key": "freezing_instructions"},
    {"type": "h2", "text": "FAQs"},
    {"type": "faq", "question": "Can I use regular chocolate instead of white chocolate?", "key": "faq_chocolate"},
    {"type": "faq", "question": "What can I substitute for cranberries?", "key": "faq_cranberries"},
    {"type": "faq", "question": "How do I make blondies more chewy?", "key": "faq_chewy"},
    {"type": "faq", "question": "Can I double the recipe?", "key": "faq_double"},
    {"type": "conclusion", "key": "final_conclusion"}
]

RECIPE_TEMPLATE = {
    "name": "White Chocolate Cranberry Blondies",
    "summary": "Deliciously sweet blondies with white chocolate and tart cranberries.",
    "prep_time": "15 min",
    "cook_time": "30 min",
    "total_time": "45 min",
    "servings": "16",
    "calories": "200 cal",
    "course": "Dessert",
    "cuisine": "American",
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
        "In a separate bowl, sift together the flour, baking powder, and salt. Gradually add the dry ingredients to the wet ingredients, stirring until just combined – be careful not to overmix.",
        "Gently fold in the white chocolate chips and dried cranberries until evenly distributed throughout the batter.",
        "Pour the batter into the prepared baking pan, spreading it out evenly.",
        "Bake for approximately 25-30 minutes, or until the edges are golden brown and a toothpick inserted into the center comes out with a few moist crumbs (not wet batter).",
        "Remove from the oven and let cool in the pan for about 15 minutes before using the parchment paper to lift the blondies out onto a wire rack to cool completely.",
        "Once fully cooled, cut into squares or rectangles and enjoy!"
    ]
}

class ArticleGenerator:
    def __init__(self):
        from ai_client import create_ai_client
        self.config = CONFIG
        self.client, self.model = create_ai_client(CONFIG)
        self.validate_config()
        
    def validate_config(self):
        required_keys = ["title", "colors", "fonts", "layout", "components", "structure_template"]
        for key in required_keys:
            if key not in CONFIG:
                raise KeyError(f"Missing required CONFIG key: {key}")
                
    def generate_slug(self, title):
        return title.lower().replace(" ", "-").replace("'", "").replace('"', "")[:50]
    
    def generate_content_with_openai(self, prompt, max_tokens=500):
        from ai_client import ai_chat
        title = CONFIG.get("title", "this recipe")
        system = (
            "You are a professional food blogger and recipe writer. Write engaging, SEO-optimized content that sounds natural and human. "
            "Never mention word counts or writing instructions. "
            "Output plain text only: no Markdown (no ##, ###, ####, no ** or * for bold/italic). "
            f"All content must be only about this recipe: {title}. Do not mention or use ingredients, steps, or dish names from any other recipe."
        )
        result = ai_chat(self, prompt, max_tokens=max_tokens, system=system)
        return result or "Content generation failed. Please try again."
    
    def generate_sections(self):
        from ai_client import ai_chat
        
        word_counts = CONFIG["structure_template"]["word_counts"]
        title = self.config["title"]
        
        schema = {
            "intro": f"string ~{word_counts['intro']} words",
            "why_i_love_this_recipe": f"array of 4 strings ~{word_counts['why_i_love_this_recipe']} total words",
            "ingredients_description": "string 1 sentence",
            "optional_conclusion": "string 1 sentence",
            "notes_on_ingredient_quality": f"string ~{word_counts['notes_on_ingredient_quality']} words",
            "prepping_the_baking_pan": f"string ~{word_counts['prepping_the_baking_pan']} words",
            "mixing_the_wet_ingredients": f"string ~{word_counts['mixing_the_wet_ingredients']} words",
            "combining_the_dry_ingredients": f"string ~{word_counts['combining_the_dry_ingredients']} words",
            "folding_in_the_white_chocolate": f"string ~{word_counts['folding_in_the_white_chocolate']} words",
            "baking_and_cooling_process": f"string ~{word_counts['baking_and_cooling_process']} words",
            "suggestions_for_serving_intro": "string 1 sentence",
            "tips_conclusion": "string 1 sentence",
            "pro_tips": f"array of 4 strings (Title: description) ~{word_counts['pro_tips']} total words",
            "nutty_variation": f"string ~{word_counts['nutty_variation']} words",
            "gluten_free_variation": f"string ~{word_counts['gluten_free_variation']} words",
            "alternative_flavor": f"string ~{word_counts['alternative_flavor']} words",
            "storage_best_practices": f"string ~{word_counts['storage_best_practices']} words",
            "how_long_last": f"string ~{word_counts['how_long_last']} words",
            "freezing_instructions": f"string ~{word_counts['freezing_instructions']} words",
            "faq_chocolate": f"string ~{word_counts['faq_chocolate']} words",
            "faq_cranberries": f"string ~{word_counts['faq_cranberries']} words",
            "faq_chewy": f"string ~{word_counts['faq_chewy']} words",
            "faq_double": f"string ~{word_counts['faq_double']} words",
            "final_conclusion": f"string ~{word_counts['final_conclusion']} words"
        }

        system = (
            "You are a professional food blogger and recipe writer. Write engaging, SEO-optimized content that sounds natural and human. "
            "Never mention word counts or writing instructions. "
            "Output the full article as ONE JSON. Plain text only: no markdown. "
            f"All content must be only about this recipe: {title}. Do not mention or use ingredients, steps, or dish names from any other recipe."
        )
        user = f"Generate the complete food blog article for '{title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        
        print("[*] Generating all sections in a single JSON API call...")
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
            return self._generate_sections_sequential()
            
        print("[*] Generated content via single JSON.")
        
        sections_content = {}
        for k in schema.keys():
            val = data.get(k)
            if isinstance(val, list):
                sections_content[k] = "\n".join(str(x) for x in val)
            else:
                sections_content[k] = str(val or "")
                
        return sections_content

    def _generate_sections_sequential(self):
        sections_content = {}
        word_counts = CONFIG["structure_template"]["word_counts"]
        
        prompts = {
            "intro": f"Write an engaging intro paragraph (about {word_counts['intro']} words) for a recipe article about White Chocolate Cranberry Blondies. Mention they are the perfect blend of sweet and tart, simple ingredients, and appeal to both baking pros and beginners. End with 'Let's dive into the sweetness that awaits!'",
            "why_i_love_this_recipe": f"Write 4 short compelling reasons why someone would love this White Chocolate Cranberry Blondies recipe. Each reason should be 1-2 sentences. Format as: 1) Delicious Flavor Combination: [text] 2) Easy to Make: [text] 3) Perfect for Any Occasion: [text] 4) Great for Meal Prep: [text]. Total around {word_counts['why_i_love_this_recipe']} words.",
            "ingredients_description": "Write one sentence describing how these ingredients create a soft, chewy treat that bursts with flavor.",
            "optional_conclusion": "Write one encouraging sentence: 'Feel free to experiment to find your favorite mix!'",
            "notes_on_ingredient_quality": f"Write a paragraph (about {word_counts['notes_on_ingredient_quality']} words) about ingredient quality for blondies. Mention using good white chocolate chips, plump dried cranberries, fresh eggs, and unsalted butter.",
            "prepping_the_baking_pan": f"Write instructions (about {word_counts['prepping_the_baking_pan']} words) for prepping a 9x13 inch baking pan. Include preheating to 350°F, greasing, lining with parchment paper with overhang.",
            "mixing_the_wet_ingredients": f"Write instructions (about {word_counts['mixing_the_wet_ingredients']} words) for mixing wet ingredients: melted butter, brown sugar, granulated sugar, eggs, and vanilla extract.",
            "combining_the_dry_ingredients": f"Write instructions (about {word_counts['combining_the_dry_ingredients']} words) for combining dry ingredients. Include sifting flour, baking powder, salt, and gradually adding to wet mix. Warn not to overmix.",
            "folding_in_the_white_chocolate": f"Write instructions (about {word_counts['folding_in_the_white_chocolate']} words) for folding in white chocolate chips and dried cranberries. Mention even distribution.",
            "baking_and_cooling_process": f"Write instructions (about {word_counts['baking_and_cooling_process']} words) for baking and cooling. Include pouring batter, baking 25-30 minutes, checking with toothpick, cooling in pan 15 minutes, then transferring to wire rack.",
            "suggestions_for_serving_intro": "Write one sentence: Serve your blondies warm or at room temperature. They taste great on their own.",
            "tips_conclusion": "Write a closing sentence for the tips section: 'These tips will help you create the perfect white chocolate cranberry blondies. Enjoy every bite!'",
            "pro_tips": f"Write 4 professional baking tips (about {word_counts['pro_tips']} words total) for perfect blondies: 1) Use High-Quality White Chocolate, 2) Chill the Batter, 3) Customize Your Mix-ins, 4) Check for Doneness. Each tip: one short title then a colon then one or two sentences. Plain text only: no markdown (no ###, no **).",
            "nutty_variation": f"Write a paragraph (about {word_counts['nutty_variation']} words) about adding nuts (walnuts or pecans) to the blondies. Mention chopping coarsely and using about 1 cup.",
            "gluten_free_variation": f"Write a paragraph (about {word_counts['gluten_free_variation']} words) about making gluten-free blondies. Mention swapping flour for gluten-free blend with xanthan gum.",
            "alternative_flavor": f"Write a paragraph (about {word_counts['alternative_flavor']} words) about flavor variations. Mention orange zest, cinnamon, nutmeg, and being creative.",
            "storage_best_practices": f"Write a paragraph (about {word_counts['storage_best_practices']} words) about storing blondies. Mention airtight container, parchment paper between layers, cool dry place.",
            "how_long_last": f"Write a paragraph (about {word_counts['how_long_last']} words) about shelf life. Mention 1 week at room temperature, 2 weeks refrigerated, checking for spoilage.",
            "freezing_instructions": f"Write instructions (about {word_counts['freezing_instructions']} words) for freezing blondies. Mention cooling completely, cutting, wrapping in plastic, freezer bags, lasting 3 months, thawing at room temperature.",
            "faq_chocolate": f"Answer this FAQ in about {word_counts['faq_chocolate']} words: Can I use regular chocolate instead of white chocolate? Yes, mention dark or milk chocolate can be used but will alter flavor.",
            "faq_cranberries": f"Answer this FAQ in about {word_counts['faq_cranberries']} words: What can I substitute for cranberries? Suggest dried cherries, raisins, or chopped nuts.",
            "faq_chewy": f"Answer this FAQ in about {word_counts['faq_chewy']} words: How do I make blondies more chewy? Mention using more brown sugar, not overmixing, and checking early.",
            "faq_double": f"Answer this FAQ in about {word_counts['faq_double']} words: Can I double the recipe? Yes, use 12x18 inch pan, bake longer, check edges.",
            "final_conclusion": f"Write a concluding paragraph (about {word_counts['final_conclusion']} words) summarizing the article. Mention key steps, ingredients, tips, and end with 'Happy baking!'"
        }
        
        for key, prompt in prompts.items():
            print(f"Generating content: {key}...")
            content = self.generate_content_with_openai(prompt)
            sections_content[key] = content
            
        return sections_content
    
    def build_numbered_list_items(self, content):
        lines = content.split('\n')
        items = []
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                clean_line = line.lstrip('1234567890.-)• ').strip()
                if clean_line:
                    if ':' in clean_line:
                        title, desc = clean_line.split(':', 1)
                        items.append({"title": title.strip(), "description": desc.strip()})
                    else:
                        items.append({"title": "", "description": clean_line})
        if not items:
            items = [{"title": "", "description": content}]
        return items
    
    def _strip_markdown(self, text):
        """Remove ###, **, * so content is safe for HTML. No raw markdown in output."""
        if not text or not isinstance(text, str):
            return text
        s = text.strip()
        s = re.sub(r'^#{1,6}\s*', '', s)
        s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'\*([^*]+)\*', r'\1', s)
        s = re.sub(r'^\s*-\s+', '', s, flags=re.MULTILINE)
        return s.strip()

    def build_pro_tips(self, content):
        if not (content and isinstance(content, str)):
            return [{"title": "Pro Tip", "description": ""}]
        raw = content.strip()
        tips = []

        # Split by ### (at start or after newline) so each block is one tip
        blocks = re.split(r'(?:^|\n)###\s*', raw)
        # If we got only one block but it contains ### in the middle, split again (e.g. content had no leading ###)
        if len(blocks) == 1 and '###' in blocks[0]:
            blocks = re.split(r'\n###\s*', blocks[0])
        if len(blocks) > 1:
            for i, block in enumerate(blocks):
                block = block.strip()
                if not block:
                    continue
                lines = block.split('\n')
                title = self._strip_markdown(lines[0].strip())
                desc = self._strip_markdown('\n'.join(lines[1:]).strip()) if len(lines) > 1 else ""
                if title or desc:
                    tips.append({"title": title or "Pro Tip", "description": desc})
        else:
            # No ###: try numbered lines (1. Title: desc or 1) Title: desc)
            lines = raw.split('\n')
            current_tip = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line[0].isdigit() and ('.' in line or ')' in line):
                    if current_tip:
                        tips.append(current_tip)
                    parts = re.split(r'[.)]\s*', line, 1)
                    title_desc = (parts[1].strip() if len(parts) > 1 else line)
                    if ':' in title_desc:
                        t, d = title_desc.split(':', 1)
                        current_tip = {"title": self._strip_markdown(t.strip()), "description": self._strip_markdown(d.strip())}
                    else:
                        current_tip = {"title": self._strip_markdown(title_desc), "description": ""}
                elif current_tip:
                    current_tip["description"] += " " + self._strip_markdown(line)
            if current_tip:
                tips.append(current_tip)

        if not tips:
            # Last resort: one tip with full content, always strip markdown so ### never appears
            tips = [{"title": "Pro Tip", "description": self._strip_markdown(raw)}]
        return tips
    
    def create_content_json(self, sections_content):
        slug = self.generate_slug(CONFIG["title"])
        existing = CONFIG.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            recipe_val = {**RECIPE_TEMPLATE, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        else:
            recipe_val = RECIPE_TEMPLATE
        content_data = {
            "title": CONFIG["title"],
            "slug": slug,
            "categorieId": "1",
            "categorie": "dessert",
            "sections": [],
            "article_html": "",
            "article_css": "",
            "prompt_used": "Video structure analysis of White Chocolate Cranberry Blondies recipe page",
            "prompt_base": "Generate SEO-optimized recipe content",
            "recipe": recipe_val,
            "recipe_title_pin": "White Chocolate Cranberry Blondies Recipe - Easy & Delicious!",
            "pinterest_title": "White Chocolate Cranberry Blondies",
            "pinterest_description": "These irresistible white chocolate cranberry blondies are the perfect blend of sweet and tart. Easy to make with simple ingredients! #blondies #dessert #recipe",
            "pinterest_keywords": "blondies, white chocolate, cranberry, dessert recipe, baking, easy dessert, cookie bars, sweet treats",
            "focus_keyphrase": "white chocolate cranberry blondies",
            "meta_description": "Make these irresistible white chocolate cranberry blondies! Perfect blend of sweet and tart with simple ingredients. Great for any occasion.",
            "keyphrase_synonyms": "cranberry blondies, white chocolate bars, cranberry dessert bars",
            "main_image": CONFIG["images"]["main_article_image"],
            "ingredient_image": CONFIG["images"]["ingredient_image"],
            "prompt_midjourney_main": "A beautiful food photography shot of white chocolate cranberry blondies cut into squares on a white marble surface. Golden brown edges, visible chunks of white chocolate and dried cranberries. Soft natural lighting, shallow depth of field, top-down angle --v 6.1",
            "prompt_midjourney_ingredients": "Flat lay food photography of baking ingredients for blondies: butter, brown sugar, flour, eggs, vanilla extract, white chocolate chips, dried cranberries in white ceramic bowls on white background. Clean, bright, organized --v 6.1"
        }
        
        for section in STRUCTURE:
            section_data = {"type": section["type"]}
            
            if section["type"] == "h2":
                section_data["content"] = section["text"]
            elif section["type"] == "h3":
                section_data["content"] = section["text"]
            elif section["type"] == "intro":
                section_data["content"] = self._strip_markdown(sections_content.get("intro", ""))
            elif section["type"] == "paragraph":
                key = section.get("key", "")
                section_data["content"] = self._strip_markdown(sections_content.get(key, ""))
            elif section["type"] == "numbered_list":
                content = self._strip_markdown(sections_content.get(section["key"], ""))
                items = self.build_numbered_list_items(content)
                section_data["items"] = [{"title": self._strip_markdown(i.get("title", "")), "description": self._strip_markdown(i.get("description", ""))} for i in items]
                section_data["intro"] = ""
            elif section["type"] == "bullet_list":
                content = self._strip_markdown(sections_content.get(section["key"], ""))
                items = self.build_numbered_list_items(content)
                section_data["items"] = [{"title": self._strip_markdown(i.get("title", "")), "description": self._strip_markdown(i.get("description", ""))} for i in items]
                section_data["intro"] = self._strip_markdown(section.get("intro", ""))
            elif section["type"] == "pro_tips_box":
                content = sections_content.get(section["key"], "")
                section_data["title"] = section.get("title", "Pro Tips")
                section_data["tips"] = self.build_pro_tips(content)
            elif section["type"] == "faq":
                key = section.get("key", "")
                section_data["question"] = section.get("question", "")
                section_data["answer"] = self._strip_markdown(sections_content.get(key, ""))
            elif section["type"] == "conclusion":
                key = section.get("key", "")
                section_data["content"] = self._strip_markdown(sections_content.get(key, ""))
            elif section["type"] == "image":
                if section["subtype"] == "hero":
                    section_data["src"] = CONFIG["images"]["main_article_image"]
                    section_data["alt"] = CONFIG["title"]
                elif section["subtype"] == "ingredients":
                    section_data["src"] = CONFIG["images"]["ingredient_image"]
                    section_data["alt"] = "Ingredients for " + CONFIG["title"]
                    
            content_data["sections"].append(section_data)
            
        return content_data
    
    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url

        colors = CONFIG["colors"]
        fonts = CONFIG["fonts"]
        layout = CONFIG["layout"]
        components = CONFIG["components"]
        import_url = build_font_import_url(fonts)
        body_font = font_family_css(fonts["body"]["family"], "sans-serif")
        heading_font = font_family_css(fonts["heading"]["family"], "serif")

        css = f"""
@import url('{import_url}');

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {body_font};
    font-weight: {fonts["body"].get("weight", 400)};
    font-size: {fonts["body"]["size"]};
    line-height: {fonts["body"]["line_height"]};
    color: {colors["text_primary"]};
    background-color: {colors["background"]};
}}

.article-container {{
    max-width: {layout["max_width"]};
    margin: 0 auto;
    padding: {layout["container_padding"]};
}}

.article-header.g2-header {{
    margin-bottom: {layout["section_spacing"]};
    padding-bottom: 1.5rem;
    border-bottom: 2px solid {colors["border"]};
}}
.article-header.g2-header .article-title {{
    font-family: {heading_font};
    font-size: 2rem;
    font-weight: 700;
    color: {colors["text_primary"]};
    margin: 0 0 1rem 0;
    line-height: 1.25;
}}
.article-header.g2-header .article-byline-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
}}
.article-header.g2-header .byline-left {{ display: flex; flex-direction: column; gap: 0.2rem; }}
.article-header.g2-header .byline-author {{ font-weight: 600; color: {colors["text_primary"]}; }}
.article-header.g2-header .byline-date {{ font-size: 0.875rem; color: {colors["text_secondary"]}; }}
.article-header.g2-header .byline-disclaimer {{ font-size: 0.8rem; color: {colors["text_secondary"]}; font-style: italic; margin-top: 0.25rem; }}
.article-header.g2-header .byline-right {{ display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; }}
.article-header.g2-header .recipe-meta-inline {{ display: flex; gap: 1rem; font-size: 0.9rem; color: {colors["text_secondary"]}; }}

.hero-image {{
    width: 100%;
    height: auto;
    border-radius: {layout["border_radius"]};
    margin-bottom: {layout["section_spacing"]};
    box-shadow: {layout["box_shadow"]};
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: {heading_font};
    font-weight: 600;
    line-height: 1.3;
    margin-bottom: 20px;
    color: {colors["text_primary"]};
}}

h1 {{
    font-size: {fonts["heading"]["sizes"]["h1"]};
    margin-bottom: 30px;
}}

h2 {{
    font-size: {fonts["heading"]["sizes"]["h2"]};
    color: {colors["primary"]};
    margin-top: {layout["section_spacing"]};
}}

h3 {{
    font-size: {fonts["heading"]["sizes"]["h3"]};
    color: {colors["text_primary"]};
    margin-top: 30px;
}}

p {{
    margin-bottom: {layout["paragraph_spacing"]};
    color: {colors["text_secondary"]};
}}

.intro {{
    font-size: 1.125rem;
    line-height: 1.8;
    margin-bottom: 30px;
}}

.numbered-list {{
    list-style: none;
    padding: 0;
    margin: 20px 0;
    counter-reset: item;
}}

.numbered-list li {{
    position: relative;
    padding-left: 50px;
    margin-bottom: {layout["list_spacing"]};
    min-height: {components["numbered_list"]["circle_size"]};
}}

.numbered-list li::before {{
    content: counter(item);
    counter-increment: item;
    position: absolute;
    left: 0;
    top: 0;
    width: {components["numbered_list"]["circle_size"]};
    height: {components["numbered_list"]["circle_size"]};
    background-color: {components["numbered_list"]["circle_bg"]};
    color: {components["numbered_list"]["circle_color"]};
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
    font-family: {body_font};
}}

.numbered-list li strong {{
    color: {colors["text_primary"]};
    font-weight: 600;
}}

.bullet-list {{
    list-style: none;
    padding: 0;
    margin: 20px 0;
}}

.bullet-list li {{
    position: relative;
    padding-left: 25px;
    margin-bottom: {layout["list_spacing"]};
}}

.bullet-list li::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 10px;
    width: 8px;
    height: 8px;
    background-color: {components["bullet_list"]["color"]};
    border-radius: 50%;
}}

.ingredients-flatlay {{
    width: 100%;
    height: auto;
    border-radius: {layout["border_radius"]};
    margin: 30px 0;
    box-shadow: {layout["box_shadow"]};
}}

.pro-tips-box {{
    background-color: {components["pro_tips_box"]["bg_color"]};
    border-left: {components["pro_tips_box"]["border_left"]};
    border-radius: 0 {layout["border_radius"]} {layout["border_radius"]} 0;
    padding: {components["pro_tips_box"]["padding"]};
    margin: 30px 0;
}}

.pro-tips-box h3 {{
    color: {colors["primary"]};
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 1.5rem;
}}

.pro-tip-item {{
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
    align-items: flex-start;
}}

.pro-tip-number {{
    min-width: {components["numbered_list"]["circle_size"]};
    height: {components["numbered_list"]["circle_size"]};
    background-color: {components["numbered_list"]["circle_bg"]};
    color: {components["numbered_list"]["circle_color"]};
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
    flex-shrink: 0;
}}

.pro-tip-content strong {{
    display: block;
    color: {colors["text_primary"]};
    margin-bottom: 5px;
    font-weight: 600;
}}

.pro-tip-content p {{
    margin: 0;
    color: {colors["text_secondary"]};
    font-size: 1rem;
    line-height: 1.6;
}}

.faq-section {{
    margin-top: 30px;
}}

.faq-item {{
    margin-bottom: 25px;
}}

.faq-item h3 {{
    font-size: 1.25rem;
    color: {colors["text_primary"]};
    margin-bottom: 10px;
    margin-top: 0;
}}

.faq-item p {{
    margin: 0;
    color: {colors["text_secondary"]};
}}

.conclusion {{
    margin: 30px 0;
    font-size: 1.125rem;
    line-height: 1.8;
}}

.recipe-card {{
    background-color: {components["recipe_card"]["bg"]};
    border: {components["recipe_card"]["border"]};
    border-radius: {components["recipe_card"]["border_radius"]};
    padding: {components["recipe_card"]["padding"]};
    margin-top: 40px;
    box-shadow: {layout["box_shadow"]};
}}

.recipe-header {{
    display: flex;
    gap: 30px;
    margin-bottom: 30px;
    align-items: center;
}}

.recipe-image {{
    width: 120px;
    height: 120px;
    object-fit: cover;
    border-radius: 50%;
    flex-shrink: 0;
}}

.recipe-title-section h2 {{
    margin: 0 0 10px 0;
    color: {colors["text_primary"]};
    font-size: 1.75rem;
}}

.recipe-summary {{
    color: {colors["text_secondary"]};
    margin: 0;
    font-size: 1rem;
}}

.recipe-meta {{
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
    flex-wrap: wrap;
}}

.meta-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    color: {colors["text_secondary"]};
    font-size: 0.95rem;
}}

.meta-icon {{
    color: {components["recipe_card"]["meta_icon_color"]};
    font-weight: 600;
}}

.recipe-buttons {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin-bottom: 30px;
}}

.btn {{
    padding: 15px 20px;
    border: none;
    border-radius: 6px;
    font-family: {body_font};
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.3s ease;
}}

.btn-print {{
    background-color: {colors["button_print"]};
    color: white;
}}

.btn-print:hover {{
    background-color: {colors["button_hover_print"]};
}}

.btn-pin {{
    background-color: {colors["button_pin"]};
    color: white;
}}

.btn-pin:hover {{
    background-color: {colors["button_hover_pin"]};
}}

.recipe-content {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    margin-top: 30px;
}}

@media (max-width: 768px) {{
    .recipe-content {{
        grid-template-columns: 1fr;
    }}
    .recipe-header {{
        flex-direction: column;
        text-align: center;
    }}
}}

.recipe-section h3 {{
    margin-top: 0;
    margin-bottom: 20px;
    color: {colors["text_primary"]};
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    gap: 10px;
}}

.recipe-section h3::before {{
    content: '';
    width: 24px;
    height: 24px;
    background-color: {colors["primary"]};
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'/%3E%3C/svg%3E") no-repeat center;
    mask-size: contain;
}}

.ingredients-list {{
    list-style: none;
    padding: 0;
}}

.ingredients-list li {{
    padding: 10px 0;
    border-bottom: 1px solid {colors["border"]};
    display: flex;
    align-items: flex-start;
    gap: 10px;
}}

.ingredients-list li:last-child {{
    border-bottom: none;
}}

.ingredients-list input[type="checkbox"] {{
    margin-top: 5px;
    cursor: pointer;
}}

.ingredients-list label {{
    cursor: pointer;
    flex: 1;
    color: {colors["text_secondary"]};
}}

.instructions-list {{
    list-style: none;
    counter-reset: step;
    padding: 0;
}}

.instructions-list li {{
    position: relative;
    padding-left: 45px;
    margin-bottom: 20px;
    counter-increment: step;
}}

.instructions-list li::before {{
    content: counter(step);
    position: absolute;
    left: 0;
    top: 0;
    width: 30px;
    height: 30px;
    background-color: {colors["primary"]};
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
}}

.chef-notes {{
    background-color: {colors["background"]};
    border: 1px solid {colors["border"]};
    border-radius: {layout["border_radius"]};
    padding: 20px;
    margin-top: 30px;
}}

.chef-notes h4 {{
    margin: 0 0 10px 0;
    color: {colors["text_primary"]};
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.chef-notes p {{
    margin: 0;
    color: {colors["text_secondary"]};
    font-size: 0.95rem;
}}

.recipe-footer {{
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid {colors["border"]};
    display: flex;
    justify-content: center;
    gap: 40px;
    font-size: 0.9rem;
    color: {colors["text_secondary"]};
}}

.recipe-footer strong {{
    color: {colors["text_primary"]};
}}

@media print {{
    .btn-print, .btn-pin {{
        display: none;
    }}
}}
"""
        return css.strip()
    
    def generate_html(self, content_data):
        colors = CONFIG["colors"]
        fonts = CONFIG["fonts"]
        
        html_parts = []
        
        html_parts.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{content_data["meta_description"]}">
    <title>{content_data["title"]}</title>
    <link rel="stylesheet" href="css.css">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <article class="article-container">
        <header class="article-header g2-header">
            <h1 class="article-title">{content_data["title"]}</h1>
            <div class="article-byline-row">
                <div class="byline-left">
                    <span class="byline-author">By <span class="article-author"></span></span>
                    <span class="byline-date">Published <span class="article-date"></span></span>
                    <p class="byline-disclaimer">This post may contain affiliate links.</p>
                </div>
                <div class="byline-right">
                    <button class="btn btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
                    <div class="recipe-meta-inline"><span>{(content_data.get("recipe") or {}).get("prep_time", "")} prep</span><span>{(content_data.get("recipe") or {}).get("cook_time", "")} cook</span><span>{(content_data.get("recipe") or {}).get("servings", "")} servings</span></div>
                </div>
            </div>
        </header>''')
        
        for section in content_data["sections"]:
            section_type = section["type"]
            
            if section_type == "image":
                if section.get("subtype") == "hero":
                    html_parts.append(f'''
        <img src="{section.get("src", "placeholder.jpg")}" alt="{section.get("alt", "")}" class="hero-image">''')
                elif section.get("subtype") == "ingredients":
                    html_parts.append(f'''
        <img src="{section.get("src", "placeholder.jpg")}" alt="{section.get("alt", "")}" class="ingredients-flatlay">''')
                    
            elif section_type == "intro":
                html_parts.append(f'''
        <p class="intro">{section.get("content", "")}</p>''')
                
            elif section_type == "h2":
                html_parts.append(f'''
        <h2>{section.get("content", "")}</h2>''')
                
            elif section_type == "h3":
                html_parts.append(f'''
        <h3>{section.get("content", "")}</h3>''')
                
            elif section_type == "paragraph":
                html_parts.append(f'''
        <p>{section.get("content", "")}</p>''')
                
            elif section_type == "numbered_list":
                items = section.get("items", [])
                html_parts.append('        <ol class="numbered-list">')
                for item in items:
                    title = item.get("title", "")
                    desc = item.get("description", "")
                    if title:
                        html_parts.append(f'            <li><strong>{title}:</strong> {desc}</li>')
                    else:
                        html_parts.append(f'            <li>{desc}</li>')
                html_parts.append('        </ol>')
                
            elif section_type == "bullet_list":
                intro = section.get("intro", "")
                items = section.get("items", [])
                if intro:
                    html_parts.append(f'''
        <p>{intro}</p>''')
                html_parts.append('        <ul class="bullet-list">')
                for item in items:
                    title = item.get("title", "")
                    desc = item.get("description", "")
                    if title:
                        html_parts.append(f'            <li><strong>{title}:</strong> {desc}</li>')
                    else:
                        html_parts.append(f'            <li>{desc}</li>')
                html_parts.append('        </ul>')
                
            elif section_type == "pro_tips_box":
                title = section.get("title", "Pro Tips")
                tips = section.get("tips", [])
                html_parts.append(f'''
        <div class="pro-tips-box">
            <h3>{title}</h3>''')
                for i, tip in enumerate(tips, 1):
                    tip_title = tip.get("title", "")
                    tip_desc = tip.get("description", "")
                    html_parts.append(f'''            <div class="pro-tip-item">
                <span class="pro-tip-number">{i}</span>
                <div class="pro-tip-content">
                    <strong>{tip_title}</strong>
                    <p>{tip_desc}</p>
                </div>
            </div>''')
                html_parts.append('        </div>')
                
            elif section_type == "faq":
                question = section.get("question", "")
                answer = section.get("answer", "")
                html_parts.append(f'''
        <div class="faq-item">
            <h3>{question}</h3>
            <p>{answer}</p>
        </div>''')
                
            elif section_type == "conclusion":
                html_parts.append(f'''
        <p class="conclusion">{section.get("content", "")}</p>''')
        
        recipe = content_data.get("recipe", {})
        html_parts.append(self._generate_recipe_card(recipe, content_data))
        
        html_parts.append('''
    </article>
</body>
</html>''')
        
        return '\n'.join(html_parts)
    
    def _generate_recipe_card(self, recipe, content_data):
        ingredients_html = []
        for i, ing in enumerate(recipe.get("ingredients", [])):
            ingredients_html.append(f'''
                    <li>
                        <input type="checkbox" id="ing{i}" name="ing{i}">
                        <label for="ing{i}">{ing}</label>
                    </li>''')
        
        instructions_html = []
        for step in recipe.get("instructions", []):
            instructions_html.append(f'''
                    <li>{step}</li>''')
        
        return f'''
        <div class="recipe-card">
            <div class="recipe-header">
                <img src="{content_data.get("main_image", "placeholder.jpg")}" alt="{recipe.get("name", "")}" class="recipe-image">
                <div class="recipe-title-section">
                    <h2>{recipe.get("name", "")}</h2>
                    <p class="recipe-summary">{recipe.get("summary", "")}</p>
                </div>
            </div>
            
            <div class="recipe-meta">
                <div class="meta-item">
                    <span class="meta-icon">⏱</span>
                    <span>{recipe.get("prep_time", "")} prep</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">🍳</span>
                    <span>{recipe.get("cook_time", "")} cook</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">👥</span>
                    <span>{recipe.get("servings", "")} servings</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">⚡</span>
                    <span>{recipe.get("calories", "")}</span>
                </div>
            </div>
            
            <div class="recipe-buttons">
                <button class="btn btn-print" onclick="window.print()">Print Recipe</button>
                <button class="btn btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
            </div>
            
            <div class="recipe-content">
                <div class="recipe-section">
                    <h3>Ingredients</h3>
                    <ul class="ingredients-list">
                        {''.join(ingredients_html)}
                    </ul>
                </div>
                
                <div class="recipe-section">
                    <h3>Instructions</h3>
                    <ol class="instructions-list">
                        {''.join(instructions_html)}
                    </ol>
                </div>
            </div>
            
            <div class="chef-notes">
                <h4>ℹ Chef's Notes</h4>
                <p>Let cool completely before cutting for best texture.</p>
            </div>
            
            <div class="recipe-footer">
                <div><strong>Course:</strong> {recipe.get("course", "")}</div>
                <div><strong>Cuisine:</strong> {recipe.get("cuisine", "")}</div>
            </div>
        </div>'''
    
    def save_files(self, content_data, html_content, css_content):
        output_dir = Path("white-chocolate-cranberry-blondies")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "content.json", "w", encoding="utf-8") as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
            
        with open(output_dir / "structure.json", "w", encoding="utf-8") as f:
            structure_output = {
                "word_counts": CONFIG["structure_template"]["word_counts"],
                "structure": STRUCTURE
            }
            json.dump(structure_output, f, indent=2, ensure_ascii=False)
            
        with open(output_dir / "article.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        with open(output_dir / "css.css", "w", encoding="utf-8") as f:
            f.write(css_content)
            
        with open(output_dir / "generator.py", "w", encoding="utf-8") as f:
            f.write(open(__file__, "r", encoding="utf-8").read())
            
        placeholder_path = output_dir / "placeholder.jpg"
        if not placeholder_path.exists():
            with open(placeholder_path, "wb") as f:
                f.write(b"")
                
        print(f"[OK] Files generated in: {output_dir.absolute()}")
        print("Files created:")
        print("  - content.json")
        print("  - structure.json")
        print("  - article.html")
        print("  - css.css")
        print("  - generator.py")
        print("  - placeholder.jpg")
    
    def _get_preview_content(self):
        """Placeholder content for template preview (no AI calls)."""
        title = CONFIG["title"]
        return {
            "intro": f"This is a sample intro paragraph for {title}. When you generate a full article, AI will write engaging content here.",
            "why_i_love_this_recipe": "1) Delicious Flavor Combination: The perfect blend of sweet and tart.\n2) Easy to Make: Simple ingredients, straightforward steps.\n3) Perfect for Any Occasion: Great for parties and family gatherings.\n4) Great for Meal Prep: Stores well and makes excellent leftovers.",
            "ingredients_description": "These ingredients create a soft, chewy treat that bursts with flavor.",
            "optional_conclusion": "Feel free to experiment to find your favorite mix!",
            "notes_on_ingredient_quality": "Using high-quality white chocolate chips, plump dried cranberries, fresh eggs, and unsalted butter makes a noticeable difference in the final result.",
            "prepping_the_baking_pan": "Preheat your oven to 350°F. Grease and line a 9x13 inch baking pan with parchment paper, leaving some overhang for easy removal.",
            "mixing_the_wet_ingredients": "In a large bowl, combine melted butter, brown sugar, granulated sugar, eggs, and vanilla. Whisk until smooth and combined.",
            "combining_the_dry_ingredients": "In a separate bowl, sift flour, baking powder, and salt. Gradually add to wet ingredients, stirring until just combined. Do not overmix.",
            "folding_in_the_white_chocolate": "Gently fold in white chocolate chips and dried cranberries until evenly distributed throughout the batter.",
            "baking_and_cooling_process": "Pour batter into the prepared pan. Bake 25-30 minutes. Cool in pan 15 minutes, then transfer to wire rack to cool completely.",
            "suggestions_for_serving_intro": "Serve your blondies warm or at room temperature. They taste great on their own.",
            "tips_conclusion": "These tips will help you create the perfect blondies. Enjoy every bite!",
            "pro_tips": "1. Use High-Quality White Chocolate: Premium chips melt smoothly.\n2. Chill the Batter: 30 minutes rest improves texture.\n3. Customize Your Mix-ins: Try nuts or different dried fruits.\n4. Check for Doneness: Toothpick should have a few moist crumbs.",
            "nutty_variation": f"Add chopped walnuts or pecans (about 1 cup) for extra crunch. Fold in with the chocolate and cranberries.",
            "gluten_free_variation": "Swap all-purpose flour for a gluten-free blend with 1 tsp xanthan gum.",
            "alternative_flavor": "Try orange zest, cinnamon, or nutmeg for a flavor twist.",
            "storage_best_practices": "Store in an airtight container. Use parchment between layers. Keep in a cool, dry place.",
            "how_long_last": "About 1 week at room temperature, 2 weeks refrigerated.",
            "freezing_instructions": "Cool completely, wrap individually in plastic, place in freezer bag. Keeps up to 3 months. Thaw at room temperature.",
            "faq_chocolate": "Yes, dark or milk chocolate can be used but will alter the flavor profile.",
            "faq_cranberries": "Dried cherries, raisins, or chopped nuts work well as substitutes.",
            "faq_chewy": "Use more brown sugar, avoid overmixing, and check for doneness a few minutes early.",
            "faq_double": "Yes. Use a 12x18 inch pan and bake 5-10 minutes longer.",
            "final_conclusion": f"Enjoy your homemade {title}! Happy baking!",
            "how_to_ensure_perfect_texture": "- Use melted (not cold) butter\n- Do not overmix the batter\n- Cool completely before cutting",
            "common_mistakes_to_avoid": "- Using cold eggs (use room temp)\n- Overbaking (check early)\n- Forgetting parchment paper",
            "suggestions_for_serving": "- Vanilla ice cream\n- Caramel drizzle\n- Fresh berries",
            "list_of_required_ingredients": "1 cup butter\n1 cup brown sugar\n1/2 cup granulated sugar\n2 eggs\n2 tsp vanilla\n2 cups flour\n1 tsp baking powder\n1/2 tsp salt\n1 cup white chocolate chips\n1 cup dried cranberries",
            "optional_ingredient_variations": "- Nuts: walnuts or pecans\n- Coconut: shredded\n- Spices: cinnamon or nutmeg",
        }

    def run_preview(self):
        """Generate article template with placeholder content (no AI). For config preview."""
        self.validate_config()
        sections_content = self._get_preview_content()
        content_data = self.create_content_json(sections_content)
        css_content = self.generate_css()
        html_content = self.generate_html(content_data)
        return {
            "title": CONFIG["title"],
            "slug": self.generate_slug(CONFIG["title"]),
            "article_html": html_content,
            "article_css": css_content,
        }

    def run(self, return_content_only=False):
        print("[*] Analyzing video structure... [DONE BY AI]")
        print("[*] Generating content with OpenAI...")
        
        try:
            sections_content = self.generate_sections()
            content_data = self.create_content_json(sections_content)
            
            print("[*] Generating CSS...")
            css_content = self.generate_css()
            
            print("[*] Building HTML...")
            html_content = self.generate_html(content_data)
            
            content_data["article_html"] = html_content
            content_data["article_css"] = css_content
            
            if return_content_only:
                return content_data
            
            print("[*] Saving files...")
            self.save_files(content_data, html_content, css_content)
            
            print("[OK] Complete!")
            
        except Exception as e:
            print(f"[ERROR] {e}")
            raise

if __name__ == "__main__":
    generator = ArticleGenerator()
    generator.run()