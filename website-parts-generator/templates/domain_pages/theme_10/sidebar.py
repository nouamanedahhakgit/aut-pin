"""Theme 10 — Sidebar: Bento-style widgets, mint accents, clean white cards."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []
    articles = config.get("articles", []) or []

    writer = config.get("writer") or {}
    writer_html = ""
    if writer and writer.get("name"):
        w_name = html_module.escape(writer.get("name", ""))
        w_title = html_module.escape(writer.get("title", ""))
        w_bio = html_module.escape(writer.get("bio", ""))
        w_avatar = (writer.get("avatar") or "").strip()
        if w_avatar and (w_avatar.startswith("http") or w_avatar.startswith("/")):
            av_html = f'<img src="{html_module.escape(w_avatar)}" alt="{w_name}" class="sb-t10-av-img">'
        else:
            initials = (w_name[0] if w_name else "?").upper()
            av_html = f'<div class="sb-t10-av-ph">{initials}</div>'
        writer_html = f"""
    <div class="sb-t10-card sb-t10-writer">
      {av_html}
      <strong class="sb-t10-writer-name">{w_name}</strong>
      <span class="sb-t10-writer-title">{w_title}</span>
      <p class="sb-t10-writer-bio">{w_bio}</p>
    </div>"""

    cat_items = ""
    for i, c in enumerate(categories[:8]):
        c_name = html_module.escape(c.get("name", ""))
        c_url = html_module.escape(c.get("url") or "#")
        count = c.get("count", "")
        count_badge = f'<span class="sb-t10-count">{count}</span>' if count else ""
        if c_name:
            cat_items += f"""
        <a href="{c_url}" class="sb-t10-cat-item">
          <span class="sb-t10-cat-dot"></span>
          <span class="sb-t10-cat-name">{c_name}</span>
          {count_badge}
        </a>"""

    popular_items = ""
    for i, art in enumerate(articles[:5]):
        title = html_module.escape((art.get("title") or "Untitled")[:70])
        url = html_module.escape(art.get("url") or "#")
        img = (art.get("main_image") or art.get("image") or "").strip()
        if img and img.startswith("http"):
            img_el = f'<img src="{html_module.escape(img)}" alt="" class="sb-t10-pop-img">'
        else:
            img_el = f'<div class="sb-t10-pop-num">{i+1:02d}</div>'
        popular_items += f"""
        <a href="{url}" class="sb-t10-pop-item">
          {img_el}
          <span class="sb-t10-pop-title">{title}</span>
        </a>"""

    html_content = f"""
<aside class="sidebar dp-t10-sidebar">
  {writer_html}
  <div class="sb-t10-card">
    <h3 class="sb-t10-heading">&#128269; Search</h3>
    <form class="sb-t10-search" action="{html_module.escape(base_url)}/search" method="get">
      <input type="text" name="q" placeholder="Find a recipe..." class="sb-t10-input">
      <button type="submit" class="sb-t10-search-btn" aria-label="Search">&rarr;</button>
    </form>
  </div>
  <div class="sb-t10-card">
    <h3 class="sb-t10-heading">&#127860; Categories</h3>
    <div class="sb-t10-cats">{cat_items or '<span class="sb-t10-empty">No categories</span>'}</div>
  </div>
  <div class="sb-t10-card">
    <h3 class="sb-t10-heading">&#128293; Popular Recipes</h3>
    <div class="sb-t10-pops">{popular_items or '<span class="sb-t10-empty">No articles yet</span>'}</div>
  </div>
  <div class="sb-t10-card sb-t10-nl">
    <h3 class="sb-t10-heading">&#128140; Stay Updated</h3>
    <p class="sb-t10-nl-text">Fresh recipes every week. No spam, ever.</p>
    <form onsubmit="return false;">
      <input type="email" placeholder="your@email.com" class="sb-t10-input sb-t10-nl-input">
      <button type="submit" class="sb-t10-nl-btn">Subscribe &rarr;</button>
    </form>
  </div>
</aside>
"""

    css = f"""
{t['font_import']}
.dp-t10-sidebar {{ {t['css_vars']} width: 100%; display: flex; flex-direction: column; gap: 1.25rem; }}
.sb-t10-card {{
    background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.4rem; box-shadow: var(--shadow-sm);
}}
.sb-t10-heading {{
    font-family: {ff}; font-size: 0.95rem; font-weight: 700; color: var(--text);
    margin: 0 0 1rem; display: flex; align-items: center; gap: 6px;
}}
.sb-t10-search {{ display: flex; border: 1.5px solid var(--border); border-radius: 50px; overflow: hidden; transition: border-color 0.2s; }}
.sb-t10-search:focus-within {{ border-color: var(--primary); }}
.sb-t10-input {{
    flex: 1; padding: 0.6rem 0.9rem; border: none; outline: none;
    font-size: 0.88rem; font-family: inherit; background: transparent; color: var(--text);
}}
.sb-t10-search-btn {{
    padding: 0 1rem; background: var(--primary); border: none; color: #fff;
    font-size: 1rem; cursor: pointer; font-weight: 700; transition: background 0.2s;
}}
.sb-t10-search-btn:hover {{ background: #00997F; }}

.sb-t10-cats {{ display: flex; flex-direction: column; gap: 0.2rem; }}
.sb-t10-cat-item {{
    display: flex; align-items: center; gap: 8px; padding: 0.5rem 0.6rem;
    border-radius: 10px; text-decoration: none; color: var(--text); font-size: 0.88rem;
    transition: all 0.2s;
}}
.sb-t10-cat-item:hover {{ background: var(--mint-pale); color: var(--primary); }}
.sb-t10-cat-dot {{
    width: 7px; height: 7px; border-radius: 50%; background: var(--border); flex-shrink: 0;
    transition: background 0.2s;
}}
.sb-t10-cat-item:hover .sb-t10-cat-dot {{ background: var(--primary); }}
.sb-t10-cat-name {{ flex: 1; font-weight: 500; }}
.sb-t10-count {{
    font-size: 0.72rem; background: var(--border); padding: 2px 8px;
    border-radius: 50px; color: var(--muted);
}}

.sb-t10-pops {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.sb-t10-pop-item {{ display: flex; gap: 10px; align-items: center; text-decoration: none; color: var(--text); transition: color 0.2s; }}
.sb-t10-pop-item:hover {{ color: var(--primary); }}
.sb-t10-pop-img {{ width: 52px; height: 52px; border-radius: 10px; object-fit: cover; flex-shrink: 0; border: 1px solid var(--border); }}
.sb-t10-pop-num {{
    width: 40px; height: 40px; border-radius: 10px; background: var(--mint-pale);
    color: var(--primary); font-family: {ff}; font-size: 1rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.sb-t10-pop-title {{ font-size: 0.85rem; font-weight: 500; line-height: 1.4; }}

.sb-t10-nl {{ background: var(--surface2); border-color: var(--mint-border); }}
.sb-t10-nl-text {{ font-size: 0.85rem; color: var(--muted); margin: 0 0 0.75rem; }}
.sb-t10-nl-input {{ border: 1.5px solid var(--border); border-radius: 10px; width: 100%; margin-bottom: 0.6rem; box-sizing: border-box; padding: 0.65rem 0.9rem; }}
.sb-t10-nl-btn {{
    width: 100%; padding: 0.65rem; background: var(--primary); color: #fff;
    border: none; border-radius: 10px; font-weight: 700; font-size: 0.9rem;
    cursor: pointer; transition: all 0.2s;
}}
.sb-t10-nl-btn:hover {{ background: #00997F; transform: translateY(-1px); }}

.sb-t10-writer {{ text-align: center; background: var(--surface2); border-color: var(--mint-border); }}
.sb-t10-av-img {{ width: 76px; height: 76px; border-radius: 50%; object-fit: cover; margin-bottom: 0.6rem; border: 2px solid var(--mint-border); }}
.sb-t10-av-ph {{
    width: 76px; height: 76px; border-radius: 50%; background: var(--primary); color: #fff;
    font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.6rem;
}}
.sb-t10-writer-name {{ display: block; font-weight: 700; font-size: 1rem; color: var(--text); }}
.sb-t10-writer-title {{ display: block; font-size: 0.75rem; color: var(--primary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }}
.sb-t10-writer-bio {{ font-size: 0.83rem; color: var(--muted); line-height: 1.5; }}
.sb-t10-empty {{ color: var(--muted); font-size: 0.83rem; font-style: italic; }}
"""
    return {"html": html_content, "css": css}
