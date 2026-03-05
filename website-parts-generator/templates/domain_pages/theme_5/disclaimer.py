"""Disclaimer page for Theme 7 — Midnight Luxe."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-disclaimer"


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    updated = datetime.utcnow().strftime("%B %d, %Y")
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
    email = f"contact@{d}"

    sections = [
        ("General Disclaimer",
         f"<p>The information provided on {name} is for general informational and entertainment "
         f"purposes only. While we strive to ensure all recipes and content are accurate, complete, "
         f"and up to date, we make no representations or warranties of any kind — express or "
         f"implied — about the completeness, accuracy, reliability, suitability, or availability "
         f"of the information, products, services, or related graphics contained on this website.</p>"
         f"<p>Any reliance you place on such information is therefore strictly at your own risk.</p>"),

        ("Not Professional Advice",
         f"<p>The content on {name} is not intended to be a substitute for professional advice. "
         f"Our recipes and articles do not constitute medical, nutritional, dietary, or health "
         f"advice. Always consult with a qualified healthcare provider, registered dietitian, or "
         f"other professional before making dietary changes, especially if you have medical "
         f"conditions, food allergies, or specific nutritional requirements.</p>"
         f"<p>Cooking techniques and food safety practices should be verified with authoritative "
         f"sources, particularly for methods involving raw ingredients, high temperatures, canning, "
         f"or preservation.</p>"),

        ("Nutritional Information",
         f"<p>Any nutritional information provided on {name} is estimated and offered as a "
         f"convenience only. Nutritional values may vary based on specific ingredients used, "
         f"portion sizes, brand differences, and preparation methods.</p>"
         f"<p>We do not guarantee the accuracy of nutritional calculations and recommend using a "
         f"professional nutritional analysis tool or consulting a registered dietitian for precise "
         f"dietary requirements. Nutritional information should not be relied upon for medical "
         f"dietary needs.</p>"),

        ("Allergen Warning",
         f"<p>Recipes on {name} may contain or come into contact with common allergens including, "
         f"but not limited to: wheat, gluten, dairy, eggs, soy, tree nuts, peanuts, fish, "
         f"shellfish, and sesame.</p>"
         f"<p>While we endeavour to identify key allergens in our recipes, we cannot guarantee "
         f"that any recipe is free from allergens. If you have food allergies or intolerances, "
         f"always carefully check ingredient labels and consult with your healthcare provider "
         f"before preparing or consuming any recipe from this site.</p>"),

        ("External Links",
         f"<p>{name} may contain links to external websites that are not operated or controlled "
         f"by us. We have no control over the content, privacy policies, or practices of any "
         f"third-party websites and assume no responsibility for them.</p>"
         f"<p>The inclusion of links does not imply endorsement, approval, or recommendation. We "
         f"encourage you to review the terms and privacy policies of any external site you visit. "
         f"You acknowledge and agree that {name} shall not be held liable for any damage or loss "
         f"caused by your use of external websites.</p>"),

        ("Affiliate Disclosure",
         f"<p>{name} may participate in affiliate marketing programmes. This means we may earn a "
         f"small commission when you purchase products through links on our website at no "
         f"additional cost to you.</p>"
         f"<p>Affiliate relationships do not influence our editorial content or recipe "
         f"recommendations. We only recommend products and services we genuinely believe will be "
         f"useful to our readers. All opinions expressed are our own.</p>"
         f"<p>For transparency, affiliate links are disclosed in accordance with applicable "
         f"advertising standards and regulations.</p>"),

        ("Limitation of Liability",
         f"<p>To the fullest extent permitted by applicable law, {name}, its owners, authors, "
         f"contributors, and affiliates shall not be held liable for any direct, indirect, "
         f"incidental, special, consequential, or punitive damages arising from:</p>"
         f"<ul>"
         f"<li>Your use of or inability to use the website or its content</li>"
         f"<li>Any errors, inaccuracies, or omissions in recipes or other content</li>"
         f"<li>Personal injury or property damage related to your use of our recipes</li>"
         f"<li>Unauthorised access to or alteration of your data transmissions</li>"
         f"<li>Any third-party content, products, or services linked from our website</li>"
         f"</ul>"
         f"<p>If you have questions or concerns about this disclaimer, please contact us at "
         f"<a href=\"mailto:{email}\">{email}</a>.</p>"),
    ]

    sects_html = "".join(
        f'<section class="t7-section"><h3>{h}</h3><div class="t7-rule"></div>'
        f'<div class="t7-body">{b}</div></section>'
        for h, b in sections
    )

    html_content = f"""
<div class="dp-t7-disclaimer">
  <div class="t7-hero"><div class="t7-hero-inner">
    <span class="t7-badge">Legal</span>
    <h1 class="t7-hero-title">Disclaimer</h1>
    <p class="t7-hero-sub">Last updated: {updated}</p>
  </div></div>
  <div class="t7-wrap">{sects_html}</div>
</div>
"""

    css_content = f"""
{t['font_import']}
{ROOT} {{ {t['css_vars']} }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{hero_css(ROOT, ff)}
{body_css(ROOT, ff)}
"""
    return {"html": html_content, "css": css_content}
