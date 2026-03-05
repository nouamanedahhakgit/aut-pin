"""
generator-10.py
---------------
Rustic Farmhouse Recipe Blog — Stitch-designed template.

Design: Warm linen (#f5f0e8) background, forest green (#2d5016) primary,
warm amber (#b8860b) accent, dark brown (#3a2a1a) text. Libre Baskerville
serif headings, Nunito body. Thick bordered hero, decorative underlines,
two-column ingredients with dotted separators, green circled step numbers,
tan-bg pro tips box, green-banner recipe card.

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
        "primary":            "#2d5016",
        "secondary":          "#b8860b",
        "accent":             "#b8860b",
        "background":         "#f5f0e8",
        "container_bg":       "#ffffff",
        "border":             "#d4c9b8",
        "text_primary":       "#3a2a1a",
        "text_secondary":     "#5c4a3a",
        "button_print":       "#2d5016",
        "button_pin":         "#E60023",
        "button_hover_print": "#1d4010",
        "button_hover_pin":   "#FF1A3C",
        "link":               "#2d5016",
        "list_marker":        "#2d5016",
    },
    "fonts": {
        "heading": {
            "family":  "Libre Baskerville",
            "weights": [400, 700],
            "sizes":   {"h1": "2.1rem", "h2": "1.5rem", "h3": "1.15rem"},
        },
        "body": {
            "family":      "Nunito",
            "weight":      400,
            "size":        "1rem",
            "line_height": 1.8,
        },
    },
    "layout": {
        "max_width":         "800px",
        "section_spacing":   "2.5rem",
        "paragraph_spacing": "1.1rem",
        "list_spacing":      "0.5rem",
        "container_padding": "2.25rem",
        "border_radius":     "6px",
        "box_shadow":        "0 2px 12px rgba(58,42,26,0.08)",
    },
    "components": {
        "numbered_list": {
            "style":       "circle",
            "circle_bg":   "#2d5016",
            "circle_color":"#ffffff",
            "circle_size": "34px",
        },
        "bullet_list": {
            "style": "checkmark",
            "color": "#2d5016",
        },
        "pro_tips_box": {
            "bg_color":     "#f7f0e0",
            "border_color": "#2d5016",
            "border_left":  "4px solid #2d5016",
            "padding":      "1.5rem",
        },
        "recipe_card": {
            "bg":             "#ffffff",
            "border":         "1px solid #d4c9b8",
            "border_radius":  "8px",
            "padding":        "0",
            "meta_icon_color":"#b8860b",
            "header_bg":      "#2d5016",
            "header_color":   "#ffffff",
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
            "why_works_item_1":       30,
            "why_works_item_2":       30,
            "why_works_item_3":       30,
            "why_works_item_4":       30,
            "ingredients_intro":      45,
            "instructions_step_1":    70,
            "instructions_step_2":    70,
            "instructions_step_3":    70,
            "instructions_step_4":    70,
            "instructions_step_5":    70,
            "pro_tip_1":              35,
            "pro_tip_2":              35,
            "pro_tip_3":              35,
            "variations":             80,
            "storage":                70,
            "conclusion":             75,
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
    {"key": "why_works",           "type": "h2",          "label": "Why This Recipe Works"},
    {"key": "why_works_item_1",    "type": "bullet_list", "label": ""},
    {"key": "why_works_item_2",    "type": "bullet_list", "label": ""},
    {"key": "why_works_item_3",    "type": "bullet_list", "label": ""},
    {"key": "why_works_item_4",    "type": "bullet_list", "label": ""},
    {"key": "pro_tips",            "type": "pro_tips_box","label": "Baker's Pro Tips"},
    {"key": "ingredients_intro",   "type": "h2",          "label": "Ingredients"},
    {"key": "instructions_intro",  "type": "h2",          "label": "Instructions"},
    {"key": "instructions_step_1", "type": "h3",          "label": "Step 1"},
    {"key": "instructions_step_2", "type": "h3",          "label": "Step 2"},
    {"key": "instructions_step_3", "type": "h3",          "label": "Step 3"},
    {"key": "instructions_step_4", "type": "h3",          "label": "Step 4"},
    {"key": "instructions_step_5", "type": "h3",          "label": "Step 5"},
    {"key": "variations",          "type": "h2",          "label": "Variations"},
    {"key": "storage",             "type": "h2",          "label": "Storage & Reheating"},
    {"key": "faqs",                "type": "faq",         "label": "Frequently Asked Questions"},
    {"key": "conclusion",          "type": "conclusion",  "label": ""},
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
            "You are a warm, experienced home cook and food blogger. "
            "Write cozy, earthy, approachable content with farmhouse charm. "
            "Output plain text only: no markdown (no ##, ###, **, *, - bullets). "
            f"All content must be only about: {self.title}."
        )
        raw = ai_chat(self, prompt, max_tokens=max_tokens, system=system)
        return self._strip_markdown(raw) if raw else ""

    # ---- content generators ----
    def _gen_intro(self):
        return self._chat(
            f"Write a warm 120-word intro about {self.title}. "
            "Mention family traditions or seasonal warmth. Plain text.", 280
        )

    def _gen_why_works(self):
        raw = self._chat(
            f"Give exactly 4 reasons why this {self.title} recipe works so well. "
            "Format: ShortPhrase: one sentence. One per line. No bullets.", 220
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        while len(lines) < 4:
            lines.append(f"Simple Ingredients: Uses pantry staples you already have.")
        return lines[:4]

    def _gen_pro_tips(self):
        raw = self._chat(
            f"Give exactly 3 pro tips for making {self.title}. "
            "Each: ShortPhrase: one sentence. One per line.", 200
        )
        lines = [self._strip_markdown(l.strip()) for l in raw.splitlines() if l.strip()]
        while len(lines) < 3:
            lines.append(f"Room Temperature: Let ingredients come to room temperature for best results.")
        return lines[:4]

    def _gen_ingredients_intro(self):
        return self._chat(
            f"Write a 45-word intro for the ingredients of {self.title}. Plain text.", 110
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
            "Format: HEADING: <5 word heading>\nBODY: <70 word paragraph>", 220
        )
        heading, body = f"Step {num}", raw
        for line in (raw or "").splitlines():
            s = line.strip()
            if s.upper().startswith("HEADING:"):
                heading = s.split(":", 1)[-1].strip() or heading
            elif s.upper().startswith("BODY:"):
                body = s.split(":", 1)[-1].strip() or body
        return {"heading": heading, "body": body}

    def _gen_variations(self):
        return self._chat(
            f"Write an 80-word paragraph about variations for {self.title}. "
            "Suggest seasonal or dietary swaps. Plain text.", 180
        )

    def _gen_storage(self):
        return self._chat(
            f"Write a 70-word paragraph about storage and reheating for {self.title}. Plain text.", 160
        )

    def _gen_conclusion(self):
        return self._chat(
            f"Write a warm 75-word conclusion for {self.title}. "
            "Encourage families to try it together. Plain text.", 180
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
                q = f"Can I freeze {self.title}?"
            if not a:
                a = self._chat(f"Answer in 2-3 sentences: {q}", 100)
            faqs.append({"question": q, "answer": a or ""})
        return faqs

    def _gen_recipe(self):
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": self.title, "summary": f"A hearty, homestyle {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "20 min", "cook_time": "45 min", "total_time": "1 hr 5 min",
                "servings": "6", "calories": "420", "course": "Main Course", "cuisine": "American",
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
                "name": self.title, "summary": f"A hearty {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "20 min", "cook_time": "45 min", "total_time": "1 hr 5 min",
                "servings": "6", "calories": "420", "course": "Main Course", "cuisine": "American",
            }

    def _gen_seo(self):
        defaults = {
            "recipe_title_pin":      self.title[:100],
            "pinterest_title":       self.title[:100],
            "pinterest_description": f"This {self.title} recipe is hearty, homemade, and full of flavor.",
            "pinterest_keywords":    f"{self.title}, recipe, homemade, farmhouse, comfort food",
            "focus_keyphrase":       self.title.lower(),
            "meta_description":      f"Make this rustic {self.title} at home with our easy recipe."[:140],
            "keyphrase_synonyms":    f"{self.title} recipe, homemade {self.title}, easy {self.title}",
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
            f"Write a Midjourney prompt for rustic farmhouse food photography of {self.title}. "
            "Include: warm wood table, natural window light, linen napkin. End with --v 6.1", 120
        )
        ingr = self._chat(
            f"Write a Midjourney prompt for rustic ingredient flat-lay for {self.title}. "
            "Wooden cutting board, burlap, warm light. End with --v 6.1", 120
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
            "why_works": "array of 4 strings (Label: sentence)",
            "pro_tips": "array of 3 strings",
            "ingredients_intro": "string ~45 words",
            "ingredient_list": "array of 10 strings",
            "steps": "array of 5 objects with heading and body",
            "variations": "string ~80 words",
            "storage": "string ~70 words",
            "conclusion": "string ~75 words",
            "faqs": "array of 4 objects with question and answer",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine" if not recipe_from_config else "(omit)",
            "meta_description": "120-140 chars",
            "focus_keyphrase": "string",
            "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        system = "You are a warm, experienced home cook and food blogger. Generate the full article as ONE JSON. Plain text only: no markdown. All content only about the recipe title."
        user = f"Generate the complete rustic farmhouse recipe article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=5000, system=system)
        data = self._extract_json(raw)

        if data:
            print("[*] Generated content via single JSON.")
            intro = self._strip_markdown(str(data.get("intro", "")))
            why_works = [self._strip_markdown(str(x)) for x in (data.get("why_works") or [])[:4]]
            tips = [self._strip_markdown(str(x)) for x in (data.get("pro_tips") or [])[:4]]
            ing_intro = self._strip_markdown(str(data.get("ingredients_intro", "")))
            ing_list = [str(x).strip() for x in (data.get("ingredient_list") or [])[:12]]
            steps_raw = data.get("steps") or []
            steps = [{"heading": str(s.get("heading", f"Step {i}")).strip() if isinstance(s, dict) else f"Step {i}", "body": self._strip_markdown(str(s.get("body", "")) if isinstance(s, dict) else "")} for i, s in enumerate(steps_raw[:5], 1)]
            variations = self._strip_markdown(str(data.get("variations", "")))
            storage = self._strip_markdown(str(data.get("storage", "")))
            conclusion = self._strip_markdown(str(data.get("conclusion", "")))
            faqs_raw = data.get("faqs") or []
            faqs = [{"question": str(f.get("question", "")).strip(), "answer": self._strip_markdown(str(f.get("answer", "")))} for f in faqs_raw[:4] if isinstance(f, dict)]
            
            if recipe_from_config:
                defaults = {"name": self.title, "summary": f"A hearty, homestyle {self.title} recipe.", "ingredients": [], "instructions": [], "prep_time": "20 min", "cook_time": "45 min", "total_time": "1 hr 5 min", "servings": "6", "calories": "420", "course": "Main Course", "cuisine": "American"}
                recipe = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
            else:
                recipe = data.get("recipe") or {}
                if not isinstance(recipe, dict):
                    recipe = {"name": self.title, "summary": f"A hearty, homestyle {self.title} recipe.", "ingredients": ing_list[:20] if ing_list else [], "instructions": [s.get("body", "") for s in steps][:15] if steps else [], "prep_time": "20 min", "cook_time": "45 min", "total_time": "1 hr 5 min", "servings": "6", "calories": "420", "course": "Main Course", "cuisine": "American"}
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            
            seo = {
                "recipe_title_pin": (str(data.get("pinterest_title", self.title)) or self.title)[:100],
                "pinterest_title": (str(data.get("pinterest_title", "")) or self.title)[:100],
                "pinterest_description": f"This {self.title} recipe is hearty, homemade, and full of flavor.",
                "pinterest_keywords": f"{self.title}, recipe, homemade, farmhouse, comfort food",
                "focus_keyphrase": str(data.get("focus_keyphrase", self.title.lower())),
                "meta_description": (str(data.get("meta_description", "")) or f"Make this rustic {self.title} at home with our easy recipe.")[:140],
                "keyphrase_synonyms": f"{self.title} recipe, homemade {self.title}, easy {self.title}"
            }
            mj_main = str(data.get("prompt_midjourney_main", "") or "").strip()
            mj_ing = str(data.get("prompt_midjourney_ingredients", "") or "").strip()
            mj = {
                "main": mj_main if mj_main and "--v 6.1" in mj_main else f"Rustic farmhouse food photography of {self.title}. warm wood table, natural window light, linen napkin --v 6.1",
                "ingredients": mj_ing if mj_ing and "--v 6.1" in mj_ing else f"Rustic ingredient flat-lay for {self.title}. Wooden cutting board, burlap, warm light --v 6.1"
            }
        else:
            print("[*] Generating intro...")
            intro = self._gen_intro()
            print("[*] Generating why-works items...")
            why_works = self._gen_why_works()
            print("[*] Generating pro tips...")
            tips = self._gen_pro_tips()
            print("[*] Generating ingredients...")
            ing_intro = self._gen_ingredients_intro()
            ing_list = self._gen_ingredient_list()
            print("[*] Generating steps 1-5...")
            steps = [self._gen_step(i) for i in range(1, 6)]
            print("[*] Generating variations...")
            variations = self._gen_variations()
            print("[*] Generating storage tips...")
            storage = self._gen_storage()
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
            {"key": "why_works_items",    "content": why_works},
            {"key": "pro_tips",           "content": tips},
            {"key": "ingredients_intro",  "content": ing_intro},
            {"key": "ingredient_list",    "content": ing_list},
            {"key": "instructions_steps", "content": steps},
            {"key": "variations",         "content": variations},
            {"key": "storage",            "content": storage},
            {"key": "conclusion",         "content": conclusion},
            {"key": "faqs",               "content": faqs},
        ]

        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": f"generator-10 / title: {self.title}",
            "prompt_base": f"Rustic farmhouse food blog for: {self.title}",
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
        heading_font = font_family_css(f["heading"]["family"], "serif")

        return f"""/* generator-10 | Rustic Farmhouse */
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
    margin: 2rem auto;
    padding: {l['container_padding']};
    background: {c['container_bg']};
    border-radius: {l['border_radius']};
    box-shadow: {l['box_shadow']};
}}

/* --- Header --- */
.article-header.g10-header {{ margin-bottom: {l['section_spacing']}; }}
.article-header.g10-header .article-title {{
    font-family: {heading_font};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 700;
    color: {c['text_primary']};
    margin: 0 0 0.5rem 0;
    line-height: 1.25;
}}
.article-header.g10-header .title-decor {{
    display: block; width: 80px; height: 3px;
    background: {c['secondary']}; margin-bottom: 0.75rem; border-radius: 2px;
}}
.article-header.g10-header .article-byline-row {{
    display: flex; flex-wrap: wrap; justify-content: space-between;
    align-items: center; gap: 0.5rem;
}}
.article-header.g10-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g10-header .byline-author {{ font-weight: 600; color: {c['text_primary']}; }}
.article-header.g10-header .byline-author .heart {{ color: {c['secondary']}; }}
.article-header.g10-header .byline-date {{ font-size: 0.85rem; color: {c['text_secondary']}; }}
.article-header.g10-header .byline-disclaimer {{ font-size: 0.78rem; color: {c['text_secondary']}; font-style: italic; margin-top: 0.2rem; }}
.article-header.g10-header .byline-right {{ display: flex; align-items: center; gap: 0.75rem; }}
.article-header.g10-header .recipe-meta-bar {{ display: flex; gap: 1rem; font-size: 0.85rem; color: {c['text_secondary']}; }}

/* --- Typography --- */
h1 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h1']}; font-weight: 700; color: {c['text_primary']}; line-height: 1.25; margin-bottom: 1rem; }}
h2 {{
    font-family: {heading_font}; font-size: {f['heading']['sizes']['h2']}; font-weight: 700;
    color: {c['primary']}; margin-top: {l['section_spacing']}; margin-bottom: 0.8rem;
}}
h3 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h3']}; font-weight: 700; color: {c['text_primary']}; margin-top: 1.5rem; margin-bottom: 0.4rem; }}
p {{ color: {c['text_secondary']}; margin-bottom: {l['paragraph_spacing']}; }}
a {{ color: {c['link']}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* --- Hero (thick border) --- */
.hero-image {{
    width: 100%; height: auto; display: block;
    border: 4px solid {c['text_primary']};
    border-radius: {l['border_radius']};
    margin: 1.25rem 0;
    object-fit: cover; max-height: 460px;
}}

/* --- Why-works list (checkmark bullets) --- */
.why-works-list {{ list-style: none; padding: 0; margin: 0.5rem 0 1.25rem; }}
.why-works-list li {{
    position: relative; padding-left: 1.6rem; margin-bottom: {l['list_spacing']};
    color: {c['text_secondary']}; line-height: 1.7;
}}
.why-works-list li::before {{
    content: "\\2714"; position: absolute; left: 0; top: 0;
    color: {c['list_marker']}; font-weight: 700;
}}
.why-works-list li strong {{ color: {c['text_primary']}; }}

/* --- Pro tips box (tan bg, green border) --- */
.pro-tips-box {{
    background: {pt['bg_color']}; border-left: {pt['border_left']};
    padding: {pt['padding']}; border-radius: 0 {l['border_radius']} {l['border_radius']} 0;
    margin: {l['section_spacing']} 0;
}}
.pro-tips-box h2 {{ margin-top: 0; font-size: 1.3rem; color: {c['primary']}; }}
.pro-tips-list {{ list-style: none; padding: 0; margin: 0.5rem 0 0; }}
.pro-tips-list li {{
    padding: 0.5rem 0; color: {c['text_secondary']};
    border-bottom: 1px solid rgba(45,80,22,0.1);
}}
.pro-tips-list li:last-child {{ border-bottom: none; }}
.pro-tips-list li strong {{ color: {c['text_primary']}; }}

/* --- Ingredient list (two-column, dotted seps) --- */
.ingredient-list {{
    list-style: none; padding: 0; margin: 0.5rem 0 1.25rem;
    columns: 2; column-gap: 2rem;
}}
.ingredient-list li {{
    position: relative; padding-left: 1.2rem; margin-bottom: 0;
    padding-bottom: 0.5rem; color: {c['text_secondary']};
    border-bottom: 1px dotted {c['border']}; break-inside: avoid;
}}
.ingredient-list li:last-child {{ border-bottom: none; }}
.ingredient-list li::before {{
    content: ""; position: absolute; left: 0; top: 0.55em;
    width: 7px; height: 7px; border-radius: 50%; background: {c['list_marker']};
}}

/* --- Steps (green circles) --- */
.step-item {{ display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1.5rem; }}
.step-number {{
    flex-shrink: 0; width: {nl['circle_size']}; height: {nl['circle_size']};
    border-radius: 50%; background: {nl['circle_bg']}; color: {nl['circle_color']};
    font-weight: 700; font-size: 1rem;
    display: flex; align-items: center; justify-content: center;
}}
.step-body h3 {{ margin-top: 0; margin-bottom: 0.3rem; font-size: 1.05rem; }}
.step-body p {{ margin: 0; font-size: 0.95rem; }}

/* --- FAQ --- */
.faq-section {{ margin: {l['section_spacing']} 0; }}
.faq-item {{ border: 1px solid {c['border']}; border-radius: {l['border_radius']}; margin-bottom: 0.6rem; overflow: hidden; }}
.faq-question {{
    width: 100%; background: {c['container_bg']}; border: none;
    text-align: left; padding: 1rem 1.2rem;
    font-family: {heading_font}; font-size: 0.95rem; font-weight: 700;
    color: {c['text_primary']}; cursor: pointer;
    display: flex; justify-content: space-between; align-items: center;
}}
.faq-question::after {{ content: '+'; font-size: 1.3rem; color: {c['secondary']}; }}
.faq-question.open::after {{ content: '\\2212'; }}
.faq-answer {{ display: none; padding: 0.75rem 1.2rem 1rem; color: {c['text_secondary']}; border-top: 1px solid {c['border']}; }}
.faq-answer.open {{ display: block; }}

/* --- Recipe card (green banner header) --- */
.recipe-card {{
    background: {rc['bg']}; border: {rc['border']};
    border-radius: {rc['border_radius']}; overflow: hidden;
    margin: {l['section_spacing']} 0; box-shadow: {l['box_shadow']};
}}
.recipe-card-header {{
    background: {rc['header_bg']}; color: {rc['header_color']};
    padding: 1.25rem 1.75rem; text-align: center;
}}
.recipe-card-header h2 {{ margin: 0; color: {rc['header_color']}; font-size: 1.5rem; }}
.recipe-card-body {{ padding: 1.75rem; }}
.recipe-card-image {{
    width: 100%; height: 260px; object-fit: cover; display: block;
    border-bottom: 1px solid {c['border']};
}}
.recipe-card-buttons {{ display: flex; gap: 0.75rem; margin: 1rem 0; }}
.btn-print {{
    flex: 1; background: {c['button_print']}; color: #fff; border: none;
    padding: 0.75rem 1rem; border-radius: {l['border_radius']};
    cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: background 0.2s;
}}
.btn-print:hover {{ background: {c['button_hover_print']}; }}
.btn-pin {{
    flex: 1; background: {c['button_pin']}; color: #fff; border: none;
    padding: 0.75rem 1rem; border-radius: {l['border_radius']};
    cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: background 0.2s;
}}
.btn-pin:hover {{ background: {c['button_hover_pin']}; }}
.recipe-meta {{
    display: flex; flex-wrap: wrap; gap: 0; margin: 1rem 0;
    border: 1px solid {c['border']}; border-radius: {l['border_radius']};
}}
.recipe-meta-item {{
    flex: 1; text-align: center; padding: 0.75rem 0.5rem; min-width: 70px;
    border-right: 1px solid {c['border']};
}}
.recipe-meta-item:last-child {{ border-right: none; }}
.recipe-meta-label {{ font-size: 0.65rem; text-transform: uppercase; color: {c['text_secondary']}; letter-spacing: 0.08em; }}
.recipe-meta-value {{ font-size: 0.95rem; font-weight: 700; color: {rc['meta_icon_color']}; display: block; margin-top: 2px; }}
.recipe-ingredients-list {{ list-style: none; padding: 0; }}
.recipe-ingredients-list li {{
    padding: 0.4rem 0 0.4rem 1.6rem; position: relative;
    color: {c['text_secondary']}; border-bottom: 1px dotted {c['border']};
}}
.recipe-ingredients-list li:last-child {{ border-bottom: none; }}
.recipe-ingredients-list li::before {{
    content: '\\2714'; position: absolute; left: 0; top: 0.4rem; color: {c['list_marker']}; font-size: 0.85rem;
}}
.recipe-instructions-list {{ list-style: none; padding: 0; counter-reset: rstep; }}
.recipe-instructions-list li {{
    counter-increment: rstep; padding: 0.6rem 0 0.6rem 2.8rem;
    position: relative; color: {c['text_secondary']}; border-bottom: 1px dotted {c['border']};
}}
.recipe-instructions-list li:last-child {{ border-bottom: none; }}
.recipe-instructions-list li::before {{
    content: counter(rstep); position: absolute; left: 0; top: 0.45rem;
    width: 26px; height: 26px; background: {nl['circle_bg']}; color: {nl['circle_color']};
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.8rem;
}}

@media print {{ body {{ background: white; }} .recipe-card-buttons {{ display: none; }} }}
@media (max-width: 600px) {{
    .ingredient-list {{ columns: 1; }}
    .recipe-card-buttons {{ flex-direction: column; }}
    h1 {{ font-size: 1.5rem; }}
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

        why_works = sec.get("why_works_items", [])
        why_html = "".join(f"  <li>{item}</li>\n" for item in why_works)

        tips = sec.get("pro_tips", [])
        tips_li = "".join(f"  <li>{tip}</li>\n" for tip in tips)

        ing_list = sec.get("ingredient_list", [])
        ing_li = "".join(f"  <li>{it}</li>\n" for it in ing_list)

        steps = sec.get("instructions_steps", [])
        steps_html = ""
        for i, step in enumerate(steps):
            h = step.get("heading", f"Step {i+1}")
            b = step.get("body", "")
            steps_html += f'<div class="step-item"><span class="step-number">{i+1}</span><div class="step-body"><h3>{h}</h3><p>{b}</p></div></div>\n'

        faqs = sec.get("faqs", [])
        faq_html = ""
        for fq in faqs:
            faq_html += f'  <div class="faq-item"><button class="faq-question" onclick="toggleFaq(this)">{fq.get("question","")}</button><div class="faq-answer">{fq.get("answer","")}</div></div>\n'

        recipe = sec.get("recipe") or self._gen_recipe()
        if not isinstance(recipe, dict):
            recipe = {}
        r_name = recipe.get("name", t)
        r_prep = recipe.get("prep_time", "20 min")
        r_cook = recipe.get("cook_time", "45 min")
        r_total = recipe.get("total_time", "1 hr 5 min")
        r_srv = str(recipe.get("servings", 6))
        r_cal = str(recipe.get("calories", ""))
        r_ing_li = "".join(f"    <li>{x}</li>\n" for x in recipe.get("ingredients", []))
        r_inst_li = "".join(f"    <li>{x}</li>\n" for x in recipe.get("instructions", []))

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

<header class="article-header g10-header">
  <h1 class="article-title">{t}</h1>
  <span class="title-decor"></span>
  <div class="article-byline-row">
    <div class="byline-left">
      <span class="byline-author"><span class="heart">&#9829;</span> By <span class="article-author"></span></span>
      <span class="byline-date">Published <span class="article-date"></span></span>
      <p class="byline-disclaimer">This post may contain affiliate links.</p>
    </div>
    <div class="byline-right">
      <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin It</button>
      <div class="recipe-meta-bar"><span>{r_prep} prep</span><span>{r_cook} cook</span><span>{r_srv} servings</span></div>
    </div>
  </div>
</header>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<p class="intro">{sec.get('intro','')}</p>

<h2>Why This Recipe Works</h2>
<ul class="why-works-list">
{why_html}</ul>

<div class="pro-tips-box">
  <h2>Baker's Pro Tips</h2>
  <ul class="pro-tips-list">
{tips_li}  </ul>
</div>

<h2>Ingredients</h2>
<p>{sec.get('ingredients_intro','')}</p>
<ul class="ingredient-list">
{ing_li}</ul>

<h2>Instructions</h2>
{steps_html}

<h2>Variations</h2>
<p>{sec.get('variations','')}</p>

<h2>Storage &amp; Reheating</h2>
<p>{sec.get('storage','')}</p>

<div class="faq-section">
  <h2>Frequently Asked Questions</h2>
{faq_html}</div>

<p>{sec.get('conclusion','')}</p>

<!-- inject:before-recipe -->
<div class="recipe-card" id="recipe-card">
  <img src="{card_img}" alt="{r_name}" class="recipe-card-image">
  <div class="recipe-card-header"><h2>{r_name}</h2></div>
  <div class="recipe-card-body">
    <div class="recipe-meta">
      <div class="recipe-meta-item"><span class="recipe-meta-label">Prep</span><span class="recipe-meta-value">{r_prep}</span></div>
      <div class="recipe-meta-item"><span class="recipe-meta-label">Cook</span><span class="recipe-meta-value">{r_cook}</span></div>
      <div class="recipe-meta-item"><span class="recipe-meta-label">Total</span><span class="recipe-meta-value">{r_total}</span></div>
      <div class="recipe-meta-item"><span class="recipe-meta-label">Servings</span><span class="recipe-meta-value">{r_srv}</span></div>
      <div class="recipe-meta-item"><span class="recipe-meta-label">Cal</span><span class="recipe-meta-value">{r_cal}</span></div>
    </div>
    <div class="recipe-card-buttons">
      <button class="btn-print" onclick="window.print()">Print Recipe</button>
      <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Save to Pinterest</button>
    </div>
    <h3>Ingredients</h3>
    <ul class="recipe-ingredients-list">
{r_ing_li}    </ul>
    <h3>Instructions</h3>
    <ol class="recipe-instructions-list">
{r_inst_li}    </ol>
  </div>
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
    gen = ArticleGenerator({"title": "Old-Fashioned Apple Pie"})
    gen.run()
