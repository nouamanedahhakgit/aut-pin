"""Theme 10 — Disclaimer: Bento Fresh."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t10-disclaimer">
  <section class="dp-t10-hero">
    <p class="dp-t10-hero-badge">&#128276; Legal</p>
    <h1><em>Disclaimer</em></h1>
    <p>Important information about the content on {name}.</p>
  </section>
  <div class="dp-t10-body">
    <section class="dp-t10-section"><h2 class="dp-t10-h2">General Information</h2><p>The information provided on {name} is for general informational and entertainment purposes only. While we strive to keep the content accurate and up-to-date, we make no representations or warranties of any kind about the completeness, accuracy, or reliability of the information.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Not Professional Advice</h2><p>The recipes and cooking tips on {name} are not substitutes for professional advice. Dietary needs vary by individual. If you have food allergies, dietary restrictions, or health concerns, please consult a qualified healthcare professional before following any recipe.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Nutritional Information</h2><p>Any nutritional information provided on this site is an estimate only and may vary based on ingredients, brands, and preparation methods. We do not guarantee the accuracy of nutritional data.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Allergen Warning</h2><p>Recipes on {name} may contain common allergens including nuts, dairy, eggs, gluten, soy, and shellfish. Always check ingredient labels and make substitutions as needed for your dietary requirements.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">External Links</h2><p>{name} may contain links to external websites. We are not responsible for the content, accuracy, or privacy practices of these third-party sites. Following external links is done at your own risk.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Affiliate Disclosure</h2><p>Some links on {name} may be affiliate links, meaning we may earn a small commission if you make a purchase through them. This does not affect the price you pay or our editorial integrity.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Limitation of Liability</h2><p>In no event shall {name} be liable for any direct, indirect, incidental, or consequential damages arising from the use of information on this site.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t10-disclaimer {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
