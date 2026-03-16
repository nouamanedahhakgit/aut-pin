"""Theme 9 — Sidebar: Gold accent widgets, search, categories, popular recipes, newsletter."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []
    articles = config.get("articles", []) or []
    domain_name = html_module.escape(config.get("domain_name", "Recipe Blog"))

    writer = config.get("writer") or {}
    writer_html = ""
    if writer and writer.get("name"):
        w_name = html_module.escape(writer.get("name", ""))
        w_title = html_module.escape(writer.get("title", ""))
        w_bio = html_module.escape(writer.get("bio", ""))
        w_avatar = (writer.get("avatar") or "").strip()
        if w_avatar and (w_avatar.startswith("http") or w_avatar.startswith("/")):
            av_html = f'<img src="{html_module.escape(w_avatar)}" alt="{w_name}" class="sb-t9-writer-av">'
        else:
            initials = (w_name[0] if w_name else "?").upper()
            av_html = f'<div class="sb-t9-writer-init">{initials}</div>'
        writer_html = f"""
    <div class="sb-t9-widget sb-t9-writer-card">
      {av_html}
      <strong class="sb-t9-writer-name">{w_name}</strong>
      <span class="sb-t9-writer-title">{w_title}</span>
      <p class="sb-t9-writer-bio">{w_bio}</p>
    </div>"""

    cat_html = ""
    for c in categories[:8]:
        c_name = html_module.escape(c.get("name", ""))
        c_url = html_module.escape(c.get("url") or "#")
        count = c.get("count", "")
        count_span = f'<span class="sb-t9-cat-count">{count}</span>' if count else ""
        if c_name:
            cat_html += f'<a href="{c_url}" class="sb-t9-cat-link"><span>{c_name}</span>{count_span}</a>'

    popular_html = ""
    for i, art in enumerate(articles[:5]):
        title = html_module.escape((art.get("title") or "Untitled")[:80])
        url = html_module.escape(art.get("url") or "#")
        img = (art.get("main_image") or art.get("image") or "").strip()
        if img and img.startswith("http"):
            img_tag = f'<img src="{html_module.escape(img)}" alt="" class="sb-t9-pop-img">'
        else:
            img_tag = f'<div class="sb-t9-pop-num">{i+1}</div>'
        popular_html += f'<a href="{url}" class="sb-t9-pop-item">{img_tag}<span class="sb-t9-pop-title">{title}</span></a>'

    html_content = f"""
<aside class="sidebar dp-t9-sidebar">
  {writer_html}
  <div class="sb-t9-widget">
    <h3 class="sb-t9-title">Search</h3>
    <form class="sb-t9-search" action="{html_module.escape(base_url)}/search" method="get">
      <input type="text" name="q" placeholder="Search recipes..." class="sb-t9-input">
      <button type="submit" class="sb-t9-search-btn" aria-label="Search">&#128269;</button>
    </form>
  </div>
  <div class="sb-t9-widget">
    <h3 class="sb-t9-title">Categories</h3>
    <div class="sb-t9-cats">{cat_html or '<span class="sb-t9-empty">No categories</span>'}</div>
  </div>
  <div class="sb-t9-widget">
    <h3 class="sb-t9-title">Popular Recipes</h3>
    <div class="sb-t9-pops">{popular_html or '<span class="sb-t9-empty">No articles yet</span>'}</div>
  </div>
  <div class="sb-t9-widget sb-t9-nl">
    <h3 class="sb-t9-title">Newsletter</h3>
    <p class="sb-t9-nl-text">Get fresh recipes delivered to your inbox every week!</p>
    <form class="sb-t9-nl-form" onsubmit="return false;">
      <input type="email" placeholder="Your email address" class="sb-t9-input">
      <button type="submit" class="sb-t9-nl-btn">Subscribe</button>
    </form>
  </div>
</aside>
"""

    css = f"""
{t['font_import']}
.dp-t9-sidebar {{ {t['css_vars']} width: 100%; }}
.sb-t9-widget {{ margin-bottom: 2rem; }}
.sb-t9-title {{
    font-family: {ff}; font-size: 1.15rem; font-weight: 700; color: var(--text);
    padding-bottom: 0.6rem; border-bottom: 2px solid var(--border); margin-bottom: 1rem;
    position: relative;
}}
.sb-t9-title::after {{
    content: ''; position: absolute; bottom: -2px; left: 0;
    width: 36px; height: 2px; background: var(--primary);
}}
.sb-t9-search {{ display: flex; }}
.sb-t9-input {{
    flex: 1; padding: 0.6rem 0.85rem; border: 1px solid var(--border); border-right: none;
    border-radius: 9999px 0 0 9999px; font-size: 0.9rem; font-family: inherit; outline: none;
    background: var(--bg); color: var(--text); transition: border-color 0.2s;
}}
.sb-t9-input:focus {{ border-color: var(--primary); }}
.sb-t9-search-btn {{
    padding: 0 0.9rem; background: var(--primary);
    border: none; border-radius: 0 9999px 9999px 0; color: #fff; cursor: pointer; font-size: 0.9rem;
    transition: background 0.2s;
}}
.sb-t9-search-btn:hover {{ background: var(--accent); }}
.sb-t9-cats {{ display: flex; flex-direction: column; gap: 0.25rem; }}
.sb-t9-cat-link {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.5rem 0.65rem; border-radius: 8px;
    text-decoration: none; color: var(--text); font-size: 0.9rem; transition: all 0.2s;
}}
.sb-t9-cat-link:hover {{ background: var(--gold-light); color: var(--primary); }}
.sb-t9-cat-count {{ background: var(--border); font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 9999px; color: var(--muted); }}
.sb-t9-pops {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.sb-t9-pop-item {{ display: flex; gap: 0.75rem; align-items: center; text-decoration: none; color: var(--text); transition: color 0.2s; }}
.sb-t9-pop-item:hover {{ color: var(--primary); }}
.sb-t9-pop-img {{ width: 56px; height: 56px; border-radius: 10px; object-fit: cover; flex-shrink: 0; border: 1px solid var(--border); }}
.sb-t9-pop-num {{
    width: 36px; height: 36px; border-radius: 50%;
    background: var(--gold-light); color: var(--primary); border: 1.5px solid var(--primary);
    font-weight: 700; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.sb-t9-pop-title {{ font-size: 0.88rem; font-weight: 500; line-height: 1.4; }}
.sb-t9-nl {{ background: var(--sage-light); padding: 1.25rem; border-radius: var(--radius); border: 1px solid rgba(122,158,126,0.3); }}
.sb-t9-nl-text {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 0.75rem; font-style: italic; }}
.sb-t9-nl-form {{ display: flex; flex-direction: column; gap: 0.5rem; }}
.sb-t9-nl-form .sb-t9-input {{ border-right: 1px solid var(--border); border-radius: 9999px; }}
.sb-t9-nl-btn {{
    padding: 0.65rem; background: var(--secondary);
    color: #fff; border: none; border-radius: 9999px; font-weight: 600; font-size: 0.9rem; cursor: pointer;
    transition: background 0.2s;
}}
.sb-t9-nl-btn:hover {{ background: #5d8462; }}
.sb-t9-empty {{ color: var(--muted); font-size: 0.85rem; font-style: italic; }}
.sb-t9-writer-card {{ text-align: center; padding: 1.5rem; background: var(--gold-light); border-radius: var(--radius); border: 1px solid rgba(212,168,67,0.25); }}
.sb-t9-writer-av {{ width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 0.5rem; border: 2px solid rgba(212,168,67,0.4); }}
.sb-t9-writer-init {{
    width: 80px; height: 80px; border-radius: 50%;
    background: var(--primary); color: #fff;
    font-size: 2rem; font-weight: 700; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem;
}}
.sb-t9-writer-name {{ display: block; font-size: 1rem; font-weight: 700; color: var(--text); }}
.sb-t9-writer-title {{ display: block; font-size: 0.78rem; color: var(--primary); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }}
.sb-t9-writer-bio {{ font-size: 0.85rem; color: var(--muted); line-height: 1.5; }}
"""
    return {"html": html_content, "css": css}
