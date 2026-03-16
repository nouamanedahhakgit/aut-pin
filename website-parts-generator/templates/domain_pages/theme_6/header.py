"""Header for Theme 6 — Neo-Brutalist.
Bold navbar with thick black borders, high-contrast hover effects, 
and 4px solid borders on the mobile menu button.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module

ROOT = ".dp-t6-header"

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
        {"name": "Recipes", "url": f"{base_url}recipes/"},
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
        links_html += f'<a class="t6-hdr-link" href="{lnk["url"]}">{lnk["name"]}</a>'
        mobile_links += f'<a class="t6-mob-link" href="{lnk["url"]}">{lnk["name"]}</a>'

    html_content = f"""
<header class="dp-t6-header">
  <div class="t6-hdr-inner">
    <a class="t6-hdr-logo" href="{base_url}">{domain_name}</a>
    <nav class="t6-hdr-nav">
      {links_html}
    </nav>
    <button class="t6-hdr-burger" aria-label="Open menu" onclick="(function(b){{var m=b.closest('.dp-t6-header').querySelector('.t6-mob-overlay');m.classList.toggle('t6-mob-open');b.classList.toggle('t6-burger-active')}})(this)">
      <span></span><span></span><span></span>
    </button>
  </div>
  <div class="t6-mob-overlay">
    <div class="t6-mob-body">
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
    background: #fff;
    border-bottom: var(--border-width) solid var(--border);
    padding: 10px 0;
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} .t6-hdr-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    height: 70px;
}}
{ROOT} .t6-hdr-logo {{
    font-family: {font_family};
    font-size: 1.8rem;
    font-weight: 900;
    color: #000;
    text-decoration: none;
    text-transform: uppercase;
    letter-spacing: -1.5px;
    background: var(--primary);
    padding: 4px 12px;
    border: var(--border-width) solid var(--border);
    box-shadow: 4px 4px 0px #000;
}}
{ROOT} .t6-hdr-logo:active {{
    transform: translate(2px, 2px);
    box-shadow: 1px 1px 0px #000;
}}
{ROOT} .t6-hdr-nav {{
    display: flex;
    align-items: center;
    gap: 15px;
}}
{ROOT} .t6-hdr-link {{
    color: #000;
    text-decoration: none;
    font-size: 1rem;
    font-weight: 900;
    padding: 8px 16px;
    border: var(--border-width) solid transparent;
    text-transform: uppercase;
    transition: all 0.1s;
}}
{ROOT} .t6-hdr-link:hover {{
    background: var(--secondary);
    color: #fff;
    border-color: #000;
    box-shadow: 4px 4px 0px #000;
}}
{ROOT} .t6-hdr-burger {{
    display: none;
    flex-direction: column;
    gap: 6px;
    background: #fff;
    border: var(--border-width) solid var(--border);
    cursor: pointer;
    box-shadow: 4px 4px 0px #000;
    padding: 10px;
}}
{ROOT} .t6-hdr-burger span {{
    display: block;
    width: 25px;
    height: 4px;
    background: #000;
}}
{ROOT} .t6-burger-active {{
    transform: translate(2px, 2px);
    box-shadow: 1px 1px 0px #000;
}}
{ROOT} .t6-mob-overlay {{
    display: none;
    position: absolute;
    top: 86px;
    left: 40px; right: 40px;
    background: #fff;
    border: var(--border-width) solid var(--border);
    box-shadow: var(--shadow);
    padding: 20px 0;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}}
{ROOT} .t6-mob-overlay.t6-mob-open {{
    max-height: 500px;
    display: block;
}}
{ROOT} .t6-mob-body {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}}
{ROOT} .t6-mob-link {{
    color: #000;
    text-decoration: none;
    font-size: 1.2rem;
    font-weight: 900;
    padding: 12px 24px;
    text-transform: uppercase;
    width: 90%;
    text-align: center;
    border: var(--border-width) solid transparent;
}}
{ROOT} .t6-mob-link:hover {{
    background: var(--primary);
    border-color: #000;
}}
@media (max-width: 992px) {{
    {ROOT} .t6-hdr-nav {{ display: none; }}
    {ROOT} .t6-hdr-burger {{ display: flex; }}
    {ROOT} .t6-hdr-inner {{ padding: 0 20px; }}
    {ROOT} .t6-mob-overlay {{ left: 20px; right: 20px; top: 80px; }}
}}
"""
    return {"html": html_content, "css": css_content}
