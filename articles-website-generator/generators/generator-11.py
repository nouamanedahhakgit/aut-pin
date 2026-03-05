"""
generator-11.py
---------------
Bold Magazine-Style Recipe Blog — Stitch-designed template.

Design: Pure white (#ffffff) background, vibrant teal (#00897b) primary,
hot pink (#e91e73) secondary, near black (#1a1a1a) text. Poppins bold
uppercase headings, DM Sans body. Timeline-style instructions with
connecting lines, horizontal card strip for highlights, large quotation
marks on pro tips, punchy editorial feel.

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
        "primary":            "#00897b",
        "secondary":          "#e91e73",
        "accent":             "#e91e73",
        "background":         "#ffffff",
        "container_bg":       "#ffffff",
        "border":             "#e8e8e8",
        "text_primary":       "#1a1a1a",
        "text_secondary":     "#4a4a4a",
        "button_print":       "#00897b",
        "button_pin":         "#e91e73",
        "button_hover_print": "#00796b",
        "button_hover_pin":   "#c2185b",
        "link":               "#00897b",
        "list_marker":        "#00897b",
    },
    "fonts": {
        "heading": {
            "family":  "Poppins",
            "weights": [600, 700, 800],
            "sizes":   {"h1": "2.4rem", "h2": "1.5rem", "h3": "1.1rem"},
        },
        "body": {
            "family":      "DM Sans",
            "weight":      400,
            "size":        "1rem",
            "line_height": 1.75,
        },
    },
    "layout": {
        "max_width":         "820px",
        "section_spacing":   "2.5rem",
        "paragraph_spacing": "1.1rem",
        "list_spacing":      "0.5rem",
        "container_padding": "2rem",
        "border_radius":     "12px",
        "box_shadow":        "none",
    },
    "components": {
        "numbered_list": {
            "style":       "circle",
            "circle_bg":   "#00897b",
            "circle_color":"#ffffff",
            "circle_size": "36px",
        },
        "bullet_list": {
            "style": "disc",
            "color": "#00897b",
        },
        "pro_tips_box": {
            "bg_color":     "#f8f8f8",
            "border_color": "#e91e73",
            "border_left":  "none",
            "padding":      "2rem 2rem 2rem 4rem",
        },
        "recipe_card": {
            "bg":             "#ffffff",
            "border":         "2px solid #e8e8e8",
            "border_radius":  "16px",
            "padding":        "0",
            "meta_icon_color":"#00897b",
            "header_stripe":  "#00897b",
        },
    },
    "images": {
        "main_article_image": "",
        "ingredient_image":   "",
        "recipe_card_image":  "",
    },
    "structure_template": {
        "word_counts": {
            "intro":                 110,
            "why_love_item_1":        35,
            "why_love_item_2":        35,
            "why_love_item_3":        35,
            "why_love_item_4":        35,
            "ingredients_intro":      40,
            "instructions_step_1":    70,
            "instructions_step_2":    70,
            "instructions_step_3":    70,
            "instructions_step_4":    70,
            "pro_tip_quote":          60,
            "conclusion":             75,
            "faq_1_answer":           55,
            "faq_2_answer":           55,
            "faq_3_answer":           55,
        }
    },
    "dark_mode": False,
}

STRUCTURE = [
    {"key": "intro",               "type": "intro",       "label": "Introduction"},
    {"key": "why_love",            "type": "h2",          "label": "WHY YOU'LL LOVE IT"},
    {"key": "why_love_item_1",     "type": "bullet_list", "label": ""},
    {"key": "why_love_item_2",     "type": "bullet_list", "label": ""},
    {"key": "why_love_item_3",     "type": "bullet_list", "label": ""},
    {"key": "why_love_item_4",     "type": "bullet_list", "label": ""},
    {"key": "ingredients_intro",   "type": "h2",          "label": "INGREDIENTS"},
    {"key": "instructions_intro",  "type": "h2",          "label": "INSTRUCTIONS"},
    {"key": "instructions_step_1", "type": "h3",          "label": "Step 1"},
    {"key": "instructions_step_2", "type": "h3",          "label": "Step 2"},
    {"key": "instructions_step_3", "type": "h3",          "label": "Step 3"},
    {"key": "instructions_step_4", "type": "h3",          "label": "Step 4"},
    {"key": "pro_tip_quote",       "type": "pro_tips_box","label": "Pro Tip"},
    {"key": "conclusion",          "type": "conclusion",  "label": ""},
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
            "You are an energetic, modern food writer with a punchy editorial voice. "
            "Write engaging, SEO-friendly content with bold personality. "
            "Output plain text only: no markdown. "
            f"All content must be only about: {self.title}."
        )
        raw = ai_chat(self, prompt, max_tokens=max_tokens, system=system)
        return self._strip_markdown(raw) if raw else ""

    def _gen_intro(self):
        return self._chat(
            f"Write a punchy 110-word intro for {self.title}. "
            "Be bold and energetic. Plain text, no headers.", 260
        )

    def _gen_why_items(self):
        raw = self._chat(
            f"Give exactly 4 reasons to love {self.title}. "
            "Format each as: SHORT TITLE: one bold sentence. One per line. No bullets.", 240
        )
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        while len(lines) < 4:
            lines.append(f"Easy Prep: {self.title} comes together faster than you think.")
        return lines[:4]

    def _gen_ingredients_intro(self):
        return self._chat(
            f"Write a 40-word intro for ingredients of {self.title}. Punchy tone.", 100
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
            "Format: HEADING: <short action heading>\nBODY: <70 word paragraph>", 220
        )
        heading, body = f"Step {num}", raw
        for line in (raw or "").splitlines():
            s = line.strip()
            if s.upper().startswith("HEADING:"):
                heading = s.split(":", 1)[-1].strip() or heading
            elif s.upper().startswith("BODY:"):
                body = s.split(":", 1)[-1].strip() or body
        return {"heading": heading, "body": body}

    def _gen_pro_tip_quote(self):
        return self._chat(
            f"Write one powerful 60-word pro tip for {self.title}. "
            "Write it like an expert quote. Plain text.", 140
        )

    def _gen_conclusion(self):
        return self._chat(
            f"Write a bold 75-word conclusion for {self.title}. "
            "Confident, encouraging tone. Plain text.", 180
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
                q = f"Can I make {self.title} ahead of time?"
            if not a:
                a = self._chat(f"Answer in 2-3 sentences: {q}", 100)
            faqs.append({"question": q, "answer": a or ""})
        return faqs

    def _gen_recipe(self):
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": self.title, "summary": f"A bold, no-fuss {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min",
                "servings": "4", "calories": "400", "course": "Main Course", "cuisine": "Fusion",
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
                "name": self.title, "summary": f"A bold {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min",
                "servings": "4", "calories": "400", "course": "Main Course", "cuisine": "Fusion",
            }

    def _gen_seo(self):
        defaults = {
            "recipe_title_pin":      self.title[:100],
            "pinterest_title":       self.title[:100],
            "pinterest_description": f"This bold {self.title} recipe is a total game-changer.",
            "pinterest_keywords":    f"{self.title}, recipe, bold, fast, easy, delicious",
            "focus_keyphrase":       self.title.lower(),
            "meta_description":      f"Make this show-stopping {self.title} — bold flavor, easy steps."[:140],
            "keyphrase_synonyms":    f"{self.title} recipe, easy {self.title}, best {self.title}",
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
            f"Write a Midjourney prompt for editorial food photography of {self.title}. "
            "Include: high contrast, bright colors, clean plating. End with --v 6.1", 120
        )
        ingr = self._chat(
            f"Write a Midjourney prompt for colorful ingredient flat-lay for {self.title}. "
            "White background, bold colors, editorial. End with --v 6.1", 120
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
            "intro": "string ~110 words",
            "why_items": "array of 4 strings (SHORT TITLE: sentence)",
            "ingredients_intro": "string ~40 words",
            "ingredient_list": "array of 10 strings",
            "steps": "array of 4 objects with heading and body",
            "pro_tip_quote": "string ~60 words",
            "conclusion": "string ~75 words",
            "faqs": "array of 3 objects with question and answer",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine" if not recipe_from_config else "(omit)",
            "meta_description": "120-140 chars",
            "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        system = "You are an energetic, modern food writer with a punchy editorial voice. Generate the full article as ONE JSON. Plain text only: no markdown. All content only about the recipe title."
        user = f"Generate the complete recipe article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=4500, system=system)
        data = self._extract_json(raw)
        
        if data:
            print("[*] Generated content via single JSON.")
            intro = self._strip_markdown(str(data.get("intro", "")))
            why_items = [self._strip_markdown(str(x)) for x in (data.get("why_items") or [])[:4]]
            ing_intro = self._strip_markdown(str(data.get("ingredients_intro", "")))
            ing_list = [str(x).strip() for x in (data.get("ingredient_list") or [])[:12]]
            steps_raw = data.get("steps") or []
            steps = [{"heading": str(s.get("heading", f"Step {i}")).strip() if isinstance(s, dict) else f"Step {i}", "body": self._strip_markdown(str(s.get("body", "")) if isinstance(s, dict) else "")} for i, s in enumerate(steps_raw[:4], 1)]
            tip_quote = self._strip_markdown(str(data.get("pro_tip_quote", "")))
            conclusion = self._strip_markdown(str(data.get("conclusion", "")))
            faqs_raw = data.get("faqs") or []
            faqs = [{"question": str(f.get("question", "")).strip(), "answer": self._strip_markdown(str(f.get("answer", "")))} for f in faqs_raw[:3] if isinstance(f, dict)]
            
            if recipe_from_config:
                defaults = {"name": self.title, "summary": "", "ingredients": [], "instructions": [], "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min", "servings": "4", "calories": "400", "course": "Main Course", "cuisine": "Fusion"}
                recipe = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
            else:
                recipe = data.get("recipe") or {}
                if not isinstance(recipe, dict) or not (recipe.get("ingredients") or recipe.get("instructions")):
                    recipe = {"name": self.title, "summary": f"A bold {self.title} recipe.", "ingredients": ing_list[:20] if ing_list else [], "instructions": [s.get("body", "") for s in steps][:15] if steps else [], "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min", "servings": "4", "calories": "400", "course": "Main Course", "cuisine": "Fusion"}
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            
            seo = {"recipe_title_pin": (str(data.get("pinterest_title", self.title)) or self.title)[:100], "pinterest_title": (str(data.get("pinterest_title", "")) or self.title)[:100], "pinterest_description": f"This bold {self.title} recipe is a total game-changer.", "pinterest_keywords": f"{self.title}, recipe, bold, fast, easy, delicious", "focus_keyphrase": self.title.lower(), "meta_description": (str(data.get("meta_description", "")) or f"Make this show-stopping {self.title} — bold flavor, easy steps.")[:140], "keyphrase_synonyms": f"{self.title} recipe, easy {self.title}, best {self.title}"}
            mj_main = str(data.get("prompt_midjourney_main", "") or "").strip()
            mj_ing = str(data.get("prompt_midjourney_ingredients", "") or "").strip()
            mj = {"main": mj_main if mj_main and "--v 6.1" in mj_main else f"Editorial food photography of {self.title} --v 6.1", "ingredients": mj_ing if mj_ing and "--v 6.1" in mj_ing else f"Colorful ingredient flat-lay for {self.title} --v 6.1"}
        else:
            print("[*] Generating intro...")
            intro = self._gen_intro()
            print("[*] Generating why-love items...")
            why_items = self._gen_why_items()
            print("[*] Generating ingredients...")
            ing_intro = self._gen_ingredients_intro()
            ing_list = self._gen_ingredient_list()
            print("[*] Generating steps 1-4...")
            steps = [self._gen_step(i) for i in range(1, 5)]
            print("[*] Generating pro tip quote...")
            tip_quote = self._gen_pro_tip_quote()
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
            {"key": "pro_tip_quote",      "content": tip_quote},
            {"key": "conclusion",         "content": conclusion},
            {"key": "faqs",               "content": faqs},
        ]

        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": f"generator-11 / title: {self.title}",
            "prompt_base": f"Bold magazine-style food blog for: {self.title}",
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

        return f"""/* generator-11 | Bold Magazine Style */
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
.article-header.g11-header {{ margin-bottom: {l['section_spacing']}; }}
.article-header.g11-header .article-title {{
    font-family: {heading_font};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 800;
    color: {c['text_primary']};
    margin: 0 0 0.75rem 0;
    line-height: 1.15;
    letter-spacing: -0.02em;
}}
.article-header.g11-header .article-byline-row {{
    display: flex; flex-wrap: wrap; justify-content: space-between;
    align-items: center; gap: 0.5rem;
}}
.article-header.g11-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g11-header .byline-author {{ font-weight: 600; color: {c['text_primary']}; font-size: 0.9rem; }}
.article-header.g11-header .byline-date {{ font-size: 0.8rem; color: {c['text_secondary']}; }}
.article-header.g11-header .byline-disclaimer {{ font-size: 0.75rem; color: {c['text_secondary']}; font-style: italic; }}
.article-header.g11-header .byline-right {{ display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }}
.tag-pill {{
    display: inline-block; padding: 0.3rem 0.75rem; border-radius: 999px;
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
}}
.tag-pill.teal {{ background: {c['primary']}; color: #fff; }}
.tag-pill.pink {{ background: {c['secondary']}; color: #fff; }}

/* --- Typography --- */
h1 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h1']}; font-weight: 800; color: {c['text_primary']}; line-height: 1.15; margin-bottom: 1rem; letter-spacing: -0.02em; }}
h2 {{
    font-family: {heading_font}; font-size: {f['heading']['sizes']['h2']}; font-weight: 700;
    color: {c['text_primary']}; text-transform: uppercase; letter-spacing: 0.04em;
    margin-top: {l['section_spacing']}; margin-bottom: 0.75rem;
}}
h3 {{ font-family: {heading_font}; font-size: {f['heading']['sizes']['h3']}; font-weight: 700; color: {c['text_primary']}; margin-top: 0; margin-bottom: 0.3rem; }}
p {{ color: {c['text_secondary']}; margin-bottom: {l['paragraph_spacing']}; }}
a {{ color: {c['link']}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* --- Hero image (teal bottom stripe) --- */
.hero-image-wrap {{
    position: relative; margin: 1.25rem 0;
}}
.hero-image {{
    width: 100%; height: auto; display: block;
    border-radius: {l['border_radius']};
    object-fit: cover; max-height: 460px;
}}
.hero-image-wrap::after {{
    content: ''; position: absolute; bottom: 0; left: 0; right: 0;
    height: 5px; background: {c['primary']};
    border-radius: 0 0 {l['border_radius']} {l['border_radius']};
}}

/* --- Why love cards (horizontal strip) --- */
.why-love-strip {{
    display: flex; gap: 0.75rem; overflow-x: auto;
    padding: 0.5rem 0 1rem; margin: 0.5rem 0 1.25rem;
    -webkit-overflow-scrolling: touch;
}}
.why-love-strip::-webkit-scrollbar {{ height: 3px; }}
.why-love-strip::-webkit-scrollbar-thumb {{ background: {c['primary']}; border-radius: 2px; }}
.why-love-card {{
    flex: 0 0 220px; padding: 1.25rem; border-radius: {l['border_radius']};
    border: 2px solid {c['border']}; transition: border-color 0.2s, box-shadow 0.2s;
}}
.why-love-card:hover {{
    border-color: {c['primary']}; box-shadow: 0 4px 16px rgba(0,137,123,0.12);
}}
.why-love-card strong {{ display: block; color: {c['primary']}; font-weight: 700; margin-bottom: 0.3rem; font-size: 0.9rem; }}
.why-love-card span {{ font-size: 0.85rem; color: {c['text_secondary']}; }}

/* --- Ingredient grid (2 columns) --- */
.ingredient-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 2rem;
    margin: 0.5rem 0 1.25rem; padding: 0;
    list-style: none;
}}
.ingredient-grid li {{
    position: relative; padding-left: 1.2rem; color: {c['text_secondary']};
    padding-bottom: 0.5rem; border-bottom: 1px solid {c['border']};
}}
.ingredient-grid li::before {{
    content: ''; position: absolute; left: 0; top: 0.55em;
    width: 8px; height: 8px; border-radius: 50%; background: {c['list_marker']};
}}

/* --- Timeline instructions --- */
.timeline {{ position: relative; padding-left: 2.75rem; margin: 1rem 0 1.5rem; }}
.timeline::before {{
    content: ''; position: absolute; left: 17px; top: 0; bottom: 0;
    width: 3px; background: {c['border']};
}}
.timeline-item {{
    position: relative; margin-bottom: 2rem;
}}
.timeline-number {{
    position: absolute; left: -2.75rem; top: 0;
    width: {nl['circle_size']}; height: {nl['circle_size']};
    border-radius: 50%; background: {nl['circle_bg']}; color: {nl['circle_color']};
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 1rem;
    z-index: 1;
}}
.timeline-item h3 {{ font-size: 1.05rem; margin-bottom: 0.3rem; }}
.timeline-item p {{ margin: 0; font-size: 0.95rem; }}

/* --- Pro tip quote (large quotation marks) --- */
.pro-tip-quote {{
    position: relative;
    background: {pt['bg_color']}; padding: {pt['padding']};
    border-radius: {l['border_radius']}; margin: {l['section_spacing']} 0;
}}
.pro-tip-quote::before {{
    content: '\\201C'; position: absolute; top: 0.5rem; left: 1rem;
    font-size: 4rem; line-height: 1; color: {c['secondary']}; font-family: Georgia, serif;
}}
.pro-tip-quote h2 {{ margin-top: 0; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.08em; color: {c['secondary']}; }}
.pro-tip-quote p {{ margin: 0; font-style: italic; font-size: 1.05rem; color: {c['text_primary']}; }}

/* --- FAQ --- */
.faq-section {{ margin: {l['section_spacing']} 0; }}
.faq-item {{ margin-bottom: 0.5rem; }}
.faq-question {{
    width: 100%; background: none; border: none; border-bottom: 2px solid {c['border']};
    text-align: left; padding: 1rem 0;
    font-family: {heading_font}; font-size: 1rem; font-weight: 700;
    color: {c['primary']}; cursor: pointer;
    display: flex; justify-content: space-between; align-items: center;
}}
.faq-question::after {{ content: '+'; font-size: 1.3rem; color: {c['secondary']}; font-weight: 400; }}
.faq-question.open::after {{ content: '\\2212'; }}
.faq-answer {{ display: none; padding: 0.75rem 0; color: {c['text_secondary']}; }}
.faq-answer.open {{ display: block; }}

/* --- Recipe card (teal header stripe) --- */
.recipe-card {{
    background: {rc['bg']}; border: {rc['border']};
    border-radius: {rc['border_radius']}; overflow: hidden;
    margin: {l['section_spacing']} 0;
}}
.recipe-card-stripe {{
    height: 6px; background: {rc.get('header_stripe', c['primary'])};
}}
.recipe-card-body {{ padding: 1.75rem; }}
.recipe-card-body h2 {{ margin-top: 0; text-align: center; color: {c['text_primary']}; text-transform: uppercase; letter-spacing: 0.04em; }}
.recipe-card-image {{
    width: 100%; height: 260px; object-fit: cover; display: block;
    border-radius: {l['border_radius']}; margin: 1rem 0;
}}
.recipe-card-buttons {{ display: flex; gap: 0.75rem; margin: 1rem 0; }}
.btn-print {{
    flex: 1; background: {c['button_print']}; color: #fff; border: none;
    padding: 0.75rem 1rem; border-radius: 999px;
    cursor: pointer; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;
    letter-spacing: 0.04em; transition: background 0.2s;
}}
.btn-print:hover {{ background: {c['button_hover_print']}; }}
.btn-pin {{
    flex: 1; background: {c['button_pin']}; color: #fff; border: none;
    padding: 0.75rem 1rem; border-radius: 999px;
    cursor: pointer; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;
    letter-spacing: 0.04em; transition: background 0.2s;
}}
.btn-pin:hover {{ background: {c['button_hover_pin']}; }}
.recipe-meta-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0; margin: 1rem 0; border: 1px solid {c['border']}; border-radius: {l['border_radius']};
}}
.recipe-meta-cell {{
    text-align: center; padding: 0.75rem 0.5rem;
    border-right: 1px solid {c['border']};
}}
.recipe-meta-cell:last-child {{ border-right: none; }}
.meta-label {{ font-size: 0.65rem; text-transform: uppercase; color: {c['text_secondary']}; letter-spacing: 0.08em; }}
.meta-val {{ font-size: 0.95rem; font-weight: 700; color: {rc['meta_icon_color']}; display: block; margin-top: 2px; }}
.recipe-ingredients-list {{ list-style: none; padding: 0; }}
.recipe-ingredients-list li {{
    padding: 0.4rem 0 0.4rem 1.4rem; position: relative;
    color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.recipe-ingredients-list li:last-child {{ border-bottom: none; }}
.recipe-ingredients-list li::before {{
    content: ''; position: absolute; left: 0; top: 0.65em;
    width: 8px; height: 8px; border-radius: 50%; background: {c['list_marker']};
}}
.recipe-instructions-list {{ list-style: none; padding: 0; counter-reset: ristep; }}
.recipe-instructions-list li {{
    counter-increment: ristep; padding: 0.6rem 0 0.6rem 2.8rem;
    position: relative; color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.recipe-instructions-list li:last-child {{ border-bottom: none; }}
.recipe-instructions-list li::before {{
    content: counter(ristep); position: absolute; left: 0; top: 0.45rem;
    width: 28px; height: 28px; background: {nl['circle_bg']}; color: {nl['circle_color']};
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem;
}}

@media print {{ .recipe-card-buttons {{ display: none; }} }}
@media (max-width: 600px) {{
    .ingredient-grid {{ grid-template-columns: 1fr; }}
    .why-love-card {{ flex: 0 0 180px; }}
    .recipe-card-buttons {{ flex-direction: column; }}
    h1 {{ font-size: 1.7rem; }}
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

        why_items = sec.get("why_love_items", [])
        why_cards = ""
        for item in why_items:
            parts = item.split(":", 1)
            title = parts[0].strip() if len(parts) > 1 else item[:20]
            desc = parts[1].strip() if len(parts) > 1 else item
            why_cards += f'  <div class="why-love-card"><strong>{title}</strong><span>{desc}</span></div>\n'

        ing_list = sec.get("ingredient_list", [])
        ing_li = "".join(f"  <li>{it}</li>\n" for it in ing_list)

        steps = sec.get("instructions_steps", [])
        steps_html = ""
        for i, step in enumerate(steps):
            h = step.get("heading", f"Step {i+1}")
            b = step.get("body", "")
            steps_html += f'<div class="timeline-item"><span class="timeline-number">{i+1}</span><h3>{h}</h3><p>{b}</p></div>\n'

        faqs = sec.get("faqs", [])
        faq_html = ""
        for fq in faqs:
            faq_html += f'  <div class="faq-item"><button class="faq-question" onclick="toggleFaq(this)">{fq.get("question","")}</button><div class="faq-answer">{fq.get("answer","")}</div></div>\n'

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

<header class="article-header g11-header">
  <h1 class="article-title">{t}</h1>
  <div class="article-byline-row">
    <div class="byline-left">
      <span class="byline-author">By <span class="article-author"></span></span>
      <span class="byline-date"><span class="article-date"></span></span>
      <p class="byline-disclaimer">This post may contain affiliate links.</p>
    </div>
    <div class="byline-right">
      <span class="tag-pill teal">{cat.get("categorie","recipe")}</span>
      <span class="tag-pill pink">Quick</span>
    </div>
  </div>
</header>

<div class="hero-image-wrap">
  <img src="{main_img}" alt="{t}" class="hero-image">
</div>
<!-- inject:after-hero -->

<p class="intro">{sec.get('intro','')}</p>

<h2>Why You'll Love It</h2>
<div class="why-love-strip">
{why_cards}</div>

<h2>Ingredients</h2>
<p>{sec.get('ingredients_intro','')}</p>
<ul class="ingredient-grid">
{ing_li}</ul>

<h2>Instructions</h2>
<div class="timeline">
{steps_html}</div>

<div class="pro-tip-quote">
  <h2>Pro Tip</h2>
  <p>{sec.get('pro_tip_quote','')}</p>
</div>

<div class="faq-section">
  <h2>Frequently Asked Questions</h2>
{faq_html}</div>

<p>{sec.get('conclusion','')}</p>

<!-- inject:before-recipe -->
<div class="recipe-card" id="recipe-card">
  <div class="recipe-card-stripe"></div>
  <div class="recipe-card-body">
    <h2>{r_name}</h2>
    <img src="{card_img}" alt="{r_name}" class="recipe-card-image">
    <div class="recipe-meta-grid">
      <div class="recipe-meta-cell"><span class="meta-label">Prep</span><span class="meta-val">{r_prep}</span></div>
      <div class="recipe-meta-cell"><span class="meta-label">Cook</span><span class="meta-val">{r_cook}</span></div>
      <div class="recipe-meta-cell"><span class="meta-label">Total</span><span class="meta-val">{r_total}</span></div>
      <div class="recipe-meta-cell"><span class="meta-label">Servings</span><span class="meta-val">{r_srv}</span></div>
    </div>
    <div class="recipe-card-buttons">
      <button class="btn-print" onclick="window.print()">Print Recipe</button>
      <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin It</button>
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
    gen = ArticleGenerator({"title": "Spicy Dragon Noodles With Basil"})
    gen.run()
