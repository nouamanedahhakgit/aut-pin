"""About Us page for Theme 7 — Minimalist Glass.
Elegant, airy layout with soft glows and glassmorphism cards.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t7-about"

def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    domain_description = html_module.escape(config.get("domain_description", "Experience culinary art through a lens of purity and refined simplicity."))

    html_content = f"""
<div class="dp-t7-about">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">Our Story</h1>
      <p class="t7-hero-sub">Elegance, stillness, and flavor at {domain_name}.</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-section">
      <div class="t7-card">
        <h3>Purity of Intent</h3>
        <div class="t7-body">
          <p>{domain_description}</p>
          <p>At {domain_name}, we approach every recipe as a piece of art. Our mission is to strip away the noise of the kitchen and focus on the core beauty of ingredients and the quiet joy of creation.</p>
        </div>
      </div>
    </div>

    <div class="t7-section">
      <div class="t7-card" style="border: none; background: transparent; box-shadow: none;">
        <h3>The Serenity Principles</h3>
        <div class="t7-body">
          <p>We follow a path of refined simplicity in everything we do:</p>
          <ul>
            <li><strong>Minimalist Composition:</strong> Focusing on essential flavors.</li>
            <li><strong>Refined Aesthetics:</strong> Every dish is a visual and sensory peace of mind.</li>
            <li><strong>Soulful Curation:</strong> We only share what we truly love.</li>
          </ul>
        </div>
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
