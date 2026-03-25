"""Theme 12 — Index: Candy Pop.
Completely unique layout — NO render_cards, all custom inline rendering.
- Playful hero with floating blob shapes + bouncy gradient title
- Rainbow bouncing category pills
- Split featured card with colorful border glow
- Fun 3-col grid with alternating pastel card backgrounds
- Emoji stats counter strip
- "Sweet Picks" horizontal scroll with candy-colored cards
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

    COLORS = ["var(--primary)", "var(--secondary)", "var(--accent)", "var(--lavender)", "var(--yellow)"]
    BG_COLORS = ["var(--pink-pale)", "var(--blue-pale)", "rgba(167,243,208,0.12)", "rgba(196,181,253,0.12)", "rgba(253,232,138,0.15)"]

    # ── 1. BOUNCY HERO ───────────────────────────────────────────────────
    # No complex image hero — just playful text with blob decorations

    # ── 2. CATEGORY PILLS ────────────────────────────────────────────────
    cat_pills = ""
    for i, cat in enumerate(categories[:10]):
        cn = e(cat.get("name") or "")
        cu = e(cat.get("url") or "#")
        color = COLORS[i % len(COLORS)]
        if cn:
            cat_pills += f'<a href="{cu}" class="it12-cat-pill" style="--pill-color:{color}">{cn}</a>'
    if not cat_pills:
        cat_pills = '<span class="it12-cat-pill" style="--pill-color:var(--primary)">All Recipes</span>'

    # ── 3. FEATURED ARTICLE ──────────────────────────────────────────────
    feat = articles[0] if articles else None
    side_cards = articles[1:4] if len(articles) > 1 else []

    if feat:
        f_img = (feat.get("main_image") or feat.get("image") or "").strip()
        f_title = e((feat.get("title") or "")[:120])
        f_url = e(feat.get("url") or "#")
        f_exc = e((feat.get("excerpt") or "")[:200])
        feat_img = f'<img src="{e(f_img)}" alt="{f_title}" class="it12-feat-img">' if f_img and f_img.startswith("http") else '<div class="it12-feat-ph"></div>'
        feat_html = f"""
<div class="it12-feat-card">
  <div class="it12-feat-img-wrap"><a href="{f_url}">{feat_img}</a></div>
  <div class="it12-feat-text">
    <span class="it12-feat-badge">&#11088; Editor&rsquo;s Pick</span>
    <h2 class="it12-feat-title"><a href="{f_url}">{f_title}</a></h2>
    <p class="it12-feat-exc">{f_exc}</p>
    <a href="{f_url}" class="it12-feat-cta">Read Recipe &#10024;</a>
  </div>
</div>"""
    else:
        feat_html = ""

    side_html = ""
    for i, art in enumerate(side_cards):
        a_img = (art.get("main_image") or art.get("image") or "").strip()
        a_title = e((art.get("title") or "")[:60])
        a_url = e(art.get("url") or "#")
        color = COLORS[(i+1) % len(COLORS)]
        thmb = f'<img src="{e(a_img)}" alt="{a_title}" class="it12-sc-img">' if a_img and a_img.startswith("http") else f'<div class="it12-sc-num" style="background:{color}">{i+2}</div>'
        side_html += f"""
<a href="{a_url}" class="it12-sc-item">
  <div class="it12-sc-thumb">{thmb}</div>
  <span class="it12-sc-title">{a_title}</span>
</a>"""

    # ── 4. EMOJI STATS ───────────────────────────────────────────────────
    stats = [
        ("&#127859;", str(len(articles)) + "+", "Recipes"),
        ("&#128218;", str(len(categories)), "Categories"),
        ("&#128147;", "100%", "Made with Love"),
    ]
    stats_html = "".join(f"""
<div class="it12-stat">
  <span class="it12-stat-emoji">{emoji}</span>
  <span class="it12-stat-n">{v}</span>
  <span class="it12-stat-l">{lb}</span>
</div>""" for emoji, v, lb in stats)

    # ── 5. COLORFUL ARTICLE GRID ─────────────────────────────────────────
    grid_articles = articles[:9] if articles else []
    grid_cards = ""
    for i, art in enumerate(grid_articles):
        a_img = (art.get("main_image") or art.get("image") or "").strip()
        a_title = e((art.get("title") or "")[:80])
        a_url = e(art.get("url") or "#")
        a_cat = e(art.get("category") or "Recipe")
        bg_color = BG_COLORS[i % len(BG_COLORS)]
        accent = COLORS[i % len(COLORS)]
        has_img = a_img and a_img.startswith("http")
        img_block = f'<img src="{e(a_img)}" alt="{a_title}" class="it12-gc-img">' if has_img else f'<div class="it12-gc-ph" style="background:{bg_color}"><span class="it12-gc-ph-emoji">&#127860;</span></div>'
        grid_cards += f"""
<a href="{a_url}" class="it12-gc" style="--card-accent:{accent}">
  <div class="it12-gc-imgwrap">{img_block}</div>
  <div class="it12-gc-body">
    <span class="it12-gc-cat">{a_cat}</span>
    <h3 class="it12-gc-title">{a_title}</h3>
  </div>
</a>"""
    if not grid_cards:
        grid_cards = '<p class="it12-empty" style="grid-column:1/-1;">No recipes yet — add some and let the fun begin! &#127881;</p>'

    # ── 6. SWEET PICKS HORIZONTAL STRIP ──────────────────────────────────
    h_strip = ""
    for i, art in enumerate(articles[:6]):
        a_img = (art.get("main_image") or art.get("image") or "").strip()
        a_title = e((art.get("title") or "")[:60])
        a_url = e(art.get("url") or "#")
        color = COLORS[i % len(COLORS)]
        thmb = f'<img src="{e(a_img)}" alt="{a_title}" class="it12-hs-img">' if a_img and a_img.startswith("http") else f'<div class="it12-hs-ph" style="background:{color}20">&#127849;</div>'
        h_strip += f"""
<a href="{a_url}" class="it12-hs-card" style="--card-accent:{color}">
  <div class="it12-hs-thumb">{thmb}</div>
  <span class="it12-hs-title">{a_title}</span>
</a>"""

    html_content = f"""
<main class="index-page it12-index">

  <!-- ░░ BOUNCY HERO ░░ -->
  <section class="it12-hero-section">
    <div class="it12-blob1"></div>
    <div class="it12-blob2"></div>
    <div class="it12-blob3"></div>
    <div class="it12-hero-inner">
      <span class="it12-hero-badge">&#127849; Welcome to</span>
      <h1 class="it12-hero-h1">{domain_name} <em>Recipes</em></h1>
      <p class="it12-hero-desc">Delicious, colorful, and oh-so-fun recipes for everyone!</p>
    </div>
  </section>

  <!-- ░░ CATEGORY PILLS ░░ -->
  <div class="it12-catstrip-wrap">
    <div class="it12-catstrip">{cat_pills}</div>
  </div>

  <!-- ░░ FEATURED + SIDE ░░ -->
  <section class="it12-feat-section">
    <h2 class="it12-sec-title">&#11088; Today&rsquo;s Special</h2>
    <div class="it12-feat-inner">
      <div class="it12-feat-left">{feat_html or '<p class="it12-empty">Add recipes to see featured content! &#127881;</p>'}</div>
      <div class="it12-feat-right">
        <h3 class="it12-sc-heading">Also Yummy &#128523;</h3>
        <div class="it12-sc-list">{side_html or '<p class="it12-empty">More coming soon!</p>'}</div>
      </div>
    </div>
  </section>

  <!-- ░░ EMOJI STATS ░░ -->
  <div class="it12-statsbar">{stats_html}</div>

  <!-- ░░ COLORFUL GRID ░░ -->
  <section class="it12-grid-section">
    <div class="it12-grid-head">
      <h2 class="it12-sec-title">&#127860; Latest Recipes</h2>
      <a href="{e(base_url)}/recipes" class="it12-viewall">See all &#10024;</a>
    </div>
    <div class="it12-grid">{grid_cards}</div>
  </section>

  <!-- ░░ SWEET PICKS STRIP ░░ -->
  {f'''
  <section class="it12-hs-section">
    <h2 class="it12-sec-title">&#127849; Sweet Picks</h2>
    <div class="it12-hs">{h_strip}</div>
  </section>''' if h_strip else ""}

  <div class="index-pagination-slot"></div>
</main>
"""

    css = f"""
{t['font_import']}
.it12-index {{ {t['css_vars']} min-height: 100vh; }}

/* ════ BOUNCY HERO ════════════════════════════════════════════════════ */
.it12-hero-section {{
    background: linear-gradient(145deg, var(--surface2) 0%, var(--blue-pale) 50%, var(--surface) 100%);
    text-align: center; padding: 5rem 1.5rem 4rem;
    position: relative; overflow: hidden;
    border-bottom: 4px solid transparent;
    border-image: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent), var(--lavender), var(--primary)) 1;
}}
.it12-blob1, .it12-blob2, .it12-blob3 {{
    position: absolute; pointer-events: none; opacity: 0.12;
    animation: t12-blob-morph 8s ease-in-out infinite;
}}
@keyframes t12-blob-morph {{
  0%,100% {{ border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }}
  50% {{ border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }}
}}
.it12-blob1 {{ width: 350px; height: 350px; top: -100px; right: -80px; background: var(--primary); }}
.it12-blob2 {{ width: 250px; height: 250px; bottom: -60px; left: -50px; background: var(--secondary); animation-delay: -3s; }}
.it12-blob3 {{ width: 180px; height: 180px; top: 40px; left: 15%; background: var(--accent); animation-delay: -6s; }}
.it12-hero-inner {{ position: relative; z-index: 1; max-width: 700px; margin: 0 auto; }}
.it12-hero-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--pink-pale); border: 2px solid var(--pink-border);
    color: var(--primary); padding: 8px 20px; border-radius: 50px;
    font-size: 0.82rem; font-weight: 800; margin-bottom: 1.25rem;
    animation: t12-float 3s ease-in-out infinite;
}}
@keyframes t12-float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}
.it12-hero-h1 {{
    font-family: {ff}; font-size: clamp(2.2rem, 5.5vw, 3.8rem);
    font-weight: 900; color: var(--text); margin: 0 0 0.75rem;
    line-height: 1.12; animation: t12-bounce-in 0.7s ease both;
}}
@keyframes t12-bounce-in {{
  0% {{ opacity: 0; transform: translateY(30px) scale(0.95); }}
  60% {{ transform: translateY(-5px) scale(1.02); }}
  100% {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
.it12-hero-h1 em {{
    font-style: normal;
    background: linear-gradient(135deg, var(--primary), var(--secondary), var(--lavender));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.it12-hero-desc {{ color: var(--muted); font-size: 1.1rem; font-weight: 500; max-width: 500px; margin: 0 auto; }}

/* ════ CATEGORY PILLS ═════════════════════════════════════════════════ */
.it12-catstrip-wrap {{
    background: var(--bg); border-bottom: 1px solid var(--border);
    position: sticky; top: 72px; z-index: 40;
}}
.it12-catstrip {{
    max-width: 1300px; margin: 0 auto; padding: 0.75rem 1.5rem;
    display: flex; align-items: center; gap: 0.5rem;
    overflow-x: auto; scrollbar-width: none; justify-content: center; flex-wrap: wrap;
}}
.it12-catstrip::-webkit-scrollbar {{ display: none; }}
.it12-cat-pill {{
    display: inline-block; padding: 0.4rem 1rem; border-radius: 50px;
    border: 2px solid var(--pill-color); color: var(--pill-color);
    text-decoration: none; font-size: 0.82rem; font-weight: 700;
    transition: all 0.3s; white-space: nowrap; background: transparent;
}}
.it12-cat-pill:hover {{
    background: var(--pill-color); color: #fff;
    transform: translateY(-3px) scale(1.06);
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}}

/* ════ SECTION TITLE ═══════════════════════════════════════════════ */
.it12-sec-title {{
    font-family: {ff}; font-size: 1.7rem; font-weight: 900;
    color: var(--text); margin: 0 0 1.5rem;
}}

/* ════ FEATURED SECTION ═══════════════════════════════════════════ */
.it12-feat-section {{ max-width: 1300px; margin: 3rem auto 0; padding: 0 1.5rem; }}
.it12-feat-inner {{ display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.5rem; align-items: start; }}
.it12-feat-card {{
    border: 2px solid var(--border); border-radius: var(--radius-lg); overflow: hidden;
    background: var(--bg); box-shadow: var(--shadow-sm); transition: all 0.35s;
}}
.it12-feat-card:hover {{ box-shadow: 0 12px 40px rgba(255,133,161,0.2); transform: translateY(-4px); }}
.it12-feat-img-wrap {{ display: block; aspect-ratio: 16/9; overflow: hidden; }}
.it12-feat-img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; display: block; }}
.it12-feat-card:hover .it12-feat-img {{ transform: scale(1.05); }}
.it12-feat-ph {{ width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, var(--surface2), var(--pink-pale)); display: flex; align-items: center; justify-content: center; font-size: 3rem; }}
.it12-feat-text {{ padding: 1.5rem; }}
.it12-feat-badge {{
    display: inline-block; background: var(--pink-pale); border: 2px solid var(--pink-border);
    color: var(--primary); padding: 4px 14px; border-radius: 50px;
    font-size: 0.75rem; font-weight: 800; margin-bottom: 0.5rem;
}}
.it12-feat-title {{ font-family: {ff}; font-size: 1.4rem; font-weight: 800; margin: 0 0 0.6rem; line-height: 1.25; }}
.it12-feat-title a {{ text-decoration: none; color: var(--text); transition: color 0.2s; }}
.it12-feat-title a:hover {{ color: var(--primary); }}
.it12-feat-exc {{ color: var(--muted); font-size: 0.9rem; line-height: 1.7; font-weight: 500; margin-bottom: 1rem; }}
.it12-feat-cta {{
    display: inline-flex; align-items: center; gap: 4px;
    background: var(--primary); color: #fff; padding: 0.6rem 1.3rem;
    border-radius: 50px; text-decoration: none; font-weight: 800; font-size: 0.85rem;
    transition: all 0.3s; box-shadow: 0 4px 16px rgba(255,133,161,0.3);
}}
.it12-feat-cta:hover {{ transform: translateY(-3px) scale(1.05); box-shadow: 0 8px 24px rgba(255,133,161,0.45); }}

/* Side cards */
.it12-sc-heading {{ font-family: {ff}; font-size: 1rem; font-weight: 800; margin: 0 0 1rem; }}
.it12-sc-list {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.it12-sc-item {{
    display: flex; gap: 0.9rem; align-items: center; text-decoration: none;
    color: var(--text); padding: 0.75rem; border-radius: 16px;
    border: 2px solid var(--border); transition: all 0.3s; background: var(--bg);
}}
.it12-sc-item:hover {{ border-color: var(--primary); transform: translateX(4px); }}
.it12-sc-thumb {{ width: 50px; height: 50px; border-radius: 12px; overflow: hidden; flex-shrink: 0; }}
.it12-sc-img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.it12-sc-num {{
    width: 50px; height: 50px; border-radius: 12px; color: #fff;
    font-family: {ff}; font-size: 1.2rem; font-weight: 900;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.it12-sc-title {{ font-size: 0.88rem; font-weight: 700; line-height: 1.35; }}

/* ════ EMOJI STATS ════════════════════════════════════════════════════ */
.it12-statsbar {{
    max-width: 900px; margin: 3rem auto 0; padding: 0 1.5rem;
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
}}
.it12-stat {{
    text-align: center; padding: 1.5rem; border: 2px solid var(--border);
    border-radius: var(--radius); background: var(--bg);
    display: flex; flex-direction: column; align-items: center; gap: 4px;
    transition: all 0.3s;
}}
.it12-stat:hover {{ transform: translateY(-4px); box-shadow: var(--shadow); }}
.it12-stat-emoji {{ font-size: 2rem; margin-bottom: 0.25rem; }}
.it12-stat-n {{
    font-family: {ff}; font-size: 2rem; font-weight: 900;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.it12-stat-l {{ font-size: 0.78rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }}

/* ════ COLORFUL GRID ═════════════════════════════════════════════════ */
.it12-grid-section {{ max-width: 1300px; margin: 3rem auto 0; padding: 0 1.5rem; }}
.it12-grid-head {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }}
.it12-viewall {{
    color: var(--primary); text-decoration: none; font-weight: 800; font-size: 0.88rem;
    transition: all 0.25s;
}}
.it12-viewall:hover {{ transform: translateX(4px); }}
.it12-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
}}
.it12-gc {{
    display: block; border: 2px solid var(--border); border-radius: var(--radius);
    text-decoration: none; color: var(--text); overflow: hidden;
    background: var(--bg); transition: all 0.35s;
}}
.it12-gc:hover {{
    border-color: var(--card-accent); transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 36px rgba(0,0,0,0.10);
}}
.it12-gc-imgwrap {{ aspect-ratio: 4/3; overflow: hidden; }}
.it12-gc-img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.45s; }}
.it12-gc:hover .it12-gc-img {{ transform: scale(1.08); }}
.it12-gc-ph {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }}
.it12-gc-ph-emoji {{ font-size: 2.5rem; opacity: 0.3; }}
.it12-gc-body {{ padding: 1rem 1.2rem 1.2rem; }}
.it12-gc-cat {{
    display: inline-block; font-size: 0.68rem; font-weight: 700;
    color: var(--card-accent); text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}}
.it12-gc-title {{
    font-family: {ff}; font-weight: 800; font-size: 1rem; color: var(--text);
    line-height: 1.3; margin: 0;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}

/* ════ HORIZONTAL SCROLL STRIP ═════════════════════════════════════ */
.it12-hs-section {{ max-width: 1300px; margin: 3rem auto 0; padding: 0 1.5rem 4rem; }}
.it12-hs {{
    display: flex; gap: 1rem; overflow-x: auto; padding-bottom: 0.75rem;
    scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}}
.it12-hs::-webkit-scrollbar {{ height: 4px; }}
.it12-hs::-webkit-scrollbar-track {{ background: transparent; }}
.it12-hs::-webkit-scrollbar-thumb {{ background: var(--primary); border-radius: 50px; }}
.it12-hs-card {{
    flex-shrink: 0; width: 210px; border-radius: var(--radius); overflow: hidden;
    border: 2px solid var(--border); text-decoration: none; color: var(--text);
    background: var(--bg); transition: all 0.3s;
}}
.it12-hs-card:hover {{ border-color: var(--card-accent); transform: translateY(-4px) scale(1.03); box-shadow: var(--shadow); }}
.it12-hs-thumb {{ width: 100%; aspect-ratio: 4/3; overflow: hidden; }}
.it12-hs-img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.4s; }}
.it12-hs-card:hover .it12-hs-img {{ transform: scale(1.08); }}
.it12-hs-ph {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2rem; opacity: 0.3; }}
.it12-hs-title {{ font-size: 0.85rem; font-weight: 700; padding: 0.7rem 0.9rem 0.85rem; line-height: 1.35; display: block; }}

/* ════ UTILITIES ════════════════════════════════════════════════════ */
.it12-empty {{ color: var(--muted); font-style: italic; font-size: 0.95rem; font-weight: 500; padding: 1rem 0; }}

/* ════ RESPONSIVE ═══════════════════════════════════════════════════ */
@media (max-width: 1100px) {{
    .it12-feat-inner {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 900px) {{
    .it12-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 600px) {{
    .it12-grid {{ grid-template-columns: 1fr; }}
    .it12-hero-h1 {{ font-size: 1.85rem; }}
    .it12-statsbar {{ grid-template-columns: 1fr; }}
}}
"""
    return {"html": html_content, "css": css}
