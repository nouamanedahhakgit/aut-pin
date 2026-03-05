"""
generator-12.py
---------------
Fresh Modern Recipe Blog — Stitch-designed template.

Design: White (#fafffe) background, mint green (#3cb587) primary,
coral (#ff6b6b) accent, dark (#1d1d1d) text. Outfit headings, Inter body.
2x2 emoji card grid for highlights, green checkboxes, large mint step
numbers, gradient left border on pro tips, pastel-badge recipe card.
Modern, playful, clean.

CONFIG["title"] = "" — user supplies title via API payload.
"""

import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary":            "#3cb587",
        "secondary":          "#ff6b6b",
        "accent":             "#ff6b6b",
        "background":         "#fafffe",
        "container_bg":       "#ffffff",
        "border":             "#e8ede8",
        "text_primary":       "#1d1d1d",
        "text_secondary":     "#4d4d4d",
        "button_print":       "#3cb587",
        "button_pin":         "#ff6b6b",
        "button_hover_print": "#2da677",
        "button_hover_pin":   "#e85a5a",
        "link":               "#3cb587",
        "list_marker":        "#3cb587",
    },
    "fonts": {
        "heading": {
            "family":  "Outfit",
            "weights": [500, 700],
            "sizes":   {"h1": "2.2rem", "h2": "1.5rem", "h3": "1.1rem"},
        },
        "body": {
            "family":      "Inter",
            "weight":      400,
            "size":        "1rem",
            "line_height": 1.75,
        },
    },
    "layout": {
        "max_width":         "800px",
        "section_spacing":   "2.5rem",
        "paragraph_spacing": "1.1rem",
        "list_spacing":      "0.5rem",
        "container_padding": "2rem",
        "border_radius":     "12px",
        "box_shadow":        "0 2px 12px rgba(0,0,0,0.05)",
    },
    "components": {
        "numbered_list": {
            "style":       "large_number",
            "circle_bg":   "#e8f7f0",
            "circle_color":"#3cb587",
            "circle_size": "42px",
        },
        "bullet_list": {
            "style": "checkbox",
            "color": "#3cb587",
        },
        "pro_tips_box": {
            "bg_color":         "#f0faf6",
            "border_color":     "#3cb587",
            "border_left":      "4px solid",
            "border_gradient":  "linear-gradient(180deg, #3cb587, #ff6b6b)",
            "padding":          "1.5rem",
        },
        "recipe_card": {
            "bg":             "#ffffff",
            "border":         "1px solid #e8ede8",
            "border_radius":  "16px",
            "padding":        "2rem",
            "meta_icon_color":"#3cb587",
        },
    },
    "images": {
        "main_article_image": "",
        "ingredient_image":   "",
        "recipe_card_image":  "",
    },
    "structure_template": {
        "word_counts": {
            "intro":                 120,
            "why_love_item_1":        30,
            "why_love_item_2":        30,
            "why_love_item_3":        30,
            "why_love_item_4":        30,
            "ingredients_intro":      40,
            "instructions_step_1":    70,
            "instructions_step_2":    70,
            "instructions_step_3":    70,
            "instructions_step_4":    70,
            "instructions_step_5":    70,
            "serving_suggestions":    60,
            "pro_tip_1":              35,
            "pro_tip_2":              35,
            "pro_tip_3":              35,
            "conclusion":             80,
            "faq_1_answer":           55,
            "faq_2_answer":           55,
            "faq_3_answer":           55,
            "faq_4_answer":           55,
        }
    },
    "dark_mode": False,
}

STRUCTURE = [
    {"key": "intro",               "type": "intro",       "label": "Introduction"},
    {"key": "why_love",            "type": "h2",          "label": "Why I Love This Recipe"},
    {"key": "why_love_item_1",     "type": "card_grid",   "label": ""},
    {"key": "why_love_item_2",     "type": "card_grid",   "label": ""},
    {"key": "why_love_item_3",     "type": "card_grid",   "label": ""},
    {"key": "why_love_item_4",     "type": "card_grid",   "label": ""},
    {"key": "ingredients_intro",   "type": "h2",          "label": "Ingredients"},
    {"key": "instructions_intro",  "type": "h2",          "label": "How to Make {title}"},
    {"key": "instructions_step_1", "type": "h3",          "label": "Step 1"},
    {"key": "instructions_step_2", "type": "h3",          "label": "Step 2"},
    {"key": "instructions_step_3", "type": "h3",          "label": "Step 3"},
    {"key": "instructions_step_4", "type": "h3",          "label": "Step 4"},
    {"key": "instructions_step_5", "type": "h3",          "label": "Step 5"},
    {"key": "serving_suggestions", "type": "h2",          "label": "Serving Suggestions"},
    {"key": "pro_tips",            "type": "pro_tips_box","label": "Tips & Tricks"},
    {"key": "faqs",                "type": "faq",         "label": "Frequently Asked Questions"},
    {"key": "conclusion",          "type": "conclusion",  "label": "Final Thoughts"},
]


class ArticleGenerator:

    def __init__(self, config_override=None):
        self.config = dict(CONFIG)
        if config_override:
            self._merge(self.config, config_override)
        from ai_client import create_ai_client
        self.client, self.model = create_ai_client(self.config)
        self.title = self.config["title"].strip()
        self.slug = self._slugify(self.title)

    def _merge(self, base, override):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._merge(base[k], v)
            else:
                base[k] = v

    def _slugify(self, text):
        text = re.sub(r"[^a-z0-9\s-]", "", text.lower())
        return re.sub(r"\s+", "-", text.strip()) or "article"

    def _strip_markdown(self, text):
        if not text or not isinstance(text, str):
            return text
        s = text.strip()
        s = re.sub(r'^#{1,6}\s*', '', s)
        s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'\*([^*]+)\*', r'\1', s)
        return s.strip()

    def _chat(self, prompt, max_tokens=500):
        from ai_client import ai_chat
        system = (
            "You are a cheerful, modern food blogger with a fresh, playful voice. "
            "Write engaging, SEO-friendly content with personality. "
            "Output plain text only: no markdown. "
            f"All content must be only about: {self.title}."
        )
        raw = ai_chat(self, prompt, max_tokens=max_tokens, system=system)
        return self._strip_markdown(raw) if raw else ""

    def _gen_intro(self):
        return self._chat(
            f"Write a cheerful 120-word intro for {self.title}. "
            "Fun, modern tone. Plain text.", 280
        )

    def _gen_why_items(self):
        """Returns list of dicts with emoji, title, desc."""
        raw = self._chat(
            f"Give exactly 4 reasons to love {self.title}. "
            "Format each on its own line as: EMOJI | ShortTitle | one sentence description. "
            "Example: 🔥 | Super Fast | Ready in under 15 minutes.\n"
            "Use fun food emojis. No bullets, no numbering.", 280
        )
        items = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 3:
                items.append({
                    "emoji": parts[0].strip(),
                    "title": parts[1].strip(),
                    "desc":  parts[2].strip(),
                })
            elif len(parts) == 2:
                items.append({"emoji": "✨", "title": parts[0].strip(), "desc": parts[1].strip()})
            else:
                items.append({"emoji": "✨", "title": line[:25], "desc": line})
        while len(items) < 4:
            items.append({"emoji": "💚", "title": "Easy & Fun", "desc": f"{self.title} is a breeze to make."})
        return items[:4]

    def _gen_ingredients_intro(self):
        return self._chat(
            f"Write a 40-word intro for the ingredients of {self.title}. Fun tone.", 100
        )

    def _gen_ingredient_list(self):
        raw = self._chat(
            f"List exactly 10 ingredients for {self.title} with measurements. One per line.", 200
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        return lines[:12] if lines else [f"Ingredient {i+1}" for i in range(10)]

    def _gen_step(self, num):
        raw = self._chat(
            f"Write step {num} for making {self.title}. "
            "Format: HEADING: <short heading>\nBODY: <70 word paragraph>", 220
        )
        heading, body = f"Step {num}", raw
        for line in (raw or "").splitlines():
            s = line.strip()
            if s.upper().startswith("HEADING:"):
                heading = s.split(":", 1)[-1].strip() or heading
            elif s.upper().startswith("BODY:"):
                body = s.split(":", 1)[-1].strip() or body
        return {"heading": heading, "body": body}

    def _gen_serving(self):
        return self._chat(
            f"Write a 60-word paragraph with serving suggestions for {self.title}. Fun tone.", 140
        )

    def _gen_pro_tips(self):
        raw = self._chat(
            f"Give exactly 3 tips for making {self.title}. "
            "Each: ShortPhrase: one sentence. One per line.", 200
        )
        lines = [self._strip_markdown(l.strip()) for l in raw.splitlines() if l.strip()]
        while len(lines) < 3:
            lines.append(f"Taste As You Go: Adjust seasoning to your preference.")
        return lines[:4]

    def _gen_conclusion(self):
        return self._chat(
            f"Write a fun 80-word conclusion for {self.title}. Encourage sharing. Plain text.", 180
        )

    def _gen_faqs(self):
        raw = self._chat(
            f"Write exactly 4 FAQ Q&A about {self.title}. "
            "Format: Q1: question\nA1: 55-word answer\nQ2:...\nA2:...\nQ3:...\nA3:...\nQ4:...\nA4:...", 500
        )
        faqs = []
        for i in range(1, 5):
            q, a = None, None
            for line in raw.splitlines():
                ls = line.strip()
                if ls.upper().startswith(f"Q{i}:"):
                    q = ls.split(":", 1)[-1].strip()
                elif ls.upper().startswith(f"A{i}:"):
                    a = ls.split(":", 1)[-1].strip()
            if not q:
                q = f"Can I customize {self.title}?"
            if not a:
                a = self._chat(f"Answer in 2-3 sentences: {q}", 100)
            faqs.append({"question": q, "answer": a or ""})
        return faqs

    def _gen_recipe(self):
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": self.title, "summary": f"A fresh and delicious {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min",
                "servings": "4", "calories": "350", "course": "Main Course", "cuisine": "International",
            }
            return {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        raw = self._chat(
            f"Create a recipe for {self.title} as valid JSON with keys: "
            "name, summary, ingredients (array), instructions (array), "
            "prep_time, cook_time, total_time, servings, calories, course, cuisine. "
            "Output only raw JSON.", 650
        )
        try:
            clean = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
            return json.loads(clean)
        except Exception:
            return {
                "name": self.title, "summary": f"A fresh {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min",
                "servings": "4", "calories": "350", "course": "Main Course", "cuisine": "International",
            }

    def _gen_seo(self):
        defaults = {
            "recipe_title_pin":      self.title[:100],
            "pinterest_title":       self.title[:100],
            "pinterest_description": f"This fresh {self.title} recipe is healthy, easy, and so delicious!",
            "pinterest_keywords":    f"{self.title}, recipe, fresh, easy, healthy, delicious",
            "focus_keyphrase":       self.title.lower(),
            "meta_description":      f"Make this fresh {self.title} with our easy step-by-step recipe."[:140],
            "keyphrase_synonyms":    f"{self.title} recipe, easy {self.title}, fresh {self.title}",
        }
        raw = self._chat(
            f"Generate SEO metadata for {self.title}. "
            "Output valid JSON: recipe_title_pin, pinterest_title, "
            "pinterest_description, pinterest_keywords, focus_keyphrase, meta_description, "
            "keyphrase_synonyms. No markdown.", 380
        )
        try:
            clean = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
            data = json.loads(clean)
            defaults.update({k: v for k, v in data.items() if k in defaults})
        except Exception:
            pass
        defaults["recipe_title_pin"] = defaults["recipe_title_pin"][:100]
        defaults["meta_description"] = defaults["meta_description"][:140]
        return defaults

    def _gen_midjourney(self):
        main = self._chat(
            f"Write a Midjourney prompt for bright, fresh food photography of {self.title}. "
            "Include: natural light, white marble, green herbs garnish, overhead angle. End with --v 6.1", 120
        )
        ingr = self._chat(
            f"Write a Midjourney prompt for colorful ingredient flat-lay for {self.title}. "
            "White surface, bright natural light, fresh vibrant colors. End with --v 6.1", 120
        )
        if "--v 6.1" not in (main or ""):
            main = (main or "") + " --v 6.1"
        if "--v 6.1" not in (ingr or ""):
            ingr = (ingr or "") + " --v 6.1"
        return {"main": main, "ingredients": ingr}

    def _extract_json(self, raw):
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

    # ------------------------------------------------------------------ content
    def generate_content(self):
        from ai_client import ai_chat
        existing = self.config.get("recipe")
        recipe_from_config = existing and isinstance(existing, dict) and (existing.get("ingredients") or existing.get("instructions"))
        schema = {
            "intro": "string ~120 words",
            "why_love_items": "array of 4 strings (EMOJI | ShortTitle | sentence)",
            "ingredients_intro": "string ~40 words",
            "ingredient_list": "array of 10 strings",
            "steps": "array of 5 objects with heading and body",
            "serving_suggestions": "string ~60 words",
            "pro_tips": "array of 3 strings",
            "conclusion": "string ~80 words",
            "faqs": "array of 4 objects with question and answer",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine" if not recipe_from_config else "(omit)",
            "meta_description": "120-140 chars",
            "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        system = "You are a cheerful, modern food blogger with a fresh, playful voice. Generate the full article as ONE JSON. Plain text only: no markdown. All content only about the recipe title."
        user = f"Generate the complete recipe article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=4500, system=system)
        data = self._extract_json(raw)
        
        if data:
            print("[*] Generated content via single JSON.")
            intro = self._strip_markdown(str(data.get("intro", "")))
            
            why_items_raw = data.get("why_love_items", [])
            why_items = []
            for line in why_items_raw[:4]:
                line_str = self._strip_markdown(str(line)).strip()
                if not line_str:
                    continue
                parts = line_str.split("|")
                if len(parts) >= 3:
                    why_items.append({"emoji": parts[0].strip(), "title": parts[1].strip(), "desc": parts[2].strip()})
                elif len(parts) == 2:
                    why_items.append({"emoji": "✨", "title": parts[0].strip(), "desc": parts[1].strip()})
                else:
                    why_items.append({"emoji": "✨", "title": line_str[:25], "desc": line_str})
            while len(why_items) < 4:
                why_items.append({"emoji": "💚", "title": "Easy & Fun", "desc": f"{self.title} is a breeze to make."})
                
            ing_intro = self._strip_markdown(str(data.get("ingredients_intro", "")))
            ing_list = [str(x).strip() for x in (data.get("ingredient_list") or [])[:12]]
            steps_raw = data.get("steps") or []
            steps = [{"heading": str(s.get("heading", f"Step {i}")).strip() if isinstance(s, dict) else f"Step {i}", "body": self._strip_markdown(str(s.get("body", "")) if isinstance(s, dict) else "")} for i, s in enumerate(steps_raw[:5], 1)]
            serving = self._strip_markdown(str(data.get("serving_suggestions", "")))
            tips = [self._strip_markdown(str(x)) for x in (data.get("pro_tips") or [])[:4]]
            conclusion = self._strip_markdown(str(data.get("conclusion", "")))
            faqs_raw = data.get("faqs") or []
            faqs = [{"question": str(f.get("question", "")).strip(), "answer": self._strip_markdown(str(f.get("answer", "")))} for f in faqs_raw[:4] if isinstance(f, dict)]
            
            if recipe_from_config:
                defaults = {"name": self.title, "summary": "", "ingredients": [], "instructions": [], "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min", "servings": "4", "calories": "350", "course": "Main Course", "cuisine": "International"}
                recipe = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
            else:
                recipe = data.get("recipe") or {}
                if not isinstance(recipe, dict) or not (recipe.get("ingredients") or recipe.get("instructions")):
                    recipe = {"name": self.title, "summary": f"A fresh {self.title} recipe.", "ingredients": ing_list[:20] if ing_list else [], "instructions": [s.get("body", "") for s in steps][:15] if steps else [], "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min", "servings": "4", "calories": "350", "course": "Main Course", "cuisine": "International"}
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            
            seo = {"recipe_title_pin": (str(data.get("pinterest_title", self.title)) or self.title)[:100], "pinterest_title": (str(data.get("pinterest_title", "")) or self.title)[:100], "pinterest_description": f"This fresh {self.title} recipe is healthy, easy, and so delicious!", "pinterest_keywords": f"{self.title}, recipe, fresh, easy, healthy, delicious", "focus_keyphrase": self.title.lower(), "meta_description": (str(data.get("meta_description", "")) or f"Make this fresh {self.title} with our easy step-by-step recipe.")[:140], "keyphrase_synonyms": f"{self.title} recipe, easy {self.title}, fresh {self.title}"}
            mj_main = str(data.get("prompt_midjourney_main", "") or "").strip()
            mj_ing = str(data.get("prompt_midjourney_ingredients", "") or "").strip()
            mj = {"main": mj_main if mj_main and "--v 6.1" in mj_main else f"Bright, fresh food photography of {self.title} --v 6.1", "ingredients": mj_ing if mj_ing and "--v 6.1" in mj_ing else f"Colorful ingredient flat-lay for {self.title} --v 6.1"}
        else:
            print("[*] Generating intro...")
            intro = self._gen_intro()
            print("[*] Generating why-love cards...")
            why_items = self._gen_why_items()
            print("[*] Generating ingredients...")
            ing_intro = self._gen_ingredients_intro()
            ing_list = self._gen_ingredient_list()
            print("[*] Generating steps 1-5...")
            steps = [self._gen_step(i) for i in range(1, 6)]
            print("[*] Generating serving suggestions...")
            serving = self._gen_serving()
            print("[*] Generating tips...")
            tips = self._gen_pro_tips()
            print("[*] Generating conclusion...")
            conclusion = self._gen_conclusion()
            print("[*] Generating FAQs...")
            faqs = self._gen_faqs()
            print("[*] Generating recipe card...")
            recipe = self._gen_recipe()
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            print("[*] Generating SEO...")
            seo = self._gen_seo()
            print("[*] Generating Midjourney prompts...")
            mj = self._gen_midjourney()

        from ai_client import get_first_category
        cat = get_first_category(self.config)
        main_img = self.config["images"].get("main_article_image") or "placeholder.jpg"

        sections = [
            {"key": "intro",              "content": intro},
            {"key": "why_love_items",     "content": why_items},
            {"key": "ingredients_intro",  "content": ing_intro},
            {"key": "ingredient_list",    "content": ing_list},
            {"key": "instructions_steps", "content": steps},
            {"key": "serving_suggestions","content": serving},
            {"key": "pro_tips",           "content": tips},
            {"key": "conclusion",         "content": conclusion},
            {"key": "faqs",               "content": faqs},
        ]

        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": f"generator-12 / title: {self.title}",
            "prompt_base": f"Fresh modern mint/coral food blog for: {self.title}",
            "recipe": recipe, **seo,
            "main_image": main_img,
            "ingredient_image": self.config["images"].get("ingredient_image") or "placeholder.jpg",
            "prompt_midjourney_main": mj["main"],
            "prompt_midjourney_ingredients": mj["ingredients"],
        }

    # ------------------------------------------------------------------ CSS
    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url

        c  = self.config["colors"]
        f  = self.config["fonts"]
        l  = self.config["layout"]
        cp = self.config["components"]
        nl = cp["numbered_list"]
        pt = cp["pro_tips_box"]
        rc = cp["recipe_card"]

        import_url = build_font_import_url(f)
        body_font = font_family_css(f["body"]["family"], "sans-serif")
        heading_font = font_family_css(f["heading"]["family"], "sans-serif")

        return f"""/* generator-12 | Fresh Modern Mint + Coral */
@import url('{import_url}');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    background: {c['background']};
    color: {c['text_primary']};
    font-family: {body_font};
    font-size: {f['body']['size']};
    font-weight: {f['body']['weight']};
    line-height: {f['body']['line_height']};
    -webkit-font-smoothing: antialiased;
}}

.article-container {{
    max-width: {l['max_width']};
    margin: 0 auto;
    padding: {l['container_padding']};
}}

/* --- Header --- */
.article-header.g12-header {{ margin-bottom: {l['section_spacing']}; }}
.article-header.g12-header .article-title {{
    font-family: {heading_font};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 700;
    color: {c['text_primary']};
    margin: 0 0 0.75rem 0;
    line-height: 1.2;
}}
.article-header.g12-header .article-byline-row {{
    display: flex; flex-wrap: wrap; justify-content: space-between;
    align-items: center; gap: 0.5rem;
}}
.article-header.g12-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g12-header .byline-author {{ font-weight: 600; color: {c['text_primary']}; font-size: 0.9rem; }}
.article-header.g12-header .byline-date {{ font-size: 0.8rem; color: {c['text_secondary']}; }}
.article-header.g12-header .byline-disclaimer {{ font-size: 0.75rem; color: {c['text_secondary']}; font-style: italic; }}
.article-header.g12-header .byline-right {{ display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }}
.pill-badge {{
    display: inline-block; padding: 0.3rem 0.75rem; border-radius: 999px;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.03em;
}}
.pill-badge.green {{ background: #e8f7f0; color: {c['primary']}; }}
.pill-badge.coral {{ background: #ffe8e8; color: {c['secondary']}; }}

/* --- Typography --- */
h1 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h1']}; font-weight: 700; color: {c['text_primary']}; line-height: 1.2; margin-bottom: 1rem; }}
h2 {{
    font-family: {heading_font}; font-size: {f['heading']['sizes']['h2']}; font-weight: 700;
    color: {c['text_primary']}; margin-top: {l['section_spacing']}; margin-bottom: 0.75rem;
}}
h3 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h3']}; font-weight: 700; color: {c['text_primary']}; margin-top: 0; margin-bottom: 0.3rem; }}
p {{ color: {c['text_secondary']}; margin-bottom: {l['paragraph_spacing']}; }}
a {{ color: {c['link']}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* --- Hero image (rounded) --- */
.hero-image {{
    width: 100%; height: auto; display: block;
    border-radius: {l['border_radius']};
    margin: 1.25rem 0;
    object-fit: cover; max-height: 460px;
    box-shadow: {l['box_shadow']};
}}

/* --- Why love cards (2x2 grid with emojis) --- */
.why-love-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;
    margin: 0.5rem 0 1.5rem;
}}
.why-love-card {{
    background: {c['container_bg']}; border: 1px solid {c['border']};
    border-radius: {l['border_radius']}; padding: 1.25rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.why-love-card:hover {{
    border-color: {c['primary']}; box-shadow: 0 4px 16px rgba(60,181,135,0.12);
}}
.why-love-emoji {{ font-size: 1.6rem; margin-bottom: 0.5rem; display: block; }}
.why-love-card strong {{ display: block; color: {c['text_primary']}; font-weight: 700; margin-bottom: 0.25rem; font-size: 0.95rem; }}
.why-love-card span {{ font-size: 0.85rem; color: {c['text_secondary']}; }}

/* --- Ingredient list (green checkboxes) --- */
.ingredient-list {{ list-style: none; padding: 0; margin: 0.5rem 0 1.25rem; }}
.ingredient-list li {{
    position: relative; padding-left: 1.8rem; margin-bottom: {l['list_spacing']};
    color: {c['text_secondary']}; line-height: 1.7;
}}
.ingredient-list li::before {{
    content: ''; position: absolute; left: 0; top: 0.35em;
    width: 14px; height: 14px; border: 2px solid {c['list_marker']};
    border-radius: 3px;
}}

/* --- Steps (large mint numbers) --- */
.step-item {{ display: flex; gap: 1.25rem; align-items: flex-start; margin-bottom: 1.75rem; }}
.step-number {{
    flex-shrink: 0; width: {nl['circle_size']}; height: {nl['circle_size']};
    border-radius: {l['border_radius']}; background: {nl['circle_bg']}; color: {nl['circle_color']};
    font-weight: 700; font-size: 1.2rem;
    display: flex; align-items: center; justify-content: center;
}}
.step-body h3 {{ margin-top: 0; margin-bottom: 0.3rem; font-size: 1.05rem; }}
.step-body p {{ margin: 0; font-size: 0.95rem; }}

/* --- Pro tips box (gradient left border) --- */
.pro-tips-box {{
    position: relative;
    background: {pt['bg_color']}; padding: {pt['padding']};
    border-radius: {l['border_radius']};
    margin: {l['section_spacing']} 0; overflow: hidden;
}}
.pro-tips-box::before {{
    content: ''; position: absolute; left: 0; top: 0; bottom: 0;
    width: 4px; background: {pt['border_gradient']};
}}
.pro-tips-box h2 {{ margin-top: 0; font-size: 1.2rem; color: {c['primary']}; }}
.pro-tips-list {{ list-style: none; padding: 0; margin: 0.5rem 0 0; }}
.pro-tips-list li {{
    padding: 0.4rem 0; color: {c['text_secondary']};
    border-bottom: 1px solid rgba(60,181,135,0.1);
}}
.pro-tips-list li:last-child {{ border-bottom: none; }}
.pro-tips-list li strong {{ color: {c['text_primary']}; }}

/* --- FAQ expandable cards --- */
.faq-section {{ margin: {l['section_spacing']} 0; }}
.faq-item {{
    background: {c['container_bg']}; border: 1px solid {c['border']};
    border-radius: {l['border_radius']}; margin-bottom: 0.6rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03); overflow: hidden;
}}
.faq-question {{
    width: 100%; background: none; border: none; text-align: left;
    padding: 1rem 1.25rem;
    font-family: {heading_font}; font-size: 0.95rem; font-weight: 700;
    color: {c['text_primary']}; cursor: pointer;
    display: flex; justify-content: space-between; align-items: center;
}}
.faq-question::after {{ content: '+'; font-size: 1.2rem; color: {c['primary']}; font-weight: 400; }}
.faq-question.open::after {{ content: '\\2212'; }}
.faq-answer {{ display: none; padding: 0 1.25rem 1rem; color: {c['text_secondary']}; }}
.faq-answer.open {{ display: block; }}

/* --- Recipe card (rounded, pastel badges) --- */
.recipe-card {{
    background: {rc['bg']}; border: {rc['border']};
    border-radius: {rc['border_radius']}; padding: {rc['padding']};
    margin: {l['section_spacing']} 0; box-shadow: {l['box_shadow']};
}}
.recipe-card h2 {{ margin-top: 0; text-align: center; color: {c['text_primary']}; }}
.recipe-card-image {{
    width: 100%; height: 260px; object-fit: cover; display: block;
    border-radius: {l['border_radius']}; margin: 1rem 0;
}}
.recipe-meta-badges {{
    display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;
    margin: 1rem 0;
}}
.meta-badge {{
    display: inline-flex; flex-direction: column; align-items: center;
    padding: 0.6rem 1rem; border-radius: 999px;
    background: #f0faf6; min-width: 85px;
}}
.meta-badge-label {{ font-size: 0.6rem; text-transform: uppercase; color: {c['text_secondary']}; letter-spacing: 0.08em; }}
.meta-badge-value {{ font-size: 0.9rem; font-weight: 700; color: {c['primary']}; margin-top: 2px; }}
.recipe-card-buttons {{ display: flex; gap: 0.75rem; margin: 1rem 0; }}
.btn-print {{
    flex: 1; background: {c['button_print']}; color: #fff; border: none;
    padding: 0.75rem 1rem; border-radius: 999px;
    cursor: pointer; font-weight: 600; font-size: 0.85rem; transition: background 0.2s;
}}
.btn-print:hover {{ background: {c['button_hover_print']}; }}
.btn-pin {{
    flex: 1; background: {c['button_pin']}; color: #fff; border: none;
    padding: 0.75rem 1rem; border-radius: 999px;
    cursor: pointer; font-weight: 600; font-size: 0.85rem; transition: background 0.2s;
}}
.btn-pin:hover {{ background: {c['button_hover_pin']}; }}
.recipe-ingredients-list {{ list-style: none; padding: 0; }}
.recipe-ingredients-list li {{
    padding: 0.4rem 0 0.4rem 1.8rem; position: relative;
    color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.recipe-ingredients-list li:last-child {{ border-bottom: none; }}
.recipe-ingredients-list li::before {{
    content: ''; position: absolute; left: 0; top: 0.5em;
    width: 14px; height: 14px; border: 2px solid {c['list_marker']}; border-radius: 3px;
}}
.recipe-instructions-list {{ list-style: none; padding: 0; counter-reset: rstep12; }}
.recipe-instructions-list li {{
    counter-increment: rstep12; padding: 0.6rem 0 0.6rem 3rem;
    position: relative; color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.recipe-instructions-list li:last-child {{ border-bottom: none; }}
.recipe-instructions-list li::before {{
    content: counter(rstep12); position: absolute; left: 0; top: 0.4rem;
    width: 30px; height: 30px; background: {nl['circle_bg']}; color: {nl['circle_color']};
    border-radius: 8px; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.9rem;
}}

@media print {{ .recipe-card-buttons {{ display: none; }} }}
@media (max-width: 600px) {{
    .why-love-grid {{ grid-template-columns: 1fr; }}
    .recipe-card-buttons {{ flex-direction: column; }}
    h1 {{ font-size: 1.6rem; }}
}}"""

    # ------------------------------------------------------------------ HTML
    def generate_html(self, sections, css_filename="css.css"):
        t = self.title
        imgs = self.config["images"]
        main_img = imgs.get("main_article_image") or "placeholder.jpg"
        card_img = imgs.get("recipe_card_image") or main_img

        sec = {}
        for s in sections:
            sec[s["key"]] = s["content"]

        # Why love cards (emoji grid)
        why_items = sec.get("why_love_items", [])
        why_cards = ""
        for item in why_items:
            if isinstance(item, dict):
                why_cards += f'  <div class="why-love-card"><span class="why-love-emoji">{item.get("emoji","✨")}</span><strong>{item.get("title","")}</strong><span>{item.get("desc","")}</span></div>\n'
            else:
                why_cards += f'  <div class="why-love-card"><span class="why-love-emoji">✨</span><strong>{str(item)[:30]}</strong><span>{item}</span></div>\n'

        ing_list = sec.get("ingredient_list", [])
        ing_li = "".join(f"  <li>{it}</li>\n" for it in ing_list)

        steps = sec.get("instructions_steps", [])
        steps_html = ""
        for i, step in enumerate(steps):
            h = step.get("heading", f"Step {i+1}")
            b = step.get("body", "")
            steps_html += f'<div class="step-item"><span class="step-number">{i+1}</span><div class="step-body"><h3>{h}</h3><p>{b}</p></div></div>\n'

        tips = sec.get("pro_tips", [])
        tips_li = "".join(f"  <li>{tip}</li>\n" for tip in tips)

        faqs = sec.get("faqs", [])
        faq_html = ""
        for fq in faqs:
            faq_html += f'  <div class="faq-item"><button class="faq-question" onclick="toggleFaq(this)">{fq.get("question","")}</button><div class="faq-answer">{fq.get("answer","")}</div></div>\n'

        recipe = sec.get("recipe") or self._gen_recipe()
        if not isinstance(recipe, dict):
            recipe = {}
        r_name = recipe.get("name", t)
        r_prep = recipe.get("prep_time", "15 min")
        r_cook = recipe.get("cook_time", "25 min")
        r_total = recipe.get("total_time", "40 min")
        r_srv = str(recipe.get("servings", 4))
        r_cal = str(recipe.get("calories", ""))
        r_ing_li = "".join(f"    <li>{x}</li>\n" for x in recipe.get("ingredients", []))
        r_inst_li = "".join(f"    <li>{x}</li>\n" for x in recipe.get("instructions", []))

        from ai_client import get_first_category
        cat = get_first_category(self.config)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t}</title>
<link rel="stylesheet" href="{css_filename}">
<!-- inject:head-end -->
</head>
<body>
<div class="article-container">

<header class="article-header g12-header">
  <h1 class="article-title">{t}</h1>
  <div class="article-byline-row">
    <div class="byline-left">
      <span class="byline-author">By <span class="article-author"></span></span>
      <span class="byline-date"><span class="article-date"></span></span>
      <p class="byline-disclaimer">This post may contain affiliate links.</p>
    </div>
    <div class="byline-right">
      <span class="pill-badge green">{cat.get("categorie","recipe")}</span>
      <span class="pill-badge coral">Easy</span>
    </div>
  </div>
</header>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<p class="intro">{sec.get('intro','')}</p>

<h2>Why I Love This Recipe</h2>
<div class="why-love-grid">
{why_cards}</div>

<h2>Ingredients</h2>
<p>{sec.get('ingredients_intro','')}</p>
<ul class="ingredient-list">
{ing_li}</ul>

<h2>How to Make {t}</h2>
{steps_html}

<h2>Serving Suggestions</h2>
<p>{sec.get('serving_suggestions','')}</p>

<div class="pro-tips-box">
  <h2>Tips &amp; Tricks</h2>
  <ul class="pro-tips-list">
{tips_li}  </ul>
</div>

<div class="faq-section">
  <h2>Frequently Asked Questions</h2>
{faq_html}</div>

<h2>Final Thoughts</h2>
<p>{sec.get('conclusion','')}</p>

<!-- inject:before-recipe -->
<div class="recipe-card" id="recipe-card">
  <h2>{r_name}</h2>
  <img src="{card_img}" alt="{r_name}" class="recipe-card-image">
  <div class="recipe-meta-badges">
    <span class="meta-badge"><span class="meta-badge-label">Prep</span><span class="meta-badge-value">{r_prep}</span></span>
    <span class="meta-badge"><span class="meta-badge-label">Cook</span><span class="meta-badge-value">{r_cook}</span></span>
    <span class="meta-badge"><span class="meta-badge-label">Total</span><span class="meta-badge-value">{r_total}</span></span>
    <span class="meta-badge"><span class="meta-badge-label">Servings</span><span class="meta-badge-value">{r_srv}</span></span>
  </div>
  <div class="recipe-card-buttons">
    <button class="btn-print" onclick="window.print()">Print Recipe</button>
    <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Save to Pinterest</button>
  </div>
  <h3>Ingredients</h3>
  <ul class="recipe-ingredients-list">
{r_ing_li}  </ul>
  <h3>Instructions</h3>
  <ol class="recipe-instructions-list">
{r_inst_li}  </ol>
</div>
<!-- inject:article-end -->

</div>
<script>
function toggleFaq(btn){{btn.classList.toggle('open');btn.nextElementSibling.classList.toggle('open');}}
</script>
</body>
</html>"""

    # ------------------------------------------------------------------ run
    def run(self, return_content_only=False):
        if not self.title:
            raise ValueError("CONFIG['title'] is required")
        content_data = self.generate_content()
        css_content = self.generate_css()
        html_content = self.generate_html(content_data["sections"])
        content_data["article_html"] = html_content
        content_data["article_css"] = css_content

        if return_content_only:
            return content_data

        slug = self.slug
        os.makedirs(slug, exist_ok=True)
        with open(os.path.join(slug, "content.json"), "w", encoding="utf-8") as fh:
            json.dump(content_data, fh, indent=2)
        with open(os.path.join(slug, "article.html"), "w", encoding="utf-8") as fh:
            fh.write(html_content)
        with open(os.path.join(slug, "css.css"), "w", encoding="utf-8") as fh:
            fh.write(css_content)
        print(f"[OK] Saved to: {slug}/")
        return content_data


if __name__ == "__main__":
    gen = ArticleGenerator({"title": "Fresh Avocado Lime Bowl"})
    gen.run()
