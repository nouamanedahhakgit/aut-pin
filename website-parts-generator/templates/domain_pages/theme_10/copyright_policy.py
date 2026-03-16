"""Theme 10 — Copyright Policy: Bento Fresh."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    year = datetime.now().year
    html_content = f"""
<div class="domain-page dp-t10-copyright">
  <section class="dp-t10-hero">
    <p class="dp-t10-hero-badge">&#169; Legal</p>
    <h1>Copyright <em>Policy</em></h1>
    <p>Protecting the original content on {name}.</p>
  </section>
  <div class="dp-t10-body">
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Copyright Notice</h2><p>&copy; {year} {name}. All rights reserved. All content on this website, including text, recipes, photographs, graphics, and code, is the property of {name} and is protected by international copyright laws.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Permitted Use</h2><p>You may view, download, and print content from {name} for personal, non-commercial use only. Any other use without prior written permission is strictly prohibited.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Recipe Sharing Guidelines</h2><p>We appreciate when you share our recipes! Please: (a) link back to the original recipe on {name}, (b) do not copy the full recipe text &mdash; use a brief summary with a link, (c) credit {name} as the source, and (d) do not use our photographs without explicit permission.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">Photography &amp; Images</h2><p>All photographs and images on {name} are original works or used under license. Downloading, copying, or redistributing images without written consent is prohibited.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">DMCA / Takedown Requests</h2><p>If you believe that content on {name} infringes on your copyright, please contact us with a description of the work, the URL, your contact information, and a statement of good faith.</p></section>
    <section class="dp-t10-section"><h2 class="dp-t10-h2">User-Submitted Content</h2><p>By submitting content to {name}, you grant us a non-exclusive, royalty-free license to use, display, and distribute such content. You represent that you own or have the right to share it.</p></section>
  </div>
</div>"""
    css = f"""{t['font_import']}
.dp-t10-copyright {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}"""
    return {"html": html_content, "css": css}
