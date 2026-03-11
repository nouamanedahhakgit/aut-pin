"""Privacy Policy page for Theme 7 — Minimalist Glass.
Elegant and airy layout for legal content with soft glows and glassmorphism.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-privacy"

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
<div class="dp-t7-privacy">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">Privacy Policy</h1>
      <p class="t7-hero-sub">Effective: {date_str}</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-section">
      <div class="t7-card">
        <h3>Commitment to Stillness</h3>
        <div class="t7-body">
          <p>At {domain_name}, we respect your quiet reflection and your privacy. This statement clarifies our transparent and balanced data practices.</p>
          <p>Your trust is essential for our serene community. We collect only what is necessary to refine your experience.</p>
        </div>
      </div>
    </div>

    <div class="t7-section">
      <h3>I. Data We Curate</h3>
      <div class="t7-body">
        <p>In our pursuit of excellence, we may collect the following data points:</p>
        <ul>
          <li><strong>Identity:</strong> Your name and email when shared through our beautiful forms.</li>
          <li><strong>Refinement:</strong> Usage data to help us track the serenity of our pages.</li>
        </ul>
      </div>
    </div>

    <div class="t7-section">
      <h3>II. Our Purpose</h3>
      <div class="t7-body">
        <p>Every piece of data is used to improve our shared silence. We use it to communicate, analyze, and refine the quality of {domain_name}.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>Reach Out</h3>
      <div class="t7-body">
        <p>For any questions on our serene practices, contact us: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
