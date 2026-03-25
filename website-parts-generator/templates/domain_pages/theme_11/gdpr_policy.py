"""Theme 11 — GDPR Policy: Art Deco Elegance."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t11-gdpr">
  <section class="dp-t11-hero">
    <p class="dp-t11-hero-label">&#9671; Legal &#9671;</p>
    <h1>GDPR <em>Policy</em></h1>
    <p>How {name} complies with the General Data Protection Regulation.</p>
    <div class="dp-t11-ornament">&#9670;</div>
  </section>
  <div class="dp-t11-body">
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Data Controller</h2><p>{name} is the data controller for the personal data collected through this website. We are committed to protecting and respecting your privacy.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Legal Basis for Processing</h2><p>We process your personal data based on your consent, the performance of a contract, or our legitimate interests in operating and improving our website.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Your Rights Under GDPR</h2><p>You have the right to access, rectify, erase, restrict processing, data portability, and object to the processing of your personal data. To exercise these rights, please contact us.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Data Retention</h2><p>We retain your personal data only for as long as necessary to fulfill the purposes for which it was collected, or as required by law.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">International Transfers</h2><p>Your data may be transferred to and processed in countries outside the European Economic Area (EEA). We ensure appropriate safeguards are in place for such transfers.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Contact Us</h2><p>If you have questions about this GDPR Policy, please reach out through our contact page.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t11-gdpr {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
