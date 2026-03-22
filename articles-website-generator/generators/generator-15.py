"""
generator-15.py  —  Chef's Masterclass
---------------------------------------
Teaching-style article.  Starts with a skill-level badge, lesson-style
intro, technique breakdown before ingredients, mise-en-place section,
step-by-step tutorial with technique notes, common mistakes to avoid,
and a "level up" advanced tips section.
Deep navy palette, Playfair Display + Outfit.
"""

import os, json, re
from dotenv import load_dotenv
load_dotenv()

CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary": "#1e3a5f", "secondary": "#e07a5f", "accent": "#e07a5f",
        "background": "#f5f5f0", "container_bg": "#ffffff", "border": "#ddd8d0",
        "text_primary": "#1a1a2e", "text_secondary": "#4a4a5a",
        "button_print": "#1e3a5f", "button_pin": "#e07a5f",
        "button_hover_print": "#152d4a", "button_hover_pin": "#c9654a",
        "link": "#1e3a5f", "list_marker": "#e07a5f",
    },
    "fonts": {
        "heading": {"family": "Playfair Display", "weights": [400, 700],
                    "sizes": {"h1": "2.3rem", "h2": "1.5rem", "h3": "1.1rem"}},
        "body": {"family": "Outfit", "weight": 400, "size": "1rem", "line_height": 1.75},
    },
    "layout": {
        "max_width": "800px", "section_spacing": "2.5rem",
        "paragraph_spacing": "1.1rem", "list_spacing": "0.5rem",
        "container_padding": "2.25rem", "border_radius": "8px",
        "box_shadow": "0 2px 12px rgba(0,0,0,0.05)",
    },
    "components": {
        "numbered_list": {"style": "circle", "circle_bg": "#1e3a5f", "circle_color": "#fff", "circle_size": "32px"},
        "bullet_list": {"style": "dash", "color": "#e07a5f"},
        "pro_tips_box": {"bg_color": "#f0ebe3", "border_color": "#1e3a5f", "border_left": "4px solid #1e3a5f", "padding": "1.5rem"},
        "recipe_card": {"bg": "#fff", "border": "2px solid #ddd8d0", "border_radius": "8px", "padding": "0",
                        "meta_icon_color": "#1e3a5f", "header_bg": "#1e3a5f", "header_color": "#f5f5f0"},
    },
    "images": {"main_article_image": "", "ingredient_image": "", "recipe_card_image": ""},
    "structure_template": {"word_counts": {"lesson_intro": 120, "technique": 100, "mise_en_place": 40, "tutorial_step": 80, "mistake": 40, "level_up": 50}},
    "dark_mode": False,
}

STRUCTURE = [
    {"key": "skill_badge",     "type": "badge",       "label": ""},
    {"key": "lesson_intro",    "type": "intro",       "label": "Today's Lesson"},
    {"key": "technique_focus", "type": "technique",   "label": "Technique Spotlight"},
    {"key": "mise_en_place",   "type": "ingredients", "label": "Mise en Place"},
    {"key": "tutorial_steps",  "type": "tutorial",    "label": "Step-by-Step Tutorial"},
    {"key": "common_mistakes", "type": "mistakes",    "label": "Common Mistakes to Avoid"},
    {"key": "level_up",        "type": "advanced",    "label": "Level Up"},
    {"key": "faqs",            "type": "faq",         "label": "Student Questions"},
    {"key": "wrap",            "type": "conclusion",  "label": ""},
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

    def _slugify(self, t): return re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", t.lower()).strip()) or "article"

    def _strip_md(self, t):
        if not t or not isinstance(t, str): return t
        s = re.sub(r'^#{1,6}\s*', '', t.strip()); s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s); return re.sub(r'\*([^*]+)\*', r'\1', s).strip()

    def _chat(self, prompt, mt=500):
        from ai_client import ai_chat
        sys = ("You are a professional culinary instructor. Write as if teaching a cooking class — "
               "clear, confident, educational. Explain WHY, not just how. Plain text only. "
               f"All content about: {self.title}.")
        return self._strip_md(ai_chat(self, prompt, max_tokens=mt, system=sys) or "")

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
            "skill_level": "string — Beginner, Intermediate, or Advanced",
            "lesson_intro": "string ~120 words — welcome students, explain what they'll learn",
            "technique_name": "string — name of the key technique (e.g. 'Braising', 'Tempering Chocolate')",
            "technique_explanation": "string ~100 words — explain the technique and why it matters",
            "mise_en_place_intro": "string ~40 words",
            "ingredient_list": "array of 10 strings with measurements",
            "tutorial_steps": "array of 5 objects {instruction, technique_note} — instruction is the step, technique_note explains the WHY",
            "common_mistakes": "array of 3 objects {mistake, fix} — things beginners get wrong",
            "level_up_tips": "array of 3 strings — advanced tips to elevate the dish",
            "faqs": "array of 3 objects {question, answer}",
            "wrap": "string ~60 words — encouraging conclusion",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine",
            "meta_description": "120-140 chars", "focus_keyphrase": "string",
            "pinterest_title": "string", "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        sys = "You are a professional culinary instructor. Generate the full masterclass article as ONE JSON. Plain text. All about the recipe title."
        user = f"Generate a chef's masterclass article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=5000, system=sys)
        d = self._xj(raw)

        if d:
            print("[*] Chef's Masterclass — single-JSON.")
            skill = str(d.get("skill_level", "Intermediate"))
            lesson = self._strip_md(str(d.get("lesson_intro", "")))
            tech_name = str(d.get("technique_name", "Key Technique"))
            tech_exp = self._strip_md(str(d.get("technique_explanation", "")))
            mise_intro = self._strip_md(str(d.get("mise_en_place_intro", "")))
            ing_list = [str(x).strip() for x in (d.get("ingredient_list") or [])[:12]]
            steps_raw = d.get("tutorial_steps") or []
            steps = [{"instruction": self._strip_md(str(s.get("instruction","")) if isinstance(s,dict) else ""),
                      "technique_note": self._strip_md(str(s.get("technique_note","")) if isinstance(s,dict) else "")}
                     for s in steps_raw[:5]]
            mistakes_raw = d.get("common_mistakes") or []
            mistakes = [{"mistake": str(m.get("mistake","")).strip(), "fix": str(m.get("fix","")).strip()}
                        for m in mistakes_raw[:3] if isinstance(m, dict)]
            levelup = [self._strip_md(str(x)) for x in (d.get("level_up_tips") or [])[:3]]
            faqs_raw = d.get("faqs") or []
            faqs = [{"question": str(f.get("question","")).strip(), "answer": self._strip_md(str(f.get("answer","")))} for f in faqs_raw[:3] if isinstance(f, dict)]
            wrap = self._strip_md(str(d.get("wrap", "")))
            recipe = d.get("recipe") or {}
            if not isinstance(recipe, dict): recipe = {}
        else:
            print("[*] Chef's Masterclass — sequential.")
            skill = "Intermediate"
            lesson = self._chat(f"Write a 120-word lesson intro for {self.title}. Welcome students.", 250)
            tech_name = "Key Technique"
            tech_exp = self._chat(f"Explain the key cooking technique behind {self.title} in ~100 words.", 200)
            mise_intro = self._chat(f"Write a 40-word intro for mise en place of {self.title}.", 100)
            raw = self._chat(f"List 10 ingredients for {self.title} with measurements. One per line.", 200)
            ing_list = [l.strip() for l in raw.splitlines() if l.strip()][:12]
            steps = []
            for i in range(1, 6):
                raw = self._chat(f"Step {i} of {self.title} tutorial. Format:\nINSTRUCTION: <what to do>\nTECHNIQUE_NOTE: <why this matters>", 200)
                inst, tn = f"Step {i}", ""
                for line in (raw or "").splitlines():
                    s = line.strip()
                    if s.upper().startswith("INSTRUCTION:"): inst = s.split(":", 1)[-1].strip()
                    elif s.upper().startswith("TECHNIQUE_NOTE:"): tn = s.split(":", 1)[-1].strip()
                steps.append({"instruction": inst, "technique_note": tn})
            raw = self._chat(f"List 3 common mistakes when making {self.title}. Format: MISTAKE: ...\nFIX: ...", 250)
            mistakes = [{"mistake": "Overcooking", "fix": "Watch carefully."}]
            raw = self._chat(f"Give 3 advanced tips to level up {self.title}. One per line.", 150)
            levelup = [self._strip_md(l.strip()) for l in raw.splitlines() if l.strip()][:3]
            raw = self._chat(f"Write 3 FAQ pairs for {self.title}. Q1:...\nA1:...\nQ2:...\nA2:...\nQ3:...\nA3:...", 400)
            faqs = []
            for i in range(1, 4):
                q = a = None
                for line in raw.splitlines():
                    ls = line.strip()
                    if ls.upper().startswith(f"Q{i}:"): q = ls.split(":", 1)[-1].strip()
                    elif ls.upper().startswith(f"A{i}:"): a = ls.split(":", 1)[-1].strip()
                faqs.append({"question": q or f"How do I know when {self.title} is done?", "answer": a or ""})
            wrap = self._chat(f"Write a 60-word encouraging conclusion for the {self.title} masterclass.", 120)
            recipe = {}; d = {}

        if not recipe.get("ingredients") and ing_list: recipe["ingredients"] = list(ing_list)[:20]
        if not recipe.get("instructions") and steps: recipe["instructions"] = [s.get("instruction", "") for s in steps][:15]
        for k, dv in {"name": self.title, "summary": f"Master {self.title} with this tutorial.", "prep_time": "25 min", "cook_time": "40 min", "total_time": "1 hr 5 min", "servings": "4", "calories": "420", "course": "Main Course", "cuisine": "International"}.items():
            recipe.setdefault(k, dv)

        from ai_client import get_first_category
        cat = get_first_category(self.config)
        main_img = self.config["images"].get("main_article_image") or "placeholder.jpg"
        mj_m = str(d.get("prompt_midjourney_main", "") or "").strip()
        mj_i = str(d.get("prompt_midjourney_ingredients", "") or "").strip()

        sections = [
            {"key": "skill_level", "content": skill}, {"key": "lesson_intro", "content": lesson},
            {"key": "technique_name", "content": tech_name}, {"key": "technique_explanation", "content": tech_exp},
            {"key": "mise_en_place_intro", "content": mise_intro}, {"key": "ingredient_list", "content": ing_list},
            {"key": "tutorial_steps", "content": steps}, {"key": "common_mistakes", "content": mistakes},
            {"key": "level_up_tips", "content": levelup}, {"key": "faqs", "content": faqs},
            {"key": "wrap", "content": wrap},
        ]
        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": f"generator-15 / title: {self.title}",
            "prompt_base": f"Chef's Masterclass for: {self.title}",
            "recipe": recipe,
            "recipe_title_pin": (str(d.get("pinterest_title", self.title)) or self.title)[:100],
            "pinterest_title": (str(d.get("pinterest_title", "")) or self.title)[:100],
            "pinterest_description": f"Master {self.title} like a pro chef!",
            "pinterest_keywords": f"{self.title}, cooking technique, masterclass, tutorial",
            "focus_keyphrase": str(d.get("focus_keyphrase", self.title.lower())),
            "meta_description": (str(d.get("meta_description", "")) or f"Learn to cook {self.title} like a pro in this chef's masterclass.")[:140],
            "keyphrase_synonyms": f"{self.title} recipe, how to make {self.title}, {self.title} tutorial",
            "main_image": main_img,
            "ingredient_image": self.config["images"].get("ingredient_image") or "placeholder.jpg",
            "prompt_midjourney_main": mj_m if mj_m and "--v 6.1" in mj_m else f"Professional culinary photography of {self.title}, chef plating, dramatic light --v 6.1",
            "prompt_midjourney_ingredients": mj_i if mj_i and "--v 6.1" in mj_i else f"Mise en place flat-lay for {self.title}, organized bowls, marble surface --v 6.1",
        }

    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url
        c = self.config["colors"]; f = self.config["fonts"]; l = self.config["layout"]
        cp = self.config["components"]; nl = cp["numbered_list"]; pt = cp["pro_tips_box"]; rc = cp["recipe_card"]
        iu = build_font_import_url(f)
        bf = font_family_css(f["body"]["family"], "sans-serif")
        hf = font_family_css(f["heading"]["family"], "serif")

        return f"""/* generator-15 | Chef's Masterclass */
@import url('{iu}');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{c['background']};color:{c['text_primary']};font-family:{bf};font-size:{f['body']['size']};font-weight:{f['body']['weight']};line-height:{f['body']['line_height']};-webkit-font-smoothing:antialiased}}
.article-container{{max-width:{l['max_width']};margin:2rem auto;padding:{l['container_padding']};background:{c['container_bg']};border-radius:{l['border_radius']};box-shadow:{l['box_shadow']}}}

.g15-header{{margin-bottom:{l['section_spacing']}}}
.g15-header .article-title{{font-family:{hf};font-size:{f['heading']['sizes']['h1']};color:{c['text_primary']};margin-bottom:0.4rem}}
.g15-header .byline-row{{font-size:0.82rem;color:{c['text_secondary']}}}
h2{{font-family:{hf};font-size:{f['heading']['sizes']['h2']};color:{c['primary']};margin-top:{l['section_spacing']};margin-bottom:0.7rem}}
h3{{font-family:{hf};font-size:{f['heading']['sizes']['h3']};color:{c['text_primary']};margin-top:1rem;margin-bottom:0.3rem}}
p{{color:{c['text_secondary']};margin-bottom:{l['paragraph_spacing']}}}
a{{color:{c['link']};text-decoration:none}}a:hover{{text-decoration:underline}}
.hero-image{{width:100%;border-radius:{l['border_radius']};margin:1.25rem 0;object-fit:cover;max-height:460px;display:block}}

/* Skill badge */
.skill-badge{{display:inline-block;background:{c['primary']};color:#fff;padding:0.3rem 1rem;border-radius:20px;font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem}}

/* Technique spotlight */
.technique-box{{background:{pt['bg_color']};border-radius:{l['border_radius']};padding:1.75rem;margin:{l['section_spacing']} 0;border:1px solid {c['border']}}}
.technique-box .tech-name{{font-family:{hf};font-size:1.2rem;color:{c['primary']};margin-bottom:0.5rem;font-weight:700}}
.technique-box p{{margin:0}}

/* Mise en place (grid: image + list) */
.mise-section{{display:grid;grid-template-columns:1fr 1fr;gap:2rem;margin:{l['section_spacing']} 0;align-items:start}}
.mise-image{{width:100%;border-radius:{l['border_radius']};object-fit:cover;max-height:350px}}
.mise-list{{list-style:none;padding:0}}
.mise-list li{{padding:0.4rem 0 0.4rem 1.5rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}
.mise-list li:last-child{{border-bottom:none}}
.mise-list li::before{{content:'\\2014';position:absolute;left:0;top:0.4rem;color:{c['list_marker']};font-weight:700}}

/* Tutorial steps (two-part: instruction + technique note) */
.tutorial-steps{{margin:{l['section_spacing']} 0}}
.tut-step{{display:flex;gap:1rem;margin-bottom:1.5rem;padding-bottom:1.5rem;border-bottom:1px solid {c['border']}}}
.tut-step:last-child{{border-bottom:none}}
.tut-num{{flex-shrink:0;width:{nl['circle_size']};height:{nl['circle_size']};border-radius:50%;background:{nl['circle_bg']};color:{nl['circle_color']};font-weight:700;display:flex;align-items:center;justify-content:center}}
.tut-body .tut-instruction{{color:{c['text_primary']};font-weight:500;margin-bottom:0.3rem}}
.tut-body .tut-note{{font-size:0.88rem;color:{c['secondary']};font-style:italic;padding-left:0.75rem;border-left:2px solid {c['secondary']}}}

/* Mistakes */
.mistakes-section{{margin:{l['section_spacing']} 0}}
.mistake-card{{background:#fdf0ed;border:1px solid #f0c4b8;border-radius:{l['border_radius']};padding:1rem 1.25rem;margin-bottom:0.75rem}}
.mistake-label{{font-weight:700;color:#c0392b;font-size:0.85rem;text-transform:uppercase;margin-bottom:0.2rem}}
.mistake-fix{{color:{c['text_secondary']};font-size:0.92rem}}
.mistake-fix strong{{color:{c['primary']}}}

/* Level up */
.levelup-section{{margin:{l['section_spacing']} 0}}
.levelup-item{{display:flex;gap:0.6rem;margin-bottom:0.5rem;color:{c['text_secondary']}}}
.levelup-icon{{color:{c['secondary']};font-size:1.1rem;flex-shrink:0}}

/* FAQ */
.faq-section{{margin:{l['section_spacing']} 0}}
.faq-item{{border:1px solid {c['border']};border-radius:{l['border_radius']};margin-bottom:0.5rem;overflow:hidden}}
.faq-question{{width:100%;background:{c['container_bg']};border:none;text-align:left;padding:0.9rem 1.1rem;font-family:{hf};font-size:0.92rem;font-weight:600;color:{c['text_primary']};cursor:pointer;display:flex;justify-content:space-between}}
.faq-question::after{{content:'+';font-size:1.2rem;color:{c['primary']}}}
.faq-question.open::after{{content:'\\2212'}}
.faq-answer{{display:none;padding:0.6rem 1.1rem 0.9rem;color:{c['text_secondary']};border-top:1px solid {c['border']};font-size:0.92rem}}
.faq-answer.open{{display:block}}

/* Recipe card */
.recipe-card{{background:{rc['bg']};border:{rc['border']};border-radius:{rc['border_radius']};overflow:hidden;margin:{l['section_spacing']} 0;box-shadow:{l['box_shadow']}}}
.recipe-card-header{{background:{rc['header_bg']};color:{rc['header_color']};padding:1.1rem 1.5rem;text-align:center}}
.recipe-card-header h2{{margin:0;color:{rc['header_color']};font-size:1.35rem}}
.recipe-card-body{{padding:1.5rem}}
.recipe-card-image{{width:100%;height:250px;object-fit:cover;display:block}}
.recipe-card-buttons{{display:flex;gap:0.65rem;margin:0.8rem 0}}
.btn-print,.btn-pin{{flex:1;color:#fff;border:none;padding:0.7rem 0.9rem;border-radius:{l['border_radius']};cursor:pointer;font-weight:600;font-size:0.88rem;transition:background 0.2s}}
.btn-print{{background:{c['button_print']}}}.btn-print:hover{{background:{c['button_hover_print']}}}
.btn-pin{{background:{c['button_pin']}}}.btn-pin:hover{{background:{c['button_hover_pin']}}}
.recipe-meta{{display:flex;flex-wrap:wrap;border:1px solid {c['border']};border-radius:{l['border_radius']};margin:0.8rem 0}}
.recipe-meta-item{{flex:1;text-align:center;padding:0.65rem 0.4rem;border-right:1px solid {c['border']}}}
.recipe-meta-item:last-child{{border-right:none}}
.recipe-meta-label{{font-size:0.6rem;text-transform:uppercase;color:{c['text_secondary']};letter-spacing:0.08em}}
.recipe-meta-value{{font-size:0.92rem;font-weight:700;color:{rc['meta_icon_color']};display:block;margin-top:2px}}
.recipe-ingredients-list{{list-style:none;padding:0}}.recipe-ingredients-list li{{padding:0.35rem 0 0.35rem 1.4rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}.recipe-ingredients-list li:last-child{{border-bottom:none}}.recipe-ingredients-list li::before{{content:'\\2014';position:absolute;left:0;top:0.4rem;color:{c['list_marker']};font-weight:700}}
.recipe-instructions-list{{list-style:none;padding:0;counter-reset:rstep}}.recipe-instructions-list li{{counter-increment:rstep;padding:0.5rem 0 0.5rem 2.4rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}.recipe-instructions-list li:last-child{{border-bottom:none}}.recipe-instructions-list li::before{{content:counter(rstep);position:absolute;left:0;top:0.38rem;width:24px;height:24px;background:{nl['circle_bg']};color:{nl['circle_color']};border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.75rem}}

@media print{{body{{background:#fff}}.recipe-card-buttons{{display:none}}}}
@media(max-width:700px){{.mise-section{{grid-template-columns:1fr}}.recipe-card-buttons{{flex-direction:column}}h1{{font-size:1.6rem}}}}"""

    def generate_html(self, sections, css_filename="css.css"):
        t = self.title; imgs = self.config["images"]
        main_img = imgs.get("main_article_image") or "placeholder.jpg"
        ing_img = imgs.get("ingredient_image") or "placeholder.jpg"
        card_img = imgs.get("recipe_card_image") or main_img
        sec = {s["key"]: s["content"] for s in sections}

        skill = sec.get("skill_level", "Intermediate")
        lesson = sec.get("lesson_intro", "")
        tech_name = sec.get("technique_name", "Key Technique")
        tech_exp = sec.get("technique_explanation", "")
        mise_intro = sec.get("mise_en_place_intro", "")
        ing_list = sec.get("ingredient_list", [])
        steps = sec.get("tutorial_steps", [])
        mistakes = sec.get("common_mistakes", [])
        levelup = sec.get("level_up_tips", [])
        faqs = sec.get("faqs", [])
        wrap = sec.get("wrap", "")

        il = "".join(f"<li>{x}</li>\n" for x in ing_list)
        sh = ""
        for i, s in enumerate(steps):
            sh += f'<div class="tut-step"><span class="tut-num">{i+1}</span><div class="tut-body"><div class="tut-instruction">{s.get("instruction","")}</div><div class="tut-note">&#128161; {s.get("technique_note","")}</div></div></div>\n'
        mh = "".join(f'<div class="mistake-card"><div class="mistake-label">&#10060; {m.get("mistake","")}</div><div class="mistake-fix"><strong>Fix:</strong> {m.get("fix","")}</div></div>\n' for m in mistakes)
        lh = "".join(f'<div class="levelup-item"><span class="levelup-icon">&#11088;</span><span>{tip}</span></div>\n' for tip in levelup)
        fh = "".join(f'<div class="faq-item"><button class="faq-question" onclick="toggleFaq(this)">{fq.get("question","")}</button><div class="faq-answer">{fq.get("answer","")}</div></div>\n' for fq in faqs)

        recipe = sec.get("recipe") or {}
        if not isinstance(recipe, dict): recipe = {}
        r = {**{"name": t, "prep_time": "25 min", "cook_time": "40 min", "total_time": "1 hr 5 min", "servings": "4", "calories": ""}, **recipe}
        ri = "".join(f"<li>{x}</li>\n" for x in recipe.get("ingredients", []))
        ris = "".join(f"<li>{x}</li>\n" for x in recipe.get("instructions", []))

        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{t}</title><link rel="stylesheet" href="{css_filename}">
<!-- inject:head-end --></head>
<body>
<div class="article-container">
<header class="g15-header">
  <span class="skill-badge">{skill}</span>
  <h1 class="article-title">{t}</h1>
  <div class="byline-row">By <span class="article-author"></span> &middot; Published <span class="article-date"></span></div>
</header>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<h2>Today's Lesson</h2>
<p>{lesson}</p>

<div class="technique-box">
  <div class="tech-name">&#128296; Technique: {tech_name}</div>
  <p>{tech_exp}</p>
</div>

<h2>Mise en Place</h2>
<p>{mise_intro}</p>
<div class="mise-section">
  <ul class="mise-list">
{il}  </ul>
  <img src="{ing_img}" alt="Mise en place for {t}" class="mise-image">
</div>

<h2>Step-by-Step Tutorial</h2>
<div class="tutorial-steps">
{sh}</div>

<h2>Common Mistakes to Avoid</h2>
<div class="mistakes-section">
{mh}</div>

<h2>Level Up &#11088;</h2>
<div class="levelup-section">
{lh}</div>

<div class="faq-section">
  <h2>Student Questions</h2>
{fh}</div>

<p>{wrap}</p>

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
    gen = ArticleGenerator({"title": "Perfect Pan-Seared Salmon"})
    gen.run()
