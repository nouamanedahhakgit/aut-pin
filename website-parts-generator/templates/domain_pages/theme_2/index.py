"""Theme 2 — Index: Modern clean style. Full-width hero banner, horizontal category tabs, category spotlight rows, latest recipes grid."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module
from shared_article_card import render_cards


def generate(config: dict) -> dict:
    t = theme_base(config)
    s = t["s"]
    ff = t["font_family"]

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    articles = config.get("articles", [])
    categories = config.get("categories", [])
    domain_name = html_module.escape(config.get("domain_name", s.get("domain_name", "Recipe Blog")))

    def e(v): return html_module.escape(str(v)) if v else ""

    feat = articles[0] if articles else None
    if feat:
        ft = e((feat.get("title") or "Recipe")[:120])
        fu = e(feat.get("url") or "#")
        fx = e((feat.get("excerpt") or "")[:200])
        fi = (feat.get("main_image") or feat.get("image") or "").strip()
    else:
        ft, fu = f"Welcome to {domain_name}", "#"
        fx = "Discover delicious recipes for every occasion."
        fi = ""
    hero_bg = f'background-image:url({e(fi)});background-size:cover;background-position:center;' if fi and fi.startswith("http") else f'background:color-mix(in srgb, var(--primary) 10%, var(--bg));'

    # --- Category tabs ---
    cat_tabs = ""
    for cat in categories[:6]:
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url") or "#")
        if c_name:
            cat_tabs += f'<a href="{c_url}" class="it2-tab">{c_name}</a>'

    # --- Category spotlight: horizontal row per category ---
    spotlights_html = ""
    for ci, cat in enumerate(categories[:2]):
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url") or "#")
        cat_arts = articles[ci*4+1 : ci*4+5] if len(articles) > ci*4+1 else articles[:4]
        cards = ""
        for a in cat_arts:
            a_img = (a.get("main_image") or a.get("image") or "").strip()
            a_title = e((a.get("title") or "")[:60])
            a_url = e(a.get("url") or "#")
            a_exc = e((a.get("excerpt") or "")[:80])
            img_tag = f'<img src="{e(a_img)}" alt="{a_title}" class="it2-spot-img">' if a_img and a_img.startswith("http") else '<div class="it2-spot-ph">&#127860;</div>'
            cards += f"""<a href="{a_url}" class="it2-spot-card">
              {img_tag}
              <div class="it2-spot-info"><h4 class="it2-spot-title">{a_title}</h4><p class="it2-spot-exc">{a_exc}</p></div>
            </a>"""
        spotlights_html += f"""
    <section class="it2-spotlight">
      <div class="it2-spot-header">
        <h2 class="it2-spot-heading">{c_name}</h2>
        <a href="{c_url}" class="it2-spot-more">View All &rarr;</a>
      </div>
      <div class="it2-spot-row">{cards}</div>
    </section>"""

    # --- Latest recipes grid ---
    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".it2")

    html_content = f"""
<main class="index-page it2">
  <section class="it2-hero" style="{hero_bg}">
    <div class="it2-hero-overlay">
      <div class="it2-hero-inner">
        <span class="it2-hero-label">{domain_name}</span>
        <h1 class="it2-hero-title">{ft}</h1>
        <p class="it2-hero-excerpt">{fx}</p>
        <a href="{fu}" class="it2-hero-btn">Read Recipe &rarr;</a>
      </div>
    </div>
  </section>

  <nav class="it2-cat-bar">
    <div class="it2-cat-inner">{cat_tabs}</div>
  </nav>

  {spotlights_html}

  <section class="it2-latest">
    <div class="it2-latest-header">
      <h2 class="it2-sec-title">Latest Recipes</h2>
      <p class="it2-sec-sub">Check out our newest additions</p>
    </div>
    <div class="it2-grid">{cards_html}</div>
    <div class="it2-more"><a href="{e(base_url)}/recipes" class="it2-btn-primary">View All Recipes &rarr;</a></div>
  </section>
  <div class="index-pagination-slot"></div>
</main>
"""

    css = f"""
{t['font_import']}
{card_css}
.it2 {{ {t['css_vars']} }}

/* --- Hero: full-width image banner with overlay --- */
.it2-hero {{ position: relative; min-height: 440px; display: flex; align-items: flex-end; }}
.it2-hero-overlay {{
    width: 100%; background: linear-gradient(to top, rgba(0,0,0,.7) 0%, rgba(0,0,0,.1) 100%);
    padding: 3rem 0;
}}
.it2-hero-inner {{ max-width: 800px; margin: 0 auto; padding: 0 1.5rem; color: #fff; text-align: center; }}
.it2-hero-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,.7); font-weight: 600; }}
.it2-hero-title {{ font-family: {ff}; font-size: 2.6rem; font-weight: 700; margin: 0.5rem 0 0.75rem; line-height: 1.15; }}
.it2-hero-excerpt {{ font-size: 1rem; opacity: 0.85; line-height: 1.6; margin-bottom: 1.5rem; }}
.it2-hero-btn {{
    display: inline-block; background: var(--primary); color: #fff;
    padding: 0.75rem 2rem; text-decoration: none; font-weight: 700; font-size: 0.95rem;
    transition: all 0.2s; border-bottom: 3px solid var(--secondary);
}}
.it2-hero-btn:hover {{ opacity: 0.9; transform: translateY(-2px); }}

/* --- Category tab bar --- */
.it2-cat-bar {{ border-bottom: 3px solid var(--primary); background: var(--bg); }}
.it2-cat-inner {{
    max-width: 1200px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; gap: 0; overflow-x: auto;
}}
.it2-tab {{
    padding: 1rem 1.5rem; text-decoration: none; color: var(--muted);
    font-size: 0.9rem; font-weight: 600; white-space: nowrap;
    border-bottom: 3px solid transparent; margin-bottom: -3px; transition: all 0.2s;
}}
.it2-tab:hover {{ color: var(--primary); border-bottom-color: var(--primary); }}

/* --- Category spotlights --- */
.it2-spotlight {{ max-width: 1200px; margin: 0 auto; padding: 2.5rem 1.5rem 1rem; }}
.it2-spot-header {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1rem; }}
.it2-spot-heading {{ font-family: {ff}; font-size: 1.5rem; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 0.5rem; }}
.it2-spot-heading::before {{ content: ''; width: 4px; height: 1.1em; background: var(--primary); border-radius: 2px; }}
.it2-spot-more {{ color: var(--primary); text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
.it2-spot-more:hover {{ opacity: 0.7; }}
.it2-spot-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }}
.it2-spot-card {{
    display: block; text-decoration: none; border: 1px solid var(--border);
    overflow: hidden; transition: all 0.3s; background: #fff;
}}
.it2-spot-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,.08); border-color: var(--primary); }}
.it2-spot-img {{ width: 100%; aspect-ratio: 4/3; object-fit: cover; display: block; }}
.it2-spot-ph {{ width: 100%; aspect-ratio: 4/3; background: var(--border); display: flex; align-items: center; justify-content: center; font-size: 2rem; }}
.it2-spot-info {{ padding: 0.75rem; }}
.it2-spot-title {{ font-size: 0.85rem; font-weight: 600; color: var(--text); line-height: 1.3; margin-bottom: 0.25rem; }}
.it2-spot-card:hover .it2-spot-title {{ color: var(--primary); }}
.it2-spot-exc {{ font-size: 0.78rem; color: var(--muted); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}

/* --- Latest recipes --- */
.it2-latest {{ max-width: 1200px; margin: 0 auto; padding: 3rem 1.5rem 4rem; }}
.it2-latest-header {{ text-align: center; margin-bottom: 2rem; }}
.it2-sec-title {{ font-family: {ff}; font-size: 2rem; font-weight: 700; color: var(--text); margin-bottom: 0.25rem; }}
.it2-sec-sub {{ color: var(--muted); font-size: 1rem; }}
.it2-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}
.it2-more {{ text-align: center; margin-top: 2.5rem; }}
.it2-btn-primary {{
    display: inline-block; background: var(--primary); color: #fff;
    padding: 0.8rem 2rem; text-decoration: none; font-weight: 700; font-size: 0.95rem;
    transition: all 0.2s; border-bottom: 3px solid var(--secondary);
}}
.it2-btn-primary:hover {{ opacity: 0.9; transform: translateY(-2px); }}

@media (max-width: 900px) {{
    .it2-spot-row {{ grid-template-columns: repeat(2, 1fr); }}
    .it2-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .it2-hero-title {{ font-size: 1.8rem; }}
}}
@media (max-width: 600px) {{
    .it2-spot-row {{ grid-template-columns: 1fr 1fr; }}
    .it2-grid {{ grid-template-columns: 1fr; }}
    .it2-hero {{ min-height: 320px; }}
    .it2-hero-title {{ font-size: 1.5rem; }}
}}
"""
    return {"html": html_content, "css": css}
