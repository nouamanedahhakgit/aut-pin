"""Theme 3 — Footer: Dark glassmorphism, 3-column layout, glow accent top border."""
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
            cat_links += f'<a href="{url}" class="ft3-tag">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<li><a href="{p_url}" class="ft3-link">{p_name}</a></li>'

    html_content = f"""
<footer class="site-footer dp-t3-footer">
  <div class="ft3-glow-line"></div>
  <div class="ft3-inner">
    <div class="ft3-col ft3-brand">
      <div class="ft3-logo">
        <span class="ft3-logo-icon">&#127860;</span>
        <span class="ft3-name">{name}</span>
      </div>
      <p class="ft3-tagline">Fresh recipes, crafted with passion. Bringing flavour and inspiration to your kitchen.</p>
    </div>
    <div class="ft3-col">
      <h4 class="ft3-heading">Explore</h4>
      <ul class="ft3-list">
        <li><a href="{html_module.escape(base_url or '/')}" class="ft3-link">Home</a></li>
        <li><a href="{html_module.escape(base_url)}/recipes" class="ft3-link">All Recipes</a></li>
        <li><a href="{html_module.escape(base_url)}/about-us" class="ft3-link">About Us</a></li>
        <li><a href="{html_module.escape(base_url)}/contact-us" class="ft3-link">Contact</a></li>
        {pages_links}
      </ul>
    </div>
    <div class="ft3-col">
      <h4 class="ft3-heading">Categories</h4>
      <div class="ft3-tags">{cat_links or '<span class="ft3-tag">Recipes</span>'}</div>
    </div>
  </div>
  <div class="ft3-bottom"><p>&copy; {year} {name}. All rights reserved.</p></div>
</footer>
"""

    css = f"""
{t['font_import']}
.dp-t3-footer {{ {t['css_vars']} margin-top: 4rem; }}
.ft3-glow-line {{
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--primary));
    box-shadow: 0 0 12px color-mix(in srgb, var(--primary) 30%, transparent);
}}
.ft3-inner {{
    max-width: 1200px; margin: 0 auto; padding: 3.5rem 1.5rem;
    display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 3rem;
}}
.ft3-logo {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }}
.ft3-logo-icon {{ font-size: 1.3rem; }}
.ft3-name {{
    font-family: {ff}; font-size: 1.35rem; font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.ft3-tagline {{ color: var(--muted); font-size: 0.88rem; line-height: 1.65; }}
.ft3-heading {{
    font-family: {ff}; font-size: 1rem; font-weight: 700; color: var(--text);
    margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.06em; font-size: 0.85rem;
}}
.ft3-list {{ list-style: none; padding: 0; margin: 0; }}
.ft3-list li {{ margin-bottom: 0.5rem; }}
.ft3-link {{
    text-decoration: none; color: var(--muted); font-size: 0.88rem;
    transition: color 0.25s;
}}
.ft3-link:hover {{ color: var(--secondary); }}
.ft3-tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
.ft3-tag {{
    display: inline-block; padding: 0.3rem 0.85rem; border-radius: 9999px;
    border: 1px solid var(--glass-border); color: var(--muted); font-size: 0.78rem;
    text-decoration: none; transition: all 0.25s;
    background: var(--glass); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
}}
.ft3-tag:hover {{
    border-color: var(--primary); color: var(--primary);
    box-shadow: 0 0 10px color-mix(in srgb, var(--primary) 20%, transparent);
}}
.ft3-bottom {{
    border-top: 1px solid var(--glass-border); text-align: center;
    padding: 1.25rem 1.5rem; color: var(--muted); font-size: 0.78rem;
}}
@media (max-width: 768px) {{ .ft3-inner {{ grid-template-columns: 1fr; gap: 2rem; }} }}
"""
    return {"html": html_content, "css": css}
