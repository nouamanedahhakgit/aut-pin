"""
Generic article preview for any generator.
Used when a generator does not implement run_preview().
Works with CONFIG structure: colors, fonts, layout, components.
Add new generators as generator-N.py – they auto-work with preview.
"""


def _get(cfg: dict, *keys, default=""):
    """Safe nested get with default."""
    for k in keys:
        if cfg is None or not isinstance(cfg, dict):
            return default
        cfg = cfg.get(k)
    return cfg if cfg is not None else default


def generic_article_preview(config: dict) -> dict:
    """
    Generate article HTML+CSS from any CONFIG (colors, fonts, layout, components).
    Adaptable: works with generators that have standard CONFIG structure.
    """
    title = _get(config, "title") or "Sample Recipe"
    c = config.get("colors") or {}
    f = config.get("fonts") or {}
    l = config.get("layout") or {}
    comp = config.get("components") or {}
    primary = _get(c, "primary", default="#6C8AE4")
    secondary = _get(c, "secondary", default="#9C6ADE")
    background = _get(c, "background", default="#FFFFFF")
    text_primary = _get(c, "text_primary", default="#2D2D2D")
    text_secondary = _get(c, "text_secondary", default="#5A5A5A")
    button_print = _get(c, "button_print", default="#1A1A2E")
    button_pin = _get(c, "button_pin", default="#E60023")
    border = _get(c, "border", default="#E2E8FF")
    from generators.font_utils import font_family_css, build_font_import_url
    heading_family = _get(f, "heading", "family") or "Playfair Display"
    body_family = _get(f, "body", "family") or "Inter"
    import_url = build_font_import_url(f)
    body_font_css = font_family_css(body_family, "sans-serif")
    heading_font_css = font_family_css(heading_family, "serif")
    h2_size = _get(f, "heading", "sizes", "h2") or "1.875rem"
    body_size = _get(f, "body", "size") or "1rem"
    line_height = _get(f, "body", "line_height") or "1.7"
    max_width = _get(l, "max_width", default="800px")
    section_spacing = _get(l, "section_spacing", default="3rem")
    container_padding = _get(l, "container_padding", default="2rem")
    border_radius = _get(l, "border_radius", default="12px")
    box_shadow = _get(l, "box_shadow", default="0 4px 20px rgba(0,0,0,0.08)")
    pro_bg = _get(comp, "pro_tips_box", "bg_color", default="#FFF5F0")
    pro_border = _get(comp, "pro_tips_box", "border_color", default="#FFE8E0")
    pro_left = _get(comp, "pro_tips_box", "border_left", default="4px solid #F4A261")
    pro_padding = _get(comp, "pro_tips_box", "padding", default="2rem")
    recipe_bg = _get(comp, "recipe_card", "bg", default="#FFFCFA") or _get(comp, "recipe_card", "bg_color", default="#FFFCFA")
    recipe_border = _get(comp, "recipe_card", "border", default="2px solid #FFE8E0")
    recipe_radius = _get(comp, "recipe_card", "border_radius", default="16px")
    recipe_padding = _get(comp, "recipe_card", "padding", default="2rem")

    css = f"""@import url('{import_url}');
:root {{--primary: {primary};--secondary: {secondary};--background: {background};--text-primary: {text_primary};--text-secondary: {text_secondary};--button-print: {button_print};--button-pin: {button_pin};--border: {border};}}
* {{margin:0;padding:0;box-sizing:border-box;}}
body {{font-family: {body_font_css};font-size: {body_size};line-height: {line_height};color: {text_primary};background: {background};}}
.article-container {{max-width: {max_width};margin: 0 auto;padding: {container_padding};}}
h1,h2,h3 {{font-family: {heading_font_css};font-weight: 600;}}
h2 {{color: {primary};font-size: {h2_size};margin-top: {section_spacing};}}
.pro-tips-box {{background: {pro_bg};border: 1px solid {pro_border};border-left: {pro_left};border-radius: {border_radius};padding: {pro_padding};margin: {section_spacing} 0;}}
.pro-tip-item {{display: flex;gap: 1rem;margin-bottom: 1rem;}}
.pro-tip-number {{width: 32px;height: 32px;background: {primary};color: white;border-radius: 50%;display: flex;align-items: center;justify-content: center;font-weight: 600;flex-shrink: 0;}}
.ingredients-list {{list-style: none;padding: 0;}}
.ingredients-list li {{display: flex;gap: 0.75rem;padding: 0.5rem 0;border-bottom: 1px solid {border};}}
.instructions-list {{list-style: none;counter-reset: i;padding: 0;}}
.instructions-list li {{display: flex;gap: 1rem;margin-bottom: 1rem;}}
.instructions-list li::before {{counter-increment: i;content: counter(i);width: 32px;height: 32px;background: {primary};color: white;border-radius: 50%;display: flex;align-items: center;justify-content: center;font-weight: 600;flex-shrink: 0;}}
.recipe-card {{background: {recipe_bg};border: {recipe_border};border-radius: {recipe_radius};padding: {recipe_padding};margin: {section_spacing} 0;box-shadow: {box_shadow};}}
.recipe-card-header {{display: flex;gap: 1.5rem;margin-bottom: 1.5rem;}}
.recipe-card-image {{width: 100px;height: 100px;border-radius: 50%;object-fit: cover;background: #ddd;}}
.recipe-meta {{display: flex;gap: 2rem;margin-bottom: 1.5rem;flex-wrap: wrap;}}
.recipe-meta-item {{display: flex;gap: 0.4rem;align-items: center;}}
.recipe-meta-item .value {{font-weight: 600;color: {primary};}}
.recipe-buttons {{display: flex;gap: 1rem;margin-bottom: 2rem;}}
.btn {{flex: 1;padding: 1rem;border: none;border-radius: 8px;font-weight: 600;cursor: pointer;display: flex;align-items: center;justify-content: center;gap: 0.5rem;}}
.btn-print {{background: var(--button-print);color: white;}}
.btn-pin {{background: var(--button-pin);color: white;}}
.recipe-columns {{display: grid;grid-template-columns: 1fr 1fr;gap: 3rem;}}
@media (max-width: 768px) {{.recipe-columns {{grid-template-columns: 1fr;}}}}
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} Recipe</title>
<link rel="stylesheet" href="css.css">
</head>
<body>
<article class="article-container">
<img src="placeholder.jpg" alt="{title}" class="recipe-card-image" style="width:100%;height:auto;border-radius:{border_radius};margin-bottom:{section_spacing};">
<p class="intro">Sample preview for <strong>{title}</strong>. Your colors, fonts, and layout from CONFIG are applied. Add a <code>run_preview()</code> method for custom structure.</p>
<div class="pro-tips-box"><h2>Why I Love This Recipe</h2>
<div class="pro-tip-item"><span class="pro-tip-number">1</span><p>Delicious flavor combination.</p></div>
<div class="pro-tip-item"><span class="pro-tip-number">2</span><p>Easy to make with simple ingredients.</p></div>
<div class="pro-tip-item"><span class="pro-tip-number">3</span><p>Perfect for any occasion.</p></div>
<div class="pro-tip-item"><span class="pro-tip-number">4</span><p>Great for meal prep.</p></div>
</div>
<h2>Ingredients</h2>
<ul class="ingredients-list">
<li><input type="checkbox" id="i1"><label for="i1">2 cups flour</label></li>
<li><input type="checkbox" id="i2"><label for="i2">1 cup sugar</label></li>
<li><input type="checkbox" id="i3"><label for="i3">1/2 cup butter</label></li>
<li><input type="checkbox" id="i4"><label for="i4">2 eggs</label></li>
</ul>
<h2>Instructions</h2>
<ol class="instructions-list">
<li>Preheat oven and prep the pan.</li>
<li>Mix wet ingredients.</li>
<li>Combine dry ingredients.</li>
<li>Bake and cool.</li>
</ol>
<div class="recipe-card">
<div class="recipe-card-header">
<img src="placeholder.jpg" alt="{title}" class="recipe-card-image">
<div><h2>{title}</h2><p>Delicious homemade recipe.</p></div>
</div>
<div class="recipe-meta">
<div class="recipe-meta-item"><span>⏱</span><span class="value">15 min</span> prep</div>
<div class="recipe-meta-item"><span>🍳</span><span class="value">30 min</span> cook</div>
<div class="recipe-meta-item"><span>👥</span><span class="value">8</span> servings</div>
</div>
<div class="recipe-buttons">
<button class="btn btn-print">Print Recipe</button>
<button class="btn btn-pin" onclick="window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&media='+encodeURIComponent((document.querySelector('[data-pin-image]')||{{}}).dataset?.pinImage||document.querySelector('.main-article-image img,.recipe-card-image img,article img')?.src||'')+'&description='+encodeURIComponent(document.title),'pinterest','width=750,height=600')">Pin Recipe</button>
</div>
<div class="recipe-columns">
<div><h3>Ingredients</h3><ul class="ingredients-list"><li>Flour</li><li>Sugar</li><li>Butter</li></ul></div>
<div><h3>Steps</h3><ol class="instructions-list"><li>Mix</li><li>Bake</li><li>Serve</li></ol></div>
</div>
</div>
</article>
</body>
</html>"""

    slug = title.lower().replace(" ", "-").replace("'", "").replace('"', "")[:50]
    return {"title": title, "slug": slug, "article_html": html, "article_css": css}
