"""Shared helpers for Theme 6 — Neo-Brutalist.
Design language: High contrast, thick black borders, hard offset shadows,
bold typography, and vibrant accent colors.
"""

from shared_style import extract_style, part_font

THEME = 6

def theme_base(config: dict) -> dict:
    s = extract_style(config)
    pf = part_font("domain_page", config)
    cdn_url = (pf.get("cdn") or "").strip()
    font_import = f"@import url('{cdn_url}');" if cdn_url else ""
    font_family = pf.get("family") or "Inter, sans-serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    css_vars = f"""
    --primary: {s.get("primary", "#FFDE00")};
    --secondary: {s.get("secondary", "#FF00FF")};
    --bg: {s.get("background", "#ffffff")};
    --text: {s.get("text_primary", "#000000")};
    --muted: {s.get("text_secondary", "#333333")};
    --border: #000000;
    --border-width: 4px;
    --shadow: 8px 8px 0px #000000;
    --shadow-small: 4px 4px 0px #000000;
    font-family: {body_font};
    color: var(--text);
    background: var(--bg);
    line-height: 1.6;
    box-sizing: border-box;"""

    return {
        "s": s,
        "font_import": font_import,
        "font_family": font_family,
        "body_font": body_font,
        "css_vars": css_vars,
    }

def hero_css(root: str, font_family: str) -> str:
    return f"""
{root} .t6-hero {{
    background: var(--primary);
    border-bottom: var(--border-width) solid var(--border);
    padding: 100px 32px;
    text-align: center;
    position: relative;
}}
{root} .t6-hero-inner {{
    max-width: 900px;
    margin: 0 auto;
    background: white;
    border: var(--border-width) solid var(--border);
    padding: 60px 40px;
    box-shadow: var(--shadow);
    display: inline-block;
}}
{root} .t6-hero-title {{
    font-family: {font_family};
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 900;
    text-transform: uppercase;
    margin: 0 0 20px;
    line-height: 1;
    letter-spacing: -2px;
}}
{root} .t6-hero-sub {{
    font-size: 1.2rem;
    font-weight: 700;
    max-width: 600px;
    margin: 0 auto;
    background: var(--secondary);
    color: white;
    padding: 8px 16px;
    display: inline-block;
    border: 3px solid #000;
}}
@media (max-width: 768px) {{
    {root} .t6-hero {{ padding: 60px 20px; }}
    {root} .t6-hero-inner {{ padding: 30px 20px; }}
}}
"""

def body_css(root: str, font_family: str) -> str:
    return f"""
{root} .t6-wrap {{
    max-width: 1000px;
    margin: 0 auto;
    padding: 80px 40px;
}}
{root} .t6-section {{
    margin-bottom: 60px;
    background: white;
    border: var(--border-width) solid var(--border);
    padding: 40px;
    box-shadow: var(--shadow);
}}
{root} .t6-section:nth-child(even) {{
    background: #fafafa;
    transform: rotate(-1deg);
}}
{root} .t6-section:nth-child(odd) {{
    transform: rotate(1deg);
}}
{root} .t6-section h3 {{
    font-family: {font_family};
    font-weight: 900;
    font-size: 2rem;
    text-transform: uppercase;
    margin: 0 0 24px;
    display: inline-block;
    border-bottom: 6px solid var(--primary);
}}
{root} .t6-body {{
    font-size: 1.1rem;
    font-weight: 500;
}}
{root} .t6-body p {{ margin-bottom: 20px; }}
{root} .t6-body ul {{ margin: 0 0 20px 30px; list-style: square; }}
{root} .t6-body li {{ margin-bottom: 10px; }}
{root} .t6-body a {{
    color: var(--text);
    text-decoration: none;
    font-weight: 800;
    border-bottom: 3px solid var(--secondary);
    transition: background 0.2s;
}}
{root} .t6-body a:hover {{ background: var(--secondary); color: white; }}
{root} .t6-btn-primary {{
    display: inline-block;
    background: var(--primary);
    color: #000;
    padding: 16px 32px;
    font-weight: 900;
    text-transform: uppercase;
    border: var(--border-width) solid var(--border);
    box-shadow: 4px 4px 0px #000;
    text-decoration: none;
    transition: transform 0.1s, box-shadow 0.1s;
}}
{root} .t6-btn-primary:active {{
    transform: translate(3px, 3px);
    box-shadow: 1px 1px 0px #000;
}}
@media (max-width: 768px) {{
    {root} .t6-wrap {{ padding: 40px 20px; }}
    {root} .t6-section {{ padding: 25px; transform: none !important; }}
}}
"""
