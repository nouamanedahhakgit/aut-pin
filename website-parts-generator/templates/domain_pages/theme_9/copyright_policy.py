"""Theme 9 — Copyright Policy: Gold-tinted hero, editorial layout, Sunlit Elegance white theme."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    from datetime import datetime
    year = datetime.now().year

    html_content = f"""
<div class="domain-page dp-t9-copyright">
  <section class="dp-t9-hero">
    <p class="dp-t9-hero-label">Legal</p>
    <h1>Copyright Policy</h1>
    <p>Protecting the original content on {name}.</p>
  </section>
  <div class="dp-t9-body">
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Copyright Notice</h2><p>&copy; {year} {name}. All rights reserved. All content on this website, including but not limited to text, recipes, photographs, graphics, and code, is the property of {name} and is protected by international copyright laws.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Permitted Use</h2><p>You may view, download, and print content from {name} for personal, non-commercial use only. Any other use, including reproduction, modification, distribution, or republication, without our prior written permission, is strictly prohibited.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Recipe Sharing Guidelines</h2><p>We appreciate when you share our recipes! When sharing, please: (a) link back to the original recipe on {name}, (b) do not copy the full recipe text &mdash; use a brief summary with a link, (c) credit {name} as the source, and (d) do not use our photographs without explicit permission.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">Photography &amp; Images</h2><p>All photographs and images on {name} are original works or used under license. Downloading, copying, or redistributing our images without written consent is prohibited. For media inquiries or licensing requests, please contact us.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">DMCA / Takedown Requests</h2><p>If you believe that content on {name} infringes on your copyright, please contact us with: (a) a description of the copyrighted work, (b) the URL where the infringing material is located, (c) your contact information, and (d) a statement of good faith. We will respond promptly.</p></section>
    <section class="dp-t9-section"><h2 class="dp-t9-h2">User-Submitted Content</h2><p>By submitting content to {name} (comments, recipe tips, photos), you grant us a non-exclusive, royalty-free license to use, display, and distribute such content. You represent that you own or have the right to share the submitted content.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t9-copyright {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
