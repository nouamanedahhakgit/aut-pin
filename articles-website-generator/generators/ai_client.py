"""
Shared AI client with automatic model fallback on rate-limit (429) errors.

Usage in generators:
    from ai_client import create_ai_client, ai_chat

    # In __init__:
    self.client, self.model = create_ai_client(self.config)

    # Instead of self.client.chat.completions.create(...):
    text = ai_chat(self, prompt, max_tokens=600, system="You are a food blogger.")
"""
import json
import os
import re
import time
import logging
import requests

from openai import OpenAI

log = logging.getLogger(__name__)


def extract_json_robust(raw: str) -> dict:
    """Extract and parse JSON from AI response. Tries repair on failure (trailing commas, truncation)."""
    text = (raw or "").strip()
    # Strip markdown code blocks
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    # Extract JSON object
    m = re.search(r"\{[\s\S]*", text)
    if not m:
        try:
            return json.loads(text) if text else {}
        except Exception:
            return {}
    text = m.group()
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Repair common issues
    repaired = re.sub(r",\s*}", "}", text)
    repaired = re.sub(r",\s*]", "]", repaired)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass
    # Try to fix truncated JSON by closing brackets
    open_brace = repaired.count("{") - repaired.count("}")
    open_bracket = repaired.count("[") - repaired.count("]")
    if open_brace > 0 or open_bracket > 0:
        try:
            closed = repaired.rstrip()
            if closed.endswith(","):
                closed = closed[:-1]
            closed += "]" * open_bracket + "}" * open_brace
            return json.loads(closed)
        except json.JSONDecodeError:
            pass
    return {}

OPENROUTER_MODELS = [
    "deepseek/deepseek-v3.2",
]

# Pricing: (input_usd_per_1M_tokens, output_usd_per_1M_tokens). Used to calculate cost when API doesn't return it.
# OpenAI: https://openai.com/api/pricing
# OpenRouter: use when cost not in response; add models as needed
MODEL_PRICING = {
    # OpenAI models
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4-turbo-preview": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-4o-2024-05-13": (2.50, 10.00),
    "gpt-4o-2024-08-06": (2.50, 10.00),
    "gpt-4o-2024-11-20": (2.50, 10.00),
    "gpt-4o-mini-2024-07-18": (0.15, 0.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.80, 3.20),
    "gpt-4.1-nano": (0.20, 0.80),
    "o1-mini": (1.10, 4.40),
    "o1": (11.00, 55.00),
    "o1-preview": (11.00, 55.00),
    # OpenRouter (provider/model) - common models when cost not returned
    "openai/gpt-4o-mini": (0.15, 0.60),
    "openai/gpt-4o": (2.50, 10.00),
    "openai/gpt-4-turbo": (10.00, 30.00),
    "openai/gpt-4": (30.00, 60.00),
    "deepseek/deepseek-v3.2": (0.32, 0.89),
    "deepseek/deepseek-chat": (0.14, 0.28),
    "anthropic/claude-3-5-sonnet": (3.00, 15.00),
    "anthropic/claude-3-5-haiku": (0.80, 4.00),
    "anthropic/claude-3-opus": (15.00, 75.00),
    "google/gemini-pro": (0.50, 1.50),
    "google/gemini-flash": (0.10, 0.40),
}

LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://192.168.1.20:11434/api/generate")
LOCAL_MODELS = os.getenv("LOCAL_MODELS", "qwen3:8b,llama3.2:3b,ibm/granite4:latest,gemma3:latest,functiongemma:latest").split(",")


def create_ai_client(config: dict):
    """Return (client, model) based on config ai_provider.
    Prefers config keys (openrouter_api_key, openai_api_key) from request payload over env vars.
    """
    provider = (config.get("ai_provider") or os.getenv("AI_PROVIDER", "openrouter")).lower()
    
    # Try to dynamically fallback based on keys if default fails
    if provider == "openai" and not config.get("openai_api_key") and config.get("openrouter_api_key"):
        provider = "openrouter"
    elif provider == "openrouter" and not config.get("openrouter_api_key") and config.get("openai_api_key"):
        provider = "openai"
    elif provider == "local" and not config.get("local_api_url"):
        if config.get("openrouter_api_key"):
            provider = "openrouter"
        elif config.get("openai_api_key"):
            provider = "openai"
    elif provider == "llamacpp" and not config.get("llamacpp_manager_url"):
        if config.get("openrouter_api_key"):
            provider = "openrouter"
        elif config.get("openai_api_key"):
            provider = "openai"
            
    if provider == "openai" and not config.get("openai_api_key") and config.get("openrouter_api_key"):
        provider = "openrouter"
    elif provider == "openrouter" and not config.get("openrouter_api_key") and config.get("openai_api_key"):
        provider = "openai"
        
    config["ai_provider"] = provider

    if provider == "openrouter":
        api_key = config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            # Fallback to checking if they provided openai key instead
            if config.get("openai_api_key") or os.getenv("OPENAI_API_KEY"):
                provider = "openai"
                api_key = config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
                client = OpenAI(api_key=api_key)
                model = config.get("openai_model") or config.get("model") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                return client, model
            raise ValueError("openrouter_api_key must be set. Add your OpenRouter API key in multi-domain-clean → Profile.")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        model = config.get("openrouter_model") or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
    elif provider == "local":
        local_base = config.get("local_api_url") or os.getenv("LOCAL_API_URL", "http://192.168.1.20:11434")
        if isinstance(local_base, str) and local_base.endswith("/api/generate"):
            local_base = local_base.rstrip("/api/generate").rstrip("/")
        client = OpenAI(
            base_url=f"{local_base}/v1",
            api_key="not-needed"
        )
        model = config.get("local_model") or config.get("local_models", "").split(",")[0] or (LOCAL_MODELS[0] if LOCAL_MODELS else "qwen3:8b")
    elif provider == "llamacpp":
        client = None  # Uses _llamacpp_call, not OpenAI client
        model = str(config.get("llamacpp_model_id") or "")
    else:
        api_key = config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Fallback to checking if they provided openrouter key instead
            if config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY"):
                api_key = config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY")
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                model = config.get("openrouter_model") or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
                return client, model
            raise ValueError("openai_api_key must be set. Add your OpenAI API key in multi-domain-clean → Profile. If using bulk run, ensure you are logged in.")
        client = OpenAI(api_key=api_key)
        model = config.get("openai_model") or config.get("model") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return client, model


def _is_rate_limit(exc):
    """Check if exception is a 429 rate-limit error."""
    msg = str(exc)
    if "429" in msg:
        return True
    exc_type = type(exc).__name__
    if "RateLimitError" in exc_type:
        return True
    code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if code == 429:
        return True
    return False


MAX_RETRIES_PER_MODEL = 3
RETRY_WAIT_SECONDS = [2, 5, 10]


def ai_chat(generator, prompt, max_tokens=600, system=None, temperature=0.7):
    """
    Call the AI API with rate-limit retries.
    Relies on `route.py` to change the `generator.model` if the current one completely fails.
    """
    client = generator.client
    model = getattr(generator, "model", None)
    provider = (getattr(generator, "config", None) or {}).get("ai_provider", "openrouter")
    
    if provider == "local":
        text, _ = _local_call(model, prompt, max_tokens, system, temperature)
        return text
    if provider == "llamacpp":
        text, _ = _llamacpp_call(generator, model, prompt, max_tokens, system, temperature)
        return text
    if provider != "openrouter" or not model:
        text, _ = _single_call(client, model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"), prompt, max_tokens, system, temperature, provider)
        return text
    for retry in range(MAX_RETRIES_PER_MODEL):
        try:
            text, _ = _single_call(client, model, prompt, max_tokens, system, temperature, provider)
            return text
        except Exception as e:
            if _is_rate_limit(e):
                wait = RETRY_WAIT_SECONDS[retry] if retry < len(RETRY_WAIT_SECONDS) else 10
                log.warning("[ai_chat] 429 on %s (try %d/%d), waiting %ds...", model, retry + 1, MAX_RETRIES_PER_MODEL, wait)
                if retry < MAX_RETRIES_PER_MODEL - 1:
                    time.sleep(wait)
                    continue
            
            log.error("[ai_chat] Error on %s: %s", model, e)
            raise

    raise RuntimeError(f"Model {model} exhausted after {MAX_RETRIES_PER_MODEL} rate-limit retries.")


def _get_model_pricing(model: str, provider: str = ""):
    """Return (input_per_1M, output_per_1M) or None if unknown."""
    if not model:
        return None
    m = (model or "").strip()
    if m in MODEL_PRICING:
        return MODEL_PRICING[m]
    # Fallbacks: gpt-4o-mini-2024-xx -> gpt-4o-mini, openai/gpt-4o -> gpt-4o
    fallbacks = [
        ("gpt-4o-mini", "gpt-4o-mini"),
        ("gpt-4o", "gpt-4o"),
        ("gpt-4-turbo", "gpt-4-turbo"),
        ("gpt-4.1-mini", "gpt-4.1-mini"),
        ("gpt-4.1", "gpt-4.1"),
        ("o1-mini", "o1-mini"),
        ("o1", "o1"),
        ("deepseek-v3.2", "deepseek/deepseek-v3.2"),
        ("deepseek-chat", "deepseek/deepseek-chat"),
    ]
    base = m.split("/")[-1] if "/" in m else m
    for substr, key in fallbacks:
        if substr in base or substr in m:
            if key in MODEL_PRICING:
                return MODEL_PRICING[key]
    return None


def calculate_cost_from_usage(usage: dict, model: str, provider: str = ""):
    """
    Calculate cost in USD from usage (prompt_tokens, completion_tokens) and model pricing.
    Returns None if usage lacks tokens or model has no pricing.
    """
    if not usage or not isinstance(usage, dict):
        return None
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is None and ct is None:
        pt = usage.get("total_tokens", 0) or 0
        ct = 0
    pt = int(pt) if pt is not None else 0
    ct = int(ct) if ct is not None else 0
    if pt == 0 and ct == 0:
        return None
    pricing = _get_model_pricing(model, provider)
    if not pricing:
        return None
    in_p, out_p = pricing
    return (pt / 1_000_000 * in_p) + (ct / 1_000_000 * out_p)


def _usage_from_response(resp, model: str = None, provider: str = ""):
    """Build usage dict from OpenAI/OpenRouter response.usage for storage and cost tracking."""
    u = getattr(resp, "usage", None)
    if not u:
        return None
    d = {}
    if getattr(u, "prompt_tokens", None) is not None:
        d["prompt_tokens"] = int(u.prompt_tokens)
    if getattr(u, "completion_tokens", None) is not None:
        d["completion_tokens"] = int(u.completion_tokens)
    if getattr(u, "total_tokens", None) is not None:
        d["total_tokens"] = int(u.total_tokens)
    # Cost: use API value (OpenRouter) or calculate from tokens (OpenAI and when missing)
    cost = getattr(u, "cost", None)
    if cost is not None:
        try:
            d["cost"] = float(cost)
        except (TypeError, ValueError):
            pass
    if "cost" not in d and d and model:
        calculated = calculate_cost_from_usage(d, model, provider)
        if calculated is not None:
            d["cost"] = round(calculated, 6)
    return d if d else None


def _single_call(client, model, prompt, max_tokens, system, temperature, provider: str = ""):
    """Make a single API call. Raises on error. Returns (content, usage_dict)."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    if not resp or not hasattr(resp, "choices") or not resp.choices:
        raise ValueError(f"Invalid API response (no choices) from model {model}: {resp}")
    content = resp.choices[0].message.content.strip()
    usage = _usage_from_response(resp, model=model, provider=provider)
    return content, usage


def _llamacpp_call(generator, model_id, prompt, max_tokens, system, temperature):
    """Call llamacpp_manager POST /ai/generate. Returns (text, usage_dict)."""
    config = (getattr(generator, "config", None) or {})
    manager_url = (config.get("llamacpp_manager_url") or os.getenv("LLAMACPP_MANAGER_URL", "http://localhost:5004")).strip().rstrip("/")
    model_id = int(model_id) if model_id else 0
    if not model_id:
        raise ValueError("llamacpp_model_id required for llama.cpp provider.")
    try:
        resp = requests.post(
            f"{manager_url}/ai/generate",
            json={
                "model_id": model_id,
                "prompt": prompt,
                "system": system or "",
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return (data.get("text") or "").strip(), data.get("usage") or None
    except Exception as e:
        log.error("[_llamacpp_call] Error: %s", e)
        raise


def _local_call(model, prompt, max_tokens, system, temperature):
    """Make a call to Local API (e.g., Ollama). Raises on error. Returns (content, None) - no usage."""
    import requests
    local_url = os.getenv("LOCAL_API_URL", "http://192.168.1.20:11434/api/generate")
    full_prompt = prompt
    if system:
        full_prompt = f"{system}\n\n{prompt}"
    try:
        resp = requests.post(
            local_url,
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        return (data.get("response") or "").strip(), None
    except Exception as e:
        log.error("[_local_call] Error calling Local API: %s", e)
        raise


def ai_chat_with_usage(generator, prompt, max_tokens=600, system=None, temperature=0.7):
    """
    Same as ai_chat but returns (text, usage_dict).
    usage_dict has prompt_tokens, completion_tokens, total_tokens, and optionally cost (OpenRouter).
    Use this when you need to persist cost/usage per article and add them to the content dict.
    """
    client = generator.client
    model = getattr(generator, "model", None)
    provider = (getattr(generator, "config", None) or {}).get("ai_provider", "openrouter")
    if provider == "local":
        return _local_call(model, prompt, max_tokens, system, temperature)
    if provider == "llamacpp":
        return _llamacpp_call(generator, model, prompt, max_tokens, system, temperature)
    if provider != "openrouter" or not model:
        return _single_call(client, model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"), prompt, max_tokens, system, temperature, provider)
    for retry in range(MAX_RETRIES_PER_MODEL):
        try:
            return _single_call(client, model, prompt, max_tokens, system, temperature, provider)
        except Exception as e:
            if _is_rate_limit(e):
                wait = RETRY_WAIT_SECONDS[retry] if retry < len(RETRY_WAIT_SECONDS) else 10
                log.warning("[ai_chat_with_usage] 429 on %s (try %d/%d), waiting %ds...", model, retry + 1, MAX_RETRIES_PER_MODEL, wait)
                if retry < MAX_RETRIES_PER_MODEL - 1:
                    time.sleep(wait)
                    continue
            raise
    raise RuntimeError(f"Model {model} exhausted after {MAX_RETRIES_PER_MODEL} rate-limit retries.")

def get_first_category(config_dict: dict) -> dict:
    """Safely extract first category from categories_list in config. 
    Handles list of dicts, list of strings, or JSON string. Returns dict with 'id' and 'categorie'."""
    cl = config_dict.get("categories_list")
    if isinstance(cl, str):
        try:
            import json
            cl = json.loads(cl) if cl.strip() else []
        except Exception:
            cl = []
    if not isinstance(cl, list) or not cl:
        return {"id": 1, "categorie": "dinner"}
    first = cl[0]
    if isinstance(first, dict):
        return {"id": first.get("id", 1), "categorie": str(first.get("categorie", "dinner") or "dinner")}
    return {"id": 1, "categorie": str(first) if first else "dinner"}
