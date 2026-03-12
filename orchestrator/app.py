"""
Orchestrator Setup Wizard
=========================
Provides a web UI at :9000 to configure:
  - Database backend (MySQL / Supabase-PostgreSQL / SQLite)
  - Database credentials
  - Service API URLs (pin_generator, articles-website-generator, etc.)
  - .env file generation for each microservice

On save, it writes .env files to a shared volume so other containers can read them.
"""

import os, json, time, textwrap
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_folder="static", static_url_path="/static")

# Where env files are written (shared volume)
ENV_OUTPUT_DIR = os.getenv("ENV_OUTPUT_DIR", "/app/env-output")
CONFIG_FILE = os.path.join(ENV_OUTPUT_DIR, "orchestrator_config.json")

# ─── Default service definitions ──────────────────────────────────────
SERVICES = [
    {
        "key": "multi-domain-clean",
        "label": "Multi-Domain Clean (Admin UI)",
        "port": 5001,
        "health": "/",
        "env_file": "multi-domain-clean/.env",
        "description": "Main admin dashboard & orchestrator",
    },
    {
        "key": "pin_generator",
        "label": "Pin Generator",
        "port": 5000,
        "health": "/",
        "env_file": "pin_generator/.env",
        "description": "Pinterest pin image generation API",
    },
    {
        "key": "articles-website-generator",
        "label": "Articles & Website Generator",
        "port": 5002,
        "health": "/",
        "env_file": "articles-website-generator/.env",
        "description": "Article content generation API",
    },
    {
        "key": "website-parts-generator",
        "label": "Website Parts Generator",
        "port": 5003,
        "health": "/",
        "env_file": "website-parts-generator/.env",
        "description": "Header, footer, sidebar templates API",
    },
    {
        "key": "llamacpp_manager",
        "label": "LlamaCpp Manager",
        "port": 5004,
        "health": "/",
        "env_file": "",
        "description": "Local LLM model manager",
    },
]


def _load_config():
    """Load saved config from disk."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
                
                # Auto-patch old ports to new ports
                if "services" in cfg:
                    svcs = cfg["services"]
                    if "articles-website-generator" in svcs:
                        svcs["articles-website-generator"]["url"] = svcs["articles-website-generator"]["url"].replace(":8000", ":5002").replace("http://localhost:5002", "http://articles-website-generator:5002")
                    if "website-parts-generator" in svcs:
                        svcs["website-parts-generator"]["url"] = svcs["website-parts-generator"]["url"].replace(":8010", ":5003").replace("http://localhost:5003", "http://website-parts-generator:5003")
                    if "llamacpp_manager" in svcs:
                        svcs["llamacpp_manager"]["url"] = svcs["llamacpp_manager"]["url"].replace(":8080", ":5004").replace("http://localhost:5004", "http://llamacpp_manager:5004")
                    if "pin_generator" in svcs:
                        svcs["pin_generator"]["url"] = svcs["pin_generator"]["url"].replace("http://localhost:5000", "http://pin_generator:5000")
                
                return cfg
        except Exception:
            pass
    return {}


def _save_config(cfg):
    """Persist config to disk."""
    os.makedirs(ENV_OUTPUT_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def _generate_env_files(cfg):
    """Generate .env files from the config."""
    os.makedirs(ENV_OUTPUT_DIR, exist_ok=True)

    db = cfg.get("database", {})
    backend = db.get("backend", "mysql")
    services_cfg = cfg.get("services", {})

    # ── multi-domain-clean/.env ───────────────────────────────────
    mdc_lines = []
    mdc_lines.append(f"DB_BACKEND={backend}")
    mdc_lines.append(f"SECRET_KEY={db.get('secret_key', 'change-me-in-production')}")

    if backend == "mysql":
        mdc_lines.append(f"MYSQL_HOST={db.get('mysql_host', 'host.docker.internal')}")
        mdc_lines.append(f"MYSQL_USER={db.get('mysql_user', 'root')}")
        mdc_lines.append(f"MYSQL_PASSWORD={db.get('mysql_password', '')}")
        mdc_lines.append(f"MYSQL_DATABASE={db.get('mysql_database', 'pinterest')}")
    elif backend == "supabase":
        mdc_lines.append(f"SUPABASE_DB_URL={db.get('supabase_db_url', '')}")
        if db.get("supabase_pooler_url"):
            mdc_lines.append(f"SUPABASE_POOLER_URL={db.get('supabase_pooler_url', '')}")

    # AI keys
    ai = cfg.get("ai", {})
    if ai.get("openai_api_key"):
        mdc_lines.append(f"OPENAI_API_KEY={ai['openai_api_key']}")
    if ai.get("openrouter_api_key"):
        mdc_lines.append(f"OPENROUTER_API_KEY={ai['openrouter_api_key']}")

    # Service URLs
    pin_url = services_cfg.get("pin_generator", {}).get("url", "http://pin_generator:5000")
    article_url = services_cfg.get("articles-website-generator", {}).get("url", "http://articles-website-generator:5002")
    website_url = services_cfg.get("website-parts-generator", {}).get("url", "http://website-parts-generator:5003")
    llama_url = services_cfg.get("llamacpp_manager", {}).get("url", "http://llamacpp_manager:5004")

    mdc_lines.append(f"PIN_API_URL={pin_url}")
    mdc_lines.append(f"GENERATE_ARTICLE_API_URL={article_url}")
    mdc_lines.append(f"WEBSITE_PARTS_API_URL={website_url}")
    mdc_lines.append(f"LLAMACPP_MANAGER_URL={llama_url}")

    _write_env(os.path.join(ENV_OUTPUT_DIR, "multi-domain-clean.env"), mdc_lines)

    # ── pin_generator/.env ────────────────────────────────────────
    pin_lines = []
    if ai.get("openai_api_key"):
        pin_lines.append(f"OPENAI_API_KEY={ai['openai_api_key']}")
    _write_env(os.path.join(ENV_OUTPUT_DIR, "pin_generator.env"), pin_lines)

    # ── articles-website-generator/.env ───────────────────────────
    awg_lines = []
    if ai.get("openai_api_key"):
        awg_lines.append(f"OPENAI_API_KEY={ai['openai_api_key']}")
    if ai.get("openrouter_api_key"):
        awg_lines.append(f"OPENROUTER_API_KEY={ai['openrouter_api_key']}")
    awg_lines.append(f"LLAMACPP_MANAGER_URL={llama_url}")
    _write_env(os.path.join(ENV_OUTPUT_DIR, "articles-website-generator.env"), awg_lines)

    # ── website-parts-generator/.env ──────────────────────────────
    wpg_lines = []
    _write_env(os.path.join(ENV_OUTPUT_DIR, "website-parts-generator.env"), wpg_lines)

    return True


def _write_env(path, lines):
    with open(path, "w") as f:
        f.write("# Auto-generated by Orchestrator Setup Wizard\n")
        f.write(f"# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for line in lines:
            f.write(line + "\n")


# ─── ROUTES ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/services", methods=["GET"])
def api_services():
    return jsonify(SERVICES)


@app.route("/api/config", methods=["GET"])
def api_get_config():
    return jsonify(_load_config())


@app.route("/api/config", methods=["POST"])
def api_save_config():
    cfg = request.get_json(force=True)
    _save_config(cfg)
    _generate_env_files(cfg)
    return jsonify({"ok": True, "message": "Configuration saved and .env files generated."})


@app.route("/api/health-check", methods=["POST"])
def api_health_check():
    """Check if a service is reachable."""
    data = request.get_json(force=True)
    url = data.get("url", "")
    try:
        r = requests.get(url, timeout=5)
        return jsonify({"ok": True, "status": r.status_code})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/test-db", methods=["POST"])
def api_test_db():
    """Test database connectivity."""
    data = request.get_json(force=True)
    backend = data.get("backend", "mysql")
    try:
        if backend == "mysql":
            import pymysql
            conn = pymysql.connect(
                host=data.get("mysql_host", "localhost"),
                user=data.get("mysql_user", "root"),
                password=data.get("mysql_password", ""),
                database=data.get("mysql_database", "pinterest"),
                connect_timeout=5,
            )
            conn.close()
            return jsonify({"ok": True, "message": "MySQL connection successful!"})
        elif backend == "supabase":
            import psycopg2
            conn = psycopg2.connect(data.get("supabase_db_url", ""), connect_timeout=5)
            conn.close()
            return jsonify({"ok": True, "message": "Supabase/PostgreSQL connection successful!"})
        else:
            return jsonify({"ok": True, "message": "SQLite requires no connection test."})
    except ImportError as e:
        return jsonify({"ok": False, "error": f"Missing driver: {e}. Install pymysql or psycopg2."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/env-files", methods=["GET"])
def api_list_env_files():
    """List generated .env files."""
    files = {}
    if os.path.isdir(ENV_OUTPUT_DIR):
        for fn in os.listdir(ENV_OUTPUT_DIR):
            if fn.endswith(".env"):
                with open(os.path.join(ENV_OUTPUT_DIR, fn)) as f:
                    files[fn] = f.read()
    return jsonify(files)


if __name__ == "__main__":
    os.makedirs(ENV_OUTPUT_DIR, exist_ok=True)
    print("=" * 60)
    print("  🚀 Orchestrator Setup Wizard")
    print("  Open http://localhost:9000 to configure your services")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5005, debug=False)
