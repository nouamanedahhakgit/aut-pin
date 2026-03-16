"""Sidebar for Theme 8 — Aurora Borealis Dark.
Dark sidebar with glowing category pills, aurora-accented article widgets,
and a floating newsletter CTA panel with violet-to-cyan gradient.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module

ROOT = ".dp-t8-sidebar"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    categories = config.get("categories") or []
    writer     = config.get("writer") or {}
    articles   = config.get("articles") or []

    # ── Writer widget ──────────────────────────────────────────────
    writer_html = ""
    writer_css  = ""
    if writer:
        import importlib.util
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "writers", "writer_7.py")
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("writer_7", path)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            w_out      = mod.generate(config)
            writer_html = w_out.get("html", "")
            writer_css  = w_out.get("css", "")

    # ── Recent articles ───────────────────────────────────────────
    from shared_article_card import render_cards
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_7"
    cards_html, cards_css = render_cards(articles, config, show_excerpt=False, scope_prefix=ROOT)

    # ── Category pills ────────────────────────────────────────────
    cat_pills = "".join(
        f'<a class="t8-cat-pill" href="{html_module.escape(c.get("url","#"))}">'
        f'{html_module.escape(c.get("name",""))}'
        f'<span class="t8-cat-count">{c.get("count", 0)}</span></a>'
        for c in categories[:10]
    )

    html_content = f"""
<div class="dp-t8-sidebar">

  {writer_html}

  <div class="t8-sb-widget">
    <div class="t8-sb-widget-top">
      <h4 class="t8-sb-title">Curated Series</h4>
    </div>
    <div class="t8-cat-pill-wrap">
      {cat_pills or '<p class="t8-sb-empty">No series yet</p>'}
    </div>
  </div>

  <div class="t8-sb-widget">
    <div class="t8-sb-widget-top">
      <h4 class="t8-sb-title">Recent Illuminations</h4>
    </div>
    <div class="t8-sb-articles">
      {cards_html or '<p class="t8-sb-empty">New recipes in progress…</p>'}
    </div>
  </div>

  <div class="t8-sb-cta">
    <div class="t8-sb-cta-glow"></div>
    <div class="t8-sb-cta-inner">
      <h4>Stay Illuminated</h4>
      <p>Join our aurora kitchen newsletter for weekly inspiration.</p>
      <input type="email" placeholder="your@email.com" class="t8-sb-input">
      <button class="t8-sb-btn">Subscribe ✦</button>
    </div>
  </div>

</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} display: flex; flex-direction: column; gap: 24px; }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{writer_css}
{cards_css}

{ROOT} .t8-sb-widget {{
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 28px;
    transition: border-color 0.3s;
}}
{ROOT} .t8-sb-widget:hover {{ border-color: rgba(124,58,237,0.45); }}
{ROOT} .t8-sb-widget-top {{
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(124,58,237,0.15);
}}
{ROOT} .t8-sb-title {{
    font-family: {font_family};
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--secondary);
    margin: 0;
}}
{ROOT} .t8-sb-empty {{
    font-size: 0.88rem;
    color: var(--muted);
    font-style: italic;
    margin: 0;
}}

/* Category pills */
{ROOT} .t8-cat-pill-wrap {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}}
{ROOT} .t8-cat-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 50px;
    color: var(--muted);
    text-decoration: none;
    font-size: 0.82rem;
    font-weight: 500;
    transition: all 0.25s ease;
}}
{ROOT} .t8-cat-pill:hover {{
    background: rgba(124,58,237,0.18);
    border-color: rgba(124,58,237,0.5);
    color: var(--text);
    transform: translateY(-2px);
}}
{ROOT} .t8-cat-count {{
    font-size: 0.7rem;
    background: rgba(6,182,212,0.2);
    color: var(--secondary);
    padding: 1px 7px;
    border-radius: 50px;
    font-weight: 700;
}}

/* Recent articles */
{ROOT} .t8-sb-articles {{ display: flex; flex-direction: column; gap: 0; }}

/* Newsletter CTA */
{ROOT} .t8-sb-cta {{
    position: relative;
    background: linear-gradient(135deg, #1a0938, #0a2040);
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: var(--radius-lg);
    padding: 32px 28px;
    overflow: hidden;
}}
{ROOT} .t8-sb-cta-glow {{
    position: absolute;
    top: -30px; right: -30px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(124,58,237,0.3), transparent 70%);
    pointer-events: none;
}}
{ROOT} .t8-sb-cta-inner {{ position: relative; z-index: 1; }}
{ROOT} .t8-sb-cta h4 {{
    font-family: {font_family};
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 8px;
    background: linear-gradient(135deg, #fff, var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
{ROOT} .t8-sb-cta p {{
    font-size: 0.85rem;
    color: var(--muted);
    line-height: 1.6;
    margin: 0 0 20px;
}}
{ROOT} .t8-sb-input {{
    width: 100%;
    padding: 12px 18px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 12px;
    color: var(--text);
    font-size: 0.88rem;
    margin-bottom: 12px;
    transition: border-color 0.25s;
}}
{ROOT} .t8-sb-input::placeholder {{ color: var(--muted); }}
{ROOT} .t8-sb-input:focus {{
    outline: none;
    border-color: var(--secondary);
    background: rgba(6,182,212,0.04);
}}
{ROOT} .t8-sb-btn {{
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    cursor: pointer;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    box-shadow: 0 4px 20px rgba(124,58,237,0.3);
}}
{ROOT} .t8-sb-btn:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(124,58,237,0.45);
}}
"""
    return {"html": html_content, "css": css_content}
