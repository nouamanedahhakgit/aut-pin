"""Shared helpers for Theme 7 — Midnight Luxe.
Design language: Deep indigo-to-plum gradient hero with gold (#d4a853) accent
highlights, 1.25rem rounded cards with soft luminous box-shadows, elegant serif
headings (generous letter-spacing, weight 700-800), smooth 0.3 s hover
transitions, and a high-end culinary-magazine aesthetic throughout.
"""

from shared_style import extract_style, part_font

THEME = 7


def theme_base(config: dict) -> dict:
    s = extract_style(config)
    pf = part_font("domain_page", config)
    cdn_url = (pf.get("cdn") or "").strip()
    font_import = (
        f"@import url('{cdn_url}');"
        if cdn_url
        else ""
    )
    font_family = pf.get("family") or "Playfair Display, serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    css_vars = f"""
    --primary: {s.get("primary", "#1a1a2e")};
    --secondary: {s.get("secondary", "#16213e")};
    --bg: {s.get("background", "#fafafa")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#555")};
    --border: {s.get("border", "#e0e0e0")};
    --radius: 1.25rem;
    --gold: #d4a853;
    --glow: 0 4px 24px rgba(26, 26, 46, .08);
    font-family: {body_font};
    color: var(--text);
    background: var(--bg);
    line-height: 1.75;
    box-sizing: border-box;"""

    return {
        "s": s,
        "font_import": font_import,
        "font_family": font_family,
        "body_font": body_font,
        "css_vars": css_vars,
    }


# ── hero ────────────────────────────────────────────────────────────────
def hero_css(root: str, font_family: str) -> str:
    return f"""
{root} .t7-hero {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 55%, var(--primary) 100%);
    padding: 80px 32px 72px;
    text-align: center;
    color: #fff;
    position: relative;
    overflow: hidden;
}}
{root} .t7-hero::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 30% 60%, rgba(212,168,83,.15) 0%, transparent 60%);
    pointer-events: none;
}}
{root} .t7-hero-inner {{
    max-width: 900px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}}
{root} .t7-badge {{
    display: inline-block;
    background: var(--gold);
    color: var(--primary);
    font-size: .7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 6px 20px;
    border-radius: 30px;
    margin-bottom: 20px;
}}
{root} .t7-hero-title {{
    font-family: {font_family};
    font-size: clamp(2rem, 5vw, 3.4rem);
    font-weight: 800;
    letter-spacing: .5px;
    margin: 0 0 16px;
    line-height: 1.18;
    color: #fff;
}}
{root} .t7-hero-sub {{
    font-size: .92rem;
    color: rgba(255,255,255,.78);
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
}}
@media (max-width: 768px) {{
    {root} .t7-hero {{ padding: 56px 20px 48px; }}
    {root} .t7-hero-title {{ font-size: clamp(1.6rem, 6vw, 2.4rem); }}
}}
"""


# ── body ────────────────────────────────────────────────────────────────
def body_css(root: str, font_family: str) -> str:
    return f"""
{root} .t7-wrap {{
    max-width: 900px;
    margin: 0 auto;
    padding: 56px 48px 80px;
}}
{root} .t7-section {{
    padding: 48px 0;
    border-bottom: 1px solid var(--border);
}}
{root} .t7-section:last-child {{ border-bottom: none; }}
{root} .t7-section h3 {{
    font-family: {font_family};
    font-weight: 800;
    font-size: 1.35rem;
    letter-spacing: .3px;
    margin: 0 0 18px;
    color: var(--text);
}}
{root} .t7-rule {{
    width: 36px;
    height: 3px;
    background: var(--gold);
    border-radius: 2px;
    margin-bottom: 18px;
}}
{root} .t7-body {{
    font-size: 1rem;
    color: var(--muted);
}}
{root} .t7-body p {{
    margin-bottom: 14px;
}}
{root} .t7-body ul {{
    margin: 10px 0 14px 20px;
    list-style: disc;
}}
{root} .t7-body li {{
    margin-bottom: 6px;
}}
{root} .t7-body a {{
    color: var(--primary);
    text-decoration: underline;
    text-underline-offset: 3px;
    transition: color .3s;
}}
{root} .t7-body a:hover {{
    color: var(--gold);
}}
{root} .t7-card {{
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 32px;
    background: var(--bg);
    box-shadow: var(--glow);
    transition: box-shadow .3s, transform .3s;
}}
{root} .t7-card:hover {{
    box-shadow: 0 8px 32px rgba(26,26,46,.13);
    transform: translateY(-2px);
}}
{root} .t7-btn-primary {{
    display: inline-block;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    padding: 14px 36px;
    font-weight: 800;
    font-size: .82rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-radius: var(--radius);
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: opacity .3s, transform .3s;
}}
{root} .t7-btn-primary:hover {{
    opacity: .9;
    transform: translateY(-1px);
}}
{root} .t7-btn-ghost {{
    display: inline-block;
    background: transparent;
    border: 2px solid var(--border);
    color: var(--text);
    padding: 14px 36px;
    font-weight: 800;
    font-size: .82rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-radius: var(--radius);
    text-decoration: none;
    cursor: pointer;
    transition: border-color .3s, color .3s;
}}
{root} .t7-btn-ghost:hover {{
    border-color: var(--gold);
    color: var(--gold);
}}
@media (max-width: 768px) {{
    {root} .t7-wrap {{ padding: 40px 20px 60px; }}
    {root} .t7-section h3 {{ font-size: 1.18rem; }}
}}
@media (max-width: 600px) {{
    {root} .t7-wrap {{ padding: 32px 16px 48px; }}
    {root} .t7-btn-primary,
    {root} .t7-btn-ghost {{ padding: 12px 24px; font-size: .78rem; }}
}}
"""
