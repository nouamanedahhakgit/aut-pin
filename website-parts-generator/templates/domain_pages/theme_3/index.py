"""Theme 3 — Index: Glassmorphism Dark Mode. Full-bleed hero overlay, glass category showcases, neon category pills, latest recipes grid."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module
from shared_article_card import render_cards


def generate(config: dict) -> dict:
    t = theme_base(config)
    s = t["s"]
    ff = t["font_family"]
    bf = t["body_font"]

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    articles = config.get("articles", [])
    categories = config.get("categories", [])
    domain_name = html_module.escape(config.get("domain_name", s.get("domain_name", "Recipe Blog")))

    def e(v): return html_module.escape(str(v)) if v else ""

    ROOT_CLS = ".it3"

    # --- HERO: featured article full-bleed with overlay ---
    feat = articles[0] if articles else None
    if feat:
        fi = (feat.get("main_image") or feat.get("image") or "").strip()
        ft = e((feat.get("title") or "Recipe")[:120])
        fu = e(feat.get("url") or "#")
        fx = e((feat.get("excerpt") or "")[:200])
    else:
        fi, ft, fu = "", f"Welcome to {domain_name}", "#"
        fx = "Discover delicious recipes crafted with passion."
    if fi and fi.startswith("http"):
        hero_bg = f'style="background-image: url(\'{e(fi)}\')"'
    else:
        hero_bg = ''

    # --- CATEGORY SHOWCASES: top 2 categories ---
    showcases_html = ""
    for ci, cat in enumerate(categories[:2]):
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url") or "#")
        c_count = cat.get("count", 0)
        cat_articles = articles[ci*3+1 : ci*3+4] if len(articles) > ci*3+1 else []
        mini_cards = ""
        for a in cat_articles:
            a_img = (a.get("main_image") or a.get("image") or "").strip()
            a_title = e((a.get("title") or "")[:60])
            a_url = e(a.get("url") or "#")
            img_tag = f'<img src="{e(a_img)}" alt="{a_title}" class="it3-mini-img">' if a_img and a_img.startswith("http") else '<div class="it3-mini-ph">&#127858;</div>'
            mini_cards += f'<a href="{a_url}" class="it3-mini-card">{img_tag}<span class="it3-mini-title">{a_title}</span></a>'
        showcases_html += f"""
    <section class="it3-showcase {'it3-showcase-alt' if ci % 2 else ''}">
      <div class="it3-showcase-inner">
        <div class="it3-show-card">
          <div class="it3-show-badge">&#10024; {c_name}</div>
          <h2 class="it3-show-title">{c_name} Recipes</h2>
          <p class="it3-show-desc">{c_count} delicious {c_name.lower()} recipes to explore.</p>
          <a href="{c_url}" class="it3-show-btn">More {c_name} &rarr;</a>
        </div>
        <div class="it3-show-grid">{mini_cards or '<p class="it3-empty">Coming soon</p>'}</div>
      </div>
    </section>"""

    # --- CATEGORIES: neon pill buttons ---
    cat_pills = ""
    for cat in categories[:8]:
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url") or "#")
        c_count = cat.get("count", "")
        if c_name:
            count_badge = f'<span class="it3-pill-count">{c_count}</span>' if c_count else ""
            cat_pills += f'<a href="{c_url}" class="it3-cat-pill">{c_name}{count_badge}</a>'

    # --- LATEST RECIPES: card grid ---
    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=ROOT_CLS)

    html_content = f"""
<main class="index-page it3">
  <section class="it3-hero" {hero_bg}>
    <div class="it3-hero-overlay"></div>
    <div class="it3-hero-content">
      <span class="it3-hero-label">Featured Recipe</span>
      <h1 class="it3-hero-title"><a href="{fu}">{ft}</a></h1>
      <p class="it3-hero-excerpt">{fx}</p>
      <div class="it3-hero-btns">
        <a href="{fu}" class="it3-btn-primary">Get Recipe &rarr;</a>
        <a href="{e(base_url)}/recipes" class="it3-btn-ghost">Browse All</a>
      </div>
    </div>
  </section>

  {showcases_html}

  <section class="it3-categories">
    <p class="it3-sub-label">What&rsquo;s cooking?</p>
    <h2 class="it3-sec-title">Recipe Categories</h2>
    <div class="it3-cat-row">{cat_pills or '<p class="it3-empty">No categories yet</p>'}</div>
  </section>

  <section class="it3-latest">
    <p class="it3-sub-label">Fresh from the kitchen</p>
    <h2 class="it3-sec-title">Latest Recipes</h2>
    <div class="it3-grid">{cards_html}</div>
    <div class="it3-more"><a href="{e(base_url)}/recipes" class="it3-btn-primary">View All Recipes &rarr;</a></div>
  </section>
  <div class="index-pagination-slot"></div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}
.it3 {{ {t['css_vars']} }}

/* --- Hero: full-bleed image with dark overlay + glassmorphism content --- */
.it3-hero {{
    position: relative; min-height: 480px; display: flex; align-items: center; justify-content: center;
    background-size: cover; background-position: center; background-color: var(--bg);
    overflow: hidden;
}}
.it3-hero-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(15,15,26,0.75) 0%, rgba(15,15,26,0.92) 100%);
}}
.it3-hero-content {{
    position: relative; z-index: 2; text-align: center; padding: 3rem 1.5rem; max-width: 720px;
}}
.it3-hero-label {{
    display: inline-block; background: var(--glass); backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px); border: 1px solid var(--glass-border);
    padding: 0.4rem 1.2rem; border-radius: 9999px; font-size: 0.78rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;
    color: var(--secondary); margin-bottom: 1.25rem;
}}
.it3-hero-title {{
    font-family: {ff}; font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 800;
    line-height: 1.15; margin: 0 0 0.75rem; color: #fff;
    text-shadow: 0 0 50px color-mix(in srgb, var(--primary) 25%, transparent);
}}
.it3-hero-title a {{ text-decoration: none; color: #fff; }}
.it3-hero-excerpt {{ color: var(--muted); font-size: 1rem; line-height: 1.7; margin-bottom: 1.75rem; }}
.it3-hero-btns {{ display: flex; gap: 0.85rem; justify-content: center; flex-wrap: wrap; }}

/* --- Buttons --- */
.it3-btn-primary {{
    display: inline-flex; align-items: center; gap: 0.3rem;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; padding: 0.75rem 1.8rem; border-radius: 12px;
    text-decoration: none; font-weight: 700; font-size: 0.92rem;
    transition: all 0.3s; border: none;
    box-shadow: 0 4px 20px color-mix(in srgb, var(--primary) 30%, transparent);
}}
.it3-btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 30px color-mix(in srgb, var(--primary) 45%, transparent);
}}
.it3-btn-ghost {{
    display: inline-flex; align-items: center;
    background: var(--glass); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    color: var(--text); padding: 0.75rem 1.8rem; border-radius: 12px;
    border: 1px solid var(--glass-border);
    text-decoration: none; font-weight: 700; font-size: 0.92rem;
    transition: all 0.3s;
}}
.it3-btn-ghost:hover {{
    border-color: var(--primary); color: #fff;
    box-shadow: 0 0 14px color-mix(in srgb, var(--primary) 20%, transparent);
}}

/* --- Category Showcase --- */
.it3-showcase {{ padding: 3.5rem 0; }}
.it3-showcase-alt {{ background: color-mix(in srgb, var(--primary) 3%, var(--bg)); }}
.it3-showcase-inner {{
    max-width: 1200px; margin: 0 auto; padding: 0 1.5rem;
    display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; align-items: start;
}}
.it3-show-card {{
    background: var(--glass); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border); border-radius: var(--radius); padding: 2rem;
    text-align: center;
}}
.it3-show-badge {{
    display: inline-block;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; padding: 0.35rem 1rem; border-radius: 9999px;
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;
}}
.it3-show-title {{ font-family: {ff}; font-size: 1.6rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem; }}
.it3-show-desc {{ color: var(--muted); font-size: 0.88rem; line-height: 1.6; margin-bottom: 1.25rem; }}
.it3-show-btn {{
    display: inline-flex; align-items: center; gap: 0.3rem;
    background: var(--primary); color: #fff; padding: 0.65rem 1.3rem;
    border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 0.85rem;
    transition: all 0.3s;
    box-shadow: 0 0 14px color-mix(in srgb, var(--primary) 25%, transparent);
}}
.it3-show-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px color-mix(in srgb, var(--primary) 40%, transparent); }}
.it3-show-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }}
.it3-mini-card {{
    display: block; background: var(--glass); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    border-radius: 12px; overflow: hidden;
    border: 1px solid var(--glass-border); text-decoration: none; transition: all 0.35s;
}}
.it3-mini-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,.3);
    border-color: var(--primary);
}}
.it3-mini-img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }}
.it3-mini-ph {{
    width: 100%; aspect-ratio: 1; background: color-mix(in srgb, var(--primary) 8%, var(--bg));
    display: flex; align-items: center; justify-content: center; font-size: 2rem;
}}
.it3-mini-title {{
    display: block; padding: 0.55rem 0.75rem; font-size: 0.78rem; font-weight: 600;
    color: var(--muted); line-height: 1.3;
}}
.it3-mini-card:hover .it3-mini-title {{ color: var(--text); }}

/* --- Category pills --- */
.it3-categories {{ text-align: center; padding: 4.5rem 1.5rem; }}
.it3-sub-label {{ color: var(--secondary); font-size: 0.92rem; font-weight: 500; margin-bottom: 0.25rem; letter-spacing: 0.04em; }}
.it3-sec-title {{ font-family: {ff}; font-size: 2rem; font-weight: 800; color: var(--text); margin-bottom: 2rem; }}
.it3-cat-row {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 0.75rem; }}
.it3-cat-pill {{
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.55rem 1.2rem; border-radius: 9999px;
    border: 1px solid var(--glass-border); color: var(--muted);
    text-decoration: none; font-size: 0.88rem; font-weight: 600;
    background: var(--glass); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    transition: all 0.3s;
}}
.it3-cat-pill:hover {{
    border-color: var(--primary); color: var(--text);
    box-shadow: 0 0 14px color-mix(in srgb, var(--primary) 25%, transparent);
    background: color-mix(in srgb, var(--primary) 8%, transparent);
}}
.it3-pill-count {{
    background: var(--primary); color: #fff; font-size: 0.68rem; font-weight: 700;
    padding: 0.1rem 0.45rem; border-radius: 9999px; min-width: 20px; text-align: center;
}}

/* --- Latest recipes --- */
.it3-latest {{ max-width: 1200px; margin: 0 auto; padding: 4rem 1.5rem; text-align: center; }}
.it3-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; text-align: left; }}
.it3-more {{ margin-top: 2.5rem; }}
.it3-empty {{ color: var(--muted); font-style: italic; }}

@media (max-width: 1024px) {{
    .it3-showcase-inner {{ grid-template-columns: 1fr; }}
    .it3-show-grid {{ grid-template-columns: repeat(3, 1fr); }}
}}
@media (max-width: 900px) {{
    .it3-hero {{ min-height: 380px; }}
    .it3-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .it3-show-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 600px) {{
    .it3-grid {{ grid-template-columns: 1fr; }}
    .it3-hero-title {{ font-size: 1.6rem; }}
    .it3-show-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .it3-sec-title {{ font-size: 1.5rem; }}
    .it3-hero {{ min-height: 340px; }}
}}
"""
    return {"html": html_content, "css": css}
