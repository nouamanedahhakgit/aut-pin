"""GDPR Policy page for Theme 8 — Aurora Borealis Dark."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t8-gdpr"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    domain_email = html_module.escape(config.get("domain_email", "privacy@domain.com"))
    date_str = datetime.now().strftime("%B %d, %Y")

    html_content = f"""
<div class="dp-t8-gdpr">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <h1 class="t8-hero-title">GDPR Rights</h1>
      <p class="t8-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t8-wrap">
    <div class="t8-section">
      <div class="t8-card">
        <h3>Privacy Compliance</h3>
        <div class="t8-body">
          <p>For our users within the European Economic Area (EEA), {domain_name} is committed to full compliance with the General Data Protection Regulation (GDPR).</p>
        </div>
      </div>
    </div>

    <div class="t8-section">
      <h3>Your Rights</h3>
      <div class="t8-body">
        <ul>
          <li><strong>Right to Access:</strong> Request a copy of the data we hold.</li>
          <li><strong>Right to Rectification:</strong> Ask us to correct inaccurate information.</li>
          <li><strong>Right to Erasure:</strong> Request the deletion of your data (The Right to be Forgotten).</li>
          <li><strong>Right to Portability:</strong> Transfer your data to another service.</li>
        </ul>
      </div>
    </div>

    <div class="t8-section">
      <h3>Inquiries</h3>
      <div class="t8-body">
        <p>To exercise any of these rights, please contact our Data protection officer at: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
"""
    return {"html": html_content, "css": css_content}
