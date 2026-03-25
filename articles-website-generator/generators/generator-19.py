"""
generator-19.py — Comparison / Guide Style
------------------------------------------
"How to Make the Best X" format: intro with tips for choosing ingredients,
comparison/guide section, ingredient image, 4 steps, simple recipe card.
Light sage/olive palette. White background only. Uses default R2 images for preview.
"""

import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

DEFAULT_MAIN_IMG = "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/main_image/5c3d26dc/9d4e2053736.png"
DEFAULT_ING_IMG = "https://pub-265e755dc4334724956a9d45d1c8bfb0.r2.dev/ingredient_image/aab89f7d/5d8abbf671e.png"

CONFIG = {
    "title": "Lemon Herb Roast Chicken",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary": "#6B7C5C", "secondary": "#8B9B7A", "accent": "#A8B89A",
        "background": "#ffffff", "container_bg": "#ffffff", "border": "#D4DDCC",
        "text_primary": "#2A3324", "text_secondary": "#4A5540",
        "button_print": "#6B7C5C", "button_pin": "#E60023",
        "button_hover_print": "#5A6B4C", "button_hover_pin": "#FF1A3C",
        "link": "#6B7C5C", "list_marker": "#6B7C5C",
        "tips_bg": "#F5F8F2", "tips_border": "#A8B89A",
    },
    "fonts": {
        "heading": {"family": "Merriweather", "weights": [600, 700], "sizes": {"h1": "2rem", "h2": "1.4rem", "h3": "1.1rem"}},
        "body": {"family": "Open Sans", "weight": 400, "size": "1rem", "line_height": 1.7},
    },
    "layout": {
        "max_width": "700px", "section_spacing": "1.75rem",
        "paragraph_spacing": "0.9rem", "list_spacing": "0.45rem",
        "container_padding": "1.75rem", "border_radius": "8px",
        "box_shadow": "0 2px 10px rgba(107,124,92,0.06)",
    },
    "components": {
        "numbered_list": {"style": "circle", "circle_bg": "#6B7C5C", "circle_color": "#fff", "circle_size": "28px"},
        "bullet_list": {"style": "disc", "color": "#6B7C5C"},
        "tips_box": {"bg_color": "#F5F8F2", "border_left": "4px solid #8B9B7A", "padding": "1rem 1.25rem"},
        "recipe_card": {"bg": "#ffffff", "border": "1px solid #D4DDCC", "border_radius": "8px", "padding": "1.25rem",
                       "meta_icon_color": "#6B7C5C"},
    },
    "images": {
        "main_article_image": DEFAULT_MAIN_IMG,
        "ingredient_image": DEFAULT_ING_IMG,
        "recipe_card_image": "",
    },
    "structure_template": {"word_counts": {"intro": 100, "guide_tips": 80, "step": 55}},
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
        self.title = (self.config["title"] or "Lemon Herb Roast Chicken").strip()
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
        s = re.sub(r'^#{1,6}\s*', '', t.strip())
        s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        return re.sub(r'\*([^*]+)\*', r'\1', s).strip()

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

    def _get_preview_content(self):
        """Fake content for preview — see final result without AI."""
        t = self.title
        return {
            "intro": f"Making the best {t} starts with choosing the right ingredients and understanding a few key techniques. This guide walks you through everything you need to know — from picking the perfect bird to achieving crisp, golden skin and juicy meat. Whether you're cooking for Sunday dinner or a special occasion, this recipe delivers every time.",
            "guide_tips": "Choose a 4-5 lb bird for even roasting. Organic or free-range birds tend to have better flavor. Bring the chicken to room temperature for 30 minutes before roasting — this helps it cook evenly. A meat thermometer is essential: the breast should reach 165°F and the thighs 175°F. Rest the chicken for 15 minutes before carving so the juices redistribute.",
            "ingredient_list": [
                "1 whole chicken (4-5 lbs)",
                "2 lemons, halved",
                "4 cloves garlic, smashed",
                "2 tbsp olive oil",
                "1 tbsp fresh rosemary, chopped",
                "1 tbsp fresh thyme, chopped",
                "1 tsp kosher salt",
                "1/2 tsp black pepper",
                "1 small onion, quartered",
            ],
            "steps": [
                {"heading": "Prep the Chicken", "body": "Pat the chicken dry with paper towels. Rub the olive oil all over the skin. Season generously with salt and pepper, then stuff the cavity with lemon halves, garlic, and onion. Tie the legs together with kitchen twine if desired."},
                {"heading": "Add the Herbs", "body": "Slide your fingers under the skin over the breast to loosen it. Spread half of the rosemary and thyme under the skin, and sprinkle the rest over the outside. Place the chicken breast-side up on a roasting rack in a pan."},
                {"heading": "Roast to Perfection", "body": "Roast at 425°F for 15 minutes, then reduce heat to 375°F. Continue roasting until the thickest part of the thigh reads 175°F, about 60-75 minutes total. Baste with pan juices halfway through."},
                {"heading": "Rest and Serve", "body": "Transfer the chicken to a cutting board and tent with foil. Let rest for 15 minutes. Carve and serve with the pan drippings, extra lemon wedges, and your favorite sides."},
            ],
            "recipe": {
                "name": t,
                "summary": f"Juicy, herb-infused {t} with crisp skin and bright lemon flavor. A classic that never disappoints.",
                "ingredients": [
                    "1 whole chicken (4-5 lbs)",
                    "2 lemons, halved",
                    "4 cloves garlic, smashed",
                    "2 tbsp olive oil",
                    "1 tbsp fresh rosemary, chopped",
                    "1 tbsp fresh thyme, chopped",
                    "1 tsp kosher salt",
                    "1/2 tsp black pepper",
                ],
                "instructions": [
                    "Pat chicken dry. Rub with oil, salt, pepper. Stuff with lemon, garlic, onion.",
                    "Loosen breast skin; add herbs under and over skin.",
                    "Roast at 425°F for 15 min, then 375°F until thigh reaches 175°F.",
                    "Rest 15 min. Carve and serve with pan drippings.",
                ],
                "prep_time": "15 min", "cook_time": "75 min",
                "total_time": "90 min", "servings": "6",
                "calories": "320", "course": "Main Course", "cuisine": "American",
            },
        }

    def run_preview(self):
        """Generate preview with fake content and default images."""
        cd = self._get_preview_content()
        from ai_client import get_first_category
        cat = get_first_category(self.config)
        recipe = cd["recipe"]
        sections = [
            {"key": "intro", "content": cd["intro"]},
            {"key": "guide_tips", "content": cd["guide_tips"]},
            {"key": "ingredient_list", "content": cd["ingredient_list"]},
            {"key": "steps", "content": cd["steps"]},
            {"key": "recipe", "content": recipe},
        ]
        content_data = {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "recipe": recipe,
            "recipe_title_pin": self.title[:100],
            "pinterest_title": self.title[:100],
            "pinterest_description": f"How to make the best {self.title}. A complete guide with tips.",
            "pinterest_keywords": f"{self.title}, roast chicken, dinner, recipe guide",
            "focus_keyphrase": f"best {self.title}",
            "meta_description": f"How to make the best {self.title}. Step-by-step guide with expert tips."[:140],
            "keyphrase_synonyms": f"perfect {self.title}, {self.title} recipe",
            "main_image": self._get_main_img(),
            "ingredient_image": self._get_ing_img(),
            "prompt_midjourney_main": f"Roast chicken photography, {self.title}, golden crispy skin --v 6.1",
            "prompt_midjourney_ingredients": f"Fresh herbs and lemon ingredients flat-lay, {self.title} --v 6.1",
        }
        css = self.generate_css()
        html = self.generate_html(content_data["sections"])
        content_data["article_html"] = html
        content_data["article_css"] = css
        return content_data

    def generate_content(self):
        from ai_client import ai_chat, get_first_category
        schema = {
            "intro": "string ~100 words — how to make the best X, what makes this recipe stand out",
            "guide_tips": "string ~80 words — tips for choosing ingredients, technique notes, what to look for",
            "ingredient_list": "array of 8–12 strings with measurements",
            "step_1": "object with heading and body (~55 words each)",
            "step_2": "object with heading and body (~55 words each)",
            "step_3": "object with heading and body (~55 words each)",
            "step_4": "object with heading and body (~55 words each)",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine",
            "meta_description": "120–140 chars",
            "focus_keyphrase": "string",
            "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        sys = "You are a cooking guide writer. Generate a 'how to make the best X' style article as ONE JSON. Practical, informative. Plain text. All about the recipe title."
        user = f"Generate a comparison/guide style recipe article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=4000, system=sys)
        d = self._xj(raw)

        if d:
            print("[*] Guide — single-JSON.")
            intro = self._strip_md(str(d.get("intro", "")))
            guide_tips = self._strip_md(str(d.get("guide_tips", "")))
            ing_list = [str(x).strip() for x in (d.get("ingredient_list") or [])[:12]]
            steps_raw = [d.get("step_1"), d.get("step_2"), d.get("step_3"), d.get("step_4")]
            steps = []
            for i, s in enumerate(steps_raw):
                if isinstance(s, dict):
                    steps.append({
                        "heading": str(s.get("heading", f"Step {i+1}")).strip(),
                        "body": self._strip_md(str(s.get("body", ""))),
                    })
                else:
                    steps.append({"heading": f"Step {i+1}", "body": self._strip_md(str(s or ""))})
            while len(steps) < 4:
                steps.append({"heading": f"Step {len(steps)+1}", "body": ""})
            recipe = d.get("recipe") or {}
        else:
            print("[*] Guide — sequential fallback.")
            intro = self._strip_md((ai_chat(self, f"Write a 100-word intro for 'how to make the best {self.title}'. Practical. Plain text.", 240) or ""))
            guide_tips = self._strip_md((ai_chat(self, f"Write 80 words of guide tips for {self.title}: choosing ingredients, technique. Plain text.", 200) or ""))
            raw = ai_chat(self, f"List 8–12 ingredients for {self.title} with measurements. One per line.", 220)
            ing_list = [l.strip() for l in (raw or "").splitlines() if l.strip()][:12]
            steps = []
            for i in range(1, 5):
                s = ai_chat(self, f"Write step {i} for {self.title} as HEADING: <title> BODY: <55 words>. Plain text.", 160)
                h, b = f"Step {i}", s or ""
                for line in (s or "").splitlines():
                    if line.strip().upper().startswith("HEADING:"):
                        h = line.split(":", 1)[-1].strip()
                    elif line.strip().upper().startswith("BODY:"):
                        b = line.split(":", 1)[-1].strip()
                steps.append({"heading": h, "body": self._strip_md(b)})
            recipe = {}

        if not isinstance(recipe, dict):
            recipe = {}
        for k, dv in [("name", self.title), ("summary", "A complete guide."), ("ingredients", ing_list),
                      ("instructions", [s.get("body", "") for s in steps]),
                      ("prep_time", "15 min"), ("cook_time", "45 min"), ("total_time", "60 min"),
                      ("servings", "4"), ("calories", ""), ("course", "Main Course"), ("cuisine", "American")]:
            recipe.setdefault(k, dv)

        cat = get_first_category(self.config)
        mj_m = str(d.get("prompt_midjourney_main", "") or "").strip() if d else ""
        mj_i = str(d.get("prompt_midjourney_ingredients", "") or "").strip() if d else ""

        sections = [
            {"key": "intro", "content": intro},
            {"key": "guide_tips", "content": guide_tips},
            {"key": "ingredient_list", "content": ing_list},
            {"key": "steps", "content": steps},
            {"key": "recipe", "content": recipe},
        ]
        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": f"generator-19 / title: {self.title}",
            "recipe": recipe,
            "recipe_title_pin": (str(d.get("pinterest_title", self.title)) or self.title)[:100] if d else self.title[:100],
            "pinterest_title": (str(d.get("pinterest_title", "")) or self.title)[:100] if d else self.title[:100],
            "pinterest_description": f"How to make the best {self.title}.",
            "pinterest_keywords": f"{self.title}, recipe guide, how to make",
            "focus_keyphrase": str(d.get("focus_keyphrase", self.title.lower())) if d else self.title.lower(),
            "meta_description": (str(d.get("meta_description", "")) or f"How to make the best {self.title}.")[:140] if d else f"How to make the best {self.title}."[:140],
            "keyphrase_synonyms": f"best {self.title}, perfect {self.title}",
            "main_image": self._get_main_img(),
            "ingredient_image": self._get_ing_img(),
            "prompt_midjourney_main": mj_m if mj_m and "--v 6.1" in mj_m else f"Food photography of {self.title} --v 6.1",
            "prompt_midjourney_ingredients": mj_i if mj_i and "--v 6.1" in mj_i else f"Ingredients for {self.title} flat-lay --v 6.1",
        }

    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url
        c = self.config["colors"]
        f = self.config["fonts"]
        l = self.config["layout"]
        comp = self.config.get("components") or CONFIG["components"]
        tb = (comp.get("tips_box") if isinstance(comp.get("tips_box"), dict) else None) or CONFIG["components"]["tips_box"]
        rc = (comp.get("recipe_card") if isinstance(comp.get("recipe_card"), dict) else None) or CONFIG["components"]["recipe_card"]
        nl = (comp.get("numbered_list") if isinstance(comp.get("numbered_list"), dict) else None) or CONFIG["components"]["numbered_list"]
        iu = build_font_import_url(f)
        bf = font_family_css(f["body"]["family"], "sans-serif")
        hf = font_family_css(f["heading"]["family"], "serif")
        media = "@media(max-width:600px){.recipe-card-buttons{flex-direction:column}h1{font-size:1.6rem}}"

        return f"""/* generator-19 | Comparison/Guide Style | white background */
@import url('{iu}');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{c['background']};color:{c['text_primary']};font-family:{bf};font-size:{f['body']['size']};line-height:{f['body']['line_height']};-webkit-font-smoothing:antialiased}}
.article-container{{max-width:{l['max_width']};margin:2rem auto;padding:{l['container_padding']};background:{c['container_bg']};border-radius:{l['border_radius']};box-shadow:{l['box_shadow']}}}
.g19-header{{margin-bottom:{l['section_spacing']}}}
.g19-header .article-title{{font-family:{hf};font-size:{f['heading']['sizes']['h1']};color:{c['text_primary']};margin-bottom:0.3rem}}
.g19-header .byline{{font-size:0.85rem;color:{c['text_secondary']}}}
h2{{font-family:{hf};font-size:{f['heading']['sizes']['h2']};color:{c['text_primary']};margin-top:{l['section_spacing']};margin-bottom:0.5rem}}
p{{color:{c['text_secondary']};margin-bottom:{l['paragraph_spacing']}}}
.guide-tips-box{{background:{tb['bg_color']};border-left:{tb['border_left']};padding:{tb['padding']};margin:{l['section_spacing']} 0;border-radius:0 8px 8px 0;color:{c['text_primary']}}}
.guide-tips-box h3{{margin:0 0 0.5rem;font-size:1rem;color:{c['primary']}}}
.hero-image{{width:100%;border-radius:{l['border_radius']};margin:1rem 0;object-fit:cover;max-height:400px;display:block}}
.ingredient-image{{width:100%;border-radius:{l['border_radius']};margin:1rem 0;object-fit:cover;max-height:320px;display:block}}
.ingredient-list{{list-style:none;padding:0;margin:0.5rem 0}}
.ingredient-list li{{padding:0.4rem 0 0.4rem 1.4rem;position:relative;color:{c['text_secondary']};border-bottom:1px solid {c['border']}}}
.ingredient-list li:last-child{{border-bottom:none}}
.ingredient-list li::before{{content:'\\2713';position:absolute;left:0;color:{c['list_marker']};font-weight:700}}
.steps-list{{margin:{l['section_spacing']} 0}}
.step-item{{display:flex;gap:1rem;margin-bottom:1.1rem}}
.step-num{{flex-shrink:0;width:{nl['circle_size']};height:{nl['circle_size']};border-radius:50%;background:{nl['circle_bg']};color:{nl['circle_color']};font-weight:700;display:flex;align-items:center;justify-content:center;font-size:0.85rem}}
.step-body h3{{margin:0 0 0.2rem;font-size:1rem;color:{c['text_primary']}}}
.step-body p{{margin:0;font-size:0.94rem}}
.recipe-card{{background:{rc['bg']};border:{rc['border']};border-radius:{rc['border_radius']};padding:{rc['padding']};margin:{l['section_spacing']} 0}}
.recipe-card-header h2{{margin:0 0 0.5rem;font-size:1.25rem}}
.recipe-card-image{{width:100%;height:200px;object-fit:cover;border-radius:{l['border_radius']};display:block;margin-bottom:1rem}}
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
.recipe-instructions-list li{{counter-increment:rstep;padding:0.5rem 0 0.5rem 2.2rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}
.recipe-instructions-list li:last-child{{border-bottom:none}}
.recipe-instructions-list{{counter-reset:rstep}}
.recipe-instructions-list li::before{{content:counter(rstep);position:absolute;left:0;top:0.35rem;width:22px;height:22px;background:{nl['circle_bg']};color:{nl['circle_color']};border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.75rem}}
{media}"""

    def generate_html(self, sections, css_filename="css.css"):
        t = self.title
        main_img = self._get_main_img()
        ing_img = self._get_ing_img()
        card_img = self.config["images"].get("recipe_card_image") or main_img
        sec = {s["key"]: s["content"] for s in sections}

        intro = sec.get("intro", "")
        guide_tips = sec.get("guide_tips", "")
        ing_list = sec.get("ingredient_list", [])
        steps = sec.get("steps", [])
        recipe = sec.get("recipe") or {}
        if not isinstance(recipe, dict):
            recipe = {}
        r = {**{"name": t, "prep_time": "15 min", "cook_time": "45 min", "total_time": "60 min",
                "servings": "4", "calories": "", "ingredients": [], "instructions": []}, **recipe}

        il = "".join("<li>{}</li>\n".format(x) for x in ing_list)
        sl = "".join(
            '<div class="step-item"><span class="step-num">{}</span><div class="step-body"><h3>{}</h3><p>{}</p></div></div>\n'.format(
                i + 1, st.get("heading", f"Step {i+1}"), st.get("body", "")
            ) for i, st in enumerate(steps)
        )
        ri = "".join("<li>{}</li>\n".format(x) for x in r.get("ingredients", []))
        ris = "".join("<li>{}</li>\n".format(x) for x in r.get("instructions", [st.get("body", "") for st in steps]))

        return """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{t}</title><link rel="stylesheet" href="{css}">
<!-- inject:head-end --></head>
<body>
<div class="article-container">
<header class="g19-header">
  <h1 class="article-title">How to Make the Best {t}</h1>
  <div class="byline">By <span class="article-author"></span> &middot; <span class="article-date"></span></div>
</header>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<p>{intro}</p>

<div class="guide-tips-box">
  <h3>Key Tips for Success</h3>
  <p>{guide_tips}</p>
</div>

<h2>Ingredients</h2>
<img src="{ing_img}" alt="Ingredients for {t}" class="ingredient-image">
<ul class="ingredient-list">
{il}</ul>

<h2>Instructions</h2>
<div class="steps-list">
{sl}</div>

<!-- inject:before-recipe -->
<div class="recipe-card" id="recipe-card">
  <img src="{card_img}" alt="{r_name}" class="recipe-card-image">
  <div class="recipe-card-header"><h2>{r_name}</h2><p>{r_summary}</p></div>
  <div class="recipe-meta">
    <div class="recipe-meta-item"><strong>Prep:</strong> {r_prep}</div>
    <div class="recipe-meta-item"><strong>Cook:</strong> {r_cook}</div>
    <div class="recipe-meta-item"><strong>Total:</strong> {r_total}</div>
    <div class="recipe-meta-item"><strong>Servings:</strong> {r_srv}</div>
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
</body></html>""".format(
            t=t, css=css_filename, main_img=main_img, ing_img=ing_img, card_img=card_img,
            intro=intro, guide_tips=guide_tips, il=il, sl=sl,
            r_name=r.get("name", t), r_summary=r.get("summary", ""),
            r_prep=r.get("prep_time", ""), r_cook=r.get("cook_time", ""),
            r_total=r.get("total_time", ""), r_srv=r.get("servings", ""), ri=ri, ris=ris,
        )

    def run(self, return_content_only=False):
        if not self.title:
            self.title = "Lemon Herb Roast Chicken"
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
    gen = ArticleGenerator({"title": "Lemon Herb Roast Chicken"})
    gen.run()
