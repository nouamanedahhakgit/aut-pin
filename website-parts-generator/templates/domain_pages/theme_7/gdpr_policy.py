"""GDPR Policy page for Theme 7 — Minimalist Glass.
Elegant and airy layout for legal content with soft glows and glassmorphism.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-gdpr"

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
<div class="dp-t7-gdpr">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">GDPR Policy</h1>
      <p class="t7-hero-sub">Effective: {date_str}</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-section">
      <div class="t7-card">
        <h3>Data Controller</h3>
        <div class="t7-body">
          <p>{domain_name} acts as the Data Controller. We are committed to transparency in our bold data handling practices, in accordance with the GDPR.</p>
        </div>
      </div>
    </div>

    <div class="t7-section">
      <h3>I. Your Privacy Rights</h3>
      <div class="t7-body">
        <p>Under the General Data Protection Regulation, you have the right to access, rectify, or erase your bold data at any time. We respect your quiet decision to withdraw consent or object to processing.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>II. Lawful Basis</h3>
      <div class="t7-body">
        <p>We process your data based on your quiet consent, our bold legitimate interests, and our absolute legal obligations.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>Reach Out</h3>
      <div class="t7-body">
        <p>For any enquiries on our GDPR practices, contact us: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
