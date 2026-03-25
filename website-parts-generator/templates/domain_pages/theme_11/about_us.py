"""Theme 11 — About Us: Art Deco Elegance — ornamental framed founder card, values with deco accents, team grid."""

def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("domain_page", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Libre Baskerville, Georgia, serif"
    body_font = s.get("body_family", "Raleway, sans-serif")

    from _shared import _hex_to_rgb_for_rgba
    primary   = s.get("primary",    "#1B1B1B")
    primary_rgb = _hex_to_rgb_for_rgba(primary)
    secondary = s.get("secondary",  "#1E5945")
    bg        = s.get("background", "#F7F1E8")
    surface   = s.get("surface", "#F0E8DB")
    surface2  = s.get("surface2", "#EBE2D3")
    text_col  = s.get("text_primary",   "#1B1B1B")
    muted     = s.get("text_secondary", "#6B6155")
    border    = s.get("border",         "#D4C8B8")
    gold      = s.get("gold",       "#C9A96E")
    gold_rgb  = _hex_to_rgb_for_rgba(gold)
    text_on_primary = s.get("text_on_primary", "#FFFFFF")
    text_on_primary_muted = s.get("text_on_primary_muted", "#B8B0A8")

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
        avatar_html = f'<img src="{html_module.escape(f_avatar)}" alt="{f_name}" class="at11-avatar-img">'
    else:
        initials = "".join(w[0].upper() for w in f_name.split()[:2]) if f_name else "C"
        avatar_html = f'<div class="at11-avatar-ph">{initials}</div>'

    cat_items = ""
    for c in categories[:8]:
        cn = html_module.escape(c.get("name", ""))
        if cn:
            cat_items += f'<span class="at11-chip">{cn}</span>'
    if not cat_items:
        cat_items = '<span class="at11-chip">Quick Dinners</span><span class="at11-chip">Baking</span><span class="at11-chip">Healthy</span>'

    team_html = ""
    if len(writers) > 1:
        cards = ""
        for w in writers[1:4]:
            wn = html_module.escape(str(w.get("name", "")))
            wt = html_module.escape(str(w.get("title", "")))
            wb = html_module.escape(str(w.get("bio", ""))[:130])
            wa = (w.get("avatar") or "").strip()
            if wa and wa.startswith("http"):
                wimg = f'<img src="{html_module.escape(wa)}" alt="{wn}" class="at11-team-av">'
            else:
                wi = "".join(x[0].upper() for x in wn.split()[:2]) if wn else "?"
                wimg = f'<div class="at11-team-av at11-avatar-ph">{wi}</div>'
            cards += f'<div class="at11-team-card">{wimg}<strong class="at11-team-name">{wn}</strong><span class="at11-team-title">{wt}</span><p class="at11-team-bio">{wb}</p></div>'
        team_html = f'<div class="at11-deco-section"><div class="it11-section-head"><span class="it11-section-ornament">&#9671;</span><h2 class="it11-section-title">The Team</h2><span class="it11-section-ornament">&#9671;</span></div><div class="at11-team-grid">{cards}</div></div>'

    VALUE_ITEMS = [
        ("&#9670;", "Heritage Recipes", "We honor culinary traditions while embracing modern techniques."),
        ("&#9670;", "Kitchen-Tested", "Every recipe is refined through multiple tests for perfection."),
        ("&#9670;", "Community Driven", "Our readers inspire and shape the recipes we create."),
    ]
    values_html = "".join(f'<div class="at11-value-card"><div class="at11-value-icon">{ico}</div><h4 class="at11-value-title">{ttl}</h4><p class="at11-value-desc">{dsc}</p></div>' for ico, ttl, dsc in VALUE_ITEMS)

    html_content = f"""
<div class="domain-page dp-t11-about">
  <section class="dp-t11-hero">
    <p class="dp-t11-hero-label">&#9671; About Us &#9671;</p>
    <h1>About <em>{name}</em></h1>
    <p>Where culinary artistry meets timeless elegance.</p>
    <div class="dp-t11-ornament">&#9670;</div>
  </section>
  <div class="at11-body">
    <div class="at11-founder-section">
      <div class="at11-founder-card">
        {avatar_html}
        <div class="at11-founder-info">
          <h2 class="at11-founder-name">{f_name}</h2>
          <p class="at11-founder-title">{f_title}</p>
          <p class="at11-founder-bio">{f_bio}</p>
        </div>
      </div>
      <div class="at11-side-cards">
        <div class="at11-story-card">
          <h3 class="at11-story-title">Our Story</h3>
          <p>Cooking has always been about connection &mdash; a way of bringing people together around the table. {f_name} started {name} to share refined, approachable recipes crafted with genuine care.</p>
        </div>
        <div class="at11-cats-card">
          <h3 class="at11-story-title">What We Cook</h3>
          <div class="at11-chips-wrap">{cat_items}</div>
        </div>
      </div>
    </div>

    <div class="at11-deco-section">
      <div class="it11-section-head"><span class="it11-section-ornament">&#9671;</span><h2 class="it11-section-title">Our Values</h2><span class="it11-section-ornament">&#9671;</span></div>
      <div class="at11-values-grid">{values_html}</div>
    </div>

    <div class="at11-deco-section">
      <div class="it11-section-head"><span class="it11-section-ornament">&#9671;</span><h2 class="it11-section-title">Philosophy</h2><span class="it11-section-ornament">&#9671;</span></div>
      <p class="at11-para">Quality ingredients, refined techniques, tested recipes &mdash; food that honors tradition while embracing the new. No pretension, just genuine culinary craft.</p>
      <p class="at11-para">Whether you&rsquo;re a novice or an experienced cook, every recipe is designed with clear, elegant instructions to guide you.</p>
    </div>

    {team_html}

    <div class="at11-cta-section">
      <div class="at11-cta-text">
        <h2>Ready to begin?</h2>
        <p>Explore our curated collection of refined recipes.</p>
      </div>
      <div class="at11-cta-btns">
        <a href="{base_url}/recipes" class="at11-btn at11-btn-primary">Browse Recipes</a>
        <a href="{base_url}/contact-us" class="at11-btn at11-btn-ghost">Get in Touch</a>
      </div>
    </div>
  </div>
</div>
"""

    css = f"""
{font_import}
.dp-t11-about {{
    --primary: {primary}; --secondary: {secondary}; --bg: {bg};
    --gold: {gold}; --gold-light: rgba({gold_rgb},0.15); --gold-border: rgba({gold_rgb},0.45);
    --text-on-primary: {text_on_primary}; --text-on-primary-muted: {text_on_primary_muted};
    --surface: {surface}; --surface2: {surface2};
    --text: {text_col}; --muted: {muted}; --border: {border};
    --shadow-sm: 0 2px 12px rgba({primary_rgb},0.06); --shadow: 0 6px 28px rgba({primary_rgb},0.10);
    font-family: {body_font}; color: var(--text); background: var(--bg);
}}
.dp-t11-about .dp-t11-hero {{
    background: var(--primary); color: var(--text-on-primary); text-align: center;
    padding: 4.5rem 1.5rem 3.5rem; position: relative;
}}
.dp-t11-about .dp-t11-hero::after {{
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}}
.dp-t11-about .dp-t11-hero-label {{
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.3em; color: var(--gold); margin-bottom: 1rem;
}}
.dp-t11-about .dp-t11-hero h1 {{ font-family: {font_family}; font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 700; margin: 0 0 0.75rem; color: var(--text-on-primary); }}
.dp-t11-about .dp-t11-hero h1 em {{ font-style: italic; color: var(--gold); }}
.dp-t11-about .dp-t11-hero p {{ color: var(--text-on-primary-muted); font-size: 1rem; }}
.dp-t11-about .dp-t11-ornament {{ color: var(--gold); font-size: 0.55rem; margin-top: 1.25rem; }}
.it11-section-head {{ display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 1.5rem; }}
.it11-section-ornament {{ color: var(--gold); font-size: 0.5rem; }}
.it11-section-title {{ font-family: {font_family}; font-size: 1.5rem; font-weight: 700; color: var(--text); margin: 0; text-transform: uppercase; letter-spacing: 0.1em; }}

.at11-body {{ max-width: 1100px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}
.at11-founder-section {{ display: grid; grid-template-columns: 1.3fr 1fr; gap: 1rem; margin-bottom: 2.5rem; }}
.at11-founder-card {{
    background: var(--bg); border: 1px solid var(--border); padding: 2rem;
    display: flex; gap: 1.5rem; align-items: flex-start; box-shadow: var(--shadow-sm);
    position: relative;
}}
.at11-founder-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }}
.at11-avatar-img {{ width: 90px; height: 90px; border-radius: 50%; object-fit: cover; flex-shrink: 0; border: 2px solid var(--gold); }}
.at11-avatar-ph {{ width: 90px; height: 90px; border-radius: 50%; background: var(--primary); color: var(--gold); font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; border: 2px solid var(--gold); }}
.at11-founder-name {{ font-family: {font_family}; font-size: 1.35rem; font-weight: 700; margin: 0 0 0.2rem; }}
.at11-founder-title {{ font-size: 0.75rem; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.6rem; }}
.at11-founder-bio {{ color: var(--muted); font-size: 0.9rem; line-height: 1.65; }}
.at11-side-cards {{ display: flex; flex-direction: column; gap: 1rem; }}
.at11-story-card, .at11-cats-card {{ background: var(--surface); border: 1px solid var(--border); padding: 1.5rem; flex: 1; box-shadow: var(--shadow-sm); }}
.at11-story-title {{ font-family: {font_family}; font-size: 1rem; font-weight: 700; margin: 0 0 0.6rem; text-transform: uppercase; letter-spacing: 0.06em; }}
.at11-story-card p {{ color: var(--muted); font-size: 0.9rem; line-height: 1.7; margin: 0; }}
.at11-chips-wrap {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.at11-chip {{ display: inline-block; border: 1px solid var(--gold-border); color: var(--gold); padding: 4px 12px; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }}
.at11-deco-section {{ margin-bottom: 2.5rem; }}
.at11-para {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin: 0 0 0.75rem; text-align: center; max-width: 700px; margin-left: auto; margin-right: auto; }}
.at11-values-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }}
.at11-value-card {{ background: var(--bg); border: 1px solid var(--border); padding: 1.5rem; text-align: center; transition: all 0.3s; position: relative; }}
.at11-value-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }}
.at11-value-card:hover {{ box-shadow: var(--shadow); transform: translateY(-3px); }}
.at11-value-icon {{ font-size: 1.2rem; color: var(--gold); margin-bottom: 0.75rem; }}
.at11-value-title {{ font-family: {font_family}; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 0.4rem; }}
.at11-value-desc {{ color: var(--muted); font-size: 0.85rem; line-height: 1.55; margin: 0; }}
.at11-team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
.at11-team-card {{ background: var(--bg); border: 1px solid var(--border); padding: 1.5rem; text-align: center; }}
.at11-team-av {{ width: 64px; height: 64px; border-radius: 50%; object-fit: cover; margin: 0 auto 0.6rem; border: 2px solid var(--gold); display: block; }}
.at11-team-name {{ display: block; font-weight: 700; font-size: 1rem; }}
.at11-team-title {{ display: block; font-size: 0.72rem; color: var(--gold); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }}
.at11-team-bio {{ color: var(--muted); font-size: 0.83rem; line-height: 1.5; }}
.at11-cta-section {{
    background: var(--primary); padding: 2.5rem; display: flex;
    align-items: center; justify-content: space-between; gap: 2rem;
    margin-top: 2rem; flex-wrap: wrap; position: relative;
}}
.at11-cta-section::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }}
.at11-cta-text h2 {{ font-family: {font_family}; font-size: 1.5rem; font-weight: 700; color: var(--text-on-primary); margin: 0 0 0.3rem; }}
.at11-cta-text p {{ color: var(--text-on-primary-muted); font-size: 0.95rem; margin: 0; }}
.at11-cta-btns {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}
.at11-btn {{ padding: 0.7rem 1.6rem; text-decoration: none; font-weight: 600; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.1em; transition: all 0.3s; }}
.at11-btn-primary {{ background: var(--gold); color: var(--primary); }}
.at11-btn-primary:hover {{ background: var(--gold); opacity: 0.9; }}
.at11-btn-ghost {{ background: transparent; color: var(--gold); border: 1px solid var(--gold); }}
.at11-btn-ghost:hover {{ background: var(--gold); color: var(--primary); }}
@media (max-width: 900px) {{ .at11-founder-section {{ grid-template-columns: 1fr; }} .at11-values-grid {{ grid-template-columns: 1fr; }} }}
@media (max-width: 600px) {{ .dp-t11-about .dp-t11-hero h1 {{ font-size: 1.8rem; }} .at11-cta-section {{ flex-direction: column; text-align: center; }} .at11-founder-card {{ flex-direction: column; align-items: center; text-align: center; }} }}
"""
    return {"html": html_content, "css": css}
