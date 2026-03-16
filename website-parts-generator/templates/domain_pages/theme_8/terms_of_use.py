"""Terms of Use page for Theme 8 — Aurora Borealis Dark."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t8-terms"


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
<div class="dp-t8-terms">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <h1 class="t8-hero-title">Terms of Use</h1>
      <p class="t8-hero-sub">Effective Date: {date_str}</p>
    </div>
  </section>

  <div class="t8-wrap">
    <div class="t8-section">
      <div class="t8-card">
        <h3>Acceptance of Terms</h3>
        <div class="t8-body">
          <p>By accessing {domain_name}, you agree to be bound by these Terms of Use. If you do not agree to these terms, please do not use our illuminated services.</p>
        </div>
      </div>
    </div>

    <div class="t8-section">
      <h3>I. Intellectual Property</h3>
      <div class="t8-body">
        <p>All content on {domain_name} — including text, images, and culinary creations — is the property of the site owners and protected by copyright laws. You may use our content for personal, non-commercial purposes only.</p>
      </div>
    </div>

    <div class="t8-section">
      <h3>II. User Conduct</h3>
      <div class="t8-body">
        <p>We expect our community members to interact with integrity. You may not disrupt our services, harvest data, or use our platform for any unlawful purpose.</p>
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
