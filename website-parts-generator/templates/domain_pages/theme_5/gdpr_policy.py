"""GDPR Policy page for Theme 7 — Midnight Luxe."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-gdpr"


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    updated = datetime.utcnow().strftime("%B %d, %Y")
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
    email = f"contact@{d}"

    sections = [
        ("Data Controller",
         f"<p>{name} acts as the data controller for personal data collected through this website. "
         f"As data controller, we determine the purposes and means of processing your personal "
         f"data in accordance with the General Data Protection Regulation (GDPR) and applicable "
         f"data protection legislation.</p>"
         f"<p>For any enquiries regarding data processing, you may contact our data protection "
         f"team at <a href=\"mailto:{email}\">{email}</a>.</p>"),

        ("Legal Basis for Processing",
         f"<p>{name} processes personal data under the following legal bases as defined by "
         f"Article 6 of the GDPR:</p>"
         f"<ul>"
         f"<li><strong>Consent:</strong> When you subscribe to our newsletter, submit comments, "
         f"or voluntarily provide personal information</li>"
         f"<li><strong>Legitimate Interest:</strong> For website analytics, security monitoring, "
         f"and service improvement where our interests do not override your fundamental rights</li>"
         f"<li><strong>Contractual Necessity:</strong> When processing is required to fulfil a "
         f"service you have requested</li>"
         f"<li><strong>Legal Obligation:</strong> When we are required by law to process or "
         f"retain certain information</li>"
         f"</ul>"),

        ("Your GDPR Rights",
         f"<p>Under the General Data Protection Regulation, you have the following rights "
         f"regarding your personal data:</p>"
         f"<ul>"
         f"<li><strong>Right of Access (Article 15):</strong> You have the right to request a "
         f"copy of the personal data we hold about you</li>"
         f"<li><strong>Right to Rectification (Article 16):</strong> You may request that we "
         f"correct any inaccurate or incomplete personal data</li>"
         f"<li><strong>Right to Erasure (Article 17):</strong> You may request deletion of your "
         f"personal data, also known as the &ldquo;right to be forgotten&rdquo;</li>"
         f"<li><strong>Right to Restrict Processing (Article 18):</strong> You may request that "
         f"we limit the processing of your personal data</li>"
         f"<li><strong>Right to Data Portability (Article 20):</strong> You may request your "
         f"data in a structured, commonly used, machine-readable format</li>"
         f"<li><strong>Right to Object (Article 21):</strong> You may object to processing of "
         f"your personal data based on legitimate interests or direct marketing</li>"
         f"<li><strong>Right to Withdraw Consent:</strong> Where processing is based on consent, "
         f"you may withdraw that consent at any time without affecting the lawfulness of prior "
         f"processing</li>"
         f"</ul>"
         f"<p>To exercise any of these rights, please contact us at "
         f"<a href=\"mailto:{email}\">{email}</a>. We will respond to your request within "
         f"30 days.</p>"),

        ("Data Retention",
         f"<p>We retain personal data only for as long as necessary to fulfil the purposes for "
         f"which it was collected, including satisfying any legal, accounting, or reporting "
         f"requirements.</p>"
         f"<p>Specifically:</p>"
         f"<ul>"
         f"<li>Newsletter subscriber data is retained until you unsubscribe</li>"
         f"<li>Comment data is retained for the lifetime of the associated content</li>"
         f"<li>Analytics data is retained in aggregated, anonymised form</li>"
         f"<li>Contact form submissions are retained for up to 12 months</li>"
         f"</ul>"),

        ("International Transfers",
         f"<p>Your personal data may be transferred to and processed in countries outside the "
         f"European Economic Area (EEA). When such transfers occur, we ensure appropriate "
         f"safeguards are in place, including:</p>"
         f"<ul>"
         f"<li>Standard Contractual Clauses approved by the European Commission</li>"
         f"<li>Transfers to countries with an adequacy decision from the European Commission</li>"
         f"<li>Binding Corporate Rules where applicable</li>"
         f"</ul>"),

        ("Contact DPO",
         f"<p>If you have any questions or concerns about how {name} processes your personal data, "
         f"or wish to exercise your rights under the GDPR, please contact our Data Protection "
         f"Officer:</p>"
         f"<p><strong>Email:</strong> <a href=\"mailto:{email}\">{email}</a><br>"
         f"Please include &ldquo;GDPR Request&rdquo; in your subject line to ensure your enquiry "
         f"is handled promptly. We aim to respond within 30 days of receiving your request.</p>"),

        ("Supervisory Authority",
         f"<p>If you are not satisfied with our response to your data protection concern, you have "
         f"the right to lodge a complaint with a supervisory authority. You may contact the "
         f"supervisory authority in your country of residence, place of work, or the place of the "
         f"alleged infringement.</p>"
         f"<p>We encourage you to reach out to us first at "
         f"<a href=\"mailto:{email}\">{email}</a> so that we can address your concerns directly.</p>"),
    ]

    sects_html = "".join(
        f'<section class="t7-section"><h3>{h}</h3><div class="t7-rule"></div>'
        f'<div class="t7-body">{b}</div></section>'
        for h, b in sections
    )

    html_content = f"""
<div class="dp-t7-gdpr">
  <div class="t7-hero"><div class="t7-hero-inner">
    <span class="t7-badge">GDPR</span>
    <h1 class="t7-hero-title">GDPR Policy</h1>
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
