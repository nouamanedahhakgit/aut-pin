"""Theme 10 — GDPR Policy: Bento Fresh."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t10-gdpr">
  <section class="dp-t10-hero">
    <p class="dp-t10-hero-badge">&#127482;&#127466; Legal</p>
    <h1>GDPR <em>Policy</em></h1>
    <p>How {name} complies with the General Data Protection Regulation.</p>
  </section>
  <div class="dp-t10-body">
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Data Controller</h2><p>{name} acts as the data controller for the personal information collected through this website. We are committed to ensuring that your privacy is protected in accordance with GDPR requirements.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Legal Basis for Processing</h2><p>We process personal data based on: (a) your consent, (b) performance of a contract, (c) legitimate interests, and (d) compliance with legal obligations.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Your GDPR Rights</h2>
      <ul>
        <li><strong>Right of Access</strong> &mdash; You can request a copy of your personal data.</li>
        <li><strong>Right to Rectification</strong> &mdash; You can ask us to correct inaccurate data.</li>
        <li><strong>Right to Erasure</strong> &mdash; You can request deletion of your personal data.</li>
        <li><strong>Right to Restrict Processing</strong> &mdash; You can limit how we use your data.</li>
        <li><strong>Right to Data Portability</strong> &mdash; You can receive your data in a portable format.</li>
        <li><strong>Right to Object</strong> &mdash; You can object to certain types of processing.</li>
      </ul>
    </section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Data Retention</h2><p>We retain personal data only for as long as necessary to fulfill the purposes for which it was collected. Newsletter subscriptions are retained until you unsubscribe.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">International Data Transfers</h2><p>Your data may be transferred to and processed in countries outside the European Economic Area. When this occurs, we ensure appropriate safeguards are in place as required by GDPR.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Data Protection Officer</h2><p>For any questions regarding our GDPR practices, contact us through our contact page. We will respond within 30 days as required by regulation.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Supervisory Authority</h2><p>If you believe that your data protection rights have been violated, you have the right to lodge a complaint with your local data protection supervisory authority.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t10-gdpr {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
