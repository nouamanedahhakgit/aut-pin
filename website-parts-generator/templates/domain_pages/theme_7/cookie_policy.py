"""Cookie Policy page for Theme 7 — Minimalist Glass.
Elegant and airy layout for legal content with soft glows and glassmorphism.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-cookies"

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
<div class="dp-t7-cookies">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">Cookie Policy</h1>
      <p class="t7-hero-sub">Effective: {date_str}</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-section">
      <div class="t7-card">
        <h3>Subtle Preferences</h3>
        <div class="t7-body">
          <p>Cookies are small tokens we use to remember your aesthetic preferences. They allow {domain_name} to recognize your browser and provide a more refined, personally curated experience.</p>
        </div>
      </div>
    </div>

    <div class="t7-section">
      <h3>I. Essential Reflections</h3>
      <div class="t7-body">
        <p>Some cookies are critical for our silence and stability. These allow you to navigate and use the essential features of our site.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>II. Insights</h3>
      <div class="t7-body">
        <p>We use analysis cookies to track where our visitors come from and how they engage with our bold, serene content. This helps us refine our creative output.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>Reach Out</h3>
      <div class="t7-body">
        <p>If you have questions about our use of cookies, contact us: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
