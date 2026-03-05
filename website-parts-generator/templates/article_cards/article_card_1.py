"""Article Card 1 — Vertical card with image top, category badge, title, excerpt."""


def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("article_card", config)
    font_import = f"@import url('{pf.get('cdn')}');" if pf.get("cdn") else ""
    font_family = pf.get("family") or "'Playfair Display', serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    article = config.get("article") or {}
    show_excerpt = config.get("show_excerpt", True)
    scope_prefix = config.get("scope_prefix", "")

    title = html_module.escape((article.get("title") or "Untitled")[:120])
    url = html_module.escape(article.get("url") or "#")
    img = (article.get("main_image") or article.get("image") or "").strip()
    excerpt = html_module.escape((article.get("excerpt") or "")[:160])
    category = html_module.escape((article.get("category") or article.get("category_name") or "")[:40])
    writer_name = html_module.escape(str((article.get("writer") or {}).get("name", "")))

    if img and img.startswith("http"):
        img_tag = f'<img src="{html_module.escape(img)}" alt="{title}" class="ac1-img">'
    else:
        img_tag = '<div class="ac1-placeholder"><span>🍽️</span></div>'

    cat_badge = f'<span class="ac1-cat">{category}</span>' if category else ""
    excerpt_html = f'<p class="ac1-excerpt">{excerpt}</p>' if show_excerpt and excerpt else ""
    writer_html = f'<span class="ac1-writer">By {writer_name}</span>' if writer_name else ""

    scope = f"{scope_prefix} " if scope_prefix else ""

    html_content = f"""
<article class="article-card ac1">
  <a href="{url}" class="ac1-link">
    <div class="ac1-media">{img_tag}{cat_badge}</div>
    <div class="ac1-body">
      <h3 class="ac1-title">{title}</h3>
      {excerpt_html}
      <div class="ac1-footer">{writer_html}<span class="ac1-more">Read More &rarr;</span></div>
    </div>
  </a>
</article>
"""

    css = f"""
{font_import}

{scope}.ac1 {{
    --primary: {s.get("primary", "#E07C5E")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font};
    border: 1px solid var(--border); border-radius: 12px;
    overflow: hidden; background: var(--bg);
    transition: transform 0.2s, box-shadow 0.2s;
}}
{scope}.ac1:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}}

{scope}.ac1-link {{ text-decoration: none; color: inherit; display: block; }}

{scope}.ac1-media {{ position: relative; }}
{scope}.ac1-img {{ width: 100%; aspect-ratio: 16/10; object-fit: cover; display: block; }}
{scope}.ac1-placeholder {{
    width: 100%; aspect-ratio: 16/10; background: var(--border);
    display: flex; align-items: center; justify-content: center; font-size: 2.5rem;
}}
{scope}.ac1-cat {{
    position: absolute; top: 0.75rem; left: 0.75rem;
    background: var(--primary); color: #fff; padding: 0.25rem 0.7rem;
    border-radius: 9999px; font-size: 0.7rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.03em;
}}

{scope}.ac1-body {{ padding: 1.25rem; }}
{scope}.ac1-title {{
    font-family: {font_family}; font-size: 1.1rem; font-weight: 700;
    color: var(--text); line-height: 1.3; margin: 0 0 0.5rem;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
{scope}.ac1-excerpt {{
    color: var(--muted); font-size: 0.85rem; line-height: 1.6; margin-bottom: 0.75rem;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}

{scope}.ac1-footer {{
    display: flex; justify-content: space-between; align-items: center;
    font-size: 0.8rem;
}}
{scope}.ac1-writer {{ color: var(--muted); }}
{scope}.ac1-more {{ color: var(--primary); font-weight: 600; }}
"""
    return {"html": html_content, "css": css}
