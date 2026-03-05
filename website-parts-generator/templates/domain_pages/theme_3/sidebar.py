"""Theme 3 — Sidebar: Dark glassmorphism widgets — writer card, search, categories, popular, newsletter."""
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
            av_html = f'<img src="{html_module.escape(w_avatar)}" alt="{w_name}" class="sb-t3-writer-av">'
        else:
            initials = (w_name[0] if w_name else "?").upper()
            av_html = f'<div class="sb-t3-writer-init">{initials}</div>'
        writer_html = f"""
    <div class="sb-t3-widget sb-t3-writer-card">
      {av_html}
      <strong class="sb-t3-writer-name">{w_name}</strong>
      <span class="sb-t3-writer-title">{w_title}</span>
      <p class="sb-t3-writer-bio">{w_bio}</p>
    </div>"""

    cat_html = ""
    for c in categories[:8]:
        c_name = html_module.escape(c.get("name", ""))
        c_url = html_module.escape(c.get("url") or "#")
        count = c.get("count", "")
        count_span = f'<span class="sb-t3-cat-count">{count}</span>' if count else ""
        if c_name:
            cat_html += f'<a href="{c_url}" class="sb-t3-cat-link"><span>{c_name}</span>{count_span}</a>'

    popular_html = ""
    for i, art in enumerate(articles[:5]):
        title = html_module.escape((art.get("title") or "Untitled")[:80])
        url = html_module.escape(art.get("url") or "#")
        img = (art.get("main_image") or art.get("image") or "").strip()
        if img and img.startswith("http"):
            img_tag = f'<img src="{html_module.escape(img)}" alt="" class="sb-t3-pop-img">'
        else:
            img_tag = f'<div class="sb-t3-pop-num">{i+1}</div>'
        popular_html += f'<a href="{url}" class="sb-t3-pop-item">{img_tag}<span class="sb-t3-pop-title">{title}</span></a>'

    html_content = f"""
<aside class="sidebar dp-t3-sidebar">
  {writer_html}
  <div class="sb-t3-widget">
    <h3 class="sb-t3-title">Search</h3>
    <form class="sb-t3-search" action="{html_module.escape(base_url)}/search" method="get">
      <input type="text" name="q" placeholder="Search recipes..." class="sb-t3-input">
      <button type="submit" class="sb-t3-search-btn" aria-label="Search">&#128269;</button>
    </form>
  </div>
  <div class="sb-t3-widget">
    <h3 class="sb-t3-title">Categories</h3>
    <div class="sb-t3-cats">{cat_html or '<span class="sb-t3-empty">No categories</span>'}</div>
  </div>
  <div class="sb-t3-widget">
    <h3 class="sb-t3-title">Popular Recipes</h3>
    <div class="sb-t3-pops">{popular_html or '<span class="sb-t3-empty">No articles yet</span>'}</div>
  </div>
  <div class="sb-t3-widget sb-t3-nl">
    <h3 class="sb-t3-title">Newsletter</h3>
    <p class="sb-t3-nl-text">Get the latest recipes and tips delivered straight to your inbox.</p>
    <form class="sb-t3-nl-form" onsubmit="return false;">
      <input type="email" placeholder="Your email" class="sb-t3-input">
      <button type="submit" class="sb-t3-nl-btn">Subscribe</button>
    </form>
  </div>
</aside>
"""

    css = f"""
{t['font_import']}
.dp-t3-sidebar {{ {t['css_vars']} width: 100%; }}
.sb-t3-widget {{
    margin-bottom: 1.75rem; background: var(--glass); backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px); border: 1px solid var(--glass-border);
    border-radius: var(--radius); padding: 1.25rem;
}}
.sb-t3-title {{
    font-family: {ff}; font-size: 0.85rem; font-weight: 700; color: var(--text);
    text-transform: uppercase; letter-spacing: 0.08em;
    padding-bottom: 0.5rem; margin-bottom: 0.75rem;
    border-bottom: 1px solid var(--glass-border); position: relative;
}}
.sb-t3-title::after {{
    content: ''; position: absolute; bottom: -1px; left: 0; width: 32px; height: 1px;
    background: var(--primary);
    box-shadow: 0 0 6px color-mix(in srgb, var(--primary) 50%, transparent);
}}

/* Search */
.sb-t3-search {{ display: flex; }}
.sb-t3-input {{
    flex: 1; padding: 0.6rem 0.85rem; border: 1px solid var(--glass-border);
    border-right: none; border-radius: 10px 0 0 10px; font-size: 0.88rem;
    font-family: inherit; outline: none; background: rgba(255,255,255,0.03);
    color: var(--text); transition: border-color 0.25s;
}}
.sb-t3-input:focus {{ border-color: var(--primary); }}
.sb-t3-input::placeholder {{ color: var(--muted); }}
.sb-t3-search-btn {{
    padding: 0 0.85rem; background: var(--primary);
    border: none; border-radius: 0 10px 10px 0; color: #fff; cursor: pointer; font-size: 0.88rem;
    transition: box-shadow 0.25s;
}}
.sb-t3-search-btn:hover {{ box-shadow: 0 0 12px color-mix(in srgb, var(--primary) 40%, transparent); }}

/* Categories */
.sb-t3-cats {{ display: flex; flex-direction: column; gap: 0.2rem; }}
.sb-t3-cat-link {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.45rem 0.5rem; border-radius: 8px;
    text-decoration: none; color: var(--muted); font-size: 0.88rem; font-weight: 500;
    transition: all 0.25s;
}}
.sb-t3-cat-link:hover {{ background: rgba(255,255,255,0.04); color: var(--text); }}
.sb-t3-cat-count {{
    background: var(--glass); border: 1px solid var(--glass-border);
    font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; color: var(--muted);
}}

/* Popular */
.sb-t3-pops {{ display: flex; flex-direction: column; gap: 0.65rem; }}
.sb-t3-pop-item {{
    display: flex; gap: 0.75rem; align-items: center; text-decoration: none;
    color: var(--muted); transition: color 0.25s;
}}
.sb-t3-pop-item:hover {{ color: var(--text); }}
.sb-t3-pop-img {{
    width: 52px; height: 52px; border-radius: 10px; object-fit: cover; flex-shrink: 0;
    border: 1px solid var(--glass-border);
}}
.sb-t3-pop-num {{
    width: 36px; height: 36px; border-radius: 10px;
    background: var(--primary); color: #fff;
    font-weight: 700; font-size: 0.85rem; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0;
    box-shadow: 0 0 10px color-mix(in srgb, var(--primary) 30%, transparent);
}}
.sb-t3-pop-title {{ font-size: 0.88rem; font-weight: 500; line-height: 1.35; }}

/* Newsletter */
.sb-t3-nl {{
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 10%, var(--bg)), color-mix(in srgb, var(--secondary) 6%, var(--bg)));
    border-color: color-mix(in srgb, var(--primary) 20%, transparent);
}}
.sb-t3-nl-text {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 0.75rem; }}
.sb-t3-nl-form {{ display: flex; flex-direction: column; gap: 0.5rem; }}
.sb-t3-nl-form .sb-t3-input {{ border-right: 1px solid var(--glass-border); border-radius: 10px; }}
.sb-t3-nl-btn {{
    padding: 0.6rem; background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; border: none; border-radius: 10px; font-weight: 600; font-size: 0.88rem;
    cursor: pointer; transition: box-shadow 0.25s;
}}
.sb-t3-nl-btn:hover {{ box-shadow: 0 0 16px color-mix(in srgb, var(--primary) 35%, transparent); }}
.sb-t3-empty {{ color: var(--muted); font-size: 0.85rem; font-style: italic; }}

/* Writer */
.sb-t3-writer-card {{
    text-align: center;
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 8%, var(--bg)), color-mix(in srgb, var(--secondary) 5%, var(--bg)));
}}
.sb-t3-writer-av {{
    width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 0.5rem;
    border: 2px solid color-mix(in srgb, var(--primary) 30%, transparent);
}}
.sb-t3-writer-init {{
    width: 80px; height: 80px; border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff;
    font-size: 2rem; font-weight: 700; display: flex; align-items: center;
    justify-content: center; margin: 0 auto 0.5rem;
    box-shadow: 0 0 20px color-mix(in srgb, var(--primary) 25%, transparent);
}}
.sb-t3-writer-name {{ display: block; font-size: 1rem; font-weight: 700; color: var(--text); }}
.sb-t3-writer-title {{
    display: block; font-size: 0.78rem; color: var(--secondary); text-transform: uppercase;
    letter-spacing: 0.06em; margin-bottom: 0.5rem;
}}
.sb-t3-writer-bio {{ font-size: 0.85rem; color: var(--muted); line-height: 1.5; }}
"""
    return {"html": html_content, "css": css}
