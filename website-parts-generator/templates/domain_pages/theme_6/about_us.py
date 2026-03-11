"""About Us page for Theme 6 — Neo-Brutalist.
Bold and boxy layout with thick black borders, high-contrast hover effects.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t6-about"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    domain_description = html_module.escape(config.get("domain_description", "Welcome to our incredible collection of recipes and cooking tips."))

    html_content = f"""
<div class="dp-t6-about">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">About {domain_name}</h1>
      <p class="t6-hero-sub">Our story of boldness and flavor.</p>
    </div>
  </section>

  <div class="t6-wrap">
    <section class="t6-section">
      <h3>Who We Are</h3>
      <div class="t6-body">
        <p>{domain_description}</p>
        <p>At {domain_name}, we believe that food should never be boring. Our team of culinary enthusiasts is passionate about exploring the boldest ingredients, the most innovative techniques, and the most vibrant food cultures on the planet.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>Our Philosophy</h3>
      <div class="t6-body">
        <p>We embrace the "Neo-Brutalist" approach to home cooking: clear, direct, and packed with impact. No unnecessary fluff, just amazing flavors and techniques that work every time.</p>
        <ul>
          <li><strong>Quality Ingredients:</strong> Only the best and freshest produce.</li>
          <li><strong>Bold Flavors:</strong> We don't hold back on spices or seasoning.</li>
          <li><strong>Accessible Mastery:</strong> We break down complex skills into bold, clear steps.</li>
        </ul>
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
