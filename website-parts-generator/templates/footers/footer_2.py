"""Footer 2 — Dark footer with centered layout and wave top border."""


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
    for c in categories[:8]:
        url = html_module.escape(c.get("url") or "#")
        cat_name = html_module.escape(c.get("name", ""))
        if cat_name:
            cat_links += f'<a href="{url}" class="sf2-cat-link">{cat_name}</a>'

    pages_links = ""
    for p in config.get("domain_pages") or []:
        if not isinstance(p, dict):
            continue
        p_url = html_module.escape(p.get("url") or "#")
        p_name = html_module.escape(p.get("name") or "").strip()
        if p_name:
            pages_links += f'<a href="{p_url}" class="sf2-page-link">{p_name}</a>'

    html_content = f"""
<footer class="site-footer site-footer-2">
  <svg class="sf2-wave" viewBox="0 0 1440 60" preserveAspectRatio="none">
    <path d="M0,30 C360,60 720,0 1080,30 C1260,45 1380,30 1440,20 L1440,60 L0,60 Z" fill="currentColor"/>
  </svg>
  <div class="sf2-body">
    <div class="sf2-top">
      <div class="sf2-logo">
        <i class="fas fa-utensils sf2-icon"></i>
        <span class="sf2-name">{name}</span>
      </div>
      <p class="sf2-tagline">Delicious recipes crafted with passion</p>
    </div>
    <div class="sf2-grid">
      <div class="sf2-section">
        <h4 class="sf2-heading">Quick Links</h4>
        <div class="sf2-links">
          <a href="{html_module.escape(base_url or '/')}" class="sf2-link">Home</a>
          <a href="{html_module.escape(base_url)}/recipes" class="sf2-link">Recipes</a>
          <a href="{html_module.escape(base_url)}/about" class="sf2-link">About</a>
        </div>
      </div>
      <div class="sf2-section">
        <h4 class="sf2-heading">Categories</h4>
        <div class="sf2-links">{cat_links or '<span class="sf2-link">Recipes</span>'}</div>
      </div>
      <div class="sf2-section">
        <h4 class="sf2-heading">Legal</h4>
        <div class="sf2-links">{pages_links or '<span class="sf2-link">&mdash;</span>'}</div>
      </div>
    </div>
    <div class="sf2-social">
      <a href="#" class="sf2-social-btn" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
      <a href="#" class="sf2-social-btn" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
      <a href="#" class="sf2-social-btn" aria-label="Pinterest"><i class="fab fa-pinterest-p"></i></a>
    </div>
    <div class="sf2-bottom">
      <p>&copy; {year} {name}. All rights reserved.</p>
      <button onclick="window.scrollTo({{top:0,behavior:'smooth'}})" class="sf2-top-btn">Back to Top &uarr;</button>
    </div>
  </div>
</footer>
"""

    css = f"""
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
{font_import}

.site-footer-2 {{
    --primary: {s.get("primary", "#E07C5E")};
    --secondary: {s.get("secondary", "#D46A4A")};
    --border: {s.get("border", "#444")};
    font-family: {body_font};
    margin-top: 4rem;
    position: relative;
}}

.sf2-wave {{ display: block; width: 100%; height: 40px; color: #1a1a1a; }}
.sf2-body {{ background: #1a1a1a; color: #ccc; }}

.sf2-top {{ text-align: center; padding: 2rem 1.5rem 1.5rem; }}
.sf2-logo {{ display: inline-flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem; }}
.sf2-icon {{ color: var(--primary); font-size: 1.5rem; }}
.sf2-name {{ font-family: {font_family}; font-size: 1.8rem; font-weight: 700; color: #fff; }}
.sf2-tagline {{ color: #999; font-size: 0.9rem; }}

.sf2-grid {{
    max-width: 900px; margin: 0 auto; padding: 1.5rem;
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem;
    text-align: center;
}}
.sf2-heading {{ color: var(--primary); font-family: {font_family}; font-size: 1rem; font-weight: 700; margin-bottom: 0.75rem; }}
.sf2-links {{ display: flex; flex-direction: column; gap: 0.4rem; }}
.sf2-link, .sf2-cat-link, .sf2-page-link {{
    color: #aaa; text-decoration: none; font-size: 0.85rem; transition: color 0.2s;
}}
.sf2-link:hover, .sf2-cat-link:hover, .sf2-page-link:hover {{ color: var(--primary); }}

.sf2-social {{
    display: flex; justify-content: center; gap: 0.75rem; padding: 1.5rem 0;
}}
.sf2-social-btn {{
    width: 40px; height: 40px; border-radius: 50%;
    border: 1px solid #444; color: #ccc;
    display: flex; align-items: center; justify-content: center;
    text-decoration: none; font-size: 0.9rem; transition: all 0.2s;
}}
.sf2-social-btn:hover {{ border-color: var(--primary); color: var(--primary); }}

.sf2-bottom {{
    border-top: 1px solid #333; padding: 1.25rem 1.5rem;
    display: flex; justify-content: space-between; align-items: center;
    max-width: 900px; margin: 0 auto; font-size: 0.8rem; color: #777;
}}
.sf2-top-btn {{
    background: none; border: 1px solid #555; color: #aaa; padding: 0.4rem 1rem;
    border-radius: 4px; cursor: pointer; font-size: 0.8rem; transition: all 0.2s;
}}
.sf2-top-btn:hover {{ border-color: var(--primary); color: var(--primary); }}

@media (max-width: 768px) {{
    .sf2-grid {{ grid-template-columns: 1fr; gap: 1.5rem; }}
    .sf2-bottom {{ flex-direction: column; gap: 0.75rem; text-align: center; }}
}}
"""
    return {"html": html_content, "css": css}
