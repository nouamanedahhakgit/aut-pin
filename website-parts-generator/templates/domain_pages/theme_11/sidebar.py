"""Theme 11 — Sidebar: Art Deco — gold-bordered cards, diamond accents, elegant search."""
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
            av_html = f'<img src="{html_module.escape(w_avatar)}" alt="{w_name}" class="sb-t11-av-img">'
        else:
            initials = (w_name[0] if w_name else "?").upper()
            av_html = f'<div class="sb-t11-av-ph">{initials}</div>'
        writer_html = f"""
    <div class="sb-t11-card sb-t11-writer">
      {av_html}
      <strong class="sb-t11-writer-name">{w_name}</strong>
      <span class="sb-t11-writer-title">{w_title}</span>
      <p class="sb-t11-writer-bio">{w_bio}</p>
    </div>"""

    cat_items = ""
    for c in categories[:8]:
        c_name = html_module.escape(c.get("name", ""))
        c_url = html_module.escape(c.get("url") or "#")
        count = c.get("count", "")
        count_badge = f'<span class="sb-t11-count">{count}</span>' if count else ""
        if c_name:
            cat_items += f"""
        <a href="{c_url}" class="sb-t11-cat-item">
          <span class="sb-t11-cat-diamond">&#9670;</span>
          <span class="sb-t11-cat-name">{c_name}</span>
          {count_badge}
        </a>"""

    popular_items = ""
    for i, art in enumerate(articles[:5]):
        title = html_module.escape((art.get("title") or "Untitled")[:70])
        url = html_module.escape(art.get("url") or "#")
        img = (art.get("main_image") or art.get("image") or "").strip()
        if img and img.startswith("http"):
            img_el = f'<img src="{html_module.escape(img)}" alt="" class="sb-t11-pop-img">'
        else:
            img_el = f'<div class="sb-t11-pop-num">{i+1:02d}</div>'
        popular_items += f"""
        <a href="{url}" class="sb-t11-pop-item">
          {img_el}
          <span class="sb-t11-pop-title">{title}</span>
        </a>"""

    html_content = f"""
<aside class="sidebar dp-t11-sidebar">
  {writer_html}
  <div class="sb-t11-card">
    <h3 class="sb-t11-heading">Search</h3>
    <form class="sb-t11-search" action="{html_module.escape(base_url)}/search" method="get">
      <input type="text" name="q" placeholder="Find a recipe..." class="sb-t11-input">
      <button type="submit" class="sb-t11-search-btn" aria-label="Search">&rarr;</button>
    </form>
  </div>
  <div class="sb-t11-card">
    <h3 class="sb-t11-heading">Categories</h3>
    <div class="sb-t11-cats">{cat_items or '<span class="sb-t11-empty">No categories</span>'}</div>
  </div>
  <div class="sb-t11-card">
    <h3 class="sb-t11-heading">Popular Recipes</h3>
    <div class="sb-t11-pops">{popular_items or '<span class="sb-t11-empty">No articles yet</span>'}</div>
  </div>
  <div class="sb-t11-card sb-t11-nl">
    <h3 class="sb-t11-heading">Stay Updated</h3>
    <p class="sb-t11-nl-text">Elegant recipes delivered weekly.</p>
    <form onsubmit="return false;">
      <input type="email" placeholder="your@email.com" class="sb-t11-input sb-t11-nl-input">
      <button type="submit" class="sb-t11-nl-btn">Subscribe &#9670;</button>
    </form>
  </div>
</aside>
"""

    css = f"""
{t['font_import']}
.dp-t11-sidebar {{ {t['css_vars']} width: 100%; display: flex; flex-direction: column; gap: 1.25rem; }}
.sb-t11-card {{
    background: var(--bg); border: 1px solid var(--border); padding: 1.4rem;
    box-shadow: var(--shadow-sm); position: relative;
}}
.sb-t11-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}}
.sb-t11-heading {{
    font-family: {ff}; font-size: 0.8rem; font-weight: 700; color: var(--text);
    text-transform: uppercase; letter-spacing: 0.15em;
    margin: 0 0 1rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}}
.sb-t11-search {{ display: flex; border: 1px solid var(--border); overflow: hidden; transition: border-color 0.25s; }}
.sb-t11-search:focus-within {{ border-color: var(--gold); }}
.sb-t11-input {{
    flex: 1; padding: 0.6rem 0.9rem; border: none; outline: none;
    font-size: 0.88rem; font-family: inherit; background: transparent; color: var(--text);
}}
.sb-t11-search-btn {{
    padding: 0 1rem; background: var(--primary); border: none; color: var(--gold);
    font-size: 1rem; cursor: pointer; font-weight: 700; transition: background 0.25s;
}}
.sb-t11-search-btn:hover {{ background: var(--secondary, #2a2a2a); }}

.sb-t11-cats {{ display: flex; flex-direction: column; gap: 0.2rem; }}
.sb-t11-cat-item {{
    display: flex; align-items: center; gap: 8px; padding: 0.5rem 0.6rem;
    text-decoration: none; color: var(--text); font-size: 0.88rem; transition: all 0.25s;
}}
.sb-t11-cat-item:hover {{ color: var(--menu-link-hover); padding-left: 0.9rem; }}
.sb-t11-cat-diamond {{ color: var(--border); font-size: 0.35rem; transition: color 0.25s; }}
.sb-t11-cat-item:hover .sb-t11-cat-diamond {{ color: var(--menu-link-hover); }}
.sb-t11-cat-name {{ flex: 1; font-weight: 500; }}
.sb-t11-count {{ font-size: 0.72rem; background: var(--surface2); padding: 2px 8px; color: var(--muted); }}

.sb-t11-pops {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.sb-t11-pop-item {{ display: flex; gap: 10px; align-items: center; text-decoration: none; color: var(--text); transition: color 0.25s; }}
.sb-t11-pop-item:hover {{ color: var(--menu-link-hover); }}
.sb-t11-pop-img {{ width: 52px; height: 52px; object-fit: cover; flex-shrink: 0; border: 1px solid var(--border); }}
.sb-t11-pop-num {{
    width: 40px; height: 40px; background: var(--primary);
    color: var(--gold); font-family: {ff}; font-size: 1rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.sb-t11-pop-title {{ font-size: 0.85rem; font-weight: 500; line-height: 1.4; }}

.sb-t11-nl {{ background: var(--surface2); }}
.sb-t11-nl-text {{ font-size: 0.85rem; color: var(--muted); margin: 0 0 0.75rem; }}
.sb-t11-nl-input {{ border: 1px solid var(--border); width: 100%; margin-bottom: 0.6rem; box-sizing: border-box; padding: 0.65rem 0.9rem; }}
.sb-t11-nl-btn {{
    width: 100%; padding: 0.65rem; background: var(--primary); color: var(--gold);
    border: 1px solid var(--gold); font-weight: 600; font-size: 0.85rem;
    cursor: pointer; text-transform: uppercase; letter-spacing: 0.1em;
    transition: all 0.25s;
}}
.sb-t11-nl-btn:hover {{ background: var(--gold); color: var(--primary); }}

.sb-t11-writer {{ text-align: center; }}
.sb-t11-av-img {{ width: 76px; height: 76px; border-radius: 50%; object-fit: cover; margin-bottom: 0.6rem; border: 2px solid var(--gold); }}
.sb-t11-av-ph {{
    width: 76px; height: 76px; border-radius: 50%; background: var(--primary); color: var(--gold);
    font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; justify-content: center;
    margin: 0 auto 0.6rem; border: 2px solid var(--gold);
}}
.sb-t11-writer-name {{ display: block; font-weight: 700; font-size: 1rem; color: var(--text); }}
.sb-t11-writer-title {{ display: block; font-size: 0.72rem; color: var(--gold); font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }}
.sb-t11-writer-bio {{ font-size: 0.83rem; color: var(--muted); line-height: 1.5; }}
.sb-t11-empty {{ color: var(--muted); font-size: 0.83rem; font-style: italic; }}
"""
    return {"html": html_content, "css": css}
