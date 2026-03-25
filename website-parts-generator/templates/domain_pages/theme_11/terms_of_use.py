"""Theme 11 — Terms of Use: Art Deco Elegance."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t11-terms">
  <section class="dp-t11-hero">
    <p class="dp-t11-hero-label">&#9671; Legal &#9671;</p>
    <h1>Terms of <em>Use</em></h1>
    <p>Please read these terms carefully before using {name}.</p>
    <div class="dp-t11-ornament">&#9670;</div>
  </section>
  <div class="dp-t11-body">
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Acceptance of Terms</h2><p>By accessing and using {name}, you accept and agree to be bound by these Terms of Use. If you do not agree, please do not use our website.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Use of Content</h2><p>All content on {name}, including recipes, photographs, text, and graphics, is protected by copyright. You may view and print content for personal, non-commercial use only.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">User Conduct</h2><p>You agree not to use our website for any unlawful purpose, not to interfere with the site's operation, and not to impersonate any person or entity.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Disclaimer of Warranties</h2><p>{name} is provided "as is" without warranties of any kind. We do not guarantee the accuracy, completeness, or usefulness of any information on the site.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Limitation of Liability</h2><p>{name} shall not be liable for any damages arising from the use or inability to use our website, including but not limited to direct, indirect, incidental, or consequential damages.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Changes to Terms</h2><p>We reserve the right to modify these terms at any time. Continued use of the site constitutes acceptance of any changes.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t11-terms {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
