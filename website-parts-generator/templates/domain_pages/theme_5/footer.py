"""Footer for Theme 7 — Midnight Luxe.
3-column grid on dark gradient, gold accent details, matching header palette.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-footer"


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
    year = datetime.now().year

    # ── Explore links ────────────────────────────────────────────────
    explore_links = [
        {"name": "Home", "url": base_url},
        {"name": "Recipes", "url": f"{base_url}recipes/"},
        {"name": "About", "url": f"{base_url}about/"},
    ]
    for pg in domain_pages:
        explore_links.append({
            "name": html_module.escape(pg.get("name", "")),
            "url": html_module.escape(pg.get("url", "#")),
        })
    explore_html = ""
    for lnk in explore_links:
        explore_html += f'<a class="t7-ftr-link" href="{lnk["url"]}">{lnk["name"]}</a>\n'

    # ── Category links ───────────────────────────────────────────────
    cats_html = ""
    for cat in categories:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url", "#"))
        cats_html += f'<a class="t7-ftr-link" href="{c_url}">{c_name}</a>\n'

    html_content = f"""
<footer class="dp-t7-footer">
  <div class="t7-ftr-inner">
    <div class="t7-ftr-grid">
      <!-- Col 1: Brand -->
      <div class="t7-ftr-col">
        <a class="t7-ftr-logo" href="{base_url}">{domain_name}</a>
        <p class="t7-ftr-tagline">Curated recipes &amp; culinary inspiration, crafted with love.</p>
        <div class="t7-ftr-gold-rule"></div>
      </div>
      <!-- Col 2: Explore -->
      <div class="t7-ftr-col">
        <h4 class="t7-ftr-heading">Explore</h4>
        <nav class="t7-ftr-links">
          {explore_html}
        </nav>
      </div>
      <!-- Col 3: Categories -->
      <div class="t7-ftr-col">
        <h4 class="t7-ftr-heading">Categories</h4>
        <nav class="t7-ftr-links">
          {cats_html}
        </nav>
      </div>
    </div>
    <!-- Bottom bar -->
    <div class="t7-ftr-bottom">
      <span>&copy; {year} {domain_name}. All rights reserved.</span>
    </div>
  </div>
</footer>
"""

    css_content = f"""
{font_import}
{ROOT} {{
    {css_vars}
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: rgba(255,255,255,.82);
    padding: 64px 32px 0;
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} .t7-ftr-inner {{
    max-width: 1140px;
    margin: 0 auto;
}}
/* ── Grid ─────────────────────────────────────────── */
{ROOT} .t7-ftr-grid {{
    display: grid;
    grid-template-columns: 1.4fr 1fr 1fr;
    gap: 48px;
    padding-bottom: 48px;
}}
/* ── Brand column ─────────────────────────────────── */
{ROOT} .t7-ftr-logo {{
    font-family: {font_family};
    font-size: 1.4rem;
    font-weight: 800;
    color: #fff;
    text-decoration: none;
    display: inline-block;
    margin-bottom: 12px;
    letter-spacing: .5px;
}}
{ROOT} .t7-ftr-logo:hover {{ color: var(--gold); }}
{ROOT} .t7-ftr-tagline {{
    font-size: .88rem;
    color: rgba(255,255,255,.6);
    line-height: 1.6;
    margin: 0 0 18px;
}}
{ROOT} .t7-ftr-gold-rule {{
    width: 40px;
    height: 3px;
    background: var(--gold);
    border-radius: 2px;
}}
/* ── Column heading ───────────────────────────────── */
{ROOT} .t7-ftr-heading {{
    font-family: {font_family};
    font-size: .78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--gold);
    margin: 0 0 18px;
}}
/* ── Links ────────────────────────────────────────── */
{ROOT} .t7-ftr-links {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
{ROOT} .t7-ftr-link {{
    color: rgba(255,255,255,.7);
    text-decoration: none;
    font-size: .88rem;
    transition: color .3s, padding-left .3s;
}}
{ROOT} .t7-ftr-link:hover {{
    color: #fff;
    padding-left: 4px;
}}
/* ── Bottom bar ───────────────────────────────────── */
{ROOT} .t7-ftr-bottom {{
    border-top: 1px solid rgba(255,255,255,.1);
    padding: 20px 0;
    text-align: center;
    font-size: .78rem;
    color: rgba(255,255,255,.45);
}}
/* ── Responsive ───────────────────────────────────── */
@media (max-width: 768px) {{
    {ROOT} {{ padding: 48px 20px 0; }}
    {ROOT} .t7-ftr-grid {{
        grid-template-columns: 1fr;
        gap: 36px;
        text-align: center;
    }}
    {ROOT} .t7-ftr-gold-rule {{ margin: 0 auto; }}
    {ROOT} .t7-ftr-links {{ align-items: center; }}
}}
@media (max-width: 600px) {{
    {ROOT} {{ padding: 40px 16px 0; }}
    {ROOT} .t7-ftr-grid {{ gap: 28px; padding-bottom: 36px; }}
}}
"""
    return {"html": html_content, "css": css_content}
