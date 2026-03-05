"""About Us page for Theme 7 — Midnight Luxe.
Founder spotlight, philosophy sections, team grid, and CTA —
all with indigo-plum gradients, gold accents, luminous shadows.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t7-about"
e = html_module.escape


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = e(config.get("domain_name", "My Blog"))
    base_url = e(config.get("base_url") or config.get("domain_url", "/"))
    writers = config.get("writers") or []
    categories = config.get("categories") or []

    # ── Hero ─────────────────────────────────────────────────────────
    hero_section = f"""
    <section class="t7-hero">
      <div class="t7-hero-inner">
        <span class="t7-badge">Nice to meet you!</span>
        <h1 class="t7-hero-title">About {domain_name}</h1>
        <p class="t7-hero-sub">The story, the people, and the passion behind every recipe.</p>
      </div>
    </section>"""

    # ── Founder section ──────────────────────────────────────────────
    founder_html = ""
    if writers:
        w = writers[0]
        w_name = e(w.get("name", ""))
        w_title = e(w.get("title", ""))
        w_bio = e(w.get("bio", ""))
        w_avatar = (w.get("avatar") or "").strip()

        if w_avatar and (w_avatar.startswith("http") or w_avatar.startswith("/")):
            av_html = f'<img class="t7-abt-founder-img" src="{e(w_avatar)}" alt="{w_name}" loading="lazy">'
        else:
            initials = (w_name[0] if w_name else "?").upper()
            av_html = f'<div class="t7-abt-founder-init">{initials}</div>'

        founder_html = f"""
    <section class="t7-abt-section t7-abt-founder-section">
      <div class="t7-abt-wrap">
        <div class="t7-rule"></div>
        <h2 class="t7-abt-section-title">Meet the Founder</h2>
        <div class="t7-abt-founder">
          <div class="t7-abt-founder-avatar">{av_html}</div>
          <div class="t7-abt-founder-info">
            <h3 class="t7-abt-founder-name">{w_name}</h3>
            {f'<span class="t7-abt-founder-role">{w_title}</span>' if w_title else ''}
            {f'<p class="t7-abt-founder-bio">{w_bio}</p>' if w_bio else ''}
            <div class="t7-abt-gold-dot"></div>
          </div>
        </div>
      </div>
    </section>"""

    # ── About paragraph ──────────────────────────────────────────────
    about_para = f"""
    <section class="t7-abt-section">
      <div class="t7-abt-wrap">
        <div class="t7-rule"></div>
        <h2 class="t7-abt-section-title">Our Story</h2>
        <div class="t7-body">
          <p>{domain_name} was born from a simple belief: that cooking should be joyful,
          accessible, and endlessly inspiring. What started as a personal collection of
          family recipes has grown into a vibrant community of home cooks and food lovers
          from around the world.</p>
          <p>Every recipe on this site is tested, tasted, and refined until it&rsquo;s
          something we&rsquo;re truly proud to share. We believe that great food doesn&rsquo;t
          require a professional kitchen &mdash; just quality ingredients, a bit of patience, and
          a whole lot of heart.</p>
        </div>
      </div>
    </section>"""

    # ── What You'll Find (categories) ────────────────────────────────
    cats_items = ""
    for cat in categories:
        c_name = e(cat.get("name", ""))
        c_url = e(cat.get("url", "#"))
        cats_items += f'<a class="t7-abt-cat-pill" href="{c_url}">{c_name}</a>\n'

    find_section = f"""
    <section class="t7-abt-section">
      <div class="t7-abt-wrap">
        <div class="t7-rule"></div>
        <h2 class="t7-abt-section-title">What You&rsquo;ll Find</h2>
        <p class="t7-body" style="margin-bottom:20px;">Explore our curated collection across a range of delicious categories:</p>
        <div class="t7-abt-cats">{cats_items}</div>
      </div>
    </section>"""

    # ── Philosophy sections ──────────────────────────────────────────
    philosophy_cards = [
        {
            "icon": "&#9733;",
            "title": "Recipe Philosophy",
            "text": "Every recipe is crafted to be approachable yet impressive. We prioritize "
                    "seasonal ingredients, bold flavours, and techniques that home cooks can master "
                    "with confidence.",
        },
        {
            "icon": "&#127860;",
            "title": "Our Kitchen Journey",
            "text": "From weeknight dinners to weekend feasts, our recipes are born from real life. "
                    "We test every dish in a home kitchen — no professional shortcuts — so you can "
                    "trust the results.",
        },
        {
            "icon": "&#10084;",
            "title": "For Every Cook",
            "text": "Whether you&rsquo;re a curious beginner or a seasoned home chef, there&rsquo;s "
                    "something here for you. Clear instructions, helpful tips, and honest cook times "
                    "guide every recipe.",
        },
    ]

    phil_cards_html = ""
    for pc in philosophy_cards:
        phil_cards_html += f"""
        <div class="t7-abt-phil-card t7-card">
          <span class="t7-abt-phil-icon">{pc["icon"]}</span>
          <h3 class="t7-abt-phil-title">{pc["title"]}</h3>
          <p class="t7-abt-phil-text">{pc["text"]}</p>
        </div>"""

    phil_section = f"""
    <section class="t7-abt-section">
      <div class="t7-abt-wrap">
        <div class="t7-rule"></div>
        <h2 class="t7-abt-section-title">What Drives Us</h2>
        <div class="t7-abt-phil-grid">{phil_cards_html}</div>
      </div>
    </section>"""

    # ── Team section ─────────────────────────────────────────────────
    team_html = ""
    if len(writers) > 1:
        team_cards = ""
        for w in writers[1:]:
            w_name = e(w.get("name", ""))
            w_title_t = e(w.get("title", ""))
            w_bio_t = e(w.get("bio", ""))
            w_av = (w.get("avatar") or "").strip()

            if w_av and (w_av.startswith("http") or w_av.startswith("/")):
                tav = f'<img class="t7-abt-team-img" src="{e(w_av)}" alt="{w_name}" loading="lazy">'
            else:
                ini = (w_name[0] if w_name else "?").upper()
                tav = f'<div class="t7-abt-team-init">{ini}</div>'

            team_cards += f"""
        <div class="t7-abt-team-card t7-card">
          <div class="t7-abt-team-avatar">{tav}</div>
          <h4 class="t7-abt-team-name">{w_name}</h4>
          {f'<span class="t7-abt-team-role">{w_title_t}</span>' if w_title_t else ''}
          {f'<p class="t7-abt-team-bio">{w_bio_t}</p>' if w_bio_t else ''}
        </div>"""

        team_html = f"""
    <section class="t7-abt-section">
      <div class="t7-abt-wrap">
        <div class="t7-rule"></div>
        <h2 class="t7-abt-section-title">Our Team</h2>
        <div class="t7-abt-team-grid">{team_cards}</div>
      </div>
    </section>"""

    # ── Connect + CTA ────────────────────────────────────────────────
    cta_section = f"""
    <section class="t7-abt-section t7-abt-cta-section">
      <div class="t7-abt-wrap" style="text-align:center;">
        <div class="t7-rule" style="margin:0 auto 18px;"></div>
        <h2 class="t7-abt-section-title">Let&rsquo;s Connect</h2>
        <p class="t7-body" style="max-width:520px;margin:0 auto 28px;">
          Have a question, a recipe idea, or just want to say hello?
          We&rsquo;d love to hear from you.
        </p>
        <div class="t7-abt-cta-buttons">
          <a class="t7-btn-primary" href="{base_url}recipes/">Browse Recipes</a>
          <a class="t7-btn-ghost" href="{base_url}contact-us/">Contact Us</a>
        </div>
      </div>
    </section>"""

    # ── Assemble HTML ────────────────────────────────────────────────
    html_content = f"""
<main class="dp-t7-about">
  {hero_section}
  {founder_html}
  {about_para}
  {find_section}
  {phil_section}
  {team_html}
  {cta_section}
</main>
"""

    # ── Assemble CSS ─────────────────────────────────────────────────
    _hero = hero_css(ROOT, font_family)
    _body = body_css(ROOT, font_family)

    css_content = f"""
{font_import}
{ROOT} {{
    {css_vars}
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{_hero}
{_body}
/* ════════════════════════════════════════════════════
   SECTION SCAFFOLD
   ════════════════════════════════════════════════════ */
{ROOT} .t7-abt-section {{
    padding: 64px 32px;
    border-bottom: 1px solid var(--border);
}}
{ROOT} .t7-abt-section:last-child {{ border-bottom: none; }}
{ROOT} .t7-abt-wrap {{
    max-width: 900px;
    margin: 0 auto;
}}
{ROOT} .t7-abt-section-title {{
    font-family: {font_family};
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: .3px;
    margin: 0 0 24px;
    color: var(--text);
}}
/* ════════════════════════════════════════════════════
   FOUNDER
   ════════════════════════════════════════════════════ */
{ROOT} .t7-abt-founder {{
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 36px;
    align-items: start;
}}
{ROOT} .t7-abt-founder-img {{
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid var(--gold);
    box-shadow: 0 6px 24px rgba(26,26,46,.12);
}}
{ROOT} .t7-abt-founder-init {{
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    font-family: {font_family};
    font-size: 2.4rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 4px solid var(--gold);
    box-shadow: 0 6px 24px rgba(26,26,46,.12);
}}
{ROOT} .t7-abt-founder-name {{
    font-family: {font_family};
    font-size: 1.25rem;
    font-weight: 800;
    margin: 0 0 4px;
    color: var(--text);
}}
{ROOT} .t7-abt-founder-role {{
    display: block;
    font-size: .78rem;
    font-weight: 700;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}}
{ROOT} .t7-abt-founder-bio {{
    font-size: .92rem;
    color: var(--muted);
    line-height: 1.7;
    margin: 0;
}}
{ROOT} .t7-abt-gold-dot {{
    width: 6px;
    height: 6px;
    background: var(--gold);
    border-radius: 50%;
    margin-top: 16px;
}}
/* ════════════════════════════════════════════════════
   CATEGORY PILLS
   ════════════════════════════════════════════════════ */
{ROOT} .t7-abt-cats {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}}
{ROOT} .t7-abt-cat-pill {{
    display: inline-block;
    padding: 9px 22px;
    border: 1px solid var(--border);
    border-radius: 40px;
    text-decoration: none;
    color: var(--text);
    font-size: .84rem;
    font-weight: 600;
    transition: background .3s, color .3s, border-color .3s, transform .3s;
}}
{ROOT} .t7-abt-cat-pill:hover {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    border-color: transparent;
    transform: translateY(-1px);
}}
/* ════════════════════════════════════════════════════
   PHILOSOPHY CARDS
   ════════════════════════════════════════════════════ */
{ROOT} .t7-abt-phil-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}}
{ROOT} .t7-abt-phil-card {{
    text-align: center;
    padding: 36px 28px;
}}
{ROOT} .t7-abt-phil-icon {{
    display: inline-block;
    font-size: 1.8rem;
    margin-bottom: 14px;
    line-height: 1;
}}
{ROOT} .t7-abt-phil-title {{
    font-family: {font_family};
    font-size: 1.05rem;
    font-weight: 800;
    margin: 0 0 10px;
    color: var(--text);
}}
{ROOT} .t7-abt-phil-text {{
    font-size: .86rem;
    color: var(--muted);
    line-height: 1.65;
    margin: 0;
}}
/* ════════════════════════════════════════════════════
   TEAM GRID
   ════════════════════════════════════════════════════ */
{ROOT} .t7-abt-team-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}}
{ROOT} .t7-abt-team-card {{
    text-align: center;
    padding: 32px 24px;
}}
{ROOT} .t7-abt-team-img {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--gold);
    margin-bottom: 14px;
}}
{ROOT} .t7-abt-team-init {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    font-family: {font_family};
    font-size: 1.6rem;
    font-weight: 800;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 3px solid var(--gold);
    margin-bottom: 14px;
}}
{ROOT} .t7-abt-team-name {{
    font-family: {font_family};
    font-size: 1rem;
    font-weight: 800;
    margin: 0 0 4px;
    color: var(--text);
}}
{ROOT} .t7-abt-team-role {{
    display: block;
    font-size: .72rem;
    font-weight: 700;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 10px;
}}
{ROOT} .t7-abt-team-bio {{
    font-size: .82rem;
    color: var(--muted);
    line-height: 1.6;
    margin: 0;
}}
/* ════════════════════════════════════════════════════
   CTA
   ════════════════════════════════════════════════════ */
{ROOT} .t7-abt-cta-section {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: #fff;
    border-bottom: none;
}}
{ROOT} .t7-abt-cta-section .t7-abt-section-title {{ color: #fff; }}
{ROOT} .t7-abt-cta-section .t7-body {{ color: rgba(255,255,255,.72); }}
{ROOT} .t7-abt-cta-section .t7-rule {{ background: var(--gold); }}
{ROOT} .t7-abt-cta-buttons {{
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
}}
{ROOT} .t7-abt-cta-section .t7-btn-ghost {{
    border-color: rgba(255,255,255,.3);
    color: rgba(255,255,255,.85);
}}
{ROOT} .t7-abt-cta-section .t7-btn-ghost:hover {{
    border-color: var(--gold);
    color: var(--gold);
}}
/* ════════════════════════════════════════════════════
   RESPONSIVE
   ════════════════════════════════════════════════════ */
@media (max-width: 768px) {{
    {ROOT} .t7-abt-section {{ padding: 48px 20px; }}
    {ROOT} .t7-abt-founder {{
        grid-template-columns: 1fr;
        text-align: center;
        justify-items: center;
    }}
    {ROOT} .t7-abt-gold-dot {{ margin: 16px auto 0; }}
    {ROOT} .t7-abt-phil-grid {{ grid-template-columns: 1fr; gap: 20px; }}
    {ROOT} .t7-abt-team-grid {{ grid-template-columns: repeat(2, 1fr); gap: 20px; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t7-abt-section {{ padding: 40px 16px; }}
    {ROOT} .t7-abt-section-title {{ font-size: 1.3rem; }}
    {ROOT} .t7-abt-founder-img,
    {ROOT} .t7-abt-founder-init {{ width: 96px; height: 96px; }}
    {ROOT} .t7-abt-team-grid {{ grid-template-columns: 1fr; }}
    {ROOT} .t7-abt-cta-buttons {{ flex-direction: column; align-items: center; }}
    {ROOT} .t7-abt-cta-buttons .t7-btn-primary,
    {ROOT} .t7-abt-cta-buttons .t7-btn-ghost {{ width: 100%; text-align: center; max-width: 280px; }}
    {ROOT} .t7-abt-cats {{ gap: 8px; }}
    {ROOT} .t7-abt-cat-pill {{ padding: 7px 16px; font-size: .78rem; }}
}}
"""
    return {"html": html_content, "css": css_content}
