"""Category page for Theme 7 — Minimalist Glass.
Elegant and airy layout for category content with soft glows and glassmorphism.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t7-category"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    category_name = html_module.escape(config.get("category_name", "Collection"))
    category_description = html_module.escape(config.get("category_description", "A curated selection of minimalist culinary inspirations."))
    
    # ── Latest Articles Grid ──────────────────────────────────────
    from shared_article_card import render_cards
    # Set default template for this theme if not specified
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_7"
    
    articles = config.get("articles") or []
    cards_html, cards_css = render_cards(articles, config, show_excerpt=True, scope_prefix=ROOT)

    html_content = f"""
<div class="dp-t7-category">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <span class="t7-hero-label">Category Archive</span>
      <h1 class="t7-hero-title">{category_name}</h1>
      <p class="t7-hero-sub">{category_description}</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-article-grid">
        {cards_html or '<p class="t7-empty">New curations for this series are coming soon.</p>'}
    </div>
  </div>
  <div class="index-pagination-slot"></div>
</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{hero_css(ROOT, font_family)}
{body_css(ROOT, font_family)}

{cards_css}

{ROOT} .t7-hero-label {{
    display: block;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--secondary);
    margin-bottom: 15px;
}}
{ROOT} .t7-article-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 30px;
}}
{ROOT} .t7-empty {{
    grid-column: 1 / -1;
    text-align: center;
    padding: 100px;
    background: var(--glass-bg);
    border-radius: var(--radius);
    color: var(--muted);
    font-style: italic;
}}

@media (max-width: 768px) {{
    {ROOT} .t7-article-grid {{ grid-template-columns: 1fr; }}
}}
"""
    return {"html": html_content, "css": css_content}
