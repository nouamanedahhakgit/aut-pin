"""Theme 12 — Footer: Candy Pop — pastel gradient, rainbow top strip, playful 3-col layout."""
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

    cat_chips = ""
    for c in categories[:8]:
        url = html_module.escape(c.get("url") or "#")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            cat_chips += f'<a href="{url}" class="ft12-chip">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<li><a href="{p_url}" class="ft12-link">{p_name}</a></li>'

    html_content = f"""
<footer class="site-footer dp-t12-footer">
  <div class="ft12-rainbow-strip"></div>
  <div class="ft12-inner">
    <div class="ft12-col ft12-brand">
      <a href="{html_module.escape(base_url or '/')}" class="ft12-logo">
        <span class="ft12-logo-emoji">&#127849;</span>
        <span class="ft12-logo-name">{name}</span>
      </a>
      <p class="ft12-tagline">Fun recipes made with love! Every dish is a little adventure. &#10024;</p>
    </div>
    <div class="ft12-col">
      <h4 class="ft12-heading">&#128279; Quick Links</h4>
      <ul class="ft12-list">
        <li><a href="{html_module.escape(base_url or '/')}" class="ft12-link">Home</a></li>
        <li><a href="{html_module.escape(base_url)}/recipes" class="ft12-link">All Recipes</a></li>
        <li><a href="{html_module.escape(base_url)}/about-us" class="ft12-link">About Us</a></li>
        <li><a href="{html_module.escape(base_url)}/contact-us" class="ft12-link">Contact</a></li>
        {pages_links}
      </ul>
    </div>
    <div class="ft12-col">
      <h4 class="ft12-heading">&#127860; Categories</h4>
      <div class="ft12-chips">{cat_chips or '<span class="ft12-chip">Recipes</span>'}</div>
    </div>
  </div>
  <div class="ft12-bottom">
    <span>&copy; {year} {name}</span>
    <span class="ft12-bottom-dot">&#10024;</span>
    <span>Made with &#128147; and sprinkles</span>
  </div>
</footer>
"""

    css = f"""
{t['font_import']}
.dp-t12-footer {{ {t['css_vars']} margin-top: 4rem; background: var(--surface); border-top: 1px solid var(--border); }}
.ft12-rainbow-strip {{
    height: 4px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent), var(--lavender), var(--yellow), var(--primary));
    background-size: 200% 100%; animation: t12-rainbow 4s linear infinite;
}}
@keyframes t12-rainbow {{ 0% {{ background-position: 0% 50%; }} 100% {{ background-position: 200% 50%; }} }}
.ft12-inner {{
    max-width: 1200px; margin: 0 auto; padding: 3rem 1.5rem;
    display: grid; grid-template-columns: 1.6fr 1fr 1.2fr; gap: 3rem;
}}
.ft12-logo {{ display: flex; align-items: center; gap: 8px; text-decoration: none; color: var(--text); margin-bottom: 0.9rem; }}
.ft12-logo-emoji {{ font-size: 1.4rem; }}
.ft12-logo-name {{ font-family: {ff}; font-size: 1.2rem; font-weight: 900; }}
.ft12-tagline {{ color: var(--muted); font-size: 0.88rem; line-height: 1.65; font-weight: 500; }}
.ft12-heading {{ font-size: 0.85rem; font-weight: 800; color: var(--text); margin-bottom: 1rem; }}
.ft12-list {{ list-style: none; padding: 0; margin: 0; }}
.ft12-list li {{ margin-bottom: 0.55rem; }}
.ft12-link {{ text-decoration: none; color: var(--muted); font-size: 0.88rem; font-weight: 600; transition: color 0.2s; }}
.ft12-link:hover {{ color: var(--primary); }}
.ft12-chips {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
.ft12-chip {{
    display: inline-block; padding: 0.35rem 0.9rem; border-radius: 50px;
    background: var(--pink-pale); border: 2px solid var(--pink-border);
    color: var(--primary); font-size: 0.78rem; font-weight: 700;
    text-decoration: none; transition: all 0.25s;
}}
.ft12-chip:hover {{ background: var(--primary); color: #fff; border-color: var(--primary); transform: scale(1.08); }}
.ft12-bottom {{
    border-top: 1px solid var(--border); text-align: center;
    padding: 1.25rem 1.5rem; color: var(--muted); font-size: 0.82rem; font-weight: 600;
    display: flex; align-items: center; justify-content: center; gap: 0.5rem; flex-wrap: wrap;
}}
.ft12-bottom-dot {{ color: var(--primary); }}
@media (max-width: 768px) {{ .ft12-inner {{ grid-template-columns: 1fr; gap: 2rem; }} }}
"""
    return {"html": html_content, "css": css}
