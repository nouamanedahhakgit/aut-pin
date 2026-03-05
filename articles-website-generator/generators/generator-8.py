"""
Article Generator - generator-1.py
Design: Warm orange/coral recipe blog with serif headings, recipe card at bottom.
Structure: intro, why_love (4 items), ingredients (bullet list), instructions (5 steps),
           must_reads pro_tips_box, perfecting_process h3+paragraph, add_your_touch h3+paragraph,
           storing_reheating h3+paragraph, chefs_tips pro_tips_box, faqs (5), conclusion, recipe_card
"""

import os
import json
import re
import shutil
import textwrap
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary": "#E8643C",
        "secondary": "#F5A623",
        "accent": "#C0392B",
        "background": "#F9F9F9",
        "container_bg": "#FFFFFF",
        "border": "#E8E8E8",
        "text_primary": "#2D2D2D",
        "text_secondary": "#666666",
        "button_print": "#E8643C",
        "button_pin": "#E8643C",
        "button_hover_print": "#C0392B",
        "button_hover_pin": "#C0392B",
        "link": "#E8643C",
        "list_marker": "#E8643C"
    },
    "fonts": {
        "heading": {
            "family": "Georgia, 'Times New Roman', serif",
            "weights": [400, 700],
            "sizes": {"h1": "2.2rem", "h2": "1.7rem", "h3": "1.3rem"}
        },
        "body": {
            "family": "'Lato', 'Open Sans', Arial, sans-serif",
            "weight": 400,
            "size": "1rem",
            "line_height": 1.75
        }
    },
    "layout": {
        "max_width": "780px",
        "section_spacing": "2rem",
        "paragraph_spacing": "1.2rem",
        "list_spacing": "0.55rem",
        "container_padding": "2rem 1.5rem",
        "border_radius": "6px",
        "box_shadow": "0 2px 12px rgba(0,0,0,0.07)"
    },
    "components": {
        "numbered_list": {
            "style": "circle",
            "circle_bg": "#E8643C",
            "circle_color": "#FFFFFF",
            "circle_size": "32px"
        },
        "bullet_list": {
            "style": "disc",
            "color": "#E8643C"
        },
        "pro_tips_box": {
            "bg_color": "#FFF8F5",
            "border_color": "#E8643C",
            "border_left": "4px solid #E8643C",
            "padding": "1.2rem 1.5rem"
        },
        "recipe_card": {
            "bg": "#FFFFFF",
            "border": "1px solid #E8E8E8",
            "border_radius": "8px",
            "padding": "2rem",
            "meta_icon_color": "#E8643C"
        }
    },
    "images": {
        "main_article_image": "",
        "ingredient_image": "",
        "recipe_card_image": ""
    },
    "structure_template": {
        "word_counts": {
            "intro": 120,
            "why_i_love_intro": 30,
            "why_i_love_item_1": 30,
            "why_i_love_item_2": 30,
            "why_i_love_item_3": 30,
            "why_i_love_item_4": 30,
            "ingredients_intro": 60,
            "ingredients_list": 120,
            "instructions_intro": 40,
            "instructions_step_1": 80,
            "instructions_step_2": 80,
            "instructions_step_3": 80,
            "instructions_step_4": 80,
            "instructions_step_5": 80,
            "must_reads_tips": 100,
            "perfecting_process": 120,
            "add_your_touch": 100,
            "storing_reheating": 100,
            "chefs_tips": 100,
            "faq_1": 60,
            "faq_2": 60,
            "faq_3": 60,
            "faq_4": 60,
            "faq_5": 60,
            "conclusion": 100
        }
    },
    "dark_mode": False
}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text


class ArticleGenerator:
    def __init__(self, config_override=None):
        self.config = dict(CONFIG)
        if config_override:
            for k, v in config_override.items():
                if isinstance(v, dict) and isinstance(self.config.get(k), dict):
                    self.config[k].update(v)
                else:
                    self.config[k] = v
        provider = (self.config.get("ai_provider") or os.getenv("AI_PROVIDER", "openrouter")).lower()
        if provider == "openrouter":
            api_key = self.config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("[ERROR] openrouter_api_key must be in config or OPENROUTER_API_KEY in env")
            self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            self.model = self.config.get("openrouter_model") or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
        else:
            api_key = self.config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("[ERROR] openai_api_key must be in config or OPENAI_API_KEY in env")
            self.client = OpenAI(api_key=api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.title = self.config["title"] or "Delicious Homemade Pasta"
        self.slug = slugify(self.title)
        self.colors = self.config["colors"]
        self.fonts = self.config["fonts"]
        self.layout = self.config["layout"]
        self.components = self.config["components"]

    def gpt(self, prompt, max_tokens=600):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.75
        )
        return resp.choices[0].message.content.strip()

    def generate_sections(self):
        t = self.title
        wc = self.config["structure_template"]["word_counts"]
        
        schema = {
            "intro": f"string ~{wc['intro']} words",
            "why_intro": f"string ~{wc['why_i_love_intro']} words",
            "why_items": f"array of 4 strings (Label: sentence) ~120 words total",
            "ingredients_intro": f"string ~{wc['ingredients_intro']} words",
            "ingredients_list": "array of 12-15 strings with amounts",
            "instructions_intro": f"string ~{wc['instructions_intro']} words",
            "steps": "array of 5 objects with title and text",
            "must_reads_list": "array of 3 strings",
            "perfecting": f"string ~{wc['perfecting_process']} words",
            "add_touch": f"string ~{wc['add_your_touch']} words",
            "storing": f"string ~{wc['storing_reheating']} words",
            "chefs_tips_list": "array of 3 strings",
            "faqs": "array of 5 objects with q and a",
            "conclusion": f"string ~{wc['conclusion']} words",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine",
            "meta_desc": "string exactly 120-140 chars",
            "pinterest_desc": "string 2-3 sentences",
            "focus_kp": "string 2-5 words",
            "kp_syn": "string comma separated terms",
            "pinterest_kw": "string 6 comma separated terms",
            "mj_main": "string ending in --v 6.1",
            "mj_ingredients": "string ending in --v 6.1"
        }

        system = (
            "You are a professional food blogger and recipe writer. Write engaging, SEO-optimized content that sounds natural and human. "
            "Never mention word counts or writing instructions. "
            "Output the full article as ONE JSON. Plain text only: no markdown. "
            f"All content must be only about this recipe: {t}. Do not mention or use ingredients, steps, or dish names from any other recipe."
        )
        user = f"Generate the complete food blog article for '{t}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        
        print("[*] Generating all sections in a single JSON API call...")
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
            return self._generate_sections_sequential()
            
        print("[*] Generated content via single JSON.")
        
        # Ensure correct formatting for keys that expect lists of strings
        for key in ["why_items", "ingredients_list", "must_reads_list", "chefs_tips_list"]:
            if key in data and isinstance(data[key], list):
                data[key] = [str(x) for x in data[key]]
            else:
                data[key] = []
                
        # Ensure steps have correct format
        if "steps" in data and isinstance(data["steps"], list):
            data["steps"] = [{"title": str(s.get("title", f"Step {i+1}")), "text": str(s.get("text", ""))} for i, s in enumerate(data["steps"])]
        else:
            data["steps"] = []
            
        # Ensure faqs have correct format
        if "faqs" in data and isinstance(data["faqs"], list):
            data["faqs"] = [{"q": str(f.get("q", "")), "a": str(f.get("a", ""))} for f in data["faqs"]]
        else:
            data["faqs"] = []
            
        # Ensure strings are strings
        for key in ["intro", "why_intro", "ingredients_intro", "instructions_intro", "perfecting", "add_touch", "storing", "conclusion", "meta_desc", "pinterest_desc", "focus_kp", "kp_syn", "pinterest_kw", "mj_main", "mj_ingredients"]:
            data[key] = str(data.get(key, ""))
            
        # Handle recipe object
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": t, "summary": "", "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min",
                "servings": 4, "calories": 450, "course": "Dinner", "cuisine": "International"
            }
            data["recipe"] = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        else:
            if "recipe" not in data or not isinstance(data["recipe"], dict):
                data["recipe"] = {"name": t, "summary": "", "ingredients": data["ingredients_list"][:15], "instructions": [s["text"] for s in data["steps"]][:10], "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min", "servings": 4, "calories": 450, "course": "Dinner", "cuisine": "International"}

        return data

    def _generate_sections_sequential(self):
        t = self.title
        wc = self.config["structure_template"]["word_counts"]

        print("[*] Generating intro...")
        intro = self.gpt(
            f"Write a warm, engaging intro paragraph (~{wc['intro']} words) for a recipe article about {t}. "
            f"Hook the reader, mention how delicious and approachable it is. No heading. Plain paragraph text only."
        )

        print("[*] Generating why-love items...")
        why_intro = self.gpt(
            f"Write 1 short sentence (~{wc['why_i_love_intro']} words) introducing why readers will love {t}. No heading."
        )
        why_items = []
        why_labels = ["Bold Flavor", "Easy to Make", "Crowd Pleaser", "Versatile"]
        for i in range(1, 5):
            item = self.gpt(
                f"Write a bullet point (~{wc[f'why_i_love_item_{i}']} words) explaining one reason to love {t}. "
                f"Start with bold label '{why_labels[i-1]}:' followed by a sentence. Plain text, no markdown bullets."
            )
            why_items.append(item)

        print("[*] Generating ingredients...")
        ingredients_intro = self.gpt(
            f"Write a short intro sentence (~{wc['ingredients_intro']} words) about the ingredients needed for {t}. "
            f"Mention they are simple/pantry-friendly. Plain text only."
        )
        ingredients_list_raw = self.gpt(
            f"List the ingredients for {t} as a plain text list, one per line (~12-15 items). "
            f"Include amounts. No dashes or bullets, just plain lines."
        )
        ingredients_list = [l.strip() for l in ingredients_list_raw.splitlines() if l.strip()]

        print("[*] Generating instructions...")
        instructions_intro = self.gpt(
            f"Write a short intro sentence (~{wc['instructions_intro']} words) before the step-by-step instructions for {t}."
        )
        steps = []
        step_titles = ["Prepare Your Ingredients", "Build the Base", "Add the Main Components",
                       "Bring It Together", "Finish and Serve"]
        for i in range(1, 6):
            step_text = self.gpt(
                f"Write step {i} of the recipe instructions for {t} (~{wc[f'instructions_step_{i}']} words). "
                f"Step title: '{step_titles[i-1]}'. Be clear and practical. Plain paragraph text only, no markdown."
            )
            steps.append({"title": step_titles[i-1], "text": step_text})

        print("[*] Generating pro tips boxes...")
        must_reads = self.gpt(
            f"Write 3 short pro tips for making {t} as a list, one tip per line (~{wc['must_reads_tips']} words total). "
            f"Plain text lines, no bullets or dashes."
        )
        must_reads_list = [l.strip() for l in must_reads.splitlines() if l.strip()]

        print("[*] Generating sub-sections...")
        perfecting = self.gpt(
            f"Write a paragraph (~{wc['perfecting_process']} words) titled 'Perfecting the Cooking Process' "
            f"with tips on technique and timing for {t}. Plain paragraph text."
        )
        add_touch = self.gpt(
            f"Write a paragraph (~{wc['add_your_touch']} words) titled 'Add Your Touch' with creative "
            f"variations and substitutions for {t}. Plain paragraph text."
        )
        storing = self.gpt(
            f"Write a paragraph (~{wc['storing_reheating']} words) titled 'Storing and Reheating' "
            f"with storage and reheating instructions for {t}. Plain paragraph text."
        )

        chefs_tips_raw = self.gpt(
            f"Write 3 short chef tips for {t} as a list, one per line (~{wc['chefs_tips']} words total). "
            f"Plain text lines, no bullets or dashes."
        )
        chefs_tips_list = [l.strip() for l in chefs_tips_raw.splitlines() if l.strip()]

        print("[*] Generating FAQs...")
        faqs = []
        faq_topics = [
            "Can I make this ahead of time?",
            "What can I substitute if I don't have a key ingredient?",
            "How do I store leftovers?",
            "Can I freeze this dish?",
            "How can I adjust the recipe for dietary restrictions?"
        ]
        for i in range(1, 6):
            ans = self.gpt(
                f"Answer this FAQ about {t} in ~{wc[f'faq_{i}']} words: '{faq_topics[i-1]}'. "
                f"Be helpful and concise. Plain text answer only."
            )
            faqs.append({"q": faq_topics[i-1], "a": ans})

        print("[*] Generating conclusion...")
        conclusion = self.gpt(
            f"Write a warm conclusion paragraph (~{wc['conclusion']} words) for a recipe article about {t}. "
            f"Encourage readers to try it and share. Plain paragraph text."
        )

        print("[*] Generating recipe card data...")
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": t, "summary": "", "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min",
                "servings": 4, "calories": 450, "course": "Dinner", "cuisine": "International"
            }
            recipe = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        else:
            recipe_json_raw = self.gpt(
                f"Create a JSON recipe card for {t} with these fields: "
                f"name, summary (1 sentence), ingredients (array of strings with amounts), "
                f"instructions (array of strings, 5 steps), prep_time, cook_time, total_time, "
                f"servings, calories, course, cuisine. "
                f"Return ONLY valid JSON, no markdown fences.",
                max_tokens=800
            )
            try:
                recipe = json.loads(recipe_json_raw)
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', recipe_json_raw, re.DOTALL)
                if match:
                    try:
                        recipe = json.loads(match.group())
                    except Exception:
                        recipe = {"name": t, "summary": "", "ingredients": [], "instructions": [],
                                  "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min",
                                  "servings": 4, "calories": 450, "course": "Dinner", "cuisine": "International"}
                else:
                    recipe = {"name": t, "summary": "", "ingredients": [], "instructions": [],
                              "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min",
                              "servings": 4, "calories": 450, "course": "Dinner", "cuisine": "International"}

        print("[*] Generating SEO fields...")
        meta_desc = self.gpt(
            f"Write a meta description for a recipe article about {t}. "
            f"Exactly 120-140 characters, SEO-optimized, engaging. Plain text only."
        )
        pinterest_desc = self.gpt(
            f"Write a Pinterest description (2-3 sentences) for {t}. Enticing, keyword-rich."
        )
        focus_kp = self.gpt(
            f"Write a concise focus keyphrase (2-5 words) for a recipe article about {t}. Plain text only."
        )
        kp_syn = self.gpt(
            f"Write 4 keyphrase synonyms for '{t}' as comma-separated terms. Plain text only."
        )
        pinterest_kw = self.gpt(
            f"Write 6 Pinterest keywords for {t} as comma-separated terms. Plain text only."
        )
        mj_main = self.gpt(
            f"Write a Midjourney prompt for a hero food photo of {t}. "
            f"Describe the dish, plating, lighting, style. End with --v 6.1"
        )
        mj_ingredients = self.gpt(
            f"Write a Midjourney prompt for a flat-lay ingredients photo for {t}. "
            f"Describe the ingredients, surface, styling. End with --v 6.1"
        )

        return {
            "intro": intro,
            "why_intro": why_intro,
            "why_items": why_items,
            "ingredients_intro": ingredients_intro,
            "ingredients_list": ingredients_list,
            "instructions_intro": instructions_intro,
            "steps": steps,
            "must_reads_list": must_reads_list,
            "perfecting": perfecting,
            "add_touch": add_touch,
            "storing": storing,
            "chefs_tips_list": chefs_tips_list,
            "faqs": faqs,
            "conclusion": conclusion,
            "recipe": recipe,
            "meta_desc": meta_desc,
            "pinterest_desc": pinterest_desc,
            "focus_kp": focus_kp,
            "kp_syn": kp_syn,
            "pinterest_kw": pinterest_kw,
            "mj_main": mj_main,
            "mj_ingredients": mj_ingredients
        }

    def build_css(self):
        c = self.colors
        f = self.fonts
        l = self.layout
        comp = self.components

        css = f"""
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

*, *::before, *::after {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    background: {c['background']};
    color: {c['text_primary']};
    font-family: {f['body']['family']};
    font-size: {f['body']['size']};
    line-height: {f['body']['line_height']};
}}

.article-wrapper {{
    max-width: {l['max_width']};
    margin: 0 auto;
    background: {c['container_bg']};
    box-shadow: {l['box_shadow']};
    padding: {l['container_padding']};
}}

.article-header.g8-header {{
    margin-bottom: 1.25rem;
}}
.article-header.g8-header .article-title {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 700;
    color: {c['text_primary']};
    margin: 0 0 0.5rem 0;
    line-height: 1.25;
}}
.article-header.g8-header .article-byline-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}}
.article-header.g8-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g8-header .byline-author {{ font-weight: 600; color: {c['text_primary']}; }}
.article-header.g8-header .byline-date {{ font-size: 0.875rem; color: {c['text_secondary']}; }}
.article-header.g8-header .byline-disclaimer {{ font-size: 0.8rem; color: {c['text_secondary']}; font-style: italic; margin-top: 0.2rem; }}
.article-header.g8-header .byline-right {{ display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }}
.article-header.g8-header .recipe-meta-inline {{ display: flex; gap: 1rem; font-size: 0.9rem; color: {c['text_secondary']}; }}

/* TYPOGRAPHY */
h1 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 700;
    color: {c['text_primary']};
    line-height: 1.25;
    margin-bottom: 1rem;
}}

h2 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h2']};
    font-weight: 700;
    color: {c['text_primary']};
    line-height: 1.3;
    margin-top: {l['section_spacing']};
    margin-bottom: 1rem;
    border-bottom: 2px solid {c['border']};
    padding-bottom: 0.4rem;
}}

h3 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h3']};
    font-weight: 700;
    color: {c['text_primary']};
    margin-top: 1.5rem;
    margin-bottom: 0.6rem;
}}

p {{
    margin-bottom: {l['paragraph_spacing']};
    color: {c['text_primary']};
}}

a {{
    color: {c['link']};
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

/* ARTICLE IMAGE */
.article-main-image {{
    width: 100%;
    height: auto;
    border-radius: {l['border_radius']};
    margin-bottom: 1.5rem;
    display: block;
}}

/* WHY LOVE LIST */
.why-love-list {{
    list-style: none;
    padding: 0;
    margin: 1rem 0 {l['section_spacing']};
}}

.why-love-list li {{
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid {c['border']};
    color: {c['text_primary']};
    line-height: 1.6;
}}

.why-love-list li:last-child {{
    border-bottom: none;
}}

.why-love-list li::before {{
    content: '';
    display: inline-block;
    width: 10px;
    height: 10px;
    min-width: 10px;
    border-radius: 50%;
    background: {c['list_marker']};
    margin-top: 0.45rem;
}}

/* BULLET LIST */
.ingredient-list {{
    list-style: none;
    padding: 0;
    margin: 0.8rem 0 1.5rem;
    column-count: 2;
    column-gap: 1.5rem;
}}

.ingredient-list li {{
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: {l['list_spacing']};
    break-inside: avoid;
    color: {c['text_primary']};
}}

.ingredient-list li::before {{
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    min-width: 8px;
    border-radius: 50%;
    background: {c['list_marker']};
    margin-top: 0.45rem;
}}

/* NUMBERED STEPS */
.steps-list {{
    list-style: none;
    padding: 0;
    margin: 1rem 0;
}}

.steps-list li {{
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.5rem;
}}

.step-number {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: {comp['numbered_list']['circle_size']};
    height: {comp['numbered_list']['circle_size']};
    min-width: {comp['numbered_list']['circle_size']};
    border-radius: 50%;
    background: {comp['numbered_list']['circle_bg']};
    color: {comp['numbered_list']['circle_color']};
    font-weight: 700;
    font-size: 0.95rem;
    font-family: {f['body']['family']};
}}

.step-content h4 {{
    font-family: {f['heading']['family']};
    font-size: 1.05rem;
    font-weight: 700;
    color: {c['text_primary']};
    margin-bottom: 0.4rem;
}}

.step-content p {{
    margin: 0;
}}

/* PRO TIPS BOX */
.pro-tips-box {{
    background: {comp['pro_tips_box']['bg_color']};
    border-left: {comp['pro_tips_box']['border_left']};
    padding: {comp['pro_tips_box']['padding']};
    border-radius: {l['border_radius']};
    margin: {l['section_spacing']} 0;
}}

.pro-tips-box h3 {{
    margin-top: 0;
    color: {c['primary']};
    font-size: 1.15rem;
}}

.pro-tips-box ul {{
    list-style: none;
    padding: 0;
    margin: 0.6rem 0 0;
}}

.pro-tips-box ul li {{
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
    color: {c['text_primary']};
}}

.pro-tips-box ul li::before {{
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    min-width: 8px;
    border-radius: 50%;
    background: {c['primary']};
    margin-top: 0.45rem;
}}

/* FAQ */
.faq-section {{
    margin: {l['section_spacing']} 0;
}}

.faq-item {{
    border: 1px solid {c['border']};
    border-radius: {l['border_radius']};
    margin-bottom: 0.8rem;
    overflow: hidden;
}}

.faq-question {{
    background: #FAFAFA;
    padding: 1rem 1.2rem;
    font-weight: 700;
    font-family: {f['heading']['family']};
    font-size: 1rem;
    color: {c['text_primary']};
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: none;
    width: 100%;
    text-align: left;
}}

.faq-question .faq-icon {{
    font-size: 1.3rem;
    color: {c['primary']};
    font-weight: 400;
    flex-shrink: 0;
}}

.faq-answer {{
    padding: 1rem 1.2rem;
    color: {c['text_secondary']};
    border-top: 1px solid {c['border']};
    line-height: 1.7;
}}

/* PRINT/PIN BUTTONS */
.article-buttons {{
    display: flex;
    gap: 0.8rem;
    margin: 1.5rem 0;
    flex-wrap: wrap;
}}

.btn-print, .btn-pin {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.3rem;
    border-radius: {l['border_radius']};
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    border: none;
    text-decoration: none;
    font-family: {f['body']['family']};
    transition: background 0.2s;
}}

.btn-print {{
    background: {c['button_print']};
    color: #fff;
}}

.btn-print:hover {{
    background: {c['button_hover_print']};
}}

.btn-pin {{
    background: {c['button_pin']};
    color: #fff;
}}

.btn-pin:hover {{
    background: {c['button_hover_pin']};
}}

/* INGREDIENT IMAGE */
.ingredient-image {{
    width: 100%;
    height: auto;
    border-radius: {l['border_radius']};
    margin: 1.2rem 0;
    display: block;
}}

/* RECIPE CARD */
.recipe-card {{
    background: {comp['recipe_card']['bg']};
    border: {comp['recipe_card']['border']};
    border-radius: {comp['recipe_card']['border_radius']};
    padding: {comp['recipe_card']['padding']};
    margin: {l['section_spacing']} 0;
    box-shadow: {l['box_shadow']};
}}

.recipe-card-header {{
    background: {c['primary']};
    color: #fff;
    padding: 1rem 1.5rem;
    margin: -{comp['recipe_card']['padding']} -{comp['recipe_card']['padding']} 1.5rem;
    border-radius: {comp['recipe_card']['border_radius']} {comp['recipe_card']['border_radius']} 0 0;
}}

.recipe-card-header h2 {{
    color: #fff;
    border: none;
    margin: 0;
    padding: 0;
    font-size: 1.4rem;
}}

.recipe-card-image {{
    width: 100%;
    height: auto;
    border-radius: {l['border_radius']};
    margin-bottom: 1.2rem;
    display: block;
}}

.recipe-meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.2rem;
}}

.recipe-meta-item {{
    display: flex;
    align-items: center;
    gap: 0.3rem;
    background: #FFF8F5;
    border: 1px solid {c['border']};
    border-radius: 4px;
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
    color: {c['text_primary']};
}}

.recipe-meta-item .meta-label {{
    font-weight: 700;
    color: {comp['recipe_card']['meta_icon_color']};
    margin-right: 2px;
}}

.recipe-card h3 {{
    margin-top: 1.2rem;
    margin-bottom: 0.6rem;
    color: {c['text_primary']};
    font-size: 1.1rem;
}}

.recipe-card-ingredients {{
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
}}

.recipe-card-ingredients li {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.3rem 0;
    border-bottom: 1px solid {c['border']};
    font-size: 0.95rem;
    color: {c['text_primary']};
}}

.recipe-card-ingredients li:last-child {{
    border-bottom: none;
}}

.recipe-card-ingredients li input[type="checkbox"] {{
    accent-color: {c['primary']};
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}}

.recipe-card-instructions {{
    list-style: none;
    padding: 0;
    margin: 0;
}}

.recipe-card-instructions li {{
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
}}

.recipe-step-num {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    min-width: 26px;
    border-radius: 50%;
    background: {c['primary']};
    color: #fff;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
}}

.recipe-card-buttons {{
    display: flex;
    gap: 0.8rem;
    margin-top: 1.2rem;
    flex-wrap: wrap;
}}

/* CONCLUSION */
.conclusion-section {{
    background: #FFF8F5;
    border-radius: {l['border_radius']};
    padding: 1.5rem;
    margin-top: {l['section_spacing']};
    border: 1px solid {c['border']};
}}

.conclusion-section p {{
    margin-bottom: 0;
}}

/* RESPONSIVE */
@media (max-width: 600px) {{
    .article-wrapper {{
        padding: 1rem;
    }}
    h1 {{
        font-size: 1.6rem;
    }}
    h2 {{
        font-size: 1.35rem;
    }}
    .ingredient-list {{
        column-count: 1;
    }}
    .recipe-meta {{
        gap: 0.4rem;
    }}
}}

@media print {{
    .article-buttons, .recipe-card-buttons, .btn-print, .btn-pin {{
        display: none;
    }}
    body {{
        background: #fff;
    }}
    .article-wrapper {{
        box-shadow: none;
        padding: 0;
    }}
}}
"""
        return css

    def build_html(self, data, css_filename="css.css"):
        t = self.title
        img_main = self.config["images"]["main_article_image"] or "placeholder.jpg"
        img_ing = self.config["images"]["ingredient_image"] or "placeholder.jpg"
        img_card = self.config["images"]["recipe_card_image"] or "placeholder.jpg"

        # Why love items
        why_items_html = ""
        for item in data["why_items"]:
            why_items_html += f'<li>{item}</li>\n'

        # Ingredients
        ing_html = ""
        for ing in data["ingredients_list"]:
            if ing.strip():
                ing_html += f'<li>{ing}</li>\n'

        # Steps
        steps_html = ""
        for i, step in enumerate(data["steps"], 1):
            steps_html += f"""
            <li>
                <div class="step-number">{i}</div>
                <div class="step-content">
                    <h4>{step['title']}</h4>
                    <p>{step['text']}</p>
                </div>
            </li>"""

        # Must reads tips
        must_reads_html = ""
        for tip in data["must_reads_list"]:
            if tip.strip():
                must_reads_html += f'<li>{tip}</li>\n'

        # Chef tips
        chefs_html = ""
        for tip in data["chefs_tips_list"]:
            if tip.strip():
                chefs_html += f'<li>{tip}</li>\n'

        # FAQs
        faqs_html = ""
        for i, faq in enumerate(data["faqs"], 1):
            faqs_html += f"""
            <div class="faq-item">
                <button class="faq-question" onclick="toggleFaq(this)">
                    {faq['q']}
                    <span class="faq-icon">+</span>
                </button>
                <div class="faq-answer" style="display:none;">
                    {faq['a']}
                </div>
            </div>"""

        # Recipe card
        recipe = data["recipe"]
        rc_ingredients_html = ""
        for ing in recipe.get("ingredients", []):
            rc_ingredients_html += f'<li><input type="checkbox"> {ing}</li>\n'

        rc_instructions_html = ""
        for i, inst in enumerate(recipe.get("instructions", []), 1):
            rc_instructions_html += f"""
            <li>
                <span class="recipe-step-num">{i}</span>
                <span>{inst}</span>
            </li>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{data['meta_desc']}">
    <title>{t}</title>
    <link rel="stylesheet" href="{css_filename}">
</head>
<body>
<div class="article-wrapper">

    <header class="article-header g8-header">
        <h1 class="article-title">{t}</h1>
        <div class="article-byline-row">
            <div class="byline-left">
                <span class="byline-author">By <span class="article-author"></span></span>
                <span class="byline-date">Published <span class="article-date"></span></span>
                <p class="byline-disclaimer">This post may contain affiliate links.</p>
            </div>
            <div class="byline-right">
                <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
                <div class="recipe-meta-inline"><span>{recipe.get("prep_time", "")} prep</span><span>{recipe.get("cook_time", "")} cook</span><span>{recipe.get("servings", "")} servings</span></div>
            </div>
        </div>
    </header>

    <img src="{img_main}" alt="{t}" class="article-main-image" loading="lazy">

    <div class="article-buttons">
        <button class="btn-print" onclick="window.print()">Print Recipe</button>
        <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Save to Pinterest</button>
    </div>

    <p>{data['intro']}</p>

    <h2>Why You'll Love This Recipe</h2>
    <p>{data['why_intro']}</p>
    <ul class="why-love-list">
        {why_items_html}
    </ul>

    <h2>Ingredients for {t}</h2>
    <p>{data['ingredients_intro']}</p>

    <img src="{img_ing}" alt="Ingredients for {t}" class="ingredient-image" loading="lazy">

    <ul class="ingredient-list">
        {ing_html}
    </ul>

    <h2>How to Make {t}</h2>
    <p>{data['instructions_intro']}</p>

    <ul class="steps-list">
        {steps_html}
    </ul>

    <div class="pro-tips-box">
        <h3>Must Reads</h3>
        <ul>
            {must_reads_html}
        </ul>
    </div>

    <h3>Perfecting the Cooking Process</h3>
    <p>{data['perfecting']}</p>

    <h3>Add Your Touch</h3>
    <p>{data['add_touch']}</p>

    <h3>Storing and Reheating</h3>
    <p>{data['storing']}</p>

    <div class="pro-tips-box">
        <h3>Chef's Helpful Tips</h3>
        <ul>
            {chefs_html}
        </ul>
    </div>

    <h2>Frequently Asked Questions</h2>
    <div class="faq-section">
        {faqs_html}
    </div>

    <div class="conclusion-section">
        <h2 style="border:none;margin-top:0;padding-bottom:0;">Conclusion for {t}</h2>
        <p>{data['conclusion']}</p>
    </div>

    <!-- RECIPE CARD -->
    <div class="recipe-card">
        <div class="recipe-card-header">
            <h2>{recipe.get('name', t)}</h2>
        </div>

        <img src="{img_card}" alt="{t}" class="recipe-card-image" loading="lazy">

        <p>{recipe.get('summary', '')}</p>

        <div class="recipe-meta">
            <span class="recipe-meta-item"><span class="meta-label">Prep:</span> {recipe.get('prep_time', '')}</span>
            <span class="recipe-meta-item"><span class="meta-label">Cook:</span> {recipe.get('cook_time', '')}</span>
            <span class="recipe-meta-item"><span class="meta-label">Total:</span> {recipe.get('total_time', '')}</span>
            <span class="recipe-meta-item"><span class="meta-label">Servings:</span> {recipe.get('servings', '')}</span>
            <span class="recipe-meta-item"><span class="meta-label">Calories:</span> {recipe.get('calories', '')} kcal</span>
            <span class="recipe-meta-item"><span class="meta-label">Course:</span> {recipe.get('course', '')}</span>
            <span class="recipe-meta-item"><span class="meta-label">Cuisine:</span> {recipe.get('cuisine', '')}</span>
        </div>

        <div class="recipe-card-buttons">
            <button class="btn-print" onclick="window.print()">Print Recipe</button>
            <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
        </div>

        <h3>Ingredients</h3>
        <ul class="recipe-card-ingredients">
            {rc_ingredients_html}
        </ul>

        <h3>Instructions</h3>
        <ol class="recipe-card-instructions">
            {rc_instructions_html}
        </ol>
    </div>

</div>

<script>
function toggleFaq(btn) {{
    var answer = btn.nextElementSibling;
    var icon = btn.querySelector('.faq-icon');
    if (answer.style.display === 'none') {{
        answer.style.display = 'block';
        icon.textContent = '-';
    }} else {{
        answer.style.display = 'none';
        icon.textContent = '+';
    }}
}}
</script>
</body>
</html>"""
        return html

    def build_content_data(self, data, html_content, css_content):
        recipe = data["recipe"]
        from ai_client import get_first_category
        cat = get_first_category(self.config)
        cat_id = cat.get("id", 1)
        cat_name = cat.get("categorie", "dinner")
        pin_title = f"{self.title} Recipe"[:100]

        return {
            "title": self.title,
            "slug": self.slug,
            "categorieId": str(cat_id),
            "categorie": cat_name,
            "sections": [
                {"type": "intro", "content": data["intro"]},
                {"type": "h2", "content": "Why You'll Love This Recipe"},
                {"type": "bullet_list", "content": data["why_items"]},
                {"type": "h2", "content": f"Ingredients for {self.title}"},
                {"type": "paragraph", "content": data["ingredients_intro"]},
                {"type": "image", "content": self.config["images"]["ingredient_image"]},
                {"type": "bullet_list", "content": data["ingredients_list"]},
                {"type": "h2", "content": f"How to Make {self.title}"},
                {"type": "paragraph", "content": data["instructions_intro"]},
                {"type": "numbered_list", "content": [f"{s['title']}: {s['text']}" for s in data["steps"]]},
                {"type": "pro_tips_box", "content": data["must_reads_list"]},
                {"type": "h3", "content": "Perfecting the Cooking Process"},
                {"type": "paragraph", "content": data["perfecting"]},
                {"type": "h3", "content": "Add Your Touch"},
                {"type": "paragraph", "content": data["add_touch"]},
                {"type": "h3", "content": "Storing and Reheating"},
                {"type": "paragraph", "content": data["storing"]},
                {"type": "pro_tips_box", "content": data["chefs_tips_list"]},
                {"type": "faq", "content": data["faqs"]},
                {"type": "conclusion", "content": data["conclusion"]}
            ],
            "article_html": html_content,
            "article_css": css_content,
            "prompt_used": f"Recipe article generator for: {self.title}",
            "prompt_base": "generator-1",
            "recipe": recipe,
            "recipe_title_pin": pin_title,
            "pinterest_title": pin_title,
            "pinterest_description": data["pinterest_desc"],
            "pinterest_keywords": data["pinterest_kw"],
            "focus_keyphrase": data["focus_kp"],
            "meta_description": data["meta_desc"],
            "keyphrase_synonyms": data["kp_syn"],
            "main_image": self.config["images"]["main_article_image"],
            "ingredient_image": self.config["images"]["ingredient_image"],
            "prompt_midjourney_main": data["mj_main"],
            "prompt_midjourney_ingredients": data["mj_ingredients"]
        }

    def save_files(self, content_data, html_content, css_content):
        out_dir = Path(self.slug)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Save structure.json
        structure = {
            "generator": "generator-1",
            "title": self.title,
            "slug": self.slug,
            "sections": self.config["structure_template"],
            "section_order": [s["type"] for s in content_data["sections"]]
        }
        (out_dir / "structure.json").write_text(
            json.dumps(structure, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Save content.json (without large html/css to keep readable, add them back)
        (out_dir / "content.json").write_text(
            json.dumps(content_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Save css.css
        (out_dir / "css.css").write_text(css_content, encoding="utf-8")

        # Save article.html
        (out_dir / "article.html").write_text(html_content, encoding="utf-8")

        # placeholder.jpg
        placeholder_src = Path("placeholder.jpg")
        placeholder_dst = out_dir / "placeholder.jpg"
        if placeholder_src.exists():
            shutil.copy(placeholder_src, placeholder_dst)
        else:
            placeholder_dst.write_bytes(b"")

        print(f"[OK] Files saved to: {out_dir}/")

    def run(self, return_content_only=False):
        print(f"[*] Generating article: {self.title}")

        data = self.generate_sections()
        css_content = self.build_css()
        html_content = self.build_html(data, css_filename="css.css")
        content_data = self.build_content_data(data, html_content, css_content)

        if return_content_only:
            return content_data

        self.save_files(content_data, html_content, css_content)
        print("[OK] Complete!")
        return content_data


if __name__ == "__main__":
    import sys
    title = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Creamy Tomato Garlic Pasta"
    gen = ArticleGenerator(config_override={"title": title})
    gen.run()
