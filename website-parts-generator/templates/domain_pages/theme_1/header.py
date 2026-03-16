"""Theme 1 — Header: Warm gradient top bar, centered logo, split navigation."""
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

    left_html = "".join(f'<a href="{html_module.escape(u)}" class="ht1-link">{html_module.escape(l)}</a>' for u, l in left_links)
    right_html = "".join(f'<a href="{html_module.escape(u)}" class="ht1-link">{html_module.escape(l)}</a>' for u, l in right_links)
    all_links = left_links + right_links
    mobile_html = "".join(f'<a href="{html_module.escape(u)}" class="ht1-mob-link">{html_module.escape(l)}</a>' for u, l in all_links)

    html_content = f"""
<header class="site-header dp-t1-header">
  <div class="ht1-top">
    <div class="ht1-top-inner">
      <span class="ht1-tagline">Delicious recipes for every occasion</span>
      <div class="ht1-top-links">
        <a href="{html_module.escape(about_url)}" class="ht1-top-link">About</a>
        <a href="{html_module.escape(base_url)}/contact-us" class="ht1-top-link">Contact</a>
      </div>
    </div>
  </div>
  <nav class="ht1-nav">
    <div class="ht1-nav-inner">
      <div class="ht1-left">{left_html}</div>
      <a href="{html_module.escape(base_url or '/')}" class="ht1-logo">
        <span class="ht1-logo-icon">&#127860;</span>
        <span class="ht1-logo-name">{name}</span>
      </a>
      <div class="ht1-right">{right_html}</div>
      <button class="ht1-burger" aria-label="Menu" onclick="this.closest('.dp-t1-header').querySelector('.ht1-mobile').style.display=this.closest('.dp-t1-header').querySelector('.ht1-mobile').style.display==='none'?'block':'none'">
        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
    </div>
  </nav>
  <div class="ht1-mobile" style="display:none;">{mobile_html}</div>
</header>
"""

    css = f"""
{t['font_import']}
.dp-t1-header {{ {t['css_vars']} position: sticky; top: 0; z-index: 50; }}
.ht1-top {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; font-size: 0.8rem;
}}
.ht1-top-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0.4rem 1.5rem;
    display: flex; justify-content: space-between; align-items: center;
}}
.ht1-tagline {{ opacity: 0.9; }}
.ht1-top-links {{ display: flex; gap: 1rem; }}
.ht1-top-link {{ color: #fff; text-decoration: none; opacity: 0.85; transition: opacity 0.2s; }}
.ht1-top-link:hover {{ opacity: 1; }}

.ht1-nav {{ border-bottom: 1px solid var(--border); background: var(--bg); }}
.ht1-nav-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; align-items: center; justify-content: center; height: 72px; gap: 2rem;
}}
.ht1-left, .ht1-right {{ display: flex; gap: 1.5rem; flex: 1; }}
.ht1-left {{ justify-content: flex-end; }}
.ht1-right {{ justify-content: flex-start; }}
.ht1-link {{
    text-decoration: none; color: var(--text); font-weight: 600;
    font-size: 0.95rem; transition: color 0.2s; white-space: nowrap;
}}
.ht1-link:hover {{ color: var(--primary); }}
.ht1-logo {{
    display: flex; flex-direction: column; align-items: center;
    text-decoration: none; color: var(--text); flex-shrink: 0;
}}
.ht1-logo-icon {{ font-size: 1.4rem; margin-bottom: 0.15rem; }}
.ht1-logo-name {{ font-family: {ff}; font-size: 1.3rem; font-weight: 700; }}
.ht1-burger {{ display: none; background: none; border: none; color: var(--text); cursor: pointer; padding: 0.5rem; }}
.ht1-mobile {{ background: var(--bg); border-bottom: 1px solid var(--border); padding: 0.5rem 0; }}
.ht1-mob-link {{
    display: block; padding: 0.75rem 1.5rem; text-decoration: none;
    color: var(--text); font-weight: 600; transition: background 0.2s;
}}
.ht1-mob-link:hover {{ background: color-mix(in srgb, var(--primary) 8%, transparent); color: var(--primary); }}
@media (max-width: 768px) {{
    .ht1-top {{ display: none; }}
    .ht1-left, .ht1-right {{ display: none; }}
    .ht1-nav-inner {{ justify-content: space-between; }}
    .ht1-burger {{ display: block; }}
    .ht1-logo {{ flex-direction: row; gap: 0.5rem; }}
}}
"""
    return {"html": html_content, "css": css}
