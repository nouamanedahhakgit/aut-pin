"""Index page 5 — Full-width overlay hero with category icon grid + masonry-style articles."""


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

    bg_style = f'background-image:url({html_module.escape(feat_img)})' if feat_img and feat_img.startswith("http") else ""

    cat_cards = ""
    emojis = ["🥗", "🍝", "🍰", "🥤", "🍕", "🥘", "🧁", "🍲"]
    for i, cat in enumerate(categories[:8]):
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url") or f"{base_url}/categories")
        emoji = emojis[i % len(emojis)]
        if c_name:
            cat_cards += f'<a href="{c_url}" class="idx5-cat-card"><span class="idx5-cat-emoji">{emoji}</span><span class="idx5-cat-name">{c_name}</span></a>'

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".index-page")

    html_content = f"""
<main class="index-page idx5">
  <section class="idx5-hero" style="{bg_style}">
    <div class="idx5-hero-overlay">
      <div class="idx5-hero-content">
        <p class="idx5-hero-label">{domain_name}</p>
        <h1 class="idx5-hero-title">{feat_title}</h1>
        <p class="idx5-hero-excerpt">{feat_excerpt}</p>
        <a href="{feat_url}" class="idx5-hero-btn">Read Recipe</a>
      </div>
    </div>
  </section>

  <section class="idx5-cats">
    <div class="idx5-cats-inner">
      <h2 class="idx5-section-title">Categories</h2>
      <div class="idx5-cat-grid">{cat_cards or '<p>No categories yet</p>'}</div>
    </div>
  </section>

  <section class="idx5-latest">
    <div class="idx5-latest-inner">
      <h2 class="idx5-section-title">Latest Recipes</h2>
      <div class="idx5-grid">{cards_html}</div>
      <div class="idx5-more">
        <a href="{html_module.escape(base_url)}/recipes" class="idx5-more-link">View All Recipes &rarr;</a>
      </div>
    </div>
  </section>
</main>
"""

    css = f"""
{font_import}
{card_css}

.idx5 {{
    --primary: {s.get("primary", "#E07C5E")};
    --secondary: {s.get("secondary", "#D46A4A")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font}; color: var(--text);
}}

.idx5-hero {{
    min-height: 420px; background-size: cover; background-position: center;
    background-color: var(--primary); position: relative;
}}
.idx5-hero-overlay {{
    background: linear-gradient(135deg, rgba(0,0,0,0.65), rgba(0,0,0,0.3));
    min-height: 420px; display: flex; align-items: center; justify-content: center;
    padding: 3rem 1.5rem; text-align: center;
}}
.idx5-hero-content {{ max-width: 700px; color: #fff; }}
.idx5-hero-label {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.8; margin-bottom: 0.75rem; }}
.idx5-hero-title {{ font-family: {font_family}; font-size: 3rem; font-weight: 700; margin: 0 0 1rem; line-height: 1.2; }}
.idx5-hero-excerpt {{ font-size: 1.1rem; opacity: 0.85; line-height: 1.6; margin-bottom: 1.5rem; }}
.idx5-hero-btn {{
    display: inline-block; background: var(--primary); color: #fff;
    padding: 0.85rem 2rem; border-radius: 9999px; text-decoration: none;
    font-weight: 600; font-size: 0.95rem; transition: opacity 0.2s;
}}
.idx5-hero-btn:hover {{ opacity: 0.85; }}

.idx5-section-title {{ font-family: {font_family}; font-size: 1.75rem; font-weight: 700; text-align: center; margin-bottom: 1.5rem; }}

.idx5-cats {{ background: color-mix(in srgb, var(--primary) 6%, var(--bg)); padding: 3rem 0; }}
.idx5-cats-inner {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }}
.idx5-cat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }}
.idx5-cat-card {{
    display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
    padding: 1.25rem 0.75rem; background: var(--bg); border-radius: 12px;
    text-decoration: none; color: var(--text); transition: all 0.2s;
    border: 1px solid var(--border);
}}
.idx5-cat-card:hover {{ border-color: var(--primary); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
.idx5-cat-emoji {{ font-size: 2rem; }}
.idx5-cat-name {{ font-size: 0.85rem; font-weight: 600; }}

.idx5-latest {{ padding: 3rem 0 4rem; }}
.idx5-latest-inner {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }}
.idx5-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}

.idx5-more {{ text-align: center; margin-top: 2rem; }}
.idx5-more-link {{ color: var(--primary); text-decoration: none; font-weight: 600; font-size: 1rem; }}
.idx5-more-link:hover {{ opacity: 0.7; }}

@media (max-width: 900px) {{
    .idx5-cat-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .idx5-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .idx5-hero-title {{ font-size: 2.2rem; }}
}}
@media (max-width: 600px) {{
    .idx5-cat-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .idx5-grid {{ grid-template-columns: 1fr; }}
    .idx5-hero {{ min-height: 320px; }}
    .idx5-hero-overlay {{ min-height: 320px; }}
    .idx5-hero-title {{ font-size: 1.8rem; }}
}}
"""
    return {"html": html_content, "css": css}
