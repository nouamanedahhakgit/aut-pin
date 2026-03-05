"""Category page 6 — Banner hero with gradient overlay + clean article grid."""


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
    articles = config.get("articles", [])
    total = config.get("total", len(articles))

    cards_html, card_css = render_cards(articles, config, show_excerpt=True, scope_prefix=".category-page")

    html_content = f"""
<main class="category-page category-6">
  <section class="cat6-hero">
    <div class="cat6-hero-inner">
      <span class="cat6-badge">Category</span>
      <h1 class="cat6-title">{category_name}</h1>
      <p class="cat6-count">{total} recipe{"s" if total != 1 else ""}</p>
    </div>
  </section>
  <div class="cat6-body">
    <div class="cat6-grid">{cards_html}</div>
  </div>
</main>
"""

    css = f"""
{font_import}
{card_css}

.category-6 {{
    --primary: {s.get("primary", "#E07C5E")};
    --secondary: {s.get("secondary", "#D46A4A")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font}; background: var(--bg);
}}

.cat6-hero {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; text-align: center; padding: 3.5rem 1.5rem 3rem;
}}
.cat6-hero-inner {{ max-width: 800px; margin: 0 auto; }}
.cat6-badge {{
    display: inline-block; background: rgba(255,255,255,0.2);
    padding: 0.3rem 1rem; border-radius: 9999px; font-size: 0.75rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;
}}
.cat6-title {{ font-family: {font_family}; font-size: 2.75rem; font-weight: 700; margin: 0 0 0.5rem; }}
.cat6-count {{ opacity: 0.8; font-size: 1rem; }}

.cat6-body {{ max-width: 1200px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}
.cat6-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}

@media (max-width: 900px) {{
    .cat6-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .cat6-title {{ font-size: 2rem; }}
}}
@media (max-width: 600px) {{
    .cat6-grid {{ grid-template-columns: 1fr; }}
    .cat6-title {{ font-size: 1.6rem; }}
    .cat6-hero {{ padding: 2.5rem 1rem 2rem; }}
}}
"""
    return {"html": html_content, "css": css}
