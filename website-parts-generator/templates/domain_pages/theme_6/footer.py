"""Footer for Theme 6 — Neo-Brutalist.
Bold footer with thick borders, black background, and high-contrast links.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module
from datetime import datetime

ROOT = ".dp-t6-footer"

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

    # ── Nav groups ──────────────────────────────────────────────────
    cat_links = ""
    for cat in categories[:5]:
        name = html_module.escape(cat.get("name", ""))
        url = html_module.escape(cat.get("url", "#"))
        cat_links += f'<li><a href="{url}">{name}</a></li>'

    legal_links = ""
    for pg in domain_pages:
        name = html_module.escape(pg.get("name", ""))
        url = html_module.escape(pg.get("url", "#"))
        legal_links += f'<li><a href="{url}">{name}</a></li>'

    html_content = f"""
<footer class="dp-t6-footer">
  <div class="t6-ftr-inner">
    <div class="t6-ftr-grid">
      <div class="t6-ftr-brand">
        <a class="t6-ftr-logo" href="{base_url}">{domain_name}</a>
        <p class="t6-ftr-desc">Bringing you the boldest and most creative recipes and culinary inspirations from around the world.</p>
      </div>
      <div class="t6-ftr-nav-col">
        <h4>Explore</h4>
        <ul>
          <li><a href="{base_url}">Home</a></li>
          {cat_links}
        </ul>
      </div>
      <div class="t6-ftr-nav-col">
        <h4>About</h4>
        <ul>
          {legal_links}
        </ul>
      </div>
    </div>
    <div class="t6-ftr-bottom">
      <p>&copy; {year} {domain_name}. Built with <span>BOLDNESS</span>.</p>
    </div>
  </div>
</footer>
"""

    css_content = f"""
{ROOT} {{
    {css_vars}
    background: #000;
    color: #fff;
    border-top: var(--border-width) solid var(--border);
    padding: 80px 0 40px;
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} .t6-ftr-inner {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 40px;
}}
{ROOT} .t6-ftr-grid {{
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr;
    gap: 60px;
    margin-bottom: 60px;
}}
{ROOT} .t6-ftr-logo {{
    font-family: {font_family};
    font-size: 2.222rem;
    font-weight: 900;
    color: #000;
    background: var(--primary);
    text-decoration: none;
    text-transform: uppercase;
    display: inline-block;
    padding: 8px 16px;
    border: var(--border-width) solid #fff;
    box-shadow: 6px 6px 0px #fff;
    margin-bottom: 24px;
}}
{ROOT} .t6-ftr-desc {{
    font-size: 1.1rem;
    line-height: 1.6;
    color: #ccc;
    max-width: 400px;
}}
{ROOT} .t6-ftr-nav-col h4 {{
    font-family: {font_family};
    font-size: 1.5rem;
    font-weight: 900;
    text-transform: uppercase;
    margin-bottom: 24px;
    color: var(--primary);
}}
{ROOT} .t6-ftr-nav-col ul {{
    list-style: none;
    padding: 0;
    margin: 0;
}}
{ROOT} .t6-ftr-nav-col li {{
    margin-bottom: 12px;
}}
{ROOT} .t6-ftr-nav-col a {{
    color: #fff;
    text-decoration: none;
    font-weight: 700;
    font-size: 1rem;
    transition: color 0.2s;
}}
{ROOT} .t6-ftr-nav-col a:hover {{
    color: var(--secondary);
    text-decoration: underline;
}}
{ROOT} .t6-ftr-bottom {{
    border-top: 2px solid #333;
    padding-top: 40px;
    text-align: center;
    color: #888;
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
}}
{ROOT} .t6-ftr-bottom span {{ color: var(--primary); }}
@media (max-width: 900px) {{
    {ROOT} .t6-ftr-grid {{ grid-template-columns: 1fr; gap: 40px; }}
    {ROOT} .t6-ftr-desc {{ max-width: none; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t6-ftr-inner {{ padding: 0 20px; }}
    {ROOT} .t6-ftr-logo {{ font-size: 1.5rem; }}
}}
"""
    return {"html": html_content, "css": css_content}
