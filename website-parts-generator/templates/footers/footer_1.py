"""Footer 1 — Light modern footer with colored accent border and 3 columns."""


def generate(config: dict) -> dict:
    import html as html_module
    from datetime import datetime
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("footer", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Playfair Display, serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []
    year = datetime.now().year

    cat_links = ""
    for c in categories[:6]:
        url = html_module.escape(c.get("url") or "#")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            cat_links += f'<a href="{url}" class="sf1-tag">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<li><a href="{p_url}" class="sf1-link">{p_name}</a></li>'

    html_content = f"""
<footer class="site-footer site-footer-1">
  <div class="sf1-accent"></div>
  <div class="sf1-inner">
    <div class="sf1-col sf1-brand">
      <div class="sf1-logo">
        <i class="fas fa-utensils sf1-icon"></i>
        <span class="sf1-name">{name}</span>
      </div>
      <p class="sf1-tagline">Fresh recipes, made with love. Bringing joy to your kitchen every day.</p>
      <div class="sf1-social">
        <a href="#" class="sf1-social-btn" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
        <a href="#" class="sf1-social-btn" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
        <a href="#" class="sf1-social-btn" aria-label="Pinterest"><i class="fab fa-pinterest-p"></i></a>
      </div>
    </div>
    <div class="sf1-col">
      <h4 class="sf1-heading">Explore</h4>
      <ul class="sf1-list">
        <li><a href="{html_module.escape(base_url or '/')}" class="sf1-link">Home</a></li>
        <li><a href="{html_module.escape(base_url)}/recipes" class="sf1-link">All Recipes</a></li>
        <li><a href="{html_module.escape(base_url)}/about" class="sf1-link">About Us</a></li>
        {pages_links}
      </ul>
    </div>
    <div class="sf1-col">
      <h4 class="sf1-heading">Categories</h4>
      <div class="sf1-tags">
        {cat_links or '<span class="sf1-tag">Recipes</span>'}
      </div>
    </div>
  </div>
  <div class="sf1-bottom">
    <p>&copy; {year} {name}. All rights reserved.</p>
  </div>
</footer>
"""

    css = f"""
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
{font_import}

.site-footer-1 {{
    --primary: {s.get("primary", "#E07C5E")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font};
    background: var(--bg);
    margin-top: 4rem;
}}
.sf1-accent {{ height: 4px; background: linear-gradient(90deg, var(--primary), color-mix(in srgb, var(--primary) 40%, #fff)); }}

.sf1-inner {{
    max-width: 1200px; margin: 0 auto; padding: 3rem 1.5rem;
    display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 3rem;
}}

.sf1-logo {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }}
.sf1-icon {{ color: var(--primary); font-size: 1.3rem; }}
.sf1-name {{ font-family: {font_family}; font-size: 1.4rem; font-weight: 700; color: var(--text); }}
.sf1-tagline {{ color: var(--muted); font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.25rem; }}

.sf1-social {{ display: flex; gap: 0.5rem; }}
.sf1-social-btn {{
    width: 36px; height: 36px; border-radius: 50%;
    background: color-mix(in srgb, var(--primary) 12%, transparent);
    color: var(--primary); display: flex; align-items: center; justify-content: center;
    text-decoration: none; font-size: 0.85rem; transition: all 0.2s;
}}
.sf1-social-btn:hover {{ background: var(--primary); color: #fff; }}

.sf1-heading {{ font-family: {font_family}; font-size: 1.1rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; }}
.sf1-list {{ list-style: none; padding: 0; margin: 0; }}
.sf1-list li {{ margin-bottom: 0.5rem; }}
.sf1-link {{ text-decoration: none; color: var(--muted); font-size: 0.9rem; transition: color 0.2s; }}
.sf1-link:hover {{ color: var(--primary); }}

.sf1-tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
.sf1-tag {{
    display: inline-block; padding: 0.35rem 0.85rem; border-radius: 9999px;
    border: 1px solid var(--border); color: var(--muted); font-size: 0.8rem;
    text-decoration: none; transition: all 0.2s;
}}
.sf1-tag:hover {{ border-color: var(--primary); color: var(--primary); }}

.sf1-bottom {{
    border-top: 1px solid var(--border); text-align: center;
    padding: 1.25rem 1.5rem; color: var(--muted); font-size: 0.8rem;
}}

@media (max-width: 768px) {{
    .sf1-inner {{ grid-template-columns: 1fr; gap: 2rem; }}
}}
"""
    return {"html": html_content, "css": css}
