"""
generator-14.py  —  Quick Glance
---------------------------------
Summary-first recipe article. Starts with an at-a-glance card showing
time/servings/difficulty, a very short hook, ingredients as a visual
checklist, concise numbered steps, substitutions grid, and straight
to the recipe card.  Minimal filler text — for readers who just want
the recipe fast.  Clean mint/slate palette, Inter + DM Sans.
"""

import os, json, re
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary": "#0d9488", "secondary": "#334155", "accent": "#0d9488",
        "background": "#f8fafb", "container_bg": "#ffffff", "border": "#e2e8f0",
        "text_primary": "#1e293b", "text_secondary": "#64748b",
        "button_print": "#334155", "button_pin": "#0d9488",
        "button_hover_print": "#1e293b", "button_hover_pin": "#0a7a70",
        "link": "#0d9488", "list_marker": "#0d9488",
    },
    "fonts": {
        "heading": {"family": "Inter", "weights": [500, 700],
                    "sizes": {"h1": "2rem", "h2": "1.35rem", "h3": "1.05rem"}},
        "body": {"family": "DM Sans", "weight": 400, "size": "0.95rem", "line_height": 1.7},
    },
    "layout": {
        "max_width": "760px", "section_spacing": "2rem",
        "paragraph_spacing": "0.9rem", "list_spacing": "0.4rem",
        "container_padding": "2rem", "border_radius": "12px",
        "box_shadow": "0 1px 8px rgba(0,0,0,0.04)",
    },
    "components": {
        "numbered_list": {"style": "circle", "circle_bg": "#0d9488", "circle_color": "#fff", "circle_size": "30px"},
        "bullet_list": {"style": "check", "color": "#0d9488"},
        "pro_tips_box": {"bg_color": "#f0fdfa", "border_color": "#0d9488", "border_left": "3px solid #0d9488", "padding": "1.25rem"},
        "recipe_card": {"bg": "#fff", "border": "1px solid #e2e8f0", "border_radius": "12px", "padding": "0", "meta_icon_color": "#0d9488", "header_bg": "#0d9488", "header_color": "#fff"},
    },
    "images": {"main_article_image": "", "ingredient_image": "", "recipe_card_image": ""},
    "structure_template": {"word_counts": {"hook": 40, "step": 50, "substitution": 20, "quick_tip": 25}},
    "dark_mode": False,
}

STRUCTURE = [
    {"key": "at_a_glance",      "type": "summary_card","label": "At a Glance"},
    {"key": "hook",             "type": "hook",        "label": ""},
    {"key": "ingredients_check","type": "checklist",   "label": "Ingredients Checklist"},
    {"key": "quick_steps",      "type": "steps",       "label": "How to Make It"},
    {"key": "substitutions",    "type": "grid",        "label": "Easy Swaps"},
    {"key": "quick_tips",       "type": "tips",        "label": "Quick Tips"},
    {"key": "faqs",             "type": "faq",         "label": "Quick Answers"},
    {"key": "wrap_up",          "type": "conclusion",  "label": ""},
]


class ArticleGenerator:

    def __init__(self, config_override=None):
        self.config = dict(CONFIG)
        if config_override: self._merge(self.config, config_override)
        from ai_client import create_ai_client
        self.client, self.model = create_ai_client(self.config)
        self.title = self.config["title"].strip()
        self.slug = self._slugify(self.title)

    def _merge(self, b, o):
        for k, v in o.items():
            if k in b and isinstance(b[k], dict) and isinstance(v, dict): self._merge(b[k], v)
            else: b[k] = v

    def _slugify(self, t):
        return re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", t.lower()).strip()) or "article"

    def _strip_md(self, t):
        if not t or not isinstance(t, str): return t
        s = re.sub(r'^#{1,6}\s*', '', t.strip()); s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s); s = re.sub(r'\*([^*]+)\*', r'\1', s)
        return s.strip()

    def _chat(self, prompt, mt=500):
        from ai_client import ai_chat
        sys = ("You are a concise, modern recipe writer. Be direct and efficient — "
               "readers want the recipe fast. No fluff. Plain text only. "
               f"All content about: {self.title}.")
        raw = ai_chat(self, prompt, max_tokens=mt, system=sys)
        return self._strip_md(raw) if raw else ""

    def _xj(self, raw):
        if not raw: return {}
        text = raw.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m: text = m.group(1).strip()
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try: return json.loads(m.group())
            except: pass
        try: return json.loads(text)
        except: return {}

    def generate_content(self):
        from ai_client import ai_chat
        schema = {
            "hook": "string ~40 words — one punchy paragraph, no intro fluff",
            "difficulty": "string — Easy, Medium, or Hard",
            "ingredient_list": "array of 10 strings with measurements",
            "steps": "array of 6 objects {action, detail} — action is 3-5 word verb phrase, detail is 1-2 sentences",
            "substitutions": "array of 4 objects {original, swap, note} — ingredient swaps",
            "quick_tips": "array of 3 short strings — one sentence each",
            "faqs": "array of 3 objects {question, answer} — concise answers",
            "wrap_up": "string ~30 words, one-sentence wrap-up",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine",
            "meta_description": "120-140 chars", "focus_keyphrase": "string",
            "pinterest_title": "string", "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        sys = "You are a concise modern recipe writer. Generate the full quick-glance recipe as ONE JSON. Plain text. All about the recipe title."
        user = f"Generate a quick-glance recipe article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=4500, system=sys)
        d = self._xj(raw)

        if d:
            print("[*] Quick Glance — single-JSON generated.")
            hook = self._strip_md(str(d.get("hook", "")))
            difficulty = str(d.get("difficulty", "Medium")).strip()
            ing_list = [str(x).strip() for x in (d.get("ingredient_list") or [])[:12]]
            steps_raw = d.get("steps") or []
            steps = [{"action": str(s.get("action", f"Step {i}")).strip() if isinstance(s, dict) else f"Step {i}",
                      "detail": self._strip_md(str(s.get("detail", "")) if isinstance(s, dict) else "")}
                     for i, s in enumerate(steps_raw[:6], 1)]
            subs_raw = d.get("substitutions") or []
            subs = [{"original": str(s.get("original","")).strip(), "swap": str(s.get("swap","")).strip(),
                     "note": str(s.get("note","")).strip()} for s in subs_raw[:4] if isinstance(s, dict)]
            tips = [self._strip_md(str(x)) for x in (d.get("quick_tips") or [])[:3]]
            faqs_raw = d.get("faqs") or []
            faqs = [{"question": str(f.get("question","")).strip(), "answer": self._strip_md(str(f.get("answer","")))} for f in faqs_raw[:3] if isinstance(f, dict)]
            wrap_up = self._strip_md(str(d.get("wrap_up", "")))
            recipe = d.get("recipe") or {}
            if not isinstance(recipe, dict): recipe = {}
        else:
            print("[*] Quick Glance — sequential generation.")
            hook = self._chat(f"Write a 40-word punchy hook for {self.title}. One paragraph, no fluff.", 100)
            difficulty = "Medium"
            raw = self._chat(f"List 10 ingredients for {self.title} with measurements. One per line.", 200)
            ing_list = [l.strip() for l in raw.splitlines() if l.strip()][:12]
            steps = []
            for i in range(1, 7):
                raw = self._chat(f"Step {i} for {self.title}. Format: ACTION: <3-5 word verb phrase>\nDETAIL: <1-2 sentences>", 120)
                a, dt = f"Step {i}", raw
                for line in (raw or "").splitlines():
                    s = line.strip()
                    if s.upper().startswith("ACTION:"): a = s.split(":", 1)[-1].strip() or a
                    elif s.upper().startswith("DETAIL:"): dt = s.split(":", 1)[-1].strip() or dt
                steps.append({"action": a, "detail": dt})
            raw = self._chat(f"Give 4 ingredient substitutions for {self.title}. Format per line: ORIGINAL > SWAP (note)", 200)
            subs = []
            for line in raw.splitlines():
                if ">" in line:
                    parts = line.split(">", 1)
                    subs.append({"original": parts[0].strip(), "swap": parts[1].strip(), "note": ""})
            subs = subs[:4]
            raw = self._chat(f"Give 3 quick one-sentence tips for {self.title}. One per line.", 150)
            tips = [self._strip_md(l.strip()) for l in raw.splitlines() if l.strip()][:3]
            raw = self._chat(f"Write 3 FAQ pairs for {self.title}. Q1:...\nA1:...\nQ2:...\nA2:...\nQ3:...\nA3:...", 400)
            faqs = []
            for i in range(1, 4):
                q = a = None
                for line in raw.splitlines():
                    ls = line.strip()
                    if ls.upper().startswith(f"Q{i}:"): q = ls.split(":", 1)[-1].strip()
                    elif ls.upper().startswith(f"A{i}:"): a = ls.split(":", 1)[-1].strip()
                faqs.append({"question": q or f"How long does {self.title} keep?", "answer": a or ""})
            wrap_up = self._chat(f"Write a 30-word wrap-up for {self.title}.", 80)
            recipe = {}; d = {}

        if not recipe.get("ingredients") and ing_list: recipe["ingredients"] = list(ing_list)[:20]
        if not recipe.get("instructions") and steps: recipe["instructions"] = [s.get("detail", "") for s in steps][:15]
        for k, dv in {"name": self.title, "summary": f"Quick & easy {self.title}.", "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min", "servings": "4", "calories": "350", "course": "Main Course", "cuisine": "American"}.items():
            recipe.setdefault(k, dv)

        from ai_client import get_first_category
        cat = get_first_category(self.config)
        main_img = self.config["images"].get("main_article_image") or "placeholder.jpg"
        mj_m = str(d.get("prompt_midjourney_main", "") or "").strip()
        mj_i = str(d.get("prompt_midjourney_ingredients", "") or "").strip()

        sections = [
            {"key": "hook", "content": hook}, {"key": "difficulty", "content": difficulty},
            {"key": "ingredient_list", "content": ing_list}, {"key": "steps", "content": steps},
            {"key": "substitutions", "content": subs}, {"key": "quick_tips", "content": tips},
            {"key": "faqs", "content": faqs}, {"key": "wrap_up", "content": wrap_up},
        ]
        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": f"generator-14 / title: {self.title}",
            "prompt_base": f"Quick Glance recipe for: {self.title}",
            "recipe": recipe,
            "recipe_title_pin": (str(d.get("pinterest_title", self.title)) or self.title)[:100],
            "pinterest_title": (str(d.get("pinterest_title", "")) or self.title)[:100],
            "pinterest_description": f"Quick & easy {self.title} — ready in no time!",
            "pinterest_keywords": f"{self.title}, quick recipe, easy dinner, fast meal",
            "focus_keyphrase": str(d.get("focus_keyphrase", self.title.lower())),
            "meta_description": (str(d.get("meta_description", "")) or f"Quick & easy {self.title} recipe — minimal effort, maximum flavor.")[:140],
            "keyphrase_synonyms": f"{self.title} recipe, quick {self.title}, easy {self.title}",
            "main_image": main_img,
            "ingredient_image": self.config["images"].get("ingredient_image") or "placeholder.jpg",
            "prompt_midjourney_main": mj_m if mj_m and "--v 6.1" in mj_m else f"Modern clean food photography of {self.title}, white plate, minimal styling --v 6.1",
            "prompt_midjourney_ingredients": mj_i if mj_i and "--v 6.1" in mj_i else f"Clean ingredient flat-lay for {self.title}, white surface, organized grid --v 6.1",
        }

    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url
        c = self.config["colors"]; f = self.config["fonts"]; l = self.config["layout"]
        cp = self.config["components"]; nl = cp["numbered_list"]; rc = cp["recipe_card"]
        iu = build_font_import_url(f)
        bf = font_family_css(f["body"]["family"], "sans-serif")
        hf = font_family_css(f["heading"]["family"], "sans-serif")

        return f"""/* generator-14 | Quick Glance */
@import url('{iu}');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{c['background']};color:{c['text_primary']};font-family:{bf};font-size:{f['body']['size']};font-weight:{f['body']['weight']};line-height:{f['body']['line_height']};-webkit-font-smoothing:antialiased}}
.article-container{{max-width:{l['max_width']};margin:2rem auto;padding:{l['container_padding']};background:{c['container_bg']};border-radius:{l['border_radius']};box-shadow:{l['box_shadow']}}}

.g14-header{{margin-bottom:1.5rem}}
.g14-header .article-title{{font-family:{hf};font-size:{f['heading']['sizes']['h1']};font-weight:700;color:{c['text_primary']};margin-bottom:0.3rem}}
.g14-header .byline-row{{display:flex;gap:1rem;align-items:center;font-size:0.82rem;color:{c['text_secondary']}}}
h2{{font-family:{hf};font-size:{f['heading']['sizes']['h2']};font-weight:700;color:{c['text_primary']};margin-top:{l['section_spacing']};margin-bottom:0.6rem}}
h3{{font-family:{hf};font-size:{f['heading']['sizes']['h3']};color:{c['text_primary']};margin-top:1rem;margin-bottom:0.3rem}}
p{{color:{c['text_secondary']};margin-bottom:{l['paragraph_spacing']}}}
a{{color:{c['link']};text-decoration:none}}a:hover{{text-decoration:underline}}

.hero-image{{width:100%;border-radius:{l['border_radius']};margin:1rem 0;object-fit:cover;max-height:400px;display:block}}

/* At a glance card */
.glance-card{{display:flex;gap:0;border:1px solid {c['border']};border-radius:{l['border_radius']};overflow:hidden;margin:1.5rem 0}}
.glance-item{{flex:1;text-align:center;padding:0.9rem 0.5rem;border-right:1px solid {c['border']}}}
.glance-item:last-child{{border-right:none}}
.glance-label{{font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;color:{c['text_secondary']}}}
.glance-value{{font-size:1rem;font-weight:700;color:{c['primary']};margin-top:2px}}

/* Hook */
.hook-text{{font-size:1.1rem;color:{c['text_primary']};font-weight:500;margin:0.5rem 0 {l['section_spacing']}}}

/* Ingredient checklist (two-column, checkmarks) */
.ing-section{{display:grid;grid-template-columns:1fr 1fr;gap:1.75rem;align-items:start;margin:{l['section_spacing']} 0}}
.ing-image{{width:100%;border-radius:{l['border_radius']};object-fit:cover;max-height:320px}}
.check-list{{list-style:none;padding:0}}
.check-list li{{padding:0.35rem 0 0.35rem 1.6rem;position:relative;color:{c['text_secondary']};font-size:0.92rem}}
.check-list li::before{{content:'\\2713';position:absolute;left:0;top:0.35rem;color:{c['primary']};font-weight:700;font-size:0.85rem}}

/* Quick steps (horizontal action labels + detail) */
.quick-steps{{margin:{l['section_spacing']} 0}}
.q-step{{display:flex;gap:0.75rem;align-items:flex-start;margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid {c['border']}}}
.q-step:last-child{{border-bottom:none}}
.q-step-num{{flex-shrink:0;width:{nl['circle_size']};height:{nl['circle_size']};border-radius:50%;background:{nl['circle_bg']};color:{nl['circle_color']};font-weight:700;display:flex;align-items:center;justify-content:center;font-size:0.85rem}}
.q-step-body .action{{font-weight:700;color:{c['text_primary']};font-size:0.95rem}}
.q-step-body .detail{{color:{c['text_secondary']};font-size:0.9rem;margin-top:0.15rem}}

/* Substitutions grid */
.subs-grid{{display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin:{l['section_spacing']} 0}}
.sub-card{{background:{c['background']};border:1px solid {c['border']};border-radius:8px;padding:0.75rem 1rem}}
.sub-original{{font-size:0.8rem;color:{c['text_secondary']};text-decoration:line-through}}
.sub-swap{{font-weight:600;color:{c['primary']};font-size:0.92rem}}
.sub-note{{font-size:0.78rem;color:{c['text_secondary']};margin-top:0.15rem}}

/* Quick tips */
.quick-tips{{margin:{l['section_spacing']} 0}}
.qt-item{{display:flex;gap:0.6rem;align-items:flex-start;margin-bottom:0.6rem;color:{c['text_secondary']};font-size:0.92rem}}
.qt-icon{{color:{c['primary']};font-weight:700;flex-shrink:0}}

/* FAQ */
.faq-section{{margin:{l['section_spacing']} 0}}
.faq-item{{border:1px solid {c['border']};border-radius:8px;margin-bottom:0.4rem;overflow:hidden}}
.faq-question{{width:100%;background:{c['container_bg']};border:none;text-align:left;padding:0.85rem 1rem;font-family:{hf};font-size:0.9rem;font-weight:600;color:{c['text_primary']};cursor:pointer;display:flex;justify-content:space-between}}
.faq-question::after{{content:'+';font-size:1.1rem;color:{c['primary']}}}
.faq-question.open::after{{content:'\\2212'}}
.faq-answer{{display:none;padding:0.6rem 1rem 0.8rem;color:{c['text_secondary']};border-top:1px solid {c['border']};font-size:0.9rem}}
.faq-answer.open{{display:block}}

/* Recipe card */
.recipe-card{{background:{rc['bg']};border:{rc['border']};border-radius:{rc['border_radius']};overflow:hidden;margin:{l['section_spacing']} 0}}
.recipe-card-header{{background:{rc['header_bg']};color:{rc['header_color']};padding:1rem 1.5rem;text-align:center}}
.recipe-card-header h2{{margin:0;color:{rc['header_color']};font-size:1.3rem}}
.recipe-card-body{{padding:1.5rem}}
.recipe-card-image{{width:100%;height:240px;object-fit:cover;display:block}}
.recipe-card-buttons{{display:flex;gap:0.6rem;margin:0.8rem 0}}
.btn-print,.btn-pin{{flex:1;color:#fff;border:none;padding:0.65rem 0.8rem;border-radius:8px;cursor:pointer;font-weight:600;font-size:0.85rem;transition:background 0.2s}}
.btn-print{{background:{c['button_print']}}}.btn-print:hover{{background:{c['button_hover_print']}}}
.btn-pin{{background:{c['button_pin']}}}.btn-pin:hover{{background:{c['button_hover_pin']}}}
.recipe-meta{{display:flex;flex-wrap:wrap;border:1px solid {c['border']};border-radius:8px;margin:0.8rem 0}}
.recipe-meta-item{{flex:1;text-align:center;padding:0.6rem 0.4rem;border-right:1px solid {c['border']}}}
.recipe-meta-item:last-child{{border-right:none}}
.recipe-meta-label{{font-size:0.58rem;text-transform:uppercase;color:{c['text_secondary']};letter-spacing:0.08em}}
.recipe-meta-value{{font-size:0.9rem;font-weight:700;color:{rc['meta_icon_color']};display:block;margin-top:2px}}
.recipe-ingredients-list{{list-style:none;padding:0}}.recipe-ingredients-list li{{padding:0.35rem 0 0.35rem 1.4rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}.recipe-ingredients-list li:last-child{{border-bottom:none}}.recipe-ingredients-list li::before{{content:'\\2713';position:absolute;left:0;top:0.4rem;color:{c['list_marker']};font-size:0.8rem}}
.recipe-instructions-list{{list-style:none;padding:0;counter-reset:rstep}}.recipe-instructions-list li{{counter-increment:rstep;padding:0.5rem 0 0.5rem 2.2rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}.recipe-instructions-list li:last-child{{border-bottom:none}}.recipe-instructions-list li::before{{content:counter(rstep);position:absolute;left:0;top:0.4rem;width:22px;height:22px;background:{nl['circle_bg']};color:{nl['circle_color']};border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.7rem}}

@media print{{body{{background:#fff}}.recipe-card-buttons{{display:none}}}}
@media(max-width:640px){{.ing-section,.subs-grid{{grid-template-columns:1fr}}.recipe-card-buttons{{flex-direction:column}}h1{{font-size:1.5rem}}}}"""

    def generate_html(self, sections, css_filename="css.css"):
        t = self.title; imgs = self.config["images"]
        main_img = imgs.get("main_article_image") or "placeholder.jpg"
        ing_img = imgs.get("ingredient_image") or "placeholder.jpg"
        card_img = imgs.get("recipe_card_image") or main_img
        sec = {s["key"]: s["content"] for s in sections}

        hook = sec.get("hook", "")
        diff = sec.get("difficulty", "Medium")
        ing_list = sec.get("ingredient_list", [])
        steps = sec.get("steps", [])
        subs = sec.get("substitutions", [])
        tips = sec.get("quick_tips", [])
        faqs = sec.get("faqs", [])
        wrap_up = sec.get("wrap_up", "")

        il = "".join(f'<li>{x}</li>\n' for x in ing_list)
        sh = ""
        for i, s in enumerate(steps):
            sh += f'<div class="q-step"><span class="q-step-num">{i+1}</span><div class="q-step-body"><div class="action">{s.get("action","")}</div><div class="detail">{s.get("detail","")}</div></div></div>\n'
        sub_h = "".join(f'<div class="sub-card"><div class="sub-original">{s.get("original","")}</div><div class="sub-swap">{s.get("swap","")}</div><div class="sub-note">{s.get("note","")}</div></div>\n' for s in subs)
        tips_h = "".join(f'<div class="qt-item"><span class="qt-icon">&#10148;</span><span>{tip}</span></div>\n' for tip in tips)
        faq_h = "".join(f'<div class="faq-item"><button class="faq-question" onclick="toggleFaq(this)">{fq.get("question","")}</button><div class="faq-answer">{fq.get("answer","")}</div></div>\n' for fq in faqs)

        recipe = sec.get("recipe") or {}
        if not isinstance(recipe, dict): recipe = {}
        r = {**{"name": t, "prep_time": "15 min", "cook_time": "30 min", "total_time": "45 min", "servings": "4", "calories": ""}, **recipe}
        ri = "".join(f"<li>{x}</li>\n" for x in recipe.get("ingredients", []))
        ris = "".join(f"<li>{x}</li>\n" for x in recipe.get("instructions", []))

        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{t}</title><link rel="stylesheet" href="{css_filename}">
<!-- inject:head-end --></head>
<body>
<div class="article-container">

<header class="g14-header">
  <h1 class="article-title">{t}</h1>
  <div class="byline-row">
    <span>By <span class="article-author"></span></span>
    <span>Published <span class="article-date"></span></span>
  </div>
</header>

<div class="glance-card">
  <div class="glance-item"><span class="glance-label">Prep</span><span class="glance-value">{r['prep_time']}</span></div>
  <div class="glance-item"><span class="glance-label">Cook</span><span class="glance-value">{r['cook_time']}</span></div>
  <div class="glance-item"><span class="glance-label">Total</span><span class="glance-value">{r['total_time']}</span></div>
  <div class="glance-item"><span class="glance-label">Servings</span><span class="glance-value">{r['servings']}</span></div>
  <div class="glance-item"><span class="glance-label">Difficulty</span><span class="glance-value">{diff}</span></div>
</div>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<p class="hook-text">{hook}</p>

<div class="ing-section">
  <div>
    <h2>Ingredients</h2>
    <ul class="check-list">
{il}    </ul>
  </div>
  <img src="{ing_img}" alt="Ingredients for {t}" class="ing-image">
</div>

<h2>How to Make It</h2>
<div class="quick-steps">
{sh}</div>

<h2>Easy Swaps</h2>
<div class="subs-grid">
{sub_h}</div>

<h2>Quick Tips</h2>
<div class="quick-tips">
{tips_h}</div>

<div class="faq-section">
  <h2>Quick Answers</h2>
{faq_h}</div>

<p>{wrap_up}</p>

<!-- inject:before-recipe -->
<div class="recipe-card" id="recipe-card">
  <img src="{card_img}" alt="{r['name']}" class="recipe-card-image">
  <div class="recipe-card-header"><h2>{r['name']}</h2></div>
  <div class="recipe-card-body">
    <div class="recipe-meta">
      <div class="recipe-meta-item"><span class="recipe-meta-label">Prep</span><span class="recipe-meta-value">{r['prep_time']}</span></div>
      <div class="recipe-meta-item"><span class="recipe-meta-label">Cook</span><span class="recipe-meta-value">{r['cook_time']}</span></div>
      <div class="recipe-meta-item"><span class="recipe-meta-label">Total</span><span class="recipe-meta-value">{r['total_time']}</span></div>
      <div class="recipe-meta-item"><span class="recipe-meta-label">Servings</span><span class="recipe-meta-value">{r['servings']}</span></div>
      <div class="recipe-meta-item"><span class="recipe-meta-label">Cal</span><span class="recipe-meta-value">{r['calories']}</span></div>
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
<script>function toggleFaq(btn){{btn.classList.toggle('open');btn.nextElementSibling.classList.toggle('open');}}</script>
</body></html>"""

    def run(self, return_content_only=False):
        if not self.title: raise ValueError("CONFIG['title'] is required")
        cd = self.generate_content(); css = self.generate_css(); html = self.generate_html(cd["sections"])
        cd["article_html"] = html; cd["article_css"] = css
        if return_content_only: return cd
        slug = self.slug; os.makedirs(slug, exist_ok=True)
        for n, ct in [("content.json", json.dumps(cd, indent=2)), ("article.html", html), ("css.css", css)]:
            with open(os.path.join(slug, n), "w", encoding="utf-8") as fh: fh.write(ct)
        print(f"[OK] Saved to: {slug}/"); return cd

if __name__ == "__main__":
    gen = ArticleGenerator({"title": "15-Minute Garlic Shrimp Pasta"})
    gen.run()
