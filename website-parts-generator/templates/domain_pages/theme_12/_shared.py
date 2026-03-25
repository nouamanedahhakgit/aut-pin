"""Shared helpers for Theme 12 — Candy Pop.
Design language: Bubblegum pink (#FF85A1) primary, sky blue (#89CFF0) secondary,
mint green (#A7F3D0) accent, lavender (#C4B5FD) highlights. Nunito display font,
Quicksand body. Super rounded corners (20px-32px), bouncy hover animations,
blob decorations, multi-color pastel accents, playful emoji badges. Fun. Joyful. Bold.
"""

from shared_style import extract_style, part_font

THEME = 12


def theme_base(config: dict) -> dict:
    """Return common theme values for theme 12."""
    s = extract_style(config)
    pf = part_font("domain_page", config)
    cdn_url = (pf.get("cdn") or "").strip()
    font_import = f"@import url('{cdn_url}');" if cdn_url else ""
    font_family = pf.get("family") or "Nunito, sans-serif"
    body_font = s.get("body_family", "Quicksand, sans-serif")

    css_vars = f"""
    --primary:   {s.get("primary",    "#FF85A1")};
    --secondary: {s.get("secondary",  "#89CFF0")};
    --accent:    {s.get("accent",     "#A7F3D0")};
    --lavender:  #C4B5FD;
    --yellow:    #FDE68A;
    --bg:        {s.get("background", "#FFFFFF")};
    --surface:   #FFF5F7;
    --surface2:  #FFF0F3;
    --pink-pale: rgba(255,133,161,0.1);
    --pink-border: rgba(255,133,161,0.3);
    --blue-pale: rgba(137,207,240,0.15);
    --text:      {s.get("text_primary",   "#2D1F3D")};
    --muted:     {s.get("text_secondary", "#7B6B8A")};
    --border:    {s.get("border",         "#F0E4F6")};
    --shadow-sm: 0 2px 12px rgba(45,31,61,0.06);
    --shadow:    0 6px 28px rgba(45,31,61,0.10);
    --shadow-lg: 0 16px 56px rgba(45,31,61,0.14);
    --radius:    20px;
    --radius-lg: 28px;
    --radius-xl: 36px;
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
@keyframes t12-bounce-in {
  0%   { opacity: 0; transform: translateY(30px) scale(0.95); }
  60%  { transform: translateY(-5px) scale(1.02); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes t12-float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-8px); }
}
@keyframes t12-blob-morph {
  0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
  50%       { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
}
@keyframes t12-rainbow {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
"""


def hero_css(font_family: str) -> str:
    """Shared Candy Pop hero section CSS for theme 12."""
    return f"""
{KEYFRAMES}
.dp-t12-hero {{
    background: linear-gradient(145deg, var(--surface2) 0%, var(--blue-pale) 50%, var(--surface) 100%);
    text-align: center; padding: 4.5rem 1.5rem 3.5rem;
    position: relative; overflow: hidden;
    border-bottom: 4px solid transparent;
    border-image: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent), var(--lavender), var(--primary)) 1;
}}
.dp-t12-hero-blob1, .dp-t12-hero-blob2 {{
    position: absolute; pointer-events: none; opacity: 0.15;
    animation: t12-blob-morph 8s ease-in-out infinite;
}}
.dp-t12-hero-blob1 {{
    width: 300px; height: 300px; top: -80px; right: -60px;
    background: var(--primary); border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
}}
.dp-t12-hero-blob2 {{
    width: 200px; height: 200px; bottom: -40px; left: -40px;
    background: var(--secondary); border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%;
    animation-delay: -4s;
}}
.dp-t12-hero-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--pink-pale); border: 2px solid var(--pink-border);
    color: var(--primary); padding: 6px 18px; border-radius: 50px;
    font-size: 0.78rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.12em; margin-bottom: 1rem;
    animation: t12-float 3s ease-in-out infinite;
}}
.dp-t12-hero h1 {{
    font-family: {font_family}; font-size: clamp(2rem, 5.5vw, 3.5rem);
    font-weight: 900; margin: 0 0 0.75rem; color: var(--text);
    line-height: 1.15; letter-spacing: -0.01em;
    animation: t12-bounce-in 0.8s ease both;
}}
.dp-t12-hero h1 em {{
    font-style: normal;
    background: linear-gradient(135deg, var(--primary), var(--secondary), var(--lavender));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.dp-t12-hero p {{
    max-width: 540px; margin: 0 auto; color: var(--muted);
    font-size: 1.05rem; line-height: 1.7; font-weight: 500;
}}
@media (max-width: 600px) {{ .dp-t12-hero h1 {{ font-size: 1.85rem; }} .dp-t12-hero {{ padding: 3rem 1rem 2.5rem; }} }}
"""


def body_css(font_family: str) -> str:
    """Shared Candy Pop body/section CSS for theme 12."""
    return f"""
.dp-t12-body {{ max-width: 840px; margin: 0 auto; padding: 3rem 1.5rem 5rem; animation: t12-bounce-in 0.6s ease both; }}
.dp-t12-section {{ margin-bottom: 2.75rem; }}
.dp-t12-h2 {{
    font-family: {font_family}; font-size: 1.45rem; font-weight: 800;
    color: var(--text); margin: 0 0 0.85rem;
    display: flex; align-items: center; gap: 10px;
}}
.dp-t12-h2::before {{
    content: ''; display: inline-block; width: 8px; height: 8px;
    background: var(--primary); border-radius: 50%; flex-shrink: 0;
    box-shadow: 12px 0 0 var(--secondary), 24px 0 0 var(--accent);
}}
.dp-t12-section p  {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin: 0 0 0.7rem; font-weight: 500; }}
.dp-t12-section li {{ color: var(--muted); font-size: 0.95rem; line-height: 1.85; margin-bottom: 0.45rem; font-weight: 500; }}
.dp-t12-section ul {{ padding-left: 1.3rem; }}
.dp-t12-section strong {{ color: var(--text); font-weight: 700; }}
"""
