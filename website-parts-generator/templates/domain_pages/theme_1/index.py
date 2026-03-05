"""Theme 1 — Index: Warm gradient style. Split hero, category showcases, circular category icons, latest recipes grid."""
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

    # --- HERO: featured article split ---
    feat = articles[0] if articles else None
    if feat:
        fi = (feat.get("main_image") or feat.get("image") or "").strip()
        ft = e((feat.get("title") or "Recipe")[:120])
        fu = e(feat.get("url") or "#")
        fx = e((feat.get("excerpt") or "")[:200])
    else:
        fi, ft, fu = "", f"Welcome to {domain_name}", "#"
        fx = "Discover delicious recipes for every occasion."
    hero_img = f'<img src="{e(fi)}" alt="{ft}" class="it1-hero-img">' if fi and fi.startswith("http") else '<div class="it1-hero-placeholder">&#127860;</div>'

    # --- CATEGORY SHOWCASES: top 2 categories, each with mini-grid ---
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
            img_tag = f'<img src="{e(a_img)}" alt="{a_title}" class="it1-mini-img">' if a_img and a_img.startswith("http") else '<div class="it1-mini-ph">&#127858;</div>'
            mini_cards += f'<a href="{a_url}" class="it1-mini-card">{img_tag}<span class="it1-mini-title">{a_title}</span></a>'
        showcases_html += f"""
    <section class="it1-showcase {'it1-showcase-alt' if ci % 2 else ''}">
      <div class="it1-showcase-inner">
        <div class="it1-show-card">
          <div class="it1-show-badge">&#11088; {c_name}</div>
          <h2 class="it1-show-title">{c_name} Recipes</h2>
          <p class="it1-show-desc">{c_count} delicious {c_name.lower()} recipes waiting for you.</p>
          <a href="{c_url}" class="it1-show-btn">More {c_name} &rarr;</a>
        </div>
        <div class="it1-show-grid">{mini_cards or '<p class="it1-empty">Coming soon</p>'}</div>
      </div>
    </section>"""

    # --- CATEGORIES: circular icons ---
    cat_circles = ""
    for cat in categories[:6]:
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url") or "#")
        emoji = "&#127869;" if cat.get("slug", "").startswith("d") else "&#127860;"
        if c_name:
            cat_circles += f'<a href="{c_url}" class="it1-cat-circle"><span class="it1-cat-icon">{emoji}</span><span class="it1-cat-name">{c_name}</span></a>'

    # --- LATEST RECIPES: card grid ---
    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".it1")

    html_content = f"""
<main class="index-page it1">
  <section class="it1-hero">
    <div class="it1-hero-inner">
      <div class="it1-hero-media">{hero_img}</div>
      <div class="it1-hero-text">
        <span class="it1-hero-label">Featured Recipe</span>
        <h1 class="it1-hero-title"><a href="{fu}">{ft}</a></h1>
        <p class="it1-hero-excerpt">{fx}</p>
        <div class="it1-hero-btns">
          <a href="{fu}" class="it1-btn-primary">Get Recipe &rarr;</a>
          <a href="{e(base_url)}/recipes" class="it1-btn-ghost">Browse All</a>
        </div>
      </div>
    </div>
  </section>

  {showcases_html}

  <section class="it1-categories">
    <p class="it1-sub-label">What are you craving?</p>
    <h2 class="it1-sec-title">Recipe Categories</h2>
    <div class="it1-cat-row">{cat_circles or '<p class="it1-empty">No categories yet</p>'}</div>
  </section>

  <section class="it1-latest">
    <p class="it1-sub-label">Fresh from the kitchen</p>
    <h2 class="it1-sec-title">Latest Recipes</h2>
    <div class="it1-grid">{cards_html}</div>
    <div class="it1-more"><a href="{e(base_url)}/recipes" class="it1-btn-primary">View All Recipes &rarr;</a></div>
  </section>
  <div class="index-pagination-slot"></div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}
.it1 {{ {t['css_vars']} }}

/* --- Hero: split image + text with gradient bg --- */
.it1-hero {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff; }}
.it1-hero-inner {{ max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; min-height: 420px; }}
.it1-hero-media {{ display: flex; align-items: center; justify-content: center; padding: 2rem; }}
.it1-hero-img {{ width: 100%; max-height: 380px; border-radius: 1.5rem; object-fit: cover; box-shadow: 0 20px 40px rgba(0,0,0,.2); }}
.it1-hero-placeholder {{ width: 200px; height: 200px; border-radius: 50%; background: rgba(255,255,255,.15); display: flex; align-items: center; justify-content: center; font-size: 4rem; }}
.it1-hero-text {{ display: flex; flex-direction: column; justify-content: center; padding: 2.5rem 2.5rem 2.5rem 0; }}
.it1-hero-label {{ display: inline-block; background: rgba(255,255,255,.2); padding: 0.4rem 1rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 1rem; width: fit-content; }}
.it1-hero-title {{ font-family: {ff}; font-size: 2.4rem; font-weight: 700; line-height: 1.15; margin: 0 0 0.75rem; }}
.it1-hero-title a {{ text-decoration: none; color: #fff; }}
.it1-hero-excerpt {{ opacity: 0.9; font-size: 1rem; line-height: 1.7; margin-bottom: 1.5rem; }}
.it1-hero-btns {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}

/* --- Buttons --- */
.it1-btn-primary {{ display: inline-flex; align-items: center; background: #fff; color: var(--primary); padding: 0.75rem 1.8rem; border-radius: 9999px; text-decoration: none; font-weight: 700; font-size: 0.95rem; transition: all 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,.1); }}
.it1-btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,.15); }}
.it1-btn-ghost {{ display: inline-flex; align-items: center; background: transparent; color: #fff; padding: 0.75rem 1.8rem; border-radius: 9999px; border: 2px solid rgba(255,255,255,.4); text-decoration: none; font-weight: 700; font-size: 0.95rem; transition: all 0.2s; }}
.it1-btn-ghost:hover {{ border-color: #fff; background: rgba(255,255,255,.1); }}

/* --- Category Showcase --- */
.it1-showcase {{ padding: 3rem 0; background: var(--bg); }}
.it1-showcase-alt {{ background: color-mix(in srgb, var(--primary) 4%, var(--bg)); }}
.it1-showcase-inner {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; align-items: start; }}
.it1-show-card {{
    background: #fff; border-radius: 1.25rem; padding: 2rem; text-align: center;
    border: 2px solid var(--border); box-shadow: 0 4px 12px rgba(0,0,0,.04);
}}
.it1-show-badge {{ display: inline-block; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff; padding: 0.4rem 1rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem; }}
.it1-show-title {{ font-family: {ff}; font-size: 1.8rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem; }}
.it1-show-desc {{ color: var(--muted); font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.25rem; }}
.it1-show-btn {{ display: inline-flex; align-items: center; gap: 0.3rem; background: var(--primary); color: #fff; padding: 0.7rem 1.5rem; border-radius: 9999px; text-decoration: none; font-weight: 700; font-size: 0.9rem; transition: all 0.2s; }}
.it1-show-btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,.12); }}
.it1-show-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }}
.it1-mini-card {{
    display: block; background: #fff; border-radius: 0.75rem; overflow: hidden;
    border: 1px solid var(--border); text-decoration: none; transition: all 0.3s;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
}}
.it1-mini-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,.1); border-color: var(--primary); }}
.it1-mini-img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }}
.it1-mini-ph {{ width: 100%; aspect-ratio: 1; background: var(--border); display: flex; align-items: center; justify-content: center; font-size: 2rem; }}
.it1-mini-title {{ display: block; padding: 0.6rem 0.75rem; font-size: 0.8rem; font-weight: 600; color: var(--text); line-height: 1.3; }}
.it1-mini-card:hover .it1-mini-title {{ color: var(--primary); }}

/* --- Category circles --- */
.it1-categories {{ text-align: center; padding: 4rem 1.5rem; background: linear-gradient(to bottom, #fff, var(--bg)); }}
.it1-sub-label {{ color: var(--primary); font-size: 1.2rem; font-style: italic; margin-bottom: 0.25rem; }}
.it1-sec-title {{ font-family: {ff}; font-size: 2.2rem; font-weight: 700; color: var(--text); margin-bottom: 2rem; }}
.it1-cat-row {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5rem; }}
.it1-cat-circle {{
    display: flex; flex-direction: column; align-items: center; text-decoration: none;
    transition: transform 0.3s;
}}
.it1-cat-circle:hover {{ transform: translateY(-4px); }}
.it1-cat-icon {{
    width: 100px; height: 100px; border-radius: 50%; background: #fff;
    border: 3px solid var(--border); display: flex; align-items: center; justify-content: center;
    font-size: 2.5rem; margin-bottom: 0.5rem; box-shadow: 0 4px 12px rgba(0,0,0,.06);
    transition: border-color 0.3s, box-shadow 0.3s;
}}
.it1-cat-circle:hover .it1-cat-icon {{ border-color: var(--primary); box-shadow: 0 8px 24px rgba(0,0,0,.1); }}
.it1-cat-name {{ font-weight: 700; font-size: 0.9rem; color: var(--text); }}
.it1-cat-circle:hover .it1-cat-name {{ color: var(--primary); }}

/* --- Latest recipes --- */
.it1-latest {{ max-width: 1200px; margin: 0 auto; padding: 4rem 1.5rem; text-align: center; }}
.it1-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; text-align: left; }}
.it1-more {{ margin-top: 2.5rem; }}
.it1-more .it1-btn-primary {{ background: var(--primary); color: #fff; }}
.it1-empty {{ color: var(--muted); font-style: italic; }}

@media (max-width: 1024px) {{
    .it1-showcase-inner {{ grid-template-columns: 1fr; }}
    .it1-show-grid {{ grid-template-columns: repeat(3, 1fr); }}
}}
@media (max-width: 900px) {{
    .it1-hero-inner {{ grid-template-columns: 1fr; }}
    .it1-hero-text {{ padding: 2rem 1.5rem; }}
    .it1-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .it1-show-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 600px) {{
    .it1-grid {{ grid-template-columns: 1fr; }}
    .it1-hero-title {{ font-size: 1.6rem; }}
    .it1-show-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .it1-cat-icon {{ width: 72px; height: 72px; font-size: 1.8rem; }}
    .it1-sec-title {{ font-size: 1.6rem; }}
}}
"""
    return {"html": html_content, "css": css}
