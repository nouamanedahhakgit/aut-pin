"""Theme 9 — Footer: Warm sage accent border, 3-column editorial layout."""
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
            cat_links += f'<a href="{url}" class="ft9-tag">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<li><a href="{p_url}" class="ft9-link">{p_name}</a></li>'

    html_content = f"""
<footer class="site-footer dp-t9-footer">
  <div class="ft9-accent"></div>
  <div class="ft9-inner">
    <div class="ft9-col ft9-brand">
      <div class="ft9-logo">
        <span class="ft9-logo-icon">&#127858;</span>
        <span class="ft9-name">{name}</span>
      </div>
      <p class="ft9-tagline">Wholesome recipes made with fresh seasonal ingredients. Bringing joy to every table.</p>
    </div>
    <div class="ft9-col">
      <h4 class="ft9-heading">Explore</h4>
      <ul class="ft9-list">
        <li><a href="{html_module.escape(base_url or '/')}" class="ft9-link">Home</a></li>
        <li><a href="{html_module.escape(base_url)}/recipes" class="ft9-link">All Recipes</a></li>
        <li><a href="{html_module.escape(base_url)}/about-us" class="ft9-link">About Us</a></li>
        {pages_links}
      </ul>
    </div>
    <div class="ft9-col">
      <h4 class="ft9-heading">Categories</h4>
      <div class="ft9-tags">{cat_links or '<span class="ft9-tag">Recipes</span>'}</div>
    </div>
  </div>
  <div class="ft9-bottom"><p>&copy; {year} {name}. All rights reserved.</p></div>
</footer>
"""

    css = f"""
{t['font_import']}
.dp-t9-footer {{ {t['css_vars']} margin-top: 4rem; border-top: 1px solid var(--border); background: var(--surface); }}
.ft9-accent {{ height: 3px; background: linear-gradient(90deg, var(--primary), var(--secondary), var(--primary)); }}
.ft9-inner {{
    max-width: 1200px; margin: 0 auto; padding: 3rem 1.5rem;
    display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 3rem;
}}
.ft9-logo {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }}
.ft9-logo-icon {{ font-size: 1.4rem; }}
.ft9-name {{ font-family: {ff}; font-size: 1.4rem; font-weight: 700; color: var(--text); }}
.ft9-tagline {{ color: var(--muted); font-size: 0.9rem; line-height: 1.6; font-style: italic; }}
.ft9-heading {{ font-family: {ff}; font-size: 1.05rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; }}
.ft9-list {{ list-style: none; padding: 0; margin: 0; }}
.ft9-list li {{ margin-bottom: 0.5rem; }}
.ft9-link {{ text-decoration: none; color: var(--muted); font-size: 0.9rem; transition: color 0.2s; }}
.ft9-link:hover {{ color: var(--primary); }}
.ft9-tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
.ft9-tag {{
    display: inline-block; padding: 0.35rem 0.9rem; border-radius: 9999px;
    border: 1px solid var(--border); color: var(--muted); font-size: 0.8rem;
    text-decoration: none; transition: all 0.2s; background: var(--bg);
}}
.ft9-tag:hover {{ border-color: var(--primary); color: var(--primary); background: var(--gold-light); }}
.ft9-bottom {{ border-top: 1px solid var(--border); text-align: center; padding: 1.25rem 1.5rem; color: var(--muted); font-size: 0.8rem; }}
@media (max-width: 768px) {{ .ft9-inner {{ grid-template-columns: 1fr; gap: 2rem; }} }}
"""
    return {"html": html_content, "css": css}
