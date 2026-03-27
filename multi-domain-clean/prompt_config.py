"""Merged AI prompt defaults (files) + profile JSON + group overrides. Supports {{placeholder}} substitution."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_ai_prompts_json(raw: Any) -> Dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return {}
        try:
            out = json.loads(s)
            return out if isinstance(out, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def apply_prompt_placeholders(template: str, context: Optional[Dict[str, Any]]) -> str:
    """Replace {{key}} with str(context[key]). Dict/list values are JSON-encoded."""
    if not template or not isinstance(template, str):
        return template or ""
    out = template
    for k, v in (context or {}).items():
        key = "{{" + str(k) + "}}"
        if v is None:
            rep = ""
        elif isinstance(v, (dict, list)):
            rep = json.dumps(v, ensure_ascii=False)
        else:
            rep = str(v)
        out = out.replace(key, rep)
    return out


def merge_prompt_layers(defaults: Optional[Dict], profile: Optional[Dict], group: Optional[Dict]) -> Dict[str, Any]:
    """Later layers override earlier. pin_field_prompts dicts are shallow-merged (child keys win)."""
    out: Dict[str, Any] = dict(defaults or {})
    for layer in (profile or {}, group or {}):
        if not isinstance(layer, dict):
            continue
        for k, v in layer.items():
            if v is None:
                continue
            if k == "pin_field_prompts" and isinstance(v, dict):
                base = out.get("pin_field_prompts")
                if isinstance(base, dict):
                    merged = dict(base)
                    merged.update(v)
                    out["pin_field_prompts"] = merged
                else:
                    out["pin_field_prompts"] = dict(v)
                continue
            if isinstance(v, str) and not v.strip():
                continue
            out[k] = v
    return out


def load_builtin_defaults() -> Dict[str, Any]:
    """Defaults from repo files (same as before per-user customization)."""
    out: Dict[str, Any] = {}
    recipe_path = os.path.join(_PKG_DIR, "prompts", "generate-image-prompts.txt")
    if os.path.isfile(recipe_path):
        try:
            with open(recipe_path, "r", encoding="utf-8") as f:
                txt = f.read().strip()
            if txt:
                out["recipe_system"] = txt
        except OSError:
            pass
    article_path = os.path.join(_PKG_DIR, "prompts", "generate-article-a.txt")
    if os.path.isfile(article_path):
        try:
            with open(article_path, "r", encoding="utf-8") as f:
                txt = f.read().strip()
            if txt:
                out["article_system"] = txt
        except OSError:
            pass
    pin_path = os.path.join(_PKG_DIR, "pin_generation_prompts.json")
    if os.path.isfile(pin_path):
        try:
            with open(pin_path, "r", encoding="utf-8") as f:
                pj = json.load(f)
            if isinstance(pj, dict):
                if pj.get("prompt"):
                    out["pin_prompt"] = pj["prompt"]
                if pj.get("field_prompts") is not None and isinstance(pj.get("field_prompts"), dict):
                    out["pin_field_prompts"] = pj["field_prompts"]
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return out


def normalize_categories_list(cats) -> list:
    if not cats:
        return []
    out = []
    for c in (cats if isinstance(cats, list) else [cats]):
        if isinstance(c, dict):
            out.append(str(c.get("categorie") or c.get("name") or c.get("category") or "").strip())
        else:
            out.append(str(c).strip())
    return [x for x in out if x]


def build_recipe_user_message(
    title: str,
    categories_list,
    pinterest_boards: Optional[list],
    ai_prompts: Optional[Dict[str, Any]],
) -> str:
    """User message for recipe / image-prompt generation. Uses recipe_user template or built-in layout."""
    cats = normalize_categories_list(categories_list or [])
    cats_str = json.dumps(cats, ensure_ascii=False) if cats else "[]"
    boards = pinterest_boards or []
    boards_payload = []
    for b in boards:
        if isinstance(b, dict) and b.get("slug"):
            boards_payload.append({"name": b.get("name"), "slug": b.get("slug"), "count": b.get("count", 0)})
    boards_str = json.dumps(boards_payload, ensure_ascii=False) if boards_payload else "[]"
    tmpl = (ai_prompts or {}).get("recipe_user") if ai_prompts else None
    if tmpl and str(tmpl).strip():
        return apply_prompt_placeholders(
            str(tmpl).strip(),
            {
                "title": title or "Recipe",
                "categories_json": cats_str,
                "boards_json": boards_str,
            },
        )
    msg = f"Recipe title: {title or 'Recipe'}\n\nCATEGORIES: {cats_str}"
    if boards_payload:
        msg += f"\n\nBOARDS: {boards_str}"
    return msg


def recipe_system_fallback() -> str:
    """Hardcoded fallback when no file and no DB prompt."""
    return (
        'Generate image prompts, recipe, and category. Return JSON: '
        '{"prompt": "...", "prompt_image_ingredients": "...", "recipe": {...}, "course": "..."}'
    )
