"""Theme 10 — Footer: Bento Fresh, clean mint accent top strip, 3-col modern layout."""
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
            cat_chips += f'<a href="{url}" class="ft10-chip">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<li><a href="{p_url}" class="ft10-link">{p_name}</a></li>'

    html_content = f"""
<footer class="site-footer dp-t10-footer">
  <div class="ft10-top-strip"></div>
  <div class="ft10-inner">
    <div class="ft10-col ft10-brand">
      <a href="{html_module.escape(base_url or '/')}" class="ft10-logo">
        <span class="ft10-logo-dot"></span>
        <span class="ft10-logo-name">{name}</span>
      </a>
      <p class="ft10-tagline">Fresh, wholesome recipes for every day. Tested, trusted, and made with love.</p>
      <div class="ft10-social-row">
        <span class="ft10-social-dot" aria-hidden="true">&#9679;</span>
        <span class="ft10-social-tag">Recipe Blog</span>
      </div>
    </div>
    <div class="ft10-col">
      <h4 class="ft10-heading">Quick Links</h4>
      <ul class="ft10-list">
        <li><a href="{html_module.escape(base_url or '/')}" class="ft10-link">Home</a></li>
        <li><a href="{html_module.escape(base_url)}/recipes" class="ft10-link">All Recipes</a></li>
        <li><a href="{html_module.escape(base_url)}/about-us" class="ft10-link">About Us</a></li>
        <li><a href="{html_module.escape(base_url)}/contact-us" class="ft10-link">Contact</a></li>
        {pages_links}
      </ul>
    </div>
    <div class="ft10-col">
      <h4 class="ft10-heading">Categories</h4>
      <div class="ft10-chips">{cat_chips or '<span class="ft10-chip">Recipes</span>'}</div>
    </div>
  </div>
  <div class="ft10-bottom">
    <span>&copy; {year} {name}. All rights reserved.</span>
    <span class="ft10-bottom-dot">&#183;</span>
    <span>Made with &#10084; for food lovers.</span>
  </div>
</footer>
"""

    css = f"""
{t['font_import']}
.dp-t10-footer {{ {t['css_vars']} margin-top: 4rem; background: var(--surface); border-top: 1px solid var(--border); }}
.ft10-top-strip {{ height: 4px; background: linear-gradient(90deg, var(--primary), #00E5CC, var(--primary)); background-size: 200% 100%; animation: ft10-shimmer 3s linear infinite; }}
@keyframes ft10-shimmer {{ 0% {{ background-position: 0% 0; }} 100% {{ background-position: 200% 0; }} }}
.ft10-inner {{
    max-width: 1200px; margin: 0 auto; padding: 3rem 1.5rem;
    display: grid; grid-template-columns: 1.6fr 1fr 1.2fr; gap: 3rem;
}}
.ft10-logo {{ display: flex; align-items: center; gap: 8px; text-decoration: none; color: var(--text); margin-bottom: 0.9rem; }}
.ft10-logo-dot {{ width: 24px; height: 24px; border-radius: 6px; background: var(--primary); flex-shrink: 0; }}
.ft10-logo-name {{ font-family: {ff}; font-size: 1.2rem; font-weight: 700; font-style: italic; }}
.ft10-tagline {{ color: var(--muted); font-size: 0.88rem; line-height: 1.65; margin-bottom: 1rem; }}
.ft10-social-row {{ display: flex; align-items: center; gap: 0.4rem; }}
.ft10-social-dot {{ color: var(--primary); font-size: 0.5rem; }}
.ft10-social-tag {{ font-size: 0.8rem; font-weight: 600; color: var(--primary); }}
.ft10-heading {{ font-size: 0.8rem; font-weight: 700; color: var(--text); text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 1rem; }}
.ft10-list {{ list-style: none; padding: 0; margin: 0; }}
.ft10-list li {{ margin-bottom: 0.55rem; }}
.ft10-link {{ text-decoration: none; color: var(--muted); font-size: 0.88rem; transition: color 0.2s; }}
.ft10-link:hover {{ color: var(--primary); }}
.ft10-chips {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
.ft10-chip {{
    display: inline-block; padding: 0.3rem 0.85rem; border-radius: 50px;
    background: var(--mint-pale); border: 1px solid var(--mint-border);
    color: var(--primary); font-size: 0.78rem; font-weight: 600;
    text-decoration: none; transition: all 0.2s;
}}
.ft10-chip:hover {{ background: var(--primary); color: #fff; border-color: var(--primary); }}
.ft10-bottom {{
    border-top: 1px solid var(--border); text-align: center;
    padding: 1.25rem 1.5rem; color: var(--muted); font-size: 0.8rem;
    display: flex; align-items: center; justify-content: center; gap: 0.5rem; flex-wrap: wrap;
}}
.ft10-bottom-dot {{ color: var(--border); }}
@media (max-width: 768px) {{ .ft10-inner {{ grid-template-columns: 1fr; gap: 2rem; }} }}
"""
    return {"html": html_content, "css": css}
