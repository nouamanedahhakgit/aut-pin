"""Shared helpers for Theme 9 — Sunlit Elegance.
Design language: Pure white backgrounds, warm gold (#D4A843) and sage green (#7A9E7E)
accents, elegant Cormorant Garamond serif headings, clean editorial layout with
generous white space. Feels like a premium food magazine — airy, bright, sophisticated.
"""

from shared_style import extract_style, part_font

THEME = 9


def theme_base(config: dict) -> dict:
    """Return common theme values: style dict, font family, font import, body font, CSS variables block."""
    s = extract_style(config)
    pf = part_font("domain_page", config)
    cdn_url = (pf.get("cdn") or "").strip()
    font_import = f"@import url('{cdn_url}');" if cdn_url else ""
    font_family = pf.get("family") or "Cormorant Garamond, Georgia, serif"
    body_font = s.get("body_family", "Lato, Inter, sans-serif")

    css_vars = f"""
    --primary:   {s.get("primary",    "#D4A843")};
    --secondary: {s.get("secondary",  "#7A9E7E")};
    --accent:    {s.get("accent",     "#C8844A")};
    --bg:        {s.get("background", "#FFFFFF")};
    --surface:   #FAFAF8;
    --surface2:  #F5F3EE;
    --text:      {s.get("text_primary",   "#2C2416")};
    --muted:     {s.get("text_secondary", "#7A6A56")};
    --border:    {s.get("border",         "#E8DFD0")};
    --gold-light: #FBF3DC;
    --sage-light: #EAF0EB;
    --shadow-sm: 0 2px 12px rgba(44,36,22,0.06);
    --shadow:    0 4px 24px rgba(44,36,22,0.10);
    --shadow-lg: 0 12px 48px rgba(44,36,22,0.14);
    --radius:    12px;
    --radius-lg: 20px;
    font-family: {body_font}; color: var(--text); background: var(--bg);"""

    return {
        "s": s,
        "font_import": font_import,
        "font_family": font_family,
        "body_font": body_font,
        "css_vars": css_vars,
    }


def hero_css(font_family: str) -> str:
    """Shared hero section CSS for theme 9."""
    return f"""
@keyframes t9-fade-up {{
  from {{ opacity: 0; transform: translateY(18px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.dp-t9-hero {{
    background: linear-gradient(160deg, var(--surface2) 0%, var(--gold-light) 100%);
    text-align: center; padding: 4rem 1.5rem 3rem;
    border-bottom: 1px solid var(--border);
}}
.dp-t9-hero-label {{
    display: inline-block; font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.22em; color: var(--primary);
    background: rgba(212,168,67,0.12); border: 1px solid rgba(212,168,67,0.35);
    padding: 5px 16px; border-radius: 50px; margin-bottom: 1rem;
}}
.dp-t9-hero h1 {{
    font-family: {font_family}; font-size: clamp(1.9rem, 5vw, 3.2rem);
    font-weight: 700; margin: 0 0 0.75rem; color: var(--text);
    letter-spacing: -0.01em; line-height: 1.2;
    animation: t9-fade-up 0.7s ease both;
}}
.dp-t9-hero p {{
    max-width: 560px; margin: 0 auto; color: var(--muted);
    font-size: 1rem; line-height: 1.7;
}}
@media (max-width: 600px) {{ .dp-t9-hero h1 {{ font-size: 1.7rem; }} }}
"""


def body_css(font_family: str) -> str:
    """Shared body and section CSS for theme 9."""
    return f"""
.dp-t9-body {{ max-width: 820px; margin: 0 auto; padding: 3rem 1.5rem 4.5rem; }}
.dp-t9-section {{ margin-bottom: 2.5rem; }}
.dp-t9-h2 {{
    font-family: {font_family}; font-size: 1.5rem; font-weight: 700;
    color: var(--text); margin-bottom: 0.75rem;
    padding-bottom: 0.5rem; border-bottom: 2px solid var(--border);
    position: relative;
}}
.dp-t9-h2::after {{
    content: ''; position: absolute; bottom: -2px; left: 0;
    width: 44px; height: 2px; background: var(--primary);
}}
.dp-t9-section p  {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin: 0 0 0.6rem; }}
.dp-t9-section li {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin-bottom: 0.4rem; }}
.dp-t9-section ul {{ padding-left: 1.3rem; }}
.dp-t9-section strong {{ color: var(--text); font-weight: 600; }}
"""
