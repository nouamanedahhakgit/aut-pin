"""Sidebar for Theme 7 — Midnight Luxe.
Writer card, search, categories, popular recipes, newsletter — all with
luminous shadows, gold accents, and the Midnight Luxe aesthetic.
"""

import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module

ROOT = ".dp-t7-sidebar"


def generate(config: dict) -> dict:
    tb = theme_base(config)
    s = tb["s"]
    font_import = tb["font_import"]
    font_family = tb["font_family"]
    body_font = tb["body_font"]
    css_vars = tb["css_vars"]

    domain_name = html_module.escape(config.get("domain_name", "My Blog"))
    base_url = html_module.escape(config.get("base_url") or config.get("domain_url", "/"))
    categories = config.get("categories") or []
    articles = config.get("articles") or []
    writer = config.get("writer") or {}

    # ── Writer card ──────────────────────────────────────────────────
    writer_html = ""
    if writer and writer.get("name"):
        w_name = html_module.escape(writer.get("name", ""))
        w_title = html_module.escape(writer.get("title", ""))
        w_bio = html_module.escape(writer.get("bio", ""))
        w_avatar = (writer.get("avatar") or "").strip()

        if w_avatar and (w_avatar.startswith("http") or w_avatar.startswith("/")):
            av_html = f'<img class="t7-sb-avatar-img" src="{html_module.escape(w_avatar)}" alt="{w_name}" loading="lazy">'
        else:
            initials = (w_name[0] if w_name else "?").upper()
            av_html = f'<div class="t7-sb-avatar-init">{initials}</div>'

        writer_html = f"""
    <div class="t7-sb-card t7-sb-writer">
      <div class="t7-sb-avatar">{av_html}</div>
      <h4 class="t7-sb-writer-name">{w_name}</h4>
      {f'<span class="t7-sb-writer-title">{w_title}</span>' if w_title else ''}
      {f'<p class="t7-sb-writer-bio">{w_bio}</p>' if w_bio else ''}
      <div class="t7-sb-gold-dot"></div>
    </div>"""

    # ── Search widget ────────────────────────────────────────────────
    search_html = f"""
    <div class="t7-sb-card t7-sb-search">
      <h4 class="t7-sb-heading">Search</h4>
      <div class="t7-sb-search-box">
        <input class="t7-sb-search-input" type="text" placeholder="Search recipes\u2026" aria-label="Search recipes">
        <button class="t7-sb-search-btn" type="button" aria-label="Search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </button>
      </div>
    </div>"""

    # ── Categories widget ────────────────────────────────────────────
    cats_items = ""
    for cat in categories:
        c_name = html_module.escape(cat.get("name", ""))
        c_url = html_module.escape(cat.get("url", "#"))
        c_count = cat.get("count", "")
        count_span = f'<span class="t7-sb-cat-count">{html_module.escape(str(c_count))}</span>' if c_count else ""
        cats_items += f'<a class="t7-sb-cat-item" href="{c_url}"><span>{c_name}</span>{count_span}</a>\n'

    categories_html = f"""
    <div class="t7-sb-card t7-sb-cats">
      <h4 class="t7-sb-heading">Categories</h4>
      <div class="t7-sb-cat-list">
        {cats_items}
      </div>
    </div>"""

    # ── Popular recipes widget ───────────────────────────────────────
    pop_items = ""
    for art in articles[:5]:
        a_title = html_module.escape(art.get("title", "Untitled"))
        a_url = html_module.escape(art.get("url", "#"))
        a_img = (art.get("image") or art.get("thumbnail") or "").strip()
        if a_img:
            img_tag = f'<img class="t7-sb-pop-img" src="{html_module.escape(a_img)}" alt="{a_title}" loading="lazy">'
        else:
            img_tag = '<div class="t7-sb-pop-placeholder"></div>'
        pop_items += f"""
        <a class="t7-sb-pop-item" href="{a_url}">
          {img_tag}
          <span class="t7-sb-pop-title">{a_title}</span>
        </a>"""

    popular_html = ""
    if pop_items:
        popular_html = f"""
    <div class="t7-sb-card t7-sb-popular">
      <h4 class="t7-sb-heading">Popular Recipes</h4>
      <div class="t7-sb-pop-list">
        {pop_items}
      </div>
    </div>"""

    # ── Newsletter widget ────────────────────────────────────────────
    newsletter_html = f"""
    <div class="t7-sb-card t7-sb-newsletter">
      <h4 class="t7-sb-heading">Newsletter</h4>
      <p class="t7-sb-nl-desc">Get the latest recipes delivered straight to your inbox.</p>
      <div class="t7-sb-nl-form">
        <input class="t7-sb-nl-input" type="email" placeholder="Your email address" aria-label="Email for newsletter">
        <button class="t7-sb-nl-btn" type="button">Subscribe</button>
      </div>
    </div>"""

    html_content = f"""
<aside class="dp-t7-sidebar">
  {writer_html}
  {search_html}
  {categories_html}
  {popular_html}
  {newsletter_html}
</aside>
"""

    css_content = f"""
{font_import}
{ROOT} {{
    {css_vars}
    display: flex;
    flex-direction: column;
    gap: 24px;
}}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
/* ── Card base ────────────────────────────────────── */
{ROOT} .t7-sb-card {{
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 24px;
    box-shadow: var(--glow);
    transition: box-shadow .3s;
}}
{ROOT} .t7-sb-card:hover {{
    box-shadow: 0 6px 28px rgba(26,26,46,.11);
}}
{ROOT} .t7-sb-heading {{
    font-family: {font_family};
    font-size: .76rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text);
    margin: 0 0 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--gold);
    display: inline-block;
}}
/* ── Writer card ──────────────────────────────────── */
{ROOT} .t7-sb-writer {{
    text-align: center;
    padding: 32px 24px;
}}
{ROOT} .t7-sb-avatar {{
    margin-bottom: 16px;
}}
{ROOT} .t7-sb-avatar-img {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--gold);
}}
{ROOT} .t7-sb-avatar-init {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    font-family: {font_family};
    font-size: 1.6rem;
    font-weight: 800;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 3px solid var(--gold);
}}
{ROOT} .t7-sb-writer-name {{
    font-family: {font_family};
    font-size: 1.1rem;
    font-weight: 800;
    margin: 0 0 4px;
    color: var(--text);
}}
{ROOT} .t7-sb-writer-title {{
    font-size: .78rem;
    color: var(--gold);
    font-weight: 600;
    letter-spacing: .5px;
    text-transform: uppercase;
    display: block;
    margin-bottom: 10px;
}}
{ROOT} .t7-sb-writer-bio {{
    font-size: .86rem;
    color: var(--muted);
    line-height: 1.6;
    margin: 0;
}}
{ROOT} .t7-sb-gold-dot {{
    width: 6px;
    height: 6px;
    background: var(--gold);
    border-radius: 50%;
    margin: 16px auto 0;
}}
/* ── Search ───────────────────────────────────────── */
{ROOT} .t7-sb-search-box {{
    display: flex;
    gap: 0;
}}
{ROOT} .t7-sb-search-input {{
    flex: 1;
    border: 1px solid var(--border);
    border-right: none;
    border-radius: var(--radius) 0 0 var(--radius);
    padding: 10px 14px;
    font-size: .88rem;
    font-family: {body_font};
    color: var(--text);
    background: var(--bg);
    outline: none;
    transition: border-color .3s;
}}
{ROOT} .t7-sb-search-input:focus {{
    border-color: var(--gold);
}}
{ROOT} .t7-sb-search-btn {{
    border: none;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    padding: 10px 16px;
    border-radius: 0 var(--radius) var(--radius) 0;
    cursor: pointer;
    transition: opacity .3s;
    display: flex;
    align-items: center;
}}
{ROOT} .t7-sb-search-btn:hover {{ opacity: .85; }}
/* ── Categories ───────────────────────────────────── */
{ROOT} .t7-sb-cat-list {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}
{ROOT} .t7-sb-cat-item {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    border-radius: calc(var(--radius) * .6);
    text-decoration: none;
    color: var(--text);
    font-size: .88rem;
    transition: background .3s, color .3s;
}}
{ROOT} .t7-sb-cat-item:hover {{
    background: rgba(212,168,83,.08);
    color: var(--primary);
}}
{ROOT} .t7-sb-cat-count {{
    font-size: .72rem;
    font-weight: 700;
    background: var(--border);
    color: var(--muted);
    padding: 2px 10px;
    border-radius: 20px;
    min-width: 28px;
    text-align: center;
}}
/* ── Popular recipes ──────────────────────────────── */
{ROOT} .t7-sb-pop-list {{
    display: flex;
    flex-direction: column;
    gap: 14px;
}}
{ROOT} .t7-sb-pop-item {{
    display: flex;
    align-items: center;
    gap: 14px;
    text-decoration: none;
    color: var(--text);
    transition: color .3s;
}}
{ROOT} .t7-sb-pop-item:hover {{
    color: var(--primary);
}}
{ROOT} .t7-sb-pop-img {{
    width: 56px;
    height: 56px;
    border-radius: calc(var(--radius) * .6);
    object-fit: cover;
    flex-shrink: 0;
    border: 1px solid var(--border);
}}
{ROOT} .t7-sb-pop-placeholder {{
    width: 56px;
    height: 56px;
    border-radius: calc(var(--radius) * .6);
    background: linear-gradient(135deg, var(--border), var(--bg));
    flex-shrink: 0;
}}
{ROOT} .t7-sb-pop-title {{
    font-size: .86rem;
    font-weight: 600;
    line-height: 1.4;
}}
/* ── Newsletter ───────────────────────────────────── */
{ROOT} .t7-sb-newsletter {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    border: none;
}}
{ROOT} .t7-sb-newsletter .t7-sb-heading {{
    color: var(--gold);
    border-bottom-color: rgba(212,168,83,.4);
}}
{ROOT} .t7-sb-nl-desc {{
    font-size: .86rem;
    color: rgba(255,255,255,.7);
    margin: 0 0 14px;
    line-height: 1.5;
}}
{ROOT} .t7-sb-nl-form {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}
{ROOT} .t7-sb-nl-input {{
    border: 1px solid rgba(255,255,255,.2);
    border-radius: var(--radius);
    padding: 11px 14px;
    font-size: .86rem;
    font-family: {body_font};
    color: #fff;
    background: rgba(255,255,255,.08);
    outline: none;
    transition: border-color .3s;
}}
{ROOT} .t7-sb-nl-input::placeholder {{ color: rgba(255,255,255,.4); }}
{ROOT} .t7-sb-nl-input:focus {{ border-color: var(--gold); }}
{ROOT} .t7-sb-nl-btn {{
    background: var(--gold);
    color: var(--primary);
    border: none;
    border-radius: var(--radius);
    padding: 12px 20px;
    font-size: .8rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    cursor: pointer;
    transition: opacity .3s, transform .3s;
}}
{ROOT} .t7-sb-nl-btn:hover {{
    opacity: .9;
    transform: translateY(-1px);
}}
/* ── Responsive ───────────────────────────────────── */
@media (max-width: 768px) {{
    {ROOT} {{ gap: 20px; }}
    {ROOT} .t7-sb-card {{ padding: 24px 20px; }}
}}
@media (max-width: 600px) {{
    {ROOT} .t7-sb-card {{ padding: 20px 16px; }}
    {ROOT} .t7-sb-pop-img,
    {ROOT} .t7-sb-pop-placeholder {{ width: 48px; height: 48px; }}
}}
"""
    return {"html": html_content, "css": css_content}
