"""Header 2 — Full-width colored banner header with large logo and horizontal nav below."""


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

    nav_items = [(f"{base_url or '/'}", "Home"), (f"{base_url}/recipes", "Recipes")]
    for c in categories[:5]:
        url = html_module.escape(c.get("url") or "#")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            nav_items.append((url, cat_name))

    about_url = f"{base_url}/about"
    for p in config.get("domain_pages") or []:
        if isinstance(p, dict) and (p.get("slug") or "").lower() in ("about-us", "about"):
            about_url = p.get("url") or about_url
            break
    nav_items.append((about_url, "About"))

    nav_html = "".join(f'<a href="{html_module.escape(u)}" class="sh2-nav-link">{html_module.escape(l)}</a>' for u, l in nav_items)
    mobile_html = "".join(f'<a href="{html_module.escape(u)}" class="sh2-mob-link">{html_module.escape(l)}</a>' for u, l in nav_items)

    html_content = f"""
<header class="site-header site-header-2">
  <div class="sh2-brand">
    <a href="{html_module.escape(base_url or '/')}" class="sh2-logo">
      <i class="fas fa-utensils sh2-icon"></i>
      <span class="sh2-name">{name}</span>
    </a>
    <p class="sh2-desc">Homemade recipes with love</p>
  </div>
  <nav class="sh2-nav">
    <div class="sh2-nav-inner">
      {nav_html}
      <button class="sh2-search-btn" aria-label="Search">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
        </svg>
      </button>
    </div>
    <button class="sh2-burger" aria-label="Menu">
      <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
    </button>
  </nav>
  <div class="sh2-mobile-menu" style="display:none;">{mobile_html}</div>
</header>
"""

    css = f"""
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
{font_import}

.site-header-2 {{
    --primary: {s.get("primary", "#E07C5E")};
    --secondary: {s.get("secondary", "#D46A4A")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    position: sticky; top: 0; z-index: 50;
    font-family: {body_font};
}}

.sh2-brand {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    text-align: center; padding: 1.5rem 1rem 1rem;
}}
.sh2-logo {{
    text-decoration: none; color: #fff;
    display: inline-flex; align-items: center; gap: 0.6rem;
}}
.sh2-icon {{ font-size: 1.8rem; }}
.sh2-name {{ font-family: {font_family}; font-size: 2rem; font-weight: 700; }}
.sh2-desc {{ color: rgba(255,255,255,0.8); font-size: 0.85rem; margin: 0.3rem 0 0; }}

.sh2-nav {{
    background: var(--bg); border-bottom: 2px solid var(--border);
    display: flex; align-items: center; justify-content: center;
}}
.sh2-nav-inner {{
    max-width: 1280px; display: flex; align-items: center;
    gap: 0.25rem; padding: 0 1rem; flex-wrap: wrap; justify-content: center;
}}
.sh2-nav-link {{
    text-decoration: none; color: var(--text); font-weight: 600;
    font-size: 0.9rem; padding: 0.85rem 1rem;
    border-bottom: 3px solid transparent; transition: all 0.2s;
}}
.sh2-nav-link:hover {{ color: var(--primary); border-bottom-color: var(--primary); }}

.sh2-search-btn {{
    background: none; border: none; color: var(--muted); cursor: pointer;
    padding: 0.6rem; margin-left: 0.5rem; transition: color 0.2s;
}}
.sh2-search-btn:hover {{ color: var(--primary); }}

.sh2-burger {{
    display: none; background: none; border: none; color: var(--text);
    cursor: pointer; padding: 0.75rem 1rem;
}}

.sh2-mobile-menu {{
    background: var(--bg); border-bottom: 2px solid var(--border); padding: 0.5rem 0;
}}
.sh2-mob-link {{
    display: block; padding: 0.75rem 1.5rem;
    text-decoration: none; color: var(--text); font-weight: 600;
    font-size: 0.95rem; transition: all 0.2s;
}}
.sh2-mob-link:hover {{ background: color-mix(in srgb, var(--primary) 10%, transparent); color: var(--primary); }}

@media (max-width: 768px) {{
    .sh2-brand {{ padding: 1rem; }}
    .sh2-name {{ font-size: 1.5rem; }}
    .sh2-nav-inner {{ display: none; }}
    .sh2-burger {{ display: block; }}
    .sh2-nav {{ justify-content: flex-end; }}
}}
"""
    return {"html": html_content, "css": css}
