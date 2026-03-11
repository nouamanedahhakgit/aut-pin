"""Copyright Policy page for Theme 7 — Minimalist Glass.
Elegant and airy layout for legal content with soft glows and glassmorphism.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-copyright"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    domain_email = html_module.escape(config.get("domain_email", "contact@domain.com"))
    date_str = datetime.now().strftime("%B %d, %Y")

    html_content = f"""
<div class="dp-t7-copyright">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">Copyright</h1>
      <p class="t7-hero-sub">Effective: {date_str}</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-section">
      <div class="t7-card">
        <h3>Creative Ownership</h3>
        <div class="t7-body">
          <p>Every piece of content at {domain_name} — from our bold photography to our serene prose — is protected by intellectual property rights. We invest heavily in our creative stillness.</p>
        </div>
      </div>
    </div>

    <div class="t7-section">
      <h3>I. Protections</h3>
      <div class="t7-body">
        <p>No part of this website may be reproduced, redistributed, or transformed without our express, quiet written consent. We respect the rights of all creators and expect the same.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>II. Infringements</h3>
      <div class="t7-body">
        <p>If you believe your creative work has been represented without intent, please reach out to our copyright agent immediately with a formal notice.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>Contact us</h3>
      <div class="t7-body">
        <p>Direct all copyright enquiries: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
"""
    return {"html": html_content, "css": css_content}
