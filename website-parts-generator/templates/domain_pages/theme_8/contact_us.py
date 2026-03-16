"""Contact Us page for Theme 8 — Aurora Borealis Dark.
Neon-themed contact form with glowing inputs and glassmorphism containers.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t8-contact"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name  = html_module.escape(config.get("domain_name", "My Blog"))
    domain_email = html_module.escape(config.get("domain_email", "contact@domain.com"))

    html_content = f"""
<div class="dp-t8-contact">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <span class="t8-hero-label">Connect</span>
      <h1 class="t8-hero-title">Stay in Touch</h1>
      <p class="t8-hero-sub">Have a question or want to share your aurora moments? Reach out to the {domain_name} team.</p>
    </div>
  </section>

  <div class="t8-wrap">
    <div class="t8-section">
      <div class="t8-card">
        <h3>Send a Message</h3>
        <div class="t8-body">
          <form class="t8-contact-form">
            <div class="t8-form-row">
              <div class="t8-input-wrap">
                <input type="text" placeholder="Your Name" class="t8-input">
              </div>
              <div class="t8-input-wrap">
                <input type="email" placeholder="Email Address" class="t8-input">
              </div>
            </div>
            <div class="t8-input-wrap">
              <textarea placeholder="How can we help?" class="t8-textarea"></textarea>
            </div>
            <button type="submit" class="t8-btn-primary">SEND MESSAGE ✦</button>
          </form>
          <div class="t8-contact-info">
            <div class="t8-info-item">
              <strong>DIRECT EMAIL:</strong>
              <a href="mailto:{domain_email}">{domain_email}</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} background: var(--bg); }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{hero_css(ROOT, font_family)}
{body_css(ROOT, font_family)}

{ROOT} .t8-contact-form {{
    display: flex;
    flex-direction: column;
    gap: 24px;
    margin-bottom: 48px;
}}
{ROOT} .t8-form-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}}
{ROOT} .t8-input-wrap {{ position: relative; }}
{ROOT} .t8-input, {ROOT} .t8-textarea {{
    width: 100%;
    padding: 18px 24px;
    background: rgba(15, 22, 36, 0.4);
    border: 1px solid var(--border);
    border-radius: 16px;
    font-size: 1rem;
    color: var(--text);
    transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
}}
{ROOT} .t8-input:focus, {ROOT} .t8-textarea:focus {{
    outline: none;
    border-color: var(--secondary);
    background: rgba(6,182,212,0.05);
    box-shadow: 0 0 20px rgba(6,182,212,0.15);
}}
{ROOT} .t8-textarea {{
    height: 180px;
    resize: vertical;
}}
{ROOT} .t8-contact-info {{
    padding-top: 32px;
    border-top: 1px solid rgba(124,58,237,0.15);
}}
{ROOT} .t8-info-item {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
{ROOT} .t8-info-item strong {{
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    color: var(--primary);
}}
{ROOT} .t8-info-item a {{
    font-size: 1.1rem;
    color: var(--text);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}}
{ROOT} .t8-info-item a:hover {{ color: var(--secondary); }}

@media (max-width: 600px) {{
    {ROOT} .t8-form-row {{ grid-template-columns: 1fr; }}
}}
"""
    return {"html": html_content, "css": css_content}
