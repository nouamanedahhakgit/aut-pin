"""
Shared font utilities for all article generators.
Use these so fonts from config (e.g. Article Template Editor) load correctly.
Import: from generators.font_utils import font_name_for_import, font_family_css, build_font_import_url
"""


def font_name_for_import(family: str) -> str:
    """Extract plain font name for Google Fonts URL.
    e.g. 'Great Vibes' or \"'Bebas Neue', sans-serif\" -> Bebas Neue
    """
    if not family or not isinstance(family, str):
        return ""
    s = family.strip().strip("'\"").split(",")[0].strip().strip("'\"")
    return s if s else "Inter"


def font_family_css(family: str, fallback: str = "sans-serif") -> str:
    """Normalize font-family for CSS. Avoid double-quoting when value already includes comma."""
    if not family or not isinstance(family, str):
        return f"'{fallback}'"
    s = family.strip()
    if "," in s and (s.startswith("'") or s.startswith('"')):
        return s  # Already properly quoted
    if "," in s:
        return s  # e.g. "Arial, sans-serif"
    return f"'{s}', {fallback}"


def build_font_import_url(fonts_config: dict) -> str:
    """Build Google Fonts @import URL from config fonts.heading and fonts.body.
    Returns full URL string (without @import url('')).
    """
    f = fonts_config or {}
    hfam = (f.get("heading") or {}).get("family") or "Playfair Display"
    bfam = (f.get("body") or {}).get("family") or "Inter"
    hname = font_name_for_import(hfam)
    bname = font_name_for_import(bfam)
    font_weights = {}
    if hname:
        font_weights[hname] = "400;600;700"
    if bname:
        existing = font_weights.get(bname, "")
        font_weights[bname] = "400;500;600;700" if existing else "400;500;600"
    if not font_weights:
        font_weights = {"Playfair Display": "400;600;700", "Inter": "400;500;600"}
    parts = [f"family={n.replace(' ', '+')}:wght@{w}" for n, w in font_weights.items()]
    return "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"
