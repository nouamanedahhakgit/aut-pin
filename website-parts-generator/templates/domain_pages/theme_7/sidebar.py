"""Sidebar for Theme 7 — Minimalist Glass.
Floating glass-style widgets with soft glows and minimal borders.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module

ROOT = ".dp-t7-sidebar"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    categories = config.get("categories") or []
    writer = config.get("writer") or {}
    articles = config.get("articles") or []
    
    # ── Writer Section ──────────────────────────────────────────
    writer_html = ""
    writer_css = ""
    if writer:
        import importlib.util
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "writers", "writer_7.py")
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("writer_7", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            w_out = mod.generate(config)
            writer_html = w_out.get("html", "")
            writer_css = w_out.get("css", "")

    # ── Related Articles ──────────────────────────────────────────
    from shared_article_card import render_cards
    # Set default template for this theme if not specified
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_7"
    
    # Just show a few articles in sidebar
    cards_html, cards_css = render_cards(articles, config, show_excerpt=False, scope_prefix=ROOT)

    # ── Categories ──────────────────────────────────────────────
    cat_links = "".join(f'<li><a href="{html_module.escape(c.get("url", "#"))}">{html_module.escape(c.get("name", ""))} <span class="t7-cat-count">{c.get("count", 0)}</span></a></li>' for c in categories[:10])

    html_content = f"""
<div class="dp-t7-sidebar">
  {writer_html}
  
  <div class="t7-sidebar-section">
    <h4 class="t7-side-title">Curated series</h4>
    <ul class="t7-cat-list">
      {cat_links or "<li>No series found</li>"}
    </ul>
  </div>

  <div class="t7-sidebar-section">
    <h4 class="t7-side-title">Latest Inspiration</h4>
    <div class="t7-side-grid">
      {cards_html or '<p class="t7-side-empty">New curation in progress...</p>'}
    </div>
  </div>
</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
    border-radius: var(--radius);
    padding: 32px;
    box-shadow: var(--shadow);
}}
{ROOT} .t7-sb-title {{
    font-family: {font_family};
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 24px;
    color: var(--secondary);
    letter-spacing: 0.15em;
}}
{ROOT} .t7-sb-body {{ font-size: 0.95rem; color: var(--muted); line-height: 1.8; }}
{ROOT} .t7-sb-list {{
    list-style: none;
    padding: 0; margin: 0;
}}
{ROOT} .t7-sb-list li {{ margin-bottom: 12px; }}
{ROOT} .t7-sb-list a {{
    color: var(--primary);
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 400;
    transition: color 0.3s;
    display: block;
}}
{ROOT} .t7-sb-list a:hover {{ color: var(--secondary); transform: translateX(4px); }}
{ROOT} .t7-sb-notif {{ background: var(--primary); color: #fff; border: none; }}
{ROOT} .t7-sb-notif .t7-sb-title {{ color: rgba(255,255,255,0.6); }}
{ROOT} .t7-sb-notif .t7-sb-body {{ color: rgba(255,255,255,0.9); }}
{ROOT} .t7-sb-input {{
    width: 100%;
    padding: 14px 20px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: #fff;
    border-radius: 50px;
    margin-bottom: 16px;
    font-size: 0.9rem;
}}
{ROOT} .t7-sb-btn {{
    width: 100%;
    padding: 14px;
    background: #fff;
    color: var(--primary);
    border: none;
    border-radius: 50px;
    font-weight: 700;
    text-transform: uppercase;
    cursor: pointer;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    transition: opacity 0.2s;
}}
{ROOT} .t7-sb-btn:hover {{ opacity: 0.9; }}
"""
    return {"html": html_content, "css": css_content}
