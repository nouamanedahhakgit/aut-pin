"""Theme 9 — Header: White editorial top bar, centered logo, split navigation."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]

    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []

    left_links = [
        (f"{base_url or '/'}", "Home"),
        (f"{base_url}/recipes", "Recipes"),
    ]
    right_links = []
    cats_with_recipes = [c for c in categories if int(c.get("count", 0) or 0) > 0]
    for c in cats_with_recipes[:3]:
        url = html_module.escape(c.get("url") or f"{base_url}/categories")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            right_links.append((url, cat_name))
    if not right_links:
        right_links.append((f"{base_url}/categories", "Categories"))

    about_url = f"{base_url}/about-us"
    for p in config.get("domain_pages") or []:
        if isinstance(p, dict) and (p.get("slug") or "").lower() in ("about-us", "about"):
            about_url = p.get("url") or about_url
            break
    right_links.append((about_url, "About"))

    left_html = "".join(f'<a href="{html_module.escape(u)}" class="ht9-link">{html_module.escape(l)}</a>' for u, l in left_links)
    right_html = "".join(f'<a href="{html_module.escape(u)}" class="ht9-link">{html_module.escape(l)}</a>' for u, l in right_links)
    all_links = left_links + right_links
    mobile_html = "".join(f'<a href="{html_module.escape(u)}" class="ht9-mob-link">{html_module.escape(l)}</a>' for u, l in all_links)

    html_content = f"""
<header class="site-header dp-t9-header">
  <div class="ht9-top">
    <div class="ht9-top-inner">
      <span class="ht9-tagline">Recipes crafted with love &amp; care</span>
      <div class="ht9-top-links">
        <a href="{html_module.escape(about_url)}" class="ht9-top-link">About</a>
        <a href="{html_module.escape(base_url)}/contact-us" class="ht9-top-link">Contact</a>
      </div>
    </div>
  </div>
  <nav class="ht9-nav">
    <div class="ht9-nav-inner">
      <div class="ht9-left">{left_html}</div>
      <a href="{html_module.escape(base_url or '/')}" class="ht9-logo">
        <span class="ht9-logo-icon">&#127858;</span>
        <span class="ht9-logo-name">{name}</span>
      </a>
      <div class="ht9-right">{right_html}</div>
      <button class="ht9-burger" aria-label="Menu" onclick="this.closest('.dp-t9-header').querySelector('.ht9-mobile').style.display=this.closest('.dp-t9-header').querySelector('.ht9-mobile').style.display==='none'?'block':'none'">
        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
    </div>
  </nav>
  <div class="ht9-mobile" style="display:none;">{mobile_html}</div>
</header>
"""

    css = f"""
{t['font_import']}
.dp-t9-header {{ {t['css_vars']} position: sticky; top: 0; z-index: 50; }}
.ht9-top {{
    background: var(--surface2); color: var(--muted); font-size: 0.78rem;
    border-bottom: 1px solid var(--border);
}}
.ht9-top-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0.4rem 1.5rem;
    display: flex; justify-content: space-between; align-items: center;
}}
.ht9-tagline {{ color: var(--muted); font-style: italic; font-family: {ff}; }}
.ht9-top-links {{ display: flex; gap: 1rem; }}
.ht9-top-link {{ color: var(--muted); text-decoration: none; font-size: 0.78rem; transition: color 0.2s; }}
.ht9-top-link:hover {{ color: var(--primary); }}

.ht9-nav {{ border-bottom: 1px solid var(--border); background: var(--bg); box-shadow: 0 2px 12px rgba(44,36,22,0.05); }}
.ht9-nav-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; align-items: center; justify-content: center; height: 76px; gap: 2rem;
}}
.ht9-left, .ht9-right {{ display: flex; gap: 1.5rem; flex: 1; }}
.ht9-left {{ justify-content: flex-end; }}
.ht9-right {{ justify-content: flex-start; }}
.ht9-link {{
    text-decoration: none; color: var(--text); font-weight: 500;
    font-size: 0.9rem; letter-spacing: 0.02em;
    transition: color 0.2s; white-space: nowrap;
    position: relative; padding-bottom: 2px;
}}
.ht9-link::after {{
    content: ''; position: absolute; bottom: -2px; left: 0; right: 0; height: 1.5px;
    background: var(--primary); transform: scaleX(0); transition: transform 0.25s ease;
}}
.ht9-link:hover {{ color: var(--primary); }}
.ht9-link:hover::after {{ transform: scaleX(1); }}
.ht9-logo {{
    display: flex; flex-direction: column; align-items: center;
    text-decoration: none; color: var(--text); flex-shrink: 0;
    transition: opacity 0.2s;
}}
.ht9-logo:hover {{ opacity: 0.85; }}
.ht9-logo-icon {{ font-size: 1.5rem; margin-bottom: 0.1rem; }}
.ht9-logo-name {{ font-family: {ff}; font-size: 1.35rem; font-weight: 700; letter-spacing: 0.01em; }}
.ht9-burger {{ display: none; background: none; border: none; color: var(--text); cursor: pointer; padding: 0.5rem; }}
.ht9-mobile {{ background: var(--bg); border-bottom: 1px solid var(--border); padding: 0.5rem 0; }}
.ht9-mob-link {{
    display: block; padding: 0.75rem 1.5rem; text-decoration: none;
    color: var(--text); font-weight: 500; transition: background 0.2s;
}}
.ht9-mob-link:hover {{ background: var(--gold-light); color: var(--primary); }}
@media (max-width: 768px) {{
    .ht9-top {{ display: none; }}
    .ht9-left, .ht9-right {{ display: none; }}
    .ht9-nav-inner {{ justify-content: space-between; }}
    .ht9-burger {{ display: block; }}
    .ht9-logo {{ flex-direction: row; gap: 0.5rem; }}
}}
"""
    return {"html": html_content, "css": css}
