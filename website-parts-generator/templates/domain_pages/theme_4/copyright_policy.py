"""Copyright Policy page for Theme 7 — Midnight Luxe."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-copyright"


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    updated = datetime.utcnow().strftime("%B %d, %Y")
    year = datetime.now().year
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
    email = f"contact@{d}"

    sections = [
        ("Copyright Notice",
         f"<p>&copy; {year} {name}. All rights reserved.</p>"
         f"<p>All content published on {name} — including but not limited to recipes, articles, "
         f"photographs, illustrations, graphics, videos, and design elements — is the intellectual "
         f"property of {name} and its respective content creators unless otherwise stated.</p>"
         f"<p>This material is protected by international copyright laws and treaties. "
         f"Unauthorised reproduction, distribution, or use of this content without express written "
         f"permission is strictly prohibited.</p>"),

        ("Permitted Use",
         f"<p>You may use content from {name} under the following conditions:</p>"
         f"<ul>"
         f"<li><strong>Personal Use:</strong> You may view, download, and print recipes for your "
         f"own personal, non-commercial use</li>"
         f"<li><strong>Attribution:</strong> If you reference our content, you must provide clear "
         f"attribution to {name} with a link back to the original page</li>"
         f"<li><strong>No Modification:</strong> You may not alter, transform, or build upon our "
         f"content without written permission</li>"
         f"<li><strong>No Republication:</strong> You may not republish full recipes, articles, "
         f"or substantial portions of our content on other websites, apps, or publications</li>"
         f"</ul>"),

        ("Recipe Sharing Policy",
         f"<p>We love when our recipes inspire your cooking! When sharing our recipes, please "
         f"follow these guidelines:</p>"
         f"<ul>"
         f"<li>Share a link to the recipe page rather than copying the full recipe text</li>"
         f"<li>If you adapt a recipe, credit {name} as the source of inspiration</li>"
         f"<li>You may share a brief summary (up to 2&ndash;3 sentences) with a link to the "
         f"full recipe</li>"
         f"<li>Do not reproduce complete ingredient lists and instructions without permission</li>"
         f"</ul>"
         f"<p>For recipe syndication or licensing enquiries, please contact "
         f"<a href=\"mailto:{email}\">{email}</a>.</p>"),

        ("Photography &amp; Media",
         f"<p>All photographs and media on {name} are original works or properly licensed content. "
         f"Unauthorised use is prohibited. Specifically:</p>"
         f"<ul>"
         f"<li>You may not download, copy, or redistribute our photographs without written "
         f"permission</li>"
         f"<li>You may not use our images for commercial purposes, including social media "
         f"marketing, product packaging, or advertising</li>"
         f"<li>You may not remove watermarks, credits, or metadata from our images</li>"
         f"<li>For media licensing or press enquiries, contact "
         f"<a href=\"mailto:{email}\">{email}</a></li>"
         f"</ul>"),

        ("DMCA / Takedown Requests",
         f"<p>If you believe that content on {name} infringes upon your copyright, you may submit "
         f"a takedown notice. Your notice must include:</p>"
         f"<ul>"
         f"<li>Identification of the copyrighted work you believe has been infringed</li>"
         f"<li>The URL or location of the allegedly infringing material on our website</li>"
         f"<li>Your contact information (name, address, telephone number, and email)</li>"
         f"<li>A statement that you have a good-faith belief that the use is not authorised</li>"
         f"<li>A statement, under penalty of perjury, that the information in your notice is "
         f"accurate and that you are the copyright owner or authorised to act on their behalf</li>"
         f"<li>Your physical or electronic signature</li>"
         f"</ul>"
         f"<p>Please send takedown notices to <a href=\"mailto:{email}\">{email}</a> with the "
         f"subject line &ldquo;DMCA Takedown Request.&rdquo;</p>"),

        ("User-Submitted Content",
         f"<p>When you submit content to {name} — including comments, recipe modifications, "
         f"photographs, or other materials — you grant us a non-exclusive, royalty-free, perpetual, "
         f"and worldwide licence to use, reproduce, modify, display, and distribute that content "
         f"in connection with our services.</p>"
         f"<p>You represent and warrant that you own or have the necessary rights to any content "
         f"you submit, and that your submission does not infringe upon the intellectual property "
         f"rights of any third party. {name} reserves the right to remove any user-submitted "
         f"content at our sole discretion.</p>"),
    ]

    sects_html = "".join(
        f'<section class="t7-section"><h3>{h}</h3><div class="t7-rule"></div>'
        f'<div class="t7-body">{b}</div></section>'
        for h, b in sections
    )

    html_content = f"""
<div class="dp-t7-copyright">
  <div class="t7-hero"><div class="t7-hero-inner">
    <span class="t7-badge">Legal</span>
    <h1 class="t7-hero-title">Copyright Policy</h1>
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
