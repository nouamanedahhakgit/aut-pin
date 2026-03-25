"""Theme 11 — Disclaimer: Art Deco Elegance."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t11-disclaimer">
  <section class="dp-t11-hero">
    <p class="dp-t11-hero-label">&#9671; Legal &#9671;</p>
    <h1><em>Disclaimer</em></h1>
    <p>Important information about the content on {name}.</p>
    <div class="dp-t11-ornament">&#9670;</div>
  </section>
  <div class="dp-t11-body">
    <section class="dp-t11-section"><h2 class="dp-t11-h2">General Information</h2><p>The information provided on {name} is for general informational and entertainment purposes only. It is not intended as professional dietary, medical, or nutritional advice.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Recipe Accuracy</h2><p>While we strive for accuracy, cooking results may vary depending on ingredients, equipment, altitude, and individual technique. {name} is not responsible for any adverse outcomes.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Allergies &amp; Dietary Needs</h2><p>Our recipes may contain allergens. Always check ingredient lists carefully if you have food allergies or dietary restrictions. Consult a healthcare professional for specific dietary needs.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">External Links</h2><p>{name} may contain links to external websites. We are not responsible for the content, accuracy, or privacy practices of those sites.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Affiliate Disclosure</h2><p>Some links on {name} may be affiliate links. This means we may earn a small commission at no extra cost to you if you make a purchase through our links.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t11-disclaimer {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
