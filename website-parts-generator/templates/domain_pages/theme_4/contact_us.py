"""Contact Us page for Theme 7 — Midnight Luxe.
2-column layout: form + sidebar info cards, gradient hero, gold accents.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t7-contact"
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

    # ── Email derivation ─────────────────────────────────────────────
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
    email = f"contact@{d}"

    # ── Hero ─────────────────────────────────────────────────────────
    hero_section = f"""
    <section class="t7-hero">
      <div class="t7-hero-inner">
        <span class="t7-badge">We&rsquo;d love to hear from you!</span>
        <h1 class="t7-hero-title">Get in Touch</h1>
        <p class="t7-hero-sub">Questions, feedback, or just a friendly hello &mdash; we&rsquo;re all ears.</p>
      </div>
    </section>"""

    # ── Form ─────────────────────────────────────────────────────────
    form_html = f"""
        <div class="t7-ct-form-card t7-card">
          <h2 class="t7-ct-form-title">Send Us a Message</h2>
          <div class="t7-ct-gold-rule"></div>
          <form class="t7-ct-form" action="#" method="post" onsubmit="return false;">
            <div class="t7-ct-field">
              <label class="t7-ct-label" for="t7-ct-name">Your Name</label>
              <input class="t7-ct-input" type="text" id="t7-ct-name" name="name"
                     placeholder="e.g. Julia Child" required>
            </div>
            <div class="t7-ct-field">
              <label class="t7-ct-label" for="t7-ct-email">Email Address</label>
              <input class="t7-ct-input" type="email" id="t7-ct-email" name="email"
                     placeholder="you@example.com" required>
            </div>
            <div class="t7-ct-field">
              <label class="t7-ct-label" for="t7-ct-subject">Subject</label>
              <select class="t7-ct-select" id="t7-ct-subject" name="subject">
                <option value="">Choose a topic&hellip;</option>
                <option value="general">General Inquiry</option>
                <option value="recipe">Recipe Question</option>
                <option value="feedback">Feedback &amp; Suggestions</option>
                <option value="collaborate">Collaboration</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div class="t7-ct-field">
              <label class="t7-ct-label" for="t7-ct-message">Message</label>
              <textarea class="t7-ct-textarea" id="t7-ct-message" name="message" rows="6"
                        placeholder="Tell us what&rsquo;s on your mind&hellip;" required></textarea>
            </div>
            <button class="t7-btn-primary t7-ct-submit" type="submit">Send Message</button>
          </form>
        </div>"""

    # ── Sidebar info cards ───────────────────────────────────────────
    info_cards = [
        {
            "icon": "&#9993;",
            "title": "Email Us",
            "desc": f'Drop us a line any time at <a href="mailto:{e(email)}" class="t7-ct-link">{e(email)}</a>. We typically respond within 24 hours.',
        },
        {
            "icon": "&#127860;",
            "title": "Recipe Feedback",
            "desc": "Tried one of our recipes? We&rsquo;d love to hear how it turned out. Share your tips, tweaks, or photos!",
        },
        {
            "icon": "&#129309;",
            "title": "Collaborate",
            "desc": "Interested in partnerships, guest posts, or brand collaborations? Let&rsquo;s create something delicious together.",
        },
    ]

    sidebar_html = ""
    for ic in info_cards:
        sidebar_html += f"""
        <div class="t7-ct-info-card t7-card">
          <span class="t7-ct-info-icon">{ic["icon"]}</span>
          <h3 class="t7-ct-info-title">{ic["title"]}</h3>
          <p class="t7-ct-info-desc">{ic["desc"]}</p>
        </div>"""

    # ── Assemble HTML ────────────────────────────────────────────────
    html_content = f"""
<main class="dp-t7-contact">
  {hero_section}
  <section class="t7-ct-body-section">
    <div class="t7-ct-layout">
      <div class="t7-ct-main">
        {form_html}
      </div>
      <aside class="t7-ct-sidebar">
        {sidebar_html}
      </aside>
    </div>
  </section>
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
   LAYOUT
   ════════════════════════════════════════════════════ */
{ROOT} .t7-ct-body-section {{
    padding: 64px 32px 80px;
    background: var(--bg);
}}
{ROOT} .t7-ct-layout {{
    max-width: 1060px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 40px;
    align-items: start;
}}
/* ════════════════════════════════════════════════════
   FORM CARD
   ════════════════════════════════════════════════════ */
{ROOT} .t7-ct-form-card {{
    padding: 40px 36px;
}}
{ROOT} .t7-ct-form-title {{
    font-family: {font_family};
    font-size: 1.35rem;
    font-weight: 800;
    margin: 0 0 8px;
    color: var(--text);
    letter-spacing: .3px;
}}
{ROOT} .t7-ct-gold-rule {{
    width: 36px;
    height: 3px;
    background: var(--gold);
    border-radius: 2px;
    margin-bottom: 28px;
}}
{ROOT} .t7-ct-form {{
    display: flex;
    flex-direction: column;
    gap: 20px;
}}
{ROOT} .t7-ct-field {{
    display: flex;
    flex-direction: column;
    gap: 6px;
}}
{ROOT} .t7-ct-label {{
    font-size: .78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--muted);
}}
{ROOT} .t7-ct-input,
{ROOT} .t7-ct-select,
{ROOT} .t7-ct-textarea {{
    border: 1px solid var(--border);
    border-radius: calc(var(--radius) * .6);
    padding: 12px 16px;
    font-size: .9rem;
    font-family: {body_font};
    color: var(--text);
    background: var(--bg);
    outline: none;
    transition: border-color .3s, box-shadow .3s;
    width: 100%;
}}
{ROOT} .t7-ct-input:focus,
{ROOT} .t7-ct-select:focus,
{ROOT} .t7-ct-textarea:focus {{
    border-color: var(--gold);
    box-shadow: 0 0 0 3px rgba(212,168,83,.12);
}}
{ROOT} .t7-ct-select {{
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%23555' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 16px center;
    padding-right: 40px;
}}
{ROOT} .t7-ct-textarea {{
    resize: vertical;
    min-height: 130px;
}}
{ROOT} .t7-ct-submit {{
    align-self: flex-start;
    margin-top: 4px;
}}
/* ════════════════════════════════════════════════════
   SIDEBAR INFO CARDS
   ════════════════════════════════════════════════════ */
{ROOT} .t7-ct-sidebar {{
    display: flex;
    flex-direction: column;
    gap: 20px;
}}
{ROOT} .t7-ct-info-card {{
    padding: 28px 24px;
    text-align: center;
}}
{ROOT} .t7-ct-info-icon {{
    display: inline-block;
    font-size: 1.6rem;
    margin-bottom: 12px;
    line-height: 1;
}}
{ROOT} .t7-ct-info-title {{
    font-family: {font_family};
    font-size: 1rem;
    font-weight: 800;
    margin: 0 0 8px;
    color: var(--text);
}}
{ROOT} .t7-ct-info-desc {{
    font-size: .84rem;
    color: var(--muted);
    line-height: 1.6;
    margin: 0;
}}
{ROOT} .t7-ct-link {{
    color: var(--primary);
    text-decoration: underline;
    text-underline-offset: 3px;
    transition: color .3s;
}}
{ROOT} .t7-ct-link:hover {{ color: var(--gold); }}
/* ════════════════════════════════════════════════════
   RESPONSIVE
   ════════════════════════════════════════════════════ */
@media (max-width: 768px) {{
    {ROOT} .t7-ct-body-section {{ padding: 48px 20px 64px; }}
    {ROOT} .t7-ct-layout {{
        grid-template-columns: 1fr;
        gap: 32px;
    }}
    {ROOT} .t7-ct-form-card {{ padding: 32px 24px; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t7-ct-body-section {{ padding: 36px 16px 48px; }}
    {ROOT} .t7-ct-form-card {{ padding: 24px 18px; }}
    {ROOT} .t7-ct-form-title {{ font-size: 1.15rem; }}
    {ROOT} .t7-ct-submit {{ width: 100%; text-align: center; }}
    {ROOT} .t7-ct-info-card {{ padding: 24px 18px; }}
}}
"""
    return {"html": html_content, "css": css_content}
