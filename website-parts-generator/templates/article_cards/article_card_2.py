"""Article Card 2 — Horizontal card (image left, content right) with overlay gradient."""


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
    excerpt = html_module.escape((article.get("excerpt") or "")[:180])
    category = html_module.escape((article.get("category") or article.get("category_name") or "")[:40])
    writer_name = html_module.escape(str((article.get("writer") or {}).get("name", "")))
    date_str = html_module.escape(str(article.get("date") or article.get("published") or ""))

    if img and img.startswith("http"):
        img_tag = f'<img src="{html_module.escape(img)}" alt="{title}" class="ac2-img">'
    else:
        img_tag = '<div class="ac2-placeholder"><span>🍽️</span></div>'

    cat_badge = f'<span class="ac2-cat">{category}</span>' if category else ""
    excerpt_html = f'<p class="ac2-excerpt">{excerpt}</p>' if show_excerpt and excerpt else ""

    meta_parts = []
    if writer_name:
        meta_parts.append(f'<span class="ac2-writer">{writer_name}</span>')
    if date_str:
        meta_parts.append(f'<span class="ac2-date">{date_str}</span>')
    meta_html = f'<div class="ac2-meta">{"<span class=\"ac2-sep\">&middot;</span>".join(meta_parts)}</div>' if meta_parts else ""

    scope = f"{scope_prefix} " if scope_prefix else ""

    html_content = f"""
<article class="article-card ac2">
  <a href="{url}" class="ac2-link">
    <div class="ac2-media">{img_tag}</div>
    <div class="ac2-body">
      {cat_badge}
      <h3 class="ac2-title">{title}</h3>
      {excerpt_html}
      {meta_html}
      <span class="ac2-read">Read Recipe &rarr;</span>
    </div>
  </a>
</article>
"""

    css = f"""
{font_import}

{scope}.ac2 {{
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
{scope}.ac2:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}}

{scope}.ac2-link {{
    text-decoration: none; color: inherit;
    display: grid; grid-template-columns: 200px 1fr;
    min-height: 180px;
}}

{scope}.ac2-media {{ position: relative; overflow: hidden; }}
{scope}.ac2-img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
{scope}.ac2-placeholder {{
    width: 100%; height: 100%; background: var(--border);
    display: flex; align-items: center; justify-content: center; font-size: 2rem;
}}

{scope}.ac2-body {{
    padding: 1.25rem; display: flex; flex-direction: column; justify-content: center;
}}

{scope}.ac2-cat {{
    display: inline-block; color: var(--primary); font-size: 0.7rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}}

{scope}.ac2-title {{
    font-family: {font_family}; font-size: 1.05rem; font-weight: 700;
    color: var(--text); line-height: 1.35; margin: 0 0 0.4rem;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}

{scope}.ac2-excerpt {{
    color: var(--muted); font-size: 0.85rem; line-height: 1.6;
    margin-bottom: 0.5rem;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}

{scope}.ac2-meta {{
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 0.75rem; color: var(--muted); margin-bottom: 0.5rem;
}}
{scope}.ac2-sep {{ opacity: 0.5; }}

{scope}.ac2-read {{
    color: var(--primary); font-weight: 600; font-size: 0.85rem;
    margin-top: auto;
}}

@media (max-width: 600px) {{
    {scope}.ac2-link {{
        grid-template-columns: 1fr;
    }}
    {scope}.ac2-media {{
        height: 180px;
    }}
}}
"""
    return {"html": html_content, "css": css}
