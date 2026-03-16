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


def _pos_css(pos):
    """Convert position dict (top, left, bottom, right) to CSS string."""
    out = []
    for k in ("top", "left", "bottom", "right"):
        if k in pos:
            v = pos[k]
            if isinstance(v, (int, float)):
                out.append(f"{k}:{v}px;")
            else:
                out.append(f"{k}:{v};")
    return " ".join(out)


def _handle_complex_prop(name, val):
    """Convert dict-based properties like border or shadow to CSS string."""
    if name == "rotation":
        deg = val if isinstance(val, (int, float, str)) else val.get("rotation", 0)
        return f"rotate({deg}deg)"
    
    if name == "backdrop_blur":
        if isinstance(val, (int, float)): return f"blur({val}px)"
        return str(val)

    if not isinstance(val, dict):
        return str(val)
    
    if name == "border":
        w = val.get("width", val.get("border_width", 1))
        if isinstance(w, int): w = f"{w}px"
        return f"{w} {val.get('style', 'solid')} {val.get('color', val.get('border_color', '#000'))}"
    
    if name == "transform":
        if "rotation" in val:
            deg = val.get("rotation", 0)
            return f"rotate({deg}deg)"
        return str(val)
    
    if name in ("shadow", "box_shadow", "text_shadow"):
        # Map gpt-4o's shadow keys to standard CSS
        ox = val.get("offset_x", val.get("x", 2))
        oy = val.get("offset_y", val.get("y", 2))
        blur = val.get("blur", val.get("blur_radius", 4))
        color = val.get("color", "rgba(0,0,0,0.3)")
        if isinstance(ox, int): ox = f"{ox}px"
        if isinstance(oy, int): oy = f"{oy}px"
        if isinstance(blur, int): blur = f"{blur}px"
        return f"{ox} {oy} {blur} {color}"
    
    return str(val)


def build_css(tpl):
    """Generate CSS from template dict. Adds overflow:hidden to all text elements."""
    c = tpl["canvas"]
    lines = [
        f"/* {tpl['name']} */",
        "* { margin: 0; padding: 0; box-sizing: border-box; }",
        ".pin-container { width: %dpx; height: %dpx; position: relative; overflow: hidden; background: %s; font-family: Arial,sans-serif; }" % (
            c["width"], c["height"], c.get("background_color", "transparent")
        ),
        "",
        "/* Images */"
    ]
    for ik, idata in tpl.get("images", {}).items():
        pos = idata.get("position", {})
        pos_str = _pos_css(pos) or "top:0px; left:0px;"
        w, h, z = idata["width"], idata["height"], idata.get("layer_order", 1)
        cls = ik.replace("_", "-")
        fit = idata.get("object_fit", "cover")
        s = f".{cls} {{ position:absolute; {pos_str} width:{w}px; height:{h}px; object-fit:{fit}; z-index:{z}; }}"
        for prop in ("border_radius", "border", "clip_path", "opacity", "box_shadow", "filter", "background"):
            if idata.get(prop) is not None:
                css_prop = prop.replace("_", "-")
                val = _handle_complex_prop(prop, idata[prop])
                if prop == "border_radius" and isinstance(idata[prop], (int, float)):
                    val = f"{val}px"
                s = s.rstrip("; }") + f"; {css_prop}:{val}; }}"
        lines.append(s)

    lines.extend(["", "/* Elements */"])
    for ek, ed in tpl.get("elements", {}).items():
        pos = ed.get("position", {})
        pos_str = _pos_css(pos) or "top:0px; left:0px;"
        z = ed.get("z_index", 10)
        cls = ek.replace("_", "-")
        etype = (ed.get("type") or "div").lower()

        if etype in ("div", "box", "shape"):
            styles = f"position:absolute; {pos_str} width:{ed.get('width', 100)}px; height:{ed.get('height', 100)}px; z-index:{z};"
            # Support both 'background_color' and 'color' (for shapes)
            bg = ed.get("background_color") or ed.get("background") or ed.get("color")
            if bg:
                styles += f" background:{_handle_complex_prop('background', bg)};"

            for prop in ("border", "border_radius", "padding", "clip_path", "box_shadow", "opacity", "filter", "backdrop_filter", "backdrop_blur", "transform", "rotation"):
                if ed.get(prop) is not None:
                    css_prop = prop.replace("_", "-")
                    if prop == "rotation": css_prop = "transform"
                    if prop == "backdrop_blur": css_prop = "backdrop-filter"
                    val = _handle_complex_prop(prop, ed[prop])
                    if prop == "border_radius" and isinstance(ed[prop], (int, float)):
                        val = f"{val}px"
                    styles += f" {css_prop}:{val};"
            lines.append(f".{cls} {{ {styles} }}")

        elif etype in ("text", "shape_text"):
            align = ed.get("text_align", "center")
            flex_align = "center"
            flex_justify = "center"
            if align == "left":
                flex_align = "flex-start"
                flex_justify = "center"
            elif align == "right":
                flex_align = "flex-end"
                flex_justify = "center"
            
            # Note: For column layout, align-items is horizontal alignment.
            styles = (
                f"position:absolute; {pos_str} "
                f"width:{ed.get('width', 200)}px; height:{ed.get('height', 100)}px; "
                f"font-family:{ed.get('font_family', 'Arial')}; font-size:{ed.get('font_size', 24)}px; "
                f"font-weight:{ed.get('font_weight', 'normal')}; color:{ed.get('color', '#000')}; "
                f"text-align:{align}; "
                f"display:flex; align-items:{flex_align}; justify-content:{flex_justify}; flex-direction:column; "
                f"overflow:hidden; word-break:break-word; "
                f"z-index:{z};"
            )
            # Handle shadow specifically for text
            sh = ed.get("shadow") or ed.get("text_shadow")
            if sh:
                styles += f" text-shadow:{_handle_complex_prop('text_shadow', sh)};"

            for k in (
                "font_style", "text_transform", "letter_spacing", "line_height",
                "background", "background_color", "border", "border_radius",
                "padding", "white_space", "opacity", "transform", "rotation",
                "backdrop_filter", "backdrop_blur", "box_shadow"
            ):
                if k in ed and ed[k] is not None:
                    v = _handle_complex_prop(k, ed[k])
                    css_k = k.replace("_", "-")
                    if k == "rotation": css_k = "transform"
                    if k == "backdrop_blur": css_k = "backdrop-filter"
                    
                    if k == "line_height" and isinstance(ed[k], (int, float)):
                        styles += f" {css_k}:{v};"
                    elif k in ("border_radius", "letter_spacing", "padding") and isinstance(ed[k], (int, float)):
                        styles += f" {css_k}:{v}px;"
                    else:
                        styles += f" {css_k}:{v};"
            lines.append(f".{cls} {{ {styles} }}")

        elif etype == "stars":
            sz = ed.get("star_size", ed.get("size", 24))
            lines.append(f".{cls} {{ position:absolute; {pos_str} display:flex; gap:{ed.get('spacing', 4)}px; z-index:{z}; }}")
            lines.append(f".{cls} svg {{ width:{sz}px; height:{sz}px; }}")

        elif etype == "icon":
            lines.append(f".{cls} {{ position:absolute; {pos_str} z-index:{z}; }}")

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
        etype = (ed.get("type") or "div").lower()
        if etype in ("div", "box", "shape"):
            body.append(f'<div class="{cls}"></div>')
        elif etype in ("text", "shape_text"):
            body.append(f'<div class="{cls}">{ed.get("text", "")}</div>')
        elif ed["type"] == "stars":
            sz = ed.get("star_size", ed.get("size", 24))
            body.append(f'<div class="{cls}">{"".join([star_svg(ed.get("color", "yellow"), sz)] * ed["count"])}</div>')
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
            if not elem_name in elements:
                continue
            for css_prop, color_key in prop_map.items():
                resolved = color_map.get(color_key)
                if resolved:
                    elements[elem_name][css_prop] = resolved

    heading = df.get("heading_family", "").strip()
    body_fam = df.get("body_family", "").strip()
    if font_slots and (heading or body_fam):
        for elem_name, role in font_slots.items():
            if not elem_name in elements:
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
    image_urls = {}
    for ik, idata in tpl.get("images", {}).items():
        # Priority 1: Top-level override (like from API body)
        if ik in template_data and isinstance(template_data[ik], str):
            image_urls[ik] = template_data[ik]
        # Priority 2: Hardcoded src/url in images dict
        elif "src" in idata:
            image_urls[ik] = idata["src"]
        elif "url" in idata:
            image_urls[ik] = idata["url"]
    
    out_dir = os.path.join(output_dir, template_id)
    os.makedirs(out_dir, exist_ok=True)
    css = build_css(tpl)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_html(tpl, image_urls, css))
    with open(os.path.join(out_dir, "images_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(build_manifest(template_id, tpl, image_urls), f, indent=2)
    print(f"Generated: {template_id} -> {out_dir} (index.html, images_manifest.json)")
