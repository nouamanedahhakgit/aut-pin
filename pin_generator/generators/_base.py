"""
Shared base for all pin template generators.

Provides:
- render_pin(template_id, template_data): builds HTML, CSS, manifest, writes files
- apply_domain_style(template_data, domain_colors, domain_fonts): injects domain colors/fonts
- All shared helpers: _css, _html, _manifest, _fonts, _star_svg, _search_icon, etc.

Each template_N.py only needs: TEMPLATE_ID, TEMPLATE_DATA, STYLE_SLOTS, FONT_SLOTS, run()
"""
import os
import json
import copy

DEFAULT_CANVAS = {"width": 600, "height": 1067, "aspect_ratio": "9:16"}

GOOGLE_FONTS = {
    "pacifico": "https://fonts.googleapis.com/css2?family=Pacifico&display=swap",
    "dancing_script": "https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap",
    "great_vibes": "https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap",
    "bebas_neue": "https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap",
    "oswald": "https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap",
    "playfair_display": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&display=swap",
    "inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap",
    "lora": "https://fonts.googleapis.com/css2?family=Lora:wght@400;700&display=swap",
    "merriweather": "https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&display=swap",
    "source_serif_4": "https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;700;900&display=swap",
    "dm_sans": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap",
    "open_sans": "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap",
    "lato": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap",
    "fraunces": "https://fonts.googleapis.com/css2?family=Fraunces:wght@400;700;900&display=swap",
    "work_sans": "https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;600;700;800&display=swap",
    "pt_sans": "https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&display=swap",
    "source_sans_3": "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap",
    "montserrat": "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap",
    "raleway": "https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700;800&display=swap",
    "poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap",
    "abril_fatface": "https://fonts.googleapis.com/css2?family=Abril+Fatface&display=swap",
}

FONT_MAP = {}
for _key in GOOGLE_FONTS:
    FONT_MAP[_key] = _key
    FONT_MAP[_key.replace("_", " ")] = _key


def _font_to_key(family_str):
    """Convert a CSS font-family string to a GOOGLE_FONTS key."""
    f = (family_str or "").lower().replace("'", "").replace('"', "").strip()
    for kw, key in FONT_MAP.items():
        if kw in f:
            return key
    return None


def collect_font_links(elements):
    """Return list of <link> tags for Google Fonts used by text elements."""
    out = set()
    for d in elements.values():
        if d.get("type") != "text":
            continue
        key = _font_to_key(d.get("font_family", ""))
        if key and key in GOOGLE_FONTS:
            out.add(f'<link href="{GOOGLE_FONTS[key]}" rel="stylesheet">')
    return list(out)


def star_svg(color, size):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}" '
        f'xmlns="http://www.w3.org/2000/svg"><path d="M12 2l3.09 6.26L22 9.27l-5 '
        f'4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'
    )


def search_icon(size, color):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>'
    )


def build_css(tpl):
    """Generate CSS from template dict. Adds overflow:hidden to all text elements."""
    c = tpl["canvas"]
    lines = [
        f"/* {tpl['name']} */",
        "* { margin: 0; padding: 0; box-sizing: border-box; }",
        ".pin-container { width: %dpx; height: %dpx; position: relative; overflow: hidden; background: #000; font-family: Arial,sans-serif; }" % (c["width"], c["height"]),
        "",
        "/* Images */"
    ]
    for ik, idata in tpl.get("images", {}).items():
        pos = idata["position"]
        w, h, z = idata["width"], idata["height"], idata.get("layer_order", 1)
        cls = ik.replace("_", "-")
        s = f".{cls} {{ position:absolute; top:{pos['top']}px; left:{pos['left']}px; width:{w}px; height:{h}px; object-fit:cover; z-index:{z}; }}"
        if idata.get("border_radius"):
            s = s.rstrip("; }") + f"; border-radius:{idata['border_radius']}; }}"
        if idata.get("border"):
            s = s.rstrip("; }") + f"; border:{idata['border']}; }}"
        lines.append(s)

    lines.extend(["", "/* Elements */"])
    for ek, ed in tpl.get("elements", {}).items():
        pos = ed["position"]
        z = ed.get("z_index", 10)
        cls = ek.replace("_", "-")

        if ed["type"] == "div":
            styles = f"position:absolute; top:{pos['top']}px; left:{pos['left']}px; width:{ed['width']}px; height:{ed['height']}px; z-index:{z};"
            for prop in ("background_color", "border", "border_radius", "padding"):
                if ed.get(prop):
                    css_prop = prop.replace("_", "-")
                    val = ed[prop]
                    if prop == "border_radius" and isinstance(val, (int, float)):
                        val = f"{val}px"
                    styles += f" {css_prop}:{val};"
            if ed.get("opacity") is not None:
                styles += f" opacity:{ed['opacity']};"
            lines.append(f".{cls} {{ {styles} }}")

        elif ed["type"] == "text":
            styles = (
                f"position:absolute; top:{pos['top']}px; left:{pos['left']}px; "
                f"width:{ed['width']}px; height:{ed['height']}px; "
                f"font-family:{ed['font_family']}; font-size:{ed['font_size']}px; "
                f"font-weight:{ed['font_weight']}; color:{ed['color']}; "
                f"text-align:{ed.get('text_align', 'center')}; "
                f"display:flex; align-items:center; justify-content:center; flex-direction:column; "
                f"overflow:hidden; word-break:break-word; "
                f"z-index:{z};"
            )
            for k in (
                "font_style", "text_transform", "letter_spacing", "line_height",
                "text_shadow", "background", "background_color", "border",
                "border_radius", "padding", "white_space", "opacity",
            ):
                if k in ed and ed[k] is not None:
                    v = ed[k]
                    css_k = k.replace("_", "-")
                    if k == "line_height" or isinstance(v, str):
                        styles += f" {css_k}:{v};"
                    else:
                        styles += f" {css_k}:{v}px;"
            lines.append(f".{cls} {{ {styles} }}")

        elif ed["type"] == "stars":
            lines.append(f".{cls} {{ position:absolute; top:{pos['top']}px; left:{pos['left']}px; display:flex; gap:4px; z-index:{z}; }}")
            lines.append(f".{cls} svg {{ width:{ed['star_size']}px; height:{ed['star_size']}px; }}")

        elif ed["type"] == "icon":
            lines.append(f".{cls} {{ position:absolute; top:{pos['top']}px; left:{pos['left']}px; z-index:{z}; }}")

    return "\n".join(lines)


def build_html(tpl, image_urls, css):
    """Generate full HTML page from template dict."""
    elements = tpl.get("elements", {})
    head = [
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>{tpl["name"]} - Pin</title>',
    ] + collect_font_links(elements) + [f'<style>\n{css}\n</style>']

    body = ['<div class="pin-container">']
    for ik, _idata in sorted(tpl.get("images", {}).items(), key=lambda x: x[1].get("layer_order", 0)):
        cls = ik.replace("_", "-")
        body.append(f'<img class="{cls}" src="{image_urls.get(ik) or ""}" alt="{ik.replace("_", " ").title()}">')
    for ek, ed in sorted(elements.items(), key=lambda x: x[1].get("z_index", 0)):
        cls = ek.replace("_", "-")
        if ed["type"] == "div":
            body.append(f'<div class="{cls}"></div>')
        elif ed["type"] == "text":
            body.append(f'<div class="{cls}">{ed.get("text", "")}</div>')
        elif ed["type"] == "stars":
            body.append(f'<div class="{cls}">{"".join([star_svg(ed["color"], ed["star_size"])] * ed["count"])}</div>')
        elif ed["type"] == "icon" and ed.get("icon") == "search":
            body.append(f'<div class="{cls}">{search_icon(ed["size"], ed["color"])}</div>')
    body.append("</div>")

    return "<!DOCTYPE html><html><head>\n  " + "\n  ".join(head) + "\n</head><body>\n  " + "\n  ".join(body) + "\n</body></html>"


def build_manifest(template_id, tpl, image_urls):
    out = {"template_id": template_id, "template_name": tpl["name"], "images": {}}
    for ik, idata in tpl.get("images", {}).items():
        out["images"][ik] = {
            "url": image_urls.get(ik) or "",
            "description_prompt": idata.get("description_prompt", ""),
            "position": idata["position"],
            "width": idata["width"],
            "height": idata["height"],
            "layer_order": idata.get("layer_order", 1),
        }
    return out


def template_from_data(data):
    return {
        "name": data.get("name", "Template"),
        "canvas": data.get("canvas", copy.deepcopy(DEFAULT_CANVAS)),
        "images": data.get("images", {}),
        "elements": data.get("elements", {}),
    }


def apply_overrides(tpl, data):
    """Apply body overrides (from API request) into the template."""
    el = tpl.get("elements", {})
    if "title" in data and "title" in el:
        el["title"]["text"] = data["title"]
    if "subtitle" in data and "subtitle" in el:
        el["subtitle"]["text"] = data["subtitle"]
    if "time_badge" in data and "time_badge" in el:
        el["time_badge"]["text"] = data["time_badge"]
    if "domain" in data:
        for k, v in el.items():
            if v.get("type") == "text" and ("website" in k or k == "domain"):
                v["text"] = data["domain"]
    for k, cfg in (data.get("elements") or {}).items():
        if k not in el or not isinstance(cfg, dict):
            continue
        e = el[k]
        if "position" in cfg and isinstance(cfg["position"], dict) and e.get("position"):
            if "top" in cfg["position"]:
                e["position"]["top"] = cfg["position"]["top"]
            if "left" in cfg["position"]:
                e["position"]["left"] = cfg["position"]["left"]
        if e.get("type") == "text" and "text" in cfg:
            e["text"] = cfg["text"]
        if "font_size" in cfg:
            e["font_size"] = cfg["font_size"]
        for sk in ("color", "background_color", "background", "border", "border_radius",
                    "padding", "text_shadow", "font_family", "opacity"):
            if sk in cfg:
                e[sk] = cfg[sk]
    if "name" in data:
        tpl["name"] = data["name"]


def apply_domain_style(template_data, style_slots, font_slots, domain_colors=None, domain_fonts=None):
    """
    Apply domain colors and fonts to template_data using style_slots and font_slots maps.

    style_slots: maps element_name -> {css_property: color_key} where color_key is from domain_colors
        e.g. {"overlay_band": {"background_color": "primary"}, "title": {"color": "on_primary"}, "badge": {"border": "border_accent"}}

    font_slots: maps element_name -> font_role ("heading" or "body")
        e.g. {"title": "heading", "subtitle": "heading", "website": "body"}

    domain_colors: {"primary": "#FF7849", "secondary": "#9C6ADE", "background": "#FFF", "text_primary": "#2D2D2D", ...}
    domain_fonts: {"heading_family": "Playfair Display", "body_family": "Inter", ...}

    Special color keys:
        "primary", "secondary", "background", "text_primary", "text_secondary", "border"
        "on_primary" -> #FFFFFF (white text on primary bg)
        "on_secondary" -> #FFFFFF
        "on_dark" -> #FFFFFF
        "accent_gold" -> derived from primary (warm gold accent)
        "border_accent" -> "2px solid {primary}"
    """
    if not domain_colors and not domain_fonts:
        return

    dc = domain_colors or {}
    df = domain_fonts or {}
    elements = template_data.get("elements") or {}

    color_map = {
        "primary": dc.get("primary"),
        "secondary": dc.get("secondary"),
        "background": dc.get("background"),
        "text_primary": dc.get("text_primary"),
        "text_secondary": dc.get("text_secondary"),
        "border": dc.get("border"),
        "on_primary": "#FFFFFF",
        "on_secondary": "#FFFFFF",
        "on_dark": "#FFFFFF",
    }
    if dc.get("primary"):
        color_map["border_accent"] = f"2px solid {dc['primary']}"
        color_map["border_accent_3"] = f"3px solid {dc['primary']}"

    if style_slots and dc:
        for elem_name, prop_map in style_slots.items():
            if elem_name not in elements:
                continue
            for css_prop, color_key in prop_map.items():
                resolved = color_map.get(color_key)
                if resolved:
                    elements[elem_name][css_prop] = resolved

    heading = df.get("heading_family", "").strip()
    body_fam = df.get("body_family", "").strip()
    if font_slots and (heading or body_fam):
        for elem_name, role in font_slots.items():
            if elem_name not in elements:
                continue
            el = elements[elem_name]
            if el.get("type") != "text":
                continue
            if role == "heading" and heading:
                el["font_family"] = f"'{heading}', serif" if " " in heading else f"{heading}, serif"
            elif role == "body" and body_fam:
                el["font_family"] = f"'{body_fam}', sans-serif" if " " in body_fam else f"{body_fam}, sans-serif"


def render_pin(template_id, template_data, output_dir=None):
    """Full render pipeline: build template, apply overrides, write HTML + manifest."""
    output_dir = output_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
    )
    tpl = template_from_data(template_data)
    apply_overrides(tpl, template_data)
    image_urls = {
        k: v for k, v in template_data.items()
        if k in tpl.get("images", {}) and isinstance(v, str)
    }
    out_dir = os.path.join(output_dir, template_id)
    os.makedirs(out_dir, exist_ok=True)
    css = build_css(tpl)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_html(tpl, image_urls, css))
    with open(os.path.join(out_dir, "images_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(build_manifest(template_id, tpl, image_urls), f, indent=2)
    print(f"Generated: {template_id} -> {out_dir} (index.html, images_manifest.json)")
