"""Shared helpers for Theme 2 — Modern clean style. Used by all pages in this theme."""

from shared_style import extract_style, part_font


def theme_base(config: dict) -> dict:
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
    return f"""
.dp-t2-hero {{
    background: color-mix(in srgb, var(--primary) 8%, var(--bg));
    text-align: center; padding: 3rem 1.5rem 2.5rem;
    border-bottom: 3px solid var(--primary);
}}
.dp-t2-hero-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--primary); font-weight: 700; margin-bottom: 0.5rem; }}
.dp-t2-hero h1 {{ font-family: {font_family}; font-size: 2.4rem; font-weight: 700; color: var(--text); margin: 0 0 0.5rem; }}
.dp-t2-hero p {{ max-width: 600px; margin: 0 auto; color: var(--muted); line-height: 1.6; }}
"""


def body_css(font_family: str) -> str:
    return f"""
.dp-t2-body {{ max-width: 800px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}
.dp-t2-section {{ margin-bottom: 2rem; }}
.dp-t2-h2 {{
    font-family: {font_family}; font-size: 1.3rem; font-weight: 700;
    color: var(--text); margin-bottom: 0.75rem;
    display: flex; align-items: center; gap: 0.5rem;
}}
.dp-t2-h2::before {{ content: ''; width: 4px; height: 1.2em; background: var(--primary); border-radius: 2px; flex-shrink: 0; }}
.dp-t2-section p, .dp-t2-section li {{ color: var(--muted); font-size: 0.95rem; line-height: 1.8; }}
.dp-t2-section ul {{ padding-left: 1.25rem; }}
@media (max-width: 600px) {{ .dp-t2-hero h1 {{ font-size: 1.8rem; }} }}
"""
