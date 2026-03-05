"""Theme 2 — GDPR Policy: Modern clean style, accent bar headings."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    html_content = f"""
<div class="domain-page dp-t2-gdpr">
  <section class="dp-t2-hero">
    <p class="dp-t2-hero-label">Legal</p>
    <h1>GDPR Policy</h1>
    <p>How {name} complies with the General Data Protection Regulation.</p>
  </section>
  <div class="dp-t2-body">
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Data Controller</h2><p>{name} acts as the data controller for the personal information collected through this website. We are committed to ensuring your privacy is protected in accordance with GDPR.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Legal Basis for Processing</h2><p>We process personal data based on: consent, performance of a contract, legitimate interests, and compliance with legal obligations.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Your GDPR Rights</h2>
      <ul>
        <li><strong>Right of Access</strong> — Request a copy of your personal data.</li>
        <li><strong>Right to Rectification</strong> — Ask us to correct inaccurate data.</li>
        <li><strong>Right to Erasure</strong> — Request deletion of your data.</li>
        <li><strong>Right to Restrict Processing</strong> — Limit how we use your data.</li>
        <li><strong>Right to Data Portability</strong> — Receive your data in a portable format.</li>
        <li><strong>Right to Object</strong> — Object to certain types of processing.</li>
      </ul>
    </section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Data Retention</h2><p>We retain personal data only as long as necessary. Newsletter subscriptions are retained until you unsubscribe.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">International Data Transfers</h2><p>Your data may be processed outside the EEA. When this occurs, we ensure appropriate safeguards are in place.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Contact &amp; Supervisory Authority</h2><p>For questions regarding our GDPR practices, contact us via our contact page. You also have the right to lodge a complaint with your local data protection supervisory authority.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t2-gdpr {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
