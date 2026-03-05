"""Theme 2 — Copyright Policy: Modern clean style, accent bar headings."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    from datetime import datetime
    year = datetime.now().year

    html_content = f"""
<div class="domain-page dp-t2-copyright">
  <section class="dp-t2-hero">
    <p class="dp-t2-hero-label">Legal</p>
    <h1>Copyright Policy</h1>
    <p>Protecting the original content on {name}.</p>
  </section>
  <div class="dp-t2-body">
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Copyright Notice</h2><p>&copy; {year} {name}. All rights reserved. All content on this website is protected by international copyright laws.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Permitted Use</h2><p>You may view, download, and print content for personal, non-commercial use only. Any other use is strictly prohibited without prior written permission.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Recipe Sharing Guidelines</h2><p>When sharing our recipes: link back to the original, do not copy the full text, credit {name} as the source, and do not use our photographs without permission.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Photography &amp; Images</h2><p>All photographs and images are original works or used under license. Downloading, copying, or redistributing without written consent is prohibited.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">DMCA / Takedown Requests</h2><p>If you believe content on {name} infringes on your copyright, please contact us with a description of the work, the URL, your contact information, and a statement of good faith.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">User-Submitted Content</h2><p>By submitting content to {name}, you grant us a non-exclusive, royalty-free license to use, display, and distribute such content.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t2-copyright {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
