"""
generator-5.py
--------------
Minimalist Japanese-Inspired Recipe Blog — Stitch-designed template.

Design: Warm white (#fdf8f2) background, deep indigo (#3d3b8e) primary,
muted terracotta (#c5705d) accent. Noto Serif headings, Noto Sans body.
Wabi-sabi aesthetic — sharp edges, generous whitespace, clean lines,
no decorative circles on numbers (plain decimal), asymmetric feel.

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
        "primary":            "#3d3b8e",
        "secondary":          "#c5705d",
        "accent":             "#c5705d",
        "background":         "#fdf8f2",
        "container_bg":       "#fdf8f2",
        "border":             "#e0ddd6",
        "text_primary":       "#333333",
        "text_secondary":     "#5a5a5a",
        "button_print":       "#3d3b8e",
        "button_pin":         "#c5705d",
        "button_hover_print": "#2d2b6e",
        "button_hover_pin":   "#a5503d",
        "link":               "#3d3b8e",
        "list_marker":        "#c5705d",
    },
    "fonts": {
        "heading": {
            "family":  "Noto Serif",
            "weights": [400, 700],
            "sizes":   {"h1": "2.1rem", "h2": "1.4rem", "h3": "1.1rem"},
        },
        "body": {
            "family":      "Noto Sans",
            "weight":      400,
            "size":        "15px",
            "line_height": 1.85,
        },
    },
    "layout": {
        "max_width":         "700px",
        "section_spacing":   "2.5rem",
        "paragraph_spacing": "1.1rem",
        "list_spacing":      "0.5rem",
        "container_padding": "1.5rem",
        "border_radius":     "0px",
        "box_shadow":        "none",
    },
    "components": {
        "numbered_list": {
            "style":       "decimal",
            "circle_bg":   "transparent",
            "circle_color":"#3d3b8e",
            "circle_size": "auto",
        },
        "bullet_list": {
            "style": "square",
            "color": "#c5705d",
        },
        "pro_tips_box": {
            "bg_color":     "#f5f2ed",
            "border_color": "#3d3b8e",
            "border_left":  "3px solid #3d3b8e",
            "padding":      "1.25rem 1.5rem",
        },
        "recipe_card": {
            "bg":             "#ffffff",
            "border":         "1px solid #e0ddd6",
            "border_radius":  "0px",
            "padding":        "1.75rem",
            "meta_icon_color":"#3d3b8e",
        },
    },
    "images": {
        "main_article_image": "",
        "ingredient_image":   "",
        "recipe_card_image":  "",
    },
    "structure_template": {
        "word_counts": {
            "intro_p1":              120,
            "intro_p2":               80,
            "highlights_item_1":      30,
            "highlights_item_2":      30,
            "highlights_item_3":      30,
            "highlights_item_4":      30,
            "ingredients_intro":      40,
            "instructions_step_1":    65,
            "instructions_step_2":    65,
            "instructions_step_3":    65,
            "instructions_step_4":    65,
            "tips_aside":             80,
            "conclusion":             65,
            "faq_1_answer":           55,
            "faq_2_answer":           55,
            "faq_3_answer":           55,
        }
    },
    "dark_mode": False,
}

STRUCTURE = [
    {"key": "intro_p1",            "type": "intro",       "label": "Introduction"},
    {"key": "intro_p2",            "type": "paragraph",   "label": "Introduction cont."},
    {"key": "highlights",          "type": "h2",          "label": "Highlights"},
    {"key": "highlights_item_1",   "type": "bullet_list", "label": ""},
    {"key": "highlights_item_2",   "type": "bullet_list", "label": ""},
    {"key": "highlights_item_3",   "type": "bullet_list", "label": ""},
    {"key": "highlights_item_4",   "type": "bullet_list", "label": ""},
    {"key": "ingredients_intro",   "type": "h2",          "label": "Ingredients"},
    {"key": "instructions_intro",  "type": "h2",          "label": "Preparation"},
    {"key": "instructions_step_1", "type": "h3",          "label": "Step 1"},
    {"key": "instructions_step_2", "type": "h3",          "label": "Step 2"},
    {"key": "instructions_step_3", "type": "h3",          "label": "Step 3"},
    {"key": "instructions_step_4", "type": "h3",          "label": "Step 4"},
    {"key": "tips_aside",          "type": "pro_tips_box","label": "Helpful Notes"},
    {"key": "conclusion",          "type": "conclusion",  "label": "Final Thoughts"},
    {"key": "faqs",                "type": "faq",         "label": "Common Questions"},
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
            "You are a refined food writer with a calm, contemplative tone. "
            "Write engaging, SEO-friendly content with sensory detail. "
            "Output plain text only: no markdown. "
            f"All content must be only about: {self.title}."
        )
        raw = ai_chat(self, prompt, max_tokens=max_tokens, system=system)
        return self._strip_markdown(raw) if raw else ""

    def _gen_intro_p1(self):
        return self._chat(
            f"Write a contemplative 120-word opening paragraph for {self.title}. "
            "Use sensory details. Plain text, no headers.", 280
        )

    def _gen_intro_p2(self):
        return self._chat(
            f"Write an 80-word second paragraph for {self.title}. "
            "Mention why this recipe is special. Plain text.", 200
        )

    def _gen_highlights(self):
        raw = self._chat(
            f"Give exactly 4 highlights of {self.title}. "
            "Format: ShortPhrase: one sentence. One per line. No bullets.", 220
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        while len(lines) < 4:
            lines.append(f"Simple Preparation: {self.title} uses only a handful of ingredients.")
        return lines[:4]

    def _gen_ingredients_intro(self):
        return self._chat(
            f"Write a 40-word intro for the ingredients section of {self.title}. Plain text.", 100
        )

    def _gen_ingredient_list(self):
        raw = self._chat(
            f"List exactly 8 ingredients for {self.title} with measurements. One per line.", 180
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        return lines[:10] if lines else [f"Ingredient {i+1}" for i in range(8)]

    def _gen_step(self, num):
        raw = self._chat(
            f"Write step {num} for making {self.title}. "
            "Format: HEADING: <5 word heading>\nBODY: <65 word paragraph>", 200
        )
        heading, body = f"Step {num}", raw
        for line in (raw or "").splitlines():
            s = line.strip()
            if s.upper().startswith("HEADING:"):
                heading = s.split(":", 1)[-1].strip() or heading
            elif s.upper().startswith("BODY:"):
                body = s.split(":", 1)[-1].strip() or body
        return {"heading": heading, "body": body}

    def _gen_tips(self):
        raw = self._chat(
            f"Write 3 helpful notes for making {self.title}. "
            "Each: ShortPhrase: one sentence. One per line. No markdown.", 200
        )
        lines = [self._strip_markdown(l.strip()) for l in raw.splitlines() if l.strip()]
        while len(lines) < 3:
            lines.append(f"Fresh Ingredients: Use the freshest ingredients for {self.title}.")
        return lines[:4]

    def _gen_conclusion(self):
        return self._chat(
            f"Write a calm 65-word conclusion for {self.title}. "
            "Encourage readers to try it. Plain text.", 180
        )

    def _gen_faqs(self):
        raw = self._chat(
            f"Write exactly 3 FAQ Q&A about {self.title}. "
            "Format: Q1: question\nA1: 55-word answer\nQ2:...\nA2:...\nQ3:...\nA3:...", 420
        )
        faqs = []
        for i in range(1, 4):
            q, a = None, None
            for line in raw.splitlines():
                ls = line.strip()
                if ls.upper().startswith(f"Q{i}:"):
                    q = ls.split(":", 1)[-1].strip()
                elif ls.upper().startswith(f"A{i}:"):
                    a = ls.split(":", 1)[-1].strip()
            if not q:
                q = f"What is the best way to serve {self.title}?"
            if not a:
                a = self._chat(f"Answer in 2-3 sentences: {q}", 100)
            faqs.append({"question": q, "answer": a or ""})
        return faqs

    def _gen_recipe(self):
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": self.title, "summary": f"A refined {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min",
                "servings": "4", "calories": "380", "course": "Main Course", "cuisine": "International",
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
                "name": self.title, "summary": f"A refined {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min",
                "servings": "4", "calories": "380", "course": "Main Course", "cuisine": "International",
            }

    def _gen_seo(self):
        defaults = {
            "recipe_title_pin":      self.title[:100],
            "pinterest_title":       self.title[:100],
            "pinterest_description": f"This {self.title} recipe is simple and full of flavor.",
            "pinterest_keywords":    f"{self.title}, recipe, easy, homemade, delicious",
            "focus_keyphrase":       self.title.lower(),
            "meta_description":      f"Learn how to make {self.title} with this simple recipe."[:140],
            "keyphrase_synonyms":    f"{self.title} recipe, easy {self.title}, homemade {self.title}",
        }
        raw = self._chat(
            f"Generate SEO metadata for {self.title}. "
            "Output valid JSON with keys: recipe_title_pin, pinterest_title, "
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
            f"Write a Midjourney prompt for editorial food photography of {self.title}. "
            "Include: overhead angle, natural light, warm tones, clean composition. End with --v 6.1", 120
        )
        ingr = self._chat(
            f"Write a Midjourney prompt for ingredients flat-lay of {self.title}. "
            "White marble, natural light, editorial style. End with --v 6.1", 120
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

    # ------------------------------------------------------------------ content (single API call for speed)
    def generate_content(self):
        from ai_client import ai_chat
        existing = self.config.get("recipe")
        recipe_from_config = existing and isinstance(existing, dict) and (existing.get("ingredients") or existing.get("instructions"))
        schema = {
            "intro_p1": "string ~120 words", "intro_p2": "string ~80 words",
            "highlights": "array of 4 strings", "ingredients_intro": "string ~40 words",
            "ingredient_list": "array of 8 strings", "steps": "array of 4 objects with heading and body",
            "tips": "array of 3 strings", "conclusion": "string ~65 words",
            "faqs": "array of 3 objects with question and answer",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine" if not recipe_from_config else "(omit)",
            "meta_description": "120-140 chars", "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1", "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        system = "You are a refined food writer. Generate the full article as ONE JSON. Plain text only: no markdown. All content only about the recipe title."
        user = f"Generate the complete recipe article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=4500, system=system)
        data = self._extract_json(raw)
        if data:
            print("[*] Generated content via single JSON.")
            intro_p1 = self._strip_markdown(str(data.get("intro_p1", "")))
            intro_p2 = self._strip_markdown(str(data.get("intro_p2", "")))
            highlights = [self._strip_markdown(str(x)) for x in (data.get("highlights") or [])[:4]]
            ing_intro = self._strip_markdown(str(data.get("ingredients_intro", "")))
            ing_list = [str(x).strip() for x in (data.get("ingredient_list") or [])[:10]]
            steps_raw = data.get("steps") or []
            steps = [{"heading": str(s.get("heading", f"Step {i}")).strip() if isinstance(s, dict) else f"Step {i}", "body": self._strip_markdown(str(s.get("body", "")) if isinstance(s, dict) else "")} for i, s in enumerate(steps_raw[:4], 1)]
            tips = [self._strip_markdown(str(x)) for x in (data.get("tips") or [])[:4]]
            conclusion = self._strip_markdown(str(data.get("conclusion", "")))
            faqs_raw = data.get("faqs") or []
            faqs = [{"question": str(f.get("question", "")).strip(), "answer": self._strip_markdown(str(f.get("answer", "")))} for f in faqs_raw[:3] if isinstance(f, dict)]
            if recipe_from_config:
                defaults = {"name": self.title, "summary": "", "ingredients": [], "instructions": [], "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min", "servings": "4", "calories": "380", "course": "Main Course", "cuisine": "International"}
                recipe = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
            else:
                recipe = data.get("recipe") or {}
                if not isinstance(recipe, dict) or not (recipe.get("ingredients") or recipe.get("instructions")):
                    recipe = {"name": self.title, "summary": f"A refined {self.title} recipe.", "ingredients": ing_list[:20] if ing_list else [], "instructions": [s.get("body", "") for s in steps][:15] if steps else [], "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min", "servings": "4", "calories": "380", "course": "Main Course", "cuisine": "International"}
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            seo = {"recipe_title_pin": (str(data.get("pinterest_title", self.title)) or self.title)[:100], "pinterest_title": (str(data.get("pinterest_title", "")) or self.title)[:100], "pinterest_description": f"This {self.title} recipe is simple and full of flavor.", "pinterest_keywords": f"{self.title}, recipe, easy, homemade", "focus_keyphrase": self.title.lower(), "meta_description": (str(data.get("meta_description", "")) or f"Learn how to make {self.title}.")[:140], "keyphrase_synonyms": f"{self.title} recipe, easy {self.title}"}
            mj_main = str(data.get("prompt_midjourney_main", "") or "").strip()
            mj_ing = str(data.get("prompt_midjourney_ingredients", "") or "").strip()
            mj = {"main": mj_main if mj_main and "--v 6.1" in mj_main else f"Editorial food photography of {self.title} --v 6.1", "ingredients": mj_ing if mj_ing and "--v 6.1" in mj_ing else f"Ingredients flat-lay for {self.title} --v 6.1"}
        else:
            print("[*] Generating intro_p1...")
            intro_p1 = self._gen_intro_p1()
            print("[*] Generating intro_p2...")
            intro_p2 = self._gen_intro_p2()
            print("[*] Generating highlights...")
            highlights = self._gen_highlights()
            print("[*] Generating ingredients...")
            ing_intro = self._gen_ingredients_intro()
            ing_list = self._gen_ingredient_list()
            print("[*] Generating steps 1-4...")
            steps = [self._gen_step(i) for i in range(1, 5)]
            print("[*] Generating tips...")
            tips = self._gen_tips()
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
            {"key": "intro_p1",           "content": intro_p1},
            {"key": "intro_p2",           "content": intro_p2},
            {"key": "highlights",         "content": highlights},
            {"key": "ingredients_intro",  "content": ing_intro},
            {"key": "ingredient_list",    "content": ing_list},
            {"key": "instructions_steps", "content": steps},
            {"key": "tips",               "content": tips},
            {"key": "conclusion",         "content": conclusion},
            {"key": "faqs",               "content": faqs},
        ]

        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": f"generator-5 / title: {self.title}",
            "prompt_base": f"Minimalist Japanese-inspired food blog for: {self.title}",
            "recipe": recipe,
            **seo,
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
        pt = cp["pro_tips_box"]
        rc = cp["recipe_card"]
        bl = cp["bullet_list"]

        import_url = build_font_import_url(f)
        body_font = font_family_css(f["body"]["family"], "sans-serif")
        heading_font = font_family_css(f["heading"]["family"], "serif")

        return f"""/* generator-5 | Minimalist Japanese-Inspired */
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

.article-wrap {{
    max-width: {l['max_width']};
    margin: 0 auto;
    padding: 0 {l['container_padding']} 3rem;
}}

/* --- Header --- */
.article-header.g5-header {{ margin-bottom: {l['section_spacing']}; }}
.article-header.g5-header .article-title {{
    font-family: {heading_font};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 700;
    color: {c['text_primary']};
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
    letter-spacing: -0.01em;
}}
.article-header.g5-header .article-byline-row {{
    display: flex; flex-wrap: wrap; justify-content: space-between;
    align-items: center; gap: 0.5rem;
    padding-top: 0.75rem; border-top: 1px solid {c['border']};
}}
.article-header.g5-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g5-header .byline-author {{ font-weight: 600; color: {c['text_primary']}; font-size: 0.9rem; }}
.article-header.g5-header .byline-date {{ font-size: 0.8rem; color: {c['text_secondary']}; }}
.article-header.g5-header .byline-disclaimer {{ font-size: 0.75rem; color: {c['text_secondary']}; font-style: italic; margin-top: 0.2rem; }}
.article-header.g5-header .byline-right {{ display: flex; align-items: center; gap: 0.75rem; }}
.article-header.g5-header .recipe-meta-bar {{ display: flex; gap: 1.25rem; font-size: 0.8rem; color: {c['text_secondary']}; }}

/* --- Typography --- */
h1 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h1']}; font-weight: 700; color: {c['text_primary']}; line-height: 1.2; margin-bottom: 1rem; }}
h2 {{
    font-family: {heading_font}; font-size: {f['heading']['sizes']['h2']}; font-weight: 700;
    color: {c['text_primary']}; margin-top: {l['section_spacing']};
    margin-bottom: 0.75rem; letter-spacing: -0.01em;
    padding-bottom: 0.35rem; border-bottom: 1px solid {c['border']};
}}
h3 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h3']}; font-weight: 700; color: {c['text_primary']}; margin-top: 1.5rem; margin-bottom: 0.4rem; }}
p {{ color: {c['text_secondary']}; margin-bottom: {l['paragraph_spacing']}; }}
a {{ color: {c['link']}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* --- Hero image (sharp edges) --- */
.hero-image {{
    width: 100%; height: auto; display: block;
    margin: 1.25rem 0; object-fit: cover; max-height: 450px;
}}

/* --- Highlights list (square bullets) --- */
.highlights-list {{ list-style: none; padding: 0; margin: 0.5rem 0 1.25rem; }}
.highlights-list li {{
    position: relative; padding-left: 1.4rem; margin-bottom: {l['list_spacing']};
    color: {c['text_secondary']}; line-height: 1.7;
}}
.highlights-list li::before {{
    content: ""; position: absolute; left: 0; top: 0.5em;
    width: 7px; height: 7px; background: {bl['color']};
}}
.highlights-list li strong {{ color: {c['text_primary']}; font-weight: 700; }}

/* --- Ingredient list --- */
.ingredient-list {{ list-style: none; padding: 0; margin: 0.5rem 0 1.25rem; border: 1px solid {c['border']}; padding: 1rem 1.25rem; }}
.ingredient-list li {{
    position: relative; padding-left: 1.2rem; margin-bottom: {l['list_spacing']};
    color: {c['text_secondary']}; padding-bottom: 0.4rem;
    border-bottom: 1px dotted {c['border']};
}}
.ingredient-list li:last-child {{ border-bottom: none; }}
.ingredient-list li::before {{
    content: ""; position: absolute; left: 0; top: 0.55em;
    width: 6px; height: 6px; background: {bl['color']};
}}

/* --- Steps (plain numbers, no circles) --- */
.steps-list {{ list-style: none; padding: 0; margin: 0.75rem 0 1.25rem; }}
.step-item {{ display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1.5rem; }}
.step-number {{
    flex-shrink: 0; font-family: {heading_font};
    font-size: 1.6rem; font-weight: 700; color: {c['primary']};
    line-height: 1; min-width: 1.6rem; padding-top: 0.05rem;
}}
.step-body h3 {{ margin-top: 0; margin-bottom: 0.3rem; font-size: 1rem; }}
.step-body p {{ margin: 0; font-size: 0.94rem; }}

/* --- Tips aside --- */
.tips-aside {{
    background: {pt['bg_color']}; border-left: {pt['border_left']};
    padding: {pt['padding']}; margin: {l['section_spacing']} 0;
}}
.tips-aside h2 {{ margin-top: 0; border: none; padding: 0; font-size: 1.2rem; color: {c['primary']}; }}
.tips-list {{ list-style: none; padding: 0; margin: 0.5rem 0 0; }}
.tips-list li {{
    padding: 0.4rem 0; color: {c['text_secondary']};
    border-bottom: 1px solid rgba(61,59,142,0.1);
}}
.tips-list li:last-child {{ border-bottom: none; }}
.tips-list li strong {{ color: {c['text_primary']}; }}

/* --- FAQ --- */
.faq-section {{ margin: {l['section_spacing']} 0; }}
.faq-item {{ border-bottom: 1px solid {c['border']}; }}
.faq-item:last-child {{ border-bottom: none; }}
.faq-question {{
    width: 100%; background: none; border: none; text-align: left;
    padding: 1rem 0; font-family: {heading_font}; font-size: 1rem;
    font-weight: 700; color: {c['text_primary']}; cursor: pointer;
    display: flex; justify-content: space-between; align-items: center;
}}
.faq-question::after {{ content: '+'; font-size: 1.2rem; color: {c['primary']}; }}
.faq-question.open::after {{ content: '\\2212'; }}
.faq-answer {{ display: none; padding: 0 0 1rem 0; color: {c['text_secondary']}; }}
.faq-answer.open {{ display: block; }}

/* --- Recipe card --- */
.recipe-card {{
    background: {rc['bg']}; border: {rc['border']};
    padding: {rc['padding']}; margin: {l['section_spacing']} 0;
}}
.recipe-card h2 {{ margin-top: 0; text-align: center; color: {c['primary']}; border: none; }}
.recipe-card-image {{
    width: 100%; height: 240px; object-fit: cover; margin: 1rem 0; display: block;
}}
.recipe-meta-strip {{
    display: flex; gap: 0; margin: 1rem 0; border-top: 1px solid {c['border']}; border-bottom: 1px solid {c['border']};
}}
.recipe-meta-strip .meta-cell {{
    flex: 1; text-align: center; padding: 0.75rem 0.5rem;
    border-right: 1px solid {c['border']};
}}
.recipe-meta-strip .meta-cell:last-child {{ border-right: none; }}
.meta-cell-label {{ font-size: 0.65rem; text-transform: uppercase; color: {c['text_secondary']}; letter-spacing: 0.08em; }}
.meta-cell-value {{ font-size: 0.95rem; font-weight: 700; color: {c['primary']}; display: block; margin-top: 2px; }}
.recipe-card-buttons {{ display: flex; gap: 0.75rem; margin: 1rem 0; }}
.btn-print {{
    flex: 1; background: {c['button_print']}; color: #fff; border: none;
    padding: 0.7rem 1rem; cursor: pointer; font-weight: 600; font-size: 0.85rem;
    transition: background 0.2s; font-family: {body_font};
}}
.btn-print:hover {{ background: {c['button_hover_print']}; }}
.btn-pin {{
    flex: 1; background: {c['button_pin']}; color: #fff; border: none;
    padding: 0.7rem 1rem; cursor: pointer; font-weight: 600; font-size: 0.85rem;
    transition: background 0.2s; font-family: {body_font};
}}
.btn-pin:hover {{ background: {c['button_hover_pin']}; }}
.recipe-ingredients-list {{ list-style: none; padding: 0; }}
.recipe-ingredients-list li {{
    padding: 0.4rem 0; color: {c['text_secondary']};
    border-bottom: 1px dotted {c['border']};
}}
.recipe-ingredients-list li:last-child {{ border-bottom: none; }}
.recipe-instructions-list {{ list-style: none; padding: 0; counter-reset: rinst; }}
.recipe-instructions-list li {{
    counter-increment: rinst; padding: 0.5rem 0 0.5rem 2rem;
    position: relative; color: {c['text_secondary']};
    border-bottom: 1px dotted {c['border']};
}}
.recipe-instructions-list li:last-child {{ border-bottom: none; }}
.recipe-instructions-list li::before {{
    content: counter(rinst); position: absolute; left: 0; top: 0.5rem;
    font-family: {heading_font}; font-size: 1.1rem; font-weight: 700; color: {c['primary']};
}}

@media print {{ body {{ background: white; }} }}
@media (max-width: 600px) {{ h1 {{ font-size: 1.5rem; }} .recipe-card-buttons {{ flex-direction: column; }} }}"""

    # ------------------------------------------------------------------ HTML
    def generate_html(self, sections, css_filename="css.css"):
        t = self.title
        imgs = self.config["images"]
        main_img = imgs.get("main_article_image") or "placeholder.jpg"
        card_img = imgs.get("recipe_card_image") or main_img

        sec = {}
        for s in sections:
            sec[s["key"]] = s["content"]

        highlights = sec.get("highlights", [])
        hl_html = "".join(f"  <li>{h}</li>\n" for h in highlights)

        ing_list = sec.get("ingredient_list", [])
        ing_li = "".join(f"  <li>{it}</li>\n" for it in ing_list)

        steps = sec.get("instructions_steps", [])
        steps_html = ""
        for i, step in enumerate(steps):
            h = step.get("heading", f"Step {i+1}")
            b = step.get("body", "")
            steps_html += f'<div class="step-item"><span class="step-number">{i+1}.</span><div class="step-body"><h3>{h}</h3><p>{b}</p></div></div>\n'

        tips = sec.get("tips", [])
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
<div class="article-wrap">

<header class="article-header g5-header">
  <h1 class="article-title">{t}</h1>
  <div class="article-byline-row">
    <div class="byline-left">
      <span class="byline-author">By <span class="article-author"></span></span>
      <span class="byline-date"><span class="article-date"></span></span>
      <p class="byline-disclaimer">This post may contain affiliate links.</p>
    </div>
    <div class="byline-right">
      <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin</button>
      <div class="recipe-meta-bar"><span>{r_prep}</span><span>{r_cook}</span><span>{r_srv} servings</span></div>
    </div>
  </div>
</header>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<p>{sec.get('intro_p1','')}</p>
<p>{sec.get('intro_p2','')}</p>

<h2>Highlights</h2>
<ul class="highlights-list">
{hl_html}</ul>

<h2>Ingredients</h2>
<p>{sec.get('ingredients_intro','')}</p>
<ul class="ingredient-list">
{ing_li}</ul>

<h2>Preparation</h2>
{steps_html}

<div class="tips-aside">
  <h2>Helpful Notes</h2>
  <ul class="tips-list">
{tips_li}  </ul>
</div>

<h2>Final Thoughts</h2>
<p>{sec.get('conclusion','')}</p>

<div class="faq-section">
  <h2>Common Questions</h2>
{faq_html}</div>

<!-- inject:before-recipe -->
<div class="recipe-card" id="recipe-card">
  <h2>{r_name}</h2>
  <img src="{card_img}" alt="{r_name}" class="recipe-card-image">
  <div class="recipe-meta-strip">
    <div class="meta-cell"><span class="meta-cell-label">Prep</span><span class="meta-cell-value">{r_prep}</span></div>
    <div class="meta-cell"><span class="meta-cell-label">Cook</span><span class="meta-cell-value">{r_cook}</span></div>
    <div class="meta-cell"><span class="meta-cell-label">Total</span><span class="meta-cell-value">{r_total}</span></div>
    <div class="meta-cell"><span class="meta-cell-label">Servings</span><span class="meta-cell-value">{r_srv}</span></div>
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
    gen = ArticleGenerator({"title": "Matcha Soufflé Pancakes"})
    gen.run()
