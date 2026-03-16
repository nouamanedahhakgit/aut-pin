"""Theme 9 — Index: Sunlit Elegance. Split hero, editorial showcases, circular categories, latest recipes grid."""
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
        fx = "Discover wholesome, delicious recipes for every occasion."
    hero_img = f'<img src="{e(fi)}" alt="{ft}" class="it9-hero-img">' if fi and fi.startswith("http") else '<div class="it9-hero-placeholder">&#127858;</div>'

    # --- CATEGORY SHOWCASES ---
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
            img_tag = f'<img src="{e(a_img)}" alt="{a_title}" class="it9-mini-img">' if a_img and a_img.startswith("http") else '<div class="it9-mini-ph">&#127857;</div>'
            mini_cards += f'<a href="{a_url}" class="it9-mini-card">{img_tag}<span class="it9-mini-title">{a_title}</span></a>'
        alt_class = " it9-showcase-alt" if ci % 2 else ""
        showcases_html += f"""
    <section class="it9-showcase{alt_class}">
      <div class="it9-showcase-inner">
        <div class="it9-show-card">
          <div class="it9-show-badge">&#127858; {c_name}</div>
          <h2 class="it9-show-title">{c_name} Recipes</h2>
          <p class="it9-show-desc">{c_count} delicious {c_name.lower()} recipes waiting for you.</p>
          <a href="{c_url}" class="it9-show-btn">More {c_name} &rarr;</a>
        </div>
        <div class="it9-show-grid">{mini_cards or '<p class="it9-empty">Coming soon</p>'}</div>
      </div>
    </section>"""

    # --- CATEGORY CIRCLES ---
    cat_circles = ""
    for cat in categories[:6]:
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url") or "#")
        emoji = "&#127869;" if cat.get("slug", "").startswith("d") else "&#127858;"
        if c_name:
            cat_circles += f'<a href="{c_url}" class="it9-cat-circle"><span class="it9-cat-icon">{emoji}</span><span class="it9-cat-name">{c_name}</span></a>'

    # --- LATEST RECIPES ---
    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".it9")

    html_content = f"""
<main class="index-page it9">
  <section class="it9-hero">
    <div class="it9-hero-inner">
      <div class="it9-hero-media">{hero_img}</div>
      <div class="it9-hero-text">
        <span class="it9-hero-label">Featured Recipe</span>
        <h1 class="it9-hero-title"><a href="{fu}">{ft}</a></h1>
        <p class="it9-hero-excerpt">{fx}</p>
        <div class="it9-hero-btns">
          <a href="{fu}" class="it9-btn-primary">Get Recipe &rarr;</a>
          <a href="{e(base_url)}/recipes" class="it9-btn-ghost">Browse All</a>
        </div>
      </div>
    </div>
  </section>

  {showcases_html}

  <section class="it9-categories">
    <p class="it9-sub-label">What are you craving?</p>
    <h2 class="it9-sec-title">Recipe Categories</h2>
    <div class="it9-cat-row">{cat_circles or '<p class="it9-empty">No categories yet</p>'}</div>
  </section>

  <section class="it9-latest">
    <p class="it9-sub-label">Fresh from the kitchen</p>
    <h2 class="it9-sec-title">Latest Recipes</h2>
    <div class="it9-grid">{cards_html}</div>
    <div class="it9-more"><a href="{e(base_url)}/recipes" class="it9-btn-main">View All Recipes &rarr;</a></div>
  </section>
  <div class="index-pagination-slot"></div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}
.it9 {{ {t['css_vars']} }}

/* --- Hero: white split with gold-tinted bg --- */
.it9-hero {{ background: linear-gradient(160deg, var(--surface2) 0%, var(--gold-light) 100%); border-bottom: 1px solid var(--border); }}
.it9-hero-inner {{ max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; min-height: 440px; }}
.it9-hero-media {{ display: flex; align-items: center; justify-content: center; padding: 2.5rem; }}
.it9-hero-img {{ width: 100%; max-height: 380px; border-radius: var(--radius-lg); object-fit: cover; box-shadow: var(--shadow-lg); }}
.it9-hero-placeholder {{ width: 200px; height: 200px; border-radius: 50%; background: rgba(212,168,67,0.15); border: 2px dashed rgba(212,168,67,0.4); display: flex; align-items: center; justify-content: center; font-size: 4rem; }}
.it9-hero-text {{ display: flex; flex-direction: column; justify-content: center; padding: 2.5rem 3rem 2.5rem 1.5rem; }}
.it9-hero-label {{ display: inline-block; background: rgba(212,168,67,0.15); border: 1px solid rgba(212,168,67,0.35); padding: 0.35rem 1rem; border-radius: 9999px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.18em; color: var(--primary); margin-bottom: 1rem; width: fit-content; }}
.it9-hero-title {{ font-family: {ff}; font-size: clamp(1.8rem, 3.5vw, 2.8rem); font-weight: 700; line-height: 1.2; margin: 0 0 1rem; color: var(--text); }}
.it9-hero-title a {{ text-decoration: none; color: inherit; }}
.it9-hero-title a:hover {{ color: var(--primary); }}
.it9-hero-excerpt {{ color: var(--muted); font-size: 1rem; line-height: 1.75; margin-bottom: 1.75rem; }}
.it9-hero-btns {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}

/* --- Buttons --- */
.it9-btn-primary {{ display: inline-flex; align-items: center; background: var(--primary); color: #fff; padding: 0.75rem 1.8rem; border-radius: 9999px; text-decoration: none; font-weight: 600; font-size: 0.92rem; transition: all 0.25s; box-shadow: 0 3px 14px rgba(212,168,67,0.35); }}
.it9-btn-primary:hover {{ background: var(--accent); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(212,168,67,0.4); }}
.it9-btn-ghost {{ display: inline-flex; align-items: center; background: transparent; color: var(--text); padding: 0.75rem 1.8rem; border-radius: 9999px; border: 1.5px solid var(--border); text-decoration: none; font-weight: 600; font-size: 0.92rem; transition: all 0.25s; }}
.it9-btn-ghost:hover {{ border-color: var(--primary); color: var(--primary); background: var(--gold-light); }}
.it9-btn-main {{ display: inline-flex; align-items: center; background: var(--secondary); color: #fff; padding: 0.8rem 2rem; border-radius: 9999px; text-decoration: none; font-weight: 600; font-size: 0.95rem; transition: all 0.25s; }}
.it9-btn-main:hover {{ background: #5d8462; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(122,158,126,0.4); }}

/* --- Category Showcase --- */
.it9-showcase {{ padding: 3rem 0; background: var(--bg); }}
.it9-showcase-alt {{ background: var(--surface); }}
.it9-showcase-inner {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; align-items: start; }}
.it9-show-card {{
    background: var(--bg); border-radius: var(--radius-lg); padding: 2rem; text-align: center;
    border: 1px solid var(--border); box-shadow: var(--shadow-sm);
}}
.it9-show-badge {{ display: inline-block; background: var(--gold-light); color: var(--primary); border: 1px solid rgba(212,168,67,0.3); padding: 0.35rem 1rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.75rem; }}
.it9-show-title {{ font-family: {ff}; font-size: 1.7rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem; }}
.it9-show-desc {{ color: var(--muted); font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.25rem; }}
.it9-show-btn {{ display: inline-flex; align-items: center; gap: 0.3rem; background: var(--primary); color: #fff; padding: 0.65rem 1.4rem; border-radius: 9999px; text-decoration: none; font-weight: 600; font-size: 0.88rem; transition: all 0.2s; }}
.it9-show-btn:hover {{ background: var(--accent); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(212,168,67,0.3); }}
.it9-show-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }}
.it9-mini-card {{
    display: block; background: var(--bg); border-radius: var(--radius); overflow: hidden;
    border: 1px solid var(--border); text-decoration: none; transition: all 0.3s;
}}
.it9-mini-card:hover {{ transform: translateY(-4px); box-shadow: var(--shadow); border-color: var(--primary); }}
.it9-mini-img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }}
.it9-mini-ph {{ width: 100%; aspect-ratio: 1; background: var(--gold-light); display: flex; align-items: center; justify-content: center; font-size: 2rem; }}
.it9-mini-title {{ display: block; padding: 0.6rem 0.75rem; font-size: 0.8rem; font-weight: 600; color: var(--text); line-height: 1.3; }}
.it9-mini-card:hover .it9-mini-title {{ color: var(--primary); }}

/* --- Category circles --- */
.it9-categories {{ text-align: center; padding: 4rem 1.5rem; background: linear-gradient(to bottom, var(--bg), var(--surface2)); }}
.it9-sub-label {{ color: var(--primary); font-family: {ff}; font-size: 1.1rem; font-style: italic; margin-bottom: 0.25rem; }}
.it9-sec-title {{ font-family: {ff}; font-size: 2.2rem; font-weight: 700; color: var(--text); margin-bottom: 2rem; }}
.it9-cat-row {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5rem; }}
.it9-cat-circle {{
    display: flex; flex-direction: column; align-items: center; text-decoration: none;
    transition: transform 0.3s;
}}
.it9-cat-circle:hover {{ transform: translateY(-5px); }}
.it9-cat-icon {{
    width: 100px; height: 100px; border-radius: 50%; background: var(--bg);
    border: 2px solid var(--border); display: flex; align-items: center; justify-content: center;
    font-size: 2.5rem; margin-bottom: 0.5rem; box-shadow: var(--shadow-sm);
    transition: border-color 0.3s, box-shadow 0.3s, background 0.3s;
}}
.it9-cat-circle:hover .it9-cat-icon {{ border-color: var(--primary); background: var(--gold-light); box-shadow: var(--shadow); }}
.it9-cat-name {{ font-weight: 700; font-size: 0.88rem; color: var(--text); }}
.it9-cat-circle:hover .it9-cat-name {{ color: var(--primary); }}

/* --- Latest recipes --- */
.it9-latest {{ max-width: 1200px; margin: 0 auto; padding: 4rem 1.5rem; text-align: center; }}
.it9-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; text-align: left; }}
.it9-more {{ margin-top: 2.5rem; }}
.it9-empty {{ color: var(--muted); font-style: italic; }}

@media (max-width: 1024px) {{
    .it9-showcase-inner {{ grid-template-columns: 1fr; }}
    .it9-show-grid {{ grid-template-columns: repeat(3, 1fr); }}
}}
@media (max-width: 900px) {{
    .it9-hero-inner {{ grid-template-columns: 1fr; }}
    .it9-hero-text {{ padding: 2rem 1.5rem; }}
    .it9-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .it9-show-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 600px) {{
    .it9-grid {{ grid-template-columns: 1fr; }}
    .it9-hero-title {{ font-size: 1.7rem; }}
    .it9-show-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .it9-cat-icon {{ width: 74px; height: 74px; font-size: 1.8rem; }}
    .it9-sec-title {{ font-size: 1.7rem; }}
}}
"""
    return {"html": html_content, "css": css}
