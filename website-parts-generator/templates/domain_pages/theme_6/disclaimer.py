"""Disclaimer page for Theme 6 — Neo-Brutalist.
Bold and boxy layout for disclaimer content with high contrast.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t6-disclaimer"

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
<div class="dp-t6-disclaimer">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">Disclaimer</h1>
      <p class="t6-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t6-wrap">
    <section class="t6-section">
      <h3>General Bold Disclaimer</h3>
      <div class="t6-body">
        <p>The information provided on {domain_name} is for general informational purposes only. All information is provided in good faith and is part of our bold creative journey.</p>
        <p>While we strive for bold accuracy, we make no representation or warranty of any kind, express or implied, regarding the accuracy, adequacy, or bold reliability of any information on the site.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>1. Culinary & Health Disclaimer</h3>
      <div class="t6-body">
        <p>The recipes and tips on {domain_name} are based on our bold experiences. Always use caution when handling kitchen tools, sharp knives, and high heat. Your bold health and safety are your own responsibility.</p>
        <p>Under no circumstance shall {domain_name} have any liability to you for any bold loss or damage of any kind incurred as a result of the use of the site or reliance on any information provided.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>2. External Links Disclaimer</h3>
      <div class="t6-body">
        <p>Our site may contain bold links to other websites or content belonging to third parties. These bold links are provided for your bold convenience. We do not warrant, endorse, or assume responsibility for the accuracy or reliability of any bold information offered by third-party websites.</p>
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
