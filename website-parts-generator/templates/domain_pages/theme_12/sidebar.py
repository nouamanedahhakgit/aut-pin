"""Theme 12 — Sidebar: Candy Pop — super-rounded pastel cards, bouncy icons, colorful accents."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from _shared import theme_base
import html as html_module


def generate(config: dict) -> dict:
    t = theme_base(config)
    ff = t["font_family"]

    base_url = (config.get("base_url") or config.get("domain_url") or "/").rstrip("/")
    categories = config.get("categories", []) or []
    articles = config.get("articles", []) or []

    COLORS = ["var(--primary)", "var(--secondary)", "var(--accent)", "var(--lavender)", "var(--yellow)"]

    writer = config.get("writer") or {}
    writer_html = ""
    if writer and writer.get("name"):
        w_name = html_module.escape(writer.get("name", ""))
        w_title = html_module.escape(writer.get("title", ""))
        w_bio = html_module.escape(writer.get("bio", ""))
        w_avatar = (writer.get("avatar") or "").strip()
        if w_avatar and (w_avatar.startswith("http") or w_avatar.startswith("/")):
            av_html = f'<img src="{html_module.escape(w_avatar)}" alt="{w_name}" class="sb-t12-av-img">'
        else:
            initials = (w_name[0] if w_name else "?").upper()
            av_html = f'<div class="sb-t12-av-ph">{initials}</div>'
        writer_html = f"""
    <div class="sb-t12-card sb-t12-writer">
      {av_html}
      <strong class="sb-t12-writer-name">{w_name}</strong>
      <span class="sb-t12-writer-title">{w_title}</span>
      <p class="sb-t12-writer-bio">{w_bio}</p>
    </div>"""

    cat_items = ""
    for i, c in enumerate(categories[:8]):
        c_name = html_module.escape(c.get("name", ""))
        c_url = html_module.escape(c.get("url") or "#")
        count = c.get("count", "")
        color = COLORS[i % len(COLORS)]
        count_badge = f'<span class="sb-t12-count">{count}</span>' if count else ""
        if c_name:
            cat_items += f"""
        <a href="{c_url}" class="sb-t12-cat-item">
          <span class="sb-t12-cat-dot" style="background:{color}"></span>
          <span class="sb-t12-cat-name">{c_name}</span>
          {count_badge}
        </a>"""

    popular_items = ""
    for i, art in enumerate(articles[:5]):
        title = html_module.escape((art.get("title") or "Untitled")[:70])
        url = html_module.escape(art.get("url") or "#")
        img = (art.get("main_image") or art.get("image") or "").strip()
        color = COLORS[i % len(COLORS)]
        if img and img.startswith("http"):
            img_el = f'<img src="{html_module.escape(img)}" alt="" class="sb-t12-pop-img">'
        else:
            img_el = f'<div class="sb-t12-pop-num" style="background:{color}">{i+1}</div>'
        popular_items += f"""
        <a href="{url}" class="sb-t12-pop-item">
          {img_el}
          <span class="sb-t12-pop-title">{title}</span>
        </a>"""

    html_content = f"""
<aside class="sidebar dp-t12-sidebar">
  {writer_html}
  <div class="sb-t12-card">
    <h3 class="sb-t12-heading">&#128269; Search</h3>
    <form class="sb-t12-search" action="{html_module.escape(base_url)}/search" method="get">
      <input type="text" name="q" placeholder="Find something yummy..." class="sb-t12-input">
      <button type="submit" class="sb-t12-search-btn" aria-label="Search">&#128270;</button>
    </form>
  </div>
  <div class="sb-t12-card">
    <h3 class="sb-t12-heading">&#127860; Categories</h3>
    <div class="sb-t12-cats">{cat_items or '<span class="sb-t12-empty">No categories</span>'}</div>
  </div>
  <div class="sb-t12-card">
    <h3 class="sb-t12-heading">&#11088; Popular Recipes</h3>
    <div class="sb-t12-pops">{popular_items or '<span class="sb-t12-empty">No articles yet</span>'}</div>
  </div>
  <div class="sb-t12-card sb-t12-nl">
    <h3 class="sb-t12-heading">&#128140; Stay Updated</h3>
    <p class="sb-t12-nl-text">Yummy recipes in your inbox every week! &#10024;</p>
    <form onsubmit="return false;">
      <input type="email" placeholder="your@email.com" class="sb-t12-input sb-t12-nl-input">
      <button type="submit" class="sb-t12-nl-btn">Subscribe &#128147;</button>
    </form>
  </div>
</aside>
"""

    css = f"""
{t['font_import']}
.dp-t12-sidebar {{ {t['css_vars']} width: 100%; display: flex; flex-direction: column; gap: 1.25rem; }}
.sb-t12-card {{
    background: var(--bg); border: 2px solid var(--border); border-radius: var(--radius);
    padding: 1.4rem; box-shadow: var(--shadow-sm); transition: transform 0.3s;
}}
.sb-t12-card:hover {{ transform: translateY(-2px); }}
.sb-t12-heading {{
    font-family: {ff}; font-size: 0.95rem; font-weight: 800; color: var(--text);
    margin: 0 0 1rem;
}}
.sb-t12-search {{ display: flex; border: 2px solid var(--border); border-radius: 50px; overflow: hidden; transition: border-color 0.25s; }}
.sb-t12-search:focus-within {{ border-color: var(--primary); }}
.sb-t12-input {{
    flex: 1; padding: 0.6rem 0.9rem; border: none; outline: none;
    font-size: 0.88rem; font-family: inherit; background: transparent; color: var(--text); font-weight: 500;
}}
.sb-t12-search-btn {{
    padding: 0 1rem; background: var(--primary); border: none; color: #fff;
    font-size: 1rem; cursor: pointer; border-radius: 0 50px 50px 0; transition: background 0.25s;
}}
.sb-t12-search-btn:hover {{ background: #FF6B8A; }}
.sb-t12-cats {{ display: flex; flex-direction: column; gap: 0.2rem; }}
.sb-t12-cat-item {{
    display: flex; align-items: center; gap: 8px; padding: 0.5rem 0.6rem;
    border-radius: 12px; text-decoration: none; color: var(--text); font-size: 0.88rem;
    font-weight: 600; transition: all 0.25s;
}}
.sb-t12-cat-item:hover {{ background: var(--pink-pale); transform: translateX(4px); }}
.sb-t12-cat-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
.sb-t12-cat-name {{ flex: 1; }}
.sb-t12-count {{ font-size: 0.72rem; background: var(--border); padding: 2px 8px; border-radius: 50px; color: var(--muted); font-weight: 700; }}
.sb-t12-pops {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.sb-t12-pop-item {{ display: flex; gap: 10px; align-items: center; text-decoration: none; color: var(--text); transition: all 0.25s; }}
.sb-t12-pop-item:hover {{ color: var(--primary); transform: translateX(4px); }}
.sb-t12-pop-img {{ width: 52px; height: 52px; border-radius: 14px; object-fit: cover; flex-shrink: 0; border: 2px solid var(--border); }}
.sb-t12-pop-num {{
    width: 40px; height: 40px; border-radius: 12px; color: #fff;
    font-family: {ff}; font-size: 1.1rem; font-weight: 900;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.sb-t12-pop-title {{ font-size: 0.85rem; font-weight: 600; line-height: 1.4; }}
.sb-t12-nl {{ background: var(--surface2); border-color: var(--pink-border); }}
.sb-t12-nl-text {{ font-size: 0.85rem; color: var(--muted); font-weight: 500; margin: 0 0 0.75rem; }}
.sb-t12-nl-input {{ border: 2px solid var(--border); border-radius: 14px; width: 100%; margin-bottom: 0.6rem; box-sizing: border-box; padding: 0.65rem 0.9rem; }}
.sb-t12-nl-btn {{
    width: 100%; padding: 0.65rem; background: var(--primary); color: #fff;
    border: none; border-radius: 14px; font-weight: 800; font-size: 0.9rem;
    cursor: pointer; transition: all 0.25s;
}}
.sb-t12-nl-btn:hover {{ background: #FF6B8A; transform: scale(1.03); }}
.sb-t12-writer {{ text-align: center; background: var(--surface2); border-color: var(--pink-border); }}
.sb-t12-av-img {{ width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 0.6rem; border: 3px solid var(--primary); }}
.sb-t12-av-ph {{
    width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; font-size: 1.8rem; font-weight: 900;
    display: flex; align-items: center; justify-content: center; margin: 0 auto 0.6rem;
}}
.sb-t12-writer-name {{ display: block; font-weight: 800; font-size: 1.05rem; }}
.sb-t12-writer-title {{ display: block; font-size: 0.75rem; color: var(--primary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }}
.sb-t12-writer-bio {{ font-size: 0.83rem; color: var(--muted); line-height: 1.5; font-weight: 500; }}
.sb-t12-empty {{ color: var(--muted); font-size: 0.83rem; font-style: italic; }}
"""
    return {"html": html_content, "css": css}
