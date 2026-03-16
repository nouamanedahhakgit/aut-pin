"""Cookie Policy page for Theme 8 — Aurora Borealis Dark."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t8-cookie"


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
<div class="dp-t8-cookie">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <h1 class="t8-hero-title">Cookie Policy</h1>
      <p class="t8-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t8-wrap">
    <div class="t8-section">
      <div class="t8-card">
        <h3>Digital Light Markers</h3>
        <div class="t8-body">
          <p>{domain_name} uses cookies to improve your browsing experience. Cookies are small data files stored on your device that help us remember your preferences and understand how you interact with our aurora kitchen.</p>
        </div>
      </div>
    </div>

    <div class="t8-section">
      <h3>Types of Cookies</h3>
      <div class="t8-body">
        <ul>
          <li><strong>Essential:</strong> Necessary for the platform to function correctly.</li>
          <li><strong>Performance:</strong> Helps us analyze user behavior to improve the light we shine.</li>
          <li><strong>Functional:</strong> Remembers your settings and preferences.</li>
        </ul>
      </div>
    </div>

    <div class="t8-section">
      <h3>Managing Cookies</h3>
      <div class="t8-body">
        <p>You can control and manage cookies through your browser settings. Please note that disabling cookies may affect the illumination of certain features on our site.</p>
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
