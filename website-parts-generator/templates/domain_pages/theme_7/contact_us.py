"""Contact Us page for Theme 7 — Minimalist Glass.
Elegant contact form with translucent inputs and soft glowing effects.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t7-contact"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    domain_email = html_module.escape(config.get("domain_email", "contact@domain.com"))

    html_content = f"""
<div class="dp-t7-contact">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">Connect</h1>
      <p class="t7-hero-sub">Stay in touch with {domain_name}.</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-section">
      <div class="t7-card">
        <h3>Share a Whisper</h3>
        <div class="t7-body">
          <form class="t7-contact-form">
            <div class="t7-form-row">
              <input type="text" placeholder="Name" class="t7-input">
              <input type="email" placeholder="Email" class="t7-input">
            </div>
            <textarea placeholder="Message" class="t7-textarea"></textarea>
            <button type="submit" class="t7-btn-primary">SEND MESSAGE</button>
          </form>
          <div class="t7-contact-info">
            <p><strong>REACH US:</strong> <a href="mailto:{domain_email}">{domain_email}</a></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{hero_css(ROOT, font_family)}
{body_css(ROOT, font_family)}

{ROOT} .t7-contact-form {{
    display: flex;
    flex-direction: column;
    gap: 24px;
    margin-bottom: 40px;
}}
{ROOT} .t7-form-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}}
{ROOT} .t7-input, {ROOT} .t7-textarea {{
    width: 100%;
    padding: 16px 24px;
    background: rgba(44, 62, 80, 0.03);
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 50px;
    font-size: 0.95rem;
    color: var(--primary);
    transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
}}
{ROOT} .t7-input:focus, {ROOT} .t7-textarea:focus {{
    outline: none;
    border-color: var(--secondary);
    background: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}}
{ROOT} .t7-textarea {{
    height: 200px;
    border-radius: 20px;
    resize: vertical;
}}
{ROOT} .t7-contact-info {{
    padding-top: 32px;
    border-top: 1px solid rgba(0,0,0,0.05);
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
@media (max-width: 600px) {{
    {ROOT} .t7-form-row {{ grid-template-columns: 1fr; }}
}}
"""
    return {"html": html_content, "css": css_content}
