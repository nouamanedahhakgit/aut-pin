"""Theme 11 — Footer: Art Deco — dark obsidian, gold ornaments, symmetrical 3-col layout."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module
from datetime import datetime


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]

    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []
    year = datetime.now().year

    cat_items = ""
    for c in categories[:6]:
        url = html_module.escape(c.get("url") or "#")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            cat_items += f'<a href="{url}" class="ft11-cat">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<li><a href="{p_url}" class="ft11-link">{p_name}</a></li>'

    html_content = f"""
<footer class="site-footer dp-t11-footer">
  <div class="ft11-gold-strip"></div>
  <div class="ft11-inner">
    <div class="ft11-col ft11-brand">
      <a href="{html_module.escape(base_url or '/')}" class="ft11-logo">
        <span class="ft11-logo-diamond">&#9670;</span>
        <span class="ft11-logo-name">{name}</span>
      </a>
      <p class="ft11-tagline">Curated recipes crafted with elegance. Every dish, a masterpiece.</p>
      <div class="ft11-ornament-sm">&#9671; &#9670; &#9671;</div>
    </div>
    <div class="ft11-col">
      <h4 class="ft11-heading">Navigation</h4>
      <ul class="ft11-list">
        <li><a href="{html_module.escape(base_url or '/')}" class="ft11-link">Home</a></li>
        <li><a href="{html_module.escape(base_url)}/recipes" class="ft11-link">All Recipes</a></li>
        <li><a href="{html_module.escape(base_url)}/about-us" class="ft11-link">About Us</a></li>
        <li><a href="{html_module.escape(base_url)}/contact-us" class="ft11-link">Contact</a></li>
        {pages_links}
      </ul>
    </div>
    <div class="ft11-col">
      <h4 class="ft11-heading">Categories</h4>
      <div class="ft11-cats">{cat_items or '<span class="ft11-cat">Recipes</span>'}</div>
    </div>
  </div>
  <div class="ft11-bottom">
    <span class="ft11-bottom-ornament">&#9670;</span>
    <span>&copy; {year} {name}. All rights reserved.</span>
    <span class="ft11-bottom-ornament">&#9670;</span>
  </div>
</footer>
"""

    css = f"""
{t['font_import']}
.dp-t11-footer {{ {t['css_vars']} margin-top: 4rem; background: var(--primary); color: var(--text-on-primary); }}
.ft11-gold-strip {{ height: 3px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }}
.ft11-inner {{
    max-width: 1100px; margin: 0 auto; padding: 3rem 1.5rem;
    display: grid; grid-template-columns: 1.6fr 1fr 1.2fr; gap: 3rem;
}}
.ft11-logo {{ display: flex; align-items: center; gap: 8px; text-decoration: none; color: var(--text-on-primary); margin-bottom: 0.9rem; }}
.ft11-logo-diamond {{ color: var(--gold); font-size: 1rem; }}
.ft11-logo-name {{ font-family: {ff}; font-size: 1.15rem; font-weight: 700; letter-spacing: 0.04em; }}
.ft11-tagline {{ color: var(--text-on-primary-muted); font-size: 0.88rem; line-height: 1.65; margin-bottom: 1rem; }}
.ft11-ornament-sm {{ color: var(--gold); font-size: 0.5rem; letter-spacing: 0.5em; }}
.ft11-heading {{
    font-size: 0.72rem; font-weight: 600; color: var(--gold);
    text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 1rem;
    padding-bottom: 0.5rem; border-bottom: 1px solid var(--gold-light);
}}
.ft11-list {{ list-style: none; padding: 0; margin: 0; }}
.ft11-list li {{ margin-bottom: 0.55rem; }}
.ft11-link {{ text-decoration: none; color: var(--text-on-primary-muted); font-size: 0.88rem; transition: color 0.25s; }}
.ft11-link:hover {{ color: var(--gold); }}
.ft11-cats {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
.ft11-cat {{
    display: inline-block; padding: 0.3rem 0.85rem;
    border: 1px solid var(--gold-border); color: var(--text-on-primary-muted);
    font-size: 0.78rem; font-weight: 500; text-decoration: none;
    text-transform: uppercase; letter-spacing: 0.08em; transition: all 0.25s;
}}
.ft11-cat:hover {{ background: var(--gold); color: var(--primary); border-color: var(--gold); }}
.ft11-bottom {{
    border-top: 1px solid var(--gold-light); text-align: center;
    padding: 1.25rem 1.5rem; color: var(--text-on-primary-muted); font-size: 0.78rem;
    display: flex; align-items: center; justify-content: center; gap: 0.75rem;
}}
.ft11-bottom-ornament {{ color: var(--gold); font-size: 0.4rem; }}
@media (max-width: 768px) {{ .ft11-inner {{ grid-template-columns: 1fr; gap: 2rem; }} }}
"""
    return {"html": html_content, "css": css}
