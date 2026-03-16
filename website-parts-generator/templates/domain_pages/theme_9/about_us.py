"""Theme 9 — About Us: Gold-tinted hero, editorial founder card, team grid."""

def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("domain_page", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Cormorant Garamond, Georgia, serif"
    body_font = s.get("body_family", "Lato, Inter, sans-serif")

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
        avatar_html = f'<img src="{html_module.escape(f_avatar)}" alt="{f_name}" class="dp-t9-avatar">'
    else:
        initials = "".join(w[0].upper() for w in f_name.split()[:2]) if f_name else "C"
        avatar_html = f'<div class="dp-t9-avatar dp-t9-avatar-ph"><span>{initials}</span></div>'

    cat_list = ""
    for c in categories[:8]:
        cn = html_module.escape(c.get("name", ""))
        if cn:
            cat_list += f"<li>{cn}</li>"
    if not cat_list:
        cat_list = "<li>Quick Weeknight Dinners</li><li>Comfort Food Classics</li><li>Healthy Meal Prep</li><li>Baking &amp; Desserts</li>"

    team_html = ""
    if len(writers) > 1:
        cards = ""
        for w in writers[1:4]:
            wn = html_module.escape(str(w.get("name", "")))
            wt = html_module.escape(str(w.get("title", "")))
            wb = html_module.escape(str(w.get("bio", ""))[:150])
            wa = (w.get("avatar") or "").strip()
            if wa and wa.startswith("http"):
                wimg = f'<img src="{html_module.escape(wa)}" alt="{wn}" class="dp-t9-team-avatar">'
            else:
                wi = "".join(x[0].upper() for x in wn.split()[:2]) if wn else "?"
                wimg = f'<div class="dp-t9-team-avatar dp-t9-avatar-ph"><span>{wi}</span></div>'
            cards += f"""<div class="dp-t9-team-card">{wimg}<h4 class="dp-t9-team-name">{wn}</h4><p class="dp-t9-team-title">{wt}</p><p class="dp-t9-team-bio">{wb}</p></div>"""
        team_html = f"""<section class="dp-t9-section"><h2 class="dp-t9-h2">Contributors &amp; Recipe Creators</h2><div class="dp-t9-team-grid">{cards}</div></section>"""

    html_content = f"""
<div class="domain-page dp-t9-about">
  <section class="dp-t9-hero">
    <p class="dp-t9-greeting">Nice to meet you!</p>
    <h1 class="dp-t9-title">About {name}</h1>
    <p class="dp-t9-intro">Welcome to our kitchen &mdash; where fresh ingredients and heartfelt recipes bring people together.</p>
  </section>
  <div class="dp-t9-body">
    <section class="dp-t9-founder">
      {avatar_html}
      <div class="dp-t9-founder-info">
        <h3 class="dp-t9-founder-name">{f_name}</h3>
        <p class="dp-t9-founder-title">{f_title}</p>
        <p class="dp-t9-founder-bio">{f_bio}</p>
      </div>
    </section>
    <section class="dp-t9-section">
      <h2 class="dp-t9-h2">About {f_name}</h2>
      <p>Cooking has always been more than just a hobby &mdash; it&rsquo;s a way of connecting with the people we love. {f_name} started {name} to share recipes that are approachable, wholesome, and made with genuine care. From everyday family dinners to celebratory feasts, every dish is crafted thoughtfully.</p>
    </section>
    <section class="dp-t9-section">
      <h2 class="dp-t9-h2">What You&rsquo;ll Find on {name}</h2>
      <ul class="dp-t9-list">{cat_list}</ul>
    </section>
    <section class="dp-t9-section">
      <h2 class="dp-t9-h2">My Recipe Philosophy</h2>
      <p>We believe in fresh, seasonal ingredients and simple techniques anyone can master. Every recipe is tested multiple times to ensure it works perfectly in your kitchen &mdash; no fuss, no complicated equipment, just honest, delicious food.</p>
    </section>
    <section class="dp-t9-section">
      <h2 class="dp-t9-h2">My Journey in the Kitchen</h2>
      <p>What started as a passion for home cooking grew into something much bigger. Years of experimenting, learning from different cuisines, and listening to our community have shaped the recipes you find here. Every recipe carries a piece of that journey.</p>
    </section>
    <section class="dp-t9-section">
      <h2 class="dp-t9-h2">For Every Kind of Home Cook</h2>
      <p>Whether you&rsquo;re a beginner just learning your way around the kitchen or a seasoned cook seeking fresh inspiration, there&rsquo;s something here for you. Clear instructions and helpful tips help you cook with confidence.</p>
    </section>
    {team_html}
    <section class="dp-t9-section">
      <h2 class="dp-t9-h2">Connect with Me</h2>
      <p>I love hearing from fellow food lovers! Share your creations, ask questions, or simply say hello. Let&rsquo;s build a community around great food.</p>
    </section>
    <section class="dp-t9-cta">
      <p class="dp-t9-cta-lead">Let&rsquo;s cook together!</p>
      <h2 class="dp-t9-cta-title">Start Your Culinary Journey</h2>
      <div class="dp-t9-cta-btns">
        <a href="{base_url}/recipes" class="dp-t9-btn dp-t9-btn-primary">Browse Recipes</a>
        <a href="{base_url}/contact-us" class="dp-t9-btn dp-t9-btn-outline">Contact Us</a>
      </div>
    </section>
  </div>
</div>
"""

    css = f"""
{font_import}
.dp-t9-about {{
    --primary:   {s.get("primary",    "#D4A843")};
    --secondary: {s.get("secondary",  "#7A9E7E")};
    --accent:    {s.get("accent",     "#C8844A")};
    --bg:        {s.get("background", "#FFFFFF")};
    --surface2:  #F5F3EE;
    --text:      {s.get("text_primary",   "#2C2416")};
    --muted:     {s.get("text_secondary", "#7A6A56")};
    --border:    {s.get("border",         "#E8DFD0")};
    --gold-light: #FBF3DC;
    font-family: {body_font}; color: var(--text); background: var(--bg);
}}
.dp-t9-hero {{
    background: linear-gradient(160deg, var(--surface2), var(--gold-light));
    text-align: center; padding: 4rem 1.5rem 3rem; border-bottom: 1px solid var(--border);
}}
.dp-t9-greeting {{ font-family: {font_family}; font-size: 1.2rem; color: var(--primary); margin-bottom: 0.5rem; font-style: italic; }}
.dp-t9-title {{ font-family: {font_family}; font-size: 2.8rem; font-weight: 700; margin: 0 0 1rem; color: var(--text); }}
.dp-t9-intro {{ max-width: 600px; margin: 0 auto; font-size: 1.05rem; color: var(--muted); line-height: 1.7; }}

.dp-t9-body {{ max-width: 820px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}

.dp-t9-founder {{
    display: flex; gap: 1.5rem; align-items: center; padding: 2rem;
    background: var(--gold-light); border-radius: 16px; margin-bottom: 2.5rem;
    border: 1px solid rgba(212,168,67,0.25);
}}
.dp-t9-avatar {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; flex-shrink: 0; border: 2.5px solid rgba(212,168,67,0.5); }}
.dp-t9-avatar-ph {{ background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700; }}
.dp-t9-founder-name {{ font-family: {font_family}; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.2rem; color: var(--text); }}
.dp-t9-founder-title {{ color: var(--primary); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; }}
.dp-t9-founder-bio {{ color: var(--muted); font-size: 0.95rem; line-height: 1.6; }}

.dp-t9-section {{ margin-bottom: 2rem; }}
.dp-t9-h2 {{
    font-family: {font_family}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.75rem;
    padding-bottom: 0.5rem; border-bottom: 2px solid var(--border); position: relative; color: var(--text);
}}
.dp-t9-h2::after {{ content: ''; position: absolute; bottom: -2px; left: 0; width: 44px; height: 2px; background: var(--primary); }}
.dp-t9-section p {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; }}
.dp-t9-list {{ color: var(--muted); padding-left: 1.25rem; line-height: 2; }}

.dp-t9-team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; }}
.dp-t9-team-card {{ text-align: center; padding: 1.5rem; border: 1px solid var(--border); border-radius: 12px; background: var(--bg); }}
.dp-t9-team-avatar {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin: 0 auto 0.75rem; border: 2px solid rgba(212,168,67,0.3); }}
.dp-t9-team-name {{ font-family: {font_family}; font-size: 1.05rem; font-weight: 700; margin-bottom: 0.15rem; color: var(--text); }}
.dp-t9-team-title {{ color: var(--primary); font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; }}
.dp-t9-team-bio {{ color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}

.dp-t9-cta {{
    text-align: center; padding: 2.5rem; margin-top: 2rem;
    background: linear-gradient(160deg, var(--surface2), var(--gold-light));
    border-radius: 16px; border: 1px solid rgba(212,168,67,0.25);
}}
.dp-t9-cta-lead {{ font-family: {font_family}; font-style: italic; color: var(--primary); margin-bottom: 0.5rem; }}
.dp-t9-cta-title {{ font-family: {font_family}; font-size: 1.8rem; font-weight: 700; margin-bottom: 1.25rem; color: var(--text); }}
.dp-t9-cta-btns {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
.dp-t9-btn {{ padding: 0.75rem 1.75rem; border-radius: 9999px; text-decoration: none; font-weight: 600; font-size: 0.95rem; transition: all 0.2s; }}
.dp-t9-btn-primary {{ background: var(--primary); color: #fff; }}
.dp-t9-btn-primary:hover {{ background: var(--accent); transform: translateY(-2px); }}
.dp-t9-btn-outline {{ background: transparent; color: var(--text); border: 1.5px solid var(--border); }}
.dp-t9-btn-outline:hover {{ border-color: var(--primary); color: var(--primary); background: var(--gold-light); }}

@media (max-width: 600px) {{
    .dp-t9-title {{ font-size: 2rem; }}
    .dp-t9-founder {{ flex-direction: column; text-align: center; }}
}}
"""
    return {"html": html_content, "css": css}
