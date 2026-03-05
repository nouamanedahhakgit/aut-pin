"""Theme 1 — About Us: Warm gradient hero, rounded cards, soft shadows."""


def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("domain_page", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Playfair Display, serif"
    body_font = s.get("body_family", "Inter, sans-serif")

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
        avatar_html = f'<img src="{html_module.escape(f_avatar)}" alt="{f_name}" class="dp-t1-avatar">'
    else:
        initials = "".join(w[0].upper() for w in f_name.split()[:2]) if f_name else "C"
        avatar_html = f'<div class="dp-t1-avatar dp-t1-avatar-ph"><span>{initials}</span></div>'

    cat_list = ""
    for c in categories[:8]:
        cn = html_module.escape(c.get("name", ""))
        if cn:
            cat_list += f"<li>{cn}</li>"
    if not cat_list:
        cat_list = "<li>Quick Weeknight Dinners</li><li>Comfort Food Classics</li><li>Healthy Meal Prep</li><li>Baking & Desserts</li>"

    team_html = ""
    if len(writers) > 1:
        cards = ""
        for w in writers[1:4]:
            wn = html_module.escape(str(w.get("name", "")))
            wt = html_module.escape(str(w.get("title", "")))
            wb = html_module.escape(str(w.get("bio", ""))[:150])
            wa = (w.get("avatar") or "").strip()
            if wa and wa.startswith("http"):
                wimg = f'<img src="{html_module.escape(wa)}" alt="{wn}" class="dp-t1-team-avatar">'
            else:
                wi = "".join(x[0].upper() for x in wn.split()[:2]) if wn else "?"
                wimg = f'<div class="dp-t1-team-avatar dp-t1-avatar-ph"><span>{wi}</span></div>'
            cards += f"""<div class="dp-t1-team-card">{wimg}<h4 class="dp-t1-team-name">{wn}</h4><p class="dp-t1-team-title">{wt}</p><p class="dp-t1-team-bio">{wb}</p></div>"""
        team_html = f"""<section class="dp-t1-section"><h2 class="dp-t1-h2">Contributors &amp; Recipe Creators</h2><div class="dp-t1-team-grid">{cards}</div></section>"""

    html_content = f"""
<div class="domain-page dp-t1-about">
  <section class="dp-t1-hero">
    <p class="dp-t1-greeting">Nice to meet you!</p>
    <h1 class="dp-t1-title">About {name}</h1>
    <p class="dp-t1-intro">Welcome to our kitchen — a place where good food brings people together and every recipe tells a story.</p>
  </section>
  <div class="dp-t1-body">
    <section class="dp-t1-founder">
      {avatar_html}
      <div class="dp-t1-founder-info">
        <h3 class="dp-t1-founder-name">{f_name}</h3>
        <p class="dp-t1-founder-title">{f_title}</p>
        <p class="dp-t1-founder-bio">{f_bio}</p>
      </div>
    </section>
    <section class="dp-t1-section">
      <h2 class="dp-t1-h2">About {f_name}</h2>
      <p>Cooking has always been more than just a hobby — it&rsquo;s a way of life. {f_name} started {name} to share recipes that are approachable, delicious, and made with love. From family dinners to special occasions, every dish is crafted with care.</p>
    </section>
    <section class="dp-t1-section">
      <h2 class="dp-t1-h2">What You&rsquo;ll Find on {name}</h2>
      <ul class="dp-t1-list">{cat_list}</ul>
    </section>
    <section class="dp-t1-section">
      <h2 class="dp-t1-h2">My Recipe Philosophy</h2>
      <p>We believe in using fresh, seasonal ingredients and simple techniques that anyone can master. Our recipes are tested multiple times to ensure they work perfectly in your kitchen. No fuss, no complicated equipment — just honest, delicious food.</p>
    </section>
    <section class="dp-t1-section">
      <h2 class="dp-t1-h2">My Journey in the Kitchen</h2>
      <p>What started as a passion for home cooking grew into something much bigger. Years of experimenting, learning from different cuisines, and listening to our community have shaped the recipes you find here today. Every recipe carries a piece of that journey.</p>
    </section>
    <section class="dp-t1-section">
      <h2 class="dp-t1-h2">For Every Kind of Home Cook</h2>
      <p>Whether you&rsquo;re a beginner just learning your way around the kitchen or a seasoned cook looking for new inspiration, there&rsquo;s something here for you. We write our recipes with clear instructions and helpful tips so you can cook with confidence.</p>
    </section>
    {team_html}
    <section class="dp-t1-section">
      <h2 class="dp-t1-h2">Connect with Me</h2>
      <p>I love hearing from fellow food lovers! Share your creations, ask questions, or just say hello. Let&rsquo;s build a community around great food.</p>
    </section>
    <section class="dp-t1-cta">
      <p class="dp-t1-cta-lead">Let&rsquo;s cook together!</p>
      <h2 class="dp-t1-cta-title">Start Your Culinary Journey</h2>
      <div class="dp-t1-cta-btns">
        <a href="{base_url}/recipes" class="dp-t1-btn dp-t1-btn-primary">Browse Recipes</a>
        <a href="{base_url}/contact-us" class="dp-t1-btn dp-t1-btn-outline">Contact Us</a>
      </div>
    </section>
  </div>
</div>
"""

    css = f"""
{font_import}
.dp-t1-about {{
    --primary: {s.get("primary", "#E07C5E")};
    --secondary: {s.get("secondary", "#D46A4A")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font}; color: var(--text); background: var(--bg);
}}
.dp-t1-hero {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; text-align: center; padding: 4rem 1.5rem 3rem;
}}
.dp-t1-greeting {{ font-family: {font_family}; font-size: 1.3rem; opacity: 0.9; margin-bottom: 0.5rem; font-style: italic; }}
.dp-t1-title {{ font-family: {font_family}; font-size: 2.8rem; font-weight: 700; margin: 0 0 1rem; }}
.dp-t1-intro {{ max-width: 600px; margin: 0 auto; font-size: 1.05rem; opacity: 0.9; line-height: 1.7; }}

.dp-t1-body {{ max-width: 800px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}

.dp-t1-founder {{
    display: flex; gap: 1.5rem; align-items: center; padding: 2rem;
    background: color-mix(in srgb, var(--primary) 6%, var(--bg));
    border-radius: 16px; margin-bottom: 2.5rem;
}}
.dp-t1-avatar {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; flex-shrink: 0; border: 3px solid color-mix(in srgb, var(--primary) 25%, transparent); }}
.dp-t1-avatar-ph {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700; }}
.dp-t1-founder-name {{ font-family: {font_family}; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.2rem; }}
.dp-t1-founder-title {{ color: var(--primary); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; }}
.dp-t1-founder-bio {{ color: var(--muted); font-size: 0.95rem; line-height: 1.6; }}

.dp-t1-section {{ margin-bottom: 2rem; }}
.dp-t1-h2 {{ font-family: {font_family}; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border); }}
.dp-t1-section p {{ color: var(--muted); font-size: 0.95rem; line-height: 1.8; }}
.dp-t1-list {{ color: var(--muted); padding-left: 1.25rem; line-height: 2; }}

.dp-t1-team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; }}
.dp-t1-team-card {{ text-align: center; padding: 1.5rem; border: 1px solid var(--border); border-radius: 12px; }}
.dp-t1-team-avatar {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin: 0 auto 0.75rem; border: 2px solid color-mix(in srgb, var(--primary) 20%, transparent); }}
.dp-t1-team-name {{ font-family: {font_family}; font-size: 1.05rem; font-weight: 700; margin-bottom: 0.15rem; }}
.dp-t1-team-title {{ color: var(--primary); font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; }}
.dp-t1-team-bio {{ color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}

.dp-t1-cta {{
    text-align: center; padding: 2.5rem; margin-top: 2rem;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 16px; color: #fff;
}}
.dp-t1-cta-lead {{ font-family: {font_family}; font-style: italic; opacity: 0.9; margin-bottom: 0.5rem; }}
.dp-t1-cta-title {{ font-family: {font_family}; font-size: 1.8rem; font-weight: 700; margin-bottom: 1.25rem; }}
.dp-t1-cta-btns {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
.dp-t1-btn {{ padding: 0.7rem 1.5rem; border-radius: 9999px; text-decoration: none; font-weight: 600; font-size: 0.95rem; transition: opacity 0.2s; }}
.dp-t1-btn-primary {{ background: #fff; color: var(--primary); }}
.dp-t1-btn-outline {{ background: transparent; color: #fff; border: 2px solid rgba(255,255,255,0.6); }}
.dp-t1-btn:hover {{ opacity: 0.85; }}

@media (max-width: 600px) {{
    .dp-t1-title {{ font-size: 2rem; }}
    .dp-t1-founder {{ flex-direction: column; text-align: center; }}
}}
"""
    return {"html": html_content, "css": css}
