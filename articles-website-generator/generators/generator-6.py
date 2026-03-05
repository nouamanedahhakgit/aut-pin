"""
generator-6.py
--------------
Production-ready article generator.
Design extracted from image analysis (NOT at runtime).
CONFIG["title"] = "" -- user supplies title via API payload.
"""

import os
import json
import re
import textwrap
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# CONFIG -- all design/layout values extracted from image analysis
# ---------------------------------------------------------------------------
CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary":           "#F07C33",
        "secondary":         "#222222",
        "accent":            "#E8813A",
        "background":        "#FFFFFF",
        "container_bg":      "#FFFFFF",
        "border":            "#E0E0E0",
        "text_primary":      "#222222",
        "text_secondary":    "#555555",
        "button_print":      "#F07C33",
        "button_pin":        "#E60023",
        "button_hover_print":"#D96820",
        "button_hover_pin":  "#C0001E",
        "link":              "#F07C33",
        "list_marker":       "#F07C33",
    },
    "fonts": {
        "heading": {
            "family":  "'Georgia', serif",
            "weights": [700, 800],
            "sizes":   {"h1": "2rem", "h2": "1.55rem", "h3": "1.2rem"},
        },
        "body": {
            "family":      "'Helvetica Neue', Arial, sans-serif",
            "weight":      400,
            "size":        "16px",
            "line_height": 1.75,
        },
    },
    "layout": {
        "max_width":          "780px",
        "section_spacing":    "2.2rem",
        "paragraph_spacing":  "1.1rem",
        "list_spacing":       "0.55rem",
        "container_padding":  "1.5rem",
        "border_radius":      "8px",
        "box_shadow":         "0 2px 8px rgba(0,0,0,0.08)",
    },
    "components": {
        "numbered_list": {
            "style":       "none",
            "circle_bg":   "#F07C33",
            "circle_color":"#FFFFFF",
            "circle_size": "32px",
        },
        "bullet_list": {
            "style": "disc",
            "color": "#F07C33",
        },
        "pro_tips_box": {
            "bg_color":     "#FFF8F2",
            "border_color": "#F07C33",
            "border_left":  "5px solid #F07C33",
            "padding":      "1.25rem 1.5rem",
        },
        "recipe_card": {
            "bg":             "#FFFFFF",
            "border":         "1px solid #E0E0E0",
            "border_radius":  "10px",
            "padding":        "1.75rem",
            "meta_icon_color":"#F07C33",
        },
    },
    "images": {
        "main_article_image":  "",
        "ingredient_image":    "",
        "recipe_card_image":   "",
    },
    "structure_template": {
        "word_counts": {
            "intro":                    120,
            "why_i_love_intro":          30,
            "why_i_love_item_1":         25,
            "why_i_love_item_2":         25,
            "why_i_love_item_3":         25,
            "why_i_love_item_4":         25,
            "ingredients_intro":         60,
            "instructions_intro":        30,
            "instructions_step_1":       80,
            "instructions_step_2":       80,
            "instructions_step_3":       80,
            "instructions_step_4":       80,
            "instructions_step_5":       80,
            "instructions_step_6":       80,
            "pro_tips_intro":            25,
            "pro_tip_1":                 30,
            "pro_tip_2":                 30,
            "pro_tip_3":                 30,
            "pro_tip_4":                 30,
            "pro_tip_5":                 30,
            "pro_tip_6":                 30,
            "equipment_intro":           25,
            "ingredients_note":          70,
            "serving_suggestions":       65,
            "conclusion":                85,
            "faq_1_question":            12,
            "faq_1_answer":              55,
            "faq_2_question":            12,
            "faq_2_answer":              55,
            "faq_3_question":            12,
            "faq_3_answer":              55,
        }
    },
    "dark_mode": False,
}

# ---------------------------------------------------------------------------
# STRUCTURE TEMPLATE
# ---------------------------------------------------------------------------
STRUCTURE = [
    {"key": "intro",                 "type": "intro",         "label": "Introduction"},
    {"key": "why_i_love_intro",      "type": "h2",            "label": "Why You'll Love This"},
    {"key": "why_i_love_item_1",     "type": "bullet_list",   "label": ""},
    {"key": "why_i_love_item_2",     "type": "bullet_list",   "label": ""},
    {"key": "why_i_love_item_3",     "type": "bullet_list",   "label": ""},
    {"key": "why_i_love_item_4",     "type": "bullet_list",   "label": ""},
    {"key": "ingredients_intro",     "type": "h2",            "label": "Ingredients"},
    {"key": "instructions_intro",    "type": "h2",            "label": "How to Make {title}"},
    {"key": "instructions_step_1",   "type": "h3",            "label": "Step 1"},
    {"key": "instructions_step_2",   "type": "h3",            "label": "Step 2"},
    {"key": "instructions_step_3",   "type": "h3",            "label": "Step 3"},
    {"key": "instructions_step_4",   "type": "h3",            "label": "Step 4"},
    {"key": "instructions_step_5",   "type": "h3",            "label": "Step 5"},
    {"key": "instructions_step_6",   "type": "h3",            "label": "Step 6"},
    {"key": "pro_tips_intro",        "type": "pro_tips_box",  "label": "Pro Tips"},
    {"key": "pro_tip_1",             "type": "bullet_list",   "label": ""},
    {"key": "pro_tip_2",             "type": "bullet_list",   "label": ""},
    {"key": "pro_tip_3",             "type": "bullet_list",   "label": ""},
    {"key": "pro_tip_4",             "type": "bullet_list",   "label": ""},
    {"key": "pro_tip_5",             "type": "bullet_list",   "label": ""},
    {"key": "pro_tip_6",             "type": "bullet_list",   "label": ""},
    {"key": "equipment_intro",       "type": "h2",            "label": "Equipment Needed"},
    {"key": "ingredients_note",      "type": "h2",            "label": "Ingredient Notes"},
    {"key": "serving_suggestions",   "type": "h2",            "label": "Serving Suggestions"},
    {"key": "conclusion",            "type": "conclusion",    "label": "Final Thoughts"},
    {"key": "faq_1_question",        "type": "faq",           "label": "FAQ"},
    {"key": "faq_1_answer",          "type": "faq",           "label": ""},
    {"key": "faq_2_question",        "type": "faq",           "label": ""},
    {"key": "faq_2_answer",          "type": "faq",           "label": ""},
    {"key": "faq_3_question",        "type": "faq",           "label": ""},
    {"key": "faq_3_answer",          "type": "faq",           "label": ""},
]


# ---------------------------------------------------------------------------
# GENERATOR CLASS
# ---------------------------------------------------------------------------
class ArticleGenerator:

    def __init__(self, config_override: dict = None):
        self.config = dict(CONFIG)
        if config_override:
            self._merge(self.config, config_override)
        self._validate_config()
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
        self.title = self.config["title"].strip()
        self.slug  = self._slugify(self.title)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _merge(self, base: dict, override: dict):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._merge(base[k], v)
            else:
                base[k] = v

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = re.sub(r"\s+", "-", text.strip())
        return text or "article"

    def _validate_config(self):
        required_top = ["title", "colors", "fonts", "layout", "components", "images",
                        "structure_template", "categories_list"]
        for key in required_top:
            if key not in self.config:
                raise KeyError(f"CONFIG missing required key: {key}")

    def _chat(self, prompt: str, max_tokens: int = 600) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": (
                    "You are an expert food blogger and SEO copywriter. "
                    "Write natural, engaging, human-like content. "
                    "Never use markdown formatting in your response unless instructed. "
                    "Output plain text only unless HTML is explicitly requested."
                )},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # content generation helpers
    # ------------------------------------------------------------------
    def _gen_intro(self) -> str:
        return self._chat(
            f"Write a compelling 120-word introduction paragraph for a food blog article about {self.title}. "
            "Hook the reader immediately. No markdown, no headers, plain text only.",
            300
        )

    def _gen_why_i_love_items(self) -> list:
        raw = self._chat(
            f"List exactly 4 reasons why readers will love making {self.title}. "
            "Each reason: one bold phrase (5 words max) followed by a colon and one sentence explanation. "
            "Output each reason on its own line. No bullets, no numbers.",
            250
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        while len(lines) < 4:
            lines.append(f"Easy to Make: {self.title} comes together quickly with simple steps.")
        return lines[:4]

    def _gen_ingredients_intro(self) -> str:
        return self._chat(
            f"Write a 60-word intro paragraph for the ingredients section of a recipe article about {self.title}. "
            "Mention that the ingredients are simple and easy to find. Plain text, no lists.",
            150
        )

    def _gen_ingredient_list(self) -> list:
        raw = self._chat(
            f"List exactly 10 ingredients needed to make {self.title}. "
            "Format: quantity + ingredient, one per line. No headers, no bullets.",
            200
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        return lines[:10] if lines else [f"Ingredient {i+1}" for i in range(10)]

    def _gen_step(self, step_num: int, step_label: str) -> dict:
        raw = self._chat(
            f"Write step {step_num} for making {self.title}. "
            f"Step heading (5 words max, action verb first): then write an 80-word paragraph describing what to do. "
            "Format your response as:\nHEADING: <heading text>\nBODY: <paragraph text>",
            250
        )
        heading = f"Step {step_num}"
        body    = raw
        for line in raw.splitlines():
            if line.startswith("HEADING:"):
                heading = line.replace("HEADING:", "").strip()
            elif line.startswith("BODY:"):
                body = line.replace("BODY:", "").strip()
        # fallback: if parsing didn't work use generic
        if heading == raw:
            heading = f"Step {step_num}"
        return {"heading": heading, "body": body}

    def _strip_markdown(self, text: str) -> str:
        """Remove ###, **, * so content is safe for HTML."""
        if not text or not isinstance(text, str):
            return text
        s = str(text).strip()
        s = re.sub(r'^#{1,6}\s*', '', s)
        s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'\*([^*]+)\*', r'\1', s)
        return s.strip()

    def _gen_pro_tips(self) -> list:
        raw = self._chat(
            f"Give exactly 6 pro cooking tips for making the best {self.title}. "
            "Each tip: one short phrase (5 words max) followed by a colon and one sentence. "
            "Output each tip on its own line. Plain text only: no markdown (no **, no ###).",
            300
        )
        lines = [self._strip_markdown(l.strip()) for l in raw.splitlines() if l.strip()]
        while len(lines) < 6:
            lines.append(f"Season Generously: Proper seasoning elevates {self.title} to restaurant quality.")
        return lines[:6]

    def _gen_equipment_list(self) -> list:
        raw = self._chat(
            f"List exactly 5 kitchen tools or equipment needed to make {self.title}. "
            "One item per line. No bullets, no numbers, no descriptions.",
            100
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        return lines[:5] if lines else ["Large pot", "Skillet", "Wooden spoon", "Colander", "Chef's knife"]

    def _gen_ingredients_note(self) -> str:
        return self._chat(
            f"Write a 70-word paragraph with ingredient notes and substitution ideas for {self.title}. "
            "Plain text only.",
            200
        )

    def _gen_serving_suggestions(self) -> str:
        return self._chat(
            f"Write a 65-word paragraph with serving suggestions and pairing ideas for {self.title}. "
            "Plain text only.",
            180
        )

    def _gen_conclusion(self) -> str:
        return self._chat(
            f"Write an 85-word conclusion paragraph for a food blog article about {self.title}. "
            "Encourage readers to try the recipe and leave a comment. Plain text only.",
            220
        )

    def _gen_faqs(self) -> list:
        raw = self._chat(
            f"Write exactly 3 real FAQ questions and answers about {self.title}. "
            "Each question must be specific (e.g. 'Can I use frozen chicken?'). Each answer ~55 words with real advice. "
            "NEVER use placeholder text like 'Question about X?' or 'Answer about X.' or 'Please see the recipe above'. "
            "Format:\nQ1: <question>\nA1: <55-word answer>\nQ2: <question>\nA2: <55-word answer>\nQ3: <question>\nA3: <55-word answer>",
            450
        )
        faqs = []
        for i in range(1, 4):
            q, a = None, None
            for line in raw.splitlines():
                stripped = line.strip()
                if stripped.lower().startswith(f"q{i}:"):
                    q = line.split(":", 1)[-1].strip()
                elif stripped.lower().startswith(f"a{i}:"):
                    a = line.split(":", 1)[-1].strip()
            # Reject placeholder-like content
            if not q or "question about" in (q or "").lower():
                q = f"What is the best way to store leftovers of {self.title}?"
            if not a or "answer about" in (a or "").lower() or "please see the recipe" in (a or "").lower():
                a = self._chat(f"Answer this FAQ in ~55 words: {q}", 120)
            faqs.append({"question": q, "answer": a or ""})
        return faqs

    def _gen_recipe(self) -> dict:
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": self.title,
                "summary": f"A delicious {self.title} recipe.",
                "ingredients": [],
                "instructions": [],
                "prep_time": "15 mins",
                "cook_time": "30 mins",
                "total_time": "45 mins",
                "servings": "4",
                "calories": "450",
                "course": "Main Course",
                "cuisine": "American",
            }
            return {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        raw = self._chat(
            f"Create a structured recipe for {self.title} in JSON format with these exact keys: "
            "name, summary, ingredients (array of strings), instructions (array of strings), "
            "prep_time, cook_time, total_time, servings, calories, course, cuisine. "
            "Output valid JSON only, no markdown fences.",
            600
        )
        try:
            clean = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
            return json.loads(clean)
        except Exception:
            return {
                "name": self.title,
                "summary": f"A delicious {self.title} recipe.",
                "ingredients": [],
                "instructions": [],
                "prep_time": "15 mins",
                "cook_time": "30 mins",
                "total_time": "45 mins",
                "servings": "4",
                "calories": "450",
                "course": "Main Course",
                "cuisine": "American",
            }

    def _gen_seo(self) -> dict:
        raw = self._chat(
            f"Generate SEO fields for a food blog post about {self.title}. "
            "Output JSON with keys: recipe_title_pin (<=100 chars), pinterest_title (<=100 chars), "
            "pinterest_description (2-3 sentences), pinterest_keywords (6 comma-separated keywords), "
            "focus_keyphrase (concise phrase), meta_description (120-140 chars), "
            "keyphrase_synonyms (comma-separated). Output valid JSON only, no markdown.",
            400
        )
        defaults = {
            "recipe_title_pin":       self.title[:100],
            "pinterest_title":        self.title[:100],
            "pinterest_description":  f"This {self.title} recipe is easy and delicious.",
            "pinterest_keywords":     f"{self.title}, recipe, easy, dinner, homemade, delicious",
            "focus_keyphrase":        self.title.lower(),
            "meta_description":       f"Learn how to make {self.title} with this easy step-by-step recipe.",
            "keyphrase_synonyms":     f"{self.title} recipe, homemade {self.title}, easy {self.title}",
        }
        try:
            clean = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
            data  = json.loads(clean)
            defaults.update({k: v for k, v in data.items() if k in defaults})
        except Exception:
            pass
        return defaults

    def _gen_midjourney(self) -> dict:
        main = self._chat(
            f"Write a Midjourney image prompt for a food photography shot of {self.title}. "
            "Include lighting, angle, style details. End with --v 6.1",
            120
        )
        ingr = self._chat(
            f"Write a Midjourney image prompt for a flat-lay of raw ingredients for {self.title}. "
            "Include lighting and style. End with --v 6.1",
            120
        )
        if "--v 6.1" not in main:
            main += " --v 6.1"
        if "--v 6.1" not in ingr:
            ingr += " --v 6.1"
        return {"main": main, "ingredients": ingr}

    def _extract_json(self, raw: str) -> dict:
        if not raw:
            return {}
        text = (raw or "").strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m:
            text = m.group(1).strip()
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
        try:
            return json.loads(text)
        except Exception:
            return {}

    # ------------------------------------------------------------------
    # content assembly
    # ------------------------------------------------------------------
    def generate_content(self) -> dict:
        from ai_client import ai_chat, get_first_category
        existing = self.config.get("recipe")
        recipe_from_config = existing and isinstance(existing, dict) and (existing.get("ingredients") or existing.get("instructions"))
        
        schema = {
            "intro": "string ~120 words",
            "why_i_love_items": "array of 4 strings (Label: sentence)",
            "ingredients_intro": "string ~60 words",
            "ingredient_list": "array of 10 strings",
            "steps": "array of 6 objects with heading and body",
            "pro_tips": "array of 6 strings",
            "equipment_list": "array of 5 strings",
            "ingredients_note": "string ~70 words",
            "serving_suggestions": "string ~65 words",
            "conclusion": "string ~85 words",
            "faqs": "array of 3 objects with question and answer",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine" if not recipe_from_config else "(omit)",
            "meta_description": "120-140 chars",
            "focus_keyphrase": "string",
            "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        
        system = "You are an expert food blogger and SEO copywriter. Generate the full article as ONE JSON. Plain text only: no markdown. All content only about the recipe title."
        user = f"Generate the complete food blog article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=5000, system=system)
        data = self._extract_json(raw)
        
        if data:
            print("[*] Generated content via single JSON.")
            intro = self._strip_markdown(str(data.get("intro", "")))
            why_items = [self._strip_markdown(str(x)) for x in (data.get("why_i_love_items") or [])[:4]]
            ing_intro = self._strip_markdown(str(data.get("ingredients_intro", "")))
            ing_list = [str(x).strip() for x in (data.get("ingredient_list") or [])[:12]]
            steps_raw = data.get("steps") or []
            steps = [{"heading": str(s.get("heading", f"Step {i}")).strip() if isinstance(s, dict) else f"Step {i}", "body": self._strip_markdown(str(s.get("body", "")) if isinstance(s, dict) else "")} for i, s in enumerate(steps_raw[:6], 1)]
            tips = [self._strip_markdown(str(x)) for x in (data.get("pro_tips") or [])[:6]]
            equip = [self._strip_markdown(str(x)) for x in (data.get("equipment_list") or [])[:5]]
            ing_note = self._strip_markdown(str(data.get("ingredients_note", "")))
            serving = self._strip_markdown(str(data.get("serving_suggestions", "")))
            conclusion = self._strip_markdown(str(data.get("conclusion", "")))
            faqs_raw = data.get("faqs") or []
            faqs = [{"question": str(f.get("question", "")).strip(), "answer": self._strip_markdown(str(f.get("answer", "")))} for f in faqs_raw[:3] if isinstance(f, dict)]
            
            if recipe_from_config:
                defaults = {"name": self.title, "summary": f"A delicious {self.title} recipe.", "ingredients": [], "instructions": [], "prep_time": "15 mins", "cook_time": "30 mins", "total_time": "45 mins", "servings": "4", "calories": "450", "course": "Main Course", "cuisine": "American"}
                recipe = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
            else:
                recipe = data.get("recipe") or {}
                if not isinstance(recipe, dict):
                    recipe = {"name": self.title, "summary": f"A delicious {self.title} recipe.", "ingredients": ing_list[:20] if ing_list else [], "instructions": [s.get("body", "") for s in steps][:15] if steps else [], "prep_time": "15 mins", "cook_time": "30 mins", "total_time": "45 mins", "servings": "4", "calories": "450", "course": "Main Course", "cuisine": "American"}
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            
            seo = {
                "recipe_title_pin": (str(data.get("pinterest_title", self.title)) or self.title)[:100],
                "pinterest_title": (str(data.get("pinterest_title", "")) or self.title)[:100],
                "pinterest_description": f"This {self.title} recipe is easy and delicious.",
                "pinterest_keywords": f"{self.title}, recipe, easy, dinner, homemade, delicious",
                "focus_keyphrase": str(data.get("focus_keyphrase", self.title.lower())),
                "meta_description": (str(data.get("meta_description", "")) or f"Learn how to make {self.title} with this easy step-by-step recipe.")[:140],
                "keyphrase_synonyms": f"{self.title} recipe, homemade {self.title}, easy {self.title}"
            }
            mj_main = str(data.get("prompt_midjourney_main", "") or "").strip()
            mj_ing = str(data.get("prompt_midjourney_ingredients", "") or "").strip()
            mj = {
                "main": mj_main if mj_main and "--v 6.1" in mj_main else f"Food photography shot of {self.title} --v 6.1",
                "ingredients": mj_ing if mj_ing and "--v 6.1" in mj_ing else f"Flat-lay of raw ingredients for {self.title} --v 6.1"
            }
        else:
            print("[*] Generating intro...")
            intro = self._gen_intro()
            print("[*] Generating why-i-love items...")
            why_items = self._gen_why_i_love_items()
            print("[*] Generating ingredients...")
            ing_intro = self._gen_ingredients_intro()
            ing_list  = self._gen_ingredient_list()
            print("[*] Generating steps 1-6...")
            steps = [self._gen_step(i, f"Step {i}") for i in range(1, 7)]
            print("[*] Generating pro tips...")
            tips = self._gen_pro_tips()
            print("[*] Generating equipment list...")
            equip = self._gen_equipment_list()
            print("[*] Generating ingredient notes...")
            ing_note = self._gen_ingredients_note()
            print("[*] Generating serving suggestions...")
            serving = self._gen_serving_suggestions()
            print("[*] Generating conclusion...")
            conclusion = self._gen_conclusion()
            print("[*] Generating FAQs...")
            faqs = self._gen_faqs()
            print("[*] Generating recipe card data...")
            recipe = self._gen_recipe()
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            print("[*] Generating SEO fields...")
            seo = self._gen_seo()
            print("[*] Generating Midjourney prompts...")
            mj  = self._gen_midjourney()

        cat = get_first_category(self.config)

        main_img = self.config["images"].get("main_article_image") or "placeholder.jpg"
        ingr_img = self.config["images"].get("ingredient_image")    or "placeholder.jpg"

        sections = [
            {"key": "intro",               "content": intro},
            {"key": "why_i_love_items",    "content": why_items},
            {"key": "ingredients_intro",   "content": ing_intro},
            {"key": "ingredient_list",     "content": ing_list},
            {"key": "instructions_steps",  "content": steps},
            {"key": "pro_tips",            "content": tips},
            {"key": "equipment_list",      "content": equip},
            {"key": "ingredients_note",    "content": ing_note},
            {"key": "serving_suggestions", "content": serving},
            {"key": "conclusion",          "content": conclusion},
            {"key": "faqs",                "content": faqs},
        ]

        content_data = {
            "title":                    self.title,
            "slug":                     self.slug,
            "categorieId":              str(cat.get("id", 1)),
            "categorie":                cat.get("categorie", "dinner"),
            "sections":                 sections,
            "article_html":             "",
            "article_css":              "",
            "prompt_used":              f"Generated for: {self.title}",
            "prompt_base":              f"Food blog article generator for {self.title}",
            "recipe":                   recipe,
            "recipe_title_pin":         seo["recipe_title_pin"],
            "pinterest_title":          seo["pinterest_title"],
            "pinterest_description":    seo["pinterest_description"],
            "pinterest_keywords":       seo["pinterest_keywords"],
            "focus_keyphrase":          seo["focus_keyphrase"],
            "meta_description":         seo["meta_description"],
            "keyphrase_synonyms":       seo["keyphrase_synonyms"],
            "main_image":               main_img,
            "ingredient_image":         ingr_img,
            "prompt_midjourney_main":   mj["main"],
            "prompt_midjourney_ingredients": mj["ingredients"],
        }
        return content_data

    # ------------------------------------------------------------------
    # CSS generation
    # ------------------------------------------------------------------
    def generate_css(self) -> str:
        c  = self.config["colors"]
        f  = self.config["fonts"]
        l  = self.config["layout"]
        cp = self.config["components"]

        nl   = cp["numbered_list"]
        bl   = cp["bullet_list"]
        ptb  = cp["pro_tips_box"]
        rc   = cp["recipe_card"]

        return f"""/* === generator-6 article styles === */

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
    font-weight: {f['body']['weight']};
    line-height: {f['body']['line_height']};
}}

.article-container {{
    max-width: {l['max_width']};
    margin: 0 auto;
    padding: {l['container_padding']};
    background: {c['container_bg']};
}}

.article-header.g6-header {{
    margin-bottom: 1.5rem;
}}
.article-header.g6-header .article-title {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 800;
    color: {c['text_primary']};
    margin: 0 0 0.75rem 0;
    line-height: 1.25;
}}
.article-header.g6-header .article-byline-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}}
.article-header.g6-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g6-header .byline-author {{ font-weight: 600; color: {c['text_primary']}; font-size: 0.95rem; }}
.article-header.g6-header .byline-date {{ font-size: 0.875rem; color: {c['text_secondary']}; }}
.article-header.g6-header .byline-disclaimer {{ font-size: 0.8rem; color: {c['text_secondary']}; font-style: italic; margin-top: 0.2rem; }}
.article-header.g6-header .byline-right {{ display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }}
.article-header.g6-header .recipe-meta-row {{ display: flex; gap: 1rem; font-size: 0.9rem; color: {c['text_secondary']}; }}

/* --- Breadcrumb --- */
.breadcrumb {{
    font-size: 0.8rem;
    color: {c['text_secondary']};
    margin-bottom: 1.2rem;
}}

.breadcrumb a {{
    color: {c['link']};
    text-decoration: none;
}}

.breadcrumb a:hover {{
    text-decoration: underline;
}}

.breadcrumb span {{
    margin: 0 0.35rem;
}}

/* --- Typography --- */
h1 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 800;
    color: {c['text_primary']};
    line-height: 1.25;
    margin-bottom: 1rem;
}}

h2 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h2']};
    font-weight: 700;
    color: {c['text_primary']};
    margin-top: {l['section_spacing']};
    margin-bottom: 0.9rem;
    padding-bottom: 0.35rem;
    border-bottom: 2px solid {c['border']};
}}

h3 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h3']};
    font-weight: 700;
    color: {c['text_primary']};
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}}

p {{
    color: {c['text_secondary']};
    margin-bottom: {l['paragraph_spacing']};
}}

a {{
    color: {c['link']};
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

/* --- Jump Links Box --- */
.jump-links {{
    background: #f8f8f8;
    border: 1px solid {c['border']};
    border-radius: {l['border_radius']};
    padding: 1rem 1.4rem;
    margin: 1.5rem 0;
}}

.jump-links h4 {{
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.6rem;
    color: {c['text_primary']};
}}

.jump-links ul {{
    list-style: none;
    padding: 0;
    margin: 0;
    columns: 2;
}}

.jump-links ul li {{
    margin-bottom: 0.35rem;
}}

.jump-links ul li a {{
    color: {c['link']};
    font-size: 0.88rem;
}}

/* --- Hero image --- */
.hero-image {{
    width: 100%;
    height: auto;
    border-radius: {l['border_radius']};
    margin: 1.2rem 0;
    display: block;
    object-fit: cover;
    max-height: 480px;
}}

/* --- Ingredient image --- */
.ingredient-image {{
    width: 100%;
    height: auto;
    border-radius: {l['border_radius']};
    margin: 1.2rem 0;
    display: block;
}}

/* --- Bullet list (why-love, etc.) --- */
.why-love-list {{
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 1rem;
}}

.why-love-list li {{
    padding: 0.45rem 0 0.45rem 1.5rem;
    position: relative;
    color: {c['text_secondary']};
    margin-bottom: {l['list_spacing']};
}}

.why-love-list li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: {c['list_marker']};
}}

.why-love-list li strong {{
    color: {c['text_primary']};
}}

/* --- Ingredient list --- */
.ingredient-list {{
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 1rem;
    columns: 2;
    column-gap: 2rem;
}}

.ingredient-list li {{
    padding: 0.35rem 0 0.35rem 1.4rem;
    position: relative;
    color: {c['text_secondary']};
    margin-bottom: {l['list_spacing']};
    break-inside: avoid;
}}

.ingredient-list li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: {c['list_marker']};
}}

/* --- Numbered steps --- */
.step-item {{
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    margin-bottom: 1.5rem;
}}

.step-number {{
    flex-shrink: 0;
    width: {nl['circle_size']};
    height: {nl['circle_size']};
    border-radius: 50%;
    background: {nl['circle_bg']};
    color: {nl['circle_color']};
    font-weight: 700;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 0.15rem;
}}

.step-content h3 {{
    margin-top: 0;
    margin-bottom: 0.35rem;
    font-size: 1.05rem;
}}

.step-content p {{
    margin: 0;
}}

/* --- Pro Tips Box --- */
.pro-tips-box {{
    background: {ptb['bg_color']};
    border-left: {ptb['border_left']};
    border-radius: 0 {l['border_radius']} {l['border_radius']} 0;
    padding: {ptb['padding']};
    margin: {l['section_spacing']} 0;
}}

.pro-tips-box h2 {{
    border: none;
    margin-top: 0;
    margin-bottom: 0.8rem;
    color: {c['primary']};
    font-size: 1.2rem;
}}

.pro-tips-list {{
    list-style: none;
    padding: 0;
    margin: 0;
}}

.pro-tips-list li {{
    padding: 0.4rem 0 0.4rem 1.5rem;
    position: relative;
    color: {c['text_secondary']};
    margin-bottom: {l['list_spacing']};
}}

.pro-tips-list li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {c['primary']};
}}

.pro-tips-list li strong {{
    color: {c['text_primary']};
}}

/* --- Equipment list --- */
.equipment-list {{
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 1rem;
}}

.equipment-list li {{
    padding: 0.4rem 0 0.4rem 1.5rem;
    position: relative;
    color: {c['text_secondary']};
    margin-bottom: {l['list_spacing']};
}}

.equipment-list li::before {{
    content: "-";
    position: absolute;
    left: 0;
    color: {c['primary']};
    font-weight: 700;
}}

/* --- Recipe Card --- */
.recipe-card {{
    background: {rc['bg']};
    border: {rc['border']};
    border-radius: {rc['border_radius']};
    padding: {rc['padding']};
    margin: {l['section_spacing']} 0;
    box-shadow: {l['box_shadow']};
}}

.recipe-card__title {{
    font-family: {f['heading']['family']};
    font-size: 1.35rem;
    font-weight: 800;
    color: {c['text_primary']};
    margin-bottom: 0.5rem;
}}

.recipe-card__summary {{
    color: {c['text_secondary']};
    font-size: 0.9rem;
    margin-bottom: 1rem;
}}

.recipe-card__image {{
    width: 100%;
    height: auto;
    border-radius: 6px;
    margin-bottom: 1rem;
    max-height: 320px;
    object-fit: cover;
    display: block;
}}

.recipe-card__meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem 1.5rem;
    border-top: 1px solid {c['border']};
    border-bottom: 1px solid {c['border']};
    padding: 0.85rem 0;
    margin-bottom: 1.2rem;
}}

.recipe-card__meta-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 0.8rem;
    color: {c['text_secondary']};
    gap: 0.15rem;
}}

.recipe-card__meta-label {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {c['text_secondary']};
    opacity: 0.8;
}}

.recipe-card__meta-value {{
    font-weight: 700;
    color: {c['text_primary']};
    font-size: 0.9rem;
}}

.recipe-card__meta-icon {{
    font-size: 1rem;
    color: {rc['meta_icon_color']};
}}

.recipe-card__section-title {{
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {c['text_primary']};
    margin: 1rem 0 0.5rem;
}}

.recipe-card__ingredient-list {{
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
    columns: 2;
    column-gap: 1.5rem;
}}

.recipe-card__ingredient-list li {{
    padding: 0.25rem 0 0.25rem 1.2rem;
    position: relative;
    font-size: 0.88rem;
    color: {c['text_secondary']};
    break-inside: avoid;
}}

.recipe-card__ingredient-list li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: {c['list_marker']};
}}

.recipe-card__instruction-list {{
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
    counter-reset: rc-step;
}}

.recipe-card__instruction-list li {{
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    margin-bottom: 0.7rem;
    font-size: 0.88rem;
    color: {c['text_secondary']};
    counter-increment: rc-step;
}}

.recipe-card__instruction-list li::before {{
    content: counter(rc-step);
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: {c['primary']};
    color: #fff;
    font-size: 0.72rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1px;
}}

/* --- Card buttons --- */
.recipe-card__buttons {{
    display: flex;
    gap: 0.75rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}}

.btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.55rem 1.2rem;
    border: none;
    border-radius: {l['border_radius']};
    font-size: 0.85rem;
    font-weight: 700;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.2s ease;
}}

.btn-print {{
    background: {c['button_print']};
    color: #fff;
}}

.btn-print:hover {{
    background: {c['button_hover_print']};
    color: #fff;
    text-decoration: none;
}}

.btn-pin {{
    background: {c['button_pin']};
    color: #fff;
}}

.btn-pin:hover {{
    background: {c['button_hover_pin']};
    color: #fff;
    text-decoration: none;
}}

/* --- FAQ --- */
.faq-section {{
    margin-top: {l['section_spacing']};
}}

.faq-item {{
    border-bottom: 1px solid {c['border']};
    padding: 1rem 0;
}}

.faq-item:last-child {{
    border-bottom: none;
}}

.faq-question {{
    font-weight: 700;
    font-size: 1rem;
    color: {c['text_primary']};
    margin-bottom: 0.4rem;
}}

.faq-answer {{
    color: {c['text_secondary']};
    font-size: 0.95rem;
}}

/* --- Social share --- */
.social-share {{
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: {l['section_spacing']};
    padding-top: 1.2rem;
    border-top: 2px solid {c['border']};
}}

.social-share__label {{
    font-size: 0.85rem;
    font-weight: 700;
    color: {c['text_secondary']};
    align-self: center;
    margin-right: 0.5rem;
}}

.social-share__btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.45rem 1rem;
    border-radius: {l['border_radius']};
    font-size: 0.82rem;
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    transition: opacity 0.2s;
}}

.social-share__btn:hover {{
    opacity: 0.88;
    text-decoration: none;
    color: #fff;
}}

.social-share__btn--facebook {{ background: #1877F2; }}
.social-share__btn--twitter  {{ background: #1DA1F2; }}
.social-share__btn--pinterest {{ background: #E60023; }}

/* --- Responsive --- */
@media (max-width: 600px) {{
    .ingredient-list,
    .recipe-card__ingredient-list {{
        columns: 1;
    }}
    .jump-links ul {{
        columns: 1;
    }}
    h1 {{
        font-size: 1.55rem;
    }}
    h2 {{
        font-size: 1.25rem;
    }}
}}
"""

    # ------------------------------------------------------------------
    # HTML generation
    # ------------------------------------------------------------------
    def generate_html(self, content_data: dict, css_filename: str = "css.css") -> str:
        title      = content_data["title"]
        meta_desc  = content_data.get("meta_description", "")
        sections   = {s["key"]: s["content"] for s in content_data["sections"]}
        recipe     = content_data.get("recipe", {})
        main_img   = content_data.get("main_image", "placeholder.jpg")
        ingr_img   = content_data.get("ingredient_image", "placeholder.jpg")
        card_img   = self.config["images"].get("recipe_card_image") or main_img
        faqs       = sections.get("faqs", [])
        steps      = sections.get("instructions_steps", [])
        why_items  = sections.get("why_i_love_items", [])
        tips       = sections.get("pro_tips", [])
        equip      = sections.get("equipment_list", [])
        ing_list   = sections.get("ingredient_list", [])
        cat        = content_data.get("categorie", "dinner").capitalize()

        def escape(text: str) -> str:
            return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        def para(text: str) -> str:
            return f'<p>{escape(text)}</p>'

        # Jump links
        jump_items = [
            ("why-i-love",         "Why You'll Love This"),
            ("ingredients",        "Ingredients"),
            ("how-to-make",        "How to Make"),
            ("pro-tips",           "Pro Tips"),
            ("equipment",          "Equipment Needed"),
            ("ingredient-notes",   "Ingredient Notes"),
            ("serving",            "Serving Suggestions"),
            ("recipe-card",        "Recipe Card"),
            ("faqs",               "FAQs"),
            ("conclusion",         "Final Thoughts"),
        ]
        jump_html = "\n".join(
            f'<li><a href="#{aid}">{escape(label)}</a></li>'
            for aid, label in jump_items
        )

        # Why love items
        why_html = "\n".join(
            f'<li>{escape(item)}</li>' for item in why_items
        )

        # Ingredient list
        ing_html = "\n".join(
            f'<li>{escape(item)}</li>' for item in ing_list
        )

        # Steps
        steps_html_parts = []
        for i, step in enumerate(steps, 1):
            sh = escape(step.get("heading", f"Step {i}"))
            sb = escape(step.get("body", ""))
            steps_html_parts.append(f"""
    <div class="step-item">
        <div class="step-number">{i}</div>
        <div class="step-content">
            <h3>{sh}</h3>
            <p>{sb}</p>
        </div>
    </div>""")
        steps_html = "\n".join(steps_html_parts)

        # Pro tips — strip markdown so no ### or ** appears
        tips_html = "\n".join(
            f'<li>{escape(self._strip_markdown(str(tip)))}</li>' for tip in tips
        )

        # Equipment
        equip_html = "\n".join(
            f'<li>{escape(item)}</li>' for item in equip
        )

        # Recipe card
        rc_ing = "\n".join(
            f'<li>{escape(str(item))}</li>'
            for item in recipe.get("ingredients", [])
        )
        rc_ins = "\n".join(
            f'<li>{escape(str(step))}</li>'
            for step in recipe.get("instructions", [])
        )

        # FAQ
        faq_html = ""
        for faq in faqs:
            faq_html += f"""
    <div class="faq-item">
        <div class="faq-question">{escape(faq.get('question',''))}</div>
        <div class="faq-answer">{escape(faq.get('answer',''))}</div>
    </div>"""

        slug = content_data.get("slug", "article")
        share_url = f"https://yoursite.com/{slug}/"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{escape(meta_desc)}" />
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{css_filename}" />
</head>
<body>
<div class="article-container">

    <!-- Breadcrumb -->
    <nav class="breadcrumb">
        <a href="/">Home</a>
        <span>/</span>
        <a href="/{cat.lower()}/">{escape(cat)}</a>
        <span>/</span>
        <span>{escape(title)}</span>
    </nav>

    <header class="article-header g6-header">
        <h1 class="article-title">{escape(title)}</h1>
        <div class="article-byline-row">
            <div class="byline-left">
                <span class="byline-author">By <span class="article-author"></span></span>
                <span class="byline-date">Published <span class="article-date"></span></span>
                <p class="byline-disclaimer">This post may contain affiliate links.</p>
            </div>
            <div class="byline-right">
                <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
                <div class="recipe-meta-row"><span>{escape(recipe.get("prep_time", ""))} prep</span><span>{escape(recipe.get("cook_time", ""))} cook</span><span>{escape(str(recipe.get("servings", "")))} servings</span></div>
            </div>
        </div>
    </header>

    <!-- Hero image -->
    <img class="hero-image" src="{escape(main_img)}" alt="{escape(title)}" width="780" height="480" loading="eager" />

    <!-- Intro -->
    <section id="intro">
        {para(sections.get('intro', ''))}
    </section>

    <!-- Jump links -->
    <div class="jump-links">
        <h4>Jump to Section</h4>
        <ul>
{jump_html}
        </ul>
    </div>

    <!-- Why You'll Love This -->
    <section id="why-i-love">
        <h2>Why You'll Love This</h2>
        <ul class="why-love-list">
{why_html}
        </ul>
    </section>

    <!-- Ingredients -->
    <section id="ingredients">
        <h2>Ingredients</h2>
        <p>{escape(sections.get('ingredients_intro', ''))}</p>
        <img class="ingredient-image" src="{escape(ingr_img)}" alt="Ingredients for {escape(title)}" loading="lazy" />
        <ul class="ingredient-list">
{ing_html}
        </ul>
    </section>

    <!-- How to Make -->
    <section id="how-to-make">
        <h2>How to Make {escape(title)}</h2>
        <p>{escape(sections.get('instructions_intro', ''))}</p>
{steps_html}
    </section>

    <!-- Pro Tips -->
    <section id="pro-tips">
        <div class="pro-tips-box">
            <h2>Pro Tips</h2>
            <ul class="pro-tips-list">
{tips_html}
            </ul>
        </div>
    </section>

    <!-- Equipment Needed -->
    <section id="equipment">
        <h2>Equipment Needed</h2>
        <ul class="equipment-list">
{equip_html}
        </ul>
    </section>

    <!-- Ingredient Notes -->
    <section id="ingredient-notes">
        <h2>Ingredient Notes</h2>
        {para(sections.get('ingredients_note', ''))}
    </section>

    <!-- Serving Suggestions -->
    <section id="serving">
        <h2>Serving Suggestions</h2>
        {para(sections.get('serving_suggestions', ''))}
    </section>

    <!-- Recipe Card -->
    <section id="recipe-card">
        <div class="recipe-card">
            <div class="recipe-card__title">{escape(recipe.get('name', title))}</div>
            <div class="recipe-card__summary">{escape(recipe.get('summary', ''))}</div>
            <img class="recipe-card__image" src="{escape(card_img)}" alt="{escape(recipe.get('name', title))}" loading="lazy" />
            <div class="recipe-card__buttons">
                <button class="btn btn-print" onclick="window.print()">Print Recipe</button>
                <button class="btn btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Save to Pinterest</button>
            </div>
            <div class="recipe-card__meta">
                <div class="recipe-card__meta-item">
                    <span class="recipe-card__meta-label">Prep Time</span>
                    <span class="recipe-card__meta-value">{escape(str(recipe.get('prep_time', '15 mins')))}</span>
                </div>
                <div class="recipe-card__meta-item">
                    <span class="recipe-card__meta-label">Cook Time</span>
                    <span class="recipe-card__meta-value">{escape(str(recipe.get('cook_time', '30 mins')))}</span>
                </div>
                <div class="recipe-card__meta-item">
                    <span class="recipe-card__meta-label">Total Time</span>
                    <span class="recipe-card__meta-value">{escape(str(recipe.get('total_time', '45 mins')))}</span>
                </div>
                <div class="recipe-card__meta-item">
                    <span class="recipe-card__meta-label">Servings</span>
                    <span class="recipe-card__meta-value">{escape(str(recipe.get('servings', '4')))}</span>
                </div>
                <div class="recipe-card__meta-item">
                    <span class="recipe-card__meta-label">Calories</span>
                    <span class="recipe-card__meta-value">{escape(str(recipe.get('calories', '400')))}</span>
                </div>
                <div class="recipe-card__meta-item">
                    <span class="recipe-card__meta-label">Course</span>
                    <span class="recipe-card__meta-value">{escape(str(recipe.get('course', 'Main')))}</span>
                </div>
                <div class="recipe-card__meta-item">
                    <span class="recipe-card__meta-label">Cuisine</span>
                    <span class="recipe-card__meta-value">{escape(str(recipe.get('cuisine', 'American')))}</span>
                </div>
            </div>
            <div class="recipe-card__section-title">Ingredients</div>
            <ul class="recipe-card__ingredient-list">
{rc_ing}
            </ul>
            <div class="recipe-card__section-title">Instructions</div>
            <ol class="recipe-card__instruction-list">
{rc_ins}
            </ol>
        </div>
    </section>

    <!-- FAQs -->
    <section id="faqs" class="faq-section">
        <h2>Frequently Asked Questions</h2>
{faq_html}
    </section>

    <!-- Conclusion -->
    <section id="conclusion">
        <h2>Final Thoughts</h2>
        {para(sections.get('conclusion', ''))}
    </section>

    <!-- Social Share -->
    <div class="social-share">
        <span class="social-share__label">Share this recipe:</span>
        <a class="social-share__btn social-share__btn--facebook"
           href="https://www.facebook.com/sharer/sharer.php?u={escape(share_url)}"
           target="_blank" rel="noopener">Facebook</a>
        <a class="social-share__btn social-share__btn--twitter"
           href="https://twitter.com/intent/tweet?text={escape(title)}&url={escape(share_url)}"
           target="_blank" rel="noopener">Twitter</a>
        <a class="social-share__btn social-share__btn--pinterest"
           href="https://pinterest.com/pin/create/button/?url={escape(share_url)}&description={escape(title)}"
           target="_blank" rel="noopener">Pinterest</a>
    </div>

</div><!-- /article-container -->
</body>
</html>"""
        return html

    # ------------------------------------------------------------------
    # file saving
    # ------------------------------------------------------------------
    def save_files(self, content_data: dict, html_content: str, css_content: str):
        out_dir = Path(self.slug)
        out_dir.mkdir(parents=True, exist_ok=True)

        # structure.json
        struct_path = out_dir / "structure.json"
        with open(struct_path, "w", encoding="utf-8") as f:
            json.dump(STRUCTURE, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved: {struct_path}")

        # content.json
        content_path = out_dir / "content.json"
        with open(content_path, "w", encoding="utf-8") as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved: {content_path}")

        # css.css
        css_path = out_dir / "css.css"
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        print(f"[OK] Saved: {css_path}")

        # article.html
        html_path = out_dir / "article.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[OK] Saved: {html_path}")

        # placeholder if needed
        for img_val in [
            content_data.get("main_image"),
            content_data.get("ingredient_image"),
        ]:
            if img_val == "placeholder.jpg":
                ph = out_dir / "placeholder.jpg"
                if not ph.exists():
                    ph.write_bytes(b"")
                break

    # ------------------------------------------------------------------
    # public entry point
    # ------------------------------------------------------------------
    def run(self, return_content_only: bool = False):
        if not self.title:
            raise ValueError("CONFIG['title'] must not be empty. Supply a title via config_override.")

        print(f"[*] Starting generation for: {self.title}")

        css_content  = self.generate_css()
        content_data = self.generate_content()
        html_content = self.generate_html(content_data, css_filename="css.css")

        content_data["article_html"] = html_content
        content_data["article_css"]  = css_content

        if return_content_only:
            return content_data

        self.save_files(content_data, html_content, css_content)
        print("[OK] Complete!")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    title = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    if not title:
        title = input("Enter recipe title: ").strip()

    gen = ArticleGenerator(config_override={"title": title})
    gen.run()
