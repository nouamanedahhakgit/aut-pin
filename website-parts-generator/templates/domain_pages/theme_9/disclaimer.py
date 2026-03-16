"""Theme 9 — Disclaimer: Gold-tinted hero, editorial layout, Sunlit Elegance white theme."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    html_content = f"""
<div class="domain-page dp-t9-disclaimer">
  <section class="dp-t9-hero">
    <p class="dp-t9-hero-label">Legal</p>
    <h1>Disclaimer</h1>
    <p>Important information about the content on {name}.</p>
  </section>
  <div class="dp-t9-body">
    <section class="dp-t9-section"><h2 class="dp-t9-h2">General Information</h2><p>The information provided on {name} is for general informational and entertainment purposes only. While we strive to keep the content accurate and up-to-date, we make no representations or warranties of any kind about the completeness, accuracy, or reliability of the information.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Not Professional Advice</h2><p>The recipes and cooking tips on {name} are not substitutes for professional advice. Dietary needs vary by individual. If you have food allergies, dietary restrictions, or health concerns, please consult a qualified healthcare professional or registered dietitian before following any recipe.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Nutritional Information</h2><p>Any nutritional information provided on this site is an estimate only and may vary based on ingredients, brands, and preparation methods. We do not guarantee the accuracy of nutritional data and recommend that you verify nutritional information independently when needed.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Allergen Warning</h2><p>Recipes on {name} may contain common allergens including but not limited to nuts, dairy, eggs, gluten, soy, and shellfish. Always check ingredient labels and make substitutions as needed for your dietary requirements.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">External Links</h2><p>{name} may contain links to external websites. We are not responsible for the content, accuracy, or privacy practices of these third-party sites. Following external links is done at your own risk.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Affiliate Disclosure</h2><p>Some links on {name} may be affiliate links, meaning we may earn a small commission if you make a purchase through them. This does not affect the price you pay or our editorial integrity. We only recommend products we genuinely use and believe in.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Limitation of Liability</h2><p>In no event shall {name} be liable for any direct, indirect, incidental, or consequential damages arising from the use of information on this site. You use the recipes and information at your own risk.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t9-disclaimer {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
