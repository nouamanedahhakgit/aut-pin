"""Theme 2 — Category page: Modern clean hero, accent-bar headings, article grid.
Shares the same visual language as theme_2 domain pages.
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

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".cat-t2")

    breadcrumb = f'<a href="{html_module.escape(base_url or "/")}">Home</a> &rsaquo; <span>{category_name}</span>'

    other_cats = ""
    for cat in categories[:10]:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or "#")
        if c_name:
            active = " cat-t2-active" if c_name.lower() == category_name.lower() else ""
            other_cats += f'<a href="{c_url}" class="cat-t2-link{active}">{c_name}</a>'

    html_content = f"""
<main class="category-page cat-t2">
  <section class="dp-t2-hero cat-t2-hero">
    <p class="dp-t2-hero-label">Category</p>
    <h1>{category_name}</h1>
    <p>{total} recipe{"s" if total != 1 else ""} in this category</p>
  </section>

  <div class="cat-t2-body">
    <nav class="cat-t2-breadcrumb">{breadcrumb}</nav>

    <div class="cat-t2-cats">
      {other_cats or '<span class="cat-t2-empty">No categories</span>'}
    </div>

    <div class="cat-t2-grid">{cards_html}</div>
  </div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}

.cat-t2 {{ {t['css_vars']} }}

/* Hero — light tinted bg with accent border (matches theme 2) */
.cat-t2-hero {{
    background: color-mix(in srgb, var(--primary) 8%, var(--bg));
    text-align: center; padding: 3rem 1.5rem 2.5rem;
    border-bottom: 3px solid var(--primary);
}}
.cat-t2-hero h1 {{ font-family: {ff}; font-size: 2.4rem; font-weight: 700; color: var(--text); margin: 0 0 0.5rem; }}
.cat-t2-hero p {{ color: var(--muted); font-size: 1rem; }}

.cat-t2-body {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }}

.cat-t2-breadcrumb {{ font-size: 0.8rem; color: var(--muted); margin-bottom: 1.5rem; }}
.cat-t2-breadcrumb a {{ color: var(--primary); text-decoration: none; }}
.cat-t2-breadcrumb span {{ color: var(--text); }}

.cat-t2-cats {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 2rem; }}
.cat-t2-link {{
    padding: 0.4rem 0.9rem; border: 1px solid var(--border);
    text-decoration: none; color: var(--text); font-size: 0.85rem;
    font-weight: 500; transition: all 0.2s;
}}
.cat-t2-link:hover {{ border-color: var(--primary); color: var(--primary); }}
.cat-t2-link.cat-t2-active {{
    background: var(--primary); border-color: var(--primary); color: #fff;
}}

.cat-t2-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}

.cat-t2-empty {{ color: var(--muted); font-style: italic; font-size: 0.85rem; }}

@media (max-width: 900px) {{
    .cat-t2-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .cat-t2-hero h1 {{ font-size: 1.8rem; }}
}}
@media (max-width: 600px) {{
    .cat-t2-grid {{ grid-template-columns: 1fr; }}
    .cat-t2-hero h1 {{ font-size: 1.5rem; }}
    .cat-t2-hero {{ padding: 2rem 1rem 1.5rem; }}
}}
"""
    return {"html": html_content, "css": css}
