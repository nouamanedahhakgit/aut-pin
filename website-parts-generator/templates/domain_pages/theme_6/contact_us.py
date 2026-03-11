"""Contact Us page for Theme 6 — Neo-Brutalist.
Bold contact form with thick borders and striking hover effects.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t6-contact"

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
<div class="dp-t6-contact">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">Get in Touch</h1>
      <p class="t6-hero-sub">We'd love to hear your boldest flavor stories.</p>
    </div>
  </section>

  <div class="t6-wrap">
    <section class="t6-section">
      <h3>Send a Message</h3>
      <div class="t6-body">
        <form class="t6-contact-form">
          <div class="t6-form-row">
            <input type="text" placeholder="Your Name" class="t6-input">
            <input type="email" placeholder="Your Email" class="t6-input">
          </div>
          <textarea placeholder="Your Message" class="t6-textarea"></textarea>
          <button type="submit" class="t6-btn-primary">Send Boldly</button>
        </form>
        <div class="t6-contact-info">
          <p><strong>Email:</strong> <a href="mailto:{domain_email}">{domain_email}</a></p>
          <p>We aim to respond to all enquiries within 48 bold hours.</p>
        </div>
      </div>
    </section>
  </div>
</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{hero_css(ROOT, font_family)}
{body_css(ROOT, font_family)}

{ROOT} .t6-contact-form {{
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 40px;
}}
{ROOT} .t6-form-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}}
{ROOT} .t6-input, {ROOT} .t6-textarea {{
    width: 100%;
    padding: 16px;
    border: var(--border-width) solid var(--border);
    font-size: 1rem;
    font-weight: 700;
    box-shadow: 4px 4px 0px #000;
}}
{ROOT} .t6-input:focus, {ROOT} .t6-textarea:focus {{
    outline: none;
    background: var(--primary);
}}
{ROOT} .t6-textarea {{
    height: 180px;
    resize: vertical;
}}
{ROOT} .t6-contact-info {{
    padding: 30px;
    background: #fafafa;
    border: 3px solid #000;
}}
@media (max-width: 600px) {{
    {ROOT} .t6-form-row {{ grid-template-columns: 1fr; }}
}}
"""
    return {"html": html_content, "css": css_content}
