"""Shared helpers for Theme 11 — Art Deco Elegance.
Design language: Rich cream backgrounds, gold (#C9A96E) accent lines & ornaments,
obsidian (#1B1B1B) text, emerald (#1E5945) secondary, Libre Baskerville display
headings, Raleway body. Geometric fan patterns, thin gold rules, symmetrical
layouts, stepped zigzag decorations, and a 1920s luxury magazine feel.
"""

from shared_style import extract_style, part_font

THEME = 11


def _hex_to_rgb_for_rgba(hex_str):
    """Convert #RRGGBB to 'r,g,b' for rgba(r,g,b,a)."""
    h = (hex_str or "#C9A96E").strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return "201,169,110"
    try:
        return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"
    except ValueError:
        return "201,169,110"


def theme_base(config: dict) -> dict:
    """Return common theme values for theme 11."""
    s = extract_style(config)
    pf = part_font("domain_page", config)
    cdn_url = (pf.get("cdn") or "").strip()
    font_import = f"@import url('{cdn_url}');" if cdn_url else ""
    font_family = pf.get("family") or "Libre Baskerville, Georgia, serif"
    body_font = s.get("body_family", "Raleway, sans-serif")

    gold = s.get("gold", "#C9A96E")
    gold_rgb = _hex_to_rgb_for_rgba(gold)
    primary = s.get("primary", "#1B1B1B")
    primary_rgb = _hex_to_rgb_for_rgba(primary)
    css_vars = f"""
    --primary:   {primary};
    --primary-rgb: {primary_rgb};
    --secondary: {s.get("secondary",  "#1E5945")};
    --accent:    {s.get("accent",     "#C9A96E")};
    --bg:        {s.get("background", "#F7F1E8")};
    --surface:   {s.get("surface", "#F0E8DB")};
    --surface2:  {s.get("surface2", "#EBE2D3")};
    --menu-link: {s.get("menu_link", s.get("text_secondary", "#6B6155"))};
    --menu-link-hover: {s.get("menu_link_hover", s.get("gold", "#C9A96E"))};
    --gold:      {gold};
    --gold-light: rgba({gold_rgb},0.15);
    --gold-very-light: rgba({gold_rgb},0.08);
    --gold-border: rgba({gold_rgb},0.45);
    --text:      {s.get("text_primary",   "#1B1B1B")};
    --muted:     {s.get("text_secondary", "#6B6155")};
    --text-on-primary: {s.get("text_on_primary", "#FFFFFF")};
    --text-on-primary-muted: {s.get("text_on_primary_muted", "#B8B0A8")};
    --border:    {s.get("border",         "#D4C8B8")};
    --border-light: {s.get("border_light", "#E5E7EB")};
    --shadow-sm: 0 2px 12px rgba({primary_rgb},0.06);
    --shadow:    0 6px 28px rgba({primary_rgb},0.10);
    --shadow-lg: 0 16px 56px rgba({primary_rgb},0.14);
    --radius:    4px;
    --radius-lg: 8px;
    font-family: {body_font}; color: var(--text); background: var(--bg);
    line-height: 1.75; box-sizing: border-box;"""

    return {
        "s": s,
        "font_import": font_import,
        "font_family": font_family,
        "body_font": body_font,
        "css_vars": css_vars,
    }


# ── Keyframes ────────────────────────────────────────────────────────────────
KEYFRAMES = """
@keyframes t11-fade-in {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes t11-fan-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
"""


def hero_css(font_family: str) -> str:
    """Shared Art Deco hero section CSS for theme 11."""
    return f"""
{KEYFRAMES}
.dp-t11-hero {{
    background: var(--primary); color: var(--text-on-primary);
    text-align: center; padding: 5rem 1.5rem 4rem;
    position: relative; overflow: hidden;
}}
.dp-t11-hero::before {{
    content: ''; position: absolute; top: -80px; left: 50%;
    transform: translateX(-50%); width: 400px; height: 400px;
    background: conic-gradient(from 0deg, transparent 0deg, var(--gold-very-light) 15deg, transparent 30deg);
    background-size: 100% 100%; border-radius: 50%;
    animation: t11-fan-spin 30s linear infinite;
    pointer-events: none;
}}
.dp-t11-hero::after {{
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, transparent 0%, var(--gold) 30%, var(--gold) 70%, transparent 100%);
}}
.dp-t11-hero-label {{
    display: inline-block; font-size: 0.7rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.35em;
    color: var(--gold); margin-bottom: 1.25rem;
    padding: 0 1.5rem; position: relative;
}}
.dp-t11-hero-label::before, .dp-t11-hero-label::after {{
    content: '◆'; position: absolute; top: 50%; transform: translateY(-50%);
    color: var(--gold); font-size: 0.45rem;
}}
.dp-t11-hero-label::before {{ left: 0; }}
.dp-t11-hero-label::after  {{ right: 0; }}
.dp-t11-hero h1 {{
    font-family: {font_family}; font-size: clamp(2rem, 5vw, 3.4rem);
    font-weight: 700; margin: 0 0 0.75rem; color: var(--text-on-primary);
    line-height: 1.2; letter-spacing: 0.02em;
}}
.dp-t11-hero h1 em {{ font-style: italic; color: var(--gold); }}
.dp-t11-hero p {{
    max-width: 560px; margin: 0 auto; color: var(--text-on-primary-muted);
    font-size: 1rem; line-height: 1.7;
}}
.dp-t11-ornament {{
    display: flex; align-items: center; justify-content: center; gap: 10px;
    margin-top: 1.5rem; color: var(--gold); font-size: 0.65rem;
    letter-spacing: 0.3em;
}}
.dp-t11-ornament::before, .dp-t11-ornament::after {{
    content: ''; width: 60px; height: 1px; background: var(--gold); opacity: 0.5;
}}
@media (max-width: 600px) {{ .dp-t11-hero h1 {{ font-size: 1.8rem; }} .dp-t11-hero {{ padding: 3.5rem 1rem 3rem; }} }}
"""


def body_css(font_family: str) -> str:
    """Shared Art Deco body/section CSS for theme 11."""
    return f"""
.dp-t11-body {{ max-width: 840px; margin: 0 auto; padding: 3rem 1.5rem 5rem; animation: t11-fade-in 0.6s ease both; }}
.dp-t11-section {{ margin-bottom: 2.75rem; }}
.dp-t11-h2 {{
    font-family: {font_family}; font-size: 1.4rem; font-weight: 700;
    color: var(--text); margin: 0 0 0.85rem;
    text-transform: uppercase; letter-spacing: 0.08em;
    padding-bottom: 0.6rem; border-bottom: 1px solid var(--border);
    position: relative;
}}
.dp-t11-h2::after {{
    content: ''; position: absolute; bottom: -1px; left: 0;
    width: 50px; height: 2px; background: var(--gold);
}}
.dp-t11-section p  {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin: 0 0 0.7rem; }}
.dp-t11-section li {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin-bottom: 0.45rem; }}
.dp-t11-section ul {{ padding-left: 1.3rem; list-style: none; }}
.dp-t11-section ul li::before {{ content: '◆'; color: var(--gold); font-size: 0.5rem; margin-right: 8px; vertical-align: middle; }}
.dp-t11-section strong {{ color: var(--text); font-weight: 700; }}
"""
