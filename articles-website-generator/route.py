"""
Route API for article generators.

GET  /generators                    - List available generators
GET  /generators/{name}/config      - Get generator's default CONFIG
POST /generate-article/{name}       - Generate content (payload: CONFIG, response: content.json)

Run: uvicorn route:app --reload
"""
import copy
import json
import logging
import os
import importlib.util
import sys
import traceback
from pathlib import Path

from fastapi import APIRouter, Body, FastAPI, HTTPException

app = FastAPI(title="Article Generator API", version="1.0.0")
router = APIRouter(tags=["generators"])
log = logging.getLogger(__name__)

GENERATORS_DIR = Path(__file__).resolve().parent / "generators"
if str(GENERATORS_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATORS_DIR))

# Import for cost calculation fallback when generator returns usage but not cost
try:
    from ai_client import calculate_cost_from_usage
except ImportError:
    calculate_cost_from_usage = None

# Round-robin OpenRouter models: each GROUP uses a different block of 4 models.
# Group 0 → models 0,1,2,3; Group 1 → models 4,5,6,7; Group 2 → 8,0,1,2; etc.
# Ordered by best quality for SEO/article writing → best value → trending
OPENROUTER_MODELS = [
    # Paid — best for SEO/article quality
    "google/gemini-2.5-pro",
    "anthropic/claude-3.7-sonnet",
    "openai/gpt-4o",
    "deepseek/deepseek-v3.2",
    "google/gemini-2.0-flash",
    "anthropic/claude-3.5-haiku",
    "openai/gpt-4o-mini",
    "deepseek/deepseek-r1",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-large-2411",
    # Free (rate-limited)
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-v3:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen2.5-72b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]
MODELS_PER_GROUP = 4

# For retries we use models spread across the list (not consecutive) to maximize diversity
OPENROUTER_RETRY_OFFSETS = [0, 5, 10]  # attempt 0 -> base_idx+0, attempt 1 -> base_idx+5, attempt 2 -> base_idx+10


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base (override wins). Nested dicts merged recursively."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _load_generator_module(name: str):
    """Load generator module by name (e.g. generator-1, generator-2)."""
    base = name.replace("_", "-")
    if not base.startswith("generator-"):
        base = f"generator-{base}" if not base.startswith("generator") else base
    file_path = GENERATORS_DIR / f"{base}.py"
    if not file_path.exists():
        raise FileNotFoundError(f"Generator '{name}' not found at {file_path}")
    spec = importlib.util.spec_from_file_location(f"gen_{base.replace('-', '_')}", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for generator '{name}'")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _list_generators() -> list[str]:
    """Find generator-*.py files."""
    return sorted(f.stem for f in GENERATORS_DIR.glob("generator-*.py"))


FAILED_CONTENT_PLACEHOLDER = "Content generation failed. Please try again."


def _is_content_failure(content_data: dict) -> bool:
    """True if article content is missing or is the known failure placeholder."""
    if not isinstance(content_data, dict):
        return True
    html = (content_data.get("article_html") or content_data.get("article") or "")
    if not isinstance(html, str):
        html = str(html) if html else ""
    html = html.strip()
    if not html:
        return True
    if FAILED_CONTENT_PLACEHOLDER in html:
        return True
    return False


def _validate_config(config: dict) -> None:
    """Validate required CONFIG fields: title and categories_list."""
    if not config:
        raise ValueError("CONFIG payload is required")
    if "title" not in config or not config["title"]:
        raise ValueError("CONFIG must include 'title'")
    if "categories_list" not in config or not isinstance(config["categories_list"], list):
        raise ValueError("CONFIG must include 'categories_list' (array)")


@router.get("/generators")
def list_generators():
    """List available generator names."""
    return {"generators": _list_generators()}


@router.get("/generators/{generator_name}/config")
def get_generator_config(generator_name: str):
    """Get the default CONFIG for a generator."""
    try:
        module = _load_generator_module(generator_name)
    except (FileNotFoundError, ImportError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    config = getattr(module, "CONFIG", None)
    if config is None:
        raise HTTPException(status_code=500, detail="Generator has no CONFIG")
    return config


@router.post("/generate-article-preview/{generator_name}")
def generate_article_preview(generator_name: str, config: dict = Body(...)):
    """
    Generate article template with placeholder content (no AI).
    For config preview in Article Template Editor.
    Adaptable: uses run_preview() if the generator has it, else generic preview from CONFIG.
    """
    try:
        _validate_config(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        module = _load_generator_module(generator_name)
    except (FileNotFoundError, ImportError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    default_config = getattr(module, "CONFIG", {})
    merged_config = _deep_merge(copy.deepcopy(default_config), config)
    # Inject dummy API keys so generator __init__ doesn't fail during preview
    merged_config["openrouter_api_key"] = "dummy_key_for_preview"
    merged_config["openai_api_key"] = "dummy_key_for_preview"
    module.CONFIG = merged_config

    ArticleGenerator = getattr(module, "ArticleGenerator", None)
    if ArticleGenerator is not None:
        try:
            generator = ArticleGenerator()
            if hasattr(generator, "run_preview"):
                return generator.run_preview()
            
            # If no run_preview, try to use generator's native HTML/CSS generation with dummy data
            if hasattr(generator, "generate_html"):
                intro = "This is a delicious sample recipe that you will absolutely love. It is easy to make and perfect for any occasion."
                why_items = ["It's quick and easy", "Requires minimal ingredients", "Tastes amazing every time"]
                ing_intro = "Gather these simple ingredients to get started."
                ing_list = ["1 cup flour", "2 eggs", "1/2 cup sugar", "1 tsp vanilla", "1/2 tsp salt"]
                steps = [
                    {"heading": "Prep", "title": "Prep", "body": "Preheat your oven and prepare the ingredients."},
                    {"heading": "Mix", "title": "Mix", "body": "Combine all ingredients in a large bowl until smooth."},
                    {"heading": "Bake", "title": "Bake", "body": "Bake for 30 minutes until golden brown."},
                ]
                tips = ["Use room temperature ingredients.", "Don't overmix the batter.", "Measure flour correctly.", "Let it cool completely before slicing."]
                serving = "Serve warm with a scoop of vanilla ice cream."
                conclusion = "We hope you enjoy this recipe as much as we do!"
                faqs = [
                    {"question": "Can I make this ahead of time?", "q": "Can I make this ahead of time?", "answer": "Yes, you can make it up to 2 days in advance.", "a": "Yes, you can make it up to 2 days in advance."},
                    {"question": "Can I freeze it?", "q": "Can I freeze it?", "answer": "Yes, it freezes beautifully for up to 3 months.", "a": "Yes, it freezes beautifully for up to 3 months."}
                ]
                variations = ["Add chocolate chips", "Use gluten-free flour"]
                storage = "Store in an airtight container for up to 3 days."
                recipe = {
                    "name": getattr(generator, "title", "Sample Recipe"),
                    "prep_time": "15 min",
                    "cook_time": "30 min",
                    "total_time": "45 min",
                    "servings": "4",
                    "calories": "350 kcal",
                    "ingredients": ing_list,
                    "instructions": [s["body"] for s in steps]
                }
                
                original_gen_recipe = getattr(generator, "_gen_recipe", None)
                generator._gen_recipe = lambda: recipe
                
                sections = [
                    {"key": "intro",              "content": intro},
                    {"key": "why_i_love_items",   "content": why_items},
                    {"key": "why_love_items",     "content": why_items},
                    {"key": "why_works_items",    "content": why_items},
                    {"key": "ingredients_intro",  "content": ing_intro},
                    {"key": "ingredient_list",    "content": ing_list},
                    {"key": "ingredients_list",   "content": ing_list},
                    {"key": "instructions_steps", "content": steps},
                    {"key": "pro_tips",           "content": tips},
                    {"key": "serving_suggestions","content": serving},
                    {"key": "variations",         "content": variations},
                    {"key": "storage",            "content": storage},
                    {"key": "conclusion",         "content": conclusion},
                    {"key": "faqs",               "content": faqs},
                    {"key": "recipe",             "content": recipe},
                ]
                
                data = {
                    "intro": intro,
                    "why_items": why_items,
                    "why_works": why_items,
                    "why_i_love_item_1": why_items[0],
                    "why_i_love_item_2": why_items[1],
                    "why_i_love_item_3": why_items[2],
                    "why_i_love_item_4": "It's a crowd pleaser.",
                    "ingredients_intro": ing_intro,
                    "ingredients_list": ing_list,
                    "ingredient_list_raw": "\n".join([f"- {x}" for x in ing_list]),
                    "steps": steps,
                    "instructions_step_1": steps[0]["body"],
                    "instructions_step_2": steps[1]["body"],
                    "instructions_step_3": steps[2]["body"],
                    "instructions_step_4": "Enjoy your dish.",
                    "instructions_step_5": "Share with friends.",
                    "step_1_label": steps[0]["heading"],
                    "step_2_label": steps[1]["heading"],
                    "step_3_label": steps[2]["heading"],
                    "step_4_label": "Serve",
                    "step_5_label": "Enjoy",
                    "tips": tips,
                    "pro_tips_tip_1": tips[0],
                    "pro_tips_tip_2": tips[1],
                    "pro_tips_tip_3": tips[2],
                    "pro_tips_tip_4": tips[3],
                    "serving": serving,
                    "serving_suggestions": serving,
                    "conclusion": conclusion,
                    "faqs": faqs,
                    "faq_1_q": faqs[0]["question"],
                    "faq_1_a": faqs[0]["answer"],
                    "faq_2_q": faqs[1]["question"],
                    "faq_2_a": faqs[1]["answer"],
                    "faq_3_q": "Can I double this?",
                    "faq_3_a": "Yes, just double the ingredients.",
                    "recipe": recipe,
                    "variations": variations,
                    "storage": storage,
                    "recipe_prep": "15 min",
                    "recipe_cook": "30 min",
                    "recipe_total": "45 min",
                    "recipe_servings": "4",
                    "recipe_calories": "350 kcal"
                }

                import inspect
                html_method = getattr(generator, "generate_html", None) or getattr(generator, "build_html", None)
                if html_method:
                    sig = inspect.signature(html_method)
                    if "data" in sig.parameters:
                        html = html_method(data)
                    else:
                        try:
                            html = html_method(sections)
                        except Exception:
                            html = html_method(data)
                else:
                    html = "<!-- Error: could not find generate_html or build_html -->"
                    
                css_method = getattr(generator, "generate_css", None) or getattr(generator, "build_css", None)
                css = css_method() if css_method else ""
                
                if original_gen_recipe:
                    generator._gen_recipe = original_gen_recipe
                
                return {
                    "title": getattr(generator, "title", "Sample Recipe"),
                    "slug": getattr(generator, "slug", "sample-recipe"),
                    "article_html": html,
                    "article_css": css
                }
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            log.warning("[generate-article-preview] native preview failed, falling back to generic: %s\n%s", e, tb)
            # Fall through to generic preview

    # Generic preview: works with any generator that has CONFIG (colors, fonts, layout, components)
    try:
        from generators.base_preview import generic_article_preview
    except ImportError:
        base_path = Path(__file__).resolve().parent / "generators" / "base_preview.py"
        if not base_path.exists():
            raise HTTPException(status_code=500, detail="Generic preview module not found. Add run_preview() to your generator.")
        spec = importlib.util.spec_from_file_location("base_preview", base_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        generic_article_preview = mod.generic_article_preview
    try:
        return generic_article_preview(merged_config)
    except Exception as e:
        log.error("[generate-article-preview] generic fallback failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Preview failed. Ensure CONFIG has colors, fonts, layout. Error: {e}")


@router.post("/generate-article/{generator_name}")
def generate_article(generator_name: str, config: dict = Body(...)):
    """
    Generate article content using the specified generator.

    - **generator_name**: e.g. generator-1, generator-2, generator-3
    - **config**: Full CONFIG JSON (title and categories_list required)
    - **Returns**: content.json structure
    """
    try:
        _validate_config(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        module = _load_generator_module(generator_name)
    except (FileNotFoundError, ImportError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Merge payload with generator's default CONFIG (only title + categories_list required)
    default_config = getattr(module, "CONFIG", {})
    merged = _deep_merge(default_config, config)
    # Round-robin OpenRouter model per domain when ai_provider is openrouter
    # Optional openrouter_models: list of model ids to use (rotation over this list). If absent, use OPENROUTER_MODELS.
    # Optional openrouter_start_index: when multi-domain-clean retries after "3 attempt(s)" failure, it can pass 5 or 10 to try a different set of 3 models
    # For local provider: use local_model from config
    # Keys must come from the request (multi-domain-clean Profile). Do not use generator .env so we never send a wrong key.
    openai_key = (merged.get("openai_api_key") or "").strip()
    openrouter_key = (merged.get("openrouter_api_key") or "").strip()
    ai_provider = (merged.get("ai_provider") or os.getenv("AI_PROVIDER", "openrouter")).lower()
    if ai_provider == "openai" and not openai_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not provided. Add it in multi-domain-clean → Profile and run again. The generator does not use its own .env for keys when called from multi-domain-clean.",
        )
    if ai_provider == "openrouter" and not openrouter_key:
        raise HTTPException(
            status_code=400,
            detail="OpenRouter API key not provided. Add it in multi-domain-clean → Profile and run again. The generator does not use its own .env for keys when called from multi-domain-clean.",
        )
    if ai_provider == "llamacpp":
        llamacpp_manager_url = (merged.get("llamacpp_manager_url") or os.getenv("LLAMACPP_MANAGER_URL", "")).strip().rstrip("/")
        llamacpp_model_id = merged.get("llamacpp_model_id")
        if not llamacpp_manager_url:
            raise HTTPException(status_code=400, detail="llamacpp_manager_url not set. Configure LLAMACPP_MANAGER_URL or llama.cpp in Profile.")
        if llamacpp_model_id is None:
            raise HTTPException(status_code=400, detail="llamacpp_model_id required when ai_provider=llamacpp.")
        merged["llamacpp_manager_url"] = llamacpp_manager_url
        merged["llamacpp_model_id"] = int(llamacpp_model_id)
    merged["openai_api_key"] = openai_key or None
    merged["openrouter_api_key"] = openrouter_key or None
    has_openai_key = bool(merged.get("openai_api_key"))
    has_openrouter_key = bool(merged.get("openrouter_api_key"))
    log.info("[generate-article] generator=%s ai_provider=%s has_openai_key=%s has_openrouter_key=%s", generator_name, ai_provider, has_openai_key, has_openrouter_key)
    domain_index = merged.get("domain_index")
    openrouter_models = merged.get("openrouter_models")
    local_model = merged.get("local_model")
    if isinstance(openrouter_models, list) and len(openrouter_models) > 0:
        models_to_use = [str(m).strip() for m in openrouter_models if str(m).strip()]
    else:
        models_to_use = OPENROUTER_MODELS
    base_idx = 0
    if ai_provider == "openrouter":
        if "openrouter_start_index" in merged and merged["openrouter_start_index"] is not None:
            base_idx = int(merged["openrouter_start_index"]) % len(models_to_use)
            log.info("[generate-article] openrouter_start_index=%s -> base_idx=%s", merged["openrouter_start_index"], base_idx)
        elif domain_index is not None:
            base_idx = int(domain_index) if isinstance(domain_index, (int, float)) else 0
    elif ai_provider == "local" and local_model:
        merged["local_model"] = str(local_model).strip()
        log.info("[generate-article] local provider with model=%s", local_model)
    elif ai_provider == "llamacpp":
        log.info("[generate-article] llamacpp provider with model_id=%s", merged.get("llamacpp_model_id"))

    ArticleGenerator = getattr(module, "ArticleGenerator", None)
    if ArticleGenerator is None:
        raise HTTPException(status_code=500, detail="Generator module has no ArticleGenerator class")

    # When a full ordered list is provided (multi-domain-clean builds it with user's pick first),
    # try each model sequentially (up to 3 per round). Spread attempts across list for diversity.
    max_attempts = 3  # per call from multi-domain-clean (it calls us multiple rounds)
    content_data = None
    last_error = None

    try:
        for attempt in range(max_attempts):
            # Set OpenRouter model: rotate to a different model each attempt
            # Use consecutive offset when full list provided (base_idx already advances per round)
            if ai_provider == "openrouter":
                offset = attempt if len(models_to_use) <= 6 else OPENROUTER_RETRY_OFFSETS[attempt] if attempt < len(OPENROUTER_RETRY_OFFSETS) else attempt
                model_idx = (base_idx + offset) % len(models_to_use)
                chosen_model = models_to_use[model_idx]
                merged["openrouter_model"] = chosen_model
                # Assign so generator module sees this model when ArticleGenerator() is created
                module.CONFIG = dict(merged)
                log.info(
                    "[generate-article] openrouter attempt %s/%s model_idx=%s model=%s",
                    attempt + 1,
                    max_attempts,
                    model_idx,
                    chosen_model,
                )
            else:
                module.CONFIG = merged  # non-OpenRouter: config unchanged across attempts

            try:
                generator = ArticleGenerator()
                # Verify generator got the rotated model (for OpenRouter)
                if ai_provider == "openrouter" and hasattr(generator, "model"):
                    log.info("[generate-article] generator.model=%s", getattr(generator, "model", None))
                content_data = generator.run(return_content_only=True)
            except Exception as e:
                last_error = e
                if ai_provider == "openrouter" and attempt < max_attempts - 1:
                    log.warning(
                        "[generate-article] generation error (attempt %s/%s), retrying with different OpenRouter model: %s",
                        attempt + 1,
                        max_attempts,
                        e,
                    )
                    continue
                
                if ai_provider == "openrouter":
                    log.warning("[generate-article] generation error on final attempt: %s", e)
                    break
                    
                raise

            # Add model_used for article_content table (provider -> model). Always use full format.
            if isinstance(content_data, dict):
                mu = content_data.get("model_used") or ""
                if " -> " not in str(mu):  # Incomplete (e.g. just "openai") or missing
                    if ai_provider == "openrouter":
                        model = merged.get("openrouter_model") or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
                        content_data["model_used"] = f"openrouter -> {model}"
                    elif ai_provider == "local":
                        model = merged.get("local_model") or os.getenv("LOCAL_MODEL", "qwen3:8b")
                        content_data["model_used"] = f"local -> {model}"
                    elif ai_provider == "llamacpp":
                        content_data["model_used"] = f"llamacpp -> model_id {merged.get('llamacpp_model_id')}"
                    else:
                        model = merged.get("openai_model") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                        content_data["model_used"] = f"openai -> {model}"

            # Add generation_cost_usd if usage has tokens but cost missing (fallback for generators that don't set it)
            if isinstance(content_data, dict) and content_data.get("generation_cost_usd") is None:
                usage = content_data.get("usage")
                if isinstance(usage, dict) and calculate_cost_from_usage:
                    provider = (ai_provider or "openai").lower()
                    model = merged.get("openrouter_model") if provider == "openrouter" else merged.get("openai_model")
                    if not model and provider == "openai":
                        model = merged.get("openai_model") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                    if not model and provider == "openrouter":
                        model = merged.get("openrouter_model") or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
                    if model:
                        cost = calculate_cost_from_usage(usage, str(model), provider)
                        if cost is not None:
                            content_data["generation_cost_usd"] = round(cost, 6)
                            if "cost" not in usage:
                                content_data["usage"] = dict(usage, cost=round(cost, 6))

            if not _is_content_failure(content_data):
                break
            if ai_provider != "openrouter" or attempt >= max_attempts - 1:
                log.warning("[generate-article] content failure and no more retries (provider=%s attempt=%s)", ai_provider, attempt + 1)
                break
            log.warning(
                "[generate-article] content failure (placeholder or empty), retrying with different OpenRouter model (attempt %s/%s)",
                attempt + 1,
                max_attempts,
            )

        if content_data is None:
            if ai_provider == "openrouter":
                raise ValueError(
                    "Content generation failed after %s attempt(s). Last error: %s"
                    % (max_attempts, last_error)
                )
            raise RuntimeError(last_error or "Generator did not return data")
        if _is_content_failure(content_data):
            html = (content_data or {}).get("article_html") or (content_data or {}).get("article") or ""
            log.warning(
                "[generate-article] content failure: article_html len=%s, placeholder=%s",
                len(html) if isinstance(html, str) else 0,
                FAILED_CONTENT_PLACEHOLDER in (html or ""),
            )
            raise ValueError(
                "Content generation failed after %s attempt(s). Please try again or use another model."
                % max_attempts
            )

        keys = list(content_data.keys()) if isinstance(content_data, dict) else []
        log.info("[generate-article] result keys=%s", keys)
        # prompt/prompt_image_ingredients come from generate-prompts step, never from article generator
        for k in ("prompt", "prompt_image_ingredients", "prompt_midjourney_main", "prompt_midjourney_ingredients"):
            if isinstance(content_data, dict) and k in content_data:
                content_data[k] = ""
        return content_data
    except ValueError as e:
        log.warning("[generate-article] 400: %s (generator=%s ai_provider=%s has_openai_key=%s has_openrouter_key=%s)", e, generator_name, ai_provider, has_openai_key, has_openrouter_key)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        tb = traceback.format_exc()
        msg = f"[generate-article] generator failed: {e}\n{tb}"
        log.error("%s", msg)
        print(msg, file=sys.stderr)  # ensure it appears in .logs/articles-website-generator.log
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
