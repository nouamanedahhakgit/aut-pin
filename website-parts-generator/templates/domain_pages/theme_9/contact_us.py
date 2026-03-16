"""Theme 9 — Contact Us: Gold-tinted hero, editorial contact form, Sunlit Elegance white theme."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = html_module.escape((config.get("base_url") or "/").rstrip("/"))

    html_content = f"""
<div class="domain-page dp-t9-contact">
  <section class="dp-t9-hero">
    <p class="dp-t9-hero-label">Get in Touch</p>
    <h1>Contact Us</h1>
    <p>We&rsquo;d love to hear from you! Reach out with questions, feedback, or recipe ideas.</p>
  </section>
  <div class="dp-t9-body">
    <div class="dp-t9-contact-grid">
      <div class="dp-t9-contact-info">
        <div class="dp-t9-info-card">
          <div class="dp-t9-info-icon">&#9993;</div>
          <h3 class="dp-t9-info-title">Email Us</h3>
          <p class="dp-t9-info-text">Drop us an email for collaborations, press inquiries, or general questions.</p>
        </div>
        <div class="dp-t9-info-card">
          <div class="dp-t9-info-icon">&#128172;</div>
          <h3 class="dp-t9-info-title">Recipe Feedback</h3>
          <p class="dp-t9-info-text">Tried one of our recipes? We&rsquo;d love to hear how it turned out!</p>
        </div>
        <div class="dp-t9-info-card">
          <div class="dp-t9-info-icon">&#129309;</div>
          <h3 class="dp-t9-info-title">Collaborate</h3>
          <p class="dp-t9-info-text">Interested in partnerships, sponsorships, or guest posts? Let&rsquo;s talk!</p>
        </div>
      </div>
      <form class="dp-t9-contact-form" onsubmit="return false;">
        <div class="dp-t9-form-group">
          <label class="dp-t9-label">Your Name</label>
          <input type="text" class="dp-t9-input" placeholder="Jane Smith">
        </div>
        <div class="dp-t9-form-group">
          <label class="dp-t9-label">Email Address</label>
          <input type="email" class="dp-t9-input" placeholder="jane@example.com">
        </div>
        <div class="dp-t9-form-group">
          <label class="dp-t9-label">Subject</label>
          <select class="dp-t9-input">
            <option value="">Choose a topic...</option>
            <option>Recipe Question</option>
            <option>Collaboration / Partnership</option>
            <option>Technical Issue</option>
            <option>General Feedback</option>
            <option>Other</option>
          </select>
        </div>
        <div class="dp-t9-form-group">
          <label class="dp-t9-label">Message</label>
          <textarea class="dp-t9-input dp-t9-textarea" rows="5" placeholder="Tell us what&rsquo;s on your mind..."></textarea>
        </div>
        <button type="submit" class="dp-t9-submit">Send Message</button>
      </form>
    </div>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t9-contact {{ {t['css_vars']} }}
{hero_css(ff)}
.dp-t9-contact .dp-t9-body {{ max-width: 1000px; }}

.dp-t9-contact-grid {{ display: grid; grid-template-columns: 1fr 1.4fr; gap: 2.5rem; }}

.dp-t9-contact-info {{ display: flex; flex-direction: column; gap: 1rem; }}
.dp-t9-info-card {{
    padding: 1.25rem; border-radius: 12px;
    background: var(--gold-light); border: 1px solid rgba(212,168,67,0.25);
}}
.dp-t9-info-icon {{ font-size: 1.5rem; margin-bottom: 0.4rem; }}
.dp-t9-info-title {{ font-family: {ff}; font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem; color: var(--text); }}
.dp-t9-info-text {{ color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}

.dp-t9-contact-form {{
    padding: 2rem; border: 1px solid var(--border); border-radius: 16px;
    background: var(--bg); box-shadow: 0 4px 24px rgba(44,36,22,0.06);
}}
.dp-t9-form-group {{ margin-bottom: 1rem; }}
.dp-t9-label {{ display: block; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.3rem; color: var(--text); }}
.dp-t9-input {{
    width: 100%; padding: 0.65rem 0.9rem; border: 1.5px solid var(--border);
    border-radius: 8px; font-size: 0.9rem; font-family: inherit; outline: none;
    transition: border-color 0.2s; background: var(--bg); color: var(--text);
    box-sizing: border-box;
}}
.dp-t9-input:focus {{ border-color: var(--primary); }}
.dp-t9-textarea {{ resize: vertical; min-height: 100px; }}
.dp-t9-submit {{
    width: 100%; padding: 0.8rem; border: none; border-radius: 9999px;
    background: var(--primary);
    color: #fff; font-weight: 600; font-size: 1rem; cursor: pointer;
    font-family: inherit; transition: all 0.25s;
}}
.dp-t9-submit:hover {{ background: var(--accent); transform: translateY(-2px); box-shadow: 0 5px 18px rgba(212,168,67,0.35); }}

@media (max-width: 768px) {{
    .dp-t9-contact-grid {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 600px) {{ .dp-t9-hero h1 {{ font-size: 1.8rem; }} }}
"""
    return {"html": html_content, "css": css}
