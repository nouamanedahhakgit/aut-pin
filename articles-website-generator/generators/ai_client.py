"""
Shared AI client with automatic model fallback on rate-limit (429) errors.

Usage in generators:
    from ai_client import create_ai_client, ai_chat

    # In __init__:
    self.client, self.model = create_ai_client(self.config)

    # Instead of self.client.chat.completions.create(...):
    text = ai_chat(self, prompt, max_tokens=600, system="You are a food blogger.")
"""
import os
import time
import logging
import requests

from openai import OpenAI

log = logging.getLogger(__name__)

OPENROUTER_MODELS = [
    "deepseek/deepseek-v3.2"
   
]

LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://192.168.1.20:11434/api/generate")
LOCAL_MODELS = os.getenv("LOCAL_MODELS", "qwen3:8b,llama3.2:3b,ibm/granite4:latest,gemma3:latest,functiongemma:latest").split(",")


def create_ai_client(config: dict):
    """Return (client, model) based on config ai_provider.
    Prefers config keys (openrouter_api_key, openai_api_key) from request payload over env vars.
    """
    provider = (config.get("ai_provider") or os.getenv("AI_PROVIDER", "openrouter")).lower()
    if provider == "openrouter":
        api_key = config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("openrouter_api_key must be set in config or OPENROUTER_API_KEY in environment")
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
        model = config.get("local_model") or (LOCAL_MODELS[0] if LOCAL_MODELS else "qwen3:8b")
    else:
        api_key = config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("openai_api_key must be set in config or OPENAI_API_KEY in environment")
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
        return _local_call(model, prompt, max_tokens, system, temperature)
    
    if provider != "openrouter" or not model:
        return _single_call(client, model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"), prompt, max_tokens, system, temperature)

    for retry in range(MAX_RETRIES_PER_MODEL):
        try:
            return _single_call(client, model, prompt, max_tokens, system, temperature)
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


def _single_call(client, model, prompt, max_tokens, system, temperature):
    """Make a single API call. Raises on error."""
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
        
    return resp.choices[0].message.content.strip()


def _local_call(model, prompt, max_tokens, system, temperature):
    """Make a call to Local API (e.g., Ollama). Raises on error."""
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
        return (data.get("response") or "").strip()
    except Exception as e:
        log.error("[_local_call] Error calling Local API: %s", e)
        raise

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
