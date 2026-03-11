"""Shared helpers for Theme 7 — Minimalist Glass (Serene).
Design language: Translucent "glass" surfaces, refined serif/sans-serif mix, 
soft luminous glows, and elegant high-end simplicity.
"""

from shared_style import extract_style, part_font

THEME = 7

def theme_base(config: dict) -> dict:
    s = extract_style(config)
    pf = part_font("domain_page", config)
    cdn_url = (pf.get("cdn") or "").strip()
    font_import = f"@import url('{cdn_url}');" if cdn_url else ""
    font_family = pf.get("family") or "Playfair Display, serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    css_vars = f"""
    --primary: {s.get("primary", "#2C3E50")};
    --secondary: {s.get("secondary", "#16A085")};
    --bg: {s.get("background", "#F9FBFC")};
    --text: {s.get("text_primary", "#1A1A1A")};
    --muted: {s.get("text_secondary", "#5D6D7E")};
    --border: rgba(255,255,255,0.4);
    --glass-bg: rgba(255, 255, 255, 0.7);
    --glass-blur: blur(12px);
    --shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    --radius: 20px;
    font-family: {body_font};
    color: var(--text);
    background: var(--bg);
    line-height: 1.8;
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
{root} .t7-hero {{
    background: linear-gradient(125deg, #eef2f3 0%, #8e9eab 100%);
    padding: 120px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
}}
{root} .t7-hero::after {{
    content: "";
    position: absolute;
    top: -10%; right: -5%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(22,160,133,0.1), transparent 70%);
    z-index: 0;
}}
{root} .t7-hero-inner {{
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}}
{root} .t7-hero-title {{
    font-family: {font_family};
    font-size: clamp(2.2rem, 5vw, 4rem);
    font-weight: 700;
    margin: 0 0 24px;
    color: var(--primary);
    letter-spacing: -0.01em;
}}
{root} .t7-hero-sub {{
    font-size: 1.1rem;
    color: var(--muted);
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.7;
    font-weight: 300;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
@media (max-width: 768px) {{
    {root} .t7-hero {{ padding: 80px 20px; }}
}}
"""

def body_css(root: str, font_family: str) -> str:
    return f"""
{root} .t7-wrap {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 100px 40px;
}}
{root} .t7-section {{
    margin-bottom: 80px;
}}
{root} .t7-section h3 {{
    font-family: {font_family};
    font-weight: 700;
    font-size: 1.8rem;
    color: var(--primary);
    margin: 0 0 32px;
    position: relative;
    padding-bottom: 12px;
}}
{root} .t7-section h3::after {{
    content: "";
    position: absolute;
    bottom: 0; left: 0;
    width: 50px; height: 1px;
    background: var(--secondary);
}}
{root} .t7-body {{
    font-size: 1.05rem;
    color: var(--muted);
}}
{root} .t7-card {{
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 40px;
    box-shadow: var(--shadow);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}
{root} .t7-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 48px 0 rgba(31, 38, 135, 0.12);
}}
{root} .t7-btn-primary {{
    display: inline-block;
    background: var(--primary);
    color: #fff;
    padding: 14px 32px;
    font-weight: 600;
    border-radius: 50px;
    text-decoration: none;
    transition: opacity 0.2s, background 0.2s;
    font-size: 0.95rem;
    letter-spacing: 0.05em;
}}
{root} .t7-btn-primary:hover {{
    background: var(--secondary);
    opacity: 0.9;
}}
@media (max-width: 768px) {{
    {root} .t7-wrap {{ padding: 60px 20px; }}
    {root} .t7-card {{ padding: 25px; }}
}}
"""
