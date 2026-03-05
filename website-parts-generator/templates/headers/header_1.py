"""Header 1 — Centered logo with split navigation. Top utility bar + main nav."""


def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("header", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Playfair Display, serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []

    left_links = [
        (f"{base_url or '/'}", "Home"),
        (f"{base_url}/recipes", "Recipes"),
    ]
    right_links = []
    for c in categories[:3]:
        url = html_module.escape(c.get("url") or f"{base_url}/categories")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            right_links.append((url, cat_name))
    if not right_links:
        right_links.append((f"{base_url}/categories", "Categories"))

    about_url = f"{base_url}/about"
    for p in config.get("domain_pages") or []:
        if isinstance(p, dict) and (p.get("slug") or "").lower() in ("about-us", "about"):
            about_url = p.get("url") or about_url
            break
    right_links.append((about_url, "About"))

    left_html = "".join(f'<a href="{html_module.escape(u)}" class="sh1-link">{html_module.escape(l)}</a>' for u, l in left_links)
    right_html = "".join(f'<a href="{html_module.escape(u)}" class="sh1-link">{html_module.escape(l)}</a>' for u, l in right_links)
    all_links = left_links + right_links
    mobile_html = "".join(f'<a href="{html_module.escape(u)}" class="sh1-mobile-link">{html_module.escape(l)}</a>' for u, l in all_links)

    html_content = f"""
<header class="site-header site-header-1">
  <div class="sh1-top-bar">
    <div class="sh1-top-inner">
      <span class="sh1-tagline">Delicious recipes for every occasion</span>
      <div class="sh1-top-links">
        <a href="{html_module.escape(about_url)}" class="sh1-top-link">About</a>
        <a href="{html_module.escape(base_url)}/contact" class="sh1-top-link">Contact</a>
      </div>
    </div>
  </div>
  <nav class="sh1-main">
    <div class="sh1-inner">
      <div class="sh1-left">{left_html}</div>
      <a href="{html_module.escape(base_url or '/')}" class="sh1-logo">
        <i class="fas fa-utensils sh1-logo-icon"></i>
        <span class="sh1-logo-name">{name}</span>
      </a>
      <div class="sh1-right">{right_html}</div>
      <button class="sh1-burger" aria-label="Menu">
        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>
  </nav>
  <div class="sh1-mobile-menu" style="display:none;">{mobile_html}</div>
</header>
"""

    css = f"""
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
{font_import}

.site-header-1 {{
    --primary: {s.get("primary", "#E07C5E")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    position: sticky; top: 0; z-index: 50;
    background: var(--bg);
    font-family: {body_font};
}}
.sh1-top-bar {{
    background: var(--primary);
    color: #fff;
    font-size: 0.8rem;
}}
.sh1-top-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0.4rem 1.5rem;
    display: flex; justify-content: space-between; align-items: center;
}}
.sh1-tagline {{ opacity: 0.9; }}
.sh1-top-links {{ display: flex; gap: 1rem; }}
.sh1-top-link {{ color: #fff; text-decoration: none; opacity: 0.85; transition: opacity 0.2s; }}
.sh1-top-link:hover {{ opacity: 1; }}

.sh1-main {{ border-bottom: 1px solid var(--border); }}
.sh1-inner {{
    max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
    display: flex; align-items: center; justify-content: center;
    height: 72px; gap: 2rem;
}}
.sh1-left, .sh1-right {{ display: flex; gap: 1.5rem; flex: 1; }}
.sh1-left {{ justify-content: flex-end; }}
.sh1-right {{ justify-content: flex-start; }}
.sh1-link {{
    text-decoration: none; color: var(--text); font-weight: 600;
    font-size: 0.95rem; transition: color 0.2s; white-space: nowrap;
}}
.sh1-link:hover {{ color: var(--primary); }}

.sh1-logo {{
    display: flex; flex-direction: column; align-items: center;
    text-decoration: none; color: var(--text); flex-shrink: 0;
}}
.sh1-logo-icon {{ color: var(--primary); font-size: 1.4rem; margin-bottom: 0.15rem; }}
.sh1-logo-name {{ font-family: {font_family}; font-size: 1.3rem; font-weight: 700; }}

.sh1-burger {{ display: none; background: none; border: none; color: var(--text); cursor: pointer; padding: 0.5rem; }}

.sh1-mobile-menu {{
    background: var(--bg); border-bottom: 1px solid var(--border);
    padding: 0.5rem 0;
}}
.sh1-mobile-link {{
    display: block; padding: 0.75rem 1.5rem;
    text-decoration: none; color: var(--text); font-weight: 600;
    transition: background 0.2s;
}}
.sh1-mobile-link:hover {{ background: color-mix(in srgb, var(--primary) 8%, transparent); color: var(--primary); }}

@media (max-width: 768px) {{
    .sh1-top-bar {{ display: none; }}
    .sh1-left, .sh1-right {{ display: none; }}
    .sh1-inner {{ justify-content: space-between; }}
    .sh1-burger {{ display: block; }}
    .sh1-logo {{ flex-direction: row; gap: 0.5rem; }}
    .sh1-logo-icon {{ margin-bottom: 0; }}
}}
"""
    return {"html": html_content, "css": css}
