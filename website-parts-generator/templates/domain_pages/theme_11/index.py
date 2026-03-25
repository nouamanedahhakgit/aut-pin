"""Theme 11 — Index: Art Deco Elegance.
Completely unique layout — NO render_cards, all custom inline rendering.
- Grand hero with sunburst ornament frame + centered title
- Gold-line connected category strip
- Magazine "Spotlight" featured panel (left image / right text with ornamental frame)
- Fan-grid article layout (alternating large/small cards with deco borders)
- Stats bar with ornamental diamond separators
- "From the Kitchen" horizontal gilded scroll strip
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    s = t["s"]
    ff = t["font_family"]

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    articles = config.get("articles", []) or []
    categories = config.get("categories", []) or []
    domain_name = html_module.escape(config.get("domain_name", s.get("domain_name", "Recipe Blog")))

    def e(v): return html_module.escape(str(v)) if v else ""

    # ── 1. GRAND HERO ────────────────────────────────────────────────────
    hero_article = articles[0] if articles else None
    hero_bg = ""
    if hero_article:
        hi = (hero_article.get("main_image") or hero_article.get("image") or "").strip()
        if hi and hi.startswith("http"):
            hero_bg = f"background-image: url('{e(hi)}');"

    # ── 2. CATEGORY STRIP ────────────────────────────────────────────────
    cat_links = ""
    for cat in categories[:8]:
        cn = e(cat.get("name") or "")
        cu = e(cat.get("url") or "#")
        if cn:
            cat_links += f'<a href="{cu}" class="it11-cat-link">{cn}</a><span class="it11-cat-sep">&#9670;</span>'
    if cat_links:
        cat_links = cat_links.rsplit('<span', 1)[0]  # remove trailing separator

    # ── 3. SPOTLIGHT FEATURED ────────────────────────────────────────────
    feat = articles[0] if articles else None
    side_list = articles[1:5] if len(articles) > 1 else []

    if feat:
        f_img = (feat.get("main_image") or feat.get("image") or "").strip()
        f_title = e((feat.get("title") or "")[:120])
        f_url = e(feat.get("url") or "#")
        f_exc = e((feat.get("excerpt") or "")[:200])
        f_cat = e(feat.get("category") or "Recipe")
        feat_img_tag = f'<img src="{e(f_img)}" alt="{f_title}" class="it11-spot-img">' if f_img and f_img.startswith("http") else '<div class="it11-spot-ph"></div>'
        feat_html = f"""
<div class="it11-spot-card">
  <div class="it11-spot-img-wrap">{feat_img_tag}</div>
  <div class="it11-spot-text">
    <div class="it11-spot-label"><span class="it11-spot-diamond">&#9670;</span> Spotlight</div>
    <span class="it11-spot-cat">{f_cat}</span>
    <h2 class="it11-spot-title"><a href="{f_url}">{f_title}</a></h2>
    <p class="it11-spot-exc">{f_exc}</p>
    <a href="{f_url}" class="it11-spot-cta">Read Recipe &rarr;</a>
  </div>
</div>"""
    else:
        feat_html = ""

    side_items = ""
    for i, art in enumerate(side_list):
        a_title = e((art.get("title") or "")[:70])
        a_url = e(art.get("url") or "#")
        a_cat = e(art.get("category") or "")
        side_items += f"""
<a href="{a_url}" class="it11-rank-item">
  <span class="it11-rank-num">{i+2:02d}</span>
  <div class="it11-rank-body">
    <span class="it11-rank-cat">{a_cat}</span>
    <span class="it11-rank-title">{a_title}</span>
  </div>
</a>"""

    # ── 4. STATS BAR ─────────────────────────────────────────────────────
    stats = [
        (str(len(articles)) + "+", "Recipes"),
        (str(len(categories)), "Categories"),
        ("100%", "Tested"),
    ]
    stats_html = '<span class="it11-stat-sep">&#9670;</span>'.join(f"""
<div class="it11-stat">
  <span class="it11-stat-n">{v}</span>
  <span class="it11-stat-l">{lb}</span>
</div>""" for v, lb in stats)

    # ── 5. FAN GRID — alternating deco card sizes ────────────────────────
    grid_articles = articles[:8] if articles else []
    SIZES = ["tall", "std", "std", "wide", "std", "tall", "std", "std"]
    grid_cards = ""
    for i, art in enumerate(grid_articles):
        a_img = (art.get("main_image") or art.get("image") or "").strip()
        a_title = e((art.get("title") or "")[:80])
        a_url = e(art.get("url") or "#")
        a_cat = e(art.get("category") or "Recipe")
        sz = SIZES[i % len(SIZES)]
        has_img = a_img and a_img.startswith("http")
        img_block = f'<img src="{e(a_img)}" alt="{a_title}" class="it11-gc-img">' if has_img else '<div class="it11-gc-ph"></div>'
        grid_cards += f"""
<a href="{a_url}" class="it11-gc it11-gc-{sz}">
  <div class="it11-gc-imgwrap">{img_block}</div>
  <div class="it11-gc-body">
    <span class="it11-gc-cat">{a_cat}</span>
    <h3 class="it11-gc-title">{a_title}</h3>
  </div>
</a>"""
    if not grid_cards:
        grid_cards = '<p class="it11-empty" style="grid-column:1/-1;">No recipes yet — add some titles and generate articles!</p>'

    # ── 6. HORIZONTAL GILDED STRIP ───────────────────────────────────────
    h_strip = ""
    for art in articles[:6]:
        a_img = (art.get("main_image") or art.get("image") or "").strip()
        a_title = e((art.get("title") or "")[:60])
        a_url = e(art.get("url") or "#")
        thmb = f'<img src="{e(a_img)}" alt="{a_title}" class="it11-hs-img">' if a_img and a_img.startswith("http") else '<div class="it11-hs-ph"></div>'
        h_strip += f"""
<a href="{a_url}" class="it11-hs-card">
  <div class="it11-hs-thumb">{thmb}</div>
  <span class="it11-hs-title">{a_title}</span>
</a>"""

    html_content = f"""
<main class="index-page it11-index">

  <!-- ░░ GRAND HERO ░░ -->
  <section class="it11-hero-section">
    <div class="it11-hero-frame">
      <div class="it11-hero-ornament-top">&#9671; &#9670; &#9671;</div>
      <p class="it11-hero-sub">Curated recipes &amp; culinary stories</p>
      <h1 class="it11-hero-h1">{domain_name}</h1>
      <div class="it11-hero-rule"></div>
      <p class="it11-hero-desc">Where timeless flavors meet elegant presentation</p>
      <div class="it11-hero-ornament-bottom">&#9671; &#9670; &#9671;</div>
    </div>
  </section>

  <!-- ░░ CATEGORY STRIP ░░ -->
  <div class="it11-catstrip-wrap">
    <div class="it11-catstrip">
      {cat_links or '<span class="it11-cat-link">All Recipes</span>'}
    </div>
  </div>

  <!-- ░░ SPOTLIGHT + RANKING ░░ -->
  <section class="it11-spotlight-section">
    <div class="it11-section-head">
      <span class="it11-section-ornament">&#9671;</span>
      <h2 class="it11-section-title">Editor&rsquo;s Spotlight</h2>
      <span class="it11-section-ornament">&#9671;</span>
    </div>
    <div class="it11-spotlight-inner">
      <div class="it11-spotlight-left">
        {feat_html or '<p class="it11-empty">Add recipes to see featured content.</p>'}
      </div>
      <div class="it11-spotlight-right">
        <h3 class="it11-rank-heading">Also Notable</h3>
        <div class="it11-rank-list">{side_items or '<p class="it11-empty">More recipes coming soon</p>'}</div>
      </div>
    </div>
  </section>

  <!-- ░░ STATS BAR ░░ -->
  <div class="it11-statsbar">
    {stats_html}
  </div>

  <!-- ░░ FAN GRID ░░ -->
  <section class="it11-grid-section">
    <div class="it11-section-head">
      <span class="it11-section-ornament">&#9671;</span>
      <h2 class="it11-section-title">Latest Recipes</h2>
      <span class="it11-section-ornament">&#9671;</span>
    </div>
    <div class="it11-fangrid">{grid_cards}</div>
    <div class="it11-viewall-wrap">
      <a href="{e(base_url)}/recipes" class="it11-viewall">View All Recipes &rarr;</a>
    </div>
  </section>

  <!-- ░░ HORIZONTAL STRIP ░░ -->
  {f'''
  <section class="it11-hs-section">
    <div class="it11-section-head">
      <span class="it11-section-ornament">&#9671;</span>
      <h2 class="it11-section-title">From the Kitchen</h2>
      <span class="it11-section-ornament">&#9671;</span>
    </div>
    <div class="it11-hs">{h_strip}</div>
  </section>''' if h_strip else ""}

  <div class="index-pagination-slot"></div>
</main>
"""

    css = f"""
{t['font_import']}
.it11-index {{ {t['css_vars']} min-height: 100vh; }}

/* ════ GRAND HERO ════════════════════════════════════════════════════ */
.it11-hero-section {{
    background: var(--primary); text-align: center;
    padding: 5rem 1.5rem 4.5rem; position: relative; overflow: hidden;
}}
.it11-hero-section::before {{
    content: ''; position: absolute; top: -100px; left: 50%;
    transform: translateX(-50%); width: 500px; height: 500px;
    background: conic-gradient(from 0deg, transparent 0deg, var(--gold-light) 15deg, transparent 30deg);
    border-radius: 50%; animation: t11-fan-spin 40s linear infinite;
    pointer-events: none;
}}
@keyframes t11-fan-spin {{ from {{ transform: translateX(-50%) rotate(0deg); }} to {{ transform: translateX(-50%) rotate(360deg); }} }}
.it11-hero-frame {{
    max-width: 680px; margin: 0 auto; position: relative; z-index: 1;
    border: 1px solid var(--gold-border); padding: 3rem 2.5rem;
    animation: t11-fade-in 0.8s ease both;
}}
@keyframes t11-fade-in {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.it11-hero-ornament-top, .it11-hero-ornament-bottom {{
    color: var(--gold); font-size: 0.5rem; letter-spacing: 0.5em; margin-bottom: 1rem;
}}
.it11-hero-ornament-bottom {{ margin-bottom: 0; margin-top: 1rem; }}
.it11-hero-sub {{
    font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.3em; color: var(--gold); margin: 0 0 0.5rem;
}}
.it11-hero-h1 {{
    font-family: {ff}; font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 700; color: var(--text-on-primary); margin: 0 0 0.75rem;
    line-height: 1.15; letter-spacing: 0.02em;
}}
.it11-hero-rule {{
    width: 60px; height: 2px; background: var(--gold); margin: 0 auto 0.75rem;
}}
.it11-hero-desc {{
    color: var(--text-on-primary-muted); font-size: 1rem; margin: 0;
    font-style: italic; line-height: 1.6;
}}

/* ════ CATEGORY STRIP ═══════════════════════════════════════════════ */
.it11-catstrip-wrap {{
    background: var(--surface2); border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
}}
.it11-catstrip {{
    max-width: 1200px; margin: 0 auto; padding: 0.85rem 1.5rem;
    display: flex; align-items: center; justify-content: center; gap: 0.5rem;
    overflow-x: auto; scrollbar-width: none; flex-wrap: wrap;
}}
.it11-catstrip::-webkit-scrollbar {{ display: none; }}
.it11-cat-link {{
    text-decoration: none; color: var(--menu-link, var(--muted)); font-size: 0.78rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em;
    padding: 0.3rem 0.8rem; transition: color 0.25s; white-space: nowrap;
}}
.it11-cat-link:hover {{ color: var(--menu-link-hover); }}
.it11-cat-sep {{ color: var(--gold); font-size: 0.35rem; opacity: 0.5; }}

/* ════ SECTION HEADS ════════════════════════════════════════════════ */
.it11-section-head {{
    display: flex; align-items: center; justify-content: center; gap: 12px;
    margin-bottom: 2rem; text-align: center;
}}
.it11-section-ornament {{ color: var(--gold); font-size: 0.5rem; }}
.it11-section-title {{
    font-family: {ff}; font-size: 1.6rem; font-weight: 700;
    color: var(--text); margin: 0; text-transform: uppercase;
    letter-spacing: 0.1em;
}}

/* ════ SPOTLIGHT + RANKING ══════════════════════════════════════════ */
.it11-spotlight-section {{
    max-width: 1200px; margin: 3rem auto 0; padding: 0 1.5rem;
}}
.it11-spotlight-inner {{
    display: grid; grid-template-columns: 1.6fr 1fr; gap: 2rem; align-items: start;
}}
.it11-spot-card {{
    border: 1px solid var(--border); overflow: hidden; background: var(--bg);
    box-shadow: var(--shadow-sm); transition: box-shadow 0.3s;
}}
.it11-spot-card:hover {{ box-shadow: var(--shadow-lg); }}
.it11-spot-img-wrap {{ display: block; aspect-ratio: 16/9; overflow: hidden; }}
.it11-spot-img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; display: block; }}
.it11-spot-card:hover .it11-spot-img {{ transform: scale(1.04); }}
.it11-spot-ph {{ width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, var(--surface2), var(--gold-light)); }}
.it11-spot-text {{ padding: 1.5rem; }}
.it11-spot-label {{
    display: flex; align-items: center; gap: 6px;
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.15em; color: var(--gold); margin-bottom: 0.5rem;
}}
.it11-spot-diamond {{ font-size: 0.5rem; }}
.it11-spot-cat {{
    display: inline-block; font-size: 0.68rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: var(--secondary); margin-bottom: 0.35rem;
}}
.it11-spot-title {{ font-family: {ff}; font-size: 1.35rem; font-weight: 700; margin: 0 0 0.6rem; line-height: 1.25; }}
.it11-spot-title a {{ text-decoration: none; color: var(--text); transition: color 0.25s; }}
.it11-spot-title a:hover {{ color: var(--menu-link-hover); }}
.it11-spot-exc {{ color: var(--muted); font-size: 0.9rem; line-height: 1.7; margin-bottom: 1rem; }}
.it11-spot-cta {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--primary); color: var(--gold); padding: 0.55rem 1.5rem;
    text-decoration: none; font-weight: 600; font-size: 0.8rem;
    text-transform: uppercase; letter-spacing: 0.1em; border: 1px solid var(--gold);
    transition: all 0.3s;
}}
.it11-spot-cta:hover {{ background: var(--gold); color: var(--primary); }}

/* Ranking side list */
.it11-rank-heading {{
    font-family: {ff}; font-size: 0.85rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.15em; color: var(--text);
    margin: 0 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border);
}}
.it11-rank-list {{ display: flex; flex-direction: column; gap: 0; }}
.it11-rank-item {{
    display: flex; gap: 1rem; align-items: center; text-decoration: none;
    color: var(--text); padding: 0.85rem 0.5rem;
    border-bottom: 1px solid var(--border); transition: all 0.25s;
}}
.it11-rank-item:last-child {{ border-bottom: none; }}
.it11-rank-item:hover {{ color: var(--menu-link-hover); padding-left: 0.75rem; }}
.it11-rank-num {{
    width: 36px; height: 36px; background: var(--primary); color: var(--gold);
    font-family: {ff}; font-size: 0.85rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.it11-rank-body {{ flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }}
.it11-rank-cat {{ font-size: 0.65rem; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 0.1em; }}
.it11-rank-title {{ font-size: 0.88rem; font-weight: 600; color: inherit; line-height: 1.35; }}

/* ════ STATS BAR ════════════════════════════════════════════════════ */
.it11-statsbar {{
    max-width: 800px; margin: 3rem auto 0; padding: 0 1.5rem;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid var(--border-light, var(--border)); background: var(--primary);
}}
.it11-stat {{
    text-align: center; padding: 1.5rem 2rem;
    display: flex; flex-direction: column; align-items: center; gap: 4px;
    flex: 1;
}}
.it11-stat-n {{
    display: block; font-family: {ff}; font-size: 2.2rem; font-weight: 700;
    color: var(--text-on-primary, var(--gold)); line-height: 1;
}}
.it11-stat-l {{
    font-size: 0.72rem; font-weight: 600; color: var(--text-on-primary-muted);
    text-transform: uppercase; letter-spacing: 0.15em;
}}
.it11-stat-sep {{ color: var(--gold); font-size: 0.4rem; flex-shrink: 0; }}

/* ════ FAN GRID ═════════════════════════════════════════════════════ */
.it11-grid-section {{
    max-width: 1200px; margin: 3rem auto 0; padding: 0 1.5rem;
}}
.it11-fangrid {{
    display: grid; grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 260px; gap: 12px;
}}
.it11-gc {{
    position: relative; display: block;
    border: 1px solid var(--border); text-decoration: none;
    color: var(--text); overflow: hidden; background: var(--bg);
    transition: all 0.3s;
}}
.it11-gc::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--gold); z-index: 2; transform: scaleX(0);
    transform-origin: center; transition: transform 0.4s;
}}
.it11-gc:hover::before {{ transform: scaleX(1); }}
.it11-gc:hover {{ box-shadow: var(--shadow-lg); transform: translateY(-4px); }}
.it11-gc-std  {{ grid-row: span 1; }}
.it11-gc-wide {{ grid-column: span 2; }}
.it11-gc-tall {{ grid-row: span 2; }}
.it11-gc-imgwrap {{ position: absolute; inset: 0; }}
.it11-gc-img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.5s; }}
.it11-gc:hover .it11-gc-img {{ transform: scale(1.05); }}
.it11-gc-ph {{ width: 100%; height: 100%; background: linear-gradient(135deg, var(--surface2), var(--gold-light)); }}
.it11-gc-body {{
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 1rem; display: flex; flex-direction: column; gap: 4px;
    background: linear-gradient(to top, rgba(var(--primary-rgb),0.8) 0%, rgba(var(--primary-rgb),0.3) 60%, transparent 100%);
    min-height: 70px;
}}
.it11-gc-cat {{
    font-size: 0.6rem; font-weight: 600; color: var(--gold);
    text-transform: uppercase; letter-spacing: 0.12em;
}}
.it11-gc-title {{
    font-family: {ff}; font-weight: 700; font-size: 0.92rem; color: var(--text-on-primary);
    line-height: 1.3; margin: 0; text-shadow: 0 1px 4px rgba(var(--primary-rgb),0.5);
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}

.it11-viewall-wrap {{ text-align: center; margin-top: 2rem; }}
.it11-viewall {{
    color: var(--gold); text-decoration: none; font-weight: 600; font-size: 0.85rem;
    text-transform: uppercase; letter-spacing: 0.12em;
    padding-bottom: 3px; border-bottom: 1px solid var(--gold);
    transition: opacity 0.25s;
}}
.it11-viewall:hover {{ opacity: 0.7; }}

/* ════ HORIZONTAL SCROLL STRIP ═════════════════════════════════════ */
.it11-hs-section {{
    max-width: 1200px; margin: 3rem auto 0; padding: 0 1.5rem 4rem;
}}
.it11-hs {{
    display: flex; gap: 1rem; overflow-x: auto; padding-bottom: 0.75rem;
    scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}}
.it11-hs::-webkit-scrollbar {{ height: 4px; }}
.it11-hs::-webkit-scrollbar-track {{ background: transparent; }}
.it11-hs::-webkit-scrollbar-thumb {{ background: var(--border); }}
.it11-hs-card {{
    flex-shrink: 0; width: 200px; overflow: hidden;
    border: 1px solid var(--border); text-decoration: none; color: var(--text);
    background: var(--bg); transition: all 0.25s;
}}
.it11-hs-card:hover {{ border-color: var(--menu-link-hover); transform: translateY(-3px); box-shadow: var(--shadow); }}
.it11-hs-thumb {{ width: 100%; aspect-ratio: 4/3; overflow: hidden; }}
.it11-hs-img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.4s; }}
.it11-hs-card:hover .it11-hs-img {{ transform: scale(1.06); }}
.it11-hs-ph {{ width: 100%; height: 100%; background: linear-gradient(135deg, var(--surface2), var(--gold-light)); }}
.it11-hs-title {{ font-size: 0.82rem; font-weight: 600; padding: 0.6rem 0.75rem 0.75rem; line-height: 1.35; display: block; }}

/* ════ UTILITIES ════════════════════════════════════════════════════ */
.it11-empty {{ color: var(--muted); font-style: italic; font-size: 0.9rem; padding: 1rem 0; }}

/* ════ RESPONSIVE ═══════════════════════════════════════════════════ */
@media (max-width: 1100px) {{
    .it11-spotlight-inner {{ grid-template-columns: 1fr; }}
    .it11-statsbar {{ max-width: 100%; margin: 3rem 1.5rem 0; flex-wrap: wrap; }}
}}
@media (max-width: 900px) {{
    .it11-fangrid {{ grid-template-columns: repeat(2, 1fr); }}
    .it11-gc-wide {{ grid-column: span 2; }}
    .it11-gc-tall {{ grid-row: span 1; }}
}}
@media (max-width: 600px) {{
    .it11-fangrid {{ grid-template-columns: 1fr; grid-auto-rows: 240px; }}
    .it11-gc-wide {{ grid-column: span 1; }}
    .it11-hero-h1 {{ font-size: 1.8rem; }}
    .it11-hero-frame {{ padding: 2rem 1.5rem; }}
    .it11-statsbar {{ flex-direction: column; }}
    .it11-stat {{ border-bottom: 1px solid var(--gold-light); }}
    .it11-stat:last-child {{ border-bottom: none; }}
    .it11-stat-sep {{ display: none; }}
}}
"""
    return {"html": html_content, "css": css}
