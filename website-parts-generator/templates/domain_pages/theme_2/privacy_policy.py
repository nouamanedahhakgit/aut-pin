"""Theme 2 — Privacy Policy: Modern clean style, accent bar headings."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    html_content = f"""
<div class="domain-page dp-t2-privacy">
  <section class="dp-t2-hero">
    <p class="dp-t2-hero-label">Legal</p>
    <h1>Privacy Policy</h1>
    <p>Your privacy matters to us. Learn how {name} handles your information.</p>
  </section>
  <div class="dp-t2-body">
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Information We Collect</h2><p>We may collect personal information such as your name and email address when you subscribe, comment, or fill out a form. We also collect non-personal data through analytics tools.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">How We Use Your Information</h2><p>We use information to improve your experience on {name}, send newsletters, respond to inquiries, and analyze site traffic. We will never sell your personal information.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Cookies</h2><p>{name} uses cookies to enhance your browsing experience. You can control cookie preferences through your browser settings.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Third-Party Services</h2><p>We may use third-party services such as Google Analytics and advertising networks. These services may collect information according to their own privacy policies.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Data Security</h2><p>We implement appropriate security measures to protect your personal information. However, no method of transmission is 100% secure.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Your Rights</h2><p>You have the right to access, correct, or delete the personal information we hold about you. You may opt out of communications at any time.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Children&rsquo;s Privacy</h2><p>Our website is not directed at children under 13. We do not knowingly collect personal information from children.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Changes to This Policy</h2><p>We may update this Privacy Policy from time to time. Changes will be posted on this page.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t2-privacy {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
