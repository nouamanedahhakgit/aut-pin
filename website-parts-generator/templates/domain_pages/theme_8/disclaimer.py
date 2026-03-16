"""Disclaimer page for Theme 8 — Aurora Borealis Dark."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t8-disclaimer"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    date_str = datetime.now().strftime("%B %d, %Y")

    html_content = f"""
<div class="dp-t8-disclaimer">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <h1 class="t8-hero-title">Disclaimer</h1>
      <p class="t8-hero-sub">Effective: {date_str}</p>
    </div>
  </section>

  <div class="t8-wrap">
    <div class="t8-section">
      <div class="t8-card">
        <h3>Navigational Clarity</h3>
        <div class="t8-body">
          <p>The information provided on {domain_name} is for general informational and inspirational purposes only. While we strive to provide accurate and illuminated content, we make no representations or warranties of any kind.</p>
        </div>
      </div>
    </div>

    <div class="t8-section">
      <h3>I. Culinary & Safety</h3>
      <div class="t8-body">
        <p>Our recipes are tested in our own aurora kitchen. However, cooking involves inherent risks. Always use caution with heat, sharp tools, and allergens. {domain_name} is not responsible for any incidents occurring in your own kitchen.</p>
      </div>
    </div>

    <div class="t8-section">
      <h3>II. External Shimmers</h3>
      <div class="t8-body">
        <p>Our site may contain links to external websites. We do not endorse or assume responsibility for the content, privacy policies, or practices of any third-party services.</p>
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
