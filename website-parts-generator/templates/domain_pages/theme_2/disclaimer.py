"""Theme 2 — Disclaimer: Modern clean style, accent bar headings."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    html_content = f"""
<div class="domain-page dp-t2-disclaimer">
  <section class="dp-t2-hero">
    <p class="dp-t2-hero-label">Legal</p>
    <h1>Disclaimer</h1>
    <p>Important information about the content on {name}.</p>
  </section>
  <div class="dp-t2-body">
    <section class="dp-t2-section"><h2 class="dp-t2-h2">General Information</h2><p>The information on {name} is for general informational purposes only. While we strive for accuracy, we make no representations about the completeness or reliability of the information.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Not Professional Advice</h2><p>Recipes and cooking tips are not substitutes for professional advice. If you have food allergies or health concerns, please consult a qualified professional.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Nutritional Information</h2><p>Any nutritional information provided is an estimate only and may vary. We recommend verifying nutritional data independently.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Allergen Warning</h2><p>Recipes may contain common allergens including nuts, dairy, eggs, gluten, soy, and shellfish. Always check ingredient labels.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">External Links</h2><p>{name} may contain links to external websites. We are not responsible for the content or privacy practices of third-party sites.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Affiliate Disclosure</h2><p>Some links may be affiliate links. This does not affect the price you pay or our editorial integrity. We only recommend products we genuinely use.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Limitation of Liability</h2><p>In no event shall {name} be liable for any damages arising from the use of information on this site. You use the recipes and information at your own risk.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t2-disclaimer {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
