"""Theme 2 — About Us: Modern clean style, accent bar headings, card-based layout."""
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
        avatar_html = f'<img src="{html_module.escape(f_avatar)}" alt="{f_name}" class="dp-t2-avatar">'
    else:
        initials = "".join(w[0].upper() for w in f_name.split()[:2]) if f_name else "C"
        avatar_html = f'<div class="dp-t2-avatar dp-t2-avatar-ph"><span>{initials}</span></div>'

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
                wimg = f'<img src="{html_module.escape(wa)}" alt="{wn}" class="dp-t2-team-avatar">'
            else:
                wi = "".join(x[0].upper() for x in wn.split()[:2]) if wn else "?"
                wimg = f'<div class="dp-t2-team-avatar dp-t2-avatar-ph"><span>{wi}</span></div>'
            cards += f"""<div class="dp-t2-team-card">{wimg}<h4 class="dp-t2-team-name">{wn}</h4><p class="dp-t2-team-title">{wt}</p><p class="dp-t2-team-bio">{wb}</p></div>"""
        team_html = f"""<section class="dp-t2-section"><h2 class="dp-t2-h2">Contributors &amp; Recipe Creators</h2><div class="dp-t2-team-grid">{cards}</div></section>"""

    html_content = f"""
<div class="domain-page dp-t2-about">
  <section class="dp-t2-hero">
    <p class="dp-t2-hero-label">About</p>
    <h1>About {name}</h1>
    <p>Welcome to our kitchen — a place where good food brings people together.</p>
  </section>
  <div class="dp-t2-body">
    <section class="dp-t2-founder">
      {avatar_html}
      <div class="dp-t2-founder-info">
        <h3 class="dp-t2-founder-name">{f_name}</h3>
        <span class="dp-t2-founder-title">{f_title}</span>
        <p class="dp-t2-founder-bio">{f_bio}</p>
      </div>
    </section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">About {f_name}</h2><p>Cooking has always been more than a hobby — it&rsquo;s a way of life. {f_name} started {name} to share recipes that are approachable, delicious, and made with love.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">What You&rsquo;ll Find</h2><ul class="dp-t2-list">{cat_list}</ul></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Recipe Philosophy</h2><p>Fresh, seasonal ingredients. Simple techniques anyone can master. Recipes tested multiple times. No fuss, no complicated equipment — just honest, delicious food.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">My Kitchen Journey</h2><p>What started as a passion for home cooking grew into something bigger. Years of experimenting and learning from different cuisines have shaped the recipes you find here today.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">For Every Home Cook</h2><p>Whether you&rsquo;re a beginner or a seasoned cook looking for new inspiration, there&rsquo;s something here for you. Clear instructions and helpful tips so you can cook with confidence.</p></section>
    {team_html}
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Connect</h2><p>I love hearing from fellow food lovers! Share your creations, ask questions, or just say hello.</p></section>
    <section class="dp-t2-cta">
      <h2 class="dp-t2-cta-title">Start Your Culinary Journey</h2>
      <div class="dp-t2-cta-btns">
        <a href="{base_url}/recipes" class="dp-t2-btn dp-t2-btn-primary">Browse Recipes</a>
        <a href="{base_url}/contact-us" class="dp-t2-btn dp-t2-btn-outline">Contact Us</a>
      </div>
    </section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t2-about {{ {t['css_vars']} }}
{hero_css(ff)}
{body_css(ff)}

.dp-t2-founder {{
    display: flex; gap: 1.5rem; align-items: center; padding: 1.5rem;
    border: 1px solid var(--border); border-left: 4px solid var(--primary);
    margin-bottom: 2.5rem;
}}
.dp-t2-avatar {{ width: 90px; height: 90px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }}
.dp-t2-avatar-ph {{ background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: 700; border-radius: 8px; }}
.dp-t2-founder-name {{ font-family: {ff}; font-size: 1.2rem; font-weight: 700; margin: 0 0 0.15rem; }}
.dp-t2-founder-title {{ color: var(--primary); font-size: 0.8rem; font-weight: 600; display: block; margin-bottom: 0.5rem; }}
.dp-t2-founder-bio {{ color: var(--muted); font-size: 0.9rem; line-height: 1.6; }}

.dp-t2-list {{ color: var(--muted); padding-left: 1.25rem; line-height: 2; }}

.dp-t2-team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; }}
.dp-t2-team-card {{ padding: 1.25rem; border: 1px solid var(--border); border-left: 3px solid var(--primary); }}
.dp-t2-team-avatar {{ width: 60px; height: 60px; border-radius: 8px; object-fit: cover; margin-bottom: 0.75rem; }}
.dp-t2-team-name {{ font-family: {ff}; font-size: 1rem; font-weight: 700; margin-bottom: 0.1rem; }}
.dp-t2-team-title {{ color: var(--primary); font-size: 0.75rem; font-weight: 600; display: block; margin-bottom: 0.4rem; }}
.dp-t2-team-bio {{ color: var(--muted); font-size: 0.8rem; line-height: 1.5; }}

.dp-t2-cta {{
    text-align: center; padding: 2rem; margin-top: 2rem;
    border: 2px solid var(--primary); border-radius: 0;
}}
.dp-t2-cta-title {{ font-family: {ff}; font-size: 1.6rem; font-weight: 700; color: var(--text); margin-bottom: 1.25rem; }}
.dp-t2-cta-btns {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
.dp-t2-btn {{ padding: 0.65rem 1.5rem; text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: all 0.2s; }}
.dp-t2-btn-primary {{ background: var(--primary); color: #fff; }}
.dp-t2-btn-outline {{ border: 2px solid var(--primary); color: var(--primary); background: transparent; }}
.dp-t2-btn:hover {{ opacity: 0.85; }}

@media (max-width: 600px) {{ .dp-t2-founder {{ flex-direction: column; text-align: center; }} }}
"""
    return {"html": html_content, "css": css}
