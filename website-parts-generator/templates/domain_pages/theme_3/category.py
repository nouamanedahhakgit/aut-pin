"""Theme 3 — Category page: Glassmorphism dark hero, frosted nav pills, article grid."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module
from shared_article_card import render_cards


def generate(config: dict) -> dict:
    t = theme_base(config)
    s = t["s"]
    ff = t["font_family"]

    category_name = html_module.escape(config.get("category_name", "Recipes"))
    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    articles = config.get("articles", [])
    categories = config.get("categories", [])
    total = config.get("total", len(articles))

    ROOT_CLS = ".cat-t3"
    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=ROOT_CLS)

    other_cats = ""
    for cat in categories[:10]:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or "#")
        if c_name:
            active = " cat-t3-active" if c_name.lower() == category_name.lower() else ""
            other_cats += f'<a href="{c_url}" class="cat-t3-pill{active}">{c_name}</a>'

    html_content = f"""
<main class="category-page cat-t3">
  <section class="dp-t3-hero cat-t3-hero">
    <span class="dp-t3-hero-label">Category</span>
    <h1>{category_name}</h1>
    <p>{total} recipe{"s" if total != 1 else ""} in this category</p>
  </section>

  <div class="cat-t3-body">
    <div class="cat-t3-pills">
      {other_cats or '<span class="cat-t3-empty">No other categories</span>'}
    </div>
    <div class="cat-t3-grid">{cards_html}</div>
  </div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}

.cat-t3 {{ {t['css_vars']} }}

/* Hero — dark glassmorphism (matches theme 3) */
.cat-t3-hero {{
    background: radial-gradient(ellipse at 30% 0%, color-mix(in srgb, var(--primary) 18%, var(--bg)), var(--bg) 70%);
    text-align: center; padding: 4.5rem 1.5rem 3rem; position: relative; overflow: hidden;
}}
.cat-t3-hero::before {{
    content: ''; position: absolute; top: -40%; right: -20%; width: 500px; height: 500px;
    background: radial-gradient(circle, color-mix(in srgb, var(--secondary) 8%, transparent), transparent 70%);
    pointer-events: none;
}}
.cat-t3-hero h1 {{
    font-family: {ff}; font-size: clamp(2rem, 5vw, 2.8rem); font-weight: 800; margin: 0 0 0.5rem;
    color: #fff; text-shadow: 0 0 40px color-mix(in srgb, var(--primary) 25%, transparent);
}}
.cat-t3-hero p {{ color: var(--muted); font-size: 1rem; }}

.cat-t3-body {{ max-width: 1200px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }}

.cat-t3-pills {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2.5rem; }}
.cat-t3-pill {{
    padding: 0.45rem 1.1rem; border-radius: 9999px;
    border: 1px solid var(--glass-border); color: var(--muted);
    text-decoration: none; font-size: 0.85rem; font-weight: 600;
    background: var(--glass); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    transition: all 0.3s;
}}
.cat-t3-pill:hover {{
    border-color: var(--primary); color: var(--text);
    box-shadow: 0 0 12px color-mix(in srgb, var(--primary) 20%, transparent);
}}
.cat-t3-pill.cat-t3-active {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-color: transparent; color: #fff;
    box-shadow: 0 4px 16px color-mix(in srgb, var(--primary) 30%, transparent);
}}

.cat-t3-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}

.cat-t3-empty {{ color: var(--muted); font-style: italic; font-size: 0.85rem; }}

@media (max-width: 900px) {{
    .cat-t3-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .cat-t3-hero h1 {{ font-size: 2rem; }}
}}
@media (max-width: 600px) {{
    .cat-t3-grid {{ grid-template-columns: 1fr; }}
    .cat-t3-hero h1 {{ font-size: 1.6rem; }}
    .cat-t3-hero {{ padding: 3rem 1rem 2rem; }}
}}
"""
    return {"html": html_content, "css": css}
