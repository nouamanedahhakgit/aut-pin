"""Header for Theme 7 — Midnight Luxe.
Sticky dark-gradient navbar with gold accent hover, burger for mobile.
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
        {"name": "Recipes", "url": f"{base_url}recipes/"},
    ]
    cats_with_recipes = [cat for cat in categories if int(cat.get("count", 0) or 0) > 0]
    for cat in cats_with_recipes[:3]:
        nav_links.append({
            "name": html_module.escape(cat.get("name", "")),
            "url": html_module.escape(cat.get("url", "#")),
        })
    # About / Contact from domain_pages
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
        links_html += f'<a class="t7-hdr-link" href="{lnk["url"]}">{lnk["name"]}</a>\n'
        mobile_links += f'<a class="t7-mob-link" href="{lnk["url"]}">{lnk["name"]}</a>\n'

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
    z-index: 50;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    border-bottom: 1px solid rgba(212,168,83,.18);
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} .t7-hdr-inner {{
    max-width: 1140px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    height: 64px;
}}
/* ── Logo ─────────────────────────────────────────── */
{ROOT} .t7-hdr-logo {{
    font-family: {font_family};
    font-size: 1.3rem;
    font-weight: 800;
    color: #fff;
    text-decoration: none;
    letter-spacing: .5px;
    white-space: nowrap;
}}
{ROOT} .t7-hdr-logo:hover {{ color: var(--gold); }}
/* ── Desktop nav ──────────────────────────────────── */
{ROOT} .t7-hdr-nav {{
    display: flex;
    align-items: center;
    gap: 6px;
}}
{ROOT} .t7-hdr-link {{
    color: rgba(255,255,255,.82);
    text-decoration: none;
    font-size: .82rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: var(--radius);
    transition: color .3s, background .3s;
    letter-spacing: .4px;
}}
{ROOT} .t7-hdr-link:hover {{
    color: #fff;
    background: rgba(212,168,83,.15);
}}
/* ── Burger ────────────────────────────────────────── */
{ROOT} .t7-hdr-burger {{
    display: none;
    flex-direction: column;
    gap: 5px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
}}
{ROOT} .t7-hdr-burger span {{
    display: block;
    width: 24px;
    height: 2px;
    background: #fff;
    border-radius: 1px;
    transition: transform .3s, opacity .3s;
}}
{ROOT} .t7-burger-active span:nth-child(1) {{ transform: translateY(7px) rotate(45deg); }}
{ROOT} .t7-burger-active span:nth-child(2) {{ opacity: 0; }}
{ROOT} .t7-burger-active span:nth-child(3) {{ transform: translateY(-7px) rotate(-45deg); }}
/* ── Mobile overlay ───────────────────────────────── */
{ROOT} .t7-mob-overlay {{
    display: none;
    position: absolute;
    top: 64px;
    left: 0; right: 0;
    background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%);
    padding: 0;
    max-height: 0;
    overflow: hidden;
    transition: max-height .4s ease, padding .4s ease;
}}
{ROOT} .t7-mob-overlay.t7-mob-open {{
    max-height: 500px;
    padding: 16px 0 24px;
}}
{ROOT} .t7-mob-body {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}}
{ROOT} .t7-mob-link {{
    color: rgba(255,255,255,.85);
    text-decoration: none;
    font-size: .92rem;
    font-weight: 600;
    padding: 10px 24px;
    border-radius: var(--radius);
    transition: color .3s, background .3s;
    width: 80%;
    text-align: center;
}}
{ROOT} .t7-mob-link:hover {{
    background: rgba(212,168,83,.12);
    color: #fff;
}}
/* ── Responsive ───────────────────────────────────── */
@media (max-width: 768px) {{
    {ROOT} .t7-hdr-nav {{ display: none; }}
    {ROOT} .t7-hdr-burger {{ display: flex; }}
    {ROOT} .t7-mob-overlay {{ display: block; }}
    {ROOT} .t7-hdr-inner {{ padding: 0 20px; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t7-hdr-inner {{ height: 56px; }}
    {ROOT} .t7-mob-overlay {{ top: 56px; }}
    {ROOT} .t7-hdr-logo {{ font-size: 1.1rem; }}
}}
"""
    return {"html": html_content, "css": css_content}
