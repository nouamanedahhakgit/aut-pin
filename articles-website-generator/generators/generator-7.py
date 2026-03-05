"""
generator-7.py
--------------
Production-ready food blog article generator.

Design style: Editorial minimal — single-column, narrow reading width,
elegant serif headings, clean sans body, earthy warm-brown accents,
flat white background, no decorative boxes, in-content food photography.

All design values are hard-coded from AI image analysis (2.png).
CONFIG["title"] = "" — user supplies title via API payload or CLI.
"""

import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# CONFIG  (all values pre-filled from image analysis — NEVER runtime analysis)
# ---------------------------------------------------------------------------
CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary":            "#7B5E3A",
        "secondary":          "#2C2C2C",
        "accent":             "#A0784C",
        "background":         "#FFFFFF",
        "container_bg":       "#FFFFFF",
        "border":             "#E0E0E0",
        "text_primary":       "#1A1A1A",
        "text_secondary":     "#4A4A4A",
        "button_print":       "#2C2C2C",
        "button_pin":         "#E60023",
        "button_hover_print": "#444444",
        "button_hover_pin":   "#C0001E",
        "link":               "#7B5E3A",
        "list_marker":        "#7B5E3A",
    },
    "fonts": {
        "heading": {
            "family":  "'Playfair Display', Georgia, 'Times New Roman', serif",
            "weights": [700, 800],
            "sizes":   {"h1": "2.1rem", "h2": "1.4rem", "h3": "1.1rem"},
        },
        "body": {
            "family":      "'Lato', 'Open Sans', Arial, sans-serif",
            "weight":      400,
            "size":        "15px",
            "line_height": 1.82,
        },
    },
    "layout": {
        "max_width":         "700px",
        "section_spacing":   "2rem",
        "paragraph_spacing": "1rem",
        "list_spacing":      "0.5rem",
        "container_padding": "1.25rem",
        "border_radius":     "4px",
        "box_shadow":        "0 1px 4px rgba(0,0,0,0.07)",
    },
    "components": {
        "numbered_list": {
            "style":       "decimal",
            "circle_bg":   "transparent",
            "circle_color":"#7B5E3A",
            "circle_size": "auto",
        },
        "bullet_list": {
            "style": "disc",
            "color": "#7B5E3A",
        },
        "pro_tips_box": {
            "bg_color":     "#F9F6F2",
            "border_color": "#C8A97E",
            "border_left":  "3px solid #C8A97E",
            "padding":      "1rem 1.25rem",
        },
        "recipe_card": {
            "bg":             "#FFFFFF",
            "border":         "1px solid #E0E0E0",
            "border_radius":  "4px",
            "padding":        "1.5rem",
            "meta_icon_color":"#7B5E3A",
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
            "why_i_love_intro":       25,
            "why_i_love_item_1":      30,
            "why_i_love_item_2":      30,
            "why_i_love_item_3":      30,
            "why_i_love_item_4":      30,
            "note_section":           70,
            "ingredients_intro":      45,
            "instructions_intro":     35,
            "instructions_step_1":    60,
            "instructions_step_2":    60,
            "instructions_step_3":    60,
            "instructions_step_4":    60,
            "instructions_step_5":    60,
            "conclusion":             65,
            "faq_1_question":         12,
            "faq_1_answer":           55,
            "faq_2_question":         12,
            "faq_2_answer":           55,
            "faq_3_question":         12,
            "faq_3_answer":           55,
        }
    },
    "dark_mode": False,
}

# ---------------------------------------------------------------------------
# STRUCTURE TEMPLATE  (generic keys — NO recipe-specific text)
# ---------------------------------------------------------------------------
STRUCTURE = [
    {"key": "intro_p1",            "type": "intro",       "label": "Introduction paragraph 1"},
    {"key": "intro_p2",            "type": "paragraph",   "label": "Introduction paragraph 2"},
    {"key": "why_i_love_intro",    "type": "h2",          "label": "Why You'll Love This"},
    {"key": "why_i_love_item_1",   "type": "bullet_list", "label": ""},
    {"key": "why_i_love_item_2",   "type": "bullet_list", "label": ""},
    {"key": "why_i_love_item_3",   "type": "bullet_list", "label": ""},
    {"key": "why_i_love_item_4",   "type": "bullet_list", "label": ""},
    {"key": "note_section",        "type": "h2",          "label": "What to Look For"},
    {"key": "ingredients_intro",   "type": "h2",          "label": "Ingredients"},
    {"key": "instructions_intro",  "type": "h2",          "label": "How to Make {title}"},
    {"key": "instructions_step_1", "type": "h3",          "label": "Step 1"},
    {"key": "instructions_step_2", "type": "h3",          "label": "Step 2"},
    {"key": "instructions_step_3", "type": "h3",          "label": "Step 3"},
    {"key": "instructions_step_4", "type": "h3",          "label": "Step 4"},
    {"key": "instructions_step_5", "type": "h3",          "label": "Step 5"},
    {"key": "conclusion",          "type": "conclusion",  "label": "Final Thoughts"},
    {"key": "faq_1_question",      "type": "faq",         "label": "FAQ"},
    {"key": "faq_1_answer",        "type": "faq",         "label": ""},
    {"key": "faq_2_question",      "type": "faq",         "label": ""},
    {"key": "faq_2_answer",        "type": "faq",         "label": ""},
    {"key": "faq_3_question",      "type": "faq",         "label": ""},
    {"key": "faq_3_answer",        "type": "faq",         "label": ""},
]


# ---------------------------------------------------------------------------
# GENERATOR
# ---------------------------------------------------------------------------
class ArticleGenerator:

    def __init__(self, config_override: dict = None):
        self.config = {k: v for k, v in CONFIG.items()}
        if config_override:
            self._deep_merge(self.config, config_override)
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
        self.title  = self.config["title"].strip()
        self.slug   = self._slugify(self.title)

    # ------------------------------------------------------------------ utils

    def _deep_merge(self, base: dict, override: dict):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = re.sub(r"\s+", "-", text.strip())
        return text or "article"

    def _validate_config(self):
        required = [
            "title", "colors", "fonts", "layout",
            "components", "images", "structure_template", "categories_list",
        ]
        for key in required:
            if key not in self.config:
                raise KeyError(f"CONFIG missing required key: '{key}'")
        color_keys = [
            "primary", "secondary", "accent", "background", "container_bg",
            "border", "text_primary", "text_secondary",
            "button_print", "button_pin", "button_hover_print", "button_hover_pin",
            "link", "list_marker",
        ]
        for ck in color_keys:
            if ck not in self.config["colors"]:
                raise KeyError(f"CONFIG['colors'] missing key: '{ck}'")

    def _chat(self, prompt: str, max_tokens: int = 500) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert food blogger and SEO copywriter. "
                            "Write natural, engaging, human-like content. "
                            "Output plain text only — no markdown, no asterisks, "
                            "no bold markers, no hashtags — unless HTML is explicitly requested."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.72,
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            print(f"[ERROR] OpenAI call failed: {exc}")
            return f"Content about {self.title}."

    # --------------------------------------------------------- content helpers

    def _gen_intro_p1(self) -> str:
        return self._chat(
            f"Write a compelling 120-word opening paragraph for a food blog article about {self.title}. "
            "Draw the reader in with sensory details. Plain text, no headers.",
            280,
        )

    def _gen_intro_p2(self) -> str:
        return self._chat(
            f"Write an 80-word second introductory paragraph for a food blog article about {self.title}. "
            "Briefly mention why this recipe is special and easy. Plain text only.",
            200,
        )

    def _gen_why_items(self) -> list:
        raw = self._chat(
            f"Give exactly 4 reasons why readers will love making {self.title}. "
            "Format each reason as: <Short Bold Phrase>: <one sentence explanation>. "
            "One reason per line. No bullets, no numbers, no markdown symbols.",
            220,
        )
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        while len(lines) < 4:
            lines.append(f"Easy Weeknight Meal: {self.title} comes together in under an hour with minimal effort.")
        return lines[:4]

    def _gen_note_section(self) -> str:
        return self._chat(
            f"Write a 70-word paragraph titled 'What to Look For' giving tips on how to select "
            f"the best key ingredients for {self.title}. Plain text only.",
            180,
        )

    def _gen_ingredients_intro(self) -> str:
        return self._chat(
            f"Write a short 45-word intro paragraph for the ingredients section of a recipe about {self.title}. "
            "Mention the ingredients are simple and easy to find. Plain text only.",
            120,
        )

    def _gen_ingredient_list(self) -> list:
        raw = self._chat(
            f"List exactly 10 ingredients needed to make {self.title}. "
            "Format: quantity + ingredient name, one per line. No bullets, no numbers.",
            180,
        )
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        return lines[:10] if lines else [f"Ingredient {i + 1}" for i in range(10)]

    def _gen_instructions_intro(self) -> str:
        return self._chat(
            f"Write a brief 35-word intro sentence for the 'How to Make {self.title}' section. "
            "Tell readers the steps are simple and easy to follow. Plain text only.",
            90,
        )

    def _gen_step(self, step_num: int) -> dict:
        raw = self._chat(
            f"Write step {step_num} for making {self.title}. "
            "Respond in this exact format:\n"
            "HEADING: <5-word action heading>\n"
            "BODY: <60-word instruction paragraph>\n"
            "Output must not be empty. BODY must contain actual instructions.",
            220,
        )
        heading = f"Step {step_num}"
        body    = raw or ""
        for line in (raw or "").splitlines():
            stripped = line.strip()
            if stripped.upper().startswith("HEADING:"):
                heading = stripped.split(":", 1)[-1].strip() or heading
            elif stripped.upper().startswith("BODY:"):
                body = stripped.split(":", 1)[-1].strip() or body
        if body == raw:
            # fallback parse: first line heading, rest body
            parts = (raw or "").strip().split("\n", 1)
            heading = parts[0].strip() if parts else f"Step {step_num}"
            body    = parts[1].strip() if len(parts) > 1 else (raw or "")
        if not body or not body.strip():
            body = self._chat(
                f"Write a brief 2-3 sentence instruction for step {step_num} of making {self.title}. Plain text.",
                120,
            )
        return {"heading": heading or f"Step {step_num}", "body": (body or "").strip()}

    def _gen_conclusion(self) -> str:
        return self._chat(
            f"Write a warm 65-word conclusion paragraph for a food blog article about {self.title}. "
            "Encourage readers to try the recipe and share their results. Plain text only.",
            180,
        )

    def _gen_faqs(self) -> list:
        raw = self._chat(
            f"Write exactly 3 real FAQ questions and answers about {self.title}. "
            "Use real questions (e.g. 'Can I freeze leftovers?', 'Can I use dried basil?'). "
            "Format strictly as:\n"
            "Q1: <question>\nA1: <55-word answer>\n"
            "Q2: <question>\nA2: <55-word answer>\n"
            "Q3: <question>\nA3: <55-word answer>",
            420,
        )
        faqs = []
        for i in range(1, 4):
            q, a = None, None
            for line in raw.splitlines():
                ls = line.strip()
                if ls.upper().startswith(f"Q{i}:"):
                    q = ls[len(f"Q{i}"):].lstrip(":").strip()
                elif ls.upper().startswith(f"A{i}:"):
                    a = ls[len(f"A{i}"):].lstrip(":").strip()
            if not q or "common question about" in (q or "").lower():
                q = f"How should I store leftover {self.title}?"
            if not a or "helpful answer about" in (a or "").lower():
                a = self._chat(f"Answer in 2-3 sentences: {q}", 100)
            faqs.append({"question": q or "", "answer": (a or "").strip()})
        return faqs

    def _gen_recipe(self) -> dict:
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and existing.get("ingredients") and existing.get("instructions"):
            defaults = {
                "name": self.title, "summary": f"A delicious {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 mins", "cook_time": "30 mins",
                "total_time": "45 mins", "servings": "4",
                "calories": "420", "course": "Main Course", "cuisine": "American",
            }
            return {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        raw = self._chat(
            f"Create a complete recipe for {self.title} as valid JSON with these exact keys: "
            "name, summary, ingredients (array of strings), instructions (array of strings), "
            "prep_time, cook_time, total_time, servings, calories, course, cuisine. "
            "Output only the raw JSON object — no markdown fences, no extra text.",
            650,
        )
        try:
            clean = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
            out = json.loads(clean)
            if not isinstance(out.get("ingredients"), list):
                out["ingredients"] = []
            if not isinstance(out.get("instructions"), list):
                out["instructions"] = []
            return out
        except Exception:
            return {
                "name": self.title, "summary": f"A delicious {self.title} recipe.",
                "ingredients": [], "instructions": [],
                "prep_time": "15 mins", "cook_time": "30 mins",
                "total_time": "45 mins", "servings": "4",
                "calories": "420", "course": "Main Course", "cuisine": "American",
            }

    def _gen_seo(self) -> dict:
        defaults = {
            "recipe_title_pin":      self.title[:100],
            "pinterest_title":       self.title[:100],
            "pinterest_description": f"This {self.title} recipe is easy to make and full of flavor.",
            "pinterest_keywords":    f"{self.title}, recipe, easy, dinner, homemade, delicious",
            "focus_keyphrase":       self.title.lower(),
            "meta_description":      f"Learn how to make {self.title} with this simple step-by-step recipe. Ready in under an hour!"[:140],
            "keyphrase_synonyms":    f"{self.title} recipe, easy {self.title}, homemade {self.title}",
        }
        raw = self._chat(
            f"Generate SEO metadata for a food blog post about {self.title}. "
            "Output valid JSON only (no markdown) with these exact keys: "
            "recipe_title_pin (max 100 chars), pinterest_title (max 100 chars), "
            "pinterest_description (2-3 sentences), pinterest_keywords (6 comma-separated), "
            "focus_keyphrase (concise phrase), meta_description (120-140 chars), "
            "keyphrase_synonyms (comma-separated).",
            380,
        )
        try:
            clean = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
            data  = json.loads(clean)
            for k in defaults:
                val = data.get(k) or data.get(k.replace("_", " "))
                if val and str(val).strip():
                    defaults[k] = str(val).strip()[:200]
        except Exception:
            pass
        # Enforce length limits
        defaults["recipe_title_pin"]  = defaults["recipe_title_pin"][:100]
        defaults["pinterest_title"]   = defaults["pinterest_title"][:100]
        defaults["meta_description"]  = defaults["meta_description"][:140]
        return defaults

    def _gen_midjourney(self) -> dict:
        main = self._chat(
            f"Write a Midjourney prompt for a professional food photography image of {self.title}. "
            "Include: overhead or 45-degree angle, natural lighting, rustic/editorial style, "
            "shallow depth of field, muted warm tones. Output the full prompt text ending with --v 6.1, not just the suffix.",
            130,
        )
        ingr = self._chat(
            f"Write a Midjourney prompt for a flat-lay image of raw ingredients for {self.title}. "
            "Include: white marble surface, natural light, editorial style. Output the full prompt text ending with --v 6.1, not just the suffix.",
            130,
        )
        main = (main or "").strip()
        ingr = (ingr or "").strip()
        if not main or len(main) < 25 or main.strip() == "--v 6.1":
            main = f"Professional food photography of {self.title}, overhead or 45-degree angle, natural lighting, rustic editorial style, shallow depth of field, muted warm tones --v 6.1"
        elif "--v 6.1" not in main:
            main = main.rstrip(" .") + " --v 6.1"
        if not ingr or len(ingr) < 25 or ingr.strip() == "--v 6.1":
            ingr = f"Flat-lay of raw ingredients for {self.title}, white marble surface, natural light, editorial style, clean composition --v 6.1"
        elif "--v 6.1" not in ingr:
            ingr = ingr.rstrip(" .") + " --v 6.1"
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

    # -------------------------------------------------- content orchestration

    def generate_content(self) -> dict:
        from ai_client import ai_chat
        existing = self.config.get("recipe")
        recipe_from_config = existing and isinstance(existing, dict) and (existing.get("ingredients") or existing.get("instructions"))
        
        schema = {
            "intro_p1": "string ~120 words",
            "intro_p2": "string ~80 words",
            "why_items": "array of 4 strings (Short Phrase: sentence)",
            "note_section": "string ~70 words",
            "ingredients_intro": "string ~45 words",
            "ingredient_list": "array of 10 strings",
            "instructions_intro": "string ~35 words",
            "steps": "array of 5 objects with heading and body",
            "conclusion": "string ~65 words",
            "faqs": "array of 3 objects with question and answer",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine" if not recipe_from_config else "(omit)",
            "meta_description": "120-140 chars",
            "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        
        system = "You are an expert food blogger and SEO copywriter. Generate the full article as ONE JSON. Plain text only: no markdown. All content only about the recipe title."
        user = f"Generate the complete editorial minimal food blog article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=4500, system=system)
        data = self._extract_json(raw)
        
        if data:
            print("[*] Generated content via single JSON.")
            intro_p1 = self._strip_markdown(str(data.get("intro_p1", "")))
            intro_p2 = self._strip_markdown(str(data.get("intro_p2", "")))
            why_items = [self._strip_markdown(str(x)) for x in (data.get("why_items") or [])[:4]]
            note_section = self._strip_markdown(str(data.get("note_section", "")))
            ing_intro = self._strip_markdown(str(data.get("ingredients_intro", "")))
            ing_list = [str(x).strip() for x in (data.get("ingredient_list") or [])[:12]]
            instr_intro = self._strip_markdown(str(data.get("instructions_intro", "")))
            steps_raw = data.get("steps") or []
            steps = [{"heading": str(s.get("heading", f"Step {i}")).strip() if isinstance(s, dict) else f"Step {i}", "body": self._strip_markdown(str(s.get("body", "")) if isinstance(s, dict) else "")} for i, s in enumerate(steps_raw[:5], 1)]
            conclusion = self._strip_markdown(str(data.get("conclusion", "")))
            faqs_raw = data.get("faqs") or []
            faqs = [{"question": str(f.get("question", "")).strip(), "answer": self._strip_markdown(str(f.get("answer", "")))} for f in faqs_raw[:3] if isinstance(f, dict)]
            
            if recipe_from_config:
                defaults = {"name": self.title, "summary": f"A delicious {self.title} recipe.", "ingredients": [], "instructions": [], "prep_time": "15 mins", "cook_time": "30 mins", "total_time": "45 mins", "servings": "4", "calories": "420", "course": "Main Course", "cuisine": "American"}
                recipe = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
            else:
                recipe = data.get("recipe") or {}
                if not isinstance(recipe, dict) or not (recipe.get("ingredients") or recipe.get("instructions")):
                    recipe = {"name": self.title, "summary": f"A delicious {self.title} recipe.", "ingredients": ing_list[:20] if ing_list else [], "instructions": [s.get("body", "") for s in steps][:15] if steps else [], "prep_time": "15 mins", "cook_time": "30 mins", "total_time": "45 mins", "servings": "4", "calories": "420", "course": "Main Course", "cuisine": "American"}
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [s.get("body", "") for s in steps][:15]
            
            seo = {"recipe_title_pin": (str(data.get("pinterest_title", self.title)) or self.title)[:100], "pinterest_title": (str(data.get("pinterest_title", "")) or self.title)[:100], "pinterest_description": f"This {self.title} recipe is easy to make and full of flavor.", "pinterest_keywords": f"{self.title}, recipe, easy, dinner, homemade, delicious", "focus_keyphrase": self.title.lower(), "meta_description": (str(data.get("meta_description", "")) or f"Learn how to make {self.title} with this simple step-by-step recipe. Ready in under an hour!")[:140], "keyphrase_synonyms": f"{self.title} recipe, easy {self.title}, homemade {self.title}"}
            mj_main = str(data.get("prompt_midjourney_main", "") or "").strip()
            mj_ing = str(data.get("prompt_midjourney_ingredients", "") or "").strip()
            mj = {"main": mj_main if mj_main and "--v 6.1" in mj_main else f"Professional food photography of {self.title}, overhead or 45-degree angle, natural lighting, rustic editorial style, shallow depth of field, muted warm tones --v 6.1", "ingredients": mj_ing if mj_ing and "--v 6.1" in mj_ing else f"Flat-lay of raw ingredients for {self.title}, white marble surface, natural light, editorial style, clean composition --v 6.1"}
        else:
            print("[*] Generating intro paragraphs...")
            intro_p1 = self._gen_intro_p1()
            intro_p2 = self._gen_intro_p2()

            print("[*] Generating why-you-love items...")
            why_items = self._gen_why_items()

            print("[*] Generating note section...")
            note_section = self._gen_note_section()

            print("[*] Generating ingredients...")
            ing_intro = self._gen_ingredients_intro()
            ing_list  = self._gen_ingredient_list()

            print("[*] Generating instructions intro...")
            instr_intro = self._gen_instructions_intro()

            print("[*] Generating 5 steps...")
            steps = [self._gen_step(i) for i in range(1, 6)]

            print("[*] Generating conclusion...")
            conclusion = self._gen_conclusion()

            print("[*] Generating FAQs...")
            faqs = self._gen_faqs()

            print("[*] Generating recipe card data...")
            recipe = self._gen_recipe()
            if not recipe.get("ingredients") and ing_list:
                recipe["ingredients"] = list(ing_list)[:20]
            if not recipe.get("instructions") and steps:
                recipe["instructions"] = [
                    (s.get("body") or s.get("heading") or "").strip() or f"Step {i}"
                    for i, s in enumerate(steps, 1)
                ][:15]

            print("[*] Generating SEO fields...")
            seo = self._gen_seo()

            print("[*] Generating Midjourney prompts...")
            mj = self._gen_midjourney()

        from ai_client import get_first_category
        cat      = get_first_category(self.config)
        main_img = self.config["images"].get("main_article_image") or "placeholder.jpg"
        ingr_img = self.config["images"].get("ingredient_image")   or "placeholder.jpg"

        sections = [
            {"key": "intro_p1",            "content": intro_p1},
            {"key": "intro_p2",            "content": intro_p2},
            {"key": "why_i_love_items",    "content": why_items},
            {"key": "note_section",        "content": note_section},
            {"key": "ingredients_intro",   "content": ing_intro},
            {"key": "ingredient_list",     "content": ing_list},
            {"key": "instructions_intro",  "content": instr_intro},
            {"key": "instructions_steps",  "content": steps},
            {"key": "conclusion",          "content": conclusion},
            {"key": "faqs",                "content": faqs},
        ]

        content_data = {
            "title":                     self.title,
            "slug":                      self.slug,
            "categorieId":               str(cat.get("id", 1)),
            "categorie":                 cat.get("categorie", "dinner"),
            "sections":                  sections,
            "article_html":              "",
            "article_css":               "",
            "prompt_used":               f"generator-7 / title: {self.title}",
            "prompt_base":               f"Editorial minimal food blog article for: {self.title}",
            "recipe":                    recipe,
            "recipe_title_pin":          seo["recipe_title_pin"],
            "pinterest_title":           seo["pinterest_title"],
            "pinterest_description":     seo["pinterest_description"],
            "pinterest_keywords":        seo["pinterest_keywords"],
            "focus_keyphrase":           seo["focus_keyphrase"],
            "meta_description":          seo["meta_description"],
            "keyphrase_synonyms":        seo["keyphrase_synonyms"],
            "main_image":                main_img,
            "ingredient_image":          ingr_img,
            "prompt_midjourney_main":    mj["main"],
            "prompt_midjourney_ingredients": mj["ingredients"],
        }
        return content_data

    # ------------------------------------------------------- CSS generation

    def generate_css(self) -> str:
        c   = self.config["colors"]
        f   = self.config["fonts"]
        lay = self.config["layout"]
        cp  = self.config["components"]

        nl  = cp["numbered_list"]
        bl  = cp["bullet_list"]
        ptb = cp["pro_tips_box"]
        rc  = cp["recipe_card"]

        return f"""/* ================================================================
   generator-7  |  Editorial Minimal Food Blog
   All values extracted from image analysis — never generated at runtime
   ================================================================ */

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
    -webkit-font-smoothing: antialiased;
}}

/* ---------- Layout ---------- */
.article-wrap {{
    max-width: {lay['max_width']};
    margin: 0 auto;
    padding: 0 {lay['container_padding']} 3rem;
    background: {c['container_bg']};
}}

.article-header.g7-header {{
    margin-bottom: 1.5rem;
}}
.article-header.g7-header .article-title {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 700;
    color: {c['text_primary']};
    margin: 0 0 0.5rem 0;
    line-height: 1.22;
    letter-spacing: -0.01em;
}}
.article-header.g7-header .article-byline-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}}
.article-header.g7-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g7-header .byline-author {{ font-weight: 600; color: {c['text_primary']}; }}
.article-header.g7-header .byline-date {{ font-size: 0.875rem; color: {c['text_secondary']}; }}
.article-header.g7-header .byline-disclaimer {{ font-size: 0.8rem; color: {c['text_secondary']}; font-style: italic; margin-top: 0.2rem; }}
.article-header.g7-header .byline-right {{ display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }}
.article-header.g7-header .recipe-meta-bar {{ display: flex; gap: 1.25rem; font-size: 0.875rem; color: {c['text_secondary']}; }}

/* ---------- Breadcrumb ---------- */
.breadcrumb {{
    padding: 0.75rem 0;
    font-size: 0.78rem;
    color: {c['text_secondary']};
    border-bottom: 1px solid {c['border']};
    margin-bottom: 1.5rem;
}}

.breadcrumb a {{
    color: {c['link']};
    text-decoration: none;
}}

.breadcrumb a:hover {{
    text-decoration: underline;
}}

.breadcrumb__sep {{
    margin: 0 0.35rem;
    opacity: 0.5;
}}

/* ---------- Typography ---------- */
h1 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h1']};
    font-weight: 700;
    color: {c['text_primary']};
    line-height: 1.22;
    margin-bottom: 1rem;
    letter-spacing: -0.01em;
}}

h2 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h2']};
    font-weight: 700;
    color: {c['text_primary']};
    margin-top: {lay['section_spacing']};
    margin-bottom: 0.75rem;
    letter-spacing: -0.01em;
}}

h3 {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h3']};
    font-weight: 700;
    color: {c['text_primary']};
    margin-top: 1.5rem;
    margin-bottom: 0.45rem;
}}

p {{
    color: {c['text_secondary']};
    margin-bottom: {lay['paragraph_spacing']};
}}

a {{
    color: {c['link']};
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

/* ---------- Hero image ---------- */
.hero-image {{
    width: 100%;
    height: auto;
    display: block;
    margin: 1.25rem 0;
    border-radius: {lay['border_radius']};
    object-fit: cover;
    max-height: 520px;
}}

/* ---------- In-content images ---------- */
.content-image {{
    width: 100%;
    height: auto;
    display: block;
    margin: 1.5rem 0;
    border-radius: {lay['border_radius']};
    object-fit: cover;
    max-height: 420px;
}}

.content-image__caption {{
    text-align: center;
    font-size: 0.8rem;
    color: {c['text_secondary']};
    opacity: 0.75;
    margin-top: -1rem;
    margin-bottom: 1rem;
}}

/* ---------- Why-love bullet list ---------- */
.why-list {{
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 1.25rem;
}}

.why-list li {{
    position: relative;
    padding-left: 1.4rem;
    margin-bottom: {lay['list_spacing']};
    color: {c['text_secondary']};
    line-height: 1.7;
}}

.why-list li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0.52em;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: {bl['color']};
}}

.why-list li strong {{
    color: {c['text_primary']};
    font-weight: 700;
}}

/* ---------- Ingredient list ---------- */
.ingredient-list {{
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 1.25rem;
    columns: 2;
    column-gap: 1.5rem;
}}

.ingredient-list li {{
    position: relative;
    padding-left: 1.2rem;
    margin-bottom: {lay['list_spacing']};
    color: {c['text_secondary']};
    break-inside: avoid;
}}

.ingredient-list li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0.55em;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: {bl['color']};
}}

/* ---------- Numbered steps (decimal, no circles) ---------- */
.steps-list {{
    list-style: none;
    padding: 0;
    margin: 0.75rem 0 1.25rem;
    counter-reset: step-counter;
}}

.step-item {{
    counter-increment: step-counter;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    margin-bottom: 1.35rem;
}}

.step-number {{
    flex-shrink: 0;
    font-family: {f['heading']['family']};
    font-size: 1.5rem;
    font-weight: 700;
    color: {nl['circle_color']};
    line-height: 1;
    min-width: 1.6rem;
    padding-top: 0.05rem;
}}

.step-body h3 {{
    margin-top: 0;
    margin-bottom: 0.3rem;
    font-size: 1rem;
    font-weight: 700;
}}

.step-body p {{
    margin: 0;
    font-size: 0.94rem;
}}

/* ---------- Pro tips box ---------- */
.pro-tips-box {{
    background: {ptb['bg_color']};
    border-left: {ptb['border_left']};
    border-radius: 0 {lay['border_radius']} {lay['border_radius']} 0;
    padding: {ptb['padding']};
    margin: {lay['section_spacing']} 0;
}}

.pro-tips-box h2 {{
    margin-top: 0;
    margin-bottom: 0.6rem;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {c['primary']};
    border: none;
}}

.pro-tips-box p {{
    font-style: italic;
    color: {c['text_secondary']};
    margin: 0;
    font-size: 0.93rem;
}}

/* ---------- Recipe Card ---------- */
.recipe-card {{
    background: {rc['bg']};
    border: {rc['border']};
    border-radius: {rc['border_radius']};
    padding: {rc['padding']};
    margin: {lay['section_spacing']} 0;
    box-shadow: {lay['box_shadow']};
}}

.recipe-card__header {{
    margin-bottom: 1rem;
}}

.recipe-card__title {{
    font-family: {f['heading']['family']};
    font-size: 1.3rem;
    font-weight: 700;
    color: {c['text_primary']};
    margin-bottom: 0.35rem;
}}

.recipe-card__summary {{
    font-size: 0.88rem;
    color: {c['text_secondary']};
    line-height: 1.65;
}}

.recipe-card__image {{
    width: 100%;
    height: auto;
    display: block;
    border-radius: {lay['border_radius']};
    margin-bottom: 1.1rem;
    max-height: 340px;
    object-fit: cover;
}}

/* Meta row */
.recipe-card__meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 0;
    border-top: 1px solid {c['border']};
    border-bottom: 1px solid {c['border']};
    padding: 0.85rem 0;
    margin-bottom: 1.25rem;
}}

.recipe-card__meta-item {{
    flex: 1 1 calc(100% / 4);
    min-width: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.15rem;
    padding: 0 0.5rem;
    border-right: 1px solid {c['border']};
}}

.recipe-card__meta-item:last-child {{
    border-right: none;
}}

.recipe-card__meta-label {{
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: {c['text_secondary']};
    opacity: 0.75;
}}

.recipe-card__meta-value {{
    font-size: 0.9rem;
    font-weight: 700;
    color: {c['text_primary']};
}}

/* Buttons */
.recipe-card__buttons {{
    display: flex;
    gap: 0.6rem;
    margin-bottom: 1.25rem;
    flex-wrap: wrap;
}}

.btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.5rem 1.1rem;
    border: none;
    border-radius: {lay['border_radius']};
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.18s ease, color 0.18s ease;
    font-family: {f['body']['family']};
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

/* Recipe ingredient + instruction lists */
.recipe-card__section-label {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: {c['text_primary']};
    margin: 1rem 0 0.5rem;
    border-bottom: 1px solid {c['border']};
    padding-bottom: 0.3rem;
}}

.recipe-card__ingredients {{
    list-style: none;
    padding: 0;
    margin: 0 0 0.5rem;
    columns: 2;
    column-gap: 1.25rem;
}}

.recipe-card__ingredients li {{
    position: relative;
    padding-left: 1rem;
    margin-bottom: 0.35rem;
    font-size: 0.86rem;
    color: {c['text_secondary']};
    break-inside: avoid;
}}

.recipe-card__ingredients li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0.52em;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: {c['list_marker']};
}}

.recipe-card__instructions {{
    list-style: none;
    padding: 0;
    margin: 0 0 0.5rem;
    counter-reset: rc-step;
}}

.recipe-card__instructions li {{
    display: flex;
    gap: 0.65rem;
    align-items: flex-start;
    margin-bottom: 0.65rem;
    font-size: 0.86rem;
    color: {c['text_secondary']};
    counter-increment: rc-step;
}}

.recipe-card__instructions li::before {{
    content: counter(rc-step) ".";
    flex-shrink: 0;
    font-weight: 700;
    color: {c['primary']};
    font-size: 0.82rem;
    min-width: 1.4rem;
    padding-top: 0.05rem;
}}

.recipe-card__notes {{
    font-size: 0.83rem;
    font-style: italic;
    color: {c['text_secondary']};
    background: {ptb['bg_color']};
    border-left: {ptb['border_left']};
    padding: 0.65rem 0.9rem;
    margin-top: 0.5rem;
    border-radius: 0 {lay['border_radius']} {lay['border_radius']} 0;
}}

/* ---------- FAQ ---------- */
.faq-section {{
    margin-top: {lay['section_spacing']};
}}

.faq-item {{
    border-bottom: 1px solid {c['border']};
    padding: 1rem 0;
}}

.faq-item:first-child {{
    border-top: 1px solid {c['border']};
}}

.faq-question {{
    font-family: {f['heading']['family']};
    font-weight: 700;
    font-size: 0.97rem;
    color: {c['text_primary']};
    margin-bottom: 0.35rem;
}}

.faq-answer {{
    font-size: 0.91rem;
    color: {c['text_secondary']};
    line-height: 1.72;
}}

/* ---------- Social share ---------- */
.social-share {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
    flex-wrap: wrap;
    margin-top: {lay['section_spacing']};
    padding-top: 1.25rem;
    border-top: 2px solid {c['border']};
}}

.social-share__label {{
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {c['text_secondary']};
    margin-right: 0.25rem;
}}

.social-share__btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.42rem 0.95rem;
    border-radius: {lay['border_radius']};
    font-size: 0.78rem;
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    transition: opacity 0.18s ease;
    letter-spacing: 0.02em;
}}

.social-share__btn:hover {{
    opacity: 0.85;
    color: #fff;
    text-decoration: none;
}}

.ssb-facebook  {{ background: #1877F2; }}
.ssb-twitter   {{ background: #1DA1F2; }}
.ssb-pinterest {{ background: #E60023; }}

/* ---------- Responsive ---------- */
@media (max-width: 600px) {{
    h1 {{ font-size: 1.65rem; }}
    h2 {{ font-size: 1.2rem; }}
    .ingredient-list,
    .recipe-card__ingredients {{ columns: 1; }}
    .recipe-card__meta-item {{ flex: 1 1 50%; }}
    .recipe-card__meta-item:nth-child(2) {{ border-right: none; }}
    .recipe-card__meta-item:nth-child(3) {{ border-top: 1px solid {c['border']}; }}
}}
"""

    # ------------------------------------------------------- HTML generation

    @staticmethod
    def _esc(text: str) -> str:
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def _p(self, text: str) -> str:
        return f'<p>{self._esc(text)}</p>\n'

    def generate_html(self, content_data: dict, css_filename: str = "css.css") -> str:
        esc  = self._esc
        title    = content_data["title"]
        meta_d   = content_data.get("meta_description", "")
        sections = {s["key"]: s["content"] for s in content_data["sections"]}
        recipe   = content_data.get("recipe", {})

        main_img = content_data.get("main_image", "placeholder.jpg")
        ingr_img = content_data.get("ingredient_image", "placeholder.jpg")
        card_img = self.config["images"].get("recipe_card_image") or main_img

        cat      = content_data.get("categorie", "dinner").capitalize()
        slug     = content_data.get("slug", "article")
        share    = f"https://yoursite.com/{slug}/"

        why_items = sections.get("why_i_love_items", [])
        ing_list  = sections.get("ingredient_list", [])
        steps     = sections.get("instructions_steps", [])
        faqs      = sections.get("faqs", [])
        recipe_ings  = recipe.get("ingredients", [])
        recipe_steps = recipe.get("instructions", [])

        # ---------- sub-blocks ----------
        def why_li(item):
            s = (item or "").strip()
            if ":" in s:
                idx = s.index(":")
                label, rest = s[:idx].strip(), s[idx + 1:].strip()
                label = re.sub(r"</?b>", "", label, flags=re.I).strip()
                return f'            <li><strong>{esc(label)}</strong>: {esc(rest)}</li>'
            return f'            <li>{esc(s)}</li>'

        why_lis = "\n".join(why_li(item) for item in why_items)

        ing_lis = "\n".join(
            f'            <li>{esc(item)}</li>' for item in ing_list
        )

        steps_html = ""
        for i, step in enumerate(steps, 1):
            sh = esc(step.get("heading", f"Step {i}"))
            sb = esc(step.get("body", ""))
            steps_html += f"""
        <li class="step-item">
            <div class="step-number">{i}</div>
            <div class="step-body">
                <h3>{sh}</h3>
                <p>{sb}</p>
            </div>
        </li>"""

        rc_ings = "\n".join(
            f'                <li>{esc(str(it))}</li>' for it in recipe_ings
        )
        rc_steps = "\n".join(
            f'                <li>{esc(str(st))}</li>' for st in recipe_steps
        )
        rc_notes = esc(str(recipe.get("notes", ""))) if recipe.get("notes") else ""

        faq_html = ""
        for faq in faqs:
            faq_html += f"""
        <div class="faq-item">
            <div class="faq-question">{esc(faq.get('question', ''))}</div>
            <div class="faq-answer">{esc(faq.get('answer', ''))}</div>
        </div>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{esc(meta_d)}" />
    <title>{esc(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Lato:wght@400;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="{css_filename}" />
</head>
<body>
<div class="article-wrap">

    <!-- Breadcrumb -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="/">Home</a>
        <span class="breadcrumb__sep">/</span>
        <a href="/{esc(cat.lower())}/">{esc(cat)}</a>
        <span class="breadcrumb__sep">/</span>
        <span>{esc(title)}</span>
    </nav>

    <header class="article-header g7-header">
        <h1 class="article-title">{esc(title)}</h1>
        <div class="article-byline-row">
            <div class="byline-left">
                <span class="byline-author">By <span class="article-author"></span></span>
                <span class="byline-date">Published <span class="article-date"></span></span>
                <p class="byline-disclaimer">This post may contain affiliate links.</p>
            </div>
            <div class="byline-right">
                <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
                <div class="recipe-meta-bar"><span>{esc(recipe.get("prep_time", ""))} prep</span><span>{esc(recipe.get("cook_time", ""))} cook</span><span>{esc(str(recipe.get("servings", "")))} servings</span></div>
            </div>
        </div>
    </header>

    <!-- Hero image -->
    <img
        class="hero-image"
        src="{esc(main_img)}"
        alt="{esc(title)}"
        width="700"
        height="467"
        loading="eager"
    />

    <!-- Intro -->
    <section id="intro" aria-label="Introduction">
        {self._p(sections.get('intro_p1', ''))}
        {self._p(sections.get('intro_p2', ''))}
    </section>

    <!-- Why You'll Love This -->
    <section id="why-youll-love-this">
        <h2>Why You'll Love This</h2>
        <ul class="why-list">
{why_lis}
        </ul>
    </section>

    <!-- Note Section (What to Look For) -->
    <section id="what-to-look-for">
        <h2>What to Look For</h2>
        {self._p(sections.get('note_section', ''))}
    </section>

    <!-- In-content image 1 -->
    <img
        class="content-image"
        src="{esc(ingr_img)}"
        alt="Ingredients for {esc(title)}"
        loading="lazy"
        width="700"
        height="467"
    />

    <!-- Ingredients -->
    <section id="ingredients">
        <h2>Ingredients</h2>
        {self._p(sections.get('ingredients_intro', ''))}
        <ul class="ingredient-list">
{ing_lis}
        </ul>
    </section>

    <!-- In-content image 2 (same as main or card) -->
    <img
        class="content-image"
        src="{esc(main_img)}"
        alt="Making {esc(title)}"
        loading="lazy"
        width="700"
        height="467"
    />

    <!-- How to Make -->
    <section id="how-to-make">
        <h2>How to Make {esc(title)}</h2>
        {self._p(sections.get('instructions_intro', ''))}
        <ol class="steps-list" aria-label="Recipe instructions">
{steps_html}
        </ol>
    </section>

    <!-- In-content image 3 (finished dish) -->
    <img
        class="content-image"
        src="{esc(card_img)}"
        alt="Finished {esc(title)}"
        loading="lazy"
        width="700"
        height="467"
    />

    <!-- Recipe Card -->
    <section id="recipe-card" aria-label="Recipe card">
        <div class="recipe-card">
            <div class="recipe-card__header">
                <div class="recipe-card__title">{esc(recipe.get('name', title))}</div>
                <p class="recipe-card__summary">{esc(recipe.get('summary', ''))}</p>
            </div>

            <img
                class="recipe-card__image"
                src="{esc(card_img)}"
                alt="{esc(recipe.get('name', title))}"
                loading="lazy"
                width="700"
                height="467"
            />

            <div class="recipe-card__buttons">
                <button class="btn btn-print" onclick="window.print()">Print Recipe</button>
                <button class="btn btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Save to Pinterest</button>
            </div>

            <div class="recipe-card__meta" role="list" aria-label="Recipe details">
                <div class="recipe-card__meta-item" role="listitem">
                    <span class="recipe-card__meta-label">Prep</span>
                    <span class="recipe-card__meta-value">{esc(str(recipe.get('prep_time', '15 min')))}</span>
                </div>
                <div class="recipe-card__meta-item" role="listitem">
                    <span class="recipe-card__meta-label">Cook</span>
                    <span class="recipe-card__meta-value">{esc(str(recipe.get('cook_time', '30 min')))}</span>
                </div>
                <div class="recipe-card__meta-item" role="listitem">
                    <span class="recipe-card__meta-label">Total</span>
                    <span class="recipe-card__meta-value">{esc(str(recipe.get('total_time', '45 min')))}</span>
                </div>
                <div class="recipe-card__meta-item" role="listitem">
                    <span class="recipe-card__meta-label">Servings</span>
                    <span class="recipe-card__meta-value">{esc(str(recipe.get('servings', '4')))}</span>
                </div>
                <div class="recipe-card__meta-item" role="listitem">
                    <span class="recipe-card__meta-label">Calories</span>
                    <span class="recipe-card__meta-value">{esc(str(recipe.get('calories', '400')))}</span>
                </div>
                <div class="recipe-card__meta-item" role="listitem">
                    <span class="recipe-card__meta-label">Course</span>
                    <span class="recipe-card__meta-value">{esc(str(recipe.get('course', 'Main')))}</span>
                </div>
                <div class="recipe-card__meta-item" role="listitem">
                    <span class="recipe-card__meta-label">Cuisine</span>
                    <span class="recipe-card__meta-value">{esc(str(recipe.get('cuisine', 'American')))}</span>
                </div>
            </div>

            <div class="recipe-card__section-label">Ingredients</div>
            <ul class="recipe-card__ingredients">
{rc_ings}
            </ul>

            <div class="recipe-card__section-label">Instructions</div>
            <ol class="recipe-card__instructions">
{rc_steps}
            </ol>

            {f'<div class="recipe-card__notes">{rc_notes}</div>' if rc_notes else ''}
        </div>
    </section>

    <!-- FAQs -->
    <section id="faqs" class="faq-section" aria-label="Frequently asked questions">
        <h2>Frequently Asked Questions</h2>
{faq_html}
    </section>

    <!-- Conclusion -->
    <section id="conclusion">
        <h2>Final Thoughts</h2>
        {self._p(sections.get('conclusion', ''))}
    </section>

    <!-- Social Share -->
    <div class="social-share" aria-label="Share this article">
        <span class="social-share__label">Share:</span>
        <a
            class="social-share__btn ssb-facebook"
            href="https://www.facebook.com/sharer/sharer.php?u={esc(share)}"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Share on Facebook"
        >Facebook</a>
        <a
            class="social-share__btn ssb-twitter"
            href="https://twitter.com/intent/tweet?text={esc(title)}&url={esc(share)}"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Share on Twitter"
        >Twitter</a>
        <a
            class="social-share__btn ssb-pinterest"
            href="https://pinterest.com/pin/create/button/?url={esc(share)}&description={esc(title)}"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Save on Pinterest"
        >Pinterest</a>
    </div>

</div><!-- /article-wrap -->
</body>
</html>"""
        return html

    # ------------------------------------------------------- file I/O

    def save_files(self, content_data: dict, html_content: str, css_content: str):
        out = Path(self.slug)
        out.mkdir(parents=True, exist_ok=True)

        # structure.json
        struct_path = out / "structure.json"
        with open(struct_path, "w", encoding="utf-8") as fh:
            json.dump(STRUCTURE, fh, indent=2, ensure_ascii=False)
        print(f"[OK] Saved: {struct_path}")

        # content.json
        content_path = out / "content.json"
        with open(content_path, "w", encoding="utf-8") as fh:
            json.dump(content_data, fh, indent=2, ensure_ascii=False)
        print(f"[OK] Saved: {content_path}")

        # css.css
        css_path = out / "css.css"
        with open(css_path, "w", encoding="utf-8") as fh:
            fh.write(css_content)
        print(f"[OK] Saved: {css_path}")

        # article.html
        html_path = out / "article.html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html_content)
        print(f"[OK] Saved: {html_path}")

        # placeholder.jpg (empty file if images not supplied)
        images_used = [
            content_data.get("main_image", ""),
            content_data.get("ingredient_image", ""),
        ]
        if "placeholder.jpg" in images_used:
            ph = out / "placeholder.jpg"
            if not ph.exists():
                ph.write_bytes(b"")
            print(f"[OK] Placeholder: {ph}")

    # ------------------------------------------------------- public entry point

    def run(self, return_content_only: bool = False):
        if not self.title:
            raise ValueError(
                "CONFIG['title'] must not be empty. "
                "Provide a title via config_override={'title': 'Your Recipe Name'} or CLI argument."
            )

        print(f"[*] generator-7 | Starting: {self.title}")

        css_content  = self.generate_css()
        content_data = self.generate_content()
        html_content = self.generate_html(content_data, css_filename="css.css")

        content_data["article_html"] = html_content
        content_data["article_css"]  = css_content

        if return_content_only:
            return content_data

        self.save_files(content_data, html_content, css_content)
        print("[OK] generator-7 complete!")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    cli_title = " ".join(sys.argv[1:]).strip()
    if not cli_title:
        cli_title = input("Enter recipe title: ").strip()

    gen = ArticleGenerator(config_override={"title": cli_title})
    gen.run()
