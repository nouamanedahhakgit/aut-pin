"""
Website Parts Generator API.
Generates header, footer, category, sidebar templates.
Each part is reskinnable via config (colors, fonts, layout).

Run: uvicorn route:app --host 0.0.0.0 --port 8010
"""
import os
import re
import sys
from pathlib import Path

# Ensure project root is on path for shared_style
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEMPLATES_DIR = ROOT / "templates"
PROMPTS_DIR = ROOT / "prompts"

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import importlib.util
import json
import logging
import traceback
from fastapi import APIRouter, Body, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Website Parts Generator", version="1.0.0")


@app.exception_handler(Exception)
def _catch_all(request: Request, exc: Exception):
    """Log and return full traceback in 500 response for debugging."""
    tb = traceback.format_exc()
    log.error("Template error: %s\n%s", exc, tb)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb.split("\n")[-10:]},
    )
router = APIRouter(tags=["parts"])
log = logging.getLogger(__name__)

FOLDER_MAP = {"header": "headers", "footer": "footers", "category": "categories", "sidebar": "sidebars", "writer": "writers", "index": "indexes", "article_card": "article_cards", "domain_page": "domain_pages"}


def _discover_article_content_prompts() -> list:
    """Scan prompts dir for article_content_*.txt files."""
    path = PROMPTS_DIR
    if not path.exists():
        return []
    names = []
    for f in sorted(path.glob("article_content_*.txt")):
        name = f.stem  # e.g. article_content_1
        if name not in names:
            names.append(name)
    return names


def _discover_templates() -> dict:
    """Scan templates dir for all .py files per part type. Uses website-parts-generator/templates."""
    reg = {"header": [], "footer": [], "category": [], "sidebar": [], "writer": [], "index": [], "article_card": [], "article_content": [], "domain_page": []}
    base = TEMPLATES_DIR
    for part, folder in FOLDER_MAP.items():
        path = base / folder
        if path.exists():
            for f in sorted(path.glob("*.py")):
                name = f.stem
                if name not in reg[part]:
                    reg[part].append(name)
    reg["article_content"] = _discover_article_content_prompts()
    return reg


REGISTRY = None


def _get_registry():
    global REGISTRY
    if REGISTRY is None:
        REGISTRY = _discover_templates()
    return REGISTRY


def _load_module(part_type: str, name: str):
    """Load template module. name can be header-1, header_1, 1, etc. Always loads fresh from disk (no cache)."""
    clean = name.replace("-", "_").strip().lower()
    folder_map = {"header": "headers", "footer": "footers", "category": "categories", "sidebar": "sidebars", "writer": "writers", "index": "indexes", "article_card": "article_cards"}
    folder = folder_map.get(part_type, part_type + "s")
    prefix = part_type + "_"
    if not clean.startswith(prefix):
        clean = prefix + clean.lstrip(part_type).lstrip("_-")
    path = TEMPLATES_DIR / folder / f"{clean}.py"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template {part_type}/{name} not found. Try: {_get_registry().get(part_type, [])}")
    # Remove from cache so we always load fresh (picks up file edits)
    if clean in sys.modules:
        del sys.modules[clean]
    spec = importlib.util.spec_from_file_location(clean, path)
    if spec is None or spec.loader is None:
        raise HTTPException(status_code=500, detail=f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@router.get("/templates")
def list_templates():
    """List all available template names for each part type."""
    return {"templates": _get_registry()}


@router.post("/generate/header/{name}")
def generate_header(name: str, config: dict = Body(default={})):
    """Generate header HTML and CSS. config: colors, fonts, layout, domain_name, domain_url."""
    mod = _load_module("header", name)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


@router.post("/generate/footer/{name}")
def generate_footer(name: str, config: dict = Body(default={})):
    """Generate footer HTML and CSS."""
    mod = _load_module("footer", name)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


@router.post("/generate/category/{name}")
def generate_category(name: str, config: dict = Body(default={})):
    """Generate category page HTML and CSS. config: category_name, articles list, + style."""
    mod = _load_module("category", name)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


@router.post("/generate/sidebar/{name}")
def generate_sidebar(name: str, config: dict = Body(default={})):
    """Generate sidebar HTML and CSS. config: articles, categories, + style."""
    mod = _load_module("sidebar", name)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


@router.post("/generate/writer/{name}")
def generate_writer(name: str, config: dict = Body(default={})):
    """Generate writer/author byline HTML and CSS. config: writer {name, title, bio, avatar}, + style."""
    mod = _load_module("writer", name)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


@router.post("/generate/article_card/{name}")
def generate_article_card(name: str, config: dict = Body(default={})):
    """Generate single article card HTML and CSS. config: article, show_excerpt, scope_prefix, + style."""
    mod = _load_module("article_card", name)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


@router.post("/generate/index/{name}")
def generate_index(name: str, config: dict = Body(default={})):
    """Generate index/home page HTML and CSS. config: domain_name, articles, categories, total, total_pages, current_page, per_page."""
    mod = _load_module("index", name)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


@router.get("/generate/domain_page")
def list_domain_page_templates():
    """List available domain page template names. Kept for backward compat — returns flat list of old-style names."""
    dp_folder = TEMPLATES_DIR / "domain_pages"
    if not dp_folder.exists():
        return {"templates": []}
    names = [f.stem for f in sorted(dp_folder.glob("*.py")) if not f.stem.startswith("_")]
    return {"templates": names}


@router.get("/domain-page-themes")
def list_domain_page_themes():
    """List available domain page themes (folders under templates/domain_pages/).
    Returns {"themes": ["theme_1", "theme_2", ...]}
    """
    dp_folder = TEMPLATES_DIR / "domain_pages"
    if not dp_folder.exists():
        return {"themes": []}
    themes = sorted(
        d.name for d in dp_folder.iterdir()
        if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".")
    )
    return {"themes": themes}


SLUG_TO_FILE = {
    "about-us": "about_us",
    "terms-of-use": "terms_of_use",
    "privacy-policy": "privacy_policy",
    "gdpr-policy": "gdpr_policy",
    "cookie-policy": "cookie_policy",
    "copyright-policy": "copyright_policy",
    "disclaimer": "disclaimer",
    "contact-us": "contact_us",
    "index": "index",
    "category": "category",
    "header": "header",
    "footer": "footer",
    "sidebar": "sidebar",
}


@router.post("/generate/domain_page/{theme}/{slug}")
def generate_domain_page_themed(theme: str, slug: str, config: dict = Body(default={})):
    """Generate a domain page using a theme folder.
    E.g. POST /generate/domain_page/theme_1/about-us
    """
    theme_clean = theme.replace("-", "_").strip().lower()
    file_name = SLUG_TO_FILE.get(slug, slug.replace("-", "_").strip().lower())
    dp_folder = TEMPLATES_DIR / "domain_pages" / theme_clean
    path = dp_folder / f"{file_name}.py"
    if not path.exists():
        themes = [d.name for d in (TEMPLATES_DIR / "domain_pages").iterdir() if d.is_dir() and not d.name.startswith("_")] if (TEMPLATES_DIR / "domain_pages").exists() else []
        raise HTTPException(status_code=404, detail=f"Theme '{theme}' page '{slug}' not found at {path}. Available themes: {themes}")
    mod_name = f"dp_{theme_clean}_{file_name}"
    for stale in [mod_name, "_shared"]:
        if stale in sys.modules:
            del sys.modules[stale]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise HTTPException(status_code=500, detail=f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


@router.post("/generate/domain_page/{name}")
def generate_domain_page(name: str, config: dict = Body(default={})):
    """Generate domain page HTML and CSS (legacy flat templates). config: domain_name, colors, fonts, writers, categories, page_slug, page_title."""
    clean = name.replace("-", "_").strip().lower()
    dp_folder = TEMPLATES_DIR / "domain_pages"
    path = dp_folder / f"{clean}.py"
    if not path.exists():
        available = [f.stem for f in sorted(dp_folder.glob("*.py")) if not f.stem.startswith("_")] if dp_folder.exists() else []
        raise HTTPException(status_code=404, detail=f"Domain page template '{name}' not found. Available: {available}")
    mod_name = f"dp_{clean}"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise HTTPException(status_code=500, detail=f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "generate"):
        raise HTTPException(status_code=500, detail="Template has no generate()")
    out = mod.generate(config)
    return {"success": True, "html": out.get("html", ""), "css": out.get("css", "")}


def _extract_json_from_response(content: str) -> dict:
    """Extract JSON from OpenAI response, handling markdown code blocks."""
    cleaned = (content or "").strip()
    cleaned = re.sub(r"```json\s*", "", cleaned)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", cleaned)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Failed to parse JSON from response: {cleaned[:300]}")


@router.post("/generate/article_content/{name}")
def generate_article_content(name: str, config: dict = Body(default={})):
    """Generate article body HTML and CSS via OpenAI. config: title, recipe, colors, fonts, content. Requires OPENAI_API_KEY."""
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    from openai import OpenAI
    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not set for OpenRouter provider")
        ai_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    else:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set. Article content generation requires OpenAI.")
        ai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        client = OpenAI(api_key=api_key)

    clean = name.replace("-", "_").strip().lower()
    if not clean.startswith("article_content_"):
        clean = "article_content_" + clean.lstrip("article_content").lstrip("_-")
    path = PROMPTS_DIR / f"{clean}.txt"
    if not path.exists():
        available = _get_registry().get("article_content", [])
        raise HTTPException(status_code=404, detail=f"Article content prompt {name} not found. Try: {available}")

    try:
        prompt_text = path.read_text(encoding="utf-8").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot read prompt file: {e}")

    try:
        user_message = json.dumps(config, ensure_ascii=False)
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": user_message},
            ],
            temperature=0.5,
            max_tokens=16000,
        )
        raw = (resp.choices[0].message.content or "").strip()
        result = _extract_json_from_response(raw)
        html_val = result.get("html", "")
        css_val = result.get("css", "")
        if not isinstance(html_val, str):
            html_val = str(html_val or "")
        if not isinstance(css_val, str):
            css_val = str(css_val or "")
        return {"success": True, "html": html_val, "css": css_val}
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Article content generation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
