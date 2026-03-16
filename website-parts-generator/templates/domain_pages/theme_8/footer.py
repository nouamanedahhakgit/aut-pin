"""Footer for Theme 8 — Aurora Borealis Dark.
Deep obsidian footer with aurora-glow brand name, aurora-gradient divider,
and a 3-column grid for brand, discover, and legal links.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module
from datetime import datetime

ROOT = ".dp-t8-footer"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name  = html_module.escape(config.get("domain_name", "My Blog"))
    base_url     = html_module.escape(config.get("base_url") or config.get("domain_url", "/"))
    categories   = config.get("categories") or []
    domain_pages = config.get("domain_pages") or []
    year = datetime.now().year

    cat_links = ""
    for cat in categories[:5]:
        name = html_module.escape(cat.get("name", ""))
        url  = html_module.escape(cat.get("url", "#"))
        cat_links += f'<li><a href="{url}">{name}</a></li>'

    legal_links = ""
    for pg in domain_pages:
        name = html_module.escape(pg.get("name", ""))
        url  = html_module.escape(pg.get("url", "#"))
        legal_links += f'<li><a href="{url}">{name}</a></li>'

    html_content = f"""
<footer class="dp-t8-footer">
  <div class="t8-ftr-aurora-bar"></div>
  <div class="t8-ftr-inner">
    <div class="t8-ftr-grid">
      <div class="t8-ftr-brand">
        <a class="t8-ftr-logo" href="{base_url}">{domain_name}</a>
        <p class="t8-ftr-desc">Where every recipe illuminates the night — bold flavors, aurora aesthetics, and culinary wonder.</p>
        <div class="t8-ftr-social">
          <span class="t8-ftr-badge">✦ Aurora Kitchen</span>
        </div>
      </div>
      <div class="t8-ftr-col">
        <h4>Explore</h4>
        <ul>
          <li><a href="{base_url}">Home</a></li>
          {cat_links}
        </ul>
      </div>
      <div class="t8-ftr-col">
        <h4>Legal</h4>
        <ul>
          {legal_links}
        </ul>
      </div>
    </div>
    <div class="t8-ftr-bottom">
      <span>&copy; {year} {domain_name}. Crafted under the aurora.</span>
      <div class="t8-ftr-dots">
        <span class="t8-dot t8-dot-v"></span>
        <span class="t8-dot t8-dot-c"></span>
        <span class="t8-dot t8-dot-g"></span>
      </div>
    </div>
  </div>
</footer>
"""

    css_content = f"""
{ROOT} {{
    {css_vars}
    background: var(--surface);
    color: var(--text);
    position: relative;
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} .t8-ftr-aurora-bar {{
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent), var(--primary));
    background-size: 300% 100%;
    animation: t8-aurora-shift 6s ease infinite;
}}
@keyframes t8-aurora-shift {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
{ROOT} .t8-ftr-inner {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 80px 40px 40px;
}}
{ROOT} .t8-ftr-grid {{
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 80px;
    margin-bottom: 60px;
}}
{ROOT} .t8-ftr-logo {{
    font-family: {font_family};
    font-size: 2rem;
    font-weight: 800;
    text-decoration: none;
    background: linear-gradient(135deg, #fff, var(--secondary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: block;
    margin-bottom: 20px;
    letter-spacing: -0.02em;
}}
{ROOT} .t8-ftr-desc {{
    font-size: 0.95rem;
    line-height: 1.75;
    color: var(--muted);
    max-width: 320px;
    margin: 0 0 24px;
    font-weight: 300;
}}
{ROOT} .t8-ftr-badge {{
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--secondary);
    background: rgba(6,182,212,0.1);
    border: 1px solid rgba(6,182,212,0.2);
    padding: 6px 16px;
    border-radius: 50px;
}}
{ROOT} .t8-ftr-col h4 {{
    font-family: {font_family};
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--primary);
    margin: 0 0 28px;
}}
{ROOT} .t8-ftr-col ul {{
    list-style: none;
    padding: 0; margin: 0;
}}
{ROOT} .t8-ftr-col li {{ margin-bottom: 14px; }}
{ROOT} .t8-ftr-col a {{
    color: var(--muted);
    text-decoration: none;
    font-size: 0.92rem;
    font-weight: 400;
    transition: color 0.25s;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}
{ROOT} .t8-ftr-col a::before {{
    content: "";
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--primary);
    opacity: 0;
    transition: opacity 0.25s, transform 0.25s;
    transform: scale(0);
}}
{ROOT} .t8-ftr-col a:hover {{ color: var(--secondary); }}
{ROOT} .t8-ftr-col a:hover::before {{ opacity: 1; transform: scale(1); }}

{ROOT} .t8-ftr-bottom {{
    border-top: 1px solid rgba(124,58,237,0.15);
    padding-top: 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.82rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.06em;
}}
{ROOT} .t8-ftr-dots {{ display: flex; gap: 8px; }}
{ROOT} .t8-dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
}}
{ROOT} .t8-dot-v {{ background: var(--primary); }}
{ROOT} .t8-dot-c {{ background: var(--secondary); }}
{ROOT} .t8-dot-g {{ background: var(--accent); }}
@media (max-width: 900px) {{
    {ROOT} .t8-ftr-grid {{ grid-template-columns: 1fr; gap: 48px; margin-bottom: 40px; }}
    {ROOT} .t8-ftr-desc  {{ max-width: none; }}
    {ROOT} .t8-ftr-bottom {{ flex-direction: column; gap: 16px; text-align: center; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t8-ftr-inner {{ padding: 60px 20px 32px; }}
}}
"""
    return {"html": html_content, "css": css_content}
