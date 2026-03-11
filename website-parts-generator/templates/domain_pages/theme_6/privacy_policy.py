"""Privacy Policy page for Theme 6 — Neo-Brutalist.
Bold and boxy layout for legal content with high contrast.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t6-privacy"

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
<div class="dp-t6-privacy">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">Privacy Policy</h1>
      <p class="t6-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t6-wrap">
    <section class="t6-section">
      <h3>Introduction</h3>
      <div class="t6-body">
        <p>At {domain_name}, we take your privacy as seriously as we take our flavors. This Privacy Policy describes how we collect, use, and protect your information when you visit our website.</p>
        <p>By using our services, you consent to the data practices described in this statement. We are committed to transparency in all our bold digital interactions.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>1. Information We Collect</h3>
      <div class="t6-body">
        <p>We collect information to provide a better, more personalized experience for you:</p>
        <ul>
          <li><strong>Personal Data:</strong> When you subscribe to our newsletter or contact us, we may collect your name and email address.</li>
          <li><strong>Usage Data:</strong> We automatically collect information about how you interact with our site via cookies and analytics.</li>
        </ul>
      </div>
    </section>

    <section class="t6-section">
      <h3>2. How We Use Your Information</h3>
      <div class="t6-body">
        <p>Your data helps us stay bold. We use it to:</p>
        <p>Process your requests, send you creative content, improve our website functionality, and ensure the security of our services.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>Contact Us</h3>
      <div class="t6-body">
        <p>If you have questions about this policy, contact us boldly at: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
