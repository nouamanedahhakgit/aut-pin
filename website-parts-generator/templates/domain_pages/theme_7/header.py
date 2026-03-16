"""Header for Theme 7 — Minimalist Glass.
Elegant, transparent sticky navbar with subtle blur effect (glassmorphism).
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module

ROOT = ".dp-t7-header"

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

    # ── Nav links ────────────────────────────────────────────────────
    nav_links = [
        {"name": "Home", "url": base_url},
    ]
    cats_with_recipes = [cat for cat in categories if int(cat.get("count", 0) or 0) > 0]
    for cat in cats_with_recipes[:3]:
        nav_links.append({
            "name": html_module.escape(cat.get("name", "")),
            "url": html_module.escape(cat.get("url", "#")),
        })
    for pg in domain_pages:
        slug = (pg.get("slug") or "").lower()
        if slug in ("about", "contact"):
            nav_links.append({
                "name": html_module.escape(pg.get("name", slug.title())),
                "url": html_module.escape(pg.get("url", "#")),
            })

    links_html = ""
    mobile_links = ""
    for lnk in nav_links:
        links_html += f'<a class="t7-hdr-link" href="{lnk["url"]}">{lnk["name"]}</a>'
        mobile_links += f'<a class="t7-mob-link" href="{lnk["url"]}">{lnk["name"]}</a>'

    html_content = f"""
<header class="dp-t7-header">
  <div class="t7-hdr-inner">
    <a class="t7-hdr-logo" href="{base_url}">{domain_name}</a>
    <nav class="t7-hdr-nav">
      {links_html}
    </nav>
    <button class="t7-hdr-burger" aria-label="Open menu" onclick="(function(b){{var m=b.closest('.dp-t7-header').querySelector('.t7-mob-overlay');m.classList.toggle('t7-mob-open');b.classList.toggle('t7-burger-active')}})(this)">
      <span></span><span></span><span></span>
    </button>
  </div>
  <div class="t7-mob-overlay">
    <div class="t7-mob-body">
      {mobile_links}
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
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding: 15px 0;
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} .t7-hdr-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    height: 60px;
}}
{ROOT} .t7-hdr-logo {{
    font-family: {font_family};
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--primary);
    text-decoration: none;
    letter-spacing: -0.01em;
}}
{ROOT} .t7-hdr-nav {{
    display: flex;
    align-items: center;
    gap: 20px;
}}
{ROOT} .t7-hdr-link {{
    color: var(--muted);
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 400;
    letter-spacing: 0.05em;
    padding: 8px 16px;
    border-radius: 50px;
    transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
}}
{ROOT} .t7-hdr-link:hover {{
    background: rgba(44, 62, 80, 0.05);
    color: var(--primary);
}}
{ROOT} .t7-hdr-burger {{
    display: none;
    flex-direction: column;
    gap: 6px;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 5px;
}}
{ROOT} .t7-hdr-burger span {{
    display: block;
    width: 25px;
    height: 1.5px;
    background: var(--primary);
    transition: all 0.3s ease;
}}
{ROOT} .t7-burger-active span:nth-child(1) {{ transform: translateY(7.5px) rotate(45deg); }}
{ROOT} .t7-burger-active span:nth-child(2) {{ opacity: 0; }}
{ROOT} .t7-burger-active span:nth-child(3) {{ transform: translateY(-7.5px) rotate(-45deg); }}

{ROOT} .t7-mob-overlay {{
    display: none;
    position: absolute;
    top: 90px;
    left: 20px; right: 20px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: var(--radius);
    border: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: 0 20px 60px rgba(0,0,0,0.1);
    padding: 40px 0;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease-out;
}}
{ROOT} .t7-mob-overlay.t7-mob-open {{
    max-height: 600px;
    display: block;
}}
{ROOT} .t7-mob-body {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}}
{ROOT} .t7-mob-link {{
    color: var(--primary);
    text-decoration: none;
    font-size: 1.3rem;
    font-weight: 500;
    padding: 12px 30px;
    width: 80%;
    text-align: center;
    border-bottom: 0.5px solid rgba(0,0,0,0.05);
}}
@media (max-width: 900px) {{
    {ROOT} .t7-hdr-nav {{ display: none; }}
    {ROOT} .t7-hdr-burger {{ display: flex; }}
    {ROOT} .t7-hdr-inner {{ padding: 0 20px; }}
}}
"""
    return {"html": html_content, "css": css_content}
