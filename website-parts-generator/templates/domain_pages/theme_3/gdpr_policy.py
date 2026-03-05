"""Theme 3 — GDPR Policy: Glassmorphism dark mode, consistent with theme_3 design."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://","").replace("http://","").replace("www.","").split("/")[0].lower()
    email = f"contact@{d}"

    html_content = f"""
<div class="domain-page dp-t3-gdpr">
  <section class="dp-t3-hero">
    <p class="dp-t3-hero-label">Legal</p>
    <h1>GDPR Policy</h1>
    <p>How {name} complies with the General Data Protection Regulation.</p>
  </section>
  <div class="dp-t3-body">
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Data Controller</h2><p>{name} acts as the data controller for all personal data collected through this website. We are committed to processing your data lawfully, fairly, and in a transparent manner in accordance with the GDPR.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Legal Basis for Processing</h2><p>We process personal data based on the following legal grounds: your consent (e.g. newsletter subscriptions), the performance of a contract, compliance with legal obligations, and our legitimate interests in operating and improving this website.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Your GDPR Rights</h2><p>Under the GDPR, you have the following rights:</p><ul><li><strong>Right of Access:</strong> Request a copy of the personal data we hold about you.</li><li><strong>Right to Rectification:</strong> Request correction of inaccurate or incomplete data.</li><li><strong>Right to Erasure:</strong> Request deletion of your personal data (&ldquo;right to be forgotten&rdquo;).</li><li><strong>Right to Restrict Processing:</strong> Request limitation of how we use your data.</li><li><strong>Right to Data Portability:</strong> Receive your data in a structured, machine-readable format.</li><li><strong>Right to Object:</strong> Object to the processing of your data for certain purposes.</li><li><strong>Right to Withdraw Consent:</strong> Withdraw your consent at any time.</li></ul></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Data Retention</h2><p>We retain personal data only as long as necessary for the purposes for which it was collected, or as required by law. When data is no longer needed, it is securely deleted or anonymised.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">International Transfers</h2><p>Your data may be transferred to and processed in countries outside the European Economic Area (EEA). Where this occurs, we ensure appropriate safeguards are in place, such as Standard Contractual Clauses approved by the European Commission.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Contact &amp; Supervisory Authority</h2><p>To exercise any of your rights, or if you have questions about how we process your data, please contact us at {email}. You also have the right to lodge a complaint with your local data protection supervisory authority.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t3-gdpr {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
