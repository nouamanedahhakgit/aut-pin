"""Sidebar 2 — Modern card-based sidebar with tags cloud and about widget."""


def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("sidebar", config)
    font_import = f"@import url('{pf.get('cdn')}');" if pf.get("cdn") else ""
    font_family = pf.get("family") or "'Playfair Display', serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []
    articles = config.get("articles", []) or []
    domain_name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    about_url = f"{base_url}/about"
    for p in config.get("domain_pages") or []:
        if isinstance(p, dict) and (p.get("slug") or "").lower() in ("about-us", "about"):
            about_url = p.get("url") or about_url
            break

    tag_html = ""
    for c in categories[:10]:
        c_name = html_module.escape(c.get("name", ""))
        c_url = html_module.escape(c.get("url") or "#")
        if c_name:
            tag_html += f'<a href="{c_url}" class="sb2-tag">{c_name}</a>'

    recent_html = ""
    for art in articles[:4]:
        title = html_module.escape((art.get("title") or "Untitled")[:80])
        url = html_module.escape(art.get("url") or "#")
        img = (art.get("main_image") or art.get("image") or "").strip()
        cat_name = html_module.escape((art.get("category") or art.get("category_name") or "")[:30])
        if img and img.startswith("http"):
            img_tag = f'<img src="{html_module.escape(img)}" alt="" class="sb2-rec-img">'
        else:
            img_tag = '<div class="sb2-rec-placeholder"></div>'
        cat_badge = f'<span class="sb2-rec-cat">{cat_name}</span>' if cat_name else ""
        recent_html += f"""
        <a href="{url}" class="sb2-rec-card">
          {img_tag}
          <div class="sb2-rec-info">
            {cat_badge}
            <h4 class="sb2-rec-title">{title}</h4>
          </div>
        </a>"""

    html_content = f"""
<aside class="sidebar sidebar-2">
  <div class="sb2-card sb2-about">
    <div class="sb2-about-accent"></div>
    <i class="fas fa-utensils sb2-about-icon"></i>
    <h3 class="sb2-about-name">{domain_name}</h3>
    <p class="sb2-about-text">Sharing our favorite recipes with a community of food lovers.</p>
    <a href="{html_module.escape(about_url)}" class="sb2-about-link">Learn More &rarr;</a>
  </div>

  <div class="sb2-card">
    <h3 class="sb2-card-title">Recent Recipes</h3>
    <div class="sb2-rec-list">{recent_html or '<p class="sb2-empty">No articles yet</p>'}</div>
  </div>

  <div class="sb2-card">
    <h3 class="sb2-card-title">Topics</h3>
    <div class="sb2-tags">{tag_html or '<span class="sb2-empty">No categories</span>'}</div>
  </div>

  <div class="sb2-card sb2-social-card">
    <h3 class="sb2-card-title">Follow Us</h3>
    <div class="sb2-social-links">
      <a href="#" class="sb2-social" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
      <a href="#" class="sb2-social" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
      <a href="#" class="sb2-social" aria-label="Pinterest"><i class="fab fa-pinterest-p"></i></a>
      <a href="#" class="sb2-social" aria-label="YouTube"><i class="fab fa-youtube"></i></a>
    </div>
  </div>
</aside>
"""

    css = f"""
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
{font_import}

.sidebar-2 {{
    --primary: {s.get("primary", "#E07C5E")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font}; width: 100%;
    display: flex; flex-direction: column; gap: 1.5rem;
}}

.sb2-card {{
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.5rem; overflow: hidden;
}}

.sb2-card-title {{
    font-family: {font_family}; font-size: 1.1rem; font-weight: 700;
    color: var(--text); margin-bottom: 1rem;
}}

.sb2-about {{
    text-align: center; padding-top: 0; position: relative;
}}
.sb2-about-accent {{
    height: 60px; margin: 0 -1.5rem 1.5rem;
    background: linear-gradient(135deg, var(--primary), color-mix(in srgb, var(--primary) 60%, #000));
}}
.sb2-about-icon {{
    width: 50px; height: 50px; border-radius: 50%;
    background: var(--bg); color: var(--primary); font-size: 1.3rem;
    display: flex; align-items: center; justify-content: center;
    margin: -25px auto 0.75rem; border: 3px solid var(--bg);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}
.sb2-about-name {{ font-family: {font_family}; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; }}
.sb2-about-text {{ color: var(--muted); font-size: 0.85rem; line-height: 1.6; margin-bottom: 1rem; }}
.sb2-about-link {{
    color: var(--primary); text-decoration: none; font-weight: 600;
    font-size: 0.9rem; transition: opacity 0.2s;
}}
.sb2-about-link:hover {{ opacity: 0.7; }}

.sb2-rec-list {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.sb2-rec-card {{
    display: flex; gap: 0.75rem; text-decoration: none; color: var(--text);
    transition: color 0.2s;
}}
.sb2-rec-card:hover {{ color: var(--primary); }}
.sb2-rec-img {{ width: 64px; height: 64px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }}
.sb2-rec-placeholder {{
    width: 64px; height: 64px; border-radius: 8px;
    background: var(--border); flex-shrink: 0;
}}
.sb2-rec-info {{ display: flex; flex-direction: column; justify-content: center; gap: 0.2rem; min-width: 0; }}
.sb2-rec-cat {{
    color: var(--primary); font-size: 0.7rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.03em;
}}
.sb2-rec-title {{ font-size: 0.9rem; font-weight: 600; line-height: 1.3; overflow: hidden; text-overflow: ellipsis; }}

.sb2-tags {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.sb2-tag {{
    display: inline-block; padding: 0.35rem 0.85rem; border-radius: 9999px;
    border: 1px solid var(--border); color: var(--muted); font-size: 0.8rem;
    text-decoration: none; font-weight: 500; transition: all 0.2s;
}}
.sb2-tag:hover {{ border-color: var(--primary); color: var(--primary); background: color-mix(in srgb, var(--primary) 6%, transparent); }}

.sb2-social-card {{ text-align: center; }}
.sb2-social-links {{ display: flex; justify-content: center; gap: 0.75rem; }}
.sb2-social {{
    width: 40px; height: 40px; border-radius: 50%;
    border: 1px solid var(--border); color: var(--muted);
    display: flex; align-items: center; justify-content: center;
    text-decoration: none; font-size: 0.9rem; transition: all 0.2s;
}}
.sb2-social:hover {{ border-color: var(--primary); color: var(--primary); }}

.sb2-empty {{ color: var(--muted); font-size: 0.85rem; font-style: italic; }}
"""
    return {"html": html_content, "css": css}
