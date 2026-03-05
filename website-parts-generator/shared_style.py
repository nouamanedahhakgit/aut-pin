"""Shared style helpers for website parts. Reskinnable via colors, fonts, layout."""


def _get(cfg: dict, *keys, default=""):
    """Safe nested get."""
    for k in keys:
        if cfg is None or not isinstance(cfg, dict):
            return default
        cfg = cfg.get(k)
    return cfg if cfg is not None and cfg != "" else default


def extract_style(config: dict) -> dict:
    """Extract style values from config (colors, fonts, layout). Domain article_template_config compatible."""
    c = config.get("colors") or {}
    f = config.get("fonts") or {}
    l = config.get("layout") or {}
    return {
        "primary": _get(c, "primary", default="#6C8AE4"),
        "secondary": _get(c, "secondary", default="#9C6ADE"),
        "background": _get(c, "background", default="#FFFFFF"),
        "text_primary": _get(c, "text_primary", default="#2D2D2D"),
        "text_secondary": _get(c, "text_secondary", default="#5A5A5A"),
        "border": _get(c, "border", default="#E2E8FF"),
        "button_pin": _get(c, "button_pin", default="#E60023"),
        "heading_family": _get(f, "heading", "family") or "Playfair Display",
        "body_family": _get(f, "body", "family") or "Inter",
        "body_size": _get(f, "body", "size") or "1rem",
        "line_height": _get(f, "body", "line_height") or "1.7",
        "max_width": _get(l, "max_width", default="1200px"),
        "border_radius": _get(l, "border_radius", default="12px"),
        "container_padding": _get(l, "container_padding", default="2rem"),
        "domain_name": _get(config, "domain_name", default="Recipe Blog"),
        "domain_url": _get(config, "domain_url", default="/"),
    }


def part_font(part: str, config: dict) -> dict:
    """Get part-specific font (CDN URL and family) from config. Keys: fonts.header.cdn, fonts.header.family."""
    f = config.get("fonts") or {}
    p = f.get(part) or {}
    if isinstance(p, dict):
        return {
            "cdn": (p.get("cdn") or "").strip(),
            "family": (p.get("family") or p.get("font_family") or "").strip(),
        }
    return {"cdn": "", "family": ""}


def css_vars(s: dict) -> str:
    """Build :root CSS variables."""
    return f"""--primary: {s['primary']};--secondary: {s['secondary']};--background: {s['background']};--text-primary: {s['text_primary']};--text-secondary: {s['text_secondary']};--border: {s['border']};--button-pin: {s['button_pin']};--border-radius: {s['border_radius']};--max-width: {s['max_width']};--container-padding: {s['container_padding']};"""
