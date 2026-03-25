"""Theme 11 — Copyright Policy: Art Deco Elegance."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t11-copyright">
  <section class="dp-t11-hero">
    <p class="dp-t11-hero-label">&#9671; Legal &#9671;</p>
    <h1>Copyright <em>Policy</em></h1>
    <p>Understanding intellectual property rights on {name}.</p>
    <div class="dp-t11-ornament">&#9670;</div>
  </section>
  <div class="dp-t11-body">
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Ownership</h2><p>All content published on {name}, including but not limited to recipes, photographs, videos, text, graphics, and logos, is the intellectual property of {name} unless otherwise stated.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Permitted Use</h2><p>You may share links to our content freely. You may quote brief excerpts (up to 100 words) with proper attribution and a link back to the original page.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">Prohibited Use</h2><p>You may not reproduce, distribute, or republish our content without prior written permission. This includes scraping, copying entire articles, or using our photographs on other websites.</p></section>
    <section class="dp-t11-section"><h2 class="dp-t11-h2">DMCA</h2><p>If you believe any content on {name} infringes your copyright, please contact us with a detailed description and we will address the matter promptly.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t11-copyright {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
