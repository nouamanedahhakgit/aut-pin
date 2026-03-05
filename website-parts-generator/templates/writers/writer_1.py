"""Writer 1 — Horizontal author card with avatar, bio, and social links."""


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
    bio = html_module.escape(str(writer.get("bio") or "")[:300])
    avatar = (writer.get("avatar") or writer.get("avatar_url") or "").strip()
    writer_url = html_module.escape(str(writer.get("url") or "#"))

    if avatar and avatar.startswith("http"):
        avatar_html = f'<img src="{html_module.escape(avatar)}" alt="{name}" class="wr1-avatar">'
    else:
        initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "A"
        avatar_html = f'<div class="wr1-avatar wr1-avatar-placeholder"><span>{initials}</span></div>'

    social_html = ""
    socials = writer.get("social") or writer.get("social_links") or {}
    if isinstance(socials, dict):
        icon_map = {"facebook": "fab fa-facebook-f", "instagram": "fab fa-instagram", "twitter": "fab fa-twitter", "pinterest": "fab fa-pinterest-p", "linkedin": "fab fa-linkedin-in"}
        for platform, url in socials.items():
            if url:
                icon = icon_map.get(platform.lower(), "fas fa-link")
                social_html += f'<a href="{html_module.escape(str(url))}" class="wr1-social" aria-label="{html_module.escape(platform)}"><i class="{icon}"></i></a>'

    title_html = f'<span class="wr1-title">{title}</span>' if title else ""

    html_content = f"""
<div class="writer-card writer-1">
  {avatar_html}
  <div class="wr1-info">
    <div class="wr1-meta">
      <a href="{writer_url}" class="wr1-name">{name}</a>
      {title_html}
    </div>
    <p class="wr1-bio">{bio}</p>
    <div class="wr1-socials">{social_html}</div>
  </div>
</div>
"""

    css = f"""
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
{font_import}

.writer-1 {{
    --primary: {s.get("primary", "#E07C5E")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font};
    display: flex; gap: 1.5rem; align-items: flex-start;
    padding: 1.75rem; border: 1px solid var(--border); border-radius: 12px;
    background: var(--bg);
}}

.wr1-avatar {{
    width: 80px; height: 80px; border-radius: 50%; object-fit: cover;
    flex-shrink: 0; border: 3px solid color-mix(in srgb, var(--primary) 20%, transparent);
}}
.wr1-avatar-placeholder {{
    background: linear-gradient(135deg, var(--primary), color-mix(in srgb, var(--primary) 60%, #000));
    color: #fff; display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; font-weight: 700; border: none;
}}

.wr1-info {{ flex: 1; min-width: 0; }}
.wr1-meta {{ display: flex; align-items: baseline; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.5rem; }}
.wr1-name {{
    font-family: {font_family}; font-size: 1.2rem; font-weight: 700;
    color: var(--text); text-decoration: none; transition: color 0.2s;
}}
.wr1-name:hover {{ color: var(--primary); }}
.wr1-title {{
    font-size: 0.8rem; color: var(--primary); font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.03em;
}}
.wr1-bio {{ color: var(--muted); font-size: 0.9rem; line-height: 1.6; margin-bottom: 0.75rem; }}

.wr1-socials {{ display: flex; gap: 0.5rem; }}
.wr1-social {{
    width: 32px; height: 32px; border-radius: 50%;
    border: 1px solid var(--border); color: var(--muted);
    display: flex; align-items: center; justify-content: center;
    text-decoration: none; font-size: 0.8rem; transition: all 0.2s;
}}
.wr1-social:hover {{ border-color: var(--primary); color: var(--primary); }}

@media (max-width: 600px) {{
    .writer-1 {{ flex-direction: column; align-items: center; text-align: center; }}
    .wr1-meta {{ justify-content: center; }}
    .wr1-socials {{ justify-content: center; }}
}}
"""
    return {"html": html_content, "css": css}
