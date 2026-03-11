"""Disclaimer page for Theme 7 — Minimalist Glass.
Elegant and airy layout for legal content with soft glows and glassmorphism.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-disclaimer"

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
<div class="dp-t7-disclaimer">
  <section class="t7-hero">
    <div class="t7-hero-inner">
      <h1 class="t7-hero-title">Disclaimer</h1>
      <p class="t7-hero-sub">Effective: {date_str}</p>
    </div>
  </section>

  <div class="t7-wrap">
    <div class="t7-section">
      <div class="t7-card">
        <h3>Shared Intent</h3>
        <div class="t7-body">
          <p>The information on {domain_name} is shared in the spirit of exploration and creativity. While we strive for quiet accuracy, we make no warranties of any kind regarding the serenity and reliability of the data presented.</p>
        </div>
      </div>
    </div>

    <div class="t7-section">
      <h3>I. Culinary & Health</h3>
      <div class="t7-body">
        <p>Our recipes and tips are based on our bold personal creations. Use common sense and professional advice when handling high heat, allergens, and kitchen tools. You are responsible for your own bold safety.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>II. External Paths</h3>
      <div class="t7-body">
        <p>We may provide quiet links to other websites or content belonging to third parties. We do not warrant, endorse, or assume responsibility for the accuracy or quiet reliability of any information offered by third-party websites.</p>
      </div>
    </div>

    <div class="t7-section">
      <h3>Enquiries</h3>
      <div class="t7-body">
        <p>Direct all disclaimer enquiries: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
