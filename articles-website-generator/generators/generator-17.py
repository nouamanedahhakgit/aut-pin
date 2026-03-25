"""
generator-17.py — Listicle
---------------------------
"5 Reasons to Love…" format. Hero image, short hook intro, 5 numbered
sections (each with heading + ~60w), ingredient image as divider after #2,
compact recipe card at the end. No FAQ. Warm amber/coral palette.
Lora + Source Sans 3.
"""

import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary": "#c2410c", "secondary": "#ea580c", "accent": "#ea580c",
        "background": "#fff7ed", "container_bg": "#ffffff", "border": "#fed7aa",
        "text_primary": "#431407", "text_secondary": "#9a3412",
        "button_print": "#c2410c", "button_pin": "#E60023",
        "button_hover_print": "#9a3412", "button_hover_pin": "#FF1A3C",
        "link": "#ea580c", "list_marker": "#c2410c",
    },
    "fonts": {
        "heading": {"family": "Lora", "weights": [500, 600, 700], "sizes": {"h1": "2.1rem", "h2": "1.35rem", "h3": "1.15rem"}},
        "body": {"family": "Source Sans 3", "weight": 400, "size": "1rem", "line_height": 1.7},
    },
    "layout": {
        "max_width": "720px", "section_spacing": "1.75rem",
        "paragraph_spacing": "0.95rem", "list_spacing": "0.45rem",
        "container_padding": "1.75rem", "border_radius": "10px",
        "box_shadow": "0 2px 12px rgba(194,65,12,0.06)",
    },
    "components": {
        "numbered_list": {"style": "circle", "circle_bg": "#c2410c", "circle_color": "#fff", "circle_size": "32px"},
        "bullet_list": {"style": "disc", "color": "#c2410c"},
        "reason_box": {"border_left": "4px solid #ea580c", "bg": "#fff7ed", "padding": "1rem 1.25rem"},
        "recipe_card": {"bg": "#fff", "border": "2px solid #fed7aa", "border_radius": "10px", "padding": "0",
                       "meta_icon_color": "#c2410c", "header_bg": "#c2410c", "header_color": "#fff"},
    },
    "images": {"main_article_image": "", "ingredient_image": "", "recipe_card_image": ""},
    "structure_template": {"word_counts": {"intro": 70, "reason": 60, "closing": 40}},
    "dark_mode": False,
}


class ArticleGenerator:
    def __init__(self, config_override=None):
        self.config = dict(CONFIG)
        if config_override:
            self._merge(self.config, config_override)
        from ai_client import create_ai_client
        self.client, self.model = create_ai_client(self.config)
        self.title = self.config["title"].strip()
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

    def _chat(self, prompt, mt=400):
        from ai_client import ai_chat
        sys = ("You are an enthusiastic home cook. Write warm, engaging listicle content. "
               "Plain text only. All content about: {self.title}.".format(self=self))
        return self._strip_md(ai_chat(self, prompt, max_tokens=mt, system=sys) or "")

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

    def generate_content(self):
        from ai_client import ai_chat, get_first_category
        schema = {
            "intro": "string ~70 words — hook for listicle",
            "reason_1_title": "string — short heading",
            "reason_1_body": "string ~60 words",
            "reason_2_title": "string",
            "reason_2_body": "string ~60 words",
            "reason_3_title": "string",
            "reason_3_body": "string ~60 words",
            "reason_4_title": "string",
            "reason_4_body": "string ~60 words",
            "reason_5_title": "string",
            "reason_5_body": "string ~60 words",
            "closing": "string ~40 words",
            "ingredient_list": "array of 8-12 strings with measurements",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine",
            "meta_description": "100-120 chars",
            "focus_keyphrase": "string",
            "pinterest_title": "string",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        sys = "You are an enthusiastic home cook. Generate a '5 Reasons to Love' listicle article as ONE JSON. Plain text. Warm tone."
        user = "Generate a '5 Reasons to Love {t}' listicle article as JSON with keys: {keys}. Return ONLY valid JSON.".format(
            t=self.title, keys=json.dumps(list(schema.keys()))
        )
        raw = ai_chat(self, user, max_tokens=4000, system=sys)
        d = self._xj(raw)

        if d:
            print("[*] Listicle — single-JSON.")
            intro = self._strip_md(str(d.get("intro", "")))
            closing = self._strip_md(str(d.get("closing", "")))
            reasons = [
                (self._strip_md(str(d.get("reason_1_title", ""))), self._strip_md(str(d.get("reason_1_body", "")))),
                (self._strip_md(str(d.get("reason_2_title", ""))), self._strip_md(str(d.get("reason_2_body", "")))),
                (self._strip_md(str(d.get("reason_3_title", ""))), self._strip_md(str(d.get("reason_3_body", "")))),
                (self._strip_md(str(d.get("reason_4_title", ""))), self._strip_md(str(d.get("reason_4_body", "")))),
                (self._strip_md(str(d.get("reason_5_title", ""))), self._strip_md(str(d.get("reason_5_body", "")))),
            ]
            ing_list = [str(x).strip() for x in (d.get("ingredient_list") or [])[:12]]
            recipe = d.get("recipe") or {}
        else:
            print("[*] Listicle — sequential.")
            intro = self._chat("Write a 70-word intro for '5 Reasons to Love {}'. Engaging hook. Plain text.".format(self.title), 160)
            reasons = []
            for i in range(1, 6):
                t = self._chat("Title for reason {} of '5 Reasons to Love {}'. Short, punchy. Plain text only.".format(i, self.title), 50)
                b = self._chat("Body for reason {} (~60 words). Plain text.".format(i), 120)
                reasons.append((t, b))
            closing = self._chat("Write a 40-word closing for '5 Reasons to Love {}'. Plain text.".format(self.title), 80)
            raw = self._chat("List 8-12 ingredients for {} with measurements. One per line.".format(self.title), 200)
            ing_list = [l.strip() for l in raw.splitlines() if l.strip()][:12]
            recipe = {}

        if not isinstance(recipe, dict):
            recipe = {}
        instructions = recipe.get("instructions") or []
        for k, dv in [("name", self.title), ("summary", "A dish you'll love."), ("ingredients", ing_list),
                      ("instructions", instructions), ("prep_time", "15 min"), ("cook_time", "25 min"),
                      ("total_time", "40 min"), ("servings", "4"), ("calories", ""), ("course", "Main Course"), ("cuisine", "American")]:
            recipe.setdefault(k, dv)

        cat = get_first_category(self.config)
        main_img = self.config["images"].get("main_article_image") or "placeholder.jpg"
        ing_img = self.config["images"].get("ingredient_image") or "placeholder.jpg"
        mj_m = str(d.get("prompt_midjourney_main", "") or "").strip() if d else ""
        mj_i = str(d.get("prompt_midjourney_ingredients", "") or "").strip() if d else ""

        sections = [
            {"key": "intro", "content": intro},
            {"key": "reasons", "content": reasons},
            {"key": "closing", "content": closing},
            {"key": "ingredient_list", "content": ing_list},
            {"key": "recipe", "content": recipe},
        ]
        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": "generator-17 / title: {}".format(self.title),
            "prompt_base": "Listicle for: {}".format(self.title),
            "recipe": recipe,
            "recipe_title_pin": (str(d.get("pinterest_title", self.title)) or self.title)[:100] if d else self.title[:100],
            "pinterest_title": (str(d.get("pinterest_title", "")) or self.title)[:100] if d else self.title[:100],
            "pinterest_description": "5 reasons to love {}!".format(self.title),
            "pinterest_keywords": "{}, recipe, why love".format(self.title),
            "focus_keyphrase": str(d.get("focus_keyphrase", self.title.lower())) if d else self.title.lower(),
            "meta_description": (str(d.get("meta_description", "")) or "5 reasons to love {}.".format(self.title))[:140] if d else ("5 reasons to love {}.".format(self.title))[:140],
            "keyphrase_synonyms": "why {}, love {}, {} recipe".format(self.title, self.title, self.title),
            "main_image": main_img,
            "ingredient_image": ing_img,
            "prompt_midjourney_main": mj_m if mj_m and "--v 6.1" in mj_m else "Warm food photography, {}, inviting styling --v 6.1".format(self.title),
            "prompt_midjourney_ingredients": mj_i if mj_i and "--v 6.1" in mj_i else "Ingredient flat-lay for {}, warm tones --v 6.1".format(self.title),
        }

    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url
        c = self.config["colors"]
        f = self.config["fonts"]
        l = self.config["layout"]
        rb = self.config["components"]["reason_box"]
        rc = self.config["components"]["recipe_card"]
        nl = self.config["components"]["numbered_list"]
        iu = build_font_import_url(f)
        bf = font_family_css(f["body"]["family"], "sans-serif")
        hf = font_family_css(f["heading"]["family"], "serif")

        return """/* generator-17 | Listicle */
@import url('{}');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{};color:{};font-family:{};font-size:{};line-height:{};-webkit-font-smoothing:antialiased}}
.article-container{{max-width:{};margin:2rem auto;padding:{};background:{};border-radius:{};box-shadow:{}}}
.g17-header{{margin-bottom:{}}}
.g17-header .article-title{{font-family:{};font-size:{};color:{};margin-bottom:0.3rem}}
.g17-header .byline{{font-size:0.82rem;color:{}}}
h2{{font-family:{};font-size:{};color:{};margin-top:{};margin-bottom:0.5rem}}
h3{{font-family:{};font-size:{};color:{};margin-bottom:0.4rem}}
p{{color:{};margin-bottom:{}}}
a{{color:{};text-decoration:none}}a:hover{{text-decoration:underline}}
.hero-image{{width:100%;border-radius:{};margin:1rem 0;object-fit:cover;max-height:420px;display:block}}
.ingredient-image{{width:100%;border-radius:{};margin:1.5rem 0;object-fit:cover;max-height:340px;display:block}}
.reason-item{{margin-bottom:{};border-left:{};background:{};padding:{};border-radius:0 8px 8px 0}}
.reason-item h3{{display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem}}
.reason-num{{width:{};height:{};border-radius:50%;background:{};color:{};font-weight:700;display:inline-flex;align-items:center;justify-content:center;font-size:0.85rem}}
.recipe-card{{background:{};border:{};border-radius:{};overflow:hidden;margin:{} 0;box-shadow:{}}}
.recipe-card-header{{background:{};color:{};padding:1rem 1.25rem;text-align:center}}
.recipe-card-header h2{{margin:0;color:{};font-size:1.25rem}}
.recipe-card-body{{padding:1.25rem}}
.recipe-card-image{{width:100%;height:220px;object-fit:cover;display:block}}
.recipe-card-buttons{{display:flex;gap:0.6rem;margin:0.75rem 0}}
.btn-print,.btn-pin{{flex:1;color:#fff;border:none;padding:0.65rem 0.9rem;border-radius:{};cursor:pointer;font-weight:600;font-size:0.85rem}}
.btn-print{{background:{}}}.btn-print:hover{{background:{}}}
.btn-pin{{background:{}}}.btn-pin:hover{{background:{}}}
.recipe-meta{{display:flex;flex-wrap:wrap;border:1px solid {};border-radius:{};margin:0.6rem 0}}
.recipe-meta-item{{flex:1;text-align:center;padding:0.5rem 0.35rem;min-width:60px;border-right:1px solid {}}}
.recipe-meta-item:last-child{{border-right:none}}
.recipe-meta-label{{font-size:0.6rem;text-transform:uppercase;color:{};letter-spacing:0.06em}}
.recipe-meta-value{{font-size:0.88rem;font-weight:700;color:{};display:block;margin-top:2px}}
.recipe-ingredients-list,.recipe-instructions-list{{list-style:none;padding:0}}
.recipe-ingredients-list li{{padding:0.3rem 0 0.3rem 1.2rem;position:relative;color:{};border-bottom:1px dotted {}}}
.recipe-ingredients-list li:last-child{{border-bottom:none}}
.recipe-ingredients-list li::before{{content:'\\2713';position:absolute;left:0;color:{};font-weight:700}}
.recipe-instructions-list li{{counter-increment:rstep;padding:0.5rem 0 0.5rem 2.2rem;position:relative;color:{};border-bottom:1px dotted {}}}
.recipe-instructions-list li:last-child{{border-bottom:none}}
.recipe-instructions-list{{counter-reset:rstep}}
.recipe-instructions-list li::before{{content:counter(rstep);position:absolute;left:0;top:0.35rem;width:22px;height:22px;background:{};color:{};border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.75rem}}
@media print{{body{{background:#fff}}.recipe-card-buttons{{display:none}}}}
@media(max-width:600px){{.recipe-card-buttons{{flex-direction:column}}h1{{font-size:1.6rem}}}}""".format(
            iu, c["background"], c["text_primary"], bf, f["body"]["size"], f["body"]["line_height"],
            l["max_width"], l["container_padding"], c["container_bg"], l["border_radius"], l["box_shadow"],
            l["section_spacing"], hf, f["heading"]["sizes"]["h1"], c["text_primary"], c["text_secondary"],
            hf, f["heading"]["sizes"]["h2"], c["primary"], l["section_spacing"],
            hf, f["heading"]["sizes"]["h3"], c["secondary"],
            c["text_secondary"], l["paragraph_spacing"], c["link"],
            l["border_radius"], l["border_radius"],
            l["section_spacing"], rb["border_left"], rb["bg"], rb["padding"],
            nl["circle_size"], nl["circle_size"], nl["circle_bg"], nl["circle_color"],
            rc["bg"], rc["border"], rc["border_radius"], l["section_spacing"], l["box_shadow"],
            rc["header_bg"], rc["header_color"], rc["header_color"],
            l["border_radius"], c["button_print"], c["button_hover_print"], c["button_pin"], c["button_hover_pin"],
            c["border"], l["border_radius"], c["border"], c["text_secondary"], rc["meta_icon_color"],
            c["text_secondary"], c["border"], c["list_marker"],
            c["text_secondary"], c["border"], nl["circle_bg"], nl["circle_color"],
        )

    def generate_html(self, sections, css_filename="css.css"):
        t = self.title
        imgs = self.config["images"]
        main_img = imgs.get("main_article_image") or "placeholder.jpg"
        ing_img = imgs.get("ingredient_image") or "placeholder.jpg"
        card_img = imgs.get("recipe_card_image") or main_img
        sec = {s["key"]: s["content"] for s in sections}

        intro = sec.get("intro", "")
        reasons = sec.get("reasons", [])
        closing = sec.get("closing", "")
        ing_list = sec.get("ingredient_list", [])
        recipe = sec.get("recipe") or {}
        if not isinstance(recipe, dict):
            recipe = {}
        r = {**{"name": t, "prep_time": "15 min", "cook_time": "25 min", "total_time": "40 min",
                "servings": "4", "calories": "", "ingredients": [], "instructions": []}, **recipe}

        reason_html = []
        for i, (rtitle, rbody) in enumerate(reasons[:5]):
            reason_html.append(
                '<div class="reason-item">'
                '<h3><span class="reason-num">{}</span> {}</h3><p>{}</p></div>'.format(
                    i + 1, rtitle or "Reason {}".format(i + 1), rbody or ""
                )
            )
            if i == 1:
                reason_html.append('<img src="{}" alt="Ingredients for {}" class="ingredient-image">'.format(ing_img, t))

        reas = "\n".join(reason_html)
        ri = "".join("<li>{}</li>\n".format(x) for x in r.get("ingredients", []))
        ris = "".join("<li>{}</li>\n".format(x) for x in r.get("instructions", []))

        return """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>5 Reasons to Love {t}</title><link rel="stylesheet" href="{css}">
<!-- inject:head-end --></head>
<body>
<div class="article-container">
<header class="g17-header">
  <h1 class="article-title">5 Reasons to Love {t}</h1>
  <div class="byline">By <span class="article-author"></span> &middot; <span class="article-date"></span></div>
</header>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<p>{intro}</p>

<h2>5 Reasons to Love {t}</h2>
{reas}

<p>{closing}</p>

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
    </div>
    <div class="recipe-card-buttons">
      <button class="btn-print" onclick="window.print()">Print</button>
      <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin</button>
    </div>
    <h3>Ingredients</h3><ul class="recipe-ingredients-list">{ri}</ul>
    <h3>Instructions</h3><ol class="recipe-instructions-list">{ris}</ol>
  </div>
</div>
<!-- inject:article-end -->
</div>
</body></html>""".format(
            t=t, css=css_filename, main_img=main_img, ing_img=ing_img, card_img=card_img,
            intro=intro, reas=reas, closing=closing,
            r_name=r.get("name", t), r_prep=r.get("prep_time", ""), r_cook=r.get("cook_time", ""),
            r_total=r.get("total_time", ""), r_srv=r.get("servings", ""), ri=ri, ris=ris,
        )

    def run(self, return_content_only=False):
        if not self.title:
            raise ValueError("CONFIG['title'] is required")
        cd = self.generate_content()
        css = self.generate_css()
        html = self.generate_html(cd["sections"])
        cd["article_html"] = html
        cd["article_css"] = css
        if return_content_only:
            return cd
        slug = self.slug
        os.makedirs(slug, exist_ok=True)
        with open(os.path.join(slug, "content.json"), "w", encoding="utf-8") as fh:
            json.dump(cd, fh, indent=2)
        with open(os.path.join(slug, "article.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
        with open(os.path.join(slug, "css.css"), "w", encoding="utf-8") as fh:
            fh.write(css)
        print("[OK] Saved to: {}/".format(slug))
        return cd


if __name__ == "__main__":
    gen = ArticleGenerator({"title": "One-Pan Chicken Thighs"})
    gen.run()
