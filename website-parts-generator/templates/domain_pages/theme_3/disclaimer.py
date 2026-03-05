"""Theme 3 — Disclaimer: Glassmorphism dark mode, consistent with theme_3 design."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    html_content = f"""
<div class="domain-page dp-t3-disclaimer">
  <section class="dp-t3-hero">
    <p class="dp-t3-hero-label">Legal</p>
    <h1>Disclaimer</h1>
    <p>Important information about the content on {name}.</p>
  </section>
  <div class="dp-t3-body">
    <section class="dp-t3-section"><h2 class="dp-t3-h2">General Disclaimer</h2><p>The information provided on {name} is for general informational and entertainment purposes only. While we strive to provide accurate and up-to-date content, we make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, or suitability of the information.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Not Professional Advice</h2><p>The recipes, cooking tips, and nutritional information on {name} should not be considered professional dietary, medical, or nutritional advice. Always consult with a qualified healthcare professional or registered dietitian before making significant changes to your diet, especially if you have specific health conditions or concerns.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Nutritional Information</h2><p>Any nutritional information provided alongside our recipes is estimated and may vary based on specific ingredients used, portion sizes, and preparation methods. These values are provided as a general guide only and should not be relied upon for precise dietary planning.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Allergen Warning</h2><p>Our recipes may contain or come into contact with common allergens including, but not limited to: nuts, dairy, eggs, wheat, soy, fish, and shellfish. Always check ingredient labels and take appropriate precautions if you have food allergies or intolerances.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">External Links</h2><p>{name} may contain links to external websites. We have no control over the content, privacy policies, or practices of any third-party sites and accept no responsibility for them. Following links to external sites is done at your own risk.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Affiliate Disclosure</h2><p>Some links on {name} may be affiliate links, meaning we may earn a small commission if you make a purchase through them. This does not affect the price you pay or our editorial integrity. We only recommend products we genuinely believe in.</p></section>
    <section class="dp-t3-section"><h2 class="dp-t3-h2">Limitation of Liability</h2><p>In no event shall {name}, its owners, or contributors be liable for any loss or damage, including personal injury or death, resulting from the use of information, recipes, or advice provided on this website. Use of this website and its content is entirely at your own risk.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t3-disclaimer {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
