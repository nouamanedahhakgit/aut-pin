"""Theme 1 — Contact Us: Warm gradient hero, contact form, consistent with theme_1 design."""
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
<div class="domain-page dp-t1-contact">
  <section class="dp-t1-hero">
    <p class="dp-t1-hero-label">Get in Touch</p>
    <h1>Contact Us</h1>
    <p>We&rsquo;d love to hear from you! Reach out with questions, feedback, or recipe ideas.</p>
  </section>
  <div class="dp-t1-body">
    <div class="dp-t1-contact-grid">
      <div class="dp-t1-contact-info">
        <div class="dp-t1-info-card">
          <div class="dp-t1-info-icon">&#9993;</div>
          <h3 class="dp-t1-info-title">Email Us</h3>
          <p class="dp-t1-info-text">Drop us an email for collaborations, press inquiries, or general questions.</p>
        </div>
        <div class="dp-t1-info-card">
          <div class="dp-t1-info-icon">&#128172;</div>
          <h3 class="dp-t1-info-title">Recipe Feedback</h3>
          <p class="dp-t1-info-text">Tried one of our recipes? We&rsquo;d love to hear how it turned out!</p>
        </div>
        <div class="dp-t1-info-card">
          <div class="dp-t1-info-icon">&#129309;</div>
          <h3 class="dp-t1-info-title">Collaborate</h3>
          <p class="dp-t1-info-text">Interested in partnerships, sponsorships, or guest posts? Let&rsquo;s talk!</p>
        </div>
      </div>
      <form class="dp-t1-contact-form" onsubmit="return false;">
        <div class="dp-t1-form-group">
          <label class="dp-t1-label">Your Name</label>
          <input type="text" class="dp-t1-input" placeholder="Jane Smith">
        </div>
        <div class="dp-t1-form-group">
          <label class="dp-t1-label">Email Address</label>
          <input type="email" class="dp-t1-input" placeholder="jane@example.com">
        </div>
        <div class="dp-t1-form-group">
          <label class="dp-t1-label">Subject</label>
          <select class="dp-t1-input">
            <option value="">Choose a topic...</option>
            <option>Recipe Question</option>
            <option>Collaboration / Partnership</option>
            <option>Technical Issue</option>
            <option>General Feedback</option>
            <option>Other</option>
          </select>
        </div>
        <div class="dp-t1-form-group">
          <label class="dp-t1-label">Message</label>
          <textarea class="dp-t1-input dp-t1-textarea" rows="5" placeholder="Tell us what&rsquo;s on your mind..."></textarea>
        </div>
        <button type="submit" class="dp-t1-submit">Send Message</button>
      </form>
    </div>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t1-contact {{ {t['css_vars']} }}
{hero_css(ff)}
.dp-t1-contact .dp-t1-body {{ max-width: 1000px; }}

.dp-t1-contact-grid {{ display: grid; grid-template-columns: 1fr 1.4fr; gap: 2.5rem; }}

.dp-t1-contact-info {{ display: flex; flex-direction: column; gap: 1rem; }}
.dp-t1-info-card {{
    padding: 1.25rem; border-radius: 12px;
    background: color-mix(in srgb, var(--primary) 6%, var(--bg));
    border: 1px solid var(--border);
}}
.dp-t1-info-icon {{ font-size: 1.5rem; margin-bottom: 0.4rem; }}
.dp-t1-info-title {{ font-family: {ff}; font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem; }}
.dp-t1-info-text {{ color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}

.dp-t1-contact-form {{
    padding: 2rem; border: 1px solid var(--border); border-radius: 16px;
    background: var(--bg);
}}
.dp-t1-form-group {{ margin-bottom: 1rem; }}
.dp-t1-label {{ display: block; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.3rem; color: var(--text); }}
.dp-t1-input {{
    width: 100%; padding: 0.65rem 0.85rem; border: 1px solid var(--border);
    border-radius: 8px; font-size: 0.9rem; font-family: inherit; outline: none;
    transition: border-color 0.2s; background: var(--bg); color: var(--text);
    box-sizing: border-box;
}}
.dp-t1-input:focus {{ border-color: var(--primary); }}
.dp-t1-textarea {{ resize: vertical; min-height: 100px; }}
.dp-t1-submit {{
    width: 100%; padding: 0.75rem; border: none; border-radius: 9999px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; font-weight: 600; font-size: 1rem; cursor: pointer;
    font-family: inherit; transition: opacity 0.2s;
}}
.dp-t1-submit:hover {{ opacity: 0.85; }}

@media (max-width: 768px) {{
    .dp-t1-contact-grid {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 600px) {{ .dp-t1-hero h1 {{ font-size: 1.8rem; }} }}
"""
    return {"html": html_content, "css": css}
