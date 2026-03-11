"""Sidebar for Theme 6 — Neo-Brutalist.
Bold and boxy widgets with hard offset shadows and thick borders.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module

ROOT = ".dp-t6-sidebar"

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
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "writers", "writer_6.py")
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("writer_6", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            w_out = mod.generate(config)
            writer_html = w_out.get("html", "")
            writer_css = w_out.get("css", "")

    # ── Related Articles ──────────────────────────────────────────
    from shared_article_card import render_cards
    # Set default template for this theme if not specified
    if not config.get("article_card_template"):
        config["article_card_template"] = "article_card_6"
    
    # Just show a few articles in sidebar
    cards_html, cards_css = render_cards(articles, config, show_excerpt=False, scope_prefix=ROOT)

    # ── Categories ──────────────────────────────────────────────
    cat_links = "".join(f'<li><a href="{html_module.escape(c.get("url", "#"))}">{html_module.escape(c.get("name", "")).upper()} <span class="t6-cat-count">{c.get("count", 0)}</span></a></li>' for c in categories[:10])

    html_content = f"""
<div class="dp-t6-sidebar">
  {writer_html}
  
  <div class="t6-sidebar-section">
    <h4 class="t6-side-title">THE ARCHIVE</h4>
    <ul class="t6-cat-list">
      {cat_links or "<li>NO COLLECTIONS YET</li>"}
    </ul>
  </div>

  <div class="t6-sidebar-section">
    <h4 class="t6-side-title">RECENT ECHOES</h4>
    <div class="t6-side-grid">
      {cards_html or '<p class="t6-side-empty">MORE BOLDNESS COMING...</p>'}
    </div>
  </div>
</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}

{writer_css}
{cards_css}

{ROOT} .t6-sidebar-section {{
    margin-bottom: 50px;
    background: #fff;
    border: 4px solid #000;
    box-shadow: 6px 6px 0px #000;
}}
{ROOT} .t6-sb-title {{
    font-family: {font_family};
    font-size: 1.5rem;
    font-weight: 900;
    text-transform: uppercase;
    margin-bottom: 20px;
    background: var(--primary);
    display: inline-block;
    padding: 4px 10px;
    border: 3px solid #000;
    margin-top: -36px;
    position: relative;
    z-index: 2;
}}
{ROOT} .t6-sb-body {{ font-size: 1rem; color: #333; }}
{ROOT} .t6-sb-list {{
    list-style: none;
    padding: 0; margin: 0;
}}
{ROOT} .t6-sb-list li {{ margin-bottom: 8px; }}
{ROOT} .t6-sb-list a {{
    color: #000;
    text-decoration: none;
    font-weight: 800;
    font-size: 1rem;
    padding: 4px 0;
    display: block;
    width: 100%;
    border-bottom: 3px solid transparent;
}}
{ROOT} .t6-sb-list a:hover {{ border-bottom: 3px solid var(--secondary); }}
{ROOT} .t6-sb-promo {{ background: var(--secondary); color: #fff; }}
{ROOT} .t6-sb-promo .t6-sb-title {{ background: #000; color: #fff; border-color: #fff; }}
{ROOT} .t6-sb-promo .t6-sb-body {{ color: #fff; }}
{ROOT} .t6-sb-input {{
    width: 100%;
    padding: 12px;
    border: 3px solid #000;
    margin-bottom: 15px;
    font-weight: 700;
}}
{ROOT} .t6-sb-btn {{
    width: 100%;
    padding: 14px;
    background: #000;
    color: #fff;
    border: 3px solid #fff;
    font-weight: 900;
    text-transform: uppercase;
    cursor: pointer;
    box-shadow: 4px 4px 0px #fff;
}}
{ROOT} .t6-sb-btn:active {{
    transform: translate(2px, 2px);
    box-shadow: 1px 1px 0px #fff;
}}
"""
    return {"html": html_content, "css": css_content}
