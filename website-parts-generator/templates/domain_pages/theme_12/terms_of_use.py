"""Theme 12 — Terms of Use: Candy Pop."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t12-terms">
  <section class="dp-t12-hero">
    <div class="dp-t12-hero-blob1"></div>
    <div class="dp-t12-hero-blob2"></div>
    <span class="dp-t12-hero-badge">&#128220; Legal Stuff</span>
    <h1>Terms of <em>Use</em></h1>
    <p>The ground rules for using {name}. &#128221;</p>
  </section>
  <div class="dp-t12-body">
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Acceptance of Terms</h2><p>By accessing and using {name}, you accept and agree to be bound by these Terms. If you disagree, please don't use our website.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Use of Content</h2><p>All content on {name} is protected by copyright. You may view and print content for personal, non-commercial use only.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">User Conduct</h2><p>Please be nice! Don't use our website for unlawful purposes, don't interfere with the site, and don't impersonate anyone.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Disclaimer of Warranties</h2><p>{name} is provided "as is" without warranties. We try our best, but can't guarantee everything will be perfect!</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Limitation of Liability</h2><p>{name} shall not be liable for any damages arising from the use or inability to use our website.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Changes to Terms</h2><p>We may modify these terms at any time. Continued use of the site means you accept any changes.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t12-terms {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
