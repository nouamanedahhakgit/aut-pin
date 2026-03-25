"""Theme 11 — Header: Art Deco — obsidian bar with gold accent line, centered logo, symmetrical nav."""
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
        f'<a href="{html_module.escape(u)}" class="ht11-link">{html_module.escape(l)}</a>'
        for u, l in nav_links
    )
    mobile_links = "".join(
        f'<a href="{html_module.escape(u)}" class="ht11-mob-link">{html_module.escape(l)}</a>'
        for u, l in nav_links + [(about_url, "About")]
    )

    html_content = f"""
<header class="site-header dp-t11-header">
  <div class="ht11-gold-strip"></div>
  <div class="ht11-inner">
    <a href="{html_module.escape(base_url or '/')}" class="ht11-logo">
      <span class="ht11-logo-diamond">&#9670;</span>
      <span class="ht11-logo-name">{name}</span>
    </a>
    <nav class="ht11-nav">
      <span class="ht11-nav-ornament">&#9671;</span>
      {links_html}
      <span class="ht11-nav-ornament">&#9671;</span>
    </nav>
    <div class="ht11-actions">
      <a href="{html_module.escape(about_url)}" class="ht11-about-link">About</a>
      <a href="{html_module.escape(base_url)}/contact-us" class="ht11-cta">Contact Us</a>
      <button class="ht11-burger" aria-label="Menu"
        onclick="document.querySelector('.ht11-mobile').style.display=document.querySelector('.ht11-mobile').style.display==='flex'?'none':'flex'">
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
    </div>
  </div>
  <div class="ht11-mobile">{mobile_links}</div>
</header>
"""

    css = f"""
{t['font_import']}
.dp-t11-header {{
    {t['css_vars']}
    position: sticky; top: 0; z-index: 100;
    background: var(--primary);
}}
.ht11-gold-strip {{
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}}
.ht11-inner {{
    max-width: 1200px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; align-items: center; height: 64px; gap: 1.5rem;
}}
.ht11-logo {{
    display: flex; align-items: center; gap: 8px;
    text-decoration: none; color: var(--text-on-primary); flex-shrink: 0;
}}
.ht11-logo-diamond {{
    color: var(--gold); font-size: 1.1rem;
}}
.ht11-logo-name {{
    font-family: {ff}; font-size: 1.15rem; font-weight: 700;
    letter-spacing: 0.04em;
}}
.ht11-nav {{
    display: flex; align-items: center; gap: 0.2rem; flex: 1;
    justify-content: center;
}}
.ht11-nav-ornament {{
    color: var(--gold); font-size: 0.5rem; opacity: 0.5; margin: 0 0.5rem;
}}
.ht11-link {{
    text-decoration: none; color: var(--text-on-primary-muted); font-size: 0.78rem;
    font-weight: 500; padding: 0.4rem 0.9rem;
    text-transform: uppercase; letter-spacing: 0.12em;
    transition: all 0.25s; white-space: nowrap;
}}
.ht11-link:hover {{ color: var(--gold); }}
.ht11-actions {{ display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }}
.ht11-about-link {{
    text-decoration: none; color: var(--text-on-primary-muted); font-size: 0.78rem;
    font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em;
    transition: color 0.25s;
}}
.ht11-about-link:hover {{ color: var(--gold); }}
.ht11-cta {{
    display: inline-flex; align-items: center;
    background: transparent; color: var(--gold); padding: 0.5rem 1.2rem;
    border: 1.5px solid var(--gold); text-decoration: none; font-weight: 600;
    font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.12em;
    transition: all 0.3s; white-space: nowrap;
}}
.ht11-cta:hover {{ background: var(--gold); color: var(--primary); }}
.ht11-burger {{ display: none; background: none; border: none; cursor: pointer; color: var(--text-on-primary); padding: 4px; }}
.ht11-mobile {{
    display: none; flex-direction: column; background: var(--primary);
    border-top: 1px solid var(--gold-light); padding: 0.75rem 1.5rem;
}}
.ht11-mob-link {{
    display: block; padding: 0.7rem 0.5rem; text-decoration: none;
    color: var(--text-on-primary); font-weight: 500; font-size: 0.88rem;
    text-transform: uppercase; letter-spacing: 0.08em;
    border-bottom: 1px solid var(--gold-light); transition: color 0.2s;
}}
.ht11-mob-link:last-child {{ border-bottom: none; }}
.ht11-mob-link:hover {{ color: var(--gold); }}
@media (max-width: 768px) {{
    .ht11-nav {{ display: none; }}
    .ht11-about-link {{ display: none; }}
    .ht11-burger {{ display: block; }}
    .ht11-cta {{ display: none; }}
}}
"""
    return {"html": html_content, "css": css}
