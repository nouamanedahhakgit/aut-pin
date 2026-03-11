"""Terms of Use page for Theme 6 — Neo-Brutalist.
Bold and boxy layout for terms content with high contrast.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t6-terms"

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
<div class="dp-t6-terms">
  <section class="t6-hero">
    <div class="t6-hero-inner">
      <h1 class="t6-hero-title">Terms of Use</h1>
      <p class="t6-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t6-wrap">
    <section class="t6-section">
      <h3>Acceptance of Terms</h3>
      <div class="t6-body">
        <p>By accessing {domain_name}, you agree to these Terms of Use. If you do not agree with any of these terms, you are prohibited from using or accessing this site.</p>
        <p>We are a bold community of food lovers, and we expect everyone to act with respect and flavor.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>1. Use License</h3>
      <div class="t6-body">
        <p>This is a license, not a transfer of title. We grant you permission to view our bold content for personal, non-commercial use only.</p>
        <p>Under this license, you may not modify our bold tutorials, use our content for commercial purposes, or attempt to decompile any software on our site.</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>2. Disclaimer</h3>
      <div class="t6-body">
        <p>The materials on {domain_name} are provided "as is". We make no warranties, expressed or implied, regarding the accuracy or reliability of our bold recipes and tips. Use them boldly and at your own risk!</p>
      </div>
    </section>

    <section class="t6-section">
      <h3>Enquiries</h3>
      <div class="t6-body">
        <p>If you have any questions about these terms, contact us boldly at: <a href="mailto:{domain_email}">{domain_email}</a></p>
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
