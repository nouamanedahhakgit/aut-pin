#!/usr/bin/env python3
"""
Production-Ready Recipe Article Generator
Clones the exact structure and design from video analysis.
"""

import os
import json
import re
import sys
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _safe_print(*args, **kwargs):
    """Print without crashing on Windows cp1252 consoles when text has emoji."""
    text = " ".join(str(a) for a in args)
    end = kwargs.get("end", "\n")
    stream = kwargs.get("file", sys.stdout)
    try:
        stream.write(text + end)
    except UnicodeEncodeError:
        enc = getattr(stream, "encoding", None) or "utf-8"
        safe = text.encode(enc, errors="replace").decode(enc, errors="replace")
        stream.write(safe + end)

CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dessert"}],
    "colors": {
    "primary": "#6C8AE4",
    "secondary": "#9C6ADE",
    "accent": "#6C8AE4",
    "background": "#FFFFFF",
    "container_bg": "#F5F7FF",
    "border": "#E2E8FF",
    "text_primary": "#2D2D2D",
    "text_secondary": "#5A5A5A",
    "button_print": "#1A1A2E",
    "button_pin": "#E60023",
    "button_hover_print": "#2D2D44",
    "button_hover_pin": "#FF1A3C",
    "link": "#6C8AE4",
    "list_marker": "#6C8AE4"
}
,
    "fonts": {
        "heading": {
            "family": "Playfair Display",
            "weights": [400, 600, 700],
            "sizes": {"h1": "2.5rem", "h2": "1.875rem", "h3": "1.5rem"}
        },
        "body": {
            "family": "Inter",
            "weight": 400,
            "size": "1rem",
            "line_height": 1.7
        }
    },
    "layout": {
        "max_width": "800px",
        "section_spacing": "3rem",
        "paragraph_spacing": "1.5rem",
        "list_spacing": "1rem",
        "container_padding": "2rem",
        "border_radius": "12px",
        "box_shadow": "0 4px 20px rgba(0,0,0,0.08)"
    },
    "components": {
        "numbered_list": {
            "style": "circle",
            "circle_bg": "#F4A261",
            "circle_color": "#FFFFFF",
            "circle_size": "32px"
        },
        "bullet_list": {
            "style": "disc",
            "color": "#F4A261"
        },
        "pro_tips_box": {
            "bg_color": "#FFF5F0",
            "border_color": "#FFE8E0",
            "border_left": "4px solid #F4A261",
            "padding": "2rem"
        },
        "recipe_card": {
            "bg": "#FFFCFA",
            "border": "2px solid #FFE8E0",
            "border_radius": "16px",
            "padding": "2rem",
            "meta_icon_color": "#F4A261"
        }
    },
    "images": {
        "main_article_image": "",
        "ingredient_image": "",
        "recipe_card_image": ""
    },
    "structure_template": {
        "word_counts": {
            "intro": 65,
            "why_i_love_item_1": 20,
            "why_i_love_item_2": 20,
            "why_i_love_item_3": 20,
            "why_i_love_item_4": 20,
            "ingredients_intro": 15,
            "ingredient_quality_notes": 50,
            "instructions_step_1": 30,
            "instructions_step_2": 35,
            "instructions_step_3": 40,
            "instructions_step_4": 35,
            "instructions_step_5": 45,
            "tips_texture": 40,
            "tips_mistakes": 45,
            "serving_intro": 15,
            "pro_tips_item_1": 25,
            "pro_tips_item_2": 25,
            "pro_tips_item_3": 25,
            "pro_tips_item_4": 25,
            "variation_nutty": 60,
            "variation_gluten_free": 50,
            "variation_flavor": 55,
            "storage_best_practices": 50,
            "storage_duration": 40,
            "storage_freezing": 45,
            "faq_1": 45,
            "faq_2": 40,
            "faq_3": 40,
            "faq_4": 45,
            "conclusion": 75
        }
    },
    "dark_mode": False
}

RECIPE_TEMPLATE = {
    "prep_time": "15 min",
    "cook_time": "30 min",
    "total_time": "45 min",
    "servings": 16,
    "calories": 200,
    "course": "Dessert",
    "cuisine": "American"
}


class RecipeArticleGenerator:
    """Generates complete recipe articles with exact video-matched design."""
    
    def __init__(self, config_override: Optional[Dict] = None):
        self.config = CONFIG.copy()
        if config_override:
            self._deep_update(self.config, config_override)
        from ai_client import create_ai_client
        self.client, self.model = create_ai_client(self.config)
        self.content_data = {}
        
    def _deep_update(self, d: Dict, u: Dict) -> Dict:
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d
    
    def _validate_config(self):
        required_keys = ["title", "colors", "fonts", "layout", "components"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        if not self.config["title"]:
            raise ValueError("CONFIG['title'] is required")
    
    def _generate_slug(self, title: str) -> str:
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:80]

    def _get_first_category(self) -> Dict[str, Any]:
        """Safely extract first category from categories_list. Handles list of dicts, list of strings, or JSON string."""
        cl = self.config.get("categories_list")
        if isinstance(cl, str):
            try:
                cl = json.loads(cl) if cl.strip() else []
            except json.JSONDecodeError:
                cl = []
        if not isinstance(cl, list) or not cl:
            return {"id": 1, "categorie": "dessert"}
        first = cl[0]
        if isinstance(first, dict):
            return {"id": first.get("id", 1), "categorie": str(first.get("categorie", "dessert") or "dessert")}
        return {"id": 1, "categorie": str(first) if first else "dessert"}
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown from AI output so it renders as plain text in HTML. No ###, ####, **, *, leading -."""
        if not text or not isinstance(text, str):
            return text
        s = text.strip()
        s = re.sub(r'^#{1,6}\s*', '', s)
        s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'\*([^*]+)\*', r'\1', s)
        s = re.sub(r'^\s*-\s+', '', s, flags=re.MULTILINE)
        s = re.sub(r'\n\s*-\s+', '\n', s)
        return s.strip()

    def _generate_content_with_openai(self, prompt: str, max_tokens: int = 500) -> str:
        from ai_client import ai_chat
        system = (
            "You are a professional food blogger who writes engaging, SEO-optimized recipe content. "
            "Output plain text only. Never use Markdown: no ##, ###, ####, no ** or * for bold/italic, no - for bullets. "
            "Your text will be inserted into HTML as-is; any markdown will appear literally and break the page."
        )
        user = prompt.rstrip() + " Plain text only: no markdown symbols, no ## or ### or ####, no ** or *."
        raw = ai_chat(self, user, max_tokens=max_tokens, system=system)
        return self._strip_markdown(raw) if raw else ""

    def generate_all_content(self) -> Dict[str, Any]:
        """Generate all article content in ONE API call (optimized for speed)."""
        from ai_client import ai_chat, extract_json_robust

        title = self.config["title"]
        wc = self.config["structure_template"]["word_counts"]

        schema = {
            "intro": f"string, ~{wc['intro']} words",
            "why_i_love": "array of 4 strings",
            "ingredients_intro": f"string, ~{wc['ingredients_intro']} words",
            "ingredient_quality": f"string, ~{wc['ingredient_quality_notes']} words",
            "recipe": "object: name, summary, ingredients (string[]), instructions (string[]), prep_time, cook_time, total_time, servings, calories, course, cuisine",
            "tips_texture": f"string, ~{wc['tips_texture']} words",
            "tips_mistakes": f"string, ~{wc['tips_mistakes']} words",
            "serving": f"string, ~{wc.get('serving_intro', 15)} words",
            "pro_tips": "array of 4 strings",
            "faqs": "array of 4 strings (each Q&A as one string, e.g. 'Can I freeze? Yes, store in...')",
            "conclusion": f"string, ~{wc['conclusion']} words",
            "meta_description": "string, 120-140 chars",
            "focus_keyphrase": "string, 3-5 words",
            "prompt_midjourney_main": "string, food photo prompt ending with --v 6.1",
            "prompt_midjourney_ingredients": "string, flat-lay ingredients prompt ending with --v 6.1",
        }

        system = (
            "You are a professional food blogger. Generate the FULL recipe article as ONE JSON object. "
            "Output ONLY valid JSON: no markdown fences (no ```), no extra text before or after. "
            "All string values: plain text only, no ##, ###, **, or * markdown. "
            "All content must be ONLY about the recipe title given."
        )
        user = (
            f"Generate the complete recipe article for '{title}' as a JSON object with these exact keys:\n"
            f"{json.dumps(schema, indent=2)}\n\n"
            f"All content must be only about {title}. Return ONLY the raw JSON object—no ```json, no explanation."
        )

        _safe_print("[*] Generating all sections in a single JSON API call...")
        raw = ai_chat(self, user, max_tokens=5000, system=system)
        data = extract_json_robust(raw)
        
        if not data:
            _safe_print("[WARN] Failed to parse JSON, falling back to sequential generation...")
            return self._generate_all_content_sequential()

        _safe_print("[*] Generated content via single JSON.")

        sections_content = {
            "intro": self._strip_markdown(str(data.get("intro", ""))),
            "why_i_love": [self._strip_markdown(str(x)) for x in (data.get("why_i_love") or [])[:4]],
            "ingredients_intro": self._strip_markdown(str(data.get("ingredients_intro", ""))),
            "ingredient_quality": self._strip_markdown(str(data.get("ingredient_quality", ""))),
            "tips_texture": self._strip_markdown(str(data.get("tips_texture", ""))),
            "tips_mistakes": self._strip_markdown(str(data.get("tips_mistakes", ""))),
            "serving": self._strip_markdown(str(data.get("serving", ""))),
            "pro_tips": [self._strip_markdown(str(x)) for x in (data.get("pro_tips") or [])[:4]],
            "faqs": [self._strip_markdown(str(x)) for x in (data.get("faqs") or [])[:4]],
            "conclusion": self._strip_markdown(str(data.get("conclusion", ""))),
        }

        recipe = data.get("recipe") or {}
        if isinstance(recipe, dict) and (recipe.get("ingredients") or recipe.get("instructions")):
            self.content_data["_ai_recipe"] = recipe
        self.content_data["_ai_seo"] = {
            "meta_description": (str(data.get("meta_description", "")) or "")[:140],
            "focus_keyphrase": str(data.get("focus_keyphrase", "")),
        }
        self.content_data["_ai_midjourney"] = {
            "prompt_midjourney_main": str(data.get("prompt_midjourney_main", "")),
            "prompt_midjourney_ingredients": str(data.get("prompt_midjourney_ingredients", "")),
        }

        return sections_content

    def _generate_all_content_sequential(self) -> Dict[str, Any]:
        """Fallback method for generating content section by section if JSON parsing fails."""
        title = self.config["title"]
        wc = self.config["structure_template"]["word_counts"]
        sections_content = {}
        
        _safe_print("[*] Generating intro...")
        sections_content["intro"] = self._generate_content_with_openai(f"Write a warm, engaging intro paragraph (~{wc['intro']} words) for a recipe article about {title}.")
        
        _safe_print("[*] Generating why-love items...")
        sections_content["why_i_love"] = [
            self._generate_content_with_openai(f"Write reason {i+1} of 4 why someone will love {title} (~{wc.get(f'why_i_love_item_{i+1}', 20)} words).") 
            for i in range(4)
        ]
        
        _safe_print("[*] Generating ingredients intro...")
        sections_content["ingredients_intro"] = self._generate_content_with_openai(f"Write a short intro (~{wc['ingredients_intro']} words) about the ingredients for {title}.")
        sections_content["ingredient_quality"] = self._generate_content_with_openai(f"Write notes on ingredient quality (~{wc['ingredient_quality_notes']} words) for {title}.")
        
        _safe_print("[*] Generating tips...")
        sections_content["tips_texture"] = self._generate_content_with_openai(f"Write tips on getting the perfect texture (~{wc['tips_texture']} words) for {title}.")
        sections_content["tips_mistakes"] = self._generate_content_with_openai(f"Write tips on avoiding common mistakes (~{wc['tips_mistakes']} words) for {title}.")
        
        _safe_print("[*] Generating serving suggestions...")
        sections_content["serving"] = self._generate_content_with_openai(f"Write serving suggestions (~{wc.get('serving_intro', 15)} words) for {title}.")
        
        _safe_print("[*] Generating pro tips...")
        sections_content["pro_tips"] = [
            self._generate_content_with_openai(f"Write pro tip {i+1} of 4 for {title} (~{wc.get(f'pro_tips_item_{i+1}', 25)} words).") 
            for i in range(4)
        ]
        
        _safe_print("[*] Generating FAQs...")
        sections_content["faqs"] = [
            self._generate_content_with_openai(f"Write FAQ {i+1} of 4 for {title} (Question and Answer combined, ~{wc.get(f'faq_{i+1}', 45)} words total).") 
            for i in range(4)
        ]
        
        _safe_print("[*] Generating conclusion...")
        sections_content["conclusion"] = self._generate_content_with_openai(f"Write a conclusion paragraph (~{wc['conclusion']} words) for {title}.")
        
        return sections_content

    def _get_preview_content(self) -> Dict[str, Any]:
        """Placeholder content for template preview (no AI calls)."""
        title = self.config["title"]
        return {
            "intro": f"This is a sample intro paragraph for {title}. When you generate a full article, AI will write engaging content here.",
            "why_i_love": [
                f"The delicious flavor combination of {title} is irresistible.",
                f"{title} is surprisingly easy to make at home.",
                f"Perfect to serve at parties and family gatherings.",
                "Great for meal prep and leftovers.",
            ],
            "ingredients_intro": "Gather these ingredients before you begin. Use the freshest quality you can find.",
            "ingredient_quality": "Using high-quality ingredients makes a noticeable difference in the final result. Opt for organic when possible.",
            "instructions": [
                "Preheat oven and prepare your baking pan.",
                "Mix the wet ingredients in a large bowl.",
                "Combine dry ingredients and fold into wet mixture.",
                "Transfer to pan and spread evenly.",
                "Bake until golden and a toothpick comes out clean.",
            ],
            "tips_texture": "For the best texture, don't overmix the batter. A few lumps are fine.",
            "tips_mistakes": "Avoid opening the oven door too early. Use an oven thermometer for accuracy.",
            "serving": "Serve warm with your favorite toppings. Pairs well with coffee or tea.",
            "pro_tips": [
                "Use room-temperature ingredients for best results.",
                "Chill the dough for 30 minutes before baking.",
                "Customize with your favorite mix-ins.",
                "Check doneness with a toothpick in the center.",
            ],
            "variation_nutty": f"Add chopped nuts for extra crunch. Walnuts or pecans work beautifully with {title}.",
            "variation_gluten_free": "Swap all-purpose flour for a gluten-free blend. Add 1 tsp xanthan gum.",
            "variation_flavor": "Try adding citrus zest or vanilla extract for a flavor boost.",
            "storage_best": "Store in an airtight container at room temperature for up to 3 days.",
            "storage_duration": "Keeps well for 3–5 days when stored properly.",
            "storage_freezing": "Freeze in a zip-top bag for up to 2 months. Thaw at room temperature.",
            "faqs": [
                f"You can substitute chocolate chips with nuts or dried fruit in {title}.",
                f"Fresh fruit works if you reduce moisture. Pat berries dry before folding in.",
                f"For a chewier texture, add 1 tablespoon of honey to the batter.",
                "Yes! Double the ingredients and use a 9x13 pan. Bake 5–10 minutes longer.",
            ],
            "conclusion": f"Enjoy your homemade {title}! Share your creation and tag us on social media.",
        }

    def run_preview(self) -> Dict[str, Any]:
        """Generate article template with placeholder content (no AI). For config preview."""
        self._validate_config()
        title = self.config["title"]
        sections_content = self._get_preview_content()
        recipe_data = self._generate_recipe_data()
        css_content = self._generate_css()
        html_content = self._generate_html(sections_content, recipe_data)
        return {
            "title": title,
            "slug": self._generate_slug(title),
            "article_html": html_content,
            "article_css": css_content,
        }
    
    def _generate_recipe_data(self) -> Dict[str, Any]:
        title = self.config["title"]
        defaults = {
            "name": title,
            "summary": f"Delicious homemade {title} perfect for any occasion.",
            "ingredients": [],
            "instructions": [],
            "prep_time": RECIPE_TEMPLATE["prep_time"],
            "cook_time": RECIPE_TEMPLATE["cook_time"],
            "total_time": RECIPE_TEMPLATE["total_time"],
            "servings": RECIPE_TEMPLATE["servings"],
            "calories": RECIPE_TEMPLATE["calories"],
            "course": RECIPE_TEMPLATE["course"],
            "cuisine": RECIPE_TEMPLATE["cuisine"]
        }
        ai_recipe = self.content_data.get("_ai_recipe")
        if ai_recipe and isinstance(ai_recipe, dict) and (ai_recipe.get("ingredients") or ai_recipe.get("instructions")):
            return {**defaults, **{k: v for k, v in ai_recipe.items() if v is not None and v != ""}}
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            return {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        return {
            "name": title,
            "summary": f"Delicious homemade {title} perfect for any occasion.",
            "ingredients": [
                "2 cups all-purpose flour",
                "1 cup sugar",
                "1/2 cup butter, melted",
                "2 large eggs",
                "1 tsp vanilla extract",
                "1 tsp baking powder",
                "1/2 tsp salt",
                "1 cup chocolate chips",
                "1 cup dried fruit"
            ],
            "instructions": [
                "Preheat oven to 350°F (175°C). Grease and line a 9x13 inch baking pan.",
                "Mix wet ingredients in a large bowl.",
                "Combine dry ingredients and mix with wet.",
                "Fold in mix-ins.",
                "Pour batter into pan and spread evenly.",
                "Bake for 25-30 minutes until golden brown.",
                "Cool in pan for 15 minutes.",
                "Lift out and cool completely on wire rack.",
                "Cut into squares and enjoy!"
            ],
            "prep_time": RECIPE_TEMPLATE["prep_time"],
            "cook_time": RECIPE_TEMPLATE["cook_time"],
            "total_time": RECIPE_TEMPLATE["total_time"],
            "servings": RECIPE_TEMPLATE["servings"],
            "calories": RECIPE_TEMPLATE["calories"],
            "course": RECIPE_TEMPLATE["course"],
            "cuisine": RECIPE_TEMPLATE["cuisine"]
        }
    
    def _generate_seo_data(self, title: str) -> Dict[str, str]:
        ai_seo = self.content_data.get("_ai_seo") or {}
        return {
            "recipe_title_pin": f"Easy {title} Recipe - Perfect for Any Occasion"[:100],
            "pinterest_title": f"Best {title} Recipe | Easy & Delicious"[:100],
            "pinterest_description": f"Learn how to make the most delicious {title} with this easy step-by-step recipe.",
            "pinterest_keywords": f"{title}, easy recipe, homemade dessert, baking recipe, family favorite",
            "focus_keyphrase": ai_seo.get("focus_keyphrase") or f"{title} recipe",
            "meta_description": (ai_seo.get("meta_description") or f"Make the best {title} with this easy recipe. Step-by-step instructions included!")[:140],
            "keyphrase_synonyms": f"homemade {title}, easy {title}, best {title} recipe"
        }
    
    def _generate_midjourney_prompts(self, title: str) -> Dict[str, str]:
        ai_mj = self.content_data.get("_ai_midjourney") or {}
        fallback_main = f"Beautiful food photography of {title}, golden brown, arranged on white marble countertop, soft natural lighting, 8k --v 6.1"
        fallback_ing = f"Flat lay food photography of baking ingredients for {title}, white background, natural lighting --v 6.1"
        return {
            "prompt_midjourney_main": (ai_mj.get("prompt_midjourney_main") or fallback_main).strip() or fallback_main,
            "prompt_midjourney_ingredients": (ai_mj.get("prompt_midjourney_ingredients") or fallback_ing).strip() or fallback_ing
        }
    
    def _generate_css(self) -> str:
        from generators.font_utils import font_family_css, build_font_import_url

        c = self.config["colors"]
        f = self.config["fonts"]
        l = self.config["layout"]
        comp = self.config["components"]

        hfam = (f.get("heading") or {}).get("family") or "Playfair Display"
        bfam = (f.get("body") or {}).get("family") or "Inter"
        import_url = build_font_import_url(f)
        body_font = font_family_css(bfam, "sans-serif")
        heading_font = font_family_css(hfam, "serif")

        return f"""@import url('{import_url}');
:root {{--primary: {c['primary']};--secondary: {c['secondary']};--background: {c['background']};--text-primary: {c['text_primary']};--text-secondary: {c['text_secondary']};--button-print: {c['button_print']};--button-pin: {c['button_pin']};}}
body {{font-family: {body_font};font-size: {f['body']['size']};line-height: {f['body']['line_height']};color: var(--text-primary);background: var(--background);margin:0;}}
.article-container {{max-width: {l['max_width']};margin: 0 auto;padding: {l['container_padding']};}}
.hero-image {{width:100%;max-width:100%;height:auto;display:block;border-radius:{l['border_radius']};margin-bottom:{l['section_spacing']};box-shadow:{l['box_shadow']};object-fit:cover;}}
h1,h2,h3 {{font-family: {heading_font};font-weight: 600;}}
h2 {{color: var(--primary);font-size: {f['heading']['sizes']['h2']};margin-top: {l['section_spacing']};}}
.pro-tips-box {{background: {comp['pro_tips_box']['bg_color']};border: 1px solid {comp['pro_tips_box']['border_color']};border-left: {comp['pro_tips_box']['border_left']};border-radius: {l['border_radius']};padding: {comp['pro_tips_box']['padding']};margin: {l['section_spacing']} 0;}}
.pro-tip-item {{display: flex;gap: 1rem;margin-bottom: 1rem;background: white;padding: 1rem;border-radius: 8px;}}
.pro-tip-number {{width: 32px;height: 32px;background: var(--primary);color: white;border-radius: 50%;display: flex;align-items: center;justify-content: center;font-weight: 600;flex-shrink: 0;}}
.ingredients-list {{list-style: none;padding: 0;}}
.ingredients-list li {{display: flex;gap: 0.75rem;padding: 0.5rem 0;border-bottom: 1px solid var(--border);}}
.instructions-list {{list-style: none;counter-reset: i;padding: 0;}}
.instructions-list li {{display: flex;gap: 1rem;margin-bottom: 1rem;}}
.instructions-list li::before {{counter-increment: i;content: counter(i);width: 32px;height: 32px;background: var(--primary);color: white;border-radius: 50%;display: flex;align-items: center;justify-content: center;font-weight: 600;flex-shrink: 0;}}
.recipe-card {{background: {comp['recipe_card']['bg']};border: {comp['recipe_card']['border']};border-radius: {comp['recipe_card']['border_radius']};padding: {comp['recipe_card']['padding']};margin: {l['section_spacing']} 0;}}
.recipe-card-header {{display: flex;gap: 1.5rem;margin-bottom: 1.5rem;}}
.recipe-card-image {{width: 100px;height: 100px;border-radius: 50%;object-fit: cover;}}
.article-header {{ margin-bottom: {l['section_spacing']}; padding-bottom: 1.5rem; border-bottom: 1px solid var(--border); }}
.article-header .article-title {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h1']}; font-weight: 700; color: var(--text-primary); margin: 0 0 1rem 0; line-height: 1.2; }}
.article-header .article-byline-row {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 1rem; }}
.article-header .byline-left {{ display: flex; flex-direction: column; gap: 0.25rem; }}
.article-header .byline-author {{ font-weight: 600; color: var(--text-primary); }}
.article-header .byline-date {{ font-size: 0.9rem; color: var(--text-secondary); }}
.article-header .byline-disclaimer {{ font-size: 0.8rem; color: var(--text-secondary); font-style: italic; margin: 0.25rem 0 0 0; }}
.article-header .byline-right {{ display: flex; flex-direction: column; align-items: flex-end; gap: 0.75rem; }}
.article-header .recipe-meta-inline {{ display: flex; gap: 1.25rem; font-size: 0.9rem; color: var(--text-secondary); }}
.article-header .recipe-meta-inline span {{ display: flex; align-items: center; gap: 0.35rem; }}
.recipe-meta {{display: flex;gap: 2rem;margin-bottom: 1.5rem;flex-wrap: wrap;}}
.recipe-meta-item {{display: flex;gap: 0.4rem;align-items: center;}}
.recipe-meta-item .value {{font-weight: 600;color: var(--primary);}}
.recipe-buttons {{display: flex;gap: 1rem;margin-bottom: 2rem;}}
.btn {{flex: 1;padding: 1rem;border: none;border-radius: 8px;font-weight: 600;cursor: pointer;display: flex;align-items: center;justify-content: center;gap: 0.5rem;}}
.btn-print {{background: var(--button-print);color: white;}}
.btn-pin {{background: var(--button-pin);color: white;}}
.recipe-columns {{display: grid;grid-template-columns: 1fr 1fr;gap: 3rem;}}
@media (max-width: 768px) {{.recipe-columns {{grid-template-columns: 1fr;}}}}
.chef-notes {{background: {comp['pro_tips_box']['bg_color']};border: 1px solid {comp['pro_tips_box']['border_color']};border-radius: {l['border_radius']};padding: 1.5rem;margin-top: 2rem;}}
.recipe-tags {{display: flex;gap: 2rem;justify-content: center;margin-top: 1.5rem;padding-top: 1.5rem;border-top: 1px solid var(--border);font-size: 0.875rem;}}"""
    
    def _get_image_url(self, key: str, fallback: str = "placeholder.jpg") -> str:
        """Get image URL from config.images or top-level config; dynamic for any field."""
        images = self.config.get("images") or {}
        url = images.get(key) or self.config.get(key) or ""
        return (url or "").strip() or fallback

    def _generate_html(self, sections_content: Dict, recipe_data: Dict) -> str:
        title = self.config["title"]
        hero_img = self._get_image_url("main_article_image")
        recipe_img = self._get_image_url("recipe_card_image", hero_img)
        why_items = "".join([f'<div class="pro-tip-item"><span class="pro-tip-number">{i+1}</span><p>{c}</p></div>' for i, c in enumerate(sections_content["why_i_love"])])
        pro_items = "".join([f'<div class="pro-tip-item"><span class="pro-tip-number">{i+1}</span><p>{c}</p></div>' for i, c in enumerate(sections_content["pro_tips"])])
        ing_list = "".join([f'<li><input type="checkbox" id="ing{i}"><label for="ing{i}">{ing}</label></li>' for i, ing in enumerate(recipe_data["ingredients"])])
        inst_list = "".join([f'<li>{inst}</li>' for inst in recipe_data["instructions"]])
        faq_html = "".join([f'<div class="faq-item"><h3>Q{i+1}</h3><p>{faq}</p></div>' for i, faq in enumerate(sections_content["faqs"])])
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} Recipe</title>
<link rel="stylesheet" href="css.css">
<!-- inject:head-end -->
</head>
<body>
<article class="article-container">
<header class="article-header g1-header">
<h1 class="article-title">{title}</h1>
<div class="article-byline-row">
<div class="byline-left">
<span class="byline-author">By <span class="article-author"></span></span>
<span class="byline-date">Published <span class="article-date"></span></span>
<p class="byline-disclaimer">This post may contain affiliate links.</p>
</div>
<div class="byline-right">
<button class="btn btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
<div class="recipe-meta-inline"><span>&#9201; {recipe_data["prep_time"]}</span><span>&#128293; {recipe_data["cook_time"]}</span><span>&#128101; {recipe_data["servings"]} servings</span></div>
</div>
</div>
</header>
<img src="{hero_img}" alt="{title}" class="hero-image">
<!-- inject:after-hero -->
<p class="intro">{sections_content["intro"]}</p>
<div class="pro-tips-box"><h2>Why I Love This Recipe</h2>{why_items}</div>
<h2>Ingredients</h2>
<p>{sections_content["ingredients_intro"]}</p>
<ul class="ingredients-list">{ing_list}</ul>
<p>{sections_content["ingredient_quality"]}</p>
<h2>Instructions</h2>
<ol class="instructions-list">{inst_list}</ol>
<h2>Tips & Tricks</h2>
<p>{sections_content["tips_texture"]}</p>
<p>{sections_content["tips_mistakes"]}</p>
<h2>Serving Suggestions</h2>
<p>{sections_content["serving"]}</p>
<div class="pro-tips-box"><h2>Pro Tips</h2>{pro_items}</div>
<h2>FAQs</h2>{faq_html}
<p>{sections_content["conclusion"]}</p>
<!-- inject:before-recipe -->
<div class="recipe-card">
<div class="recipe-card-header">
<img src="{recipe_img}" alt="{title}" class="recipe-card-image">
<div><h2>{title}</h2><p>{recipe_data["summary"]}</p></div>
</div>
<div class="recipe-meta">
<div class="recipe-meta-item"><span>&#9201;</span><span class="value">{recipe_data["prep_time"]}</span></div>
<div class="recipe-meta-item"><span>&#128293;</span><span class="value">{recipe_data["cook_time"]}</span></div>
<div class="recipe-meta-item"><span>&#128101;</span><span class="value">{recipe_data["servings"]}</span></div>
<div class="recipe-meta-item"><span>&#9889;</span><span class="value">{recipe_data["calories"]}</span></div>
</div>
<div class="recipe-buttons">
<button class="btn btn-print">Print Recipe</button>
<button class="btn btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
</div>
<div class="recipe-columns">
<div><h3>Ingredients</h3><ul class="ingredients-list">{ing_list}</ul></div>
<div><h3>Instructions</h3><ol class="instructions-list">{inst_list}</ol></div>
</div>
<div class="chef-notes"><h4>Chef's Notes</h4><p>Let cool completely before cutting.</p></div>
<div class="recipe-tags"><div><strong>Course:</strong> {recipe_data["course"]}</div><div><strong>Cuisine:</strong> {recipe_data["cuisine"]}</div></div>
</div>
<!-- inject:article-end -->
</article>
</body>
</html>"""
    
    def run(self, return_content_only: bool = False) -> Dict[str, Any]:
        self._validate_config()
        title = self.config["title"]
        _safe_print(f"Generating: {title}")
        
        sections_content = self.generate_all_content()
        recipe_data = self._generate_recipe_data()
        seo_data = self._generate_seo_data(title)
        midjourney = self._generate_midjourney_prompts(title)
        
        css_content = self._generate_css()
        html_content = self._generate_html(sections_content, recipe_data)
        
        cat = self._get_first_category()
        content_data = {
            "title": title,
            "slug": self._generate_slug(title),
            "categorieId": cat["id"],
            "categorie": cat["categorie"],
            "article_html": html_content,
            "article_css": css_content,
            "recipe": recipe_data,
            **seo_data,
            **midjourney,
            "main_image": self._get_image_url("main_article_image")
        }
        
        if return_content_only:
            return content_data
        
        self._save_files(content_data, html_content, css_content)
        _safe_print("Complete!")
        return content_data
    
    def _save_files(self, content_data: Dict, html_content: str, css_content: str):
        slug = content_data["slug"]
        os.makedirs(slug, exist_ok=True)
        
        with open(os.path.join(slug, "content.json"), "w", encoding="utf-8") as f:
            json.dump(content_data, f, indent=2)
        with open(os.path.join(slug, "article.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(os.path.join(slug, "css.css"), "w", encoding="utf-8") as f:
            f.write(css_content)
        
        _safe_print(f"Saved to: {slug}/")


ArticleGenerator = RecipeArticleGenerator  # alias for route API compatibility


if __name__ == "__main__":
    config = {"title": "couscous"}
    generator = RecipeArticleGenerator(config)
    generator.run()