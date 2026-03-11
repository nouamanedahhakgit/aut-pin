"""Cookie Policy page for Theme 6 — Neo-Brutalist.
Bold and boxy layout for cookie content with high contrast.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t6-cookies"

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
<div class="dp-t6-cookies">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">Cookie Policy</h1>
      <p class="t6-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t6-wrap">
    <section class="t6-section">
      <h3>What are Cookies?</h3>
      <div class="t6-body">
        <p>Cookies are small text files that websites place on your device to remember your preferences and tracking data. They're like little bold bits of flavor for your browser.</p>
        <p>At {domain_name}, we use cookies to provide a smarter, faster, and bolder user experience.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>1. Types of Cookies We Use</h3>
      <div class="t6-body">
        <ul>
          <li><strong>Essential Cookies:</strong> These are required for the site to function boldly.</li>
          <li><strong>Performance Cookies:</strong> These help us track how visitors use our bold content.</li>
          <li><strong>Targeting Cookies:</strong> These allow us to deliver personalized bold content and ads.</li>
        </ul>
      </div>
    </section>

    <section class="t6-section">
      <h3>2. Controlling Cookies</h3>
      <div class="t6-body">
        <p>Most browsers allow you to manage cookies through their settings. You can block or delete them, though some bold features of our site may not work correctly as a result.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>Contact Us</h3>
      <div class="t6-body">
        <p>If you have any questions about this cookie policy, contact us boldly at: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
