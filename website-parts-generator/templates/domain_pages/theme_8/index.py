"""Index page for Theme 8 — Aurora Borealis Dark.
Deep obsidian hero with animated radial aurora mesh, vivid gradient
headings, glassmorphism article cards, and glowing category spotlight panels.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t8-index"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name        = html_module.escape(config.get("domain_name", "My Blog"))
    domain_description = html_module.escape(config.get("domain_description",
        "Bold flavors illuminated under the aurora — a culinary journey unlike any other."))
    categories = config.get("categories") or []

    # ── Category Spotlight ──────────────────────────────────────────
    cat_cards = ""
    for cat in categories[:3]:
        name = html_module.escape(cat.get("name", "Collection"))
        desc = html_module.escape(cat.get("description", "A curated selection of inspired recipes."))
        url  = html_module.escape(cat.get("url", "#"))
        cat_cards += f"""
<div class="t8-cat-card">
  <div class="t8-cat-glow"></div>
  <h3>{name}</h3>
  <p>{desc}</p>
  <a href="{url}" class="t8-cat-link">Browse &rarr;</a>
</div>"""

    # ── Latest Articles Grid ──────────────────────────────────────
    from shared_article_card import render_cards
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_7"
    articles = config.get("articles") or []
    cards_html, cards_css = render_cards(articles, config, show_excerpt=True, scope_prefix=ROOT)

    html_content = f"""
<div class="dp-t8-index">

  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <span class="t8-hero-label">Culinary Universe</span>
      <h1 class="t8-hero-title">{domain_name}</h1>
      <p class="t8-hero-sub">{domain_description}</p>
      <div class="t8-hero-ctas">
        <a href="#t8-latest" class="t8-btn-primary">Explore Recipes ✦</a>
      </div>
    </div>
  </section>

  <div class="t8-wrap">

    <div class="t8-section" id="t8-latest">
      <div class="t8-grid-head">
        <h2 class="t8-sec-title">Latest Inspiration</h2>
        <p class="t8-sec-sub">Fresh from the aurora kitchen.</p>
      </div>
      <div class="t8-article-grid">
        {cards_html or '<p class="t8-empty">New recipes are being curated under the aurora…</p>'}
      </div>
    </div>

    <div class="t8-section">
      <div class="t8-grid-head">
        <h2 class="t8-sec-title">Curated Series</h2>
        <p class="t8-sec-sub">Hand-picked collections for every palate.</p>
      </div>
      <div class="t8-cat-grid">
        {cat_cards or '<p class="t8-empty">Collections coming soon.</p>'}
      </div>
    </div>

    <div class="t8-section">
      <div class="t8-promise-card">
        <div class="t8-promise-glow t8-pg-v"></div>
        <div class="t8-promise-glow t8-pg-c"></div>
        <div class="t8-promise-inner">
          <div class="t8-promise-label">Our Promise</div>
          <h2 class="t8-promise-title">Bold. Beautiful. Unforgettable.</h2>
          <p class="t8-promise-body">Every recipe on {domain_name} is a journey through flavor, color, and light. We believe cooking is art — and art deserves the most vibrant canvas.</p>
        </div>
      </div>
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

{ROOT} .t8-hero-ctas {{
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 40px;
    flex-wrap: wrap;
}}

{ROOT} .t8-grid-head {{
    text-align: center;
    margin-bottom: 50px;
}}
{ROOT} .t8-sec-title {{
    font-family: {font_family};
    font-size: 2rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 10px;
    letter-spacing: -0.02em;
}}
{ROOT} .t8-sec-sub {{
    font-size: 0.95rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.04em;
}}
{ROOT} .t8-article-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
    margin-bottom: 30px;
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

/* Category cards */
{ROOT} .t8-cat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
}}
{ROOT} .t8-cat-card {{
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 36px 32px;
    overflow: hidden;
    transition: transform 0.35s ease, box-shadow 0.35s ease;
}}
{ROOT} .t8-cat-card:hover {{
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
}}
{ROOT} .t8-cat-glow {{
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(124,58,237,0.2), transparent 70%);
    transition: transform 0.5s ease;
}}
{ROOT} .t8-cat-card:hover .t8-cat-glow {{ transform: scale(1.3); }}
{ROOT} .t8-cat-card h3 {{
    font-family: {font_family};
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 12px;
    position: relative;
}}
{ROOT} .t8-cat-card p {{
    font-size: 0.92rem;
    color: var(--muted);
    line-height: 1.7;
    margin: 0 0 24px;
    position: relative;
}}
{ROOT} .t8-cat-link {{
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--secondary);
    text-decoration: none;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    position: relative;
    transition: opacity 0.2s;
}}
{ROOT} .t8-cat-link:hover {{ opacity: 0.7; }}

/* Promise card */
{ROOT} .t8-promise-card {{
    position: relative;
    background: linear-gradient(135deg, #0F1624, #141D2E);
    border: 1px solid var(--border);
    border-radius: 32px;
    padding: 80px 60px;
    text-align: center;
    overflow: hidden;
}}
{ROOT} .t8-promise-glow {{
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    animation: t8-glow-pulse 6s ease-in-out infinite;
}}
{ROOT} .t8-pg-v {{
    width: 400px; height: 400px;
    top: -100px; left: -100px;
    background: rgba(124,58,237,0.18);
}}
{ROOT} .t8-pg-c {{
    width: 300px; height: 300px;
    bottom: -80px; right: -80px;
    background: rgba(6,182,212,0.15);
    animation-delay: 3s;
}}
{ROOT} .t8-promise-inner {{ position: relative; z-index: 1; }}
{ROOT} .t8-promise-label {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.25em;
    color: var(--accent);
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.25);
    padding: 6px 18px;
    border-radius: 50px;
    margin-bottom: 24px;
}}
{ROOT} .t8-promise-title {{
    font-family: {font_family};
    font-size: clamp(1.8rem, 4vw, 3rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #fff 0%, var(--secondary) 50%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 20px;
}}
{ROOT} .t8-promise-body {{
    font-size: 1.05rem;
    color: var(--muted);
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.8;
    font-weight: 300;
}}

@media (max-width: 768px) {{
    {ROOT} .t8-article-grid {{ grid-template-columns: 1fr; }}
    {ROOT} .t8-cat-grid     {{ grid-template-columns: 1fr; }}
    {ROOT} .t8-promise-card  {{ padding: 48px 24px; }}
}}
"""
    return {"html": html_content, "css": css_content}
