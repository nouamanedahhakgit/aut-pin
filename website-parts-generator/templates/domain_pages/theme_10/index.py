"""Theme 10 — Index: Bento Fresh.
Completely unique layout — NO render_cards, all custom inline rendering.
- Full-screen bento hero mosaic (no text/image split)
- Category scroll pill strip
- Magazine-style featured article (big image + numbered side list)
- Masonry mixed-size article grid (not uniform)
- Stats counter bar
- Horizontal newest strip
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    s = t["s"]
    ff = t["font_family"]
    bf = t["body_font"]

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    articles  = config.get("articles", []) or []
    categories = config.get("categories", []) or []
    domain_name = html_module.escape(config.get("domain_name", s.get("domain_name", "Recipe Blog")))

    def e(v): return html_module.escape(str(v)) if v else ""
    def img_or_ph(img_url, alt="", cls="", ph_class=""):
        if img_url and str(img_url).startswith("http"):
            return f'<img src="{e(img_url)}" alt="{e(alt)}" class="{cls}" loading="lazy">'
        return f'<div class="{ph_class or "it10-ph"}"></div>'

    # ── 1. BENTO HERO MOSAIC ──────────────────────────────────────────────
    bento_items = articles[:5] if articles else []
    bento_cards = ""
    for i, art in enumerate(bento_items):
        fi = (art.get("main_image") or art.get("image") or "").strip()
        ft = e((art.get("title") or "")[:75])
        fu = e(art.get("url") or "#")
        cat = e((art.get("category") or "Recipe"))
        # Use single quotes inside url() to avoid breaking the outer style="..." attribute
        bg = f"background-image:url('{e(fi)}'); background-size:cover; background-position:center;" if fi and fi.startswith("http") else ""
        size_cls = {0: "it10-b-main", 1: "it10-b-tall", 2: "it10-b-wide", 3: "it10-b-sm", 4: "it10-b-sm"}.get(i, "it10-b-sm")
        bento_cards += f"""
<a href="{fu}" class="it10-bento-card {size_cls}" style="{bg}">
  <div class="it10-b-gloss"></div>
  <div class="it10-b-info">
    <span class="it10-b-tag">{cat}</span>
    <span class="it10-b-title">{ft or domain_name}</span>
  </div>
</a>"""
    if not bento_cards:
        bento_cards = f'<div class="it10-bento-card it10-b-main"><div class="it10-b-info"><span class="it10-b-tag">Welcome</span><span class="it10-b-title">{domain_name}</span></div></div>'

    # ── 2. CATEGORY PILLS SCROLL STRIP ───────────────────────────────────
    cat_pills = ""
    for cat in categories[:10]:
        cn = e(cat.get("name") or "")
        cu = e(cat.get("url") or "#")
        if cn:
            cat_pills += f'<a href="{cu}" class="it10-cat-pill">{cn}</a>'
    if not cat_pills:
        cat_pills = '<span class="it10-cat-pill it10-pill-empty">All Recipes</span>'

    # ── 3. FEATURED ARTICLE (big card) + NUMBERED SIDE LIST ─────────────
    feat = articles[0] if articles else None
    side_list = articles[1:6] if len(articles) > 1 else []

    if feat:
        f_img = (feat.get("main_image") or feat.get("image") or "").strip()
        f_title = e((feat.get("title") or "")[:120])
        f_url = e(feat.get("url") or "#")
        f_exc = e((feat.get("excerpt") or "")[:200])
        feat_img_tag = f'<img src="{e(f_img)}" alt="{f_title}" class="it10-feat-img">' if f_img and f_img.startswith("http") else '<div class="it10-feat-ph"></div>'
        feat_html = f"""
<div class="it10-feat-card">
  <a href="{f_url}" class="it10-feat-img-wrap">{feat_img_tag}</a>
  <div class="it10-feat-text">
    <div class="it10-feat-eyebrow">
      <span class="it10-feat-dot"></span>Editor&rsquo;s Pick
    </div>
    <h2 class="it10-feat-title"><a href="{f_url}">{f_title}</a></h2>
    <p class="it10-feat-exc">{f_exc}</p>
    <a href="{f_url}" class="it10-feat-cta">Read Recipe <span>&rarr;</span></a>
  </div>
</div>"""
    else:
        feat_html = ""

    side_items = ""
    for i, art in enumerate(side_list):
        a_img = (art.get("main_image") or art.get("image") or "").strip()
        a_title = e((art.get("title") or "")[:70])
        a_url = e(art.get("url") or "#")
        thmb = f'<img src="{e(a_img)}" alt="{a_title}" class="it10-sl-img">' if a_img and a_img.startswith("http") else f'<div class="it10-sl-num">{i+2:02d}</div>'
        side_items += f"""
<a href="{a_url}" class="it10-sl-item">
  <div class="it10-sl-thumb">{thmb}</div>
  <div class="it10-sl-body">
    <span class="it10-sl-num-label">#{i+2:02d}</span>
    <span class="it10-sl-title">{a_title}</span>
  </div>
</a>"""
    if not side_items:
        side_items = '<p class="it10-empty">More recipes coming soon</p>'

    # ── 4. STATS BAR ─────────────────────────────────────────────────────
    stats = [
        (str(len(articles)) + "+", "Recipes"),
        (str(len(categories)), "Categories"),
        ("100%", "Kitchen Tested"),
    ]
    stats_html = "".join(f"""
<div class="it10-stat">
  <span class="it10-stat-n" data-target="{v}">{v}</span>
  <span class="it10-stat-l">{lb}</span>
</div>""" for v, lb in stats)

    # ── 5. MASONRY ARTICLE GRID — uniquely alternating sizes ─────────────
    # Cards rendered entirely inline with unique theme-10 styling
    grid_articles = articles[:9] if articles else []
    SIZES = ["wide", "std", "std", "tall", "std", "wide", "std", "std", "tall"]
    grid_cards = ""
    for i, art in enumerate(grid_articles):
        a_img = (art.get("main_image") or art.get("image") or "").strip()
        a_title = e((art.get("title") or "")[:80])
        a_url = e(art.get("url") or "#")
        a_exc = e((art.get("excerpt") or "")[:110])
        sz = SIZES[i % len(SIZES)]
        has_img = a_img and a_img.startswith("http")
        img_block = f'<img src="{e(a_img)}" alt="{a_title}" class="it10-gc-img">' if has_img else '<div class="it10-gc-ph"></div>'
        grid_cards += f"""
<a href="{a_url}" class="it10-gc it10-gc-{sz}">
  <div class="it10-gc-imgwrap">{img_block}</div>
  <div class="it10-gc-body">
    <h3 class="it10-gc-title">{a_title}</h3>
    {"<p class='it10-gc-exc'>" + a_exc + "</p>" if sz in ("wide", "tall") and a_exc else ""}
    <span class="it10-gc-arrow">&rarr;</span>
  </div>
</a>"""
    if not grid_cards:
        grid_cards = '<p class="it10-empty" style="grid-column:1/-1;">No recipes yet — add some titles and generate articles!</p>'

    # ── 6. NEWEST HORIZONTAL STRIP ───────────────────────────────────────
    h_strip = ""
    for art in articles[:6]:
        a_img = (art.get("main_image") or art.get("image") or "").strip()
        a_title = e((art.get("title") or "")[:60])
        a_url = e(art.get("url") or "#")
        thmb = f'<img src="{e(a_img)}" alt="{a_title}" class="it10-hs-img">' if a_img and a_img.startswith("http") else '<div class="it10-hs-ph"></div>'
        h_strip += f"""
<a href="{a_url}" class="it10-hs-card">
  <div class="it10-hs-thumb">{thmb}</div>
  <span class="it10-hs-title">{a_title}</span>
</a>"""

    html_content = f"""
<main class="index-page it10-index">

  <!-- ░░ BENTO HERO ░░ -->
  <section class="it10-bento-section">
    <div class="it10-bento-head">
      <p class="it10-bento-sub">What&rsquo;s cooking today?</p>
      <h1 class="it10-bento-h1">{domain_name} <em>Recipes</em></h1>
    </div>
    <div class="it10-bento-grid">{bento_cards}</div>
  </section>

  <!-- ░░ CATEGORY SCROLL STRIP ░░ -->
  <div class="it10-catstrip-wrap">
    <div class="it10-catstrip">
      <span class="it10-catstrip-label">Browse:</span>
      {cat_pills}
    </div>
  </div>

  <!-- ░░ FEATURED + SIDE LIST ░░ -->
  <section class="it10-featured-section">
    <div class="it10-featured-inner">
      <div class="it10-featured-left">
        <div class="it10-sec-head">
          <span class="it10-sec-badge">&#9733; Featured</span>
          <h2 class="it10-sec-title">Editor&rsquo;s Choice</h2>
        </div>
        {feat_html or '<p class="it10-empty">Add recipes to see featured content.</p>'}
      </div>
      <div class="it10-featured-right">
        <div class="it10-sec-head">
          <span class="it10-sec-badge">&#128197; Also Trending</span>
          <h2 class="it10-sec-title">Worth Trying</h2>
        </div>
        <div class="it10-side-list">{side_items}</div>
      </div>
    </div>
  </section>

  <!-- ░░ STATS BAR ░░ -->
  <div class="it10-statsbar">
    {stats_html}
  </div>

  <!-- ░░ MASONRY GRID ░░ -->
  <section class="it10-grid-section">
    <div class="it10-grid-head">
      <div>
        <p class="it10-grid-sub">&#128197; New this week</p>
        <h2 class="it10-grid-title">Latest Recipes</h2>
      </div>
      <a href="{e(base_url)}/recipes" class="it10-grid-viewall">All recipes &rarr;</a>
    </div>
    <div class="it10-masonry">{grid_cards}</div>
  </section>

  <!-- ░░ NEWEST HORIZONTAL SCROLL ░░ -->
  {f'''
  <section class="it10-hs-section">
    <h2 class="it10-hs-title">&#127860; From the Kitchen</h2>
    <div class="it10-hs">{h_strip}</div>
  </section>''' if h_strip else ""}

  <div class="index-pagination-slot"></div>
</main>
"""

    css = f"""
{t['font_import']}
.it10-index {{ {t['css_vars']} min-height: 100vh; }}

/* ════ BENTO HERO ════════════════════════════════════════════════════ */
.it10-bento-section {{
    max-width: 1400px; margin: 0 auto;
    padding: 2.5rem 1.5rem 1.5rem;
}}
.it10-bento-head {{ text-align: center; margin-bottom: 1.5rem; }}
.it10-bento-sub {{
    font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.18em; color: var(--primary); margin-bottom: 0.35rem;
}}
.it10-bento-h1 {{
    font-family: {ff}; font-size: clamp(2rem, 4.5vw, 3.2rem);
    font-weight: 700; color: var(--text); margin: 0;
    line-height: 1.15; letter-spacing: -0.02em;
}}
.it10-bento-h1 em {{ font-style: italic; color: var(--primary); }}

/* Bento grid — 4 col / 2 rows */
.it10-bento-grid {{
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    grid-template-rows: 240px 200px;
    gap: 10px;
    border-radius: 20px; overflow: hidden;
}}
.it10-bento-card {{
    position: relative; display: block; text-decoration: none;
    border-radius: 14px; overflow: hidden;
    background: var(--surface2);
    transition: transform 0.4s cubic-bezier(.165,.84,.44,1), box-shadow 0.3s;
}}
.it10-bento-card:hover {{ transform: scale(1.025); box-shadow: 0 16px 48px rgba(0,0,0,0.14); }}
.it10-b-main  {{ grid-column: 1; grid-row: 1 / span 2; }}
.it10-b-tall  {{ grid-column: 2; grid-row: 1 / span 2; }}
.it10-b-wide  {{ grid-column: 3; grid-row: 1; }}
.it10-b-sm    {{ grid-column: 3; grid-row: 2; }}
.it10-b-gloss {{
    position: absolute; inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0.08) 55%, transparent 100%);
}}
.it10-b-info {{
    position: absolute; bottom: 0; left: 0; right: 0; padding: 1rem 1.1rem 1.1rem;
    display: flex; flex-direction: column; gap: 4px;
}}
.it10-b-tag {{
    display: inline-block; background: var(--primary); color: #fff;
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;
    padding: 2px 8px; border-radius: 50px; width: fit-content;
}}
.it10-b-title {{
    color: #fff; font-family: {ff}; font-weight: 700;
    font-size: clamp(0.85rem, 1.5vw, 1.15rem);
    line-height: 1.3; text-shadow: 0 1px 6px rgba(0,0,0,0.5);
}}

/* ════ CATEGORY STRIP ══════════════════════════════════════════════ */
.it10-catstrip-wrap {{
    position: sticky; top: 68px; z-index: 40;
    background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
    border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
}}
.it10-catstrip {{
    max-width: 1400px; margin: 0 auto; padding: 0.65rem 1.5rem;
    display: flex; align-items: center; gap: 0.5rem;
    overflow-x: auto; scrollbar-width: none;
}}
.it10-catstrip::-webkit-scrollbar {{ display: none; }}
.it10-catstrip-label {{
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; color: var(--muted); white-space: nowrap; flex-shrink: 0;
}}
.it10-cat-pill {{
    display: inline-block; padding: 0.3rem 0.9rem; border-radius: 50px; white-space: nowrap;
    border: 1.5px solid var(--border); color: var(--muted);
    text-decoration: none; font-size: 0.78rem; font-weight: 600; transition: all 0.2s; flex-shrink: 0;
    background: var(--bg);
}}
.it10-cat-pill:hover {{ border-color: var(--primary); color: var(--primary); background: var(--mint-pale); }}
.it10-pill-empty {{ background: var(--mint-pale); border-color: var(--mint-border); color: var(--primary); }}

/* ════ FEATURED + SIDE LIST ════════════════════════════════════════ */
.it10-featured-section {{
    max-width: 1400px; margin: 3rem auto 0; padding: 0 1.5rem;
}}
.it10-featured-inner {{
    display: grid; grid-template-columns: 1.6fr 1fr; gap: 2rem; align-items: start;
}}
.it10-sec-head {{ margin-bottom: 1.25rem; }}
.it10-sec-badge {{
    display: inline-block; background: var(--mint-pale); border: 1px solid var(--mint-border);
    color: var(--primary); padding: 4px 12px; border-radius: 50px;
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 0.4rem;
}}
.it10-sec-title {{
    font-family: {ff}; font-size: 1.6rem; font-weight: 700;
    color: var(--text); margin: 0; line-height: 1.2;
}}

/* Featured Big Card */
.it10-feat-card {{
    border: 1px solid var(--border); border-radius: 20px; overflow: hidden;
    background: var(--bg); box-shadow: var(--shadow-sm); transition: box-shadow 0.3s;
}}
.it10-feat-card:hover {{ box-shadow: var(--shadow-lg); }}
.it10-feat-img-wrap {{ display: block; aspect-ratio: 16/9; overflow: hidden; }}
.it10-feat-img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; display: block; }}
.it10-feat-card:hover .it10-feat-img {{ transform: scale(1.04); }}
.it10-feat-ph {{ width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, var(--surface2), var(--mint-pale)); }}
.it10-feat-text {{ padding: 1.5rem; }}
.it10-feat-eyebrow {{
    display: flex; align-items: center; gap: 6px;
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em;
    color: var(--primary); margin-bottom: 0.6rem;
}}
.it10-feat-dot {{
    width: 7px; height: 7px; border-radius: 50%; background: var(--primary);
    animation: t10-pulse-dot 2s infinite;
}}
@keyframes t10-pulse-dot {{
    0%,100% {{ transform: scale(1); opacity: 1; }}
    50% {{ transform: scale(1.4); opacity: 0.6; }}
}}
.it10-feat-title {{ font-family: {ff}; font-size: 1.4rem; font-weight: 700; margin: 0 0 0.75rem; line-height: 1.25; }}
.it10-feat-title a {{ text-decoration: none; color: var(--text); transition: color 0.2s; }}
.it10-feat-title a:hover {{ color: var(--primary); }}
.it10-feat-exc {{ color: var(--muted); font-size: 0.9rem; line-height: 1.7; margin-bottom: 1rem; }}
.it10-feat-cta {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--primary); color: #fff; padding: 0.55rem 1.25rem;
    border-radius: 50px; text-decoration: none; font-weight: 700; font-size: 0.85rem; transition: all 0.2s;
}}
.it10-feat-cta:hover {{ background: #00997F; transform: translateY(-2px); box-shadow: 0 5px 18px rgba(0,191,165,0.35); }}

/* Side numbered list */
.it10-side-list {{ display: flex; flex-direction: column; gap: 0; }}
.it10-sl-item {{
    display: flex; gap: 0.9rem; align-items: center; text-decoration: none; color: var(--text);
    padding: 0.85rem 0.5rem; border-bottom: 1px solid var(--border); transition: background 0.2s;
    border-radius: 10px;
}}
.it10-sl-item:last-child {{ border-bottom: none; }}
.it10-sl-item:hover {{ background: var(--mint-pale); padding-left: 0.75rem; }}
.it10-sl-thumb {{ width: 56px; height: 56px; border-radius: 10px; overflow: hidden; flex-shrink: 0; }}
.it10-sl-img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.it10-sl-num {{
    width: 40px; height: 40px; border-radius: 10px; background: var(--mint-pale);
    color: var(--primary); font-family: {ff}; font-size: 0.95rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.it10-sl-body {{ flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }}
.it10-sl-num-label {{
    font-size: 0.68rem; font-weight: 700; color: var(--primary);
    text-transform: uppercase; letter-spacing: 0.1em;
}}
.it10-sl-title {{ font-size: 0.88rem; font-weight: 600; color: var(--text); line-height: 1.35; }}
.it10-sl-item:hover .it10-sl-title {{ color: var(--primary); }}

/* ════ STATS BAR ════════════════════════════════════════════════════ */
.it10-statsbar {{
    max-width: 900px; margin: 3rem auto 0; padding: 0 1.5rem;
    display: grid; grid-template-columns: repeat(3, 1fr);
    border: 1px solid var(--border); border-radius: 20px;
    background: linear-gradient(135deg, var(--surface2), var(--mint-pale));
    overflow: hidden;
}}
.it10-stat {{
    text-align: center; padding: 1.75rem 1rem;
    border-right: 1px solid var(--border);
    display: flex; flex-direction: column; align-items: center; gap: 4px;
}}
.it10-stat:last-child {{ border-right: none; }}
.it10-stat-n {{
    display: block; font-family: {ff}; font-size: 2.5rem; font-weight: 700;
    color: var(--primary); line-height: 1; letter-spacing: -0.02em;
}}
.it10-stat-l {{ font-size: 0.8rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }}

/* ════ MASONRY GRID ════════════════════════════════════════════════ */
.it10-grid-section {{
    max-width: 1400px; margin: 3rem auto 0; padding: 0 1.5rem;
}}
.it10-grid-head {{
    display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 1.5rem;
}}
.it10-grid-sub {{ font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; color: var(--primary); margin-bottom: 0.25rem; }}
.it10-grid-title {{ font-family: {ff}; font-size: 1.8rem; font-weight: 700; color: var(--text); margin: 0; }}
.it10-grid-viewall {{
    color: var(--primary); text-decoration: none; font-weight: 700; font-size: 0.88rem;
    display: flex; align-items: center; gap: 4px; white-space: nowrap;
    padding-bottom: 4px; border-bottom: 1.5px solid var(--primary); transition: opacity 0.2s;
}}
.it10-grid-viewall:hover {{ opacity: 0.7; }}

/* Masonry: uses CSS grid with varying row spans — tall rows for big images */
.it10-masonry {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 280px;
    gap: 14px;
}}
.it10-gc {{
    position: relative; display: block;
    border: 1px solid var(--border); border-radius: var(--radius);
    text-decoration: none; color: var(--text); overflow: hidden;
    background: var(--bg); transition: all 0.3s;
}}
.it10-gc:hover {{ box-shadow: var(--shadow-lg); transform: translateY(-4px); border-color: var(--mint-border); }}
.it10-gc-std  {{ grid-row: span 1; }}
.it10-gc-wide {{ grid-column: span 2; }}
.it10-gc-tall {{ grid-row: span 2; }}
/* Image fills entire card */
.it10-gc-imgwrap {{ position: absolute; inset: 0; }}
.it10-gc-img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.45s; }}
.it10-gc:hover .it10-gc-img {{ transform: scale(1.06); }}
.it10-gc-ph {{ width: 100%; height: 100%; background: linear-gradient(135deg, var(--surface2), var(--mint-pale)); }}
/* Body overlays bottom of image */
.it10-gc-body {{
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 0.85rem 1rem; display: flex; align-items: center; gap: 0.5rem;
    background: linear-gradient(to top, rgba(0,0,0,0.72) 0%, rgba(0,0,0,0.35) 60%, transparent 100%);
    min-height: 70px;
}}
.it10-gc-title {{
    font-weight: 600; font-size: 0.92rem; color: #fff;
    line-height: 1.35; flex: 1; margin: 0;
    text-shadow: 0 1px 4px rgba(0,0,0,0.5);
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.it10-gc-exc {{
    font-size: 0.78rem; color: rgba(255,255,255,0.8); line-height: 1.5;
    margin-top: 0.2rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
    text-shadow: 0 1px 3px rgba(0,0,0,0.4);
}}
.it10-gc-arrow {{
    color: #fff; font-weight: 700; font-size: 1rem; flex-shrink: 0; opacity: 0;
    transition: opacity 0.2s, transform 0.2s;
}}
.it10-gc:hover .it10-gc-arrow {{ opacity: 1; transform: translateX(3px); }}

/* ════ HORIZONTAL SCROLL STRIP ═════════════════════════════════════ */
.it10-hs-section {{
    max-width: 1400px; margin: 3rem auto 0; padding: 0 1.5rem 4rem;
}}
.it10-hs-title {{
    font-family: {ff}; font-size: 1.35rem; font-weight: 700; color: var(--text);
    margin-bottom: 1rem;
}}
.it10-hs {{
    display: flex; gap: 1rem; overflow-x: auto; padding-bottom: 0.75rem;
    scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}}
.it10-hs::-webkit-scrollbar {{ height: 4px; }}
.it10-hs::-webkit-scrollbar-track {{ background: transparent; }}
.it10-hs::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 50px; }}
.it10-hs-card {{
    flex-shrink: 0; width: 200px; border-radius: var(--radius); overflow: hidden;
    border: 1px solid var(--border); text-decoration: none; color: var(--text);
    background: var(--bg); transition: all 0.25s;
}}
.it10-hs-card:hover {{ border-color: var(--primary); transform: translateY(-3px); box-shadow: var(--shadow); }}
.it10-hs-thumb {{ width: 100%; aspect-ratio: 4/3; overflow: hidden; }}
.it10-hs-img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.4s; }}
.it10-hs-card:hover .it10-hs-img {{ transform: scale(1.07); }}
.it10-hs-ph {{ width: 100%; height: 100%; background: linear-gradient(135deg, var(--surface2), var(--mint-pale)); }}
.it10-hs-title {{ font-size: 0.82rem; font-weight: 600; padding: 0.6rem 0.75rem 0.75rem; line-height: 1.35; }}

/* ════ UTILITIES ════════════════════════════════════════════════════ */
.it10-ph {{ background: linear-gradient(135deg, var(--surface2), var(--mint-pale)); width: 100%; height: 100%; }}
.it10-empty {{ color: var(--muted); font-style: italic; font-size: 0.9rem; padding: 1rem 0; }}

/* ════ RESPONSIVE ═══════════════════════════════════════════════════ */
@media (max-width: 1100px) {{
    .it10-bento-grid {{ grid-template-columns: 1.5fr 1fr; grid-template-rows: 220px 200px; }}
    .it10-b-wide, .it10-b-sm {{ grid-column: 2; }}
    .it10-featured-inner {{ grid-template-columns: 1fr; }}
    .it10-statsbar {{ max-width: 100%; margin: 3rem 1.5rem 0; }}
}}
@media (max-width: 900px) {{
    .it10-masonry {{ grid-template-columns: repeat(2, 1fr); }}
    .it10-gc-wide {{ grid-column: span 2; }}
    .it10-gc-tall {{ grid-row: span 1; }}
    .it10-bento-grid {{ grid-template-columns: 1fr 1fr; grid-template-rows: 200px 160px; }}
    .it10-b-tall {{ grid-row: span 1; }}
}}
@media (max-width: 600px) {{
    .it10-bento-grid {{ grid-template-columns: 1fr; grid-template-rows: 200px 140px 140px; }}
    .it10-b-main {{ grid-column: 1; grid-row: 1; }}
    .it10-b-tall, .it10-b-wide, .it10-b-sm {{ grid-column: 1; grid-row: auto; }}
    .it10-masonry {{ grid-template-columns: 1fr; grid-auto-rows: 260px; }}
    .it10-gc-wide {{ grid-column: span 1; }}
    .it10-statsbar {{ grid-template-columns: 1fr; border-radius: 16px; }}
    .it10-stat {{ border-right: none; border-bottom: 1px solid var(--border); }}
    .it10-stat:last-child {{ border-bottom: none; }}
    .it10-bento-h1 {{ font-size: 1.7rem; }}
}}
"""
    return {"html": html_content, "css": css}
