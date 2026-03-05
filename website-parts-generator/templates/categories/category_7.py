"""Category page 7 — Minimal top bar title + list-style articles with sidebar filter."""


def generate(config: dict) -> dict:
    from shared_style import extract_style, part_font
    from shared_article_card import render_cards
    import html as html_module

    s = extract_style(config)
    pf = part_font("category", config)
    font_import = f"@import url('{pf.get('cdn')}');" if pf.get("cdn") else ""
    font_family = pf.get("family") or "'Playfair Display', serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    category_name = html_module.escape(config.get("category_name", "Recipes"))
    categories = config.get("categories", [])
    articles = config.get("articles", [])
    total = config.get("total", len(articles))
    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")

    other_cats = ""
    for cat in categories[:10]:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or "#")
        if c_name:
            active = " cat7-active" if c_name.lower() == category_name.lower() else ""
            other_cats += f'<a href="{c_url}" class="cat7-side-link{active}">{c_name}</a>'

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".category-page")

    html_content = f"""
<main class="category-page category-7">
  <div class="cat7-header">
    <div class="cat7-header-inner">
      <nav class="cat7-breadcrumb">
        <a href="{html_module.escape(base_url or '/')}">Home</a> &rsaquo; <span>{category_name}</span>
      </nav>
      <h1 class="cat7-title">{category_name}</h1>
      <p class="cat7-count">{total} recipe{"s" if total != 1 else ""} in this category</p>
    </div>
  </div>
  <div class="cat7-body">
    <aside class="cat7-sidebar">
      <h3 class="cat7-side-title">All Categories</h3>
      <div class="cat7-side-links">{other_cats or '<span>No categories</span>'}</div>
    </aside>
    <div class="cat7-content">
      <div class="cat7-grid">{cards_html}</div>
    </div>
  </div>
</main>
"""

    css = f"""
{font_import}
{card_css}

.category-7 {{
    --primary: {s.get("primary", "#E07C5E")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font}; background: var(--bg);
}}

.cat7-header {{
    border-bottom: 1px solid var(--border);
    background: color-mix(in srgb, var(--primary) 4%, var(--bg));
    padding: 2rem 1.5rem 1.5rem;
}}
.cat7-header-inner {{ max-width: 1200px; margin: 0 auto; }}
.cat7-breadcrumb {{ font-size: 0.8rem; color: var(--muted); margin-bottom: 0.75rem; }}
.cat7-breadcrumb a {{ color: var(--primary); text-decoration: none; }}
.cat7-breadcrumb span {{ color: var(--text); }}
.cat7-title {{ font-family: {font_family}; font-size: 2.25rem; font-weight: 700; margin: 0 0 0.25rem; color: var(--text); }}
.cat7-count {{ color: var(--muted); font-size: 0.9rem; }}

.cat7-body {{
    max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem 4rem;
    display: grid; grid-template-columns: 220px 1fr; gap: 2.5rem;
}}

.cat7-sidebar {{ position: sticky; top: 100px; align-self: start; }}
.cat7-side-title {{ font-family: {font_family}; font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 0.75rem; }}
.cat7-side-links {{ display: flex; flex-direction: column; gap: 0.25rem; }}
.cat7-side-link {{
    display: block; padding: 0.5rem 0.75rem; border-radius: 6px;
    text-decoration: none; color: var(--muted); font-size: 0.9rem;
    font-weight: 500; transition: all 0.2s;
}}
.cat7-side-link:hover {{ background: color-mix(in srgb, var(--primary) 10%, transparent); color: var(--primary); }}
.cat7-side-link.cat7-active {{
    background: color-mix(in srgb, var(--primary) 12%, transparent);
    color: var(--primary); font-weight: 600;
}}

.cat7-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }}

@media (max-width: 900px) {{
    .cat7-body {{ grid-template-columns: 1fr; gap: 1.5rem; }}
    .cat7-sidebar {{ position: static; }}
    .cat7-side-links {{ flex-direction: row; flex-wrap: wrap; gap: 0.4rem; }}
    .cat7-side-link {{ padding: 0.4rem 0.8rem; }}
}}
@media (max-width: 600px) {{
    .cat7-grid {{ grid-template-columns: 1fr; }}
    .cat7-title {{ font-size: 1.6rem; }}
}}
"""
    return {"html": html_content, "css": css}
