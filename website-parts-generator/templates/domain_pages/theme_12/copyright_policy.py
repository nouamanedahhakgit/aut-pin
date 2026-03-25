"""Theme 12 — Copyright Policy: Candy Pop."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    html_content = f"""
<div class="domain-page dp-t12-copyright">
  <section class="dp-t12-hero">
    <div class="dp-t12-hero-blob1"></div>
    <div class="dp-t12-hero-blob2"></div>
    <span class="dp-t12-hero-badge">&#169; Copyright</span>
    <h1>Copyright <em>Policy</em></h1>
    <p>Understanding intellectual property rights on {name}.</p>
  </section>
  <div class="dp-t12-body">
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Ownership</h2><p>All content on {name} &mdash; recipes, photos, text, graphics, and logos &mdash; is our intellectual property unless stated otherwise.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Permitted Use</h2><p>You may share links to our content freely! Brief excerpts (up to 100 words) with attribution and a link back are also welcome.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">Prohibited Use</h2><p>Please don&rsquo;t reproduce, distribute, or republish our content without permission. This includes scraping, copying articles, or using our photos elsewhere.</p></section>
    <section class="dp-t12-section"><h2 class="dp-t12-h2">DMCA</h2><p>If you believe any content on {name} infringes your copyright, please contact us and we&rsquo;ll handle it promptly.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t12-copyright {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
