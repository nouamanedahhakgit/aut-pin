"""Theme 11 — Category page: Art Deco — gold-line filter links, deco article card grid."""
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

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".cat-t11")

    cat_links = ""
    for cat in categories[:12]:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or "#")
        if c_name:
            active = " cat-t11-active" if c_name.lower() == category_name.lower() else ""
            cat_links += f'<a href="{c_url}" class="cat-t11-link{active}">{c_name}</a>'

    html_content = f"""
<main class="category-page cat-t11">
  <section class="cat-t11-hero">
    <div class="cat-t11-hero-inner">
      <span class="cat-t11-label">&#9671; Category &#9671;</span>
      <h1>{category_name}</h1>
      <p><strong style="color:var(--gold)">{total}</strong> recipe{"s" if total != 1 else ""} in this collection</p>
    </div>
  </section>
  <div class="cat-t11-body">
    <div class="cat-t11-links">{cat_links or '<span style="color:var(--muted);font-size:0.85rem;">No other categories</span>'}</div>
    <div class="cat-t11-grid">{cards_html}</div>
  </div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}
.cat-t11 {{ {t['css_vars']} }}
.cat-t11-hero {{
    background: var(--primary); color: var(--text-on-primary);
    padding: 3.5rem 1.5rem 2.5rem; text-align: center;
    position: relative;
}}
.cat-t11-hero::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }}
.cat-t11-hero-inner {{ max-width: 700px; margin: 0 auto; }}
.cat-t11-label {{
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.3em; color: var(--gold); margin-bottom: 1rem; display: inline-block;
}}
.cat-t11-hero h1 {{
    font-family: {ff}; font-size: clamp(1.8rem, 5vw, 3rem);
    font-weight: 700; margin: 0 0 0.5rem; color: var(--text-on-primary);
    text-transform: uppercase; letter-spacing: 0.05em;
}}
.cat-t11-hero p {{ color: var(--text-on-primary-muted); font-size: 1rem; }}
.cat-t11-body {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }}
.cat-t11-links {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2rem; justify-content: center; }}
.cat-t11-link {{
    padding: 0.4rem 1rem; border: 1px solid var(--border); color: var(--muted);
    text-decoration: none; font-size: 0.78rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; transition: all 0.25s;
}}
.cat-t11-link:hover {{ border-color: var(--gold); color: var(--gold); }}
.cat-t11-link.cat-t11-active {{ background: var(--primary); border-color: var(--primary); color: var(--gold); }}
.cat-t11-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; }}
@media (max-width: 900px) {{ .cat-t11-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
@media (max-width: 600px) {{ .cat-t11-grid {{ grid-template-columns: 1fr; }} .cat-t11-hero h1 {{ font-size: 1.7rem; }} }}
"""
    return {"html": html_content, "css": css}
