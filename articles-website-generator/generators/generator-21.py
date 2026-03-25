"""
generator-21.py — TEMPLATE (see ARTICLE_GENERATOR_PROMPT.md)
============================================================
Copy this file when adding a new generator: rename to generator-N.py, change
preview profile, section keys, gNN- prefix, fonts, and colors — keep API shape.

Preview profile: Peruvian causa — layered potato, ají amarillo, avocado (NOT generic Western stew).
Reader job: scan + save (kicker, pull stat, glance rail before hero).
Order: kicker → deck → at-a-glance rail → mise copy → ingredient_image + mise list →
       hero (main) → heat_sequence steps → aroma_note → slim recipe footer (two columns).
Visual motif: left-rail timeline steps + postcard panels; class prefix g21-.
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
    "title": "Ají Amarillo Causa Rellena with Avocado",
    "categories_list": [{"id": 1, "categorie": "lunch"}],
    "colors": {
        "primary": "#B8860B",
        "secondary": "#2F4F4F",
        "accent": "#E8DCC4",
        "background": "#ffffff",
        "container_bg": "#ffffff",
        "border": "#DDD5C7",
        "text_primary": "#1C1B18",
        "text_secondary": "#4A4540",
        "button_print": "#2F4F4F",
        "button_pin": "#E60023",
        "button_hover_print": "#1a3333",
        "button_hover_pin": "#FF1A3C",
        "link": "#B8860B",
        "list_marker": "#B8860B",
        "rail": "#F7F4ED",
    },
    "fonts": {
        "heading": {"family": "Fraunces", "weights": [500, 700], "sizes": {"h1": "2rem", "h2": "1.35rem", "h3": "1.05rem"}},
        "body": {"family": "DM Sans", "weight": 400, "size": "1.02rem", "line_height": 1.72},
    },
    "layout": {
        "max_width": "680px",
        "section_spacing": "1.6rem",
        "paragraph_spacing": "0.95rem",
        "container_padding": "1.75rem",
        "border_radius": "12px",
        "box_shadow": "0 3px 18px rgba(47,79,79,0.06)",
    },
    "components": {
        "numbered_list": {"circle_bg": "#2F4F4F", "circle_color": "#fff", "circle_size": "28px"},
        "glance_rail": {"bg": "#F7F4ED", "border": "1px solid #DDD5C7"},
        "recipe_footer": {"bg": "#FFFCF7", "border_top": "2px solid #B8860B"},
    },
    "images": {
        "main_article_image": DEFAULT_MAIN_IMG,
        "ingredient_image": DEFAULT_ING_IMG,
        "recipe_card_image": "",
    },
    "structure_template": {"word_counts": {"deck": 90, "mise_blurb": 70, "step": 55, "aroma_note": 40}},
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

    def _preview_sections_payload(self):
        """Coherent fake content for Peruvian causa template."""
        t = self.title
        recipe = {
            "name": t,
            "summary": f"Bright ají-kissed potato layers with creamy avocado — a {t} built for sharing.",
            "ingredients": [
                "1.5 lb yellow potatoes (Yukon Gold)",
                "3–4 tbsp ají amarillo paste (jarred)",
                "3 tbsp lime juice",
                "3 tbsp neutral oil",
                "1 ripe avocado, sliced",
                "1/4 cup mayonnaise",
                "1 small red onion, minced",
                "Salt and white pepper",
                "Microgreens or cilantro for garnish",
            ],
            "instructions": [
                "Boil potatoes until tender; peel while warm; rice or mash until smooth.",
                "Beat in ají paste, lime, oil, salt — cool to room temperature.",
                "Layer half the causa in a ring mold; add avocado; top with remaining potato.",
                "Chill 30 min; unmold, garnish, slice with a hot knife.",
            ],
            "prep_time": "35 min",
            "cook_time": "25 min",
            "total_time": "90 min",
            "servings": "6",
            "calories": "280",
            "course": "Appetizer",
            "cuisine": "Peruvian",
        }
        return {
            "kicker": "Cold layered · Picnic-friendly",
            "deck": f"This {t} stacks silky potato with the gentle heat of ají amarillo and cool avocado. "
            f"It is assembled ahead, travels well, and reads as impressive with minimal last-minute work.",
            "pull_stat": "25 min active · rest 30 min",
            "mise_blurb": "Work the potatoes while hot for the smoothest mash; taste the ají — brands vary in heat.",
            "mise_list": recipe["ingredients"][:],
            "aroma_note": "You should smell lime first, then a faint pepper warmth — never raw alcohol from the jarred paste.",
            "heat_sequence": [
                {
                    "heading": "Mash and season the base",
                    "body": "Rice the potatoes through a food mill or press through a drum sieve. Fold in ají, lime, oil, and salt until the color is even sunset yellow.",
                },
                {
                    "heading": "Build the layers",
                    "body": "Oil a ring mold or deep loaf pan. Press half the mixture firmly, smoothing the top so layers stay distinct after slicing.",
                },
                {
                    "heading": "Fill and cap",
                    "body": "Fan avocado; thin spread of mayo keeps layers from sliding. Cover with remaining potato; press gently — do not crush the avocado.",
                },
                {
                    "heading": "Chill and finish",
                    "body": "Refrigerate until firm. Run a warm knife around the mold, invert, and garnish with onion and herbs.",
                },
            ],
            "recipe": recipe,
        }

    def run_preview(self):
        from ai_client import get_first_category

        p = self._preview_sections_payload()
        cat = get_first_category(self.config)
        recipe = p["recipe"]
        sections = [
            {"key": "kicker", "content": p["kicker"]},
            {"key": "deck", "content": p["deck"]},
            {"key": "pull_stat", "content": p["pull_stat"]},
            {"key": "mise_blurb", "content": p["mise_blurb"]},
            {"key": "mise_list", "content": p["mise_list"]},
            {"key": "aroma_note", "content": p["aroma_note"]},
            {"key": "heat_sequence", "content": p["heat_sequence"]},
            {"key": "recipe", "content": recipe},
        ]
        out = {
            "title": self.title,
            "slug": self.slug,
            "categorieId": str(cat.get("id", 1)),
            "categorie": cat.get("categorie", "lunch"),
            "sections": sections,
            "article_html": "",
            "article_css": "",
            "recipe": recipe,
            "recipe_title_pin": self.title[:100],
            "pinterest_title": f"{self.title} | Layered Peruvian Causa"[:100],
            "pinterest_description": f"Make {self.title}: ají potato layers, avocado, chill-ahead.",
            "pinterest_keywords": f"{self.title}, causa, ají amarillo, Peruvian appetizer",
            "focus_keyphrase": f"{self.title.lower()} recipe",
            "meta_description": f"Step-by-step {self.title}: mise, layers, chill, slice. Timings and ingredients included."[:140],
            "keyphrase_synonyms": f"causa rellena, Peruvian potato appetizer",
            "main_image": self._get_main_img(),
            "ingredient_image": self._get_ing_img(),
            "prompt_midjourney_main": f"Plated {self.title}, yellow potato layers, avocado, microgreens, soft daylight --v 6.1",
            "prompt_midjourney_ingredients": f"Ají amarillo paste, potatoes, lime, avocado flat-lay, marble --v 6.1",
        }
        out["article_css"] = self.generate_css()
        out["article_html"] = self.generate_html(sections)
        return out

    def generate_content(self):
        from ai_client import ai_chat, get_first_category

        schema_keys = [
            "kicker",
            "deck",
            "pull_stat",
            "mise_blurb",
            "mise_list",
            "aroma_note",
            "step_1",
            "step_2",
            "step_3",
            "step_4",
            "recipe",
            "meta_description",
            "focus_keyphrase",
            "pinterest_title",
            "prompt_midjourney_main",
            "prompt_midjourney_ingredients",
        ]
        sys = (
            "You write vivid recipe articles as ONE JSON object. Plain text. "
            "heat_sequence equivalent: step_1..step_4 each {heading, body ~55 words}. "
            "mise_list: array of 8–12 ingredient strings. kicker: 2–5 words. deck: ~90 words."
        )
        user = f"Dish: '{self.title}'. Keys: {json.dumps(schema_keys)}. Cuisine should match the title. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=4200, system=sys)
        d = self._xj(raw)
        p = self._preview_sections_payload()

        if d:
            kicker = self._strip_md(str(d.get("kicker", p["kicker"])))
            deck = self._strip_md(str(d.get("deck", p["deck"])))
            pull_stat = self._strip_md(str(d.get("pull_stat", p["pull_stat"])))
            mise_blurb = self._strip_md(str(d.get("mise_blurb", p["mise_blurb"])))
            mise_list = [str(x).strip() for x in (d.get("mise_list") or p["mise_list"])[:14]]
            aroma_note = self._strip_md(str(d.get("aroma_note", p["aroma_note"])))
            heat_sequence = []
            for i in range(1, 5):
                s = d.get(f"step_{i}")
                if isinstance(s, dict):
                    heat_sequence.append(
                        {
                            "heading": str(s.get("heading", f"Step {i}")).strip(),
                            "body": self._strip_md(str(s.get("body", ""))),
                        }
                    )
                else:
                    heat_sequence.append(p["heat_sequence"][i - 1] if i <= len(p["heat_sequence"]) else {"heading": f"Step {i}", "body": ""})
            recipe = d.get("recipe") if isinstance(d.get("recipe"), dict) else {}
        else:
            kicker, deck, pull_stat = p["kicker"], p["deck"], p["pull_stat"]
            mise_blurb, mise_list, aroma_note = p["mise_blurb"], list(p["mise_list"]), p["aroma_note"]
            heat_sequence = list(p["heat_sequence"])
            recipe = {}
            d = {}

        if not isinstance(recipe, dict):
            recipe = {}
        for k, dv in [
            ("name", self.title),
            ("summary", p["recipe"]["summary"]),
            ("ingredients", mise_list),
            ("instructions", [x.get("body", "") for x in heat_sequence]),
            ("prep_time", "30 min"),
            ("cook_time", "20 min"),
            ("total_time", "70 min"),
            ("servings", "6"),
            ("calories", ""),
            ("course", "Appetizer"),
            ("cuisine", "Peruvian"),
        ]:
            recipe.setdefault(k, dv)

        cat = get_first_category(self.config)
        mj_m = str(d.get("prompt_midjourney_main", "") or "").strip() if d else ""
        mj_i = str(d.get("prompt_midjourney_ingredients", "") or "").strip() if d else ""

        sections = [
            {"key": "kicker", "content": kicker},
            {"key": "deck", "content": deck},
            {"key": "pull_stat", "content": pull_stat},
            {"key": "mise_blurb", "content": mise_blurb},
            {"key": "mise_list", "content": mise_list},
            {"key": "aroma_note", "content": aroma_note},
            {"key": "heat_sequence", "content": heat_sequence},
            {"key": "recipe", "content": recipe},
        ]
        return {
            "title": self.title,
            "slug": self.slug,
            "categorieId": str(cat.get("id", 1)),
            "categorie": cat.get("categorie", "lunch"),
            "sections": sections,
            "article_html": "",
            "article_css": "",
            "prompt_used": f"generator-21 template / {self.title}",
            "recipe": recipe,
            "recipe_title_pin": (str(d.get("pinterest_title", self.title)) or self.title)[:100] if d else self.title[:100],
            "pinterest_title": (str(d.get("pinterest_title", "")) or self.title)[:100] if d else self.title[:100],
            "pinterest_description": f"Make {self.title} with this layered causa-style method.",
            "pinterest_keywords": f"{self.title}, recipe, causa, appetizer",
            "focus_keyphrase": str(d.get("focus_keyphrase", self.title.lower())) if d else self.title.lower(),
            "meta_description": (str(d.get("meta_description", "")) or f"{self.title} — mise, layers, chill.")[:140]
            if d
            else f"{self.title} — mise, layers, chill."[:140],
            "keyphrase_synonyms": f"{self.title}, Peruvian appetizer",
            "main_image": self._get_main_img(),
            "ingredient_image": self._get_ing_img(),
            "prompt_midjourney_main": mj_m if mj_m and "--v 6.1" in mj_m else f"Food photo {self.title}, soft light --v 6.1",
            "prompt_midjourney_ingredients": mj_i if mj_i and "--v 6.1" in mj_i else f"Ingredients flat-lay {self.title} --v 6.1",
        }

    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url

        c = self.config["colors"]
        f = self.config["fonts"]
        l = self.config["layout"]
        comp = self.config.get("components") or CONFIG["components"]
        gr = (comp.get("glance_rail") if isinstance(comp.get("glance_rail"), dict) else None) or CONFIG["components"].get(
            "glance_rail", {"bg": "#F7F4ED", "border": "1px solid #DDD5C7"}
        )
        rf = (comp.get("recipe_footer") if isinstance(comp.get("recipe_footer"), dict) else None) or CONFIG["components"].get(
            "recipe_footer", {"bg": "#FFFCF7", "border_top": "2px solid #B8860B"}
        )
        nl = comp.get("numbered_list") or CONFIG["components"]["numbered_list"]
        iu = build_font_import_url(f)
        bf = font_family_css(f["body"]["family"], "sans-serif")
        hf = font_family_css(f["heading"]["family"], "serif")
        media = "@media(max-width:600px){.g21-glance-pills{flex-wrap:wrap}.g21-foot-cols{grid-template-columns:1fr}.g21-rail{flex-direction:column}}"

        return f"""/* generator-21 | template — causa rail | white bg */
@import url('{iu}');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{c['background']};color:{c['text_primary']};font-family:{bf};font-size:{f['body']['size']};line-height:{f['body']['line_height']};-webkit-font-smoothing:antialiased}}
.g21-wrap{{max-width:{l['max_width']};margin:2rem auto;padding:{l['container_padding']};background:{c['container_bg']};border-radius:{l['border_radius']};box-shadow:{l['box_shadow']}}}
.g21-kicker{{font-size:0.72rem;letter-spacing:0.16em;text-transform:uppercase;color:{c['primary']};font-weight:700;margin-bottom:0.45rem}}
.g21-title{{font-family:{hf};font-size:{f['heading']['sizes']['h1']};color:{c['text_primary']};line-height:1.15;margin-bottom:0.5rem}}
.g21-deck{{color:{c['text_secondary']};margin-bottom:{l['section_spacing']};font-size:1.02rem}}
.g21-byline{{font-size:0.85rem;color:{c['text_secondary']};margin-bottom:1rem}}
.g21-pull{{display:inline-block;background:{c['rail']};border:1px solid {c['border']};padding:0.35rem 0.75rem;border-radius:999px;font-size:0.82rem;font-weight:600;color:{c['secondary']};margin-bottom:1rem}}
.g21-glance{{background:{gr['bg']};border:{gr['border']};border-radius:{l['border_radius']};padding:1rem 1.15rem;margin-bottom:{l['section_spacing']}}}
.g21-glance-pills{{display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.65rem}}
.g21-pill{{background:#fff;border:1px solid {c['border']};border-radius:6px;padding:0.25rem 0.6rem;font-size:0.78rem;color:{c['text_secondary']}}}
.g21-pill strong{{color:{c['text_primary']};font-weight:600}}
.g21-glance-sum{{font-size:0.92rem;color:{c['text_secondary']};line-height:1.45}}
.g21-mise-blurb{{margin-bottom:1rem;color:{c['text_secondary']}}}
.g21-ing-block{{margin-bottom:{l['section_spacing']}}}
.g21-ing-img{{width:100%;border-radius:{l['border_radius']};object-fit:cover;max-height:300px;display:block;margin-bottom:0.75rem}}
.g21-mise-list{{list-style:none;padding:0}}
.g21-mise-list li{{padding:0.35rem 0;border-bottom:1px dotted {c['border']};color:{c['text_secondary']};font-size:0.95rem}}
.g21-mise-list li:last-child{{border-bottom:none}}
.g21-hero{{width:100%;border-radius:{l['border_radius']};object-fit:cover;max-height:380px;display:block;margin:{l['section_spacing']} 0}}
.g21-h2{{font-family:{hf};font-size:{f['heading']['sizes']['h2']};color:{c['text_primary']};margin-bottom:0.75rem}}
.g21-rail{{display:flex;flex-direction:column;gap:1rem}}
.g21-step{{display:flex;gap:1rem;align-items:flex-start;padding-left:0.25rem;border-left:3px solid {c['accent']};padding-bottom:0.5rem}}
.g21-step-num{{flex-shrink:0;width:{nl['circle_size']};height:{nl['circle_size']};border-radius:50%;background:{nl['circle_bg']};color:{nl['circle_color']};font-weight:700;font-size:0.8rem;display:flex;align-items:center;justify-content:center}}
.g21-step h3{{font-family:{hf};font-size:1rem;margin:0 0 0.3rem;color:{c['text_primary']}}}
.g21-step p{{margin:0;font-size:0.95rem;color:{c['text_secondary']}}}
.g21-aroma{{border-left:4px solid {c['primary']};padding:0.75rem 1rem;background:{c['rail']};margin:{l['section_spacing']} 0;font-size:0.95rem;color:{c['text_secondary']};border-radius:0 8px 8px 0}}
.g21-foot{{background:{rf['bg']};border-top:{rf['border_top']};margin-top:{l['section_spacing']};padding:1.25rem;border-radius:0 0 {l['border_radius']} {l['border_radius']}}}
.g21-foot h2{{font-family:{hf};font-size:1.15rem;margin-bottom:0.75rem;color:{c['text_primary']}}}
.g21-foot-cols{{display:grid;grid-template-columns:1fr 1fr;gap:1.25rem}}
.g21-foot-col h3{{font-size:0.85rem;text-transform:uppercase;letter-spacing:0.06em;color:{c['primary']};margin-bottom:0.5rem}}
.g21-foot-col ul,.g21-foot-col ol{{margin:0;padding-left:1.1rem;font-size:0.9rem;color:{c['text_secondary']}}}
.g21-foot-col li{{margin-bottom:0.35rem}}
.g21-btns{{display:flex;gap:0.5rem;margin-top:1rem}}
.g21-btns button{{flex:1;padding:0.55rem 0.75rem;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:0.82rem;color:#fff}}
.g21-print{{background:{c['button_print']}}}
.g21-pin{{background:{c['button_pin']}}}
{media}"""

    def generate_html(self, sections, css_filename="css.css"):
        sec = {s["key"]: s["content"] for s in sections}
        kicker = sec.get("kicker", "")
        deck = sec.get("deck", "")
        pull_stat = sec.get("pull_stat", "")
        mise_blurb = sec.get("mise_blurb", "")
        mise_list = sec.get("mise_list") or []
        if not isinstance(mise_list, list):
            mise_list = []
        aroma_note = sec.get("aroma_note", "")
        heat_sequence = sec.get("heat_sequence") or []
        if not isinstance(heat_sequence, list):
            heat_sequence = []
        recipe = sec.get("recipe") or {}
        if not isinstance(recipe, dict):
            recipe = {}
        r = {
            **{
                "name": self.title,
                "summary": "",
                "prep_time": "",
                "cook_time": "",
                "total_time": "",
                "servings": "",
                "ingredients": [],
                "instructions": [],
            },
            **recipe,
        }

        ing_img = _e(self._get_ing_img(), attr=True)
        hero = _e(self._get_main_img(), attr=True)
        t = _e(self.title)

        mise_li = "".join(f"<li>{_e(x)}</li>" for x in mise_list)
        steps_html = ""
        for i, st in enumerate(heat_sequence[:8]):
            if not isinstance(st, dict):
                continue
            steps_html += (
                f'<div class="g21-step"><span class="g21-step-num">{i+1}</span><div>'
                f'<h3>{_e(st.get("heading", ""))}</h3><p>{_e(st.get("body", ""))}</p></div></div>'
            )

        ri = "".join(f"<li>{_e(x)}</li>" for x in r.get("ingredients", []))
        ris = "".join(f"<li>{_e(x)}</li>" for x in r.get("instructions", []))

        pills = (
            f'<span class="g21-pill"><strong>Prep</strong> {_e(r.get("prep_time",""))}</span>'
            f'<span class="g21-pill"><strong>Cook</strong> {_e(r.get("cook_time",""))}</span>'
            f'<span class="g21-pill"><strong>Total</strong> {_e(r.get("total_time",""))}</span>'
            f'<span class="g21-pill"><strong>Serves</strong> {_e(r.get("servings",""))}</span>'
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{t}</title><link rel="stylesheet" href="{_e(css_filename, attr=True)}">
<!-- inject:head-end --></head>
<body>
<div class="g21-wrap">
  <p class="g21-kicker">{_e(kicker)}</p>
  <h1 class="g21-title">{t}</h1>
  <p class="g21-byline">By <span class="article-author"></span> · <span class="article-date"></span></p>
  <p class="g21-deck">{_e(deck)}</p>
  <p class="g21-pull">{_e(pull_stat)}</p>

  <section class="g21-glance" aria-label="At a glance">
    <div class="g21-glance-pills">{pills}</div>
    <p class="g21-glance-sum">{_e(r.get("summary", ""))}</p>
  </section>

  <p class="g21-mise-blurb">{_e(mise_blurb)}</p>
  <div class="g21-ing-block">
    <img class="g21-ing-img" src="{ing_img}" alt="Mise en place for {t}">
    <ul class="g21-mise-list">{mise_li}</ul>
  </div>

  <img class="g21-hero hero-image" src="{hero}" alt="{t} plated">

  <h2 class="g21-h2">Assembly sequence</h2>
  <div class="g21-rail">{steps_html}</div>

  <p class="g21-aroma"><strong>Sensor check:</strong> {_e(aroma_note)}</p>

  <footer class="g21-foot" id="recipe-card">
    <h2>{_e(r.get("name", self.title))}</h2>
    <div class="g21-foot-cols">
      <div class="g21-foot-col"><h3>Ingredients</h3><ul>{ri}</ul></div>
      <div class="g21-foot-col"><h3>Method</h3><ol>{ris}</ol></div>
    </div>
    <div class="g21-btns">
      <button type="button" class="g21-print" onclick="window.print()">Print</button>
      <button type="button" class="g21-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent(document.querySelector('.hero-image')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin</button>
    </div>
  </footer>
</div>
<!-- inject:article-end -->
</body></html>"""

    def run(self, return_content_only=False):
        if not self.title:
            self.title = CONFIG["title"]
            self.slug = self._slugify(self.title)
        cd = self.generate_content()
        cd["article_css"] = self.generate_css()
        cd["article_html"] = self.generate_html(cd["sections"])
        if return_content_only:
            return cd
        os.makedirs(self.slug, exist_ok=True)
        with open(os.path.join(self.slug, "content.json"), "w", encoding="utf-8") as fh:
            json.dump(cd, fh, indent=2)
        with open(os.path.join(self.slug, "article.html"), "w", encoding="utf-8") as fh:
            fh.write(cd["article_html"])
        with open(os.path.join(self.slug, "css.css"), "w", encoding="utf-8") as fh:
            fh.write(cd["article_css"])
        print("[OK] Saved to: {}/".format(self.slug))
        return cd


if __name__ == "__main__":
    ArticleGenerator({"title": "Ají Amarillo Causa Rellena with Avocado"}).run()
