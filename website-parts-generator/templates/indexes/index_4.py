"""Index page 4 — Split hero (image left, text right) + category pills + article grid."""


def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font
    from shared_article_card import render_cards

    s = extract_style(config)
    pf = part_font("index", config)
    font_import = f"@import url('{pf.get('cdn')}');" if pf.get("cdn") else ""
    font_family = pf.get("family") or "'Playfair Display', serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    articles = config.get("articles", [])
    categories = config.get("categories", [])
    domain_name = html_module.escape(s.get("domain_name", "Recipe Blog"))

    featured = articles[0] if articles else None
    if featured:
        feat_img = (featured.get("main_image") or featured.get("image") or "").strip()
        feat_title = html_module.escape((featured.get("title") or "Recipe")[:120])
        feat_url = html_module.escape(featured.get("url") or "#")
        feat_excerpt = html_module.escape((featured.get("excerpt") or "")[:200])
    else:
        feat_img, feat_title, feat_url = "", f"Welcome to {domain_name}", "#"
        feat_excerpt = "Discover delicious recipes for every occasion."

    if feat_img and feat_img.startswith("http"):
        hero_img = f'<img src="{html_module.escape(feat_img)}" alt="{feat_title}" class="idx4-hero-img">'
    else:
        hero_img = '<div class="idx4-hero-placeholder"><span>🍽️</span></div>'

    cat_pills = ""
    for cat in categories[:8]:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or f"{base_url}/categories")
        if c_name:
            cat_pills += f'<a href="{c_url}" class="idx4-pill">{c_name}</a>'

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".index-page")

    html_content = f"""
<main class="index-page idx4">
  <section class="idx4-hero">
    <div class="idx4-hero-image">{hero_img}</div>
    <div class="idx4-hero-text">
      <span class="idx4-badge">Featured Recipe</span>
      <h1 class="idx4-hero-title"><a href="{feat_url}">{feat_title}</a></h1>
      <p class="idx4-hero-excerpt">{feat_excerpt}</p>
      <a href="{feat_url}" class="idx4-hero-btn">Read Recipe &rarr;</a>
    </div>
  </section>

  <section class="idx4-cats">
    <h2 class="idx4-section-title">Browse Categories</h2>
    <div class="idx4-pills">{cat_pills or '<p class="idx4-no-cats">No categories yet</p>'}</div>
  </section>

  <section class="idx4-latest">
    <h2 class="idx4-section-title">Latest Recipes</h2>
    <div class="idx4-grid">{cards_html}</div>
    <div class="idx4-more">
      <a href="{html_module.escape(base_url)}/recipes" class="idx4-more-btn">View All Recipes &rarr;</a>
    </div>
  </section>
</main>
"""

    css = f"""
{font_import}
{card_css}

.idx4 {{
    --primary: {s.get("primary", "#E07C5E")};
    --secondary: {s.get("secondary", "#D46A4A")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font}; color: var(--text); background: var(--bg);
}}

.idx4-hero {{
    max-width: 1200px; margin: 2rem auto; padding: 0 1.5rem;
    display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: center;
}}
.idx4-hero-img {{ width: 100%; border-radius: 16px; object-fit: cover; aspect-ratio: 4/3; }}
.idx4-hero-placeholder {{
    width: 100%; aspect-ratio: 4/3; border-radius: 16px;
    background: var(--border); display: flex; align-items: center; justify-content: center;
    font-size: 4rem;
}}
.idx4-badge {{
    display: inline-block; background: var(--primary); color: #fff;
    padding: 0.3rem 0.9rem; border-radius: 9999px; font-size: 0.75rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;
}}
.idx4-hero-title {{ font-family: {font_family}; font-size: 2.5rem; font-weight: 700; line-height: 1.2; margin: 0 0 1rem; }}
.idx4-hero-title a {{ text-decoration: none; color: var(--text); transition: color 0.2s; }}
.idx4-hero-title a:hover {{ color: var(--primary); }}
.idx4-hero-excerpt {{ color: var(--muted); font-size: 1.05rem; line-height: 1.7; margin-bottom: 1.5rem; }}
.idx4-hero-btn {{
    display: inline-block; background: var(--primary); color: #fff;
    padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none;
    font-weight: 600; font-size: 0.95rem; transition: opacity 0.2s;
}}
.idx4-hero-btn:hover {{ opacity: 0.85; }}

.idx4-section-title {{ font-family: {font_family}; font-size: 1.75rem; font-weight: 700; text-align: center; margin-bottom: 1.5rem; }}

.idx4-cats {{ max-width: 1200px; margin: 3rem auto; padding: 0 1.5rem; text-align: center; }}
.idx4-pills {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 0.6rem; }}
.idx4-pill {{
    padding: 0.5rem 1.2rem; border-radius: 9999px;
    border: 2px solid var(--border); color: var(--text);
    text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: all 0.2s;
}}
.idx4-pill:hover {{ border-color: var(--primary); color: var(--primary); }}

.idx4-latest {{ max-width: 1200px; margin: 3rem auto; padding: 0 1.5rem; }}
.idx4-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}
.idx4-more {{ text-align: center; margin-top: 2rem; }}
.idx4-more-btn {{
    color: var(--primary); text-decoration: none; font-weight: 600;
    font-size: 1rem; transition: opacity 0.2s;
}}
.idx4-more-btn:hover {{ opacity: 0.7; }}

@media (max-width: 900px) {{
    .idx4-hero {{ grid-template-columns: 1fr; gap: 1.5rem; }}
    .idx4-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 600px) {{
    .idx4-grid {{ grid-template-columns: 1fr; }}
    .idx4-hero-title {{ font-size: 1.8rem; }}
}}
"""
    return {"html": html_content, "css": css}
