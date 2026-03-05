"""Theme 1 — Footer: Warm gradient accent border, 3-column layout."""
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

    cat_links = ""
    for c in categories[:6]:
        url = html_module.escape(c.get("url") or "#")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            cat_links += f'<a href="{url}" class="ft1-tag">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<li><a href="{p_url}" class="ft1-link">{p_name}</a></li>'

    html_content = f"""
<footer class="site-footer dp-t1-footer">
  <div class="ft1-accent"></div>
  <div class="ft1-inner">
    <div class="ft1-col ft1-brand">
      <div class="ft1-logo">
        <span class="ft1-logo-icon">&#127860;</span>
        <span class="ft1-name">{name}</span>
      </div>
      <p class="ft1-tagline">Fresh recipes, made with love. Bringing joy to your kitchen every day.</p>
    </div>
    <div class="ft1-col">
      <h4 class="ft1-heading">Explore</h4>
      <ul class="ft1-list">
        <li><a href="{html_module.escape(base_url or '/')}" class="ft1-link">Home</a></li>
        <li><a href="{html_module.escape(base_url)}/recipes" class="ft1-link">All Recipes</a></li>
        <li><a href="{html_module.escape(base_url)}/about-us" class="ft1-link">About Us</a></li>
        {pages_links}
      </ul>
    </div>
    <div class="ft1-col">
      <h4 class="ft1-heading">Categories</h4>
      <div class="ft1-tags">{cat_links or '<span class="ft1-tag">Recipes</span>'}</div>
    </div>
  </div>
  <div class="ft1-bottom"><p>&copy; {year} {name}. All rights reserved.</p></div>
</footer>
"""

    css = f"""
{t['font_import']}
.dp-t1-footer {{ {t['css_vars']} margin-top: 4rem; }}
.ft1-accent {{ height: 4px; background: linear-gradient(90deg, var(--primary), var(--secondary)); }}
.ft1-inner {{
    max-width: 1200px; margin: 0 auto; padding: 3rem 1.5rem;
    display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 3rem;
}}
.ft1-logo {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }}
.ft1-logo-icon {{ font-size: 1.3rem; }}
.ft1-name {{ font-family: {ff}; font-size: 1.4rem; font-weight: 700; color: var(--text); }}
.ft1-tagline {{ color: var(--muted); font-size: 0.9rem; line-height: 1.6; }}
.ft1-heading {{ font-family: {ff}; font-size: 1.1rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; }}
.ft1-list {{ list-style: none; padding: 0; margin: 0; }}
.ft1-list li {{ margin-bottom: 0.5rem; }}
.ft1-link {{ text-decoration: none; color: var(--muted); font-size: 0.9rem; transition: color 0.2s; }}
.ft1-link:hover {{ color: var(--primary); }}
.ft1-tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
.ft1-tag {{
    display: inline-block; padding: 0.35rem 0.85rem; border-radius: 9999px;
    border: 1px solid var(--border); color: var(--muted); font-size: 0.8rem;
    text-decoration: none; transition: all 0.2s;
}}
.ft1-tag:hover {{ border-color: var(--primary); color: var(--primary); }}
.ft1-bottom {{ border-top: 1px solid var(--border); text-align: center; padding: 1.25rem 1.5rem; color: var(--muted); font-size: 0.8rem; }}
@media (max-width: 768px) {{ .ft1-inner {{ grid-template-columns: 1fr; gap: 2rem; }} }}
"""
    return {"html": html_content, "css": css}
