"""Theme 3 — About Us: Glassmorphism dark mode, frosted glass cards, glow accents."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    s = t["s"]
    ff = t["font_family"]

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
        avatar_html = f'<img src="{html_module.escape(f_avatar)}" alt="{f_name}" class="dp-t3-avatar">'
    else:
        initials = "".join(w[0].upper() for w in f_name.split()[:2]) if f_name else "C"
        avatar_html = f'<div class="dp-t3-avatar dp-t3-avatar-ph"><span>{initials}</span></div>'

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
                wimg = f'<img src="{html_module.escape(wa)}" alt="{wn}" class="dp-t3-team-avatar">'
            else:
                wi = "".join(x[0].upper() for x in wn.split()[:2]) if wn else "?"
                wimg = f'<div class="dp-t3-team-avatar dp-t3-avatar-ph"><span>{wi}</span></div>'
            cards += f"""<div class="dp-t3-team-card">{wimg}<h4 class="dp-t3-team-name">{wn}</h4><p class="dp-t3-team-title">{wt}</p><p class="dp-t3-team-bio">{wb}</p></div>"""
        team_html = f"""<section class="dp-t3-section"><h2 class="dp-t3-h2">Contributors &amp; Recipe Creators</h2><div class="dp-t3-team-grid">{cards}</div></section>"""

    html_content = f"""
<div class="domain-page dp-t3-about">
  <section class="dp-t3-hero">
    <p class="dp-t3-hero-label">Nice to meet you!</p>
    <h1>About {name}</h1>
    <p>Welcome to our kitchen &mdash; a place where great food brings people together and every recipe tells a story.</p>
  </section>
  <div class="dp-t3-body">
    <section class="dp-t3-founder">
      {avatar_html}
      <div class="dp-t3-founder-info">
        <h3 class="dp-t3-founder-name">{f_name}</h3>
        <p class="dp-t3-founder-title">{f_title}</p>
        <p class="dp-t3-founder-bio">{f_bio}</p>
      </div>
    </section>
    <section class="dp-t3-section">
      <h2 class="dp-t3-h2">About {f_name}</h2>
      <p>Cooking has always been more than just a hobby &mdash; it&rsquo;s a way of life. {f_name} started {name} to share recipes that are approachable, delicious, and made with love. From family dinners to special occasions, every dish is crafted with care.</p>
    </section>
    <section class="dp-t3-section">
      <h2 class="dp-t3-h2">What You&rsquo;ll Find on {name}</h2>
      <ul class="dp-t3-list">{cat_list}</ul>
    </section>
    <section class="dp-t3-section">
      <h2 class="dp-t3-h2">My Recipe Philosophy</h2>
      <p>We believe in using fresh, seasonal ingredients and simple techniques anyone can master. Our recipes are tested multiple times to ensure they work perfectly in your kitchen. No fuss, no complicated equipment &mdash; just honest, delicious food.</p>
    </section>
    <section class="dp-t3-section">
      <h2 class="dp-t3-h2">My Journey in the Kitchen</h2>
      <p>What started as a passion for home cooking grew into something much bigger. Years of experimenting, learning from cuisines around the world, and listening to our community have shaped the recipes you find here today. Every recipe carries a piece of that journey.</p>
    </section>
    <section class="dp-t3-section">
      <h2 class="dp-t3-h2">For Every Kind of Home Cook</h2>
      <p>Whether you&rsquo;re a beginner just learning your way around the kitchen or a seasoned cook looking for new inspiration, there&rsquo;s something here for you. We write our recipes with clear instructions and helpful tips so you can cook with confidence.</p>
    </section>
    {team_html}
    <section class="dp-t3-section">
      <h2 class="dp-t3-h2">Connect with Me</h2>
      <p>I love hearing from fellow food lovers! Share your creations, ask questions, or just say hello. <a href="{base_url}/contact-us">Get in touch here</a>.</p>
    </section>
    <section class="dp-t3-cta">
      <p class="dp-t3-cta-lead">Let&rsquo;s cook together!</p>
      <h2 class="dp-t3-cta-title">Start Your Culinary Journey</h2>
      <div class="dp-t3-cta-btns">
        <a href="{base_url}/recipes" class="dp-t3-btn dp-t3-btn-primary">Browse Recipes</a>
        <a href="{base_url}/contact-us" class="dp-t3-btn dp-t3-btn-outline">Contact Us</a>
      </div>
    </section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t3-about {{ {t['css_vars']} }}
{hero_css(ff)}
{body_css(ff)}

.dp-t3-about .dp-t3-section a {{ color: var(--secondary); text-decoration: underline; }}
.dp-t3-about .dp-t3-section a:hover {{ color: var(--primary); }}

.dp-t3-founder {{
    display: flex; gap: 1.5rem; align-items: center; padding: 2rem;
    background: var(--glass); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius); margin-bottom: 2.5rem;
}}
.dp-t3-avatar {{
    width: 100px; height: 100px; border-radius: 50%; object-fit: cover; flex-shrink: 0;
    border: 2px solid color-mix(in srgb, var(--primary) 30%, transparent);
}}
.dp-t3-avatar-ph {{
    background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; font-weight: 700;
    box-shadow: 0 0 20px color-mix(in srgb, var(--primary) 25%, transparent);
}}
.dp-t3-founder-name {{ font-family: {ff}; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.2rem; color: var(--text); }}
.dp-t3-founder-title {{ color: var(--secondary); font-size: 0.82rem; font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; }}
.dp-t3-founder-bio {{ color: var(--muted); font-size: 0.95rem; line-height: 1.65; }}
.dp-t3-list {{ color: var(--muted); padding-left: 1.25rem; line-height: 2; }}

.dp-t3-team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; }}
.dp-t3-team-card {{
    text-align: center; padding: 1.5rem;
    background: var(--glass); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border); border-radius: var(--radius);
    transition: border-color 0.3s;
}}
.dp-t3-team-card:hover {{ border-color: var(--primary); }}
.dp-t3-team-avatar {{
    width: 70px; height: 70px; border-radius: 50%; object-fit: cover;
    margin: 0 auto 0.75rem; border: 2px solid color-mix(in srgb, var(--primary) 20%, transparent);
}}
.dp-t3-team-name {{ font-family: {ff}; font-size: 1.05rem; font-weight: 700; color: var(--text); margin-bottom: 0.15rem; }}
.dp-t3-team-title {{ color: var(--secondary); font-size: 0.78rem; font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; }}
.dp-t3-team-bio {{ color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}

.dp-t3-cta {{
    text-align: center; padding: 2.5rem; margin-top: 2rem;
    background: var(--glass); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
    border-radius: var(--radius);
    position: relative; overflow: hidden;
}}
.dp-t3-cta::before {{
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 10%, transparent), color-mix(in srgb, var(--secondary) 8%, transparent));
    pointer-events: none;
}}
.dp-t3-cta-lead {{ color: var(--secondary); font-style: italic; margin-bottom: 0.5rem; position: relative; }}
.dp-t3-cta-title {{ font-family: {ff}; font-size: 1.8rem; font-weight: 800; margin-bottom: 1.25rem; color: var(--text); position: relative; }}
.dp-t3-cta-btns {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; position: relative; }}
.dp-t3-btn {{
    padding: 0.75rem 1.5rem; border-radius: 12px; text-decoration: none;
    font-weight: 700; font-size: 0.92rem; transition: all 0.3s;
}}
.dp-t3-btn-primary {{
    background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff;
    box-shadow: 0 4px 16px color-mix(in srgb, var(--primary) 30%, transparent);
}}
.dp-t3-btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px color-mix(in srgb, var(--primary) 45%, transparent); }}
.dp-t3-btn-outline {{
    background: transparent; color: var(--text); border: 1px solid var(--glass-border);
}}
.dp-t3-btn-outline:hover {{ border-color: var(--primary); color: var(--primary); }}

@media (max-width: 600px) {{
    .dp-t3-founder {{ flex-direction: column; text-align: center; }}
    .dp-t3-cta-title {{ font-size: 1.4rem; }}
}}
"""
    return {"html": html_content, "css": css}
