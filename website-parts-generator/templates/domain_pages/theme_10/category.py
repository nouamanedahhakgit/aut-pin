"""Theme 10 — Category page: Bento Fresh — pill filter bar, article grid with mint accents."""
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

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".cat-t10")

    pills = ""
    for cat in categories[:12]:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or "#")
        if c_name:
            active = " cat-t10-active" if c_name.lower() == category_name.lower() else ""
            pills += f'<a href="{c_url}" class="cat-t10-pill{active}">{c_name}</a>'

    html_content = f"""
<main class="category-page cat-t10">
  <section class="cat-t10-hero">
    <div class="cat-t10-hero-inner">
      <span class="cat-t10-badge">&#127860; Category</span>
      <h1>{category_name}</h1>
      <p><strong style="color:var(--primary)">{total}</strong> recipe{"s" if total != 1 else ""} ready to explore</p>
    </div>
  </section>

  <div class="cat-t10-body">
    <div class="cat-t10-pills">{pills or '<span style="color:var(--muted);font-size:0.85rem;">No other categories</span>'}</div>
    <div class="cat-t10-grid">{cards_html}</div>
  </div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}

.cat-t10 {{ {t['css_vars']} }}

.cat-t10-hero {{
    background: var(--surface2); border-bottom: 1px solid var(--border);
    padding: 3.5rem 1.5rem 2.5rem; text-align: center;
}}
.cat-t10-hero-inner {{ max-width: 700px; margin: 0 auto; }}
.cat-t10-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--mint-pale); border: 1px solid var(--mint-border);
    color: var(--primary); padding: 5px 14px; border-radius: 50px;
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.15em; margin-bottom: 1rem;
}}
.cat-t10-hero h1 {{
    font-family: {ff}; font-size: clamp(1.8rem, 5vw, 3rem);
    font-weight: 700; margin: 0 0 0.5rem; color: var(--text); letter-spacing: -0.02em;
}}
.cat-t10-hero p {{ color: var(--muted); font-size: 1rem; }}

.cat-t10-body {{ max-width: 1280px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }}

.cat-t10-pills {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2rem; }}
.cat-t10-pill {{
    padding: 0.45rem 1.1rem; border-radius: 50px;
    border: 1.5px solid var(--border); color: var(--muted);
    text-decoration: none; font-size: 0.85rem; font-weight: 600; transition: all 0.2s;
    background: var(--bg);
}}
.cat-t10-pill:hover {{ border-color: var(--primary); color: var(--primary); background: var(--mint-pale); }}
.cat-t10-pill.cat-t10-active {{
    background: var(--primary); border-color: var(--primary); color: #fff;
}}

.cat-t10-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; }}

@media (max-width: 900px) {{ .cat-t10-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
@media (max-width: 600px) {{ .cat-t10-grid {{ grid-template-columns: 1fr; }} .cat-t10-hero h1 {{ font-size: 1.7rem; }} }}
"""
    return {"html": html_content, "css": css}
