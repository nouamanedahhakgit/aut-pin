"""Theme 3 — Header: Dark glassmorphism sticky nav with glow accent line."""
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
    for c in categories[:3]:
        url = html_module.escape(c.get("url") or f"{base_url}/categories")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            nav_links.append((url, cat_name))

    about_url = f"{base_url}/about-us"
    contact_url = f"{base_url}/contact-us"
    for p in config.get("domain_pages") or []:
        if isinstance(p, dict):
            slug = (p.get("slug") or "").lower()
            if slug in ("about-us", "about"):
                about_url = p.get("url") or about_url
            elif slug in ("contact-us", "contact"):
                contact_url = p.get("url") or contact_url
    nav_links.append((about_url, "About"))
    nav_links.append((contact_url, "Contact"))

    desktop_html = "".join(
        f'<a href="{html_module.escape(u)}" class="ht3-link">{html_module.escape(l)}</a>'
        for u, l in nav_links
    )
    mobile_html = "".join(
        f'<a href="{html_module.escape(u)}" class="ht3-mob-link">{html_module.escape(l)}</a>'
        for u, l in nav_links
    )

    html_content = f"""
<header class="site-header dp-t3-header">
  <div class="ht3-glow-line"></div>
  <nav class="ht3-nav">
    <div class="ht3-nav-inner">
      <a href="{html_module.escape(base_url or '/')}" class="ht3-logo">
        <span class="ht3-logo-icon">&#127860;</span>
        <span class="ht3-logo-name">{name}</span>
      </a>
      <div class="ht3-links">{desktop_html}</div>
      <button class="ht3-burger" aria-label="Menu" onclick="this.closest('.dp-t3-header').querySelector('.ht3-mobile').style.display=this.closest('.dp-t3-header').querySelector('.ht3-mobile').style.display==='none'?'flex':'none'">
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
    </div>
  </nav>
  <div class="ht3-mobile" style="display:none;">{mobile_html}</div>
</header>
"""

    css = f"""
{t['font_import']}
.dp-t3-header {{ {t['css_vars']} position: sticky; top: 0; z-index: 50; }}
.ht3-glow-line {{
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--primary));
    box-shadow: 0 0 12px color-mix(in srgb, var(--primary) 40%, transparent);
}}
.ht3-nav {{
    background: color-mix(in srgb, var(--bg) 85%, transparent);
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--glass-border);
}}
.ht3-nav-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; align-items: center; justify-content: space-between; height: 64px;
}}
.ht3-logo {{
    display: flex; align-items: center; gap: 0.6rem;
    text-decoration: none; color: var(--text); flex-shrink: 0;
}}
.ht3-logo-icon {{ font-size: 1.3rem; }}
.ht3-logo-name {{
    font-family: {ff}; font-size: 1.25rem; font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.ht3-links {{ display: flex; gap: 1.5rem; align-items: center; }}
.ht3-link {{
    text-decoration: none; color: var(--muted); font-weight: 500;
    font-size: 0.9rem; transition: color 0.25s; white-space: nowrap;
    position: relative;
}}
.ht3-link::after {{
    content: ''; position: absolute; bottom: -4px; left: 0; width: 0; height: 2px;
    background: var(--primary); transition: width 0.3s;
    box-shadow: 0 0 6px color-mix(in srgb, var(--primary) 40%, transparent);
}}
.ht3-link:hover {{ color: var(--text); }}
.ht3-link:hover::after {{ width: 100%; }}
.ht3-burger {{
    display: none; background: none; border: 1px solid var(--glass-border);
    border-radius: 8px; color: var(--text); cursor: pointer; padding: 0.4rem;
}}
.ht3-mobile {{
    background: color-mix(in srgb, var(--bg) 95%, transparent);
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--glass-border);
    flex-direction: column; padding: 0.5rem 0;
}}
.ht3-mob-link {{
    display: block; padding: 0.75rem 1.5rem; text-decoration: none;
    color: var(--muted); font-weight: 500; font-size: 0.95rem;
    transition: all 0.2s; border-left: 2px solid transparent;
}}
.ht3-mob-link:hover {{
    color: var(--text); background: var(--glass);
    border-left-color: var(--primary);
}}
@media (max-width: 768px) {{
    .ht3-links {{ display: none; }}
    .ht3-burger {{ display: flex; }}
}}
"""
    return {"html": html_content, "css": css}
