"""Category listing page for Theme 7 — Midnight Luxe.
Hero with category name, pill nav for all categories, article card grid.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
from shared_article_card import render_cards
import html as html_module

ROOT = ".dp-t7-category"
e = html_module.escape


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    category_name = e(config.get("category_name", "Category"))
    base_url = e(config.get("base_url") or config.get("domain_url", "/"))
    articles = config.get("articles") or []
    categories = config.get("categories") or []
    total = config.get("total", len(articles))

    # ── Hero ─────────────────────────────────────────────────────────
    hero_section = f"""
    <section class="t7-cat-hero">
      <div class="t7-cat-hero-inner">
        <span class="t7-badge">Category</span>
        <h1 class="t7-cat-hero-title">{category_name}</h1>
        <p class="t7-cat-hero-count">{total} recipe{"s" if total != 1 else ""} to explore</p>
        <div class="t7-cat-hero-rule"></div>
      </div>
    </section>"""

    # ── Category pills ───────────────────────────────────────────────
    pills_html = ""
    for cat in categories:
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url", "#"))
        active = "t7-cat-pill-active" if c_name.lower() == category_name.lower() else ""
        pills_html += f'<a class="t7-cat-pill {active}" href="{c_url}">{c_name}</a>\n'

    catnav = f"""
    <section class="t7-cat-nav">
      <div class="t7-cat-nav-inner">
        <div class="t7-cat-pills">
          <a class="t7-cat-pill" href="{base_url}recipes/">All</a>
          {pills_html}
        </div>
      </div>
    </section>"""

    # ── Article grid ─────────────────────────────────────────────────
    cards_html, card_css = render_cards(
        articles, config, show_excerpt=True, scope_prefix=ROOT
    )

    grid_section = f"""
    <section class="t7-cat-grid-section">
      <div class="t7-cat-grid-inner">
        <div class="t7-cat-cards">{cards_html}</div>
      </div>
    </section>"""

    # ── Pagination slot ──────────────────────────────────────────────
    pagination = '<div class="index-pagination-slot"></div>'

    # ── Assemble HTML ────────────────────────────────────────────────
    html_content = f"""
<main class="dp-t7-category category-page">
  {hero_section}
  {catnav}
  {grid_section}
  {pagination}
</main>
"""

    # ── Assemble CSS ─────────────────────────────────────────────────
    _hero = hero_css(ROOT, font_family)
    _body = body_css(ROOT, font_family)

    page_css = f"""
{font_import}
{ROOT} {{
    {css_vars}
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{_hero}
{_body}
/* ════════════════════════════════════════════════════
   CATEGORY HERO
   ════════════════════════════════════════════════════ */
{ROOT} .t7-cat-hero {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 55%, var(--primary) 100%);
    padding: 72px 32px 56px;
    text-align: center;
    color: #fff;
    position: relative;
    overflow: hidden;
}}
{ROOT} .t7-cat-hero::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 80%, rgba(212,168,83,.12) 0%, transparent 55%);
    pointer-events: none;
}}
{ROOT} .t7-cat-hero-inner {{
    max-width: 700px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}}
{ROOT} .t7-cat-hero-title {{
    font-family: {font_family};
    font-size: clamp(1.8rem, 5vw, 3rem);
    font-weight: 800;
    margin: 12px 0 10px;
    letter-spacing: .3px;
    line-height: 1.15;
    color: #fff;
}}
{ROOT} .t7-cat-hero-count {{
    font-size: .88rem;
    color: rgba(255,255,255,.6);
    margin: 0 0 20px;
}}
{ROOT} .t7-cat-hero-rule {{
    width: 40px;
    height: 3px;
    background: var(--gold);
    border-radius: 2px;
    margin: 0 auto;
}}
/* ════════════════════════════════════════════════════
   CATEGORY PILL NAV
   ════════════════════════════════════════════════════ */
{ROOT} .t7-cat-nav {{
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    padding: 20px 32px;
    position: sticky;
    top: 64px;
    z-index: 40;
}}
{ROOT} .t7-cat-nav-inner {{
    max-width: 1140px;
    margin: 0 auto;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
}}
{ROOT} .t7-cat-nav-inner::-webkit-scrollbar {{ display: none; }}
{ROOT} .t7-cat-pills {{
    display: flex;
    gap: 8px;
    flex-wrap: nowrap;
    min-width: max-content;
}}
{ROOT} .t7-cat-pill {{
    display: inline-block;
    padding: 8px 20px;
    border: 1px solid var(--border);
    border-radius: 40px;
    text-decoration: none;
    color: var(--muted);
    font-size: .82rem;
    font-weight: 600;
    white-space: nowrap;
    transition: background .3s, color .3s, border-color .3s, transform .3s;
}}
{ROOT} .t7-cat-pill:hover {{
    border-color: var(--primary);
    color: var(--primary);
    transform: translateY(-1px);
}}
{ROOT} .t7-cat-pill-active {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    border-color: transparent;
}}
{ROOT} .t7-cat-pill-active:hover {{
    color: #fff;
    border-color: transparent;
    opacity: .9;
}}
/* ════════════════════════════════════════════════════
   ARTICLE GRID
   ════════════════════════════════════════════════════ */
{ROOT} .t7-cat-grid-section {{
    padding: 56px 32px 72px;
    background: var(--bg);
}}
{ROOT} .t7-cat-grid-inner {{
    max-width: 1140px;
    margin: 0 auto;
}}
{ROOT} .t7-cat-cards {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px;
}}
/* ════════════════════════════════════════════════════
   RESPONSIVE
   ════════════════════════════════════════════════════ */
@media (max-width: 768px) {{
    {ROOT} .t7-cat-hero {{ padding: 56px 20px 44px; }}
    {ROOT} .t7-cat-nav {{ padding: 14px 20px; top: 56px; }}
    {ROOT} .t7-cat-grid-section {{ padding: 40px 20px 56px; }}
    {ROOT} .t7-cat-cards {{ grid-template-columns: repeat(2, 1fr); gap: 20px; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t7-cat-hero {{ padding: 44px 16px 36px; }}
    {ROOT} .t7-cat-hero-title {{ font-size: clamp(1.5rem, 6vw, 2.2rem); }}
    {ROOT} .t7-cat-nav {{ padding: 12px 16px; }}
    {ROOT} .t7-cat-pill {{ padding: 6px 14px; font-size: .76rem; }}
    {ROOT} .t7-cat-grid-section {{ padding: 32px 16px 48px; }}
    {ROOT} .t7-cat-cards {{ grid-template-columns: 1fr; gap: 18px; }}
}}
"""

    css_content = page_css + "\n" + card_css
    return {"html": html_content, "css": css_content}
