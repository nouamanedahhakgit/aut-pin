"""
generator-20.py — Five Kitchen Secrets (listicle + science)
------------------------------------------------------------
Listicle structure: eyebrow, hero, hook intro, five numbered "secret" cards,
"Why it works" science strip, ingredient image + list, steps, mini FAQ, recipe card.
Warm terracotta / cream on white. Default R2 images for preview.
"""

import html as html_module
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MAIN_IMG = "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/5c3d26dc/9d4e2053736.png"
DEFAULT_ING_IMG = "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/ingredient_image/aab89f7d/5d8abbf671e.png"


def _e(s, attr=False):
    return html_module.escape(str(s if s is not None else ""), quote=attr)


CONFIG = {
    "title": "Cast-Iron Skillet Ribeye with Garlic Butter",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary": "#B85C38",
        "secondary": "#D4A574",
        "accent": "#E8C4A8",
        "background": "#ffffff",
        "container_bg": "#ffffff",
        "border": "#EDDED4",
        "text_primary": "#2B2118",
        "text_secondary": "#5C4A3D",
        "button_print": "#B85C38",
        "button_pin": "#E60023",
        "button_hover_print": "#9A4A2E",
        "button_hover_pin": "#FF1A3C",
        "link": "#B85C38",
        "list_marker": "#B85C38",
    },
    "fonts": {
        "heading": {
            "family": "Libre Baskerville",
            "weights": [400, 700],
            "sizes": {"h1": "2.1rem", "h2": "1.45rem", "h3": "1.05rem"},
        },
        "body": {"family": "Source Sans 3", "weight": 400, "size": "1.05rem", "line_height": 1.75},
    },
    "layout": {
        "max_width": "720px",
        "section_spacing": "1.85rem",
        "paragraph_spacing": "1rem",
        "list_spacing": "0.5rem",
        "container_padding": "2rem",
        "border_radius": "10px",
        "box_shadow": "0 2px 14px rgba(184, 92, 56, 0.07)",
    },
    "components": {
        "numbered_list": {
            "style": "circle",
            "circle_bg": "#B85C38",
            "circle_color": "#fff",
            "circle_size": "30px",
        },
        "bullet_list": {"style": "disc", "color": "#B85C38"},
        "secret_card": {"number_bg": "#FDF6F3", "accent_border": "#D4A574"},
        "science_box": {"bg_color": "#FFF9F5", "border_left": "4px solid #B85C38"},
        "recipe_card": {
            "bg": "#ffffff",
            "border": "1px solid #EDDED4",
            "border_radius": "10px",
            "padding": "1.5rem",
            "meta_icon_color": "#B85C38",
        },
    },
    "images": {
        "main_article_image": DEFAULT_MAIN_IMG,
        "ingredient_image": DEFAULT_ING_IMG,
        "recipe_card_image": "",
    },
    "structure_template": {
        "word_counts": {"intro": 120, "secret": 55, "why_it_works": 70, "step": 65}
    },
    "dark_mode": False,
}


class ArticleGenerator:
    def __init__(self, config_override=None):
        self.config = dict(CONFIG)
        if config_override:
            self._merge(self.config, config_override)
        if not self.config.get("components") or not isinstance(self.config.get("components"), dict):
            self.config["components"] = dict(CONFIG["components"])
        from ai_client import create_ai_client

        self.client, self.model = create_ai_client(self.config)
        self.title = (self.config["title"] or CONFIG["title"]).strip()
        self.slug = self._slugify(self.title)

    def _merge(self, b, o):
        for k, v in o.items():
            if k in b and isinstance(b[k], dict) and isinstance(v, dict):
                self._merge(b[k], v)
            else:
                b[k] = v

    def _slugify(self, t):
        return re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", t.lower()).strip()) or "article"

    def _strip_md(self, t):
        if not t or not isinstance(t, str):
            return t
        s = re.sub(r"^#{1,6}\s*", "", t.strip())
        s = re.sub(r"\n#{1,6}\s*", "\n", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
        return re.sub(r"\*([^*]+)\*", r"\1", s).strip()

    def _get_main_img(self):
        return self.config["images"].get("main_article_image") or DEFAULT_MAIN_IMG

    def _get_ing_img(self):
        return self.config["images"].get("ingredient_image") or DEFAULT_ING_IMG

    def _xj(self, raw):
        if not raw:
            return {}
        text = raw.strip()
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

    def _normalize_secrets(self, raw):
        out = []
        items = None
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict):
            if isinstance(raw.get("secrets"), list):
                items = raw["secrets"]
        if items:
            for i, item in enumerate(items[:5]):
                if isinstance(item, dict):
                    out.append(
                        {
                            "title": str(item.get("title", f"Secret {i+1}")).strip(),
                            "body": self._strip_md(str(item.get("body", ""))),
                        }
                    )
        if isinstance(raw, dict):
            for k in ("secret_1", "secret_2", "secret_3", "secret_4", "secret_5"):
                if k in raw:
                    v = raw[k]
                    if isinstance(v, dict):
                        out.append(
                            {
                                "title": str(v.get("title", "")).strip() or k.replace("_", " ").title(),
                                "body": self._strip_md(str(v.get("body", ""))),
                            }
                        )
        out = out[:5]
        while len(out) < 5:
            n = len(out) + 1
            out.append({"title": f"Secret {n}", "body": ""})
        return out[:5]

    def _get_preview_content(self):
        t = self.title
        return {
            "intro": (
                f"Great {t} is less about fancy tools and more about a handful of habits "
                f"that professionals use every night. Below are five secrets that change how "
                f"the dish tastes—from how you season to when you pull it from the heat."
            ),
            "secrets": [
                {
                    "title": "Start with a screaming-hot pan",
                    "body": "Pat the meat dry and preheat your skillet until a drop of water skitters. "
                    "A proper sear builds flavor through Maillard browning before you even add butter.",
                },
                {
                    "title": "Salt early, but not all at once",
                    "body": "A light salt on both sides 15 minutes before cooking draws out surface moisture "
                    "you can blot away, which helps crust formation. Save a pinch to finish.",
                },
                {
                    "title": "Butter belongs at the end",
                    "body": "Garlic butter is for basting in the last minute, not frying from the start. "
                    "That keeps the milk solids golden instead of bitter.",
                },
                {
                    "title": "Use a thermometer, not guesswork",
                    "body": "For medium-rare, pull the steak around 125–130°F and let carryover cooking "
                    "do the rest while it rests on a warm plate.",
                },
                {
                    "title": "Rest before you slice",
                    "body": "Five to ten minutes under loose foil lets juices redistribute. "
                    "Cutting too soon floods the board instead of your plate.",
                },
            ],
            "why_it_works": (
                "High dry heat creates hundreds of new flavor compounds on the surface of the meat while "
                "the interior stays tender. Resting allows muscle fibers to relax so juices stay bound "
                "inside the slices instead of running out."
            ),
            "ingredient_list": [
                "2 ribeye steaks (1–1.25 inches thick)",
                "2 tbsp high-smoke-point oil (avocado or grapeseed)",
                "4 tbsp unsalted butter",
                "4 cloves garlic, smashed",
                "3 sprigs fresh thyme",
                "Kosher salt and black pepper",
                "Flaky sea salt for finishing",
            ],
            "steps": [
                {
                    "heading": "Dry and season",
                    "body": "Pat steaks dry with paper towels. Season both sides with kosher salt and pepper. "
                    "Let sit at room temperature for 20 minutes, then blot any surface moisture again.",
                },
                {
                    "heading": "Sear hard",
                    "body": "Heat oil in a cast-iron skillet over high heat until shimmering. "
                    "Lay steaks in and do not move for 2–3 minutes until a deep crust forms. Flip once.",
                },
                {
                    "heading": "Butter-baste",
                    "body": "Reduce heat to medium. Add butter, garlic, and thyme. Tilt the pan and spoon "
                    "foaming butter over the steaks for 1–2 minutes while monitoring internal temperature.",
                },
                {
                    "heading": "Rest and slice",
                    "body": "Transfer to a cutting board, tent loosely with foil, and rest 7–10 minutes. "
                    "Slice against the grain, finish with flaky salt, and serve with pan drippings.",
                },
            ],
            "faqs": [
                {
                    "question": "Can I use a stainless pan instead of cast iron?",
                    "answer": "Yes. Use a heavy-bottomed stainless skillet and the same high-heat approach. "
                    "Cast iron holds heat more evenly, but a good stainless pan works if it is fully preheated.",
                },
                {
                    "question": "What if I only have salted butter?",
                    "answer": "Use less kosher salt on the steak before cooking and skip extra salt in the "
                    "baste. Taste after resting and adjust with flaky salt at the end.",
                },
                {
                    "question": "How do I store leftovers?",
                    "answer": "Refrigerate sliced steak in an airtight container up to three days. "
                    "Reheat gently in a covered pan with a splash of broth to keep it moist.",
                },
            ],
            "recipe": {
                "name": t,
                "summary": f"Restaurant-style {t}: perfect sear, garlic-thyme butter, and juicy medium-rare slices.",
                "ingredients": [
                    "2 ribeye steaks (1–1.25 inches thick)",
                    "2 tbsp high-smoke-point oil",
                    "4 tbsp unsalted butter",
                    "4 cloves garlic, smashed",
                    "3 sprigs fresh thyme",
                    "Kosher salt and black pepper",
                    "Flaky sea salt",
                ],
                "instructions": [
                    "Dry steaks; salt and pepper; rest 20 min; blot dry.",
                    "Sear in hot oil 2–3 min per side for crust.",
                    "Baste with butter, garlic, thyme; target 125–130°F interior.",
                    "Rest 7–10 min; slice; finish with flaky salt.",
                ],
                "prep_time": "25 min",
                "cook_time": "12 min",
                "total_time": "40 min",
                "servings": "2",
                "calories": "680",
                "course": "Main Course",
                "cuisine": "American",
            },
        }

    def run_preview(self):
        cd = self._get_preview_content()
        from ai_client import get_first_category

        cat = get_first_category(self.config)
        recipe = cd["recipe"]
        sections = [
            {"key": "intro", "content": cd["intro"]},
            {"key": "secrets", "content": cd["secrets"]},
            {"key": "why_it_works", "content": cd["why_it_works"]},
            {"key": "ingredient_list", "content": cd["ingredient_list"]},
            {"key": "steps", "content": cd["steps"]},
            {"key": "faqs", "content": cd["faqs"]},
            {"key": "recipe", "content": recipe},
        ]
        content_data = {
            "title": self.title,
            "slug": self.slug,
            "categorieId": str(cat.get("id", 1)),
            "categorie": cat.get("categorie", "dinner"),
            "sections": sections,
            "article_html": "",
            "article_css": "",
            "recipe": recipe,
            "recipe_title_pin": self.title[:100],
            "pinterest_title": self.title[:100],
            "pinterest_description": f"Five kitchen secrets for the best {self.title}.",
            "pinterest_keywords": f"{self.title}, steak, cooking tips, recipe secrets",
            "focus_keyphrase": f"{self.title} secrets",
            "meta_description": f"Five pro secrets for perfect {self.title}, plus science, steps, and printable recipe."[
                :140
            ],
            "keyphrase_synonyms": f"best {self.title}, how to cook {self.title}",
            "main_image": self._get_main_img(),
            "ingredient_image": self._get_ing_img(),
            "prompt_midjourney_main": f"Sizzling ribeye in cast iron, {self.title}, dramatic steam, editorial food photo --v 6.1",
            "prompt_midjourney_ingredients": f"Raw ribeye, garlic, thyme, butter on slate board, {self.title} ingredients --v 6.1",
        }
        css = self.generate_css()
        html = self.generate_html(content_data["sections"])
        content_data["article_html"] = html
        content_data["article_css"] = css
        return content_data

    def generate_content(self):
        from ai_client import ai_chat, get_first_category

        schema_keys = [
            "intro",
            "secrets",
            "why_it_works",
            "ingredient_list",
            "step_1",
            "step_2",
            "step_3",
            "step_4",
            "faq_1",
            "faq_2",
            "faq_3",
            "recipe",
            "meta_description",
            "focus_keyphrase",
            "pinterest_title",
            "prompt_midjourney_main",
            "prompt_midjourney_ingredients",
        ]
        sys = (
            "You are a food editor who writes sharp, practical listicles. "
            "Return ONE JSON object. Plain text in strings. secrets must be an array of exactly 5 objects, "
            "each with title (~6 words) and body (~55 words). faq_1, faq_2, faq_3 are objects with question and answer."
        )
        user = (
            f"Recipe article: '{self.title}'. Keys: {json.dumps(schema_keys)}. "
            f"secrets: exactly 5 {{title, body}} items—real cooking secrets, not filler. "
            f"why_it_works: ~70 words on food science. step_1..step_4: {{heading, body}}. "
            f"recipe: full card with ingredients, instructions, times, servings, course, cuisine."
        )
        raw = ai_chat(self, user, max_tokens=4500, system=sys)
        d = self._xj(raw)

        if d:
            print("[*] generator-20 — single JSON.")
            intro = self._strip_md(str(d.get("intro", "")))
            secrets = self._normalize_secrets(d.get("secrets"))
            why_it_works = self._strip_md(str(d.get("why_it_works", "")))
            ing_list = [str(x).strip() for x in (d.get("ingredient_list") or [])[:14]]
            steps_raw = [d.get("step_1"), d.get("step_2"), d.get("step_3"), d.get("step_4")]
            steps = []
            for i, s in enumerate(steps_raw):
                if isinstance(s, dict):
                    steps.append(
                        {
                            "heading": str(s.get("heading", f"Step {i+1}")).strip(),
                            "body": self._strip_md(str(s.get("body", ""))),
                        }
                    )
                else:
                    steps.append({"heading": f"Step {i+1}", "body": self._strip_md(str(s or ""))})
            while len(steps) < 4:
                steps.append({"heading": f"Step {len(steps)+1}", "body": ""})
            faqs = []
            for fk in ("faq_1", "faq_2", "faq_3"):
                fq = d.get(fk)
                if isinstance(fq, dict):
                    faqs.append(
                        {
                            "question": str(fq.get("question", "")).strip(),
                            "answer": self._strip_md(str(fq.get("answer", ""))),
                        }
                    )
            recipe = d.get("recipe") or {}
        else:
            print("[*] generator-20 — sequential fallback.")
            intro = self._strip_md(
                (ai_chat(self, f"Write a 120-word hook intro for '{self.title}' as five kitchen secrets article.", 280) or "")
            )
            why_it_works = self._strip_md(
                (
                    ai_chat(
                        self,
                        f"In ~70 words explain why the main techniques for {self.title} work (science, plain text).",
                        200,
                    )
                    or ""
                )
            )
            secrets = []
            for i in range(1, 6):
                block = ai_chat(
                    self,
                    f"Secret {i} for {self.title}: return JSON {{\"title\": \"...\", \"body\": \"~55 words\"}} only.",
                    180,
                )
                parsed = self._xj(block or "{}")
                if isinstance(parsed, dict) and parsed.get("title"):
                    secrets.append(
                        {
                            "title": str(parsed.get("title", "")).strip(),
                            "body": self._strip_md(str(parsed.get("body", ""))),
                        }
                    )
                else:
                    secrets.append({"title": f"Secret {i}", "body": self._strip_md(block or "")})
            secrets = self._normalize_secrets(secrets)
            raw_ing = ai_chat(self, f"List 8–14 ingredients with measurements for {self.title}. One per line.", 240)
            ing_list = [l.strip() for l in (raw_ing or "").splitlines() if l.strip()][:14]
            steps = []
            for i in range(1, 5):
                s = ai_chat(
                    self,
                    f"Step {i} for {self.title}: HEADING: ... BODY: ~65 words. Plain text.",
                    200,
                )
                h, b = f"Step {i}", s or ""
                for line in (s or "").splitlines():
                    lu = line.strip().upper()
                    if lu.startswith("HEADING:"):
                        h = line.split(":", 1)[-1].strip()
                    elif lu.startswith("BODY:"):
                        b = line.split(":", 1)[-1].strip()
                steps.append({"heading": h, "body": self._strip_md(b)})
            faqs = []
            for i in range(1, 4):
                q = ai_chat(self, f"One FAQ question about {self.title} (one line).", 80) or f"Question {i}"
                a = ai_chat(self, f"Answer in ~50 words: {q}", 150) or ""
                faqs.append({"question": q.strip(), "answer": self._strip_md(a)})
            recipe = {}
            d = {}

        if not isinstance(recipe, dict):
            recipe = {}
        for k, dv in [
            ("name", self.title),
            ("summary", "A flavorful recipe with pro techniques."),
            ("ingredients", ing_list),
            ("instructions", [s.get("body", "") for s in steps]),
            ("prep_time", "20 min"),
            ("cook_time", "25 min"),
            ("total_time", "45 min"),
            ("servings", "4"),
            ("calories", ""),
            ("course", "Main Course"),
            ("cuisine", "American"),
        ]:
            recipe.setdefault(k, dv)

        cat = get_first_category(self.config)
        mj_m = str(d.get("prompt_midjourney_main", "") or "").strip() if d else ""
        mj_i = str(d.get("prompt_midjourney_ingredients", "") or "").strip() if d else ""

        sections = [
            {"key": "intro", "content": intro},
            {"key": "secrets", "content": secrets},
            {"key": "why_it_works", "content": why_it_works},
            {"key": "ingredient_list", "content": ing_list},
            {"key": "steps", "content": steps},
            {"key": "faqs", "content": faqs},
            {"key": "recipe", "content": recipe},
        ]
        return {
            "title": self.title,
            "slug": self.slug,
            "categorieId": str(cat.get("id", 1)),
            "categorie": cat.get("categorie", "dinner"),
            "sections": sections,
            "article_html": "",
            "article_css": "",
            "prompt_used": f"generator-20 / title: {self.title}",
            "recipe": recipe,
            "recipe_title_pin": (str(d.get("pinterest_title", self.title)) or self.title)[:100] if d else self.title[:100],
            "pinterest_title": (str(d.get("pinterest_title", "")) or self.title)[:100] if d else self.title[:100],
            "pinterest_description": f"Five kitchen secrets for the best {self.title}.",
            "pinterest_keywords": f"{self.title}, cooking tips, recipe",
            "focus_keyphrase": str(d.get("focus_keyphrase", self.title.lower())) if d else self.title.lower(),
            "meta_description": (str(d.get("meta_description", "")) or f"Unlock five secrets for perfect {self.title}.")[:140]
            if d
            else f"Unlock five secrets for perfect {self.title}."[:140],
            "keyphrase_synonyms": f"{self.title} tips, best {self.title}",
            "main_image": self._get_main_img(),
            "ingredient_image": self._get_ing_img(),
            "prompt_midjourney_main": mj_m if mj_m and "--v 6.1" in mj_m else f"Editorial food photo, {self.title}, warm light --v 6.1",
            "prompt_midjourney_ingredients": mj_i
            if mj_i and "--v 6.1" in mj_i
            else f"Ingredient flat-lay for {self.title}, marble, natural light --v 6.1",
        }

    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url

        c = self.config["colors"]
        f = self.config["fonts"]
        l = self.config["layout"]
        comp = self.config.get("components") or CONFIG["components"]
        sc = (comp.get("secret_card") if isinstance(comp.get("secret_card"), dict) else None) or CONFIG["components"][
            "secret_card"
        ]
        sb = (comp.get("science_box") if isinstance(comp.get("science_box"), dict) else None) or CONFIG["components"][
            "science_box"
        ]
        rc = (comp.get("recipe_card") if isinstance(comp.get("recipe_card"), dict) else None) or CONFIG["components"][
            "recipe_card"
        ]
        nl = (comp.get("numbered_list") if isinstance(comp.get("numbered_list"), dict) else None) or CONFIG["components"][
            "numbered_list"
        ]
        iu = build_font_import_url(f)
        bf = font_family_css(f["body"]["family"], "sans-serif")
        hf = font_family_css(f["heading"]["family"], "serif")
        media = "@media(max-width:600px){.g20-secret{flex-direction:column}.recipe-card-buttons{flex-direction:column}h1{font-size:1.65rem}}"

        nb = sc.get("number_bg", "#FDF6F3")
        ab = sc.get("accent_border", "#D4A574")

        return f"""/* generator-20 | Five Kitchen Secrets | white background */
@import url('{iu}');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{c['background']};color:{c['text_primary']};font-family:{bf};font-size:{f['body']['size']};line-height:{f['body']['line_height']};-webkit-font-smoothing:antialiased}}
.article-container{{max-width:{l['max_width']};margin:2rem auto;padding:{l['container_padding']};background:{c['container_bg']};border-radius:{l['border_radius']};box-shadow:{l['box_shadow']}}}
.g20-eyebrow{{display:inline-block;font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;color:{c['primary']};font-weight:700;margin-bottom:0.5rem;border-bottom:2px solid {c['secondary']};padding-bottom:0.2rem}}
.g20-header{{margin-bottom:{l['section_spacing']}}}
.g20-header .article-title{{font-family:{hf};font-size:{f['heading']['sizes']['h1']};color:{c['text_primary']};line-height:1.2;margin-bottom:0.35rem}}
.g20-header .byline{{font-size:0.85rem;color:{c['text_secondary']}}}
h2{{font-family:{hf};font-size:{f['heading']['sizes']['h2']};color:{c['text_primary']};margin-top:{l['section_spacing']};margin-bottom:0.65rem}}
p{{color:{c['text_secondary']};margin-bottom:{l['paragraph_spacing']}}}
.g20-secrets{{display:flex;flex-direction:column;gap:1rem;margin:{l['section_spacing']} 0}}
.g20-secret{{display:flex;gap:1rem;align-items:flex-start;padding:1.1rem 1.2rem;border:1px solid {c['border']};border-radius:{l['border_radius']};border-left:4px solid {ab};background:{nb}}}
.g20-secret-num{{flex-shrink:0;width:36px;height:36px;border-radius:50%;background:{c['primary']};color:#fff;font-weight:700;font-size:0.95rem;display:flex;align-items:center;justify-content:center;font-family:{hf}}}
.g20-secret-title{{font-family:{hf};font-size:1.05rem;color:{c['text_primary']};margin:0 0 0.35rem}}
.g20-secret p{{margin:0;font-size:0.95rem}}
.g20-science{{background:{sb['bg_color']};border-left:{sb['border_left']};padding:1.1rem 1.35rem;margin:{l['section_spacing']} 0;border-radius:0 10px 10px 0}}
.g20-science h3{{font-family:{hf};font-size:1rem;color:{c['primary']};margin:0 0 0.5rem}}
.g20-science p{{margin:0;color:{c['text_secondary']};font-size:0.95rem}}
.hero-image{{width:100%;border-radius:{l['border_radius']};margin:1rem 0;object-fit:cover;max-height:420px;display:block}}
.ingredient-image{{width:100%;border-radius:{l['border_radius']};margin:1rem 0;object-fit:cover;max-height:340px;display:block}}
.ingredient-list{{list-style:none;padding:0;margin:0.5rem 0}}
.ingredient-list li{{padding:0.4rem 0 0.4rem 1.4rem;position:relative;color:{c['text_secondary']};border-bottom:1px solid {c['border']}}}
.ingredient-list li:last-child{{border-bottom:none}}
.ingredient-list li::before{{content:'\\2022';position:absolute;left:0;color:{c['list_marker']};font-weight:700;font-size:1.1rem;line-height:1.2}}
.steps-list{{margin:{l['section_spacing']} 0}}
.step-item{{display:flex;gap:1rem;margin-bottom:1.2rem}}
.step-num{{flex-shrink:0;width:{nl['circle_size']};height:{nl['circle_size']};border-radius:50%;background:{nl['circle_bg']};color:{nl['circle_color']};font-weight:700;display:flex;align-items:center;justify-content:center;font-size:0.9rem}}
.step-body h3{{margin:0 0 0.25rem;font-size:1rem;color:{c['text_primary']}}}
.step-body p{{margin:0;font-size:0.95rem}}
.g20-faqs{{margin:{l['section_spacing']} 0}}
.g20-faq{{padding:0.85rem 0;border-bottom:1px dotted {c['border']}}}
.g20-faq:last-child{{border-bottom:none}}
.g20-faq-q{{font-family:{hf};font-size:0.95rem;color:{c['text_primary']};margin:0 0 0.35rem}}
.g20-faq p{{margin:0;font-size:0.92rem}}
.recipe-card{{background:{rc['bg']};border:{rc['border']};border-radius:{rc['border_radius']};padding:{rc['padding']};margin:{l['section_spacing']} 0}}
.recipe-card-header h2{{margin:0 0 0.5rem;font-size:1.3rem;font-family:{hf}}}
.recipe-card-image{{width:100%;height:210px;object-fit:cover;border-radius:{l['border_radius']};display:block;margin-bottom:1rem}}
.recipe-meta{{display:flex;flex-wrap:wrap;gap:0.75rem;margin:0.75rem 0;padding:0.75rem 0;border-top:1px solid {c['border']};border-bottom:1px solid {c['border']}}}
.recipe-meta-item{{font-size:0.85rem;color:{c['text_secondary']}}}
.recipe-meta-item strong{{color:{c['text_primary']};margin-right:0.25rem}}
.recipe-card-buttons{{display:flex;gap:0.6rem;margin:0.75rem 0}}
.btn-print,.btn-pin{{flex:1;color:#fff;border:none;padding:0.65rem 0.9rem;border-radius:{l['border_radius']};cursor:pointer;font-weight:600;font-size:0.85rem}}
.btn-print{{background:{c['button_print']}}}.btn-print:hover{{background:{c['button_hover_print']}}}
.btn-pin{{background:{c['button_pin']}}}.btn-pin:hover{{background:{c['button_hover_pin']}}}
.recipe-ingredients-list,.recipe-instructions-list{{list-style:none;padding:0}}
.recipe-ingredients-list li{{padding:0.3rem 0 0.3rem 1.2rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}
.recipe-ingredients-list li:last-child{{border-bottom:none}}
.recipe-ingredients-list li::before{{content:'\\2713';position:absolute;left:0;color:{c['list_marker']};font-weight:700}}
.recipe-instructions-list li{{counter-increment:r20;padding:0.5rem 0 0.5rem 2.2rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}
.recipe-instructions-list li:last-child{{border-bottom:none}}
.recipe-instructions-list{{counter-reset:r20}}
.recipe-instructions-list li::before{{content:counter(r20);position:absolute;left:0;top:0.35rem;width:22px;height:22px;background:{nl['circle_bg']};color:{nl['circle_color']};border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.75rem}}
{media}"""

    def generate_html(self, sections, css_filename="css.css"):
        t = self.title
        main_img = _e(self._get_main_img(), attr=True)
        ing_img = _e(self._get_ing_img(), attr=True)
        card_img = _e(self.config["images"].get("recipe_card_image") or self._get_main_img(), attr=True)
        sec = {s["key"]: s["content"] for s in sections}

        intro = sec.get("intro", "")
        secrets = sec.get("secrets") or []
        if not isinstance(secrets, list):
            secrets = []
        why_it_works = sec.get("why_it_works", "")
        ing_list = sec.get("ingredient_list", [])
        if not isinstance(ing_list, list):
            ing_list = []
        steps = sec.get("steps", [])
        if not isinstance(steps, list):
            steps = []
        faqs = sec.get("faqs", [])
        if not isinstance(faqs, list):
            faqs = []
        recipe = sec.get("recipe") or {}
        if not isinstance(recipe, dict):
            recipe = {}
        r = {
            **{
                "name": t,
                "prep_time": "15 min",
                "cook_time": "45 min",
                "total_time": "60 min",
                "servings": "4",
                "calories": "",
                "ingredients": [],
                "instructions": [],
                "summary": "",
            },
            **recipe,
        }

        secret_blocks = []
        for i, item in enumerate(secrets[:5], 1):
            if not isinstance(item, dict):
                continue
            title = _e(item.get("title", f"Secret {i}"))
            body = _e(item.get("body", ""))
            secret_blocks.append(
                f'<article class="g20-secret"><span class="g20-secret-num">{i}</span><div>'
                f'<h3 class="g20-secret-title">{title}</h3><p>{body}</p></div></article>'
            )
        secrets_html = "\n".join(secret_blocks) if secret_blocks else ""

        il = "".join(f"<li>{_e(x)}</li>\n" for x in ing_list)
        sl = "".join(
            f'<div class="step-item"><span class="step-num">{i + 1}</span><div class="step-body">'
            f"<h3>{_e(st.get('heading', f'Step {i+1}'))}</h3><p>{_e(st.get('body', ''))}</p></div></div>\n"
            for i, st in enumerate(steps)
            if isinstance(st, dict)
        )
        ri = "".join(f"<li>{_e(x)}</li>\n" for x in r.get("ingredients", []))
        ris = "".join(
            f"<li>{_e(x)}</li>\n"
            for x in r.get("instructions", [st.get("body", "") for st in steps if isinstance(st, dict)])
        )

        faq_blocks = []
        for fq in faqs[:5]:
            if not isinstance(fq, dict):
                continue
            faq_blocks.append(
                f'<div class="g20-faq"><h3 class="g20-faq-q">{_e(fq.get("question", ""))}</h3>'
                f'<p>{_e(fq.get("answer", ""))}</p></div>'
            )
        faqs_html = "\n".join(faq_blocks)

        te = _e(t)
        rname = _e(r.get("name", t))

        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{te}</title><link rel="stylesheet" href="{_e(css_filename, attr=True)}">
<!-- inject:head-end --></head>
<body>
<div class="article-container">
<header class="g20-header">
  <span class="g20-eyebrow">Recipe deep dive</span>
  <h1 class="article-title">Five Kitchen Secrets: {te}</h1>
  <div class="byline">By <span class="article-author"></span> &middot; <span class="article-date"></span></div>
</header>

<img src="{main_img}" alt="{te}" class="hero-image">
<!-- inject:after-hero -->

<p>{_e(intro)}</p>

<h2>Five secrets</h2>
<div class="g20-secrets">
{secrets_html}
</div>

<div class="g20-science">
  <h3>Why it works</h3>
  <p>{_e(why_it_works)}</p>
</div>

<h2>Ingredients</h2>
<img src="{ing_img}" alt="Ingredients for {te}" class="ingredient-image">
<ul class="ingredient-list">
{il}</ul>

<h2>Instructions</h2>
<div class="steps-list">
{sl}</div>

<h2>Your questions</h2>
<div class="g20-faqs">
{faqs_html}
</div>

<!-- inject:before-recipe -->
<div class="recipe-card" id="recipe-card">
  <img src="{card_img}" alt="{rname}" class="recipe-card-image">
  <div class="recipe-card-header"><h2>{rname}</h2><p>{_e(r.get("summary", ""))}</p></div>
  <div class="recipe-meta">
    <div class="recipe-meta-item"><strong>Prep:</strong> {_e(r.get("prep_time", ""))}</div>
    <div class="recipe-meta-item"><strong>Cook:</strong> {_e(r.get("cook_time", ""))}</div>
    <div class="recipe-meta-item"><strong>Total:</strong> {_e(r.get("total_time", ""))}</div>
    <div class="recipe-meta-item"><strong>Servings:</strong> {_e(r.get("servings", ""))}</div>
  </div>
  <div class="recipe-card-buttons">
    <button class="btn-print" onclick="window.print()">Print</button>
    <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent(document.querySelector('.hero-image')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin</button>
  </div>
  <h3>Ingredients</h3><ul class="recipe-ingredients-list">{ri}</ul>
  <h3>Instructions</h3><ol class="recipe-instructions-list">{ris}</ol>
</div>
<!-- inject:article-end -->
</div>
</body></html>"""

    def run(self, return_content_only=False):
        if not self.title:
            self.title = CONFIG["title"]
            self.slug = self._slugify(self.title)
        cd = self.generate_content()
        css = self.generate_css()
        html = self.generate_html(cd["sections"])
        cd["article_html"] = html
        cd["article_css"] = css
        if return_content_only:
            return cd
        os.makedirs(self.slug, exist_ok=True)
        with open(os.path.join(self.slug, "content.json"), "w", encoding="utf-8") as fh:
            json.dump(cd, fh, indent=2)
        with open(os.path.join(self.slug, "article.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
        with open(os.path.join(self.slug, "css.css"), "w", encoding="utf-8") as fh:
            fh.write(css)
        print("[OK] Saved to: {}/".format(self.slug))
        return cd


if __name__ == "__main__":
    gen = ArticleGenerator({"title": "Cast-Iron Skillet Ribeye with Garlic Butter"})
    gen.run()
