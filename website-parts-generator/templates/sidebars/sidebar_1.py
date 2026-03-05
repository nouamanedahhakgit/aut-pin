"""Sidebar 1 — Classic sidebar: search, categories, popular posts, newsletter."""


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

    cat_html = ""
    for c in categories[:8]:
        c_name = html_module.escape(c.get("name", ""))
        c_url = html_module.escape(c.get("url") or "#")
        count = c.get("count", "")
        count_span = f'<span class="sb1-cat-count">{count}</span>' if count else ""
        if c_name:
            cat_html += f'<a href="{c_url}" class="sb1-cat-link"><span>{c_name}</span>{count_span}</a>'

    popular_html = ""
    for i, art in enumerate(articles[:5]):
        title = html_module.escape((art.get("title") or "Untitled")[:80])
        url = html_module.escape(art.get("url") or "#")
        img = (art.get("main_image") or art.get("image") or "").strip()
        if img and img.startswith("http"):
            img_tag = f'<img src="{html_module.escape(img)}" alt="" class="sb1-pop-img">'
        else:
            img_tag = f'<div class="sb1-pop-num">{i+1}</div>'
        popular_html += f"""
        <a href="{url}" class="sb1-pop-item">
          {img_tag}
          <span class="sb1-pop-title">{title}</span>
        </a>"""

    html_content = f"""
<aside class="sidebar sidebar-1">
  <div class="sb1-widget">
    <h3 class="sb1-widget-title">Search</h3>
    <form class="sb1-search" action="{html_module.escape(base_url)}/search" method="get">
      <input type="text" name="q" placeholder="Search recipes..." class="sb1-search-input">
      <button type="submit" class="sb1-search-btn" aria-label="Search">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
        </svg>
      </button>
    </form>
  </div>

  <div class="sb1-widget">
    <h3 class="sb1-widget-title">Categories</h3>
    <div class="sb1-cat-list">{cat_html or '<span class="sb1-empty">No categories</span>'}</div>
  </div>

  <div class="sb1-widget">
    <h3 class="sb1-widget-title">Popular Recipes</h3>
    <div class="sb1-pop-list">{popular_html or '<span class="sb1-empty">No articles yet</span>'}</div>
  </div>

  <div class="sb1-widget sb1-newsletter">
    <h3 class="sb1-widget-title">Newsletter</h3>
    <p class="sb1-nl-text">Get the latest recipes delivered to your inbox!</p>
    <form class="sb1-nl-form" onsubmit="return false;">
      <input type="email" placeholder="Your email" class="sb1-nl-input">
      <button type="submit" class="sb1-nl-btn">Subscribe</button>
    </form>
  </div>
</aside>
"""

    css = f"""
{font_import}

.sidebar-1 {{
    --primary: {s.get("primary", "#E07C5E")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font}; width: 100%;
}}

.sb1-widget {{ margin-bottom: 2rem; }}
.sb1-widget-title {{
    font-family: {font_family}; font-size: 1.1rem; font-weight: 700;
    color: var(--text); padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--primary); margin-bottom: 1rem;
}}

.sb1-search {{ display: flex; gap: 0; }}
.sb1-search-input {{
    flex: 1; padding: 0.6rem 0.8rem; border: 1px solid var(--border);
    border-right: none; border-radius: 6px 0 0 6px; font-size: 0.9rem;
    font-family: inherit; outline: none; transition: border-color 0.2s;
}}
.sb1-search-input:focus {{ border-color: var(--primary); }}
.sb1-search-btn {{
    padding: 0 0.85rem; background: var(--primary); border: 1px solid var(--primary);
    border-radius: 0 6px 6px 0; color: #fff; cursor: pointer; transition: opacity 0.2s;
}}
.sb1-search-btn:hover {{ opacity: 0.85; }}

.sb1-cat-list {{ display: flex; flex-direction: column; gap: 0.25rem; }}
.sb1-cat-link {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.5rem 0.6rem; border-radius: 6px;
    text-decoration: none; color: var(--text); font-size: 0.9rem;
    font-weight: 500; transition: all 0.2s;
}}
.sb1-cat-link:hover {{ background: color-mix(in srgb, var(--primary) 8%, transparent); color: var(--primary); }}
.sb1-cat-count {{
    background: var(--border); font-size: 0.75rem; padding: 0.15rem 0.5rem;
    border-radius: 9999px; color: var(--muted);
}}

.sb1-pop-list {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.sb1-pop-item {{
    display: flex; gap: 0.75rem; align-items: center;
    text-decoration: none; color: var(--text); transition: color 0.2s;
}}
.sb1-pop-item:hover {{ color: var(--primary); }}
.sb1-pop-img {{ width: 56px; height: 56px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }}
.sb1-pop-num {{
    width: 36px; height: 36px; border-radius: 50%;
    background: color-mix(in srgb, var(--primary) 12%, transparent);
    color: var(--primary); font-weight: 700; font-size: 0.85rem;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.sb1-pop-title {{ font-size: 0.9rem; font-weight: 500; line-height: 1.4; }}

.sb1-newsletter {{
    background: color-mix(in srgb, var(--primary) 6%, var(--bg));
    padding: 1.25rem; border-radius: 10px;
}}
.sb1-nl-text {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 0.75rem; }}
.sb1-nl-form {{ display: flex; flex-direction: column; gap: 0.5rem; }}
.sb1-nl-input {{
    padding: 0.6rem 0.8rem; border: 1px solid var(--border); border-radius: 6px;
    font-size: 0.9rem; font-family: inherit; outline: none;
}}
.sb1-nl-input:focus {{ border-color: var(--primary); }}
.sb1-nl-btn {{
    padding: 0.6rem; background: var(--primary); color: #fff; border: none;
    border-radius: 6px; font-weight: 600; font-size: 0.9rem;
    cursor: pointer; transition: opacity 0.2s; font-family: inherit;
}}
.sb1-nl-btn:hover {{ opacity: 0.85; }}

.sb1-empty {{ color: var(--muted); font-size: 0.85rem; font-style: italic; }}
"""
    return {"html": html_content, "css": css}
