"""Theme 9 — Category page: Gold-tinted hero banner, article grid. Sunlit Elegance white theme."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module
from shared_article_card import render_cards


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]

    category_name = html_module.escape(config.get("category_name", "Recipes"))
    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    articles = config.get("articles", [])
    categories = config.get("categories", [])
    total = config.get("total", len(articles))

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".cat-t9")

    other_cats = ""
    for cat in categories[:10]:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or "#")
        if c_name:
            active = " cat-t9-active" if c_name.lower() == category_name.lower() else ""
            other_cats += f'<a href="{c_url}" class="cat-t9-pill{active}">{c_name}</a>'

    html_content = f"""
<main class="category-page cat-t9">
  <section class="cat-t9-hero">
    <span class="cat-t9-badge">Category</span>
    <h1>{category_name}</h1>
    <p>{total} recipe{"s" if total != 1 else ""} in this category</p>
  </section>

  <div class="cat-t9-body">
    <div class="cat-t9-pills">
      {other_cats or '<span class="cat-t9-empty">No other categories</span>'}
    </div>
    <div class="cat-t9-grid">{cards_html}</div>
  </div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}

.cat-t9 {{ {t['css_vars']} }}

.cat-t9-hero {{
    background: linear-gradient(160deg, var(--surface2), var(--gold-light));
    color: var(--text); text-align: center; padding: 3.5rem 1.5rem 2.5rem;
    border-bottom: 1px solid var(--border);
}}
.cat-t9-hero h1 {{ font-family: {ff}; font-size: 2.5rem; font-weight: 700; margin: 0 0 0.5rem; color: var(--text); }}
.cat-t9-hero p {{ color: var(--muted); font-size: 1rem; }}
.cat-t9-badge {{
    display: inline-block; background: rgba(212,168,67,0.15); border: 1px solid rgba(212,168,67,0.35);
    padding: 0.3rem 1rem; border-radius: 9999px; font-size: 0.72rem;
    font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; color: var(--primary); margin-bottom: 0.75rem;
}}

.cat-t9-body {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }}

.cat-t9-pills {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2rem; }}
.cat-t9-pill {{
    padding: 0.4rem 1.1rem; border-radius: 9999px;
    border: 1.5px solid var(--border); color: var(--text);
    text-decoration: none; font-size: 0.85rem; font-weight: 500; transition: all 0.2s;
    background: var(--bg);
}}
.cat-t9-pill:hover {{ border-color: var(--primary); color: var(--primary); background: var(--gold-light); }}
.cat-t9-pill.cat-t9-active {{
    background: var(--primary); border-color: var(--primary); color: #fff;
}}

.cat-t9-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}

.cat-t9-empty {{ color: var(--muted); font-style: italic; font-size: 0.85rem; }}

@media (max-width: 900px) {{
    .cat-t9-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .cat-t9-hero h1 {{ font-size: 2rem; }}
}}
@media (max-width: 600px) {{
    .cat-t9-grid {{ grid-template-columns: 1fr; }}
    .cat-t9-hero h1 {{ font-size: 1.6rem; }}
    .cat-t9-hero {{ padding: 2.5rem 1rem 2rem; }}
}}
"""
    return {"html": html_content, "css": css}
