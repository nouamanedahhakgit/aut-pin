"""Header for Theme 8 — Aurora Borealis Dark.
Obsidian sticky navbar with aurora-glow logo, pill-shaped nav links,
and an animated slide-in mobile drawer.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module

ROOT = ".dp-t8-header"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    base_url = html_module.escape(config.get("base_url") or config.get("domain_url", "/"))
    categories = config.get("categories") or []
    domain_pages = config.get("domain_pages") or []

    nav_links = [{"name": "Home", "url": base_url}]
    cats_with_recipes = [cat for cat in categories if int(cat.get("count", 0) or 0) > 0]
    for cat in cats_with_recipes[:3]:
        nav_links.append({
            "name": html_module.escape(cat.get("name", "")),
            "url":  html_module.escape(cat.get("url", "#")),
        })
    for pg in domain_pages:
        slug = (pg.get("slug") or "").lower()
        if slug in ("about", "contact"):
            nav_links.append({
                "name": html_module.escape(pg.get("name", slug.title())),
                "url":  html_module.escape(pg.get("url", "#")),
            })

    links_html  = "".join(f'<a class="t8-hdr-link" href="{lnk["url"]}">{lnk["name"]}</a>' for lnk in nav_links)
    mobile_html = "".join(f'<a class="t8-mob-link" href="{lnk["url"]}">{lnk["name"]}</a>' for lnk in nav_links)

    html_content = f"""
<header class="dp-t8-header">
  <div class="t8-hdr-inner">
    <a class="t8-hdr-logo" href="{base_url}">{domain_name}</a>
    <nav class="t8-hdr-nav" aria-label="Main navigation">
      {links_html}
    </nav>
    <button class="t8-hdr-burger" aria-label="Open menu"
      onclick="(function(b){{var d=b.closest('.dp-t8-header').querySelector('.t8-mob-drawer');d.classList.toggle('t8-mob-open');b.classList.toggle('t8-burger-active')}})(this)">
      <span></span><span></span><span></span>
    </button>
  </div>
  <div class="t8-mob-drawer" role="dialog" aria-label="Mobile navigation">
    <div class="t8-mob-inner">
      {mobile_html}
    </div>
  </div>
</header>
"""

    css_content = f"""
{font_import}
{ROOT} {{
    {css_vars}
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(8, 11, 20, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(124, 58, 237, 0.2);
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} .t8-hdr-inner {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 40px;
    height: 68px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
{ROOT} .t8-hdr-logo {{
    font-family: {font_family};
    font-size: 1.5rem;
    font-weight: 800;
    text-decoration: none;
    background: linear-gradient(135deg, #fff 0%, var(--secondary) 60%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    transition: opacity 0.2s;
}}
{ROOT} .t8-hdr-logo:hover {{ opacity: 0.8; }}
{ROOT} .t8-hdr-nav {{
    display: flex;
    align-items: center;
    gap: 4px;
}}
{ROOT} .t8-hdr-link {{
    color: var(--muted);
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    padding: 8px 18px;
    border-radius: 50px;
    border: 1px solid transparent;
    transition: all 0.25s cubic-bezier(0.165, 0.84, 0.44, 1);
}}
{ROOT} .t8-hdr-link:hover {{
    color: var(--text);
    background: rgba(124,58,237,0.12);
    border-color: rgba(124,58,237,0.25);
}}
{ROOT} .t8-hdr-burger {{
    display: none;
    flex-direction: column;
    gap: 5px;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 8px;
    border-radius: 8px;
}}
{ROOT} .t8-hdr-burger span {{
    display: block;
    width: 24px;
    height: 2px;
    background: var(--text);
    border-radius: 2px;
    transition: all 0.3s ease;
}}
{ROOT} .t8-burger-active span:nth-child(1) {{ transform: translateY(7px) rotate(45deg); }}
{ROOT} .t8-burger-active span:nth-child(2) {{ opacity: 0; }}
{ROOT} .t8-burger-active span:nth-child(3) {{ transform: translateY(-7px) rotate(-45deg); }}

{ROOT} .t8-mob-drawer {{
    display: none;
    position: absolute;
    top: 100%;
    left: 16px; right: 16px;
    background: rgba(15, 22, 36, 0.98);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 20px;
    padding: 32px 24px;
    box-shadow: 0 24px 60px rgba(0,0,0,0.6);
    transform: translateY(-10px);
    opacity: 0;
    transition: transform 0.35s cubic-bezier(0.165,0.84,0.44,1), opacity 0.3s ease;
}}
{ROOT} .t8-mob-drawer.t8-mob-open {{
    display: block;
    transform: translateY(0);
    opacity: 1;
}}
{ROOT} .t8-mob-inner {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
{ROOT} .t8-mob-link {{
    color: var(--muted);
    text-decoration: none;
    font-size: 1.1rem;
    font-weight: 500;
    padding: 14px 20px;
    border-radius: 12px;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}}
{ROOT} .t8-mob-link:hover {{
    color: var(--text);
    background: rgba(124,58,237,0.12);
    border-color: rgba(124,58,237,0.25);
}}
@media (max-width: 900px) {{
    {ROOT} .t8-hdr-nav {{ display: none; }}
    {ROOT} .t8-hdr-burger {{ display: flex; }}
    {ROOT} .t8-hdr-inner {{ padding: 0 20px; }}
}}
"""
    return {"html": html_content, "css": css_content}
