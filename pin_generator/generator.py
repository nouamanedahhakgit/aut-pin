#!/usr/bin/env python3
"""
Run a single template generator by name, or all (CLI).
Or run as web API: pass template name in param and template_data in body.

CLI:
  python generator.py --name template_1
  python generator.py --name template_2 --output-dir ./my_pins
  python generator.py --name all
  python generator.py --list

API (--serve):
  python generator.py --serve --port 5000
  POST /generate?name=template_1   Body (JSON, optional): { "title": "...", "elements": { "title": { "text": "..." } }, "background": "https://..." }
  Response includes index_html, images_manifest, and screenshot_base64 (PNG of the pin as data URL).
  GET  /templates  -> list template names
  For screenshot: pip install playwright && playwright install chromium
"""

import os
import sys
import copy
import tempfile
import argparse
import base64
import json
import logging
import re
import uuid

# Project root
ROOT = os.path.dirname(os.path.abspath(__file__))

# Logging: clear, readable view of generator flow
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("generator")
DEFAULT_OUTPUT = os.path.join(ROOT, "output")


class OpenAIServiceError(Exception):
    """Raised when OpenAI API is called but fails (quota, rate limit, etc.)."""
    pass


def _load_env():
    """Load .env from project root."""
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, ".env"))
    except ImportError:
        pass


def _deep_merge(base, override):
    """Recursively merge override into base (mutates base)."""
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = copy.deepcopy(v)


def _apply_variables(obj, variables):
    """Recursively replace {{key}} in strings with variables.get(key, '{{key}}'). Mutates obj."""
    if not variables or not isinstance(variables, dict):
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                for var_k, var_v in variables.items():
                    v = v.replace("{{" + str(var_k) + "}}", str(var_v))
                obj[k] = v
            else:
                _apply_variables(v, variables)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                for var_k, var_v in variables.items():
                    v = v.replace("{{" + str(var_k) + "}}", str(var_v))
                obj[i] = v
            else:
                _apply_variables(v, variables)


def _truncate_to_limit(text, limit):
    """Trim text to <= limit chars, preferring whole words."""
    s = str(text or "").strip()
    if limit <= 0 or len(s) <= limit:
        return s
    cut = s[:limit].rstrip()
    sp = cut.rfind(" ")
    if sp >= int(limit * 0.6):
        cut = cut[:sp].rstrip()
    return cut + "..."


def _estimate_text_limit(el):
    """
    Estimate safe max chars from element box and font size.
    Helps keep generated text within pin layout bounds.
    """
    if not isinstance(el, dict):
        return 80
    width = int(el.get("width") or 320)
    height = int(el.get("height") or 60)
    fz = int(el.get("font_size") or 24)
    # Rough typography heuristic for latin text.
    chars_per_line = max(4, int(width / max(1.0, fz * 0.58)))
    line_h = max(1.0, fz * 1.2)
    lines = max(1, int(height / line_h))
    return max(8, min(160, chars_per_line * lines))


def _fit_generated_texts(generated, elements):
    """Apply per-element max-char limits to generated texts."""
    out = {}
    for key, val in (generated or {}).items():
        el = (elements or {}).get(key) if isinstance(elements, dict) else None
        limit = _estimate_text_limit(el)
        out[key] = _truncate_to_limit(val, limit)
    return out


def _generate_texts_via_openai(title, prompt, field_prompts, config=None, field_examples=None):
    """
    Call OpenAI to generate text for each field based on recipe title.
    config: optional dict with openai_api_key, openrouter_api_key, ai_provider, openai_model, openrouter_model (from multi-domain-clean profile).
    field_examples: optional dict {"field_name": "example text"} - when provided, AI must match EXACT word count and reskin for the new recipe.
    Returns dict like {"subtitle": "...", "title": "..."}.
    Raises OpenAIServiceError if the API is called but fails (quota, rate limit, etc.).
    Returns {} only when OpenAI is skipped (no key, no title, no field_prompts).
    """
    cfg = config or {}
    provider = (cfg.get("ai_provider") or os.environ.get("AI_PROVIDER", "openai")).lower()
    from openai import OpenAI
    if provider == "openrouter":
        api_key = (cfg.get("openrouter_api_key") or os.environ.get("OPENROUTER_API_KEY", "")).strip()
        model = (cfg.get("openrouter_model") or os.environ.get("OPENROUTER_MODEL", "openai/gpt-oss-120b"))
        if not api_key and cfg.get("openai_api_key"):
            api_key = cfg.get("openai_api_key", "").strip()
            provider = "openai"
            model = cfg.get("openai_model") or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            client = OpenAI(api_key=api_key)
        elif not api_key:
            log.warning("OpenRouter skipped: no openrouter_api_key in config or env")
            return {}
        else:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    elif provider == "groq":
        api_key = (cfg.get("groq_api_key") or os.environ.get("GROQ_API_KEY", "")).strip()
        model = (cfg.get("groq_model") or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"))
        if not api_key:
            log.warning("Groq skipped: no groq_api_key in config or env")
            return {}
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
    elif provider == "local":
        base_raw = (cfg.get("local_api_url") or os.environ.get("LOCAL_API_URL", "http://127.0.0.1:11434/api/generate")).strip()
        if "/api/generate" in base_raw:
            base_url = base_raw.split("/api/generate")[0].rstrip("/") + "/v1"
        else:
            base_url = base_raw.rstrip("/") if base_raw.endswith("/v1") else (base_raw.rstrip("/") + "/v1")
        model = (cfg.get("local_model") or os.environ.get("LOCAL_MODEL", "qwen3:8b")).strip()
        client = OpenAI(base_url=base_url, api_key=(cfg.get("local_api_key") or "ollama"))
    else:
        api_key = (cfg.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")).strip()
        model = (cfg.get("openai_model") or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
        if not api_key and cfg.get("openrouter_api_key"):
            api_key = cfg.get("openrouter_api_key", "").strip()
            provider = "openrouter"
            model = cfg.get("openrouter_model") or os.environ.get("OPENROUTER_MODEL", "openai/gpt-oss-120b")
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        elif not api_key:
            log.warning("OpenAI skipped: no openai_api_key in config or env")
            return {}
        else:
            client = OpenAI(api_key=api_key)

    if not title or not field_prompts:
        if not title:
            log.warning("AI skipped: no title in request")
        else:
            log.warning("AI skipped: no field_prompts")
        return {}
    log.info("AI request | title=%r | fields=%s | model=%s", title[:60] + ("..." if len(title) > 60 else ""), list(field_prompts.keys()), model)
    try:
        # Replace {{title}} in each field prompt so the model gets the actual recipe name
        resolved = {k: v.replace("{{title}}", title) for k, v in field_prompts.items()}
        user_parts = [
            prompt,
            "",
            f"Recipe/ARTICLE title (you MUST use this — do not invent a different recipe): {title}",
            "",
            "Field prompts (generate one value per key; output only the JSON object):",
            json.dumps(resolved, indent=2),
        ]
        if field_examples:
            word_counts = {k: len(v.split()) for k, v in field_examples.items() if isinstance(v, str) and v.strip()}
            user_parts.extend([
                "",
                "FIELD EXAMPLES (match EXACT word count — reskin for the new recipe):",
                json.dumps(field_examples, indent=2),
                "",
                f"Word counts to match: {json.dumps(word_counts)}. Your output MUST have the SAME number of words per field.",
            ])
        user_content = "\n".join(user_parts)
        system_content = (
            "You return only a single valid JSON object. No markdown, no code fence, no explanation. "
            "Keys are field names, values are the generated text strings. "
            "CRITICAL: All generated text must be ABOUT THE GIVEN RECIPE/ARTICLE TITLE ONLY. Do not invent a different dish or generic text; the badge and title must relate directly to the recipe title provided. "
        )
        if field_examples:
            system_content += (
                "When field_examples are provided: RESKIN the content — create new text for the given recipe that matches the EXACT word count of each example. Same structure, different words."
            )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            temperature=0.5,
        )
        text = (resp.choices[0].message.content or "").strip()
        # Strip markdown code fence if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        out = json.loads(text)
        result = out if isinstance(out, dict) else {}
        for k, v in result.items():
            log.info("  → %s: %s", k, (v[:50] + "..." if isinstance(v, str) and len(v) > 50 else v))
        log.info("OpenAI done | %d fields", len(result))
        return result
    except OpenAIServiceError:
        raise
    except Exception as e:
        err_msg = str(e).strip()
        log.exception("OpenAI error: %s", e)
        # User-friendly message for quota / rate limit
        if "quota" in err_msg.lower() or "rate" in err_msg.lower() or "limit" in err_msg.lower():
            raise OpenAIServiceError("OpenAI quota or rate limit exceeded. Please try again later or check your API usage.") from e
        raise OpenAIServiceError(f"OpenAI request failed: {err_msg}") from e


def _html_to_screenshot_bytes(html, width=600, height=1067):
    """Render HTML in headless browser and return PNG bytes, or None on failure."""
    log.info("Screenshot | %dx%d | html_len=%d", width, height, len(html or ""))
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.warning("Screenshot skipped: playwright not installed")
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": height})
            page.set_content(html, wait_until="load")
            page.wait_for_timeout(2000)
            screenshot_bytes = page.screenshot(type="png")
            browser.close()
        size_k = (len(screenshot_bytes) + 512) // 1024
        log.info("Screenshot ok | size=%d KB", size_k)
        return screenshot_bytes
    except Exception as e:
        log.exception("Screenshot failed: %s", e)
        return None


def _html_to_screenshot_base64(html, width=600, height=1067):
    """Render HTML in headless browser and return PNG screenshot as data URL base64, or None on failure."""
    raw = _html_to_screenshot_bytes(html, width, height)
    return ("data:image/png;base64," + base64.b64encode(raw).decode("utf-8")) if raw else None


_R2_KEYS = ("r2_account_id", "r2_access_key_id", "r2_secret_access_key", "r2_bucket_name", "r2_public_url")


def _normalize_r2_config(d):
    """Return dict with all five R2 keys (multi-domain profile / Pin API JSON) or None if incomplete."""
    if not isinstance(d, dict) or not d:
        return None
    out = {}
    for k in _R2_KEYS:
        v = d.get(k)
        if v is None or (isinstance(v, str) and not str(v).strip()):
            return None
        out[k] = str(v).strip()
    out["r2_public_url"] = out["r2_public_url"].rstrip("/")
    return out


def _r2_config_from_request_body(body):
    """Build R2 config from POST JSON (flat keys and/or nested body.r2). Read-only."""
    if not isinstance(body, dict):
        return None
    merged = {}
    for k in _R2_KEYS:
        v = body.get(k)
        if v is not None and str(v).strip():
            merged[k] = v
    nested = body.get("r2")
    if isinstance(nested, dict):
        for k in _R2_KEYS:
            if k not in merged and nested.get(k) is not None and str(nested.get(k)).strip():
                merged[k] = nested[k]
    return _normalize_r2_config(merged)


def _upload_png_to_r2(png_bytes, r2_config=None):
    """
    Upload PNG bytes to Cloudflare R2. Returns public URL string or None on failure.
    r2_config: optional dict with r2_account_id, r2_access_key_id, r2_secret_access_key,
      r2_bucket_name, r2_public_url (same as multi-domain-clean profile). When set, used instead of env.
    Fallback env: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL.
    """
    account_id = access_key = secret_key = bucket = public_base = None
    norm = _normalize_r2_config(r2_config) if r2_config else None
    if norm:
        account_id = norm["r2_account_id"]
        access_key = norm["r2_access_key_id"]
        secret_key = norm["r2_secret_access_key"]
        bucket = norm["r2_bucket_name"]
        public_base = norm["r2_public_url"]
    else:
        account_id = os.environ.get("R2_ACCOUNT_ID")
        access_key = os.environ.get("R2_ACCESS_KEY_ID")
        secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
        bucket = os.environ.get("R2_BUCKET_NAME")
        public_base = (os.environ.get("R2_PUBLIC_URL") or "").strip().rstrip("/") or None
    if not all([account_id, access_key, secret_key, bucket, public_base]):
        log.warning(
            "R2 upload skipped: set R2_* env on the Pin API process, or pass r2_account_id, r2_access_key_id, "
            "r2_secret_access_key, r2_bucket_name, r2_public_url in the JSON body (from your Profile)."
        )
        return None
    size_k = (len(png_bytes) + 512) // 1024
    log.info("R2 upload | bucket=%s | size=%d KB", bucket, size_k)
    try:
        import boto3
        import ssl
        key = f"pins/{uuid.uuid4().hex}.png"
        endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
        ssl_verify = os.environ.get("R2_SSL_VERIFY", "true").strip().lower() not in ("0", "false", "no", "off")
        _create_default_https_context = None
        if not ssl_verify:
            _create_default_https_context = ssl._create_default_https_context
            ssl._create_default_https_context = ssl._create_unverified_context
        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name="auto",
            )
            s3.put_object(Bucket=bucket, Key=key, Body=png_bytes, ContentType="image/png")
            url = f"{public_base}/{key}"
            log.info("R2 upload ok | url=%s", url)
            return url
        finally:
            if _create_default_https_context is not None:
                ssl._create_default_https_context = _create_default_https_context
    except Exception as e:
        log.exception("R2 upload failed: %s", e)
        return None


def main_cli():
    parser = argparse.ArgumentParser(
        description="Generate one Pinterest Pin template by name, or all.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--name", "-n",
        metavar="NAME",
        help="Generator name: template_1, template_2, template_3, template_4, template_5, or 'all'",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available generator names and exit",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--serve", "-s",
        action="store_true",
        help="Run as web API server",
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=5000,
        help="Port for API server (default: 5000)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for API server (default: 0.0.0.0)",
    )
    args = parser.parse_args()

    from generators import list_generators, load_generator

    available = list_generators()
    if not available:
        print("No generators found in generators/ (template_1.py, template_2.py, ...)")
        return 1

    if args.serve:
        return run_server(available, args.host, args.port)

    if args.list:
        print("Available generators:")
        for name in available:
            print(f"  {name}")
        return 0

    name = (args.name or "").strip().lower().replace("-", "_")
    if not name:
        parser.error("Use --name <template_N> or --name all (or --list to see names)")

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    if name == "all":
        print("=" * 50)
        print("Generating all templates")
        print("=" * 50)
        print(f"Output: {output_dir}\n")
        for gen_name in available:
            mod = load_generator(gen_name)
            if mod and hasattr(mod, "run"):
                mod.run(output_dir=output_dir)
        print("\nDone.")
        return 0

    if name not in available:
        print(f"Unknown generator: {name}")
        print("Available:", ", ".join(available))
        print("Use --list to see names.")
        return 1

    mod = load_generator(name)
    if not mod or not hasattr(mod, "run"):
        print(f"Generator {name} has no run(output_dir) function.")
        return 1

    print(f"Running: {name}")
    mod.run(output_dir=output_dir)
    return 0


def run_server(available_templates, host="0.0.0.0", port=5000):
    try:
        from flask import Flask, request, jsonify, send_from_directory
    except ImportError:
        print("Flask is required for API server. Install: pip install flask")
        return 1

    from generators import load_generator

    _load_env()
    app = Flask(__name__)

    # Enable werkzeug request logging even in non-debug mode
    wz_log = logging.getLogger("werkzeug")
    wz_log.setLevel(logging.INFO)
    if not wz_log.handlers:
        wz_log.addHandler(logging.StreamHandler(sys.stderr))

    @app.after_request
    def _cors(resp):
        """Allow other projects (e.g. external editor) to call this API."""
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    @app.errorhandler(Exception)
    def _handle_exception(exc):
        import traceback
        tb = traceback.format_exc()
        print(f"[pin_api] UNHANDLED EXCEPTION:\n{tb}", flush=True)
        log.exception("Unhandled exception: %s", exc)
        return jsonify({"success": False, "error": str(exc), "traceback": tb}), 500

    @app.route("/")
    @app.route("/editor")
    def serve_editor():
        """Serve the pin editor UI."""
        return send_from_directory(ROOT, "editor.html")

    @app.route("/templates", methods=["GET"])
    def list_templates():
        """List available template names. Add ?debug=1 to test-load each template."""
        from generators import _TEMPLATES_ROOT
        templates_with_previews = []
        for tname in available_templates:
            preview_url = None
            try:
                mod = load_generator(tname)
                if mod and hasattr(mod, "TEMPLATE_DATA"):
                    preview_url = mod.TEMPLATE_DATA.get("preview_url")
            except Exception:
                pass
            
            has_local_preview = os.path.isfile(os.path.join(_TEMPLATES_ROOT, f"{tname}.png"))
            templates_with_previews.append({
                "name": tname,
                "has_preview": has_local_preview or preview_url is not None,
                "preview_url": (f"/preview/{tname}" if has_local_preview else preview_url)
            })
        if request.args.get("debug") == "1":
            results = {}
            for tname in available_templates:
                try:
                    mod = load_generator(tname)
                    if mod and hasattr(mod, "TEMPLATE_DATA"):
                        results[tname] = {"ok": True, "keys": list(mod.TEMPLATE_DATA.keys())}
                    else:
                        results[tname] = {"ok": False, "error": "load_generator returned None or no TEMPLATE_DATA"}
                except Exception as e:
                    import traceback
                    results[tname] = {"ok": False, "error": str(e), "traceback": traceback.format_exc()}
            return jsonify({"templates": templates_with_previews, "debug": results, "pid": os.getpid()})
        return jsonify({"templates": templates_with_previews})

    @app.route("/debug/load-templates", methods=["GET"])
    def debug_load_templates():
        """Test-load every template and report success/failure."""
        results = {}
        for tname in available_templates:
            try:
                mod = load_generator(tname)
                if mod and hasattr(mod, "TEMPLATE_DATA"):
                    results[tname] = {"ok": True, "keys": list(mod.TEMPLATE_DATA.keys())}
                else:
                    results[tname] = {"ok": False, "error": "No TEMPLATE_DATA"}
            except Exception as e:
                results[tname] = {"ok": False, "error": str(e)}
        return jsonify(results)

    @app.route("/template/<name>", methods=["GET"])
    def get_template(name):
        """Return default template_data for a template (for editor form)."""
        n = (name or "").strip().lower().replace("-", "_")
        if not n or n not in available_templates:
            return jsonify({"success": False, "error": f"Unknown template: {name}", "available": available_templates}), 404
        try:
            mod = load_generator(n)
        except Exception as exc:
            import traceback
            tb = traceback.format_exc()
            print(f"[pin_api] get_template({n}) load error:\n{tb}", flush=True)
            return jsonify({"success": False, "error": f"Failed to load {n}: {exc}", "traceback": tb}), 500
        if not mod:
            print(f"[pin_api] get_template({n}): load_generator returned None", flush=True)
            return jsonify({"success": False, "error": f"load_generator returned None for {n} — check pin_generator.log for traceback"}), 500
        if not hasattr(mod, "TEMPLATE_DATA"):
            print(f"[pin_api] get_template({n}): module has no TEMPLATE_DATA, attrs={dir(mod)}", flush=True)
            return jsonify({"success": False, "error": f"No TEMPLATE_DATA for {n}"}), 500
        template_id = getattr(mod, "TEMPLATE_ID", n)
        return jsonify({
            "success": True,
            "template_id": template_id,
            "template_name": n,
            "template_data": copy.deepcopy(mod.TEMPLATE_DATA),
            "style_slots": getattr(mod.TEMPLATE_DATA, "style_slots", getattr(mod, "STYLE_SLOTS", None)) or {},
            "font_slots": getattr(mod.TEMPLATE_DATA, "font_slots", getattr(mod, "FONT_SLOTS", None)) or {},
        })

    @app.route("/preview/<path:name>", methods=["GET"])
    def get_preview(name):
        """Serve the preview PNG for a template if it exists."""
        from generators import _TEMPLATES_ROOT
        n = (name or "").strip().lower().replace("-", "_")
        if n.endswith(".png"):
            n = n[:-4]
        
        path = os.path.join(_TEMPLATES_ROOT, f"{n}.png")
        if os.path.isfile(path):
            return send_from_directory(_TEMPLATES_ROOT, f"{n}.png")
        
        # Check if it was in a subfolder like group_1/template_1
        # n might be group_1/template_1
        if os.sep != "/":
            path = os.path.join(_TEMPLATES_ROOT, n.replace("/", os.sep) + ".png")
            if os.path.isfile(path):
                return send_from_directory(os.path.dirname(path), os.path.basename(path))

        return jsonify({"error": f"Preview for '{n}' not found at {path}"}), 404

    @app.route("/merge-template", methods=["POST"])
    def merge_template():
        """
        Merge payload into template_data (e.g. from DB) and optionally run OpenAI for text fields.
        Body: { "template_data": {...}, "variables": {...}, "elements": {...}, "title", "domain", "domain_colors", "domain_fonts", ... }
        Returns: { "success": True, "template_data": merged }. Used by JavaScript pin path (multi-domain-clean).
        """
        from generators._base import template_from_data, apply_overrides, apply_domain_style
        body = request.get_json(silent=True) or {}
        tpl_data = body.get("template_data") or body
        if not isinstance(tpl_data, dict):
            return jsonify({"success": False, "error": "Missing or invalid template_data"}), 400
        merged = copy.deepcopy(tpl_data)
        # Normalize to template shape (skip for HTML templates - preserve html, template_type, field_prompts)
        if merged.get("template_type") != "html":
            tpl = template_from_data(merged)
            merged = copy.deepcopy(tpl)
        # Domain style
        dc = body.get("domain_colors")
        df = body.get("domain_fonts")
        if dc or df:
            style_slots = body.get("style_slots") or {}
            font_slots = body.get("font_slots") or {}
            try:
                apply_domain_style(merged, style_slots, font_slots, dc, df)
            except Exception as e:
                log.warning("merge_template domain_style: %s", e)
        _deep_merge(merged, {k: v for k, v in body.items() if k not in ("template_data", "style_slots", "font_slots") and v is not None})
        # Build variables: merge body variables + domain color placeholders for HTML templates
        variables = dict(body.get("variables") or {})
        if merged.get("template_type") == "html" and dc:
            variables.setdefault("domain_primary", dc.get("primary") or "#5D4037")
            variables.setdefault("domain_secondary", dc.get("secondary") or "#8B5A2B")
            variables.setdefault("domain_background", dc.get("background") or "#FFFFFF")
            variables.setdefault("domain_text_primary", dc.get("text_primary") or "#000000")
            variables.setdefault("domain_text_secondary", dc.get("text_secondary") or "#666666")
            variables.setdefault("domain_on_primary", "#FFFFFF")
            variables.setdefault("domain_on_secondary", "#FFFFFF")
        if variables:
            _apply_variables(merged, variables)
        # Apply layout/position/domain overrides BEFORE AI, so AI-generated text is not overwritten (same as Python /generate)
        apply_overrides(merged, body)
        # OpenAI text for fields with field_prompts — runs after apply_overrides so generated text wins
        _ai_keys = (
            "openai_api_key",
            "openrouter_api_key",
            "groq_api_key",
            "ai_provider",
            "openai_model",
            "openrouter_model",
            "groq_model",
            "local_api_url",
            "local_model",
        )
        ai_config = {k: body[k] for k in _ai_keys if k in body and body[k] is not None}
        title = (body.get("variables") or {}).get("title") or body.get("title") or body.get("name")
        domain = (body.get("variables") or {}).get("domain") or body.get("domain") or "example.com"
        if title and isinstance(title, str):
            elements = merged.get("elements") or {}
            field_prompts = merged.get("field_prompts") or {}
            if not field_prompts:
                for ek, ev in elements.items():
                    if isinstance(ev, dict) and ev.get("type") == "text" and ev.get("text_prompt"):
                        field_prompts[ek] = ev["text_prompt"]
            prompt = merged.get("prompt") or "Generate text for each field. Replace {{title}} with the recipe title; output a JSON object with one key per field."
            field_examples = merged.get("field_examples") or {}
            if field_prompts and prompt:
                try:
                    generated = _generate_texts_via_openai(title, prompt, field_prompts, config=ai_config, field_examples=field_examples if field_examples else None)
                    if generated:
                        if merged.get("template_type") == "html":
                            # HTML templates: put generated text in variables for placeholder replacement
                            merged.setdefault("variables", {})
                            merged["variables"].update(generated)
                            merged["variables"]["title"] = title
                            merged["variables"]["domain"] = domain
                        else:
                            generated = _fit_generated_texts(generated, elements)
                            for fn, text in generated.items():
                                if fn in merged.get("elements", {}):
                                    merged["elements"][fn]["text"] = text
                except OpenAIServiceError as e:
                    log.warning("merge_template OpenAI: %s", e)
        return jsonify({"success": True, "template_data": merged})

    @app.route("/generate-from-html", methods=["POST"])
    def generate_from_html():
        """
        Generate a pin image from raw HTML (e.g. from JavaScript renderer).
        Body (JSON): { "html": "<!DOCTYPE html>...", "width": 600, "height": 1067,
          optional R2 (per-profile, same keys as multi-domain-clean): r2_account_id, r2_access_key_id,
          r2_secret_access_key, r2_bucket_name, r2_public_url — or nested under "r2": { ... }.
        Returns: same shape as /generate (screenshot_base64, image_url).
        """
        try:
            body = request.get_json(silent=True) or {}
            if not isinstance(body, dict):
                return jsonify({"success": False, "error": "Body must be a JSON object"}), 400
            html = (body.get("html") or "").strip()
            if not html:
                return jsonify({"success": False, "error": "Missing or empty body.html"}), 400
            try:
                w = int(body.get("width") or 600)
                h = int(body.get("height") or 1067)
            except (TypeError, ValueError):
                w, h = 600, 1067
            r2_cfg = _r2_config_from_request_body(body)
            log.info("POST /generate-from-html | %dx%d | html_len=%d | r2=%s", w, h, len(html), "profile/body" if r2_cfg else "env")
            screenshot_bytes = _html_to_screenshot_bytes(html, width=w, height=h)
            if not screenshot_bytes:
                return jsonify({
                    "success": False,
                    "error": "Screenshot failed (install playwright + chromium: pip install playwright && playwright install chromium)",
                }), 500
            image_url = _upload_png_to_r2(screenshot_bytes, r2_cfg)
            payload = {"success": True}
            if image_url:
                payload["image_url"] = image_url
            else:
                payload["screenshot_base64"] = "data:image/png;base64," + base64.b64encode(screenshot_bytes).decode("utf-8")
            return jsonify(payload)
        except Exception as e:
            log.exception("generate-from-html failed: %s", e)
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/generate", methods=["POST"])
    def generate():
        """
        Generate a pin. Query param: name (template_1, template_2, ...).
        Body (JSON, optional): template_data overrides, e.g.:
          { "name": "My Recipe", "elements": { "title": { "text": "New Title" } }, "background": "https://..." }
        Returns: { "success": true, "template_id": "...", "index_html": "...", "images_manifest": { ... } }
        """
        name = (request.args.get("name") or request.args.get("template") or "").strip().lower().replace("-", "_")
        if not name:
            log.warning("POST /generate | missing name")
            return jsonify({"success": False, "error": "Missing query param: name (e.g. ?name=template_1)"}), 400
        if name not in available_templates:
            log.warning("POST /generate | unknown template: %s", name)
            return jsonify({"success": False, "error": f"Unknown template: {name}", "available": available_templates}), 404

        template_only = str(request.args.get("template_only") or "").strip().lower() in ("1", "true", "yes")
        preview_small = str(request.args.get("preview_small") or "").strip().lower() in ("1", "true", "yes")
        log.info("--- /generate | template=%s | template_only=%s | preview_small=%s", name, template_only, preview_small)

        body = {}
        if request.is_json:
            body = request.get_json(silent=True) or {}
        elif request.data:
            try:
                import json as _json
                body = _json.loads(request.data)
            except Exception:
                pass

        variables = body.pop("variables", None)
        if variables is not None and not isinstance(variables, dict):
            variables = None
        # API keys from multi-domain-clean profile (passed in body)
        ai_config = {}
        _ai_keys_gen = (
            "openai_api_key",
            "openrouter_api_key",
            "groq_api_key",
            "ai_provider",
            "openai_model",
            "openrouter_model",
            "groq_model",
            "local_api_url",
            "local_model",
        )
        for k in _ai_keys_gen:
            if k in body:
                ai_config[k] = body.pop(k)
        r2_upload_cfg = {}
        for k in _R2_KEYS:
            if k in body:
                r2_upload_cfg[k] = body.pop(k)
        nested_r2 = body.pop("r2", None)
        if isinstance(nested_r2, dict):
            for k in _R2_KEYS:
                if k in nested_r2 and nested_r2[k] is not None:
                    r2_upload_cfg.setdefault(k, nested_r2[k])
        r2_upload_cfg = _normalize_r2_config(r2_upload_cfg)
        body_keys = list(body.keys()) if isinstance(body, dict) else []
        title_from_req = (variables or {}).get("title") or body.get("title") or body.get("name")
        log.info("  body keys=%s | variables.title=%s", body_keys, (title_from_req[:40] + "..." if isinstance(title_from_req, str) and len(title_from_req) > 40 else title_from_req))

        mod = load_generator(name)
        if not mod or not hasattr(mod, "run") or not hasattr(mod, "TEMPLATE_DATA"):
            log.error("Generator %s has no run or TEMPLATE_DATA", name)
            return jsonify({"success": False, "error": f"Generator {name} has no run or TEMPLATE_DATA"}), 500

        # Generate text for each field using element text_prompt: replace {{title}} with article title, call OpenAI, write result into element text
        if not template_only:
            title = None
            if variables and variables.get("title"):
                title = variables.get("title")
            if not title and body.get("title"):
                title = body.get("title")
            if not title and body.get("name"):
                title = body.get("name")
            if title and isinstance(title, str):
                template_data = getattr(mod, "TEMPLATE_DATA", {})
                # Build field_prompts from each element's text_prompt (except website)
                elements = template_data.get("elements") or {}
                field_prompts = {}
                for ek, ev in elements.items():
                    if ek == "website" or "website" in (ek or "").lower():
                        continue
                    if isinstance(ev, dict) and ev.get("type") == "text" and ev.get("text_prompt"):
                        field_prompts[ek] = ev["text_prompt"]
                if not field_prompts:
                    field_prompts = template_data.get("field_prompts") or {}
                prompt = template_data.get("prompt") or "Generate text for each field. Replace {{title}} with the recipe title in each prompt; output a JSON object with one key per field and the generated text as value."
                field_examples = template_data.get("field_examples") or {}
                if prompt and field_prompts and isinstance(field_prompts, dict):
                    try:
                        generated = _generate_texts_via_openai(title, prompt, field_prompts, config=ai_config, field_examples=field_examples if field_examples else None)
                    except OpenAIServiceError as e:
                        log.error("Pin generation aborted: OpenAI failed — %s", e)
                        return jsonify({
                            "success": False,
                            "error": str(e),
                            "code": "openai_error",
                        }), 503
                    if generated:
                        generated = _fit_generated_texts(generated, elements)
                        body.setdefault("elements", {})
                        for field_name, text in generated.items():
                            body["elements"].setdefault(field_name, {})["text"] = text
                    elif field_prompts:
                        log.warning("OpenAI returned no text; pin will use template/default text")
                else:
                    log.info("No OpenAI text generation (no prompt or field_prompts)")

        merged = copy.deepcopy(mod.TEMPLATE_DATA)
        # Apply domain colors/fonts FIRST as defaults; then client merge so user edits take precedence
        dc = body.get("domain_colors")
        df = body.get("domain_fonts")
        if dc or df:
            style_slots = getattr(mod, "STYLE_SLOTS", None)
            font_slots = getattr(mod, "FONT_SLOTS", None)
            if style_slots or font_slots:
                try:
                    from generators._base import apply_domain_style
                    apply_domain_style(merged, style_slots or {}, font_slots or {}, dc, df)
                    log.info("  Applied domain_colors=%s domain_fonts=%s (defaults)", bool(dc), bool(df))
                except Exception as e:
                    log.warning("  Could not apply domain style: %s", e)
        _deep_merge(merged, body)
        if variables:
            _apply_variables(merged, variables)
        log.info("Merged template_data | elements=%s", list((merged.get("elements") or {}).keys()))

        # Pass merged to template WITHOUT domain_colors/domain_fonts so template's run() won't
        # re-apply domain style and overwrite user's manual color/setting edits
        merged_for_run = copy.deepcopy(merged)
        merged_for_run.pop("domain_colors", None)
        merged_for_run.pop("domain_fonts", None)

        original_data = mod.TEMPLATE_DATA
        try:
            mod.TEMPLATE_DATA = merged_for_run
            tmpdir = tempfile.mkdtemp(prefix="pin_")
            try:
                log.info("Run generator | output_dir=%s", tmpdir)
                mod.run(output_dir=tmpdir)
                template_id = getattr(mod, "TEMPLATE_ID", name)
                out_dir = os.path.join(tmpdir, template_id)
                index_path = os.path.join(out_dir, "index.html")
                manifest_path = os.path.join(out_dir, "images_manifest.json")
                index_html = ""
                images_manifest = {}
                if os.path.isfile(index_path):
                    with open(index_path, "r", encoding="utf-8") as f:
                        index_html = f.read()
                if os.path.isfile(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        images_manifest = json.load(f)
                payload = {
                    "success": True,
                    "template_id": template_id,
                    "index_html": index_html,
                    "images_manifest": images_manifest,
                }
                if template_only:
                    log.info("Response | template_only=1 | no screenshot")
                    payload["template_data"] = copy.deepcopy(merged)
                    return jsonify(payload)
                # Use template canvas dimensions so the full pin is captured (no cropping).
                # Previously used fixed 600x1067 which cropped templates with 736x1308 canvas.
                canvas = merged.get("canvas") or {}
                w = int(canvas.get("width") or 600)
                h = int(canvas.get("height") or 1067)
                if body.get("preview_width") and body.get("preview_height"):
                    try:
                        w, h = int(body["preview_width"]), int(body["preview_height"])
                    except (TypeError, ValueError):
                        pass
                screenshot_bytes = _html_to_screenshot_bytes(index_html, width=w, height=h)
                if screenshot_bytes:
                    image_url = _upload_png_to_r2(screenshot_bytes, r2_upload_cfg)
                    if image_url:
                        payload["image_url"] = image_url
                        log.info("Response | success | image_url=%s", image_url)
                    else:
                        payload["screenshot_base64"] = "data:image/png;base64," + base64.b64encode(screenshot_bytes).decode("utf-8")
                        log.info("Response | success | image in screenshot_base64 (R2 not configured)")
                else:
                    payload["screenshot_error"] = "No screenshot (install playwright + chromium on pin API server: pip install playwright && playwright install chromium)"
                    log.warning("Response | no screenshot")
                return jsonify(payload)
            finally:
                try:
                    import shutil
                    shutil.rmtree(tmpdir, ignore_errors=True)
                except Exception:
                    pass
        finally:
            mod.TEMPLATE_DATA = original_data

    log.info("Pin API server: http://%s:%s", host, port)
    log.info("  Editor: http://%s:%s/  or  /editor", host, port)
    print(f"API server: http://{host}:{port}")
    print("  Editor:  http://%s:%s/  or  /editor" % (host, port))
    print("  GET  /templates        -> list template names")
    print("  GET  /template/<name>  -> default template_data for editor")
    print("  POST /generate?name=template_1   Body: JSON template_data overrides")
    app.run(host=host, port=port)
    return 0


if __name__ == "__main__":
    exit(main_cli() or 0)
