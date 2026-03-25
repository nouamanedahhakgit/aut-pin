"""Theme 12 — GDPR Policy: Candy Pop."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t12-gdpr">
  <section class="dp-t12-hero">
    <div class="dp-t12-hero-blob1"></div>
    <div class="dp-t12-hero-blob2"></div>
    <span class="dp-t12-hero-badge">&#128272; Data Protection</span>
    <h1>GDPR <em>Policy</em></h1>
    <p>How {name} complies with the General Data Protection Regulation.</p>
  </section>
  <div class="dp-t12-body">
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Data Controller</h2><p>{name} is the data controller for the personal data collected through this website. We are committed to protecting your privacy!</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Legal Basis</h2><p>We process your data based on your consent, contract performance, or our legitimate interests.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Your GDPR Rights</h2><p>You have the right to access, rectify, erase, restrict processing, data portability, and object to the processing of your data. Contact us to exercise these rights!</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Data Retention</h2><p>We retain your data only as long as necessary to fulfill the purposes for which it was collected.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">International Transfers</h2><p>Your data may be transferred outside the EEA. We ensure appropriate safeguards are in place.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Contact Us</h2><p>Questions about GDPR? Reach out through our contact page!</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t12-gdpr {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
