"""Theme 10 — Header: Minimal white sticky bar, pill-nav links, mint CTA button."""
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
    # Only show categories that actually have recipes (count > 0)
    cats_with_recipes = [c for c in categories if int(c.get("count", 0) or 0) > 0]
    for c in cats_with_recipes[:3]:
        url = html_module.escape(c.get("url") or f"{base_url}/categories")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            nav_links.append((url, cat_name))
    if len(nav_links) < 4:
        nav_links.append((f"{base_url}/categories", "Categories"))

    about_url = f"{base_url}/about-us"
    for p in config.get("domain_pages") or []:
        if isinstance(p, dict) and (p.get("slug") or "").lower() in ("about-us", "about"):
            about_url = p.get("url") or about_url
            break

    links_html = "".join(
        f'<a href="{html_module.escape(u)}" class="ht10-link">{html_module.escape(l)}</a>'
        for u, l in nav_links
    )
    mobile_links = "".join(
        f'<a href="{html_module.escape(u)}" class="ht10-mob-link">{html_module.escape(l)}</a>'
        for u, l in nav_links + [(about_url, "About")]
    )

    html_content = f"""
<header class="site-header dp-t10-header">
  <div class="ht10-inner">
    <a href="{html_module.escape(base_url or '/')}" class="ht10-logo">
      <span class="ht10-logo-dot"></span>
      <span class="ht10-logo-name">{name}</span>
    </a>
    <nav class="ht10-nav">{links_html}</nav>
    <div class="ht10-actions">
      <a href="{html_module.escape(about_url)}" class="ht10-about-link">About</a>
      <a href="{html_module.escape(base_url)}/contact-us" class="ht10-cta">Get in Touch</a>
      <button class="ht10-burger" aria-label="Menu"
        onclick="document.querySelector('.ht10-mobile').style.display=document.querySelector('.ht10-mobile').style.display==='flex'?'none':'flex'">
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
    </div>
  </div>
  <div class="ht10-mobile">{mobile_links}</div>
</header>
"""

    css = f"""
{t['font_import']}
.dp-t10-header {{
    {t['css_vars']}
    position: sticky; top: 0; z-index: 100;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
}}
.ht10-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; align-items: center; height: 68px; gap: 1.5rem;
}}
.ht10-logo {{
    display: flex; align-items: center; gap: 8px;
    text-decoration: none; color: var(--text); flex-shrink: 0;
}}
.ht10-logo-dot {{
    width: 28px; height: 28px; border-radius: 8px;
    background: var(--primary); flex-shrink: 0;
}}
.ht10-logo-name {{ font-family: {ff}; font-size: 1.25rem; font-weight: 700; font-style: italic; }}
.ht10-nav {{ display: flex; align-items: center; gap: 0.25rem; flex: 1; padding-left: 1.5rem; }}
.ht10-link {{
    text-decoration: none; color: var(--muted); font-size: 0.88rem; font-weight: 500;
    padding: 0.4rem 0.9rem; border-radius: 50px; transition: all 0.2s;
    white-space: nowrap;
}}
.ht10-link:hover {{ color: var(--text); background: var(--border); }}
.ht10-actions {{ display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }}
.ht10-about-link {{
    text-decoration: none; color: var(--muted); font-size: 0.88rem; font-weight: 500;
    transition: color 0.2s;
}}
.ht10-about-link:hover {{ color: var(--primary); }}
.ht10-cta {{
    display: inline-flex; align-items: center;
    background: var(--primary); color: #fff; padding: 0.55rem 1.25rem;
    border-radius: 50px; text-decoration: none; font-weight: 600; font-size: 0.85rem;
    transition: all 0.25s; white-space: nowrap;
    box-shadow: 0 2px 12px rgba(0,191,165,0.3);
}}
.ht10-cta:hover {{ transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0,191,165,0.45); }}
.ht10-burger {{ display: none; background: none; border: none; cursor: pointer; color: var(--text); padding: 4px; }}
.ht10-mobile {{
    display: none; flex-direction: column;
    border-top: 1px solid var(--border); padding: 0.75rem 1.5rem;
}}
.ht10-mob-link {{
    display: block; padding: 0.7rem 0.5rem; text-decoration: none;
    color: var(--text); font-weight: 500; font-size: 0.95rem;
    border-bottom: 1px solid var(--border); transition: color 0.2s;
}}
.ht10-mob-link:last-child {{ border-bottom: none; }}
.ht10-mob-link:hover {{ color: var(--primary); }}
@media (max-width: 768px) {{
    .ht10-nav {{ display: none; }}
    .ht10-about-link {{ display: none; }}
    .ht10-burger {{ display: block; }}
    .ht10-cta {{ display: none; }}
}}
"""
    return {"html": html_content, "css": css}
