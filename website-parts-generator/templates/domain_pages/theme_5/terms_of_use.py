"""Terms of Use page for Theme 7 — Midnight Luxe."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-terms"


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    updated = datetime.utcnow().strftime("%B %d, %Y")
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
    email = f"contact@{d}"

    sections = [
        ("Acceptance of Terms",
         f"<p>By accessing and using {name}, you acknowledge that you have read, understood, and "
         f"agree to be bound by these Terms of Use. If you do not agree with any part of these "
         f"terms, please discontinue use of our website immediately.</p>"
         f"<p>These terms apply to all visitors, users, and contributors who access or use {name}. "
         f"Your continued use of the site following the posting of any changes constitutes acceptance "
         f"of those changes.</p>"),

        ("Use License",
         f"<p>Permission is granted to temporarily view and download materials on {name} for "
         f"personal, non-commercial use only. This is a grant of a licence, not a transfer of "
         f"title, and under this licence you may not:</p>"
         f"<ul>"
         f"<li>Modify or copy the materials beyond personal recipe use</li>"
         f"<li>Use the materials for any commercial purpose or public display</li>"
         f"<li>Remove any copyright or proprietary notations from the materials</li>"
         f"<li>Transfer the materials to another person or mirror them on another server</li>"
         f"</ul>"
         f"<p>This licence shall automatically terminate if you violate any of these restrictions.</p>"),

        ("User Content",
         f"<p>When you submit comments, recipe modifications, photographs, or other content to "
         f"{name}, you grant us a non-exclusive, royalty-free, perpetual, and worldwide licence to "
         f"use, reproduce, modify, and display such content in connection with our services.</p>"
         f"<p>You represent that you own or have the necessary rights to any content you submit, and "
         f"that your content does not infringe upon the rights of any third party.</p>"),

        ("Intellectual Property",
         f"<p>All content on {name} — including but not limited to recipes, photographs, graphics, "
         f"text, logos, and design elements — is the property of {name} or its content creators and "
         f"is protected by applicable intellectual property laws.</p>"
         f"<p>Unauthorised use of any materials may violate copyright, trademark, and other laws. "
         f"You may not reproduce, distribute, or create derivative works without express written "
         f"permission.</p>"),

        ("Disclaimer of Warranties",
         f"<p>The materials on {name} are provided on an &ldquo;as is&rdquo; basis. {name} makes no "
         f"warranties, expressed or implied, and hereby disclaims all warranties including, without "
         f"limitation, implied warranties of merchantability, fitness for a particular purpose, or "
         f"non-infringement of intellectual property.</p>"
         f"<p>We do not warrant that the website will be uninterrupted, error-free, or free of "
         f"viruses or other harmful components.</p>"),

        ("Limitation of Liability",
         f"<p>In no event shall {name}, its owners, contributors, or affiliates be liable for any "
         f"damages — including but not limited to direct, indirect, incidental, special, or "
         f"consequential damages — arising out of the use or inability to use the materials on this "
         f"website, even if {name} has been advised of the possibility of such damages.</p>"
         f"<p>Some jurisdictions do not allow limitations on implied warranties or liability for "
         f"incidental damages; these limitations may not apply to you.</p>"),

        ("Governing Law",
         f"<p>These terms and conditions are governed by and construed in accordance with applicable "
         f"laws, and you irrevocably submit to the exclusive jurisdiction of the courts in that "
         f"location. Any claim relating to {name} shall be governed without regard to conflict of "
         f"law provisions.</p>"),

        ("Changes to Terms",
         f"<p>{name} reserves the right to revise these Terms of Use at any time without notice. "
         f"By continuing to use this website, you agree to be bound by the current version of these "
         f"terms. We encourage you to review this page periodically for updates.</p>"
         f"<p>If you have questions regarding these terms, please contact us at "
         f"<a href=\"mailto:{email}\">{email}</a>.</p>"),
    ]

    sects_html = "".join(
        f'<section class="t7-section"><h3>{h}</h3><div class="t7-rule"></div>'
        f'<div class="t7-body">{b}</div></section>'
        for h, b in sections
    )

    html_content = f"""
<div class="dp-t7-terms">
  <div class="t7-hero"><div class="t7-hero-inner">
    <span class="t7-badge">Legal</span>
    <h1 class="t7-hero-title">Terms of Use</h1>
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
