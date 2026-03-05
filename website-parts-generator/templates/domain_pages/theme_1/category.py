"""Theme 1 — Category page: Warm gradient hero banner, article grid.
Shares the same visual language as theme_1 domain pages.
"""
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

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".cat-t1")

    other_cats = ""
    for cat in categories[:10]:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or "#")
        if c_name:
            active = " cat-t1-active" if c_name.lower() == category_name.lower() else ""
            other_cats += f'<a href="{c_url}" class="cat-t1-pill{active}">{c_name}</a>'

    html_content = f"""
<main class="category-page cat-t1">
  <section class="dp-t1-hero cat-t1-hero">
    <span class="cat-t1-badge">Category</span>
    <h1>{category_name}</h1>
    <p>{total} recipe{"s" if total != 1 else ""} in this category</p>
  </section>

  <div class="cat-t1-body">
    <div class="cat-t1-pills">
      {other_cats or '<span class="cat-t1-empty">No other categories</span>'}
    </div>
    <div class="cat-t1-grid">{cards_html}</div>
  </div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}

.cat-t1 {{ {t['css_vars']} }}

/* Hero — gradient banner (matches theme 1) */
.cat-t1-hero {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; text-align: center; padding: 3.5rem 1.5rem 2.5rem;
}}
.cat-t1-hero h1 {{ font-family: {ff}; font-size: 2.5rem; font-weight: 700; margin: 0 0 0.5rem; }}
.cat-t1-hero p {{ opacity: 0.9; font-size: 1rem; }}
.cat-t1-badge {{
    display: inline-block; background: rgba(255,255,255,0.2);
    padding: 0.3rem 1rem; border-radius: 9999px; font-size: 0.75rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;
}}

.cat-t1-body {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }}

.cat-t1-pills {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2rem; }}
.cat-t1-pill {{
    padding: 0.4rem 1rem; border-radius: 9999px;
    border: 2px solid var(--border); color: var(--text);
    text-decoration: none; font-size: 0.85rem; font-weight: 500; transition: all 0.2s;
}}
.cat-t1-pill:hover {{ border-color: var(--primary); color: var(--primary); }}
.cat-t1-pill.cat-t1-active {{
    background: var(--primary); border-color: var(--primary); color: #fff;
}}

.cat-t1-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}

.cat-t1-empty {{ color: var(--muted); font-style: italic; font-size: 0.85rem; }}

@media (max-width: 900px) {{
    .cat-t1-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .cat-t1-hero h1 {{ font-size: 2rem; }}
}}
@media (max-width: 600px) {{
    .cat-t1-grid {{ grid-template-columns: 1fr; }}
    .cat-t1-hero h1 {{ font-size: 1.6rem; }}
    .cat-t1-hero {{ padding: 2.5rem 1rem 2rem; }}
}}
"""
    return {"html": html_content, "css": css}
