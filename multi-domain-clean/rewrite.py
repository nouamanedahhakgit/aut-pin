"""Single function: rewrite article content to generate B, C, D."""
import os
import re
import json
import logging
import openai
from config import get_openai_client
from keyutil import parse_groq_api_keys
from prompt_config import (
    apply_prompt_placeholders,
    build_recipe_user_message,
    recipe_system_fallback,
)

log = logging.getLogger(__name__)

PROMPT_ARTICLE_A_PATH = os.path.join(os.path.dirname(__file__), "prompts", "generate-article-a.txt")
PROMPT_IMAGE_PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "prompts", "generate-image-prompts.txt")


def _read_prompt_image_prompts() -> str:
    """Read prompt for generating image prompts (prompt + prompt_image_ingredients) from recipe title."""
    if not os.path.exists(PROMPT_IMAGE_PROMPTS_PATH):
        return ""
    with open(PROMPT_IMAGE_PROMPTS_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _effective_recipe_system(ai_prompts: dict = None) -> str:
    if ai_prompts and (ai_prompts.get("recipe_system") or "").strip():
        return (ai_prompts.get("recipe_system") or "").strip()
    return _read_prompt_image_prompts() or recipe_system_fallback()


def _normalize_categories_list(cats) -> list:
    """Normalize categories to a list of strings. Accepts ['a','b'] or [{'categorie':'a'}, ...]."""
    if not cats:
        return []
    out = []
    for c in (cats if isinstance(cats, list) else [cats]):
        if isinstance(c, dict):
            out.append(str(c.get("categorie") or c.get("name") or c.get("category") or "").strip())
        else:
            out.append(str(c).strip())
    return [x for x in out if x]


# Course values that indicate a beverage (drink board only for these)
_BEVERAGE_COURSES = frozenset({"beverages", "beverage", "drinks", "drink"})
# Course values that are clearly NOT beverages — never put these in "drink" board
_NON_BEVERAGE_COURSES = frozenset({
    "desserts", "dessert", "main course", "main courses", "appetizers", "appetizer",
    "soups", "soup", "salads", "salad", "snacks", "snack", "breakfast", "sides", "side",
    "main", "entree", "entrees", "lunch", "dinner"
})
_BEVERAGE_KEYWORDS = re.compile(
    r"\b(smoothie|smoothies|cocktail|juice|tea|coffee|lemonade|mocktail|milkshake|"
    r"latte|cappuccino|soda|punch|infusion|tonic)\b",
    re.IGNORECASE
)


def _is_likely_beverage(recipe_val: dict, title: str) -> bool:
    """True if recipe is clearly a beverage (for drink board). Else False so we can avoid putting dishes in drink."""
    if not recipe_val and not title:
        return False
    title_lower = (title or "").lower()
    course = ""
    if isinstance(recipe_val, dict):
        course = str(recipe_val.get("course") or "").strip().lower()
        summary = str(recipe_val.get("summary") or "").lower()
    else:
        summary = ""
    # Explicit: desserts, main courses, etc. are never beverages
    if course and course in _NON_BEVERAGE_COURSES:
        return False
    if course and course in _BEVERAGE_COURSES:
        return True
    text = f"{title_lower} {summary}"
    return bool(_BEVERAGE_KEYWORDS.search(text))


def _fix_drink_board_mismatch(board_slug: str, recipe_val: dict, title: str, boards: list) -> str:
    """If AI returned 'drink' but recipe is not a beverage, return the non-drink board with smallest count."""
    if not board_slug or board_slug != "drink" or not boards:
        return board_slug
    if _is_likely_beverage(recipe_val, title):
        return board_slug
    non_drink = [b for b in boards if b.get("slug") and str(b.get("slug", "")).strip().lower() != "drink"]
    if not non_drink:
        return board_slug
    best = min(non_drink, key=lambda b: int(b.get("count") or 0))
    fixed = str(best.get("slug", "")).strip()
    if fixed:
        log.info("[generate_image_prompts] Override board: recipe is not a beverage, using %s instead of drink", fixed)
        return fixed
    return board_slug


def generate_image_prompts_for_title(title: str, categories_list: list = None, user_config: dict = None, ai_provider: str = None, openai_model: str = None, openrouter_model: str = None, groq_model: str = None, local_model: str = None, llamacpp_model_id=None, pinterest_boards: list = None, ai_prompts: dict = None) -> dict:
    """Generate prompt, prompt_image_ingredients, recipe, course, and optionally board_slug for a recipe title via LLM.
    categories_list: domain's categories (strings or {categorie:...}). AI picks the best matching one.
    pinterest_boards: optional list of {name, slug, count} for RSS board assignment; AI picks one slug (prefer smallest count).
    Returns {prompt, prompt_image_ingredients, recipe, course, board_slug?} or {error}."""
    client = None
    ai_model = None
    if user_config and ai_provider:
        p = (ai_provider or "").strip().lower()
        if p == "openrouter":
            key = user_config.get("openrouter_api_key")
            if not key:
                return {"error": "OpenRouter API key not configured"}
            client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
            ai_model = openrouter_model or user_config.get("openrouter_model") or "openai/gpt-4o-mini"
        elif p == "openai":
            key = user_config.get("openai_api_key")
            if not key:
                return {"error": "OpenAI API key not configured"}
            client = openai.OpenAI(api_key=key)
            ai_model = openai_model or user_config.get("openai_model") or "gpt-4o-mini"
        elif p == "groq":
            gq_keys = user_config.get("groq_api_keys")
            if not isinstance(gq_keys, list) or not gq_keys:
                gq_keys = parse_groq_api_keys(user_config.get("groq_api_key"))
            if not gq_keys:
                return {"error": "Groq API key not configured"}
            ai_model = groq_model or user_config.get("groq_model") or "llama-3.3-70b-versatile"
            base_i = abs(hash(title or "")) % len(gq_keys)
            last_err = None
            max_tries = min(3, len(gq_keys))
            for t in range(max_tries):
                key = gq_keys[(base_i + t) % len(gq_keys)]
                try:
                    client = openai.OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
                    sys_prompt = _effective_recipe_system(ai_prompts)
                    user_msg = build_recipe_user_message(title, categories_list, pinterest_boards, ai_prompts)
                    boards = pinterest_boards or []
                    cats = _normalize_categories_list(categories_list or [])
                    log.info("[generate_image_prompts] Calling groq for: %s (key %s/%s)", (title or "Recipe")[:50], t + 1, max_tries)
                    resp = client.chat.completions.create(
                        model=ai_model,
                        messages=[
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": user_msg},
                        ],
                        temperature=0.5,
                        max_tokens=2500,
                        timeout=120.0,
                    )
                    raw = resp.choices[0].message.content or ""
                    result = _extract_json(raw)
                    prompt = str(result.get("prompt", "") or "").strip()
                    prompt_ing = str(result.get("prompt_image_ingredients", "") or "").strip()
                    if not prompt or len(prompt) < 25:
                        prompt = f"Professional food photography of {title or 'Recipe'}, overhead shot, natural lighting, editorial style --v 6.1"
                    if not prompt_ing or len(prompt_ing) < 25:
                        prompt_ing = f"Flat-lay of ingredients for {title or 'Recipe'}, white surface, natural light, editorial style --v 6.1"
                    recipe_val = result.get("recipe")
                    course_val = str(result.get("course") or (recipe_val.get("course") if isinstance(recipe_val, dict) else "") or "").strip()
                    if isinstance(recipe_val, dict) and course_val and not recipe_val.get("course"):
                        recipe_val["course"] = course_val
                    elif not course_val and isinstance(recipe_val, dict) and recipe_val.get("course"):
                        course_val = str(recipe_val["course"] or "").strip()
                    if not course_val and cats:
                        course_val = cats[0] if cats else ""
                    recipe_str = json.dumps(recipe_val, ensure_ascii=False) if isinstance(recipe_val, dict) else ""
                    out = {"prompt": prompt, "prompt_image_ingredients": prompt_ing, "recipe": recipe_str, "course": course_val}
                    valid_slugs = {str(b.get("slug", "")).strip() for b in boards if b.get("slug")}
                    board_slug = str(result.get("board_slug") or "").strip()
                    if board_slug and board_slug in valid_slugs:
                        board_slug = _fix_drink_board_mismatch(board_slug, recipe_val, title, boards)
                        out["board_slug"] = board_slug
                    return out
                except Exception as e:
                    last_err = e
                    log.warning("[generate_image_prompts] Groq attempt %s/%s failed: %s", t + 1, max_tries, e)
                    continue
            return {"error": str(last_err) if last_err else "Groq generation failed after key retries"}
        elif p == "local":
            url = (user_config.get("local_api_url") or "http://localhost:11434").rstrip("/")
            if "/v1" not in url and "/api" not in url:
                url = url + "/v1"
            client = openai.OpenAI(base_url=url, api_key="ollama")
            ai_model = local_model or (user_config.get("local_models") or "qwen3:8b").split(",")[0].strip()
        elif p == "llamacpp":
            try:
                import requests
                mgr = user_config.get("llamacpp_manager_url") or "http://localhost:5004"
                mid = llamacpp_model_id or user_config.get("llamacpp_model_id")
                if not mid:
                    r = requests.get(f"{mgr.rstrip('/')}/api/models", timeout=5)
                    models = (r.json() or {}).get("models") or []
                    if not models:
                        return {"error": "No llama.cpp model available"}
                    mid = models[0].get("id") or models[0]
                user_content = build_recipe_user_message(title, categories_list, pinterest_boards, ai_prompts)
                boards = pinterest_boards or []
                cats = _normalize_categories_list(categories_list or [])
                r = requests.post(f"{mgr.rstrip('/')}/api/chat", json={"model_id": mid, "messages": [
                    {"role": "system", "content": _effective_recipe_system(ai_prompts)},
                    {"role": "user", "content": user_content}
                ]}, timeout=180)
                data = r.json() or {}
                raw = (data.get("message") or data.get("content") or "").strip()
                if not raw:
                    return {"error": "Empty response from llama.cpp"}
                result = _extract_json(raw)
                prompt = str(result.get("prompt", "") or "").strip()
                prompt_ing = str(result.get("prompt_image_ingredients", "") or "").strip()
                if not prompt or len(prompt) < 25:
                    prompt = f"Professional food photography of {title or 'Recipe'}, overhead shot, natural lighting, editorial style --v 6.1"
                if not prompt_ing or len(prompt_ing) < 25:
                    prompt_ing = f"Flat-lay of ingredients for {title or 'Recipe'}, white surface, natural light, editorial style --v 6.1"
                recipe_val = result.get("recipe")
                course_val = str(result.get("course") or (recipe_val.get("course") if isinstance(recipe_val, dict) else "") or "").strip()
                if isinstance(recipe_val, dict) and course_val and not recipe_val.get("course"):
                    recipe_val["course"] = course_val
                elif not course_val and isinstance(recipe_val, dict) and recipe_val.get("course"):
                    course_val = str(recipe_val["course"] or "").strip()
                if not course_val and cats:
                    course_val = cats[0] if cats else ""
                recipe_str = json.dumps(recipe_val, ensure_ascii=False) if isinstance(recipe_val, dict) else ""
                out = {"prompt": prompt, "prompt_image_ingredients": prompt_ing, "recipe": recipe_str, "course": course_val}
                valid_slugs = {str(b.get("slug", "")).strip() for b in boards if b.get("slug")}
                board_slug = str(result.get("board_slug") or "").strip()
                if board_slug and board_slug in valid_slugs:
                    board_slug = _fix_drink_board_mismatch(board_slug, recipe_val, title, boards)
                    out["board_slug"] = board_slug
                return out
            except Exception as e:
                return {"error": str(e)}
    if client is None:
        try:
            client, ai_model = get_openai_client(ai_provider or None)
        except ValueError as e:
            return {"error": str(e)}
    sys_prompt = _effective_recipe_system(ai_prompts)
    user_msg = build_recipe_user_message(title, categories_list, pinterest_boards, ai_prompts)
    boards = pinterest_boards or []
    cats = _normalize_categories_list(categories_list or [])
    try:
        log.info("[generate_image_prompts] Calling %s for: %s", (ai_model or "LLM"), (title or "Recipe")[:50])
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.5,
            max_tokens=2500,
            timeout=120.0,
        )
        log.info("[generate_image_prompts] Done for: %s", (title or "Recipe")[:50])
        raw = resp.choices[0].message.content or ""
        result = _extract_json(raw)
        prompt = str(result.get("prompt", "") or "").strip()
        prompt_ing = str(result.get("prompt_image_ingredients", "") or "").strip()
        if not prompt or len(prompt) < 25:
            prompt = f"Professional food photography of {title or 'Recipe'}, overhead shot, natural lighting, editorial style --v 6.1"
        if not prompt_ing or len(prompt_ing) < 25:
            prompt_ing = f"Flat-lay of ingredients for {title or 'Recipe'}, white surface, natural light, editorial style --v 6.1"
        recipe_val = result.get("recipe")
        course_val = str(result.get("course") or (recipe_val.get("course") if isinstance(recipe_val, dict) else "") or "").strip()
        if isinstance(recipe_val, dict) and course_val and not recipe_val.get("course"):
            recipe_val["course"] = course_val
        elif not course_val and isinstance(recipe_val, dict) and recipe_val.get("course"):
            course_val = str(recipe_val["course"] or "").strip()
        if not course_val and cats:
            course_val = cats[0] if cats else ""
        recipe_str = json.dumps(recipe_val, ensure_ascii=False) if isinstance(recipe_val, dict) else ""
        out = {"prompt": prompt, "prompt_image_ingredients": prompt_ing, "recipe": recipe_str, "course": course_val}
        valid_slugs = {str(b.get("slug", "")).strip() for b in boards if b.get("slug")}
        board_slug = str(result.get("board_slug") or "").strip()
        if board_slug and board_slug in valid_slugs:
            board_slug = _fix_drink_board_mismatch(board_slug, recipe_val, title, boards)
            out["board_slug"] = board_slug
        return out
    except Exception as e:
        err = str(e)
        # OpenRouter returns 401 with message "User not found" for invalid/revoked API keys (not "user" of this app).
        if "401" in err and ("user not found" in err.lower() or "'code': 401" in err):
            err = (
                "OpenRouter rejected the API key (401). That message means the key is invalid, revoked, or not from "
                "https://openrouter.ai/keys — not your app login. Create a new key there, paste it in Profile → "
                "OpenRouter Key (no 'Bearer' prefix), Save, and retry."
            )
        return {"error": err}


def _read_prompt_article_a() -> str:
    """Read external prompt for Generate (A). Edit prompts/generate-article-a.txt to customize."""
    if not os.path.exists(PROMPT_ARTICLE_A_PATH):
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_ARTICLE_A_PATH}")
    with open(PROMPT_ARTICLE_A_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _extract_json(content: str) -> dict:
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


def rewrite(article: str) -> dict:
    """
    Rewrite an article to produce B, C, D outputs.
    B = rewritten/summarized title
    C = keywords or tags
    D = meta description
    """
    if not article or not article.strip():
        return {"B": "", "C": "", "D": ""}

    try:
        client, ai_model = get_openai_client()
    except ValueError as e:
        return {"B": "", "C": "", "D": "", "error": str(e)}

    prompt = f"""Given this article text, return exactly three outputs:
- B: A rewritten or improved title (1 line)
- C: Comma-separated keywords or tags (1 line)
- D: Meta description for SEO, max 160 chars (1 line)

Article:
{article[:8000]}

Respond in this exact format:
B: [title]
C: [keywords]
D: [meta description]"""

    try:
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        text = resp.choices[0].message.content.strip()
        result = {"B": "", "C": "", "D": ""}
        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith("B:"):
                result["B"] = line[2:].strip()
            elif line.upper().startswith("C:"):
                result["C"] = line[2:].strip()
            elif line.upper().startswith("D:"):
                result["D"] = line[2:].strip()
        return result
    except Exception as e:
        return {"B": "", "C": "", "D": "", "error": str(e)}


def rewrite_recipe(recipe: str) -> str:
    """Rewrite recipe JSON for variation (Domain B/C/D). Same structure, different wording."""
    if not recipe or not str(recipe).strip():
        return recipe or ""
    try:
        client, ai_model = get_openai_client()
    except ValueError as e:
        log.warning(f"[rewrite_recipe] {e}")
        return ""
    try:
        data = json.loads(recipe) if isinstance(recipe, str) else recipe
    except Exception as e:
        log.warning("[rewrite_recipe] recipe not valid JSON: %s", e)
        return recipe or ""
    prompt = f"""Rewrite this recipe JSON. Keep the exact same structure and keys. Use different wording for summary, description, instructions, ingredient descriptions. Same quantities and logic. Return ONLY valid JSON, no other text.

Recipe:
{json.dumps(data, ensure_ascii=False)[:8000]}"""
    try:
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        raw = resp.choices[0].message.content or ""
        result = _extract_json(raw)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        log.warning("[rewrite_recipe] LLM error: %s", e)
        return recipe or ""


def _extract_html_from_llm_response(raw: str) -> str:
    """If LLM added preamble (e.g. 'Here is...'), extract just the HTML part."""
    s = (raw or "").strip()
    if not s:
        return ""
    # Prefer content starting with <!DOCTYPE or <html
    for start in ("<!DOCTYPE", "<!doctype", "<html", "<HTML"):
        idx = s.find(start)
        if idx >= 0:
            return s[idx:].strip()
    # If it looks like HTML already, use as-is
    if s.lstrip().startswith("<"):
        return s.strip()
    return s


def rewrite_article_body(article: str) -> str:
    """Rewrite article body text for variation (Domain B/C/D). Uses recipe-based article HTML."""
    if not article or not article.strip():
        return ""
    try:
        client, ai_model = get_openai_client()
    except ValueError as e:
        log.warning(f"[rewrite_article_body] {e}")
        return ""
    prompt = f"""Rewrite this article HTML. Keep the exact same HTML structure, tags, and layout. Change only the text content (paragraphs, headings text, list items) to use different wording and phrasing. Preserve all HTML tags, class names, and attributes. Output ONLY the rewritten HTML document, no markdown, no explanation, no preamble.

Article:
{article[:12000]}"""
    try:
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        raw = resp.choices[0].message.content or ""
        out = _extract_html_from_llm_response(raw)
        log.info("[rewrite_article_body] response len=%s extracted len=%s", len(raw), len(out))
        return out
    except Exception as e:
        log.warning("[rewrite_article_body] LLM error: %s", e)
        return ""


def generate_article_content_for_a(title: str, prompt_text: str = "", ai_prompts: dict = None) -> dict:
    """Generate article_content for Domain A via OpenAI using external prompt. Returns A.4-style fields in one call."""
    try:
        client, ai_model = get_openai_client()
    except ValueError as e:
        return {"error": str(e)}
    system_prompt = _read_prompt_article_a()
    if ai_prompts and (ai_prompts.get("article_system") or "").strip():
        system_prompt = (ai_prompts.get("article_system") or "").strip()
    user_payload = f"Recipe title: {title or 'Recipe'}"
    if ai_prompts and (ai_prompts.get("article_user") or "").strip():
        user_payload = apply_prompt_placeholders(
            (ai_prompts.get("article_user") or "").strip(),
            {"title": title or "Recipe", "prompt_text": prompt_text or ""},
        )
    elif prompt_text:
        user_payload += f"\n\nAdditional context: {prompt_text}"
    try:
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_payload},
            ],
            temperature=0.6,
            max_tokens=16000,
        )
        raw = resp.choices[0].message.content or ""
        result = _extract_json(raw)
        article = result.get("article", result.get("article_markdown", "")) or ""
        content_val = result.get("content")
        if isinstance(content_val, dict) and "blocks" in content_val:
            content_str = json.dumps(content_val, ensure_ascii=False)
        elif isinstance(content_val, str):
            content_str = content_val
        else:
            content_str = json.dumps({"blocks": []}, ensure_ascii=False)
        recipe_val = result.get("recipe", "")
        if isinstance(recipe_val, dict):
            recipe_val = json.dumps(recipe_val, ensure_ascii=False)
        # prompt and prompt_image_ingredients are generated separately (generate-prompts step), never by article generation
        return {
            "article": article,
            "content": content_str,
            "recipe": str(recipe_val or ""),
            "prompt": "",
            "prompt_image_ingredients": "",
            "recipe_title_pin": str(result.get("recipe_title_pin", "") or ""),
            "pinterest_title": str(result.get("pinterest_title", "") or ""),
            "pinterest_description": str(result.get("pinterest_description", "") or ""),
            "pinterest_keywords": str(result.get("pinterest_keywords", "") or ""),
            "focus_keyphrase": str(result.get("focus_keyphrase", "") or ""),
            "meta_description": str(result.get("meta_description", "") or ""),
            "keyphrase_synonyms": str(result.get("keyphrase_synonyms", "") or ""),
        }
    except Exception as e:
        return {"error": str(e)}
