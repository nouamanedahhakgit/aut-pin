"""Privacy Policy page for Theme 8 — Aurora Borealis Dark."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t8-privacy"


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
<div class="dp-t8-privacy">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <h1 class="t8-hero-title">Privacy Policy</h1>
      <p class="t8-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t8-wrap">
    <div class="t8-section">
      <div class="t8-card">
        <h3>Your Glow, Your Data</h3>
        <div class="t8-body">
          <p>At {domain_name}, we take your digital privacy as seriously as we take our culinary art. This policy outlines how we protect and respect the information you share with us under the aurora.</p>
        </div>
      </div>
    </div>

    <div class="t8-section">
      <h3>I. Information Collection</h3>
      <div class="t8-body">
        <p>We only collect information that helps illuminate your experience on our platform:</p>
        <ul>
          <li><strong>Identity:</strong> Name and email addresses when voluntarily submitted.</li>
          <li><strong>Engagement:</strong> Analytical data regarding how you move through our recipes.</li>
        </ul>
      </div>
    </div>

    <div class="t8-section">
      <h3>II. Purpose of Processing</h3>
      <div class="t8-body">
        <p>Your data is used solely to refine the light we provide — personalized recipe suggestions, community updates, and platform optimizations.</p>
      </div>
    </div>

    <div class="t8-section">
      <h3>Contact Us</h3>
      <div class="t8-body">
        <p>For any privacy-related enquiries, reach us at: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
