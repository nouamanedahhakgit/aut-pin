"""Theme 12 — Header: Candy Pop — white bar with rainbow gradient bottom, bouncy logo, colorful nav."""
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
        f'<a href="{html_module.escape(u)}" class="ht12-link">{html_module.escape(l)}</a>'
        for u, l in nav_links
    )
    mobile_links = "".join(
        f'<a href="{html_module.escape(u)}" class="ht12-mob-link">{html_module.escape(l)}</a>'
        for u, l in nav_links + [(about_url, "About")]
    )

    html_content = f"""
<header class="site-header dp-t12-header">
  <div class="ht12-inner">
    <a href="{html_module.escape(base_url or '/')}" class="ht12-logo">
      <span class="ht12-logo-emoji">&#127849;</span>
      <span class="ht12-logo-name">{name}</span>
    </a>
    <nav class="ht12-nav">{links_html}</nav>
    <div class="ht12-actions">
      <a href="{html_module.escape(about_url)}" class="ht12-about-link">About</a>
      <a href="{html_module.escape(base_url)}/contact-us" class="ht12-cta">Say Hi! &#128075;</a>
      <button class="ht12-burger" aria-label="Menu"
        onclick="document.querySelector('.ht12-mobile').style.display=document.querySelector('.ht12-mobile').style.display==='flex'?'none':'flex'">
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
    </div>
  </div>
  <div class="ht12-rainbow-strip"></div>
  <div class="ht12-mobile">{mobile_links}</div>
</header>
"""

    css = f"""
{t['font_import']}
.dp-t12-header {{
    {t['css_vars']}
    position: sticky; top: 0; z-index: 100;
    background: rgba(255,255,255,0.96);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}}
.ht12-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; align-items: center; height: 68px; gap: 1.5rem;
}}
.ht12-logo {{
    display: flex; align-items: center; gap: 8px;
    text-decoration: none; color: var(--text); flex-shrink: 0;
    transition: transform 0.3s;
}}
.ht12-logo:hover {{ transform: scale(1.05) rotate(-2deg); }}
.ht12-logo-emoji {{ font-size: 1.6rem; }}
.ht12-logo-name {{ font-family: {ff}; font-size: 1.25rem; font-weight: 900; }}
.ht12-nav {{ display: flex; align-items: center; gap: 0.25rem; flex: 1; padding-left: 1.5rem; }}
.ht12-link {{
    text-decoration: none; color: var(--muted); font-size: 0.88rem; font-weight: 700;
    padding: 0.4rem 0.9rem; border-radius: 50px; transition: all 0.25s;
    white-space: nowrap;
}}
.ht12-link:hover {{ color: var(--primary); background: var(--pink-pale); transform: translateY(-2px); }}
.ht12-actions {{ display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }}
.ht12-about-link {{
    text-decoration: none; color: var(--muted); font-size: 0.88rem; font-weight: 700;
    transition: color 0.25s;
}}
.ht12-about-link:hover {{ color: var(--primary); }}
.ht12-cta {{
    display: inline-flex; align-items: center; gap: 4px;
    background: var(--primary); color: #fff; padding: 0.55rem 1.25rem;
    border-radius: 50px; text-decoration: none; font-weight: 800; font-size: 0.85rem;
    transition: all 0.3s; white-space: nowrap;
    box-shadow: 0 4px 16px rgba(255,133,161,0.35);
}}
.ht12-cta:hover {{ transform: translateY(-3px) scale(1.05); box-shadow: 0 8px 24px rgba(255,133,161,0.5); }}
.ht12-rainbow-strip {{
    height: 4px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent), var(--lavender), var(--yellow), var(--primary));
    background-size: 200% 100%;
    animation: t12-rainbow 4s linear infinite;
}}
@keyframes t12-rainbow {{ 0% {{ background-position: 0% 50%; }} 100% {{ background-position: 200% 50%; }} }}
.ht12-burger {{ display: none; background: none; border: none; cursor: pointer; color: var(--text); padding: 4px; }}
.ht12-mobile {{
    display: none; flex-direction: column;
    border-top: 1px solid var(--border); padding: 0.75rem 1.5rem;
    background: #fff;
}}
.ht12-mob-link {{
    display: block; padding: 0.7rem 0.5rem; text-decoration: none;
    color: var(--text); font-weight: 700; font-size: 0.95rem;
    border-bottom: 1px solid var(--border); transition: color 0.2s;
}}
.ht12-mob-link:last-child {{ border-bottom: none; }}
.ht12-mob-link:hover {{ color: var(--primary); }}
@media (max-width: 768px) {{
    .ht12-nav {{ display: none; }}
    .ht12-about-link {{ display: none; }}
    .ht12-burger {{ display: block; }}
    .ht12-cta {{ display: none; }}
}}
"""
    return {"html": html_content, "css": css}
