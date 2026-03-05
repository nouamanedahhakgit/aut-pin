"""Theme 3 — Contact Us: Glassmorphism dark mode, frosted glass form + info cards."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    s = t["s"]
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = html_module.escape((config.get("base_url") or "/").rstrip("/"))
    raw = str(config.get("domain_name", "site.com"))
    d = raw.replace("https://","").replace("http://","").replace("www.","").split("/")[0].lower()
    email = f"contact@{d}"
    recipes_email = f"recipes@{d}"
    business_email = f"business@{d}"

    html_content = f"""
<div class="domain-page dp-t3-contact">
  <section class="dp-t3-hero">
    <p class="dp-t3-hero-label">We&rsquo;d love to hear from you!</p>
    <h1>Get in Touch</h1>
    <p>Questions, feedback, recipe ideas, or partnership inquiries &mdash; we&rsquo;re all ears.</p>
  </section>
  <div class="dp-t3-body">
    <div class="dp-t3-contact-grid">
      <div class="dp-t3-contact-info">
        <div class="dp-t3-info-card">
          <div class="dp-t3-info-icon">&#9993;</div>
          <h3 class="dp-t3-info-title">Email Us</h3>
          <p class="dp-t3-info-text">General inquiries, press, and collaborations. Reach us at <strong>{email}</strong>.</p>
        </div>
        <div class="dp-t3-info-card">
          <div class="dp-t3-info-icon">&#128172;</div>
          <h3 class="dp-t3-info-title">Recipe Feedback</h3>
          <p class="dp-t3-info-text">Tried one of our recipes? Tell us at <strong>{recipes_email}</strong>.</p>
        </div>
        <div class="dp-t3-info-card">
          <div class="dp-t3-info-icon">&#129309;</div>
          <h3 class="dp-t3-info-title">Collaborate</h3>
          <p class="dp-t3-info-text">Partnerships, sponsorships, or guest posts. Contact <strong>{business_email}</strong>.</p>
        </div>
      </div>
      <form class="dp-t3-contact-form" onsubmit="return false;">
        <div class="dp-t3-form-group">
          <label class="dp-t3-label">Your Name</label>
          <input type="text" class="dp-t3-input" placeholder="Jane Smith">
        </div>
        <div class="dp-t3-form-group">
          <label class="dp-t3-label">Email Address</label>
          <input type="email" class="dp-t3-input" placeholder="jane@example.com">
        </div>
        <div class="dp-t3-form-group">
          <label class="dp-t3-label">Subject</label>
          <select class="dp-t3-input">
            <option value="">Choose a topic...</option>
            <option>Recipe Question</option>
            <option>Collaboration / Partnership</option>
            <option>Technical Issue</option>
            <option>General Feedback</option>
            <option>Other</option>
          </select>
        </div>
        <div class="dp-t3-form-group">
          <label class="dp-t3-label">Message</label>
          <textarea class="dp-t3-input dp-t3-textarea" rows="5" placeholder="Tell us what&rsquo;s on your mind..."></textarea>
        </div>
        <button type="submit" class="dp-t3-submit">Send Message</button>
      </form>
    </div>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t3-contact {{ {t['css_vars']} }}
{hero_css(ff)}
.dp-t3-contact .dp-t3-body {{ max-width: 1000px; }}

.dp-t3-contact-grid {{ display: grid; grid-template-columns: 1fr 1.4fr; gap: 2.5rem; }}

.dp-t3-contact-info {{ display: flex; flex-direction: column; gap: 1rem; }}
.dp-t3-info-card {{
    padding: 1.25rem; border-radius: var(--radius);
    background: var(--glass); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    transition: border-color 0.3s;
}}
.dp-t3-info-card:hover {{ border-color: var(--primary); }}
.dp-t3-info-icon {{ font-size: 1.5rem; margin-bottom: 0.4rem; }}
.dp-t3-info-title {{ font-family: {ff}; font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem; color: var(--text); }}
.dp-t3-info-text {{ color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}
.dp-t3-info-text strong {{ color: var(--secondary); }}

.dp-t3-contact-form {{
    padding: 2rem; border-radius: var(--radius);
    background: var(--glass); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
}}
.dp-t3-form-group {{ margin-bottom: 1rem; }}
.dp-t3-label {{ display: block; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.35rem; color: var(--text); }}
.dp-t3-input {{
    width: 100%; padding: 0.65rem 0.85rem; border: 1px solid var(--glass-border);
    border-radius: 10px; font-size: 0.9rem; font-family: inherit; outline: none;
    background: rgba(255,255,255,0.03); color: var(--text);
    transition: border-color 0.25s; box-sizing: border-box;
}}
.dp-t3-input:focus {{
    border-color: var(--primary);
    box-shadow: 0 0 8px color-mix(in srgb, var(--primary) 20%, transparent);
}}
.dp-t3-input::placeholder {{ color: var(--muted); }}
.dp-t3-textarea {{ resize: vertical; min-height: 100px; }}
.dp-t3-submit {{
    width: 100%; padding: 0.75rem; border: none; border-radius: 12px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; font-weight: 700; font-size: 0.95rem; cursor: pointer;
    font-family: inherit; transition: all 0.3s;
    box-shadow: 0 4px 16px color-mix(in srgb, var(--primary) 30%, transparent);
}}
.dp-t3-submit:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 24px color-mix(in srgb, var(--primary) 45%, transparent);
}}

@media (max-width: 768px) {{
    .dp-t3-contact-grid {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 600px) {{ .dp-t3-hero h1 {{ font-size: 1.8rem; }} }}
"""
    return {"html": html_content, "css": css}
