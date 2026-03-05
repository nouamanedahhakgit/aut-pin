"""Theme 2 — Header: Modern clean with accent border-bottom, horizontal nav."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]

    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []

    nav_links = [
        (f"{base_url or '/'}", "Home"),
        (f"{base_url}/recipes", "Recipes"),
    ]
    for c in categories[:4]:
        url = html_module.escape(c.get("url") or f"{base_url}/categories")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            nav_links.append((url, cat_name))

    about_url = f"{base_url}/about-us"
    for p in config.get("domain_pages") or []:
        if isinstance(p, dict) and (p.get("slug") or "").lower() in ("about-us", "about"):
            about_url = p.get("url") or about_url
            break
    nav_links.append((about_url, "About"))
    nav_links.append((f"{base_url}/contact-us", "Contact"))

    links_html = "".join(f'<a href="{html_module.escape(u)}" class="ht2-link">{html_module.escape(l)}</a>' for u, l in nav_links)
    mobile_html = "".join(f'<a href="{html_module.escape(u)}" class="ht2-mob-link">{html_module.escape(l)}</a>' for u, l in nav_links)

    html_content = f"""
<header class="site-header dp-t2-header">
  <div class="ht2-inner">
    <a href="{html_module.escape(base_url or '/')}" class="ht2-logo">{name}</a>
    <nav class="ht2-nav">{links_html}</nav>
    <button class="ht2-burger" aria-label="Menu" onclick="this.closest('.dp-t2-header').querySelector('.ht2-mobile').style.display=this.closest('.dp-t2-header').querySelector('.ht2-mobile').style.display==='none'?'block':'none'">
      <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
  </div>
  <div class="ht2-mobile" style="display:none;">{mobile_html}</div>
</header>
"""

    css = f"""
{t['font_import']}
.dp-t2-header {{ {t['css_vars']} position: sticky; top: 0; z-index: 50; background: var(--bg); border-bottom: 3px solid var(--primary); }}
.ht2-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; align-items: center; height: 64px; gap: 2rem;
}}
.ht2-logo {{
    font-family: {ff}; font-size: 1.4rem; font-weight: 700;
    color: var(--text); text-decoration: none; flex-shrink: 0;
}}
.ht2-nav {{ display: flex; gap: 1.5rem; margin-left: auto; }}
.ht2-link {{
    text-decoration: none; color: var(--muted); font-size: 0.9rem;
    font-weight: 500; transition: color 0.2s; white-space: nowrap;
}}
.ht2-link:hover {{ color: var(--primary); }}
.ht2-burger {{ display: none; background: none; border: none; color: var(--text); cursor: pointer; margin-left: auto; }}
.ht2-mobile {{ background: var(--bg); border-bottom: 1px solid var(--border); padding: 0.5rem 0; }}
.ht2-mob-link {{ display: block; padding: 0.7rem 1.5rem; text-decoration: none; color: var(--text); font-weight: 500; font-size: 0.9rem; transition: background 0.2s; }}
.ht2-mob-link:hover {{ background: color-mix(in srgb, var(--primary) 6%, transparent); color: var(--primary); }}
@media (max-width: 768px) {{
    .ht2-nav {{ display: none; }}
    .ht2-burger {{ display: block; }}
}}
"""
    return {"html": html_content, "css": css}
