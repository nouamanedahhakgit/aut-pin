"""
generator-13.py  —  Story Kitchen
----------------------------------
Personal narrative recipe blog.  The article reads like a short memoir:
a warm personal story first, then a "secret" reveal, ingredients shown
alongside an ingredient image, narrative-style steps, and a nostalgic
conclusion.   Warm amber palette, Lora + Source Serif Pro.
"""

import os, json, re
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "title": "",
    "categories_list": [{"id": 1, "categorie": "dinner"}],
    "colors": {
        "primary": "#b8860b", "secondary": "#6b4226", "accent": "#d4a853",
        "background": "#faf6ef", "container_bg": "#ffffff", "border": "#e8dcc5",
        "text_primary": "#2c1b0e", "text_secondary": "#5e4b3a",
        "button_print": "#6b4226", "button_pin": "#b8860b",
        "button_hover_print": "#4a2e1a", "button_hover_pin": "#96700a",
        "link": "#b8860b", "list_marker": "#b8860b",
    },
    "fonts": {
        "heading": {"family": "Lora", "weights": [400, 600, 700],
                    "sizes": {"h1": "2.4rem", "h2": "1.55rem", "h3": "1.15rem"}},
        "body": {"family": "Source Serif Pro", "weight": 400,
                 "size": "1.05rem", "line_height": 1.85},
    },
    "layout": {
        "max_width": "780px", "section_spacing": "2.5rem",
        "paragraph_spacing": "1.15rem", "list_spacing": "0.5rem",
        "container_padding": "2.25rem", "border_radius": "10px",
        "box_shadow": "0 4px 20px rgba(0,0,0,0.06)",
    },
    "components": {
        "numbered_list": {"style": "circle", "circle_bg": "#b8860b",
                          "circle_color": "#fff", "circle_size": "32px"},
        "bullet_list": {"style": "disc", "color": "#b8860b"},
        "pro_tips_box": {"bg_color": "#fdf5e6", "border_color": "#b8860b",
                         "border_left": "4px solid #b8860b", "padding": "1.5rem"},
        "recipe_card": {"bg": "#fff", "border": "2px solid #e8dcc5",
                        "border_radius": "10px", "padding": "0",
                        "meta_icon_color": "#b8860b",
                        "header_bg": "#6b4226", "header_color": "#fdf5e6"},
    },
    "images": {"main_article_image": "", "ingredient_image": "", "recipe_card_image": ""},
    "structure_template": {"word_counts": {
        "personal_story": 180, "the_secret": 100, "ingredients_intro": 50,
        "step_narrative": 90, "memory_conclusion": 100,
        "faq_answer": 55,
    }},
    "dark_mode": False,
}

STRUCTURE = [
    {"key": "personal_story",    "type": "narrative",   "label": "A Memory from My Kitchen"},
    {"key": "the_secret",        "type": "reveal_box",  "label": "The Secret"},
    {"key": "ingredients_showcase","type": "ingredients","label": "What You'll Need"},
    {"key": "step_narrative",    "type": "narrative_steps","label": "How I Make It"},
    {"key": "tips_from_heart",   "type": "callout",     "label": "Tips From the Heart"},
    {"key": "faqs",              "type": "faq",         "label": "You Might Be Wondering"},
    {"key": "memory_conclusion", "type": "conclusion",  "label": ""},
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

    def _merge(self, b, o):
        for k, v in o.items():
            if k in b and isinstance(b[k], dict) and isinstance(v, dict):
                self._merge(b[k], v)
            else:
                b[k] = v

    def _slugify(self, t):
        return re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", t.lower()).strip()) or "article"

    def _strip_md(self, t):
        if not t or not isinstance(t, str): return t
        s = re.sub(r'^#{1,6}\s*', '', t.strip())
        s = re.sub(r'\n#{1,6}\s*', '\n', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'\*([^*]+)\*', r'\1', s)
        return s.strip()

    def _chat(self, prompt, max_tokens=500):
        from ai_client import ai_chat
        sys = (
            "You are a warm, nostalgic home cook sharing family recipes. "
            "Write as if telling a story to a close friend at the kitchen table. "
            "Output plain text only — no markdown, no bullets, no hashtags. "
            f"All content about: {self.title}."
        )
        raw = ai_chat(self, prompt, max_tokens=max_tokens, system=sys)
        return self._strip_md(raw) if raw else ""

    def _extract_json(self, raw):
        if not raw: return {}
        text = raw.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m: text = m.group(1).strip()
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try: return json.loads(m.group())
            except Exception: pass
        try: return json.loads(text)
        except Exception: return {}

    # ---- content generation (single JSON, fallback to sequential) ----
    def generate_content(self):
        from ai_client import ai_chat
        schema = {
            "personal_story": "string ~180 words, a warm personal memory connected to this dish",
            "the_secret": "string ~100 words, the one secret that makes this recipe special",
            "ingredients_intro": "string ~50 words, warm intro to ingredients",
            "ingredient_list": "array of 10 strings with measurements",
            "steps": "array of 5 objects {title, narrative} — each ~90 words written as storytelling paragraphs, not instructions",
            "tips_from_heart": "array of 3 strings — heartfelt cooking tips",
            "faqs": "array of 4 objects {question, answer}",
            "memory_conclusion": "string ~100 words, nostalgic wrap-up encouraging reader",
            "recipe": "object: name, summary, ingredients[], instructions[], prep_time, cook_time, total_time, servings, calories, course, cuisine",
            "meta_description": "120-140 chars",
            "focus_keyphrase": "string",
            "pinterest_title": "string ≤100 chars",
            "prompt_midjourney_main": "string ending --v 6.1",
            "prompt_midjourney_ingredients": "string ending --v 6.1",
        }
        sys = "You are a warm, nostalgic home cook and storyteller. Generate the full story-recipe article as ONE JSON. Plain text only. All about the recipe title."
        user = f"Generate a complete story-kitchen recipe article for '{self.title}' as JSON with keys: {json.dumps(list(schema.keys()))}. Return ONLY valid JSON."
        raw = ai_chat(self, user, max_tokens=5000, system=sys)
        d = self._extract_json(raw)

        if d:
            print("[*] Story Kitchen — single-JSON generated.")
            personal_story = self._strip_md(str(d.get("personal_story", "")))
            the_secret     = self._strip_md(str(d.get("the_secret", "")))
            ing_intro      = self._strip_md(str(d.get("ingredients_intro", "")))
            ing_list       = [str(x).strip() for x in (d.get("ingredient_list") or [])[:12]]
            steps_raw      = d.get("steps") or []
            steps = [{"title": str(s.get("title", f"Part {i}")).strip() if isinstance(s, dict) else f"Part {i}",
                      "narrative": self._strip_md(str(s.get("narrative", "")) if isinstance(s, dict) else "")}
                     for i, s in enumerate(steps_raw[:5], 1)]
            tips = [self._strip_md(str(x)) for x in (d.get("tips_from_heart") or [])[:4]]
            faqs_raw = d.get("faqs") or []
            faqs = [{"question": str(f.get("question","")).strip(),
                     "answer": self._strip_md(str(f.get("answer","")))}
                    for f in faqs_raw[:4] if isinstance(f, dict)]
            conclusion = self._strip_md(str(d.get("memory_conclusion", "")))
            recipe = d.get("recipe") or {}
            if not isinstance(recipe, dict): recipe = {}
        else:
            print("[*] Story Kitchen — sequential generation.")
            personal_story = self._chat(f"Write a 180-word personal memory about {self.title}. Maybe your grandmother made it, or a rainy day it comforted you.", 350)
            the_secret = self._chat(f"Reveal the one secret that makes {self.title} extraordinary. ~100 words.", 200)
            ing_intro = self._chat(f"Write a warm 50-word intro to ingredients for {self.title}.", 120)
            raw = self._chat(f"List exactly 10 ingredients for {self.title} with measurements. One per line.", 200)
            ing_list = [l.strip() for l in raw.splitlines() if l.strip()][:12]
            steps = []
            for i in range(1, 6):
                raw = self._chat(f"Write part {i} of making {self.title} as a storytelling paragraph (~90 words). Format: TITLE: <short title>\nNARRATIVE: <paragraph>", 220)
                title, narrative = f"Part {i}", raw
                for line in (raw or "").splitlines():
                    s = line.strip()
                    if s.upper().startswith("TITLE:"): title = s.split(":", 1)[-1].strip() or title
                    elif s.upper().startswith("NARRATIVE:"): narrative = s.split(":", 1)[-1].strip() or narrative
                steps.append({"title": title, "narrative": narrative})
            raw = self._chat(f"Give 3 heartfelt cooking tips for {self.title}. One per line.", 180)
            tips = [self._strip_md(l.strip()) for l in raw.splitlines() if l.strip()][:4]
            raw = self._chat(f"Write 4 FAQ pairs for {self.title}. Q1: ...\nA1: ...\nQ2:...\nA2:...\nQ3:...\nA3:...\nQ4:...\nA4:...", 500)
            faqs = []
            for i in range(1, 5):
                q = a = None
                for line in raw.splitlines():
                    ls = line.strip()
                    if ls.upper().startswith(f"Q{i}:"): q = ls.split(":", 1)[-1].strip()
                    elif ls.upper().startswith(f"A{i}:"): a = ls.split(":", 1)[-1].strip()
                faqs.append({"question": q or f"Can I freeze {self.title}?", "answer": a or ""})
            conclusion = self._chat(f"Write a 100-word nostalgic conclusion for {self.title}.", 200)
            recipe = {}
            d = {}

        # fill recipe if empty
        if not recipe.get("ingredients") and ing_list:
            recipe["ingredients"] = list(ing_list)[:20]
        if not recipe.get("instructions") and steps:
            recipe["instructions"] = [s.get("narrative", "") for s in steps][:15]
        for k, dv in {"name": self.title, "summary": f"A cherished {self.title} recipe.", "prep_time": "20 min", "cook_time": "40 min", "total_time": "1 hr", "servings": "6", "calories": "400", "course": "Main Course", "cuisine": "American"}.items():
            recipe.setdefault(k, dv)

        from ai_client import get_first_category
        cat = get_first_category(self.config)
        main_img = self.config["images"].get("main_article_image") or "placeholder.jpg"
        mj_main = str(d.get("prompt_midjourney_main", "") or "").strip()
        mj_ing = str(d.get("prompt_midjourney_ingredients", "") or "").strip()

        sections = [
            {"key": "personal_story",    "content": personal_story},
            {"key": "the_secret",        "content": the_secret},
            {"key": "ingredients_intro",  "content": ing_intro},
            {"key": "ingredient_list",    "content": ing_list},
            {"key": "steps",             "content": steps},
            {"key": "tips_from_heart",   "content": tips},
            {"key": "faqs",              "content": faqs},
            {"key": "memory_conclusion", "content": conclusion},
        ]
        return {
            "title": self.title, "slug": self.slug,
            "categorieId": str(cat.get("id", 1)), "categorie": cat.get("categorie", "dinner"),
            "sections": sections, "article_html": "", "article_css": "",
            "prompt_used": f"generator-13 / title: {self.title}",
            "prompt_base": f"Story Kitchen narrative for: {self.title}",
            "recipe": recipe,
            "recipe_title_pin": (str(d.get("pinterest_title", self.title)) or self.title)[:100],
            "pinterest_title": (str(d.get("pinterest_title", "")) or self.title)[:100],
            "pinterest_description": f"The story behind my {self.title} — and how you can make it too.",
            "pinterest_keywords": f"{self.title}, recipe, family recipe, comfort food, homemade",
            "focus_keyphrase": str(d.get("focus_keyphrase", self.title.lower())),
            "meta_description": (str(d.get("meta_description", "")) or f"The personal story behind this {self.title} recipe — with tips from the heart.")[:140],
            "keyphrase_synonyms": f"{self.title} recipe, homemade {self.title}, best {self.title}",
            "main_image": main_img,
            "ingredient_image": self.config["images"].get("ingredient_image") or "placeholder.jpg",
            "prompt_midjourney_main": mj_main if mj_main and "--v 6.1" in mj_main else f"Warm storytelling food photography of {self.title}, soft window light, handwritten recipe card, wooden table --v 6.1",
            "prompt_midjourney_ingredients": mj_ing if mj_ing and "--v 6.1" in mj_ing else f"Rustic ingredient still-life for {self.title}, scattered on wooden board, warm tones --v 6.1",
        }

    # ------------------------------------------------------------------ CSS
    def generate_css(self):
        from generators.font_utils import font_family_css, build_font_import_url
        c = self.config["colors"]; f = self.config["fonts"]; l = self.config["layout"]
        cp = self.config["components"]; pt = cp["pro_tips_box"]; rc = cp["recipe_card"]
        nl = cp["numbered_list"]
        import_url = build_font_import_url(f)
        bf = font_family_css(f["body"]["family"], "serif")
        hf = font_family_css(f["heading"]["family"], "serif")

        return f"""/* generator-13 | Story Kitchen */
@import url('{import_url}');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{c['background']};color:{c['text_primary']};font-family:{bf};font-size:{f['body']['size']};font-weight:{f['body']['weight']};line-height:{f['body']['line_height']};-webkit-font-smoothing:antialiased}}
.article-container{{max-width:{l['max_width']};margin:2.5rem auto;padding:{l['container_padding']};background:{c['container_bg']};border-radius:{l['border_radius']};box-shadow:{l['box_shadow']}}}

/* header */
.g13-header{{margin-bottom:{l['section_spacing']};text-align:center}}
.g13-header .article-title{{font-family:{hf};font-size:{f['heading']['sizes']['h1']};color:{c['text_primary']};line-height:1.2;margin-bottom:0.5rem}}
.g13-header .title-flourish{{display:inline-block;width:60px;height:2px;background:{c['primary']};margin:0.5rem auto 1rem}}
.g13-header .byline-author,.g13-header .byline-date{{font-size:0.85rem;color:{c['text_secondary']}}}
.g13-header .byline-disclaimer{{font-size:0.75rem;color:{c['text_secondary']};font-style:italic;margin-top:0.3rem}}

h1{{font-family:{hf};font-size:{f['heading']['sizes']['h1']};font-weight:700;color:{c['text_primary']};line-height:1.2;margin-bottom:1rem}}
h2{{font-family:{hf};font-size:{f['heading']['sizes']['h2']};color:{c['primary']};margin-top:{l['section_spacing']};margin-bottom:0.8rem;font-weight:600;font-style:italic}}
h3{{font-family:{hf};font-size:{f['heading']['sizes']['h3']};color:{c['text_primary']};margin-top:1.2rem;margin-bottom:0.4rem}}
p{{color:{c['text_secondary']};margin-bottom:{l['paragraph_spacing']}}}
a{{color:{c['link']};text-decoration:none}}a:hover{{text-decoration:underline}}

/* hero */
.hero-image{{width:100%;height:auto;display:block;border-radius:{l['border_radius']};margin:1.5rem 0;object-fit:cover;max-height:480px}}

/* --- Personal story (italic block, left border) --- */
.story-block{{border-left:3px solid {c['primary']};padding:1.5rem 1.5rem 1.5rem 2rem;margin:{l['section_spacing']} 0;font-style:italic;color:{c['text_secondary']};line-height:1.9;background:linear-gradient(135deg,{c['container_bg']},{c['background']})}}
.story-block h2{{font-style:italic;border:none;margin-top:0}}

/* --- The Secret (reveal box) --- */
.secret-box{{background:{pt['bg_color']};border:{rc['border']};border-radius:{l['border_radius']};padding:2rem;margin:{l['section_spacing']} 0;text-align:center}}
.secret-box h2{{margin-top:0;color:{c['secondary']};font-style:normal;text-transform:uppercase;letter-spacing:0.08em;font-size:1rem}}
.secret-box .secret-icon{{font-size:2rem;color:{c['primary']};margin-bottom:0.5rem}}
.secret-box p{{font-size:1.05rem;max-width:600px;margin:0.75rem auto 0;font-style:italic}}

/* --- Ingredients showcase (side-by-side image + list) --- */
.ingredients-showcase{{display:grid;grid-template-columns:1fr 1fr;gap:2rem;align-items:start;margin:{l['section_spacing']} 0}}
.ingredients-showcase .ing-image{{width:100%;height:auto;border-radius:{l['border_radius']};object-fit:cover;max-height:380px}}
.ingredients-showcase .ing-body h2{{margin-top:0}}
.ingredients-showcase .ing-list{{list-style:none;padding:0}}
.ingredients-showcase .ing-list li{{padding:0.4rem 0 0.4rem 1.4rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}
.ingredients-showcase .ing-list li:last-child{{border-bottom:none}}
.ingredients-showcase .ing-list li::before{{content:'\\25CF';position:absolute;left:0;top:0.45rem;color:{c['list_marker']};font-size:0.5rem}}

/* --- Narrative steps (alternating left/right feeling) --- */
.narrative-steps{{margin:{l['section_spacing']} 0}}
.narrative-step{{display:flex;gap:1.25rem;align-items:flex-start;margin-bottom:1.75rem;padding-bottom:1.75rem;border-bottom:1px solid {c['border']}}}
.narrative-step:last-child{{border-bottom:none}}
.narrative-step .step-marker{{flex-shrink:0;width:{nl['circle_size']};height:{nl['circle_size']};border-radius:50%;background:{nl['circle_bg']};color:{nl['circle_color']};font-weight:700;display:flex;align-items:center;justify-content:center;font-size:0.9rem}}
.narrative-step .step-text h3{{margin-top:0;margin-bottom:0.3rem}}
.narrative-step .step-text p{{margin:0;font-size:0.97rem}}

/* --- Tips from heart (warm cards) --- */
.heart-tips{{display:grid;grid-template-columns:1fr;gap:0.75rem;margin:{l['section_spacing']} 0}}
.heart-tip{{background:{pt['bg_color']};padding:1rem 1.25rem;border-radius:{l['border_radius']};border-left:3px solid {c['primary']};color:{c['text_secondary']}}}

/* --- FAQ --- */
.faq-section{{margin:{l['section_spacing']} 0}}
.faq-item{{border:1px solid {c['border']};border-radius:{l['border_radius']};margin-bottom:0.5rem;overflow:hidden}}
.faq-question{{width:100%;background:{c['container_bg']};border:none;text-align:left;padding:1rem 1.2rem;font-family:{hf};font-size:0.95rem;font-weight:600;color:{c['text_primary']};cursor:pointer;display:flex;justify-content:space-between;align-items:center}}
.faq-question::after{{content:'+';font-size:1.3rem;color:{c['primary']}}}
.faq-question.open::after{{content:'\\2212'}}
.faq-answer{{display:none;padding:0.75rem 1.2rem 1rem;color:{c['text_secondary']};border-top:1px solid {c['border']}}}
.faq-answer.open{{display:block}}

/* --- Recipe card --- */
.recipe-card{{background:{rc['bg']};border:{rc['border']};border-radius:{rc['border_radius']};overflow:hidden;margin:{l['section_spacing']} 0;box-shadow:{l['box_shadow']}}}
.recipe-card-header{{background:{rc['header_bg']};color:{rc['header_color']};padding:1.2rem 1.75rem;text-align:center}}
.recipe-card-header h2{{margin:0;color:{rc['header_color']};font-size:1.4rem;font-style:normal}}
.recipe-card-body{{padding:1.75rem}}
.recipe-card-image{{width:100%;height:260px;object-fit:cover;display:block}}
.recipe-card-buttons{{display:flex;gap:0.75rem;margin:1rem 0}}
.btn-print,.btn-pin{{flex:1;color:#fff;border:none;padding:0.75rem 1rem;border-radius:{l['border_radius']};cursor:pointer;font-weight:600;font-size:0.9rem;transition:background 0.2s}}
.btn-print{{background:{c['button_print']}}}.btn-print:hover{{background:{c['button_hover_print']}}}
.btn-pin{{background:{c['button_pin']}}}.btn-pin:hover{{background:{c['button_hover_pin']}}}
.recipe-meta{{display:flex;flex-wrap:wrap;gap:0;margin:1rem 0;border:1px solid {c['border']};border-radius:{l['border_radius']}}}
.recipe-meta-item{{flex:1;text-align:center;padding:0.7rem 0.5rem;min-width:60px;border-right:1px solid {c['border']}}}
.recipe-meta-item:last-child{{border-right:none}}
.recipe-meta-label{{font-size:0.6rem;text-transform:uppercase;color:{c['text_secondary']};letter-spacing:0.08em}}
.recipe-meta-value{{font-size:0.95rem;font-weight:700;color:{rc['meta_icon_color']};display:block;margin-top:2px}}
.recipe-ingredients-list{{list-style:none;padding:0}}
.recipe-ingredients-list li{{padding:0.4rem 0 0.4rem 1.4rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}
.recipe-ingredients-list li:last-child{{border-bottom:none}}
.recipe-ingredients-list li::before{{content:'\\25CF';position:absolute;left:0;top:0.5rem;color:{c['list_marker']};font-size:0.5rem}}
.recipe-instructions-list{{list-style:none;padding:0;counter-reset:rstep}}
.recipe-instructions-list li{{counter-increment:rstep;padding:0.6rem 0 0.6rem 2.5rem;position:relative;color:{c['text_secondary']};border-bottom:1px dotted {c['border']}}}
.recipe-instructions-list li:last-child{{border-bottom:none}}
.recipe-instructions-list li::before{{content:counter(rstep);position:absolute;left:0;top:0.4rem;width:24px;height:24px;background:{nl['circle_bg']};color:{nl['circle_color']};border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.75rem}}

@media print{{body{{background:#fff}}.recipe-card-buttons{{display:none}}}}
@media(max-width:700px){{
  .ingredients-showcase{{grid-template-columns:1fr}}
  .recipe-card-buttons{{flex-direction:column}}
  h1{{font-size:1.7rem}}
}}"""

    # ------------------------------------------------------------------ HTML
    def generate_html(self, sections, css_filename="css.css"):
        t = self.title
        imgs = self.config["images"]
        main_img = imgs.get("main_article_image") or "placeholder.jpg"
        ing_img = imgs.get("ingredient_image") or "placeholder.jpg"
        card_img = imgs.get("recipe_card_image") or main_img

        sec = {s["key"]: s["content"] for s in sections}
        story = sec.get("personal_story", "")
        secret = sec.get("the_secret", "")
        ing_intro = sec.get("ingredients_intro", "")
        ing_list = sec.get("ingredient_list", [])
        steps = sec.get("steps", [])
        tips = sec.get("tips_from_heart", [])
        faqs = sec.get("faqs", [])
        conclusion = sec.get("memory_conclusion", "")

        ing_li = "".join(f"    <li>{x}</li>\n" for x in ing_list)
        steps_html = ""
        for i, s in enumerate(steps):
            tt = s.get("title", f"Part {i+1}")
            n = s.get("narrative", "")
            steps_html += f'<div class="narrative-step"><span class="step-marker">{i+1}</span><div class="step-text"><h3>{tt}</h3><p>{n}</p></div></div>\n'
        tips_html = "".join(f'<div class="heart-tip">{tip}</div>\n' for tip in tips)
        faq_html = "".join(f'<div class="faq-item"><button class="faq-question" onclick="toggleFaq(this)">{fq.get("question","")}</button><div class="faq-answer">{fq.get("answer","")}</div></div>\n' for fq in faqs)

        recipe = sec.get("recipe") or {}
        if not isinstance(recipe, dict): recipe = {}
        r = {**{"name": t, "prep_time": "20 min", "cook_time": "40 min", "total_time": "1 hr", "servings": "6", "calories": ""}, **recipe}
        r_ing = "".join(f"    <li>{x}</li>\n" for x in recipe.get("ingredients", []))
        r_inst = "".join(f"    <li>{x}</li>\n" for x in recipe.get("instructions", []))

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{t}</title>
<link rel="stylesheet" href="{css_filename}">
<!-- inject:head-end -->
</head>
<body>
<div class="article-container">

<header class="g13-header">
  <h1 class="article-title">{t}</h1>
  <span class="title-flourish"></span>
  <div>
    <span class="byline-author">By <span class="article-author"></span></span><br>
    <span class="byline-date">Published <span class="article-date"></span></span>
    <p class="byline-disclaimer">This post may contain affiliate links.</p>
  </div>
</header>

<img src="{main_img}" alt="{t}" class="hero-image">
<!-- inject:after-hero -->

<div class="story-block">
  <h2>A Memory from My Kitchen</h2>
  <p>{story}</p>
</div>

<div class="secret-box">
  <div class="secret-icon">&#10024;</div>
  <h2>The Secret</h2>
  <p>{secret}</p>
</div>

<div class="ingredients-showcase">
  <img src="{ing_img}" alt="Ingredients for {t}" class="ing-image">
  <div class="ing-body">
    <h2>What You'll Need</h2>
    <p>{ing_intro}</p>
    <ul class="ing-list">
{ing_li}    </ul>
  </div>
</div>

<h2>How I Make It</h2>
<div class="narrative-steps">
{steps_html}</div>

<h2>Tips From the Heart</h2>
<div class="heart-tips">
{tips_html}</div>

<div class="faq-section">
  <h2>You Might Be Wondering</h2>
{faq_html}</div>

<p>{conclusion}</p>

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
      <button class="btn-print" onclick="window.print()">Print Recipe</button>
      <button class="btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.hero-image,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Save to Pinterest</button>
    </div>
    <h3>Ingredients</h3>
    <ul class="recipe-ingredients-list">
{r_ing}    </ul>
    <h3>Instructions</h3>
    <ol class="recipe-instructions-list">
{r_inst}    </ol>
  </div>
</div>
<!-- inject:article-end -->

</div>
<script>function toggleFaq(btn){{btn.classList.toggle('open');btn.nextElementSibling.classList.toggle('open');}}</script>
</body>
</html>"""

    # ------------------------------------------------------------------ run
    def run(self, return_content_only=False):
        if not self.title: raise ValueError("CONFIG['title'] is required")
        cd = self.generate_content()
        css = self.generate_css()
        html = self.generate_html(cd["sections"])
        cd["article_html"] = html; cd["article_css"] = css
        if return_content_only: return cd
        slug = self.slug
        os.makedirs(slug, exist_ok=True)
        for name, content in [("content.json", json.dumps(cd, indent=2)), ("article.html", html), ("css.css", css)]:
            with open(os.path.join(slug, name), "w", encoding="utf-8") as fh: fh.write(content)
        print(f"[OK] Saved to: {slug}/"); return cd

if __name__ == "__main__":
    gen = ArticleGenerator({"title": "Grandma's Chicken Pot Pie"})
    gen.run()
