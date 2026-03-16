"""Theme 10 — About Us: Bento Fresh — bento-style info cards, team grid, clean white."""

def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("domain_page", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Fraunces, Georgia, serif"
    body_font = s.get("body_family", "DM Sans, Inter, sans-serif")

    primary   = s.get("primary",    "#00BFA5")
    secondary = s.get("secondary",  "#FF6B6B")
    bg        = s.get("background", "#FFFFFF")
    text_col  = s.get("text_primary",   "#111827")
    muted     = s.get("text_secondary", "#6B7280")
    border    = s.get("border",         "#E5E7EB")

    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = html_module.escape((config.get("base_url") or "/").rstrip("/"))
    writers = config.get("writers") or []
    categories = config.get("categories") or []

    founder = writers[0] if writers else {}
    f_name = html_module.escape(str(founder.get("name", "Our Chef")))
    f_title = html_module.escape(str(founder.get("title", "Founder & Recipe Creator")))
    f_bio = html_module.escape(str(founder.get("bio", f"The passionate cook behind {name}.")))
    f_avatar = (founder.get("avatar") or "").strip()
    if f_avatar and f_avatar.startswith("http"):
        avatar_html = f'<img src="{html_module.escape(f_avatar)}" alt="{f_name}" class="at10-avatar-img">'
    else:
        initials = "".join(w[0].upper() for w in f_name.split()[:2]) if f_name else "C"
        avatar_html = f'<div class="at10-avatar-ph">{initials}</div>'

    cat_chips = ""
    for c in categories[:8]:
        cn = html_module.escape(c.get("name", ""))
        if cn:
            cat_chips += f'<span class="at10-chip">{cn}</span>'
    if not cat_chips:
        cat_chips = '<span class="at10-chip">Quick Dinners</span><span class="at10-chip">Baking</span><span class="at10-chip">Healthy</span><span class="at10-chip">Comfort Food</span>'

    team_html = ""
    if len(writers) > 1:
        cards = ""
        for w in writers[1:4]:
            wn = html_module.escape(str(w.get("name", "")))
            wt = html_module.escape(str(w.get("title", "")))
            wb = html_module.escape(str(w.get("bio", ""))[:130])
            wa = (w.get("avatar") or "").strip()
            if wa and wa.startswith("http"):
                wimg = f'<img src="{html_module.escape(wa)}" alt="{wn}" class="at10-team-av">'
            else:
                wi = "".join(x[0].upper() for x in wn.split()[:2]) if wn else "?"
                wimg = f'<div class="at10-team-av at10-avatar-ph">{wi}</div>'
            cards += f'<div class="at10-team-card">{wimg}<strong class="at10-team-name">{wn}</strong><span class="at10-team-title">{wt}</span><p class="at10-team-bio">{wb}</p></div>'
        team_html = f'<div class="at10-bento-section"><h2 class="at10-h2">Meet the Team</h2><div class="at10-team-grid">{cards}</div></div>'

    VALUE_ITEMS = [
        ("&#127793;", "Fresh Ingredients", "We believe in seasonal, locally sourced produce for the best flavour."),
        ("&#128200;", "Kitchen-Tested", "Every recipe is tested multiple times in a real home kitchen."),
        ("&#128101;", "Community Driven", "Our readers shape the blog — your feedback makes us better."),
    ]
    values_html = "".join(f'<div class="at10-value-card"><div class="at10-value-icon">{ico}</div><h4 class="at10-value-title">{ttl}</h4><p class="at10-value-desc">{dsc}</p></div>' for ico, ttl, dsc in VALUE_ITEMS)

    html_content = f"""
<div class="domain-page dp-t10-about">
  <section class="at10-hero">
    <div class="at10-hero-inner">
      <span class="at10-hero-badge">&#128075; Nice to meet you</span>
      <h1>About <em>{name}</em></h1>
      <p>Where every recipe tells a story and every dish brings people together.</p>
    </div>
  </section>
  <div class="at10-body">
    <div class="at10-founder-bento">
      <div class="at10-founder-card">
        {avatar_html}
        <div class="at10-founder-info">
          <h2 class="at10-founder-name">{f_name}</h2>
          <p class="at10-founder-title">{f_title}</p>
          <p class="at10-founder-bio">{f_bio}</p>
        </div>
      </div>
      <div class="at10-side-bento">
        <div class="at10-story-card">
          <h3 class="at10-story-title">Our Story</h3>
          <p>Cooking has always been more than a hobby &mdash; it&rsquo;s a way of connecting with the people we love. {f_name} started {name} to share approachable, wholesome recipes made with real care.</p>
        </div>
        <div class="at10-cats-card">
          <h3 class="at10-story-title">What We Cook</h3>
          <div class="at10-chips-wrap">{cat_chips}</div>
        </div>
      </div>
    </div>

    <div class="at10-bento-section">
      <h2 class="at10-h2">Why We Cook</h2>
      <div class="at10-values-grid">{values_html}</div>
    </div>

    <div class="at10-bento-section">
      <h2 class="at10-h2">Our Philosophy</h2>
      <p class="at10-para">Fresh ingredients, simple techniques, tested recipes &mdash; food that works in your kitchen every time. No fuss, no elaborate equipment.</p>
      <p class="at10-para">Whether you&rsquo;re a beginner or a confident cook, there&rsquo;s something here for you. Clear instructions and helpful tips help you cook with real confidence.</p>
    </div>

    {team_html}

    <div class="at10-cta-bento">
      <div class="at10-cta-text">
        <h2>Ready to start cooking?</h2>
        <p>Explore hundreds of tested, trusted recipes.</p>
      </div>
      <div class="at10-cta-btns">
        <a href="{base_url}/recipes" class="at10-btn at10-btn-primary">Browse Recipes</a>
        <a href="{base_url}/contact-us" class="at10-btn at10-btn-ghost">Say Hello</a>
      </div>
    </div>
  </div>
</div>
"""

    css = f"""
{font_import}
.dp-t10-about {{
    --primary: {primary}; --secondary: {secondary}; --bg: {bg};
    --surface: #F8FFFE; --surface2: #F0FAF8;
    --mint-pale: rgba(0,191,165,0.08); --mint-border: rgba(0,191,165,0.25);
    --text: {text_col}; --muted: {muted}; --border: {border};
    --shadow-sm: 0 1px 8px rgba(0,0,0,0.05); --shadow: 0 4px 20px rgba(0,0,0,0.08);
    --radius: 16px; --radius-lg: 24px;
    font-family: {body_font}; color: var(--text); background: var(--bg);
}}
.at10-hero {{
    background: var(--surface2); border-bottom: 1px solid var(--border);
    padding: 4.5rem 1.5rem 3.5rem; text-align: center;
}}
.at10-hero-inner {{ max-width: 700px; margin: 0 auto; }}
.at10-hero-badge {{
    display: inline-block; background: var(--mint-pale); border: 1px solid var(--mint-border);
    color: var(--primary); padding: 6px 16px; border-radius: 50px;
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;
}}
.at10-hero h1 {{ font-family: {font_family}; font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 700; margin: 0 0 0.75rem; color: var(--text); }}
.at10-hero h1 em {{ font-style: italic; color: var(--primary); }}
.at10-hero p {{ color: var(--muted); font-size: 1.05rem; }}

.at10-body {{ max-width: 1100px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}

.at10-founder-bento {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 1rem; margin-bottom: 2rem; }}
.at10-founder-card {{
    background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius-lg);
    padding: 2rem; display: flex; gap: 1.5rem; align-items: flex-start;
    box-shadow: var(--shadow-sm); border-top: 4px solid var(--primary);
}}
.at10-avatar-img {{ width: 90px; height: 90px; border-radius: 50%; object-fit: cover; flex-shrink: 0; border: 2px solid var(--mint-border); }}
.at10-avatar-ph {{
    width: 90px; height: 90px; border-radius: 50%; background: var(--primary); color: #fff;
    font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.at10-founder-name {{ font-family: {font_family}; font-size: 1.4rem; font-weight: 700; margin: 0 0 0.2rem; }}
.at10-founder-title {{ font-size: 0.8rem; font-weight: 700; color: var(--primary); text-transform: uppercase; letter-spacing: 0.07em; display: block; margin-bottom: 0.6rem; }}
.at10-founder-bio {{ color: var(--muted); font-size: 0.9rem; line-height: 1.65; }}

.at10-side-bento {{ display: flex; flex-direction: column; gap: 1rem; }}
.at10-story-card, .at10-cats-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.5rem; flex: 1; box-shadow: var(--shadow-sm);
}}
.at10-story-title {{ font-family: {font_family}; font-size: 1.1rem; font-weight: 700; margin: 0 0 0.6rem; color: var(--text); }}
.at10-story-card p {{ color: var(--muted); font-size: 0.9rem; line-height: 1.7; margin: 0; }}

.at10-chips-wrap {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.at10-chip {{
    display: inline-block; background: var(--mint-pale); border: 1px solid var(--mint-border);
    color: var(--primary); padding: 4px 12px; border-radius: 50px; font-size: 0.78rem; font-weight: 600;
}}

.at10-bento-section {{ margin-bottom: 2.5rem; }}
.at10-h2 {{ font-family: {font_family}; font-size: 1.6rem; font-weight: 700; color: var(--text); margin: 0 0 1.25rem; display: flex; align-items: center; gap: 10px; }}
.at10-h2::before {{ content: ''; display: inline-block; width: 5px; height: 1.2em; background: var(--primary); border-radius: 4px; flex-shrink: 0; }}
.at10-para {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin: 0 0 0.75rem; }}

.at10-values-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }}
.at10-value-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; transition: all 0.25s; }}
.at10-value-card:hover {{ box-shadow: var(--shadow); transform: translateY(-3px); border-color: var(--mint-border); }}
.at10-value-icon {{ font-size: 1.8rem; margin-bottom: 0.75rem; }}
.at10-value-title {{ font-family: {font_family}; font-size: 1rem; font-weight: 700; color: var(--text); margin: 0 0 0.4rem; }}
.at10-value-desc {{ color: var(--muted); font-size: 0.85rem; line-height: 1.55; margin: 0; }}

.at10-team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
.at10-team-card {{ background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; text-align: center; }}
.at10-team-av {{ width: 64px; height: 64px; border-radius: 50%; object-fit: cover; margin: 0 auto 0.6rem; border: 2px solid var(--mint-border); display: block; }}
.at10-team-name {{ display: block; font-weight: 700; font-size: 1rem; color: var(--text); margin-bottom: 0.15rem; }}
.at10-team-title {{ display: block; font-size: 0.75rem; color: var(--primary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }}
.at10-team-bio {{ color: var(--muted); font-size: 0.83rem; line-height: 1.5; }}

.at10-cta-bento {{
    background: var(--surface2); border: 1.5px solid var(--mint-border); border-radius: var(--radius-lg);
    padding: 2.5rem; display: flex; align-items: center; justify-content: space-between; gap: 2rem;
    margin-top: 2rem; flex-wrap: wrap;
}}
.at10-cta-text h2 {{ font-family: {font_family}; font-size: 1.6rem; font-weight: 700; color: var(--text); margin: 0 0 0.3rem; }}
.at10-cta-text p {{ color: var(--muted); font-size: 0.95rem; margin: 0; }}
.at10-cta-btns {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}
.at10-btn {{ padding: 0.7rem 1.6rem; border-radius: 50px; text-decoration: none; font-weight: 700; font-size: 0.9rem; transition: all 0.25s; }}
.at10-btn-primary {{ background: var(--primary); color: #fff; box-shadow: 0 2px 12px rgba(0,191,165,0.3); }}
.at10-btn-primary:hover {{ background: #00997F; transform: translateY(-2px); }}
.at10-btn-ghost {{ background: transparent; color: var(--text); border: 1.5px solid var(--border); }}
.at10-btn-ghost:hover {{ border-color: var(--primary); color: var(--primary); }}

@media (max-width: 900px) {{
    .at10-founder-bento {{ grid-template-columns: 1fr; }}
    .at10-values-grid {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 600px) {{
    .at10-hero h1 {{ font-size: 1.8rem; }}
    .at10-cta-bento {{ flex-direction: column; }}
    .at10-founder-card {{ flex-direction: column; align-items: center; text-align: center; }}
}}
"""
    return {"html": html_content, "css": css}
