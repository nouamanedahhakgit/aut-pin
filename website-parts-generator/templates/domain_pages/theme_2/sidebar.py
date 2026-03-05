"""Theme 2 — Sidebar: Modern clean, accent-bar widget titles, rectangular links."""
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
            av_html = f'<img src="{html_module.escape(w_avatar)}" alt="{w_name}" class="sb-t2-writer-av">'
        else:
            initials = (w_name[0] if w_name else "?").upper()
            av_html = f'<div class="sb-t2-writer-init">{initials}</div>'
        writer_html = f"""
    <div class="sb-t2-widget sb-t2-writer-card">
      {av_html}
      <strong class="sb-t2-writer-name">{w_name}</strong>
      <span class="sb-t2-writer-title">{w_title}</span>
      <p class="sb-t2-writer-bio">{w_bio}</p>
    </div>"""

    cat_html = ""
    for c in categories[:8]:
        c_name = html_module.escape(c.get("name", ""))
        c_url = html_module.escape(c.get("url") or "#")
        count = c.get("count", "")
        count_span = f'<span class="sb-t2-cnt">{count}</span>' if count else ""
        if c_name:
            cat_html += f'<a href="{c_url}" class="sb-t2-cat"><span>{c_name}</span>{count_span}</a>'

    popular_html = ""
    for i, art in enumerate(articles[:5]):
        title = html_module.escape((art.get("title") or "Untitled")[:80])
        url = html_module.escape(art.get("url") or "#")
        img = (art.get("main_image") or art.get("image") or "").strip()
        if img and img.startswith("http"):
            img_tag = f'<img src="{html_module.escape(img)}" alt="" class="sb-t2-pop-img">'
        else:
            img_tag = f'<div class="sb-t2-pop-num">{i+1}</div>'
        popular_html += f'<a href="{url}" class="sb-t2-pop-item">{img_tag}<span class="sb-t2-pop-title">{title}</span></a>'

    html_content = f"""
<aside class="sidebar dp-t2-sidebar">
  {writer_html}
  <div class="sb-t2-widget">
    <h3 class="sb-t2-wt">Search</h3>
    <form class="sb-t2-search" action="{html_module.escape(base_url)}/search" method="get">
      <input type="text" name="q" placeholder="Search recipes..." class="sb-t2-input">
      <button type="submit" class="sb-t2-search-btn" aria-label="Search">&#128269;</button>
    </form>
  </div>
  <div class="sb-t2-widget">
    <h3 class="sb-t2-wt">Categories</h3>
    <div class="sb-t2-cats">{cat_html or '<span class="sb-t2-empty">No categories</span>'}</div>
  </div>
  <div class="sb-t2-widget">
    <h3 class="sb-t2-wt">Popular Recipes</h3>
    <div class="sb-t2-pops">{popular_html or '<span class="sb-t2-empty">No articles yet</span>'}</div>
  </div>
  <div class="sb-t2-widget sb-t2-nl">
    <h3 class="sb-t2-wt">Newsletter</h3>
    <p class="sb-t2-nl-text">Get the latest recipes in your inbox!</p>
    <form class="sb-t2-nl-form" onsubmit="return false;">
      <input type="email" placeholder="Your email" class="sb-t2-input sb-t2-nl-input">
      <button type="submit" class="sb-t2-nl-btn">Subscribe</button>
    </form>
  </div>
</aside>
"""

    css = f"""
{t['font_import']}
.dp-t2-sidebar {{ {t['css_vars']} width: 100%; }}
.sb-t2-widget {{ margin-bottom: 2rem; }}
.sb-t2-wt {{
    font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--text); margin-bottom: 1rem; padding-left: 12px; border-left: 3px solid var(--primary);
}}
.sb-t2-search {{ display: flex; }}
.sb-t2-input {{
    flex: 1; padding: 0.55rem 0.8rem; border: 1px solid var(--border); border-right: none;
    font-size: 0.9rem; font-family: inherit; outline: none; transition: border-color 0.2s;
}}
.sb-t2-input:focus {{ border-color: var(--primary); }}
.sb-t2-search-btn {{
    padding: 0 0.8rem; background: var(--primary); border: 1px solid var(--primary);
    color: #fff; cursor: pointer; font-size: 0.85rem;
}}
.sb-t2-cats {{ display: flex; flex-direction: column; gap: 0.2rem; }}
.sb-t2-cat {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.45rem 0.6rem; text-decoration: none; color: var(--text);
    font-size: 0.9rem; font-weight: 500; transition: all 0.2s;
}}
.sb-t2-cat:hover {{ background: color-mix(in srgb, var(--primary) 6%, transparent); color: var(--primary); }}
.sb-t2-cnt {{ background: var(--border); font-size: 0.7rem; padding: 0.1rem 0.45rem; color: var(--muted); }}
.sb-t2-pops {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.sb-t2-pop-item {{ display: flex; gap: 0.75rem; align-items: center; text-decoration: none; color: var(--text); transition: color 0.2s; }}
.sb-t2-pop-item:hover {{ color: var(--primary); }}
.sb-t2-pop-img {{ width: 52px; height: 52px; object-fit: cover; flex-shrink: 0; }}
.sb-t2-pop-num {{
    width: 32px; height: 32px; background: var(--primary); color: #fff;
    font-weight: 700; font-size: 0.8rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.sb-t2-pop-title {{ font-size: 0.9rem; font-weight: 500; line-height: 1.4; }}
.sb-t2-nl {{ background: color-mix(in srgb, var(--primary) 5%, var(--bg)); padding: 1.25rem; }}
.sb-t2-nl-text {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 0.75rem; }}
.sb-t2-nl-form {{ display: flex; flex-direction: column; gap: 0.5rem; }}
.sb-t2-nl-input {{ border-right: 1px solid var(--border) !important; }}
.sb-t2-nl-btn {{ padding: 0.55rem; background: var(--primary); color: #fff; border: none; font-weight: 600; font-size: 0.9rem; cursor: pointer; }}
.sb-t2-empty {{ color: var(--muted); font-size: 0.85rem; font-style: italic; }}
.sb-t2-writer-card {{ text-align: center; padding: 1.5rem; border: 1px solid var(--border); }}
.sb-t2-writer-av {{ width: 72px; height: 72px; object-fit: cover; margin-bottom: 0.5rem; }}
.sb-t2-writer-init {{
    width: 72px; height: 72px; background: var(--primary); color: #fff;
    font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem;
}}
.sb-t2-writer-name {{ display: block; font-size: 1rem; font-weight: 700; color: var(--text); }}
.sb-t2-writer-title {{ display: block; font-size: 0.75rem; color: var(--primary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
.sb-t2-writer-bio {{ font-size: 0.85rem; color: var(--muted); line-height: 1.5; }}
"""
    return {"html": html_content, "css": css}
