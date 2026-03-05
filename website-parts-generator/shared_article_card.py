"""
Load article card from template (article_card_1, article_card_2, etc.).
Index, category, and sidebar use: render_cards(articles, config, show_excerpt, scope_prefix)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "templates"


def _load_article_card_template(name: str):
    """Load article card template module by name (e.g. article_card_1)."""
    clean = name.replace("-", "_").strip().lower()
    if not clean.startswith("article_card_"):
        clean = "article_card_" + clean.lstrip("article_card").lstrip("_-")
    path = TEMPLATES_DIR / "article_cards" / f"{clean}.py"
    if not path.exists():
        path = TEMPLATES_DIR / "article_cards" / "article_card_1.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location(clean, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load article card template: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def render_cards(articles: list, config: dict, show_excerpt: bool = True, scope_prefix: str = "") -> tuple:
    """
    Render article cards using the domain's article_card_template.
    Returns (cards_html, card_css).
    config must have article_card_template (e.g. "article_card_1") and style/colors.
    """
    from shared_style import extract_style

    template_name = (config.get("article_card_template") or "article_card_1").strip() or "article_card_1"
    mod = _load_article_card_template(template_name)
    s = extract_style(config)

    card_cfg = dict(config)
    card_cfg["style"] = s
    card_cfg["show_excerpt"] = show_excerpt
    card_cfg["scope_prefix"] = scope_prefix

    cards_html = []
    card_css = ""
    for article in articles:
        card_cfg["article"] = article
        out = mod.generate(card_cfg)
        cards_html.append(out.get("html", ""))
        if not card_css and out.get("css"):
            card_css = out["css"]
    return "".join(cards_html), card_css
