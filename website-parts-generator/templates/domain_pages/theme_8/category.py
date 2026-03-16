"""Category page for Theme 8 — Aurora Borealis Dark.
Aurora hero banner with neon label + dark glassmorphism article grid.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t8-category"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    category_name        = html_module.escape(config.get("category_name", "Collection"))
    category_description = html_module.escape(config.get("category_description",
        "A vibrant selection of aurora-inspired culinary creations."))

    from shared_article_card import render_cards
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_7"
    articles  = config.get("articles") or []
    cards_html, cards_css = render_cards(articles, config, show_excerpt=True, scope_prefix=ROOT)

    html_content = f"""
<div class="dp-t8-category">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <span class="t8-hero-label">Category Archive</span>
      <h1 class="t8-hero-title">{category_name}</h1>
      <p class="t8-hero-sub">{category_description}</p>
    </div>
  </section>

  <div class="t8-wrap">
    <div class="t8-article-grid">
      {cards_html or '<p class="t8-empty">New curations for this series are illuminating soon.</p>'}
    </div>
  </div>
  <div class="index-pagination-slot"></div>
</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} background: var(--bg); }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{hero_css(ROOT, font_family)}
{body_css(ROOT, font_family)}
{cards_css}

{ROOT} .t8-article-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
}}
{ROOT} .t8-empty {{
    grid-column: 1 / -1;
    text-align: center;
    padding: 80px 20px;
    color: var(--muted);
    font-style: italic;
    background: var(--glass-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
}}
@media (max-width: 768px) {{
    {ROOT} .t8-article-grid {{ grid-template-columns: 1fr; }}
}}
"""
    return {"html": html_content, "css": css_content}
