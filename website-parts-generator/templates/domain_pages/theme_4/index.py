"""Index / Home page for Theme 7 — Midnight Luxe.
Rich multi-section layout: featured hero, category showcases, category nav,
latest recipes grid, and pagination slot.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
from shared_article_card import render_cards
import html as html_module

ROOT = ".dp-t7-index"
e = html_module.escape


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = e(config.get("domain_name", "My Blog"))
    base_url = e(config.get("base_url") or config.get("domain_url", "/"))
    articles = config.get("articles") or []
    categories = config.get("categories") or []

    # ── 1. HERO — Featured article ───────────────────────────────────
    feat = articles[0] if articles else {}
    feat_title = e(feat.get("title", "Welcome to Our Kitchen"))
    feat_url = e(feat.get("url", "#"))
    feat_excerpt = e(feat.get("excerpt", "Discover handcrafted recipes that bring warmth and joy to your table."))
    feat_cat = e(feat.get("category", ""))
    fi = (feat.get("main_image") or feat.get("image") or "").strip()
    if fi and fi.startswith("http"):
        feat_img = f'<img src="{e(fi)}" alt="{feat_title}" class="t7-idx-hero-img" loading="eager">'
    else:
        feat_img = '<div class="t7-idx-hero-placeholder">&#127860;</div>'

    hero_html = f"""
    <section class="t7-idx-hero">
      <div class="t7-idx-hero-inner">
        <div class="t7-idx-hero-media">{feat_img}</div>
        <div class="t7-idx-hero-content">
          <span class="t7-badge">Featured Recipe</span>
          {f'<span class="t7-idx-hero-cat">{feat_cat}</span>' if feat_cat else ''}
          <h1 class="t7-idx-hero-title">{feat_title}</h1>
          <p class="t7-idx-hero-excerpt">{feat_excerpt}</p>
          <div class="t7-idx-hero-actions">
            <a class="t7-btn-primary" href="{feat_url}">Get Recipe</a>
            <a class="t7-btn-ghost" href="{base_url}recipes/">Browse All</a>
          </div>
        </div>
      </div>
    </section>"""

    # ── 2. CATEGORY SHOWCASES — Top 2 categories ────────────────────
    showcase_html = ""
    top_cats = categories[:2]
    showcase_slices = [articles[1:4], articles[4:7]]

    for idx, cat in enumerate(top_cats):
        c_name = e(cat.get("name", "Category"))
        c_url = e(cat.get("url", "#"))
        c_slug = e(cat.get("slug", ""))
        c_count = cat.get("count", "")
        slice_articles = showcase_slices[idx] if idx < len(showcase_slices) else []

        # Mini thumbnails
        mini_cards = ""
        for art in slice_articles[:3]:
            a_title = e(art.get("title", "Untitled"))
            a_url = e(art.get("url", "#"))
            a_img = (art.get("main_image") or art.get("image") or "").strip()
            if a_img and a_img.startswith("http"):
                thumb = f'<img src="{e(a_img)}" alt="{a_title}" class="t7-idx-mini-img" loading="lazy">'
            else:
                thumb = '<div class="t7-idx-mini-placeholder">&#127860;</div>'
            mini_cards += f"""
            <a class="t7-idx-mini-card" href="{a_url}">
              {thumb}
              <span class="t7-idx-mini-title">{a_title}</span>
            </a>"""

        reverse_cls = "t7-idx-show-reverse" if idx % 2 == 1 else ""
        showcase_html += f"""
    <div class="t7-idx-showcase {reverse_cls}">
      <div class="t7-idx-show-info">
        <div class="t7-sb-gold-dot" style="width:6px;height:6px;background:var(--gold);border-radius:50%;margin-bottom:14px;"></div>
        <h2 class="t7-idx-show-name">{c_name}</h2>
        {f'<span class="t7-idx-show-count">{c_count} Recipes</span>' if c_count else ''}
        <a class="t7-btn-primary t7-idx-show-btn" href="{c_url}">More {c_name}</a>
      </div>
      <div class="t7-idx-show-grid">{mini_cards}</div>
    </div>"""

    showcase_section = ""
    if showcase_html:
        showcase_section = f"""
    <section class="t7-idx-section t7-idx-showcases">
      <div class="t7-idx-section-inner">
        <div class="t7-rule"></div>
        <h2 class="t7-idx-section-title">Explore by Category</h2>
        {showcase_html}
      </div>
    </section>"""

    # ── 3. CATEGORY NAVIGATION — All categories ─────────────────────
    cat_pills = ""
    for cat in categories:
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url", "#"))
        c_count = cat.get("count", "")
        count_badge = f' <span class="t7-idx-pill-count">{e(str(c_count))}</span>' if c_count else ""
        cat_pills += f'<a class="t7-idx-pill" href="{c_url}">{c_name}{count_badge}</a>\n'

    catnav_section = f"""
    <section class="t7-idx-section t7-idx-catnav">
      <div class="t7-idx-section-inner">
        <div class="t7-rule"></div>
        <h2 class="t7-idx-section-title">All Categories</h2>
        <div class="t7-idx-pills">{cat_pills}</div>
      </div>
    </section>"""

    # ── 4. LATEST RECIPES — article card grid ────────────────────────
    cards_html, card_css = render_cards(
        articles, config, show_excerpt=True, scope_prefix=ROOT
    )

    latest_section = f"""
    <section class="t7-idx-section t7-idx-latest">
      <div class="t7-idx-section-inner">
        <div class="t7-rule"></div>
        <h2 class="t7-idx-section-title">Latest Recipes</h2>
        <div class="t7-idx-cards">{cards_html}</div>
        <div class="t7-idx-cta-row">
          <a class="t7-btn-ghost" href="{base_url}recipes/">View All Recipes</a>
        </div>
      </div>
    </section>"""

    # ── 5. PAGINATION SLOT ───────────────────────────────────────────
    pagination = '<div class="index-pagination-slot"></div>'

    # ── Assemble HTML ────────────────────────────────────────────────
    html_content = f"""
<main class="dp-t7-index index-page">
  {hero_html}
  {showcase_section}
  {catnav_section}
  {latest_section}
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
   FEATURED HERO
   ════════════════════════════════════════════════════ */
{ROOT} .t7-idx-hero {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 55%, var(--primary) 100%);
    position: relative;
    overflow: hidden;
}}
{ROOT} .t7-idx-hero::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 70% 40%, rgba(212,168,83,.1) 0%, transparent 60%);
    pointer-events: none;
}}
{ROOT} .t7-idx-hero-inner {{
    max-width: 1140px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 480px;
    position: relative;
    z-index: 1;
}}
{ROOT} .t7-idx-hero-media {{
    position: relative;
    overflow: hidden;
}}
{ROOT} .t7-idx-hero-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}
{ROOT} .t7-idx-hero-placeholder {{
    width: 100%;
    height: 100%;
    min-height: 360px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 4rem;
    background: linear-gradient(135deg, var(--secondary), var(--primary));
    color: rgba(255,255,255,.15);
}}
{ROOT} .t7-idx-hero-content {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 56px 48px;
    color: #fff;
}}
{ROOT} .t7-idx-hero-cat {{
    font-size: .72rem;
    font-weight: 700;
    color: rgba(255,255,255,.55);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}}
{ROOT} .t7-idx-hero-title {{
    font-family: {font_family};
    font-size: clamp(1.6rem, 4vw, 2.6rem);
    font-weight: 800;
    line-height: 1.18;
    margin: 12px 0 16px;
    color: #fff;
    letter-spacing: .3px;
}}
{ROOT} .t7-idx-hero-excerpt {{
    font-size: .92rem;
    color: rgba(255,255,255,.72);
    line-height: 1.7;
    margin: 0 0 28px;
    max-width: 440px;
}}
{ROOT} .t7-idx-hero-actions {{
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
}}
{ROOT} .t7-idx-hero-actions .t7-btn-ghost {{
    border-color: rgba(255,255,255,.3);
    color: rgba(255,255,255,.85);
}}
{ROOT} .t7-idx-hero-actions .t7-btn-ghost:hover {{
    border-color: var(--gold);
    color: var(--gold);
}}
/* ════════════════════════════════════════════════════
   SECTIONS (shared)
   ════════════════════════════════════════════════════ */
{ROOT} .t7-idx-section {{
    padding: 64px 32px;
}}
{ROOT} .t7-idx-section-inner {{
    max-width: 1140px;
    margin: 0 auto;
}}
{ROOT} .t7-idx-section-title {{
    font-family: {font_family};
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: .3px;
    margin: 0 0 36px;
    color: var(--text);
}}
/* ════════════════════════════════════════════════════
   CATEGORY SHOWCASES
   ════════════════════════════════════════════════════ */
{ROOT} .t7-idx-showcases {{
    background: var(--bg);
}}
{ROOT} .t7-idx-showcase {{
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 36px;
    align-items: start;
    margin-bottom: 48px;
    padding: 32px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--glow);
    background: var(--bg);
}}
{ROOT} .t7-idx-showcase:last-child {{ margin-bottom: 0; }}
{ROOT} .t7-idx-show-reverse {{
    direction: rtl;
}}
{ROOT} .t7-idx-show-reverse > * {{
    direction: ltr;
}}
{ROOT} .t7-idx-show-info {{
    display: flex;
    flex-direction: column;
}}
{ROOT} .t7-idx-show-name {{
    font-family: {font_family};
    font-size: 1.35rem;
    font-weight: 800;
    margin: 0 0 6px;
    color: var(--text);
}}
{ROOT} .t7-idx-show-count {{
    font-size: .78rem;
    color: var(--muted);
    margin-bottom: 20px;
}}
{ROOT} .t7-idx-show-btn {{
    align-self: flex-start;
    font-size: .72rem;
    padding: 10px 24px;
}}
{ROOT} .t7-idx-show-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}}
{ROOT} .t7-idx-mini-card {{
    text-decoration: none;
    color: var(--text);
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: transform .3s;
}}
{ROOT} .t7-idx-mini-card:hover {{ transform: translateY(-3px); }}
{ROOT} .t7-idx-mini-img {{
    width: 100%;
    aspect-ratio: 4/3;
    object-fit: cover;
    border-radius: calc(var(--radius) * .7);
    border: 1px solid var(--border);
}}
{ROOT} .t7-idx-mini-placeholder {{
    width: 100%;
    aspect-ratio: 4/3;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    background: linear-gradient(135deg, var(--border), var(--bg));
    border-radius: calc(var(--radius) * .7);
    color: var(--muted);
}}
{ROOT} .t7-idx-mini-title {{
    font-size: .78rem;
    font-weight: 600;
    line-height: 1.35;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
/* ════════════════════════════════════════════════════
   CATEGORY NAV PILLS
   ════════════════════════════════════════════════════ */
{ROOT} .t7-idx-catnav {{
    background: var(--bg);
    border-top: 1px solid var(--border);
}}
{ROOT} .t7-idx-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}}
{ROOT} .t7-idx-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 22px;
    border: 1px solid var(--border);
    border-radius: 40px;
    text-decoration: none;
    color: var(--text);
    font-size: .84rem;
    font-weight: 600;
    transition: background .3s, color .3s, border-color .3s, transform .3s;
}}
{ROOT} .t7-idx-pill:hover {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    border-color: transparent;
    transform: translateY(-1px);
}}
{ROOT} .t7-idx-pill-count {{
    font-size: .68rem;
    font-weight: 800;
    background: var(--border);
    color: var(--muted);
    padding: 2px 8px;
    border-radius: 20px;
}}
{ROOT} .t7-idx-pill:hover .t7-idx-pill-count {{
    background: rgba(255,255,255,.2);
    color: #fff;
}}
/* ════════════════════════════════════════════════════
   LATEST RECIPES
   ════════════════════════════════════════════════════ */
{ROOT} .t7-idx-latest {{
    border-top: 1px solid var(--border);
}}
{ROOT} .t7-idx-cards {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px;
    margin-bottom: 40px;
}}
{ROOT} .t7-idx-cta-row {{
    text-align: center;
    padding-top: 8px;
}}
/* ════════════════════════════════════════════════════
   RESPONSIVE
   ════════════════════════════════════════════════════ */
@media (max-width: 768px) {{
    {ROOT} .t7-idx-hero-inner {{
        grid-template-columns: 1fr;
        min-height: auto;
    }}
    {ROOT} .t7-idx-hero-media {{ max-height: 280px; }}
    {ROOT} .t7-idx-hero-content {{ padding: 36px 24px 40px; }}
    {ROOT} .t7-idx-section {{ padding: 48px 20px; }}
    {ROOT} .t7-idx-showcase {{
        grid-template-columns: 1fr;
        padding: 24px;
    }}
    {ROOT} .t7-idx-show-reverse {{ direction: ltr; }}
    {ROOT} .t7-idx-show-grid {{ grid-template-columns: repeat(3, 1fr); gap: 12px; }}
    {ROOT} .t7-idx-cards {{ grid-template-columns: repeat(2, 1fr); gap: 20px; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t7-idx-hero-content {{ padding: 28px 16px 32px; }}
    {ROOT} .t7-idx-hero-actions {{ flex-direction: column; }}
    {ROOT} .t7-idx-hero-actions .t7-btn-primary,
    {ROOT} .t7-idx-hero-actions .t7-btn-ghost {{ text-align: center; }}
    {ROOT} .t7-idx-section {{ padding: 40px 16px; }}
    {ROOT} .t7-idx-section-title {{ font-size: 1.3rem; }}
    {ROOT} .t7-idx-showcase {{ padding: 20px 16px; }}
    {ROOT} .t7-idx-show-grid {{ grid-template-columns: 1fr 1fr; }}
    {ROOT} .t7-idx-show-grid .t7-idx-mini-card:nth-child(3) {{ display: none; }}
    {ROOT} .t7-idx-cards {{ grid-template-columns: 1fr; gap: 18px; }}
    {ROOT} .t7-idx-pills {{ gap: 8px; }}
    {ROOT} .t7-idx-pill {{ padding: 8px 16px; font-size: .78rem; }}
}}
"""

    css_content = page_css + "\n" + card_css
    return {"html": html_content, "css": css_content}
