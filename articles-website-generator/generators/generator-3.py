"""
generator-3.py
--------------
Dark Moody Recipe Blog — Stitch-designed template.

Design: Dark navy/charcoal (#1a1f2e) background, gold (#d4a853) accents,
cream (#f0e6d3) text. Merriweather serif headings, Source Sans Pro body.
Elegant, luxurious feel — pro tips on dark cards, gold numbered circles.

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
        "primary":            "#d4a853",
        "secondary":          "#2a3040",
        "accent":             "#e8b95a",
        "background":         "#1a1f2e",
        "container_bg":       "#222838",
        "border":             "#3a4050",
        "text_primary":       "#f0e6d3",
        "text_secondary":     "#b8b0a0",
        "button_print":       "#d4a853",
        "button_pin":         "#E60023",
        "button_hover_print": "#e8b95a",
        "button_hover_pin":   "#FF1A3C",
        "link":               "#d4a853",
        "list_marker":        "#d4a853",
    },
    "fonts": {
        "heading": {
            "family":  "Merriweather",
            "weights": [400, 700],
            "sizes":   {"h1": "2.2rem", "h2": "1.6rem", "h3": "1.2rem"},
        },
        "body": {
            "family":      "Source Sans Pro",
            "weight":      400,
            "size":        "1rem",
            "line_height": 1.78,
        },
    },
    "layout": {
        "max_width":         "800px",
        "section_spacing":   "2.5rem",
        "paragraph_spacing": "1.2rem",
        "list_spacing":      "0.6rem",
        "container_padding": "2rem",
        "border_radius":     "8px",
        "box_shadow":        "0 4px 24px rgba(0,0,0,0.3)",
    },
    "components": {
        "numbered_list": {
            "style":       "circle",
            "circle_bg":   "#d4a853",
            "circle_color":"#1a1f2e",
            "circle_size": "32px",
        },
        "bullet_list": {
            "style": "disc",
            "color": "#d4a853",
        },
        "pro_tips_box": {
            "bg_color":     "#2a3040",
            "border_color": "#d4a853",
            "border_left":  "4px solid #d4a853",
            "padding":      "1.5rem",
        },
        "recipe_card": {
            "bg":             "#222838",
            "border":         "1px solid #3a4050",
            "border_radius":  "12px",
            "padding":        "2rem",
            "meta_icon_color":"#d4a853",
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
            "why_i_love_item_1":      30,
            "why_i_love_item_2":      30,
            "why_i_love_item_3":      30,
            "why_i_love_item_4":      30,
            "ingredients_intro":      50,
            "instructions_step_1":    70,
            "instructions_step_2":    70,
            "instructions_step_3":    70,
            "instructions_step_4":    70,
            "instructions_step_5":    70,
            "pro_tip_1":              35,
            "pro_tip_2":              35,
            "pro_tip_3":              35,
            "pro_tip_4":              35,
            "serving_suggestions":    60,
            "conclusion":             80,
            "faq_1_answer":           55,
            "faq_2_answer":           55,
            "faq_3_answer":           55,
        }
    },
    "dark_mode": True,
}

STRUCTURE = [
    {"key": "intro",               "type": "intro",       "label": "Introduction"},
    {"key": "why_i_love",          "type": "h2",          "label": "Why You'll Love This"},
    {"key": "why_i_love_item_1",   "type": "bullet_list", "label": ""},
    {"key": "why_i_love_item_2",   "type": "bullet_list", "label": ""},
    {"key": "why_i_love_item_3",   "type": "bullet_list", "label": ""},
    {"key": "why_i_love_item_4",   "type": "bullet_list", "label": ""},
    {"key": "ingredients_intro",   "type": "h2",          "label": "Ingredients"},
    {"key": "instructions_intro",  "type": "h2",          "label": "How to Make {title}"},
    {"key": "instructions_step_1", "type": "h3",          "label": "Step 1"},
    {"key": "instructions_step_2", "type": "h3",          "label": "Step 2"},
    {"key": "instructions_step_3", "type": "h3",          "label": "Step 3"},
    {"key": "instructions_step_4", "type": "h3",          "label": "Step 4"},
    {"key": "instructions_step_5", "type": "h3",          "label": "Step 5"},
    {"key": "pro_tips",            "type": "pro_tips_box","label": "Pro Tips"},
    {"key": "serving_suggestions", "type": "h2",          "label": "Serving Suggestions"},
    {"key": "conclusion",          "type": "conclusion",  "label": "Final Thoughts"},
    {"key": "faqs",                "type": "faq",         "label": "FAQ"},
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
            "You are a professional food blogger. Write engaging, SEO-friendly content. "
            "Output plain text only: no markdown (no ##, ###, ####, no ** or *, no - bullets). "
            f"All content must be only about: {self.title}."
        )
        raw = ai_chat(self, prompt, max_tokens=max_tokens, system=system)
        return self._strip_markdown(raw) if raw else ""

    def _gen_intro(self):
        return self._chat(
            f"Write a compelling 120-word intro paragraph for a food blog article about {self.title}. "
            "Draw the reader in with sensory details and warmth. Plain text, no headers."
        )

    def _gen_why_items(self):
        raw = self._chat(
            f"Give exactly 4 reasons why readers will love {self.title}. "
            "Format each: ShortPhrase: one sentence. One per line. No bullets/numbers.",
            250
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        while len(lines) < 4:
            lines.append(f"Easy to Make: {self.title} comes together quickly.")
        return lines[:4]

    def _gen_ingredients_intro(self):
        return self._chat(
            f"Write a 50-word intro for the ingredients section of {self.title}. Plain text.",
            120
        )

    def _gen_ingredient_list(self):
        raw = self._chat(
            f"List exactly 10 ingredients for {self.title} with measurements. One per line. No bullets.",
            200
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        return lines[:10] if lines else [f"Ingredient {i+1}" for i in range(10)]

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

    def _gen_pro_tips(self):
        raw = self._chat(
            f"Give exactly 4 pro tips for making {self.title}. "
            "Each: ShortPhrase: one sentence. One per line. No markdown.", 250
        )
        lines = [self._strip_markdown(l.strip()) for l in raw.splitlines() if l.strip()]
        while len(lines) < 4:
            lines.append(f"Season Well: Proper seasoning elevates {self.title}.")
        return lines[:4]

    def _gen_serving(self):
        return self._chat(
            f"Write a 60-word paragraph with serving suggestions for {self.title}. Plain text.", 150
        )

    def _gen_conclusion(self):
        return self._chat(
            f"Write a warm 80-word conclusion for a food blog about {self.title}. "
            "Encourage readers to try it. Plain text.", 200
        )

    def _gen_faqs(self):
        raw = self._chat(
            f"Write exactly 3 FAQ Q&A about {self.title}. "
            "Format: Q1: question\nA1: 55-word answer\nQ2: ...\nA2: ...\nQ3: ...\nA3: ...",
            420
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
                q = f"How should I store leftover {self.title}?"
            if not a:
                a = self._chat(f"Answer in 2-3 sentences: {q}", 100)
            faqs.append({"question": q, "answer": a or ""})
        return faqs

    def _gen_recipe(self):
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": self.title, "summary": f"A delicious {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min",
                "servings": "4", "calories": "450", "course": "Main Course", "cuisine": "American",
            }
            return {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        raw = self._chat(
            f"Create a recipe for {self.title} as valid JSON with keys: "
            "name, summary, ingredients (array), instructions (array), "
            "prep_time, cook_time, total_time, servings, calories, course, cuisine. "
            "Output only raw JSON, no markdown fences.", 650
        )
        try:
            clean = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
            return json.loads(clean)
        except Exception:
            return {
                "name": self.title, "summary": f"A delicious {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min",
                "servings": "4", "calories": "450", "course": "Main Course", "cuisine": "American",
            }

    def _gen_seo(self):
        defaults = {
            "recipe_title_pin":      self.title[:100],
            "pinterest_title":       self.title[:100],
            "pinterest_description": f"This {self.title} recipe is easy and full of flavor.",
            "pinterest_keywords":    f"{self.title}, recipe, easy, dinner, homemade, delicious",
            "focus_keyphrase":       self.title.lower(),
            "meta_description":      f"Learn how to make {self.title} with this step-by-step recipe."[:140],
            "keyphrase_synonyms":    f"{self.title} recipe, easy {self.title}, homemade {self.title}",
        }
        raw = self._chat(
            f"Generate SEO metadata for a food blog about {self.title}. "
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
            f"Write a Midjourney prompt for moody, dark food photography of {self.title}. "
            "Include: dramatic lighting, dark background, shallow depth of field. End with --v 6.1", 120
        )
        ingr = self._chat(
            f"Write a Midjourney prompt for dark flat-lay of ingredients for {self.title}. "
            "Dark marble surface, moody lighting. End with --v 6.1", 120
        )
        if "--v 6.1" not in (main or ""):
            main = (main or "") + " --v 6.1"
        if "--v 6.1" not in (ingr or ""):
            ingr = (ingr or "") + " --v 6.1"
        return {"main": main, "ingredients": ingr}

    def _extract_json(self, raw):
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
            "intro": "string ~120 words", "why_items": "array of 4 strings (Label: sentence)",
            "ingredients_intro": "string ~50 words", "ingredient_list": "array of 10 strings",
            "steps": "array of 5 objects with heading and body",
            "pro_tips": "array of 4 strings", "serving": "string ~60 words",
            "conclusion": "string ~80 words",
            "faqs": "array of 3 objects with question and answer",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine" if not recipe_from_config else "(omit)",
            "meta_description": "120-140 chars", "focus_keyphrase": "string", "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1", "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        system = "You are a professional food blogger. Generate the full article as ONE JSON. Plain text only: no markdown. All content only about the recipe title."
        user = f"Generate the complete recipe article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=5000, system=system)
        data = self._extract_json(raw)
        if data:
            intro = self._strip_markdown(str(data.get("intro", "")))
            why_items = [self._strip_markdown(str(x)) for x in (data.get("why_items") or [])[:4]]
            ing_intro = self._strip_markdown(str(data.get("ingredients_intro", "")))
            ing_list = [str(x).strip() for x in (data.get("ingredient_list") or [])[:10]]
            steps_raw = data.get("steps") or []
            steps = [{"heading": str(s.get("heading", f"Step {i}")).strip() if isinstance(s, dict) else f"Step {i}", "body": self._strip_markdown(str(s.get("body", "")) if isinstance(s, dict) else "")} for i, s in enumerate(steps_raw[:5], 1)]
            tips = [self._strip_markdown(str(x)) for x in (data.get("pro_tips") or [])[:4]]
            serving = self._strip_markdown(str(data.get("serving", "")))
            conclusion = self._strip_markdown(str(data.get("conclusion", "")))
            faqs_raw = data.get("faqs") or []
            faqs = [{"question": str(f.get("question", "")).strip(), "answer": self._strip_markdown(str(f.get("answer", "")))} for f in faqs_raw[:3] if isinstance(f, dict)]
            if recipe_from_config:
                defaults = {"name": self.title, "summary": "", "ingredients": [], "instructions": [], "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min", "servings": "4", "calories": "450", "course": "Main Course", "cuisine": "American"}
                recipe = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
            else:
                recipe = data.get("recipe") or {}
                if isinstance(recipe, dict) and (recipe.get("ingredients") or recipe.get("instructions")):
                    pass
                else:
                    recipe = {"name": self.title, "summary": f"A delicious {self.title} recipe.", "ingredients": ing_list[:20] if ing_list else [], "instructions": [s.get("body", "") for s in steps][:15] if steps else [], "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min", "servings": "4", "calories": "450", "course": "Main Course", "cuisine": "American"}
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            seo = {"recipe_title_pin": (str(data.get("pinterest_title", self.title)) or self.title)[:100], "pinterest_title": (str(data.get("pinterest_title", "")) or self.title)[:100], "pinterest_description": f"This {self.title} recipe is easy and full of flavor.", "pinterest_keywords": f"{self.title}, recipe, easy, dinner, homemade", "focus_keyphrase": str(data.get("focus_keyphrase", self.title.lower())), "meta_description": (str(data.get("meta_description", "")) or f"Learn how to make {self.title}.")[:140], "keyphrase_synonyms": f"{self.title} recipe, easy {self.title}"}
            mj_main = str(data.get("prompt_midjourney_main", "") or "").strip()
            mj_ing = str(data.get("prompt_midjourney_ingredients", "") or "").strip()
            mj = {"main": mj_main if mj_main and "--v 6.1" in mj_main else f"Moody food photography of {self.title}, dark background --v 6.1", "ingredients": mj_ing if mj_ing and "--v 6.1" in mj_ing else f"Dark flat-lay ingredients for {self.title} --v 6.1"}
        else:
            intro = self._gen_intro()
            why_items = self._gen_why_items()
            ing_intro = self._gen_ingredients_intro()
            ing_list = self._gen_ingredient_list()
            steps = [self._gen_step(i) for i in range(1, 6)]
            tips = self._gen_pro_tips()
            serving = self._gen_serving()
            conclusion = self._gen_conclusion()
            faqs = self._gen_faqs()
            recipe = self._gen_recipe()
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            seo = self._gen_seo()
            mj = self._gen_midjourney()

        from ai_client import get_first_category
        cat = get_first_category(self.config)
        main_img = self.config["images"].get("main_article_image") or "placeholder.jpg"

        sections = [
            {"key": "intro",              "content": intro},
            {"key": "why_i_love_items",   "content": why_items},
            {"key": "ingredients_intro",  "content": ing_intro},
            {"key": "ingredient_list",    "content": ing_list},
            {"key": "instructions_steps", "content": steps},
            {"key": "pro_tips",           "content": tips},
            {"key": "serving_suggestions","content": serving},
            {"key": "conclusion",         "content": conclusion},
            {"key": "faqs",               "content": faqs},
        ]

        content_data = {
            "title":                     self.title,
            "slug":                      self.slug,
            "categorieId":               str(cat.get("id", 1)),
            "categorie":                 cat.get("categorie", "dinner"),
            "sections":                  sections,
            "article_html":              "",
            "article_css":               "",
            "prompt_used":               f"generator-3 / title: {self.title}",
            "prompt_base":               f"Dark moody food blog article for: {self.title}",
            "recipe":                    recipe,
            "recipe_title_pin":          seo["recipe_title_pin"],
            "pinterest_title":           seo["pinterest_title"],
            "pinterest_description":     seo["pinterest_description"],
            "pinterest_keywords":        seo["pinterest_keywords"],
            "focus_keyphrase":           seo["focus_keyphrase"],
            "meta_description":          seo["meta_description"],
            "keyphrase_synonyms":        seo["keyphrase_synonyms"],
            "main_image":                main_img,
            "ingredient_image":          self.config["images"].get("ingredient_image") or "placeholder.jpg",
            "prompt_midjourney_main":    mj["main"],
            "prompt_midjourney_ingredients": mj["ingredients"],
        }
        return content_data

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

        return f"""/* generator-3 | Dark Moody Recipe Blog */
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
    background: {c['container_bg']};
    border-radius: {l['border_radius']};
    box-shadow: {l['box_shadow']};
}}

/* --- Header --- */
.article-header.g3-header {{ margin-bottom: {l['section_spacing']}; }}
.article-header.g3-header .article-title {{
    font-family: {heading_font};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 700;
    color: {c['text_primary']};
    margin: 0 0 0.75rem 0;
    line-height: 1.25;
}}
.article-header.g3-header .article-byline-row {{
    display: flex; flex-wrap: wrap; justify-content: space-between;
    align-items: center; gap: 0.5rem;
}}
.article-header.g3-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g3-header .byline-author {{ font-weight: 600; color: {c['primary']}; }}
.article-header.g3-header .byline-date {{ font-size: 0.875rem; color: {c['text_secondary']}; }}
.article-header.g3-header .byline-disclaimer {{ font-size: 0.8rem; color: {c['text_secondary']}; font-style: italic; margin-top: 0.2rem; }}
.article-header.g3-header .byline-right {{ display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }}
.article-header.g3-header .recipe-meta-inline {{
    display: flex; gap: 1rem; font-size: 0.9rem; color: {c['primary']};
}}

/* --- Typography --- */
h1 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h1']}; font-weight: 700; color: {c['text_primary']}; line-height: 1.25; margin-bottom: 1rem; }}
h2 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h2']}; font-weight: 700; color: {c['primary']}; margin-top: {l['section_spacing']}; margin-bottom: 0.75rem; padding-bottom: 0.4rem; border-bottom: 1px solid {c['border']}; }}
h3 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h3']}; font-weight: 700; color: {c['text_primary']}; margin-top: 1.5rem; margin-bottom: 0.5rem; }}
p {{ color: {c['text_secondary']}; margin-bottom: {l['paragraph_spacing']}; }}
a {{ color: {c['link']}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* --- Hero --- */
.hero-image {{
    width: 100%; height: auto; display: block;
    border-radius: {l['border_radius']};
    margin: 1.25rem 0;
    object-fit: cover; max-height: 480px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}}

/* --- Why love list --- */
.why-love-list {{ list-style: none; padding: 0; margin: 0.5rem 0 1.25rem; }}
.why-love-list li {{
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 0.75rem 0; border-bottom: 1px solid {c['border']};
    color: {c['text_secondary']};
}}
.why-love-list li:last-child {{ border-bottom: none; }}
.why-love-number {{
    flex-shrink: 0; width: {nl['circle_size']}; height: {nl['circle_size']};
    background: {nl['circle_bg']}; color: {nl['circle_color']};
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.9rem;
}}
.why-love-list li strong {{ color: {c['text_primary']}; }}

/* --- Ingredient list --- */
.ingredient-list {{ list-style: none; padding: 0; margin: 0.5rem 0 1.25rem; columns: 2; column-gap: 2rem; }}
.ingredient-list li {{
    position: relative; padding-left: 1.4rem; margin-bottom: {l['list_spacing']};
    color: {c['text_secondary']}; break-inside: avoid;
}}
.ingredient-list li::before {{
    content: ""; position: absolute; left: 0; top: 0.55em;
    width: 7px; height: 7px; border-radius: 50%; background: {c['list_marker']};
}}

/* --- Steps --- */
.step-item {{ display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1.5rem; }}
.step-number {{
    flex-shrink: 0; width: {nl['circle_size']}; height: {nl['circle_size']};
    border-radius: 50%; background: {nl['circle_bg']}; color: {nl['circle_color']};
    font-weight: 700; font-size: 0.95rem;
    display: flex; align-items: center; justify-content: center;
}}
.step-body h3 {{ margin-top: 0; margin-bottom: 0.3rem; font-size: 1rem; }}
.step-body p {{ margin: 0; font-size: 0.95rem; }}

/* --- Pro tips box --- */
.pro-tips-box {{
    background: {pt['bg_color']}; border-left: {pt['border_left']};
    padding: {pt['padding']}; border-radius: 0 {l['border_radius']} {l['border_radius']} 0;
    margin: {l['section_spacing']} 0;
}}
.pro-tips-box h2 {{ margin-top: 0; color: {c['primary']}; font-size: 1.4rem; border: none; padding: 0; }}
.pro-tips-list {{ list-style: none; padding: 0; margin: 0.75rem 0 0; }}
.pro-tips-list li {{
    padding: 0.5rem 0; color: {c['text_secondary']};
    border-bottom: 1px solid rgba(212,168,83,0.15);
}}
.pro-tips-list li:last-child {{ border-bottom: none; }}
.pro-tips-list li strong {{ color: {c['text_primary']}; }}

/* --- FAQ --- */
.faq-section {{ margin: {l['section_spacing']} 0; }}
.faq-item {{ border: 1px solid {c['border']}; border-radius: {l['border_radius']}; margin-bottom: 0.75rem; overflow: hidden; }}
.faq-question {{
    width: 100%; background: {c['secondary']}; border: none;
    text-align: left; padding: 1rem 1.2rem;
    font-family: {heading_font}; font-size: 1rem; font-weight: 700;
    color: {c['text_primary']}; cursor: pointer;
    display: flex; justify-content: space-between; align-items: center;
}}
.faq-question::after {{ content: '+'; font-size: 1.3rem; color: {c['primary']}; }}
.faq-question.open::after {{ content: '-'; }}
.faq-answer {{
    display: none; padding: 1rem 1.2rem;
    color: {c['text_secondary']}; background: {c['container_bg']};
    border-top: 1px solid {c['border']};
}}
.faq-answer.open {{ display: block; }}

/* --- Recipe card --- */
.recipe-card {{
    background: {rc['bg']}; border: {rc['border']};
    border-radius: {rc['border_radius']}; padding: {rc['padding']};
    margin: {l['section_spacing']} 0; box-shadow: {l['box_shadow']};
}}
.recipe-card h2 {{ margin-top: 0; text-align: center; color: {c['primary']}; border: none; }}
.recipe-card-image {{
    width: 100%; height: 260px; object-fit: cover;
    border-radius: {l['border_radius']}; margin: 1rem 0; display: block;
}}
.recipe-card-buttons {{ display: flex; gap: 0.75rem; margin: 1rem 0; }}
.btn-print {{
    background: {c['button_print']}; color: {c['background']}; border: none;
    padding: 0.75rem 1.5rem; border-radius: {l['border_radius']};
    cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: background 0.2s;
}}
.btn-print:hover {{ background: {c['button_hover_print']}; }}
.btn-pin {{
    background: {c['button_pin']}; color: #fff; border: none;
    padding: 0.75rem 1.5rem; border-radius: {l['border_radius']};
    cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: background 0.2s;
}}
.btn-pin:hover {{ background: {c['button_hover_pin']}; }}
.recipe-meta {{
    display: flex; flex-wrap: wrap; gap: 1rem; margin: 1rem 0;
    padding: 1rem; background: {c['background']}; border-radius: {l['border_radius']};
}}
.recipe-meta-item {{ text-align: center; flex: 1; min-width: 80px; }}
.recipe-meta-label {{ font-size: 0.7rem; text-transform: uppercase; color: {c['text_secondary']}; letter-spacing: 0.05em; }}
.recipe-meta-value {{ font-size: 1rem; font-weight: 700; color: {rc['meta_icon_color']}; display: block; margin-top: 4px; }}
.recipe-ingredients-list {{ list-style: none; padding: 0; }}
.recipe-ingredients-list li {{
    padding: 0.5rem 0 0.5rem 1.4rem; position: relative;
    color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.recipe-ingredients-list li:last-child {{ border-bottom: none; }}
.recipe-ingredients-list li::before {{
    content: ''; position: absolute; left: 0; top: 1rem;
    width: 7px; height: 7px; background: {c['list_marker']}; border-radius: 50%;
}}
.recipe-instructions-list {{ list-style: none; padding: 0; counter-reset: step-counter; }}
.recipe-instructions-list li {{
    counter-increment: step-counter; padding: 0.75rem 0 0.75rem 3rem;
    position: relative; color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.recipe-instructions-list li:last-child {{ border-bottom: none; }}
.recipe-instructions-list li::before {{
    content: counter(step-counter); position: absolute; left: 0; top: 0.6rem;
    width: 28px; height: 28px; background: {nl['circle_bg']}; color: {nl['circle_color']};
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem;
}}

@media print {{ .recipe-card-buttons {{ display: none; }} body {{ background: white; color: black; }} }}
@media (max-width: 600px) {{
    .ingredient-list {{ columns: 1; }}
    .recipe-card-buttons {{ flex-direction: column; }}
    h1 {{ font-size: 1.6rem; }}
}}"""

    # ------------------------------------------------------------------ HTML
    def generate_html(self, sections, css_filename="css.css"):
        t = self.title
        imgs = self.config["images"]
        main_img = imgs.get("main_article_image") or "placeholder.jpg"
        card_img = imgs.get("recipe_card_image") or main_img
        ing_img  = imgs.get("ingredient_image") or "placeholder.jpg"

        # Unpack sections
        sec = {}
        for s in sections:
            sec[s["key"]] = s["content"]

        # Why love items
        why_items = sec.get("why_i_love_items", [])
        why_html = ""
        for i, item in enumerate(why_items):
            why_html += f'  <li><span class="why-love-number">{i+1}</span><span>{item}</span></li>\n'

        # Ingredients
        ing_list = sec.get("ingredient_list", [])
        ing_li = "".join(f"  <li>{it}</li>\n" for it in ing_list)

        # Steps
        steps = sec.get("instructions_steps", [])
        steps_html = ""
        for i, step in enumerate(steps):
            h = step.get("heading", f"Step {i+1}")
            b = step.get("body", "")
            steps_html += f"""<div class="step-item">
  <span class="step-number">{i+1}</span>
  <div class="step-body"><h3>{h}</h3><p>{b}</p></div>
</div>\n"""

        # Pro tips
        tips = sec.get("pro_tips", [])
        tips_li = "".join(f"  <li>{tip}</li>\n" for tip in tips)

        # FAQs
        faqs = sec.get("faqs", [])
        faq_html = ""
        for fq in faqs:
            faq_html += f"""  <div class="faq-item">
    <button class="faq-question" onclick="toggleFaq(this)">{fq.get('question','')}</button>
    <div class="faq-answer">{fq.get('answer','')}</div>
  </div>\n"""

        # Recipe card
        recipe = sec.get("recipe") or self._gen_recipe()
        if not isinstance(recipe, dict):
            recipe = {}
        r_name = recipe.get("name", t)
        r_prep = recipe.get("prep_time", "15 min")
        r_cook = recipe.get("cook_time", "30 min")
        r_total = recipe.get("total_time", "45 min")
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
<div class="article-container">

<header class="article-header g3-header">
  <h1 class="article-title">{t}</h1>
  <div class="article-byline-row">
    <div class="byline-left">
      <span class="byline-author">By <span class="article-author"></span></span>
      <span class="byline-date">Published <span class="article-date"></span></span>
      <p class="byline-disclaimer">This post may contain affiliate links.</p>
    </div>
    <div class="byline-right">
      <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
      <div class="recipe-meta-inline"><span>{r_prep} prep</span><span>{r_cook} cook</span><span>{r_srv} servings</span></div>
    </div>
  </div>
</header>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<p class="intro">{sec.get('intro','')}</p>

<h2>Why You'll Love This</h2>
<ul class="why-love-list">
{why_html}</ul>

<h2>Ingredients</h2>
<p>{sec.get('ingredients_intro','')}</p>
<ul class="ingredient-list">
{ing_li}</ul>

<h2>How to Make {t}</h2>
{steps_html}

<div class="pro-tips-box">
  <h2>Pro Tips</h2>
  <ul class="pro-tips-list">
{tips_li}  </ul>
</div>

<h2>Serving Suggestions</h2>
<p>{sec.get('serving_suggestions','')}</p>

<div class="faq-section">
  <h2>Frequently Asked Questions</h2>
{faq_html}</div>

<h2>Final Thoughts</h2>
<p>{sec.get('conclusion','')}</p>

<!-- inject:before-recipe -->
<div class="recipe-card" id="recipe-card">
  <h2>{r_name}</h2>
  <img src="{card_img}" alt="{r_name}" class="recipe-card-image">
  <div class="recipe-card-buttons">
    <button class="btn-print" onclick="window.print()">Print Recipe</button>
    <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Save to Pinterest</button>
  </div>
  <div class="recipe-meta">
    <div class="recipe-meta-item"><span class="recipe-meta-label">Prep</span><span class="recipe-meta-value">{r_prep}</span></div>
    <div class="recipe-meta-item"><span class="recipe-meta-label">Cook</span><span class="recipe-meta-value">{r_cook}</span></div>
    <div class="recipe-meta-item"><span class="recipe-meta-label">Total</span><span class="recipe-meta-value">{r_total}</span></div>
    <div class="recipe-meta-item"><span class="recipe-meta-label">Servings</span><span class="recipe-meta-value">{r_srv}</span></div>
    <div class="recipe-meta-item"><span class="recipe-meta-label">Calories</span><span class="recipe-meta-value">{r_cal}</span></div>
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
    gen = ArticleGenerator({"title": "Midnight Chocolate Truffle Cake"})
    gen.run()
