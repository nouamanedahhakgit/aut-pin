"""
generator-6.py - Articles Website Generator
Design source: image 4.png (warm white/red accent recipe article)

DESIGN ANALYSIS (extracted by AI, never by this script):
- Background: #f9f7f5 (warm white), Container: #ffffff
- Primary/accent: #e8472a (red), list markers red
- Heading font: Georgia serif | Body: system sans-serif
- Max width: 780px, section spacing 40px
- Pro tips box: #fff8e7 with orange left border #f5a623
- Chef tips box: dark green #2d5016 bg, white text
- FAQ: light green #f0f4f0 buttons with accordion
- Recipe card: white, bordered, with meta grid
- Structure: intro | why_love(4) | ingredients | steps(5) | pro_tips(4) |
             perfecting | add_your_touch | storing_reheating | chef_tips(3) |
             faq(4) | conclusion | recipe_card
"""

import os
import json
import re
import shutil
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary": "#e8472a",
        "secondary": "#2c2c2c",
        "accent": "#e8472a",
        "background": "#f9f7f5",
        "container_bg": "#ffffff",
        "border": "#e5e0da",
        "text_primary": "#2c2c2c",
        "text_secondary": "#555555",
        "button_print": "#e8472a",
        "button_pin": "#e85d7a",
        "button_hover_print": "#c73a1f",
        "button_hover_pin": "#cc3d5e",
        "link": "#e8472a",
        "list_marker": "#e8472a"
    },
    "fonts": {
        "heading": {
            "family": "Georgia, 'Times New Roman', serif",
            "weights": [400, 700],
            "sizes": {"h1": "32px", "h2": "26px", "h3": "20px"}
        },
        "body": {
            "family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif",
            "weight": 400,
            "size": "16px",
            "line_height": 1.7
        }
    },
    "layout": {
        "max_width": "780px",
        "section_spacing": "40px",
        "paragraph_spacing": "18px",
        "list_spacing": "10px",
        "container_padding": "20px",
        "border_radius": "8px",
        "box_shadow": "0 2px 8px rgba(0,0,0,0.08)"
    },
    "components": {
        "numbered_list": {
            "style": "circle",
            "circle_bg": "#e8472a",
            "circle_color": "#ffffff",
            "circle_size": "32px"
        },
        "bullet_list": {"style": "disc", "color": "#e8472a"},
        "pro_tips_box": {
            "bg_color": "#fff8e7",
            "border_color": "#f5a623",
            "border_left": "4px solid #f5a623",
            "padding": "20px 24px"
        },
        "recipe_card": {
            "bg": "#ffffff",
            "border": "1px solid #e5e0da",
            "border_radius": "10px",
            "padding": "28px",
            "meta_icon_color": "#e8472a"
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
            "why_i_love_item_1": 25, "why_i_love_item_2": 25,
            "why_i_love_item_3": 25, "why_i_love_item_4": 25,
            "ingredients_intro": 60,
            "instructions_intro": 60,
            "instructions_step_1": 75, "instructions_step_2": 75,
            "instructions_step_3": 75, "instructions_step_4": 75,
            "instructions_step_5": 75,
            "pro_tips_tip_1": 30, "pro_tips_tip_2": 30,
            "pro_tips_tip_3": 30, "pro_tips_tip_4": 30,
            "perfecting": 80, "add_your_touch": 80, "storing_reheating": 80,
            "chef_tips_tip_1": 30, "chef_tips_tip_2": 30, "chef_tips_tip_3": 30,
            "faq_1_q": 10, "faq_1_a": 50, "faq_2_q": 10, "faq_2_a": 50,
            "faq_3_q": 10, "faq_3_a": 50, "faq_4_q": 10, "faq_4_a": 50,
            "conclusion": 100
        }
    },
    "dark_mode": False
}

STRUCTURE = [
    {"type": "intro", "key": "intro"},
    {"type": "h2", "key": "why_i_love_heading"},
    {"type": "bullet_list", "key": "why_i_love", "count": 4},
    {"type": "h2", "key": "ingredients_heading"},
    {"type": "image", "key": "ingredient_image"},
    {"type": "bullet_list", "key": "ingredient_list"},
    {"type": "h2", "key": "instructions_heading"},
    {"type": "paragraph", "key": "instructions_intro"},
    {"type": "h3", "key": "step_1_heading"},
    {"type": "paragraph", "key": "instructions_step_1"},
    {"type": "h3", "key": "step_2_heading"},
    {"type": "paragraph", "key": "instructions_step_2"},
    {"type": "h3", "key": "step_3_heading"},
    {"type": "paragraph", "key": "instructions_step_3"},
    {"type": "h3", "key": "step_4_heading"},
    {"type": "paragraph", "key": "instructions_step_4"},
    {"type": "h3", "key": "step_5_heading"},
    {"type": "paragraph", "key": "instructions_step_5"},
    {"type": "pro_tips_box", "key": "pro_tips", "count": 4},
    {"type": "h2", "key": "perfecting_heading"},
    {"type": "paragraph", "key": "perfecting"},
    {"type": "h2", "key": "add_your_touch_heading"},
    {"type": "paragraph", "key": "add_your_touch"},
    {"type": "h2", "key": "storing_reheating_heading"},
    {"type": "paragraph", "key": "storing_reheating"},
    {"type": "pro_tips_box", "key": "chef_tips", "count": 3, "variant": "chef"},
    {"type": "faq", "key": "faqs", "count": 4},
    {"type": "h2", "key": "conclusion_heading"},
    {"type": "paragraph", "key": "conclusion"},
    {"type": "image", "key": "main_article_image"},
    {"type": "recipe_card", "key": "recipe_card"}
]


class ArticleGenerator:
    def __init__(self, config_override=None):
        self.config = {}
        for k, v in CONFIG.items():
            self.config[k] = dict(v) if isinstance(v, dict) else v
        if config_override:
            for k, v in config_override.items():
                if isinstance(v, dict) and k in self.config and isinstance(self.config[k], dict):
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

        self.title = self.config.get("title", "").strip()
        if not self.title:
            raise ValueError("[ERROR] CONFIG['title'] must not be empty.")
        self.slug = re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")

    def gpt(self, prompt, max_tokens=600, system=None):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.75
        )
        return resp.choices[0].message.content.strip()

    def _extract_json(self, raw):
        text = (raw or "").strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m:
            text = m.group(1).strip()
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            return json.loads(m.group())
        return {}

    def _strip_markdown(self, s):
        if not s or not isinstance(s, str):
            return str(s or "")
        s = re.sub(r"^#{1,6}\s*", "", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
        s = re.sub(r"\*([^*]+)\*", r"\1", s)
        return s.strip()

    def generate_sections(self):
        """Generate all sections in ONE API call (optimized for speed)."""
        t = self.title
        wc = self.config["structure_template"]["word_counts"]
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and (existing.get("ingredients") or existing.get("instructions")):
            recipe_in_config = True
        else:
            recipe_in_config = False

        schema = {
            "intro": f"string ~{wc['intro']} words",
            "why_i_love_item_1": f"string ~{wc['why_i_love_item_1']} words, format 'Label: text'",
            "why_i_love_item_2": "same",
            "why_i_love_item_3": "same",
            "why_i_love_item_4": "same",
            "ingredients_intro": f"string ~{wc['ingredients_intro']} words",
            "ingredient_list_raw": "string: 10-12 ingredients, one per line with '- '",
            "instructions_intro": f"string ~{wc['instructions_intro']} words",
            "step_1_label": "e.g. Prepare Your Ingredients",
            "instructions_step_1": f"string ~{wc['instructions_step_1']} words",
            "step_2_label": "e.g. Start the Base",
            "instructions_step_2": f"string ~{wc['instructions_step_2']} words",
            "step_3_label": "e.g. Build the Sauce",
            "instructions_step_3": f"string ~{wc['instructions_step_3']} words",
            "step_4_label": "e.g. Combine and Cook",
            "instructions_step_4": f"string ~{wc['instructions_step_4']} words",
            "step_5_label": "e.g. Finish and Serve",
            "instructions_step_5": f"string ~{wc['instructions_step_5']} words",
            "pro_tips_tip_1": f"string ~{wc['pro_tips_tip_1']} words, format 'TipName: advice'",
            "pro_tips_tip_2": "same", "pro_tips_tip_3": "same", "pro_tips_tip_4": "same",
            "perfecting": f"string ~{wc['perfecting']} words",
            "add_your_touch": f"string ~{wc['add_your_touch']} words",
            "storing_reheating": f"string ~{wc['storing_reheating']} words",
            "chef_tips_tip_1": f"string ~{wc['chef_tips_tip_1']} words",
            "chef_tips_tip_2": "same", "chef_tips_tip_3": "same",
            "faq_1_q": "short question", "faq_1_a": f"answer ~{wc['faq_1_a']} words",
            "faq_2_q": "short question", "faq_2_a": "answer",
            "faq_3_q": "short question", "faq_3_a": "answer",
            "faq_4_q": "short question", "faq_4_a": "answer",
            "conclusion": f"string ~{wc['conclusion']} words",
            "meta_description": "120-140 chars",
            "focus_keyphrase": "3-5 words",
            "keyphrase_synonyms": "comma-separated",
            "pinterest_title": "max 100 chars",
            "pinterest_description": "2-3 sentences",
            "pinterest_keywords": "6 comma-separated",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine" if not recipe_in_config else "(omit - provided)",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        if recipe_in_config:
            schema.pop("recipe", None)

        system = (
            "You are a professional food blogger. Generate the FULL recipe article as ONE JSON object. "
            "All content must be ONLY about the recipe title. Plain text only: no ##, ###, **, * markdown. "
            "Return ONLY valid JSON."
        )
        user = (
            f"Generate the complete recipe article for '{t}' as JSON with these keys:\n{json.dumps(schema, indent=2)}\n\n"
            f"All content for {t} only. Return ONLY the JSON object."
        )

        print("[*] Generating all sections in a single JSON API call...")
        from ai_client import ai_chat
        raw = ai_chat(self, user, max_tokens=6000, system=system)
        
        # Extract json manually for robustness
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

        s = {}
        for k in ["intro", "ingredients_intro", "ingredient_list_raw", "instructions_intro",
                  "instructions_step_1", "instructions_step_2", "instructions_step_3",
                  "instructions_step_4", "instructions_step_5",
                  "perfecting", "add_your_touch", "storing_reheating", "conclusion",
                  "meta_description", "focus_keyphrase", "keyphrase_synonyms",
                  "pinterest_title", "pinterest_description", "pinterest_keywords",
                  "prompt_midjourney_main", "prompt_midjourney_ingredients"]:
            v = data.get(k, "")
            s[k] = self._strip_markdown(str(v)) if isinstance(v, str) else v

        step_labels = ["Prepare Your Ingredients", "Start the Base", "Build the Sauce", "Combine and Cook", "Finish and Serve"]
        for i in range(1, 6):
            s[f"step_{i}_label"] = data.get(f"step_{i}_label", step_labels[i - 1])

        for i in range(1, 5):
            raw_val = data.get(f"why_i_love_item_{i}", "")
            if isinstance(raw_val, str) and raw_val.strip().lower().startswith("boldlabel:"):
                raw_val = raw_val.split(":", 1)[-1].strip()
                raw_val = "Key Benefit: " + raw_val if raw_val else raw_val
            s[f"why_i_love_item_{i}"] = self._strip_markdown(str(raw_val or ""))

        for i in range(1, 5):
            s[f"pro_tips_tip_{i}"] = self._strip_markdown(str(data.get(f"pro_tips_tip_{i}", "")))
        for i in range(1, 4):
            s[f"chef_tips_tip_{i}"] = self._strip_markdown(str(data.get(f"chef_tips_tip_{i}", "")))
        for i in range(1, 5):
            s[f"faq_{i}_q"] = self._strip_markdown(str(data.get(f"faq_{i}_q", "")))
            s[f"faq_{i}_a"] = self._strip_markdown(str(data.get(f"faq_{i}_a", "")))

        s["meta_description"] = (s.get("meta_description") or "")[:140]
        s["pinterest_title"] = (s.get("pinterest_title") or "")[:100]

        if recipe_in_config:
            defaults = {"name": t, "summary": "", "ingredients": [], "instructions": [],
                        "prep_time": "15 mins", "cook_time": "30 mins", "total_time": "45 mins",
                        "servings": 4, "calories": 450, "course": "Main", "cuisine": "American"}
            s["recipe"] = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        else:
            recipe = data.get("recipe") or {}
            try:
                if isinstance(recipe, dict) and (recipe.get("ingredients") or recipe.get("instructions")):
                    s["recipe"] = recipe
                else:
                    raise ValueError("No recipe in response")
            except Exception:
                s["recipe"] = {
                    "name": t, "summary": "", "ingredients": [], "instructions": [],
                    "prep_time": "15 mins", "cook_time": "30 mins", "total_time": "45 mins",
                    "servings": 4, "calories": 450, "course": "Main", "cuisine": "American"
                }

        return s

    def _generate_sections_sequential(self):
        t = self.title
        wc = self.config["structure_template"]["word_counts"]
        existing = self.config.get("recipe")
        if existing and isinstance(existing, dict) and (existing.get("ingredients") or existing.get("instructions")):
            recipe_in_config = True
        else:
            recipe_in_config = False

        s = {}

        print("[*] Generating intro...")
        s["intro"] = self._strip_markdown(self.gpt(f"Write a warm, engaging intro paragraph (~{wc['intro']} words) for a recipe article about {t}. No headings. Plain text.", 300))

        print("[*] Generating why-love items...")
        for i in range(1, 5):
            s[f"why_i_love_item_{i}"] = self._strip_markdown(self.gpt(f"Write reason {i} of 4 why someone will love {t} (~{wc[f'why_i_love_item_{i}']} words). Format 'Label: description'. Plain text.", 150))

        print("[*] Generating ingredients...")
        s["ingredients_intro"] = self._strip_markdown(self.gpt(f"Write a short intro (~{wc['ingredients_intro']} words) about the ingredients for {t}.", 150))
        s["ingredient_list_raw"] = self._strip_markdown(self.gpt(f"List 10-12 ingredients for {t} with amounts. One per line starting with '- '.", 250))

        print("[*] Generating instructions...")
        s["instructions_intro"] = self._strip_markdown(self.gpt(f"Write a short intro (~{wc['instructions_intro']} words) for the instructions of {t}.", 150))
        
        step_labels = ["Prepare Your Ingredients", "Start the Base", "Build the Sauce", "Combine and Cook", "Finish and Serve"]
        for i in range(1, 6):
            s[f"step_{i}_label"] = step_labels[i-1]
            s[f"instructions_step_{i}"] = self._strip_markdown(self.gpt(f"Write step {i} instructions for making {t} (~{wc[f'instructions_step_{i}']} words). Step title is '{step_labels[i-1]}'. Plain text paragraph.", 200))

        print("[*] Generating pro tips...")
        for i in range(1, 5):
            s[f"pro_tips_tip_{i}"] = self._strip_markdown(self.gpt(f"Write pro tip {i} of 4 for {t} (~{wc[f'pro_tips_tip_{i}']} words). Format 'TipName: advice'.", 150))

        print("[*] Generating sub-sections...")
        s["perfecting"] = self._strip_markdown(self.gpt(f"Write a paragraph (~{wc['perfecting']} words) on perfecting the cooking process for {t}.", 200))
        s["add_your_touch"] = self._strip_markdown(self.gpt(f"Write a paragraph (~{wc['add_your_touch']} words) on adding personal touches/variations to {t}.", 200))
        s["storing_reheating"] = self._strip_markdown(self.gpt(f"Write a paragraph (~{wc['storing_reheating']} words) on storing and reheating {t}.", 200))

        print("[*] Generating chef tips...")
        for i in range(1, 4):
            s[f"chef_tips_tip_{i}"] = self._strip_markdown(self.gpt(f"Write chef tip {i} of 3 for {t} (~{wc[f'chef_tips_tip_{i}']} words).", 150))

        print("[*] Generating FAQs...")
        faq_topics = [
            "Can I make this ahead of time?",
            "What can I substitute if I don't have a key ingredient?",
            "How do I store leftovers?",
            "Can I freeze this dish?"
        ]
        for i in range(1, 5):
            s[f"faq_{i}_q"] = faq_topics[i-1]
            s[f"faq_{i}_a"] = self._strip_markdown(self.gpt(f"Answer FAQ: '{faq_topics[i-1]}' for {t} (~{wc[f'faq_{i}_a']} words).", 150))

        print("[*] Generating conclusion...")
        s["conclusion"] = self._strip_markdown(self.gpt(f"Write a conclusion paragraph (~{wc['conclusion']} words) for {t}.", 200))

        print("[*] Generating SEO data...")
        s["meta_description"] = self._strip_markdown(self.gpt(f"Write a 120-140 char meta description for {t}.", 100))[:140]
        s["focus_keyphrase"] = self._strip_markdown(self.gpt(f"Write a 3-5 word focus keyphrase for {t}.", 50))
        s["keyphrase_synonyms"] = self._strip_markdown(self.gpt(f"Write comma separated keyphrase synonyms for {t}.", 100))
        s["pinterest_title"] = self._strip_markdown(self.gpt(f"Write a max 100 char Pinterest title for {t}.", 100))[:100]
        s["pinterest_description"] = self._strip_markdown(self.gpt(f"Write a 2-3 sentence Pinterest description for {t}.", 150))
        s["pinterest_keywords"] = self._strip_markdown(self.gpt(f"Write 6 comma separated Pinterest keywords for {t}.", 100))

        print("[*] Generating Midjourney prompts...")
        s["prompt_midjourney_main"] = self._strip_markdown(self.gpt(f"Write a Midjourney prompt for the main photo of {t} ending with --v 6.1", 150))
        s["prompt_midjourney_ingredients"] = self._strip_markdown(self.gpt(f"Write a Midjourney prompt for the ingredients flat-lay of {t} ending with --v 6.1", 150))

        print("[*] Generating recipe card data...")
        if recipe_in_config:
            defaults = {"name": t, "summary": "", "ingredients": [], "instructions": [],
                        "prep_time": "15 mins", "cook_time": "30 mins", "total_time": "45 mins",
                        "servings": 4, "calories": 450, "course": "Main", "cuisine": "American"}
            s["recipe"] = {**defaults, **{k: v for k, v in existing.items() if v is not None and v != ""}}
        else:
            recipe_json_raw = self.gpt(
                f"Create a JSON recipe card for {t} with: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine.",
                max_tokens=800
            )
            data = self._extract_json(recipe_json_raw)
            if data and isinstance(data, dict):
                s["recipe"] = data
            else:
                s["recipe"] = {
                    "name": t, "summary": "", "ingredients": [], "instructions": [],
                    "prep_time": "15 mins", "cook_time": "30 mins", "total_time": "45 mins",
                    "servings": 4, "calories": 450, "course": "Main", "cuisine": "American"
                }

        return s

    def build_css(self):
        c = self.config["colors"]
        f = self.config["fonts"]
        lay = self.config["layout"]
        comp = self.config["components"]
        nl = comp["numbered_list"]
        pt = comp["pro_tips_box"]
        rc = comp["recipe_card"]

        return f"""/* generator-6 stylesheet */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    background-color: {c['background']};
    color: {c['text_primary']};
    font-family: {f['body']['family']};
    font-size: {f['body']['size']};
    line-height: {f['body']['line_height']};
}}

.article-container {{
    max-width: {lay['max_width']};
    margin: 0 auto;
    padding: 30px {lay['container_padding']};
    background: {c['container_bg']};
}}

.article-header.g9-header {{
    margin-bottom: 24px;
}}
.article-header.g9-header .article-title {{
    font-family: {f['heading']['family']};
    font-size: {f['heading']['sizes']['h1']};
    color: {c['text_primary']};
    margin: 0 0 12px 0;
    line-height: 1.3;
}}
.article-header.g9-header .article-byline-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}}
.article-header.g9-header .byline-left {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.article-header.g9-header .byline-author {{ font-weight: 600; color: {c['text_primary']}; }}
.article-header.g9-header .byline-date {{ font-size: 0.875rem; color: {c['text_secondary']}; }}
.article-header.g9-header .byline-disclaimer {{ font-size: 0.8rem; color: {c['text_secondary']}; font-style: italic; margin-top: 0.2rem; }}
.article-header.g9-header .byline-right {{ display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }}
.article-header.g9-header .recipe-meta-stack {{ display: flex; gap: 1rem; font-size: 0.9rem; color: {c['text_secondary']}; }}

h1, h2, h3, h4 {{
    font-family: {f['heading']['family']};
    color: {c['text_primary']};
    line-height: 1.3;
}}
h1 {{ font-size: {f['heading']['sizes']['h1']}; margin-bottom: 20px; }}
h2 {{ font-size: {f['heading']['sizes']['h2']}; margin-top: {lay['section_spacing']}; margin-bottom: 16px; }}
h3 {{ font-size: {f['heading']['sizes']['h3']}; margin-top: 28px; margin-bottom: 12px; }}

p {{ margin-bottom: {lay['paragraph_spacing']}; color: {c['text_secondary']}; }}
a {{ color: {c['link']}; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

.article-intro {{ margin-bottom: {lay['section_spacing']}; }}

.article-image {{
    width: 100%; border-radius: {lay['border_radius']};
    margin: 24px 0; display: block;
    object-fit: cover; max-height: 420px;
}}

.why-love-list {{ list-style: none; padding: 0; margin: 0 0 {lay['section_spacing']} 0; }}
.why-love-list li {{
    padding: 10px 0 10px 28px; position: relative;
    color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.why-love-list li::before {{
    content: ''; position: absolute; left: 0; top: 18px;
    width: 10px; height: 10px; background: {c['list_marker']}; border-radius: 50%;
}}
.why-love-list li strong {{ color: {c['text_primary']}; }}

.ingredient-list {{
    list-style: none; padding: 0;
    margin: 0 0 {lay['section_spacing']} 0;
    columns: 2; column-gap: 30px;
}}
.ingredient-list li {{
    padding: {lay['list_spacing']} 0 {lay['list_spacing']} 20px;
    position: relative; color: {c['text_secondary']}; break-inside: avoid;
}}
.ingredient-list li::before {{
    content: ''; position: absolute; left: 0; top: 18px;
    width: 8px; height: 8px; background: {c['list_marker']}; border-radius: 50%;
}}
@media (max-width: 600px) {{ .ingredient-list {{ columns: 1; }} }}

.step-block {{ margin-bottom: 24px; }}
.step-heading-row {{ display: flex; align-items: center; margin-bottom: 10px; }}
.step-heading-row h3 {{ margin: 0; }}
.step-number {{
    display: inline-flex; align-items: center; justify-content: center;
    width: {nl['circle_size']}; height: {nl['circle_size']};
    background: {nl['circle_bg']}; color: {nl['circle_color']};
    border-radius: 50%; font-weight: 700; font-size: 14px;
    margin-right: 10px; flex-shrink: 0;
}}

.pro-tips-box {{
    background: {pt['bg_color']};
    border-left: {pt['border_left']};
    padding: {pt['padding']};
    border-radius: 0 {lay['border_radius']} {lay['border_radius']} 0;
    margin: {lay['section_spacing']} 0;
}}
.pro-tips-box h3 {{ margin-top: 0; margin-bottom: 14px; font-size: 18px; }}
.pro-tips-list {{ list-style: none; padding: 0; margin: 0; }}
.pro-tips-list li {{
    padding: 7px 0; color: {c['text_secondary']};
    border-bottom: 1px solid rgba(0,0,0,0.06);
}}
.pro-tips-list li:last-child {{ border-bottom: none; }}
.pro-tips-list li strong {{ color: {c['text_primary']}; }}

.chef-tips-box {{
    background: #2d5016; color: #ffffff;
    padding: 24px 28px; border-radius: {lay['border_radius']};
    margin: {lay['section_spacing']} 0;
}}
.chef-tips-box h3 {{ color: #ffffff; margin-top: 0; margin-bottom: 14px; font-size: 18px; }}
.chef-tips-list {{ list-style: none; padding: 0; margin: 0; }}
.chef-tips-list li {{
    padding: 7px 0; color: rgba(255,255,255,0.9);
    border-bottom: 1px solid rgba(255,255,255,0.15);
}}
.chef-tips-list li:last-child {{ border-bottom: none; }}
.chef-tips-list li strong {{ color: #ffffff; }}

.faq-section {{ margin: {lay['section_spacing']} 0; }}
.faq-item {{
    border: 1px solid {c['border']}; border-radius: {lay['border_radius']};
    margin-bottom: 10px; overflow: hidden;
}}
.faq-question {{
    width: 100%; background: #f0f4f0; border: none;
    text-align: left; padding: 16px 20px;
    font-family: {f['heading']['family']};
    font-size: 16px; font-weight: 700; color: {c['text_primary']};
    cursor: pointer; display: flex; justify-content: space-between; align-items: center;
}}
.faq-question::after {{ content: '+'; font-size: 22px; color: {c['primary']}; }}
.faq-question.open::after {{ content: '-'; }}
.faq-answer {{
    display: none; padding: 14px 20px;
    color: {c['text_secondary']}; background: {c['container_bg']};
    border-top: 1px solid {c['border']};
}}
.faq-answer.open {{ display: block; }}

.recipe-card {{
    background: {rc['bg']}; border: {rc['border']};
    border-radius: {rc['border_radius']}; padding: {rc['padding']};
    margin: {lay['section_spacing']} 0; box-shadow: {lay['box_shadow']};
}}
.recipe-card h2 {{ margin-top: 0; font-size: 24px; text-align: center; }}
.recipe-card-image {{
    width: 100%; height: 260px; object-fit: cover;
    border-radius: {lay['border_radius']}; margin: 16px 0; display: block;
}}
.recipe-card-buttons {{ display: flex; gap: 12px; margin: 16px 0; }}
.btn-print {{
    background: {c['button_print']}; color: #fff; border: none;
    padding: 10px 20px; border-radius: {lay['border_radius']};
    cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.2s;
}}
.btn-print:hover {{ background: {c['button_hover_print']}; }}
.btn-pin {{
    background: {c['button_pin']}; color: #fff; border: none;
    padding: 10px 20px; border-radius: {lay['border_radius']};
    cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.2s;
}}
.btn-pin:hover {{ background: {c['button_hover_pin']}; }}
.recipe-meta {{
    display: flex; flex-wrap: wrap; gap: 16px; margin: 16px 0;
    padding: 16px; background: {c['background']}; border-radius: {lay['border_radius']};
}}
.recipe-meta-item {{ text-align: center; flex: 1; min-width: 80px; }}
.recipe-meta-label {{
    font-size: 11px; text-transform: uppercase;
    color: {c['text_secondary']}; letter-spacing: 0.05em;
}}
.recipe-meta-value {{
    font-size: 16px; font-weight: 700; color: {rc['meta_icon_color']};
    display: block; margin-top: 4px;
}}
.recipe-summary {{ color: {c['text_secondary']}; margin: 14px 0; font-style: italic; }}
.recipe-card h3 {{
    margin-top: 22px; margin-bottom: 10px; font-size: 18px;
    border-bottom: 2px solid {c['primary']}; padding-bottom: 6px;
}}
.recipe-ingredients-list {{ list-style: none; padding: 0; margin: 0; }}
.recipe-ingredients-list li {{
    padding: 7px 0 7px 20px; position: relative;
    color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.recipe-ingredients-list li:last-child {{ border-bottom: none; }}
.recipe-ingredients-list li::before {{
    content: ''; position: absolute; left: 0; top: 17px;
    width: 8px; height: 8px; background: {c['list_marker']}; border-radius: 50%;
}}
.recipe-instructions-list {{
    list-style: none; padding: 0; margin: 0; counter-reset: step-counter;
}}
.recipe-instructions-list li {{
    counter-increment: step-counter;
    padding: 10px 0 10px 48px; position: relative;
    color: {c['text_secondary']}; border-bottom: 1px solid {c['border']};
}}
.recipe-instructions-list li:last-child {{ border-bottom: none; }}
.recipe-instructions-list li::before {{
    content: counter(step-counter);
    position: absolute; left: 0; top: 10px;
    width: 32px; height: 32px;
    background: {nl['circle_bg']}; color: {nl['circle_color']};
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 14px;
}}
.recipe-nutrition {{
    background: {c['background']}; padding: 14px 16px;
    border-radius: {lay['border_radius']}; margin-top: 16px;
    font-size: 14px; color: {c['text_secondary']};
}}
@media print {{
    .recipe-card-buttons {{ display: none; }}
    body {{ background: white; }}
}}
@media (max-width: 600px) {{
    h1 {{ font-size: 24px; }}
    h2 {{ font-size: 20px; }}
    .recipe-card-buttons {{ flex-direction: column; }}
}}""".strip()

    def parse_bullets(self, raw):
        lines = [l.strip().lstrip("-*+ ").strip() for l in raw.strip().split("\n") if l.strip()]
        return [l for l in lines if l]

    def _strip_markdown(self, text):
        """Remove ###, **, * so content is safe for HTML."""
        if not text or not isinstance(text, str):
            return text
        s = str(text).strip()
        s = re.sub(r'^#{1,6}\s*', '', s)
        s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'\*([^*]+)\*', r'\1', s)
        return s.strip()

    def e(self, s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def build_html(self, sections, css_filename="css.css"):
        t = self.title
        esc = self.e
        imgs = self.config["images"]
        main_img = imgs.get("main_article_image") or "placeholder.jpg"
        ing_img = imgs.get("ingredient_image") or "placeholder.jpg"
        card_img = imgs.get("recipe_card_image") or "placeholder.jpg"

        # Why love items
        why_html = "".join(
            f"  <li>{sections.get(f'why_i_love_item_{i}', '')}</li>\n"
            for i in range(1, 5)
        )

        # Ingredient list
        raw_ing = sections.get("ingredient_list_raw", "")
        ing_items = self.parse_bullets(raw_ing)
        ing_li = "".join(f"  <li>{esc(it)}</li>\n" for it in ing_items)

        # Steps
        step_labels = [sections.get(f"step_{i}_label", f"Step {i}") for i in range(1, 6)]
        steps_html = ""
        for i in range(1, 6):
            label = esc(step_labels[i - 1])
            content = sections.get(f"instructions_step_{i}", "")
            steps_html += f"""
<div class="step-block">
  <div class="step-heading-row">
    <span class="step-number">{i}</span>
    <h3>{label}</h3>
  </div>
  <p>{content}</p>
</div>"""

        # Pro tips — strip markdown so no ### or ** appears
        pro_li = "".join(
            f"  <li>{esc(self._strip_markdown(sections.get(f'pro_tips_tip_{i}', '')))}</li>\n"
            for i in range(1, 5)
        )

        # Chef tips — strip markdown
        chef_li = "".join(
            f"  <li>{esc(self._strip_markdown(sections.get(f'chef_tips_tip_{i}', '')))}</li>\n"
            for i in range(1, 4)
        )

        # FAQs
        faq_html = ""
        for i in range(1, 5):
            q = esc(sections.get(f"faq_{i}_q", f"Question {i}"))
            a = sections.get(f"faq_{i}_a", "")
            faq_html += f"""  <div class="faq-item">
    <button class="faq-question" onclick="toggleFaq(this)">{q}</button>
    <div class="faq-answer">{a}</div>
  </div>
"""

        # Recipe card
        recipe = sections.get("recipe", {})
        r_name = esc(recipe.get("name", t))
        r_summary = esc(recipe.get("summary", ""))
        r_prep = esc(recipe.get("prep_time", "15 mins"))
        r_cook = esc(recipe.get("cook_time", "30 mins"))
        r_total = esc(recipe.get("total_time", "45 mins"))
        r_srv = esc(str(recipe.get("servings", 4)))
        r_cal = esc(str(recipe.get("calories", "")))
        r_course = esc(recipe.get("course", "Main"))
        r_cuisine = esc(recipe.get("cuisine", ""))
        r_ing_li = "".join(f"    <li>{esc(x)}</li>\n" for x in recipe.get("ingredients", []))
        r_inst_li = "".join(f"    <li>{esc(x)}</li>\n" for x in recipe.get("instructions", []))

        meta_desc = esc(sections.get("meta_description", ""))

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{meta_desc}" />
  <title>{esc(t)}</title>
  <link rel="stylesheet" href="{css_filename}" />
</head>
<body>
<div class="article-container">

<header class="article-header g9-header">
  <h1 class="article-title">{esc(t)}</h1>
  <div class="article-byline-row">
    <div class="byline-left">
      <span class="byline-author">By <span class="article-author"></span></span>
      <span class="byline-date">Published <span class="article-date"></span></span>
      <p class="byline-disclaimer">This post may contain affiliate links.</p>
    </div>
    <div class="byline-right">
      <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
      <div class="recipe-meta-stack"><span>{r_prep} prep</span><span>{r_cook} cook</span><span>{r_srv} servings</span></div>
    </div>
  </div>
</header>
<img src="{main_img}" alt="{esc(t)}" class="article-image" />

<div class="article-intro">
  <p>{sections.get('intro', '')}</p>
</div>

<h2>Why You'll Love This {esc(t)}</h2>
<ul class="why-love-list">
{why_html}</ul>

<h2>Ingredients for {esc(t)}</h2>
<p>{sections.get('ingredients_intro', '')}</p>
<img src="{ing_img}" alt="Ingredients for {esc(t)}" class="article-image" />
<ul class="ingredient-list">
{ing_li}</ul>

<h2>How to Make {esc(t)}</h2>
<p>{sections.get('instructions_intro', '')}</p>
{steps_html}

<div class="pro-tips-box">
  <h3>You Must Know About {esc(t)}</h3>
  <ul class="pro-tips-list">
{pro_li}  </ul>
</div>

<h2>Perfecting {esc(t)}</h2>
<p>{sections.get('perfecting', '')}</p>

<h2>Add Your Touch to {esc(t)}</h2>
<p>{sections.get('add_your_touch', '')}</p>

<h2>Storing and Reheating {esc(t)}</h2>
<p>{sections.get('storing_reheating', '')}</p>

<div class="chef-tips-box">
  <h3>Chef's Helpful Tips for {esc(t)}</h3>
  <ul class="chef-tips-list">
{chef_li}  </ul>
</div>

<div class="faq-section">
  <h2>FAQs About {esc(t)}</h2>
{faq_html}</div>

<h2>Conclusion for {esc(t)}</h2>
<p>{sections.get('conclusion', '')}</p>

<div class="recipe-card" id="recipe-card">
  <h2>{r_name}</h2>
  <img src="{card_img}" alt="{r_name}" class="recipe-card-image" />
  <div class="recipe-card-buttons">
    <button class="btn-print" onclick="window.print()">Print Recipe</button>
    <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Save to Pinterest</button>
  </div>
  <div class="recipe-meta">
    <div class="recipe-meta-item">
      <span class="recipe-meta-label">Prep Time</span>
      <span class="recipe-meta-value">{r_prep}</span>
    </div>
    <div class="recipe-meta-item">
      <span class="recipe-meta-label">Cook Time</span>
      <span class="recipe-meta-value">{r_cook}</span>
    </div>
    <div class="recipe-meta-item">
      <span class="recipe-meta-label">Total Time</span>
      <span class="recipe-meta-value">{r_total}</span>
    </div>
    <div class="recipe-meta-item">
      <span class="recipe-meta-label">Servings</span>
      <span class="recipe-meta-value">{r_srv}</span>
    </div>
    <div class="recipe-meta-item">
      <span class="recipe-meta-label">Calories</span>
      <span class="recipe-meta-value">{r_cal}</span>
    </div>
  </div>
  <p class="recipe-summary">{r_summary}</p>
  <h3>Ingredients</h3>
  <ul class="recipe-ingredients-list">
{r_ing_li}  </ul>
  <h3>Instructions</h3>
  <ol class="recipe-instructions-list">
{r_inst_li}  </ol>
  <div class="recipe-nutrition">
    <strong>Course:</strong> {r_course} &nbsp;|&nbsp;
    <strong>Cuisine:</strong> {r_cuisine} &nbsp;|&nbsp;
    <strong>Calories per serving:</strong> {r_cal} kcal
  </div>
</div>

</div>

<script>
function toggleFaq(btn) {{
  btn.classList.toggle('open');
  var answer = btn.nextElementSibling;
  answer.classList.toggle('open');
}}
</script>
</body>
</html>"""

    def build_content_data(self, sections, html_content, css_content):
        from ai_client import get_first_category
        cat = get_first_category(self.config)
        return {
            "title": self.title,
            "slug": self.slug,
            "categorieId": str(cat.get("id", "")),
            "categorie": cat.get("categorie", ""),
            "sections": STRUCTURE,
            "article_html": html_content,
            "article_css": css_content,
            "prompt_used": f"Article generated for: {self.title}",
            "prompt_base": "generator-6",
            "recipe": sections.get("recipe", {}),
            "recipe_title_pin": sections.get("pinterest_title", self.title)[:100],
            "pinterest_title": sections.get("pinterest_title", self.title)[:100],
            "pinterest_description": sections.get("pinterest_description", ""),
            "pinterest_keywords": sections.get("pinterest_keywords", ""),
            "focus_keyphrase": sections.get("focus_keyphrase", ""),
            "meta_description": sections.get("meta_description", "")[:140],
            "keyphrase_synonyms": sections.get("keyphrase_synonyms", ""),
            "main_image": self.config["images"].get("main_article_image", ""),
            "ingredient_image": self.config["images"].get("ingredient_image", ""),
            "prompt_midjourney_main": sections.get("prompt_midjourney_main", ""),
            "prompt_midjourney_ingredients": sections.get("prompt_midjourney_ingredients", "")
        }

    def save_files(self, content_data, html_content, css_content):
        out_dir = Path(self.slug)
        out_dir.mkdir(parents=True, exist_ok=True)

        with open(out_dir / "content.json", "w", encoding="utf-8") as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)

        with open(out_dir / "article.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        with open(out_dir / "css.css", "w", encoding="utf-8") as f:
            f.write(css_content)

        with open(out_dir / "structure.json", "w", encoding="utf-8") as f:
            json.dump(STRUCTURE, f, indent=2)

        placeholder_src = Path("placeholder.jpg")
        if placeholder_src.exists():
            shutil.copy(placeholder_src, out_dir / "placeholder.jpg")

        print(f"[OK] Files saved to: {self.slug}/")

    def run(self, return_content_only=False):
        print(f"[*] Starting generator-6 for: {self.title}")
        sections = self.generate_sections()
        css_content = self.build_css()
        html_content = self.build_html(sections, css_filename="css.css")
        content_data = self.build_content_data(sections, html_content, css_content)

        if return_content_only:
            return content_data

        self.save_files(content_data, html_content, css_content)
        print("[OK] Complete!")
        return content_data


if __name__ == "__main__":
    import sys
    title = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    if not title:
        print("[ERROR] Usage: python generator-6.py <Recipe Title>")
        print("[ERROR] Example: python generator-6.py Creamy Garlic Butter Pasta")
        sys.exit(1)
    gen = ArticleGenerator(config_override={"title": title})
    gen.run()
