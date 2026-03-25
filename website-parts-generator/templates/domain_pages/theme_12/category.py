"""Theme 12 — Category page: Candy Pop — bouncy colorful pills, playful article grid."""
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

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".cat-t12")

    COLORS = ["var(--primary)", "var(--secondary)", "var(--accent)", "var(--lavender)", "var(--yellow)"]
    pills = ""
    for i, cat in enumerate(categories[:12]):
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or "#")
        color = COLORS[i % len(COLORS)]
        if c_name:
            active = " cat-t12-active" if c_name.lower() == category_name.lower() else ""
            pills += f'<a href="{c_url}" class="cat-t12-pill{active}" style="--pill-color:{color}">{c_name}</a>'

    html_content = f"""
<main class="category-page cat-t12">
  <section class="cat-t12-hero">
    <div class="cat-t12-hero-inner">
      <span class="cat-t12-badge">&#127860; Category</span>
      <h1>{category_name}</h1>
      <p><strong style="color:var(--primary)">{total}</strong> fun recipe{"s" if total != 1 else ""} to explore! &#10024;</p>
    </div>
  </section>
  <div class="cat-t12-body">
    <div class="cat-t12-pills">{pills or '<span style="color:var(--muted);font-size:0.85rem;">No other categories</span>'}</div>
    <div class="cat-t12-grid">{cards_html}</div>
  </div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}
.cat-t12 {{ {t['css_vars']} }}
.cat-t12-hero {{
    background: linear-gradient(145deg, var(--surface2), var(--blue-pale), var(--surface));
    padding: 3.5rem 1.5rem 2.5rem; text-align: center;
    border-bottom: 4px solid transparent;
    border-image: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent), var(--lavender)) 1;
}}
.cat-t12-hero-inner {{ max-width: 700px; margin: 0 auto; }}
.cat-t12-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--pink-pale); border: 2px solid var(--pink-border);
    color: var(--primary); padding: 5px 16px; border-radius: 50px;
    font-size: 0.78rem; font-weight: 800; margin-bottom: 1rem;
}}
.cat-t12-hero h1 {{
    font-family: {ff}; font-size: clamp(1.8rem, 5vw, 3rem);
    font-weight: 900; margin: 0 0 0.5rem; color: var(--text);
}}
.cat-t12-hero p {{ color: var(--muted); font-size: 1rem; font-weight: 500; }}
.cat-t12-body {{ max-width: 1280px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }}
.cat-t12-pills {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2rem; justify-content: center; }}
.cat-t12-pill {{
    padding: 0.45rem 1.1rem; border-radius: 50px;
    border: 2px solid var(--pill-color); color: var(--pill-color);
    text-decoration: none; font-size: 0.85rem; font-weight: 700;
    transition: all 0.3s; background: transparent;
}}
.cat-t12-pill:hover {{ background: var(--pill-color); color: #fff; transform: translateY(-3px) scale(1.05); }}
.cat-t12-pill.cat-t12-active {{ background: var(--primary); border-color: var(--primary); color: #fff; }}
.cat-t12-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; }}
@media (max-width: 900px) {{ .cat-t12-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
@media (max-width: 600px) {{ .cat-t12-grid {{ grid-template-columns: 1fr; }} .cat-t12-hero h1 {{ font-size: 1.7rem; }} }}
"""
    return {"html": html_content, "css": css}
