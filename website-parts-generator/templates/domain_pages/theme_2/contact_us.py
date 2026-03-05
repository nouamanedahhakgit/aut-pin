"""Theme 2 — Contact Us: Modern clean style, structured form, accent bar headings."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    s = t["s"]
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = html_module.escape((config.get("base_url") or "/").rstrip("/"))

    html_content = f"""
<div class="domain-page dp-t2-contact">
  <section class="dp-t2-hero">
    <p class="dp-t2-hero-label">Get in Touch</p>
    <h1>Contact Us</h1>
    <p>We&rsquo;d love to hear from you. Questions, feedback, or recipe ideas — reach out!</p>
  </section>
  <div class="dp-t2-body">
    <div class="dp-t2-contact-layout">
      <form class="dp-t2-form" onsubmit="return false;">
        <div class="dp-t2-row">
          <div class="dp-t2-field">
            <label class="dp-t2-label">Name</label>
            <input type="text" class="dp-t2-input" placeholder="Your name">
          </div>
          <div class="dp-t2-field">
            <label class="dp-t2-label">Email</label>
            <input type="email" class="dp-t2-input" placeholder="your@email.com">
          </div>
        </div>
        <div class="dp-t2-field">
          <label class="dp-t2-label">Subject</label>
          <select class="dp-t2-input">
            <option value="">Select a topic...</option>
            <option>Recipe Question</option>
            <option>Collaboration</option>
            <option>Technical Issue</option>
            <option>General Feedback</option>
            <option>Other</option>
          </select>
        </div>
        <div class="dp-t2-field">
          <label class="dp-t2-label">Message</label>
          <textarea class="dp-t2-input dp-t2-textarea" rows="6" placeholder="What&rsquo;s on your mind?"></textarea>
        </div>
        <button type="submit" class="dp-t2-submit">Send Message</button>
      </form>
      <div class="dp-t2-contact-side">
        <div class="dp-t2-side-card">
          <h3 class="dp-t2-side-title">Quick Response</h3>
          <p class="dp-t2-side-text">We aim to respond to all inquiries within 24&ndash;48 hours.</p>
        </div>
        <div class="dp-t2-side-card">
          <h3 class="dp-t2-side-title">Collaborations</h3>
          <p class="dp-t2-side-text">Interested in partnerships or sponsored content? Let&rsquo;s discuss!</p>
        </div>
        <div class="dp-t2-side-card">
          <h3 class="dp-t2-side-title">Recipe Ideas</h3>
          <p class="dp-t2-side-text">Have a recipe you&rsquo;d like us to try? We love community suggestions.</p>
        </div>
      </div>
    </div>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t2-contact {{ {t['css_vars']} }}
{hero_css(ff)}
.dp-t2-contact .dp-t2-body {{ max-width: 1000px; }}

.dp-t2-contact-layout {{ display: grid; grid-template-columns: 1.5fr 1fr; gap: 2.5rem; }}

.dp-t2-form {{ }}
.dp-t2-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
.dp-t2-field {{ margin-bottom: 1rem; }}
.dp-t2-label {{ display: block; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.3rem; color: var(--text); }}
.dp-t2-input {{
    width: 100%; padding: 0.65rem 0.85rem; border: 1px solid var(--border);
    font-size: 0.9rem; font-family: inherit; outline: none;
    transition: border-color 0.2s; background: var(--bg); color: var(--text);
    box-sizing: border-box;
}}
.dp-t2-input:focus {{ border-color: var(--primary); }}
.dp-t2-textarea {{ resize: vertical; min-height: 120px; }}
.dp-t2-submit {{
    width: 100%; padding: 0.75rem; border: none;
    background: var(--primary); color: #fff;
    font-weight: 600; font-size: 1rem; cursor: pointer;
    font-family: inherit; transition: opacity 0.2s;
}}
.dp-t2-submit:hover {{ opacity: 0.85; }}

.dp-t2-contact-side {{ display: flex; flex-direction: column; gap: 1rem; }}
.dp-t2-side-card {{
    padding: 1.25rem; border-left: 4px solid var(--primary);
    background: color-mix(in srgb, var(--primary) 5%, var(--bg));
}}
.dp-t2-side-title {{ font-family: {ff}; font-size: 1rem; font-weight: 700; margin-bottom: 0.3rem; }}
.dp-t2-side-text {{ color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}

@media (max-width: 768px) {{
    .dp-t2-contact-layout {{ grid-template-columns: 1fr; }}
    .dp-t2-row {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 600px) {{ .dp-t2-hero h1 {{ font-size: 1.8rem; }} }}
"""
    return {"html": html_content, "css": css}
