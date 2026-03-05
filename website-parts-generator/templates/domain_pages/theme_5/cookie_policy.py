"""Cookie Policy page for Theme 7 — Midnight Luxe."""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module
from datetime import datetime

ROOT = ".dp-t7-cookie"


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    updated = datetime.utcnow().strftime("%B %d, %Y")
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
    email = f"contact@{d}"

    sections = [
        ("What Are Cookies",
         f"<p>Cookies are small text files placed on your device when you visit {name}. They are "
         f"widely used to make websites work more efficiently and to provide information to site "
         f"owners. Cookies help us remember your preferences, understand how you interact with our "
         f"content, and improve your overall experience.</p>"
         f"<p>Cookies do not typically contain personal information that directly identifies you, "
         f"but the data they store may be linked to information we hold about you.</p>"),

        ("How We Use Cookies",
         f"<p>{name} uses the following categories of cookies:</p>"
         f"<ul>"
         f"<li><strong>Essential Cookies:</strong> Required for the basic functionality of our "
         f"website. They enable core features such as page navigation, security, and access to "
         f"secure areas. The website cannot function properly without these cookies.</li>"
         f"<li><strong>Analytics Cookies:</strong> Help us understand how visitors interact with "
         f"{name} by collecting information about pages visited, time spent on the site, and any "
         f"errors encountered. This data is aggregated and anonymised.</li>"
         f"<li><strong>Functional Cookies:</strong> Allow the website to remember choices you "
         f"make — such as your preferred language, region, or font size — and provide enhanced, "
         f"personalised features.</li>"
         f"<li><strong>Advertising Cookies:</strong> Used to deliver advertisements relevant to "
         f"you and your interests. They may also be used to limit the number of times you see an "
         f"advertisement and to measure the effectiveness of advertising campaigns.</li>"
         f"</ul>"),

        ("Third-Party Cookies",
         f"<p>Some cookies on {name} are set by third-party services that appear on our pages. "
         f"These include:</p>"
         f"<ul>"
         f"<li><strong>Google Analytics:</strong> For traffic analysis and user behaviour insights</li>"
         f"<li><strong>Social media plugins:</strong> Facebook, Pinterest, Instagram, and other "
         f"platforms may set cookies when you interact with sharing buttons</li>"
         f"<li><strong>Advertising partners:</strong> Ad networks may use cookies to serve "
         f"targeted advertisements based on your browsing activity</li>"
         f"</ul>"
         f"<p>We do not control third-party cookies. Please refer to the respective third-party "
         f"privacy policies for more information.</p>"),

        ("Managing Cookies",
         f"<p>You have the right to decide whether to accept or reject cookies. You can manage "
         f"your cookie preferences in the following ways:</p>"
         f"<ul>"
         f"<li><strong>Browser Settings:</strong> Most web browsers allow you to control cookies "
         f"through their settings. You can set your browser to refuse cookies or to alert you when "
         f"cookies are being sent.</li>"
         f"<li><strong>Opt-Out Links:</strong> Some third-party services offer direct opt-out "
         f"mechanisms. For example, you may opt out of Google Analytics by installing the Google "
         f"Analytics Opt-out Browser Add-on.</li>"
         f"</ul>"
         f"<p>Please note that disabling cookies may affect the functionality of {name} and limit "
         f"your ability to use certain features.</p>"),

        ("Cookie Duration",
         f"<p>Cookies used on {name} have varying durations:</p>"
         f"<ul>"
         f"<li><strong>Session Cookies:</strong> Temporary cookies that are deleted when you close "
         f"your browser. They are used to maintain your session while browsing.</li>"
         f"<li><strong>Persistent Cookies:</strong> These remain on your device for a predetermined "
         f"period (ranging from 30 days to 2 years) or until you manually delete them. They help "
         f"us recognise returning visitors and remember preferences.</li>"
         f"</ul>"),

        ("Policy Updates",
         f"<p>{name} may update this Cookie Policy from time to time to reflect changes in "
         f"technology, legislation, or our data practices. Any changes will be posted on this "
         f"page with a revised &ldquo;last updated&rdquo; date.</p>"
         f"<p>We encourage you to review this policy periodically. If you have questions about "
         f"our use of cookies, please contact us at "
         f"<a href=\"mailto:{email}\">{email}</a>.</p>"),
    ]

    sects_html = "".join(
        f'<section class="t7-section"><h3>{h}</h3><div class="t7-rule"></div>'
        f'<div class="t7-body">{b}</div></section>'
        for h, b in sections
    )

    html_content = f"""
<div class="dp-t7-cookie">
  <div class="t7-hero"><div class="t7-hero-inner">
    <span class="t7-badge">Cookies</span>
    <h1 class="t7-hero-title">Cookie Policy</h1>
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
