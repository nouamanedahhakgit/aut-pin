"""Theme 12 — Contact Us: Candy Pop — colorful info cards, playful form, rainbow accents."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]
    name = html_module.escape(config.get("domain_name", "Recipe Blog"))
    base_url = html_module.escape((config.get("base_url") or "/").rstrip("/"))

    html_content = f"""
<div class="domain-page dp-t12-contact">
  <section class="dp-t12-hero">
    <div class="dp-t12-hero-blob1"></div>
    <div class="dp-t12-hero-blob2"></div>
    <span class="dp-t12-hero-badge">&#128172; Let&rsquo;s Chat!</span>
    <h1>Contact <em>Us</em></h1>
    <p>We&rsquo;d love to hear from you! Drop us a message anytime. &#10024;</p>
  </section>
  <div class="dp-t12-body">
    <div class="ct12-grid">
      <div class="ct12-info">
        <div class="ct12-info-card" style="--info-color:var(--primary)">
          <div class="ct12-info-icon">&#9993;</div>
          <h3 class="ct12-info-title">Email Us</h3>
          <p class="ct12-info-text">For collabs, press inquiries, or just to say hi!</p>
        </div>
        <div class="ct12-info-card" style="--info-color:var(--secondary)">
          <div class="ct12-info-icon">&#127860;</div>
          <h3 class="ct12-info-title">Recipe Feedback</h3>
          <p class="ct12-info-text">Made something from our blog? Tell us how it turned out!</p>
        </div>
        <div class="ct12-info-card" style="--info-color:var(--accent)">
          <div class="ct12-info-icon">&#129309;</div>
          <h3 class="ct12-info-title">Collaborate</h3>
          <p class="ct12-info-text">Partnerships, sponsorships, or guest posts? Let&rsquo;s talk!</p>
        </div>
      </div>
      <form class="ct12-form" onsubmit="return false;">
        <h2 class="ct12-form-title">Send a Message &#128140;</h2>
        <div class="ct12-row">
          <div class="ct12-fg"><label class="ct12-label">Name</label><input type="text" class="ct12-input" placeholder="Jane Smith"></div>
          <div class="ct12-fg"><label class="ct12-label">Email</label><input type="email" class="ct12-input" placeholder="jane@example.com"></div>
        </div>
        <div class="ct12-fg"><label class="ct12-label">Topic</label>
          <select class="ct12-input"><option value="">Pick a topic...</option><option>Recipe Question</option><option>Collaboration</option><option>Technical Issue</option><option>General Feedback</option><option>Just Saying Hi! &#128075;</option></select>
        </div>
        <div class="ct12-fg"><label class="ct12-label">Message</label><textarea class="ct12-input ct12-textarea" rows="5" placeholder="Tell us what&rsquo;s on your mind..."></textarea></div>
        <button type="submit" class="ct12-submit">Send Message &#128147;</button>
      </form>
    </div>
  </div>
</div>
"""

    css = f"""
{t['font_import']}
.dp-t12-contact {{ {t['css_vars']} }}
{hero_css(ff)}
.dp-t12-contact .dp-t12-body {{ max-width: 1050px; }}
.ct12-grid {{ display: grid; grid-template-columns: 1fr 1.5fr; gap: 1.5rem; }}
.ct12-info {{ display: flex; flex-direction: column; gap: 0.9rem; }}
.ct12-info-card {{
    background: var(--bg); border: 2px solid var(--border); border-radius: var(--radius);
    padding: 1.25rem; display: flex; gap: 1rem; align-items: flex-start;
    box-shadow: var(--shadow-sm); transition: all 0.3s;
}}
.ct12-info-card:hover {{ border-color: var(--info-color); transform: translateY(-3px) scale(1.02); box-shadow: var(--shadow); }}
.ct12-info-icon {{
    width: 44px; height: 44px; border-radius: 14px; flex-shrink: 0;
    background: var(--info-color); color: #fff;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}}
.ct12-info-title {{ font-family: {ff}; font-size: 1rem; font-weight: 800; margin: 0 0 0.25rem; }}
.ct12-info-text {{ color: var(--muted); font-size: 0.84rem; line-height: 1.5; font-weight: 500; margin: 0; }}
.ct12-form {{
    background: var(--bg); border: 2px solid var(--border); border-radius: var(--radius-lg);
    padding: 2rem; box-shadow: var(--shadow-sm);
}}
.ct12-form-title {{ font-family: {ff}; font-size: 1.4rem; font-weight: 900; margin: 0 0 1.5rem; }}
.ct12-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }}
.ct12-fg {{ margin-bottom: 0.85rem; }}
.ct12-label {{ display: block; font-weight: 700; font-size: 0.82rem; margin-bottom: 0.3rem; color: var(--text); }}
.ct12-input {{
    width: 100%; padding: 0.7rem 0.9rem; border: 2px solid var(--border);
    border-radius: 14px; font-size: 0.9rem; font-family: inherit; outline: none;
    transition: border-color 0.25s; background: var(--bg); color: var(--text);
    box-sizing: border-box; font-weight: 500;
}}
.ct12-input:focus {{ border-color: var(--primary); }}
.ct12-textarea {{ resize: vertical; min-height: 100px; }}
.ct12-submit {{
    width: 100%; padding: 0.85rem; border: none; border-radius: 50px;
    background: var(--primary); color: #fff; font-weight: 800; font-size: 1rem;
    cursor: pointer; font-family: inherit; transition: all 0.3s;
    box-shadow: 0 4px 16px rgba(255,133,161,0.3);
}}
.ct12-submit:hover {{ transform: translateY(-3px) scale(1.03); box-shadow: 0 8px 24px rgba(255,133,161,0.45); }}
@media (max-width: 768px) {{ .ct12-grid {{ grid-template-columns: 1fr; }} .ct12-row {{ grid-template-columns: 1fr; }} }}
@media (max-width: 600px) {{ .dp-t12-hero h1 {{ font-size: 1.8rem; }} }}
"""
    return {"html": html_content, "css": css}
