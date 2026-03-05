"""Shared helpers for Theme 3 — Glassmorphism Dark Mode.

Design language:
- Hero: dark radial-gradient background with frosted glass inner panel
- Headings: bold, tracked uppercase with glow underline accent
- Sections: separated by subtle glass-border dividers, generous spacing
- Cards: frosted glass (backdrop-filter blur), soft border, subtle glow on hover
- Fonts: heading from part_font, body from s.get("body_family")
"""
from shared_style import extract_style, part_font

THEME = 3


def theme_base(config: dict) -> dict:
    """Return common theme values: style dict, font family, font import, body font, CSS variables block."""
    s = extract_style(config)
    pf = part_font("domain_page", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Playfair Display, serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    css_vars = f"""
    --primary: {s.get("primary", "#7C5CFC")};
    --secondary: {s.get("secondary", "#00D4AA")};
    --bg: {s.get("background", "#0F0F1A")};
    --text: {s.get("text_primary", "#E8E8F0")};
    --muted: {s.get("text_secondary", "#9898B0")};
    --border: {s.get("border", "rgba(255,255,255,0.08)")};
    --glass: rgba(255,255,255,0.04);
    --glass-border: rgba(255,255,255,0.1);
    --glow: {s.get("primary", "#7C5CFC")};
    --radius: 16px;
    font-family: {body_font}; color: var(--text); background: var(--bg);
    line-height: 1.75; box-sizing: border-box;"""

    return {
        "s": s,
        "font_import": font_import,
        "font_family": font_family,
        "body_font": body_font,
        "css_vars": css_vars,
    }


def hero_css(font_family: str) -> str:
    """Theme-consistent frosted-glass hero used by EVERY page."""
    return f"""
.dp-t3-hero {{
    background: radial-gradient(ellipse at 30% 0%, color-mix(in srgb, var(--primary) 18%, var(--bg)), var(--bg) 70%);
    text-align: center; padding: 5rem 1.5rem 3.5rem; position: relative; overflow: hidden;
}}
.dp-t3-hero::before {{
    content: ''; position: absolute; top: -40%; right: -20%; width: 600px; height: 600px;
    background: radial-gradient(circle, color-mix(in srgb, var(--secondary) 10%, transparent), transparent 70%);
    pointer-events: none;
}}
.dp-t3-hero-label {{
    display: inline-block; background: var(--glass); backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px); border: 1px solid var(--glass-border);
    padding: 0.4rem 1.2rem; border-radius: 9999px; font-size: 0.78rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--secondary); margin-bottom: 1rem;
}}
.dp-t3-hero h1 {{
    font-family: {font_family}; font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 800; margin: 0 0 0.75rem; color: #fff;
    text-shadow: 0 0 40px color-mix(in srgb, var(--primary) 30%, transparent);
}}
.dp-t3-hero p {{
    max-width: 600px; margin: 0 auto; color: var(--muted); font-size: 1rem; line-height: 1.7;
}}
"""


def body_css(font_family: str) -> str:
    """Theme-consistent body/section styles."""
    return f"""
.dp-t3-body {{ max-width: 860px; margin: 0 auto; padding: 3rem 1.5rem 5rem; }}
.dp-t3-section {{ margin-bottom: 2.5rem; }}
.dp-t3-h2 {{
    font-family: {font_family}; font-size: 1.35rem; font-weight: 700;
    margin-bottom: 0.75rem; padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--glass-border); color: var(--text);
    position: relative;
}}
.dp-t3-h2::after {{
    content: ''; position: absolute; bottom: -2px; left: 0; width: 48px; height: 2px;
    background: var(--primary);
    box-shadow: 0 0 8px color-mix(in srgb, var(--primary) 50%, transparent);
}}
.dp-t3-section p, .dp-t3-section li {{
    color: var(--muted); font-size: 0.95rem; line-height: 1.85;
}}
.dp-t3-section ul {{ padding-left: 1.25rem; }}
@media (max-width: 768px) {{
    .dp-t3-hero {{ padding: 3.5rem 1rem 2.5rem; }}
    .dp-t3-body {{ padding: 2rem 1rem 3.5rem; }}
}}
@media (max-width: 600px) {{
    .dp-t3-hero h1 {{ font-size: 1.8rem; }}
}}
"""
