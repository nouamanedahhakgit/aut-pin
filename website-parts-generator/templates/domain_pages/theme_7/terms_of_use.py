"""Terms of Use page for Theme 7 — Minimalist Glass.
Elegant and airy layout for legal content with soft glows and glassmorphism.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-terms"

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
<div class="dp-t7-terms">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">Terms of Use</h1>
      <p class="t7-hero-sub">Effective: {date_str}</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-section">
      <div class="t7-card">
        <h3>Acceptance of Serenity</h3>
        <div class="t7-body">
          <p>By entering {domain_name}, you align yourself with our terms of refined engagement. If these terms do not resonate with your intent, we ask that you depart in peace.</p>
        </div>
      </div>
    </div>

    <div class="t7-section">
      <h3>I. Refined Usage</h3>
      <div class="t7-body">
        <p>Our content is intended for your personal, aesthetic inspiration. We grant you a limited license to explore our bold and quiet creations for non-commercial purposes only.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>II. Integrity</h3>
      <div class="t7-body">
        <p>You may not disrupt the stillness of our services, harvest data without intent, or misrepresent the source of our creative output.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>Enquiries</h3>
      <div class="t7-body">
        <p>For clarifications on our terms, reach out: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
