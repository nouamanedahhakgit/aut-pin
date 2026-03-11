"""Copyright Policy page for Theme 6 — Neo-Brutalist.
Bold and boxy layout for copyright content with high contrast.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t6-copyright"

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
<div class="dp-t6-copyright">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">Copyright Policy</h1>
      <p class="t6-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t6-wrap">
    <section class="t6-section">
      <h3>Ownership of Bold Content</h3>
      <div class="t6-body">
        <p>All content on {domain_name}, including but not limited to the bold text, vibrant images, creative recipes, and bold videos, is the property of {domain_name} and is protected by copyright laws.</p>
        <p>We work hard to create bold culinary content. Please respect our creative investment.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>1. DMCA Compliance</h3>
      <div class="t6-body">
        <p>We strictly respect the intellectual property of others. If you believe your bold content has been copied in a way that constitutes copyright infringement, please provide our Copyright Agent with a formal notice.</p>
        <p>Your notice must include your physical/electronic signature, a description of the copyrighted work, and a bold statement of good faith belief.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>2. Reporting Infringement</h3>
      <div class="t6-body">
        <p>Please send all copyright notices boldly to: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
