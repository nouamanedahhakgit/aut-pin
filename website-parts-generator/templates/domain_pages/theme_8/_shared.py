"""Shared helpers for Theme 8 — Aurora Borealis Dark.
Design language: Deep obsidian backgrounds, vivid aurora-gradient accents
(violet → cyan → emerald), animated mesh glow, neon edges, and premium
glassmorphism panels. Every page feels like looking at the night sky.
"""

from shared_style import extract_style, part_font

THEME = 8


def theme_base(config: dict) -> dict:
    s = extract_style(config)
    pf = part_font("domain_page", config)
    cdn_url = (pf.get("cdn") or "").strip()
    font_import = f"@import url('{cdn_url}');" if cdn_url else ""
    font_family = pf.get("family") or "Outfit, sans-serif"
    body_font = s.get("body_family", "Inter, sans-serif")

    css_vars = f"""
    --primary:   {s.get("primary",    "#7C3AED")};
    --secondary: {s.get("secondary",  "#06B6D4")};
    --accent:    {s.get("accent",     "#10B981")};
    --bg:        {s.get("background", "#080B14")};
    --surface:   #0F1624;
    --surface2:  #141D2E;
    --text:      {s.get("text_primary",   "#E2E8F0")};
    --muted:     {s.get("text_secondary", "#94A3B8")};
    --border:    rgba(124, 58, 237, 0.25);
    --glass-bg:  rgba(15, 22, 36, 0.75);
    --glass-blur: blur(18px);
    --shadow:    0 8px 40px rgba(124, 58, 237, 0.18);
    --shadow-lg: 0 24px 80px rgba(6, 182, 212, 0.12);
    --radius:    16px;
    --radius-lg: 24px;
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


# ── Keyframes (injected once per page) ──────────────────────────────────────
KEYFRAMES = """
@keyframes t8-aurora-shift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes t8-glow-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50%       { opacity: 1;   transform: scale(1.08); }
}
@keyframes t8-fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
"""


def hero_css(root: str, font_family: str) -> str:
    return f"""
{KEYFRAMES}
{root} .t8-hero {{
    position: relative;
    overflow: hidden;
    padding: 140px 40px 100px;
    text-align: center;
    background: var(--bg);
}}
{root} .t8-hero-mesh {{
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 30%,  rgba(124,58,237,0.35) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 70%,  rgba(6,182,212,0.30) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 55% 10%,  rgba(16,185,129,0.20) 0%, transparent 50%);
    animation: t8-glow-pulse 8s ease-in-out infinite;
    z-index: 0;
}}
{root} .t8-hero-inner {{
    position: relative;
    z-index: 1;
    max-width: 860px;
    margin: 0 auto;
    animation: t8-fade-up 0.8s ease both;
}}
{root} .t8-hero-label {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.25em;
    color: var(--secondary);
    background: rgba(6,182,212,0.12);
    border: 1px solid rgba(6,182,212,0.3);
    padding: 6px 18px;
    border-radius: 50px;
    margin-bottom: 28px;
}}
{root} .t8-hero-title {{
    font-family: {font_family};
    font-size: clamp(2.4rem, 6vw, 4.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 24px;
    background: linear-gradient(135deg, #fff 0%, var(--secondary) 50%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}}
{root} .t8-hero-sub {{
    font-size: 1.15rem;
    color: var(--muted);
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.75;
    font-weight: 300;
}}
@media (max-width: 768px) {{
    {root} .t8-hero {{ padding: 100px 20px 70px; }}
}}
"""


def body_css(root: str, font_family: str) -> str:
    return f"""
{root} .t8-wrap {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 80px 40px;
}}
{root} .t8-section {{
    margin-bottom: 64px;
}}
{root} .t8-section h3 {{
    font-family: {font_family};
    font-weight: 700;
    font-size: 1.6rem;
    color: var(--text);
    margin: 0 0 28px;
    position: relative;
    padding-left: 20px;
}}
{root} .t8-section h3::before {{
    content: "";
    position: absolute;
    left: 0; top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 70%;
    background: linear-gradient(180deg, var(--primary), var(--secondary));
    border-radius: 4px;
}}
{root} .t8-body {{
    font-size: 1rem;
    color: var(--muted);
    line-height: 1.8;
}}
{root} .t8-body p  {{ margin: 0 0 16px; }}
{root} .t8-body ul {{ padding-left: 1.4rem; }}
{root} .t8-body li {{ margin-bottom: 10px; }}
{root} .t8-body strong {{ color: var(--text); font-weight: 600; }}
{root} .t8-body a {{
    color: var(--secondary);
    text-decoration: none;
    border-bottom: 1px solid rgba(6,182,212,0.3);
    transition: border-color 0.2s;
}}
{root} .t8-body a:hover {{ border-color: var(--secondary); }}

{root} .t8-card {{
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 40px;
    box-shadow: var(--shadow);
    transition: transform 0.35s cubic-bezier(0.165,0.84,0.44,1),
                box-shadow 0.35s ease,
                border-color 0.35s ease;
    position: relative;
    overflow: hidden;
}}
{root} .t8-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
    opacity: 0;
    transition: opacity 0.35s ease;
}}
{root} .t8-card:hover {{
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
    border-color: rgba(124,58,237,0.5);
}}
{root} .t8-card:hover::before {{
    opacity: 1;
}}

{root} .t8-btn-primary {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    padding: 14px 32px;
    font-weight: 600;
    font-size: 0.95rem;
    border-radius: 50px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    letter-spacing: 0.04em;
    box-shadow: 0 4px 24px rgba(124,58,237,0.3);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}}
{root} .t8-btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 36px rgba(124,58,237,0.45);
}}

@media (max-width: 768px) {{
    {root} .t8-wrap {{ padding: 50px 20px; }}
    {root} .t8-card  {{ padding: 24px; }}
}}
"""
