"""Writer 2 — Centered author profile with accent background and article count."""


def generate(config: dict) -> dict:
    import html as html_module
    from shared_style import extract_style, part_font

    s = extract_style(config)
    pf = part_font("writer", config)
    font_import = f"@import url('{pf.get('cdn')}');" if pf.get("cdn") else ""
    font_family = pf.get("family") or "'Playfair Display', serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    writer = config.get("writer") or config
    name = html_module.escape(str(writer.get("name") or "Author"))
    title = html_module.escape(str(writer.get("title") or ""))
    bio = html_module.escape(str(writer.get("bio") or "")[:400])
    avatar = (writer.get("avatar") or writer.get("avatar_url") or "").strip()
    writer_url = html_module.escape(str(writer.get("url") or "#"))
    article_count = writer.get("article_count") or writer.get("articles_count") or ""

    if avatar and avatar.startswith("http"):
        avatar_html = f'<img src="{html_module.escape(avatar)}" alt="{name}" class="wr2-avatar">'
    else:
        initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "A"
        avatar_html = f'<div class="wr2-avatar wr2-avatar-placeholder"><span>{initials}</span></div>'

    social_html = ""
    socials = writer.get("social") or writer.get("social_links") or {}
    if isinstance(socials, dict):
        icon_map = {"facebook": "fab fa-facebook-f", "instagram": "fab fa-instagram", "twitter": "fab fa-twitter", "pinterest": "fab fa-pinterest-p", "linkedin": "fab fa-linkedin-in"}
        for platform, url in socials.items():
            if url:
                icon = icon_map.get(platform.lower(), "fas fa-link")
                social_html += f'<a href="{html_module.escape(str(url))}" class="wr2-social" aria-label="{html_module.escape(platform)}"><i class="{icon}"></i></a>'

    stats_html = ""
    if article_count:
        stats_html = f"""
        <div class="wr2-stats">
          <div class="wr2-stat">
            <span class="wr2-stat-num">{html_module.escape(str(article_count))}</span>
            <span class="wr2-stat-label">Articles</span>
          </div>
        </div>"""

    html_content = f"""
<div class="writer-card writer-2">
  <div class="wr2-banner"></div>
  <div class="wr2-body">
    {avatar_html}
    <a href="{writer_url}" class="wr2-name">{name}</a>
    {"<p class='wr2-title'>" + title + "</p>" if title else ""}
    <p class="wr2-bio">{bio}</p>
    {stats_html}
    <div class="wr2-socials">{social_html}</div>
    <a href="{writer_url}" class="wr2-view-btn">View All Articles</a>
  </div>
</div>
"""

    css = f"""
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
{font_import}

.writer-2 {{
    --primary: {s.get("primary", "#E07C5E")};
    --secondary: {s.get("secondary", "#D46A4A")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font};
    border: 1px solid var(--border); border-radius: 16px;
    background: var(--bg); overflow: hidden; text-align: center;
}}

.wr2-banner {{
    height: 80px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
}}

.wr2-body {{ padding: 0 1.75rem 1.75rem; }}

.wr2-avatar {{
    width: 90px; height: 90px; border-radius: 50%; object-fit: cover;
    margin: -45px auto 0.75rem; border: 4px solid var(--bg);
    box-shadow: 0 2px 12px rgba(0,0,0,0.1); display: block;
}}
.wr2-avatar-placeholder {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; font-weight: 700;
}}

.wr2-name {{
    font-family: {font_family}; font-size: 1.4rem; font-weight: 700;
    color: var(--text); text-decoration: none; display: block;
    margin-bottom: 0.25rem; transition: color 0.2s;
}}
.wr2-name:hover {{ color: var(--primary); }}
.wr2-title {{
    color: var(--primary); font-size: 0.85rem; font-weight: 600;
    margin-bottom: 0.75rem;
}}
.wr2-bio {{
    color: var(--muted); font-size: 0.9rem; line-height: 1.7;
    margin-bottom: 1rem; max-width: 400px; margin-left: auto; margin-right: auto;
}}

.wr2-stats {{ display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem; }}
.wr2-stat {{ display: flex; flex-direction: column; align-items: center; }}
.wr2-stat-num {{ font-family: {font_family}; font-size: 1.4rem; font-weight: 700; color: var(--primary); }}
.wr2-stat-label {{ font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}

.wr2-socials {{ display: flex; justify-content: center; gap: 0.6rem; margin-bottom: 1rem; }}
.wr2-social {{
    width: 36px; height: 36px; border-radius: 50%;
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    color: var(--primary); display: flex; align-items: center; justify-content: center;
    text-decoration: none; font-size: 0.85rem; transition: all 0.2s;
}}
.wr2-social:hover {{ background: var(--primary); color: #fff; }}

.wr2-view-btn {{
    display: inline-block; padding: 0.6rem 1.5rem;
    border: 2px solid var(--primary); border-radius: 9999px;
    color: var(--primary); text-decoration: none; font-weight: 600;
    font-size: 0.9rem; transition: all 0.2s;
}}
.wr2-view-btn:hover {{ background: var(--primary); color: #fff; }}
"""
    return {"html": html_content, "css": css}
