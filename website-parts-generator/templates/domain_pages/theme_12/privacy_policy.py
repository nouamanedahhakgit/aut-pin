"""Theme 12 — Privacy Policy: Candy Pop — playful blobs, rainbow border, colorful dot headings."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t12-privacy">
  <section class="dp-t12-hero">
    <div class="dp-t12-hero-blob1"></div>
    <div class="dp-t12-hero-blob2"></div>
    <span class="dp-t12-hero-badge">&#128274; Legal Stuff</span>
    <h1>Privacy <em>Policy</em></h1>
    <p>Your privacy matters to us! Here&rsquo;s how {name} handles your info. &#128275;</p>
  </section>
  <div class="dp-t12-body">
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Information We Collect</h2><p>We may collect personal information such as your name and email address when you subscribe to our newsletter, leave a comment, or fill out a contact form. We also collect non-personal data such as browser type, device, and pages visited.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">How We Use Your Information</h2><p>We use the information to improve your experience on {name}, send newsletters (if subscribed), respond to inquiries, and analyze traffic. We never sell or rent your personal information!</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Cookies</h2><p>{name} uses cookies to enhance your browsing experience. You can control cookie preferences through your browser settings.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Third-Party Services</h2><p>We may use third-party services such as Google Analytics and social media plugins. These services may collect info according to their own privacy policies.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Data Security</h2><p>We implement appropriate security measures to protect your personal information. However, no method of transmission is 100% secure.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Your Rights</h2><p>You have the right to access, correct, or delete the personal information we hold about you. You may opt out of communications at any time.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Children&rsquo;s Privacy</h2><p>Our website is not directed at children under 13. We do not knowingly collect personal information from children.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Changes to This Policy</h2><p>We may update this Privacy Policy from time to time. Changes will be posted on this page.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t12-privacy {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
