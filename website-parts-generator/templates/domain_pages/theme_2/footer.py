"""Theme 2 — Footer: Modern clean, accent top line, 3-column grid."""
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
            cat_links += f'<a href="{url}" class="ft2-cat">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<li><a href="{p_url}" class="ft2-link">{p_name}</a></li>'

    html_content = f"""
<footer class="site-footer dp-t2-footer">
  <div class="ft2-inner">
    <div class="ft2-col">
      <span class="ft2-logo">{name}</span>
      <p class="ft2-desc">Fresh recipes, made with love. Bringing joy to your kitchen every day.</p>
    </div>
    <div class="ft2-col">
      <h4 class="ft2-heading">Pages</h4>
      <ul class="ft2-list">
        <li><a href="{html_module.escape(base_url or '/')}" class="ft2-link">Home</a></li>
        <li><a href="{html_module.escape(base_url)}/recipes" class="ft2-link">Recipes</a></li>
        <li><a href="{html_module.escape(base_url)}/about-us" class="ft2-link">About</a></li>
        {pages_links}
      </ul>
    </div>
    <div class="ft2-col">
      <h4 class="ft2-heading">Categories</h4>
      <div class="ft2-cats">{cat_links or '<span class="ft2-cat">Recipes</span>'}</div>
    </div>
  </div>
  <div class="ft2-bottom"><p>&copy; {year} {name}. All rights reserved.</p></div>
</footer>
"""

    css = f"""
{t['font_import']}
.dp-t2-footer {{ {t['css_vars']} margin-top: 4rem; border-top: 3px solid var(--primary); }}
.ft2-inner {{
    max-width: 1200px; margin: 0 auto; padding: 3rem 1.5rem;
    display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 3rem;
}}
.ft2-logo {{ font-family: {ff}; font-size: 1.3rem; font-weight: 700; color: var(--text); display: block; margin-bottom: 0.75rem; }}
.ft2-desc {{ color: var(--muted); font-size: 0.9rem; line-height: 1.6; }}
.ft2-heading {{ font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text); margin-bottom: 1rem; }}
.ft2-list {{ list-style: none; padding: 0; margin: 0; }}
.ft2-list li {{ margin-bottom: 0.4rem; }}
.ft2-link {{ text-decoration: none; color: var(--muted); font-size: 0.9rem; transition: color 0.2s; }}
.ft2-link:hover {{ color: var(--primary); }}
.ft2-cats {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.ft2-cat {{
    display: inline-block; padding: 0.3rem 0.75rem; border: 1px solid var(--border);
    color: var(--muted); font-size: 0.8rem; text-decoration: none; transition: all 0.2s;
}}
.ft2-cat:hover {{ border-color: var(--primary); color: var(--primary); }}
.ft2-bottom {{ border-top: 1px solid var(--border); text-align: center; padding: 1.25rem 1.5rem; color: var(--muted); font-size: 0.8rem; }}
@media (max-width: 768px) {{ .ft2-inner {{ grid-template-columns: 1fr; gap: 2rem; }} }}
"""
    return {"html": html_content, "css": css}
