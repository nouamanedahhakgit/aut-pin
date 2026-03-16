"""Copyright Policy page for Theme 8 — Aurora Borealis Dark."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t8-copyright"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    year = datetime.now().year

    html_content = f"""
<div class="dp-t8-copyright">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <h1 class="t8-hero-title">Copyright Policy</h1>
      <p class="t8-hero-sub">&copy; {year} {domain_name}</p>
    </div>
  </section>

  <div class="t8-wrap">
    <div class="t8-section">
      <div class="t8-card">
        <h3>Creative Ownership</h3>
        <div class="t8-body">
          <p>All recipes, photography, and design elements featured on {domain_name} are the original intellectual property of the site creators, unless otherwise stated. We work hard to create this light — please respect it.</p>
        </div>
      </div>
    </div>

    <div class="t8-section">
      <h3>Usage Permissions</h3>
      <div class="t8-body">
        <p>You are welcome to share a link to our recipes or use a single photo with a direct link back to the original post on {domain_name}. However, republishing the full recipe or multiple photos is strictly prohibited without prior written consent.</p>
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
