"""Category page for Theme 6 — Neo-Brutalist.
Bold and boxy layout for category content with high contrast.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t6-category"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    category_name = html_module.escape(config.get("category_name", "Collection")).upper()
    category_description = html_module.escape(config.get("category_description", "A bold selection of recipes from our archives."))
    
    # ── Latest Articles Grid ──────────────────────────────────────
    from shared_article_card import render_cards
    # Set default template for this theme if not specified
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_6"
    
    articles = config.get("articles") or []
    cards_html, cards_css = render_cards(articles, config, show_excerpt=True, scope_prefix=ROOT)

    html_content = f"""
<div class="dp-t6-category">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <span class="t6-hero-label">SERIES ARCHIVE</span>
      <h1 class="t6-hero-title">{category_name}</h1>
      <p class="t6-hero-sub">{category_description}</p>
    </div>
  </section>

  <div class="t6-wrap">
    <div class="t6-article-grid">
        {cards_html or '<p class="t6-empty">FRESH CURATIONS IN PROGRESS...</p>'}
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

{ROOT} .t6-hero-label {{
    display: block;
    font-size: 0.9rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--secondary);
    margin-bottom: 20px;
}}
{ROOT} .t6-article-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 40px;
}}
{ROOT} .t6-empty {{
    grid-column: 1 / -1;
    text-align: center;
    padding: 100px;
    background: #fff;
    border: 4px solid #000;
    box-shadow: 8px 8px 0px #000;
    font-weight: 900;
}}

@media (max-width: 768px) {{
    {ROOT} .t6-article-grid {{ grid-template-columns: 1fr; }}
}}
"""
    return {"html": html_content, "css": css_content}
