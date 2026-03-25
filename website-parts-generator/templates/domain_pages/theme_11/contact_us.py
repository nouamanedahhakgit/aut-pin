"""Theme 11 — Contact Us: Art Deco — gold-framed form, deco info cards, symmetrical layout."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = html_module.escape((config.get("base_url") or "/").rstrip("/"))

    html_content = f"""
<div class="domain-page dp-t11-contact">
  <section class="dp-t11-hero">
    <p class="dp-t11-hero-label">&#9671; Contact &#9671;</p>
    <h1>Get in <em>Touch</em></h1>
    <p>We&rsquo;d love to hear from you. Questions, feedback, or collaboration ideas welcome.</p>
    <div class="dp-t11-ornament">&#9670;</div>
  </section>
  <div class="dp-t11-body">
    <div class="ct11-grid">
      <div class="ct11-info">
        <div class="ct11-info-card">
          <div class="ct11-info-icon">&#9993;</div>
          <h3 class="ct11-info-title">Email Us</h3>
          <p class="ct11-info-text">For collaborations, press inquiries, or general questions.</p>
        </div>
        <div class="ct11-info-card">
          <div class="ct11-info-icon">&#127860;</div>
          <h3 class="ct11-info-title">Recipe Feedback</h3>
          <p class="ct11-info-text">Tried one of our recipes? We&rsquo;d love to hear your thoughts.</p>
        </div>
        <div class="ct11-info-card">
          <div class="ct11-info-icon">&#129309;</div>
          <h3 class="ct11-info-title">Collaborate</h3>
          <p class="ct11-info-text">Interested in partnerships, sponsorships, or guest contributions?</p>
        </div>
      </div>
      <form class="ct11-form" onsubmit="return false;">
        <h2 class="ct11-form-title">Send a Message</h2>
        <div class="ct11-row">
          <div class="ct11-fg"><label class="ct11-label">Name</label><input type="text" class="ct11-input" placeholder="Jane Smith"></div>
          <div class="ct11-fg"><label class="ct11-label">Email</label><input type="email" class="ct11-input" placeholder="jane@example.com"></div>
        </div>
        <div class="ct11-fg"><label class="ct11-label">Topic</label>
          <select class="ct11-input"><option value="">Choose a topic...</option><option>Recipe Question</option><option>Collaboration</option><option>Technical Issue</option><option>General Feedback</option><option>Other</option></select>
        </div>
        <div class="ct11-fg"><label class="ct11-label">Message</label><textarea class="ct11-input ct11-textarea" rows="5" placeholder="Tell us what&rsquo;s on your mind..."></textarea></div>
        <button type="submit" class="ct11-submit">Send Message &#9670;</button>
      </form>
    </div>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t11-contact {{ {t['css_vars']} }}
{hero_css(ff)}
.dp-t11-contact .dp-t11-body {{ max-width: 1050px; }}

.ct11-grid {{ display: grid; grid-template-columns: 1fr 1.5fr; gap: 1.5rem; }}
.ct11-info {{ display: flex; flex-direction: column; gap: 0.9rem; }}
.ct11-info-card {{
    background: var(--bg); border: 1px solid var(--border); padding: 1.25rem;
    display: flex; gap: 1rem; align-items: flex-start; box-shadow: var(--shadow-sm);
    transition: all 0.25s; position: relative;
}}
.ct11-info-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }}
.ct11-info-card:hover {{ box-shadow: var(--shadow); transform: translateY(-2px); }}
.ct11-info-icon {{ width: 44px; height: 44px; background: var(--primary); color: var(--gold); flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }}
.ct11-info-title {{ font-family: {ff}; font-size: 0.95rem; font-weight: 700; margin: 0 0 0.25rem; text-transform: uppercase; letter-spacing: 0.06em; }}
.ct11-info-text {{ color: var(--muted); font-size: 0.84rem; line-height: 1.5; margin: 0; }}

.ct11-form {{ background: var(--bg); border: 1px solid var(--border); padding: 2rem; box-shadow: var(--shadow-sm); position: relative; }}
.ct11-form::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }}
.ct11-form-title {{ font-family: {ff}; font-size: 1.3rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 1.5rem; }}
.ct11-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }}
.ct11-fg {{ margin-bottom: 0.85rem; }}
.ct11-label {{ display: block; font-weight: 600; font-size: 0.78rem; margin-bottom: 0.3rem; text-transform: uppercase; letter-spacing: 0.08em; }}
.ct11-input {{ width: 100%; padding: 0.7rem 0.9rem; border: 1px solid var(--border); font-size: 0.9rem; font-family: inherit; outline: none; transition: border-color 0.25s; background: var(--bg); color: var(--text); box-sizing: border-box; }}
.ct11-input:focus {{ border-color: var(--gold); }}
.ct11-textarea {{ resize: vertical; min-height: 100px; }}
.ct11-submit {{
    width: 100%; padding: 0.85rem; border: 1px solid var(--gold); background: var(--primary); color: var(--gold);
    font-weight: 600; font-size: 0.9rem; cursor: pointer; font-family: inherit;
    text-transform: uppercase; letter-spacing: 0.1em; transition: all 0.3s;
}}
.ct11-submit:hover {{ background: var(--gold); color: var(--primary); }}

@media (max-width: 768px) {{ .ct11-grid {{ grid-template-columns: 1fr; }} .ct11-row {{ grid-template-columns: 1fr; }} }}
@media (max-width: 600px) {{ .dp-t11-hero h1 {{ font-size: 1.8rem; }} }}
"""
    return {"html": html_content, "css": css}
