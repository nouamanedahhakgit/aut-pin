"""About Us page for Theme 8 — Aurora Borealis Dark.
Glowing obsidian hero + mission glass cards + highlighted principles list.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base, hero_css, body_css
import html as html_module

ROOT = ".dp-t8-about"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name        = html_module.escape(config.get("domain_name", "My Blog"))
    domain_description = html_module.escape(config.get("domain_description",
        "Where culinary art meets the brilliance of the aurora — bold flavors, vivid aesthetics."))

    html_content = f"""
<div class="dp-t8-about">
  <section class="t8-hero">
    <div class="t8-hero-mesh"></div>
    <div class="t8-hero-inner">
      <span class="t8-hero-label">Our Story</span>
      <h1 class="t8-hero-title">The Aurora Kitchen</h1>
      <p class="t8-hero-sub">Bold flavors and radiant creativity — discover the story behind {domain_name}.</p>
    </div>
  </section>

  <div class="t8-wrap">

    <div class="t8-section">
      <div class="t8-card">
        <h3>Our Vision</h3>
        <div class="t8-body">
          <p>{domain_description}</p>
          <p>At {domain_name}, we believe every dish carries its own light. We craft our recipes to illuminate the joy of cooking — turning everyday ingredients into something extraordinary and beautiful.</p>
        </div>
      </div>
    </div>

    <div class="t8-section">
      <h3>The Aurora Principles</h3>
      <div class="t8-body">
        <ul class="t8-about-list">
          <li><strong>Vivid Creativity:</strong> We infuse every recipe with bold imagination — no dull plates, no shortcuts.</li>
          <li><strong>Culinary Integrity:</strong> Honest ingredients, clear methods, and real-kitchen results you can trust.</li>
          <li><strong>Radiant Aesthetics:</strong> Presentation matters — every dish should be as beautiful as it is delicious.</li>
          <li><strong>Community Light:</strong> We grow as a constellation of passionate cooks who share their aurora moments.</li>
        </ul>
      </div>
    </div>

    <div class="t8-about-stats">
      <div class="t8-stat-card">
        <div class="t8-stat-glow t8-sg-v"></div>
        <span class="t8-stat-num">500+</span>
        <span class="t8-stat-label">Recipes</span>
      </div>
      <div class="t8-stat-card">
        <div class="t8-stat-glow t8-sg-c"></div>
        <span class="t8-stat-num">50K+</span>
        <span class="t8-stat-label">Monthly Readers</span>
      </div>
      <div class="t8-stat-card">
        <div class="t8-stat-glow t8-sg-g"></div>
        <span class="t8-stat-num">12+</span>
        <span class="t8-stat-label">Culinary Series</span>
      </div>
    </div>

  </div>
</div>
"""

    css_content = f"""
{font_import}
{ROOT} {{ {css_vars} background: var(--bg); }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{hero_css(ROOT, font_family)}
{body_css(ROOT, font_family)}

{ROOT} .t8-about-list {{ list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 18px; }}
{ROOT} .t8-about-list li {{
    display: flex;
    gap: 16px;
    padding: 20px 24px;
    background: var(--glass-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    position: relative;
    transition: border-color 0.3s;
}}
{ROOT} .t8-about-list li::before {{ display: none; }}
{ROOT} .t8-about-list li:hover {{ border-color: rgba(124,58,237,0.5); }}

{ROOT} .t8-about-stats {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin-top: 48px;
}}
{ROOT} .t8-stat-card {{
    position: relative;
    text-align: center;
    padding: 40px 20px;
    background: var(--glass-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: transform 0.35s ease, box-shadow 0.35s ease;
}}
{ROOT} .t8-stat-card:hover {{ transform: translateY(-6px); box-shadow: var(--shadow-lg); }}
{ROOT} .t8-stat-glow {{
    position: absolute;
    top: -30px; left: 50%; transform: translateX(-50%);
    width: 150px; height: 150px;
    border-radius: 50%;
    filter: blur(40px);
    animation: t8-glow-pulse 5s ease-in-out infinite;
}}
{ROOT} .t8-sg-v {{ background: rgba(124,58,237,0.3); }}
{ROOT} .t8-sg-c {{ background: rgba(6,182,212,0.3); animation-delay: 1.5s; }}
{ROOT} .t8-sg-g {{ background: rgba(16,185,129,0.3); animation-delay: 3s; }}
{ROOT} .t8-stat-num {{
    display: block;
    font-family: {font_family};
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fff, var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
    z-index: 1;
}}
{ROOT} .t8-stat-label {{
    display: block;
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--muted);
    position: relative;
    z-index: 1;
    margin-top: 8px;
}}
@keyframes t8-glow-pulse {{
    0%, 100% {{ opacity: 0.5; transform: translateX(-50%) scale(1); }}
    50%       {{ opacity: 1;   transform: translateX(-50%) scale(1.1); }}
}}
@media (max-width: 768px) {{
    {ROOT} .t8-about-stats {{ grid-template-columns: 1fr; }}
}}
"""
    return {"html": html_content, "css": css_content}
