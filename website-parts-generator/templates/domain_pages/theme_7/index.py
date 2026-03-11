"""Index page for Theme 7 — Minimalist Glass.
Features a soft gradient hero, airy content spacing, and glassmorphism-style 
content cards for a high-end, contemporary aesthetic.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t7-index"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    domain_description = html_module.escape(config.get("domain_description", "Experience culinary art through a lens of purity and refined simplicity."))
    categories = config.get("categories") or []
    
    # ── Category Spotlight ──────────────────────────────────────────
    sections_html = ""
    for idx, cat in enumerate(categories[:2]):
        name = html_module.escape(cat.get("name", "New Curation"))
        desc = html_module.escape(cat.get("description", "A carefully selected group of inspired culinary creations."))
        url = html_module.escape(cat.get("url", "#"))
        
        sections_html += f"""
<section class="t7-section">
  <div class="t7-card">
    <div class="t7-card-head">
        <h3>{name}</h3>
        <a href="{url}" class="t7-link-text">Browse Collection &rarr;</a>
    </div>
    <div class="t7-body">
      <p>{desc}</p>
    </div>
  </div>
</section>
"""

    # ── Latest Articles Grid ──────────────────────────────────────
    from shared_article_card import render_cards
    # Set default template for this theme if not specified
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_7"
    
    articles = config.get("articles") or []
    cards_html, cards_css = render_cards(articles, config, show_excerpt=True, scope_prefix=ROOT)

    html_content = f"""
<div class="dp-t7-index">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">{domain_name}</h1>
      <p class="t7-hero-sub">{domain_description}</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-grid-head">
        <h2 class="t7-sec-title">The Latest Inspiration</h2>
        <p class="t7-sec-sub">Recently discovered flavors and refined techniques.</p>
    </div>
    
    <div class="t7-article-grid">
        {cards_html or '<p class="t7-empty">New inspirations are being curated...</p>'}
    </div>

    {sections_html}
    
    <div class="t7-section">
      <div class="t7-card" style="background: var(--primary); color: #fff; box-shadow: 0 40px 100px rgba(0,0,0,0.1);">
        <div class="t7-card-head" style="border-bottom: 1px solid rgba(255,255,255,0.2);">
            <h3 style="color:#fff;">The Serene Promise</h3>
        </div>
        <div class="t7-body" style="color: rgba(255,255,255,0.85); margin-top: 20px;">
          <p>We are creating a space where flavor meets stillness. Every recipe on {domain_name} is curated to bring balance and minimalist beauty to your table.</p>
        </div>
      </div>
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

{ROOT} .t7-grid-head {{
    text-align: center;
    margin-bottom: 50px;
}}
{ROOT} .t7-sec-title {{
    font-family: {font_family};
    font-size: 2.2rem;
    color: var(--primary);
    margin: 0 0 10px;
}}
{ROOT} .t7-sec-sub {{
    font-size: 1rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.05em;
}}
{ROOT} .t7-article-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 30px;
    margin-bottom: 80px;
}}
{ROOT} .t7-card-head {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    margin-bottom: 20px;
    padding-bottom: 15px;
}}
{ROOT} .t7-card-head h3 {{
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
}}
{ROOT} .t7-card-head h3::after {{ display: none !important; }}

{ROOT} .t7-link-text {{
    color: var(--secondary);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
    transition: opacity 0.2s;
}}
{ROOT} .t7-link-text:hover {{ opacity: 0.7; }}
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
    {ROOT} .t7-card-head {{ flex-direction: column; gap: 10px; }}
}}
"""
    return {"html": html_content, "css": css_content}
