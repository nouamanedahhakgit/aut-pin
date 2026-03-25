"""Theme 12 — Disclaimer: Candy Pop."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t12-disclaimer">
  <section class="dp-t12-hero">
    <div class="dp-t12-hero-blob1"></div>
    <div class="dp-t12-hero-blob2"></div>
    <span class="dp-t12-hero-badge">&#9888; Heads Up!</span>
    <h1><em>Disclaimer</em></h1>
    <p>Important info about the content on {name}.</p>
  </section>
  <div class="dp-t12-body">
    <section class="dp-t12-section"><h2 class="dp-t12-h2">General Information</h2><p>The info on {name} is for general informational and entertainment purposes only. It&rsquo;s not professional dietary, medical, or nutritional advice.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Recipe Accuracy</h2><p>While we try our best, cooking results may vary! Different ingredients, equipment, and techniques can affect outcomes. {name} isn&rsquo;t responsible for any mishaps.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Allergies &amp; Dietary Needs</h2><p>Our recipes may contain allergens. Always check ingredient lists carefully! Consult a healthcare professional for specific dietary needs.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">External Links</h2><p>{name} may contain links to external websites. We&rsquo;re not responsible for their content or privacy practices.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Affiliate Disclosure</h2><p>Some links on {name} may be affiliate links. We may earn a small commission at no extra cost to you if you purchase through our links. &#128147;</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t12-disclaimer {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
