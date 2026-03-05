"""Theme 2 — Terms of Use: Modern clean style, accent bar headings."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    html_content = f"""
<div class="domain-page dp-t2-terms">
  <section class="dp-t2-hero">
    <p class="dp-t2-hero-label">Legal</p>
    <h1>Terms of Use</h1>
    <p>Please read these terms carefully before using {name}.</p>
  </section>
  <div class="dp-t2-body">
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Acceptance of Terms</h2><p>By accessing and using {name}, you agree to be bound by these Terms of Use and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing this site.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Use License</h2><p>Permission is granted to temporarily view the materials on {name} for personal, non-commercial use only. This is the grant of a license, not a transfer of title. You may not modify or copy the materials, use them for commercial purposes, or attempt to reverse engineer any software on this site.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">User Content</h2><p>By submitting comments, recipes, or other content to {name}, you grant us a non-exclusive, royalty-free, worldwide license to use, reproduce, and display such content in connection with our services.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Intellectual Property</h2><p>All recipes, photographs, articles, and other content published on {name} are protected by copyright and intellectual property laws. Unauthorized reproduction or distribution is strictly prohibited.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Disclaimer</h2><p>The materials on {name} are provided on an &ldquo;as is&rdquo; basis. We make no warranties, expressed or implied, and hereby disclaim all warranties.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Limitations</h2><p>In no event shall {name} or its operators be liable for any damages arising out of the use or inability to use the materials on this site.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Governing Law</h2><p>These terms are governed by and construed in accordance with applicable laws, and you irrevocably submit to the exclusive jurisdiction of the courts in that location.</p></section>
    <section class="dp-t2-section"><h2 class="dp-t2-h2">Changes to Terms</h2><p>We reserve the right to revise these terms at any time without notice. By using this website, you agree to be bound by the current version of these Terms of Use.</p></section>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t2-terms {{ {t['css_vars']} }}
{hero_css(t['font_family'])}
{body_css(t['font_family'])}
"""
    return {"html": html_content, "css": css}
