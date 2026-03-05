"""Theme 2 — Cookie Policy: Modern clean style, accent bar headings."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    html_content = f"""
<div class="domain-page dp-t2-cookie">
  <section class="dp-t2-hero">
    <p class="dp-t2-hero-label">Legal</p>
    <h1>Cookie Policy</h1>
    <p>Learn how {name} uses cookies to improve your experience.</p>
  </section>
  <div class="dp-t2-body">
    <section class="dp-t2-section"><h2 class="dp-t2-h2">What Are Cookies</h2><p>Cookies are small text files stored on your device when you visit a website. They are widely used to make websites work more efficiently and to provide information to the website owners.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">How We Use Cookies</h2>
      <ul>
        <li><strong>Essential Cookies</strong> — Required for basic site functionality.</li>
        <li><strong>Analytics Cookies</strong> — Help us understand how visitors interact with our site.</li>
        <li><strong>Preference Cookies</strong> — Remember your settings and preferences.</li>
        <li><strong>Advertising Cookies</strong> — May be used by third-party ad networks.</li>
      </ul>
    </section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Third-Party Cookies</h2><p>Some cookies are placed by third-party services. We do not control these cookies. Please refer to their respective privacy policies.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Managing Cookies</h2><p>You can control and manage cookies through your browser settings. Note that disabling cookies may affect site functionality.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Cookie Duration</h2><p>Session cookies are deleted when you close your browser. Persistent cookies remain for a set period or until you delete them.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Updates</h2><p>We may update this Cookie Policy from time to time. We encourage you to check this page periodically.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t2-cookie {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
