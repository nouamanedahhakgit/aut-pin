"""Index page for Theme 6 — Neo-Brutalist.
Features a bold hero section, jagged sections, and thick black borders for 
a distinct high-contrast, playful aesthetic.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t6-index"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    domain_description = html_module.escape(config.get("domain_description", "Welcome to our incredible collection of recipes and cooking tips."))
    categories = config.get("categories") or []
    
    # ── Category Spotlight ──────────────────────────────────────────
    sections_html = ""
    for idx, cat in enumerate(categories[:2]):
        name = html_module.escape(cat.get("name", "New Collection")).upper()
        desc = html_module.escape(cat.get("description", "A bold and punchy selection of recipes."))
        url = html_module.escape(cat.get("url", "#"))
        
        sections_html += f"""
<section class="t6-section">
  <div class="t6-flex-head">
    <h3>{name}</h3>
    <a href="{url}" class="t6-link-btn">EXPLORE &rarr;</a>
  </div>
  <div class="t6-body">
    <p>{desc}</p>
  </div>
</section>
"""

    # ── Latest Articles Grid ──────────────────────────────────────
    from shared_article_card import render_cards
    # Set default template for this theme if not specified
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_6"
    
    articles = config.get("articles") or []
    cards_html, cards_css = render_cards(articles, config, show_excerpt=True, scope_prefix=ROOT)

    html_content = f"""
<div class="dp-t6-index">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">{domain_name}</h1>
      <p class="t6-hero-sub">{domain_description}</p>
    </div>
  </section>

  <div class="t6-wrap">
    <h2 class="t6-sec-title">LATEST DISCOVERIES</h2>
    
    <div class="t6-article-grid">
        {cards_html or '<p class="t6-empty">FRESH RECIPES LOADING NOW...</p>'}
    </div>

    {sections_html}
    
    <section class="t6-section" style="background: var(--secondary); color:#fff; transform: rotate(0deg) !important; margin-top: 80px;">
      <h3 style="background: white; color: black; border: 4px solid #000; padding: 10px 20px;">ABOUT OUR MISSION</h3>
      <div class="t6-body" style="margin-top: 40px;">
        <p>We are dedicated to making cooking accessible, bold, and undeniably fun. From quick weeknight dinners to extravagant weekend feasts, we've got you covered with a fresh perspective on flavors.</p>
        <p>Our community of food lovers is growing every day. Join us as we explore new ingredients and classic techniques updated for the modern kitchen.</p>
      </div>
    </section>
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

{ROOT} .t6-sec-title {{
    font-family: {font_family};
    font-size: 2.5rem;
    font-weight: 950;
    margin: 0 0 40px;
    background: var(--secondary);
    color: white;
    padding: 10px 30px;
    display: table;
    border: 4px solid #000;
    box-shadow: 6px 6px 0px #000;
}}
{ROOT} .t6-article-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 40px;
    margin-bottom: 100px;
}}
{ROOT} .t6-flex-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}}
{ROOT} .t6-flex-head h3 {{
    margin: 0 !important;
}}
{ROOT} .t6-link-btn {{
    background: var(--primary);
    color: black;
    border: 3px solid #000;
    padding: 8px 20px;
    font-weight: 900;
    text-decoration: none;
    box-shadow: 4px 4px 0px #000;
    transition: transform 0.1s, box-shadow 0.1s;
}}
{ROOT} .t6-link-btn:hover {{
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0px #000;
}}
{ROOT} .t6-empty {{
    grid-column: 1 / -1;
    text-align: center;
    padding: 100px;
    background: #fff;
    border: 4px solid #000;
    box-shadow: 8px 8px 0px #000;
    font-weight: 900;
    color: var(--muted);
}}

@media (max-width: 768px) {{
    {ROOT} .t6-article-grid {{ grid-template-columns: 1fr; }}
    {ROOT} .t6-flex-head {{ flex-direction: column; align-items: flex-start; gap: 20px; }}
    {ROOT} .t6-sec-title {{ font-size: 1.5rem; }}
}}
"""
    return {"html": html_content, "css": css_content}
