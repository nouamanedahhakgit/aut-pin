"""Footer for Theme 7 — Minimalist Glass.
Soft, airy footer with subtle borders and refined typography.
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
<footer class="dp-t7-footer">
  <div class="t7-ftr-inner">
    <div class="t7-ftr-grid">
      <div class="t7-ftr-brand">
        <a class="t7-ftr-logo" href="{base_url}">{domain_name}</a>
        <p class="t7-ftr-desc">Experience culinary art through a lens of purity and refined simplicity.</p>
      </div>
      <div class="t7-ftr-nav-col">
        <h4>Discover</h4>
        <ul>
          <li><a href="{base_url}">Home</a></li>
          {cat_links}
        </ul>
      </div>
      <div class="t7-ftr-nav-col">
        <h4>Legal</h4>
        <ul>
          {legal_links}
        </ul>
      </div>
    </div>
    <div class="t7-ftr-bottom">
      <p>&copy; {year} {domain_name}. Elegance in Every Bite.</p>
    </div>
  </div>
</footer>
"""

    css_content = f"""
{ROOT} {{
    {css_vars}
    background: #fff;
    color: var(--text);
    border-top: 1px solid rgba(0,0,0,0.05);
    padding: 100px 0 60px;
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} .t7-ftr-inner {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 40px;
}}
{ROOT} .t7-ftr-grid {{
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 80px;
    margin-bottom: 80px;
}}
{ROOT} .t7-ftr-logo {{
    font-family: {font_family};
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--primary);
    text-decoration: none;
    display: inline-block;
    margin-bottom: 30px;
    letter-spacing: -0.01em;
}}
{ROOT} .t7-ftr-desc {{
    font-size: 1.05rem;
    line-height: 1.8;
    color: var(--muted);
    max-width: 350px;
    font-weight: 300;
}}
{ROOT} .t7-ftr-nav-col h4 {{
    font-family: {font_family};
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 32px;
    color: var(--primary);
    letter-spacing: 0.15em;
}}
{ROOT} .t7-ftr-nav-col ul {{
    list-style: none;
    padding: 0; margin: 0;
}}
{ROOT} .t7-ftr-nav-col li {{ margin-bottom: 16px; }}
{ROOT} .t7-ftr-nav-col a {{
    color: var(--muted);
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 400;
    transition: color 0.3s;
}}
{ROOT} .t7-ftr-nav-col a:hover {{
    color: var(--secondary);
}}
{ROOT} .t7-ftr-bottom {{
    border-top: 1px solid rgba(0,0,0,0.03);
    padding-top: 60px;
    text-align: left;
    color: var(--muted);
    font-size: 0.85rem;
    font-weight: 300;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
@media (max-width: 900px) {{
    {ROOT} .t7-ftr-grid {{ grid-template-columns: 1fr; gap: 60px; }}
    {ROOT} .t7-ftr-desc {{ max-width: none; }}
    {ROOT} .t7-ftr-bottom {{ text-align: center; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t7-ftr-inner {{ padding: 0 20px; }}
}}
"""
    return {"html": html_content, "css": css_content}
