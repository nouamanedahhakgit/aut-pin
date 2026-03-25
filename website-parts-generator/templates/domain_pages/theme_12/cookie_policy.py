"""Theme 12 — Cookie Policy: Candy Pop."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t12-cookie">
  <section class="dp-t12-hero">
    <div class="dp-t12-hero-blob1"></div>
    <div class="dp-t12-hero-blob2"></div>
    <span class="dp-t12-hero-badge">&#127850; Cookie Time!</span>
    <h1>Cookie <em>Policy</em></h1>
    <p>How {name} uses cookies (the digital kind, not the chocolate chip kind!).</p>
  </section>
  <div class="dp-t12-body">
    <section class="dp-t12-section"><h2 class="dp-t12-h2">What Are Cookies</h2><p>Cookies are small text files stored on your device when you visit a website. They help remember your preferences.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">How We Use Cookies</h2><p>{name} uses cookies to analyze traffic, remember your preferences, and deliver relevant content.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Third-Party Cookies</h2><p>Some cookies are placed by third-party services like Google Analytics. These are governed by their own privacy policies.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Managing Cookies</h2><p>You can control cookies through your browser settings. Disabling cookies may affect how our site works.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Updates</h2><p>We may update this policy from time to time. Check back for any changes!</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t12-cookie {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
