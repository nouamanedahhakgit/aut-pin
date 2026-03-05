"""Privacy Policy page for Theme 7 — Midnight Luxe."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-privacy"


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    updated = datetime.utcnow().strftime("%B %d, %Y")
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
    email = f"contact@{d}"

    sections = [
        ("Information We Collect",
         f"<p>{name} collects information to provide and improve our services. "
         f"The types of information we may collect include:</p>"
         f"<ul>"
         f"<li><strong>Personal Information:</strong> Name, email address, and other details "
         f"you voluntarily provide when subscribing to our newsletter, leaving comments, or "
         f"contacting us</li>"
         f"<li><strong>Usage Data:</strong> Pages visited, time spent on pages, links clicked, "
         f"referring URLs, and other browsing behaviour</li>"
         f"<li><strong>Device Information:</strong> Browser type, operating system, screen "
         f"resolution, and IP address</li>"
         f"</ul>"),

        ("How We Use Information",
         f"<p>We use the information we collect for the following purposes:</p>"
         f"<ul>"
         f"<li>To operate, maintain, and improve {name}</li>"
         f"<li>To personalise your experience and deliver relevant recipe content</li>"
         f"<li>To send newsletters and updates you have opted in to receive</li>"
         f"<li>To respond to your comments, questions, and requests</li>"
         f"<li>To analyse site usage and trends to enhance our services</li>"
         f"<li>To detect, prevent, and address technical issues</li>"
         f"</ul>"),

        ("Cookies &amp; Tracking",
         f"<p>{name} uses cookies and similar tracking technologies to enhance your browsing "
         f"experience. Cookies are small data files stored on your device that help us recognise "
         f"your preferences and understand how you use our site.</p>"
         f"<p>We use both session cookies (which expire when you close your browser) and persistent "
         f"cookies (which remain on your device for a set period). You can control cookie "
         f"preferences through your browser settings. Please see our Cookie Policy for full "
         f"details.</p>"),

        ("Third-Party Services",
         f"<p>We may use third-party services that collect, monitor, and analyse information to "
         f"improve our services. These may include:</p>"
         f"<ul>"
         f"<li><strong>Google Analytics:</strong> For website traffic analysis and reporting</li>"
         f"<li><strong>Email service providers:</strong> For newsletter delivery and management</li>"
         f"<li><strong>Advertising networks:</strong> For serving relevant advertisements</li>"
         f"<li><strong>Social media platforms:</strong> For sharing functionality and embedded "
         f"content</li>"
         f"</ul>"
         f"<p>These third parties have their own privacy policies that govern their use of "
         f"your information.</p>"),

        ("Data Security",
         f"<p>We implement reasonable security measures to protect your personal information from "
         f"unauthorised access, alteration, disclosure, or destruction. However, no method of "
         f"transmission over the Internet or electronic storage is 100% secure.</p>"
         f"<p>While we strive to use commercially acceptable means to protect your personal "
         f"information, we cannot guarantee its absolute security. You provide personal information "
         f"at your own risk.</p>"),

        ("Your Rights",
         f"<p>Depending on your location, you may have the following rights regarding your "
         f"personal data:</p>"
         f"<ul>"
         f"<li><strong>Access:</strong> Request a copy of the personal information we hold about you</li>"
         f"<li><strong>Correction:</strong> Request correction of inaccurate or incomplete data</li>"
         f"<li><strong>Deletion:</strong> Request deletion of your personal information</li>"
         f"<li><strong>Opt-out:</strong> Unsubscribe from marketing communications at any time</li>"
         f"<li><strong>Portability:</strong> Request a machine-readable copy of your data</li>"
         f"</ul>"
         f"<p>To exercise any of these rights, please contact us at "
         f"<a href=\"mailto:{email}\">{email}</a>.</p>"),

        ("Children&rsquo;s Privacy",
         f"<p>{name} does not knowingly collect personal information from children under the age "
         f"of 13 (or the applicable age of consent in your jurisdiction). If we become aware that "
         f"we have collected personal data from a child without appropriate parental consent, we "
         f"will take steps to delete that information promptly.</p>"
         f"<p>If you believe your child has provided us with personal information, please contact "
         f"us at <a href=\"mailto:{email}\">{email}</a>.</p>"),

        ("Policy Changes",
         f"<p>{name} reserves the right to update this Privacy Policy at any time. Changes will be "
         f"posted on this page with an updated revision date. We encourage you to review this "
         f"policy periodically.</p>"
         f"<p>Your continued use of {name} after any modifications indicates your acceptance of "
         f"the updated Privacy Policy. For questions, contact us at "
         f"<a href=\"mailto:{email}\">{email}</a>.</p>"),
    ]

    sects_html = "".join(
        f'<section class="t7-section"><h3>{h}</h3><div class="t7-rule"></div>'
        f'<div class="t7-body">{b}</div></section>'
        for h, b in sections
    )

    html_content = f"""
<div class="dp-t7-privacy">
  <div class="t7-hero"><div class="t7-hero-inner">
    <span class="t7-badge">Privacy</span>
    <h1 class="t7-hero-title">Privacy Policy</h1>
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
