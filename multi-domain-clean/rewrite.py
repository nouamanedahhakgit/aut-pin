"""Single function: rewrite article content to generate B, C, D."""
import os
import re
import json
import logging
import openai
from config import get_openai_client

log = logging.getLogger(__name__)

PROMPT_ARTICLE_A_PATH = os.path.join(os.path.dirname(__file__), "prompts", "generate-article-a.txt")
PROMPT_IMAGE_PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "prompts", "generate-image-prompts.txt")


def _read_prompt_image_prompts() -> str:
    """Read prompt for generating image prompts (prompt + prompt_image_ingredients) from recipe title."""
    if not os.path.exists(PROMPT_IMAGE_PROMPTS_PATH):
        return ""
    with open(PROMPT_IMAGE_PROMPTS_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def generate_image_prompts_for_title(title: str, user_config: dict = None, ai_provider: str = None, openai_model: str = None, openrouter_model: str = None, local_model: str = None, llamacpp_model_id=None) -> dict:
    """Generate prompt and prompt_image_ingredients for a recipe title via LLM. Returns {prompt, prompt_image_ingredients} or {error}.
    When user_config and ai_provider are provided, uses user's API keys and model. Otherwise uses config.get_openai_client()."""
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
        elif p == "local":
            url = (user_config.get("local_api_url") or "http://localhost:11434").rstrip("/")
            if "/v1" not in url and "/api" not in url:
                url = url + "/v1"
            client = openai.OpenAI(base_url=url, api_key="ollama")
            ai_model = local_model or (user_config.get("local_models") or "qwen3:8b").split(",")[0].strip()
        elif p == "llamacpp":
            try:
                import requests
                mgr = user_config.get("llamacpp_manager_url") or "http://localhost:8080"
                mid = llamacpp_model_id or user_config.get("llamacpp_model_id")
                if not mid:
                    r = requests.get(f"{mgr.rstrip('/')}/api/models", timeout=5)
                    models = (r.json() or {}).get("models") or []
                    if not models:
                        return {"error": "No llama.cpp model available"}
                    mid = models[0].get("id") or models[0]
                r = requests.post(f"{mgr.rstrip('/')}/api/chat", json={"model_id": mid, "messages": [
                    {"role": "system", "content": _read_prompt_image_prompts() or "Generate two Midjourney prompts for a recipe. Return JSON: {\"prompt\": \"...\", \"prompt_image_ingredients\": \"...\"}"},
                    {"role": "user", "content": f"Recipe title: {title or 'Recipe'}"}
                ]}, timeout=120)
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
                return {"prompt": prompt, "prompt_image_ingredients": prompt_ing}
            except Exception as e:
                return {"error": str(e)}
    if client is None:
        try:
            client, ai_model = get_openai_client(ai_provider or None)
        except ValueError as e:
            return {"error": str(e)}
    sys_prompt = _read_prompt_image_prompts() or """Generate two Midjourney prompts for a recipe. Return JSON: {"prompt": "main dish photo... --v 6.1", "prompt_image_ingredients": "ingredients flat lay... --v 6.1"}"""
    user_msg = f"Recipe title: {title or 'Recipe'}"
    try:
        log.info("[generate_image_prompts] Calling %s for: %s", (ai_model or "LLM"), (title or "Recipe")[:50])
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.5,
            max_tokens=500,
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
        return {"prompt": prompt, "prompt_image_ingredients": prompt_ing}
    except Exception as e:
        return {"error": str(e)}


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


def generate_article_content_for_a(title: str, prompt_text: str = "") -> dict:
    """Generate article_content for Domain A via OpenAI using external prompt. Returns A.4-style fields in one call."""
    try:
        client, ai_model = get_openai_client()
    except ValueError as e:
        return {"error": str(e)}
    system_prompt = _read_prompt_article_a()
    user_payload = f"Recipe title: {title or 'Recipe'}"
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
