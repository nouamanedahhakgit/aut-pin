"""Shared helpers for Theme 1 — Warm gradient style. Used by all pages in this theme."""

from shared_style import extract_style, part_font


def theme_base(config: dict) -> dict:
    """Return common theme values: style dict, font family, font import, body font, CSS variables block."""
    s = extract_style(config)
    pf = part_font("domain_page", config)
    font_import = f"@import url('{pf.get('cdn')}');" if (pf.get("cdn") or "").strip() else ""
    font_family = pf.get("family") or "Playfair Display, serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    css_vars = f"""
    --primary: {s.get("primary", "#E07C5E")};
    --secondary: {s.get("secondary", "#D46A4A")};
    --bg: {s.get("background", "#fff")};
    --text: {s.get("text_primary", "#2D2D2D")};
    --muted: {s.get("text_secondary", "#6B5B55")};
    --border: {s.get("border", "#F0E0D8")};
    font-family: {body_font}; color: var(--text); background: var(--bg);"""

    return {
        "s": s,
        "font_import": font_import,
        "font_family": font_family,
        "body_font": body_font,
        "css_vars": css_vars,
    }


def hero_css(font_family: str) -> str:
    """Shared hero section CSS for theme 1."""
    return f"""
.dp-t1-hero {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; text-align: center; padding: 3.5rem 1.5rem 2.5rem;
}}
.dp-t1-hero-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.8; margin-bottom: 0.5rem; }}
.dp-t1-hero h1 {{ font-family: {font_family}; font-size: 2.5rem; font-weight: 700; margin: 0 0 0.5rem; }}
.dp-t1-hero p {{ max-width: 600px; margin: 0 auto; opacity: 0.9; line-height: 1.6; }}
"""


def body_css(font_family: str) -> str:
    """Shared body and section CSS for theme 1."""
    return f"""
.dp-t1-body {{ max-width: 800px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}
.dp-t1-section {{ margin-bottom: 2rem; }}
.dp-t1-h2 {{ font-family: {font_family}; font-size: 1.4rem; font-weight: 700; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border); }}
.dp-t1-section p, .dp-t1-section li {{ color: var(--muted); font-size: 0.95rem; line-height: 1.8; }}
.dp-t1-section ul {{ padding-left: 1.25rem; }}
@media (max-width: 600px) {{ .dp-t1-hero h1 {{ font-size: 1.8rem; }} }}
"""
