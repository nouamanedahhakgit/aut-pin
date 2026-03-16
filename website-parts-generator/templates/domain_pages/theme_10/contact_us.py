"""Theme 10 — Contact Us: Bento Fresh — clean white form, info bento cards, mint accents."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = html_module.escape((config.get("base_url") or "/").rstrip("/"))

    html_content = f"""
<div class="domain-page dp-t10-contact">
  <section class="dp-t10-hero">
    <p class="dp-t10-hero-badge">&#128172; Get in Touch</p>
    <h1>Contact <em>Us</em></h1>
    <p>We&rsquo;d love to hear from you! Reach out with questions, feedback, or recipe ideas.</p>
  </section>
  <div class="dp-t10-body">
    <div class="ct10-grid">
      <div class="ct10-info">
        <div class="ct10-info-card">
          <div class="ct10-info-icon" style="background:rgba(0,191,165,0.1);color:#00BFA5;">&#9993;</div>
          <h3 class="ct10-info-title">Email Us</h3>
          <p class="ct10-info-text">For collaborations, press inquiries, or general questions.</p>
        </div>
        <div class="ct10-info-card">
          <div class="ct10-info-icon" style="background:rgba(255,107,107,0.1);color:#FF6B6B;">&#127860;</div>
          <h3 class="ct10-info-title">Recipe Feedback</h3>
          <p class="ct10-info-text">Tried one of our recipes? Tell us how it went!</p>
        </div>
        <div class="ct10-info-card">
          <div class="ct10-info-icon" style="background:rgba(255,193,7,0.1);color:#FFC107;">&#129309;</div>
          <h3 class="ct10-info-title">Collaborate</h3>
          <p class="ct10-info-text">Interested in partnerships, sponsorships, or guest posts?</p>
        </div>
      </div>
      <form class="ct10-form" onsubmit="return false;">
        <h2 class="ct10-form-title">Send a Message</h2>
        <div class="ct10-row">
          <div class="ct10-fg">
            <label class="ct10-label">Name</label>
            <input type="text" class="ct10-input" placeholder="Jane Smith">
          </div>
          <div class="ct10-fg">
            <label class="ct10-label">Email</label>
            <input type="email" class="ct10-input" placeholder="jane@example.com">
          </div>
        </div>
        <div class="ct10-fg">
          <label class="ct10-label">Topic</label>
          <select class="ct10-input">
            <option value="">Choose a topic...</option>
            <option>Recipe Question</option>
            <option>Collaboration / Partnership</option>
            <option>Technical Issue</option>
            <option>General Feedback</option>
            <option>Other</option>
          </select>
        </div>
        <div class="ct10-fg">
          <label class="ct10-label">Message</label>
          <textarea class="ct10-input ct10-textarea" rows="5" placeholder="Tell us what&rsquo;s on your mind..."></textarea>
        </div>
        <button type="submit" class="ct10-submit">Send Message &rarr;</button>
      </form>
    </div>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t10-contact {{ {t['css_vars']} }}
{hero_css(ff)}
.dp-t10-contact .dp-t10-body {{ max-width: 1050px; }}

.ct10-grid {{ display: grid; grid-template-columns: 1fr 1.5fr; gap: 1.5rem; }}
.ct10-info {{ display: flex; flex-direction: column; gap: 0.9rem; }}
.ct10-info-card {{
    background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.25rem; display: flex; gap: 1rem; align-items: flex-start;
    box-shadow: var(--shadow-sm); transition: all 0.25s;
}}
.ct10-info-card:hover {{ box-shadow: var(--shadow); transform: translateY(-2px); }}
.ct10-info-icon {{
    width: 44px; height: 44px; border-radius: 12px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}}
.ct10-info-title {{ font-family: {ff}; font-size: 1rem; font-weight: 700; margin: 0 0 0.25rem; color: var(--text); }}
.ct10-info-text {{ color: var(--muted); font-size: 0.84rem; line-height: 1.5; margin: 0; }}

.ct10-form {{
    background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius-lg);
    padding: 2rem; box-shadow: var(--shadow-sm);
}}
.ct10-form-title {{ font-family: {ff}; font-size: 1.4rem; font-weight: 700; color: var(--text); margin: 0 0 1.5rem; }}
.ct10-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }}
.ct10-fg {{ margin-bottom: 0.85rem; }}
.ct10-label {{ display: block; font-weight: 600; font-size: 0.82rem; margin-bottom: 0.3rem; color: var(--text); text-transform: uppercase; letter-spacing: 0.05em; }}
.ct10-input {{
    width: 100%; padding: 0.7rem 0.9rem; border: 1.5px solid var(--border);
    border-radius: 10px; font-size: 0.9rem; font-family: inherit; outline: none;
    transition: border-color 0.2s; background: var(--bg); color: var(--text);
    box-sizing: border-box;
}}
.ct10-input:focus {{ border-color: var(--primary); }}
.ct10-textarea {{ resize: vertical; min-height: 100px; }}
.ct10-submit {{
    width: 100%; padding: 0.85rem; border: none; border-radius: 50px;
    background: var(--primary); color: #fff; font-weight: 700; font-size: 1rem;
    cursor: pointer; font-family: inherit; transition: all 0.25s;
    box-shadow: 0 2px 12px rgba(0,191,165,0.3);
}}
.ct10-submit:hover {{ background: #00997F; transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0,191,165,0.4); }}

@media (max-width: 768px) {{
    .ct10-grid {{ grid-template-columns: 1fr; }}
    .ct10-row {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 600px) {{ .dp-t10-hero h1 {{ font-size: 1.8rem; }} }}
"""
    return {"html": html_content, "css": css}
