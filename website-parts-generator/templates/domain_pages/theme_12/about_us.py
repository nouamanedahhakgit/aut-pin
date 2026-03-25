"""Theme 12 — About Us: Candy Pop — playful founder card, colorful values, bouncy team grid."""

def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("domain_page", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Nunito, sans-serif"
    body_font = s.get("body_family", "Quicksand, sans-serif")

    primary   = s.get("primary",    "#FF85A1")
    secondary = s.get("secondary",  "#89CFF0")
    bg        = s.get("background", "#FFFFFF")
    text_col  = s.get("text_primary",   "#2D1F3D")
    muted     = s.get("text_secondary", "#7B6B8A")
    border    = s.get("border",         "#F0E4F6")

    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = html_module.escape((config.get("base_url") or "/").rstrip("/"))
    writers = config.get("writers") or []
    categories = config.get("categories") or []

    founder = writers[0] if writers else {}
    f_name = html_module.escape(str(founder.get("name", "Our Chef")))
    f_title = html_module.escape(str(founder.get("title", "Founder & Recipe Creator")))
    f_bio = html_module.escape(str(founder.get("bio", f"The fun-loving cook behind {name}.")))
    f_avatar = (founder.get("avatar") or "").strip()
    if f_avatar and f_avatar.startswith("http"):
        avatar_html = f'<img src="{html_module.escape(f_avatar)}" alt="{f_name}" class="at12-avatar-img">'
    else:
        initials = "".join(w[0].upper() for w in f_name.split()[:2]) if f_name else "C"
        avatar_html = f'<div class="at12-avatar-ph">{initials}</div>'

    cat_chips = ""
    for c in categories[:8]:
        cn = html_module.escape(c.get("name", ""))
        if cn:
            cat_chips += f'<span class="at12-chip">{cn}</span>'
    if not cat_chips:
        cat_chips = '<span class="at12-chip">Quick Dinners</span><span class="at12-chip">Baking</span><span class="at12-chip">Healthy</span>'

    team_html = ""
    if len(writers) > 1:
        cards = ""
        for w in writers[1:4]:
            wn = html_module.escape(str(w.get("name", "")))
            wt = html_module.escape(str(w.get("title", "")))
            wb = html_module.escape(str(w.get("bio", ""))[:130])
            wa = (w.get("avatar") or "").strip()
            if wa and wa.startswith("http"):
                wimg = f'<img src="{html_module.escape(wa)}" alt="{wn}" class="at12-team-av">'
            else:
                wi = "".join(x[0].upper() for x in wn.split()[:2]) if wn else "?"
                wimg = f'<div class="at12-team-av at12-avatar-ph">{wi}</div>'
            cards += f'<div class="at12-team-card">{wimg}<strong class="at12-team-name">{wn}</strong><span class="at12-team-title">{wt}</span><p class="at12-team-bio">{wb}</p></div>'
        team_html = f'<div class="at12-section"><h2 class="at12-sec-title">&#128101; The Team</h2><div class="at12-team-grid">{cards}</div></div>'

    COLORS = ["#FF85A1", "#89CFF0", "#A7F3D0", "#C4B5FD"]
    VALUE_ITEMS = [
        ("&#127793;", "Fresh & Fun", "Seasonal ingredients, colorful presentation, joy in every bite!", COLORS[0]),
        ("&#128200;", "Totally Tested", "Every recipe is tested in real kitchens by real people!", COLORS[1]),
        ("&#128101;", "Community Love", "Our readers are our biggest inspiration. You make us better!", COLORS[2]),
    ]
    values_html = "".join(f'<div class="at12-value-card" style="--val-color:{color}"><div class="at12-value-icon">{ico}</div><h4 class="at12-value-title">{ttl}</h4><p class="at12-value-desc">{dsc}</p></div>' for ico, ttl, dsc, color in VALUE_ITEMS)

    html_content = f"""
<div class="domain-page dp-t12-about">
  <section class="dp-t12-hero">
    <div class="dp-t12-hero-blob1"></div>
    <div class="dp-t12-hero-blob2"></div>
    <span class="dp-t12-hero-badge">&#128075; Hey there!</span>
    <h1>About <em>{name}</em></h1>
    <p>Where every recipe is a colorful little adventure!</p>
  </section>
  <div class="at12-body">
    <div class="at12-founder-section">
      <div class="at12-founder-card">
        {avatar_html}
        <div class="at12-founder-info">
          <h2 class="at12-founder-name">{f_name}</h2>
          <p class="at12-founder-title">{f_title}</p>
          <p class="at12-founder-bio">{f_bio}</p>
        </div>
      </div>
      <div class="at12-side-cards">
        <div class="at12-story-card">
          <h3 class="at12-story-title">&#128218; Our Story</h3>
          <p>Cooking should be fun, not stressful! {f_name} started {name} to share easy, joyful recipes that make everyone smile.</p>
        </div>
        <div class="at12-cats-card">
          <h3 class="at12-story-title">&#127860; What We Cook</h3>
          <div class="at12-chips-wrap">{cat_chips}</div>
        </div>
      </div>
    </div>

    <div class="at12-section">
      <h2 class="at12-sec-title">&#128147; Why We Cook</h2>
      <div class="at12-values-grid">{values_html}</div>
    </div>

    <div class="at12-section">
      <h2 class="at12-sec-title">&#10024; Philosophy</h2>
      <p class="at12-para">Colorful, simple, delicious &mdash; food made with love and served with joy. No complicated steps, just real good cooking!</p>
      <p class="at12-para">Whether you&rsquo;re a total beginner or a seasoned pro, we&rsquo;ve got something fun for you.</p>
    </div>

    {team_html}

    <div class="at12-cta-section">
      <div class="at12-cta-text">
        <h2>Ready to cook something amazing? &#127881;</h2>
        <p>Explore our colorful collection of tested recipes!</p>
      </div>
      <div class="at12-cta-btns">
        <a href="{base_url}/recipes" class="at12-btn at12-btn-primary">Browse Recipes &#10024;</a>
        <a href="{base_url}/contact-us" class="at12-btn at12-btn-ghost">Say Hi! &#128075;</a>
      </div>
    </div>
  </div>
</div>
"""

    css = f"""
{font_import}
.dp-t12-about {{
    --primary: {primary}; --secondary: {secondary}; --bg: {bg};
    --accent: #A7F3D0; --lavender: #C4B5FD; --yellow: #FDE68A;
    --surface: #FFF5F7; --surface2: #FFF0F3;
    --pink-pale: rgba(255,133,161,0.1); --pink-border: rgba(255,133,161,0.3);
    --blue-pale: rgba(137,207,240,0.15);
    --text: {text_col}; --muted: {muted}; --border: {border};
    --shadow-sm: 0 2px 12px rgba(45,31,61,0.06); --shadow: 0 6px 28px rgba(45,31,61,0.10);
    --radius: 20px; --radius-lg: 28px;
    font-family: {body_font}; color: var(--text); background: var(--bg);
}}
@keyframes t12-blob-morph {{ 0%,100% {{ border-radius: 60% 40% 30% 70%/60% 30% 70% 40%; }} 50% {{ border-radius: 30% 60% 70% 40%/50% 60% 30% 60%; }} }}
.dp-t12-about .dp-t12-hero {{
    background: linear-gradient(145deg, var(--surface2), var(--blue-pale), var(--surface));
    text-align: center; padding: 4.5rem 1.5rem 3.5rem; position: relative; overflow: hidden;
    border-bottom: 4px solid transparent;
    border-image: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent), var(--lavender)) 1;
}}
.dp-t12-hero-blob1, .dp-t12-hero-blob2 {{ position: absolute; pointer-events: none; opacity: 0.12; animation: t12-blob-morph 8s ease-in-out infinite; }}
.dp-t12-hero-blob1 {{ width: 300px; height: 300px; top: -80px; right: -60px; background: var(--primary); }}
.dp-t12-hero-blob2 {{ width: 200px; height: 200px; bottom: -40px; left: -40px; background: var(--secondary); animation-delay: -4s; }}
.dp-t12-about .dp-t12-hero-badge {{ display: inline-flex; align-items: center; gap: 6px; background: var(--pink-pale); border: 2px solid var(--pink-border); color: var(--primary); padding: 6px 18px; border-radius: 50px; font-size: 0.78rem; font-weight: 800; margin-bottom: 1rem; }}
.dp-t12-about .dp-t12-hero h1 {{ font-family: {font_family}; font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 900; margin: 0 0 0.75rem; position: relative; z-index: 1; }}
.dp-t12-about .dp-t12-hero h1 em {{ font-style: normal; background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
.dp-t12-about .dp-t12-hero p {{ color: var(--muted); font-size: 1.05rem; font-weight: 500; position: relative; z-index: 1; }}

.at12-body {{ max-width: 1100px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}
.at12-sec-title {{ font-family: {font_family}; font-size: 1.6rem; font-weight: 900; color: var(--text); margin: 0 0 1.25rem; }}
.at12-section {{ margin-bottom: 2.5rem; }}
.at12-para {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; font-weight: 500; margin: 0 0 0.75rem; text-align: center; max-width: 700px; margin-left: auto; margin-right: auto; }}

.at12-founder-section {{ display: grid; grid-template-columns: 1.3fr 1fr; gap: 1rem; margin-bottom: 2.5rem; }}
.at12-founder-card {{ background: var(--bg); border: 2px solid var(--border); border-radius: var(--radius-lg); padding: 2rem; display: flex; gap: 1.5rem; box-shadow: var(--shadow-sm); }}
.at12-avatar-img {{ width: 90px; height: 90px; border-radius: 50%; object-fit: cover; flex-shrink: 0; border: 3px solid var(--primary); }}
.at12-avatar-ph {{ width: 90px; height: 90px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff; font-size: 1.8rem; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
.at12-founder-name {{ font-family: {font_family}; font-size: 1.35rem; font-weight: 800; margin: 0 0 0.2rem; }}
.at12-founder-title {{ font-size: 0.78rem; font-weight: 700; color: var(--primary); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.6rem; }}
.at12-founder-bio {{ color: var(--muted); font-size: 0.9rem; line-height: 1.65; font-weight: 500; }}
.at12-side-cards {{ display: flex; flex-direction: column; gap: 1rem; }}
.at12-story-card, .at12-cats-card {{ background: var(--surface); border: 2px solid var(--border); border-radius: var(--radius); padding: 1.5rem; flex: 1; box-shadow: var(--shadow-sm); }}
.at12-story-title {{ font-family: {font_family}; font-size: 1.05rem; font-weight: 800; margin: 0 0 0.6rem; }}
.at12-story-card p {{ color: var(--muted); font-size: 0.9rem; line-height: 1.7; font-weight: 500; margin: 0; }}
.at12-chips-wrap {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.at12-chip {{ display: inline-block; background: var(--pink-pale); border: 2px solid var(--pink-border); color: var(--primary); padding: 4px 14px; border-radius: 50px; font-size: 0.78rem; font-weight: 700; }}
.at12-values-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }}
.at12-value-card {{ background: var(--bg); border: 2px solid var(--border); border-radius: var(--radius); padding: 1.5rem; text-align: center; transition: all 0.35s; }}
.at12-value-card:hover {{ border-color: var(--val-color); transform: translateY(-5px) scale(1.03); box-shadow: var(--shadow); }}
.at12-value-icon {{ font-size: 2rem; margin-bottom: 0.75rem; }}
.at12-value-title {{ font-family: {font_family}; font-size: 1.05rem; font-weight: 800; margin: 0 0 0.4rem; }}
.at12-value-desc {{ color: var(--muted); font-size: 0.85rem; line-height: 1.55; font-weight: 500; margin: 0; }}
.at12-team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
.at12-team-card {{ background: var(--bg); border: 2px solid var(--border); border-radius: var(--radius); padding: 1.5rem; text-align: center; transition: all 0.3s; }}
.at12-team-card:hover {{ transform: translateY(-4px); box-shadow: var(--shadow); }}
.at12-team-av {{ width: 64px; height: 64px; border-radius: 50%; object-fit: cover; margin: 0 auto 0.6rem; border: 3px solid var(--primary); display: block; }}
.at12-team-name {{ display: block; font-weight: 800; font-size: 1rem; }}
.at12-team-title {{ display: block; font-size: 0.72rem; color: var(--primary); font-weight: 700; text-transform: uppercase; margin-bottom: 0.5rem; }}
.at12-team-bio {{ color: var(--muted); font-size: 0.83rem; line-height: 1.5; font-weight: 500; }}
.at12-cta-section {{
    background: linear-gradient(135deg, var(--surface2), var(--blue-pale));
    border: 2px solid var(--border); border-radius: var(--radius-lg);
    padding: 2.5rem; display: flex; align-items: center; justify-content: space-between;
    gap: 2rem; margin-top: 2rem; flex-wrap: wrap;
}}
.at12-cta-text h2 {{ font-family: {font_family}; font-size: 1.5rem; font-weight: 900; margin: 0 0 0.3rem; }}
.at12-cta-text p {{ color: var(--muted); font-size: 0.95rem; font-weight: 500; margin: 0; }}
.at12-cta-btns {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}
.at12-btn {{ padding: 0.7rem 1.6rem; border-radius: 50px; text-decoration: none; font-weight: 800; font-size: 0.9rem; transition: all 0.3s; }}
.at12-btn-primary {{ background: var(--primary); color: #fff; box-shadow: 0 4px 16px rgba(255,133,161,0.3); }}
.at12-btn-primary:hover {{ transform: translateY(-3px) scale(1.05); box-shadow: 0 8px 24px rgba(255,133,161,0.45); }}
.at12-btn-ghost {{ background: transparent; color: var(--text); border: 2px solid var(--border); }}
.at12-btn-ghost:hover {{ border-color: var(--primary); color: var(--primary); }}
@media (max-width: 900px) {{ .at12-founder-section {{ grid-template-columns: 1fr; }} .at12-values-grid {{ grid-template-columns: 1fr; }} }}
@media (max-width: 600px) {{ .dp-t12-about .dp-t12-hero h1 {{ font-size: 1.8rem; }} .at12-cta-section {{ flex-direction: column; text-align: center; }} .at12-founder-card {{ flex-direction: column; align-items: center; text-align: center; }} }}
"""
    return {"html": html_content, "css": css}
