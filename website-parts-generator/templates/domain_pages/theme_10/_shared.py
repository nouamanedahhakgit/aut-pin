"""Shared helpers for Theme 10 — Bento Fresh.
Design language: Ultra-clean white (#FFFFFF) base, fresh mint/teal (#00BFA5) primary
accent, warm coral (#FF6B6B) secondary, DM Sans body, Fraunces display headings.
App-like 24px rounded corners, soft shadows, bento grid layouts. Zero clutter.
"""

from shared_style import extract_style, part_font

THEME = 10


def theme_base(config: dict) -> dict:
    """Return common theme values for theme 10."""
    s = extract_style(config)
    pf = part_font("domain_page", config)
    cdn_url = (pf.get("cdn") or "").strip()
    font_import = f"@import url('{cdn_url}');" if cdn_url else ""
    font_family = pf.get("family") or "Fraunces, Georgia, serif"
    body_font = s.get("body_family", "DM Sans, Inter, sans-serif")

    css_vars = f"""
    --primary:   {s.get("primary",    "#00BFA5")};
    --secondary: {s.get("secondary",  "#FF6B6B")};
    --accent:    {s.get("accent",     "#FFC107")};
    --bg:        {s.get("background", "#FFFFFF")};
    --surface:   #F8FFFE;
    --surface2:  #F0FAF8;
    --mint-pale: rgba(0,191,165,0.08);
    --mint-border: rgba(0,191,165,0.25);
    --text:      {s.get("text_primary",   "#111827")};
    --muted:     {s.get("text_secondary", "#6B7280")};
    --border:    {s.get("border",         "#E5E7EB")};
    --shadow-sm: 0 1px 8px rgba(0,0,0,0.05);
    --shadow:    0 4px 20px rgba(0,0,0,0.08);
    --shadow-lg: 0 12px 48px rgba(0,0,0,0.12);
    --radius:    16px;
    --radius-lg: 24px;
    --radius-xl: 32px;
    font-family: {body_font}; color: var(--text); background: var(--bg);
    line-height: 1.7; box-sizing: border-box;"""

    return {
        "s": s,
        "font_import": font_import,
        "font_family": font_family,
        "body_font": body_font,
        "css_vars": css_vars,
    }


# ── Keyframes ────────────────────────────────────────────────────────────────
KEYFRAMES = """
@keyframes t10-fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes t10-pulse-dot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.4); opacity: 0.7; }
}
"""


def hero_css(font_family: str) -> str:
    """Shared hero section CSS for theme 10."""
    return f"""
{KEYFRAMES}
.dp-t10-hero {{
    background: var(--bg); padding: 4.5rem 1.5rem 3.5rem;
    border-bottom: 1px solid var(--border);
    text-align: center;
}}
.dp-t10-hero-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--mint-pale); border: 1px solid var(--mint-border);
    color: var(--primary); padding: 6px 16px; border-radius: 50px;
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.18em; margin-bottom: 1.25rem;
}}
.dp-t10-hero-badge::before {{
    content: ''; width: 6px; height: 6px; border-radius: 50%;
    background: var(--primary); animation: t10-pulse-dot 2s infinite;
}}
.dp-t10-hero h1 {{
    font-family: {font_family}; font-size: clamp(2rem, 5.5vw, 3.5rem);
    font-weight: 700; margin: 0 0 0.85rem; color: var(--text);
    line-height: 1.15; letter-spacing: -0.02em;
}}
.dp-t10-hero h1 em {{ font-style: italic; color: var(--primary); }}
.dp-t10-hero p {{
    max-width: 540px; margin: 0 auto; color: var(--muted);
    font-size: 1.05rem; line-height: 1.7;
}}
@media (max-width: 600px) {{ .dp-t10-hero h1 {{ font-size: 1.85rem; }} }}
"""


def body_css(font_family: str) -> str:
    """Shared body and section CSS for theme 10."""
    return f"""
.dp-t10-body {{ max-width: 840px; margin: 0 auto; padding: 3rem 1.5rem 5rem; animation: t10-fade-up 0.6s ease both; }}
.dp-t10-section {{ margin-bottom: 2.75rem; }}
.dp-t10-h2 {{
    font-family: {font_family}; font-size: 1.45rem; font-weight: 700;
    color: var(--text); margin: 0 0 0.85rem;
    display: flex; align-items: center; gap: 10px;
}}
.dp-t10-h2::before {{
    content: ''; display: inline-block; width: 5px; height: 1.2em;
    background: var(--primary); border-radius: 4px; flex-shrink: 0;
}}
.dp-t10-section p  {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin: 0 0 0.7rem; }}
.dp-t10-section li {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin-bottom: 0.45rem; }}
.dp-t10-section ul {{ padding-left: 1.3rem; }}
.dp-t10-section strong {{ color: var(--text); font-weight: 600; }}
.dp-t10-chip {{
    display: inline-block; background: var(--mint-pale); color: var(--primary);
    border: 1px solid var(--mint-border); padding: 3px 12px;
    border-radius: 50px; font-size: 0.78rem; font-weight: 600;
}}
"""
