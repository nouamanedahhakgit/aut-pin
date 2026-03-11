"""GDPR Policy page for Theme 6 — Neo-Brutalist.
Bold and boxy layout for GDPR content with high contrast.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t6-gdpr"

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
<div class="dp-t6-gdpr">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">GDPR Policy</h1>
      <p class="t6-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t6-wrap">
    <section class="t6-section">
      <h3>Data Controller</h3>
      <div class="t6-body">
        <p>{domain_name} is the Data Controller of your bold information. We are committed to your bold privacy rights under the GDPR.</p>
        <p>You can contact our bold data protection team at: <a href="mailto:{domain_email}">{domain_email}</a></p>
      </div>
    </section>

    <section class="t6-section">
      <h3>1. Your Rights</h3>
      <div class="t6-body">
        <p>Under the GDPR, you have the following bold rights:</p>
        <ul>
          <li><strong>Right of Access:</strong> You can request a copy of your bold data.</li>
          <li><strong>Right to Rectification:</strong> You can request to correct your bold data.</li>
          <li><strong>Right to Erasure:</strong> You can request to delete your bold data.</li>
          <li><strong>Right to Data Portability:</strong> You can request your bold data in a portable format.</li>
        </ul>
      </div>
    </section>

    <section class="t6-section">
      <h3>2. Legal Basis</h3>
      <div class="t6-body">
        <p>We process your bold data based on your bold consent, our bold legitimate interests, and our bold legal obligations.</p>
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
"""
    return {"html": html_content, "css": css_content}
