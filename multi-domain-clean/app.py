"""Clean Multi-Domain Flask app - database-management, admin pages."""
import html
import io
import json
from datetime import datetime
import re
import os
import base64
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
import subprocess
import tempfile
import traceback
import threading
import uuid
import time
import urllib.request
import urllib.error
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, redirect, url_for, jsonify, send_from_directory, send_file, session, make_response
import requests as requests_lib
from db import get_connection, init_db, dict_row, execute as db_execute, last_insert_id
from rewrite import rewrite, generate_article_content_for_a
from config import GENERATE_ARTICLE_API_URL, PIN_EDITOR_URL, PIN_API_URL, ARTICLE_GENERATORS_DIR, OPENAI_API_KEY, OPENAI_MODEL, WEBSITE_PARTS_API_URL, STATIC_PROJECT_OUTPUT_DIR, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, get_ai_config
import imagine
import r2_upload
import openai
from pinterest_upload import _build_article_url as pinterest_build_article_url

SITE_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site_templates")

# Domain colors: used for header, footer, sidebar, category, articles. Each domain has its own palette.
DEFAULT_DOMAIN_COLORS = {"primary": "#2ecc71", "secondary": "#27ae60", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"}
# Distinct palettes for bulk add: background white, normal text; primary/secondary/border matching accent colors
GOOD_BULK_COLOR_PALETTES = [
    {"primary": "#6C8AE4", "secondary": "#9C6ADE", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E2E8FF"},
    {"primary": "#E07C5E", "secondary": "#9B5B4F", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#F0E0D8"},
    {"primary": "#3D8B7A", "secondary": "#2A5A4E", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#D4EDE8"},
    {"primary": "#8B5A9B", "secondary": "#5A3A6B", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E8D8F0"},
    {"primary": "#2E86AB", "secondary": "#1A5276", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#D4E8F4"},
    {"primary": "#D4A24C", "secondary": "#A67C32", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#F0E4D0"},
    {"primary": "#C75B7A", "secondary": "#8B3A52", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#F0D8E0"},
    {"primary": "#4A90A4", "secondary": "#2E6B7A", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#D4EDF4"},
]
# Domain fonts: heading/body used across header, footer, sidebar, category, articles. Same structure as article_template_config.fonts.
DEFAULT_DOMAIN_FONTS = {
    "heading_family": "Playfair Display",
    "heading_h1": "2.5rem", "heading_h2": "1.875rem", "heading_h3": "1.5rem",
    "body_family": "Inter",
    "body_size": "1rem",
    "body_line_height": "1.7",
}
FONT_FAMILY_OPTIONS = ["Inter", "Playfair Display", "Lora", "Merriweather", "Source Serif 4", "Fraunces", "Source Sans 3", "Open Sans", "Lato", "DM Sans", "PT Sans", "Work Sans", "Georgia", "Arial"]

# OpenRouter models for content generation (rotation or user selection). Keep in sync with articles-website-generator route.py
OPENROUTER_MODELS = [
    "deepseek/deepseek-v3.2"
]

# Local models for content generation (e.g., Ollama, LM Studio, etc.)
LOCAL_MODELS = [
    "qwen3:8b",
    "llama3.2:3b",
    "mistral:7b",
    "functiongemma:latest",
    "ibm/granite4:latest",
    "gemma3:latest",
]

# Local API endpoint (configure this to point to your local LLM server)
LOCAL_API_URL = "http://192.168.1.20:11434/api/generate"

# Legal/About pages: each has own slug, db column, prompt, and button
DOMAIN_PAGE_SLUGS = [
    "about-us", "terms-of-use", "privacy-policy", "gdpr-policy",
    "cookie-policy", "copyright-policy", "disclaimer", "contact-us",
]
PAGE_SLUG_TO_COLUMN = {
    "about-us": "domain_page_about_us",
    "terms-of-use": "domain_page_terms_of_use",
    "privacy-policy": "domain_page_privacy_policy",
    "gdpr-policy": "domain_page_gdpr_policy",
    "cookie-policy": "domain_page_cookie_policy",
    "copyright-policy": "domain_page_copyright_policy",
    "disclaimer": "domain_page_disclaimer",
    "contact-us": "domain_page_contact_us",
}

DOMAIN_PAGE_THEMES_FALLBACK = [
    ("theme_1", "Theme 1 (Warm)"),
    ("theme_2", "Theme 2 (Modern)"),
]

DOMAIN_PAGE_TITLE_MAP = {
    "about-us": "About Us", "terms-of-use": "Terms Of Use", "privacy-policy": "Privacy Policy",
    "gdpr-policy": "GDPR Policy", "cookie-policy": "Cookie Policy", "copyright-policy": "Copyright Policy",
    "disclaimer": "Disclaimer", "contact-us": "Contact Us",
}

LEGAL_SLUGS = ["terms-of-use", "privacy-policy", "gdpr-policy", "cookie-policy", "copyright-policy", "disclaimer"]


def _domain_url_to_display_name(url_or_name):
    """Return display name from domain URL (website name only, no TLD).

    Examples:
    - domaine1.com -> domaine1
    - domaine1.art -> domaine1
    - blog.domaine1.com -> domaine1
    - domaine1.co.uk -> domaine1
    """
    raw = (url_or_name or "").strip()
    if not raw:
        return "Recipe Blog"
    host = re.sub(r"^https?://", "", raw).split("/")[0].split("?")[0]
    if host.lower().startswith("www."):
        host = host[4:]
    host = host.split(":")[0]  # drop port if present
    labels = [p for p in host.split(".") if p]
    if not labels:
        return "Recipe Blog"
    if len(labels) == 1:
        return labels[0].strip() or "Recipe Blog"

    low = [l.lower() for l in labels]
    # Handle common "second-level TLD" patterns like co.uk, com.au, org.nz, etc.
    if len(labels) >= 3 and low[-2] in ("co", "com", "org", "net") and low[-1] in ("uk", "au", "nz"):
        return labels[-3].strip() or "Recipe Blog"

    # Default: second-level domain (label before the TLD)
    return labels[-2].strip() or "Recipe Blog"


def _domain_fonts_to_config(domain_fonts_raw):
    """Parse domain_fonts JSON and return config['fonts'] dict for article/site parts."""
    fonts = dict(DEFAULT_DOMAIN_FONTS)
    raw = (domain_fonts_raw or "").strip()
    if raw:
        try:
            df = json.loads(raw)
            if isinstance(df, dict):
                for k, v in df.items():
                    if v is not None and str(v).strip():
                        fonts[k] = str(v).strip()
        except (json.JSONDecodeError, TypeError):
            pass
    hf = fonts.get("heading_family") or "Playfair Display"
    bf = fonts.get("body_family") or "Inter"
    cfg = {
        "heading": {
            "family": hf,
            "sizes": {
                "h1": fonts.get("heading_h1") or "2.5rem",
                "h2": fonts.get("heading_h2") or "1.875rem",
                "h3": fonts.get("heading_h3") or "1.5rem",
            },
        },
        "body": {
            "family": bf,
            "size": fonts.get("body_size") or "1rem",
            "line_height": float(fonts.get("body_line_height") or 1.7),
        },
    }
    # Part-specific entries so part_font("header") etc. get domain fonts
    def _ff(name, generic):
        return f'"{name}", {generic}' if " " in name else f"{name}, {generic}"
    def _gfont_url(name):
        if not name or name in ("Georgia", "Arial"):
            return ""
        encoded = name.replace(" ", "+")
        return f"https://fonts.googleapis.com/css2?family={encoded}:wght@400;500;600;700&display=swap"
    for part in ("header", "footer", "category", "index"):
        cfg[part] = {"family": _ff(hf, "serif"), "cdn": _gfont_url(hf)}
    for part in ("side_article", "writer"):
        cfg[part] = {"family": _ff(bf, "sans-serif"), "cdn": _gfont_url(bf)}
    # domain_page inherits same as header (heading font) so About/Legal/Contact match the site
    cfg["domain_page"] = {"family": _ff(hf, "serif"), "cdn": _gfont_url(hf)}
    return cfg
RANDOM_COLOR_PALETTES = [
    # Modern Green (Fresh & Clean)
    {"primary": "#2ecc71", "secondary": "#27ae60", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Ocean Blue (Professional)
    {"primary": "#3498db", "secondary": "#2980b9", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Coral (Warm & Inviting)
    {"primary": "#e74c3c", "secondary": "#c0392b", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Purple (Creative)
    {"primary": "#9b59b6", "secondary": "#8e44ad", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Teal (Calm & Modern)
    {"primary": "#1abc9c", "secondary": "#16a085", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Orange (Energetic)
    {"primary": "#f39c12", "secondary": "#e67e22", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Navy Blue (Trustworthy)
    {"primary": "#34495e", "secondary": "#2c3e50", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Rose (Elegant)
    {"primary": "#e91e63", "secondary": "#c2185b", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Amber (Warm)
    {"primary": "#ff9800", "secondary": "#f57c00", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
    # Indigo (Deep & Rich)
    {"primary": "#3f51b5", "secondary": "#303f9f", "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#333333", "border": "#E0E0E0"},
]

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
_bulk_progress = {}  # job_id -> { status, current_title, message, ok, failed, type, group_id?, mode, created_at }
_BULK_HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bulk_jobs_history.json")

# Authentication helpers
def get_current_user():
    """Get current logged-in user from session."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, username, email, is_admin, is_active FROM users WHERE id = ?", (user_id,))
        return dict_row(cur.fetchone())

def login_required(f):
    """Decorator to require login for routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for("login", next=request.url))
        if not user.get("is_active"):
            session.clear()
            return redirect(url_for("login", error="Account is inactive"))
        
        # Check if profile is complete for admin pages and operations
        current_path = request.path
        
        # Paths that are allowed without profile completion
        allowed_paths = ['/profile', '/logout', '/login', '/register', '/static']
        is_allowed = any(current_path.startswith(path) for path in allowed_paths)
        
        # Check if this is an admin page or operation that requires profile completion
        requires_profile = (
            current_path.startswith('/admin') or 
            current_path.startswith('/database-management') or
            current_path.startswith('/preview-website') or
            current_path.startswith('/api/')
        )
        
        # Block access if profile is incomplete (except for allowed paths)
        if requires_profile and not is_allowed:
            if not is_profile_complete(user["id"]):
                # For API calls, return JSON error instead of redirect
                if current_path.startswith('/api/'):
                    return jsonify({"success": False, "error": "Please complete your profile settings first"}), 403
                # For page requests, redirect to profile
                return redirect(url_for("profile") + "?error=" + urllib.parse.quote("Please complete your profile settings before accessing this page"))
        
        return f(*args, **kwargs)
    return decorated_function

def get_user_api_keys(user_id):
    """Get user's API keys from database."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT * FROM user_api_keys WHERE user_id = ?", (user_id,))
        keys = dict_row(cur.fetchone())
        return keys if keys else {}

def is_profile_complete(user_id):
    """Check if user has completed required profile fields."""
    keys = get_user_api_keys(user_id)
    if not keys:
        return False
    
    # Required fields (OpenRouter and Local are optional)
    required_fields = [
        'openai_api_key',
        'openai_model',
        'midjourney_api_token',
        'midjourney_channel_id',
        'r2_account_id',
        'r2_access_key_id',
        'r2_secret_access_key',
        'r2_bucket_name',
        'r2_public_url',
        'cloudflare_account_id',
        'cloudflare_api_token',
        'default_categories'
    ]
    
    for field in required_fields:
        value = keys.get(field)
        if not value or not str(value).strip():
            return False
    
    return True

def get_user_domain_ids(user_id, is_admin=False):
    """Get list of domain IDs accessible by user."""
    if is_admin:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id FROM domains")
            return [dict_row(r)["id"] for r in cur.fetchall()]
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_id FROM user_domains WHERE user_id = ?", (user_id,))
        return [dict_row(r)["domain_id"] for r in cur.fetchall()]

def get_user_group_ids(user_id, is_admin=False):
    """Get list of group IDs accessible by user (via user_groups table or their domains)."""
    if is_admin:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id FROM `groups`")
            return [dict_row(r)["id"] for r in cur.fetchall()]
    
    with get_connection() as conn:
        # Get groups directly assigned to user
        cur = db_execute(conn, "SELECT group_id FROM user_groups WHERE user_id = ?", (user_id,))
        direct_groups = [dict_row(r)["group_id"] for r in cur.fetchall()]
        
        # Also get groups via domains (for backward compatibility)
        cur = db_execute(conn, """
            SELECT DISTINCT d.group_id 
            FROM user_domains ud
            JOIN domains d ON d.id = ud.domain_id
            WHERE ud.user_id = ? AND d.group_id IS NOT NULL
        """, (user_id,))
        domain_groups = [dict_row(r)["group_id"] for r in cur.fetchall()]
        
        # Combine and deduplicate
        all_groups = list(set(direct_groups + domain_groups))
        
        # Include all parent groups recursively
        def get_all_parents(gid):
            result = [gid]
            cur = db_execute(conn, "SELECT parent_group_id FROM `groups` WHERE id = ?", (gid,))
            row = dict_row(cur.fetchone())
            if row and row.get("parent_group_id"):
                result.extend(get_all_parents(row["parent_group_id"]))
            return result
        
        # Include all child groups recursively
        def get_all_children(gid):
            result = [gid]
            cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
            children = [dict_row(r)["id"] for r in cur.fetchall()]
            for child_id in children:
                result.extend(get_all_children(child_id))
            return result
        
        # Expand to include parents and children
        expanded = set()
        for gid in all_groups:
            expanded.update(get_all_parents(gid))
            expanded.update(get_all_children(gid))
        
        return list(expanded)

def get_user_config_for_api(user_id):
    """Get user's API configuration from database only."""
    keys = get_user_api_keys(user_id)
    
    # Build config dict with user keys
    config = {}
    
    # OpenAI
    config["openai_api_key"] = keys.get("openai_api_key")
    config["openai_model"] = keys.get("openai_model") or "gpt-4o-mini"
    
    # OpenRouter
    config["openrouter_api_key"] = keys.get("openrouter_api_key")
    config["openrouter_model"] = keys.get("openrouter_model") or "openai/gpt-oss-120b"
    
    # Local
    config["local_api_url"] = keys.get("local_api_url") or "http://localhost:11434/api/generate"
    config["local_models"] = keys.get("local_models") or "qwen3:8b,llama3.2:3b"
    
    # Midjourney
    config["midjourney_api_token"] = keys.get("midjourney_api_token")
    config["midjourney_channel_id"] = keys.get("midjourney_channel_id")
    
    # R2
    config["r2_account_id"] = keys.get("r2_account_id")
    config["r2_access_key_id"] = keys.get("r2_access_key_id")
    config["r2_secret_access_key"] = keys.get("r2_secret_access_key")
    config["r2_bucket_name"] = keys.get("r2_bucket_name")
    config["r2_public_url"] = keys.get("r2_public_url")
    
    # Cloudflare
    config["cloudflare_account_id"] = keys.get("cloudflare_account_id")
    config["cloudflare_api_token"] = keys.get("cloudflare_api_token")
    
    return config

def check_user_has_required_keys(user_id, operation_type="content"):
    """Check if user has required API keys for the operation."""
    config = get_user_config_for_api(user_id)
    
    if operation_type == "content":
        # Need at least one AI provider
        has_openai = bool(config.get("openai_api_key"))
        has_openrouter = bool(config.get("openrouter_api_key"))
        has_local = bool(config.get("local_api_url"))
        return has_openai or has_openrouter or has_local, "No AI provider API keys configured. Please add OpenAI, OpenRouter, or Local API keys in your profile."
    
    elif operation_type == "image":
        # Need Midjourney
        has_midjourney = bool(config.get("midjourney_api_token") and config.get("midjourney_channel_id"))
        return has_midjourney, "Midjourney API keys not configured. Please add them in your profile."
    
    elif operation_type == "r2":
        # Need R2
        has_r2 = bool(config.get("r2_account_id") and config.get("r2_access_key_id") and config.get("r2_secret_access_key"))
        return has_r2, "Cloudflare R2 keys not configured. Please add them in your profile."
    
    elif operation_type == "cloudflare":
        # Need Cloudflare
        has_cf = bool(config.get("cloudflare_account_id") and config.get("cloudflare_api_token"))
        return has_cf, "Cloudflare API keys not configured. Please add them in your profile."
    
    return True, ""


def _load_bulk_history():
    """Load persisted bulk job history from disk."""
    try:
        if not os.path.isfile(_BULK_HISTORY_PATH):
            return {}
        with open(_BULK_HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_bulk_history(history):
    """Persist bulk job history to disk."""
    try:
        # Keep file bounded to newest 500 jobs.
        items = []
        for jid, p in (history or {}).items():
            if isinstance(p, dict):
                items.append((jid, p))
        items.sort(key=lambda kv: float((kv[1] or {}).get("created_at") or 0), reverse=True)
        trimmed = dict(items[:500])
        with open(_BULK_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(trimmed, f, ensure_ascii=False)
    except Exception:
        pass


_bulk_history = _load_bulk_history()

# On startup, any jobs that were left "running" in history are actually dead because the server restarted.
history_changed_on_startup = False
for jid, p in list(_bulk_history.items()):
    if isinstance(p, dict) and p.get("status") == "running":
        p["status"] = "error"
        p["message"] = "Server restarted"
        history_changed_on_startup = True

if history_changed_on_startup:
    _save_bulk_history(_bulk_history)


@app.route("/favicon.ico")
def favicon():
    """Avoid 404 for favicon requests."""
    return "", 204
_bulk_cancel = {}  # job_id -> True if cancel requested


def _app_log(log_type, success, message, reason=None, title_id=None, domain_id=None, group_id=None, job_id=None, application="multi-domain", details=None):
    """Insert into app_logs. log_type: run, article, image, pin, template_change, etc. success: bool."""
    try:
        details_json = json.dumps(details, ensure_ascii=False) if details is not None and not isinstance(details, str) else (details or "")
        with get_connection() as conn:
            db_execute(conn, """
                INSERT INTO app_logs (log_type, application, success, title_id, domain_id, group_id, job_id, message, reason, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (log_type, application, 1 if success else 0, title_id, domain_id, group_id, job_id, (message or "")[:500], (reason or "")[:1000] if reason else None, details_json[:10000] if details_json else None))
    except Exception as e:
        log.warning("[app_log] failed to insert: %s", e)


def base_layout(content, title, nav_extra=None):
    nav_extra_html = nav_extra or ""
    
    # Add user info to navbar
    user = get_current_user()
    user_nav = ""
    if user:
        username = html.escape(user.get("username", "User"))
        admin_badge = '<span class="badge bg-warning text-dark ms-1">Admin</span>' if user.get("is_admin") else ""
        user_nav = f'''
        <span class="navbar-text text-white me-3">{username}{admin_badge}</span>
        <a class="nav-link" href="/profile">Profile</a>
        '''
        if user.get("is_admin"):
            user_nav += '<a class="nav-link" href="/admin/users">Users</a>'
        user_nav += '<a class="nav-link" href="/logout">Logout</a>'
    
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
  .page-body {{ width: 100%; max-width: 100%; padding: 0 1rem; }}
  .groups-scroll-wrapper {{ -webkit-overflow-scrolling: touch; }}
  .title-row {{ padding: 0.3rem 0.5rem; border-radius: 0.375rem; transition: background 0.15s; }}
  .title-row:hover {{ background: rgba(0,0,0,.04); }}
  .title-text {{ font-size: 0.75rem; font-weight: 500; color: #212529; flex: 1; min-width: 0; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .btn-group-custom {{ display: flex; flex-wrap: wrap; gap: 0.35rem; justify-content: flex-end; }}
  .btn-group-custom .btn {{ white-space: nowrap; padding: 0.25rem 0.5rem; font-size: 0.75rem; }}
  .card-title-domain {{ font-size: 0.95rem; margin: 0; }}
  .card-subtitle-domain {{ font-size: 0.75rem; opacity: 0.9; }}
  .status-dots {{ display: flex; gap: 4px; align-items: center; margin-right: 6px; flex-shrink: 0; }}
  .status-dot {{ width: 6px; height: 6px; border-radius: 50%; }}
  .status-dot.all {{ background: #198754; }}
  .status-dot.main {{ background: #0d6efd; }}
  .status-dot.ing {{ background: #fd7e14; }}
  .run-domain-actions {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 4px; }}
  .run-domain-action-pill {{ display: inline-flex; flex-direction: column; align-items: center; gap: 2px; padding: 4px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 600; }}
  .run-domain-action-pill.pill-success {{ background: #d1e7dd; border: 1px solid #198754; }}
  .run-domain-action-pill.pill-warning {{ background: #fff3cd; border: 1px solid #fd7e14; }}
  .run-domain-action-pill.pill-info {{ background: #cff4fc; border: 1px solid #0d6efd; }}
  .run-domain-action-pill.pill-empty {{ background: #fff; border: 1px solid #dee2e6; }}
  .run-domain-action-pill .pill-label {{ font-size: 0.7rem; }}
  .run-domain-action-pill .pill-btns {{ display: flex; gap: 2px; flex-wrap: wrap; justify-content: center; }}
  .run-domain-action-pill .pill-btns .btn {{ padding: 0.1rem 0.25rem; font-size: 0.6rem; }}
  .run-domain-action-pill .pill-hint {{ display: block; font-size: 0.55rem; line-height: 1.1; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 1px; }}
  .progress-workflow-section {{ background: #f8f9fa; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.75rem; border: 1px solid #e9ecef; }}
  .progress-workflow-section .workflow-label {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6c757d; font-weight: 700; margin-bottom: 0.5rem; }}
  .workflow-pipeline {{ display: flex; align-items: center; gap: 0; flex-wrap: wrap; }}
  .workflow-node {{ display: flex; align-items: center; gap: 0.35rem; padding: 0.5rem 0.75rem; border-radius: 8px; font-size: 0.8rem; font-weight: 600; background: #e9ecef; color: #6c757d; border: 2px solid #dee2e6; min-width: 90px; justify-content: center; }}
  .workflow-node.state-done {{ background: #d1e7dd; color: #198754; border-color: #198754; }}
  .workflow-node.state-running {{ background: #cfe2ff; color: #0d6efd; border-color: #0d6efd; box-shadow: 0 0 0 3px rgba(13,110,253,0.25); animation: workflow-pulse 1.2s ease-in-out infinite; }}
  .workflow-node.state-error {{ background: #f8d7da; color: #dc3545; border-color: #dc3545; }}
  .workflow-node .node-num {{ font-size: 0.65rem; opacity: 0.9; background: rgba(0,0,0,0.08); padding: 2px 5px; border-radius: 4px; }}
  .workflow-node.state-done .node-num {{ background: rgba(25,135,84,0.2); }}
  .workflow-connector {{ width: 24px; height: 3px; background: #dee2e6; flex-shrink: 0; border-radius: 2px; }}
  .workflow-connector.active {{ background: #198754; }}
  @keyframes workflow-pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.8; }} }}
</style></head>
<body class="bg-light">
<nav class="navbar navbar-expand navbar-dark bg-dark mb-0">
  <div class="container-fluid px-3">
    <a class="navbar-brand fw-bold" href="/admin/domains">Multi-Domain</a>
    <div class="navbar-nav ms-auto">
      {nav_extra_html}
      <a class="nav-link" href="/admin/domains">Domains</a>
      <a class="nav-link" href="/admin/titles">Titles</a>
      {f'<a class="nav-link" href="/admin/users">👥 Users</a>' if session.get('is_admin') else ''}
      <a class="nav-link" href="/profile">👤 {session.get('username', 'Profile')}</a>
      <a class="nav-link" href="/logout">Logout</a>
    </div>
  </div>
</nav>
<div class="container-fluid page-body py-4">{content}</div>
<div id="globalLoadingOverlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:9999;align-items:center;justify-content:center;">
  <div class="spinner-border text-light" role="status" style="width:3rem;height:3rem;"><span class="visually-hidden">Loading...</span></div>
</div>
<script>
function showGlobalLoading() {{
  var el = document.getElementById('globalLoadingOverlay');
  if (el) {{ el.style.display = 'flex'; }}
}}
function hideGlobalLoading() {{
  var el = document.getElementById('globalLoadingOverlay');
  if (el) {{ el.style.display = 'none'; }}
}}
function fetchApi(url, data) {{
  showGlobalLoading();
  fetch(url, {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify(data) }})
    .then(r => r.json())
    .then(d => {{ alert(d.success ? 'OK' : 'Error: ' + (d.error || '')); if(d.success && typeof refreshGroups==='function') refreshGroups(); else if(d.success) location.reload(); }})
    .catch(e => alert('Error: ' + e))
    .finally(function() {{ hideGlobalLoading(); }});
}}
function viewContent(tid) {{
  showGlobalLoading();
  fetch('/api/article-content/' + tid).then(r=>r.json()).then(d=>{{
    if(d.error) {{ alert(d.error); return; }}
    var raw = (d.article_html || '').toString();
    var html = raw.startsWith('<') ? raw : raw.replace(/\\n/g, '<br>');
    var css = (d.article_css || '').toString().trim();
    if(css) html = '<style>' + css + '</style><div class="article-preview">' + (html || '') + '</div>';
    var meta = (d.model_used || d.generated_at || d.generation_time_seconds != null) ? '<p class="mb-2 small text-muted">Model: ' + (d.model_used || '-') + (d.generated_at ? ' &bull; Generated: ' + d.generated_at : '') + (d.generation_time_seconds != null ? ' &bull; Time: ' + d.generation_time_seconds + 's' : '') + '</p>' : '';
    var editLink = '<p class="mb-2"><a href="/article-html-editor?title_id='+tid+'" target="_blank" class="btn btn-sm btn-outline-primary">Edit HTML/CSS (no regeneration)</a></p>';
    document.getElementById('viewModalBody').innerHTML = meta + editLink + (html || '<em>Empty</em>');
    document.getElementById('viewModalTitle').textContent = 'Content';
    new bootstrap.Modal(document.getElementById('viewModal')).show();
  }}).finally(function() {{ hideGlobalLoading(); }});
}}
function viewRecipe(tid) {{
  showGlobalLoading();
  fetch('/api/article-content/' + tid).then(r=>r.json()).then(d=>{{
    if(d.error) {{ alert(d.error); return; }}
    var r = d.recipe || '';
    document.getElementById('viewModalBody').innerHTML = (typeof r==='string' && r.startsWith('{{')) ? '<pre>' + r + '</pre>' : r.replace(/\\n/g, '<br>') || '<em>Empty</em>';
    document.getElementById('viewModalTitle').textContent = 'Recipe';
    new bootstrap.Modal(document.getElementById('viewModal')).show();
  }}).finally(function() {{ hideGlobalLoading(); }});
}}
function viewDomainSingle(tid, label) {{
  showGlobalLoading();
  fetch('/api/article-content/' + tid).then(r=>r.json()).then(d=>{{
    if(d.error) {{ alert(d.error); return; }}
    var html = '';
    var raw = (d.article_html || '').toString();
    var adisp = raw.startsWith('<') ? raw : raw.replace(/\\n/g,'<br>') || '<em>Empty</em>';
    var css = (d.article_css || '').toString().trim();
    if(css) adisp = '<style>' + css + '</style><div class="article-preview">' + adisp + '</div>';
    if(d.model_used || d.generated_at || d.generation_time_seconds != null) html += '<div class="mb-2 small text-muted">Model: ' + (d.model_used || '-') + (d.generated_at ? ' &bull; Generated: ' + d.generated_at : '') + (d.generation_time_seconds != null ? ' &bull; Time: ' + d.generation_time_seconds + 's' : '') + '</div>';
    html += '<div class="mb-3"><strong>Article</strong><div class="border rounded p-2">'+adisp+'</div></div>';
    var r = (d.recipe || '').toString();
    var rdisp = (r.startsWith('{{') ? '<pre>'+r+'</pre>' : r.replace(/\\n/g,'<br>')) || '<em>Empty</em>';
    html += '<div class="mb-3"><strong>Recipe</strong><div class="border rounded p-2">'+rdisp+'</div></div>';
    var mainUrl = (d.main_image || '').trim();
    if(mainUrl && mainUrl.startsWith('http')) html += '<div class="mb-3"><strong>Main image</strong><div class="border rounded p-2"><img src="'+mainUrl.replace(/"/g,'&quot;')+'" style="max-width:100%;height:auto" alt=""></div></div>';
    else html += '<div class="mb-3"><strong>Main image</strong><div class="text-muted">None</div></div>';
    var ingUrl = (d.ingredient_image || '').trim();
    if(ingUrl && ingUrl.startsWith('http')) html += '<div class="mb-3"><strong>Ingredient image</strong><div class="border rounded p-2"><img src="'+ingUrl.replace(/"/g,'&quot;')+'" style="max-width:100%;height:auto" alt=""></div></div>';
    else html += '<div class="mb-3"><strong>Ingredient image</strong><div class="text-muted">None</div></div>';
    var pinUrl = (d.pin_image || '').trim();
    if(pinUrl && pinUrl.startsWith('http')) html += '<div class="mb-3"><strong>Pin image</strong><div class="border rounded p-2"><img src="'+pinUrl.replace(/"/g,'&quot;')+'" style="max-width:100%;height:auto" alt=""></div></div>';
    else html += '<div class="mb-3"><strong>Pin image</strong><div class="text-muted">None</div></div>';
    document.getElementById('viewModalBody').innerHTML = html;
    document.getElementById('viewModalTitle').textContent = 'Domain ' + (label||'') + ' – Article, Recipe, Images';
    new bootstrap.Modal(document.getElementById('viewModal')).show();
  }}).finally(function() {{ hideGlobalLoading(); }});
}}
function viewImage(url, title) {{
  if(!url || !url.startsWith('http')) {{ alert('No image'); return; }}
  document.getElementById('viewModalBody').innerHTML = '<img src="'+url.replace(/"/g,'&quot;')+'" style="max-width:100%; height:auto;" alt="">';
  document.getElementById('viewModalTitle').textContent = title || 'Image';
  new bootstrap.Modal(document.getElementById('viewModal')).show();
}}
function viewImagesAll(urls, title, labelsStr) {{
  var arr = (typeof urls==='string') ? (urls ? urls.split('|||') : []) : (urls||[]);
  var labels = (labelsStr && labelsStr.split('|||')) || ['A','B','C','D'];
  var html = '<div class="d-flex flex-wrap gap-3">';
  for(var i=0;i<4;i++) {{
    var u = arr[i] || '';
    var l = labels[i] || ('Domain '+(i+1));
    if(u && u.startsWith('http'))
      html += '<div class="text-center"><div class="small fw-bold mb-1">'+l+'</div><img src="'+u.replace(/"/g,'&quot;')+'" style="max-width:200px;height:auto;" alt=""></div>';
    else if(l)
      html += '<div class="text-center"><div class="small fw-bold mb-1">'+l+'</div><div class="text-muted small">No image</div></div>';
  }}
  html += '</div>';
  document.getElementById('viewModalBody').innerHTML = html;
  document.getElementById('viewModalTitle').textContent = title || 'Images';
  new bootstrap.Modal(document.getElementById('viewModal')).show();
}}
function viewContentAll(idsStr, labelsStr) {{
  var ids = (idsStr||'').split(',').filter(function(x){{ return x; }});
  if(ids.length===0) {{ alert('No data'); return; }}
  var labels = (labelsStr && labelsStr.split('|||')) || ['A','B','C','D'];
  showGlobalLoading();
  Promise.all(ids.map(function(id){{ return fetch('/api/article-content/'+id).then(function(r){{ return r.json(); }}); }}))
    .then(function(results){{
      var html = '';
      results.forEach(function(d,i){{
        var raw = (d.article_html || '').toString();
        var disp = raw.startsWith('<') ? raw : raw.replace(/\\n/g,'<br>') || '<em>Empty</em>';
        var css = (d.article_css || '').toString().trim();
        if(css) disp = '<style>' + css + '</style><div class="article-preview">' + disp + '</div>';
        var l = labels[i] || ('Domain '+(i+1));
        var meta = (d.model_used || d.generated_at || d.generation_time_seconds != null) ? '<span class="small text-muted">Model: ' + (d.model_used || '-') + (d.generated_at ? ' &bull; ' + d.generated_at : '') + (d.generation_time_seconds != null ? ' &bull; ' + d.generation_time_seconds + 's' : '') + '</span>' : '';
        html += '<div class="mb-3"><strong>'+l+'</strong>' + (meta ? ' ' + meta : '') + '<div class="border rounded p-2">'+disp+'</div></div>';
      }});
      document.getElementById('viewModalBody').innerHTML = html || '<em>Empty</em>';
      document.getElementById('viewModalTitle').textContent = 'Article / Content';
      new bootstrap.Modal(document.getElementById('viewModal')).show();
    }})
    .catch(function(e){{ alert('Error: '+e); }})
    .finally(function() {{ hideGlobalLoading(); }});
}}
function viewRecipeAll(idsStr, labelsStr) {{
  var ids = (idsStr||'').split(',').filter(function(x){{ return x; }});
  if(ids.length===0) {{ alert('No data'); return; }}
  var labels = (labelsStr && labelsStr.split('|||')) || ['A','B','C','D'];
  showGlobalLoading();
  Promise.all(ids.map(function(id){{ return fetch('/api/article-content/'+id).then(function(r){{ return r.json(); }}); }}))
    .then(function(results){{
      var html = '';
      results.forEach(function(d,i){{
        var r = (d.recipe || '').toString();
        var disp = (r.startsWith('{{') ? '<pre>'+r+'</pre>' : r.replace(/\\n/g,'<br>')) || '<em>Empty</em>';
        var l = labels[i] || ('Domain '+(i+1));
        html += '<div class="mb-3"><strong>'+l+'</strong><div class="border rounded p-2">'+disp+'</div></div>';
      }});
      document.getElementById('viewModalBody').innerHTML = html || '<em>Empty</em>';
      document.getElementById('viewModalTitle').textContent = 'Recipe';
      new bootstrap.Modal(document.getElementById('viewModal')).show();
    }})
    .catch(function(e){{ alert('Error: '+e); }})
    .finally(function() {{ hideGlobalLoading(); }});
}}
function _updateBulkModalAiHints(prefix) {{
  var sel = document.getElementById(prefix + 'AiProvider');
  var provider = (sel && sel.value) ? sel.value : 'openrouter';
  var wrap = document.getElementById(prefix + 'OpenRouterWrap');
  var modeSelect = document.querySelector('input[name="' + prefix + 'OpenRouterMode"][value="select"]');
  var modelsEl = document.getElementById(prefix + 'OpenRouterModels');
  if (wrap) wrap.style.display = (provider === 'openrouter') ? 'block' : 'none';
  if (modelsEl) modelsEl.style.display = (provider === 'openrouter' && modeSelect && modeSelect.checked) ? 'block' : 'none';
  /* Wire radio-button toggles so model select shows/hides when switching Rotation ↔ Select */
  document.querySelectorAll('input[name="' + prefix + 'OpenRouterMode"]').forEach(function(radio) {{
    if (radio._orWired) return;
    radio._orWired = true;
    radio.addEventListener('change', function() {{
      var ms = document.getElementById(prefix + 'OpenRouterModels');
      if (ms) ms.style.display = (this.value === 'select') ? 'block' : 'none';
    }});
  }});
  if (provider === 'openrouter' && modelsEl && (!modelsEl.options || modelsEl.options.length === 0) && !window._openRouterModelsLoaded) {{
    window._openRouterModelsLoaded = true;
    fetch('/api/openrouter-models').then(function(r){{ return r.json(); }}).then(function(d){{
      var models = d.models || [];
      window._openRouterModelsList = models;
      ['bulkModal','bulkGroupModal','bulkAllGroupsModal'].forEach(function(p){{
        var m = document.getElementById(p + 'OpenRouterModels');
        if (m) {{ m.innerHTML = ''; models.forEach(function(id){{ var o = document.createElement('option'); o.value = id; o.textContent = id; m.appendChild(o); }}); }}
      }});
    }}).catch(function(){{}});
  }}
  fetch('/api/ai-config?provider=' + encodeURIComponent(provider)).then(function(r){{ return r.json(); }}).then(function(cfg) {{
    var hint = 'AI: ' + (cfg.label || cfg.provider + '/' + cfg.model);
    var btnIds = prefix === 'bulkModal' ? ['bulkModalBtnArticle','bulkModalBtnAll'] : prefix === 'bulkGroupModal' ? ['bulkGroupBtnArticle','bulkGroupBtnAll'] : ['bulkAllGroupsBtnArticle','bulkAllGroupsBtnAll'];
    btnIds.forEach(function(id) {{ var b = document.getElementById(id); if (b) b.title = (b.textContent || '') + ' — ' + hint; }});
  }}).catch(function(){{}});
}}
function _getOpenRouterModelsParam(prefix) {{
  var sel = document.getElementById(prefix + 'AiProvider');
  if (!sel || sel.value !== 'openrouter') return '';
  var modeEl = document.querySelector('input[name="' + prefix + 'OpenRouterMode"][value="select"]');
  if (!modeEl || !modeEl.checked) return '';
  var modelsEl = document.getElementById(prefix + 'OpenRouterModels');
  if (!modelsEl || !modelsEl.options) return '';
  var selected = [];
  for (var i = 0; i < modelsEl.options.length; i++) {{ if (modelsEl.options[i].selected) selected.push(modelsEl.options[i].value); }}
  return selected.length ? '&openrouter_models=' + encodeURIComponent(selected.join(',')) : '';
}}
function _updateBulkModalButtons(d) {{
  var btnArticle = document.getElementById('bulkModalBtnArticle');
  var btnImages = document.getElementById('bulkModalBtnImages');
  var btnAll = document.getElementById('bulkModalBtnAll');
  var sc = (document.querySelector('input[name="bulkModalScopeContent"]:checked') || {{}}).value || 'empty_only';
  var si = (document.querySelector('input[name="bulkModalScopeImages"]:checked') || {{}}).value || 'empty_only';
  var nc = sc === 'override' ? (d.total || 0) : (d.no_html_css || 0);
  var ni = si === 'override' ? (d.total || 0) : (d.no_images || 0);
  if (btnArticle) btnArticle.textContent = 'Run content(' + nc + ')';
  if (btnImages) btnImages.textContent = 'Run images (' + ni + ')';
  if (btnAll) btnAll.textContent = 'Run all (' + nc + ', ' + ni + ')';
}}
function openBulkModal(taId) {{
  document.getElementById('bulkModalTitleId').value = taId;
  var btnArticle = document.getElementById('bulkModalBtnArticle');
  var btnImages = document.getElementById('bulkModalBtnImages');
  var btnAll = document.getElementById('bulkModalBtnAll');
  if (btnArticle) btnArticle.textContent = 'Run content';
  if (btnImages) btnImages.textContent = 'Run images';
  if (btnAll) btnAll.textContent = 'Run all (content first, then images)';
  fetch('/api/bulk-row-counts?title_id=' + encodeURIComponent(taId)).then(function(r){{ return r.json(); }}).then(function(d) {{
    window._bulkModalCounts = d;
    _updateBulkModalButtons(d);
    _updateBulkModalAiHints('bulkModal');
    var handler = function(){{ _updateBulkModalButtons(window._bulkModalCounts || {{}}); }};
    ['bulkModalScopeContent','bulkModalScopeImages'].forEach(function(name){{
      document.querySelectorAll('input[name="' + name + '"]').forEach(function(el){{
        if (window._bulkModalScopeHandler) el.removeEventListener('change', window._bulkModalScopeHandler);
        el.addEventListener('change', handler);
      }});
    }});
    window._bulkModalScopeHandler = handler;
    var aiSel = document.getElementById('bulkModalAiProvider');
    if (aiSel) aiSel.addEventListener('change', function(){{ _updateBulkModalAiHints('bulkModal'); }});
    document.querySelectorAll('input[name="bulkModalOpenRouterMode"]').forEach(function(r){{ r.addEventListener('change', function(){{ _updateBulkModalAiHints('bulkModal'); }}); }});
  }}).catch(function(){{}});
  new bootstrap.Modal(document.getElementById('bulkModal')).show();
}}
function runBulk(mode) {{
  var tid = document.getElementById('bulkModalTitleId').value;
  if(!tid) return;
  bootstrap.Modal.getInstance(document.getElementById('bulkModal')).hide();
  var scEl = document.querySelector('input[name="bulkModalScopeContent"]:checked');
  var siEl = document.querySelector('input[name="bulkModalScopeImages"]:checked');
  var scopeContent = (scEl && scEl.value) || 'override';
  var scopeImages = (siEl && siEl.value) || 'override';
    var aiProvider = (document.getElementById('bulkModalAiProvider') || {{}}).value || '';
    var url = '/api/bulk-run?title_id=' + tid + '&mode=' + mode + '&scope_content=' + scopeContent + '&scope_images=' + scopeImages + (aiProvider ? '&ai_provider=' + encodeURIComponent(aiProvider) : '') + _getOpenRouterModelsParam('bulkModal');
  fetch(url, {{ method: 'POST' }}).then(r=>r.json()).then(d=>{{
    if (typeof notifyTaskComplete==='function' && document.hidden) notifyTaskComplete('Run', d.success ? 'done' : 'error', d.success ? 'Done' : d.error);
    alert(d.success ? 'Done' : 'Error: ' + (d.error||''));
    if(d.success && typeof refreshAfterRun==='function') refreshAfterRun();
  }});
}}
function _updateBulkGroupModalButtons(d) {{
  var btnArticle = document.getElementById('bulkGroupBtnArticle');
  var btnImages = document.getElementById('bulkGroupBtnImages');
  var btnAll = document.getElementById('bulkGroupBtnAll');
  var sc = (document.querySelector('input[name="bulkGroupModalScopeContent"]:checked') || {{}}).value || 'empty_only';
  var si = (document.querySelector('input[name="bulkGroupModalScopeImages"]:checked') || {{}}).value || 'empty_only';
  var nc = sc === 'override' ? (d.total || 0) : (d.no_html_css || 0);
  var ni = si === 'override' ? (d.total || 0) : (d.no_images || 0);
  if (btnArticle) btnArticle.textContent = 'Run content(' + nc + ')';
  if (btnImages) btnImages.textContent = 'Run images (' + ni + ')';
  if (btnAll) btnAll.textContent = 'Run all (' + nc + ', ' + ni + ')';
}}
function openBulkGroupModal(gid) {{
  document.getElementById('bulkGroupModalGroupId').value = gid;
  var btnArticle = document.getElementById('bulkGroupBtnArticle');
  var btnImages = document.getElementById('bulkGroupBtnImages');
  var btnAll = document.getElementById('bulkGroupBtnAll');
  if (btnArticle) btnArticle.textContent = 'Run content';
  if (btnImages) btnImages.textContent = 'Run images';
  if (btnAll) btnAll.textContent = 'Run all (content first, then images)';
  fetch('/api/bulk-group-counts?group_id=' + encodeURIComponent(gid)).then(function(r){{ return r.json(); }}).then(function(d) {{
    window._bulkGroupModalCounts = d;
    _updateBulkGroupModalButtons(d);
    _updateBulkModalAiHints('bulkGroupModal');
    var handler = function(){{ _updateBulkGroupModalButtons(window._bulkGroupModalCounts || {{}}); }};
    ['bulkGroupModalScopeContent','bulkGroupModalScopeImages'].forEach(function(name){{
      document.querySelectorAll('input[name="' + name + '"]').forEach(function(el){{
        if (window._bulkGroupModalScopeHandler) el.removeEventListener('change', window._bulkGroupModalScopeHandler);
        el.addEventListener('change', handler);
      }});
    }});
    window._bulkGroupModalScopeHandler = handler;
    var aiSel = document.getElementById('bulkGroupModalAiProvider');
    if (aiSel) aiSel.addEventListener('change', function(){{ _updateBulkModalAiHints('bulkGroupModal'); }});
    document.querySelectorAll('input[name="bulkGroupModalOpenRouterMode"]').forEach(function(r){{ r.addEventListener('change', function(){{ _updateBulkModalAiHints('bulkGroupModal'); }}); }});
  }}).catch(function(){{}});
  new bootstrap.Modal(document.getElementById('bulkGroupModal')).show();
}}
function runBulkGroupFromModal(mode) {{
  var gid = document.getElementById('bulkGroupModalGroupId').value;
  if(!gid) return;
  bootstrap.Modal.getInstance(document.getElementById('bulkGroupModal')).hide();
  var scEl = document.querySelector('input[name="bulkGroupModalScopeContent"]:checked');
  var siEl = document.querySelector('input[name="bulkGroupModalScopeImages"]:checked');
  var scopeContent = (scEl && scEl.value) || 'override';
  var scopeImages = (siEl && siEl.value) || 'override';
  var aiProvider = (document.getElementById('bulkGroupModalAiProvider') || {{}}).value || '';
  var url = '/api/bulk-run-group?group_id=' + gid + '&mode=' + mode + '&scope_content=' + scopeContent + '&scope_images=' + scopeImages + (aiProvider ? '&ai_provider=' + encodeURIComponent(aiProvider) : '') + _getOpenRouterModelsParam('bulkGroupModal');
  var asyncUrl = url + (url.indexOf('?')>=0 ? '&' : '?') + 'async=1';
  fetch(asyncUrl, {{ method: 'POST' }}).then(r=>r.json()).then(function(d){{
    if (d.error) {{ alert('Error: ' + d.error); return; }}
    if (d.success && d.job_id && typeof refreshRunningTasks==='function') refreshRunningTasks();
  }}).catch(function(e){{ alert('Error: ' + e); }});
  if (typeof refreshRunningTasks==='function') setTimeout(refreshRunningTasks, 500);
}}
function _updateBulkAllGroupsModalButtons(d) {{
  var btnArticle = document.getElementById('bulkAllGroupsBtnArticle');
  var btnImages = document.getElementById('bulkAllGroupsBtnImages');
  var btnAll = document.getElementById('bulkAllGroupsBtnAll');
  var sc = (document.querySelector('input[name="bulkAllGroupsModalScopeContent"]:checked') || {{}}).value || 'empty_only';
  var si = (document.querySelector('input[name="bulkAllGroupsModalScopeImages"]:checked') || {{}}).value || 'empty_only';
  var nc = sc === 'override' ? (d.total || 0) : (d.rows_needs_content != null ? d.rows_needs_content : d.no_html_css || 0);
  var ni = si === 'override' ? (d.total || 0) : (d.rows_needs_images != null ? d.rows_needs_images : d.no_images || 0);
  if (btnArticle) btnArticle.textContent = 'Run content(' + nc + ')';
  if (btnImages) btnImages.textContent = 'Run images (' + ni + ')';
  if (btnAll) btnAll.textContent = 'Run all (' + nc + ', ' + ni + ')';
}}
function openBulkGroupModal(groupId, groupName) {{
  var modal = document.getElementById('bulkGroupModal');
  var btnArticle = document.getElementById('bulkGroupBtnArticle');
  var btnImages = document.getElementById('bulkGroupBtnImages');
  var btnAll = document.getElementById('bulkGroupBtnAll');
  if (btnArticle) btnArticle.textContent = 'Run content';
  if (btnImages) btnImages.textContent = 'Run images';
  if (btnAll) btnAll.textContent = 'Run all (content first, then images)';
  document.getElementById('bulkGroupModalTitle').textContent = 'Run for group: ' + groupName;
  document.getElementById('bulkGroupModalGroupId').value = groupId;
  
  fetch('/api/bulk-group-counts?group_id=' + groupId).then(function(r){{ return r.json(); }}).then(function(d) {{
    window._bulkGroupModalCounts = d;
    _updateBulkGroupModalButtons(d);
    _updateBulkModalAiHints('bulkGroupModal');
    var handler = function(){{ _updateBulkGroupModalButtons(window._bulkGroupModalCounts || {{}}); }};
    ['bulkGroupModalScopeContent','bulkGroupModalScopeImages'].forEach(function(name){{
      document.querySelectorAll('input[name="' + name + '"]').forEach(function(el){{
        if (window._bulkGroupModalScopeHandler) el.removeEventListener('change', window._bulkGroupModalScopeHandler);
        el.addEventListener('change', handler);
      }});
    }});
    window._bulkGroupModalScopeHandler = handler;
    var aiSel = document.getElementById('bulkGroupModalAiProvider');
    if (aiSel) aiSel.addEventListener('change', function(){{ _updateBulkModalAiHints('bulkGroupModal'); }});
    document.querySelectorAll('input[name="bulkGroupModalOpenRouterMode"]').forEach(function(r){{ r.addEventListener('change', function(){{ _updateBulkModalAiHints('bulkGroupModal'); }}); }});
  }}).catch(function(){{}});
  new bootstrap.Modal(modal).show();
}}

function _updateBulkGroupModalButtons(d) {{
  var btnArticle = document.getElementById('bulkGroupBtnArticle');
  var btnImages = document.getElementById('bulkGroupBtnImages');
  var btnAll = document.getElementById('bulkGroupBtnAll');
  var sc = (document.querySelector('input[name="bulkGroupModalScopeContent"]:checked') || {{}}).value || 'empty_only';
  var si = (document.querySelector('input[name="bulkGroupModalScopeImages"]:checked') || {{}}).value || 'empty_only';
  var nc = sc === 'override' ? (d.total || 0) : (d.rows_needs_content != null ? d.rows_needs_content : d.no_html_css || 0);
  var ni = si === 'override' ? (d.total || 0) : (d.rows_needs_images != null ? d.rows_needs_images : d.no_images || 0);
  if (btnArticle) btnArticle.textContent = 'Run content (' + nc + ')';
  if (btnImages) btnImages.textContent = 'Run images (' + ni + ')';
  if (btnAll) btnAll.textContent = 'Run all (' + nc + ', ' + ni + ')';
}}

function runBulkGroupFromModal(mode) {{
  var groupId = document.getElementById('bulkGroupModalGroupId').value;
  bootstrap.Modal.getInstance(document.getElementById('bulkGroupModal')).hide();
  runBulkGroup(groupId, mode);
}}

function openBulkAllGroupsModal() {{
  var modal = document.getElementById('bulkAllGroupsModal');
  var btnArticle = document.getElementById('bulkAllGroupsBtnArticle');
  var btnImages = document.getElementById('bulkAllGroupsBtnImages');
  var btnAll = document.getElementById('bulkAllGroupsBtnAll');
  if (btnArticle) btnArticle.textContent = 'Run content';
  if (btnImages) btnImages.textContent = 'Run images';
  if (btnAll) btnAll.textContent = 'Run all (content first, then images)';
  fetch('/api/bulk-all-groups-counts').then(function(r){{ return r.json(); }}).then(function(d) {{
    window._bulkAllGroupsModalCounts = d;
    _updateBulkAllGroupsModalButtons(d);
    _updateBulkModalAiHints('bulkAllGroupsModal');
    var handler = function(){{ _updateBulkAllGroupsModalButtons(window._bulkAllGroupsModalCounts || {{}}); }};
    ['bulkAllGroupsModalScopeContent','bulkAllGroupsModalScopeImages'].forEach(function(name){{
      document.querySelectorAll('input[name="' + name + '"]').forEach(function(el){{
        if (window._bulkAllGroupsModalScopeHandler) el.removeEventListener('change', window._bulkAllGroupsModalScopeHandler);
        el.addEventListener('change', handler);
      }});
    }});
    window._bulkAllGroupsModalScopeHandler = handler;
    var aiSel = document.getElementById('bulkAllGroupsModalAiProvider');
    if (aiSel) aiSel.addEventListener('change', function(){{ _updateBulkModalAiHints('bulkAllGroupsModal'); }});
    document.querySelectorAll('input[name="bulkAllGroupsModalOpenRouterMode"]').forEach(function(r){{ r.addEventListener('change', function(){{ _updateBulkModalAiHints('bulkAllGroupsModal'); }}); }});
  }}).catch(function(){{}});
  new bootstrap.Modal(modal).show();
}}
function runBulkAllGroups(mode) {{
  bootstrap.Modal.getInstance(document.getElementById('bulkAllGroupsModal')).hide();
  var ct = document.querySelector('input[name="allGroupsConcurrency"]:checked');
  var concurrencyType = (ct && ct.value) || 'row';
  var n = concurrencyType === 'row' ? document.getElementById('allGroupsConcurrencyN').value : document.getElementById('allGroupsGroupN').value;
  n = Math.max(1, Math.min(parseInt(n, 10) || 1, concurrencyType === 'row' ? 20 : 10));
  var scEl = document.querySelector('input[name="bulkAllGroupsModalScopeContent"]:checked');
  var siEl = document.querySelector('input[name="bulkAllGroupsModalScopeImages"]:checked');
  var scopeContent = (scEl && scEl.value) || 'override';
  var scopeImages = (siEl && siEl.value) || 'override';
  var aiProvider = (document.getElementById('bulkAllGroupsModalAiProvider') || {{}}).value || '';
  var url = '/api/bulk-run-all-groups?mode=' + mode + '&concurrency_type=' + concurrencyType + '&concurrency_n=' + n + '&scope_content=' + scopeContent + '&scope_images=' + scopeImages + (aiProvider ? '&ai_provider=' + encodeURIComponent(aiProvider) : '') + _getOpenRouterModelsParam('bulkAllGroupsModal');
  var asyncUrl = url + (url.indexOf('?')>=0 ? '&' : '?') + 'async=1';
  fetch(asyncUrl, {{ method: 'POST' }}).then(r=>r.json()).then(function(d){{
    if (d.error) {{ alert('Error: ' + d.error); return; }}
    if (d.success && d.job_id && typeof refreshRunningTasks==='function') refreshRunningTasks();
  }}).catch(function(e){{ alert('Error: ' + e); }});
  if (typeof refreshRunningTasks==='function') setTimeout(refreshRunningTasks, 500);
}}
function runBulkWithProgressChoice(baseUrl, mode) {{
  document.getElementById('bulkChoiceUrl').value = baseUrl;
  document.getElementById('bulkChoiceMode').value = mode || 'all';
  document.getElementById('bulkChoiceModal').querySelector('.modal-title').textContent = 'Run (mode: ' + (mode||'all').toUpperCase() + ')';
  new bootstrap.Modal(document.getElementById('bulkChoiceModal')).show();
}}
function runBulkChoice(foreground) {{
  var baseUrl = document.getElementById('bulkChoiceUrl').value;
  var mode = document.getElementById('bulkChoiceMode').value || 'all';
  bootstrap.Modal.getInstance(document.getElementById('bulkChoiceModal')).hide();
  var url = baseUrl + (baseUrl.indexOf('?')>=0 ? '&' : '?') + 'async=1';
  if (foreground) {{
    runBulkWithProgress(url, mode);
  }} else {{
    if (typeof requestTaskNotificationPermission==='function') requestTaskNotificationPermission();
    fetch(url, {{ method: 'POST' }}).then(r=>r.json()).then(function(d){{
      if (d.error) {{ alert('Error: ' + d.error); return; }}
      if (d.job_id && typeof refreshRunningTasks==='function') refreshRunningTasks();
      else if (d.message) {{
        if (typeof notifyTaskComplete==='function') notifyTaskComplete('Run', 'done', d.message);
        if (typeof refreshAfterRun==='function') refreshAfterRun();
      }}
    }}).catch(function(e){{ alert('Error: ' + e); }});
    if(typeof refreshRunningTasks==='function') setTimeout(refreshRunningTasks, 500);
  }}
}}
function refreshAfterRun() {{
  if(window.location.pathname.indexOf('admin/domains')>=0) {{
    location.reload();
  }} else if(typeof refreshGroups==='function') {{
    refreshGroups();
  }}
}}
function refreshGroups() {{
  fetch('/api/database-management-groups').then(r=>r.text()).then(html=>{{
    var el = document.getElementById('groups-container');
    if(el) el.innerHTML = html || el.innerHTML;
    var lists = el ? el.querySelectorAll('[id^="group-rows-"]') : [];
    lists.forEach(function(list) {{
      var m = list.id.match(/group-rows-(.+)/);
      if(m && typeof showGroupPage==='function') showGroupPage(m[1], 1);
    }});
  }}).catch(function(){{}});
}}
var _progressPollInterval = null;
function workflowStepsFromStatus(s) {{
  if(s.type==='single' && s.action) return [s.action];
  var m = (s.mode||'').toLowerCase();
  if(m==='all') return ['Article A+BCD','Main image','Ingredient image'];
  if(m==='article') return ['Article A+BCD'];
  if(m==='images') return ['Main image','Ingredient image'];
  if(m==='main_image') return ['Main image'];
  if(m==='ingredient_image') return ['Ingredient image'];
  if(m==='pin_image') return ['Pin image'];
  return ['Run'];
}}
function workflowState(st, i, steps) {{
  if(st==='done'||st==='cancelled') return 'done';
  if(st==='error') return i===steps.length-1?'error':'done';
  return i===0?'running':'pending';
}}
function renderProgressBody(s, body) {{
  var wSteps = workflowStepsFromStatus(s);
  var st = s.status || '';
  var wHtml = '<div class="progress-workflow-section"><div class="workflow-label">Workflow</div><div class="workflow-pipeline">' + wSteps.map(function(label,i){{
    var state = workflowState(st, i, wSteps);
    var sep = i>0 ? '<span class="workflow-connector ' + (state!=='pending'?'active':'') + '"></span>' : '';
    return sep + '<span class="workflow-node state-' + state + '"><span class="node-num">' + (i+1) + '</span>' + (String(label).replace(/</g,'&lt;').replace(/>/g,'&gt;')) + '</span>';
  }}).join('') + '</div></div>';
  var steps = s.steps || [];
  var totalRows = s.total_rows;
  var done = s.done;
  var processedCount = s.processed_count;
  var activeTitles = s.active_titles || [];
  var activeArticles = s.active_articles || [];
  if (!Array.isArray(activeTitles) && (s.current_title||'')) {{
    var ct = String(s.current_title).replace(/\s*\+\d+\s*more\s*$/, '').split(/,\s*/);
    activeTitles = ct.filter(function(x){{ return x.trim(); }}).slice(0, 5);
  }}
  var progressSteps = steps.filter(function(st){{ return /R\d+.*:.*\[.*\].*[✓✗]/.test(st); }});
  var completedSteps = progressSteps;
  var remaining = (typeof totalRows==='number' && typeof done==='number') ? Math.max(0, totalRows - done) : null;
  var articlesHtml = '';
  if (activeTitles.length > 0 || activeArticles.length > 0 || completedSteps.length > 0 || (remaining !== null && remaining > 0) || (processedCount !== undefined && processedCount > 0)) {{
    articlesHtml = '<div class="progress-workflow-section" style="margin-top:0.5rem;"><div class="workflow-label">Articles (ID + title + domain + group)</div><div class="progress-articles-list" style="font-size:0.75rem;line-height:1.5;max-height:40vh;overflow-y:auto">';
    if (activeArticles.length > 0 || activeTitles.length > 0) {{
      articlesHtml += '<div class="fw-medium text-primary mb-1" style="font-size:0.7rem">Processing (' + (activeArticles.length || activeTitles.length) + '):</div>';
      if (activeArticles.length > 0) {{
        activeArticles.forEach(function(a) {{
          var tid = a.tid || '';
          var title = (a.title || '').replace(/</g,'&lt;').replace(/>/g,'&gt;');
          var url = (a.domain_url || '-').replace(/</g,'&lt;').replace(/>/g,'&gt;');
          var gid = a.group_id != null ? 'G' + a.group_id : '';
          var letters = (a.domain_letters || a.domain_letter || 'A').replace(/</g,'&lt;').replace(/>/g,'&gt;');
          var meta = [url, letters, gid].filter(function(x){{ return x; }}).join(' · ');
          articlesHtml += '<div class="text-primary mb-1" style="line-height:1.4">• <span class="fw-medium">[' + tid + ']</span> ' + title + '<br><span class="text-muted small">' + (meta || '-') + '</span> <span class="badge bg-primary" style="font-size:0.6rem">processing</span></div>';
        }});
      }} else {{
        activeTitles.forEach(function(t) {{
          var parts = String(t).split(':');
          var tid = parts[0] || '';
          var title = parts.slice(1).join(':').trim().replace(/</g,'&lt;').replace(/>/g,'&gt;');
          var display = (tid ? '[' + tid + '] ' : '') + (title || t);
          articlesHtml += '<div class="text-truncate text-primary mb-1">• ' + display + ' <span class="badge bg-primary" style="font-size:0.6rem">processing</span></div>';
        }});
      }}
    }}
    if (completedSteps.length > 0) {{
      articlesHtml += '<div class="fw-medium text-success mt-2 mb-1" style="font-size:0.7rem">Completed (' + completedSteps.length + '):</div>';
      completedSteps.forEach(function(st) {{
        var reason = '';
        var stBase = st;
        var pipeIdx = st.indexOf(' | ');
        if (pipeIdx >= 0) {{ reason = st.slice(pipeIdx + 3).replace(/</g,'&lt;').replace(/>/g,'&gt;'); stBase = st.slice(0, pipeIdx); }}
        var m = stBase.match(/:\s*\[(\d+)\]\s*(.+?)\s*[✓✗]/);
        if (m) {{
          var display = '[' + m[1] + '] ' + (m[2] || '').trim().replace(/</g,'&lt;').replace(/>/g,'&gt;');
          var ok = /✓/.test(st);
          articlesHtml += '<div class="mb-1" style="color:' + (ok ? '#198754' : '#dc3545') + '">' + (ok ? '✓' : '✗') + ' ' + display + (reason ? '<br><span class="text-muted small" style="font-size:0.65rem">' + reason + '</span>' : '') + '</div>';
        }}
      }});
    }}
    if (remaining !== null && remaining > 0) {{
      articlesHtml += '<div class="fw-medium text-muted mt-2" style="font-size:0.7rem">Remaining: ' + remaining + '</div>';
    }}
    articlesHtml += '</div></div>';
  }}
  
  // For test_content jobs: add View/Retry buttons when done/error
  var actionBtns = '';
  if (s.type === 'test_content' && (st === 'done' || st === 'error')) {{
    var ok = s.ok || 0;
    var failed = s.failed || 0;
    actionBtns = '<div class="mt-3 d-flex gap-2 flex-wrap"><button type="button" class="btn btn-sm btn-outline-primary" onclick="viewTestContentResults(\\''+window._currentProgressJobId+'\\')">View ' + (ok + failed) + ' articles</button>';
    if (failed > 0) {{
      actionBtns += '<button type="button" class="btn btn-sm btn-outline-danger" onclick="retryTestContentFailed(\\''+window._currentProgressJobId+'\\')">Retry ' + failed + ' failed</button>';
    }}
    actionBtns += '</div>';
  }}
  
  var stepsHtml = steps.length > 5 ? '<div class="progress-steps-log small font-monospace" style="font-size:0.65rem;max-height:20vh;overflow-y:auto;background:#f8f9fa;border-radius:4px;padding:4px 6px;margin-top:6px">' + steps.slice(-20).map(function(st){{ return '<div class="text-nowrap" style="line-height:1.35">' + st.replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</div>'; }}).join('') + '</div>' : '';
  var current = (s.current_title||'') && activeTitles.length === 0 && !articlesHtml ? '<span class="text-info">' + String(s.current_title).replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</span>' : '';
  body.innerHTML = '<div class="progress-summary">' + wHtml + '<div class="d-flex justify-content-between align-items-center gap-2 flex-wrap"><span class="fw-medium">' + (s.status||'') + '</span><span class="badge bg-secondary" style="font-size:0.7rem">' + (s.message||'') + '</span></div>' + (current ? '<div class="mt-1 text-truncate" style="font-size:0.75rem">' + current + '</div>' : '') + articlesHtml + stepsHtml + actionBtns + '</div>';
  var logEl = body.querySelector('.progress-steps-log');
  if(logEl) logEl.scrollTop = logEl.scrollHeight;
  var titleEl = document.getElementById('progressModalTitle');
  if(titleEl) titleEl.textContent = st==='done' ? 'Done' : st==='error' ? 'Error' : st==='cancelled' ? 'Cancelled' : 'Workflow progress';
}}
function renderProgressBodyFromMode(mode, status, message, currentTitle, steps) {{
  var s = {{ status: status||'running', message: message||'Starting...', current_title: currentTitle||'', mode: mode||'all', steps: steps||[] }};
  var body = document.getElementById('progressModalBody');
  if(body) renderProgressBody(s, body);
}}
function runBulkWithProgress(url, mode) {{
  var modal = document.getElementById('progressModal');
  var body = document.getElementById('progressModalBody');
  if (typeof requestTaskNotificationPermission==='function') requestTaskNotificationPermission();
  renderProgressBodyFromMode(mode, 'running', 'Starting...', '', []);
  document.getElementById('progressBgBtn').style.display = 'none';
  new bootstrap.Modal(modal).show();
  fetch(url, {{ method: 'POST' }}).then(r=>r.json()).then(d=>{{
    if(d.error) {{ body.innerHTML = '<p class="text-danger">' + d.error + '</p>'; return; }}
    var jobId = d.job_id;
    if(!jobId) {{
      renderProgressBodyFromMode(mode, 'done', d.message||'Done', '', []);
      if(typeof refreshAfterRun==='function') refreshAfterRun();
      setTimeout(function(){{ bootstrap.Modal.getInstance(modal).hide(); }}, 1500);
      return;
    }}
    window._currentProgressJobId = jobId;
    var bgBtn = document.getElementById('progressBgBtn');
    if(bgBtn) bgBtn.style.display = 'inline-block';
    function poll() {{
      fetch('/api/bulk-run-status?job_id=' + jobId).then(r=>r.json()).then(s=>{{
        renderProgressBody(s, body);
        if(s.status === 'done' || s.status === 'error' || s.status === 'cancelled') {{
          clearInterval(iv);
          _progressPollInterval = null;
          var b = document.getElementById('progressBgBtn'); if(b) b.style.display = 'none';
          if (typeof notifyTaskComplete==='function') notifyTaskComplete(workflowStepsFromStatus(s)[0] || 'Run', s.status, s.message);
          if(typeof refreshAfterRun==='function') refreshAfterRun();
          if(typeof refreshRunningTasks==='function') refreshRunningTasks();
          setTimeout(function(){{ bootstrap.Modal.getInstance(modal).hide(); }}, 2000);
        }}
      }}).catch(function(){{ clearInterval(iv); }});
    }}
    poll();
    var iv = setInterval(poll, 800);
    _progressPollInterval = iv;
  }}).catch(function(e){{ body.innerHTML = '<p class="text-danger">Error: ' + e + '</p>'; }});
}}
function runInBackground() {{
  if(_progressPollInterval) clearInterval(_progressPollInterval);
  _progressPollInterval = null;
  var modal = document.getElementById('progressModal');
  bootstrap.Modal.getInstance(modal).hide();
  if(typeof refreshRunningTasks==='function') refreshRunningTasks();
}}
function openProgressModalForJob(jobId) {{
  var modal = document.getElementById('progressModal');
  var body = document.getElementById('progressModalBody');
  if(!modal || !body) return;
  body.innerHTML = '<p class="text-muted">Loading...</p>';
  var bgBtn = document.getElementById('progressBgBtn');
  if(bgBtn) bgBtn.style.display = 'none';
  new bootstrap.Modal(modal).show();
  window._currentProgressJobId = jobId;
  function poll() {{
    fetch('/api/bulk-run-status?job_id=' + jobId).then(r=>r.json()).then(s=>{{
      renderProgressBody(s, body);
      if(s.status === 'done' || s.status === 'error' || s.status === 'cancelled') {{
        clearInterval(iv);
        _progressPollInterval = null;
        if (typeof notifyTaskComplete==='function') notifyTaskComplete(workflowStepsFromStatus(s)[0] || 'Run', s.status, s.message);
        if(typeof refreshRunningTasks==='function') refreshRunningTasks();
      }}
    }}).catch(function(){{}});
  }}
  poll();
  var iv = setInterval(poll, 800);
  _progressPollInterval = iv;
}}
function refreshRunningTasks() {{
  var el = document.getElementById('running-tasks-panel');
  if(!el) return;
  var filterVal = (el.querySelector && el.querySelector('#runTasksFilter')) ? el.querySelector('#runTasksFilter').value : 'all';
  var domainFilter = (el.querySelector && el.querySelector('#runTasksDomainFilter')) ? el.querySelector('#runTasksDomainFilter').value : '';
  var dateFilter = (el.querySelector && el.querySelector('#runTasksDateFilter')) ? el.querySelector('#runTasksDateFilter').value : 'all';
  var url = '/api/bulk-run-jobs?';
  if (domainFilter) url += 'domain_id=' + encodeURIComponent(domainFilter) + '&';
  if (dateFilter && dateFilter !== 'all') url += 'date=' + encodeURIComponent(dateFilter) + '&';
  fetch(url).then(r=>r.json()).then(d=>{{
    var jobs = (d.jobs||[]).filter(function(j){{
      if(filterVal==='all') return true;
      return j.status===filterVal;
    }});
    var hasAnyJobs = (d.jobs||[]).length > 0;
    var hasActiveFilters = !!(domainFilter || (dateFilter && dateFilter !== 'all'));
    if(!hasAnyJobs && !hasActiveFilters) {{ el.innerHTML = ''; el.style.display='none'; return; }}
    el.style.display = 'block';
    var html = '<div class="card mb-3"><div class="card-header py-2 d-flex flex-wrap align-items-center justify-content-between gap-2">';
    html += '<div class="d-flex align-items-center gap-2 flex-wrap"><strong>Running tasks</strong>';
    html += '<select id="runTasksFilter" class="form-select form-select-sm" style="width:auto" onchange="refreshRunningTasks()">';
    html += '<option value="all"' + (filterVal==='all'?' selected':'') + '>All</option>';
    html += '<option value="running"' + (filterVal==='running'?' selected':'') + '>Running</option>';
    html += '<option value="done"' + (filterVal==='done'?' selected':'') + '>Done</option>';
    html += '<option value="error"' + (filterVal==='error'?' selected':'') + '>Error</option>';
    html += '<option value="cancelled"' + (filterVal==='cancelled'?' selected':'') + '>Cancelled</option>';
    html += '</select>';
    html += '<select id="runTasksDomainFilter" class="form-select form-select-sm" style="width:auto;max-width:160px" onchange="refreshRunningTasks()" title="Filter by domain"><option value="">All domains</option></select>';
    html += '<select id="runTasksDateFilter" class="form-select form-select-sm" style="width:auto" onchange="refreshRunningTasks()" title="Filter by date">';
    html += '<option value="all"' + (dateFilter==='all'?' selected':'') + '>All dates</option>';
    html += '<option value="today"' + (dateFilter==='today'?' selected':'') + '>Today</option>';
    html += '<option value="week"' + (dateFilter==='week'?' selected':'') + '>Last 7 days</option>';
    html += '</select></div>';
    html += '<div class="d-flex align-items-center gap-2"><span class="text-muted small">Click row to view progress</span>';
    html += '<button type="button" class="btn btn-outline-secondary btn-sm" onclick="clearBulkJobs(); return false;" title="Clear done/error/cancelled tasks">Clear all</button></div></div>';
    html += '<div class="card-body py-2"><ul class="list-unstyled mb-0 small">';
    jobs.slice(0,25).forEach(function(j){{
      var jidEsc = (j.job_id||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      var jidShort = (j.job_id||'').substring(0,8);
      var action = (j.action||'').toLowerCase();
      var mode = (j.mode||'all').toLowerCase();
      var badges = '';
      if(j.type==='single') {{
        if(action.indexOf('article')>=0||action.indexOf('art')>=0||action==='a') badges += '<span class="badge bg-success me-1" title="Article">Art</span>';
        if(action.indexOf('image')>=0||action.indexOf('main')>=0||action==='m') badges += '<span class="badge bg-info me-1" title="Main image">M</span>';
        if(action.indexOf('ingredient')>=0||action==='i') badges += '<span class="badge bg-warning text-dark me-1" title="Ingredient image">I</span>';
        if(action.indexOf('pin')>=0||action==='p') badges += '<span class="badge bg-secondary me-1" title="Pin image">P</span>';
      }} else {{
        badges = '<span class="badge bg-secondary me-1">' + (mode==='all'?'Art+M+I':(mode==='article'?'Art':(mode==='images'?'M+I':mode))) + '</span>';
      }}
      var typeLabel = j.type==='all' ? 'All groups' : (j.type==='single' ? ((j.action||'') + (j.title_id ? ' (id '+j.title_id+')' : '')) : ('Group '+j.group_id));
      var modeLabel = j.type==='single' ? '' : (' (' + (j.mode||'all').toUpperCase() + ')');
      var statusClass = j.status==='running' ? 'text-primary' : (j.status==='done' ? 'text-success' : (j.status==='cancelled' ? 'text-warning' : 'text-danger'));
      var activeLine = (j.current_title||'') ? ('<br><span class="text-info small">Processing: ' + (j.current_title||'').replace(/</g,'&lt;') + '</span>') : '';
      var stepsLine = (j.steps&&j.steps.length) ? ('<br><span class="text-muted small">'+j.steps.length+' step(s)</span>') : '';
      var clickable = (j.status==='running') ? 'cursor:pointer' : '';
      var btns = '<span class="text-muted me-1" title="Job ID">' + jidShort + '</span>';
      if(j.status==='running') btns += '<button type="button" class="btn btn-outline-primary btn-sm flex-shrink-0 me-1 run-task-view-btn" data-job-id="' + jidEsc + '" title="View workflow">View</button><button type="button" class="btn btn-outline-danger btn-sm flex-shrink-0 run-task-stop" data-job-id="' + jidEsc + '">Stop</button>';
      else {{
        if(j.title_id && (j.status==='done'||j.status==='error') && typeof viewContent==='function') btns += '<button type="button" class="btn btn-outline-success btn-sm flex-shrink-0 me-1 run-task-view-article" data-title-id="' + j.title_id + '" title="View article">View</button>';
        var tid = j.title_id || '';
        if(tid) btns += '<div class="stats-article-actions d-inline-flex flex-wrap gap-1 me-1"><button type="button" class="btn btn-success btn-sm py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-article-external\\',{{title_id:'+tid+'}},\\'Article\\')" title="Article">Art</button><button type="button" class="btn btn-info btn-sm text-white py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-main-image\\',{{title_id:'+tid+'}},\\'Main image\\')" title="Main">M</button><button type="button" class="btn btn-warning btn-sm text-dark py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-ingredient-image\\',{{title_id:'+tid+'}},\\'Ingredient\\')" title="Ingredient">I</button><button type="button" class="btn btn-outline-primary btn-sm py-0 px-1" onclick="event.stopPropagation(); openPinPickerModal('+tid+')" title="Pin">P</button><button type="button" class="btn btn-danger btn-sm py-0 px-1" onclick="event.stopPropagation(); openPinToPinterest('+tid+')" title="Pin (open Pinterest)">Post</button><button type="button" class="btn btn-secondary btn-sm py-0 px-1" onclick="event.stopPropagation(); var sm=document.getElementById(\\'statsArticlesModal\\'); if(sm&&bootstrap.Modal.getInstance(sm)) bootstrap.Modal.getInstance(sm).hide(); openBulkModal('+tid+');" title="Run A,B,C,D">Run</button></div>';
        else if((j.type==='group'||j.type==='all') && (j.status==='done'||j.status==='error')) btns += '<button type="button" class="btn btn-outline-secondary btn-sm flex-shrink-0 run-task-view-articles" data-job-id="' + jidEsc + '" title="Preview articles in this task">Articles</button>';
      }}
      html += '<li class="d-flex justify-content-between align-items-start gap-2 mb-1 py-1 border-bottom run-task-row" style="' + clickable + '" data-job-id="' + jidEsc + '"><div class="flex-grow-1"><span class="fw-medium">' + typeLabel + modeLabel + (badges ? ' ' + badges : '') + '</span><br><span class="' + statusClass + '">' + (j.status||'') + '</span>: ' + (j.message||'').replace(/</g,'&lt;') + activeLine + stepsLine + '</div>';
      html += '<span class="d-flex flex-wrap align-items-center gap-1">' + btns + '</span></li>';
    }});
    if(jobs.length===0) html += '<li class="text-muted small py-2">No tasks match your filters.</li>';
    html += '</ul></div></div>';
    el.innerHTML = html;
    fetch('/api/domains').then(r=>r.json()).then(function(dm){{
      var sel = document.getElementById('runTasksDomainFilter');
      if(sel && dm.domains && dm.domains.length) {{
        if(sel.options.length <= 1) {{
          dm.domains.forEach(function(d){{
            var o = document.createElement('option');
            o.value = d.id || '';
            o.textContent = (d.domain_url || d.domain_name || 'id '+d.id).substring(0,30);
            sel.appendChild(o);
          }});
        }}
        sel.value = domainFilter || '';
      }}
    }}).catch(function(){{}});
    el.querySelectorAll('.run-task-view-btn').forEach(function(btn){{
      btn.addEventListener('click', function(e){{ e.stopPropagation(); openProgressModalForJob(this.getAttribute('data-job-id')); }});
    }});
    el.querySelectorAll('.run-task-view-article').forEach(function(btn){{
      btn.addEventListener('click', function(e){{ e.stopPropagation(); var tid = this.getAttribute('data-title-id'); if(tid && typeof viewContent==='function') viewContent(tid); }});
    }});
    el.querySelectorAll('.run-task-view-articles').forEach(function(btn){{
      btn.addEventListener('click', function(e){{ e.stopPropagation(); openTaskArticlesModal(this.getAttribute('data-job-id')); }});
    }});
    el.querySelectorAll('.run-task-stop').forEach(function(btn){{
      btn.addEventListener('click', function(e){{ e.stopPropagation(); cancelBulkJob(btn.getAttribute('data-job-id')); }});
    }});
    el.querySelectorAll('.run-task-row[data-job-id]').forEach(function(row){{
      var jid = row.getAttribute('data-job-id');
      if(!jid) return;
      var stopBtn = row.querySelector('.run-task-stop');
      if(stopBtn) row.addEventListener('click', function(e){{
        if(e.target.closest('button')) return;
        openProgressModalForJob(jid);
      }});
    }});
  }}).catch(function(){{}});
}}
function openTaskArticlesModal(jobId) {{
  if(!jobId) return;
  var modal = document.getElementById('taskArticlesModal');
  var titleEl = document.getElementById('taskArticlesModalTitle');
  var listEl = document.getElementById('taskArticlesModalList');
  var domainSel = document.getElementById('taskArticlesDomainFilter');
  if(!modal || !listEl) return;
  titleEl.textContent = 'Articles — Task ' + (jobId||'').substring(0,8);
  listEl.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm"></div> Loading...</div>';
  window._taskArticlesJobId = jobId;
  function loadTaskArticles() {{
    var jid = window._taskArticlesJobId;
    if(!jid) return;
    var url = '/api/bulk-run-jobs/' + encodeURIComponent(jid) + '/articles';
    if(domainSel && domainSel.value) url += '?domain_id=' + encodeURIComponent(domainSel.value);
    fetch(url).then(r=>r.json()).then(function(d){{
      listEl.innerHTML = '';
      var arts = d.articles || [];
      if(arts.length===0) {{ listEl.innerHTML = '<p class="text-muted small py-3 mb-0">No articles in this task.</p>'; }}
      else {{
        arts.forEach(function(it){{
          var tid = it.id || '';
          var title = (it.title || '').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
          var dom = (it.domain_url || it.domain_name || '').replace(/</g,'&lt;');
          var actions = '<div class="stats-article-actions mt-1"><button type="button" class="btn btn-success btn-sm py-0 px-1" onclick="openSingleActionModal(\\'/api/generate-article-external\\',{{title_id:'+tid+'}},\\'Article\\')" title="Article">Art</button><button type="button" class="btn btn-info btn-sm text-white py-0 px-1" onclick="openSingleActionModal(\\'/api/generate-main-image\\',{{title_id:'+tid+'}},\\'Main\\')" title="Main">M</button><button type="button" class="btn btn-warning btn-sm text-dark py-0 px-1" onclick="openSingleActionModal(\\'/api/generate-ingredient-image\\',{{title_id:'+tid+'}},\\'Ingredient\\')" title="Ingredient">I</button><button type="button" class="btn btn-outline-primary btn-sm py-0 px-1" onclick="openPinPickerModal('+tid+')" title="Pin">P</button><button type="button" class="btn btn-danger btn-sm py-0 px-1" onclick="event.stopPropagation(); openPinToPinterest('+tid+')" title="Pin (open Pinterest)">Post</button><button type="button" class="btn btn-secondary btn-sm py-0 px-1" onclick="openBulkModal('+tid+');" title="Run">Run</button>';
          if(typeof viewContent==='function') actions += '<button type="button" class="btn btn-outline-success btn-sm py-0 px-1 ms-1" onclick="viewContent('+tid+')" title="Preview">Preview</button>';
          var li = document.createElement('li');
          li.className = 'list-group-item py-1 px-2';
          li.innerHTML = '<span class="text-muted small me-1">'+tid+'</span><span class="me-1" style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+title+'">'+title+'</span><span class="text-muted small me-2">'+dom+'</span>'+actions;
          listEl.appendChild(li);
        }});
      }}
    }}).catch(function(){{ listEl.innerHTML = '<p class="text-danger small py-3 mb-0">Error loading articles.</p>'; }});
  }}
  if(domainSel) {{
    domainSel.innerHTML = '<option value="">All domains</option>';
    fetch('/api/domains').then(r=>r.json()).then(function(dm){{
      if(dm.domains) dm.domains.forEach(function(d){{
        var o = document.createElement('option');
        o.value = d.id || '';
        o.textContent = (d.domain_url || d.domain_name || 'id '+d.id).substring(0,35);
        domainSel.appendChild(o);
      }});
      domainSel.onchange = loadTaskArticles;
      loadTaskArticles();
    }}).catch(function(){{ loadTaskArticles(); }});
  }} else {{ loadTaskArticles(); }}
  if(bootstrap && bootstrap.Modal) {{ var m = new bootstrap.Modal(modal); m.show(); }}
}}
function clearBulkJobs() {{
  fetch('/api/bulk-run-clear', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{}}) }}).then(r=>r.json()).then(d=>{{
    if(d.success && typeof refreshRunningTasks==='function') refreshRunningTasks();
  }});
}}
function cancelBulkJob(jobId) {{
  fetch('/api/bulk-run-cancel?job_id=' + jobId, {{ method: 'POST' }}).then(r=>r.json()).then(d=>{{
    if(d.success) refreshRunningTasks();
  }});
}}
function generateForFilteredArticles() {{
  var domainId = window._statsModalDomainId;
  var stype = window._statsModalType;
  var arts = window._statsModalArticles || [];
  if (!domainId || !stype || arts.length === 0) {{
    alert('No articles to generate');
    return;
  }}
  
  var mode = stype.indexOf('html_css') >= 0 ? 'article' : (stype.indexOf('main_img') >= 0 ? 'main_image' : (stype.indexOf('ing_img') >= 0 ? 'ingredient_image' : 'images'));
  var titleIds = arts.map(function(a) {{ return a.id; }});
  
  var sm = document.getElementById('statsArticlesModal');
  if (sm && bootstrap.Modal.getInstance(sm)) bootstrap.Modal.getInstance(sm).hide();
  
  var modal = document.getElementById('progressModal');
  var body = document.getElementById('progressModalBody');
  renderProgressBody({{ type: 'filtered', action: 'Generate', status: 'running', message: 'Starting...', steps: [] }}, body);
  document.getElementById('progressBgBtn').style.display = 'none';
  new bootstrap.Modal(modal).show();
  
  fetch('/api/bulk-run-filtered', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ domain_id: domainId, title_ids: titleIds, mode: mode, async: 1 }})
  }})
  .then(r=>r.json())
  .then(d=>{{
    if (d.error) {{ body.innerHTML = '<p class="text-danger">' + d.error + '</p>'; return; }}
    var jobId = d.job_id;
    if (!jobId) {{ body.innerHTML = '<p class="text-muted">No job created</p>'; return; }}
    
    window._currentProgressJobId = jobId;
    var bgBtn = document.getElementById('progressBgBtn');
    if (bgBtn) bgBtn.style.display = 'inline-block';
    
    function poll() {{
      fetch('/api/bulk-run-status?job_id=' + jobId).then(r=>r.json()).then(s=>{{
        if (typeof renderProgressBody === 'function') renderProgressBody(s, body);
        else body.innerHTML = '<p><strong>' + (s.status||'') + '</strong></p><p class="small">' + (s.message||'') + '</p>';
        if (s.status === 'done' || s.status === 'error' || s.status === 'cancelled') {{
          clearInterval(iv);
          _progressPollInterval = null;
          var b = document.getElementById('progressBgBtn'); if (b) b.style.display = 'none';
          if (typeof notifyTaskComplete === 'function') notifyTaskComplete(label, s.status, s.message);
          if (typeof refreshAfterRun === 'function') refreshAfterRun();
          if (typeof refreshRunningTasks === 'function') refreshRunningTasks();
          setTimeout(function() {{ bootstrap.Modal.getInstance(modal).hide(); }}, 2000);
        }}
      }}).catch(function() {{ clearInterval(iv); }});
    }}
    poll();
    var iv = setInterval(poll, 800);
    _progressPollInterval = iv;
  }})
  .catch(function(e) {{ body.innerHTML = '<p class="text-danger">Error: ' + e + '</p>'; }});
}}
function showGroupPage(grpKey, page) {{
  var list = document.getElementById('group-rows-' + grpKey);
  if(!list) return;
  var perPageInput = document.getElementById('group-perpage-' + grpKey);
  var raw = (perPageInput && perPageInput.value) ? String(perPageInput.value).trim().toLowerCase() : '20';
  var perPage = 20;
  if (raw === '' || raw === 'all') perPage = 999999;
  else {{
    var n = parseInt(raw, 10);
    if (!isNaN(n) && n >= 1) perPage = n;
  }}
  var items = list.querySelectorAll('li.title-row');
  var total = items.length;
  var totalPages = Math.max(1, Math.ceil(total / perPage));
  page = Math.max(1, Math.min(page, totalPages));
  var start = (page - 1) * perPage;
  var end = Math.min(start + perPage, total);
  items.forEach(function(li, i) {{
    li.style.display = (i >= start && i < end) ? '' : 'none';
  }});
  var nav = document.getElementById('group-pager-' + grpKey);
  if (nav) {{
    var navSpan = nav.querySelector('.group-pager-nav');
    if (navSpan) {{
      navSpan.innerHTML = totalPages > 1 ? '<span class="small text-muted">' + page + '/' + totalPages + ' (' + total + ')</span> <button type="button" class="btn btn-outline-secondary btn-sm py-0 px-1" onclick="showGroupPage(\\'' + grpKey + '\\',' + (page-1) + ')" ' + (page<=1?'disabled':'') + '>Prev</button> <button type="button" class="btn btn-outline-secondary btn-sm py-0 px-1" onclick="showGroupPage(\\'' + grpKey + '\\',' + (page+1) + ')" ' + (page>=totalPages?'disabled':'') + '>Next</button>' : '<span class="small text-muted">Showing all ' + total + ' items</span>';
    }}
  }}
  // Store current page for this group
  if (!window._groupPages) window._groupPages = {{}};
  window._groupPages[grpKey] = page;
}}
function _updateSingleActionOpenRouterOptions() {{
  var sel = document.getElementById('singleActionAiProvider');
  var provider = (sel && sel.value) ? sel.value : 'openrouter';
  var orWrap = document.getElementById('singleActionOpenRouterWrap');
  var localWrap = document.getElementById('singleActionLocalWrap');
  var modeSelect = document.querySelector('input[name="singleActionOpenRouterMode"][value="select"]');
  var modelsEl = document.getElementById('singleActionOpenRouterModels');
  if (orWrap) orWrap.style.display = (provider === 'openrouter') ? 'block' : 'none';
  if (localWrap) localWrap.style.display = (provider === 'local') ? 'block' : 'none';
  if (modelsEl) modelsEl.style.display = (provider === 'openrouter' && modeSelect && modeSelect.checked) ? 'block' : 'none';
  if (provider === 'openrouter' && modelsEl && (!modelsEl.options || modelsEl.options.length === 0) && window._openRouterModelsList) {{
    modelsEl.innerHTML = '';
    window._openRouterModelsList.forEach(function(id){{ var o = document.createElement('option'); o.value = id; o.textContent = id; modelsEl.appendChild(o); }});
  }}
  if (provider === 'local' && !window._localModelsLoaded) {{
    window._localModelsLoaded = true;
    fetch('/api/local-models').then(function(r){{ return r.json(); }}).then(function(d){{
      var localSel = document.getElementById('singleActionLocalModel');
      if (localSel && d.models) {{
        localSel.innerHTML = '';
        d.models.forEach(function(id){{ var o = document.createElement('option'); o.value = id; o.textContent = id; localSel.appendChild(o); }});
      }}
    }}).catch(function(){{}});
  }}
}}
function _getSingleActionOpenRouterModels() {{
  var sel = document.getElementById('singleActionAiProvider');
  if (!sel || sel.value !== 'openrouter') return null;
  var modeEl = document.querySelector('input[name="singleActionOpenRouterMode"][value="select"]');
  if (!modeEl || !modeEl.checked) return null;
  var modelsEl = document.getElementById('singleActionOpenRouterModels');
  if (!modelsEl || !modelsEl.options) return null;
  var selected = [];
  for (var i = 0; i < modelsEl.options.length; i++) {{ if (modelsEl.options[i].selected) selected.push(modelsEl.options[i].value); }}
  return selected.length ? selected : null;
}}
function _getSingleActionLocalModel() {{
  var sel = document.getElementById('singleActionAiProvider');
  if (!sel || sel.value !== 'local') return null;
  var modelEl = document.getElementById('singleActionLocalModel');
  if (!modelEl || !modelEl.value) return null;
  return modelEl.value;
}}
function openSingleActionModal(url, data, label) {{
  document.getElementById('singleActionUrl').value = url;
  document.getElementById('singleActionData').value = JSON.stringify(data || {{}});
  document.getElementById('singleActionLabel').value = label || 'Task';
  document.getElementById('singleActionModalTitle').textContent = label || 'Run';
  document.getElementById('singleActionPrompt').textContent = 'Run ' + (label || '') + ' in background?';
  var isContent = (url || '').indexOf('generate-article') >= 0;
  var wrap = document.getElementById('singleActionAiProviderWrap');
  if (wrap) wrap.style.display = isContent ? 'block' : 'none';
  if (isContent) {{
    _updateSingleActionOpenRouterOptions();
    if (!window._singleActionOpenRouterListeners) {{
      window._singleActionOpenRouterListeners = true;
      var sel = document.getElementById('singleActionAiProvider');
      if (sel) sel.addEventListener('change', _updateSingleActionOpenRouterOptions);
      document.querySelectorAll('input[name="singleActionOpenRouterMode"]').forEach(function(r){{ r.addEventListener('change', _updateSingleActionOpenRouterOptions); }});
    }}
    if (!window._openRouterModelsList && document.getElementById('singleActionOpenRouterModels').options.length === 0) {{
      fetch('/api/openrouter-models').then(function(r){{ return r.json(); }}).then(function(d){{
        window._openRouterModelsList = d.models || [];
        window._openRouterModelsLoaded = true;
        _updateSingleActionOpenRouterOptions();
        ['bulkModal','bulkGroupModal','bulkAllGroupsModal'].forEach(function(p){{
          var m = document.getElementById(p + 'OpenRouterModels');
          if (m) {{ m.innerHTML = ''; (window._openRouterModelsList || []).forEach(function(id){{ var o = document.createElement('option'); o.value = id; o.textContent = id; m.appendChild(o); }}); }}
        }});
      }}).catch(function(){{}});
    }} else {{ _updateSingleActionOpenRouterOptions(); }}
    fetch('/api/ai-config?provider=openrouter').then(function(r){{ return r.json(); }}).then(function(cfg) {{
      var btn = document.querySelector('#singleActionModal .btn-primary');
      if (btn) btn.title = 'AI: ' + (cfg.label || cfg.provider + '/' + cfg.model);
    }}).catch(function(){{}});
  }}
  new bootstrap.Modal(document.getElementById('singleActionModal')).show();
}}
var _pinPickerSelectedTemplateId = null;
function openPinPickerModal(titleId) {{
  _pinPickerSelectedTemplateId = null;
  document.getElementById('pinPickerTitleId').value = titleId;
  document.getElementById('pinPickerLoading').style.display = 'block';
  document.getElementById('pinPickerEmpty').style.display = 'none';
  document.getElementById('pinPickerGrid').style.display = 'none';
  document.getElementById('pinPickerActions').style.display = 'none';
  new bootstrap.Modal(document.getElementById('pinPickerModal')).show();
  fetch('/api/title-pin-templates?title_id=' + titleId)
    .then(function(r) {{ return r.json(); }})
    .then(function(d) {{
      document.getElementById('pinPickerLoading').style.display = 'none';
      var templates = d.templates || [];
      if (!templates.length) {{
        document.getElementById('pinPickerEmpty').style.display = 'block';
        return;
      }}
      var grid = document.getElementById('pinPickerGrid');
      grid.innerHTML = '';
      grid.style.display = 'flex';
      templates.forEach(function(t) {{
        var card = document.createElement('div');
        card.className = 'pin-picker-card text-center';
        card.setAttribute('data-template-id', t.id);
        card.style.cssText = 'cursor:pointer; border:2px solid #dee2e6; border-radius:8px; padding:8px; width:120px; transition:border-color .2s, box-shadow .2s;';
        var img = (t.preview_image_url || '').trim();
        var imgHtml = img
          ? '<img src="' + img + '" style="width:100px;height:150px;object-fit:cover;border-radius:4px;" alt="">'
          : '<div style="width:100px;height:150px;background:#e9ecef;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#6c757d;font-size:2rem;">?</div>';
        card.innerHTML = imgHtml + '<div class="small mt-1 text-truncate" style="max-width:100px" title="' + (t.name || '').replace(/"/g,'&quot;') + '">' + (t.name || 'Template') + '</div>';
        card.onclick = function() {{
          grid.querySelectorAll('.pin-picker-card').forEach(function(c) {{
            c.style.borderColor = '#dee2e6';
            c.style.boxShadow = 'none';
          }});
          card.style.borderColor = '#0d6efd';
          card.style.boxShadow = '0 0 0 3px rgba(13,110,253,.25)';
          _pinPickerSelectedTemplateId = t.id;
          document.getElementById('pinPickerSelected').textContent = 'Selected: ' + (t.name || 'Template');
          document.getElementById('pinPickerActions').style.display = 'flex';
        }};
        grid.appendChild(card);
      }});
    }})
    .catch(function(e) {{
      document.getElementById('pinPickerLoading').innerHTML = '<span class="text-danger">Error: ' + e + '</span>';
    }});
}}
function openPinToPinterest(titleId) {{
  if (!titleId) return;
  fetch('/api/pinterest-pin-url?title_id=' + titleId)
    .then(function(r) {{ return r.json(); }})
    .then(function(d) {{
      if (d.url) window.open(d.url, 'pinterest', 'width=750,height=600');
      else alert(d.error || 'No pin image. Generate pin first (P button).');
    }})
    .catch(function(e) {{ alert('Error: ' + e); }});
}}
function runPinPicker(foreground) {{
  if (typeof requestTaskNotificationPermission==='function') requestTaskNotificationPermission();
  var titleId = document.getElementById('pinPickerTitleId').value;
  var templateId = _pinPickerSelectedTemplateId;
  bootstrap.Modal.getInstance(document.getElementById('pinPickerModal')).hide();
  var data = {{ title_id: parseInt(titleId) }};
  if (templateId) data.domain_template_id = templateId;
  var modal = document.getElementById('progressModal');
  var body = document.getElementById('progressModalBody');
  renderProgressBody({{ type: 'single', action: 'Pin image', status: 'running', message: 'Starting...', steps: [] }}, body);
  document.getElementById('progressBgBtn').style.display = 'none';
  new bootstrap.Modal(modal).show();
  if (foreground) {{
    fetch('/api/generate-pin-image', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify(data) }})
      .then(function(r) {{ return r.json(); }})
      .then(function(d) {{
        var st = d.success ? 'done' : 'error';
        var msg = d.success ? 'Done.' : (d.error||'');
        renderProgressBody({{ type: 'single', action: 'Pin image', status: st, message: msg, steps: [] }}, body);
        if (typeof notifyTaskComplete==='function') notifyTaskComplete('Pin image', st, msg);
        if (d.success && typeof refreshAfterRun === 'function') refreshAfterRun();
        setTimeout(function() {{ bootstrap.Modal.getInstance(modal).hide(); }}, 1500);
      }})
      .catch(function(e) {{ body.innerHTML = '<p class="text-danger">Error: ' + e + '</p>'; }});
  }} else {{
    if (typeof requestTaskNotificationPermission==='function') requestTaskNotificationPermission();
    data.async = 1;
    fetch('/api/generate-pin-image', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify(data) }})
      .then(function(r) {{ return r.json(); }})
      .then(function(d) {{
        if (d.error) {{ body.innerHTML = '<p class="text-danger">' + d.error + '</p>'; return; }}
        var jobId = d.job_id;
        renderProgressBody({{ type: 'single', action: 'Pin image', status: 'running', message: 'Running in background...', steps: [] }}, body);
        function poll() {{
          fetch('/api/bulk-run-jobs/' + jobId).then(function(r){{ return r.json(); }}).then(function(j) {{
            renderProgressBody({{ type: 'single', action: 'Pin image', status: j.status, message: j.message || '', steps: [] }}, body);
            if (j.status === 'done' || j.status === 'error') {{
              if (typeof notifyTaskComplete==='function') notifyTaskComplete('Pin image', j.status, j.message);
              if (j.status === 'done' && typeof refreshAfterRun === 'function') refreshAfterRun();
              setTimeout(function() {{ bootstrap.Modal.getInstance(modal).hide(); }}, 1500);
            }} else {{ setTimeout(poll, 2000); }}
          }}).catch(function() {{ setTimeout(poll, 3000); }});
        }}
        poll();
      }})
      .catch(function(e) {{ body.innerHTML = '<p class="text-danger">Error: ' + e + '</p>'; }});
  }}
}}
function runSingleAction(foreground) {{
  var url = document.getElementById('singleActionUrl').value;
  var data = {{}};
  try {{ data = JSON.parse(document.getElementById('singleActionData').value || '{{}}'); }} catch(e) {{}}
  var aiWrap = document.getElementById('singleActionAiProviderWrap');
  if (aiWrap && aiWrap.style.display !== 'none') {{
    var sel = document.getElementById('singleActionAiProvider');
    if (sel && sel.value) data.ai_provider = sel.value;
    var orModels = _getSingleActionOpenRouterModels();
    if (orModels && orModels.length) data.openrouter_models = orModels;
    var localModel = _getSingleActionLocalModel();
    if (localModel) data.local_model = localModel;
  }}
  var label = document.getElementById('singleActionLabel').value || 'Task';
  if (typeof requestTaskNotificationPermission==='function') requestTaskNotificationPermission();
  bootstrap.Modal.getInstance(document.getElementById('singleActionModal')).hide();
  var modal = document.getElementById('progressModal');
  var body = document.getElementById('progressModalBody');
  renderProgressBody({{ type: 'single', action: label, status: 'running', message: 'Starting...', steps: [] }}, body);
  document.getElementById('progressBgBtn').style.display = 'none';
  new bootstrap.Modal(modal).show();
  if(foreground) {{
    fetch(url, {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify(data) }})
      .then(r=>r.json())
      .then(d=>{{
        var st = d.success ? 'done' : 'error';
        renderProgressBody({{ type: 'single', action: label, status: st, message: d.success ? 'Done.' : (d.error||''), steps: [] }}, body);
        if (typeof notifyTaskComplete==='function') notifyTaskComplete(label, st, d.success ? 'Done' : d.error);
        if(d.success && typeof refreshAfterRun==='function') refreshAfterRun();
        setTimeout(function(){{ bootstrap.Modal.getInstance(modal).hide(); }}, 1500);
      }})
      .catch(function(e){{ body.innerHTML = '<p class="text-danger">Error: ' + e + '</p>'; }});
  }} else {{
    renderProgressBody({{ type: 'single', action: label, status: 'running', message: 'Starting...', steps: [] }}, body);
    data.async = 1;
    fetch(url, {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify(data) }})
      .then(r=>r.json())
      .then(d=>{{
        if(d.error) {{ body.innerHTML = '<p class="text-danger">' + d.error + '</p>'; return; }}
        var jobId = d.job_id;
        if(!jobId) {{
          renderProgressBody({{ type: 'single', action: label, status: 'done', message: d.message||'Done', steps: [] }}, body);
          if (typeof notifyTaskComplete==='function') notifyTaskComplete(label, 'done', d.message);
          if(d.success && typeof refreshAfterRun==='function') refreshAfterRun();
          setTimeout(function(){{ bootstrap.Modal.getInstance(modal).hide(); }}, 1500);
          return;
        }}
        window._currentProgressJobId = jobId;
        var bgBtn = document.getElementById('progressBgBtn');
        if(bgBtn) bgBtn.style.display = 'inline-block';
        function poll() {{
          fetch('/api/bulk-run-status?job_id=' + jobId).then(r=>r.json()).then(s=>{{
            if(typeof renderProgressBody==='function') renderProgressBody(s, body);
            else body.innerHTML = '<p><strong>' + (s.status||'') + '</strong></p><p class="small">' + (s.message||'') + '</p>';
            if(s.status === 'done' || s.status === 'error' || s.status === 'cancelled') {{
              clearInterval(iv);
              _progressPollInterval = null;
              var b = document.getElementById('progressBgBtn'); if(b) b.style.display = 'none';
              if (typeof notifyTaskComplete==='function') notifyTaskComplete(label, s.status, s.message);
              if(typeof refreshAfterRun==='function') refreshAfterRun();
              if(typeof refreshRunningTasks==='function') refreshRunningTasks();
              setTimeout(function(){{ bootstrap.Modal.getInstance(modal).hide(); }}, 2000);
            }}
          }}).catch(function(){{ clearInterval(iv); }});
        }}
        poll();
        var iv = setInterval(poll, 800);
        _progressPollInterval = iv;
      }})
      .catch(function(e){{ body.innerHTML = '<p class="text-danger">Error: ' + e + '</p>'; }});
  }}
}}
</script>
<div id="viewModal" class="modal fade" tabindex="-1"><div class="modal-dialog modal-lg modal-dialog-scrollable"><div class="modal-content"><div class="modal-header"><h5 class="modal-title" id="viewModalTitle">View</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body" id="viewModalBody"></div></div></div></div>
<div id="bulkModal" class="modal fade" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Run for this row</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><input type="hidden" id="bulkModalTitleId"><p class="mb-2">What do you want to run?</p><div class="d-flex flex-column gap-2 mb-3"><button type="button" id="bulkModalBtnArticle" class="btn btn-outline-success" onclick="runBulk('article')">Run content</button><button type="button" id="bulkModalBtnImages" class="btn btn-outline-info" onclick="runBulk('images')">Run images</button><button type="button" id="bulkModalBtnAll" class="btn btn-primary" onclick="runBulk('all')">Run all (content first, then images)</button></div><p class="mb-2 fw-medium small">AI provider (for content):</p><select id="bulkModalAiProvider" class="form-select form-select-sm mb-2" style="max-width:200px"><option value="openrouter" selected>OpenRouter</option><option value="openai">OpenAI</option></select><div id="bulkModalOpenRouterWrap" class="mb-3" style="display:none"><p class="mb-1 fw-medium small">OpenRouter:</p><div class="mb-1"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkModalOpenRouterMode" value="rotation" checked> Rotation (try next on failure)</label></div><div class="mb-1"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkModalOpenRouterMode" value="select"> Select model(s)</label></div><select id="bulkModalOpenRouterModels" class="form-select form-select-sm" multiple style="max-height:100px;width:100%"></select></div><p class="mb-2 fw-medium small">Scope for content:</p><div class="mb-2"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkModalScopeContent" value="override"> Override existing</label></div><div class="mb-3"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkModalScopeContent" value="empty_only" checked> Only rows without HTML+CSS</label></div><p class="mb-2 fw-medium small">Scope for images (main+ingredient):</p><div class="mb-2"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkModalScopeImages" value="override"> Override existing</label></div><div class="mb-2"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkModalScopeImages" value="empty_only" checked> Only rows without main+ingredient images</label></div><p class="small text-muted mt-2 mb-0">Note: Articles without article_html will be skipped for image generation.</p></div></div></div></div>
<div id="bulkGroupModal" class="modal fade" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title" id="bulkGroupModalTitle">Run for group</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><input type="hidden" id="bulkGroupModalGroupId"><p class="mb-2">Run for all rows in this group. What do you want to run?</p><div class="d-flex flex-column gap-2 mb-3"><button type="button" id="bulkGroupBtnArticle" class="btn btn-outline-success" onclick="runBulkGroupFromModal('article')">Run content</button><button type="button" id="bulkGroupBtnImages" class="btn btn-outline-info" onclick="runBulkGroupFromModal('images')">Run images</button><button type="button" id="bulkGroupBtnAll" class="btn btn-primary" onclick="runBulkGroupFromModal('all')">Run all (content first, then images)</button></div><p class="mb-2 fw-medium small">AI provider (for content):</p><select id="bulkGroupModalAiProvider" class="form-select form-select-sm mb-2" style="max-width:200px"><option value="openrouter" selected>OpenRouter</option><option value="openai">OpenAI</option></select><div id="bulkGroupModalOrOpts" class="mb-3 p-2 bg-light border rounded small" style="display:none;"><div class="fw-medium mb-1">OpenRouter:</div><div class="mb-2"><div class="form-check form-check-inline"><input class="form-check-input" type="radio" name="bulkGroupModalOpenRouterMode" id="bulkGroupModalOrModeRot" value="rotation" checked><label class="form-check-label" for="bulkGroupModalOrModeRot">Rotation (try next on failure)</label></div><div class="form-check form-check-inline"><input class="form-check-input" type="radio" name="bulkGroupModalOpenRouterMode" id="bulkGroupModalOrModeFall" value="fallback"><label class="form-check-label" for="bulkGroupModalOrModeFall">Fallback (run all simultaneously, use first success)</label></div></div><div class="fw-medium mb-1">Select model(s) <span class="text-muted fw-normal">(drag to reorder)</span></div><div class="openrouter-models-container border bg-white rounded p-1 mb-1" id="bulkGroupModalOrModels"></div><button type="button" class="btn btn-outline-secondary btn-sm" onclick="_resetOpenRouterModels('bulkGroupModal')">Reset to defaults</button></div><p class="mb-2 fw-medium small">Scope for content:</p><div class="form-check mb-1"><input class="form-check-input" type="radio" name="bulkGroupModalScopeContent" id="bgmScopeContent1" value="override"><label class="form-check-label small" for="bgmScopeContent1">Override existing</label></div><div class="form-check mb-3"><input class="form-check-input" type="radio" name="bulkGroupModalScopeContent" id="bgmScopeContent2" value="empty_only" checked><label class="form-check-label small" for="bgmScopeContent2">Only rows without HTML+CSS</label></div><p class="mb-2 fw-medium small">Scope for images:</p><div class="form-check mb-1"><input class="form-check-input" type="radio" name="bulkGroupModalScopeImages" id="bgmScopeImages1" value="override"><label class="form-check-label small" for="bgmScopeImages1">Override existing</label></div><div class="form-check"><input class="form-check-input" type="radio" name="bulkGroupModalScopeImages" id="bgmScopeImages2" value="empty_only" checked><label class="form-check-label small" for="bgmScopeImages2">Only rows without main+ingredient images</label></div></div></div></div></div>

<div id="bulkAllGroupsModal" class="modal fade" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Run for all groups</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><p class="mb-2">Run for all rows in all groups. What do you want to run?</p><div class="d-flex flex-column gap-2 mb-3"><button type="button" id="bulkAllGroupsBtnArticle" class="btn btn-outline-success" onclick="runBulkAllGroups('article')">Run content</button><button type="button" id="bulkAllGroupsBtnImages" class="btn btn-outline-info" onclick="runBulkAllGroups('images')">Run images</button><button type="button" id="bulkAllGroupsBtnAll" class="btn btn-primary" onclick="runBulkAllGroups('all')">Run all (content first, then images)</button></div><p class="mb-2 fw-medium small">AI provider (for content):</p><select id="bulkAllGroupsModalAiProvider" class="form-select form-select-sm mb-2" style="max-width:200px"><option value="openrouter" selected>OpenRouter</option><option value="openai">OpenAI</option></select><div id="bulkAllGroupsModalOpenRouterWrap" class="mb-3" style="display:none"><p class="mb-1 fw-medium small">OpenRouter:</p><div class="mb-1"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkAllGroupsModalOpenRouterMode" value="rotation" checked> Rotation (try next on failure)</label></div><div class="mb-1"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkAllGroupsModalOpenRouterMode" value="select"> Select model(s)</label></div><select id="bulkAllGroupsModalOpenRouterModels" class="form-select form-select-sm" multiple style="max-height:100px;width:100%"></select></div><p class="mb-2 fw-medium small">Scope for content:</p><div class="mb-2"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkAllGroupsModalScopeContent" value="override"> Override existing</label></div><div class="mb-3"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkAllGroupsModalScopeContent" value="empty_only" checked> Only rows without HTML+CSS</label></div><p class="mb-2 fw-medium small">Scope for images:</p><div class="mb-2"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkAllGroupsModalScopeImages" value="override"> Override existing</label></div><div class="mb-3"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="bulkAllGroupsModalScopeImages" value="empty_only" checked> Only rows without main+ingredient images</label></div><hr class="my-3"><p class="mb-2 fw-medium">Concurrency:</p><div class="mb-2"><label class="d-flex align-items-center gap-2"><input type="radio" name="allGroupsConcurrency" value="row" checked> Row by row — max <input type="number" id="allGroupsConcurrencyN" value="3" min="1" max="20" class="form-control form-control-sm d-inline-block" style="width:60px"> rows at a time</label></div><div><label class="d-flex align-items-center gap-2"><input type="radio" name="allGroupsConcurrency" value="group"> Group by group — max <input type="number" id="allGroupsGroupN" value="2" min="1" max="10" class="form-control form-control-sm d-inline-block" style="width:60px"> groups at a time (rows run one by one per group)</label></div><p class="small text-muted mt-2 mb-0">Note: Articles without article_html will be skipped for image generation.</p></div></div></div></div>
<div id="singleActionModal" class="modal fade" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title" id="singleActionModalTitle">Run</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><input type="hidden" id="singleActionUrl"><input type="hidden" id="singleActionData"><input type="hidden" id="singleActionLabel"><div id="singleActionAiProviderWrap" class="mb-3" style="display:none"><p class="mb-2 fw-medium small">AI provider:</p><select id="singleActionAiProvider" class="form-select form-select-sm mb-2" style="max-width:200px"><option value="openrouter" selected>OpenRouter</option><option value="openai">OpenAI</option><option value="local">Local</option></select><div id="singleActionOpenRouterWrap" class="mb-2" style="display:none"><p class="mb-1 fw-medium small">OpenRouter:</p><div class="mb-1"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="singleActionOpenRouterMode" value="rotation" checked> Rotation (try next on failure)</label></div><div class="mb-1"><label class="d-flex align-items-center gap-2 small"><input type="radio" name="singleActionOpenRouterMode" value="select"> Select model(s)</label></div><select id="singleActionOpenRouterModels" class="form-select form-select-sm" multiple style="max-height:100px;width:100%"></select></div><div id="singleActionLocalWrap" class="mb-2" style="display:none"><p class="mb-1 fw-medium small">Local model:</p><select id="singleActionLocalModel" class="form-select form-select-sm" style="width:100%"></select></div></div><p class="mb-3" id="singleActionPrompt">Run in background?</p><div class="d-flex gap-2"><button type="button" class="btn btn-primary" onclick="runSingleAction(false)">Background</button></div></div></div></div></div>
<div id="pinPickerModal" class="modal fade" tabindex="-1"><div class="modal-dialog modal-lg"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Select Pin Template</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><input type="hidden" id="pinPickerTitleId"><div id="pinPickerLoading" class="text-center py-4"><div class="spinner-border spinner-border-sm"></div> Loading templates...</div><div id="pinPickerEmpty" class="text-center py-4 text-muted" style="display:none">No templates found for this domain.<br>Add templates in Admin &rarr; Domains &rarr; Templates.</div><div id="pinPickerGrid" class="d-flex flex-wrap gap-3 justify-content-center" style="display:none"></div><div id="pinPickerActions" class="d-flex flex-wrap gap-2 mt-3 pt-3 border-top align-items-center" style="display:none"><span class="me-auto small text-muted" id="pinPickerSelected"></span><label class="d-flex align-items-center gap-1 small mb-0"><input type="checkbox" id="pinPickerPostToPinterest"> Pin (open Pinterest) after</label><button type="button" class="btn btn-primary btn-sm" onclick="runPinPicker(true)">Foreground</button><button type="button" class="btn btn-outline-secondary btn-sm" onclick="runPinPicker(false)">Background</button></div></div></div></div></div>
<div id="bulkChoiceModal" class="modal fade" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Run</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><input type="hidden" id="bulkChoiceUrl"><input type="hidden" id="bulkChoiceMode"><p class="mb-3">Run in foreground or background?</p><div class="d-flex gap-2"><button type="button" class="btn btn-primary" onclick="runBulkChoice(true)">Foreground</button><button type="button" class="btn btn-outline-secondary" onclick="runBulkChoice(false)">Background</button></div></div></div></div></div>
<div id="progressModal" class="modal fade" tabindex="-1" data-bs-backdrop="static"><div class="modal-dialog modal-dialog-scrollable" style="max-width:680px"><div class="modal-content"><div class="modal-header py-1"><h6 class="modal-title mb-0" id="progressModalTitle">Workflow progress</h6><button type="button" class="btn-close btn-close-sm" data-bs-dismiss="modal" aria-label="Close"></button></div><div class="modal-body py-2" id="progressModalBody" style="max-height:65vh"><p class="mb-0 small">Please wait.</p></div><div class="modal-footer py-1"><button type="button" class="btn btn-outline-secondary btn-sm" id="progressBgBtn" onclick="runInBackground()" style="display:none">Run in background</button></div></div></div></div>
<div id="taskArticlesModal" class="modal fade" tabindex="-1"><div class="modal-dialog modal-lg modal-dialog-scrollable"><div class="modal-content"><div class="modal-header py-2 d-flex align-items-center gap-2"><h6 class="modal-title mb-0" id="taskArticlesModalTitle">Articles in task</h6><select id="taskArticlesDomainFilter" class="form-select form-select-sm" style="width:auto;max-width:180px" title="Filter by domain"><option value="">All domains</option></select><button type="button" class="btn-close btn-close-sm ms-auto" data-bs-dismiss="modal"></button></div><div class="modal-body py-2"><ul class="list-group list-group-flush" id="taskArticlesModalList"></ul></div></div></div></div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
if(typeof refreshRunningTasks==='function') refreshRunningTasks();
// Only poll running tasks every 5s on database-management; avoids constant API calls on admin/domains
if(window.location.pathname.indexOf('database-management')>=0 || window.location.pathname==='/') {{
  setInterval(function() {{ if(typeof refreshRunningTasks==='function') refreshRunningTasks(); }}, 5000);
  setInterval(function() {{ if(typeof refreshGroups==='function') refreshGroups(); }}, 60000);
  setTimeout(function() {{
    var el = document.getElementById('groups-container');
    var lists = el ? el.querySelectorAll('[id^="group-rows-"]') : [];
    lists.forEach(function(list) {{
      var m = list.id.match(/group-rows-(.+)/);
      if(m && typeof showGroupPage==='function') showGroupPage(m[1], 1);
    }});
  }}, 100);
}}

// Domain search autocomplete (for /admin/domains page)
if (window.location.pathname.indexOf('/admin/domains') >= 0) {{
  var domainSearchTimer = null;
  var domainSearchInput = document.getElementById('domainSearch');
  
  if (domainSearchInput) {{
    domainSearchInput.addEventListener('input', function(e) {{
      clearTimeout(domainSearchTimer);
      var query = e.target.value.trim();
      if (query.length < 2) {{
        document.getElementById('domainSearchSuggestions').style.display = 'none';
        return;
      }}
      domainSearchTimer = setTimeout(function() {{
        fetchDomainSuggestions(query);
      }}, 300);
    }});
    
    domainSearchInput.addEventListener('keypress', function(e) {{
      if (e.key === 'Enter') {{
        document.getElementById('domainSearchSuggestions').style.display = 'none';
        var query = e.target.value.trim();
        if (query) highlightDomainInTable(query);
      }}
    }});
    
    domainSearchInput.addEventListener('focus', function() {{
      if (this.value.length >= 2) fetchDomainSuggestions(this.value);
    }});
    
    document.addEventListener('click', function(e) {{
      if (!e.target.closest('#domainSearch') && !e.target.closest('#domainSearchSuggestions')) {{
        document.getElementById('domainSearchSuggestions').style.display = 'none';
      }}
    }});
  }}
}}

function fetchDomainSuggestions(query) {{
  fetch('/api/domains-search-suggestions?q=' + encodeURIComponent(query))
    .then(r => r.json())
    .then(data => {{
      var suggestions = data.suggestions || [];
      var suggestionsDiv = document.getElementById('domainSearchSuggestions');
      
      if (suggestions.length === 0) {{
        suggestionsDiv.style.display = 'none';
        return;
      }}
      
      var html = '';
      suggestions.forEach(function(s) {{
        var icon = s.type === 'group' ? '📁' : '🌐';
        var badge = s.type === 'group' ? '<span class="badge bg-secondary ms-2">Group</span>' : '<span class="badge bg-primary ms-2">Domain</span>';
        var path = s.group_path ? '<div class="small text-muted mt-1">Group: ' + s.group_path + '</div>' : '';
        var info = s.info ? '<div class="small text-muted">' + s.info + '</div>' : '';
        html += '<div class="p-2 border-bottom domain-suggestion-item" style="cursor:pointer" onclick="selectDomainSuggestion('+s.domain_id+',\\''+s.type+'\\')">';
        html += '<div>' + icon + ' <strong>' + s.label + '</strong>' + badge + '</div>' + info + path;
        html += '</div>';
      }});
      
      suggestionsDiv.innerHTML = html;
      suggestionsDiv.style.display = 'block';
    }})
    .catch(function() {{
      document.getElementById('domainSearchSuggestions').style.display = 'none';
    }});
}}

function selectDomainSuggestion(domainId, type) {{
  document.getElementById('domainSearchSuggestions').style.display = 'none';
  if (domainId) {{
    highlightDomainInTable(domainId);
  }}
}}

function highlightDomainInTable(domainIdOrQuery) {{
  var rows = document.querySelectorAll('.domains-row');
  var found = false;
  rows.forEach(function(row) {{
    row.style.backgroundColor = '';
  }});
  
  if (typeof domainIdOrQuery === 'number' || String(domainIdOrQuery).match(/^\\d+$/)) {{
    var targetRow = document.querySelector('.domains-row[data-domain-id="'+domainIdOrQuery+'"]');
    if (targetRow) {{
      targetRow.style.backgroundColor = '#fff3cd';
      targetRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      found = true;
    }}
  }} else {{
    var query = String(domainIdOrQuery).toLowerCase();
    rows.forEach(function(row) {{
      var text = row.textContent.toLowerCase();
      if (text.indexOf(query) >= 0) {{
        row.style.backgroundColor = '#fff3cd';
        if (!found) {{
          row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
          found = true;
        }}
      }}
    }});
  }}
}}

function clearDomainSearch() {{
  document.getElementById('domainSearch').value = '';
  document.getElementById('domainSearchSuggestions').style.display = 'none';
  var rows = document.querySelectorAll('.domains-row');
  rows.forEach(function(row) {{
    row.style.backgroundColor = '';
  }});
}}

function clearAllGroups() {{
  if (!confirm('Remove ALL domains from ALL groups? Domains will remain as standalone.')) return;
  if (typeof showGlobalLoading === 'function') showGlobalLoading();
  fetch('/api/domains/clear-all-groups', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }}
  }})
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
      if (data.success) {{
        alert('Unassigned ' + (data.count || 0) + ' domains from groups');
        location.reload();
      }} else {{
        alert(data.error || 'Failed to clear groups');
      }}
    }})
    .catch(function(err) {{ alert(err.message || 'Network error'); }})
    .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
}}

function deleteAllDomains() {{
  if (!confirm('⚠️ WARNING: This will PERMANENTLY DELETE all domains, titles, and articles!\\n\\nAre you absolutely sure?')) return;
  if (!confirm('This action CANNOT be undone. All domains and their content will be deleted.\\n\\nContinue?')) return;
  
  if (typeof showGlobalLoading === 'function') showGlobalLoading();
  fetch('/api/domains/delete-all', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }}
  }})
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
      if (data.success) {{
        alert('Deleted ' + (data.count || 0) + ' domains and all their content');
        location.reload();
      }} else {{
        alert(data.error || 'Failed to delete domains');
      }}
    }})
    .catch(function(err) {{ alert(err.message || 'Network error'); }})
    .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
}}

function clearCurrentGroup() {{
  var groupId = null; // Will be set from URL params
  var urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('group_id')) {{
    groupId = parseInt(urlParams.get('group_id'));
  }}
  if (!groupId) return;
  if (!confirm('Remove all domains from this group?')) return;
  if (typeof showGlobalLoading === 'function') showGlobalLoading();
  fetch('/api/domains/clear-group/' + groupId, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }}
  }})
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
      if (data.success) {{
        alert('Cleared ' + (data.count || 0) + ' domains from group');
        location.reload();
      }} else {{
        alert(data.error || 'Failed to clear group');
      }}
    }})
    .catch(function(err) {{ alert(err.message || 'Network error'); }})
    .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
}}

function deleteCurrentGroupDomains() {{
  var groupId = null;
  var urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('group_id')) {{
    groupId = parseInt(urlParams.get('group_id'));
  }}
  if (!groupId) return;
  if (!confirm('⚠️ WARNING: This will PERMANENTLY DELETE all domains in this group and their content!\\n\\nAre you sure?')) return;
  if (typeof showGlobalLoading === 'function') showGlobalLoading();
  fetch('/api/domains/delete-group/' + groupId, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }}
  }})
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
      if (data.success) {{
        alert('Deleted ' + (data.count || 0) + ' domains from group');
        window.location.href = '/admin/domains';
      }} else {{
        alert(data.error || 'Failed to delete domains');
      }}
    }})
    .catch(function(err) {{ alert(err.message || 'Network error'); }})
    .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
}}
</script>
</body></html>"""


def _render_article_run_actions_html(ids, domain_index, ac_map, title_a_id, in_group=True):
    """Shared helper: returns HTML for Run action buttons (Art, M, I, P, C, Run). Used by database-management and admin/domains stats popup. Run button only if in_group."""
    labels = ["A", "B", "C", "D"]
    a_has_all = ac_map.get(ids[0] or 0, {}).get("has_all", False) if ids else False
    tid_i = ids[domain_index] if domain_index < len(ids) and ids[domain_index] else None
    ta_id = ids[0] if ids else None
    if not tid_i and domain_index != 0:
        tid_i = ids[domain_index]
    if not title_a_id and ta_id:
        title_a_id = ta_id
    if not ta_id:
        ta_id = title_a_id
    btns = []
    if domain_index == 0:
        btns.append(f'<button type="button" class="btn btn-success btn-sm" onclick="openSingleActionModal(\'/api/generate-article-external\',{{title_id:{tid_i}}},\'Article A\')" title="Article">Art</button>')
        btns.append(f'<button type="button" class="btn btn-info btn-sm text-white" onclick="openSingleActionModal(\'/api/generate-main-image\',{{title_id:{tid_i}}},\'Main image\')" title="Main">M</button>')
        btns.append(f'<button type="button" class="btn btn-warning btn-sm text-dark" onclick="openSingleActionModal(\'/api/generate-ingredient-image\',{{title_id:{tid_i}}},\'Ingredient\')" title="Ingredient">I</button>')
        btns.append(f'<button type="button" class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); openPinPickerModal({tid_i})" title="Pin">P</button>')
    else:
        dis = ' disabled' if not a_has_all else ''
        btns.append(f'<button type="button" class="btn btn-primary btn-sm"{dis} onclick="openSingleActionModal(\'/api/generate-article-bcd\',{{title_id:{tid_i}}},\'BCD\')" title="Content from A">C</button>')
        btns.append(f'<button type="button" class="btn btn-info btn-sm text-white" onclick="openSingleActionModal(\'/api/generate-main-image\',{{title_id:{ta_id}}},\'Main\')" title="Main (all)">M</button>')
        btns.append(f'<button type="button" class="btn btn-warning btn-sm text-dark" onclick="openSingleActionModal(\'/api/generate-ingredient-image\',{{title_id:{ta_id}}},\'Ingr\')" title="Ingr (all)">I</button>')
        btns.append(f'<button type="button" class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); openPinPickerModal({tid_i})" title="Pin">P</button>')
    if in_group and (title_a_id or ta_id):
        run_tid = title_a_id or ta_id
        btns.append(f'<button type="button" class="btn btn-secondary btn-sm" onclick="var sm=document.getElementById(&#39;statsArticlesModal&#39;); if(sm && bootstrap.Modal.getInstance(sm)) bootstrap.Modal.getInstance(sm).hide(); openBulkModal({run_tid});" title="Run content+images for A,B,C,D">Run</button>')
    return "".join(btns)


def _get_groups_with_domains_and_titles(filter_group_id=None, filter_domain_id=None, user_domain_ids=None):
    """Group → domains → titles hierarchy (like C1-MultiDomain).
    
    Args:
        filter_group_id: If set, only show this group and its subgroups
        filter_domain_id: If set, only show this domain
        user_domain_ids: If set (list), only show domains in this list
    """
    with get_connection() as conn:
        # Build domain filter
        domain_filter = ""
        domain_params = []
        
        if filter_domain_id:
            domain_filter = " WHERE id = ?"
            domain_params = [filter_domain_id]
        elif filter_group_id:
            # Get all descendant groups
            def get_all_descendants(gid):
                result = [gid]
                cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
                children = [dict_row(r)["id"] for r in cur.fetchall()]
                for child_id in children:
                    result.extend(get_all_descendants(child_id))
                return result
            
            group_ids = get_all_descendants(filter_group_id)
            placeholders = ",".join(["?"] * len(group_ids))
            domain_filter = f" WHERE group_id IN ({placeholders})"
            domain_params = group_ids
        elif user_domain_ids:
            placeholders = ",".join(["?"] * len(user_domain_ids))
            domain_filter = f" WHERE id IN ({placeholders})"
            domain_params = user_domain_ids
        
        # Get groups
        if filter_group_id:
            # Only get the filtered group and its descendants
            def get_group_and_descendants(gid):
                result = []
                cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` WHERE id = ?", (gid,))
                g = dict_row(cur.fetchone())
                if g:
                    result.append(g)
                cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` WHERE parent_group_id = ?", (gid,))
                children = [dict_row(r) for r in cur.fetchall()]
                for child in children:
                    result.extend(get_group_and_descendants(child["id"]))
                return result
            groups = get_group_and_descendants(filter_group_id)
        else:
            cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` ORDER BY id")
            groups = [dict_row(r) for r in cur.fetchall()]
        
        # Get domains
        cur = db_execute(conn, f"SELECT id, domain_url, domain_name, group_id, domain_index, website_template FROM domains{domain_filter} ORDER BY group_id, domain_index", tuple(domain_params))
        domains = [dict_row(r) for r in cur.fetchall()]
        
        # Get titles for these domains
        if domains:
            domain_ids = [d["id"] for d in domains]
            placeholders = ",".join(["?"] * len(domain_ids))
            cur = db_execute(conn, f"SELECT id, title, domain_id, group_id FROM titles WHERE domain_id IN ({placeholders}) ORDER BY domain_id, id", tuple(domain_ids))
            titles = [dict_row(r) for r in cur.fetchall()]
        else:
            titles = []
        cur = db_execute(conn, "SELECT title_id, recipe, article_html, article_css, main_image, ingredient_image, pin_image, model_used, generated_at, generation_time_seconds FROM article_content WHERE language_code = 'en'")
        ac_map = {}
        for r in cur.fetchall():
            row = dict_row(r)
            rid = row.get("title_id")
            recipe_ok = bool((row.get("recipe") or "").strip())
            article_html_ok = bool((row.get("article_html") or "").strip())
            article_css_ok = bool((row.get("article_css") or "").strip())
            main_img = (row.get("main_image") or "").strip()
            ing_img = (row.get("ingredient_image") or "").strip()
            pin_img = (row.get("pin_image") or "").strip()
            ac_map[rid] = {
                "has_all": recipe_ok and article_html_ok and article_css_ok,
                "has_main": bool(main_img and main_img.startswith("http")),
                "has_ingredient": bool(ing_img and ing_img.startswith("http")),
                "has_pin": bool(pin_img and pin_img.startswith("http")),
                "main_image": main_img,
                "ingredient_image": ing_img,
                "pin_image": pin_img,
                "model_used": (row.get("model_used") or "").strip(),
                "generated_at": row.get("generated_at"),
                "generation_time_seconds": row.get("generation_time_seconds"),
            }
    domain_titles = {}
    for t in titles:
        did = t["domain_id"]
        if did not in domain_titles:
            domain_titles[did] = []
        domain_titles[did].append(t)
    group_domains = {}
    for d in domains:
        gid = d.get("group_id")
        if gid not in group_domains:
            group_domains[gid] = []
        d["titles"] = domain_titles.get(d["id"], [])
        group_domains[gid].append(d)
    result = []
    for g in groups:
        g["domains"] = sorted(group_domains.get(g["id"], []), key=lambda x: x.get("domain_index") or 0)
        result.append(g)
    ungrouped = group_domains.get(None, [])
    if ungrouped:
        for d in ungrouped:
            d["titles"] = domain_titles.get(d["id"], [])
        result.append({"id": None, "name": "Ungrouped", "domains": ungrouped})
    return result, ac_map


def _render_groups_html(groups_data, ac_map):
    """Render groups HTML fragment for database management."""
    labels = ["A", "B", "C", "D"]
    groups_html = ""
    for grp in groups_data:
        grp_name = grp.get("name") or f"Group {grp.get('id')}"
        doms = grp.get("domains", [])
        dom_a = next((d for d in doms if d.get("domain_index") == 0), None)
        title_a_map = {}
        row_ids = {}  # (group_id, title_text) -> [idA, idB, idC, idD]
        for d in doms:
            for t in d.get("titles", []):
                key = (grp.get("id"), t.get("title", ""))
                if key not in row_ids:
                    row_ids[key] = [None, None, None, None]
                idx = d.get("domain_index") if d.get("domain_index") is not None and 0 <= d.get("domain_index") < 4 else 0
                row_ids[key][idx] = t.get("id")
        run_col_html = ""
        if dom_a:
            for ta in dom_a.get("titles", []):
                title_a_map[(grp.get("id"), ta.get("title", ""))] = ta.get("id")
            def _row_priority(ta):
                tid = ta.get("id")
                ttxt = ta.get("title", "")
                ids = row_ids.get((grp.get("id"), ttxt), [tid, None, None, None])
                if ids[0] is None:
                    ids[0] = tid
                ac = ac_map.get(ids[0] or 0, {})
                c_ok = ac.get("has_all", False)
                m_ok = bool((ac.get("main_image") or "").startswith("http"))
                ing_ok = bool((ac.get("ingredient_image") or "").startswith("http"))
                if c_ok and m_ok and ing_ok:
                    return 3
                elif c_ok and m_ok:
                    return 1
                elif c_ok:
                    return 0
                else:
                    return 2
            sorted_titles = sorted(dom_a.get("titles", []), key=_row_priority)
            header_parts = []
            for i in range(4):
                dm = next((d for d in doms if d.get("domain_index") == i), {})
                lb = labels[i] if i < len(labels) else str(i)
                dm_id = dm.get("id") or "-"
                dm_name = (dm.get("domain_url") or "").strip() or "-"
                template = (dm.get("website_template") or "").strip() or "—"
                template_esc = html.escape(template)
                
                # Make domain name clickable to filter by this domain
                if dm.get("id"):
                    domain_link = f'<a href="/database-management?domain_id={dm["id"]}" class="text-decoration-none" title="View this domain only">{dm_id} {dm_name}({lb})</a>'
                else:
                    domain_link = f'{dm_id} {dm_name}({lb})'
                
                header_parts.append(
                    f'<span class="d-inline-block"><span>{domain_link}</span><br><span class="text-muted" style="font-size:0.65rem;font-weight:400;" title="Article generator">{template_esc}</span></span>'
                )
            domain_header = " &nbsp; ".join(header_parts)
            
            # Add button to view all articles in this group
            view_group_btn = ""
            if grp.get("id"):
                view_group_btn = f'<a href="/database-management?group_id={grp["id"]}" class="btn btn-sm btn-outline-info ms-2" title="View only this group">🔍 View Group</a>'
            
            run_col_html = f'<li class="domain-header-row py-1 px-2 bg-light border-bottom d-flex justify-content-between align-items-center" style="font-weight:600;font-size:0.7rem;"><span>{domain_header}</span>{view_group_btn}</li>'
            for ta in sorted_titles:
                tid = ta.get("id")
                ttxt = ta.get("title", "")
                ids = row_ids.get((grp.get("id"), ttxt), [tid, None, None, None])
                if ids[0] is None:
                    ids[0] = tid
                main_urls = [ac_map.get(ids[i] or 0, {}).get("main_image", "") or "" for i in range(4)]
                ing_urls = [ac_map.get(ids[i] or 0, {}).get("ingredient_image", "") or "" for i in range(4)]
                has_main_list = [bool(u and u.startswith("http")) for u in main_urls]
                has_ing_list = [bool(u and u.startswith("http")) for u in ing_urls]
                has_all_list = [ac_map.get(ids[i] or 0, {}).get("has_all", False) for i in range(4)]
                a_has_all = ac_map.get(ids[0] or 0, {}).get("has_all", False)
                def action_pill(i):
                    lb = labels[i] if i < 4 else "?"
                    tid_i = ids[i] if i < len(ids) else None
                    dm_i = next((d for d in doms if d.get("domain_index") == i), {})
                    nm_i = (dm_i.get("domain_url") or dm_i.get("domain_name") or "").strip() or "-"
                    pill_label_raw = f"{tid_i}({nm_i})({lb})" if tid_i else f"-(-)({lb})"
                    pill_label = (pill_label_raw or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
                    ac_i = ac_map.get(tid_i or 0, {}) if tid_i else {}
                    c_ok = ac_i.get("has_all", False)
                    m_ok = bool((ac_i.get("main_image") or "").startswith("http"))
                    ing_ok = bool((ac_i.get("ingredient_image") or "").startswith("http"))
                    if c_ok and m_ok and ing_ok:
                        pill_class = "pill-success"
                    elif c_ok and m_ok:
                        pill_class = "pill-warning"
                    elif c_ok:
                        pill_class = "pill-info"
                    else:
                        pill_class = "pill-empty"
                    if not tid_i:
                        return f'<span class="run-domain-action-pill {pill_class}"><span class="pill-label">{pill_label}</span><span class="pill-btns">-</span></span>'
                    pill_hint = ""
                    if c_ok:
                        mu = (ac_i.get("model_used") or "").strip()
                        ga = ac_i.get("generated_at")
                        ga_str = (str(ga)[:10] if ga else "") or ""
                        gs = ac_i.get("generation_time_seconds")
                        gs_str = (f"{gs}s" if gs is not None else "") or ""
                        if mu or ga_str or gs_str:
                            short_model = (mu.replace("openrouter -> ", "OR ")[:25] + ("…" if len(mu) > 25 else "")) if mu else ""
                            title_esc = (mu or "-").replace('"', "&quot;") + "; Generated: " + ga_str + ("; Time: " + gs_str if gs_str else "")
                            pill_hint = f'<span class="pill-hint small text-muted" title="Model: {title_esc}">{short_model}{" · " + ga_str if ga_str else ""}{" · " + gs_str if gs_str else ""}</span>'
                    if i == 0:
                        btns = f'<button type="button" class="btn btn-success btn-sm" onclick="openSingleActionModal(\'/api/generate-article-external\',{{title_id:{tid_i}}},\'Article A\')" title="Article">Art</button>'
                        btns += f'<button type="button" class="btn btn-info btn-sm text-white" onclick="openSingleActionModal(\'/api/generate-main-image\',{{title_id:{tid_i}}},\'Main image\')" title="Main image">M</button>'
                        btns += f'<button type="button" class="btn btn-warning btn-sm text-dark" onclick="openSingleActionModal(\'/api/generate-ingredient-image\',{{title_id:{tid_i}}},\'Ingredient image\')" title="Ingredient">I</button>'
                        btns += f'<button type="button" class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); openPinPickerModal({tid_i})" title="Pin">P</button>'
                        btns += f'<button type="button" class="btn btn-outline-secondary btn-sm" onclick="viewDomainSingle({tid_i},\'{lb}\')" title="View all">V</button>'
                    else:
                        dis = ' disabled' if not a_has_all else ''
                        ta_id = ids[0]
                        btns = f'<button type="button" class="btn btn-primary btn-sm"{dis} onclick="openSingleActionModal(\'/api/generate-article-bcd\',{{title_id:{tid_i}}},\'BCD\')" title="Content from A">C</button>'
                        btns += f'<button type="button" class="btn btn-info btn-sm text-white" onclick="openSingleActionModal(\'/api/generate-main-image\',{{title_id:{ta_id}}},\'Main image\')" title="Main (all)">M</button>'
                        btns += f'<button type="button" class="btn btn-warning btn-sm text-dark" onclick="openSingleActionModal(\'/api/generate-ingredient-image\',{{title_id:{ta_id}}},\'Ingredient image\')" title="Ingr (all)">I</button>'
                        btns += f'<button type="button" class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); openPinPickerModal({tid_i})" title="Pin">P</button>'
                        btns += f'<button type="button" class="btn btn-outline-secondary btn-sm" onclick="viewDomainSingle({tid_i},\'{lb}\')" title="View all">V</button>'
                    return f'<span class="run-domain-action-pill {pill_class}"><span class="pill-label">{pill_label}</span><span class="pill-btns">{btns}</span>{pill_hint}</span>'
                action_pills = "".join(action_pill(i) for i in range(4))
                has_main = any(has_main_list)
                has_ing = any(has_ing_list)
                has_all = any((ac_map.get(ids[i] or 0, {}).get("has_all", False) for i in range(4) if ids[i]))
                esc = lambda u: (u or "").replace("\\", "\\\\").replace("'", "\\'")
                main_join = "|||".join(esc(u) for u in main_urls)
                ing_join = "|||".join(esc(u) for u in ing_urls)
                pin_urls = [ac_map.get(ids[i] or 0, {}).get("pin_image", "") or "" for i in range(4)]
                pin_join = "|||".join(esc(u) for u in pin_urls)
                has_pin = any((u and u.startswith("http") for u in pin_urls))
                ids_str = ",".join(str(x) for x in ids if x)
                lbl_parts = []
                for i in range(4):
                    dm = next((d for d in doms if d.get("domain_index") == i), {})
                    lb = labels[i] if i < len(labels) else str(i)
                    nm = (dm.get("domain_url") or dm.get("domain_name") or "").strip()
                    ti = ids[i] if i < len(ids) else None
                    part = f"Group {grp_name} | Domain {lb}"
                    if nm:
                        part += f" ({nm})"
                    if ti:
                        part += f" | id:{ti}"
                    lbl_parts.append(part)
                lbl_join = "|||".join(esc(p) for p in lbl_parts)
                vb = ""
                if has_main: vb += f'<button type="button" class="btn btn-outline-secondary btn-sm py-0 px-1" onclick="viewImagesAll(\'{main_join}\',\'Main images\',\'{lbl_join}\')" title="Main images">M</button>'
                if has_ing: vb += f'<button type="button" class="btn btn-outline-secondary btn-sm py-0 px-1" onclick="viewImagesAll(\'{ing_join}\',\'Ingredient images\',\'{lbl_join}\')" title="Ingredient images">I</button>'
                if has_pin: vb += f'<button type="button" class="btn btn-outline-secondary btn-sm py-0 px-1" onclick="viewImagesAll(\'{pin_join}\',\'Pin images\',\'{lbl_join}\')" title="Pin images">P</button>'
                if has_all: vb += f'<button type="button" class="btn btn-outline-secondary btn-sm py-0 px-1" onclick="viewContentAll(\'{ids_str}\',\'{lbl_join}\')" title="Content A,B,C,D">C</button>'
                if has_all: vb += f'<button type="button" class="btn btn-outline-secondary btn-sm py-0 px-1" onclick="viewRecipeAll(\'{ids_str}\',\'{lbl_join}\')" title="Recipe A,B,C,D">R</button>'
                vbs = f'<span class="d-flex gap-1">{vb}</span>' if vb else ""
                tdisp_run = ttxt[:50] + ("…" if len(ttxt) > 50 else "")
                ttxt_esc = (ttxt or "").replace('"', "&quot;")
                run_col_html += f'<li class="title-row d-flex flex-column gap-0 mb-1 py-1"><div class="run-domain-actions">{action_pills}</div><div class="d-flex align-items-center gap-1 flex-wrap"><span class="small text-muted flex-shrink-0">{tid}</span><span class="small text-truncate flex-grow-1" title="{ttxt_esc}">{tdisp_run}</span><span class="d-flex gap-1 flex-shrink-0"><button type="button" class="btn btn-secondary btn-sm" onclick="openBulkModal({tid})" title="Run for this row">Run</button>{vbs}</span></div></li>'
            grp_key = f"g{grp.get('id') or 'u'}"
            total_titles = len(sorted_titles)
            pagination_html = ""
            if total_titles > 0:
                pagination_html = f'<div id="group-pager-{grp_key}" class="d-flex align-items-center gap-2 mt-2 pt-2 border-top small flex-wrap"><label class="d-flex align-items-center gap-1 small text-muted mb-0">Per page: <input type="text" id="group-perpage-{grp_key}" value="20" size="4" class="form-control form-control-sm d-inline-block" style="width:4rem;" title="Enter number or \'all\'" onchange="showGroupPage(\'{grp_key}\', 1)" onkeypress="if(event.key===\'Enter\')showGroupPage(\'{grp_key}\',1)"></label><button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" onclick="showGroupPage(\'{grp_key}\', 1)" title="Apply">↻</button><span class="group-pager-nav"></span></div>'
            empty_li = '<li class="text-muted small py-2">-</li>'
            run_col_html = f'<ul id="group-rows-{grp_key}" class="list-unstyled mb-0">{run_col_html or empty_li}</ul>{pagination_html}'
        run_grp_btn = ""
        if grp.get("id") is not None and dom_a and dom_a.get("titles"):
            run_grp_btn = f'<button type="button" class="btn btn-light btn-sm ms-2" onclick="openBulkGroupModal({grp.get("id")})" title="Run for all rows in group">Run group</button>'
        grp_frag = "group-" + str(grp.get("id")) if grp.get("id") is not None else "group-u"
        groups_html += f"""
        <div id="{grp_frag}" class="card shadow-sm" style="flex:0 0 auto;min-width:320px;">
          <div class="card-header bg-secondary text-white py-2 d-flex align-items-center"><strong>{grp_name}</strong>{run_grp_btn}</div>
          <div class="card-body py-3"><div class="card shadow-sm"><div class="card-header py-2 bg-dark text-white small">Run · Bulk row <span class="text-white-50 small">(needs work → complete)</span></div><div class="card-body py-2 px-2">{run_col_html}</div></div></div>
        </div>
        """
    return groups_html


def _nav_groups_dropdown(groups_data):
    """Build navbar Groups dropdown: each item = group name + small text with domain URLs."""
    if not groups_data:
        return ""
    items = []
    for grp in groups_data:
        grp_name = grp.get("name") or f"Group {grp.get('id')}"
        doms = grp.get("domains", [])
        urls = []
        for d in sorted(doms, key=lambda x: x.get("domain_index") or 0):
            u = (d.get("domain_url") or d.get("domain_name") or "").strip()
            if u:
                urls.append(u)
        domain_line = " · ".join(urls) if urls else "—"
        domain_esc = html.escape(domain_line)
        grp_esc = html.escape(grp_name)
        grp_id = grp.get("id")
        frag = f"group-{grp_id}" if grp_id is not None else "group-u"
        anchor = f'<a class="dropdown-item py-2" href="/database-management#{frag}"><div class="fw-medium">{grp_esc}</div><div class="small text-muted" style="font-size:0.7rem;line-height:1.3;">{domain_esc}</div></a>'
        items.append(anchor)
    return f'<li class="nav-item dropdown"><a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" aria-expanded="false">Groups</a><ul class="dropdown-menu dropdown-menu-end">{chr(10).join(items)}</ul></li>'


@app.route("/database-management", methods=["GET"])
@login_required
def database_management():
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)
    
    # Support filtering by group_id (similar to /admin/domains)
    filter_group_id = request.args.get("group_id")
    filter_group_id = int(filter_group_id) if filter_group_id and str(filter_group_id).isdigit() else None
    
    # Support filtering by domain_id
    filter_domain_id = request.args.get("domain_id")
    filter_domain_id = int(filter_domain_id) if filter_domain_id and str(filter_domain_id).isdigit() else None
    
    # Get user's accessible domains
    user_domain_ids = get_user_domain_ids(user_id, is_admin)
    
    groups_data, ac_map = _get_groups_with_domains_and_titles(
        filter_group_id=filter_group_id,
        filter_domain_id=filter_domain_id,
        user_domain_ids=user_domain_ids if not is_admin else None
    )
    
    groups_html = _render_groups_html(groups_data, ac_map)
    err = request.args.get("err", "")
    
    # Build filter info
    filter_info = ""
    if filter_group_id:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT name FROM `groups` WHERE id = ?", (filter_group_id,))
            g = dict_row(cur.fetchone())
            if g:
                filter_info = f'''
                <div class="alert alert-info alert-dismissible">
                    <strong>Filtered by group:</strong> {html.escape(g["name"])}
                    <button type="button" class="btn-close" onclick="window.location.href='/database-management'"></button>
                </div>
                '''
    elif filter_domain_id:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_name FROM domains WHERE id = ?", (filter_domain_id,))
            d = dict_row(cur.fetchone())
            if d:
                filter_info = f'''
                <div class="alert alert-info alert-dismissible">
                    <strong>Filtered by domain:</strong> {html.escape(d["domain_name"])}
                    <button type="button" class="btn-close" onclick="window.location.href='/database-management'"></button>
                </div>
                '''
    
    if filter_group_id:
        group_name = next((g["name"] for g in groups_data if g["id"] == filter_group_id), "Current Group")
        escaped_group_name = html.escape(group_name).replace("'", "\\'")
        run_all_btn = f'<button type="button" class="btn btn-primary btn-sm ms-2" onclick="openBulkGroupModal({filter_group_id}, \'{escaped_group_name}\')" title="Run for all rows in this group">Run this group</button>'
    else:
        run_all_btn = '<button type="button" class="btn btn-primary btn-sm ms-2" onclick="openBulkAllGroupsModal()" title="Run for all groups">Run all groups</button>' if any(grp.get("id") is not None for grp in groups_data) else ""
    
    # Add link to admin/domains
    admin_domains_btn = '<a href="/admin/domains" class="btn btn-outline-secondary btn-sm ms-2">📋 Domains Admin</a>'
    
    # Build group filter dropdown
    with get_connection() as conn:
        if not is_admin and user_domain_ids:
            placeholders = ",".join(["?"] * len(user_domain_ids))
            cur = db_execute(conn, f"""
                SELECT DISTINCT g.id, g.name, g.parent_group_id
                FROM `groups` g
                JOIN domains d ON d.group_id = g.id
                WHERE d.id IN ({placeholders})
                ORDER BY g.name
            """, tuple(user_domain_ids))
        else:
            cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` ORDER BY name")
        all_groups = [dict_row(r) for r in cur.fetchall()]
    
    group_filter_options = '<option value="">-- All Groups --</option>'
    for g in all_groups:
        selected = 'selected' if filter_group_id == g["id"] else ''
        group_name_escaped = html.escape(g["name"])
        group_filter_options += f'<option value="{g["id"]}" {selected}>{group_name_escaped}</option>'
    
    content_html = f"""
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <h1 class="h3 mb-0 fw-bold">Database Management{run_all_btn}</h1>
        <div class="d-flex gap-2 flex-wrap">
            <select class="form-select form-select-sm" style="width:200px" onchange="window.location.href='/database-management?group_id='+this.value">
                {group_filter_options}
            </select>
            {admin_domains_btn}
        </div>
    </div>
    {f'<div class="alert alert-warning mb-4">{err}</div>' if err else ''}
    {filter_info}
    <div id="running-tasks-panel" class="mb-3" style="display:none"></div>
    <div class="mb-4 groups-scroll-wrapper" style="overflow-x:auto;padding-bottom:0.5rem;">
      <div id="groups-container" style="display:flex;flex-direction:row;flex-wrap:nowrap;gap:1rem;min-width:min-content;">{groups_html or "<p class='text-muted'>No groups. Add domains and group them from Admin Domains.</p>"}</div>
    </div>
    <script>
    // Initialize pagination for all groups on page load
    document.addEventListener('DOMContentLoaded', function() {{
      // Find all group containers and initialize their pagination
      var groupPagers = document.querySelectorAll('[id^="group-pager-"]');
      groupPagers.forEach(function(pager) {{
        var grpKey = pager.id.replace('group-pager-', '');
        if (typeof showGroupPage === 'function') {{
          showGroupPage(grpKey, 1);
        }}
      }});
    }});
    </script>
    """
    nav_extra = _nav_groups_dropdown(groups_data)
    return base_layout(content_html, "Database Management", nav_extra=nav_extra)


@app.route("/api/database-management-groups", methods=["GET"])
def api_database_management_groups():
    """Return groups HTML fragment for 60s auto-refresh."""
    groups_data, ac_map = _get_groups_with_domains_and_titles()
    return _render_groups_html(groups_data, ac_map) or "<p class='text-muted'>No groups.</p>"


@app.route("/database-management/rewrite", methods=["POST"])
def do_rewrite():
    article = request.form.get("article", "")
    result = rewrite(article)
    enc = base64.urlsafe_b64encode(json.dumps(result).encode()).decode()
    return redirect(url_for("database_management", r=enc))


def _build_group_filter_alert(group_hierarchy_path, domain_count):
    """Build alert HTML for group filter without backslash in f-string."""
    if not group_hierarchy_path:
        return ""
    path_str = " > ".join(bc['name'] for bc in group_hierarchy_path)
    close_onclick = 'window.location.href="/admin/domains"'
    return f"<div class='alert alert-info alert-dismissible'><strong>Filtered by group:</strong> {path_str} <span class='badge bg-primary'>{domain_count} domain(s)</span> <button type='button' class='btn-close' onclick='{close_onclick}'></button></div>"


def _parse_openrouter_models(req):
    """Parse openrouter_models from request (list, JSON string, or comma-separated string). Return None or list of model ids."""
    raw = req.get("openrouter_models")
    if raw is None:
        return None
    if isinstance(raw, list):
        return [str(m).strip() for m in raw if str(m).strip()] or None
    s = (raw if isinstance(raw, str) else str(raw)).strip()
    if not s:
        return None
    if s.startswith("["):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(m).strip() for m in parsed if str(m).strip()] or None
        except json.JSONDecodeError:
            pass
    return [x.strip() for x in s.split(",") if x.strip()] or None


def _do_generate_article_external(title_id, recipe_from_a=None, ai_provider=None, openrouter_models=None, local_model=None, user_id=None):
    """Call external API http://localhost:8000/generate-article/{website_template} and save to article_content.
    When recipe_from_a is provided (from Domain A), B/C/D use it to generate from recipe instead of from title.
    ai_provider: optional override (openrouter, openai, local).
    openrouter_models: optional list of OpenRouter model ids to use (rotation over this list). If None, generator uses its full list.
    local_model: optional Local model id (e.g., qwen3:8b) when ai_provider=local.
    user_id: optional user ID to use user-specific API keys."""
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT t.id, t.title, t.domain_id
            FROM titles t WHERE t.id = ?""", (title_id,))
        row = dict_row(cur.fetchone())
        if not row:
            raise ValueError("Title not found")
        title_text = (row.get("title") or "").strip()
        domain_id = row.get("domain_id")
        if not domain_id:
            raise ValueError("Title has no domain")
        cur = db_execute(conn, "SELECT website_template, categories_list, article_template_config, domain_colors, domain_fonts, writers, last_writer_index, domain_index, group_id FROM domains WHERE id = ?", (domain_id,))
        d = dict_row(cur.fetchone())
        template = (d.get("website_template") or "").strip()
        domain_index = d.get("domain_index")
        group_id = d.get("group_id")
        if not template:
            raise ValueError("Domain has no website_template. Set it in Admin Domains.")
        categories_raw = (d.get("categories_list") or "").strip()
        categories_list = []
        if categories_raw:
            try:
                categories_list = json.loads(categories_raw)
                if not isinstance(categories_list, list):
                    categories_list = []
            except json.JSONDecodeError:
                pass
        ac_row = None
        cur = db_execute(conn, """SELECT main_image, ingredient_image, top_image, bottom_image, avatar_image, pin_image
            FROM article_content WHERE title_id = ? AND language_code = 'en'""", (title_id,))
        ac_row = dict_row(cur.fetchone())
    IMAGE_FIELDS = ("main_image", "ingredient_image", "top_image", "bottom_image", "avatar_image", "pin_image")
    IMAGE_TO_CONFIG = {"main_image": "main_article_image", "ingredient_image": "ingredient_image", "top_image": "top_image", "bottom_image": "bottom_image", "avatar_image": "avatar_image"}
    base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
    url = f"{base}/generate-article/{template}"
    payload = {"title": title_text}
    
    # Add user-specific API keys to payload
    if user_id:
        user_config = get_user_config_for_api(user_id)
        # Add API keys to payload so external generator can use them
        if user_config.get("openai_api_key"):
            payload["openai_api_key"] = user_config["openai_api_key"]
        if user_config.get("openrouter_api_key"):
            payload["openrouter_api_key"] = user_config["openrouter_api_key"]
        if user_config.get("local_api_url"):
            payload["local_api_url"] = user_config["local_api_url"]
        if user_config.get("local_models"):
            payload["local_models"] = user_config["local_models"]
    
    if ai_provider and str(ai_provider).strip():
        payload["ai_provider"] = str(ai_provider).strip().lower()
    if openrouter_models is not None and isinstance(openrouter_models, list) and len(openrouter_models) > 0:
        payload["openrouter_models"] = [str(m).strip() for m in openrouter_models if str(m).strip()]
    if local_model and str(local_model).strip():
        payload["local_model"] = str(local_model).strip()
    if domain_index is not None:
        payload["domain_index"] = int(domain_index) if isinstance(domain_index, (int, float)) else 0
    if group_id is not None:
        payload["group_id"] = int(group_id) if isinstance(group_id, (int, float)) else 0
    if categories_list:
        payload["categories_list"] = categories_list
    if ac_row:
        images_config = {}
        for f in IMAGE_FIELDS:
            val = (ac_row.get(f) or "").strip()
            if val and (val.startswith("http") or val.startswith("//")):
                payload[f] = val
                cfg_key = IMAGE_TO_CONFIG.get(f)
                if cfg_key:
                    images_config[cfg_key] = val
        if "main_article_image" not in images_config and payload.get("main_image"):
            images_config["main_article_image"] = payload["main_image"]
        if "ingredient_image" not in images_config and payload.get("ingredient_image"):
            images_config["ingredient_image"] = payload["ingredient_image"]
        if "recipe_card_image" not in images_config and payload.get("main_image"):
            images_config["recipe_card_image"] = payload["main_image"]
        elif "recipe_card_image" not in images_config and payload.get("ingredient_image"):
            images_config["recipe_card_image"] = payload["ingredient_image"]
        if images_config:
            payload.setdefault("images", {})
            if isinstance(payload.get("images"), dict):
                payload["images"].update(images_config)
            else:
                payload["images"] = images_config
    cfg_raw = (d.get("article_template_config") or "").strip()
    if cfg_raw:
        try:
            domain_config = json.loads(cfg_raw) if isinstance(cfg_raw, str) else cfg_raw
            if isinstance(domain_config, dict):
                for k, v in domain_config.items():
                    if k not in payload:
                        payload[k] = v
        except json.JSONDecodeError:
            pass
    # Merge domain_colors for articles (primary, secondary, etc.)
    dc_raw = (d.get("domain_colors") or "").strip()
    if dc_raw:
        try:
            dc = json.loads(dc_raw) if isinstance(dc_raw, str) else dc_raw
            if isinstance(dc, dict):
                payload.setdefault("colors", {})
                if isinstance(payload.get("colors"), dict):
                    for k, v in dc.items():
                        if v:
                            payload["colors"][k] = v
        except json.JSONDecodeError:
            pass
    if "colors" not in payload or not payload.get("colors"):
        payload["colors"] = dict(DEFAULT_DOMAIN_COLORS)
    # Merge domain_fonts for articles (heading, body)
    df_raw = (d.get("domain_fonts") or "").strip()
    if df_raw:
        try:
            fonts_cfg = _domain_fonts_to_config(df_raw)
            payload.setdefault("fonts", {})
            if isinstance(payload.get("fonts"), dict):
                for k, v in fonts_cfg.items():
                    if v:
                        payload["fonts"][k] = v
        except Exception:
            pass
    
    # Writer rotation: pick next writer from domain's writers list
    writers_raw = (d.get("writers") or "").strip()
    if writers_raw:
        try:
            writers = json.loads(writers_raw) if isinstance(writers_raw, str) else writers_raw
            if isinstance(writers, list) and len(writers) > 0:
                last_idx = d.get("last_writer_index") or 0
                next_idx = (last_idx + 1) % len(writers)
                writer = writers[next_idx]
                if isinstance(writer, dict):
                    payload["writer"] = {
                        "name": writer.get("name", ""),
                        "title": writer.get("title", ""),
                        "bio": writer.get("bio", ""),
                        "avatar": writer.get("avatar", "")
                    }
                    # Update last_writer_index for next article
                    with get_connection() as conn2:
                        db_execute(conn2, "UPDATE domains SET last_writer_index = ? WHERE id = ?", (next_idx, domain_id))
        except json.JSONDecodeError:
            pass
    if recipe_from_a is not None:
        if isinstance(recipe_from_a, dict):
            payload["recipe"] = recipe_from_a
        elif isinstance(recipe_from_a, str) and recipe_from_a.strip():
            try:
                payload["recipe"] = json.loads(recipe_from_a)
            except json.JSONDecodeError:
                pass
    
    _enforce_pinterest_pin_color(payload)
    _MAX_RETRIES = 3
    # When OpenRouter returns 400 "Content generation failed after 3 attempt(s)", retry with different model set (openrouter_start_index=5 then 10) so we try up to 9 models total
    _openrouter_extra_starts = [5, 10]
    use_openrouter = (payload.get("ai_provider") or "").strip().lower() == "openrouter"
    out = None
    t0 = time.time()
    for _round in range(1 + (len(_openrouter_extra_starts) if use_openrouter else 0)):
        if _round > 0:
            payload["openrouter_start_index"] = _openrouter_extra_starts[_round - 1]
            log.warning("[generate-article-external] retry round %s with openrouter_start_index=%s (different model set)", _round + 1, payload["openrouter_start_index"])
        else:
            payload.pop("openrouter_start_index", None)
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
        log.info("[generate-article-external] payload url=%s round=%s", url, _round + 1)
        for _attempt in range(_MAX_RETRIES + 1):
            try:
                with urllib.request.urlopen(req, timeout=360) as resp:  # 6 min - generator does multiple OpenAI calls
                    raw = resp.read().decode()
                    out = json.loads(raw)
                keys = list(out.keys()) if isinstance(out, dict) else []
                log.info("[generate-article-external] response keys=%s", keys)
                resp_log = {}
                for k, v in (out or {}).items():
                    if isinstance(v, str) and len(v) > 200:
                        resp_log[k] = f"<str len={len(v)} preview={repr(v[:100])}...>"
                    elif isinstance(v, (dict, list)):
                        resp_log[k] = f"<{type(v).__name__} len={len(v)}>"
                    else:
                        resp_log[k] = v
                log.info("[generate-article-external] response=%s", json.dumps(resp_log, ensure_ascii=False, default=str)[:2000])
                try:
                    debug_path = os.path.join(os.path.dirname(__file__), "..", ".logs", "generate-article-debug.json")
                    os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                    with open(debug_path, "w", encoding="utf-8") as f:
                        json.dump(out, f, indent=2, ensure_ascii=False)
                    log.info("[generate-article-external] full response saved to .logs/generate-article-debug.json")
                except Exception as e:
                    log.warning("[generate-article-external] could not save debug file: %s", e)
                break  # success — exit attempt loop
            except urllib.error.HTTPError as e:
                err_body = e.read().decode() if e.fp else str(e)
                log.warning("[generate-article-external] external API HTTP %s response: %s", e.code, err_body[:1500])
                if "insufficient_quota" in err_body or "quota" in err_body.lower():
                    _app_log("article", False, f"OpenAI quota exceeded (HTTP {e.code})", reason=err_body[:300], title_id=title_id)
                    raise ValueError(f"OpenAI quota exceeded — check billing. HTTP {e.code}: {err_body[:300]}")
                # 400 "Content generation failed after 3 attempt(s)" with OpenRouter: try next round with different model set
                if e.code == 400 and "Content generation failed after 3 attempt(s)" in err_body and use_openrouter and _round < len(_openrouter_extra_starts):
                    log.warning("[generate-article-external] 400 after 3 attempts (OpenRouter), retrying with different model set (round %s)", _round + 2)
                    break  # exit attempt loop, continue to next _round
                if _attempt < _MAX_RETRIES and (e.code >= 500 or e.code in (408, 429)):
                    wait = (_attempt + 1) * 10
                    log.warning("[generate-article-external] retry %d/%d after HTTP %s, waiting %ds...", _attempt + 1, _MAX_RETRIES, e.code, wait)
                    time.sleep(wait)
                    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
                    continue
                _app_log("article", False, f"External API error {e.code}", reason=err_body[:300], title_id=title_id)
                raise ValueError(f"External API error {e.code}: {err_body[:500]}")
            except (urllib.error.URLError, OSError) as e:
                log.warning("[generate-article-external] connection/timeout error: %s", e)
                if _attempt < _MAX_RETRIES:
                    wait = (_attempt + 1) * 10
                    log.warning("[generate-article-external] retry %d/%d, waiting %ds...", _attempt + 1, _MAX_RETRIES, wait)
                    time.sleep(wait)
                    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
                    continue
                _app_log("article", False, f"API unreachable after {_MAX_RETRIES} retries: {e}", title_id=title_id)
                raise ValueError(f"External API unreachable after {_MAX_RETRIES} retries: {e}")
        if out is not None:
            break
    if out is None:
        raise ValueError("External API returned no data after retries")

    article_html = (out.get("article_html") or out.get("article") or
                    (out.get("data") or {}).get("article_html") or (out.get("data") or {}).get("article") or "")
    if not isinstance(article_html, str):
        article_html = str(article_html) if article_html else ""
    article_html = article_html.strip()
    log.info("[generate-article-external] article_html len=%s (has_html=%s)", len(article_html), article_html.startswith("<") if article_html else False)
    if not article_html and isinstance(out, dict):
        log.warning("[generate-article-external] article_html EMPTY - response keys: %s", list(out.keys()))
    recipe = out.get("recipe")
    recipe_str = json.dumps(recipe, ensure_ascii=False) if isinstance(recipe, dict) else (recipe or "")
    prompt = (out.get("prompt_midjourney_main") or out.get("prompt_used") or out.get("prompt", "") or "").strip()
    prompt_ing = (out.get("prompt_midjourney_ingredients") or out.get("prompt_image_ingredients") or "").strip()
    if not prompt or len(prompt) < 25 or prompt == "--v 6.1":
        prompt = f"Professional food photography of {title_text}, overhead shot, natural lighting, editorial style --v 6.1"
    if not prompt_ing or len(prompt_ing) < 25 or prompt_ing == "--v 6.1":
        prompt_ing = f"Flat-lay of ingredients for {title_text}, white surface, natural light, editorial style --v 6.1"
    article_css = (out.get("article_css") or out.get("content_css") or
                  (out.get("data") or {}).get("article_css") or (out.get("data") or {}).get("content_css") or "")
    if not isinstance(article_css, str):
        article_css = str(article_css) if article_css else ""
    article_css = article_css.strip()
    log.info("[generate-article-external] article_css len=%s", len(article_css))
    
    # Inject writer HTML at top of article if writer_template is set
    if article_html and payload.get("writer"):
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT writer_template, domain_colors, article_template_config FROM domains WHERE id = ?", (domain_id,))
            dom = dict_row(cur.fetchone())
            writer_tpl = (dom.get("writer_template") or "").strip()
            if writer_tpl:
                log.info(f"[generate-article-external] Injecting writer template: {writer_tpl}")
                # Build config for writer template
                writer_config = {"writer": payload["writer"]}
                # Add colors
                dc_raw = (dom.get("domain_colors") or "").strip()
                if dc_raw:
                    try:
                        dc = json.loads(dc_raw)
                        if isinstance(dc, dict):
                            writer_config["colors"] = dc
                    except:
                        pass
                if "colors" not in writer_config:
                    writer_config["colors"] = dict(DEFAULT_DOMAIN_COLORS)
                # Fetch writer HTML/CSS from website-parts-generator
                writer_part = _fetch_site_part_internal("writer", writer_tpl, writer_config)
                if writer_part and writer_part.get("html"):
                    writer_html = writer_part["html"]
                    writer_css = writer_part.get("css", "")
                    
                    # NOTE: Article generators produce single-column HTML without sidebar
                    # The sidebar is added by the preview-website system when displaying
                    # So we DON'T inject writer into article_html here
                    # Instead, we just save the writer data to article_content table
                    # The preview-website will handle injecting writer into sidebar-area
                    
                    log.info(f"[generate-article-external] Writer data prepared (will be injected by preview-website into sidebar)")
                    
                    # Append writer CSS to article CSS for when it's used
                    if writer_css:
                        article_css = article_css + "\n\n/* Writer Byline */\n" + writer_css
    
    def _valid_url(v):
        s = (v or "").strip()
        return s if s and (s.startswith("http") or s.startswith("//")) else ""

    main_img = _valid_url(out.get("main_image"))
    ing_img = _valid_url(out.get("ingredient_image"))
    top_img = _valid_url(out.get("top_image"))
    bottom_img = _valid_url(out.get("bottom_image"))
    avatar_img = _valid_url(out.get("avatar_image"))

    # Preserve existing image URLs if generator returned empty/placeholder
    existing_imgs = {}
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT main_image, ingredient_image, top_image, bottom_image, avatar_image FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
        row = dict_row(cur.fetchone())
        if row:
            for k in ("main_image", "ingredient_image", "top_image", "bottom_image", "avatar_image"):
                existing_imgs[k] = _valid_url(row.get(k))
    if not main_img and existing_imgs.get("main_image"):
        main_img = existing_imgs["main_image"]
    if not ing_img and existing_imgs.get("ingredient_image"):
        ing_img = existing_imgs["ingredient_image"]
    if not top_img and existing_imgs.get("top_image"):
        top_img = existing_imgs["top_image"]
    if not bottom_img and existing_imgs.get("bottom_image"):
        bottom_img = existing_imgs["bottom_image"]
    if not avatar_img and existing_imgs.get("avatar_image"):
        avatar_img = existing_imgs["avatar_image"]

    model_used = (out.get("model_used") or "").strip()
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    generation_time_seconds = int(round(time.time() - t0))
    
    # Prepare writer data for saving
    writer_json = ""
    writer_avatar_url = ""
    if payload.get("writer"):
        writer_json = json.dumps(payload["writer"])
        writer_avatar_url = payload["writer"].get("avatar", "")
    
    vals = (
        article_html, recipe_str, prompt, prompt_ing,
        out.get("recipe_title_pin", ""), out.get("pinterest_title", ""), out.get("pinterest_description", ""),
        out.get("pinterest_keywords", ""), out.get("focus_keyphrase", ""), out.get("meta_description", ""),
        out.get("keyphrase_synonyms", ""), article_css,
        main_img, ing_img, top_img, bottom_img, avatar_img,
        writer_json, writer_avatar_url, model_used, generated_at, generation_time_seconds, title_id
    )
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
        if cur.fetchone():
            db_execute(conn, """UPDATE article_content SET article_html=?, article=?, recipe=?, prompt=?, prompt_image_ingredients=?,
                recipe_title_pin=?, pinterest_title=?, pinterest_description=?, pinterest_keywords=?,
                focus_keyphrase=?, meta_description=?, keyphrase_synonyms=?, article_css=?,
                main_image=?, ingredient_image=?, top_image=?, bottom_image=?, avatar_image=?,
                writer=?, writer_avatar=?, model_used=?, generated_at=?, generation_time_seconds=?
                WHERE title_id=? AND language_code='en'""", (vals[0],) + vals)
        else:
            db_execute(conn, """INSERT INTO article_content (title_id, language_code, article_html, article, recipe, prompt, prompt_image_ingredients,
                recipe_title_pin, pinterest_title, pinterest_description, pinterest_keywords, focus_keyphrase, meta_description, keyphrase_synonyms, article_css,
                main_image, ingredient_image, top_image, bottom_image, avatar_image, writer, writer_avatar, model_used, generated_at, generation_time_seconds)
                VALUES (?, 'en', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (title_id, vals[0]) + vals[:-1])
    _update_article_html_images(title_id)
    _update_article_html_pin_image(title_id)
    return article_html, article_css


@app.route("/api/ai-config", methods=["GET"])
def api_ai_config():
    """Return current AI provider and model for UI hints. Optional ?provider=openrouter for override."""
    provider = request.args.get("provider", "").strip()
    p, model = get_ai_config(provider)
    return jsonify({"provider": p, "model": model, "label": f"{p}/{model}"})


@app.route("/api/openrouter-models", methods=["GET"])
def api_openrouter_models():
    """Return list of OpenRouter model ids for content generation (rotation or select)."""
    return jsonify({"models": OPENROUTER_MODELS})


@app.route("/api/local-models", methods=["GET"])
def api_local_models():
    """Return list of Local model ids for content generation."""
    return jsonify({"models": LOCAL_MODELS})


@app.route("/api/generate-article-external", methods=["POST"])
@login_required
def api_generate_article_external():
    """Generate Article A via external API using domain's website_template."""
    user = get_current_user()
    user_id = user["id"]
    
    # Check user has required API keys
    has_keys, error_msg = check_user_has_required_keys(user_id, "content")
    if not has_keys:
        return jsonify({"success": False, "error": error_msg}), 403
    
    data = request.get_json(silent=True) or request.form or {}
    req = {**data, **dict(request.args)}
    title_id = req.get("title_id")
    ai_provider = (req.get("ai_provider") or "").strip() or None
    openrouter_models = _parse_openrouter_models(req)
    local_model = (req.get("local_model") or "").strip() or None
    log.info("[api/generate-article-external] request payload=%s", dict(data) if hasattr(data, "items") else data)
    async_mode = str(req.get("async") or "").lower() in ("1", "true", "yes")
    if not title_id:
        return jsonify({"success": False, "error": "title_id required"}), 400
    title_id = int(title_id)
    
    if async_mode:
        job_id = str(uuid.uuid4())
        domain_id = None
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_id FROM titles WHERE id = ?", (title_id,))
            r = dict_row(cur.fetchone())
            if r:
                domain_id = r.get("domain_id")
        _bulk_progress[job_id] = {"status": "running", "message": "Calling external Article API...", "current_title": "", "type": "single", "action": "Article A", "title_id": title_id, "domain_id": domain_id, "created_at": time.time()}
        def task():
            try:
                _do_generate_article_external(title_id, ai_provider=ai_provider, openrouter_models=openrouter_models, local_model=local_model, user_id=user_id)
                _bulk_progress[job_id].update({"status": "done", "message": "Article content generated", "has_article_html": True})
            except Exception as e:
                _bulk_progress[job_id].update({"status": "error", "message": str(e)})
        threading.Thread(target=task, daemon=True).start()
        return jsonify({"success": True, "job_id": job_id})
    try:
        article, article_css = _do_generate_article_external(title_id, ai_provider=ai_provider, openrouter_models=openrouter_models, local_model=local_model, user_id=user_id)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    resp = {"success": True, "message": "Article content generated"}
    if article is not None:
        resp["article_html"] = article
    if article_css is not None:
        resp["article_css"] = article_css
    resp_log = {}
    for k, v in resp.items():
        if isinstance(v, str) and len(v) > 300:
            resp_log[k] = f"{v[:300]}...[truncated total={len(v)}]"
        else:
            resp_log[k] = v
    log.info("[api/generate-article-external] response=%s", json.dumps(resp_log, ensure_ascii=False)[:8000])
    return jsonify(resp)


def _do_generate_article_a(title_id, prompt=""):
    """Legacy: generate Article A via rewrite module. Use generate-article-external for Domain A (Art button)."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT title FROM titles WHERE id = ?", (title_id,))
        row = dict_row(cur.fetchone())
        if not row:
            raise ValueError("Title not found")
        title_text = row.get("title", "")
    t0 = time.time()
    out = generate_article_content_for_a(title_text, prompt)
    generation_time_seconds = int(round(time.time() - t0))
    if out.get("error"):
        raise ValueError(out["error"])
    # Prefer content.blocks converted to HTML (clean structure) over raw article (may contain markdown)
    content_str = (out.get("content") or "").strip()
    article_html_val = _content_blocks_to_html(content_str) if content_str else ""
    if not article_html_val:
        article_html_val = (out.get("article") or "").strip()
    provider, model_name = get_ai_config()
    model_used = f"openrouter -> {model_name}" if provider == "openrouter" else "openai"
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    vals = (article_html_val, out.get("recipe", ""), out.get("prompt", ""), out.get("prompt_image_ingredients", ""),
            out.get("recipe_title_pin", ""), out.get("pinterest_title", ""), out.get("pinterest_description", ""),
            out.get("pinterest_keywords", ""), out.get("focus_keyphrase", ""), out.get("meta_description", ""),
            out.get("keyphrase_synonyms", ""), "", model_used, generated_at, generation_time_seconds, title_id)  # article_css empty for legacy
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
        if cur.fetchone():
            db_execute(conn, """UPDATE article_content SET article_html=?, recipe=?, prompt=?, prompt_image_ingredients=?,
                recipe_title_pin=?, pinterest_title=?, pinterest_description=?, pinterest_keywords=?,
                focus_keyphrase=?, meta_description=?, keyphrase_synonyms=?, article_css=?, model_used=?, generated_at=?, generation_time_seconds=?
                WHERE title_id=? AND language_code='en'""", vals)
        else:
            db_execute(conn,
                """INSERT INTO article_content (title_id, language_code, article_html, recipe, prompt, prompt_image_ingredients,
                   recipe_title_pin, pinterest_title, pinterest_description, pinterest_keywords, focus_keyphrase, meta_description, keyphrase_synonyms, article_css, model_used, generated_at, generation_time_seconds)
                   VALUES (?, 'en', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (title_id,) + vals[:-1])
    _update_article_html_images(title_id)
    _update_article_html_pin_image(title_id)


@app.route("/api/generate-article-a", methods=["POST"])
def api_generate_article_a():
    data = request.get_json(silent=True) or request.form or {}
    title_id = data.get("title_id") or request.args.get("title_id")
    prompt = data.get("prompt", "") or ""
    async_mode = str(data.get("async") or request.args.get("async", "") or "").lower() in ("1", "true", "yes")
    if not title_id:
        return jsonify({"success": False, "error": "title_id required"}), 400
    title_id = int(title_id)
    if async_mode:
        job_id = str(uuid.uuid4())
        domain_id = None
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_id FROM titles WHERE id = ?", (title_id,))
            r = dict_row(cur.fetchone())
            if r:
                domain_id = r.get("domain_id")
        _bulk_progress[job_id] = {"status": "running", "message": "Starting Article A...", "current_title": "", "type": "single", "action": "Article A", "title_id": title_id, "domain_id": domain_id, "created_at": time.time()}
        def task():
            try:
                _do_generate_article_a(title_id, prompt)
                _bulk_progress[job_id].update({"status": "done", "message": "Article content generated"})
            except Exception as e:
                _bulk_progress[job_id].update({"status": "error", "message": str(e)})
        threading.Thread(target=task, daemon=True).start()
        return jsonify({"success": True, "job_id": job_id})
    _do_generate_article_a(title_id, prompt)
    return jsonify({"success": True, "message": "Article content generated"})


def _do_generate_article_bcd(title_id, ai_provider=None):
    """Generate article for B/C/D domain using same flow as A: call external API with domain's template config.
    Each domain (B, C, D) gets full generation based on its own website_template and article_template_config."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT t.id, t.title, t.domain_id, t.group_id, d.domain_index FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id,))
        t = dict_row(cur.fetchone())
        if not t:
            raise ValueError("Title not found")
        dom_idx = t.get("domain_index")
        if dom_idx is None or dom_idx == 0:
            raise ValueError("Use Generate (A) for Domain A")
    article_html, article_css = _do_generate_article_external(title_id, ai_provider=ai_provider)
    if article_html is None or article_css is None:
        raise ValueError("Article generation failed. Check domain has website_template set and generator API is running.")


@app.route("/api/generate-article-bcd", methods=["POST"])
def api_generate_article_bcd():
    data = request.get_json(silent=True) or request.form or {}
    title_id = data.get("title_id") or request.args.get("title_id")
    ai_provider = (data.get("ai_provider") or request.args.get("ai_provider") or "").strip() or None
    async_mode = str(data.get("async") or request.args.get("async", "") or "").lower() in ("1", "true", "yes")
    if not title_id:
        return jsonify({"success": False, "error": "title_id required"}), 400
    title_id = int(title_id)
    if async_mode:
        job_id = str(uuid.uuid4())
        domain_id = None
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_id FROM titles WHERE id = ?", (title_id,))
            r = dict_row(cur.fetchone())
            if r:
                domain_id = r.get("domain_id")
        _bulk_progress[job_id] = {"status": "running", "message": "Starting BCD...", "current_title": "", "type": "single", "action": "BCD", "title_id": title_id, "domain_id": domain_id, "created_at": time.time()}
        def task():
            try:
                _do_generate_article_bcd(title_id, ai_provider=ai_provider)
                _bulk_progress[job_id].update({"status": "done", "message": "Article content generated (domain template)"})
            except Exception as e:
                _bulk_progress[job_id].update({"status": "error", "message": str(e)})
        threading.Thread(target=task, daemon=True).start()
        return jsonify({"success": True, "job_id": job_id})
    _do_generate_article_bcd(title_id, ai_provider=ai_provider)
    return jsonify({"success": True, "message": "Article content generated (domain template)"})


def _title_has_content(conn, title_id):
    """Return True if article_content has non-empty article_html and article_css for title_id."""
    cur = db_execute(conn, "SELECT article_html, article_css FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
    row = dict_row(cur.fetchone())
    if not row:
        return False
    html = (row.get("article_html") or "").strip()
    css = (row.get("article_css") or "").strip()
    return bool(html and css)


def _title_has_main_image(conn, title_id):
    """Return True if article_content has non-empty main_image for title_id."""
    cur = db_execute(conn, "SELECT main_image FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
    row = dict_row(cur.fetchone())
    return bool(row and (row.get("main_image") or "").strip())


def _title_has_ingredient_image(conn, title_id):
    """Return True if article_content has non-empty ingredient_image for title_id."""
    cur = db_execute(conn, "SELECT ingredient_image FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
    row = dict_row(cur.fetchone())
    return bool(row and (row.get("ingredient_image") or "").strip())


def _title_has_pin_image(conn, title_id):
    """Return True if article_content has non-empty pin_image for title_id."""
    cur = db_execute(conn, "SELECT pin_image FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
    row = dict_row(cur.fetchone())
    return bool(row and (row.get("pin_image") or "").strip())


def _should_skip_content(conn, title_id, scope_content):
    """Return True if content generation should be skipped (scope_content=empty_only and has content)."""
    if scope_content != "empty_only":
        return False
    return _title_has_content(conn, title_id)


def _row_any_needs_content(conn, title_id_a, scope_content):
    """For a row (A,B,C,D), return True if any needs content. Used with empty_only to skip row only when all 4 have content."""
    if scope_content != "empty_only":
        return True  # override mode: always need
    cur = db_execute(conn, "SELECT t.group_id, t.title, d.group_id as d_group_id FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id_a,))
    r = dict_row(cur.fetchone())
    if not r:
        return True
    gid = r.get("group_id") if r.get("group_id") is not None else r.get("d_group_id")
    cur = db_execute(conn, """SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id
        WHERE COALESCE(t.group_id, d.group_id) = ? AND t.title = ? ORDER BY d.domain_index""", (gid, r.get("title") or ""))
    ids = [dict_row(x).get("id") for x in cur.fetchall()]
    for tid in ids:
        if tid and not _title_has_content(conn, tid):
            return True
    return False


def _row_any_needs_images(conn, title_id_a, scope_images):
    """For a row (A,B,C,D), return True if any needs images. Used with empty_only to exclude rows where all 4 have main+ingredient."""
    if scope_images != "empty_only":
        return True
    cur = db_execute(conn, "SELECT t.group_id, t.title, d.group_id as d_group_id FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id_a,))
    r = dict_row(cur.fetchone())
    if not r:
        return True
    gid = r.get("group_id") if r.get("group_id") is not None else r.get("d_group_id")
    cur = db_execute(conn, """SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id
        WHERE COALESCE(t.group_id, d.group_id) = ? AND t.title = ? ORDER BY d.domain_index""", (gid, r.get("title") or ""))
    ids = [dict_row(x).get("id") for x in cur.fetchall()]
    for tid in ids:
        if tid and not (_title_has_main_image(conn, tid) and _title_has_ingredient_image(conn, tid)):
            return True
    return False


def _should_skip_images(conn, title_id, scope_images):
    """Return True if image generation should be skipped (scope_images=empty_only and has main+ingredient)."""
    if scope_images != "empty_only":
        return False
    return _title_has_main_image(conn, title_id) and _title_has_ingredient_image(conn, title_id)


def _should_skip_bulk_row(conn, title_id, mode, scope, scope_content=None, scope_images=None):
    """Return True if this row should be skipped. scope is legacy; scope_content/scope_images override per phase.
    For mode=article with empty_only: skip only when ALL of A,B,C,D have content (not just A)."""
    sc = scope_content if scope_content is not None else scope
    si = scope_images if scope_images is not None else scope
    if mode == "article":
        return not _row_any_needs_content(conn, title_id, sc)
    if mode == "images":
        return _should_skip_images(conn, title_id, si)
    if mode == "all":
        return False  # Per-phase skip in article/images blocks
    if mode in ("main_image",):
        return si == "empty_only" and _title_has_main_image(conn, title_id)
    if mode in ("ingredient_image",):
        return si == "empty_only" and _title_has_ingredient_image(conn, title_id)
    if mode in ("pin_image",):
        return si == "empty_only" and _title_has_pin_image(conn, title_id)
    return False


@app.route("/api/bulk-run", methods=["POST"])
@login_required
def api_bulk_run():
    """Bulk run: article (A+BCD), images (main+ingredient), main_image, ingredient_image, pin_image, or all. scope_content/scope_images for content vs images."""
    user = get_current_user()
    user_id = user["id"]
    data = request.get_json(silent=True) or {}
    req = {**data, **dict(request.args)}
    title_id = req.get("title_id")
    mode = str(req.get("mode", "all")).lower()
    scope = str(req.get("scope") or "override").lower()
    scope_content = str(req.get("scope_content") or scope).lower()
    scope_images = str(req.get("scope_images") or scope).lower()
    for s in (scope, scope_content, scope_images):
        if s not in ("override", "empty_only"):
            scope = scope_content = scope_images = "override"
            break
    ai_provider = (req.get("ai_provider") or "").strip() or None
    openrouter_models = _parse_openrouter_models(req)
    if not title_id:
        return jsonify({"success": False, "error": "title_id required"}), 400
    title_id = int(title_id)
    mode = str(mode).lower()
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT t.id, t.title, t.group_id, d.domain_index FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id,))
        t = dict_row(cur.fetchone())
        if not t or t.get("domain_index") != 0:
            return jsonify({"success": False, "error": "Use Domain A title_id"}), 400
        cur = db_execute(conn, "SELECT title FROM titles WHERE id = ?", (title_id,))
        title_row = dict_row(cur.fetchone())
        title_text = (title_row.get("title") or "") if title_row else ""
        cur = db_execute(conn, """SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id
            WHERE t.group_id = ? AND t.title = ? AND d.domain_index IN (0,1,2,3) ORDER BY d.domain_index""", (t["group_id"], t["title"]))
        title_ids = [dict_row(r).get("id") for r in cur.fetchall()]
    if len(title_ids) < 4:
        return jsonify({"success": False, "error": "Need 4 domains (A,B,C,D)"}), 400
    with get_connection() as conn:
        if _should_skip_bulk_row(conn, title_id, mode, scope, scope_content, scope_images):
            if mode == "article":
                return jsonify({"success": True, "message": "Skipped — row already has HTML+CSS"})
            if mode == "main_image":
                return jsonify({"success": True, "message": "Skipped — row already has main image"})
            if mode == "ingredient_image":
                return jsonify({"success": True, "message": "Skipped — row already has ingredient image"})
            if mode == "pin_image":
                return jsonify({"success": True, "message": "Skipped — row already has pin image"})
            if mode == "images":
                return jsonify({"success": True, "message": "Skipped — row already has main+ingredient images"})
    done = []
    if mode in ("article", "all"):
        with get_connection() as conn:
            skip_content = not _row_any_needs_content(conn, title_id, scope_content)
        if skip_content:
            if mode == "article":
                return jsonify({"success": True, "message": "Skipped — row already has HTML+CSS"})
        else:
            # A first, then B,C,D with recipe from A. For empty_only, skip titles that already have content.
            recipe_a = None
            with get_connection() as conn:
                gen_a = scope_content != "empty_only" or not _title_has_content(conn, title_ids[0])
            if gen_a:
                try:
                    _do_generate_article_external(title_ids[0], ai_provider=ai_provider, openrouter_models=openrouter_models)
                except Exception as e:
                    return jsonify({"success": False, "error": f"Generate article for A (title_id {title_ids[0]}): {e}"}), 500
            with get_connection() as conn:
                cur = db_execute(conn, "SELECT recipe FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_ids[0],))
                row = dict_row(cur.fetchone())
                if row:
                    rv = row.get("recipe")
                    if isinstance(rv, dict):
                        recipe_a = rv
                    elif isinstance(rv, str) and rv.strip():
                        try:
                            recipe_a = json.loads(rv)
                        except json.JSONDecodeError:
                            pass
            for tid in title_ids[1:4]:
                with get_connection() as conn:
                    if scope_content == "empty_only" and _title_has_content(conn, tid):
                        continue
                try:
                    _do_generate_article_external(tid, recipe_from_a=recipe_a, ai_provider=ai_provider, openrouter_models=openrouter_models)
                except Exception as e:
                    return jsonify({"success": False, "error": f"Generate article for title_id {tid}: {e}"}), 500
            done.append("article+BCD")
    if mode in ("images", "all"):
        with get_connection() as conn:
            skip_images = _should_skip_images(conn, title_id, scope_images)
        if not skip_images:
            from imagine import generate_4_images
            with get_connection() as conn:
                cur = db_execute(conn, "SELECT prompt, prompt_image_ingredients FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
                row = dict_row(cur.fetchone())
            prompt = (row.get("prompt") or "").strip() if row else ""
            prompt_ing = (row.get("prompt_image_ingredients") or "").strip() if row else ""
            if prompt:
                urls, err = generate_4_images(prompt, key_prefix="main_image")
                if not err:
                    from imagine import flip_image_vertical_and_upload
                    BOTTOM_SOURCE_INDEX = (1, 0, 3, 2)
                    bottom_urls = [None] * 4
                    for i in range(min(4, len(urls))):
                        src = BOTTOM_SOURCE_INDEX[i]
                        if src < len(urls) and urls[src]:
                            try:
                                bottom_urls[i] = flip_image_vertical_and_upload(urls[src], "bottom_image")
                            except Exception:
                                bottom_urls[i] = None
                    with get_connection() as conn:
                        for i, tid in enumerate(title_ids[:4]):
                            if i < len(urls):
                                main_url = urls[i]
                                bottom_url = bottom_urls[i] if i < len(bottom_urls) else None
                                cur = db_execute(conn, "UPDATE article_content SET main_image = ?, top_image = ?, bottom_image = ? WHERE title_id = ? AND language_code = 'en'", (main_url, main_url, bottom_url, tid))
                                if cur.rowcount == 0:
                                    db_execute(conn, "INSERT INTO article_content (title_id, language_code, main_image, top_image, bottom_image) VALUES (?, 'en', ?, ?, ?)", (tid, main_url, main_url, bottom_url))
            if prompt_ing:
                urls2, err2 = generate_4_images(prompt_ing, key_prefix="ingredient_image")
                if not err2:
                    with get_connection() as conn:
                        for i, tid in enumerate(title_ids[:4]):
                            if i < len(urls2):
                                cur = db_execute(conn, "UPDATE article_content SET ingredient_image = ? WHERE title_id = ? AND language_code = 'en'", (urls2[i], tid))
                                if cur.rowcount == 0:
                                    db_execute(conn, "INSERT INTO article_content (title_id, language_code, ingredient_image) VALUES (?, 'en', ?)", (tid, urls2[i]))
            for tid in title_ids[:4]:
                _update_article_html_images(tid)
            done.append("images")
    elif mode == "main_image":
        from imagine import generate_4_images
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT prompt FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
            row = dict_row(cur.fetchone())
        prompt = (row.get("prompt") or "").strip() if row else ""
        if not prompt:
            return jsonify({"success": False, "error": "Generate article first to get prompt"}), 400
        urls, err = generate_4_images(prompt, key_prefix="main_image")
        if err:
            return jsonify({"success": False, "error": err}), 500
        from imagine import flip_image_vertical_and_upload
        BOTTOM_SOURCE_INDEX = (1, 0, 3, 2)
        bottom_urls = [None] * 4
        for i in range(min(4, len(urls))):
            src = BOTTOM_SOURCE_INDEX[i]
            if src < len(urls) and urls[src]:
                try:
                    bottom_urls[i] = flip_image_vertical_and_upload(urls[src], "bottom_image")
                except Exception:
                    bottom_urls[i] = None
        with get_connection() as conn:
            for i, tid in enumerate(title_ids[:4]):
                if i < len(urls):
                    main_url = urls[i]
                    bottom_url = bottom_urls[i] if i < len(bottom_urls) else None
                    cur = db_execute(conn, "UPDATE article_content SET main_image = ?, top_image = ?, bottom_image = ? WHERE title_id = ? AND language_code = 'en'", (main_url, main_url, bottom_url, tid))
                    if cur.rowcount == 0:
                        db_execute(conn, "INSERT INTO article_content (title_id, language_code, main_image, top_image, bottom_image) VALUES (?, 'en', ?, ?, ?)", (tid, main_url, main_url, bottom_url))
        for tid in title_ids[:4]:
            _update_article_html_images(tid)
        done.append("main_image")
    elif mode == "ingredient_image":
        from imagine import generate_4_images
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT prompt_image_ingredients FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
            row = dict_row(cur.fetchone())
        prompt_ing = (row.get("prompt_image_ingredients") or "").strip() if row else ""
        if not prompt_ing:
            return jsonify({"success": False, "error": "Generate article first to get prompt_image_ingredients"}), 400
        urls2, err2 = generate_4_images(prompt_ing, key_prefix="ingredient_image")
        if err2:
            return jsonify({"success": False, "error": err2}), 500
        with get_connection() as conn:
            for i, tid in enumerate(title_ids[:4]):
                if i < len(urls2):
                    cur = db_execute(conn, "UPDATE article_content SET ingredient_image = ? WHERE title_id = ? AND language_code = 'en'", (urls2[i], tid))
                    if cur.rowcount == 0:
                        db_execute(conn, "INSERT INTO article_content (title_id, language_code, ingredient_image) VALUES (?, 'en', ?)", (tid, urls2[i]))
        for tid in title_ids[:4]:
            _update_article_html_images(tid)
        done.append("ingredient_image")
    elif mode == "pin_image":
        for tid in title_ids[:4]:
            try:
                _do_generate_pin_image(tid)
            except Exception as e:
                return jsonify({"success": False, "error": f"Generate pin for title_id {tid}: {e}"}), 500
        done.append("pin_image")
    return jsonify({"success": True, "message": f"Done: {', '.join(done)}"})


def _bulk_run_one_group(group_id, mode, progress_updater=None, job_id=None, scope="override", scope_content=None, scope_images=None, ai_provider=None, openrouter_models=None, user_id=None):
    """Run bulk-run for all rows in one group. scope_content/scope_images for per-phase skip."""
    user_config = get_user_config_for_api(user_id) if user_id else {}
    sc = scope_content if scope_content is not None else scope
    si = scope_images if scope_images is not None else scope
    with get_connection() as conn:
        def get_all_group_descendants(gid):
            result = [gid]
            cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
            children = [dict_row(r)["id"] for r in cur.fetchall()]
            for child_id in children:
                result.extend(get_all_group_descendants(child_id))
            return result
        all_gids = get_all_group_descendants(group_id)
        placeholders = ",".join(["?"] * len(all_gids))
        cur = db_execute(conn, f"""SELECT MIN(t.id) as id FROM titles t
            JOIN domains d ON t.domain_id = d.id
            WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders})
            GROUP BY COALESCE(t.group_id, d.group_id), t.title
            ORDER BY MIN(t.id)""", tuple(all_gids))
        title_a_ids = [dict_row(r).get("id") for r in cur.fetchall() if dict_row(r).get("id")]
    if not title_a_ids:
        return 0, 0
    total = len(title_a_ids)
    ok, failed = 0, 0
    for idx, title_id in enumerate(title_a_ids):
        if job_id and _bulk_cancel.get(job_id):
            break
        with get_connection() as conn:
            if _should_skip_bulk_row(conn, title_id, mode, scope, sc, si):
                continue
        try:
            with get_connection() as conn:
                cur = db_execute(conn, "SELECT t.id, t.title, t.group_id, d.group_id as d_group_id, d.domain_index, d.domain_url, d.domain_name FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id,))
                t = dict_row(cur.fetchone())
                if not t:
                    failed += 1
                    continue
                gid_val = t.get("group_id") if t.get("group_id") is not None else t.get("d_group_id")
                domain_url = (t.get("domain_url") or t.get("domain_name") or "").strip() or "-"
                cur = db_execute(conn, "SELECT title FROM titles WHERE id = ?", (title_id,))
                title_row = dict_row(cur.fetchone())
                title_text = (title_row.get("title") or "") if title_row else ""
                if progress_updater:
                    progress_updater(title_id, title_text, idx, total, ok, failed, extra={"domain_url": domain_url, "group_id": gid_val, "domain_letters": "A,B,C,D"})
                cur = db_execute(conn, """SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id
                    WHERE COALESCE(t.group_id, d.group_id) = ? AND t.title = ? ORDER BY d.domain_index""", (gid_val, t["title"]))
                ids = [dict_row(r).get("id") for r in cur.fetchall()]
            if not ids:
                failed += 1
                continue
            if mode in ("article", "all"):
                if job_id and _bulk_cancel.get(job_id):
                    break
                with get_connection() as conn:
                    skip_content = not _row_any_needs_content(conn, title_id, sc)
                if not skip_content:
                    article_ok = True
                    with get_connection() as conn:
                        gen_a = sc != "empty_only" or not _title_has_content(conn, ids[0])
                    if gen_a:
                        try:
                            _do_generate_article_external(ids[0], ai_provider=ai_provider, openrouter_models=openrouter_models)
                        except Exception as e:
                            failed += 1
                            article_ok = False
                            log.error("[bulk-group] article A failed tid=%s: %s", ids[0], e)
                            _app_log("article", False, f"Article A failed: {e}", title_id=ids[0], group_id=group_id, job_id=job_id)
                            if progress_updater:
                                _bulk_progress.get(job_id, {})["_last_error"] = str(e)[:200]
                    if article_ok:
                        recipe_a = None
                        with get_connection() as conn:
                            cur = db_execute(conn, "SELECT recipe FROM article_content WHERE title_id = ? AND language_code = 'en'", (ids[0],))
                            row = dict_row(cur.fetchone())
                            if row:
                                rv = row.get("recipe")
                                if isinstance(rv, dict):
                                    recipe_a = rv
                                elif isinstance(rv, str) and rv.strip():
                                    try:
                                        recipe_a = json.loads(rv)
                                    except json.JSONDecodeError:
                                        pass
                        for tid in ids[1:4]:
                            if job_id and _bulk_cancel.get(job_id):
                                break
                            with get_connection() as conn:
                                if sc == "empty_only" and _title_has_content(conn, tid):
                                    continue
                            try:
                                _do_generate_article_external(tid, recipe_from_a=recipe_a, ai_provider=ai_provider, openrouter_models=openrouter_models)
                            except Exception as e:
                                failed += 1
                                article_ok = False
                                log.error("[bulk-group] article BCD failed tid=%s: %s", tid, e)
                                _app_log("article", False, f"Article BCD failed: {e}", title_id=tid, group_id=group_id, job_id=job_id)
                                if progress_updater:
                                    _bulk_progress.get(job_id, {})["_last_error"] = str(e)[:200]
                                break
                    if not article_ok:
                        continue
            if mode in ("images", "all"):
                if job_id and _bulk_cancel.get(job_id):
                    break
                with get_connection() as conn:
                    skip_images = _should_skip_images(conn, title_id, si)
                if not skip_images:
                    from imagine import generate_4_images
                    cancel_check = (lambda: bool(job_id and _bulk_cancel.get(job_id))) if job_id else None
                    with get_connection() as conn:
                        cur = db_execute(conn, "SELECT prompt, prompt_image_ingredients FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
                        row = dict_row(cur.fetchone())
                    prompt = (row.get("prompt") or "").strip() if row else ""
                    prompt_ing = (row.get("prompt_image_ingredients") or "").strip() if row else ""
                    if prompt:
                        urls, err = generate_4_images(prompt, key_prefix="main_image", cancel_check=cancel_check, user_config=user_config)
                        if err and err == "Cancelled":
                            break
                        if not err:
                            from imagine import flip_image_vertical_and_upload
                            BOTTOM_SOURCE_INDEX = (1, 0, 3, 2)
                            bottom_urls = [None] * 4
                            for i in range(min(4, len(urls))):
                                src = BOTTOM_SOURCE_INDEX[i]
                                if src < len(urls) and urls[src]:
                                    try:
                                        bottom_urls[i] = flip_image_vertical_and_upload(urls[src], "bottom_image", user_config=user_config)
                                    except Exception:
                                        bottom_urls[i] = None
                            with get_connection() as conn:
                                for i, tid in enumerate(ids[:4]):
                                    if i < len(urls):
                                        main_url = urls[i]
                                        bottom_url = bottom_urls[i] if i < len(bottom_urls) else None
                                        cur = db_execute(conn, "UPDATE article_content SET main_image = ?, top_image = ?, bottom_image = ? WHERE title_id = ? AND language_code = 'en'", (main_url, main_url, bottom_url, tid))
                                        if cur.rowcount == 0:
                                            db_execute(conn, "INSERT INTO article_content (title_id, language_code, main_image, top_image, bottom_image) VALUES (?, 'en', ?, ?, ?)", (tid, main_url, main_url, bottom_url))
                    if prompt_ing and not (job_id and _bulk_cancel.get(job_id)):
                        urls2, err2 = generate_4_images(prompt_ing, key_prefix="ingredient_image", cancel_check=cancel_check, user_config=user_config)
                        if err2 == "Cancelled":
                            break
                        if not err2:
                            with get_connection() as conn:
                                for i, tid in enumerate(ids[:4]):
                                    if i < len(urls2):
                                        cur = db_execute(conn, "UPDATE article_content SET ingredient_image = ? WHERE title_id = ? AND language_code = 'en'", (urls2[i], tid))
                                        if cur.rowcount == 0:
                                            db_execute(conn, "INSERT INTO article_content (title_id, language_code, ingredient_image) VALUES (?, 'en', ?)", (tid, urls2[i]))
                            for tid in ids[:4]:
                                _update_article_html_images(tid)
            if mode == "main_image":
                if job_id and _bulk_cancel.get(job_id):
                    break
                from imagine import generate_4_images
                cancel_check = (lambda: bool(job_id and _bulk_cancel.get(job_id))) if job_id else None
                with get_connection() as conn:
                    cur = db_execute(conn, "SELECT prompt FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
                    row = dict_row(cur.fetchone())
                prompt = (row.get("prompt") or "").strip() if row else ""
                if prompt:
                    urls, err = generate_4_images(prompt, key_prefix="main_image", cancel_check=cancel_check)
                    if err == "Cancelled":
                        break
                    if not err:
                        from imagine import flip_image_vertical_and_upload
                        BOTTOM_SOURCE_INDEX = (1, 0, 3, 2)
                        bottom_urls = [None] * 4
                        for i in range(min(4, len(urls))):
                            src = BOTTOM_SOURCE_INDEX[i]
                            if src < len(urls) and urls[src]:
                                try:
                                    bottom_urls[i] = flip_image_vertical_and_upload(urls[src], "bottom_image")
                                except Exception as e:
                                    log.warning("[bulk-group] flip_image failed: %s", e)
                                    bottom_urls[i] = None
                        with get_connection() as conn:
                            for i, tid in enumerate(ids[:4]):
                                if i < len(urls):
                                    main_url = urls[i]
                                    bottom_url = bottom_urls[i] if i < len(bottom_urls) else None
                                    cur = db_execute(conn, "UPDATE article_content SET main_image = ?, top_image = ?, bottom_image = ? WHERE title_id = ? AND language_code = 'en'", (main_url, main_url, bottom_url, tid))
                                    if cur.rowcount == 0:
                                        db_execute(conn, "INSERT INTO article_content (title_id, language_code, main_image, top_image, bottom_image) VALUES (?, 'en', ?, ?, ?)", (tid, main_url, main_url, bottom_url))
                        for tid in ids[:4]:
                            _update_article_html_images(tid)
            if mode == "ingredient_image":
                if job_id and _bulk_cancel.get(job_id):
                    break
                from imagine import generate_4_images
                cancel_check = (lambda: bool(job_id and _bulk_cancel.get(job_id))) if job_id else None
                with get_connection() as conn:
                    cur = db_execute(conn, "SELECT prompt_image_ingredients FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
                    row = dict_row(cur.fetchone())
                prompt_ing = (row.get("prompt_image_ingredients") or "").strip() if row else ""
                if prompt_ing:
                    urls2, err2 = generate_4_images(prompt_ing, key_prefix="ingredient_image", cancel_check=cancel_check)
                    if err2 == "Cancelled":
                        break
                    if not err2:
                        with get_connection() as conn:
                            for i, tid in enumerate(ids[:4]):
                                if i < len(urls2):
                                    cur = db_execute(conn, "UPDATE article_content SET ingredient_image = ? WHERE title_id = ? AND language_code = 'en'", (urls2[i], tid))
                                    if cur.rowcount == 0:
                                        db_execute(conn, "INSERT INTO article_content (title_id, language_code, ingredient_image) VALUES (?, 'en', ?)", (tid, urls2[i]))
                        for tid in ids[:4]:
                            _update_article_html_images(tid)
            if mode == "pin_image":
                if job_id and _bulk_cancel.get(job_id):
                    break
                pin_ok = True
                for tid in ids[:4]:
                    if job_id and _bulk_cancel.get(job_id):
                        break
                    try:
                        _do_generate_pin_image(tid)
                    except Exception as e:
                        failed += 1
                        pin_ok = False
                        log.error("[bulk-group] pin_image failed tid=%s: %s", tid, e)
                        _app_log("pin", False, f"Pin image failed: {e}", title_id=tid, group_id=group_id, job_id=job_id)
                        break
                if not pin_ok:
                    continue
            ok += 1
        except Exception as e:
            failed += 1
            err_str = str(e)
            log.error("[bulk-group] row failed tid=%s: %s", title_id, err_str)
            _app_log("run", False, f"Bulk row failed: {err_str[:200]}", title_id=title_id, group_id=group_id, job_id=job_id)
            if progress_updater:
                _bulk_progress.get(job_id, {})["_last_error"] = err_str[:200]
            if "quota exceeded" in err_str.lower():
                log.error("[bulk-group] FATAL: quota exceeded, stopping bulk run")
                break
    return ok, failed


def _run_bulk_group_async(job_id, group_id, mode, scope="override", scope_content=None, scope_images=None, ai_provider=None, openrouter_models=None, user_id=None):
    """scope_content/scope_images passed through to _bulk_run_one_group."""
    """Background thread for bulk-run-group."""
    try:
        def upd(tid, title, idx, total, ok, failed, extra=None):
            p = _bulk_progress[job_id]
            prev = p.get("_prev", {"idx": -1, "ok": 0, "failed": 0, "title": "", "tid": None})
            if idx > prev.get("idx", -1) and prev.get("idx", -1) >= 0:
                prev_ok, prev_fail = prev.get("ok", 0), prev.get("failed", 0)
                step_ok = ok - prev_ok
                step_fail = failed - prev_fail
                if step_ok or step_fail:
                    sym = "✓" if step_ok else "✗"
                    t = prev.get("total", total)
                    pt = (prev.get("title") or "")[:45]
                    ptid = prev.get("tid") or ""
                    st = f"G{group_id} R{prev['idx']+1}/{t}: [{ptid}] {pt} {sym}"
                    if step_fail and p.get("_last_error"):
                        st += " | " + p["_last_error"][:80]
                        p["_last_error"] = ""  # reset after showing
                    steps = p.get("steps", [])
                    steps.append(st)
                    p["steps"] = steps[-80:]
            p["_prev"] = {"idx": idx, "ok": ok, "failed": failed, "title": title, "tid": tid, "total": total}
            art = []
            if (title or "").strip() and extra and isinstance(extra, dict):
                art = [{"tid": tid, "title": (title or "")[:60], "domain_url": extra.get("domain_url", "-"), "group_id": extra.get("group_id"), "domain_letters": extra.get("domain_letters", "A,B,C,D")}]
            p.update({
                "status": "running",
                "current_title": (title or "")[:80],
                "current_index": idx,
                "total": total,
                "total_rows": total,
                "done": idx,
                "active_titles": [f"{tid}:{title}"[:80]] if (title or "").strip() else [],
                "active_articles": art,
                "ok": ok,
                "failed": failed,
                "message": f"Row {idx + 1}/{total}",
            })
        ok, failed = _bulk_run_one_group(group_id, mode, progress_updater=upd, job_id=job_id, scope=scope, scope_content=scope_content, scope_images=scope_images, ai_provider=ai_provider, openrouter_models=openrouter_models, user_id=user_id)
        if _bulk_cancel.get(job_id):
            _bulk_progress[job_id].update({"status": "cancelled", "message": f"Cancelled. {ok} rows done" + (f", {failed} failed" if failed else ""), "ok": ok, "failed": failed})
        else:
            _bulk_progress[job_id].update({"status": "done", "message": f"{ok} rows done" + (f", {failed} failed" if failed else ""), "ok": ok, "failed": failed})
    except Exception as e:
        _bulk_progress[job_id].update({"status": "error", "message": str(e)})


def _bulk_run_one_row(title_id, mode, job_id=None, on_active=None, scope="override", scope_content=None, scope_images=None, ai_provider=None, openrouter_models=None):
    """Run bulk for a single row (Domain A title). Returns (ok, failed, reason) - reason is error message when failed."""
    sc = scope_content if scope_content is not None else scope
    si = scope_images if scope_images is not None else scope
    with get_connection() as conn:
        if _should_skip_bulk_row(conn, title_id, mode, scope, sc, si):
            return 0, 0, None
    cancel_check = (lambda: bool(job_id and _bulk_cancel.get(job_id))) if job_id else None
    try:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT t.id, t.title, t.group_id, d.group_id as d_group_id, d.domain_index, d.domain_url, d.domain_name FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id,))
            t = dict_row(cur.fetchone())
            if not t or t.get("domain_index") != 0:
                return 0, 1, "Use Domain A title"
            gid_val = t.get("group_id") if t.get("group_id") is not None else t.get("d_group_id")
            domain_url = (t.get("domain_url") or t.get("domain_name") or "").strip() or "-"
            domain_letter = "ABCD"[min(3, int(t.get("domain_index") or 0))]
            cur = db_execute(conn, "SELECT title FROM titles WHERE id = ?", (title_id,))
            title_row = dict_row(cur.fetchone())
            title_text = (title_row.get("title") or "") if title_row else ""
            cur = db_execute(conn, """SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id
                WHERE COALESCE(t.group_id, d.group_id) = ? AND t.title = ? AND d.domain_index IN (0,1,2,3) ORDER BY d.domain_index""", (gid_val, t["title"]))
            ids = [dict_row(r).get("id") for r in cur.fetchall()]
        if len(ids) < 4:
            return 0, 1, "Need 4 domains (A,B,C,D)"
        title_text = (title_row.get("title") or "")[:50] if title_row else ""
        if on_active:
            extra = {"domain_url": domain_url, "group_id": gid_val, "domain_letter": domain_letter, "domain_letters": "A,B,C,D"}
            on_active(title_id, title_text, True, extra)
        try:
            if mode in ("article", "all"):
                if cancel_check and cancel_check():
                    return 0, 0, None
                with get_connection() as conn:
                    skip_content = not _row_any_needs_content(conn, title_id, sc)
                if not skip_content:
                    with get_connection() as conn:
                        gen_a = sc != "empty_only" or not _title_has_content(conn, ids[0])
                    if gen_a:
                        try:
                            _do_generate_article_external(ids[0], ai_provider=ai_provider, openrouter_models=openrouter_models)
                        except Exception as e:
                            return 0, 1, str(e)[:200]
                    recipe_a = None
                    with get_connection() as conn:
                        cur = db_execute(conn, "SELECT recipe FROM article_content WHERE title_id = ? AND language_code = 'en'", (ids[0],))
                        row = dict_row(cur.fetchone())
                        if row:
                            rv = row.get("recipe")
                            if isinstance(rv, dict):
                                recipe_a = rv
                            elif isinstance(rv, str) and rv.strip():
                                try:
                                    recipe_a = json.loads(rv)
                                except json.JSONDecodeError:
                                    pass
                    for tid in ids[1:4]:
                        if cancel_check and cancel_check():
                            return 0, 0, None
                        with get_connection() as conn:
                            if sc == "empty_only" and _title_has_content(conn, tid):
                                continue
                        try:
                            _do_generate_article_external(tid, recipe_from_a=recipe_a, ai_provider=ai_provider, openrouter_models=openrouter_models)
                        except Exception as e:
                            return 0, 1, str(e)[:200]
            if mode in ("images", "all"):
                if cancel_check and cancel_check():
                    return 0, 0, None
                with get_connection() as conn:
                    skip_images = _should_skip_images(conn, title_id, si)
                if not skip_images:
                    from imagine import generate_4_images
                    with get_connection() as conn:
                        cur = db_execute(conn, "SELECT prompt, prompt_image_ingredients FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
                        row = dict_row(cur.fetchone())
                    prompt = (row.get("prompt") or "").strip() if row else ""
                    prompt_ing = (row.get("prompt_image_ingredients") or "").strip() if row else ""
                    if prompt:
                        urls, err = generate_4_images(prompt, key_prefix="main_image", cancel_check=cancel_check)
                        if err == "Cancelled":
                            return 0, 0, None
                        if not err:
                            from imagine import flip_image_vertical_and_upload
                            BOTTOM_SOURCE_INDEX = (1, 0, 3, 2)
                            bottom_urls = [None] * 4
                            for i in range(min(4, len(urls))):
                                src = BOTTOM_SOURCE_INDEX[i]
                                if src < len(urls) and urls[src]:
                                    try:
                                        bottom_urls[i] = flip_image_vertical_and_upload(urls[src], "bottom_image")
                                    except Exception:
                                        bottom_urls[i] = None
                            with get_connection() as conn:
                                for i, tid in enumerate(ids[:4]):
                                    if i < len(urls):
                                        main_url = urls[i]
                                        bottom_url = bottom_urls[i] if i < len(bottom_urls) else None
                                        cur = db_execute(conn, "UPDATE article_content SET main_image = ?, top_image = ?, bottom_image = ? WHERE title_id = ? AND language_code = 'en'", (main_url, main_url, bottom_url, tid))
                                        if cur.rowcount == 0:
                                            db_execute(conn, "INSERT INTO article_content (title_id, language_code, main_image, top_image, bottom_image) VALUES (?, 'en', ?, ?, ?)", (tid, main_url, main_url, bottom_url))
                    if prompt_ing and not (cancel_check and cancel_check()):
                        urls2, err2 = generate_4_images(prompt_ing, key_prefix="ingredient_image", cancel_check=cancel_check)
                        if err2 == "Cancelled":
                            return 0, 0, None
                        if not err2:
                            with get_connection() as conn:
                                for i, tid in enumerate(ids[:4]):
                                    if i < len(urls2):
                                        cur = db_execute(conn, "UPDATE article_content SET ingredient_image = ? WHERE title_id = ? AND language_code = 'en'", (urls2[i], tid))
                                        if cur.rowcount == 0:
                                            db_execute(conn, "INSERT INTO article_content (title_id, language_code, ingredient_image) VALUES (?, 'en', ?)", (tid, urls2[i]))
                    for tid in ids[:4]:
                        _update_article_html_images(tid)
            return 1, 0, None
        finally:
            if on_active:
                on_active(title_id, title_text, False, None)
    except Exception as e:
        return 0, 1, str(e)[:200]


def _run_bulk_all_groups_async(job_id, mode, concurrency_type="row", concurrency_n=1, scope="override", scope_content=None, scope_images=None, ai_provider=None, openrouter_models=None, user_id=None):
    """Background thread for bulk-run-all-groups. scope_content/scope_images for per-phase skip."""
    _progress_lock = threading.Lock()
    try:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id FROM `groups` WHERE id IS NOT NULL ORDER BY id")
            group_ids = [dict_row(r).get("id") for r in cur.fetchall() if dict_row(r).get("id")]
        if not group_ids:
            _bulk_progress[job_id].update({"status": "error", "message": "No groups"})
            return
        total_ok, total_failed = 0, 0
        n = max(1, min(int(concurrency_n), 20 if concurrency_type == "row" else 10))
        num_groups = len(group_ids)
        _bulk_progress[job_id].update({"status": "running", "message": f"Loading {num_groups} groups...", "current_title": ""})
        if concurrency_type == "group":
            _bulk_progress[job_id].update({"message": f"Running {n} groups in parallel...", "total_groups": num_groups})
            grp_done = [0]
            with ThreadPoolExecutor(max_workers=n) as ex:
                futures = {ex.submit(_bulk_run_one_group, gid, mode, None, job_id, scope, scope_content, scope_images, ai_provider, openrouter_models, user_id): gid for gid in group_ids}
                for future in as_completed(futures):
                    if _bulk_cancel.get(job_id):
                        for f in futures:
                            f.cancel()
                        break
                    gid = futures[future]
                    try:
                        ok, failed = future.result()
                        with _progress_lock:
                            total_ok += ok
                            total_failed += failed
                            grp_done[0] += 1
                            st = f"G{gid}: {ok}✓ {failed}✗"
                            steps = _bulk_progress[job_id].get("steps", [])
                            steps.append(st)
                            _bulk_progress[job_id]["steps"] = steps[-80:]
                            _bulk_progress[job_id].update({
                                "status": "running",
                                "message": f"Group {grp_done[0]}/{num_groups} ({total_ok}✓ {total_failed}✗)",
                            })
                    except Exception as e:
                        with _progress_lock:
                            total_failed += 1
                            grp_done[0] += 1
                            log.error("[bulk-all] group %s failed: %s", gid, e)
                            st = f"G{gid}: ✗ {str(e)[:60]}"
                            steps = _bulk_progress[job_id].get("steps", [])
                            steps.append(st)
                            _bulk_progress[job_id]["steps"] = steps[-80:]
        else:
            row_queue = []
            sc = scope_content if scope_content is not None else scope
            si = scope_images if scope_images is not None else scope
            with get_connection() as conn:
                for gid in group_ids:
                    cur = db_execute(conn, """SELECT t.id, t.title FROM titles t JOIN domains d ON t.domain_id = d.id
                        WHERE COALESCE(t.group_id, d.group_id) = ? ORDER BY t.id""", (gid,))
                    for r in cur.fetchall():
                        row = dict_row(r)
                        tid = row.get("id")
                        if not tid:
                            continue
                        if mode == "article" and sc == "empty_only" and not _row_any_needs_content(conn, tid, sc):
                            continue
                        if mode == "images" and si == "empty_only" and not _row_any_needs_images(conn, tid, si):
                            continue
                        if mode == "all" and (sc == "empty_only" or si == "empty_only"):
                            needs_c = sc != "empty_only" or _row_any_needs_content(conn, tid, sc)
                            needs_i = si != "empty_only" or _row_any_needs_images(conn, tid, si)
                            if not needs_c and not needs_i:
                                continue
                        row_queue.append((gid, tid, (row.get("title") or "")[:45]))
            total_rows = len(row_queue)
            _bulk_progress[job_id].update({"status": "running", "message": f"0/{total_rows} rows queued, starting...", "current_title": "", "total_rows": total_rows, "done": 0})
            active_items = {}  # tid -> {tid, title, domain_url, group_id, domain_letter} or "tid:title"
            def on_active(tid, tt, is_start, extra=None):
                with _progress_lock:
                    if is_start:
                        if extra and isinstance(extra, dict):
                            active_items[tid] = {"tid": tid, "title": (tt or "")[:60], "domain_url": extra.get("domain_url", "-"), "group_id": extra.get("group_id"), "domain_letter": extra.get("domain_letter", "A"), "domain_letters": extra.get("domain_letters", "A,B,C,D")}
                        else:
                            active_items[tid] = f"{tid}:{(tt or '')[:40]}"
                    else:
                        active_items.pop(tid, None)
                    lst = list(active_items.values())[:5]
                    active_str = ", ".join(x.get("title", str(x)) if isinstance(x, dict) else str(x).split(":", 1)[-1] for x in lst) if lst else "-"
                    _bulk_progress[job_id]["current_title"] = active_str
                    _bulk_progress[job_id]["active_titles"] = [f"{x.get('tid','')}:{x.get('title','')}" if isinstance(x, dict) else x for x in lst]
                    _bulk_progress[job_id]["active_articles"] = [x for x in lst if isinstance(x, dict)]
                    _bulk_progress[job_id]["done"] = processed_count
            done = 0
            processed_count = 0
            _bulk_progress[job_id]["steps"] = _bulk_progress[job_id].get("steps", [])
            with ThreadPoolExecutor(max_workers=n) as ex:
                futures = {ex.submit(_bulk_run_one_row, tid, mode, job_id, on_active, scope, scope_content, scope_images, ai_provider, openrouter_models): (gid, tid, title) for gid, tid, title in row_queue}
                for future in as_completed(futures):
                    if _bulk_cancel.get(job_id):
                        for f in futures:
                            f.cancel()
                        break
                    gid, tid, title = futures[future]
                    try:
                        res = future.result()
                        ok = res[0] if len(res) >= 1 else 0
                        failed = res[1] if len(res) >= 2 else 0
                        reason = res[2] if len(res) >= 3 else None
                        with _progress_lock:
                            total_ok += ok
                            total_failed += failed
                            done += 1
                            if ok or failed:
                                processed_count += 1
                                sym = "✓" if ok else "✗"
                                st = f"G{gid} R{processed_count}: [{tid}] {title} {sym}"
                                if not ok and reason:
                                    st += " | " + (reason[:80] if len(reason) > 80 else reason)
                                steps = _bulk_progress[job_id].get("steps", [])
                                steps.append(st)
                                _bulk_progress[job_id]["steps"] = steps[-80:]
                            lst = list(active_items.values())[:5]
                            _bulk_progress[job_id]["active_titles"] = [f"{x.get('tid','')}:{x.get('title','')}" if isinstance(x, dict) else x for x in lst]
                            _bulk_progress[job_id]["active_articles"] = [x for x in lst if isinstance(x, dict)]
                            _bulk_progress[job_id].update({
                                "status": "running",
                                "message": f"Row {done}/{total_rows} ({total_ok}✓ {total_failed}✗)",
                                "current_title": "",
                                "total_rows": total_rows,
                                "done": done,
                                "processed_count": processed_count,
                            })
                    except Exception as e:
                        with _progress_lock:
                            total_failed += 1
                            done += 1
                            processed_count += 1
                            reason = str(e)[:80]
                            st = f"G{gid} R{processed_count}: [{tid}] {title} ✗ | {reason}"
                            steps = _bulk_progress[job_id].get("steps", [])
                            steps.append(st)
                            _bulk_progress[job_id]["steps"] = steps[-80:]
        if _bulk_cancel.get(job_id):
            _bulk_progress[job_id].update({"status": "cancelled", "message": f"Cancelled. {total_ok} rows done" + (f", {total_failed} failed" if total_failed else ""), "ok": total_ok, "failed": total_failed})
        else:
            _bulk_progress[job_id].update({"status": "done", "message": f"{total_ok} rows done" + (f", {total_failed} failed" if total_failed else ""), "ok": total_ok, "failed": total_failed})
    except Exception as e:
        _bulk_progress[job_id].update({"status": "error", "message": str(e)})


@app.route("/api/bulk-run-jobs", methods=["GET"])
def api_bulk_run_jobs():
    """Return all bulk jobs. Persisted until cleared. Supports ?domain_id= and ?date= (today|week|all)."""
    domain_id_filter = request.args.get("domain_id", type=int)
    date_filter = request.args.get("date", "all")
    # Sync in-memory live jobs into persisted history so they survive reload/restart.
    history_changed = False
    for jid, p in list(_bulk_progress.items()):
        j = {"job_id": jid, **{k: v for k, v in p.items() if k != "job_id" and not k.startswith("_")}}
        prev = _bulk_history.get(jid)
        if prev != j:
            _bulk_history[jid] = j
            history_changed = True
    if history_changed:
        _save_bulk_history(_bulk_history)

    jobs = []
    for jid, p in list(_bulk_history.items()):
        if not isinstance(p, dict):
            continue
        j = {"job_id": jid, **{k: v for k, v in p.items() if k != "job_id" and not str(k).startswith("_")}}
        # Apply domain filter
        if domain_id_filter:
            did = j.get("domain_id")
            dids = j.get("domain_ids") or []
            if did and int(did) != domain_id_filter:
                continue
            if dids and domain_id_filter not in [int(x) for x in dids]:
                continue
            if not did and not dids:
                continue
        # Apply date filter
        created_at = float(j.get("created_at") or 0)
        now_ts = time.time()
        if date_filter == "today" and created_at < now_ts - 24 * 3600:
            continue
        if date_filter == "week" and created_at < now_ts - 7 * 24 * 3600:
            continue
        jobs.append(j)
    jobs.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return jsonify({"jobs": jobs[:50]})


@app.route("/api/bulk-run-jobs/<job_id>", methods=["GET"])
def api_bulk_run_job_detail(job_id):
    """Return full job details. Used by pin picker poll and task detail."""
    p = _bulk_progress.get(job_id)
    if not p:
        return jsonify({"status": "unknown", "message": "Job not found"}), 404
    out = {"job_id": job_id, **{k: v for k, v in p.items() if k != "job_id" and not k.startswith("_")}}
    return jsonify(out)


@app.route("/api/bulk-run-jobs/<job_id>/articles", methods=["GET"])
def api_bulk_run_job_articles(job_id):
    """Return articles (title_ids) in this job, optionally filtered by domain_id."""
    p = _bulk_progress.get(job_id)
    if not p:
        return jsonify({"error": "Job not found", "articles": []}), 404
    domain_id_filter = request.args.get("domain_id", type=int)
    articles = []
    jtype = p.get("type", "")
    if jtype == "single":
        tid = p.get("title_id")
        if tid:
            with get_connection() as conn:
                cur = db_execute(conn, """SELECT t.id, t.title, t.domain_id, d.domain_url, d.domain_name
                    FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?""", (tid,))
                row = dict_row(cur.fetchone())
            if row and (not domain_id_filter or row.get("domain_id") == domain_id_filter):
                articles.append({"id": row.get("id"), "title": (row.get("title") or "")[:80], "domain_id": row.get("domain_id"), "domain_url": row.get("domain_url") or row.get("domain_name")})
    elif jtype == "group":
        gid = p.get("group_id")
        if gid:
            with get_connection() as conn:
                cur = db_execute(conn, """SELECT t.id, t.title, t.domain_id, d.domain_url, d.domain_name
                    FROM titles t JOIN domains d ON t.domain_id = d.id
                    WHERE COALESCE(t.group_id, d.group_id) = ? AND COALESCE(d.domain_index, 0) = 0
                    ORDER BY t.id""", (gid,))
                for r in cur.fetchall():
                    row = dict_row(r)
                    if not domain_id_filter or row.get("domain_id") == domain_id_filter:
                        articles.append({"id": row.get("id"), "title": (row.get("title") or "")[:80], "domain_id": row.get("domain_id"), "domain_url": row.get("domain_url") or row.get("domain_name")})
    elif jtype == "all":
        # Parse title_ids from steps: "G1 R1: [50] Title ✓" -> 50
        import re
        seen = set()
        for s in (p.get("steps") or []):
            m = re.search(r'\[(\d+)\]', str(s))
            if m:
                tid = int(m.group(1))
                if tid not in seen:
                    seen.add(tid)
                    with get_connection() as conn:
                        cur = db_execute(conn, """SELECT t.id, t.title, t.domain_id, d.domain_url, d.domain_name
                            FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?""", (tid,))
                        row = dict_row(cur.fetchone())
                    if row and (not domain_id_filter or row.get("domain_id") == domain_id_filter):
                        articles.append({"id": row.get("id"), "title": (row.get("title") or "")[:80], "domain_id": row.get("domain_id"), "domain_url": row.get("domain_url") or row.get("domain_name")})
    return jsonify({"job_id": job_id, "articles": articles})


@app.route("/api/bulk-run-cancel", methods=["POST"])
def api_bulk_run_cancel():
    """Request cancel for a running bulk job."""
    job_id = request.args.get("job_id") or (request.get_json(silent=True) or {}).get("job_id")
    if not job_id:
        return jsonify({"success": False, "error": "job_id required"}), 400
    if job_id not in _bulk_progress:
        return jsonify({"success": False, "error": "Job not found"}), 404
    p = _bulk_progress[job_id]
    if p.get("status") != "running":
        return jsonify({"success": False, "error": "Job not running"}), 400
    _bulk_cancel[job_id] = True
    return jsonify({"success": True, "message": "Cancel requested"})


@app.route("/api/bulk-run-clear", methods=["POST"])
def api_bulk_run_clear():
    """Clear done/error/cancelled jobs from running tasks. Keeps genuinely running jobs."""
    req = request.get_json(silent=True) or {}
    only_done = req.get("only_done", False)  # if True, clear only done; else clear done+error+cancelled
    to_remove = []
    for jid, p in list(_bulk_progress.items()):
        s = p.get("status", "")
        if s == "running":
            continue
        if only_done and s != "done":
            continue
        to_remove.append(jid)
    for jid in to_remove:
        del _bulk_progress[jid]
    # Also clear persisted history so removed jobs do not reappear.
    hist_remove = []
    for jid, p in list(_bulk_history.items()):
        s = (p or {}).get("status", "")
        
        # If it's marked as running in history but not in our active progress, it's dead
        is_actually_running = jid in _bulk_progress and _bulk_progress[jid].get("status") == "running"
        if is_actually_running:
            continue
            
        if s == "running":
            # If it reached here, it's a "dead" running job (not in _bulk_progress)
            pass
        elif only_done and s != "done":
            continue
            
        hist_remove.append(jid)
    for jid in hist_remove:
        _bulk_history.pop(jid, None)
    _save_bulk_history(_bulk_history)
    return jsonify({"success": True, "cleared": len(hist_remove)})


@app.route("/api/bulk-run-status", methods=["GET"])
def api_bulk_run_status():
    """Return progress for async bulk run."""
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"error": "job_id required"}), 400
    p = _bulk_progress.get(job_id)
    if not p:
        return jsonify({"status": "unknown", "message": "Job not found"})
    out = {k: v for k, v in p.items() if not k.startswith("_")}
    return jsonify(out)


@app.route("/api/bulk-run-group", methods=["POST"])
def api_bulk_run_group():
    """Run bulk-run for all Domain A rows in a group. scope_content/scope_images for content vs images."""
    req = {**(request.get_json(silent=True) or {}), **dict(request.args)}
    group_id = req.get("group_id")
    mode = str(req.get("mode", "all")).lower()
    ai_provider = (req.get("ai_provider") or "").strip() or None
    openrouter_models = _parse_openrouter_models(req)
    scope = str(req.get("scope") or "override").lower()
    scope_content = str(req.get("scope_content") or scope).lower()
    scope_images = str(req.get("scope_images") or scope).lower()
    for s in (scope, scope_content, scope_images):
        if s not in ("override", "empty_only"):
            scope = scope_content = scope_images = "override"
            break
    async_mode = str(req.get("async", "") or "").lower() in ("1", "true", "yes")
    if group_id is None or group_id == "":
        return jsonify({"success": False, "error": "group_id required"}), 400
    group_id = int(group_id)
    if async_mode:
        job_id = str(uuid.uuid4())
        domain_ids = []
        with get_connection() as conn:
            cur = db_execute(conn, """SELECT DISTINCT d.id FROM titles t JOIN domains d ON t.domain_id = d.id
                WHERE COALESCE(t.group_id, d.group_id) = ?""", (group_id,))
            domain_ids = [dict_row(r).get("id") for r in cur.fetchall() if dict_row(r).get("id")]
        _bulk_progress[job_id] = {"status": "running", "message": "Starting...", "current_title": "", "type": "group", "group_id": group_id, "mode": mode, "domain_ids": domain_ids, "created_at": time.time(), "steps": []}
        user = get_current_user()
        user_id = user["id"] if user else None
        threading.Thread(target=_run_bulk_group_async, args=(job_id, group_id, mode, scope, scope_content, scope_images, ai_provider, openrouter_models, user_id), daemon=True).start()
        return jsonify({"success": True, "job_id": job_id})
    ok, failed = _bulk_run_one_group(group_id, mode, scope=scope, scope_content=scope_content, scope_images=scope_images, ai_provider=ai_provider, openrouter_models=openrouter_models)
    if ok == 0 and failed == 0:
        return jsonify({"success": False, "error": "No Domain A titles in group"}), 400
    return jsonify({"success": True, "message": f"{ok} rows done" + (f", {failed} failed" if failed else "")})


@app.route("/api/bulk-group-counts-old", methods=["GET"])
def api_bulk_group_counts_old():
    """Return no_html_css, no_images for Domain A titles in one group."""
    group_id = request.args.get("group_id")
    if not group_id:
        return jsonify({"error": "group_id required"}), 400
    try:
        gid = int(group_id)
    except ValueError:
        return jsonify({"error": "invalid group_id"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM titles t
            JOIN domains d ON t.domain_id = d.id AND COALESCE(d.domain_index, 0) = 0
            WHERE COALESCE(t.group_id, d.group_id) = ?
        """, (gid,))
        row = cur.fetchone()
        total = (row.get('n', 0) if row else 0) or 0
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM (
              SELECT t.id FROM titles t
              JOIN domains d ON t.domain_id = d.id AND COALESCE(d.domain_index, 0) = 0
              WHERE COALESCE(t.group_id, d.group_id) = ?
                AND NOT EXISTS (SELECT 1 FROM article_content ac WHERE ac.title_id = t.id AND ac.language_code = 'en')
              UNION
              SELECT t.id FROM titles t
              JOIN domains d ON t.domain_id = d.id AND COALESCE(d.domain_index, 0) = 0
              JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
              WHERE COALESCE(t.group_id, d.group_id) = ?
                AND (TRIM(IFNULL(ac.article_html,'')) = '' OR TRIM(IFNULL(ac.article_css,'')) = '')
            ) x
        """, (gid, gid))
        row = cur.fetchone()
        no_html_css = (row.get('n', 0) if row else 0) or 0
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM (
              SELECT t.id FROM titles t
              JOIN domains d ON t.domain_id = d.id AND COALESCE(d.domain_index, 0) = 0
              WHERE COALESCE(t.group_id, d.group_id) = ?
                AND NOT EXISTS (SELECT 1 FROM article_content ac WHERE ac.title_id = t.id AND ac.language_code = 'en')
              UNION
              SELECT t.id FROM titles t
              JOIN domains d ON t.domain_id = d.id AND COALESCE(d.domain_index, 0) = 0
              JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
              WHERE COALESCE(t.group_id, d.group_id) = ?
                AND (TRIM(IFNULL(ac.main_image,'')) = '' OR TRIM(IFNULL(ac.ingredient_image,'')) = '')
            ) x
        """, (gid, gid))
        row = cur.fetchone()
        no_images = (row.get('n', 0) if row else 0) or 0
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM titles t
            JOIN domains d ON t.domain_id = d.id AND d.domain_index = 0
            LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE COALESCE(t.group_id, d.group_id) = ? AND ac.id IS NOT NULL AND TRIM(COALESCE(ac.article_html,'')) != ''
        """, (gid,))
        row = cur.fetchone()
        with_html = (row.get('n', 0) if row else 0) or 0
    return jsonify({"total": total, "no_html_css": no_html_css, "no_images": no_images, "with_html": with_html})


@app.route("/api/bulk-row-counts", methods=["GET"])
def api_bulk_row_counts():
    """Return no_html_css (0/1), no_images (0/1) for one title (Domain A)."""
    title_id = request.args.get("title_id")
    if not title_id:
        return jsonify({"error": "title_id required"}), 400
    try:
        tid = int(title_id)
    except ValueError:
        return jsonify({"error": "invalid title_id"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT article_html, article_css, main_image, ingredient_image FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
        row = cur.fetchone()
    if not row:
        return jsonify({"total": 1, "no_html_css": 1, "no_images": 1, "with_html": 0})
    r = dict_row(row)
    has_html = bool((r.get("article_html") or "").strip())
    has_css = bool((r.get("article_css") or "").strip())
    no_html = not (has_html and has_css)
    no_img = not (bool((r.get("main_image") or "").strip()) and bool((r.get("ingredient_image") or "").strip()))
    return jsonify({"total": 1, "no_html_css": 1 if no_html else 0, "no_images": 1 if no_img else 0, "with_html": 1 if has_html else 0})


@app.route("/api/bulk-group-counts", methods=["GET"])
def api_bulk_group_counts():
    """Return no_html_css, no_images for Domain A titles in one group."""
    group_id = request.args.get("group_id")
    if not group_id:
        return jsonify({"error": "group_id required"}), 400
    try:
        gid = int(group_id)
    except ValueError:
        return jsonify({"error": "invalid group_id"}), 400
        
    try:
        with get_connection() as conn:
            # Check access
            user = get_current_user()
            if not user or not user.get("is_admin", False):
                if not user:
                     return jsonify({"error": "Not logged in"}), 401
                user_groups_list = get_user_groups(user["id"])
                user_domain_ids = get_user_domain_ids(user["id"])
                
                cur = conn.cursor()
                cur.execute("SELECT id FROM domains WHERE group_id = ?", (gid,))
                group_domains = [row[0] for row in cur.fetchall()]
                
                has_access = False
                if gid in user_groups_list:
                    has_access = True
                elif all(d in user_domain_ids for d in group_domains) and group_domains:
                    has_access = True
                    
                if not has_access:
                    return jsonify({"error": "Forbidden"}), 403

            def get_all_group_descendants(group_id):
                result = [group_id]
                cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (group_id,))
                children = [dict_row(r)["id"] for r in cur.fetchall()]
                for child_id in children:
                    result.extend(get_all_group_descendants(child_id))
                return result
            
            all_gids = get_all_group_descendants(gid)
            placeholders = ",".join(["?"] * len(all_gids))

            cur = db_execute(conn, f"""
                SELECT COUNT(DISTINCT t.title) as n FROM titles t
                JOIN domains d ON t.domain_id = d.id
                WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders})
            """, tuple(all_gids))
            row = cur.fetchone()
            total = (row.get('n', 0) if row else 0) or 0
            
            cur = db_execute(conn, f"""
                SELECT COUNT(DISTINCT title) as n FROM (
                  SELECT t.title FROM titles t
                  JOIN domains d ON t.domain_id = d.id
                  WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders})
                    AND NOT EXISTS (SELECT 1 FROM article_content ac WHERE ac.title_id = t.id AND ac.language_code = 'en')
                  UNION
                  SELECT t.title FROM titles t
                  JOIN domains d ON t.domain_id = d.id
                  JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                  WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders})
                    AND (TRIM(IFNULL(ac.article_html,'')) = '' OR TRIM(IFNULL(ac.article_css,'')) = '')
                ) x
            """, tuple(all_gids + all_gids))
            row = cur.fetchone()
            no_html_css = (row.get('n', 0) if row else 0) or 0
            
            cur = db_execute(conn, f"""
                SELECT COUNT(DISTINCT title) as n FROM (
                  SELECT t.title FROM titles t
                  JOIN domains d ON t.domain_id = d.id
                  WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders})
                    AND NOT EXISTS (SELECT 1 FROM article_content ac WHERE ac.title_id = t.id AND ac.language_code = 'en')
                  UNION
                  SELECT t.title FROM titles t
                  JOIN domains d ON t.domain_id = d.id
                  JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                  WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders})
                    AND (TRIM(IFNULL(ac.main_image,'')) = '' OR TRIM(IFNULL(ac.ingredient_image,'')) = '')
                ) x
            """, tuple(all_gids + all_gids))
            row = cur.fetchone()
            no_images = (row.get('n', 0) if row else 0) or 0
            
            cur = db_execute(conn, f"""
                SELECT COUNT(DISTINCT t.title) as n FROM titles t
                JOIN domains d ON t.domain_id = d.id
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders}) AND ac.id IS NOT NULL AND TRIM(COALESCE(ac.article_html,'')) != ''
            """, tuple(all_gids))
            row = cur.fetchone()
            with_html = (row.get('n', 0) if row else 0) or 0
            
            # calculate needs rows dynamically based on domain equivalents
            rows_needs_content = 0
            cur = db_execute(conn, f"""SELECT MIN(t.id) as id FROM titles t JOIN domains d ON t.domain_id = d.id
                WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders})
                GROUP BY COALESCE(t.group_id, d.group_id), t.title
                ORDER BY MIN(t.id)""", tuple(all_gids))
            for r in cur.fetchall():
                tid = dict_row(r).get("id")
                # find all tids for this title and group
                if tid:
                    title_text = dict_row(db_execute(conn, "SELECT title FROM titles WHERE id = ?", (tid,)).fetchone())["title"]
                    title_gids_placeholders = ",".join(["?"] * len(all_gids))
                    tids_cur = db_execute(conn, f"SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id WHERE COALESCE(t.group_id, d.group_id) IN ({title_gids_placeholders}) AND t.title = ?", tuple(all_gids) + (title_text,))
                    all_tids = [dict_row(tr)["id"] for tr in tids_cur.fetchall()]
                    
                    needs = False
                    for atid in all_tids:
                        if _row_any_needs_content(conn, atid, "empty_only"):
                            needs = True
                            break
                    if needs:
                        rows_needs_content += 1
                        
            rows_needs_images = 0
            cur2 = db_execute(conn, f"""SELECT MIN(t.id) as id FROM titles t JOIN domains d ON t.domain_id = d.id
                WHERE COALESCE(t.group_id, d.group_id) IN ({placeholders})
                GROUP BY COALESCE(t.group_id, d.group_id), t.title
                ORDER BY MIN(t.id)""", tuple(all_gids))
            for r in cur2.fetchall():
                tid = dict_row(r).get("id")
                if tid:
                    title_text = dict_row(db_execute(conn, "SELECT title FROM titles WHERE id = ?", (tid,)).fetchone())["title"]
                    title_gids_placeholders = ",".join(["?"] * len(all_gids))
                    tids_cur = db_execute(conn, f"SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id WHERE COALESCE(t.group_id, d.group_id) IN ({title_gids_placeholders}) AND t.title = ?", tuple(all_gids) + (title_text,))
                    all_tids = [dict_row(tr)["id"] for tr in tids_cur.fetchall()]
                    
                    needs = False
                    for atid in all_tids:
                        if _row_any_needs_images(conn, atid, "empty_only"):
                            needs = True
                            break
                    if needs:
                        rows_needs_images += 1
            
        return jsonify({"total": total, "no_html_css": no_html_css, "no_images": no_images, "with_html": with_html, "rows_needs_content": rows_needs_content, "rows_needs_images": rows_needs_images})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/bulk-all-groups-counts", methods=["GET"])
def api_bulk_all_groups_counts():
    """Return counts of all titles in grouped domains: no_html_css, no_images. Includes titles with no article_content row."""
    with get_connection() as conn:
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM titles t
            JOIN domains d ON t.domain_id = d.id
            WHERE d.group_id IS NOT NULL
        """)
        row = cur.fetchone()
        total = (row.get('n', 0) if row else 0) or 0
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM (
              SELECT t.id FROM titles t
              JOIN domains d ON t.domain_id = d.id
              WHERE d.group_id IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM article_content ac WHERE ac.title_id = t.id AND ac.language_code = 'en')
              UNION
              SELECT t.id FROM titles t
              JOIN domains d ON t.domain_id = d.id
              JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
              WHERE d.group_id IS NOT NULL
                AND (TRIM(IFNULL(ac.article_html,'')) = '' OR TRIM(IFNULL(ac.article_css,'')) = '')
            ) x
        """)
        row = cur.fetchone()
        no_html_css = (row.get('n', 0) if row else 0) or 0
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM (
              SELECT t.id FROM titles t
              JOIN domains d ON t.domain_id = d.id
              WHERE d.group_id IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM article_content ac WHERE ac.title_id = t.id AND ac.language_code = 'en')
              UNION
              SELECT t.id FROM titles t
              JOIN domains d ON t.domain_id = d.id
              JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
              WHERE d.group_id IS NOT NULL
                AND (TRIM(IFNULL(ac.main_image,'')) = '' OR TRIM(IFNULL(ac.ingredient_image,'')) = '')
            ) x
        """)
        row = cur.fetchone()
        no_images = (row.get('n', 0) if row else 0) or 0
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM titles t
            JOIN domains d ON t.domain_id = d.id
            INNER JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE d.group_id IS NOT NULL AND TRIM(IFNULL(ac.article_html,'')) != ''
        """)
        row = cur.fetchone()
        with_html = (row.get('n', 0) if row else 0) or 0
        cur = db_execute(conn, """
            SELECT COUNT(*) as n FROM titles t
            JOIN domains d ON t.domain_id = d.id
            WHERE d.group_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM article_content ac2 WHERE ac2.title_id = t.id AND ac2.language_code = 'en')
        """)
        row = cur.fetchone()
        no_ac_row = (row.get('n', 0) if row else 0) or 0
        # Rows (Domain A titles) that need content - matches what bulk run actually processes
        cur = db_execute(conn, """
            SELECT COUNT(DISTINCT t.title) as n FROM titles t
            JOIN domains d ON t.domain_id = d.id
            WHERE d.group_id IS NOT NULL
        """)
        row = cur.fetchone()
        total_rows = (row.get('n', 0) if row else 0) or 0
        rows_needs_content = 0
        cur = db_execute(conn, """SELECT MIN(t.id) as id FROM titles t JOIN domains d ON t.domain_id = d.id
            WHERE d.group_id IS NOT NULL
            GROUP BY d.group_id, t.title
            ORDER BY MIN(t.id)""")
        for r in cur.fetchall():
            tid = dict_row(r).get("id")
            if tid and _row_any_needs_content(conn, tid, "empty_only"):
                rows_needs_content += 1
        rows_needs_images = 0
        cur2 = db_execute(conn, """SELECT MIN(t.id) as id FROM titles t JOIN domains d ON t.domain_id = d.id
            WHERE d.group_id IS NOT NULL
            GROUP BY d.group_id, t.title
            ORDER BY MIN(t.id)""")
        for r in cur2.fetchall():
            tid = dict_row(r).get("id")
            if tid and _row_any_needs_images(conn, tid, "empty_only"):
                rows_needs_images += 1
    return jsonify({"total": total, "no_html_css": no_html_css, "no_images": no_images, "with_html": with_html, "no_ac_row": no_ac_row, "rows_needs_content": rows_needs_content, "rows_needs_images": rows_needs_images, "total_rows": total_rows})


@app.route("/api/bulk-run-filtered", methods=["POST"])
def api_bulk_run_filtered():
    """Run generation for a filtered list of title_ids. Body: {domain_id, title_ids[], mode, async}."""
    req = request.get_json(silent=True) or {}
    domain_id = req.get("domain_id")
    title_ids = req.get("title_ids") or []
    mode = str(req.get("mode", "all")).lower()
    async_mode = str(req.get("async", "")).lower() in ("1", "true", "yes")
    ai_provider = (req.get("ai_provider") or "").strip() or None
    openrouter_models = _parse_openrouter_models(req)
    
    if not domain_id or not title_ids:
        return jsonify({"success": False, "error": "domain_id and title_ids required"}), 400
    
    if not async_mode:
        return jsonify({"success": False, "error": "Only async mode supported for filtered runs"}), 400
    
    job_id = str(uuid.uuid4())
    _bulk_progress[job_id] = {
        "status": "running",
        "message": "Starting...",
        "current_title": "",
        "type": "filtered",
        "domain_id": domain_id,
        "mode": mode,
        "total_rows": len(title_ids),
        "done": 0,
        "created_at": time.time(),
        "steps": []
    }
    
    def task():
        try:
            total_ok, total_failed = 0, 0
            for idx, tid in enumerate(title_ids):
                if _bulk_cancel.get(job_id):
                    break
                
                with get_connection() as conn:
                    cur = db_execute(conn, "SELECT title FROM titles WHERE id = ?", (tid,))
                    r = dict_row(cur.fetchone())
                    title = (r.get("title") or "")[:50] if r else ""
                
                _bulk_progress[job_id]["current_title"] = title
                _bulk_progress[job_id]["done"] = idx
                _bulk_progress[job_id]["message"] = f"Processing {idx+1}/{len(title_ids)}"
                
                try:
                    if mode == "article":
                        _do_generate_article_external(tid, ai_provider=ai_provider, openrouter_models=openrouter_models)
                    elif mode == "main_image":
                        from imagine import generate_4_images
                        with get_connection() as conn:
                            cur = db_execute(conn, "SELECT prompt FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
                            row = dict_row(cur.fetchone())
                        prompt = (row.get("prompt") or "").strip() if row else ""
                        if prompt:
                            urls, err = generate_4_images(prompt, key_prefix="main_image")
                            if not err and urls:
                                with get_connection() as conn:
                                    db_execute(conn, "UPDATE article_content SET main_image = ?, top_image = ? WHERE title_id = ? AND language_code = 'en'", (urls[0], urls[0], tid))
                    elif mode == "ingredient_image":
                        from imagine import generate_4_images
                        with get_connection() as conn:
                            cur = db_execute(conn, "SELECT prompt_image_ingredients FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
                            row = dict_row(cur.fetchone())
                        prompt = (row.get("prompt_image_ingredients") or "").strip() if row else ""
                        if prompt:
                            urls, err = generate_4_images(prompt, key_prefix="ingredient_image")
                            if not err and urls:
                                with get_connection() as conn:
                                    db_execute(conn, "UPDATE article_content SET ingredient_image = ? WHERE title_id = ? AND language_code = 'en'", (urls[0], tid))
                    elif mode == "images":
                        from imagine import generate_4_images
                        with get_connection() as conn:
                            cur = db_execute(conn, "SELECT prompt, prompt_image_ingredients FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
                            row = dict_row(cur.fetchone())
                        prompt = (row.get("prompt") or "").strip() if row else ""
                        prompt_ing = (row.get("prompt_image_ingredients") or "").strip() if row else ""
                        if prompt:
                            urls, err = generate_4_images(prompt, key_prefix="main_image")
                            if not err and urls:
                                with get_connection() as conn:
                                    db_execute(conn, "UPDATE article_content SET main_image = ?, top_image = ? WHERE title_id = ? AND language_code = 'en'", (urls[0], urls[0], tid))
                        if prompt_ing:
                            urls2, err2 = generate_4_images(prompt_ing, key_prefix="ingredient_image")
                            if not err2 and urls2:
                                with get_connection() as conn:
                                    db_execute(conn, "UPDATE article_content SET ingredient_image = ? WHERE title_id = ? AND language_code = 'en'", (urls2[0], tid))
                    
                    total_ok += 1
                    steps = _bulk_progress[job_id].get("steps", [])
                    steps.append(f"✓ [{tid}] {title}")
                    _bulk_progress[job_id]["steps"] = steps[-80:]
                except Exception as e:
                    total_failed += 1
                    steps = _bulk_progress[job_id].get("steps", [])
                    steps.append(f"✗ [{tid}] {title} | {str(e)[:60]}")
                    _bulk_progress[job_id]["steps"] = steps[-80:]
            
            if _bulk_cancel.get(job_id):
                _bulk_progress[job_id].update({"status": "cancelled", "message": f"Cancelled. {total_ok}✓ {total_failed}✗", "ok": total_ok, "failed": total_failed})
            else:
                _bulk_progress[job_id].update({"status": "done", "message": f"Done. {total_ok}✓ {total_failed}✗", "ok": total_ok, "failed": total_failed})
        except Exception as e:
            _bulk_progress[job_id].update({"status": "error", "message": str(e)})
    
    threading.Thread(target=task, daemon=True).start()
    return jsonify({"success": True, "job_id": job_id})


@app.route("/api/bulk-run-all-groups", methods=["POST"])
def api_bulk_run_all_groups():
    """Run bulk-run for all rows in all groups. scope_content/scope_images for content vs images."""
    data = request.get_json(silent=True) or {}
    req = {**data, **dict(request.args)}
    mode = str(req.get("mode", "all")).lower()
    scope = str(req.get("scope") or "override").lower()
    scope_content = str(req.get("scope_content") or scope).lower()
    scope_images = str(req.get("scope_images") or scope).lower()
    for s in (scope, scope_content, scope_images):
        if s not in ("override", "empty_only"):
            scope = scope_content = scope_images = "override"
            break
    async_mode = str(req.get("async", "") or "").lower() in ("1", "true", "yes")
    concurrency_type = str(req.get("concurrency_type", "row")).lower()
    if concurrency_type not in ("row", "group"):
        concurrency_type = "row"
    concurrency_n = int(req.get("concurrency_n") or 1)
    ai_provider = (req.get("ai_provider") or "").strip() or None
    openrouter_models = _parse_openrouter_models(req)
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM `groups` WHERE id IS NOT NULL ORDER BY id")
        group_ids = [dict_row(r).get("id") for r in cur.fetchall() if dict_row(r).get("id")]
    if not group_ids:
        return jsonify({"success": False, "error": "No groups"}), 400
    if async_mode:
        job_id = str(uuid.uuid4())
        domain_ids = []
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT DISTINCT id FROM domains")
            domain_ids = [dict_row(r).get("id") for r in cur.fetchall() if dict_row(r).get("id")]
        _bulk_progress[job_id] = {"status": "running", "message": "Starting...", "current_title": "", "type": "all", "mode": mode, "domain_ids": domain_ids, "created_at": time.time(), "steps": []}
        user = get_current_user()
        user_id = user["id"] if user else None
        threading.Thread(target=_run_bulk_all_groups_async, args=(job_id, mode, concurrency_type, concurrency_n, scope, scope_content, scope_images, ai_provider, openrouter_models, user_id), daemon=True).start()
        return jsonify({"success": True, "job_id": job_id})
    total_ok, total_failed = 0, 0
    for gid in group_ids:
        ok, failed = _bulk_run_one_group(gid, mode, scope=scope, scope_content=scope_content, scope_images=scope_images, ai_provider=ai_provider, openrouter_models=openrouter_models)
        total_ok += ok
        total_failed += failed
    return jsonify({"success": True, "message": f"{total_ok} rows done" + (f", {total_failed} failed" if total_failed else "")})


def _content_blocks_to_html(content_str):
    """Convert content JSON (blocks) to HTML."""
    if not content_str or not content_str.strip():
        return ""
    try:
        data = json.loads(content_str)
        blocks = data.get("blocks") if isinstance(data, dict) else []
    except Exception:
        return content_str
    out = []
    for b in blocks if isinstance(blocks, list) else []:
        if not isinstance(b, dict):
            continue
        t = b.get("type", "")
        c = b.get("content", "")
        items = b.get("items", [])
        if t == "p" and c:
            out.append(f"<p>{c}</p>")
        elif t == "h2" and c:
            out.append(f"<h2>{c}</h2>")
        elif t == "h3" and c:
            out.append(f"<h3>{c}</h3>")
        elif t == "lightbulb":
            title = b.get("title", "")
            if title:
                out.append(f"<h3>{title}</h3>")
            if items:
                out.append("<ul>")
                for it in items:
                    out.append(f"<li>{it}</li>")
                out.append("</ul>")
    return "".join(out) if out else content_str


@app.route("/api/domain-articles/<int:domain_id>", methods=["GET"])
def api_domain_articles(domain_id):
    """Return all articles for a domain in ARTICLES format. GET /api/domain-articles/<domain_id>"""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM domains WHERE id = ?", (domain_id,))
        if not cur.fetchone():
            return jsonify({"error": "Domain not found"}), 404
        cur = db_execute(conn, """SELECT t.id, t.title, t.created_at, ac.article_html, ac.meta_description, ac.main_image, ac.ingredient_image, ac.recipe
            FROM titles t
            LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ?
            ORDER BY t.id""", (domain_id,))
        rows = [dict_row(r) for r in cur.fetchall()]
    articles = []
    for r in rows:
        recipe = {}
        try:
            recipe = json.loads(r.get("recipe") or "{}") if isinstance(r.get("recipe"), str) else (r.get("recipe") or {})
        except Exception:
            pass
        html_content = (r.get("article_html") or "").strip()
        main_img = (r.get("main_image") or "").strip()
        ing_img = (r.get("ingredient_image") or "").strip()
        created = r.get("created_at") or ""
        if hasattr(created, "strftime"):
            created = created.strftime("%Y-%m-%d") if created else ""
        else:
            created = str(created)[:10] if created else ""
        articles.append({
            "id": r.get("id"),
            "title": r.get("title") or "",
            "category": recipe.get("course") or "",
            "excerpt": r.get("meta_description") or "",
            "html_content": html_content,
            "image": main_img,
            "image_ingredient": ing_img,
            "prep_time": recipe.get("prep_time") or "",
            "cook_time": recipe.get("cook_time") or "",
            "servings": recipe.get("servings") or "",
            "date": created,
            "recipe": recipe,
        })
    return jsonify({"articles": articles})


@app.route("/api/groups")
def api_groups():
    """Return groups with id and name."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, name FROM `groups` ORDER BY id")
        rows = [dict_row(r) for r in cur.fetchall()]
    return jsonify({"groups": [{"id": r["id"], "name": r.get("name") or f"Group {r['id']}"} for r in rows]})


@app.route("/api/title-context/<int:title_id>")
def api_title_context(title_id):
    """Return domain_id and group_id for a title. Used to pre-select domain/group when opening article editor with ?title_id=X."""
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT t.domain_id, COALESCE(t.group_id, d.group_id) as group_id
            FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?""", (title_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Title not found"}), 404
    return jsonify({"domain_id": row.get("domain_id"), "group_id": row.get("group_id")})


@app.route("/api/titles-with-article")
def api_titles_with_article():
    """Return titles that have article_content. Query: domain_id, group_id, title_id, title_search.
    If title_id: return list mode with that title (and others from same domain). If group_id: returns rows (each row = same title across A,B,C,D)."""
    domain_id = request.args.get("domain_id", type=int)
    group_id = request.args.get("group_id", type=int)
    title_id = request.args.get("title_id", type=int)
    title_search = (request.args.get("title_search") or "").strip().lower()
    category = (request.args.get("category") or "").strip().lower()
    with get_connection() as conn:
        # When title_id is passed, return list mode with that title (for direct article selection in editor)
        if title_id:
            cur = db_execute(conn, """SELECT t.id, t.title, d.domain_name, d.domain_url, d.id as domain_id
                FROM titles t
                JOIN domains d ON t.domain_id = d.id
                JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.id = ? AND (ac.article_html IS NOT NULL AND ac.article_html != '')""", (title_id,))
            r = dict_row(cur.fetchone())
            if r:
                return jsonify({"mode": "list", "titles": [{"id": r["id"], "title": (r.get("title") or "")[:80], "domain": r.get("domain_url") or r.get("domain_name") or "", "domain_id": r.get("domain_id")}]})
            return jsonify({"mode": "list", "titles": []})
        if group_id:
            cur = db_execute(conn, """SELECT t.id, t.title, t.domain_id, d.domain_index, d.domain_name, d.domain_url, ac.main_image
                FROM titles t
                JOIN domains d ON t.domain_id = d.id AND d.group_id = ?
                JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE (ac.article_html IS NOT NULL AND ac.article_html != '')
                ORDER BY t.title, d.domain_index""", (group_id,))
            rows = [dict_row(r) for r in cur.fetchall()]
            row_map = {}
            labels = ["A", "B", "C", "D"]
            for r in rows:
                ttxt = (r.get("title") or "").strip()
                if title_search and title_search not in ttxt.lower():
                    continue
                key = ttxt
                if key not in row_map:
                    row_map[key] = {"title": ttxt[:80], "title_ids": [None, None, None, None], "main_images": ["", "", "", ""], "domain_labels": labels}
                idx = r.get("domain_index") if r.get("domain_index") is not None and 0 <= r.get("domain_index") < 4 else 0
                row_map[key]["title_ids"][idx] = r["id"]
                main_img = (r.get("main_image") or "").strip()
                if main_img and main_img.startswith("http"):
                    row_map[key]["main_images"][idx] = main_img
            return jsonify({"mode": "group", "rows": list(row_map.values())})
        base_sql = """SELECT t.id, t.title, d.domain_name, d.domain_url, d.id as domain_id, ac.recipe
            FROM titles t
            JOIN domains d ON t.domain_id = d.id
            JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE (ac.article_html IS NOT NULL AND ac.article_html != '')"""
        params = []
        if domain_id:
            base_sql += " AND d.id = ?"
            params.append(domain_id)
        if title_search:
            base_sql += " AND LOWER(t.title) LIKE ?"
            params.append("%" + title_search + "%")
        base_sql += " ORDER BY t.id DESC LIMIT 500"
        cur = db_execute(conn, base_sql, tuple(params) if params else ())
        rows = [dict_row(r) for r in cur.fetchall()]
        if category:
            filtered = []
            for r in rows:
                try:
                    recipe = json.loads(r.get("recipe") or "{}") if isinstance(r.get("recipe"), str) else (r.get("recipe") or {})
                    course = (recipe.get("course") or recipe.get("categorie") or "").strip().lower()
                    if course == category:
                        filtered.append(r)
                except (json.JSONDecodeError, TypeError):
                    pass
            rows = filtered
    return jsonify({"mode": "list", "titles": [{"id": r["id"], "title": (r.get("title") or "")[:80], "domain": r.get("domain_url") or r.get("domain_name") or "", "domain_id": r.get("domain_id")} for r in rows]})


@app.route("/api/article-content/<int:title_id>", methods=["GET", "PUT"])
def api_article_content(title_id):
    """GET: Return article_content fields. PUT: Update article_html and/or article_css only (no AI regeneration). Body: { article_html?, article_css? }"""
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT article_html, article_css, recipe, main_image, ingredient_image, pin_image, model_used, generated_at, generation_time_seconds FROM article_content
            WHERE title_id = ? AND language_code = 'en'""", (title_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Not found"}), 404
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        html_val = data.get("article_html")
        css_val = data.get("article_css")
        if html_val is None and css_val is None:
            return jsonify({"success": False, "error": "Provide article_html and/or article_css"}), 400
        updates = []
        params = []
        if html_val is not None:
            updates.append("article_html = ?")
            params.append((html_val if isinstance(html_val, str) else str(html_val)).strip())
        if css_val is not None:
            updates.append("article_css = ?")
            params.append((css_val if isinstance(css_val, str) else str(css_val)).strip())
        params.append(title_id)
        with get_connection() as conn:
            db_execute(conn, f"UPDATE article_content SET {', '.join(updates)} WHERE title_id = ? AND language_code = 'en'", tuple(params))
        return jsonify({"success": True, "message": "Updated (HTML/CSS only, no regeneration)"})
    html = (row.get("article_html") or "").strip()
    return jsonify({
        "article_html": html,
        "article_css": row.get("article_css") or "",
        "recipe": row.get("recipe") or "",
        "main_image": row.get("main_image") or "",
        "ingredient_image": row.get("ingredient_image") or "",
        "pin_image": row.get("pin_image") or "",
        "model_used": row.get("model_used") or "",
        "generated_at": str(row.get("generated_at") or "") if row.get("generated_at") else "",
        "generation_time_seconds": row.get("generation_time_seconds"),
    })


@app.route("/api/article-content/<int:title_id>/validated", methods=["PUT"])
def api_article_content_set_validated(title_id):
    """Set validated flag for this article. Body: { \"validated\": true|false }. Returns { success, validated }."""
    data = request.get_json(silent=True) or {}
    validated = data.get("validated")
    if validated is None:
        return jsonify({"success": False, "error": "Provide validated (true/false)"}), 400
    val = 1 if validated else 0
    with get_connection() as conn:
        cur = db_execute(conn, "UPDATE article_content SET validated = ? WHERE title_id = ? AND language_code = 'en'", (val, title_id))
        affected = cur.rowcount if hasattr(cur, 'rowcount') else 0
    return jsonify({"success": True, "validated": bool(val), "updated": affected > 0})


# Injection points for article HTML snippets (add ads, scripts per section). Marker or fallback search.
SNIPPET_POINTS = [
    ("head-end", "<!-- inject:head-end -->", "</head>", "before"),
    ("after-hero", "<!-- inject:after-hero -->", 'class="hero-image">', "after"),
    ("before-recipe", "<!-- inject:before-recipe -->", '<div class="recipe-card">', "before"),
    ("article-end", "<!-- inject:article-end -->", "</article>", "before"),
]


def _strip_injected_snippets(html_content):
    """Remove previously injected snippet blocks (idempotent apply)."""
    if not html_content:
        return html_content
    for point_name, _, _, _ in SNIPPET_POINTS:
        start_tag = f"<!-- snippet:{point_name} -->"
        end_tag = f"<!-- /snippet:{point_name} -->"
        if start_tag in html_content and end_tag in html_content:
            pattern = re.compile(re.escape(start_tag) + r"[\s\S]*?" + re.escape(end_tag), re.DOTALL)
            html_content = pattern.sub("", html_content)
    return html_content


def _inject_snippets_into_html(html_content, snippets):
    """Inject snippets at markers or fallback positions. snippets: dict { point_name: html }. Idempotent."""
    if not html_content or not isinstance(html_content, str) or not isinstance(snippets, dict):
        return html_content
    result = _strip_injected_snippets(html_content)
    for point_name, marker, fallback_search, position in SNIPPET_POINTS:
        snippet = (snippets.get(point_name) or "").strip()
        if not snippet:
            continue
        wrapped = f"<!-- snippet:{point_name} -->\n{snippet}\n<!-- /snippet:{point_name} -->"
        if marker in result:
            result = result.replace(marker, marker + "\n" + wrapped, 1)
        elif fallback_search and fallback_search in result:
            idx = result.find(fallback_search)
            if position == "after":
                insert_at = idx + len(fallback_search)
                result = result[:insert_at] + "\n" + wrapped + result[insert_at:]
            else:
                result = result[:idx] + wrapped + "\n" + result[idx:]
    return result


def _inject_snippets_into_article_html(html_content, snippets_json):
    """Apply domain snippets to HTML. snippets_json: JSON string or dict."""
    if not snippets_json:
        return html_content
    if isinstance(snippets_json, str):
        try:
            snippets = json.loads(snippets_json) if snippets_json.strip() else {}
        except json.JSONDecodeError:
            return html_content
    else:
        snippets = snippets_json
    return _inject_snippets_into_html(html_content, snippets)


_PLACEHOLDER_SRC_RE = re.compile(r'^(placeholder|dummy|sample|#|about:blank|data:image/svg)', re.I)


def _is_placeholder_src(src):
    """Return True if the src looks like a placeholder, not a real image URL."""
    s = (src or "").strip()
    if not s:
        return True
    if _PLACEHOLDER_SRC_RE.match(s):
        return True
    if s in ("#", "/", "//"):
        return True
    return False


def _inject_images_into_article_html(html_content, main_image, ingredient_image, top_image=None, bottom_image=None):
    """Replace img src in article HTML with corresponding URLs. Works with hero-image, recipe-card-image, ingredients-flatlay, article-image.
    Also replaces placeholder src values (placeholder.jpg, #, empty) as a fallback."""
    if not html_content or not isinstance(html_content, str):
        return html_content
    main_url = (main_image or "").strip() if main_image else ""
    ing_url = (ingredient_image or "").strip() if ingredient_image else ""
    if not main_url and not ing_url:
        return html_content

    pattern = re.compile(r'<img\s+([^>]+)>', re.IGNORECASE)
    result = []
    pos = 0
    article_image_count = [0]
    placeholder_count = [0]
    for m in pattern.finditer(html_content):
        result.append(html_content[pos:m.start()])
        full = m.group(0)
        attrs = m.group(1)
        src_m = re.search(r'(?:^|\s)src\s*=\s*["\']([^"\']*)["\']', attrs, re.I)
        class_m = re.search(r'(?:^|\s)class\s*=\s*["\']([^"\']*)["\']', attrs, re.I)
        classes = (class_m.group(1) or "").lower().split() if class_m else []
        cls_str = " ".join(classes)
        current_src = src_m.group(1) if src_m else ""
        new_url = None

        if "hero-image" in classes or "recipe-card-image" in classes or "recipe-image" in classes:
            new_url = main_url
        elif "ingredients-flatlay" in classes or "ingredient" in cls_str:
            new_url = ing_url
        elif "article-image" in classes:
            article_image_count[0] += 1
            new_url = main_url if article_image_count[0] == 1 else ing_url
        elif src_m and _is_placeholder_src(current_src):
            placeholder_count[0] += 1
            new_url = main_url if placeholder_count[0] == 1 else (ing_url or main_url)

        if new_url and src_m:
            new_src = ' src="' + new_url + '"'
            new_attrs = attrs[:src_m.start()] + new_src + attrs[src_m.end():]
            result.append('<img ' + new_attrs + '>')
        else:
            result.append(full)
        pos = m.end()
    result.append(html_content[pos:])
    return "".join(result)


def _update_article_html_images(title_id):
    """Fetch current image URLs and inject into article_html for title_id. Call after generating images."""
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT article_html, article, main_image, ingredient_image, top_image, bottom_image
            FROM article_content WHERE title_id = ? AND language_code = 'en'""", (title_id,))
        row = dict_row(cur.fetchone())
        
    if not row:
        return
        
    html_orig = (row.get("article_html") or "").strip()
    article_orig = (row.get("article") or "").strip()
    main_img = (row.get("main_image") or "").strip()
    ing_img = (row.get("ingredient_image") or "").strip()
    
    updates = []
    vals = []
    
    if html_orig:
        html_new = _inject_images_into_article_html(html_orig, main_img, ing_img)
        if html_new != html_orig:
            updates.append("article_html = ?")
            vals.append(html_new)
            
    if article_orig:
        article_new = _inject_images_into_article_html(article_orig, main_img, ing_img)
        if article_new != article_orig:
            updates.append("article = ?")
            vals.append(article_new)
            
    if updates:
        vals.append(title_id)
        query = f"UPDATE article_content SET {', '.join(updates)} WHERE title_id = ? AND language_code = 'en'"
        with get_connection() as conn:
            db_execute(conn, query, tuple(vals))
        log.info("[inject-images] Updated %s with image URLs for title_id=%s", ", ".join([u.split("=")[0].strip() for u in updates]), title_id)


_PIN_IMAGE_TAG_RE = re.compile(r'<div\s+class="pin-image-data"\s+data-pin-image="[^"]*"\s+style="display:none"></div>\s*', re.IGNORECASE)


def _inject_pin_image_into_article_html(html_content, pin_image_url):
    """Embed a hidden data-pin-image element inside article_html so the Pin button can find it in any rendering context."""
    if not html_content or not isinstance(html_content, str):
        return html_content
    cleaned = _PIN_IMAGE_TAG_RE.sub("", html_content)
    if not pin_image_url:
        return cleaned
    tag = f'<div class="pin-image-data" data-pin-image="{pin_image_url}" style="display:none"></div>\n'
    return tag + cleaned


def _update_article_html_pin_image(title_id):
    """Fetch current pin_image URL and inject into article_html for title_id. Call after generating pin image."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT article_html, article, pin_image FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
        row = dict_row(cur.fetchone())
        
    if not row:
        return
        
    html_orig = (row.get("article_html") or "").strip()
    article_orig = (row.get("article") or "").strip()
    pin_url = (row.get("pin_image") or "").strip()
    
    updates = []
    vals = []
    
    if html_orig:
        html_new = _inject_pin_image_into_article_html(html_orig, pin_url)
        if html_new != html_orig:
            updates.append("article_html = ?")
            vals.append(html_new)
            
    if article_orig:
        article_new = _inject_pin_image_into_article_html(article_orig, pin_url)
        if article_new != article_orig:
            updates.append("article = ?")
            vals.append(article_new)
            
    if updates:
        vals.append(title_id)
        query = f"UPDATE article_content SET {', '.join(updates)} WHERE title_id = ? AND language_code = 'en'"
        with get_connection() as conn:
            db_execute(conn, query, tuple(vals))
        log.info("[inject-pin-image] Updated %s with pin_image for title_id=%s", ", ".join([u.split("=")[0].strip() for u in updates]), title_id)


def _do_generate_main_image(title_id, user_id=None):
    """Core logic for generate-main-image. Raises on error."""
    from imagine import generate_4_images
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT t.id, t.title, t.group_id, d.domain_index FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id,))
        t = dict_row(cur.fetchone())
        if not t or t.get("domain_index") != 0:
            raise ValueError("Use Domain A title")
        cur = db_execute(conn, "SELECT prompt FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
        row = dict_row(cur.fetchone())
        prompt = (row.get("prompt") or "").strip() if row else ""
        if not prompt:
            raise ValueError("Generate (A) first to get prompt")
        cur = db_execute(conn, """SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id
            WHERE t.group_id = ? AND t.title = ? AND d.domain_index IN (0,1,2,3) ORDER BY d.domain_index""", (t["group_id"], t["title"]))
        title_ids = [dict_row(r).get("id") for r in cur.fetchall()]
    if len(title_ids) < 4:
        raise ValueError("Need 4 domains (A,B,C,D) in group")
    user_config = get_user_config_for_api(user_id) if user_id else {}
    urls, err = generate_4_images(prompt, key_prefix="main_image", user_config=user_config)
    if err:
        raise ValueError(err)
    from imagine import flip_image_vertical_and_upload
    BOTTOM_SOURCE_INDEX = (1, 0, 3, 2)
    bottom_urls = [None] * 4
    for i in range(min(4, len(urls))):
        src = BOTTOM_SOURCE_INDEX[i]
        if src < len(urls) and urls[src]:
            try:
                bottom_urls[i] = flip_image_vertical_and_upload(urls[src], "bottom_image", user_config=user_config)
            except Exception:
                bottom_urls[i] = None
    with get_connection() as conn:
        for i, tid in enumerate(title_ids[:4]):
            if i < len(urls):
                main_url = urls[i]
                bottom_url = bottom_urls[i] if i < len(bottom_urls) else None
                cur = db_execute(conn, "UPDATE article_content SET main_image = ?, top_image = ?, bottom_image = ? WHERE title_id = ? AND language_code = 'en'", (main_url, main_url, bottom_url, tid))
                if cur.rowcount == 0:
                    db_execute(conn, "INSERT INTO article_content (title_id, language_code, main_image, top_image, bottom_image) VALUES (?, 'en', ?, ?, ?)", (tid, main_url, main_url, bottom_url))
    for tid in title_ids[:4]:
        _update_article_html_images(tid)


@app.route("/api/generate-main-image", methods=["POST"])
@login_required
def api_generate_main_image():
    """Generate main image via Midjourney. Takes title_id (Domain A). Assigns image 1->A, 2->B, 3->C, 4->D."""
    user = get_current_user()
    user_id = user["id"]
    
    # Check user has required API keys
    has_keys, error_msg = check_user_has_required_keys(user_id, "image")
    if not has_keys:
        return jsonify({"success": False, "error": error_msg}), 403
    
    data = request.get_json(silent=True) or request.form or {}
    title_id = data.get("title_id") or request.args.get("title_id")
    async_mode = str(data.get("async") or request.args.get("async", "") or "").lower() in ("1", "true", "yes")
    if not title_id:
        return jsonify({"success": False, "error": "title_id required"}), 400
    title_id = int(title_id)
    if async_mode:
        job_id = str(uuid.uuid4())
        domain_id = None
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_id FROM titles WHERE id = ?", (title_id,))
            r = dict_row(cur.fetchone())
            if r:
                domain_id = r.get("domain_id")
        _bulk_progress[job_id] = {"status": "running", "message": "Generating main images...", "current_title": "", "type": "single", "action": "Main image", "title_id": title_id, "domain_id": domain_id, "created_at": time.time()}
        def task():
            try:
                _do_generate_main_image(title_id)
                _bulk_progress[job_id].update({"status": "done", "message": "Main images generated"})
            except Exception as e:
                _bulk_progress[job_id].update({"status": "error", "message": str(e)})
        threading.Thread(target=task, daemon=True).start()
        return jsonify({"success": True, "job_id": job_id})
    _do_generate_main_image(title_id)
    return jsonify({"success": True, "message": "Main images generated"})


def _do_generate_ingredient_image(title_id, user_id=None):
    """Core logic for generate-ingredient-image. Raises on error."""
    from imagine import generate_4_images
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT t.id, t.title, t.group_id, d.domain_index FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id,))
        t = dict_row(cur.fetchone())
        if not t or t.get("domain_index") != 0:
            raise ValueError("Use Domain A title")
        cur = db_execute(conn, "SELECT prompt_image_ingredients FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
        row = dict_row(cur.fetchone())
        prompt = (row.get("prompt_image_ingredients") or "").strip() if row else ""
        if not prompt:
            raise ValueError("Generate (A) first to get prompt_image_ingredients")
        cur = db_execute(conn, """SELECT t.id FROM titles t JOIN domains d ON t.domain_id = d.id
            WHERE t.group_id = ? AND t.title = ? AND d.domain_index IN (0,1,2,3) ORDER BY d.domain_index""", (t["group_id"], t["title"]))
        title_ids = [dict_row(r).get("id") for r in cur.fetchall()]
    if len(title_ids) < 4:
        raise ValueError("Need 4 domains (A,B,C,D) in group")
    user_config = get_user_config_for_api(user_id) if user_id else {}
    urls, err = generate_4_images(prompt, key_prefix="ingredient_image", user_config=user_config)
    if err:
        raise ValueError(err)
    with get_connection() as conn:
        for i, tid in enumerate(title_ids[:4]):
            if i < len(urls):
                cur = db_execute(conn, "UPDATE article_content SET ingredient_image = ? WHERE title_id = ? AND language_code = 'en'", (urls[i], tid))
                if cur.rowcount == 0:
                    db_execute(conn, "INSERT INTO article_content (title_id, language_code, ingredient_image) VALUES (?, 'en', ?)", (tid, urls[i]))
    for tid in title_ids[:4]:
        _update_article_html_images(tid)


@app.route("/api/generate-ingredient-image", methods=["POST"])
def api_generate_ingredient_image():
    """Generate ingredient image via Midjourney. Takes title_id (Domain A). Assigns image 1->A, 2->B, 3->C, 4->D."""
    data = request.get_json(silent=True) or request.form or {}
    title_id = data.get("title_id") or request.args.get("title_id")
    async_mode = str(data.get("async") or request.args.get("async", "") or "").lower() in ("1", "true", "yes")
    if not title_id:
        return jsonify({"success": False, "error": "title_id required"}), 400
    title_id = int(title_id)
    if async_mode:
        job_id = str(uuid.uuid4())
        domain_id = None
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_id FROM titles WHERE id = ?", (title_id,))
            r = dict_row(cur.fetchone())
            if r:
                domain_id = r.get("domain_id")
        _bulk_progress[job_id] = {"status": "running", "message": "Generating ingredient images...", "current_title": "", "type": "single", "action": "Ingredient image", "title_id": title_id, "domain_id": domain_id, "created_at": time.time()}
        def task():
            try:
                _do_generate_ingredient_image(title_id)
                _bulk_progress[job_id].update({"status": "done", "message": "Ingredient images generated"})
            except Exception as e:
                _bulk_progress[job_id].update({"status": "error", "message": str(e)})
        threading.Thread(target=task, daemon=True).start()
        return jsonify({"success": True, "job_id": job_id})
    _do_generate_ingredient_image(title_id)
    return jsonify({"success": True, "message": "Ingredient images generated"})


def _do_generate_pin_image(title_id, domain_template_id=None):
    """Generate pin image for this title: use its domain's template and article_content, call Pin API, save to this title's article_content only.
    If domain_template_id is given, use that specific template; otherwise auto-rotate."""
    import re
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT t.id, t.title, t.group_id, d.id AS domain_id, d.domain_index, d.last_pin_template_index FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id,))
        t = dict_row(cur.fetchone())
        if not t:
            raise ValueError("Title not found")
        domain_id = t["domain_id"]
        if domain_template_id:
            cur = db_execute(conn, "SELECT id, template_json FROM domain_templates WHERE id = ? AND domain_id = ?", (domain_template_id, domain_id))
            template_row = dict_row(cur.fetchone())
            if not template_row:
                raise ValueError(f"Template #{domain_template_id} not found for this domain")
        else:
            cur = db_execute(conn, """SELECT id, template_json FROM domain_templates WHERE domain_id = ? ORDER BY sort_order, id""", (domain_id,))
            templates = [dict_row(r) for r in cur.fetchall()]
            if not templates:
                raise ValueError("No pin templates for this domain. Add templates in Admin → Domains → Templates.")
            idx = (t.get("last_pin_template_index") or 0) % len(templates)
            template_row = templates[idx]
            next_idx = ((t.get("last_pin_template_index") or 0) + 1) % len(templates)
            db_execute(conn, "UPDATE domains SET last_pin_template_index = ? WHERE id = ?", (next_idx, domain_id))
        template_json_str = (template_row.get("template_json") or "").strip()
        if not template_json_str:
            raise ValueError("Template JSON is empty")
        # Article content for title_id (domain A)
        cur = db_execute(conn, """SELECT main_image, ingredient_image, top_image, bottom_image, recipe_title_pin FROM article_content WHERE title_id = ? AND language_code = 'en'""", (title_id,))
        ac = dict_row(cur.fetchone()) or {}
        cur = db_execute(conn, "SELECT title FROM titles WHERE id = ?", (title_id,))
        title_row = dict_row(cur.fetchone())
        title_text = (title_row.get("title") or "").strip() if title_row else ""
        article_title = (ac.get("recipe_title_pin") or "").strip() or title_text
        main_img = (ac.get("main_image") or "").strip()
        ing_img = (ac.get("ingredient_image") or "").strip()
        top_img = (ac.get("top_image") or "").strip() or main_img
        bottom_img = (ac.get("bottom_image") or "").strip() or ing_img or main_img
        cur = db_execute(conn, "SELECT domain_url, domain_name, domain_colors, domain_fonts FROM domains WHERE id = ?", (domain_id,))
        dom_row = dict_row(cur.fetchone()) or {}
        domain_display = (dom_row.get("domain_url") or "").strip() or (dom_row.get("domain_name") or "").strip()
        if domain_display and "://" in domain_display:
            try:
                from urllib.parse import urlparse
                domain_display = urlparse(domain_display).hostname or domain_display
            except Exception:
                pass
        # 5001: replace ALL {{}} in domain template with correspondent data from article_content and domain
        def esc(s):
            return (s or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        replacements = {
            "main_image": esc(main_img),
            "top_image": esc(top_img),
            "bottom_image": esc(bottom_img),
            "avatar_image": esc(main_img or ing_img),
            "title": esc(article_title),
            "subtitle": "",
            "badge": "",
            "website": esc(domain_display),
            "time_badge": "",
        }
        filled = template_json_str
        for k, v in replacements.items():
            filled = filled.replace("{{" + k + "}}", (v or ""))
        filled = re.sub(r'\{\{[^}]+\}\}', '', filled)
        try:
            body = json.loads(filled)
        except json.JSONDecodeError as e:
            raise ValueError("Template JSON invalid after replace: " + str(e))
        template_name = body.get("template_name") or body.get("template_id") or ""
        payload = body.get("template_data") if "template_data" in body else body
        if not template_name:
            raise ValueError("Template JSON must include template_name or template_id (e.g. template_5). Save from Pin Editor with a selected template.")
        if not isinstance(payload, dict):
            payload = {}
        # Ensure template image slots use article images: inject URLs so 5000 uses main_image, top_image, bottom_image, etc.
        if main_img:
            payload["main_image"] = main_img
            payload["background"] = main_img  # template_1 and others use "background" for full-screen main
        if top_img:
            payload["top_image"] = top_img
        if bottom_img:
            payload["bottom_image"] = bottom_img
        if main_img or ing_img:
            payload["avatar_image"] = main_img or ing_img
        # Pass article title so 5000 injects it into prompts and calls OpenAI for text elements (except website)
        payload["variables"] = {"title": article_title}
        # Pass domain colors/fonts so Pin API can style the pin to match the domain
        raw_colors = (dom_row.get("domain_colors") or "").strip()
        if raw_colors:
            try:
                payload["domain_colors"] = json.loads(raw_colors) if isinstance(raw_colors, str) else raw_colors
            except (json.JSONDecodeError, TypeError):
                pass
        raw_fonts = (dom_row.get("domain_fonts") or "").strip()
        if raw_fonts:
            try:
                payload["domain_fonts"] = json.loads(raw_fonts) if isinstance(raw_fonts, str) else raw_fonts
            except (json.JSONDecodeError, TypeError):
                pass
        # Kimi_Agent_Pin (Pin API) generates the image and uploads to Cloudflare R2; it returns image_url.
        pin_api_base = (PIN_API_URL or "http://localhost:5000").rstrip("/")
        api_url = pin_api_base + "/generate?name=" + str(template_name).strip().lower().replace("-", "_")
        try:
            r = requests_lib.post(api_url, json=payload, timeout=90)
            r.raise_for_status()
            data = r.json()
        except requests_lib.RequestException as e:
            raise ValueError("Pin API error: " + str(e))
        if not data.get("success"):
            raise ValueError(data.get("error") or "Pin API returned failure")
        pin_url = data.get("image_url")
        if not pin_url:
            raise ValueError(
                data.get("screenshot_error")
                or "Pin API did not return image_url. Configure R2 (and Playwright) in the Kimi_Agent_Pin folder so the Pin API generates the image and uploads it to Cloudflare, then returns the link."
            )
    # Save pin_image only to this title's article_content
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
        if cur.fetchone():
            db_execute(conn, "UPDATE article_content SET pin_image = ? WHERE title_id = ? AND language_code = 'en'", (pin_url, title_id))
        else:
            db_execute(conn, "INSERT INTO article_content (title_id, language_code, pin_image) VALUES (?, 'en', ?)", (title_id, pin_url))
    _update_article_html_pin_image(title_id)


@app.route("/api/title-pin-templates", methods=["GET"])
def api_title_pin_templates():
    """Get pin templates for a title's domain. Query: title_id."""
    title_id = request.args.get("title_id")
    if not title_id:
        return jsonify({"error": "title_id required"}), 400
    title_id = int(title_id)
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT d.id AS domain_id FROM titles t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?", (title_id,))
        row = dict_row(cur.fetchone())
        if not row:
            return jsonify({"error": "Title not found"}), 404
        domain_id = row["domain_id"]
        cur = db_execute(conn, "SELECT id, name, preview_image_url, sort_order FROM domain_templates WHERE domain_id = ? ORDER BY sort_order, id", (domain_id,))
        templates = []
        for r in cur.fetchall():
            dr = dict_row(r)
            templates.append({"id": dr["id"], "name": dr.get("name") or "", "preview_image_url": dr.get("preview_image_url") or ""})
    return jsonify({"domain_id": domain_id, "templates": templates})


@app.route("/api/generate-pin-image", methods=["POST"])
def api_generate_pin_image():
    """Generate pin image: call Pin API (Kimi_Agent_Pin) to generate and upload to Cloudflare; save returned image_url to article_content.pin_image."""
    data = request.get_json(silent=True) or request.form or {}
    title_id = data.get("title_id") or request.args.get("title_id")
    domain_template_id = data.get("domain_template_id")
    async_mode = str(data.get("async") or request.args.get("async", "") or "").lower() in ("1", "true", "yes")
    if not title_id:
        return jsonify({"success": False, "error": "title_id required"}), 400
    title_id = int(title_id)
    dt_id = int(domain_template_id) if domain_template_id else None
    if async_mode:
        job_id = str(uuid.uuid4())
        domain_id = None
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_id FROM titles WHERE id = ?", (title_id,))
            r = dict_row(cur.fetchone())
            if r:
                domain_id = r.get("domain_id")
        _bulk_progress[job_id] = {"status": "running", "message": "Generating pin image...", "current_title": "", "type": "single", "action": "Pin image", "title_id": title_id, "domain_id": domain_id, "created_at": time.time()}
        def task():
            try:
                _do_generate_pin_image(title_id, domain_template_id=dt_id)
                _bulk_progress[job_id].update({"status": "done", "message": "Pin image generated"})
            except Exception as e:
                _bulk_progress[job_id].update({"status": "error", "message": str(e)})
        threading.Thread(target=task, daemon=True).start()
        return jsonify({"success": True, "job_id": job_id})
    _do_generate_pin_image(title_id, domain_template_id=dt_id)
    return jsonify({"success": True, "message": "Pin image generated"})


@app.route("/api/pinterest-pin-url", methods=["GET"])
def api_pinterest_pin_url():
    """Build Pinterest 'Pin it' URL (no API key). Opens pre-filled save form. Query: title_id."""
    title_id = request.args.get("title_id", type=int)
    if not title_id:
        return jsonify({"error": "title_id required"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, """
            SELECT t.title, d.domain_url
            FROM titles t JOIN domains d ON t.domain_id = d.id
            WHERE t.id = ?
        """, (title_id,))
        row = dict_row(cur.fetchone())
        if not row:
            return jsonify({"error": "Title not found"}), 404
        cur = db_execute(conn, "SELECT pin_image, pinterest_title, recipe_title_pin FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
        ac = dict_row(cur.fetchone()) or {}
    pin_img = (ac.get("pin_image") or "").strip()
    if not pin_img or not pin_img.startswith("http"):
        return jsonify({"error": "No pin image. Generate pin first (P button)."}), 400
    article_url = pinterest_build_article_url(row.get("domain_url"), title_id)
    desc = (ac.get("pinterest_title") or ac.get("recipe_title_pin") or row.get("title") or "")[:500]
    base = "https://www.pinterest.com/pin/create/button/"
    params = "url=" + urllib.parse.quote(article_url or "", safe="") + "&media=" + urllib.parse.quote(pin_img, safe="") + "&description=" + urllib.parse.quote(desc, safe="")
    return jsonify({"url": base + "?" + params})


@app.route("/rss/domain/<int:domain_id>", methods=["GET"])
def rss_domain_feed(domain_id):
    """
    RSS 2.0 feed for a domain. For Pinterest auto-pin: connect this URL in
    Pinterest Business → Settings → Create Pins in bulk → Auto-publish → Connect RSS feed.
    Pins are created automatically from new items (no API, no manual action).
    """
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, domain_url, domain_name FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
        if not row:
            return jsonify({"error": "Domain not found"}), 404
        domain_url = (row.get("domain_url") or "").strip()
        domain_name = (row.get("domain_name") or domain_url or ("Domain %s" % domain_id))[:200]
        cur = db_execute(conn, """
            SELECT t.id AS title_id, t.title,
                   ac.pin_image, ac.pinterest_title, ac.recipe_title_pin
            FROM titles t
            JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ?
              AND ac.pin_image IS NOT NULL AND TRIM(ac.pin_image) != ''
            ORDER BY t.id DESC
            LIMIT 100
        """, (domain_id,))
        rows = [dict_row(r) for r in cur.fetchall()]
    # Build RSS 2.0 (Pinterest supports RSS 2.*; needs title, description, link, image via enclosure)
    feed_title = html.escape(domain_name)
    feed_link = (domain_url if domain_url.startswith("http") else "https://" + domain_url).rstrip("/") if domain_url else request.url_root.rstrip("/")
    out = io.StringIO()
    out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    out.write('<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">\n')
    out.write("  <channel>\n")
    out.write("    <title>%s</title>\n" % feed_title)
    out.write("    <link>%s</link>\n" % html.escape(feed_link))
    out.write("    <description>Articles for %s</description>\n" % feed_title)
    for r in rows:
        title_id = r.get("title_id")
        title = (r.get("title") or "").strip() or "Article %s" % title_id
        desc = (r.get("pinterest_title") or r.get("recipe_title_pin") or title or "")[:500]
        link = pinterest_build_article_url(domain_url, title_id) or ""
        pin_img = (r.get("pin_image") or "").strip()
        out.write("    <item>\n")
        out.write("      <title>%s</title>\n" % html.escape(title))
        out.write("      <link>%s</link>\n" % html.escape(link))
        out.write("      <description>%s</description>\n" % html.escape(desc))
        if pin_img and pin_img.startswith("http"):
            out.write('      <enclosure url="%s" type="image/jpeg" />\n' % html.escape(pin_img))
        out.write("    </item>\n")
    out.write("  </channel>\n</rss>\n")
    resp = make_response(out.getvalue())
    resp.headers["Content-Type"] = "application/rss+xml; charset=utf-8"
    return resp


# --- Pin Editor (in-app at /pin-editor): proxy to Kimi_Agent_Pin API ---
def _pin_api_url():
    return (PIN_API_URL or "http://localhost:5000").rstrip("/")


@app.route("/api/pin-templates", methods=["GET"])
def api_pin_templates():
    """Proxy to Kimi_Agent_Pin /templates for the in-app editor. Pin API must be running (e.g. python generator.py --serve on port 5000)."""
    try:
        r = requests_lib.get(_pin_api_url() + "/templates", timeout=15)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"templates": [], "error": str(e)})


@app.route("/api/pin-template/<path:name>", methods=["GET"])
def api_pin_template(name):
    """Proxy to Kimi_Agent_Pin /template/<name> for the in-app editor."""
    try:
        r = requests_lib.get(_pin_api_url() + "/template/" + name, timeout=15)
        if r.status_code != 200:
            try:
                body = r.json()
            except Exception:
                body = {"raw": r.text[:500]}
            return jsonify({"success": False, "error": f"Pin API returned {r.status_code}", "pin_api_response": body}), 502
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 502


@app.route("/api/pin-generate", methods=["POST"])
def api_pin_generate():
    """
    Proxy to Kimi_Agent_Pin /generate.
    - With template_only=1 (editor preview): returns JSON + index_html only, no screenshot, no R2 upload.
    - Without template_only (Generate image): full generate, screenshot, upload to R2, returns image_url.
    Query: name=, template_only=1 (optional).
    """
    name = request.args.get("name") or (request.get_json(silent=True) or {}).get("template_name")
    if not name:
        return jsonify({"success": False, "error": "name required"}), 400
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"success": False, "error": "JSON body required"}), 400
    template_only = request.args.get("template_only", "")
    url = _pin_api_url() + "/generate?name=" + str(name)
    if str(template_only).strip().lower() in ("1", "true", "yes"):
        url += "&template_only=1"
    try:
        r = requests_lib.post(url, json=body, timeout=90)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 502


@app.route("/api/article-generators")
def api_article_generators():
    """List available article generators from articles-website-generator."""
    base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
    if base:
        try:
            req = urllib.request.Request(f"{base}/generators", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            return jsonify(data)
        except Exception:
            pass
    generators = _list_article_generator_files()
    return jsonify({"generators": generators})


ARTICLE_GENERATOR_DEFAULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "article_generator_defaults.json")


def _load_article_generator_defaults():
    """Load stored defaults from JSON file. Returns dict generator -> config."""
    if not os.path.isfile(ARTICLE_GENERATOR_DEFAULTS_PATH):
        return {}
    try:
        with open(ARTICLE_GENERATOR_DEFAULTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_article_generator_default(gen, config):
    """Save config as default for generator. Merges into existing file."""
    all_defaults = _load_article_generator_defaults()
    all_defaults[gen] = config
    with open(ARTICLE_GENERATOR_DEFAULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_defaults, f, indent=2)


def _deep_merge_dict(base, override):
    """Merge override into base recursively. Override wins for leaf values."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge_dict(result[k], v)
        else:
            result[k] = v
    return result


@app.route("/api/article-generator-defaults", methods=["GET"])
def api_article_generator_defaults_get():
    """Get stored default config for a generator. Query: generator."""
    gen = request.args.get("generator", "generator-1")
    defaults = _load_article_generator_defaults()
    cfg = defaults.get(gen, {})
    return jsonify({"success": True, "config": cfg, "generator": gen})


@app.route("/api/article-generator-defaults", methods=["PUT", "POST"])
def api_article_generator_defaults_save():
    """Save config as default for a generator. Body: { generator, config }."""
    data = request.get_json(silent=True) or {}
    gen = (data.get("generator") or "generator-1").strip()
    cfg = data.get("config")
    if not isinstance(cfg, dict):
        return jsonify({"success": False, "error": "Provide config object"}), 400
    try:
        _save_article_generator_default(gen, cfg)
        return jsonify({"success": True, "generator": gen})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/article-generator-config")
def api_article_generator_config():
    """Fetch default CONFIG: stored defaults merged over generator CONFIG from articles-website-generator."""
    gen = request.args.get("generator", "generator-1")
    base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
    generator_config = {}
    if base:
        try:
            url = f"{base}/generators/{gen}/config"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                generator_config = json.loads(resp.read().decode())
        except Exception as e:
            log.warning("[article-generator-config] Could not fetch from generator: %s", e)
    stored = _load_article_generator_defaults().get(gen, {})
    merged = _deep_merge_dict(generator_config, stored) if generator_config else stored
    return jsonify({"success": True, "config": merged, "generator": gen})


def _list_article_generator_files():
    """List generator-N.py files from ARTICLE_GENERATORS_DIR."""
    if not os.path.isdir(ARTICLE_GENERATORS_DIR):
        return []
    names = []
    for f in os.listdir(ARTICLE_GENERATORS_DIR):
        if f.startswith("generator-") and f.endswith(".py"):
            names.append(f[:-3])  # strip .py
    return sorted(names)


def _get_next_generator_number():
    """Return next generator number (e.g. 5 if generator-1..4 exist)."""
    existing = _list_article_generator_files()
    nums = []
    for n in existing:
        try:
            nums.append(int(n.split("-")[1]))
        except (IndexError, ValueError):
            pass
    return max(nums, default=0) + 1


def _create_new_article_generator(base_name, primary_color, display_name):
    """Create a new generator by copying base and applying new design. Returns (generator_name, error)."""
    base_name = (base_name or "generator-1").strip()
    if not base_name.startswith("generator-"):
        base_name = f"generator-{base_name}" if base_name.isdigit() else "generator-1"
    base_path = os.path.join(ARTICLE_GENERATORS_DIR, base_name + ".py")
    if not os.path.isfile(base_path):
        return None, f"Base generator {base_name} not found"
    next_num = _get_next_generator_number()
    new_name = f"generator-{next_num}"
    new_path = os.path.join(ARTICLE_GENERATORS_DIR, new_name + ".py")
    if os.path.isfile(new_path):
        return None, f"{new_name} already exists"
    primary = (primary_color or "#6C8AE4").strip()
    if not primary.startswith("#"):
        primary = "#" + primary
    with open(base_path, "r", encoding="utf-8") as f:
        content = f.read()
    if primary and len(primary) >= 7:
        content = re.sub(r'"primary":\s*"#[0-9a-fA-F]{6}"', f'"primary": "{primary}"', content, count=1)
    try:
        with open(new_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return None, str(e)
    return new_name, None


@app.route("/api/article-generator-create", methods=["POST"])
def api_article_generator_create():
    """Create a new article generator (Python file). Body: { base_generator, primary_color?, display_name? }."""
    data = request.get_json(silent=True) or {}
    base = (data.get("base_generator") or "generator-1").strip()
    primary = (data.get("primary_color") or "").strip()
    display = (data.get("display_name") or "").strip()
    name, err = _create_new_article_generator(base, primary or None, display or None)
    if err:
        return jsonify({"success": False, "error": err}), 400
    return jsonify({"success": True, "generator": name})


def _apply_article_template_css_to_domain(domain_id, cfg, generator):
    """Fetch new CSS from article-preview API and apply to all articles in domain. Returns count updated, or None on failure."""
    gen = (generator or "generator-1").strip()
    payload = dict(cfg)
    if "title" not in payload or not payload.get("title"):
        payload["title"] = "Sample Recipe Title"
    if "categories_list" not in payload or not isinstance(payload.get("categories_list"), list):
        payload["categories_list"] = [{"id": 1, "categorie": "dessert"}]
    _enforce_pinterest_pin_color(payload)
    base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
    if not base:
        log.warning("[apply-article-css] GENERATE_ARTICLE_API_URL not set")
        return None
    url = f"{base}/generate-article-preview/{gen}"
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            out = json.loads(resp.read().decode())
        article_css = (out.get("article_css") or "").strip()
        if not article_css:
            log.warning("[apply-article-css] No article_css in generator response")
            return None
    except Exception as e:
        log.warning("[apply-article-css] Failed to fetch CSS from generator: %s", e)
        return None
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM titles WHERE domain_id = ?", (domain_id,))
        title_ids = [r["id"] for r in cur.fetchall() if r and r.get("id")]
    if not title_ids:
        return 0
    placeholders = ",".join(["?"] * len(title_ids))
    with get_connection() as conn:
        cur = db_execute(conn, f"UPDATE article_content SET article_css = ? WHERE title_id IN ({placeholders})", (article_css,) + tuple(title_ids))
        updated = cur.rowcount if hasattr(cur, "rowcount") else 0
    log.info("[apply-article-css] Updated %s article_content rows for domain %s", updated, domain_id)
    return updated


@app.route("/api/article-preview", methods=["POST"])
def api_article_preview():
    """Generate article template preview (placeholder content, no AI). For Article Template Editor."""
    data = request.get_json(silent=True) or {}
    config = data.get("config") or {}
    gen = (data.get("generator") or "generator-1").strip()
    if "title" not in config or not config.get("title"):
        config = dict(config)
        config["title"] = config.get("title") or "Sample Recipe Title"
    if "categories_list" not in config or not isinstance(config.get("categories_list"), list):
        config = dict(config)
        config["categories_list"] = config.get("categories_list") or [{"id": 1, "categorie": "dessert"}]
    _enforce_pinterest_pin_color(config)
    base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
    url = f"{base}/generate-article-preview/{gen}"
    try:
        req = urllib.request.Request(url, data=json.dumps(config).encode("utf-8"), method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            out = json.loads(resp.read().decode())
        article_html = (out.get("article_html") or "").strip()
        article_css = (out.get("article_css") or "").strip()
        return jsonify({"success": True, "article_html": article_html, "article_css": article_css})
    except urllib.error.HTTPError as e:
        err = e.read().decode() if e.fp else str(e)
        try:
            det = json.loads(err).get("detail", err)
        except Exception:
            det = err[:500]
        return jsonify({"success": False, "error": str(det), "hint": "Is articles-website-generator running?"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "hint": "Is articles-website-generator running on port 8000?"}), 500


@app.route("/api/article-generator-example")
def api_article_generator_example():
    """Return full HTML for a generator's template example (HTML+CSS combined in one file). For popup preview."""
    gen = (request.args.get("generator") or "generator-1").strip()
    if not gen:
        gen = "generator-1"
    config = {
        "title": "Sample Recipe Title",
        "categories_list": [{"id": 1, "categorie": "dessert"}],
        "colors": {"primary": "#6C8AE4", "secondary": "#9C6ADE", "button_pin": "#E60023", "button_hover_pin": "#FF1A3C"},
    }
    _enforce_pinterest_pin_color(config)
    base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
    if not base:
        return jsonify({"success": False, "error": "GENERATE_ARTICLE_API_URL not set", "html": ""}), 500
    url = f"{base}/generate-article-preview/{gen}"
    try:
        req = urllib.request.Request(url, data=json.dumps(config).encode("utf-8"), method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            out = json.loads(resp.read().decode())
        article_html = (out.get("article_html") or "").strip()
        article_css = (out.get("article_css") or "").strip()
        if not article_html:
            return jsonify({"success": False, "error": "No article_html from generator", "html": ""}), 500
        # Combine into one HTML document: inject <style> with article_css into head or before body
        if article_css:
            style_tag = f"<style>{article_css}</style>"
            if "<head" in article_html and "</head>" in article_html:
                article_html = article_html.replace("</head>", style_tag + "</head>")
            elif "<body" in article_html:
                article_html = article_html.replace("<body", style_tag + "<body", 1)
            else:
                article_html = style_tag + article_html
        return jsonify({"success": True, "html": article_html, "generator": gen})
    except urllib.error.HTTPError as e:
        err = (e.read().decode() if e.fp else str(e))[:500]
        return jsonify({"success": False, "error": str(err), "html": ""}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "html": ""}), 500

@app.route("/api/article-generator-example-raw")
def api_article_generator_example_raw():
    """Return raw HTML directly for iframe consumption."""
    with app.test_request_context(f"/api/article-generator-example?generator={request.args.get('generator', 'generator-1')}"):
        res = api_article_generator_example()
        if res[1] != 200 if isinstance(res, tuple) else res.status_code != 200:
            return f"Error loading preview: {res[0].get_json().get('error') if hasattr(res[0], 'get_json') else 'Unknown'}", 500
        data = res[0].get_json() if isinstance(res, tuple) else res.get_json()
        return data.get("html", "No HTML returned")



@app.route("/article-editor")
@login_required
def article_editor_page():
    """Article template editor: edit domain's article config (colors, fonts, layout) and save to domains.article_template_config."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, "article_editor.html")


@app.route("/article-html-editor")
def article_html_editor_page():
    """Edit article HTML and CSS directly without AI regeneration. Add ads, sections, scripts."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, "article_html_editor.html")


@app.route("/article-snippet-editor")
def article_snippet_editor_page():
    """Edit domain snippets (scripts, ads) per section. Bulk apply to all articles in domain."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, "article_snippet_editor.html")


@app.route("/pin-editor")
@login_required
def pin_editor_page():
    """Serve the in-app Pin Editor (own code, inspired by Pinterest-Pin-Editor)."""
    import os
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    return send_from_directory(static_dir, "pin_editor.html")


# --- Domain API ---
@app.route("/api/domains", methods=["GET"])
def api_domains_list():
    """List domains (id, domain_url, website_template) for article-editor dropdown."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, domain_url, domain_name, website_template FROM domains ORDER BY id")
        rows = [dict_row(r) for r in cur.fetchall()]
    return jsonify({"domains": rows})


@app.route("/api/domains/<int:pk>", methods=["GET", "PUT"])
def api_domain_get(pk):
    """GET: Return domain by id (domain_url). PUT: Update domain_url (domain_name synced to domain_url)."""
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        raw = (data.get("domain_url") or "").strip()
        url = _normalize_domain(raw) or None
        if not url:
            return jsonify({"success": False, "error": "Domain URL is required"}), 400
        # Duplicate check (exclude self)
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id FROM domains WHERE domain_url = ? AND id != ?", (url, pk))
            if cur.fetchone():
                return jsonify({"success": False, "error": f"'{url}' is already in the database"}), 409
            db_execute(conn, "UPDATE domains SET domain_url = ?, domain_name = ? WHERE id = ?", (url, url, pk))
        return jsonify({"success": True, "id": pk, "domain_url": url})
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, domain_url, domain_name, domain_colors, domain_fonts, pinterest_board_id, pinterest_access_token, pinterest_app_id, pinterest_app_secret, pinterest_mode FROM domains WHERE id = ?", (pk,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Domain not found"}), 404
    dc = {}
    raw_c = (row.get("domain_colors") or "").strip()
    if raw_c:
        try:
            dc = json.loads(raw_c) if isinstance(raw_c, str) else raw_c
        except (json.JSONDecodeError, TypeError):
            pass
    df = {}
    raw_f = (row.get("domain_fonts") or "").strip()
    if raw_f:
        try:
            df = json.loads(raw_f) if isinstance(raw_f, str) else raw_f
        except (json.JSONDecodeError, TypeError):
            pass
    out = {"id": row["id"], "domain_url": row.get("domain_url") or "", "domain_name": row.get("domain_name") or "", "domain_colors": dc, "domain_fonts": df}
    out["pinterest_board_id"] = (row.get("pinterest_board_id") or "").strip()
    out["pinterest_app_id"] = (row.get("pinterest_app_id") or "").strip()
    out["pinterest_app_secret_set"] = bool((row.get("pinterest_app_secret") or "").strip())
    out["pinterest_configured"] = bool((row.get("pinterest_access_token") or "").strip() and (row.get("pinterest_board_id") or "").strip())
    # RSS feed for Pinterest auto-pin (no API): connect in Pinterest → Auto-publish
    out["pinterest_rss_feed_url"] = (request.url_root or "").rstrip("/") + "/rss/domain/" + str(pk)
    out["pinterest_mode"] = (row.get("pinterest_mode") or "").strip() or None  # 'rss' | 'manual' | 'schedule'
    return jsonify(out)


@app.route("/api/domains/<int:pk>/pinterest", methods=["PUT"])
@login_required
def api_domain_pinterest(pk):
    """Set Pinterest mode for domain: 'rss' (auto from feed), 'manual' (button per article), 'schedule' (Pinterest checks feed periodically)."""
    data = request.get_json(silent=True) or {}
    mode = (data.get("pinterest_mode") or "").strip().lower()
    if mode not in ("rss", "manual", "schedule", ""):
        return jsonify({"success": False, "error": "pinterest_mode must be rss, manual, or schedule"}), 400
    mode = mode if mode else None
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM domains WHERE id = ?", (pk,))
        if not cur.fetchone():
            return jsonify({"error": "Domain not found"}), 404
        db_execute(conn, "UPDATE domains SET pinterest_mode = ? WHERE id = ?", (mode, pk))
    return jsonify({"success": True, "pinterest_mode": mode})


@app.route("/api/domains/<int:pk>/change-group", methods=["PUT"])
@login_required
def api_domain_change_group(pk):
    """Change the group assignment for a domain."""
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)
    
    data = request.get_json(silent=True) or {}
    group_id = data.get("group_id")
    if group_id == "":
        group_id = None
    elif group_id:
        group_id = int(group_id)
    
    # Check if user has access to this domain
    user_domain_ids = get_user_domain_ids(user_id, is_admin)
    if not is_admin and pk not in user_domain_ids:
        return jsonify({"success": False, "error": "Access denied"}), 403
    
    # If assigning to a group, check if user has access to that group
    if group_id and not is_admin:
        user_group_ids = get_user_group_ids(user_id, is_admin)
        if group_id not in user_group_ids:
            return jsonify({"success": False, "error": "You don't have access to this group"}), 403
    
    with get_connection() as conn:
        # Get next domain_index in the group
        domain_index = None
        if group_id:
            cur = db_execute(conn, "SELECT COALESCE(MAX(domain_index), -1) + 1 as next_idx FROM domains WHERE group_id = ?", (group_id,))
            row = dict_row(cur.fetchone())
            domain_index = row.get("next_idx") if row else 0
        
        db_execute(conn, "UPDATE domains SET group_id = ?, domain_index = ? WHERE id = ?", (group_id, domain_index, pk))
    
    return jsonify({"success": True})


@app.route("/api/domains/clear-all-groups", methods=["POST"])
@login_required
def api_domains_clear_all_groups():
    """Remove all domains from all groups (make them standalone)."""
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)
    
    # Get user's accessible domains
    user_domain_ids = get_user_domain_ids(user_id, is_admin)
    
    with get_connection() as conn:
        if is_admin:
            # Admin: clear all domains
            cur = db_execute(conn, "UPDATE domains SET group_id = NULL, domain_index = NULL")
            count = cur.rowcount
        elif user_domain_ids:
            # Regular user: clear only their domains
            placeholders = ",".join(["?"] * len(user_domain_ids))
            cur = db_execute(conn, f"UPDATE domains SET group_id = NULL, domain_index = NULL WHERE id IN ({placeholders})", tuple(user_domain_ids))
            count = cur.rowcount
        else:
            count = 0
    
    return jsonify({"success": True, "count": count})


@app.route("/api/domains/delete-all", methods=["POST"])
@login_required
def api_domains_delete_all():
    """Delete all domains and their content (admin deletes all, users delete their own)."""
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)

    # Get user's accessible domains
    user_domain_ids = get_user_domain_ids(user_id, is_admin)

    if not user_domain_ids and not is_admin:
        return jsonify({"success": False, "error": "No domains to delete"}), 400

    with get_connection() as conn:
        if is_admin:
            # Admin: delete ALL domains
            cur = db_execute(conn, "SELECT COUNT(*) as cnt FROM domains")
            domains_count = dict_row(cur.fetchone())["cnt"]

            # Delete in order to respect foreign keys
            db_execute(conn, "DELETE FROM titles")
            db_execute(conn, "DELETE FROM article_content")
            db_execute(conn, "DELETE FROM user_domains")
            db_execute(conn, "DELETE FROM domains")
        else:
            # Regular user: delete only their domains
            domains_count = len(user_domain_ids)
            placeholders = ",".join(["?"] * len(user_domain_ids))

            # Get title IDs for these domains
            cur = db_execute(conn, f"SELECT id FROM titles WHERE domain_id IN ({placeholders})", tuple(user_domain_ids))
            title_ids = [dict_row(r)["id"] for r in cur.fetchall()]

            if title_ids:
                title_placeholders = ",".join(["?"] * len(title_ids))
                # Delete article content for these titles
                db_execute(conn, f"DELETE FROM article_content WHERE title_id IN ({title_placeholders})", tuple(title_ids))
                # Delete titles
                db_execute(conn, f"DELETE FROM titles WHERE id IN ({title_placeholders})", tuple(title_ids))

            # Delete user_domains associations
            db_execute(conn, f"DELETE FROM user_domains WHERE user_id = ? AND domain_id IN ({placeholders})", (user_id,) + tuple(user_domain_ids))

            # Delete domains
            db_execute(conn, f"DELETE FROM domains WHERE id IN ({placeholders})", tuple(user_domain_ids))

    return jsonify({"success": True, "count": domains_count})


@app.route("/api/domains/delete-group/<int:group_id>", methods=["POST"])
@login_required
def api_domains_delete_group(group_id):
    """Delete all domains in a specific group (and subgroups)."""
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)

    # Check group access
    if not is_admin:
        user_group_ids = get_user_group_ids(user_id, is_admin)
        if group_id not in user_group_ids:
            return jsonify({"success": False, "error": "Access denied"}), 403

    with get_connection() as conn:
        # Get all descendant groups
        def get_all_descendants(gid):
            result = [gid]
            cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
            children = [dict_row(r)["id"] for r in cur.fetchall()]
            for child_id in children:
                result.extend(get_all_descendants(child_id))
            return result

        all_group_ids = get_all_descendants(group_id)
        placeholders = ",".join(["?"] * len(all_group_ids))

        # Get domains in these groups
        cur = db_execute(conn, f"SELECT id FROM domains WHERE group_id IN ({placeholders})", tuple(all_group_ids))
        domain_ids = [dict_row(r)["id"] for r in cur.fetchall()]

        if not domain_ids:
            return jsonify({"success": True, "count": 0, "message": "No domains found in this group"})

        # User has group access (passed 403 check above); delete all domains in the group (incl. subgroups)
        # Do NOT filter by user_domain_ids - group access implies permission to delete domains in that group
        domain_placeholders = ",".join(["?"] * len(domain_ids))

        # Get title IDs
        cur = db_execute(conn, f"SELECT id FROM titles WHERE domain_id IN ({domain_placeholders})", tuple(domain_ids))
        title_ids = [dict_row(r)["id"] for r in cur.fetchall()]

        if title_ids:
            title_placeholders = ",".join(["?"] * len(title_ids))
            # Delete article content
            db_execute(conn, f"DELETE FROM article_content WHERE title_id IN ({title_placeholders})", tuple(title_ids))
            # Delete titles
            db_execute(conn, f"DELETE FROM titles WHERE id IN ({title_placeholders})", tuple(title_ids))

        # Delete user_domains associations
        db_execute(conn, f"DELETE FROM user_domains WHERE domain_id IN ({domain_placeholders})", tuple(domain_ids))

        # Delete domain_templates and assignments (FK to domains)
        db_execute(conn, f"DELETE FROM domain_template_assignments WHERE domain_id IN ({domain_placeholders})", tuple(domain_ids))
        db_execute(conn, f"DELETE FROM domain_templates WHERE domain_id IN ({domain_placeholders})", tuple(domain_ids))

        # Delete domains
        db_execute(conn, f"DELETE FROM domains WHERE id IN ({domain_placeholders})", tuple(domain_ids))

    return jsonify({"success": True, "count": len(domain_ids)})


@app.route("/api/domains/clear-group/<int:group_id>", methods=["POST"])
@login_required
def api_domains_clear_group(group_id):
    """Remove all domains from a specific group."""
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)
    
    # Check if user has access to this group
    if not is_admin:
        user_group_ids = get_user_group_ids(user_id, is_admin)
        if group_id not in user_group_ids:
            return jsonify({"success": False, "error": "Access denied to this group"}), 403
    
    # Get user's accessible domains
    user_domain_ids = get_user_domain_ids(user_id, is_admin)
    
    with get_connection() as conn:
        if is_admin:
            # Admin: clear all domains in this group
            cur = db_execute(conn, "UPDATE domains SET group_id = NULL, domain_index = NULL WHERE group_id = ?", (group_id,))
            count = cur.rowcount
        elif user_domain_ids:
            # Regular user: clear only their domains in this group
            placeholders = ",".join(["?"] * len(user_domain_ids))
            cur = db_execute(conn, f"UPDATE domains SET group_id = NULL, domain_index = NULL WHERE group_id = ? AND id IN ({placeholders})", (group_id,) + tuple(user_domain_ids))
            count = cur.rowcount
        else:
            count = 0
    
    return jsonify({"success": True, "count": count})

@app.route("/api/domains/<int:pk>/categories", methods=["GET", "PUT"])
def api_domain_categories(pk):
    """GET: Return categories_list for domain. PUT: Update categories_list (body: {"categories": [...]})."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, categories_list FROM domains WHERE id = ?", (pk,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Domain not found"}), 404
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        raw = data.get("categories")
        if raw is None:
            return jsonify({"success": False, "error": "categories is required"}), 400
        # Accept list of strings or list of {id, categorie}
        out = []
        if isinstance(raw, list):
            for i, item in enumerate(raw):
                if isinstance(item, dict):
                    name = (item.get("categorie") or item.get("name") or item.get("category") or "").strip()
                    out.append({"id": int(item.get("id", i + 1)), "categorie": name or "Other"})
                else:
                    out.append({"id": i + 1, "categorie": (str(item) or "").strip() or "Other"})
        categories_json = json.dumps(out) if out else None
        with get_connection() as conn:
            db_execute(conn, "UPDATE domains SET categories_list = ? WHERE id = ?", (categories_json, pk))
        return jsonify({"success": True, "id": pk, "categories": out})
    raw = (row.get("categories_list") or "").strip()
    categories = []
    if raw:
        try:
            categories = json.loads(raw)
            if not isinstance(categories, list):
                categories = []
        except Exception:
            pass
    return jsonify({"id": pk, "categories": categories})


def _update_article_colors(conn, title_id, domain_colors, old_colors=None):
    """Update article CSS with new domain colors. Generators use both :root vars and direct hex
    (e.g. color: #6C8AE4). We replace ALL occurrences of each old hex with the new value.
    old_colors: previous domain_colors from DB (used when generators output direct hex, no :root)."""
    import re
    old_colors = old_colors or {}
    cur = db_execute(conn, "SELECT article_css FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
    row = cur.fetchone()
    if not row:
        return
    css = (dict_row(row).get("article_css") or "").strip()
    if not css:
        return
    
    # Map of CSS variable names to domain color keys
    color_map = {
        "--primary": "primary", "--secondary": "secondary", "--accent": "primary",
        "--background": "background", "--container-bg": "background",
        "--text-primary": "text_primary", "--text-secondary": "text_secondary",
        "--border": "border", "--button-print": "primary", "--button-pin": "button_pin",
        "--link": "primary", "--list-marker": "primary"
    }
    
    # Build old_hex -> (color_key, new_color) for replacement. Use placeholders to avoid collisions.
    placeholder_prefix = "__DOMAIN_COLOR_"
    replacements = []  # (old_hex, placeholder or new_color)
    
    # Source 1: old_colors from DB (works for direct hex in generators 2,4,6,7,8,9)
    for color_key, new_color in domain_colors.items():
        old_hex = old_colors.get(color_key)
        if old_hex and old_hex != new_color and re.match(r'^#[0-9a-fA-F]{3,6}$', old_hex):
            placeholder = placeholder_prefix + color_key.upper() + "__"
            replacements.append((old_hex, placeholder))
    
    # Source 2: extract from :root (for generators that use CSS variables)
    for css_var, color_key in color_map.items():
        if color_key not in domain_colors:
            continue
        new_color = domain_colors[color_key]
        for hex_pat in (r'#[0-9a-fA-F]{6}', r'#[0-9a-fA-F]{3}'):
            for m in re.finditer(rf'{re.escape(css_var)}\s*:\s*({hex_pat})\s*[;)]', css):
                old_hex = m.group(1)
                if old_hex != new_color and not any(r[0] == old_hex for r in replacements):
                    placeholder = placeholder_prefix + color_key.upper() + "__"
                    replacements.append((old_hex, placeholder))
    
    # Apply: replace old hex with placeholder (case-insensitive; CSS hex is case-insensitive)
    for old_hex, placeholder in replacements:
        css = re.sub(re.escape(old_hex), placeholder, css, flags=re.IGNORECASE)
    
    # Replace placeholders with new colors
    for color_key, new_color in domain_colors.items():
        placeholder = placeholder_prefix + color_key.upper() + "__"
        css = css.replace(placeholder, new_color)
    
    db_execute(conn, "UPDATE article_content SET article_css = ? WHERE title_id = ? AND language_code = 'en'", (css, title_id))


def _regenerate_domain_site_parts(domain_id, domain_colors):
    """Regenerate header, footer, sidebar, category templates with new colors to cache them."""
    # This ensures headers/footers are regenerated with new colors
    # Since they're generated on-the-fly, we just need to ensure the domain_colors are in the DB
    # The next request will automatically use the new colors from _get_domain_website_context
    # We can optionally pre-generate and warm the cache by making a test request
    try:
        base = (WEBSITE_PARTS_API_URL or "").rstrip("/")
        if not base:
            return 0
        
        with get_connection() as conn:
            cur = db_execute(conn, """SELECT header_template, footer_template, side_article_template, 
                category_page_template, writer_template, index_template, article_template_config, domain_fonts, categories_list FROM domains WHERE id = ?""", (domain_id,))
            row = dict_row(cur.fetchone())
            if not row:
                return 0
        
        # Build config with new colors and domain fonts
        config = {"colors": domain_colors, "domain_name": "Preview"}
        cfg_raw = (row.get("article_template_config") or "").strip()
        if cfg_raw:
            try:
                cfg = json.loads(cfg_raw) if isinstance(cfg_raw, str) else cfg_raw
                if isinstance(cfg, dict):
                    config.update(cfg)
                    config["colors"] = domain_colors  # Override with new colors
            except json.JSONDecodeError:
                pass
        df_raw = (row.get("domain_fonts") or "").strip()
        if df_raw:
            try:
                config["fonts"] = _domain_fonts_to_config(df_raw)
            except Exception:
                pass
        
        parts_regenerated = 0
        # Regenerate header
        h_tpl = (row.get("header_template") or "").strip()
        if h_tpl:
            try:
                _fetch_site_part_internal("header", h_tpl, config)
                parts_regenerated += 1
            except Exception:
                pass
        
        # Regenerate footer
        f_tpl = (row.get("footer_template") or "").strip()
        if f_tpl:
            try:
                _fetch_site_part_internal("footer", f_tpl, config)
                parts_regenerated += 1
            except Exception:
                pass
        
        # Regenerate sidebar
        s_tpl = (row.get("side_article_template") or "").strip()
        if s_tpl:
            try:
                _fetch_site_part_internal("sidebar", s_tpl, config)
                parts_regenerated += 1
            except Exception:
                pass
        
        # Regenerate category
        c_tpl = (row.get("category_page_template") or "").strip()
        if c_tpl:
            try:
                config["category_name"] = "Recipes"
                config["articles"] = []
                _fetch_site_part_internal("category", c_tpl, config)
                parts_regenerated += 1
            except Exception:
                pass
        
        # Regenerate writer template
        w_tpl = (row.get("writer_template") or "").strip()
        if w_tpl:
            try:
                config["writer"] = {"name": "Sample Writer", "title": "Food Blogger", "bio": "Sample bio", "avatar": ""}
                _fetch_site_part_internal("writer", w_tpl, config)
                parts_regenerated += 1
            except Exception:
                pass
        
        # Regenerate index template
        idx_tpl = (row.get("index_template") or "").strip()
        if idx_tpl:
            try:
                config["articles"] = []
                config["categories"] = []
                _fetch_site_part_internal("index", idx_tpl, config)
                parts_regenerated += 1
            except Exception:
                pass
        
        return parts_regenerated
    except Exception:
        return 0


@app.route("/api/domains/<int:pk>/articles-by-stat", methods=["GET"])
def api_domain_articles_by_stat(pk):
    """Return articles filtered by stat type (html_css, no_html_css, main_img, no_main_img, ing_img, no_ing_img)."""
    stat_type = request.args.get("type", "")
    if not stat_type:
        return jsonify({"error": "type parameter required"}), 400
    
    with get_connection() as conn:
        if stat_type == "html_css":
            cur = db_execute(conn, """SELECT t.id, t.title FROM titles t
                JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND TRIM(COALESCE(ac.article_html,'')) != '' AND TRIM(COALESCE(ac.article_css,'')) != ''
                ORDER BY t.id""", (pk,))
        elif stat_type == "no_html_css":
            cur = db_execute(conn, """SELECT t.id, t.title FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND (ac.id IS NULL OR TRIM(COALESCE(ac.article_html,'')) = '' OR TRIM(COALESCE(ac.article_css,'')) = '')
                ORDER BY t.id""", (pk,))
        elif stat_type == "main_img":
            cur = db_execute(conn, """SELECT t.id, t.title FROM titles t
                JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND ac.main_image IS NOT NULL AND TRIM(ac.main_image) LIKE 'http%'
                ORDER BY t.id""", (pk,))
        elif stat_type == "no_main_img":
            cur = db_execute(conn, """SELECT t.id, t.title FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND (ac.main_image IS NULL OR TRIM(COALESCE(ac.main_image,'')) NOT LIKE 'http%')
                ORDER BY t.id""", (pk,))
        elif stat_type == "ing_img":
            cur = db_execute(conn, """SELECT t.id, t.title FROM titles t
                JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND ac.ingredient_image IS NOT NULL AND TRIM(ac.ingredient_image) LIKE 'http%'
                ORDER BY t.id""", (pk,))
        elif stat_type == "no_ing_img":
            cur = db_execute(conn, """SELECT t.id, t.title FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND (ac.ingredient_image IS NULL OR TRIM(COALESCE(ac.ingredient_image,'')) NOT LIKE 'http%')
                ORDER BY t.id""", (pk,))
        else:
            return jsonify({"error": "Invalid type"}), 400
        
        articles = [{"id": dict_row(r).get("id"), "title": (dict_row(r).get("title") or "")[:80]} for r in cur.fetchall()]
    
    return jsonify({"articles": articles, "count": len(articles), "type": stat_type, "domain_id": pk})


@app.route("/api/domains/<int:pk>/article-count", methods=["GET"])
def api_domain_article_count(pk):
    """Return count and with_html (titles with generated HTML+CSS) for this domain."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT COUNT(*) AS n FROM titles WHERE domain_id = ?", (pk,))
        row = dict_row(cur.fetchone())
        n = (row.get('n', 0) if row else 0) or 0
        cur = db_execute(conn, """
            SELECT COUNT(*) AS n FROM article_content ac
            JOIN titles t ON t.id = ac.title_id AND t.domain_id = ?
            WHERE ac.language_code = 'en'
              AND TRIM(IFNULL(ac.article_html,'')) != '' AND TRIM(IFNULL(ac.article_css,'')) != ''
        """, (pk,))
        row = dict_row(cur.fetchone())
        with_html = (row.get('n', 0) if row else 0) or 0
    return jsonify({"count": n, "with_html": with_html})


@app.route("/api/domains/<int:pk>/website-template", methods=["PUT"])
def api_domain_website_template_put(pk):
    """Update website_template for a domain. Body: { website_template: string, clear_article_content: bool }.
    When clear_article_content is True, clears article_html and article_css for all article_content of titles in this domain."""
    data = request.get_json(silent=True) or {}
    template = (data.get("website_template") or "").strip() or None
    clear_content = data.get("clear_article_content") is True
    with get_connection() as conn:
        db_execute(conn, "UPDATE domains SET website_template = ? WHERE id = ?", (template, pk))
        if clear_content:
            db_execute(conn, """
                UPDATE article_content SET article_html = '', article_css = ''
                WHERE language_code = 'en' AND title_id IN (SELECT id FROM titles WHERE domain_id = ?)
            """, (pk,))
    return jsonify({"success": True, "website_template": template})


@app.route("/api/generate-color-palette", methods=["POST"])
@login_required
def api_generate_color_palette():
    """Use OpenAI to generate a matching color palette with guaranteed text contrast for recipe blogs."""
    user = get_current_user()
    user_config = get_user_config_for_api(user["id"])
    openai_key = user_config.get("openai_api_key")
    openrouter_key = user_config.get("openrouter_api_key")
    
    if not openai_key and not openrouter_key:
        return jsonify({"success": False, "error": "OpenAI or OpenRouter API key not configured in your profile"}), 500
    try:
        if openrouter_key:
            import openai
            client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)
            ai_model = user_config.get("openrouter_model") or "openai/gpt-4o-mini"
        else:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            ai_model = user_config.get("openai_model") or "gpt-4o-mini"
            
        prompt = """Generate a single harmonious color palette for a recipe/food blog. Return ONLY valid JSON, no markdown.

RULES (mandatory):
1. Keys: primary, secondary, background, text_primary, text_secondary, border
2. All values must be hex: #RRGGBB (e.g. #6C8AE4)
3. CONTRAST: text_primary and text_secondary must be readable on background. Light background (#fff, #f9f9f9, #f5f5f5) → dark text (#1a1a1a, #2D2D2D, #333). Dark background → light text (#fff, #f5f5f5). Never dark text on dark background.
4. primary: accent for links, buttons, headings. secondary: complementary. background: page bg. border: subtle border, slightly darker/lighter than background.
5. Colors must be harmonious (e.g. warm coral+cream, sage green, navy+gold, terracotta). Vary the theme each time.

Output format:
{"primary":"#hex","secondary":"#hex","background":"#hex","text_primary":"#hex","text_secondary":"#hex","border":"#hex"}"""
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=400,
        )
        content = (resp.choices[0].message.content or "").strip()
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        keys = ["primary", "secondary", "background", "text_primary", "text_secondary", "border"]
        palette = {}
        for k in keys:
            v = (data.get(k) or "").strip()
            if v and v.startswith("#") and len(v) == 7:
                palette[k] = v.upper()
            else:
                palette[k] = (dict(DEFAULT_DOMAIN_COLORS)).get(k, "#888888")
        return jsonify({"success": True, "colors": palette})
    except json.JSONDecodeError as e:
        return jsonify({"success": False, "error": f"Invalid palette JSON: {e}"}), 500
    except Exception as e:
        log.error(f"[generate-color-palette] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/domains/<int:pk>/colors", methods=["GET"])
def api_domain_colors_get(pk):
    """Return domain_colors JSON for a domain."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_colors FROM domains WHERE id = ?", (pk,))
        row = cur.fetchone()
    if not row:
        return jsonify({"error": "Domain not found"}), 404
    d = dict_row(row)
    raw = (d.get("domain_colors") or "").strip()
    colors = dict(DEFAULT_DOMAIN_COLORS)
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                for k, v in parsed.items():
                    if v:
                        colors[k] = str(v)
        except Exception:
            pass
    return jsonify({"success": True, "colors": colors})


@app.route("/api/domains/<int:pk>/colors", methods=["PUT"])
def api_domain_colors_put(pk):
    """Save domain_colors for a domain. Body: { colors: { primary, secondary, ... }, update_articles: bool }."""
    data = request.get_json(silent=True) or {}
    colors = data.get("colors")
    update_articles = data.get("update_articles", True)
    if not isinstance(colors, dict):
        return jsonify({"success": False, "error": "colors object required"}), 400
    merged = dict(DEFAULT_DOMAIN_COLORS)
    for k, v in colors.items():
        if v:
            merged[k] = str(v).strip()
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_colors FROM domains WHERE id = ?", (pk,))
        old_row = cur.fetchone()
        old_colors = {}
        if old_row:
            raw = (dict_row(old_row).get("domain_colors") or "").strip()
            if raw:
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        old_colors = {k: str(v) for k, v in parsed.items() if v}
                except (json.JSONDecodeError, TypeError):
                    pass
        db_execute(conn, "UPDATE domains SET domain_colors = ? WHERE id = ?", (json.dumps(merged), pk))
        # Sync article_template_config.colors so Article Editor and future generation use same palette
        cur = db_execute(conn, "SELECT article_template_config FROM domains WHERE id = ?", (pk,))
        row = cur.fetchone()
        if row:
            cfg_raw = (dict_row(row).get("article_template_config") or "").strip()
            if cfg_raw:
                try:
                    cfg = json.loads(cfg_raw) if isinstance(cfg_raw, str) else cfg_raw
                    if isinstance(cfg, dict):
                        cfg.setdefault("colors", {})
                        if isinstance(cfg.get("colors"), dict):
                            for k, v in merged.items():
                                if v:
                                    cfg["colors"][k] = v
                            db_execute(conn, "UPDATE domains SET article_template_config = ? WHERE id = ?", (json.dumps(cfg), pk))
                except (json.JSONDecodeError, TypeError):
                    pass
        articles_updated = 0
        if update_articles:
            cur = db_execute(conn, "SELECT t.id FROM titles t WHERE t.domain_id = ?", (pk,))
            title_ids = [dict_row(r).get("id") for r in cur.fetchall()]
            if title_ids:
                for tid in title_ids:
                    try:
                        _update_article_colors(conn, tid, merged, old_colors)
                        articles_updated += 1
                    except Exception:
                        pass
    
    # Regenerate site parts (header, footer, sidebar, category) with new colors
    parts_regenerated = _regenerate_domain_site_parts(pk, merged)
    
    return jsonify({
        "success": True,
        "articles_updated": articles_updated,
        "parts_regenerated": parts_regenerated,
        "note": "Headers, footers, sidebars, and category pages regenerated with new colors"
    })


@app.route("/api/domains/<int:pk>/fonts", methods=["GET"])
def api_domain_fonts_get(pk):
    """Return domain_fonts for a domain (heading_family, body_family, sizes, etc.)."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_fonts FROM domains WHERE id = ?", (pk,))
        row = cur.fetchone()
    if not row:
        return jsonify({"error": "Domain not found"}), 404
    d = dict_row(row)
    raw = (d.get("domain_fonts") or "").strip()
    fonts = dict(DEFAULT_DOMAIN_FONTS)
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                for k, v in parsed.items():
                    if v:
                        fonts[k] = str(v)
        except Exception:
            pass
    return jsonify({"success": True, "fonts": fonts})


@app.route("/api/domains/<int:pk>/fonts", methods=["PUT"])
def api_domain_fonts_put(pk):
    """Save domain_fonts. Body: { fonts: { heading_family, body_family, ... }, update_articles: bool }."""
    data = request.get_json(silent=True) or {}
    fonts_in = data.get("fonts")
    update_articles = data.get("update_articles", True)
    if not isinstance(fonts_in, dict):
        return jsonify({"success": False, "error": "fonts object required"}), 400
    merged = dict(DEFAULT_DOMAIN_FONTS)
    for k in list(DEFAULT_DOMAIN_FONTS.keys()):
        v = fonts_in.get(k)
        if v is not None and str(v).strip():
            merged[k] = str(v).strip()
    with get_connection() as conn:
        db_execute(conn, "UPDATE domains SET domain_fonts = ? WHERE id = ?", (json.dumps(merged), pk))
        # Sync article_template_config.fonts
        cur = db_execute(conn, "SELECT article_template_config FROM domains WHERE id = ?", (pk,))
        row = cur.fetchone()
        if row:
            cfg_raw = (dict_row(row).get("article_template_config") or "").strip()
            if cfg_raw:
                try:
                    cfg = json.loads(cfg_raw) if isinstance(cfg_raw, str) else cfg_raw
                    if isinstance(cfg, dict):
                        cfg["fonts"] = _domain_fonts_to_config(json.dumps(merged))
                        db_execute(conn, "UPDATE domains SET article_template_config = ? WHERE id = ?", (json.dumps(cfg), pk))
                except (json.JSONDecodeError, TypeError):
                    pass
    # Regenerate site parts with new fonts
    config = {"colors": dict(DEFAULT_DOMAIN_COLORS), "fonts": _domain_fonts_to_config(json.dumps(merged))}
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_colors FROM domains WHERE id = ?", (pk,))
        r = cur.fetchone()
        if r:
            dc_raw = (dict_row(r).get("domain_colors") or "").strip()
            if dc_raw:
                try:
                    dc = json.loads(dc_raw)
                    if isinstance(dc, dict):
                        config["colors"] = {k: v for k, v in dc.items() if v}
                except Exception:
                    pass
    _regenerate_domain_site_parts(pk, config.get("colors", {}))
    return jsonify({"success": True, "note": "Fonts saved; site parts regenerated"})


@app.route("/api/domains/<int:pk>/articles-list")
def api_domain_articles_list(pk):
    """Return paginated list of titles for domain. Params: validated=0|1|all (default 0), content=any|empty (default any). content=empty = no article_content row or empty article_html/article_css."""
    offset = max(0, int(request.args.get("offset", 0)))
    limit = min(100, max(1, int(request.args.get("limit", 30))))
    validated_filter = (request.args.get("validated") or "0").strip().lower()
    if validated_filter not in ("0", "1", "all"):
        validated_filter = "0"
    content_filter = (request.args.get("content") or "any").strip().lower()
    if content_filter not in ("any", "empty"):
        content_filter = "any"
    with get_connection() as conn:
        base_where = "t.domain_id = ?"
        validated_where = ""
        if validated_filter == "0":
            # Not validated: must have article_content with both html and css (exclude "not generated yet")
            validated_where = " AND ac.id IS NOT NULL AND TRIM(COALESCE(ac.article_html,'')) != '' AND TRIM(COALESCE(ac.article_css,'')) != '' AND COALESCE(ac.validated, 0) = 0"
        elif validated_filter == "1":
            validated_where = " AND ac.id IS NOT NULL AND COALESCE(ac.validated, 0) = 1"
        content_where = ""
        if content_filter == "empty":
            content_where = " AND (ac.id IS NULL OR TRIM(COALESCE(ac.article_html,'')) = '' OR TRIM(COALESCE(ac.article_css,'')) = '')"
        cur = db_execute(conn, """
            SELECT COUNT(*) AS total FROM titles t
            LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE """ + base_where + validated_where + content_where, (pk,))
        row = dict_row(cur.fetchone())
        total = (row.get("total") or 0) or 0
        cur = db_execute(conn, """
            SELECT t.id, t.title, t.domain_id, t.group_id, d.domain_index,
                   ac.generated_at, ac.model_used, COALESCE(ac.validated, 0) AS validated
            FROM titles t
            JOIN domains d ON t.domain_id = d.id
            LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE """ + base_where + validated_where + content_where + """
            ORDER BY t.id DESC LIMIT ? OFFSET ?
        """, (pk, limit, offset))
        rows = cur.fetchall()
    items = []
    for r in rows:
        row = dict_row(r)
        gid = row.get("group_id")
        title_text = (row.get("title") or "").strip()
        siblings = {}
        if gid is not None and title_text:
            with get_connection() as conn2:
                cur2 = db_execute(conn2, """
                    SELECT t.id, d.domain_index
                    FROM titles t
                    JOIN domains d ON t.domain_id = d.id
                    WHERE d.group_id = ? AND t.title = ? AND d.domain_index IN (0,1,2,3)
                    ORDER BY d.domain_index
                """, (gid, row.get("title") or ""))
                for r2 in cur2.fetchall():
                    d = dict_row(r2)
                    idx = d.get("domain_index")
                    if idx is not None and 0 <= idx < 4:
                        siblings["ABCD"[idx]] = d.get("id")
        gen_at = row.get("generated_at")
        is_validated = bool(row.get("validated"))
        items.append({
            "id": row.get("id"),
            "title": title_text,
            "generated_at": str(gen_at)[:19] if gen_at else None,
            "model_used": (row.get("model_used") or "").strip() or None,
            "domain_index": row.get("domain_index"),
            "validated": is_validated,
            "siblings": siblings,
        })
    return jsonify({"total": total, "items": items, "offset": offset, "limit": limit})


@app.route("/api/articles-list")
def api_articles_list():
    """Return paginated articles across all domains (or one domain). Params: offset, limit, validated=0|1|all (default 0), domain_id (optional). Each item includes domain_id, domain_url."""
    offset = max(0, int(request.args.get("offset", 0)))
    limit = min(100, max(1, int(request.args.get("limit", 30))))
    validated_filter = (request.args.get("validated") or "0").strip().lower()
    if validated_filter not in ("0", "1", "all"):
        validated_filter = "0"
    domain_id_param = request.args.get("domain_id", "").strip()
    domain_id = int(domain_id_param) if domain_id_param.isdigit() else None
    validated_where = ""
    if validated_filter == "0":
        validated_where = " AND (ac.id IS NULL OR COALESCE(ac.validated, 0) = 0)"
    elif validated_filter == "1":
        validated_where = " AND ac.id IS NOT NULL AND COALESCE(ac.validated, 0) = 1"
    with get_connection() as conn:
        if domain_id is not None:
            base_where = "t.domain_id = ?"
            params_count = (domain_id,)
            params_list = (domain_id, limit, offset)
        else:
            base_where = "1 = 1"
            params_count = ()
            params_list = (limit, offset)
        cur = db_execute(conn, """
            SELECT COUNT(*) AS total FROM titles t
            LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE """ + base_where + validated_where, params_count)
        row = dict_row(cur.fetchone())
        total = (row.get("total") or 0) or 0
        cur = db_execute(conn, """
            SELECT t.id, t.title, t.domain_id, t.group_id, d.domain_index, d.domain_url, d.domain_name, d.website_template,
                   ac.generated_at, ac.model_used, COALESCE(ac.validated, 0) AS validated
            FROM titles t
            JOIN domains d ON t.domain_id = d.id
            LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE """ + base_where + validated_where + """
            ORDER BY t.id DESC LIMIT ? OFFSET ?
        """, params_list)
        rows = cur.fetchall()
    items = []
    for r in rows:
        row = dict_row(r)
        gid = row.get("group_id")
        title_text = (row.get("title") or "").strip()
        siblings = {}
        if gid is not None and title_text:
            with get_connection() as conn2:
                cur2 = db_execute(conn2, """
                    SELECT t.id, d.domain_index
                    FROM titles t
                    JOIN domains d ON t.domain_id = d.id
                    WHERE d.group_id = ? AND t.title = ? AND d.domain_index IN (0,1,2,3)
                    ORDER BY d.domain_index
                """, (gid, row.get("title") or ""))
                for r2 in cur2.fetchall():
                    d = dict_row(r2)
                    idx = d.get("domain_index")
                    if idx is not None and 0 <= idx < 4:
                        siblings["ABCD"[idx]] = d.get("id")
        gen_at = row.get("generated_at")
        domain_url = (row.get("domain_url") or row.get("domain_name") or "").strip() or "—"
        generator = (row.get("website_template") or "").strip() or None
        items.append({
            "id": row.get("id"),
            "title": title_text,
            "generated_at": str(gen_at)[:19] if gen_at else None,
            "model_used": (row.get("model_used") or "").strip() or None,
            "domain_id": row.get("domain_id"),
            "domain_url": domain_url,
            "domain_index": row.get("domain_index"),
            "validated": bool(row.get("validated")),
            "siblings": siblings,
            "generator": generator,
        })
    return jsonify({"total": total, "items": items, "offset": offset, "limit": limit})


@app.route("/api/all-articles-test-content", methods=["POST"])
def api_all_articles_test_content():
    """Run content generation for the first article of each filtered domain, or specific title_ids. Body: {validated, domain_id, title_ids, async}."""
    req = request.get_json(silent=True) or {}
    validated_filter = str(req.get("validated", "0")).strip().lower()
    if validated_filter not in ("0", "1", "all"):
        validated_filter = "0"
    domain_id_raw = str(req.get("domain_id", "")).strip()
    domain_id = int(domain_id_raw) if domain_id_raw.isdigit() else None
    async_mode = str(req.get("async", "1")).lower() in ("1", "true", "yes")
    ai_provider = (req.get("ai_provider") or "").strip() or None
    openrouter_models = _parse_openrouter_models(req)
    local_model = (req.get("local_model") or "").strip() or None
    
    # Support retry via title_ids
    explicit_title_ids = req.get("title_ids") or []
    if not isinstance(explicit_title_ids, list):
        explicit_title_ids = []
    explicit_title_ids = [int(x) for x in explicit_title_ids if str(x).isdigit()]

    if not async_mode:
        return jsonify({"success": False, "error": "Only async mode supported"}), 400

    # If title_ids provided, use them directly (retry mode)
    if explicit_title_ids:
        title_ids = explicit_title_ids
        with get_connection() as conn:
            placeholders = ",".join("?" * len(title_ids))
            cur = db_execute(conn, f"SELECT DISTINCT domain_id FROM titles WHERE id IN ({placeholders})", title_ids)
            domain_ids = [r[0] for r in cur.fetchall()]
    else:
        # Otherwise, query first article per domain (test mode)
        validated_where = ""
        if validated_filter == "0":
            validated_where = " AND (ac.id IS NULL OR COALESCE(ac.validated, 0) = 0)"
        elif validated_filter == "1":
            validated_where = " AND ac.id IS NOT NULL AND COALESCE(ac.validated, 0) = 1"

        with get_connection() as conn:
            if domain_id is not None:
                base_where = "t.domain_id = ?"
                params = (domain_id,)
            else:
                base_where = "1 = 1"
                params = ()
            cur = db_execute(conn, """
                SELECT t.domain_id, MIN(t.id) AS title_id
                FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE """ + base_where + validated_where + """
                GROUP BY t.domain_id
                ORDER BY t.domain_id
            """, params)
            pairs = [dict_row(r) for r in cur.fetchall()]

        title_ids = [int(p.get("title_id")) for p in pairs if p and p.get("title_id")]
        domain_ids = [int(p.get("domain_id")) for p in pairs if p and p.get("domain_id")]
    
    if not title_ids:
        return jsonify({"success": False, "error": "No matching domains/articles found"}), 400

    job_id = str(uuid.uuid4())
    _bulk_progress[job_id] = {
        "status": "running",
        "message": f"Starting test for {len(title_ids)} domain(s)...",
        "current_title": "",
        "type": "test_content",
        "action": "Test content",
        "mode": "article",
        "domain_id": domain_id,
        "domain_ids": domain_ids,
        "total_rows": len(title_ids),
        "done": 0,
        "ok": 0,
        "failed": 0,
        "created_at": time.time(),
        "steps": [],
    }

    def task():
        ok, failed = 0, 0
        try:
            for idx, tid in enumerate(title_ids):
                if _bulk_cancel.get(job_id):
                    break
                with get_connection() as conn:
                    cur = db_execute(conn, """
                        SELECT t.title, t.domain_id, d.domain_url, d.domain_name
                        FROM titles t
                        LEFT JOIN domains d ON d.id = t.domain_id
                        WHERE t.id = ?
                    """, (tid,))
                    row = dict_row(cur.fetchone()) or {}
                ttitle = (row.get("title") or "")[:60]
                durl = (row.get("domain_url") or row.get("domain_name") or f"id {row.get('domain_id')}")
                _bulk_progress[job_id].update({
                    "message": f"Testing {idx + 1}/{len(title_ids)}",
                    "current_title": f"[{durl}] {ttitle}",
                    "done": idx,
                })
                try:
                    _do_generate_article_external(tid, ai_provider=ai_provider, openrouter_models=openrouter_models, local_model=local_model)
                    ok += 1
                    _bulk_progress[job_id].get("steps", []).append(f"R{idx+1}: [{tid}] {ttitle} ✓")
                except Exception as e:
                    failed += 1
                    _bulk_progress[job_id].get("steps", []).append(f"R{idx+1}: [{tid}] {ttitle} ✗ | {str(e)[:80]}")
            if _bulk_cancel.get(job_id):
                _bulk_progress[job_id].update({
                    "status": "cancelled",
                    "message": f"Cancelled. {ok} done" + (f", {failed} failed" if failed else ""),
                    "ok": ok,
                    "failed": failed,
                    "done": ok + failed,
                })
            else:
                _bulk_progress[job_id].update({
                    "status": "done",
                    "message": f"Test finished: {ok} done" + (f", {failed} failed" if failed else ""),
                    "ok": ok,
                    "failed": failed,
                    "done": ok + failed,
                })
        except Exception as e:
            _bulk_progress[job_id].update({"status": "error", "message": str(e), "ok": ok, "failed": failed})

    threading.Thread(target=task, daemon=True).start()
    return jsonify({"success": True, "job_id": job_id, "count": len(title_ids), "domain_ids": domain_ids})


@app.route("/api/domains/<int:pk>/stats-articles")
def api_domain_stats_articles(pk):
    """Return articles for domain filtered by type: html_css, no_html_css, main_img, no_main_img, ing_img, no_ing_img. Includes actions_html and group_id for Run UI."""
    stype = (request.args.get("type") or "").strip() or "html_css"
    if stype not in ("html_css", "no_html_css", "main_img", "no_main_img", "ing_img", "no_ing_img"):
        stype = "html_css"
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT group_id, domain_index FROM domains WHERE id = ?", (pk,))
        dom_row = dict_row(cur.fetchone())
    group_id = dom_row.get("group_id") if dom_row else None
    domain_index = dom_row.get("domain_index") if dom_row is not None else 0
    if domain_index is None or domain_index not in (0, 1, 2, 3):
        domain_index = 0
    ac_map = {}
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT title_id, recipe, article_html, article_css, main_image, ingredient_image, pin_image FROM article_content WHERE language_code = 'en'")
        for r in cur.fetchall():
            row = dict_row(r)
            rid = row.get("title_id")
            recipe_ok = bool((row.get("recipe") or "").strip())
            article_html_ok = bool((row.get("article_html") or "").strip())
            article_css_ok = bool((row.get("article_css") or "").strip())
            main_img = (row.get("main_image") or "").strip()
            ing_img = (row.get("ingredient_image") or "").strip()
            pin_img = (row.get("pin_image") or "").strip()
            ac_map[rid] = {
                "has_all": recipe_ok and article_html_ok and article_css_ok,
                "main_image": main_img,
                "ingredient_image": ing_img,
                "pin_image": pin_img,
            }
    with get_connection() as conn:
        if stype == "html_css":
            cur = db_execute(conn, """SELECT t.id AS title_id, t.title, ac.main_image, ac.ingredient_image, 1 AS has_val
                FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND ac.id IS NOT NULL AND TRIM(COALESCE(ac.article_html,'')) != '' AND TRIM(COALESCE(ac.article_css,'')) != ''
                ORDER BY t.id DESC""", (pk,))
        elif stype == "no_html_css":
            cur = db_execute(conn, """SELECT t.id AS title_id, t.title, ac.main_image, ac.ingredient_image, 0 AS has_val
                FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND (ac.id IS NULL OR TRIM(COALESCE(ac.article_html,'')) = '' OR TRIM(COALESCE(ac.article_css,'')) = '')
                ORDER BY t.id DESC""", (pk,))
        elif stype == "main_img":
            cur = db_execute(conn, """SELECT t.id AS title_id, t.title, ac.main_image, ac.ingredient_image, 1 AS has_val
                FROM titles t
                JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND ac.main_image IS NOT NULL AND TRIM(ac.main_image) LIKE 'http%%'
                ORDER BY t.id DESC""", (pk,))
        elif stype == "no_main_img":
            cur = db_execute(conn, """SELECT t.id AS title_id, t.title, ac.main_image, ac.ingredient_image, 0 AS has_val
                FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND (ac.id IS NULL OR ac.main_image IS NULL OR TRIM(ac.main_image) NOT LIKE 'http%%')
                ORDER BY t.id DESC""", (pk,))
        elif stype == "ing_img":
            cur = db_execute(conn, """SELECT t.id AS title_id, t.title, ac.main_image, ac.ingredient_image, 1 AS has_val
                FROM titles t
                JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND ac.ingredient_image IS NOT NULL AND TRIM(ac.ingredient_image) LIKE 'http%%'
                ORDER BY t.id DESC""", (pk,))
        else:  # no_ing_img
            cur = db_execute(conn, """SELECT t.id AS title_id, t.title, ac.main_image, ac.ingredient_image, 0 AS has_val
                FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ? AND (ac.id IS NULL OR ac.ingredient_image IS NULL OR TRIM(ac.ingredient_image) NOT LIKE 'http%%')
                ORDER BY t.id DESC""", (pk,))
        rows = cur.fetchall()
    articles = []
    for r in rows or []:
        ro = dict_row(r)
        title_id = ro.get("title_id")
        title_text = (ro.get("title") or "")[:100]
        ids = [None, None, None, None]
        title_a_id = None
        if group_id is not None:
            with get_connection() as conn2:
                cur2 = db_execute(conn2, """SELECT t.id, d.domain_index FROM titles t
                    JOIN domains d ON t.domain_id = d.id
                    WHERE t.group_id = ? AND t.title = ? AND d.domain_index IN (0,1,2,3)
                    ORDER BY d.domain_index""", (group_id, ro.get("title")))
                for r2 in cur2.fetchall():
                    r2d = dict_row(r2)
                    idx = r2d.get("domain_index")
                    if idx is not None and 0 <= idx < 4:
                        ids[idx] = r2d.get("id")
                if ids[0]:
                    title_a_id = ids[0]
        if not ids[0]:
            ids[0] = title_id if domain_index == 0 else None
            if domain_index == 0:
                title_a_id = title_id
            elif title_id:
                ids[domain_index] = title_id
        actions_html = _render_article_run_actions_html(ids, domain_index, ac_map, title_a_id, in_group=(group_id is not None))
        articles.append({
            "title_id": title_id,
            "title": title_text,
            "main_image": (ro.get("main_image") or "").strip(),
            "ingredient_image": (ro.get("ingredient_image") or "").strip(),
            "actions_html": actions_html,
            "title_a_id": title_a_id,
        })
    labels = {
        "html_css": "Articles with HTML+CSS",
        "no_html_css": "Articles without HTML+CSS",
        "main_img": "Articles with main image",
        "no_main_img": "Articles without main image",
        "ing_img": "Articles with ingredient image",
        "no_ing_img": "Articles without ingredient image",
    }
    # Include counts for filter toggles (with_count, without_count)
    with_count = without_count = 0
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT
            SUM(CASE WHEN ac.id IS NOT NULL AND TRIM(COALESCE(ac.article_html,'')) != '' AND TRIM(COALESCE(ac.article_css,'')) != '' THEN 1 ELSE 0 END) AS html_css,
            SUM(CASE WHEN ac.main_image IS NOT NULL AND TRIM(ac.main_image) LIKE 'http%%' THEN 1 ELSE 0 END) AS main_img,
            SUM(CASE WHEN ac.ingredient_image IS NOT NULL AND TRIM(ac.ingredient_image) LIKE 'http%%' THEN 1 ELSE 0 END) AS ing_img,
            COUNT(DISTINCT t.id) AS total
            FROM titles t
            LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ?""", (pk,))
        row = dict_row(cur.fetchone())
        total = row.get("total") or 0
        html_css_n = row.get("html_css") or 0
        main_img_n = row.get("main_img") or 0
        ing_img_n = row.get("ing_img") or 0
    counts = {
        "html_css": {"with": html_css_n, "without": total - html_css_n},
        "main_img": {"with": main_img_n, "without": total - main_img_n},
        "ing_img": {"with": ing_img_n, "without": total - ing_img_n},
    }
    return jsonify({
        "success": True,
        "articles": articles,
        "type": stype,
        "label": labels.get(stype, stype),
        "group_id": group_id,
        "counts": counts,
    })


@app.route("/api/domains/<int:pk>/writers", methods=["GET"])
def api_domain_writers_get(pk):
    """Return writers JSON for a domain."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT writers FROM domains WHERE id = ?", (pk,))
        row = cur.fetchone()
    if not row:
        return jsonify({"error": "Domain not found"}), 404
    d = dict_row(row)
    raw = (d.get("writers") or "").strip()
    writers = []
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                writers = parsed
        except Exception:
            pass
    return jsonify({"success": True, "writers": writers})


@app.route("/api/domains/<int:pk>/writers", methods=["PUT"])
def api_domain_writers_put(pk):
    """Save writers for a domain. Body: { writers: [ {name, title, bio, avatar}, ... ] }."""
    data = request.get_json(silent=True) or {}
    writers = data.get("writers")
    if not isinstance(writers, list):
        return jsonify({"success": False, "error": "writers array required"}), 400
    with get_connection() as conn:
        db_execute(conn, "UPDATE domains SET writers = ? WHERE id = ?", (json.dumps(writers), pk))
    return jsonify({"success": True})


@app.route("/api/domains/<int:pk>/writers/generate", methods=["POST"])
@login_required
def api_domain_writers_generate(pk):
    """Auto-generate 4 writers with AI-generated avatars via ONE Midjourney job (4 images from grid)."""
    try:
        user = get_current_user()
        user_id = user["id"]
        user_config = get_user_config_for_api(user_id)
        api_key = user_config.get("openai_api_key")
        model = user_config.get("openai_model") or OPENAI_MODEL
        base_url = None
        if not api_key and user_config.get("openrouter_api_key"):
            api_key = user_config.get("openrouter_api_key")
            model = user_config.get("openrouter_model") or "openai/gpt-4o-mini"
            base_url = "https://openrouter.ai/api/v1"
        if not api_key:
            return jsonify({"success": False, "error": "No OpenAI or OpenRouter API key configured. Add one in your profile."}), 400

        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_url, domain_name FROM domains WHERE id = ?", (pk,))
            row = cur.fetchone()
            if not row:
                return jsonify({"success": False, "error": "Domain not found"}), 404
            domain_name = dict_row(row).get("domain_url") or dict_row(row).get("domain_name") or "Food Blog"
        
        log.info(f"[generate-writers] Starting generation for domain {pk} ({domain_name})")
        
        # Generate 4 writers using OpenAI/OpenRouter (user's keys from DB)
        log.info(f"[generate-writers] Generating writer profiles with AI...")
        writers = _generate_writers_with_ai(domain_name, api_key=api_key, model=model, base_url=base_url)
        log.info(f"[generate-writers] Generated {len(writers)} writers: {[w['name'] for w in writers]}")
        
        # Generate ONE Midjourney job with 4 avatars (2x2 grid)
        log.info(f"[generate-writers] Generating 4 avatars with ONE Midjourney job...")
        avatar_urls = _generate_writer_avatars_batch(writers)
        
        # Assign avatars to writers
        for i, writer in enumerate(writers):
            if i < len(avatar_urls):
                writer["avatar"] = avatar_urls[i]
                log.info(f"[generate-writers] Avatar {i+1}/4 assigned: {avatar_urls[i]}")
            else:
                writer["avatar"] = ""
        
        # Save writers to database
        with get_connection() as conn:
            db_execute(conn, "UPDATE domains SET writers = ? WHERE id = ?", (json.dumps(writers), pk))
        
        log.info(f"[generate-writers] Completed! {len(avatar_urls)}/4 avatars generated successfully")
        return jsonify({"success": True, "writers": writers, "avatars_generated": len(avatar_urls)})
    except Exception as e:
        log.error(f"[generate-writers] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/domains/<int:pk>/writers/distribute", methods=["POST"])
def api_domain_writers_distribute(pk):
    """Randomly distribute domain's 4 writers to all existing articles by re-injecting writer HTML."""
    try:
        with get_connection() as conn:
            # Get domain info
            cur = db_execute(conn, "SELECT writer_template, writers, domain_colors, article_template_config FROM domains WHERE id = ?", (pk,))
            row = cur.fetchone()
            if not row:
                return jsonify({"success": False, "error": "Domain not found"}), 404
            dom = dict_row(row)
            
            writer_tpl = (dom.get("writer_template") or "").strip()
            
            writers_raw = (dom.get("writers") or "").strip()
            if not writers_raw:
                return jsonify({"success": False, "error": "Domain has no writers. Generate writers first."}), 400
            
            writers = json.loads(writers_raw)
            if not isinstance(writers, list) or len(writers) == 0:
                return jsonify({"success": False, "error": "Invalid writers data"}), 400
            
            # Get all articles for this domain
            cur = db_execute(conn, "SELECT t.id FROM titles t WHERE t.domain_id = ?", (pk,))
            title_ids = [dict_row(r).get("id") for r in cur.fetchall()]
            
            if not title_ids:
                return jsonify({"success": False, "error": "No articles found for this domain"}), 400
            
            log.info(f"[distribute-writers] Distributing writers to {len(title_ids)} articles in domain {pk}")
            
            # Prepare domain colors config
            dc_raw = (dom.get("domain_colors") or "").strip()
            colors = dict(DEFAULT_DOMAIN_COLORS)
            if dc_raw:
                try:
                    dc = json.loads(dc_raw)
                    if isinstance(dc, dict):
                        colors = dc
                except:
                    pass
            
            # Distribute writers randomly to articles
            import random
            updated = 0
            for title_id in title_ids:
                try:
                    # Pick random writer
                    writer = random.choice(writers)
                    
                    # Save writer data to article (preview-website will handle rendering)
                    writer_json = json.dumps(writer)
                    writer_avatar = writer.get("avatar", "")
                    db_execute(conn, "UPDATE article_content SET writer = ?, writer_avatar = ? WHERE title_id = ? AND language_code = 'en'",
                             (writer_json, writer_avatar, title_id))
                    updated += 1
                    log.info(f"[distribute-writers] Assigned writer '{writer.get('name')}' to article {title_id}")
                    
                except Exception as e:
                    log.error(f"[distribute-writers] Failed to update article {title_id}: {e}")
                    continue
            
            log.info(f"[distribute-writers] Updated {updated}/{len(title_ids)} articles")
            return jsonify({"success": True, "updated": updated, "total": len(title_ids)})
            
    except Exception as e:
        log.error(f"[distribute-writers] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/debug/article/<int:title_id>")
def api_debug_article(title_id):
    """Debug endpoint to check article HTML structure."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT article_html, writer, writer_avatar FROM article_content WHERE title_id = ? LIMIT 1", (title_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Article not found"}), 404
    
    html = row.get("article_html") or ""
    return jsonify({
        "title_id": title_id,
        "html_length": len(html),
        "has_writer_data": bool(row.get("writer")),
        "writer_avatar": row.get("writer_avatar"),
        "counts": {
            "Latest Recipes": html.count("Latest Recipes"),
            "Popular Recipes": html.count("Popular Recipes"),
            "side-article-card": html.count("side-article-card"),
            "aside_tags": html.count("<aside"),
            "sidebar-area": html.count("sidebar-area"),
            "article-writer": html.count("article-writer"),
            "writer-card": html.count("writer-card"),
        },
        "first_1000_chars": html[:1000]
    })


@app.route("/api/domains/<int:pk>/writers/cleanup", methods=["POST"])
def api_domain_writers_cleanup(pk):
    """Remove any embedded writer HTML from article_html and article_css columns."""
    try:
        with get_connection() as conn:
            # Get all articles for this domain
            cur = db_execute(conn, """
                SELECT t.id FROM titles t 
                WHERE t.domain_id = ?
            """, (pk,))
            title_ids = [r["id"] for r in cur.fetchall()]
            
            if not title_ids:
                return jsonify({"success": True, "updated": 0, "total": 0})
            
            updated = 0
            for title_id in title_ids:
                try:
                    cur = db_execute(conn, "SELECT article_html, article_css FROM article_content WHERE title_id = ? AND language_code = 'en'", (title_id,))
                    ac_row = dict_row(cur.fetchone())
                    if not ac_row:
                        continue
                    
                    article_html = ac_row.get("article_html") or ""
                    article_css = ac_row.get("article_css") or ""
                    
                    if not article_html:
                        continue
                    
                    # Remove any embedded writer HTML (old format)
                    original_html = article_html
                    original_css = article_css
                    
                    # Remove writer divs with various class names
                    article_html = re.sub(r'<div[^>]*class="[^"]*article-writer[^"]*"[^>]*>.*?</div>\s*', '', article_html, flags=re.DOTALL | re.IGNORECASE)
                    article_html = re.sub(r'<div[^>]*class="[^"]*writer-card[^"]*"[^>]*>.*?</div>\s*', '', article_html, flags=re.DOTALL | re.IGNORECASE)
                    article_html = re.sub(r'<div[^>]*class="[^"]*writer-byline[^"]*"[^>]*>.*?</div>\s*', '', article_html, flags=re.DOTALL | re.IGNORECASE)
                    
                    # Remove writer CSS comments and styles
                    article_css = re.sub(r'/\*\s*Writer Byline\s*\*/.*?(?=/\*|$)', '', article_css, flags=re.DOTALL)
                    article_css = re.sub(r'\.article-writer\s*\{[^}]*\}', '', article_css, flags=re.DOTALL)
                    article_css = re.sub(r'\.writer-card\s*\{[^}]*\}', '', article_css, flags=re.DOTALL)
                    
                    # Only update if something changed
                    if article_html != original_html or article_css != original_css:
                        db_execute(conn, "UPDATE article_content SET article_html = ?, article_css = ? WHERE title_id = ? AND language_code = 'en'",
                                 (article_html, article_css, title_id))
                        updated += 1
                        log.info(f"[cleanup-writers] Cleaned embedded writer HTML from article {title_id}")
                    
                except Exception as e:
                    log.error(f"[cleanup-writers] Failed to clean article {title_id}: {e}")
                    continue
            
            log.info(f"[cleanup-writers] Cleaned {updated}/{len(title_ids)} articles")
            return jsonify({"success": True, "updated": updated, "total": len(title_ids)})
            
    except Exception as e:
        log.error(f"[cleanup-writers] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/domains/<int:domain_id>/generate-page/<slug>", methods=["POST"])
def api_domains_generate_page(domain_id, slug):
    """Generate or regenerate a single domain page. Uses template-based generation (instant, no AI cost) or AI via OpenRouter."""
    if slug not in DOMAIN_PAGE_SLUGS:
        return jsonify({"success": False, "error": "Invalid page slug"}), 400
    col = PAGE_SLUG_TO_COLUMN.get(slug)
    if not col:
        return jsonify({"success": False, "error": "Page not configured"}), 400
    data = request.get_json(silent=True) or {}
    theme = (data.get("theme") or data.get("template") or "ai").strip()
    
    user = get_current_user()
    user_id = user["id"] if user else 1
    
    try:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_url, domain_name, writers, domain_colors, domain_fonts, categories_list FROM domains WHERE id = ?", (domain_id,))
            row = dict_row(cur.fetchone())
        if not row:
            return jsonify({"success": False, "error": "Domain not found"}), 404
        domain_name = row.get("domain_url") or row.get("domain_name") or ""
        writers = []
        raw = (row.get("writers") or "").strip()
        if raw:
            try:
                parsed = json.loads(raw)
                writers = parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                pass

        if theme != "ai":
            out = _generate_domain_page_with_theme(domain_id, slug, theme, row, domain_name, writers)
        else:
            design_styles = [
                "warm coral and cream, light backgrounds, soft gradients",
                "minimal light theme with accent gold, white/cream backgrounds",
                "botanical green and sage, light card backgrounds",
                "earthy terracotta and sand, cream content areas",
                "elegant navy and cream, white cards for team section",
                "cozy amber and warm gray, light backgrounds for readability",
                "fresh mint and soft lavender, white or #f9f9f9 cards",
                "bold burgundy accents on cream/white, high contrast text",
            ]
            import random
            design_seed = random.choice(design_styles)
            log.info(f"[domain-pages] AI generating {slug} for domain {domain_id} ({domain_name}), design: {design_seed}")
            out = _generate_single_domain_page_with_openai(domain_name, slug, design_seed, writers=writers if slug == "about-us" else None, user_id=user_id)

        stored = json.dumps({"main_html": out["main_html"], "main_css": out.get("main_css", ""), "theme": theme})
        with get_connection() as conn:
            db_execute(conn, f"UPDATE domains SET {col} = ? WHERE id = ?", (stored, domain_id))
        return jsonify({"success": True, "slug": slug, "theme": theme})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        log.error(f"[domain-pages] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/domains/<int:domain_id>/visual-customizations", methods=["GET", "POST"])
def api_domain_visual_customizations(domain_id):
    """GET: Return visual customizations. POST: Add/update customization with scope (page/domain/template)."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT visual_customizations, website_template FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Domain not found"}), 404
    
    if request.method == "GET":
        page_url = request.args.get("page_url", "")
        raw = (row.get("visual_customizations") or "").strip()
        customizations = []
        if raw:
            try:
                customizations = json.loads(raw) if isinstance(raw, str) else raw
            except json.JSONDecodeError:
                pass
        # Filter by page_url if scope=page
        if page_url:
            customizations = [c for c in customizations if c.get("scope") != "page" or c.get("pageUrl") == page_url]
        return jsonify({"customizations": customizations if isinstance(customizations, list) else []})
    
    # POST: Add customization with scope
    data = request.get_json(silent=True) or {}
    selector = (data.get("selector") or "").strip()
    styles = (data.get("styles") or "").strip()
    text_override = data.get("textOverride")
    insert_after = (data.get("insertAfter") or "").strip()
    scope = (data.get("scope") or "domain").strip()
    page_url = (data.get("pageUrl") or "").strip()
    
    if not selector:
        return jsonify({"success": False, "error": "selector required"}), 400
    
    if scope not in ("page", "domain", "template"):
        scope = "domain"
    
    affected_domains = 1
    
    if scope == "template":
        # Apply to all domains with same website_template
        template = row.get("website_template")
        if not template:
            return jsonify({"success": False, "error": "Domain has no template set"}), 400
        
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id, visual_customizations FROM domains WHERE website_template = ?", (template,))
            target_domains = [dict_row(r) for r in cur.fetchall()]
        
        affected_domains = len(target_domains)
        
        for td in target_domains:
            did = td["id"]
            raw = (td.get("visual_customizations") or "").strip()
            customizations = []
            if raw:
                try:
                    customizations = json.loads(raw) if isinstance(raw, str) else raw
                except json.JSONDecodeError:
                    pass
            if not isinstance(customizations, list):
                customizations = []
            
            # Remove old customizations with same selector and scope=template
            customizations = [c for c in customizations if not (c.get("selector") == selector and c.get("scope") == "template")]
            
            new_custom = {"selector": selector, "scope": "template"}
            if styles:
                new_custom["styles"] = styles
            if text_override is not None:
                new_custom["textOverride"] = text_override
            if insert_after:
                new_custom["insertAfter"] = insert_after
            customizations.append(new_custom)
            
            with get_connection() as conn:
                db_execute(conn, "UPDATE domains SET visual_customizations = ? WHERE id = ?", (json.dumps(customizations), did))
    
    else:
        # scope = page or domain
        raw = (row.get("visual_customizations") or "").strip()
        customizations = []
        if raw:
            try:
                customizations = json.loads(raw) if isinstance(raw, str) else raw
            except json.JSONDecodeError:
                pass
        if not isinstance(customizations, list):
            customizations = []
        
        # Remove old customizations with same selector and scope (and pageUrl if scope=page)
        if scope == "page":
            customizations = [c for c in customizations if not (c.get("selector") == selector and c.get("scope") == "page" and c.get("pageUrl") == page_url)]
        else:
            customizations = [c for c in customizations if not (c.get("selector") == selector and c.get("scope") in ("domain", None))]
        
        new_custom = {"selector": selector, "scope": scope}
        if scope == "page":
            new_custom["pageUrl"] = page_url
        if styles:
            new_custom["styles"] = styles
        if text_override is not None:
            new_custom["textOverride"] = text_override
        if insert_after:
            new_custom["insertAfter"] = insert_after
        customizations.append(new_custom)
        
        with get_connection() as conn:
            db_execute(conn, "UPDATE domains SET visual_customizations = ? WHERE id = ?", (json.dumps(customizations), domain_id))
    
    return jsonify({"success": True, "message": "Customization saved", "affected_domains": affected_domains})


@app.route("/api/domains/<int:domain_id>/page-theme", methods=["PUT"])
def api_domain_set_page_theme(domain_id):
    """Save page theme for a domain. Updates the 'theme' key in all existing page JSON columns.
    If no page columns have data yet, writes a minimal {'theme': theme} to domain_page_about_us so the preference is persisted."""
    data = request.get_json(silent=True) or {}
    theme = (data.get("theme") or "").strip()
    if not theme:
        return jsonify({"success": False, "error": "No theme specified"}), 400
    try:
        page_columns = list(PAGE_SLUG_TO_COLUMN.values())
        with get_connection() as conn:
            cur = db_execute(conn, f"SELECT id, {', '.join(page_columns)} FROM domains WHERE id = ?", (domain_id,))
            row = dict_row(cur.fetchone())
        if not row:
            return jsonify({"success": False, "error": "Domain not found"}), 404
        updated_cols = 0
        with get_connection() as conn:
            for col in page_columns:
                raw = (row.get(col) or "").strip()
                if not raw:
                    continue
                try:
                    j = json.loads(raw)
                    if isinstance(j, dict):
                        j["theme"] = theme
                        db_execute(conn, f"UPDATE domains SET {col} = ? WHERE id = ?", (json.dumps(j), domain_id))
                        updated_cols += 1
                except (json.JSONDecodeError, AttributeError):
                    pass
            # If no columns had data, persist theme in domain_page_about_us so it's stored and _get_domain_page_theme finds it
            if updated_cols == 0:
                placeholder = {"theme": theme}
                db_execute(conn, "UPDATE domains SET domain_page_about_us = ? WHERE id = ?",
                           (json.dumps(placeholder), domain_id))
                updated_cols = 1
        log.info(f"[page-theme] domain {domain_id} theme set to '{theme}', updated {updated_cols} page columns")
        return jsonify({"success": True, "theme": theme, "updated": updated_cols})
    except Exception as e:
        log.error(f"[page-theme] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


def _get_available_page_themes():
    """Fetch available page themes from website-parts-generator API. Auto-detected when themes are added/removed there."""
    base = (WEBSITE_PARTS_API_URL or "").rstrip("/")
    if base:
        try:
            req = urllib.request.Request(f"{base}/domain-page-themes", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            themes = (data.get("themes") or []) if isinstance(data, dict) else []
            if themes:
                return themes
        except Exception as e:
            log.debug("[page-themes] API fetch failed: %s", e)
    return [t[0] for t in DOMAIN_PAGE_THEMES_FALLBACK]  # Fallback only when API unavailable


@app.route("/api/domain-page-themes", methods=["GET"])
def api_domain_page_themes():
    """Return available domain page themes. Fetches from website-parts-generator."""
    themes = _get_available_page_themes()
    return jsonify({"themes": themes})


def _generate_domain_page_with_theme(domain_id, slug, theme, row, domain_name, writers):
    """Generate a domain page using a theme folder via website-parts-generator API. Returns {main_html, main_css}."""
    base = (WEBSITE_PARTS_API_URL or "").rstrip("/")
    if not base:
        raise ValueError("WEBSITE_PARTS_API_URL not set. Start website-parts-generator on port 8010.")

    colors = {}
    dc_raw = (row.get("domain_colors") or "").strip()
    if dc_raw:
        try:
            colors = json.loads(dc_raw)
        except json.JSONDecodeError:
            pass

    categories = []
    cl_raw = (row.get("categories_list") or "").strip()
    if cl_raw:
        try:
            cl = json.loads(cl_raw)
            if isinstance(cl, list):
                base_url = f"/preview-website/{domain_id}"
                for c in cl:
                    if isinstance(c, dict):
                        cname = c.get("name") or c.get("categorie") or ""
                        if cname:
                            cslug = cname.lower().replace(" ", "-")
                            categories.append({"name": cname, "url": f"{base_url}/category/{cslug}", "slug": cslug})
        except json.JSONDecodeError:
            pass

    df_raw = (row.get("domain_fonts") or "").strip()
    fonts = _domain_fonts_to_config(df_raw)

    if not isinstance(colors, dict):
        colors = {}
    if not isinstance(writers, list):
        writers = []
    if not isinstance(categories, list):
        categories = []

    config = {
        "domain_name": _domain_url_to_display_name(domain_name),
        "base_url": f"/preview-website/{domain_id}",
        "domain_url": domain_name or "",
        "colors": colors,
        "fonts": fonts,
        "writers": writers,
        "categories": categories,
        "page_slug": slug,
        "page_title": DOMAIN_PAGE_TITLE_MAP.get(slug, slug.replace("-", " ").title()),
    }

    url = f"{base}/generate/domain_page/{theme}/{slug}"
    log.info(f"[domain-pages] POST {url}")
    try:
        preflight = urllib.request.Request(f"{base}/domain-page-themes", method="GET")
        try:
            with urllib.request.urlopen(preflight, timeout=5) as _:
                pass
        except urllib.error.HTTPError as pre:
            if pre.code == 404:
                raise ValueError(
                    f"Domain page themes API not found at {base}. "
                    "Ensure website-parts-generator is the latest code and restarted (uvicorn route:app --port 8010). "
                    f"Test: curl {base}/domain-page-themes"
                )
        body = json.dumps(config, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json; charset=utf-8"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        if not result.get("success"):
            msg = result.get("detail") or result.get("error") or "Template generation failed"
            if isinstance(msg, list):
                msg = msg[0] if msg else "Template generation failed"
            elif isinstance(msg, dict):
                msg = msg.get("msg", str(msg))
            raise ValueError(msg)
        return {"main_html": result.get("html", ""), "main_css": result.get("css", "")}
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = (e.fp.read() if e.fp else b"").decode()
        except Exception:
            err_body = str(e)
        try:
            err_data = json.loads(err_body)
            msg = err_data.get("detail", err_body)
            if isinstance(msg, list) and msg:
                msg = msg[0].get("msg", str(msg[0])) if isinstance(msg[0], dict) else str(msg[0])
            elif isinstance(msg, dict):
                msg = msg.get("msg", str(msg))
        except Exception:
            msg = err_body
        log.warning(f"[domain-pages] Template API HTTP {e.code}: {msg[:500]}")
        hint = " Restart website-parts-generator (uvicorn route:app --port 8010) so it loads the domain_page route." if e.code == 404 else ""
        raise ValueError(f"Template API (HTTP {e.code}): {str(msg)[:350]}{hint}")


def _generate_writers_with_ai(domain_name: str, api_key: str = None, model: str = None, base_url: str = None) -> list:
    """Use OpenAI/OpenRouter to generate 4 writer profiles. Uses api_key/model from args, else env defaults."""
    import openai
    key = api_key or OPENAI_API_KEY
    ai_model = model or OPENAI_MODEL
    if not key:
        raise ValueError("No OpenAI API key. Add it in your profile or set OPENAI_API_KEY in .env")
    client = openai.OpenAI(api_key=key, base_url=base_url) if base_url else openai.OpenAI(api_key=key)
    
    prompt = f"""Generate 4 writer profiles for a food blog called "{domain_name}". 
Each writer should have:
- A realistic first name (diverse backgrounds)
- A professional title/role (e.g., "Owner & Founder", "Recipe Developer", "Food Photographer", "Culinary Expert", "Home Cook & Blogger")
- A warm, engaging 2-3 sentence bio that reflects their personality and expertise

Return ONLY valid JSON array format:
[
  {{"name": "Emma", "title": "Owner & Founder", "bio": "Emma is the founder of {domain_name} and the home cook behind its cozy, family friendly recipes. She loves turning simple ingredients into comforting meals anyone can make."}},
  {{"name": "...", "title": "...", "bio": "..."}},
  {{"name": "...", "title": "...", "bio": "..."}},
  {{"name": "...", "title": "...", "bio": "..."}}
]"""
    
    response = client.chat.completions.create(
        model=ai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1000
    )
    
    content = response.choices[0].message.content.strip()
    # Extract JSON from markdown code blocks if present
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    writers = json.loads(content)
    if not isinstance(writers, list) or len(writers) != 4:
        raise ValueError("AI did not return 4 writers")
    
    return writers


def _generate_writer_avatars_batch(writers: list) -> list:
    """Generate 4 avatars from ONE Midjourney job (2x2 grid) and upload to Cloudflare R2.
    Returns list of 4 avatar URLs. Uses same approach as generate_4_images for main/ingredient images."""
    
    # Determine the gender/type for all 4 avatars based on first writer
    # If first writer sounds male, make all 4 male names. Otherwise diverse.
    first_name = writers[0].get("name", "").lower()
    male_names = ["james", "michael", "david", "john", "robert", "william", "richard", "thomas", "charles", "daniel", "matthew", "mark", "paul", "steven", "andrew"]
    
    is_male_group = any(mn in first_name for mn in male_names)
    
    if is_male_group:
        gender = "man"
        descriptor = "male"
    else:
        gender = "person"
        descriptor = "diverse"
    
    # Create ONE Midjourney prompt for 4 avatars with CENTERED FACES
    prompt = f"professional headshot portrait of {gender} food blogger, face perfectly centered in frame, warm friendly smile, soft studio lighting, neutral blurred background, professional photography, high quality --ar 1:1 --v 6.1"
    
    log.info(f"[generate-writer-avatars] Generating 4 {descriptor} avatars with ONE Midjourney job")
    log.info(f"[generate-writer-avatars] Prompt: {prompt}")
    
    # Use the same generate_4_images function as main_image and ingredient_image
    urls, err = imagine.generate_4_images(prompt, key_prefix="writer_avatars")
    
    if err:
        log.error(f"[generate-writer-avatars] Failed: {err}")
        raise RuntimeError(f"Avatar generation failed: {err}")
    
    if len(urls) != 4:
        log.error(f"[generate-writer-avatars] Expected 4 avatars, got {len(urls)}")
        raise RuntimeError(f"Expected 4 avatars, got {len(urls)}")
    
    log.info(f"[generate-writer-avatars] Successfully generated 4 avatars: {urls}")
    return urls


# UI/UX requirements for all generated pages
UI_UX_REQUIREMENTS = """
OUTPUT FORMAT (required): Reply with nothing else. Start with the line ---HTML--- then your full <main class="domain-page ...">...</main>, then the line ---CSS--- then only raw CSS (no <style> or </style>), then ---END---. No markdown, no ``` code fences.
CSS: raw CSS only—no <style>, </style>, or HTML.
UI/UX: body 1rem min, line-height 1.6; h1 2rem+, h2 1.5rem+, h3 1.25rem+; padding 2rem; max-width 720–900px centered. Dark bg → light text; light bg → dark text. border-radius 8–12px, subtle shadow. Responsive.
"""


# Per-page prompts: each page type has its own dedicated prompt
def _get_page_prompt(slug: str, domain: str, design: str, writers_json: str = "") -> str:
    prompts = {
        "about-us": f"""Create a professional, well-designed About Us page for "{domain}" (a recipe/food blog). Follow the MomdishMagic-style structure.

MANDATORY STRUCTURE:
1. Hero: greeting ("Nice to meet you!"), h1 "About {domain}", short intro paragraph (warm welcome, passion for cooking, recipes that bring joy)
2. Meet the Chef / Author section: featured card for primary writer. Use Avatar URL if given, else placeholder div with initials. Label "Meet the Chef", h2 with name, subtitle (title), bio. If 2–4 writers: add "Contributors & Recipe Creators" section with cards (photo, name, role, bio, "View Recipes →" link)
3. Story content with h2 and <hr /> between major sections:
   - "About [primary founder]" — first-person intro, mission (help readers feel confident in the kitchen), personal touches
   - "What You'll Find on {domain}" — bullet list (weeknight dinners, desserts, appetizers, drinks), mention categories
   - "My Recipe Philosophy" — self-taught home cook, approachable; bullet list: simple ingredients, clear instructions, comforting flavors, tips
   - "My Journey in the Kitchen" — personal story (family meals, grandmother's cookies), how the blog grew; bullet list of what readers get
   - "For Every Kind of Home Cook" — bullet list: beginners, stuck in a rut, experienced cooks; "you're welcome here"
   - "Connect with Me" — bullet list: Get New Recipes, Follow on Social Media, Say Hello (contact link)
4. CTA section: "Let's cook together!", h2 "Start Your Culinary Journey", buttons: Browse Recipes, Contact Us

MEET THE TEAM CARDS – READABILITY (mandatory): Use EITHER (a) light card background (#fff, #f9f9f9) with dark text (#1a1a1a, #333), OR (b) dark card with WHITE text. Never dark text on dark background.

WRITERS (use this data):
{writers_json}

{UI_UX_REQUIREMENTS}

Design: {design}. Output ONLY the blocks below. CSS block must contain ONLY CSS (no <style>, </style>, or HTML tags).
---HTML---
<main class="domain-page domain-page-about-us">...</main>
---CSS---
...scoped CSS...
---END---""",
        "terms-of-use": f"""Create a professional Terms of Use page for "{domain}" (recipe/food blog). Follow MomdishMagic-style: Hero "Legal Information" + h1 "Terms Of Use"; content section with h2 "Terms of Use", <p><strong>Last Updated:</strong> [current date]</p>, then h3 sections: Agreement to Terms, Use License (ul: no modify/copy, no commercial use, no decompile/reverse engineer, no remove copyright, no transfer/mirror), User Content, Prohibited Uses (ul), Intellectual Property, Disclaimer (materials "as is"), Limitations, Modifications, Contact Information (email link). Use {domain} in body text. Max-width ~900px.

{UI_UX_REQUIREMENTS}

Design: {design}. Output ONLY the blocks below.
---HTML---
<main class="domain-page domain-page-terms-of-use">...</main>
---CSS---
...
---END---""",
        "privacy-policy": f"""Create a professional Privacy Policy for "{domain}" (recipe/food blog). MomdishMagic-style: Hero "Legal Information" + h1 "Privacy Policy"; h2 "Privacy Policy", Last Updated; h3: Introduction; Information We Collect (ul: Identity Data, Contact Data, Technical Data, Usage Data); How We Use Your Information (ul); Cookies; Data Security; Your Rights (ul: access, correction, erasure, object, restrict, portability, withdraw consent); Contact Us. Use {domain} in body. Max-width ~900px.

{UI_UX_REQUIREMENTS}

Design: {design}. Output ONLY the blocks below.
---HTML---
<main class="domain-page domain-page-privacy-policy">...</main>
---CSS---
...
---END---""",
        "gdpr-policy": f"""Create a GDPR Policy for "{domain}" (recipe/food blog). MomdishMagic-style: Hero "Legal Information" + h1 "GDPR Policy"; h2 "GDPR Policy", Last Updated; h3: Introduction (GDPR in EU law); Legal Basis for Processing (ul: Consent, Contract, Legal obligation, Legitimate interests); Data Protection Rights (ul: access, rectification, erasure, restrict, object, portability); Data Retention; International Transfers; Contact Our Data Protection Officer. Use {domain} in body. Max-width ~900px.

{UI_UX_REQUIREMENTS}

Design: {design}. Output ONLY the blocks below.
---HTML---
<main class="domain-page domain-page-gdpr-policy">...</main>
---CSS---
...
---END---""",
        "cookie-policy": f"""Create a Cookie Policy for "{domain}" (recipe/food blog). MomdishMagic-style: Hero "Legal Information" + h1 "Cookie Policy"; h2 "Cookie Policy", Last Updated; h3: What Are Cookies; How We Use Cookies (ul: Essential, Performance, Functionality, Targeting); Types of Cookies — h4 Strictly Necessary, Performance and Analytics, Functionality, Targeting and Advertising; Third-Party Cookies; Managing Cookies — h4 Browser Controls (ul: Chrome, Firefox, Safari, Edge); Cookie Retention (Session, Persistent); Updates; Contact Us. Use {domain} in body. Max-width ~900px.

{UI_UX_REQUIREMENTS}

Design: {design}. Output ONLY the blocks below.
---HTML---
<main class="domain-page domain-page-cookie-policy">...</main>
---CSS---
...
---END---""",
        "copyright-policy": f"""Create a Copyright Policy for "{domain}" (recipe/food blog). MomdishMagic-style: Hero "Legal Information" + h1 "Copyright Policy"; h2 "Copyright Policy", Last Updated; h3: Copyright Ownership; Recipe Content (expression, photos protected); User-Generated Content (license grant); Permitted Use (ul); Prohibited Use (ul); DMCA Compliance (ul with notice requirements); Copyright Infringement Notifications; Attribution Requirements; Image Rights; Contact Information. Use {domain} in body. Max-width ~900px.

{UI_UX_REQUIREMENTS}

Design: {design}. Output ONLY the blocks below.
---HTML---
<main class="domain-page domain-page-copyright-policy">...</main>
---CSS---
...
---END---""",
        "disclaimer": f"""Create a Disclaimer for "{domain}" (recipe/food blog). MomdishMagic-style: Hero "Legal Information" + h1 "Disclaimer"; h2 "Disclaimer", Last Updated; h3: General Disclaimer; Recipe Accuracy (ul: ovens, ingredients, altitude, experience); Dietary and Nutritional Information; h4 Allergen Warning (ul); Health and Medical Disclaimer; External Links; Professional Disclaimer; Results Disclaimer; Food Safety (ul); Errors and Omissions; Assumption of Risk; Liability Limitation; Changes to Disclaimer. End with Contact (email). Use {domain} in body. Max-width ~900px.

{UI_UX_REQUIREMENTS}

Design: {design}. Output ONLY the blocks below.
---HTML---
<main class="domain-page domain-page-disclaimer">...</main>
---CSS---
...
---END---""",
        "contact-us": f"""Create a Contact Us page for "{domain}" (recipe/food blog). MomdishMagic-style: Hero greeting "We'd love to hear from you!", h1 "Get in Touch", short subtitle. Two-column layout: (1) Form section "Send a Message" — form with name, email, subject, message (label, input, textarea), submit button "Send Message"; (2) Sidebar: "Quick Contact" — General, Recipe Questions, Business (each with email link); "Follow Us" social; "Response Time" (e.g. 2-3 business days). Optional: "All Contact Options" section with cards — General Inquiries, Recipe Questions, Business Inquiries, Technical Support, Legal Matters, Media & Press (icon, title, description, email link). Use proper form markup. Contact emails: use placeholder or #. Use {domain} in text.

{UI_UX_REQUIREMENTS}

Design: {design}. Output ONLY the blocks below.
---HTML---
<main class="domain-page domain-page-contact-us">...</main>
---CSS---
...
---END---""",
    }
    return prompts.get(slug, "")


# OpenRouter model for domain page generation (default: Claude 3 Haiku — good quality, low cost; override via DOMAIN_PAGE_MODEL in .env)
# Alternatives: openai/gpt-3.5-turbo, openai/gpt-3.5-turbo-16k, google/palm-2-chat-bison, meta-llama/llama-2-70b-chat
DOMAIN_PAGE_MODEL = os.environ.get("DOMAIN_PAGE_MODEL", "anthropic/claude-3-haiku")


def _generate_single_domain_page_with_openai(domain_name: str, slug: str, design_seed: str, writers=None, user_id=None) -> dict:
    """Generate one domain page with OpenAI/OpenRouter."""
    user_config = get_user_config_for_api(user_id) if user_id else {}
    
    openrouter_key = user_config.get("openrouter_api_key")
    openai_key = user_config.get("openai_api_key")
    
    if openrouter_key:
        import openai
        client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)
        ai_model = user_config.get("openrouter_model") or DOMAIN_PAGE_MODEL
        log.info(f"[domain-pages] {slug}: using OpenRouter + {ai_model}")
    elif openai_key:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        ai_model = user_config.get("openai_model") or DOMAIN_PAGE_MODEL
    else:
        raise ValueError("No API key configured for OpenAI or OpenRouter")
        
    domain_clean = _domain_url_to_display_name(domain_name)
    writers_list = writers if isinstance(writers, list) else []
    writers_json = "No writers configured. Create one founder with a plausible name, title (e.g. Owner & Founder), and 2-sentence bio."
    if writers_list:
        parts = []
        for w in writers_list[:4]:
            name = (w.get("name") or "Unknown").strip()
            title = (w.get("title") or "").strip()
            bio = (w.get("bio") or "").strip()
            avatar = (w.get("avatar") or "").strip()
            line = f"- Name: {name} | Title: {title} | Bio: {bio}"
            if avatar and str(avatar).startswith("http"):
                line += f" | Avatar URL: {avatar}"
            parts.append(line)
        writers_json = "\n".join(parts) if parts else writers_json
    prompt = _get_page_prompt(slug, domain_clean, design_seed, writers_json=writers_json)
    if not prompt:
        raise ValueError(f"No prompt for {slug}")
    resp = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are an expert web designer. Create clean, professional HTML and CSS. Follow the user's structure exactly. You MUST output in this exact format: first the line ---HTML--- then the full <main class=\"domain-page ...\">...</main> block, then the line ---CSS--- then only raw CSS (no <style> tags), then ---END---. No markdown, no code fences, no extra text before or after."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=6000,
    )
    content = (resp.choices[0].message.content or "").strip()
    main_html = ""
    main_css = ""
    if "---HTML---" in content and "---CSS---" in content:
        parts = content.split("---HTML---", 1)[1].split("---CSS---", 1)
        main_html = (parts[0] or "").strip()
        main_css = (parts[1] or "").split("---END---")[0].strip()
    elif "<main" in content:
        idx = content.find("<main")
        end = content.find("</main>") + 7 if "</main>" in content else len(content)
        main_html = content[idx:end] if end > idx else content[idx:]
        if "```" in content:
            css_idx = content.find("```css") if "```css" in content else content.find("```")
            if css_idx >= 0:
                css_end = content.find("```", css_idx + 5) if css_idx >= 0 else -1
                if css_end > css_idx:
                    main_css = content[css_idx:css_end].replace("```css", "").replace("```", "").strip()
        if not main_css:
            main_css = ".domain-page { max-width: 880px; margin: 0 auto; padding: 2rem; line-height: 1.7; font-size: 1rem; }"
    for tag in ("```html", "```",):
        if main_html.startswith(tag):
            main_html = main_html[len(tag):].strip()
    if main_html.endswith("```"):
        main_html = main_html[:-3].strip()
    if not main_html:
        raise ValueError(f"Empty output for {slug}")
    return {"main_html": main_html, "main_css": main_css or ""}


# --- Domain templates API (for Pin Editor) ---
PLACEHOLDER_IMAGE_URL = "https://placehold.co/600x1067/1a1a1a/888?text=Pin"


def _generate_domain_template_preview(template_json_str: str, domain_colors: dict = None) -> str:
    """Generate preview image for template JSON via Pin API (screenshot + Cloudflare R2); return image URL or None on failure.
    domain_colors: optional dict with primary, secondary, etc. - Pin API will style the pin to match the domain."""
    import base64
    import re
    try:
        filled = template_json_str
        for key in ("main_image", "top_image", "bottom_image", "title", "badge", "subtitle", "website", "time_badge", "avatar_image"):
            filled = filled.replace("{{" + key + "}}", PLACEHOLDER_IMAGE_URL if "image" in key or key == "avatar_image" else "Preview")
        filled = re.sub(r"\{\{[^}]+\}\}", "Preview", filled)
        body = json.loads(filled)
        template_name = (body.get("template_name") or body.get("template_id") or "template_1").strip().lower().replace("-", "_")
        payload = body.get("template_data") if "template_data" in body else body
        if not isinstance(payload, dict):
            payload = {}
        payload["variables"] = {"title": "Preview"}
        if domain_colors and isinstance(domain_colors, dict):
            payload["domain_colors"] = domain_colors
        pin_base = (PIN_API_URL or "http://localhost:5000").rstrip("/")
        api_url = f"{pin_base}/generate?name={template_name}"
        r = requests_lib.post(api_url, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()
        if not data.get("success"):
            return None
        image_url = data.get("image_url")
        if image_url and str(image_url).startswith("http"):
            return image_url
        screenshot_b64 = data.get("screenshot_base64")
        if screenshot_b64 and isinstance(screenshot_b64, str) and screenshot_b64.startswith("data:image/png;base64,"):
            try:
                b64 = screenshot_b64.split(",", 1)[-1]
                png_bytes = base64.b64decode(b64)
                if png_bytes and len(png_bytes) >= 100:
                    import r2_upload
                    user = get_current_user()
                    user_config = get_user_config_for_api(user["id"]) if user else {}
                    return r2_upload.upload_bytes_to_r2(png_bytes, "template_preview", "image/png", user_config=user_config)
            except Exception:
                pass
    except Exception:
        pass
    return None


@app.route("/api/domain-templates", methods=["GET"])
def api_domain_templates_list():
    """List templates for a domain. Query: domain_id."""
    domain_id = request.args.get("domain_id")
    if not domain_id:
        return jsonify({"error": "domain_id required"}), 400
    domain_id = int(domain_id)
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, domain_id, name, template_json, sort_order, preview_image_url, created_at FROM domain_templates WHERE domain_id = ? ORDER BY sort_order, id", (domain_id,))
        rows = [dict_row(r) for r in cur.fetchall()]
    return jsonify({"templates": [{"id": r["id"], "name": r["name"], "sort_order": r.get("sort_order") or 0, "preview_image_url": r.get("preview_image_url") or "", "created_at": r.get("created_at")} for r in rows]})


@app.route("/api/domain-templates", methods=["POST"])
def api_domain_templates_create():
    """Create a template. Body: domain_id, name, template_json."""
    data = request.get_json(silent=True) or request.form or {}
    domain_id = data.get("domain_id")
    name = (data.get("name") or "").strip() or "Unnamed"
    template_json = data.get("template_json")
    if template_json is None and "template_json" in request.form:
        template_json = request.form.get("template_json")
    if domain_id is None:
        return jsonify({"success": False, "error": "domain_id required"}), 400
    domain_id = int(domain_id)
    if template_json is None:
        return jsonify({"success": False, "error": "template_json required"}), 400
    if isinstance(template_json, dict):
        template_json = json.dumps(template_json)
    template_json = (template_json or "").strip()
    if not template_json:
        return jsonify({"success": False, "error": "template_json required"}), 400
    try:
        json.loads(template_json)
    except json.JSONDecodeError as e:
        return jsonify({"success": False, "error": "Invalid JSON: " + str(e)}), 400
    with get_connection() as conn:
        cur = db_execute(conn, "INSERT INTO domain_templates (domain_id, name, template_json, sort_order) VALUES (?, ?, ?, 0)", (domain_id, name, template_json))
        tid = last_insert_id(cur)
    if not tid:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id FROM domain_templates WHERE domain_id = ? ORDER BY id DESC LIMIT 1", (domain_id,))
            row = cur.fetchone()
            tid = dict_row(row).get("id") if row else None
    preview_url = _generate_domain_template_preview(template_json)
    if preview_url and tid:
        with get_connection() as conn:
            db_execute(conn, "UPDATE domain_templates SET preview_image_url = ? WHERE id = ?", (preview_url, tid))
    return jsonify({"success": True, "id": tid, "message": "Template added", "preview_image_url": preview_url or ""})


@app.route("/api/domain-templates/<int:pk>", methods=["GET"])
def api_domain_templates_get(pk):
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, domain_id, name, template_json, sort_order FROM domain_templates WHERE id = ?", (pk,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"id": row["id"], "domain_id": row["domain_id"], "name": row["name"], "template_json": row["template_json"], "sort_order": row.get("sort_order") or 0})


@app.route("/api/domain-templates/<int:pk>", methods=["PUT", "DELETE"])
def api_domain_templates_update_delete(pk):
    if request.method == "DELETE":
        with get_connection() as conn:
            db_execute(conn, "DELETE FROM domain_templates WHERE id = ?", (pk,))
        return jsonify({"success": True, "message": "Deleted"})
    data = request.get_json(silent=True) or request.form or {}
    name = (data.get("name") or "").strip()
    template_json = data.get("template_json")
    if template_json is not None and isinstance(template_json, dict):
        template_json = json.dumps(template_json)
    if template_json is not None:
        template_json = (template_json or "").strip()
        try:
            json.loads(template_json)
        except json.JSONDecodeError:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400
    with get_connection() as conn:
        if name:
            db_execute(conn, "UPDATE domain_templates SET name = ? WHERE id = ?", (name, pk))
        if template_json is not None:
            db_execute(conn, "UPDATE domain_templates SET template_json = ? WHERE id = ?", (template_json, pk))
    if template_json is not None:
        preview_url = _generate_domain_template_preview(template_json)
        if preview_url:
            with get_connection() as conn:
                db_execute(conn, "UPDATE domain_templates SET preview_image_url = ? WHERE id = ?", (preview_url, pk))
    return jsonify({"success": True, "message": "Updated"})


# --- Admin: Article Templates ---
@app.route("/admin/article-templates")
def admin_article_templates():
    """List article templates (generators) and create new ones."""
    generators = []
    try:
        base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
        if base:
            req = urllib.request.Request(f"{base}/generators", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                generators = data.get("generators", [])
    except Exception:
        pass
    if not generators:
        generators = _list_article_generator_files()
    rows = "".join(
        f'<tr><td><code>{html.escape(g)}</code></td>'
        f'<td><a href="/article-editor?generator={html.escape(g)}" target="_blank" class="btn btn-sm btn-outline-primary">Edit design</a></td></tr>'
        for g in generators
    )
    base_opts = "".join(f'<option value="{html.escape(g)}">{g}</option>' for g in generators)
    content = f"""
    <h2>Article Templates</h2>
    <p class="text-muted">Manage article generators. Each template has its own design (colors, fonts, layout) and structure.</p>
    <table class="table table-bordered mb-4"><thead><tr><th>Generator</th><th>Actions</th></tr></thead><tbody>{rows}</tbody></table>
    <div class="card">
      <div class="card-header">Create new generator</div>
      <div class="card-body">
        <p class="text-muted">Creates a new <code>generator-N.py</code> with a new design. The articles-website-generator API will auto-discover it (restart the API if needed).</p>
        <form id="createGeneratorForm" class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Copy from (base template)</label>
            <select name="base_generator" class="form-select" required>{base_opts}</select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Primary color (hex)</label>
            <input type="text" name="primary_color" class="form-control" placeholder="#6C8AE4" value="#6C8AE4">
          </div>
          <div class="col-md-3">
            <label class="form-label">Display name</label>
            <input type="text" name="display_name" class="form-control" placeholder="My New Design">
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button type="submit" class="btn btn-primary">Create</button>
          </div>
        </form>
        <div id="createResult" class="mt-2"></div>
      </div>
    </div>
    <script>
    document.getElementById('createGeneratorForm').addEventListener('submit', function(e) {{
      e.preventDefault();
      var fd = new FormData(this);
      var result = document.getElementById('createResult');
      result.innerHTML = '<span class="text-muted">Creating...</span>';
      fetch('/api/article-generator-create', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
          base_generator: fd.get('base_generator'),
          primary_color: fd.get('primary_color') || null,
          display_name: fd.get('display_name') || null
        }})
      }})
      .then(r => r.json())
      .then(d => {{
        if (d.success) {{
          result.innerHTML = '<span class="text-success">Created ' + d.generator + '. Restart articles-website-generator API to use it.</span>';
          setTimeout(function() {{ location.reload(); }}, 1500);
        }} else {{
          result.innerHTML = '<span class="text-danger">' + (d.error || 'Failed') + '</span>';
        }}
      }})
      .catch(err => {{ result.innerHTML = '<span class="text-danger">' + err + '</span>'; }});
    }});
    </script>
    """
    return base_layout(content, "Article Templates")


# --- Admin: Domains ---
def _build_group_filter_alert(group_hierarchy_path, domain_count):
    """Build the group filter alert HTML (extracted to avoid f-string backslash issues)."""
    if not group_hierarchy_path:
        return ""
    path_str = " > ".join(bc['name'] for bc in group_hierarchy_path)
    close_onclick = 'window.location.href="/admin/domains"'
    return f"<div class='alert alert-info alert-dismissible'><strong>Filtered by group:</strong> {path_str} <span class='badge bg-primary'>{domain_count} domain(s)</span> <button type='button' class='btn-close' onclick='{close_onclick}'></button></div>"


@app.route("/admin/domains")
@login_required
def admin_domains():
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)
    
    # Support filtering by group_id (including all subgroups recursively)
    filter_group_id = request.args.get("group_id")
    filter_group_id = int(filter_group_id) if filter_group_id and str(filter_group_id).isdigit() else None
    
    # Get user's accessible domain IDs
    user_domain_ids = get_user_domain_ids(user_id, is_admin)
    
    # If no group selected, show group selector page
    if not filter_group_id:
        with get_connection() as conn:
            user_group_ids = get_user_group_ids(user_id, is_admin)
            if not is_admin:
                if user_group_ids:
                    placeholders = ",".join(["?"] * len(user_group_ids))
                    cur = db_execute(conn, f"SELECT id, name, parent_group_id FROM `groups` WHERE id IN ({placeholders}) ORDER BY name", tuple(user_group_ids))
                else:
                    cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` WHERE 1=0")
            else:
                cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` ORDER BY name")
            all_groups = [dict_row(r) for r in cur.fetchall()]
            
            # Build hierarchy for display
            def build_hierarchy(gid, groups_list):
                path = []
                current = gid
                visited = set()
                while current and current not in visited:
                    visited.add(current)
                    g = next((x for x in groups_list if x["id"] == current), None)
                    if g:
                        path.insert(0, g["name"])
                        current = g.get("parent_group_id")
                    else:
                        break
                return " → ".join(path) if path else "-"
            
            # Get top-level parent (grandparent) for each group
            def get_top_parent(gid, groups_list):
                current = gid
                visited = set()
                while current and current not in visited:
                    visited.add(current)
                    g = next((x for x in groups_list if x["id"] == current), None)
                    if g and g.get("parent_group_id"):
                        current = g["parent_group_id"]
                    else:
                        return current
                return gid
            
            # Filter to show only top-level parent groups
            top_parent_ids = set()
            for g in all_groups:
                top_parent_id = get_top_parent(g["id"], all_groups)
                top_parent_ids.add(top_parent_id)
            
            # Keep only groups that are top-level parents
            all_groups = [g for g in all_groups if g["id"] in top_parent_ids]
            
            for g in all_groups:
                g["hierarchy"] = build_hierarchy(g["id"], all_groups)
            
            # Get all descendant groups
            def get_descendants(gid):
                result = [gid]
                cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
                children = [dict_row(r)["id"] for r in cur.fetchall()]
                for child_id in children:
                    result.extend(get_descendants(child_id))
                return result

            # Get user assignments for top-level groups if admin
            group_users_map = {}
            if is_admin:
                for g in all_groups:
                    descendants = get_descendants(g["id"])
                    if descendants:
                        placeholders = ",".join(["?"] * len(descendants))
                        cur = db_execute(conn, f"""
                            SELECT DISTINCT u.username 
                            FROM user_groups ug 
                            JOIN users u ON ug.user_id = u.id 
                            WHERE ug.group_id IN ({placeholders})
                        """, tuple(descendants))
                        users = [dict_row(r)["username"] for r in cur.fetchall()]
                        group_users_map[g["id"]] = users

            # Get statistics for each group (domains and articles)
            for g in all_groups:
                group_ids = get_descendants(g["id"])
                placeholders = ",".join(["?"] * len(group_ids))
                
                # Get domain count and article stats
                cur = db_execute(conn, f"""
                    SELECT 
                        COUNT(DISTINCT d.id) as domain_count,
                        COUNT(DISTINCT t.id) as total_articles,
                        SUM(CASE WHEN ac.article_html IS NOT NULL AND TRIM(ac.article_html) != '' THEN 1 ELSE 0 END) as articles_with_html
                    FROM domains d
                    LEFT JOIN titles t ON t.domain_id = d.id
                    LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                    WHERE d.group_id IN ({placeholders})
                """, tuple(group_ids))
                stats = dict_row(cur.fetchone())
                
                g["domain_count"] = stats.get("domain_count") or 0
                g["total_articles"] = stats.get("total_articles") or 0
                g["articles_with_html"] = stats.get("articles_with_html") or 0
                g["articles_without_html"] = g["total_articles"] - g["articles_with_html"]
                
                # Get creation date
                cur = db_execute(conn, "SELECT created_at FROM `groups` WHERE id = ?", (g["id"],))
                row = dict_row(cur.fetchone())
                g["created_at"] = row.get("created_at") if row else None
            
            # Group the all_groups by user
            groups_by_user = {}
            for g in all_groups:
                if is_admin:
                    users = group_users_map.get(g["id"], [])
                    user_key = ", ".join(sorted(users)) if users else "Unassigned"
                else:
                    user_key = "Your Groups"
                
                if user_key not in groups_by_user:
                    groups_by_user[user_key] = []
                groups_by_user[user_key].append(g)
            
            # Show group selector page
            group_cards_html = ""
            
            # Sort user keys: Unassigned at the end, others alphabetically
            user_keys = sorted(list(groups_by_user.keys()), key=lambda k: (k == "Unassigned", k))
            
            for user_key in user_keys:
                user_groups = groups_by_user[user_key]
                if not user_groups:
                    continue
                    
                if is_admin:
                    group_cards_html += f'<h4 class="mt-4 mb-3 border-bottom pb-2 text-secondary">👤 User: {html.escape(user_key)}</h4>'
                
                group_cards_html += '<div class="row g-3 mb-4">'
                
                for g in user_groups:
                    created_at = g.get("created_at")
                    if created_at:
                        if isinstance(created_at, str):
                            created_date = created_at[:10]
                        else:
                            created_date = created_at.strftime("%Y-%m-%d")
                    else:
                        created_date = "N/A"
                    
                    # Get domain list with article stats for this group
                    group_ids = get_descendants(g["id"])
                    placeholders = ",".join(["?"] * len(group_ids))
                    cur = db_execute(conn, f"""
                        SELECT 
                            d.domain_url,
                            d.domain_index,
                            d.group_id,
                            COUNT(DISTINCT t.id) as total_articles,
                            SUM(CASE WHEN ac.article_html IS NOT NULL AND TRIM(ac.article_html) != '' THEN 1 ELSE 0 END) as with_html
                        FROM domains d
                        LEFT JOIN titles t ON t.domain_id = d.id
                        LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                        WHERE d.group_id IN ({placeholders})
                        GROUP BY d.id, d.domain_url, d.domain_index, d.group_id
                        ORDER BY d.group_id, d.domain_index
                    """, tuple(group_ids))
                    domains = [dict_row(r) for r in cur.fetchall()]
                    
                    # Create mini table with 4 domains per row (A, B, C, D)
                    domain_table = '<table class="table table-sm table-bordered mb-0" style="font-size:0.7rem"><tbody>'
                    
                    # Group domains by their group_id (subgroups)
                    from itertools import groupby
                    for subgroup_id, subgroup_domains in groupby(domains, key=lambda x: x["group_id"]):
                        subgroup_list = list(subgroup_domains)
                        if subgroup_list:
                            domain_table += '<tr>'
                            labels = ['A', 'B', 'C', 'D']
                            for i in range(4):
                                if i < len(subgroup_list):
                                    domain = subgroup_list[i]
                                    total = domain.get("total_articles") or 0
                                    with_html = domain.get("with_html") or 0
                                    without_html = total - with_html
                                    domain_name = domain["domain_url"][:15] + "..." if len(domain["domain_url"]) > 15 else domain["domain_url"]
                                    domain_table += f'''
                                    <td class="p-1" title="{html.escape(domain["domain_url"])}">
                                        <strong>{labels[i]}:</strong> {html.escape(domain_name)} <small class="text-success">✓{with_html}</small>/<small class="text-warning">{without_html}</small>
                                    </td>
                                    '''
                                else:
                                    domain_table += f'<td class="p-1 text-muted"><strong>{labels[i]}:</strong> -</td>'
                            domain_table += '</tr>'
                    
                    domain_table += '</tbody></table>'
                    
                    domain_display = domain_table if domains else '<span class="text-muted small">No domains</span>'
                    
                    group_cards_html += f'''
                    <div class="col-lg-4 col-md-6">
                      <div class="card h-100 group-card shadow-sm" style="cursor:pointer; transition: transform 0.2s;" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'" onclick="window.location.href='/admin/domains?group_id={g["id"]}'">
                        <div class="card-body">
                          <h5 class="card-title text-truncate mb-2" title="{html.escape(g["name"])}">{html.escape(g["name"])}</h5>
                          <p class="card-text small text-muted mb-2">
                            📅 {created_date}
                          </p>
                          <div class="mb-2">
                            <span class="badge bg-primary">{g["domain_count"]} Domain{"s" if g["domain_count"] != 1 else ""}</span>
                            <span class="badge bg-info">{g["total_articles"]} Article{"s" if g["total_articles"] != 1 else ""}</span>
                          </div>
                          <div class="mb-2" style="font-size:0.75rem">
                            <span class="text-success">✅ {g["articles_with_html"]}</span>
                            <span class="text-muted mx-1">/</span>
                            <span class="text-warning">⏳ {g["articles_without_html"]}</span>
                          </div>
                          <div class="mb-2" style="max-height:200px; overflow-y:auto; overflow-x:hidden;">
                            {domain_display}
                          </div>
                          <a href="/admin/domains?group_id={g["id"]}" class="btn btn-sm btn-primary w-100">View Domains</a>
                        </div>
                      </div>
                    </div>
                    '''
                
                group_cards_html += '</div>'
            
            content = f'''
            <style>
            .group-card {{
              border-left: 4px solid #0d6efd;
            }}
            .group-card:hover {{
              box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15) !important;
            }}
            </style>
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h2 class="mb-0">Select a Group</h2>
              <button type="button" class="btn btn-success" onclick="showCreateGroupModal()">+ Create New Group</button>
            </div>
            <div class="alert alert-info">
              <strong>📁 Select a top-level parent group to manage domains</strong><br>
              Showing only top-level parent groups. Each group can have multiple subgroups with domains.
            </div>
            {group_cards_html if group_cards_html else '<div class="alert alert-warning">No groups yet. Create your first group to get started!</div>'}
            
            <div id="createGroupModal" class="modal fade" tabindex="-1">
              <div class="modal-dialog">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title">Create New Group</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                  </div>
                  <form method="post" action="/admin/groups/add">
                    <div class="modal-body">
                      <div class="mb-3">
                        <label class="form-label">Group Name</label>
                        <input type="text" name="name" class="form-control" placeholder="e.g., Food Recipes" required>
                      </div>
                    </div>
                    <div class="modal-footer">
                      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                      <button type="submit" class="btn btn-primary">Create Group</button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
            
            <script>
            function showCreateGroupModal() {{
              var modal = new bootstrap.Modal(document.getElementById('createGroupModal'));
              modal.show();
            }}
            </script>
            '''
            return base_layout(content, "Domains - Select Group")
    
    # Get all group IDs to include (current + all descendants)
    group_ids_to_include = []
    group_hierarchy_path = None
    if filter_group_id:
        # Check if user has access to this group
        if not is_admin:
            user_group_ids = get_user_group_ids(user_id, is_admin)
            if filter_group_id not in user_group_ids:
                return base_layout("<div class='alert alert-danger'>You don't have access to this group.</div>", "Domains")
        
        with get_connection() as conn:
            # Build hierarchy path for breadcrumb
            def build_group_path(gid):
                path = []
                current = gid
                visited = set()
                while current and current not in visited:
                    visited.add(current)
                    cur = db_execute(conn, "SELECT name, parent_group_id FROM `groups` WHERE id = ?", (current,))
                    g = dict_row(cur.fetchone())
                    if g:
                        path.insert(0, {"id": current, "name": g["name"]})
                        current = g.get("parent_group_id")
                    else:
                        break
                return path
            
            group_hierarchy_path = build_group_path(filter_group_id)
            
            # Get all descendant groups recursively
            def get_all_descendants(gid):
                result = [gid]
                cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
                children = [dict_row(r)["id"] for r in cur.fetchall()]
                for child_id in children:
                    result.extend(get_all_descendants(child_id))
                return result
            
            group_ids_to_include = get_all_descendants(filter_group_id)
    
    with get_connection() as conn:
        # Build user domain filter
        user_domain_filter = ""
        user_domain_params = []
        if not is_admin:
            if user_domain_ids:
                user_domain_placeholders = ",".join(["?"] * len(user_domain_ids))
                user_domain_filter = f" AND id IN ({user_domain_placeholders})"
                user_domain_params = user_domain_ids
            elif not filter_group_id:
                # User has no domains and not filtering by group - show nothing
                user_domain_filter = " AND id = -1"
                user_domain_params = []
            # If filtering by group and user owns that group, don't apply domain filter (show empty group)
        
        if group_ids_to_include:
            placeholders = ",".join(["?"] * len(group_ids_to_include))
            cur = db_execute(conn, f"""SELECT id, domain_url, domain_name, group_id, domain_index, cloudflare_info,
                website_template, article_template_config, domain_colors, domain_fonts, categories_list,
                header_template, footer_template,
                side_article_template, category_page_template, writer_template, writers,
                domain_page_about_us, domain_page_terms_of_use, domain_page_privacy_policy, domain_page_gdpr_policy,
                domain_page_cookie_policy, domain_page_copyright_policy, domain_page_disclaimer, domain_page_contact_us
                FROM domains
                WHERE group_id IN ({placeholders}){user_domain_filter}
                ORDER BY COALESCE(group_id, 0), COALESCE(domain_index, 0)""", tuple(group_ids_to_include) + tuple(user_domain_params))
        else:
            cur = db_execute(conn, f"""SELECT id, domain_url, domain_name, group_id, domain_index, cloudflare_info,
                website_template, article_template_config, domain_colors, domain_fonts, categories_list,
                header_template, footer_template,
                side_article_template, category_page_template, writer_template, writers,
                domain_page_about_us, domain_page_terms_of_use, domain_page_privacy_policy, domain_page_gdpr_policy,
                domain_page_cookie_policy, domain_page_copyright_policy, domain_page_disclaimer, domain_page_contact_us
                FROM domains
                WHERE 1=1{user_domain_filter}
                ORDER BY (group_id IS NULL), COALESCE(group_id, 0), COALESCE(domain_index, 0)""", tuple(user_domain_params))
        rows = cur.fetchall()
        domains = [dict_row(r) for r in rows]
    
    # If no domains found and user is not admin, show helpful message
    if not domains and not is_admin:
        if filter_group_id:
            msg = f"<div class='alert alert-info'>This group has no domains yet. <a href='/admin/domains' class='alert-link'>Add domains to this group</a>.</div>"
        elif not user_domain_ids:
            msg = f"<div class='alert alert-warning'>No domains assigned to your account. <a href='#' class='alert-link' data-bs-toggle='modal' data-bs-target='#bulkAddModal'>Add domains</a> or contact administrator.</div>"
        else:
            msg = "<div class='alert alert-info'>No domains found matching your filters.</div>"
        # Still show the page with add domain form
        # Don't return early, let the page render normally
    
    with get_connection() as conn:
        # Get user's accessible group IDs for filtering
        user_group_ids = get_user_group_ids(user_id, is_admin)
        
        # Get all groups (filtered by user if not admin)
        if not is_admin:
            if user_group_ids:
                placeholders = ",".join(["?"] * len(user_group_ids))
                cur = db_execute(conn, f"SELECT id, name, parent_group_id FROM `groups` WHERE id IN ({placeholders}) ORDER BY name", tuple(user_group_ids))
            else:
                all_groups = []
                group_map = {}
        else:
            cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` ORDER BY name")
        
        if is_admin or user_group_ids:
            all_groups = [dict_row(r) for r in cur.fetchall()]
            group_map = {g["id"]: g["name"] for g in all_groups}
        else:
            all_groups = []
            group_map = {}
        
        # Build complete hierarchy for each domain's group
        def build_full_hierarchy(gid):
            if not gid:
                return "-"
            path = []
            current = gid
            visited = set()
            while current and current not in visited:
                visited.add(current)
                g = next((x for x in all_groups if x["id"] == current), None)
                if g:
                    path.insert(0, g["name"])
                    current = g.get("parent_group_id")
                else:
                    break
            return " > ".join(path) if path else group_map.get(gid, "-")
        
        for d in domains:
            d["group_name"] = group_map.get(d.get("group_id")) or "-"
            d["group_hierarchy"] = build_full_hierarchy(d.get("group_id"))
        
        # Add hierarchy to all_groups for the change group modal
        for g in all_groups:
            g["hierarchy"] = build_full_hierarchy(g["id"])
        for g in all_groups:
            g["hierarchy"] = build_full_hierarchy(g["id"])
        all_groups_json = json.dumps(all_groups)
        
        # Build group options with hierarchy for add domain form (only groups with <4 domains)
        cur = db_execute(conn, """
            SELECT g.id, COUNT(d.id) as domain_count
            FROM `groups` g
            LEFT JOIN domains d ON d.group_id = g.id
            GROUP BY g.id
            HAVING domain_count < 4
            ORDER BY g.id
        """)
        groups_with_space = {dict_row(r)["id"]: dict_row(r).get("domain_count", 0) for r in cur.fetchall()}
        
        group_opts = '<option value="">-- Select Group --</option>'
        for g in all_groups:
            if g["id"] in groups_with_space:
                hierarchy = build_full_hierarchy(g["id"])
                domain_count = groups_with_space[g["id"]]
                slots_left = 4 - domain_count
                group_opts += f'<option value="{g["id"]}">{hierarchy} ({domain_count}/4 - {slots_left} slots left)</option>'
    with get_connection() as conn:
        for d in domains:
            cur = db_execute(conn, "SELECT id, name, preview_image_url FROM domain_templates WHERE domain_id = ? ORDER BY sort_order, id", (d["id"],))
            d["templates"] = [dict_row(r) for r in cur.fetchall()]

    # Domain stats: html+css, main_image, ingredient_image counts vs total titles
    # Fetch available generators from articles-website-generator
    generators = []
    try:
        base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
        if base:
            req = urllib.request.Request(f"{base}/generators", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                generators = data.get("generators", [])
    except Exception:
        pass
    if not generators:
        generators = _list_article_generator_files()

    # Fetch available page themes from website-parts-generator (auto-detected)
    page_themes_list = _get_available_page_themes()

    domain_ids = [d["id"] for d in domains]
    stats_map = {}
    if domain_ids:
        placeholders = ",".join(["?"] * len(domain_ids))
        with get_connection() as conn:
            cur = db_execute(conn, f"""
                SELECT t.domain_id,
                    COUNT(DISTINCT t.id) AS total,
                    SUM(CASE WHEN ac.id IS NOT NULL AND TRIM(COALESCE(ac.article_html,'')) != '' AND TRIM(COALESCE(ac.article_css,'')) != '' THEN 1 ELSE 0 END) AS html_css,
                    SUM(CASE WHEN ac.main_image IS NOT NULL AND TRIM(ac.main_image) LIKE 'http%%' THEN 1 ELSE 0 END) AS main_img,
                    SUM(CASE WHEN ac.ingredient_image IS NOT NULL AND TRIM(ac.ingredient_image) LIKE 'http%%' THEN 1 ELSE 0 END) AS ing_img
                FROM titles t
                LEFT JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id IN ({placeholders})
                GROUP BY t.domain_id
            """, tuple(domain_ids))
            for r in cur.fetchall():
                row = dict_row(r)
                stats_map[row["domain_id"]] = row
    for d in domains:
        s = stats_map.get(d["id"], {}) or {}
        d["stats_total"] = s.get("total") or 0
        d["stats_html_css"] = s.get("html_css") or 0
        d["stats_main_img"] = s.get("main_img") or 0
        d["stats_ing_img"] = s.get("ing_img") or 0
        total = d.get("stats_total") or 0
        d["stats_no_html_css"] = total - (d["stats_html_css"] or 0)
        d["stats_no_main_img"] = total - (d["stats_main_img"] or 0)
        d["stats_no_ing_img"] = total - (d["stats_ing_img"] or 0)
        d["stats_pin_count"] = len(d.get("templates") or [])
        # Extract saved page theme from domain page JSON
        d["saved_page_theme"] = _get_domain_page_theme(d)

    def stats_cell(d):
        """Stats column: separate badges for with/without (html+css, main_img, ing_img); Pin templates link."""
        total = d.get("stats_total") or 0
        html_css = d.get("stats_html_css") or 0
        main_img = d.get("stats_main_img") or 0
        ing_img = d.get("stats_ing_img") or 0
        no_html_css = d.get("stats_no_html_css") or 0
        no_main_img = d.get("stats_no_main_img") or 0
        no_ing_img = d.get("stats_no_ing_img") or 0
        pin_count = d.get("stats_pin_count") or 0
        did = d["id"]
        if total == 0:
            return '<div class="stats-cell text-muted small">—</div>'
        parts = [
            f'<button type="button" class="badge bg-secondary stats-badge stats-filter-btn" data-domain-id="{did}" data-stats-type="html_css" data-count="{html_css}" title="With HTML+CSS - Click to view & generate">{html_css}✓</button>',
            f'<button type="button" class="badge bg-secondary bg-opacity-50 text-dark stats-badge stats-filter-btn" data-domain-id="{did}" data-stats-type="no_html_css" data-count="{no_html_css}" title="Without HTML+CSS - Click to view & generate">{no_html_css}✗</button>',
            f'<button type="button" class="badge bg-info text-dark stats-badge stats-filter-btn" data-domain-id="{did}" data-stats-type="main_img" data-count="{main_img}" title="With main image - Click to view & generate">{main_img}✓</button>',
            f'<button type="button" class="badge bg-info bg-opacity-50 text-dark stats-badge stats-filter-btn" data-domain-id="{did}" data-stats-type="no_main_img" data-count="{no_main_img}" title="Without main image - Click to view & generate">{no_main_img}✗</button>',
            f'<button type="button" class="badge bg-primary stats-badge stats-filter-btn" data-domain-id="{did}" data-stats-type="ing_img" data-count="{ing_img}" title="With ingredient image - Click to view & generate">{ing_img}✓</button>',
            f'<button type="button" class="badge bg-primary bg-opacity-50 text-dark stats-badge stats-filter-btn" data-domain-id="{did}" data-stats-type="no_ing_img" data-count="{no_ing_img}" title="Without ingredient image - Click to view & generate">{no_ing_img}✗</button>',
            f'<a href="/admin/domains/{did}/templates" class="btn btn-sm btn-outline-warning py-0 px-1" title="Pin templates ({pin_count})">📌{pin_count}</a>',
        ]
        return '<div class="stats-cell d-flex flex-wrap align-items-center" style="gap:2px">' + "".join(parts) + "</div>"

    def last_deploy_cell(d):
        cf_raw = (d.get("cloudflare_info") or "").strip()
        if not cf_raw:
            return '<span class="text-muted small">—</span>'
        try:
            cf = json.loads(cf_raw) if isinstance(cf_raw, str) else cf_raw
            deploys = cf.get("deployments") or []
            if not deploys:
                return '<span class="text-muted small">—</span>'
            created_on = deploys[0].get("created_on") or ""
            if not created_on:
                return '<span class="text-muted small">—</span>'
            # Parse ISO date and compute relative time
            import datetime as _dt
            ts = _dt.datetime.fromisoformat(created_on.replace("Z", "+00:00"))
            now = _dt.datetime.now(_dt.timezone.utc)
            diff = now - ts
            days = diff.days
            if days == 0:
                hours = diff.seconds // 3600
                label = f"{hours}h ago" if hours > 0 else "just now"
            elif days == 1:
                label = "1d ago"
            elif days < 30:
                label = f"{days}d ago"
            elif days < 365:
                label = f"{days // 30}mo ago"
            else:
                label = f"{days // 365}y ago"
            status = (deploys[0].get("status") or "")
            cls = "success" if status == "success" else ("danger" if status == "failure" else "secondary")
            return f'<span class="badge bg-{cls}" title="{html.escape(created_on)}">{html.escape(label)}</span>'
        except Exception:
            return '<span class="text-muted small">—</span>'

    def pin_templates_cell(domain_id, templates_list):
        parts = []
        for t in templates_list:
            prev = (t.get("preview_image_url") or "").strip()
            tid = t.get("id")
            name_esc = html.escape(t.get("name") or "")
            del_btn = f'<button type="button" class="pin-del" data-template-id="{tid}" title="Delete {name_esc}">&times;</button>'
            if prev and prev.startswith("http"):
                parts.append(f'<span class="pin-thumb-wrap">{del_btn}<img src="{html.escape(prev)}" class="pin-thumb" data-domain-id="{domain_id}" data-template-id="{tid}" title="{name_esc}" alt=""></span>')
            else:
                parts.append(f'<span class="pin-thumb-wrap">{del_btn}<span class="pin-thumb pin-thumb-placeholder" data-domain-id="{domain_id}" data-template-id="{tid}" title="{name_esc}">?</span></span>')
        parts.append(f'<button type="button" class="pin-thumb pin-add" data-domain-id="{domain_id}" title="Add template">+</button>')
        return '<div class="pin-templates-cell">' + "".join(parts) + "</div>"

    def colors_cell(domain_id, domain_colors_json):
        colors = dict(DEFAULT_DOMAIN_COLORS)
        raw = (domain_colors_json or "").strip()
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        if v:
                            colors[k] = str(v)
            except Exception:
                pass
        parts = []
        for key in ["primary", "secondary", "background", "text_primary", "text_secondary", "border"]:
            val = colors.get(key, "#888888")
            parts.append(f'<input type="color" class="color-input" data-domain-id="{domain_id}" data-color-key="{key}" value="{val}" title="{key}">')
        parts.append(f'<button type="button" class="btn-save-colors" data-domain-id="{domain_id}" title="Save colors and update all articles" style="display:none;">💾</button>')
        parts.append(f'<button type="button" class="btn btn-sm btn-outline-secondary colors-random-btn" data-domain-id="{domain_id}" title="AI palette: matching colors with readable contrast">🎨</button>')
        return '<div class="colors-cell" data-domain-id="' + str(domain_id) + '">' + "".join(parts) + '</div>'

    def fonts_cell(domain_id, domain_fonts_json):
        fonts = dict(DEFAULT_DOMAIN_FONTS)
        raw = (domain_fonts_json or "").strip()
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        if v:
                            fonts[k] = str(v)
            except Exception:
                pass
        h_opts = "".join(f'<option value="{html.escape(f)}"{" selected" if fonts.get("heading_family") == f else ""}>{html.escape(f)}</option>' for f in FONT_FAMILY_OPTIONS)
        b_opts = "".join(f'<option value="{html.escape(f)}"{" selected" if fonts.get("body_family") == f else ""}>{html.escape(f)}</option>' for f in FONT_FAMILY_OPTIONS)
        return f'<div class="fonts-cell" data-domain-id="{domain_id}"><select class="form-select form-select-sm font-heading-select" data-domain-id="{domain_id}" title="Heading font">{h_opts}</select><select class="form-select form-select-sm font-body-select mt-1" data-domain-id="{domain_id}" title="Body font">{b_opts}</select><button type="button" class="btn-fonts-save btn btn-sm btn-success mt-1" data-domain-id="{domain_id}" title="Save fonts" style="display:none;">💾</button></div>'

    def theme_cell(d):
        """Show theme select dropdown + eye preview + Pages button."""
        did = d.get("id")
        saved_theme = d.get("saved_page_theme") or ""
        # Build page states for pages-btn
        page_states = {}
        for slug in DOMAIN_PAGE_SLUGS:
            col = PAGE_SLUG_TO_COLUMN.get(slug)
            raw = (d.get(col) or "").strip() if col else ""
            has_it = False
            if raw:
                try:
                    j = json.loads(raw)
                    has_it = isinstance(j, dict) and bool((j.get("main_html") or "").strip())
                except Exception:
                    pass
            page_states[slug] = has_it
        domain_url = (d.get("domain_url") or "").strip() or "-"
        domain_url_esc = html.escape(domain_url)
        states_json = html.escape(json.dumps(page_states), quote=True)
        theme_esc = html.escape(saved_theme, quote=True)
        # Theme select dropdown
        opts = []
        for t in page_themes_list:
            label = t.replace('_', ' ').title()
            sel = ' selected' if t == saved_theme else ''
            opts.append(f'<option value="{html.escape(t)}"{sel}>{html.escape(label)}</option>')
        sel_html = f'<select class="form-select form-select-sm page-theme-select" data-domain-id="{did}" data-original="{theme_esc}" style="min-width:90px;font-size:0.7rem;padding:0.15rem 0.25rem;">' + ''.join(opts) + '</select>'
        eye_btn = f'<a href="/preview-website/{did}" class="btn btn-sm btn-outline-success py-0 px-1 theme-example-btn" target="_blank" title="Preview site" data-domain-id="{did}">👁</a>' if did else ''
        return f'<div class="theme-cell">{sel_html}{eye_btn}</div>'
    
    def writers_cell(domain_id, writers_json):
        """Show writers count and edit button."""
        count = 0
        raw = (writers_json or "").strip()
        if raw:
            try:
                writers = json.loads(raw)
                if isinstance(writers, list):
                    count = len(writers)
            except Exception:
                pass
        status = f'<span class="badge bg-success" style="font-size:0.65rem;padding:0.1em 0.3em;">{count}</span>' if count > 0 else '<span class="badge bg-secondary" style="font-size:0.65rem;padding:0.1em 0.3em;">0</span>'
        return f'<div class="writers-cell"><button type="button" class="btn btn-sm btn-outline-primary writers-btn" data-domain-id="{domain_id}" title="Manage writers">Writers</button>{status}<button type="button" class="btn btn-sm btn-outline-success generate-distribute-btn" data-domain-id="{domain_id}" title="Generate 4 writers and distribute to all articles">✨</button></div>'

    def categories_cell(domain_id, categories_list_raw):
        """Show category names (short) and Edit button."""
        names = []
        raw = (categories_list_raw or "").strip()
        if raw:
            try:
                cats = json.loads(raw)
                if isinstance(cats, list):
                    for c in cats[:8]:
                        if isinstance(c, dict):
                            n = (c.get("categorie") or c.get("name") or c.get("category") or "").strip()
                        else:
                            n = str(c).strip() if c else ""
                        if n:
                            names.append(n)
            except Exception:
                pass
        preview = ", ".join(html.escape(n) for n in names[:4]) if names else "—"
        if len(names) > 4:
            preview += "…"
        count = len(names) if names else 0
        badge = f'<span class="badge bg-info" style="font-size:0.65rem;padding:0.1em 0.3em;">{count}</span>' if count > 0 else '<span class="badge bg-secondary" style="font-size:0.65rem;padding:0.1em 0.3em;">0</span>'
        return f'<div class="categories-cell" data-domain-id="{domain_id}"><span class="categories-preview text-muted small" title="{html.escape(", ".join(names) if names else "No categories")}">{preview}</span>{badge}<button type="button" class="btn btn-sm btn-outline-primary categories-btn py-0 px-1" data-domain-id="{domain_id}" title="Edit categories">Edit</button></div>'

    def _domain_href(url):
        u = (url or "").strip()
        if not u:
            return "#"
        return u if u.startswith(("http://", "https://")) else "https://" + u

    def domain_url_cell(d, grp_display):
        """Domain cell with link, group badge, Edit text button, change group button, and clear group button.
        Change group button only shown when domain has no titles and no article content."""
        url = (d.get("domain_url") or "").strip() or "-"
        edit_btn = f'<button type="button" class="btn btn-sm btn-outline-secondary py-0 px-1 edit-domain-text-btn" data-domain-id="{d["id"]}" data-domain-url="{html.escape(url)}" title="Edit domain URL">📝</button>'
        has_data = (d.get("stats_total") or 0) > 0
        change_group_btn = '' if has_data else f'<button type="button" class="btn btn-sm btn-outline-primary py-0 px-1 change-group-btn" data-domain-id="{d["id"]}" data-current-group="{d.get("group_id") or ""}" title="Change group">📁</button>'
        # Show clear button only if domain is in a group
        clear_btn = ''
        if d.get("group_id"):
            clear_btn = f'<button type="button" class="btn btn-sm btn-outline-danger py-0 px-1 clear-group-btn" data-domain-id="{d["id"]}" title="Remove from group">✖️</button>'
        return f'<div class="d-flex flex-column gap-1"><div class="d-flex align-items-center gap-1 flex-wrap"><a href="{html.escape(_domain_href(d.get("domain_url")))}" target="_blank" rel="noopener" class="domain-url-link">{html.escape(url)}</a>{edit_btn}{change_group_btn}{clear_btn}</div><span class="badge bg-light text-dark align-self-start" style="font-size:0.65rem;padding:0.1em 0.35em;">{html.escape(grp_display)}</span></div>'

    def article_cell(domain_id, website_template, article_config, gens):
        """Select for generator + button to open Article Editor + button to show template example."""
        # Use domains.website_template as primary source (what the PUT API saves)
        cv = (website_template or "").strip()
        if not cv and article_config:
            try:
                config = json.loads(article_config) if isinstance(article_config, str) else article_config
                generator_num = config.get("generator")
                if generator_num:
                    cv = f"generator-{generator_num}" if not str(generator_num).startswith("generator-") else str(generator_num)
            except Exception:
                pass
        
        opts = ['<option value="">—</option>']
        for g in gens:
            sel = ' selected' if cv == g else ''
            opts.append(f'<option value="{html.escape(g)}"{sel}>{html.escape(g)}</option>')
        sel_html = f'<select class="form-select form-select-sm website-template-select" data-domain-id="{domain_id}" data-original="{html.escape(cv)}" style="min-width:100px">' + "".join(opts) + '</select>'
        edit_btn = f'<button type="button" class="btn btn-sm btn-outline-secondary article-edit-btn" data-domain-id="{domain_id}" title="Edit article template (colors, fonts, layout)">✏️</button>'
        example_btn = f'<button type="button" class="btn btn-sm btn-outline-info article-example-btn" data-domain-id="{domain_id}" title="Show template example">👁</button>'
        return f'<div class="article-cell"><span class="article-select-wrap">{sel_html}</span>{edit_btn}{example_btn}</div>'

    def cloudflare_cell(d):
        did = d["id"]
        cf_raw = (d.get("cloudflare_info") or "").strip()
        cf = {}
        if cf_raw:
            try:
                cf = json.loads(cf_raw) if isinstance(cf_raw, str) else cf_raw
            except json.JSONDecodeError:
                pass
        status = cf.get("status", "")
        # Determine badge state: check if pages.dev is up but custom domain is down
        checks = cf.get("check_details") or []
        pages_up = any(c.get("up") and ".pages.dev" in (c.get("url") or "") for c in checks)
        custom_up = any(c.get("up") and ".pages.dev" not in (c.get("url") or "") for c in checks)
        if checks:
            if pages_up and custom_up:
                badge_cls, badge_label = "success", "up"
            elif pages_up and not custom_up:
                badge_cls, badge_label = "warning", "↑ pages / ↓ domain"
            elif status == "up":
                badge_cls, badge_label = "success", "up"
            else:
                badge_cls, badge_label = "danger", "down"
        elif status == "up":
            badge_cls, badge_label = "success", "up"
        elif status in ("down", "error"):
            badge_cls, badge_label = "danger", status
        else:
            badge_cls, badge_label = "secondary", status or "—"
        badge = f'<span class="badge bg-{badge_cls} cf-info-badge" data-domain-id="{did}" data-cf-json="{html.escape(cf_raw or "{}", quote=True)}" title="Click to view full JSON">{badge_label}</span>' if cf else '<span class="text-muted">—</span>'
        dns_setup = cf.get("dns_setup", False)
        dns_badge = f'<span class="badge bg-{"success" if dns_setup else "secondary"}" title="DNS zone in Cloudflare: {"yes" if dns_setup else "no"}">DNS{"✓" if dns_setup else "✗"}</span>'
        dns_btn = f'<button type="button" class="btn btn-sm btn-outline-primary cf-dns-btn" data-domain-id="{did}" data-domain-url="{html.escape(d.get("domain_url") or "")}" title="Setup DNS in Cloudflare">DNS</button>'
        ver_btn = f'<button type="button" class="btn btn-sm btn-outline-secondary cf-versions-btn" data-domain-id="{did}" data-domain-url="{html.escape(d.get("domain_url") or "")}" title="Manage deployment versions">🕓</button>'
        deploy_btn = f'<button type="button" class="btn btn-sm btn-info deploy-cf-btn" data-domain-id="{did}" title="Deploy to Cloudflare">☁️</button>'
        return f'<div class="cloudflare-cell d-flex align-items-center gap-1">{deploy_btn}{dns_btn}{ver_btn}{dns_badge}{badge}</div>'

    prev_gid = None
    row_parts = []
    for d in domains:
        gid = d.get("group_id")
        idx = d.get("domain_index")
        abcd = chr(65 + idx) if idx is not None and 0 <= idx < 26 else ""
        # Show complete group hierarchy instead of just group name
        grp_hierarchy = d.get("group_hierarchy") or "-"
        grp_display = grp_hierarchy + (f" {abcd}" if abcd else "")
        tr_class = " group-row-start" if prev_gid is not None and gid != prev_gid else ""
        prev_gid = gid
        data_grp = f' data-group-id="{gid}"' if gid is not None else ' data-group-id=""'
        data_domain_id = f' data-domain-id="{d["id"]}"'
        row_parts.append(
        f'<tr class="domains-row{tr_class}"{data_grp}{data_domain_id}>'
        f'<td class="text-muted small">{d["id"]}</td>'
        f'<td class="domain-url-cell">{domain_url_cell(d, grp_display)}</td>'
        f'<td class="cloudflare-td">{cloudflare_cell(d)}</td>'
        f'<td class="colors-td">{colors_cell(d["id"], d.get("domain_colors"))}</td>'
        f'<td class="fonts-td">{fonts_cell(d["id"], d.get("domain_fonts"))}</td>'
        f'<td class="categories-td">{categories_cell(d["id"], d.get("categories_list"))}</td>'
        f'<td class="writers-td">{writers_cell(d["id"], d.get("writers"))}</td>'
        f'<td class="pin-templates-td">{pin_templates_cell(d["id"], d.get("templates") or [])}</td>'
        f'<td class="theme-td">{theme_cell(d)}</td>'
        f'<td class="article-td">{article_cell(d["id"], d.get("website_template"), d.get("article_template_config"), generators)}</td>'
        f'<td class="stats-td">{stats_cell(d)}</td>'
        f'<td class="last-deploy-td">{last_deploy_cell(d)}</td>'
        f'<td class="actions-cell"><div class="btn-group btn-group-sm" role="group">'
        f'<a href="/preview-website/{d["id"]}" class="btn btn-success" target="_blank" title="View site">👁</a>'
        f'<button type="button" class="btn btn-outline-primary list-domain-articles-btn" data-domain-id="{d["id"]}" data-domain-url="{html.escape((d.get("domain_url") or "").strip() or "-")}" title="List all articles in this domain">Articles</button>'
        f'<button type="button" class="btn btn-outline-danger pinterest-setup-btn" data-domain-id="{d["id"]}" data-domain-name="{html.escape((d.get("domain_url") or d.get("domain_name") or "").strip() or "-", quote=True)}" title="Pinterest setup (RSS, schedule, manual)">📌</button>'
        f'<a href="/database-management?domain_id={d["id"]}" class="btn btn-outline-info" title="View in Database Management">📊</a>'
        f'<a href="/admin/domains/delete/{d["id"]}{"?group_id=" + str(filter_group_id) if filter_group_id else ""}" class="btn btn-outline-danger" title="Delete" onclick="return confirm(\'Delete this domain?\')">🗑</a>'
        f'</div></td></tr>'
        )
    rows_html = "".join(row_parts)
    domains_json = json.dumps([{"id": d["id"], "domain_url": (d.get("domain_url") or d.get("domain_name") or "").strip() or "\u2014"} for d in domains])
    # SITE_TEMPLATES loaded via fetch in script - avoids JSON embedding issues

    run_this_group_btn_html = ""
    if filter_group_id:
        gname = html.escape(next((g["name"] for g in all_groups if g["id"] == filter_group_id), "Current Group")).replace("'", "\\'")
        run_this_group_btn_html = f'<button type="button" class="btn btn-primary btn-sm" onclick="openBulkGroupModal({filter_group_id}, \'{gname}\')" title="Run for all rows in this group">Run this group</button>'

    content = f"""
    <style>
    .domains-table {{ font-size: 0.8rem; border-collapse: collapse; }}
    .domains-table tr.group-row-start {{ border-top: 2px solid #6c757d; }}
    .domains-table tr.group-row-start > td {{ padding-top: 0.4rem; }}
    .domains-table th, .domains-table td {{ padding: 0.25rem 0.35rem; vertical-align: middle; }}
    .domains-table th {{ font-weight: 600; white-space: nowrap; }}
    .domains-table .col-id, .domains-table td.text-muted.small:first-child {{ width: 32px; }}
    .domains-table .col-domain, .domains-table .domain-url-cell {{ max-width: 220px; }}
    .domains-table .col-last-deploy, .domains-table .last-deploy-td {{ width: 80px; white-space: nowrap; text-align: center; }}
    .domains-table .col-cf, .domains-table .cloudflare-td {{ white-space: nowrap; }}
    .domains-table .col-actions, .domains-table .actions-cell {{ white-space: nowrap; }}
    .domains-table .btn {{ white-space: nowrap; }}
    .cf-info-badge {{ cursor: pointer; }}
    .domain-url-link {{ color: #0d6efd; text-decoration: none; }}
    .domain-url-link:hover {{ text-decoration: underline; color: #0a58ca; }}
    .domain-url-cell {{ word-break: break-all; line-height: 1.3; }}
    .pin-templates-cell {{ display: flex; flex-wrap: wrap; gap: 2px; align-items: center; }}
    .pin-thumb-wrap {{ position: relative; display: inline-block; }}
    .pin-thumb-wrap .pin-del {{ display: none; position: absolute; top: -5px; right: -5px; width: 14px; height: 14px; border-radius: 50%; background: #dc3545; color: #fff; border: 1px solid #fff; font-size: 9px; line-height: 12px; text-align: center; cursor: pointer; padding: 0; z-index: 2; }}
    .pin-thumb-wrap:hover .pin-del {{ display: block; }}
    .pin-thumb {{ width: 32px; height: 32px; object-fit: cover; border-radius: 4px; border: 1px solid #dee2e6; cursor: pointer; flex-shrink: 0; }}
    .pin-thumb:hover {{ border-color: #0d6efd; box-shadow: 0 0 0 2px rgba(13,110,253,.25); }}
    .pin-thumb-placeholder {{ display: inline-flex; align-items: center; justify-content: center; background: #e9ecef; color: #6c757d; font-size: 0.75rem; text-decoration: none; }}
    .pin-add {{ background: #e9ecef; color: #0d6efd; font-size: 0.9rem; font-weight: bold; line-height: 1; }}
    .pin-add:hover {{ background: #0d6efd; color: #fff; }}
    .pin-thumb-hover-preview {{ display: none; position: fixed; z-index: 9999; pointer-events: none; border: 2px solid #0d6efd; border-radius: 8px; box-shadow: 0 8px 32px rgba(0,0,0,0.25); background: #fff; max-width: 240px; max-height: 420px; object-fit: contain; }}
    .article-cell {{ display: flex; gap: 2px; align-items: center; flex-wrap: wrap; }}
    .article-cell .article-select-wrap {{ flex: 1; min-width: 90px; }}
    .article-cell .article-edit-btn, .article-cell .article-example-btn {{ padding: 0.15rem 0.3rem; font-size: 0.75rem; flex-shrink: 0; }}
    .colors-cell {{ display: flex; flex-wrap: wrap; gap: 2px; align-items: center; }}
    .colors-cell .color-input {{ width: 22px; height: 22px; padding: 1px; border: 1px solid #dee2e6; border-radius: 3px; cursor: pointer; }}
    .colors-cell .color-input:hover {{ border-color: #0d6efd; box-shadow: 0 0 0 2px rgba(13,110,253,.15); }}
    .btn-save-colors {{ width: 22px; height: 22px; padding: 0; border: 1px solid #198754; border-radius: 3px; background: #198754; color: white; cursor: pointer; font-size: 12px; line-height: 1; }}
    .btn-save-colors:hover {{ background: #157347; }}
    .btn-save-colors.saving {{ opacity: 0.6; cursor: wait; }}
    .colors-cell .colors-random-btn {{ width: 22px; height: 22px; padding: 0; font-size: 12px; line-height: 1; }}
    .fonts-cell {{ min-width: 100px; }}
    .fonts-cell .form-select {{ font-size: 0.7rem; padding: 0.15rem 0.25rem; min-height: auto; }}
    .fonts-cell .btn-fonts-save {{ padding: 0.15rem 0.3rem; font-size: 0.7rem; }}
    .theme-cell {{ display: flex; gap: 2px; align-items: center; flex-wrap: wrap; }}
    .theme-cell .page-theme-select {{ min-width: 90px; }}
    .theme-badge {{ display: inline-block; padding: 1px 4px; background: #e9ecef; border: 1px solid #dee2e6; border-radius: 3px; font-size: 0.65rem; font-weight: 600; color: #495057; white-space: nowrap; cursor: pointer; }}
    .theme-badge:hover {{ background: #dee2e6; border-color: #adb5bd; }}
    .theme-badge-edit {{ display: inline-flex; align-items: center; gap: 2px; vertical-align: middle; }}
    .theme-badge-edit .theme-filter {{ width: 60px; font-size: 0.65rem; padding: 1px 4px; }}
    .theme-badge-edit .theme-select {{ font-size: 0.65rem; padding: 1px 4px; min-width: 70px; max-width: 100px; }}
    .theme-stepper-nav .nav-link {{ font-size: 0.8rem; padding: 0.35rem 0.5rem; }}
    .theme-preview-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 0.75rem; }}
    .theme-preview-card {{ border: 2px solid #dee2e6; border-radius: 8px; overflow: hidden; cursor: pointer; background: #fff; transition: border-color 0.2s, box-shadow 0.2s; }}
    .theme-preview-card:hover {{ border-color: #86b7fe; }}
    .theme-preview-card.selected {{ border-color: #0d6efd; box-shadow: 0 0 0 2px rgba(13,110,253,0.25); }}
    .theme-preview-card .theme-preview-label {{ padding: 0.35rem 0.5rem; background: #f8f9fa; font-size: 0.75rem; font-weight: 600; }}
    .theme-preview-card .theme-preview-frame-wrap {{ height: 120px; background: #f8f9fa; position: relative; overflow: hidden; }}
    .theme-preview-card .theme-preview-frame-wrap iframe {{ width: 100%; height: 100%; border: 0; transform-origin: 0 0; }}
    .theme-preview-card .theme-preview-loading {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.8); font-size: 0.7rem; color: #6c757d; }}
    .stats-cell {{ font-size: 0.75rem; }}
    .stats-cell .badge, .stats-cell .stats-badge {{ font-size: 0.65rem; padding: 0.15em 0.4em; cursor: pointer; border: none; }}
    .stats-badge:hover {{ opacity: 0.9; }}
    .stats-articles-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 6px; }}
    .stats-article-card {{ border: 1px solid #dee2e6; border-radius: 4px; padding: 4px; display: flex; flex-direction: column; gap: 4px; font-size: 0.7rem; min-height: 36px; }}
    .stats-article-card a {{ color: #0d6efd; text-decoration: none; font-weight: 600; min-width: 28px; flex-shrink: 0; }}
    .stats-article-card a:hover {{ text-decoration: underline; }}
    .stats-article-thumb {{ width: 32px; height: 32px; object-fit: cover; border-radius: 3px; flex-shrink: 0; }}
    .stats-article-thumb-placeholder {{ width: 32px; height: 32px; background: #e9ecef; border-radius: 3px; font-size: 0.6rem; display: flex; align-items: center; justify-content: center; color: #6c757d; flex-shrink: 0; }}
    .stats-article-title {{ flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 0.65rem; }}
    .stats-article-actions {{ display: flex; flex-wrap: wrap; gap: 2px; }}
    .stats-article-actions .btn {{ padding: 0.15rem 0.35rem; font-size: 0.7rem; line-height: 1.2; min-width: 0; }}
    .writers-cell {{ display: flex; gap: 2px; align-items: center; flex-wrap: wrap; }}
    .writers-btn {{ font-size: 0.7rem; padding: 0.15rem 0.3rem; }}
    .categories-cell {{ display: flex; gap: 4px; align-items: center; flex-wrap: wrap; }}
    .categories-cell .categories-preview {{ max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .article-td {{ min-width: 120px; }}
    .article-td .form-select {{ padding: 0.15rem 0.25rem; font-size: 0.75rem; min-height: auto; }}
    .actions-cell .btn-group .btn {{ padding: 0.15rem 0.3rem; font-size: 0.75rem; }}
    #pinEditorModal .modal-dialog {{ max-width: 98vw; width: 1400px; height: 92vh; }}
    #pinEditorModal .modal-body {{ height: calc(92vh - 60px); padding: 0; overflow: hidden; }}
    #pinEditorModal iframe {{ width: 100%; height: 100%; border: none; display: block; min-height: 500px; }}
    #articleEditorModal .modal-dialog {{ max-width: 98vw; width: 1600px; height: 95vh; }}
    #articleEditorModal .modal-body {{ height: calc(95vh - 60px); padding: 0; overflow: hidden; }}
    #articleEditorModal iframe {{ width: 100%; height: 100%; border: none; display: block; }}
    #domainArticlesModal .modal-body {{ height: calc(90vh - 120px); overflow: hidden; }}
    #domainArticlesModal .modal-body .row {{ min-height: 0; flex: 1 1 0; }}
    #domainArticlesModal .col-md-7 {{ min-height: 0; }}
    #domainArticlesHtmlWrap {{ overflow-y: auto; overflow-x: hidden; -webkit-overflow-scrolling: touch; flex: 1 1 0%; min-height: 200px; height: 0; max-height: 65vh; }}
    #domainArticlesHtmlContent {{ overflow: visible !important; min-height: 0; }}
    #domainArticlesHtmlWrap .article-preview {{ overflow: visible !important; max-height: none !important; height: auto !important; display: block; }}
    #domainArticlesList .list-group-item.active,
    #allArticlesList .list-group-item.active {{
      background-color: #76a88b !important; border-color: #6a9a7f !important; color: #fff;
    }}
    #domainArticlesList .list-group-item.active .text-muted,
    #allArticlesList .list-group-item.active .text-muted {{ color: rgba(255,255,255,0.8) !important; }}
    #domainArticlesList .list-group-item.active .btn-domain-sibling {{
      background: #fff; color: #212529; border: 1px solid rgba(0,0,0,0.2);
    }}
    #domainArticlesList .list-group-item.active .btn-domain-sibling.btn-primary {{
      background: #fff; color: #0d6efd; border: 1px solid #0d6efd; font-weight: 600;
    }}
    #domainArticlesList .list-group-item.active .btn-outline-primary,
    #allArticlesList .list-group-item.active .btn-outline-primary {{
      background: #fff; color: #0d6efd; border-color: #0d6efd;
    }}
    #domainArticlesList .list-group-item .stats-article-actions .btn,
    #allArticlesList .list-group-item .stats-article-actions .btn {{
      padding: 0.15rem 0.35rem; font-size: 0.7rem; line-height: 1.2; min-width: 0;
    }}
    #allArticlesModal .modal-body {{ height: calc(90vh - 120px); overflow: hidden; display: flex; flex-direction: column; }}
    #allArticlesModal .modal-body .row {{ min-height: 0; flex: 1 1 0; display: flex; }}
    #allArticlesModal .modal-body .col-md-5 {{ min-height: 0; display: flex; flex-direction: column; overflow: hidden; }}
    #allArticlesModal .col-md-7 {{ min-height: 0; }}
    #allArticlesListWrap {{ height: 55vh; max-height: 100%; overflow-y: scroll !important; overflow-x: hidden; -webkit-overflow-scrolling: touch; overscroll-behavior: contain; flex-shrink: 0; }}
    #allArticlesList .list-group-item.active .btn-domain-sibling {{ background: #fff; color: #212529; border: 1px solid rgba(0,0,0,0.2); }}
    #allArticlesList .list-group-item.active .btn-domain-sibling.btn-primary {{ background: #fff; color: #0d6efd; border: 1px solid #0d6efd; font-weight: 600; }}
    .domain-search-suggestions {{ border-top: 2px solid #6C8AE4; }}
    .domain-suggestion-item:hover {{ background-color: #f8f9fa; }}
    </style>
    <h2 class="mb-4">Domains</h2>
    {"<nav aria-label='breadcrumb'><ol class='breadcrumb'><li class='breadcrumb-item'><a href='/admin/domains'>All Domains</a></li>" + "".join(f"<li class='breadcrumb-item'><a href='/admin/domains?group_id={bc['id']}'>{bc['name']}</a></li>" for bc in (group_hierarchy_path or [])) + "<li class='breadcrumb-item active'>Filtered</li></ol></nav>" if group_hierarchy_path else ""}
    {_build_group_filter_alert(group_hierarchy_path, len(domains)) if group_hierarchy_path else ""}
    <div id="running-tasks-panel" class="mb-3" style="display:none"></div>
    {('<div class="alert alert-warning alert-dismissible fade show" role="alert" style="max-width:540px">' + html.escape(request.args.get("add_error","")) + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>') if request.args.get("add_error") else ""}
    {('<div class="alert alert-danger alert-dismissible fade show" role="alert" style="max-width:540px">' + html.escape(request.args.get("error","")) + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>') if request.args.get("error") else ""}
    {('<div class="alert alert-success alert-dismissible fade show" role="alert" style="max-width:540px">' + html.escape(request.args.get("success","")) + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>') if request.args.get("success") else ""}
    <div class="mb-3 d-flex gap-2 align-items-center flex-wrap">
      <div class="position-relative" style="max-width:400px;flex:1">
        <input type="text" id="domainSearch" class="form-control" placeholder="Search domains or groups..." autocomplete="off">
        <div id="domainSearchSuggestions" class="position-absolute w-100 bg-white border rounded shadow-sm domain-search-suggestions" style="display:none;max-height:350px;overflow-y:auto;z-index:1000;top:100%;margin-top:2px"></div>
      </div>
      <button type="button" class="btn btn-outline-secondary btn-sm" onclick="clearDomainSearch()">Clear Search</button>
      <div class="ms-auto d-flex gap-2">
        <button type="button" class="btn btn-outline-warning btn-sm" onclick="clearAllGroups()" title="Remove all domains from all groups (domains remain)" {('style="display:none"' if filter_group_id else '')}>🔓 Ungroup All</button>
        <button type="button" class="btn btn-outline-danger btn-sm" onclick="deleteAllDomains()" title="Delete all domains permanently" {('style="display:none"' if filter_group_id else '')}>🗑️ Delete All Domains</button>
        <button type="button" class="btn btn-outline-warning btn-sm" onclick="clearCurrentGroup()" title="Remove all domains from current group" {('style="display:none"' if not filter_group_id else '')}>🔓 Ungroup This Group</button>
        <button type="button" class="btn btn-outline-danger btn-sm" onclick="deleteCurrentGroupDomains()" title="Delete all domains in this group" {('style="display:none"' if not filter_group_id else '')}>🗑️ Delete Group Domains</button>
      </div>
    </div>
    <div class="d-flex flex-wrap gap-2 mb-4 align-items-center">
      <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-toggle="collapse" data-bs-target="#bulkAddCard">Bulk add domains</button>
      {('<button type="button" class="btn btn-outline-success btn-sm" data-bs-toggle="collapse" data-bs-target="#distributeTitlesCard">📝 Distribute Titles</button>') if filter_group_id else ''}
      {('<button type="button" class="btn btn-primary btn-sm" onclick="openBulkAllGroupsModal()" title="Run for all groups (same as Database Management)">Run all groups</button>') if not filter_group_id and any(d.get("group_id") for d in domains) else ""}
      {run_this_group_btn_html}
      <button type="button" class="btn btn-outline-primary btn-sm" onclick="openAllArticlesModal()" title="List all articles (filter by domain, default not validated)">Articles</button>
    </div>

    <div class="collapse mb-4" id="bulkAddCard">
      <div class="card">
        <div class="card-body">
          <form method="post" action="/admin/domains/bulk-add" id="bulkAddForm" onsubmit="return validateBulkAdd(event)">
            <div class="mb-2">
              <label class="form-label small fw-medium">Domains (one per line)</label>
              <textarea name="domains" id="bulkDomainsInput" class="form-control font-monospace small" rows="4" placeholder="example1.com&#10;example2.com&#10;(no https:// or www needed)" style="min-width: 320px;"></textarea>
            </div>
            {'<input type="hidden" name="target_group_id" value="' + str(filter_group_id) + '">' if filter_group_id else '''
            <div class="mb-2">
              <label class="form-label small fw-medium">Assign to Group <span class="text-danger">*</span></label>
              <select name="target_group_id" class="form-select form-select-sm" style="max-width: 320px;" required>
                <option value="">-- Select Group --</option>
                ''' + group_opts + '''
              </select>
              <div class="form-text small">All domains will be added to this group</div>
            </div>
            '''}
            <button type="submit" class="btn btn-primary btn-sm">Bulk Add</button>
          </form>
        </div>
      </div>
    </div>
    
    <div class="collapse mb-4" id="distributeTitlesCard">
      <div class="card">
        <div class="card-body">
          <h6 class="mb-3">📝 Distribute Titles to Group Domains</h6>
          <form method="post" action="/admin/titles/distribute">
            <input type="hidden" name="group_id" value="{filter_group_id if filter_group_id else ''}">
            <div class="mb-2">
              <label class="form-label small fw-medium">Titles (one per line)</label>
              <textarea name="titles" class="form-control font-monospace small" rows="8" placeholder="Best Chocolate Cake Recipe&#10;Easy Pasta Carbonara&#10;Homemade Pizza Dough&#10;..." style="min-width: 320px;" required></textarea>
              <div class="form-text small">
                Each title will be distributed to all domains in subgroups with exactly 4 domains (A, B, C, D).
                Titles are distributed round-robin across valid subgroups.
              </div>
            </div>
            <button type="submit" class="btn btn-success btn-sm">Distribute Titles</button>
          </form>
        </div>
      </div>
    </div>
    
    <script>
    function validateBulkAdd(event) {{
      const textarea = document.getElementById('bulkDomainsInput');
      const domainsText = textarea.value.trim();
      
      if (!domainsText) {{
        alert('Please enter at least one domain.');
        return false;
      }}
      
      // Count non-empty lines
      const domains = domainsText.split('\\n').filter(line => line.trim() !== '');
      const count = domains.length;
      
      // Check if number is not divisible by 4
      const remainder = count % 4;
      
      if (remainder !== 0) {{
        const completeGroups = Math.floor(count / 4);
        const message = `You are adding ${{count}} domain(s).\\n\\n` +
                       `This will create ${{completeGroups}} complete group(s) of 4 domains, ` +
                       `with ${{remainder}} domain(s) remaining in an incomplete group.\\n\\n` +
                       `Do you want to continue?`;
        
        if (!confirm(message)) {{
          return false;
        }}
      }}
      
      return true;
    }}
    </script>

    <div id="cfRefreshStatus" class="alert alert-info py-2 mb-2" style="display:none;"><span class="spinner-border spinner-border-sm me-2" role="status"></span><span id="cfRefreshStatusText">Updating Cloudflare status for all domains...</span></div>
    <div class="table-responsive">
    <table class="table table-sm table-hover table-bordered domains-table"><thead class="table-light"><tr><th class="col-id">#</th><th class="col-domain">Domain</th><th class="col-cf">CF</th><th class="col-colors">Colors</th><th class="col-fonts">Fonts</th><th class="col-categories">Categories</th><th class="col-writers">Writers</th><th class="col-pins">Pins</th><th class="col-theme">Theme</th><th class="col-article">Article</th><th class="col-stats">Stats</th><th class="col-last-deploy">Deployed</th><th class="col-actions">Actions</th></tr></thead><tbody>{rows_html}</tbody></table>
    </div>

    <div id="articleEditorModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Article Template — <span id="articleEditorDomainUrl"></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" id="articleEditorBody">
            <iframe id="articleEditorIframe" src="about:blank" title="Article editor"></iframe>
          </div>
        </div>
      </div>
    </div>
    <div id="templateExampleModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-scrollable" style="max-width:95%;height:90vh;">
        <div class="modal-content" style="height:90vh; background: #f8f9fa;">
          <div class="modal-header py-2">
            <h5 class="modal-title">Preview All Generators <span id="templateExampleDomainInfo" class="text-muted ms-2" style="font-size: 0.9rem;"></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-3 overflow-auto" id="templateExampleBody" style="height:calc(90vh - 60px);">
            <div id="templateExampleContent" class="row g-4"></div>
          </div>
        </div>
      </div>
    </div>
    <div id="pinEditorModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Pin Editor — <span id="pinEditorDomainUrl"></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-0" id="pinEditorBody" style="min-height:500px;">
            <iframe id="pinEditorIframe" src="about:blank" title="Pin editor"></iframe>
          </div>
        </div>
      </div>
    </div>
    
    <div id="writersModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Manage Writers</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div id="writersContainer"></div>
            <button type="button" class="btn btn-success btn-sm mt-3" id="addWriterBtn">+ Add Writer</button>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" id="saveWritersBtn">Save Writers</button>
          </div>
        </div>
      </div>
    </div>
    <div id="categoriesModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Categories — <span id="categoriesModalDomainUrl" class="text-muted">—</span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <label class="form-label small">One category per line (e.g. dessert, breakfast, main course)</label>
            <textarea id="categoriesModalTextarea" class="form-control font-monospace" rows="8" placeholder="dessert&#10;breakfast&#10;main course"></textarea>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" id="saveCategoriesBtn">Save Categories</button>
          </div>
        </div>
      </div>
    </div>
    <div id="themeStepperModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-scrollable" style="max-width:900px;">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Theme — <span id="themeStepperDomainUrl" class="text-muted">—</span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <input type="hidden" id="themeStepperDomainId" value="">
            <ul class="theme-stepper-nav nav nav-pills nav-fill mb-3 small" id="themeStepperNav" role="tablist">
              <li class="nav-item" role="presentation"><button class="nav-link rounded-0 active" id="theme-step-1-tab" data-bs-toggle="pill" data-bs-target="#theme-step-1" type="button" role="tab">1. Header</button></li>
              <li class="nav-item" role="presentation"><button class="nav-link rounded-0" id="theme-step-2-tab" data-bs-toggle="pill" data-bs-target="#theme-step-2" type="button" role="tab">2. Footer</button></li>
              <li class="nav-item" role="presentation"><button class="nav-link rounded-0" id="theme-step-3-tab" data-bs-toggle="pill" data-bs-target="#theme-step-3" type="button" role="tab">3. Sidebar</button></li>
              <li class="nav-item" role="presentation"><button class="nav-link rounded-0" id="theme-step-4-tab" data-bs-toggle="pill" data-bs-target="#theme-step-4" type="button" role="tab">4. Category</button></li>
              <li class="nav-item" role="presentation"><button class="nav-link rounded-0" id="theme-step-5-tab" data-bs-toggle="pill" data-bs-target="#theme-step-5" type="button" role="tab">5. Writer</button></li>
            </ul>
            <div class="tab-content" id="themeStepperContent">
              <div class="tab-pane fade show active" id="theme-step-1" role="tabpanel"><div class="theme-preview-grid" id="themePreviewGrid1"></div></div>
              <div class="tab-pane fade" id="theme-step-2" role="tabpanel"><div class="theme-preview-grid" id="themePreviewGrid2"></div></div>
              <div class="tab-pane fade" id="theme-step-3" role="tabpanel"><div class="theme-preview-grid" id="themePreviewGrid3"></div></div>
              <div class="tab-pane fade" id="theme-step-4" role="tabpanel"><div class="theme-preview-grid" id="themePreviewGrid4"></div></div>
              <div class="tab-pane fade" id="theme-step-5" role="tabpanel"><div class="theme-preview-grid" id="themePreviewGrid5"></div></div>
            </div>
          </div>
          <div class="modal-footer py-2 d-flex justify-content-between">
            <button type="button" class="btn btn-outline-secondary btn-sm" id="themeStepperBackBtn" disabled>Back</button>
            <button type="button" class="btn btn-primary btn-sm" id="themeStepperNextBtn">Next</button>
            <button type="button" class="btn btn-success btn-sm" id="themeStepperSaveBtn" style="display:none;">Save theme</button>
          </div>
        </div>
      </div>
    </div>
    <div id="statsArticlesModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header py-1 px-2 d-flex flex-column gap-1">
            <div class="d-flex align-items-center justify-content-between gap-2 w-100">
              <h6 class="modal-title mb-0" id="statsArticlesModalTitle">Articles</h6>
              <span id="statsArticlesModalRunGroup"></span>
              <button type="button" class="btn-close btn-close-sm" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div id="statsArticlesModalFilter" class="d-flex gap-1 small d-none"></div>
          </div>
          <div class="modal-body p-2" id="statsArticlesModalBody" style="max-height:70vh;overflow-y:auto;">
            <div class="stats-articles-grid" id="statsArticlesGrid"></div>
          </div>
        </div>
      </div>
    </div>
    <div id="domainArticlesModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-xl" style="max-width:95%;height:90vh;margin:2vh auto;">
        <div class="modal-content d-flex flex-column" style="height:90vh;">
          <div class="modal-header py-2 flex-shrink-0">
            <h5 class="modal-title" id="domainArticlesModalTitle">Articles</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-2 d-flex flex-column" id="domainArticlesModalBody">
            <div class="d-flex flex-wrap align-items-center gap-2 mb-2 flex-shrink-0">
              <span class="small text-muted" id="domainArticlesModalCount">—</span>
              <span class="small text-muted">Filter:</span>
              <div class="btn-group btn-group-sm" role="group" id="domainArticlesFilterGroup">
                <input type="radio" class="btn-check" name="domainArticlesValidatedFilter" id="domainArticlesFilterNot" value="0" checked>
                <label class="btn btn-outline-secondary btn-sm" for="domainArticlesFilterNot">Not validated</label>
                <input type="radio" class="btn-check" name="domainArticlesValidatedFilter" id="domainArticlesFilterYes" value="1">
                <label class="btn btn-outline-secondary btn-sm" for="domainArticlesFilterYes">Validated</label>
                <input type="radio" class="btn-check" name="domainArticlesValidatedFilter" id="domainArticlesFilterAll" value="all">
                <label class="btn btn-outline-secondary btn-sm" for="domainArticlesFilterAll">All</label>
                <input type="radio" class="btn-check" name="domainArticlesValidatedFilter" id="domainArticlesFilterEmpty" value="empty">
                <label class="btn btn-outline-secondary btn-sm" for="domainArticlesFilterEmpty">Not generated yet</label>
              </div>
            </div>
            <div class="row g-2 flex-grow-1 overflow-hidden" style="min-height:0;">
              <div class="col-md-5 d-flex flex-column overflow-hidden" style="min-height:0;">
                <div id="domainArticlesListWrap" class="border rounded overflow-auto" style="min-height:0;flex:1 1 0%;height:0;">
                  <ul class="list-group list-group-flush" id="domainArticlesList"></ul>
                  <div id="domainArticlesListLoading" class="text-center py-3 text-muted small" style="display:none;">Loading more…</div>
                </div>
              </div>
              <div class="col-md-7 d-flex flex-column overflow-hidden" style="min-height:0;">
                <p class="small fw-bold mb-1 flex-shrink-0 d-flex flex-wrap align-items-center gap-1">Article HTML <span id="domainArticlesHtmlMeta" class="text-muted fw-normal ms-1"></span><span class="ms-2 fw-normal small"><label class="mb-0"><input type="checkbox" id="domainArticlesAutoScrollCheck"> Smooth scroll</label> <input type="number" id="domainArticlesAutoScrollSec" min="1" step="0.5" value="5" style="width:3.5em" class="form-control form-control-sm d-inline-block" title="Seconds to scroll from top to bottom (one pass)"> s to bottom</span></p>
                <div id="domainArticlesHtmlWrap" class="border rounded p-2 bg-light" style="min-height:200px;flex:1 1 0%;height:0;max-height:65vh;overflow-y:auto;overflow-x:hidden;">
                  <p class="text-muted small mb-0" id="domainArticlesHtmlPlaceholder">Click an article to view HTML.</p>
                  <div id="domainArticlesHtmlContent" style="display:none;"></div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer py-2 d-flex align-items-center justify-content-between border-top flex-shrink-0">
            <button type="button" class="btn btn-outline-secondary btn-sm" id="domainArticlesPrevBtn" disabled>Previous</button>
            <span class="small text-muted" id="domainArticlesPosition">0 of 0</span>
            <div class="btn-group btn-group-sm">
              <button type="button" class="btn btn-outline-secondary btn-sm" id="domainArticlesNextBtn" disabled>Next</button>
              <button type="button" class="btn btn-outline-secondary btn-sm dropdown-toggle dropdown-toggle-split" id="domainArticlesNextDropdownToggle" data-bs-toggle="dropdown" aria-expanded="false" title="More actions" disabled><span class="visually-hidden">More</span></button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><button type="button" class="dropdown-item" id="domainArticlesValidateNextBtn" title="Mark current as validated and go to next">Validate &amp; next</button></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div id="allArticlesModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-xl" style="max-width:95%;height:90vh;margin:2vh auto;">
        <div class="modal-content d-flex flex-column" style="height:90vh;">
          <div class="modal-header py-2 flex-shrink-0">
            <h5 class="modal-title" id="allArticlesModalTitle">All Articles</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-2 d-flex flex-column" id="allArticlesModalBody">
            <div class="d-flex flex-wrap align-items-center gap-2 mb-2 flex-shrink-0">
              <span class="small text-muted" id="allArticlesModalCount">—</span>
              <span class="small text-muted">Domain:</span>
              <select class="form-select form-select-sm" id="allArticlesDomainSelect" style="max-width:200px;"><option value="">All domains</option></select>
              <span class="small text-muted">Validated:</span>
              <div class="btn-group btn-group-sm" role="group">
                <input type="radio" class="btn-check" name="allArticlesValidatedFilter" id="allArticlesFilterNot" value="0" checked>
                <label class="btn btn-outline-secondary btn-sm" for="allArticlesFilterNot">Not validated</label>
                <input type="radio" class="btn-check" name="allArticlesValidatedFilter" id="allArticlesFilterYes" value="1">
                <label class="btn btn-outline-secondary btn-sm" for="allArticlesFilterYes">Validated</label>
                <input type="radio" class="btn-check" name="allArticlesValidatedFilter" id="allArticlesFilterAll" value="all">
                <label class="btn btn-outline-secondary btn-sm" for="allArticlesFilterAll">All</label>
              </div>
              <button type="button" class="btn btn-primary btn-sm" id="allArticlesTestContentBtn" title="Run content for first article of each filtered domain">Test content</button>
              <button type="button" class="btn btn-success btn-sm" id="allArticlesValidateNextBtn" title="Mark current as validated and go to next">Validate &amp; next</button>
            </div>
            <div class="row g-2 flex-grow-1 overflow-hidden" style="min-height:0;">
              <div class="col-md-5 d-flex flex-column overflow-hidden" style="min-height:0;flex:1 1 0;">
                <div id="allArticlesListWrap" class="border rounded" style="height:55vh;overflow-y:scroll;overflow-x:hidden;">
                  <ul class="list-group list-group-flush" id="allArticlesList"></ul>
                  <div id="allArticlesListLoading" class="text-center py-3 text-muted small" style="display:none;">Loading more…</div>
                </div>
              </div>
              <div class="col-md-7 d-flex flex-column overflow-hidden" style="min-height:0;">
                <p class="small fw-bold mb-1 flex-shrink-0 d-flex flex-wrap align-items-center gap-1">Article HTML <span id="allArticlesHtmlMeta" class="text-muted fw-normal ms-1"></span><span class="ms-2 fw-normal small"><label class="mb-0"><input type="checkbox" id="allArticlesAutoScrollCheck"> Smooth scroll</label> <input type="number" id="allArticlesAutoScrollSec" min="1" step="0.5" value="5" style="width:3.5em" class="form-control form-control-sm d-inline-block" title="Seconds to scroll from top to bottom (one pass)"> s to bottom</span></p>
                <div id="allArticlesHtmlWrap" class="border rounded p-2 bg-light" style="min-height:200px;flex:1 1 0%;height:0;max-height:65vh;overflow-y:auto;overflow-x:hidden;">
                  <p class="text-muted small mb-0" id="allArticlesHtmlPlaceholder">Click an article to view HTML.</p>
                  <div id="allArticlesHtmlContent" style="display:none;"></div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer py-2 d-flex align-items-center justify-content-between border-top flex-shrink-0">
            <button type="button" class="btn btn-outline-secondary btn-sm" id="allArticlesPrevBtn" disabled>Previous</button>
            <span class="small text-muted" id="allArticlesPosition">0 of 0</span>
            <button type="button" class="btn btn-outline-secondary btn-sm" id="allArticlesNextBtn" disabled>Next</button>
          </div>
        </div>
      </div>
    </div>
    <div id="cloudflareDnsModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Cloudflare DNS Setup — <span id="cfDnsDomainUrl"></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div id="cfDnsStatus" class="mb-3"></div>
            <div id="cfDnsNameservers" class="mb-3" style="display:none;">
              <label class="form-label small fw-bold">Add these nameservers at your domain registrar:</label>
              <div id="cfDnsNsList" class="bg-light p-2 rounded"></div>
              <button type="button" class="btn btn-sm btn-outline-secondary mt-2" id="cfDnsCopyAll">Copy all</button>
            </div>
            <button type="button" class="btn btn-primary w-100" id="cfDnsSetupBtn">🚀 Setup Cloudflare (zone + DNS + Pages)</button>
          </div>
        </div>
      </div>
    </div>
    <div id="cloudflareInfoModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Cloudflare Info — <span id="cloudflareInfoDomainUrl"></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div id="cloudflareInfoSummary" class="mb-3" style="display:none;"></div>
            <details class="mb-2"><summary class="small text-muted" style="cursor:pointer;">Raw JSON</summary>
            <pre id="cloudflareInfoJson" class="bg-dark text-light p-3 rounded small mt-1" style="max-height:50vh;overflow:auto;font-size:0.75rem;"></pre>
            </details>
          </div>
        </div>
      </div>
    </div>
    <div id="editDomainTextModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Edit domain (URL)</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <input type="hidden" id="editDomainTextId">
            <div class="mb-2">
              <label class="form-label small">Domain URL</label>
              <input type="text" id="editDomainTextUrl" class="form-control" placeholder="example.com">
              <div class="form-text text-muted small">Enter domain only — no https:// or www needed</div>
              <div id="editDomainTextError" class="text-danger small mt-1"></div>
            </div>
          </div>
          <div class="modal-footer py-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" id="editDomainTextSaveBtn">Save</button>
          </div>
        </div>
      </div>
    </div>
    <div id="changeGroupModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Change Domain Group</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <input type="hidden" id="changeGroupDomainId">
            <div class="mb-2">
              <label class="form-label small">Select Group</label>
              <select id="changeGroupSelect" class="form-select">
                <option value="">-- No Group (Standalone) --</option>
              </select>
              <div class="form-text text-muted small">Choose a parent group for this domain</div>
              <div id="changeGroupError" class="text-danger small mt-1"></div>
            </div>
          </div>
          <div class="modal-footer py-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" id="changeGroupSaveBtn" class="btn btn-primary">Save</button>
          </div>
        </div>
      </div>
    </div>
    <div id="cfVersionsModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Deployments — <span id="cfVersionsDomainUrl"></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-2">
            <div id="cfVersionsStatus" class="mb-2"></div>
            <div id="cfVersionsList"></div>
          </div>
        </div>
      </div>
    </div>
    <div id="domainPagesModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header py-2 d-flex justify-content-between align-items-center">
            <h5 class="modal-title mb-0">Domain Pages — <span id="domainPagesDomainUrl"></span></h5>
            <div class="d-flex gap-1 align-items-center">
              <button type="button" class="btn btn-sm btn-primary" id="domainPagesGenerateAllBtn" title="Generate all 8 pages at once">Generate All</button>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
          </div>
          <div class="modal-body">
            <div class="d-flex align-items-center gap-2 mb-3">
              <label class="form-label small mb-0 fw-bold text-nowrap">Page Theme:</label>
              <select id="domainPageThemeSelect" class="form-select form-select-sm" style="max-width:240px">
                <option value="">Loading...</option>
              </select>
              <span class="small text-muted">Theme applies to <strong>all pages + header, footer, sidebar, index &amp; category</strong> for a cohesive design.</span>
            </div>
            <div id="domainPagesStatus" class="small text-muted mb-2"></div>
            <table class="table table-sm align-middle">
              <thead><tr><th style="width:160px">Page</th><th>Actions</th></tr></thead>
              <tbody id="domainPagesTableBody">
                <tr data-slug="about-us"><td>About Us</td><td><button type="button" class="btn btn-sm btn-primary page-gen-btn">Generate</button><a href="#" class="btn btn-sm btn-outline-secondary page-view-btn ms-1" target="_blank" style="display:none;">View</a><button type="button" class="btn btn-sm btn-outline-warning page-regenerate-btn ms-1" style="display:none;">Regenerate</button><span class="page-status ms-1"></span></td></tr>
                <tr data-slug="terms-of-use"><td>Terms of Use</td><td><button type="button" class="btn btn-sm btn-primary page-gen-btn">Generate</button><a href="#" class="btn btn-sm btn-outline-secondary page-view-btn ms-1" target="_blank" style="display:none;">View</a><button type="button" class="btn btn-sm btn-outline-warning page-regenerate-btn ms-1" style="display:none;">Regenerate</button><span class="page-status ms-1"></span></td></tr>
                <tr data-slug="privacy-policy"><td>Privacy Policy</td><td><button type="button" class="btn btn-sm btn-primary page-gen-btn">Generate</button><a href="#" class="btn btn-sm btn-outline-secondary page-view-btn ms-1" target="_blank" style="display:none;">View</a><button type="button" class="btn btn-sm btn-outline-warning page-regenerate-btn ms-1" style="display:none;">Regenerate</button><span class="page-status ms-1"></span></td></tr>
                <tr data-slug="gdpr-policy"><td>GDPR Policy</td><td><button type="button" class="btn btn-sm btn-primary page-gen-btn">Generate</button><a href="#" class="btn btn-sm btn-outline-secondary page-view-btn ms-1" target="_blank" style="display:none;">View</a><button type="button" class="btn btn-sm btn-outline-warning page-regenerate-btn ms-1" style="display:none;">Regenerate</button><span class="page-status ms-1"></span></td></tr>
                <tr data-slug="cookie-policy"><td>Cookie Policy</td><td><button type="button" class="btn btn-sm btn-primary page-gen-btn">Generate</button><a href="#" class="btn btn-sm btn-outline-secondary page-view-btn ms-1" target="_blank" style="display:none;">View</a><button type="button" class="btn btn-sm btn-outline-warning page-regenerate-btn ms-1" style="display:none;">Regenerate</button><span class="page-status ms-1"></span></td></tr>
                <tr data-slug="copyright-policy"><td>Copyright Policy</td><td><button type="button" class="btn btn-sm btn-primary page-gen-btn">Generate</button><a href="#" class="btn btn-sm btn-outline-secondary page-view-btn ms-1" target="_blank" style="display:none;">View</a><button type="button" class="btn btn-sm btn-outline-warning page-regenerate-btn ms-1" style="display:none;">Regenerate</button><span class="page-status ms-1"></span></td></tr>
                <tr data-slug="disclaimer"><td>Disclaimer</td><td><button type="button" class="btn btn-sm btn-primary page-gen-btn">Generate</button><a href="#" class="btn btn-sm btn-outline-secondary page-view-btn ms-1" target="_blank" style="display:none;">View</a><button type="button" class="btn btn-sm btn-outline-warning page-regenerate-btn ms-1" style="display:none;">Regenerate</button><span class="page-status ms-1"></span></td></tr>
                <tr data-slug="contact-us"><td>Contact Us</td><td><button type="button" class="btn btn-sm btn-primary page-gen-btn">Generate</button><a href="#" class="btn btn-sm btn-outline-secondary page-view-btn ms-1" target="_blank" style="display:none;">View</a><button type="button" class="btn btn-sm btn-outline-warning page-regenerate-btn ms-1" style="display:none;">Regenerate</button><span class="page-status ms-1"></span></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <div id="colorsModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Domain Colors — <span id="colorsDomainName"></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <input type="hidden" id="colorsDomainId">
            <div class="row g-2 mb-2">
              <div class="col-6"><label class="form-label small">Primary</label><div class="d-flex gap-1"><input type="color" id="c_primary" class="form-control form-control-color" style="width:48px;height:38px"><input type="text" id="t_primary" class="form-control" placeholder="#6C8AE4"></div></div>
              <div class="col-6"><label class="form-label small">Secondary</label><div class="d-flex gap-1"><input type="color" id="c_secondary" class="form-control form-control-color" style="width:48px;height:38px"><input type="text" id="t_secondary" class="form-control" placeholder="#9C6ADE"></div></div>
              <div class="col-6"><label class="form-label small">Background</label><div class="d-flex gap-1"><input type="color" id="c_background" class="form-control form-control-color" style="width:48px;height:38px"><input type="text" id="t_background" class="form-control" placeholder="#FFFFFF"></div></div>
              <div class="col-6"><label class="form-label small">Text primary</label><div class="d-flex gap-1"><input type="color" id="c_text_primary" class="form-control form-control-color" style="width:48px;height:38px"><input type="text" id="t_text_primary" class="form-control" placeholder="#2D2D2D"></div></div>
              <div class="col-6"><label class="form-label small">Text secondary</label><div class="d-flex gap-1"><input type="color" id="c_text_secondary" class="form-control form-control-color" style="width:48px;height:38px"><input type="text" id="t_text_secondary" class="form-control" placeholder="#5A5A5A"></div></div>
              <div class="col-6"><label class="form-label small">Border</label><div class="d-flex gap-1"><input type="color" id="c_border" class="form-control form-control-color" style="width:48px;height:38px"><input type="text" id="t_border" class="form-control" placeholder="#E2E8FF"></div></div>
            </div>
            <button type="button" class="btn btn-sm btn-outline-secondary" id="colorsRandomBtn" title="AI palette: matching colors with readable contrast">Random palette</button>
          </div>
          <div class="modal-footer py-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" id="colorsSaveBtn">Save</button>
          </div>
        </div>
      </div>
    </div>
    <div id="pinterestSetupModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header py-2">
            <h5 class="modal-title">Pinterest RSS — <span id="pinterestSetupDomainName"></span></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <input type="hidden" id="pinterestSetupDomainId">
            <p class="small text-muted mb-2">Connect this RSS feed in Pinterest. New articles are pinned automatically on Pinterest&apos;s schedule.</p>
            <div class="mb-3">
              <label class="form-label small fw-bold">RSS feed URL</label>
              <div class="input-group input-group-sm">
                <input type="text" id="pinterestFeedUrl" class="form-control" readonly>
                <button type="button" class="btn btn-outline-secondary" id="pinterestCopyFeedBtn" title="Copy">Copy</button>
              </div>
              <div class="form-text small">Pinterest: Settings → Create Pins in bulk → Auto-publish → Connect RSS feed. (App must be deployed so the URL is reachable.)</div>
            </div>
            <a href="https://www.pinterest.com" target="_blank" rel="noopener" class="btn btn-sm btn-outline-danger">Open Pinterest</a>
          </div>
          <div class="modal-footer py-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
    <script>
    window.allDomainsForArticles = {domains_json};
    window.SITE_TEMPLATES = {{}};
    window.openAllArticlesModal = function() {{}};
    document.addEventListener('DOMContentLoaded', function() {{
      fetch('/api/site-templates').then(function(r){{return r.json();}}).then(function(d){{window.SITE_TEMPLATES=d||{{}};}}).catch(function(){{}});

      /* --- Pin thumbnail hover preview --- */
      var pinHoverImg = document.createElement('img');
      pinHoverImg.className = 'pin-thumb-hover-preview';
      document.body.appendChild(pinHoverImg);
      document.querySelectorAll('.pin-thumb-wrap img.pin-thumb').forEach(function(img) {{
        img.addEventListener('mouseenter', function(e) {{
          pinHoverImg.src = this.src;
          pinHoverImg.style.display = 'block';
          var rect = this.getBoundingClientRect();
          pinHoverImg.style.left = (rect.right + 8) + 'px';
          pinHoverImg.style.top = Math.max(8, rect.top - 60) + 'px';
        }});
        img.addEventListener('mousemove', function(e) {{
          pinHoverImg.style.left = (e.clientX + 16) + 'px';
          pinHoverImg.style.top = Math.max(8, e.clientY - 60) + 'px';
        }});
        img.addEventListener('mouseleave', function() {{
          pinHoverImg.style.display = 'none';
        }});
      }});

      /* --- Page theme select: save on change --- */
      document.querySelectorAll('.page-theme-select').forEach(function(sel) {{
        sel.addEventListener('change', function() {{
          var domainId = this.getAttribute('data-domain-id');
          var theme = this.value;
          var original = this.getAttribute('data-original') || '';
          if (theme === original) return;
          var selectEl = this;
          selectEl.disabled = true;
          fetch('/api/domains/' + domainId + '/page-theme', {{
            method: 'PUT',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{theme: theme}})
          }})
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              if (d.success) {{
                selectEl.setAttribute('data-original', theme);
                selectEl.style.borderColor = '#198754';
                setTimeout(function() {{ selectEl.style.borderColor = ''; }}, 2000);
              }} else {{
                alert('Failed to save theme: ' + (d.error || 'Unknown error'));
                selectEl.value = original;
              }}
            }})
            .catch(function(e) {{
              alert('Error saving theme: ' + e);
              selectEl.value = original;
            }})
            .finally(function() {{ selectEl.disabled = false; }});
        }});
      }});
      if (typeof bootstrap === 'undefined') return;
      var pinModal = document.getElementById('pinEditorModal');
      var pinBsModal = pinModal ? new bootstrap.Modal(pinModal) : null;
      function esc(s) {{ return (s||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
      function openPinEditor(domainId, templateId) {{
        if (!domainId) return;
        document.getElementById('pinEditorDomainUrl').textContent = 'Domain ' + domainId;
        var iframe = document.getElementById('pinEditorIframe');
        var url = '/pin-editor?domain_id=' + domainId + '&embed=1';
        if (templateId) url += '&template_id=' + templateId;
        iframe.src = url;
        if (pinBsModal) pinBsModal.show();
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domains/' + domainId).then(r => r.json()).then(function(dom) {{
          document.getElementById('pinEditorDomainUrl').textContent = dom.domain_url || ('Domain ' + domainId);
        }}).catch(function() {{}}).finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }};
      pinModal.addEventListener('hidden.bs.modal', function() {{
        document.getElementById('pinEditorIframe').src = 'about:blank';
        if (typeof window.refreshDomainsAfterPinEditor === 'function') window.refreshDomainsAfterPinEditor();
      }});
      document.querySelectorAll('.pin-templates-cell').forEach(function(cell) {{
        cell.addEventListener('click', function(e) {{
          var delBtn = e.target.closest('.pin-del');
          if (delBtn) {{
            e.stopPropagation();
            var tid = delBtn.getAttribute('data-template-id');
            if (!tid) return;
            if (!confirm('Delete this pin template?')) return;
            fetch('/api/domain-templates/' + tid, {{ method: 'DELETE' }})
              .then(function(r) {{ return r.json(); }})
              .then(function(d) {{
                if (d.success) {{
                  var wrap = delBtn.closest('.pin-thumb-wrap');
                  if (wrap) wrap.remove();
                }} else {{
                  alert(d.error || 'Error deleting template');
                }}
              }})
              .catch(function(err) {{ alert('Error: ' + err); }});
            return;
          }}
          var t = e.target.closest('[data-domain-id]');
          if (!t) return;
          var domainId = t.getAttribute('data-domain-id');
          var templateId = t.getAttribute('data-template-id');
          if (t.classList.contains('pin-add')) templateId = null;
          openPinEditor(domainId, templateId);
        }});
      }});
      var editDomainTextModal = document.getElementById('editDomainTextModal');
      var editDomainTextBsModal = editDomainTextModal ? new bootstrap.Modal(editDomainTextModal) : null;
      document.addEventListener('click', function(e) {{
        var btn = e.target.closest('.edit-domain-text-btn');
        if (!btn) return;
        e.preventDefault();
        var domainId = btn.getAttribute('data-domain-id');
        var url = btn.getAttribute('data-domain-url') || '';
        document.getElementById('editDomainTextId').value = domainId;
        document.getElementById('editDomainTextUrl').value = url === '-' ? '' : url;
        if (editDomainTextBsModal) editDomainTextBsModal.show();
      }});
      document.getElementById('editDomainTextSaveBtn').addEventListener('click', function() {{
        var domainId = document.getElementById('editDomainTextId').value;
        var inp = document.getElementById('editDomainTextUrl');
        // Normalize: strip https://, http://, www.
        var raw = inp.value.trim();
        raw = raw.replace(/^https?:\/\//i, '').replace(/^www\./i, '').split('/')[0].split('?')[0].trim().toLowerCase();
        inp.value = raw;
        var errEl = document.getElementById('editDomainTextError');
        if (errEl) errEl.textContent = '';
        if (!domainId || !raw) return;
        var btn = this;
        btn.disabled = true;
        btn.textContent = 'Saving...';
        fetch('/api/domains/' + domainId, {{
          method: 'PUT',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ domain_url: raw }})
        }})
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.success) {{
              if (editDomainTextBsModal) editDomainTextBsModal.hide();
              var btn = document.querySelector('button[data-domain-id="' + domainId + '"].edit-domain-text-btn') || document.querySelector('button[data-domain-id="' + domainId + '"]');
              var link = btn ? btn.closest('tr').querySelector('.domain-url-link') : null;
              if (link) link.textContent = raw;
            }} else {{
              if (errEl) errEl.textContent = data.error || 'Save failed';
              else alert(data.error || 'Save failed');
            }}
          }})
          .catch(function(err) {{ if (errEl) errEl.textContent = err.message || 'Network error'; else alert(err.message); }})
          .finally(function() {{ btn.disabled = false; btn.textContent = 'Save'; }});
      }});
      
      // Clear single domain from group
      document.addEventListener('click', function(e) {{
        var btn = e.target.closest('.clear-group-btn');
        if (!btn) return;
        e.preventDefault();
        var domainId = btn.getAttribute('data-domain-id');
        if (!confirm('Remove this domain from its group?')) return;
        
        btn.disabled = true;
        btn.textContent = '...';
        
        fetch('/api/domains/' + domainId + '/change-group', {{
          method: 'PUT',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ group_id: null }})
        }})
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.success) {{
              location.reload();
            }} else {{
              alert(data.error || 'Failed to remove from group');
              btn.disabled = false;
              btn.textContent = '✖️';
            }}
          }})
          .catch(function(err) {{ 
            alert(err.message || 'Network error'); 
            btn.disabled = false;
            btn.textContent = '✖️';
          }});
      }});
      
      // Change Group Modal
      var changeGroupModal = document.getElementById('changeGroupModal');
      var changeGroupBsModal = changeGroupModal ? new bootstrap.Modal(changeGroupModal) : null;
      var allGroupsData = {all_groups_json};
      
      document.addEventListener('click', function(e) {{
        var btn = e.target.closest('.change-group-btn');
        if (!btn) return;
        e.preventDefault();
        var domainId = btn.getAttribute('data-domain-id');
        var currentGroup = btn.getAttribute('data-current-group') || '';
        document.getElementById('changeGroupDomainId').value = domainId;
        
        // Populate group select
        var sel = document.getElementById('changeGroupSelect');
        sel.innerHTML = '<option value="">-- No Group (Standalone) --</option>';
        allGroupsData.forEach(function(g) {{
          var opt = document.createElement('option');
          opt.value = g.id;
          opt.textContent = g.hierarchy || g.name;
          if (currentGroup && g.id == currentGroup) opt.selected = true;
          sel.appendChild(opt);
        }});
        
        if (changeGroupBsModal) changeGroupBsModal.show();
      }});
      
      document.getElementById('changeGroupSaveBtn').addEventListener('click', function() {{
        var domainId = document.getElementById('changeGroupDomainId').value;
        var groupId = document.getElementById('changeGroupSelect').value || null;
        var errEl = document.getElementById('changeGroupError');
        if (errEl) errEl.textContent = '';
        if (!domainId) return;
        
        var btn = this;
        btn.disabled = true;
        btn.textContent = 'Saving...';
        
        fetch('/api/domains/' + domainId + '/change-group', {{
          method: 'PUT',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ group_id: groupId }})
        }})
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.success) {{
              if (changeGroupBsModal) changeGroupBsModal.hide();
              location.reload(); // Reload to show updated group
            }} else {{
              if (errEl) errEl.textContent = data.error || 'Save failed';
              else alert(data.error || 'Save failed');
            }}
          }})
          .catch(function(err) {{ if (errEl) errEl.textContent = err.message || 'Network error'; else alert(err.message); }})
          .finally(function() {{ btn.disabled = false; btn.textContent = 'Save'; }});
      }});
      
      // Change group modal
      var changeGroupModal = document.getElementById('changeGroupModal');
      var changeGroupBsModal = changeGroupModal ? new bootstrap.Modal(changeGroupModal) : null;
      var allGroupsData = {all_groups_json};
      document.addEventListener('click', function(e) {{
        var btn = e.target.closest('.change-group-btn');
        if (!btn) return;
        e.preventDefault();
        var domainId = btn.getAttribute('data-domain-id');
        var currentGroup = btn.getAttribute('data-current-group') || '';
        document.getElementById('changeGroupDomainId').value = domainId;
        var sel = document.getElementById('changeGroupSelect');
        sel.innerHTML = '<option value="">-- No Group (Standalone) --</option>';
        allGroupsData.forEach(function(g) {{
          var opt = document.createElement('option');
          opt.value = g.id;
          opt.textContent = g.hierarchy || g.name;
          if (String(g.id) === String(currentGroup)) opt.selected = true;
          sel.appendChild(opt);
        }});
        if (changeGroupBsModal) changeGroupBsModal.show();
      }});
      document.getElementById('changeGroupSaveBtn').addEventListener('click', function() {{
        var domainId = document.getElementById('changeGroupDomainId').value;
        var groupId = document.getElementById('changeGroupSelect').value || null;
        var errEl = document.getElementById('changeGroupError');
        if (errEl) errEl.textContent = '';
        if (!domainId) return;
        var btn = this;
        btn.disabled = true;
        btn.textContent = 'Saving...';
        fetch('/api/domains/' + domainId + '/change-group', {{
          method: 'PUT',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ group_id: groupId }})
        }})
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.success) {{
              if (changeGroupBsModal) changeGroupBsModal.hide();
              location.reload();
            }} else {{
              if (errEl) errEl.textContent = data.error || 'Save failed';
              else alert(data.error || 'Save failed');
            }}
          }})
          .catch(function(err) {{ if (errEl) errEl.textContent = err.message || 'Network error'; else alert(err.message); }})
          .finally(function() {{ btn.disabled = false; btn.textContent = 'Save'; }});
      }});
      
      document.querySelectorAll('.deploy-cf-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (!domainId) return;
          var orig = this.innerHTML;
          this.disabled = true;
          this.innerHTML = '...';
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/' + domainId + '/deploy-cloudflare', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }} }})
            .then(function(r) {{
              return r.text().then(function(text) {{
                try {{ return JSON.parse(text); }} catch(e) {{ return {{ success: false, error: text && text.indexOf('<') >= 0 ? 'Server error (check console)' : text || 'Unknown error' }}; }}
              }});
            }})
            .then(function(data) {{
              if (data && data.success) {{
                if (data.url) {{
                  window.open(data.url, '_blank');
                  alert('Deployed! Live at: ' + data.url);
                }} else {{
                  alert('Deployed successfully.');
                }}
              }} else {{
                var errMsg = data && data.error ? data.error : 'Unknown error';
                if (data && data.traceback) console.error('Deploy traceback:', data.traceback);
                alert('Deploy failed: ' + errMsg);
              }}
            }})
            .catch(function(err) {{ alert('Deploy failed: ' + (err.message || 'Network error')); }})
            .finally(function() {{
              this.disabled = false;
              this.innerHTML = orig;
              if (typeof hideGlobalLoading === 'function') hideGlobalLoading();
            }}.bind(this));
        }});
      }});
      var cfDnsModal = document.getElementById('cloudflareDnsModal');
      var cfDnsBsModal = cfDnsModal ? new bootstrap.Modal(cfDnsModal) : null;
      var cfDnsDomainId = null;
      document.querySelector('.domains-table') && document.querySelector('.domains-table').addEventListener('click', function(e) {{
        var btn = e.target.closest('.cf-dns-btn');
        if (!btn) return;
        cfDnsDomainId = btn.getAttribute('data-domain-id');
        var url = btn.getAttribute('data-domain-url') || 'Domain ' + cfDnsDomainId;
        document.getElementById('cfDnsDomainUrl').textContent = url;
        document.getElementById('cfDnsStatus').innerHTML = '';
        document.getElementById('cfDnsNameservers').style.display = 'none';
        document.getElementById('cfDnsSetupBtn').disabled = false;
        document.getElementById('cfDnsSetupBtn').innerHTML = '🚀 Setup Cloudflare (zone + DNS + Pages)';
        if (cfDnsBsModal) cfDnsBsModal.show();
      }});
      document.getElementById('cfDnsSetupBtn') && document.getElementById('cfDnsSetupBtn').addEventListener('click', function() {{
        if (!cfDnsDomainId) return;
        var btn = this;
        btn.disabled = true;
        btn.innerHTML = '⏳ Working...';
        var statusEl = document.getElementById('cfDnsStatus');
        statusEl.innerHTML = '<div class="alert alert-info py-2 small mb-0"><b>Step 1/3</b> — Creating Cloudflare zone...</div>';
        fetch('/api/domains/' + cfDnsDomainId + '/cloudflare-setup-dns', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }} }})
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.success) {{
              var lines = [];
              lines.push('<b>✅ Zone:</b> ' + (data.zone_id || '').replace(/</g,'&lt;'));
              var dnsOk = data.dns_records_added && data.dns_records_added.length;
              if (dnsOk) {{
                lines.push('<b>✅ DNS records:</b> ' + data.dns_records_added.join(', '));
              }} else if (data.dns_errors && data.dns_errors.length) {{
                lines.push('<b>❌ DNS records failed:</b> ' + data.dns_errors.map(function(e){{return e.replace(/</g,'&lt;')}}).join('<br>&nbsp;&nbsp;') + '<br><small>Fix: add <b>Zone → DNS → Edit</b> permission to your Cloudflare API token, then click "Retry DNS".</small>');
              }} else {{
                lines.push('<b>⚠️ DNS records:</b> none added — token may be missing <b>Zone → DNS → Edit</b> permission. Click "Retry DNS" below.');
              }}
              if (data.domains_added && data.domains_added.length) {{
                lines.push('<b>✅ Pages domains:</b> ' + data.domains_added.join(', '));
              }} else {{
                lines.push('<b>ℹ️ Pages:</b> deploy your site first (☁️) to link the domain.');
              }}
              var alertClass = dnsOk ? 'alert-success' : 'alert-warning';
              statusEl.innerHTML = '<div class="alert ' + alertClass + ' py-2 small mb-2">' + lines.join('<br>') + '</div>'
                + (!dnsOk ? '<button type="button" class="btn btn-warning btn-sm mb-2 w-100" id="cfDnsRetryBtn">🔄 Retry: Add DNS records (CNAME @ and www)</button>' : '');
              var nsList = document.getElementById('cfDnsNsList');
              var ns = (data.name_servers || []);
              nsList.innerHTML = ns.map(function(n) {{ return '<div class="d-flex align-items-center gap-2 mb-1"><code class="flex-grow-1">' + (n.replace(/</g,'&lt;')) + '</code><button type="button" class="btn btn-sm btn-outline-secondary copy-ns-btn" data-ns="' + (n.replace(/"/g,'&quot;')) + '">Copy</button></div>'; }}).join('');
              document.getElementById('cfDnsNameservers').style.display = ns.length ? '' : 'none';
              document.getElementById('cfDnsCopyAll').setAttribute('data-ns-list', ns.join('\\n'));
              nsList.querySelectorAll('.copy-ns-btn').forEach(function(b) {{
                b.addEventListener('click', function() {{
                  navigator.clipboard.writeText(this.getAttribute('data-ns')).then(function() {{ b.textContent = 'Copied!'; setTimeout(function() {{ b.textContent = 'Copy'; }}, 800); }});
                }});
              }});
            }} else {{
              statusEl.innerHTML = '<div class="alert alert-danger py-2 small">' + (data.error || 'Unknown error').replace(/</g,'&lt;') + '</div>';
            }}
          }})
          .catch(function(err) {{
            statusEl.innerHTML = '<div class="alert alert-danger py-2 small">' + (err.message || 'Network error').replace(/</g,'&lt;') + '</div>';
          }})
          .finally(function() {{ btn.disabled = false; btn.innerHTML = '🚀 Setup Cloudflare (zone + DNS + Pages)'; }});
      }});
      document.getElementById('cfDnsCopyAll') && document.getElementById('cfDnsCopyAll').addEventListener('click', function() {{
        var list = this.getAttribute('data-ns-list') || '';
        if (list) navigator.clipboard.writeText(list).then(function() {{ alert('Copied nameservers!'); }});
      }});
      document.getElementById('cloudflareDnsModal') && document.getElementById('cloudflareDnsModal').addEventListener('click', function(e) {{
        var btn = e.target.closest('#cfDnsRetryBtn');
        if (!btn || !cfDnsDomainId) return;
        btn.disabled = true;
        btn.innerHTML = '⏳ Adding records...';
        fetch('/api/domains/' + cfDnsDomainId + '/cloudflare-add-dns-records', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }} }})
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.success) {{
              btn.outerHTML = '<div class="alert alert-success py-2 small mb-2">✅ DNS records added: ' + (data.records_added || []).join(', ') + '</div>';
            }} else {{
              btn.disabled = false;
              btn.innerHTML = '🔄 Retry: Add DNS records (CNAME @ and www)';
              document.getElementById('cfDnsStatus').insertAdjacentHTML('beforeend',
                '<div class="alert alert-danger py-2 small mt-1">❌ ' + (data.error || 'Unknown error').replace(/</g,'&lt;') + '</div>');
            }}
          }})
          .catch(function(err) {{
            btn.disabled = false;
            btn.innerHTML = '🔄 Retry: Add DNS records (CNAME @ and www)';
            document.getElementById('cfDnsStatus').insertAdjacentHTML('beforeend',
              '<div class="alert alert-danger py-2 small mt-1">❌ ' + (err.message || 'Network error') + '</div>');
          }});
      }});
      // ── Versions modal ──────────────────────────────────────────────────
      var cfVersionsModal = document.getElementById('cfVersionsModal');
      var cfVersionsBsModal = cfVersionsModal ? new bootstrap.Modal(cfVersionsModal) : null;
      var cfVersionsDomainId = null;
      document.querySelector('.domains-table') && document.querySelector('.domains-table').addEventListener('click', function(e) {{
        var btn = e.target.closest('.cf-versions-btn');
        if (!btn) return;
        cfVersionsDomainId = btn.getAttribute('data-domain-id');
        var url = btn.getAttribute('data-domain-url') || ('Domain ' + cfVersionsDomainId);
        document.getElementById('cfVersionsDomainUrl').textContent = url;
        document.getElementById('cfVersionsStatus').innerHTML = '<div class="text-muted small">Loading deployments...</div>';
        document.getElementById('cfVersionsList').innerHTML = '';
        if (cfVersionsBsModal) cfVersionsBsModal.show();
        cfVersionsLoad(cfVersionsDomainId);
      }});
      function cfVersionsLoad(domainId) {{
        fetch('/api/domains/' + domainId + '/cloudflare-deployments')
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            var statusEl = document.getElementById('cfVersionsStatus');
            var listEl = document.getElementById('cfVersionsList');
            if (!data.success) {{
              statusEl.innerHTML = '<div class="alert alert-danger py-2 small">' + (data.error || 'Failed').replace(/</g,'&lt;') + '</div>';
              return;
            }}
            statusEl.innerHTML = '';
            var deploys = data.deployments || [];
            if (!deploys.length) {{
              listEl.innerHTML = '<p class="text-muted small">No deployments found.</p>';
              return;
            }}
            var rows = deploys.map(function(d) {{
              var isLive = d.is_live;
              var statusBadge = d.status === 'success' ? '<span class="badge bg-success">success</span>'
                : d.status === 'failure' ? '<span class="badge bg-danger">failure</span>'
                : '<span class="badge bg-secondary">' + (d.status || '?') + '</span>';
              var liveBadge = isLive ? ' <span class="badge bg-warning text-dark">LIVE</span>' : '';
              var date = d.created_on ? d.created_on.replace('T',' ').substring(0,16) + ' UTC' : '';
              var previewLink = d.url ? '<a href="' + d.url.replace(/"/g,'&quot;') + '" target="_blank" class="btn btn-sm btn-outline-secondary">Preview</a>' : '';
              var setLiveBtn = (!isLive && d.status === 'success')
                ? '<button type="button" class="btn btn-sm btn-primary cf-set-live-btn" data-deployment-id="' + (d.id||'').replace(/"/g,'&quot;') + '">Set as live</button>'
                : '';
              return '<tr><td class="small font-monospace text-muted" style="max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="' + (d.id||'') + '">' + (d.id||'').substring(0,8) + '…</td>'
                + '<td class="small">' + date + '</td>'
                + '<td>' + statusBadge + liveBadge + '</td>'
                + '<td class="text-end">' + previewLink + ' ' + setLiveBtn + '</td></tr>';
            }}).join('');
            listEl.innerHTML = '<table class="table table-sm table-hover mb-0 small"><thead><tr><th>ID</th><th>Date</th><th>Status</th><th></th></tr></thead><tbody>' + rows + '</tbody></table>';
          }})
          .catch(function(err) {{
            document.getElementById('cfVersionsStatus').innerHTML = '<div class="alert alert-danger py-2 small">' + (err.message || 'Network error') + '</div>';
          }});
      }}
      document.getElementById('cfVersionsModal') && document.getElementById('cfVersionsModal').addEventListener('click', function(e) {{
        var btn = e.target.closest('.cf-set-live-btn');
        if (!btn || !cfVersionsDomainId) return;
        var deployId = btn.getAttribute('data-deployment-id');
        if (!deployId) return;
        btn.disabled = true;
        btn.textContent = '⏳ Setting...';
        fetch('/api/domains/' + cfVersionsDomainId + '/cloudflare-rollback/' + deployId, {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }} }})
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.success) {{
              document.getElementById('cfVersionsStatus').innerHTML = '<div class="alert alert-success py-2 small">✅ Deployment set as live. Refreshing list...</div>';
              setTimeout(function() {{
                document.getElementById('cfVersionsStatus').innerHTML = '';
                cfVersionsLoad(cfVersionsDomainId);
              }}, 2000);
            }} else {{
              btn.disabled = false;
              btn.textContent = 'Set as live';
              document.getElementById('cfVersionsStatus').innerHTML = '<div class="alert alert-danger py-2 small">❌ ' + (data.error || 'Failed').replace(/</g,'&lt;') + '</div>';
            }}
          }})
          .catch(function(err) {{
            btn.disabled = false;
            btn.textContent = 'Set as live';
            document.getElementById('cfVersionsStatus').innerHTML = '<div class="alert alert-danger py-2 small">❌ ' + (err.message || 'Network error') + '</div>';
          }});
      }});
      // ────────────────────────────────────────────────────────────────────
      var cfInfoModal = document.getElementById('cloudflareInfoModal');
      var cfInfoBsModal = cfInfoModal ? new bootstrap.Modal(cfInfoModal) : null;
      document.querySelectorAll('.cf-fetch-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (!domainId) return;
          var currentBtn = this;
          var orig = this.innerHTML;
          this.disabled = true;
          this.innerHTML = '...';
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/' + domainId + '/cloudflare-info', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }} }})
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{
              if (data && data.success) {{
                currentBtn.innerHTML = '✓';
                currentBtn.classList.remove('btn-outline-secondary', 'btn-outline-warning', 'btn-outline-danger');
                currentBtn.classList.add('btn-success');
                orig = '✓';
              }} else {{
                alert('Fetch failed: ' + (data && data.error ? data.error : 'Unknown error'));
              }}
            }})
            .catch(function(err) {{ alert('Fetch failed: ' + (err.message || 'Network error')); }})
            .finally(function() {{
              this.disabled = false;
              this.innerHTML = orig;
              if (typeof hideGlobalLoading === 'function') hideGlobalLoading();
            }}.bind(this));
        }});
      }});
      document.querySelector('.domains-table') && document.querySelector('.domains-table').addEventListener('click', function(e) {{
        var badge = e.target.closest('.cf-info-badge');
        if (!badge) return;
        var domainId = badge.getAttribute('data-domain-id');
        var raw = badge.getAttribute('data-cf-json') || '{{}}';
        var obj = {{}};
        try {{ obj = JSON.parse(raw); }} catch(err) {{ obj = {{}}; }}
        document.getElementById('cloudflareInfoJson').textContent = JSON.stringify(obj, null, 2);
        var domainLabel = (obj.domain_url || obj.project_name || 'Domain ' + domainId);
        document.getElementById('cloudflareInfoDomainUrl').textContent = domainLabel;
        var sum = document.getElementById('cloudflareInfoSummary');
        sum.style.display = '';
        var status = obj.status || '';
        var err = obj.error || '';
        var hint = '';
        if (err) {{
          var el = err.toLowerCase();
          if (el.indexOf('not configured') >= 0 || el.indexOf('cloudflare') >= 0 && el.indexOf('config') >= 0)
            hint = 'Add CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN to .env';
          else if (el.indexOf('404') >= 0 || el.indexOf('not found') >= 0 || el.indexOf('does not exist') >= 0 || (!obj.project && status === 'error'))
            hint = 'Deploy the site first — click the cloud (☁️) button to deploy to Cloudflare Pages';
          else if (el.indexOf('401') >= 0 || el.indexOf('unauthorized') >= 0)
            hint = 'Check CLOUDFLARE_API_TOKEN in .env — token may be invalid or expired';
          else if (el.indexOf('403') >= 0 || el.indexOf('forbidden') >= 0)
            hint = 'Check Cloudflare account permissions — token needs Workers and Pages access';
          else
            hint = 'See the error above; check Cloudflare dashboard and .env config';
        }} else if (status === 'down') {{
          var dr = obj.down_reason || '';
          if (dr) hint = 'Check failed: ' + dr + '. If the site loads in your browser, it may be Cloudflare blocking automated checks.';
          else hint = 'Site may be building or DNS not yet propagated. Check Cloudflare Pages dashboard.';
        }}
        var esc2 = function(s) {{ return (s||'').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }};
        var statusCls = status === 'up' ? 'success' : (status === 'down' || status === 'error' ? 'danger' : 'secondary');
        var html = '<div class="d-flex align-items-center gap-2 mb-2"><span class="badge bg-' + statusCls + ' px-2 py-1">' + (status || 'unknown') + '</span>' + (obj.project_name ? '<code class="small">' + esc2(obj.project_name) + '</code>' : '') + '</div>';
        if (err) html += '<div class="alert alert-danger py-2 mb-2 small"><strong>Error:</strong> ' + esc2(err).substring(0, 500) + '</div>';
        if (obj.check_details && obj.check_details.length) {{
          html += '<table class="table table-sm table-bordered mb-2 small"><thead><tr><th>URL</th><th style="width:90px">Status</th></tr></thead><tbody>';
          obj.check_details.forEach(function(d) {{
            var rowCls = d.up ? 'table-success' : 'table-danger';
            var icon = d.up ? '✅ up' : '❌ down';
            var reason = (!d.up && d.reason) ? ' <span class=\\'text-muted\\'>— ' + esc2(d.reason) + '</span>' : '';
            html += '<tr class="' + rowCls + '"><td><a href="' + esc2(d.url) + '" target="_blank" rel="noopener">' + esc2(d.url) + '</a></td><td>' + icon + reason + '</td></tr>';
          }});
          html += '</tbody></table>';
        }}
        if (hint) html += '<div class="alert alert-warning py-2 mb-0 small"><strong>What to do:</strong> ' + hint + '</div>';
        sum.innerHTML = html;
        if (cfInfoBsModal) cfInfoBsModal.show();
      }});
      (function cfAutoRefreshAll() {{
        var btns = document.querySelectorAll('.cf-fetch-btn');
        if (btns.length === 0) return;
        var ids = [];
        btns.forEach(function(b) {{ var id = b.getAttribute('data-domain-id'); if (id) ids.push(id); }});
        if (ids.length === 0) return;
        var bar = document.getElementById('cfRefreshStatus');
        var txt = document.getElementById('cfRefreshStatusText');
        if (bar) bar.style.display = '';
        var done = 0;
        var concurrency = 3;
        function renderCfCell(id, cf) {{
          var status = (cf && cf.status) || '';
          var raw = JSON.stringify(cf || {{}});
          var esc = function(s) {{ return (s||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;'); }};
          var checks = (cf && cf.check_details) || [];
          var pagesUp = checks.some(function(c) {{ return c.up && (c.url||'').indexOf('.pages.dev') >= 0; }});
          var customUp = checks.some(function(c) {{ return c.up && (c.url||'').indexOf('.pages.dev') < 0; }});
          var cls, label;
          if (checks.length) {{
            if (pagesUp && customUp)   {{ cls = 'success'; label = 'up'; }}
            else if (pagesUp)          {{ cls = 'warning'; label = '↑ pages / ↓ domain'; }}
            else if (status === 'up')  {{ cls = 'success'; label = 'up'; }}
            else                       {{ cls = 'danger';  label = 'down'; }}
          }} else {{
            cls   = status === 'up' ? 'success' : (status === 'down' || status === 'error' ? 'danger' : 'secondary');
            label = status || '—';
          }}
          var badge = '<span class="badge bg-' + cls + ' cf-info-badge" data-domain-id="' + id + '" data-cf-json="' + esc(raw) + '" title="Click to view">' + label + '</span>';
          var dnsSetup = !!(cf && cf.dns_setup);
          var dnsBadge = '<span class="badge bg-' + (dnsSetup ? 'success' : 'secondary') + '" title="DNS zone: ' + (dnsSetup ? 'yes' : 'no') + '">DNS' + (dnsSetup ? '✓' : '✗') + '</span>';
          var dnsUrl = (cf && cf.domain_url) || '';
          var dnsBtn = '<button type="button" class="btn btn-sm btn-outline-primary cf-dns-btn" data-domain-id="' + id + '" data-domain-url="' + esc(dnsUrl) + '" title="Setup DNS">DNS</button>';
          var verBtn = '<button type="button" class="btn btn-sm btn-outline-secondary cf-versions-btn" data-domain-id="' + id + '" data-domain-url="' + esc(dnsUrl) + '" title="Manage deployment versions">🕓</button>';
          return '<div class="cloudflare-cell d-flex align-items-center gap-1">' + dnsBtn + verBtn + dnsBadge + badge + '</div>';
        }}
        function fetchOne(id) {{
          return fetch('/api/domains/' + id + '/cloudflare-info', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }} }})
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{
              done++;
              if (txt) txt.textContent = 'Updating Cloudflare status... (' + done + '/' + ids.length + ')';
              var btn = document.querySelector('.cf-fetch-btn[data-domain-id="' + id + '"]');
              if (btn) {{
                var td = btn.closest('.cloudflare-td');
                if (td && data && data.cloudflare_info) td.innerHTML = renderCfCell(id, data.cloudflare_info);
              }}
            }})
            .catch(function() {{ done++; }});
        }}
        function runBatch(start) {{
          var batch = ids.slice(start, start + concurrency);
          if (batch.length === 0) return Promise.resolve();
          return Promise.all(batch.map(fetchOne)).then(function() {{
            if (done < ids.length) return runBatch(done);
          }});
        }}
        runBatch(0).then(function() {{
          if (bar) bar.style.display = 'none';
        }});
      }})();
      var articleModal = document.getElementById('articleEditorModal');
      var articleBsModal = articleModal ? new bootstrap.Modal(articleModal) : null;
      function openArticleEditor(domainId) {{
        if (!domainId) return;
        document.getElementById('articleEditorDomainUrl').textContent = 'Loading...';
        if (articleBsModal) articleBsModal.show();
        var iframe = document.getElementById('articleEditorIframe');
        iframe.src = '/article-editor?domain_id=' + domainId + '&embed=1';
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domain-article-template/' + domainId).then(r => r.json()).then(function(d) {{
          document.getElementById('articleEditorDomainUrl').textContent = d.domain_url || ('Domain ' + domainId);
        }}).catch(function() {{
          document.getElementById('articleEditorDomainUrl').textContent = 'Domain ' + domainId;
        }}).finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }}
      document.querySelectorAll('.article-edit-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (domainId) openArticleEditor(domainId);
        }});
      }});
      document.querySelectorAll('.article-example-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var cell = this.closest('.article-cell');
          var sel = cell ? cell.querySelector('.website-template-select') : null;
          var domainId = this.getAttribute('data-domain-id');
          var tr = this.closest('tr');
          var domainName = tr ? (tr.querySelector('.domain-url-cell')?.textContent || 'Domain ' + domainId) : 'Domain ' + domainId;
          
          // Get all available generator options from the select dropdown
          var gens = [];
          if (sel) {{
            Array.from(sel.options).forEach(function(opt) {{
              var val = opt.value;
              if (val && val.startsWith('generator-')) gens.push(val);
            }});
          }}
          if (gens.length === 0) gens = ['generator-1', 'generator-2', 'generator-3', 'generator-4', 'generator-5', 'generator-6', 'generator-7', 'generator-8', 'generator-9', 'generator-10', 'generator-11', 'generator-12'];
          
          var modal = document.getElementById('templateExampleModal');
          var infoEl = document.getElementById('templateExampleDomainInfo');
          var bodyEl = document.getElementById('templateExampleContent');
          
          if (infoEl) infoEl.textContent = '— ' + domainName;
          
          if (bodyEl) {{
            var currentGen = sel ? sel.value : null;
            bodyEl.innerHTML = gens.map(function(gen) {{
              var isSelected = gen === currentGen;
              var cardBorder = isSelected ? 'border-success border-2' : 'border-0';
              var headerBg = isSelected ? 'bg-success text-white' : 'bg-white';
              var btnClass = isSelected ? 'btn-light text-success fw-bold' : 'btn-primary';
              var btnText = isSelected ? 'Selected' : 'Select';
              
              return `
                <div class="col-md-6 col-lg-4 mb-4">
                  <div class="card h-100 shadow-sm ${{cardBorder}}">
                    <div class="card-header ${{headerBg}} d-flex justify-content-between align-items-center py-2 border-bottom">
                      <span class="fw-bold" style="font-size:0.9rem;">${{gen}}</span>
                      <button type="button" class="btn btn-sm ${{btnClass}} select-gen-btn" data-gen="${{gen}}" ${{isSelected ? 'disabled' : ''}}>${{btnText}}</button>
                    </div>
                    <div class="card-body p-0 position-relative" style="height: 400px; overflow: hidden; background: #fff;">
                      <div class="position-absolute w-100 h-100 d-flex justify-content-center align-items-center loading-spinner">
                        <div class="spinner-border text-secondary" role="status"><span class="visually-hidden">Loading...</span></div>
                      </div>
                      <iframe src="/api/article-generator-example-raw?generator=${{encodeURIComponent(gen)}}" 
                              style="width: 200%; height: 200%; border: none; transform: scale(0.5); transform-origin: top left; position: relative; z-index: 1;"
                              onload="this.previousElementSibling.style.display='none';"></iframe>
                    </div>
                  </div>
                </div>
              `;
            }}).join('');
            
            // Add event listeners to the Select buttons
            bodyEl.querySelectorAll('.select-gen-btn').forEach(function(btn) {{
              btn.addEventListener('click', function() {{
                var selectedGen = this.getAttribute('data-gen');
                if (sel) {{
                  sel.value = selectedGen;
                  // Trigger change event to save
                  sel.dispatchEvent(new Event('change'));
                }}
                var mInstance = bootstrap.Modal.getInstance(modal);
                if (mInstance) mInstance.hide();
              }});
            }});
          }}
          
          if (modal) new bootstrap.Modal(modal).show();
        }});
      }});
      document.querySelectorAll('.theme-example-btn').forEach(function(btn) {{
        btn.addEventListener('click', function(e) {{
          e.preventDefault();
          var cell = this.closest('.theme-cell');
          var sel = cell ? cell.querySelector('.page-theme-select') : null;
          var domainId = this.getAttribute('data-domain-id');
          var tr = this.closest('tr');
          var domainName = tr ? (tr.querySelector('.domain-url-cell')?.textContent || 'Domain ' + domainId) : 'Domain ' + domainId;
          
          var themes = [];
          if (sel) {{
            Array.from(sel.options).forEach(function(opt) {{
              if (opt.value) themes.push({{ value: opt.value, label: opt.textContent }});
            }});
          }}
          if (themes.length === 0) themes = [{{value: 'default', label: 'Default'}}];
          
          var modal = document.getElementById('templateExampleModal');
          var infoEl = document.getElementById('templateExampleDomainInfo');
          var bodyEl = document.getElementById('templateExampleContent');
          
          if (infoEl) infoEl.textContent = '— ' + domainName + ' (Themes)';
          
          if (bodyEl) {{
            var currentTheme = sel ? sel.value : null;
            bodyEl.innerHTML = themes.map(function(t) {{
              var isSelected = t.value === currentTheme;
              var cardBorder = isSelected ? 'border-success border-2' : 'border-0';
              var headerBg = isSelected ? 'bg-success text-white' : 'bg-white';
              var btnClass = isSelected ? 'btn-light text-success fw-bold' : 'btn-primary';
              var btnText = isSelected ? 'Selected' : 'Select';
              
              // We'll use the site preview URL with a temporary theme parameter
              var previewUrl = '/preview-website/' + domainId + '?theme=' + encodeURIComponent(t.value);
              
              return `
                <div class="col-md-6 col-lg-4 mb-4">
                  <div class="card h-100 shadow-sm ${{cardBorder}}">
                    <div class="card-header ${{headerBg}} d-flex justify-content-between align-items-center py-2 border-bottom">
                      <span class="fw-bold" style="font-size:0.9rem;">${{t.label}}</span>
                      <button type="button" class="btn btn-sm ${{btnClass}} select-theme-btn" data-theme="${{t.value}}" ${{isSelected ? 'disabled' : ''}}>${{btnText}}</button>
                    </div>
                    <div class="card-body p-0 position-relative" style="height: 400px; overflow: hidden; background: #fff;">
                      <div class="position-absolute w-100 h-100 d-flex justify-content-center align-items-center loading-spinner">
                        <div class="spinner-border text-secondary" role="status"><span class="visually-hidden">Loading...</span></div>
                      </div>
                      <iframe src="${{previewUrl}}" 
                              style="width: 200%; height: 200%; border: none; transform: scale(0.5); transform-origin: top left; position: relative; z-index: 1;"
                              onload="this.previousElementSibling.style.display='none';"></iframe>
                    </div>
                  </div>
                </div>
              `;
            }}).join('');
            
            bodyEl.querySelectorAll('.select-theme-btn').forEach(function(btn) {{
              btn.addEventListener('click', function() {{
                var selectedTheme = this.getAttribute('data-theme');
                if (sel) {{
                  sel.value = selectedTheme;
                  sel.dispatchEvent(new Event('change'));
                }}
                var mInstance = bootstrap.Modal.getInstance(modal);
                if (mInstance) mInstance.hide();
              }});
            }});
          }}
          
          if (modal) new bootstrap.Modal(modal).show();
        }});
      }});
      document.addEventListener('change', function(e) {{
        if (!e.target || !e.target.matches || !e.target.matches('.website-template-select')) return;
        var selEl = e.target;
        var domainId = selEl.getAttribute('data-domain-id');
        var val = (selEl.value || '').trim() || null;
        var orig = selEl.getAttribute('data-original') || '';
        if (!domainId || val === orig) return;
        function doSave(clearContent) {{
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/' + domainId + '/website-template', {{
            method: 'PUT',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{website_template: val || '', clear_article_content: !!clearContent}})
          }}).then(function(r) {{ return r.json(); }}).then(function(d) {{
            if (d.success) {{
              selEl.setAttribute('data-original', val || '');
              if (typeof refreshAfterRun === 'function') refreshAfterRun();
            }} else {{
              alert('Error: ' + (d.error || 'Failed to save'));
              selEl.value = orig;
            }}
          }}).catch(function(err) {{
            alert('Error: ' + err);
            selEl.value = orig;
          }}).finally(function() {{
            if (typeof hideGlobalLoading === 'function') hideGlobalLoading();
          }});
        }}
        fetch('/api/domains/' + domainId + '/article-count')
          .then(function(r) {{ return r.json(); }})
          .then(function(d) {{
            var withHtml = (d && typeof d.with_html === 'number') ? d.with_html : 0;
            if (withHtml > 0) {{
              var parts = [];
              parts.push('This domain has ' + withHtml + ' articles with generated HTML+CSS.');
              parts.push('');
              parts.push('If you change the template, all generated HTML and CSS for this domain will be CLEARED.');
              parts.push('You will need to run \"Run content\" again for these articles.');
              parts.push('');
              parts.push('Do you want to continue?');
              var msg = parts.join('\\n');
              if (!confirm(msg)) {{
                selEl.value = orig;
                return;
              }}
              doSave(true);
            }} else {{
              doSave(false);
            }}
          }})
          .catch(function() {{
            doSave(false);
          }});
      }});
      
      var writersModal = document.getElementById('writersModal');
      var writersBsModal = writersModal ? new bootstrap.Modal(writersModal) : null;
      var currentWritersDomainId = null;
      var writersData = [];
      
      function renderWriters() {{
        var container = document.getElementById('writersContainer');
        if (!container) return;
        container.innerHTML = '';
        writersData.forEach(function(w, idx) {{
          var div = document.createElement('div');
          div.className = 'card mb-3';
          div.innerHTML = `
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">Writer ${{idx + 1}}</h6>
                <button type="button" class="btn btn-sm btn-danger remove-writer-btn" data-index="${{idx}}">Remove</button>
              </div>
              <div class="mb-2">
                <label class="form-label small">Name</label>
                <input type="text" class="form-control writer-name" data-index="${{idx}}" value="${{(w.name || '').replace(/"/g, '&quot;')}}">
              </div>
              <div class="mb-2">
                <label class="form-label small">Title (e.g. "Owner & Founder")</label>
                <input type="text" class="form-control writer-title" data-index="${{idx}}" value="${{(w.title || '').replace(/"/g, '&quot;')}}">
              </div>
              <div class="mb-2">
                <label class="form-label small">Bio</label>
                <textarea class="form-control writer-bio" data-index="${{idx}}" rows="3">${{w.bio || ''}}</textarea>
              </div>
              <div class="mb-2">
                <label class="form-label small">Avatar URL (optional)</label>
                <input type="text" class="form-control writer-avatar" data-index="${{idx}}" value="${{(w.avatar || '').replace(/"/g, '&quot;')}}">
              </div>
            </div>
          `;
          container.appendChild(div);
        }});
        document.querySelectorAll('.remove-writer-btn').forEach(function(btn) {{
          btn.addEventListener('click', function() {{
            var idx = parseInt(this.getAttribute('data-index'));
            writersData.splice(idx, 1);
            renderWriters();
          }});
        }});
      }}
      
      document.getElementById('addWriterBtn')?.addEventListener('click', function() {{
        writersData.push({{name: '', title: '', bio: '', avatar: ''}});
        renderWriters();
      }});
      
      document.querySelectorAll('.writers-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          currentWritersDomainId = this.getAttribute('data-domain-id');
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/' + currentWritersDomainId + '/writers')
            .then(r => r.json())
            .then(data => {{
              writersData = data.writers || [];
              renderWriters();
              if (writersBsModal) writersBsModal.show();
            }})
            .catch(e => alert('Error loading writers: ' + e))
            .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
        }});
      }});
      
      document.getElementById('saveWritersBtn')?.addEventListener('click', function() {{
        var writers = [];
        writersData.forEach(function(w, idx) {{
          var nameEl = document.querySelector('.writer-name[data-index="' + idx + '"]');
          var titleEl = document.querySelector('.writer-title[data-index="' + idx + '"]');
          var bioEl = document.querySelector('.writer-bio[data-index="' + idx + '"]');
          var avatarEl = document.querySelector('.writer-avatar[data-index="' + idx + '"]');
          writers.push({{
            name: nameEl ? nameEl.value : '',
            title: titleEl ? titleEl.value : '',
            bio: bioEl ? bioEl.value : '',
            avatar: avatarEl ? avatarEl.value : ''
          }});
        }});
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domains/' + currentWritersDomainId + '/writers', {{
          method: 'PUT',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{writers: writers}})
        }})
          .then(r => r.json())
          .then(data => {{
            if (data.success) {{
              alert('Writers saved!');
              if (writersBsModal) writersBsModal.hide();
              var badge = document.querySelector('button.writers-btn[data-domain-id="' + currentWritersDomainId + '"]');
              if (badge) {{
                  badge.classList.remove('btn-outline-primary', 'btn-outline-secondary');
                  badge.classList.add('btn-primary');
              }}
            }} else {{
              alert('Error: ' + (data.error || 'Unknown'));
            }}
          }})
          .catch(e => alert('Error: ' + e))
          .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }});
      
      document.querySelectorAll('.generate-distribute-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (!confirm('Generate 4 writers and distribute to all articles?\\n\\nThis will:\\n- Generate 4 diverse writer profiles with OpenAI\\n- Create 4 avatar images with Midjourney\\n- Upload avatars to R2\\n- Distribute writers to all existing articles\\n\\nTakes 1-2 minutes. Continue?')) return;
          this.disabled = true;
          this.innerHTML = '⏳';
          var originalBtn = this;
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          var startTime = Date.now();
          fetch('/api/domains/' + domainId + '/writers/generate', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}}
          }})
            .then(r => r.json())
            .then(function(data) {{
              if (!data.success) {{
                alert('Error: ' + (data.error || 'Unknown') + '\\n\\nCheck logs for details.');
                originalBtn.disabled = false;
                originalBtn.innerHTML = '✨';
                return;
              }}
              originalBtn.innerHTML = '⏳';
              return fetch('/api/domains/' + domainId + '/writers/distribute', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}}
              }}).then(r => r.json());
            }})
            .then(function(distData) {{
              if (!distData) return;
              var elapsed = Math.round((Date.now() - startTime) / 1000);
              if (distData.success) {{
                alert('✓ Done!\\n\\n- 4 writers generated\\n- ' + (distData.updated || 0) + '/' + (distData.total || 0) + ' articles updated\\n- Time: ' + elapsed + 's');
                originalBtn.innerHTML = '✓';
                originalBtn.classList.remove('btn-outline-success');
                originalBtn.classList.add('btn-success');
              }} else {{
                alert('Writers generated but distribute failed: ' + (distData.error || 'Unknown'));
                originalBtn.innerHTML = '⚠️';
              }}
            }})
            .catch(function(e) {{
              alert('Error: ' + e + '\\n\\nCheck logs for details.');
              originalBtn.disabled = false;
              originalBtn.innerHTML = '✨';
            }})
            .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
        }});
      }});
      
      var categoriesModal = document.getElementById('categoriesModal');
      var categoriesBsModal = categoriesModal ? new bootstrap.Modal(categoriesModal) : null;
      var currentCategoriesDomainId = null;
      document.querySelectorAll('.categories-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          currentCategoriesDomainId = this.getAttribute('data-domain-id');
          var row = this.closest('tr.domains-row');
          var link = row ? row.querySelector('.domain-url-link') : null;
          var domainUrl = link ? link.textContent.trim() : '—';
          document.getElementById('categoriesModalDomainUrl').textContent = domainUrl;
          document.getElementById('categoriesModalTextarea').value = '';
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/' + currentCategoriesDomainId + '/categories')
            .then(r => r.json())
            .then(function(data) {{
              var lines = [];
              (data.categories || []).forEach(function(c) {{
                if (typeof c === 'object' && c !== null) {{
                  var n = c.categorie || c.name || c.category || '';
                  if (n) lines.push(n);
                }} else if (typeof c === 'string' && c) {{ lines.push(c); }}
              }});
              document.getElementById('categoriesModalTextarea').value = lines.join('\\n');
              if (categoriesBsModal) categoriesBsModal.show();
            }})
            .catch(function(e) {{ alert('Error loading categories: ' + e); }})
            .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
        }});
      }});
      document.getElementById('saveCategoriesBtn')?.addEventListener('click', function() {{
        if (!currentCategoriesDomainId) return;
        var text = document.getElementById('categoriesModalTextarea').value || '';
        var categories = text.split(/\\n/).map(function(s) {{ return s.trim(); }}).filter(Boolean);
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domains/' + currentCategoriesDomainId + '/categories', {{
          method: 'PUT',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{categories: categories}})
        }})
          .then(r => r.json())
          .then(function(data) {{
            if (data.success) {{
              if (categoriesBsModal) categoriesBsModal.hide();
              var badge = document.querySelector('button.categories-btn[data-domain-id="' + currentCategoriesDomainId + '"]');
              if (badge) {{
                  badge.classList.remove('btn-outline-primary', 'btn-outline-secondary');
                  badge.classList.add('btn-primary');
                  badge.textContent = categories.length ? categories.length + ' cats' : 'Add cats';
              }}
            }} else {{
              alert('Error: ' + (data.error || 'Unknown'));
            }}
          }})
          .catch(function(e) {{ alert('Error: ' + e); }})
          .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }});
      
      var domainPagesModal = document.getElementById('domainPagesModal');
      var domainPagesBsModal = domainPagesModal ? new bootstrap.Modal(domainPagesModal) : null;
      var currentPagesDomainId = null;
      var themeSelect = document.getElementById('domainPageThemeSelect');

      function fillThemeSelect(themes, savedTheme) {{
        if (!themeSelect) return;
        var html = '';
        if (themes && themes.length) {{
          themes.forEach(function(t) {{
            var label = t.replace(/_/g, ' ').replace(/\b\w/g, function(c) {{ return c.toUpperCase(); }});
            html += '<option value="' + t + '">' + label + '</option>';
          }});
        }}
        html += '<option value="ai">AI Generated</option>';
        themeSelect.innerHTML = html;
        if (savedTheme) themeSelect.value = savedTheme;
      }}

      function getSelectedTheme() {{
        return themeSelect ? themeSelect.value : 'ai';
      }}

      document.querySelectorAll('.pages-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          currentPagesDomainId = this.getAttribute('data-domain-id');
          var domainUrl = this.getAttribute('data-domain-url') || '-';
          var states = {{}};
          var savedTheme = this.getAttribute('data-page-theme') || '';
          try {{ states = JSON.parse(this.getAttribute('data-page-states') || '{{}}'); }} catch(e) {{}}
          document.getElementById('domainPagesDomainUrl').textContent = domainUrl;
          document.getElementById('domainPagesStatus').textContent = '';
          fetch('/api/domain-page-themes')
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{ fillThemeSelect(data.themes || [], savedTheme); }})
            .catch(function() {{ fillThemeSelect([], savedTheme); }});
          document.querySelectorAll('#domainPagesTableBody tr').forEach(function(tr) {{
            var slug = tr.getAttribute('data-slug');
            var hasIt = states[slug] === true;
            var genBtn = tr.querySelector('.page-gen-btn');
            var viewBtn = tr.querySelector('.page-view-btn');
            var regBtn = tr.querySelector('.page-regenerate-btn');
            var statusSpan = tr.querySelector('.page-status');
            genBtn.style.display = hasIt ? 'none' : 'inline-block';
            viewBtn.style.display = hasIt ? 'inline-block' : 'none';
            regBtn.style.display = hasIt ? 'inline-block' : 'none';
            if (viewBtn) viewBtn.href = '/preview-website/' + currentPagesDomainId + '/' + slug;
            genBtn.disabled = false;
            regBtn.disabled = false;
            genBtn.textContent = 'Generate';
            regBtn.textContent = 'Regenerate';
            statusSpan.textContent = hasIt ? '\\u2713' : '';
          }});
          if (domainPagesBsModal) domainPagesBsModal.show();
        }});
      }});

      function generateOnePage(tr) {{
        if (!tr || !currentPagesDomainId) return;
        var slug = tr.getAttribute('data-slug');
        var theme = getSelectedTheme();
        var genBtn = tr.querySelector('.page-gen-btn');
        var regBtn = tr.querySelector('.page-regenerate-btn');
        var statusSpan = tr.querySelector('.page-status');
        genBtn.disabled = true;
        regBtn.disabled = true;
        statusSpan.textContent = theme === 'ai' ? 'AI\\u2026' : '\\u2026';
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domains/' + currentPagesDomainId + '/generate-page/' + slug, {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{theme: theme}})
        }})
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.success) {{
              statusSpan.textContent = '\\u2713';
              genBtn.style.display = 'none';
              tr.querySelector('.page-view-btn').style.display = 'inline-block';
              regBtn.style.display = 'inline-block';
              tr.querySelector('.page-view-btn').href = '/preview-website/' + currentPagesDomainId + '/' + slug;
              var pagesBtn = document.querySelector('.pages-btn[data-domain-id="' + currentPagesDomainId + '"]');
              if (pagesBtn) {{
                var st = {{}};
                try {{ st = JSON.parse(pagesBtn.getAttribute('data-page-states') || '{{}}'); }} catch(e) {{}}
                st[slug] = true;
                pagesBtn.setAttribute('data-page-states', JSON.stringify(st));
                pagesBtn.setAttribute('data-page-theme', theme);
              }}
            }} else {{
              statusSpan.textContent = 'Error: ' + (data.error || '');
              genBtn.disabled = false;
              regBtn.disabled = false;
            }}
          }})
          .catch(function(e) {{
            statusSpan.textContent = 'Error: ' + e;
            genBtn.disabled = false;
            regBtn.disabled = false;
          }})
          .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }}

      document.querySelectorAll('.page-gen-btn, .page-regenerate-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var tr = this.closest('tr');
          var isRegenerate = this.classList.contains('page-regenerate-btn');
          if (isRegenerate && !confirm('Regenerate with a new design?')) return;
          generateOnePage(tr);
        }});
      }});

      var generateAllBtn = document.getElementById('domainPagesGenerateAllBtn');
      if (generateAllBtn) {{
        generateAllBtn.addEventListener('click', function() {{
          if (!currentPagesDomainId) return;
          var theme = getSelectedTheme();
          if (!confirm('Generate all pages with ' + (theme === 'ai' ? 'AI' : theme.replace(/_/g, ' ')) + '? Header, footer, sidebar, index & category will also use this theme.')) return;
          var rows = document.querySelectorAll('#domainPagesTableBody tr');
          var slugs = Array.from(rows).map(function(tr) {{ return tr.getAttribute('data-slug'); }}).filter(Boolean);
          if (slugs.length === 0) return;
          generateAllBtn.disabled = true;
          generateAllBtn.textContent = 'Generating\\u2026';
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          var promises = slugs.map(function(slug) {{
            return fetch('/api/domains/' + currentPagesDomainId + '/generate-page/' + slug, {{
              method: 'POST',
              headers: {{'Content-Type': 'application/json'}},
              body: JSON.stringify({{theme: theme}})
            }}).then(function(r) {{ return r.json().then(function(data) {{ return {{slug: slug, ok: data.success, error: data.error}}; }}); }})
              .catch(function(e) {{ return {{slug: slug, ok: false, error: String(e)}}; }});
          }});
          Promise.all(promises).then(function(results) {{
            var pagesBtn = document.querySelector('.pages-btn[data-domain-id="' + currentPagesDomainId + '"]');
            var st = {{}};
            if (pagesBtn) {{ try {{ st = JSON.parse(pagesBtn.getAttribute('data-page-states') || '{{}}'); }} catch(e) {{}} }}
            results.forEach(function(r) {{
              var tr = document.querySelector('#domainPagesTableBody tr[data-slug="' + r.slug + '"]');
              if (!tr) return;
              var genBtn = tr.querySelector('.page-gen-btn');
              var viewBtn = tr.querySelector('.page-view-btn');
              var regBtn = tr.querySelector('.page-regenerate-btn');
              var statusSpan = tr.querySelector('.page-status');
              if (r.ok) {{
                statusSpan.textContent = '\\u2713';
                genBtn.style.display = 'none';
                viewBtn.style.display = 'inline-block';
                regBtn.style.display = 'inline-block';
                viewBtn.href = '/preview-website/' + currentPagesDomainId + '/' + r.slug;
                st[r.slug] = true;
              }} else {{
                statusSpan.textContent = 'Error';
                statusSpan.title = r.error || '';
              }}
            }});
            if (pagesBtn) {{
              pagesBtn.setAttribute('data-page-states', JSON.stringify(st));
              pagesBtn.setAttribute('data-page-theme', theme);
            }}
            generateAllBtn.disabled = false;
            generateAllBtn.textContent = 'Generate All';
            if (typeof hideGlobalLoading === 'function') hideGlobalLoading();
          }});
        }});
      }}
      var colorsModal = document.getElementById('colorsModal');
      var colorsBsModal = colorsModal ? new bootstrap.Modal(colorsModal) : null;
      var colorKeys = ['primary','secondary','background','text_primary','text_secondary','border'];
      var randomPalettes = [
        {{"primary":"#6C8AE4","secondary":"#9C6ADE","background":"#FFFFFF","text_primary":"#2D2D2D","text_secondary":"#5A5A5A","border":"#E2E8FF"}},
        {{"primary":"#E07C5E","secondary":"#9B5B4F","background":"#FFF8F5","text_primary":"#2D2D2D","text_secondary":"#6B5B55","border":"#F0E0D8"}},
        {{"primary":"#3D8B7A","secondary":"#2A5A4E","background":"#F5FFFC","text_primary":"#1A2E2A","text_secondary":"#4A6B63","border":"#D4EDE8"}},
        {{"primary":"#8B5A9B","secondary":"#5A3A6B","background":"#FAF5FC","text_primary":"#2D1A35","text_secondary":"#5A4A63","border":"#E8D8F0"}}
      ];
      function setColorInputs(colors) {{
        colorKeys.forEach(function(k) {{
          var v = (colors[k] || '').replace(/^#/,'');
          var hex = v ? '#'+v : '#888888';
          var c = document.getElementById('c_'+k);
          var t = document.getElementById('t_'+k);
          if (c) {{ c.value = hex.length===7 ? hex : '#'+v; }}
          if (t) {{ t.value = hex.length===7 ? hex : hex; }}
        }});
      }}
      function getColorInputs() {{
        var o = {{}};
        colorKeys.forEach(function(k) {{
          var t = document.getElementById('t_'+k);
          if (t && t.value.trim()) o[k] = t.value.trim();
        }});
        return o;
      }}
      function syncColorToText(k) {{ var c = document.getElementById('c_'+k); var t = document.getElementById('t_'+k); if (c && t) t.value = c.value; }}
      function syncTextToColor(k) {{ var c = document.getElementById('c_'+k); var t = document.getElementById('t_'+k); if (c && t && /^#[0-9A-Fa-f]{{6}}$/.test(t.value)) c.value = t.value; }}
      colorKeys.forEach(function(k) {{
        var c = document.getElementById('c_'+k);
        var t = document.getElementById('t_'+k);
        if (c) c.addEventListener('input', function() {{ syncColorToText(k); }});
        if (t) t.addEventListener('input', function() {{ syncTextToColor(k); }});
      }});
      document.querySelectorAll('.colors-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          var domainName = this.getAttribute('data-domain-name') || '';
        if (!domainId) return;
        document.getElementById('colorsDomainId').value = domainId;
        document.getElementById('colorsDomainName').textContent = domainName || 'Domain '+domainId;
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domains/'+domainId+'/colors').then(function(r) {{ return r.json(); }}).then(function(d) {{
          setColorInputs(d.colors || {{}});
          if (colorsBsModal) colorsBsModal.show();
        }}).catch(function() {{ setColorInputs({{}}); if (colorsBsModal) colorsBsModal.show(); }})
        .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
        }});
      }});
      document.getElementById('colorsSaveBtn').addEventListener('click', function() {{
        var domainId = document.getElementById('colorsDomainId').value;
        if (!domainId) return;
        var colors = getColorInputs();
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domains/'+domainId+'/colors', {{ method: 'PUT', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{ colors: colors, update_articles: true }}) }})
          .then(function(r) {{ return r.json(); }})
          .then(function(d) {{
            if (d.success) {{
              var msg = 'Colors saved.';
              if (d.articles_updated > 0) msg += ' ' + d.articles_updated + ' articles updated.';
              if (d.parts_regenerated > 0) msg += ' Site parts regenerated.';
              if (colorsBsModal) colorsBsModal.hide();
              if (msg !== 'Colors saved.') alert(msg);
            }} else alert(d.error || 'Failed');
          }})
          .catch(function(e) {{ alert(e); }})
          .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }});
      var pinterestSetupModal = document.getElementById('pinterestSetupModal');
      var pinterestSetupBsModal = pinterestSetupModal ? new bootstrap.Modal(pinterestSetupModal) : null;
      document.querySelectorAll('.pinterest-setup-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          var domainName = this.getAttribute('data-domain-name') || ('Domain ' + domainId);
          if (!domainId) return;
          document.getElementById('pinterestSetupDomainId').value = domainId;
          document.getElementById('pinterestSetupDomainName').textContent = domainName;
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/' + domainId).then(function(r) {{ return r.json(); }}).then(function(d) {{
            var feedUrl = (d.pinterest_rss_feed_url || '').trim() || (window.location.origin + '/rss/domain/' + domainId);
            document.getElementById('pinterestFeedUrl').value = feedUrl;
            if (pinterestSetupBsModal) pinterestSetupBsModal.show();
          }}).catch(function() {{
            document.getElementById('pinterestFeedUrl').value = window.location.origin + '/rss/domain/' + domainId;
            if (pinterestSetupBsModal) pinterestSetupBsModal.show();
          }}).finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
        }});
      }});
      document.getElementById('pinterestCopyFeedBtn').addEventListener('click', function() {{
        var input = document.getElementById('pinterestFeedUrl');
        if (input && input.value) {{
          input.select();
          try {{
            navigator.clipboard.writeText(input.value);
            this.textContent = 'Copied!';
            var t = this;
            setTimeout(function() {{ t.textContent = 'Copy'; }}, 2000);
          }} catch (e) {{}}
        }}
      }});
      document.getElementById('colorsRandomBtn').addEventListener('click', function() {{
        var btn = this;
        btn.disabled = true;
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/generate-color-palette', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{}}) }})
          .then(function(r) {{ return r.json(); }})
          .then(function(d) {{
            if (d.success && d.colors) setColorInputs(d.colors);
            else setColorInputs(randomPalettes[Math.floor(Math.random()*randomPalettes.length)]);
          }})
          .catch(function() {{ setColorInputs(randomPalettes[Math.floor(Math.random()*randomPalettes.length)]); }})
          .finally(function() {{ btn.disabled = false; if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }});
      document.querySelectorAll('.color-input').forEach(function(input) {{
        input.addEventListener('input', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (!domainId) return;
          var saveBtn = document.querySelector('.btn-save-colors[data-domain-id="'+domainId+'"]');
          if (saveBtn) saveBtn.style.display = '';
        }});
      }});
      document.querySelectorAll('.btn-save-colors').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (!domainId) return;
          var inputs = document.querySelectorAll('.color-input[data-domain-id="'+domainId+'"]');
          var colors = {{}};
          inputs.forEach(function(inp) {{
            var key = inp.getAttribute('data-color-key');
            if (key) colors[key] = inp.value;
          }});
          btn.classList.add('saving');
          btn.disabled = true;
          btn.textContent = '⏳';
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/'+domainId+'/colors', {{ method: 'PUT', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{ colors: colors, update_articles: true }}) }})
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              if (d.success) {{
                var msg = 'Colors saved.';
                if (d.articles_updated > 0) msg += ', ' + d.articles_updated + ' articles updated';
                if (d.parts_regenerated > 0) msg += ', ' + d.parts_regenerated + ' site parts regenerated';
                btn.textContent = '✓';
                btn.title = msg;
                setTimeout(function() {{ 
                  btn.style.display = 'none';
                  btn.textContent = '💾'; 
                  btn.title = 'Save colors and update all articles';
                }}, 3000);
              }} else {{
                alert(d.error || 'Failed to save');
                btn.textContent = '💾';
              }}
            }})
            .catch(function(e) {{ 
              alert('Error: ' + e); 
              btn.textContent = '💾';
            }})
            .finally(function() {{
              btn.classList.remove('saving');
              btn.disabled = false;
              if (typeof hideGlobalLoading === 'function') hideGlobalLoading();
            }});
        }});
      }});
      document.querySelectorAll('.colors-random-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (!domainId) return;
          var self = this;
          self.disabled = true;
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/generate-color-palette', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{}}) }})
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              var p = (d.success && d.colors) ? d.colors : randomPalettes[Math.floor(Math.random()*randomPalettes.length)];
              var colorKeys = ['primary','secondary','background','text_primary','text_secondary','border'];
              colorKeys.forEach(function(key) {{
                var input = document.querySelector('.color-input[data-domain-id="'+domainId+'"][data-color-key="'+key+'"]');
                if (input && p[key]) {{ input.value = p[key]; input.dispatchEvent(new Event('input')); }}
              }});
              var saveBtn = document.querySelector('.btn-save-colors[data-domain-id="'+domainId+'"]');
              if (saveBtn) saveBtn.style.display = '';
            }})
            .catch(function() {{
              var p = randomPalettes[Math.floor(Math.random()*randomPalettes.length)];
              var colorKeys = ['primary','secondary','background','text_primary','text_secondary','border'];
              colorKeys.forEach(function(key) {{
                var input = document.querySelector('.color-input[data-domain-id="'+domainId+'"][data-color-key="'+key+'"]');
                if (input && p[key]) {{ input.value = p[key]; input.dispatchEvent(new Event('input')); }}
              }});
              var saveBtn = document.querySelector('.btn-save-colors[data-domain-id="'+domainId+'"]');
              if (saveBtn) saveBtn.style.display = '';
            }})
            .finally(function() {{ self.disabled = false; if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
        }});
      }});
      var statsModal = document.getElementById('statsArticlesModal');
      var statsBsModal = statsModal ? new bootstrap.Modal(statsModal) : null;
      document.querySelectorAll('.stats-filter-btn').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          var stype = this.getAttribute('data-stats-type');
          var count = parseInt(this.getAttribute('data-count') || '0');
          if (!domainId || !stype || count === 0) return;
          
          document.getElementById('statsArticlesModalTitle').textContent = 'Loading…';
          document.getElementById('statsArticlesGrid').innerHTML = '';
          if (statsBsModal) statsBsModal.show();
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          
          window._statsModalDomainId = domainId;
          window._statsModalType = stype;
          
          fetch('/api/domains/'+domainId+'/articles-by-stat?type='+encodeURIComponent(stype))
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              var typeLabels = {{
                html_css: 'Articles with HTML+CSS',
                no_html_css: 'Articles without HTML+CSS',
                main_img: 'Articles with main image',
                no_main_img: 'Articles without main image',
                ing_img: 'Articles with ingredient image',
                no_ing_img: 'Articles without ingredient image'
              }};
              var label = typeLabels[stype] || stype;
              var arts = d.articles || [];
              document.getElementById('statsArticlesModalTitle').textContent = label + ' (' + arts.length + ')';
              
              var runGroupEl = document.getElementById('statsArticlesModalRunGroup');
              if (runGroupEl && arts.length > 0) {{
                var mode = stype.indexOf('html_css') >= 0 ? 'article' : 'images';
                runGroupEl.innerHTML = '<button type="button" class="btn btn-success btn-sm" onclick="generateForFilteredArticles()">Generate for these ' + arts.length + ' articles</button>';
              }} else if (runGroupEl) {{
                runGroupEl.innerHTML = '';
              }}
              var filterEl = document.getElementById('statsArticlesModalFilter');
              if (filterEl) filterEl.classList.add('d-none');
              var grid = document.getElementById('statsArticlesGrid');
              var arts = d.articles || [];
              window._statsModalArticles = arts;
              if (arts.length === 0) {{
                grid.innerHTML = '<p class="text-muted small mb-0">No articles</p>';
                return;
              }}
              var html = '';
              arts.forEach(function(a) {{
                var tid = a.id;
                var url = '/preview-website/'+domainId+'/article/'+tid;
                var rawTitle = a.title||'';
                var title = rawTitle.length>45 ? rawTitle.substring(0,45)+'…' : rawTitle;
                var titleEsc = title.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
                var actions = '<div class="stats-article-actions mt-1 w-100"><button type="button" class="btn btn-success btn-sm py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-article-external\\',{{title_id:'+tid+'}},\\'Article\\')" title="Article">Art</button><button type="button" class="btn btn-info btn-sm text-white py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-main-image\\',{{title_id:'+tid+'}},\\'Main\\')" title="Main">M</button><button type="button" class="btn btn-warning btn-sm text-dark py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-ingredient-image\\',{{title_id:'+tid+'}},\\'Ingredient\\')" title="Ingredient">I</button><button type="button" class="btn btn-outline-primary btn-sm py-0 px-1" onclick="event.stopPropagation(); openPinPickerModal('+tid+')" title="Pin">P</button></div>';
                html += '<div class="stats-article-card"><div class="d-flex align-items-start gap-2"><a href="'+url+'" target="_blank" rel="noopener" title="Open">'+tid+'</a><span class="stats-article-title flex-grow-1" title="'+titleEsc+'">'+titleEsc+'</span></div>'+actions+'</div>';
              }});
              grid.innerHTML = html;
            }})
            .catch(function(e) {{ document.getElementById('statsArticlesModalTitle').textContent = 'Error'; document.getElementById('statsArticlesGrid').innerHTML = '<p class="text-danger small">'+e+'</p>'; }})
            .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
        }});
      }});
      (function() {{
        var domainArticlesModal = document.getElementById('domainArticlesModal');
        var domainArticlesList = document.getElementById('domainArticlesList');
        var domainArticlesListWrap = document.getElementById('domainArticlesListWrap');
        var domainArticlesListLoading = document.getElementById('domainArticlesListLoading');
        var domainArticlesPrevBtn = document.getElementById('domainArticlesPrevBtn');
        var domainArticlesNextBtn = document.getElementById('domainArticlesNextBtn');
        var domainArticlesPosition = document.getElementById('domainArticlesPosition');
        var domainArticlesDomainId = null;
        var domainArticlesDomainUrl = '';
        var domainArticlesTotal = 0;
        var domainArticlesItems = [];
        var domainArticlesAutoScrollTimer = null;
        var domainArticlesCurrentIndex = 0;
        var domainArticlesNextOffset = 0;
        var domainArticlesLoading = false;
        var PAGE_SIZE = 30;
        function updateDomainArticlesPosition() {{
          var pos = domainArticlesPosition;
          if (!pos) return;
          pos.textContent = (domainArticlesTotal === 0 ? '0 of 0' : (domainArticlesCurrentIndex + 1) + ' of ' + domainArticlesTotal);
          if (domainArticlesPrevBtn) {{ domainArticlesPrevBtn.disabled = domainArticlesTotal === 0 || domainArticlesCurrentIndex <= 0; }}
          var nextDisabled = domainArticlesTotal === 0 || domainArticlesCurrentIndex >= domainArticlesTotal - 1;
          if (domainArticlesNextBtn) {{ domainArticlesNextBtn.disabled = nextDisabled; }}
          var nextDrop = document.getElementById('domainArticlesNextDropdownToggle');
          if (nextDrop) {{ nextDrop.disabled = nextDisabled; }}
        }}
        function scrollToDomainArticleIndex(index) {{
          var list = domainArticlesList;
          if (!list || index < 0 || index >= domainArticlesItems.length) return;
          list.querySelectorAll('[data-article-index]').forEach(function(el) {{ el.classList.remove('active'); }});
          var row = list.querySelector('[data-article-index="'+index+'"]');
          if (row) {{
            row.classList.add('active');
            row.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
          }}
        }}
        function getDomainArticlesValidatedFilter() {{
          var el = document.querySelector('input[name="domainArticlesValidatedFilter"]:checked');
          return (el && el.value) ? el.value : '0';
        }}
        function getDomainArticlesListParams() {{
          var vf = getDomainArticlesValidatedFilter();
          if (vf === 'empty') return {{ validated: 'all', content: 'empty' }};
          return {{ validated: vf, content: 'any' }};
        }}
        function loadMoreDomainArticles(callback) {{
          if (!domainArticlesDomainId || domainArticlesLoading) {{ if (callback) callback(); return; }}
          if (domainArticlesNextOffset >= domainArticlesTotal && domainArticlesTotal > 0) {{ if (callback) callback(); return; }}
          domainArticlesLoading = true;
          if (domainArticlesListLoading) domainArticlesListLoading.style.display = '';
          var p = getDomainArticlesListParams();
          var q = 'offset='+domainArticlesNextOffset+'&limit='+PAGE_SIZE+'&validated='+encodeURIComponent(p.validated)+'&content='+encodeURIComponent(p.content);
          fetch('/api/domains/'+domainArticlesDomainId+'/articles-list?'+q)
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              var items = d.items || [];
              domainArticlesNextOffset += items.length;
              items.forEach(function(it, i) {{
                var idx = domainArticlesItems.length;
                domainArticlesItems.push(it);
                var li = document.createElement('li');
                li.setAttribute('data-article-index', idx);
                li.setAttribute('data-title-id', it.id || '');
                li.style.cursor = 'pointer';
                var title = (it.title || '').trim();
                if (title.length > 80) title = title.substring(0, 80) + '…';
                var titleEsc = title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
                var genAt = (it.generated_at || '').trim();
                var modelUsed = (it.model_used || '').trim();
                if (modelUsed.length > 20) modelUsed = modelUsed.substring(0, 20) + '…';
                var meta = (genAt || modelUsed) ? '<span class="small text-muted me-2">' + (genAt ? genAt.substring(0,10) : '') + (genAt && modelUsed ? ' · ' : '') + (modelUsed ? modelUsed.replace(/</g,'&lt;') : '') + '</span>' : '';
                var sibs = it.siblings || {{}};
                var btnHtml = '';
                ['A','B','C','D'].forEach(function(l) {{
                  if (sibs[l]) {{
                    var isCur = sibs[l] == it.id;
                    btnHtml += '<button type="button" class="btn btn-sm btn-domain-sibling ' + (isCur ? 'btn-primary' : 'btn-outline-secondary') + ' py-0 px-1 me-1" style="font-size:0.7rem" data-sibling-id="' + sibs[l] + '" title="' + (isCur ? 'Current' : 'View '+l+' HTML') + '">' + l + '</button>';
                  }}
                }});
                var sibWrap = btnHtml ? '<span class="d-inline-flex flex-nowrap flex-shrink-0 align-items-center">' + btnHtml + '</span>' : '';
                var validBadge = (it.validated ? '<span class="badge bg-success ms-1 flex-shrink-0">Validated</span>' : '<span class="text-muted small ms-1 flex-shrink-0">—</span>');
                var tid = it.id || '';
                var actionsHtml = '<div class="stats-article-actions mt-1 w-100"><button type="button" class="btn btn-success btn-sm" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-article-external\\',{{title_id:'+tid+'}},\\'Article\\')" title="Article">Art</button><button type="button" class="btn btn-info btn-sm text-white" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-main-image\\',{{title_id:'+tid+'}},\\'Main image\\')" title="Main">M</button><button type="button" class="btn btn-warning btn-sm text-dark" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-ingredient-image\\',{{title_id:'+tid+'}},\\'Ingredient\\')" title="Ingredient">I</button><button type="button" class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); openPinPickerModal('+tid+')" title="Pin">P</button><button type="button" class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); var sm=document.getElementById(\\'statsArticlesModal\\'); if(sm && bootstrap.Modal.getInstance(sm)) bootstrap.Modal.getInstance(sm).hide(); openBulkModal('+tid+');" title="Run content+images for A,B,C,D">Run</button></div>';
                li.className = 'list-group-item list-group-item-action py-1 px-2 d-flex flex-wrap align-items-center';
                li.innerHTML = '<span class="text-muted small me-1 flex-shrink-0">'+ (it.id || '') + '</span><span class="text-truncate me-1" style="min-width:0;max-width:140px" title="'+ titleEsc +'">'+ titleEsc +'</span>' + validBadge + meta + sibWrap + actionsHtml;
                if (domainArticlesList) domainArticlesList.appendChild(li);
              }});
              if (callback) callback();
            }})
            .catch(function() {{ if (callback) callback(); }})
            .finally(function() {{
              domainArticlesLoading = false;
              if (domainArticlesListLoading) domainArticlesListLoading.style.display = 'none';
            }});
        }}
        document.querySelectorAll('.list-domain-articles-btn').forEach(function(btn) {{
          btn.addEventListener('click', function() {{
            var domainId = this.getAttribute('data-domain-id');
            var domainUrl = (this.getAttribute('data-domain-url') || '').trim() || '—';
            if (!domainId) return;
            domainArticlesDomainId = domainId;
            domainArticlesDomainUrl = domainUrl;
            domainArticlesTotal = 0;
            domainArticlesItems = [];
            domainArticlesCurrentIndex = 0;
            domainArticlesNextOffset = 0;
            var listParams = getDomainArticlesListParams();
            document.getElementById('domainArticlesModalTitle').textContent = 'Articles — ' + domainUrl;
            document.getElementById('domainArticlesModalCount').textContent = 'Loading…';
            if (domainArticlesList) domainArticlesList.innerHTML = '';
            showDomainArticleHtmlPlaceholder();
            if (domainArticlesModal && bootstrap.Modal) {{
              var m = new bootstrap.Modal(domainArticlesModal);
              m.show();
            }}
            var q0 = 'offset=0&limit='+PAGE_SIZE+'&validated='+encodeURIComponent(listParams.validated)+'&content='+encodeURIComponent(listParams.content);
            fetch('/api/domains/'+domainId+'/articles-list?'+q0)
              .then(function(r) {{ return r.json(); }})
              .then(function(d) {{
                domainArticlesTotal = d.total || 0;
                document.getElementById('domainArticlesModalCount').textContent = domainArticlesTotal + ' article' + (domainArticlesTotal !== 1 ? 's' : '');
                domainArticlesNextOffset = (d.items || []).length;
                (d.items || []).forEach(function(it, i) {{
                  var idx = domainArticlesItems.length;
                  domainArticlesItems.push(it);
                  var li = document.createElement('li');
                  li.className = 'list-group-item list-group-item-action py-2';
                  li.setAttribute('data-article-index', idx);
                  li.setAttribute('data-title-id', it.id || '');
                  li.style.cursor = 'pointer';
                  var title = (it.title || '').trim();
                  if (title.length > 80) title = title.substring(0, 80) + '…';
                  var titleEsc = title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
                  var genAt = (it.generated_at || '').trim();
                  var modelUsed = (it.model_used || '').trim();
                  if (modelUsed.length > 20) modelUsed = modelUsed.substring(0, 20) + '…';
                  var meta = (genAt || modelUsed) ? '<span class="small text-muted me-2">' + (genAt ? genAt.substring(0,10) : '') + (genAt && modelUsed ? ' · ' : '') + (modelUsed ? modelUsed.replace(/</g,'&lt;') : '') + '</span>' : '';
                  var sibs = it.siblings || {{}};
                  var btnHtml = '';
                  ['A','B','C','D'].forEach(function(l) {{
                    if (sibs[l]) {{
                      var isCur = sibs[l] == it.id;
                      btnHtml += '<button type="button" class="btn btn-sm btn-domain-sibling ' + (isCur ? 'btn-primary' : 'btn-outline-secondary') + ' py-0 px-1 me-1" style="font-size:0.7rem" data-sibling-id="' + sibs[l] + '" title="' + (isCur ? 'Current' : 'View '+l+' HTML') + '">' + l + '</button>';
                    }}
                  }});
                  var sibWrap = btnHtml ? '<span class="d-inline-flex flex-nowrap flex-shrink-0 align-items-center">' + btnHtml + '</span>' : '';
                  var validBadge = (it.validated ? '<span class="badge bg-success ms-1 flex-shrink-0">Validated</span>' : '<span class="text-muted small ms-1 flex-shrink-0">—</span>');
                  var tid = it.id || '';
                  var actionsHtml = '<div class="stats-article-actions mt-1 w-100"><button type="button" class="btn btn-success btn-sm" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-article-external\\',{{title_id:'+tid+'}},\\'Article\\')" title="Article">Art</button><button type="button" class="btn btn-info btn-sm text-white" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-main-image\\',{{title_id:'+tid+'}},\\'Main image\\')" title="Main">M</button><button type="button" class="btn btn-warning btn-sm text-dark" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-ingredient-image\\',{{title_id:'+tid+'}},\\'Ingredient\\')" title="Ingredient">I</button><button type="button" class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); openPinPickerModal('+tid+')" title="Pin">P</button><button type="button" class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); var sm=document.getElementById(\\'statsArticlesModal\\'); if(sm && bootstrap.Modal.getInstance(sm)) bootstrap.Modal.getInstance(sm).hide(); openBulkModal('+tid+');" title="Run content+images for A,B,C,D">Run</button></div>';
                  li.className = 'list-group-item list-group-item-action py-1 px-2 d-flex flex-wrap align-items-center';
                  li.innerHTML = '<span class="text-muted small me-1 flex-shrink-0">'+ (it.id || '') + '</span><span class="text-truncate me-1" style="min-width:0;max-width:140px" title="'+ titleEsc +'">'+ titleEsc +'</span>' + validBadge + meta + sibWrap + actionsHtml;
                  if (domainArticlesList) domainArticlesList.appendChild(li);
                }});
                updateDomainArticlesPosition();
                if (domainArticlesCurrentIndex < domainArticlesItems.length) scrollToDomainArticleIndex(domainArticlesCurrentIndex);
                showDomainArticleHtmlPlaceholder();
              }})
              .catch(function() {{ document.getElementById('domainArticlesModalCount').textContent = 'Error loading'; }});
          }});
        }});
        if (domainArticlesListWrap) {{
          domainArticlesListWrap.addEventListener('scroll', function() {{
            if (!domainArticlesDomainId || domainArticlesLoading) return;
            var el = domainArticlesListWrap;
            if (el.scrollHeight - el.scrollTop - el.clientHeight < 120) loadMoreDomainArticles();
          }});
        }}
        function refetchDomainArticlesList() {{
          if (!domainArticlesDomainId || domainArticlesLoading) return;
          domainArticlesLoading = true;
          domainArticlesItems = [];
          domainArticlesNextOffset = 0;
          domainArticlesCurrentIndex = 0;
          if (domainArticlesList) domainArticlesList.innerHTML = '';
          if (domainArticlesListLoading) domainArticlesListLoading.style.display = '';
          document.getElementById('domainArticlesModalCount').textContent = 'Loading…';
          var p = getDomainArticlesListParams();
          var qr = 'offset=0&limit='+PAGE_SIZE+'&validated='+encodeURIComponent(p.validated)+'&content='+encodeURIComponent(p.content);
          fetch('/api/domains/'+domainArticlesDomainId+'/articles-list?'+qr)
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              domainArticlesTotal = d.total || 0;
              document.getElementById('domainArticlesModalCount').textContent = domainArticlesTotal + ' article' + (domainArticlesTotal !== 1 ? 's' : '');
              domainArticlesNextOffset = (d.items || []).length;
              (d.items || []).forEach(function(it, i) {{
                var idx = domainArticlesItems.length;
                domainArticlesItems.push(it);
                var li = document.createElement('li');
                li.setAttribute('data-article-index', idx);
                li.setAttribute('data-title-id', it.id || '');
                li.style.cursor = 'pointer';
                var title = (it.title || '').trim();
                if (title.length > 80) title = title.substring(0, 80) + '…';
                var titleEsc = title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
                var genAt = (it.generated_at || '').trim();
                var modelUsed = (it.model_used || '').trim();
                if (modelUsed.length > 20) modelUsed = modelUsed.substring(0, 20) + '…';
                var meta = (genAt || modelUsed) ? '<span class="small text-muted me-2">' + (genAt ? genAt.substring(0,10) : '') + (genAt && modelUsed ? ' · ' : '') + (modelUsed ? modelUsed.replace(/</g,'&lt;') : '') + '</span>' : '';
                var sibs = it.siblings || {{}};
                var btnHtml = '';
                ['A','B','C','D'].forEach(function(l) {{
                  if (sibs[l]) {{
                    var isCur = sibs[l] == it.id;
                    btnHtml += '<button type="button" class="btn btn-sm btn-domain-sibling ' + (isCur ? 'btn-primary' : 'btn-outline-secondary') + ' py-0 px-1 me-1" style="font-size:0.7rem" data-sibling-id="' + sibs[l] + '" title="' + (isCur ? 'Current' : 'View '+l+' HTML') + '">' + l + '</button>';
                  }}
                }});
                var sibWrap = btnHtml ? '<span class="d-inline-flex flex-nowrap flex-shrink-0 align-items-center">' + btnHtml + '</span>' : '';
                var validBadge = (it.validated ? '<span class="badge bg-success ms-1 flex-shrink-0">Validated</span>' : '<span class="text-muted small ms-1 flex-shrink-0">—</span>');
                var tid = it.id || '';
                var actionsHtml = '<div class="stats-article-actions mt-1 w-100"><button type="button" class="btn btn-success btn-sm" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-article-external\\',{{title_id:'+tid+'}},\\'Article\\')" title="Article">Art</button><button type="button" class="btn btn-info btn-sm text-white" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-main-image\\',{{title_id:'+tid+'}},\\'Main image\\')" title="Main">M</button><button type="button" class="btn btn-warning btn-sm text-dark" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-ingredient-image\\',{{title_id:'+tid+'}},\\'Ingredient\\')" title="Ingredient">I</button><button type="button" class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); openPinPickerModal('+tid+')" title="Pin">P</button><button type="button" class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); var sm=document.getElementById(\\'statsArticlesModal\\'); if(sm && bootstrap.Modal.getInstance(sm)) bootstrap.Modal.getInstance(sm).hide(); openBulkModal('+tid+');" title="Run content+images for A,B,C,D">Run</button></div>';
                li.className = 'list-group-item list-group-item-action py-1 px-2 d-flex flex-wrap align-items-center';
                li.innerHTML = '<span class="text-muted small me-1 flex-shrink-0">'+ (it.id || '') + '</span><span class="text-truncate me-1" style="min-width:0;max-width:140px" title="'+ titleEsc +'">'+ titleEsc +'</span>' + validBadge + meta + sibWrap + actionsHtml;
                if (domainArticlesList) domainArticlesList.appendChild(li);
              }});
              updateDomainArticlesPosition();
              if (domainArticlesCurrentIndex < domainArticlesItems.length) {{ scrollToDomainArticleIndex(domainArticlesCurrentIndex); refreshDomainArticleHtmlPreview(); }} else {{ showDomainArticleHtmlPlaceholder(); }}
            }})
            .catch(function() {{ document.getElementById('domainArticlesModalCount').textContent = 'Error loading'; }})
            .finally(function() {{ domainArticlesLoading = false; if (domainArticlesListLoading) domainArticlesListLoading.style.display = 'none'; }});
        }}
        document.querySelectorAll('input[name="domainArticlesValidatedFilter"]').forEach(function(radio) {{
          radio.addEventListener('change', function() {{ if (domainArticlesDomainId) refetchDomainArticlesList(); }});
        }});
        var domainArticlesValidateNextBtn = document.getElementById('domainArticlesValidateNextBtn');
        if (domainArticlesValidateNextBtn) {{
          domainArticlesValidateNextBtn.addEventListener('click', function() {{
            if (domainArticlesCurrentIndex < 0 || domainArticlesCurrentIndex >= domainArticlesItems.length) return;
            var it = domainArticlesItems[domainArticlesCurrentIndex];
            var titleId = it && it.id;
            if (!titleId) return;
            var vf = getDomainArticlesValidatedFilter();
            fetch('/api/article-content/' + titleId + '/validated', {{ method: 'PUT', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ validated: true }}) }})
              .then(function(r) {{ return r.json(); }})
              .then(function(d) {{
                if (!d.success) return;
                if (vf === '0') {{
                  refetchDomainArticlesList();
                }} else {{
                  it.validated = true;
                  var row = domainArticlesList && domainArticlesList.querySelector('[data-article-index="'+domainArticlesCurrentIndex+'"]');
                  if (row) {{
                    var oldBadge = row.querySelector('.badge.bg-success, .text-muted.ms-1');
                    if (oldBadge) oldBadge.outerHTML = '<span class="badge bg-success ms-1 flex-shrink-0">Validated</span>';
                  }}
                  domainArticlesCurrentIndex++;
                  if (domainArticlesCurrentIndex >= domainArticlesItems.length) {{
                    loadMoreDomainArticles(function() {{
                      updateDomainArticlesPosition();
                      if (domainArticlesCurrentIndex < domainArticlesItems.length) {{ scrollToDomainArticleIndex(domainArticlesCurrentIndex); refreshDomainArticleHtmlPreview(); }} else {{ showDomainArticleHtmlPlaceholder(); }}
                    }});
                  }} else {{
                    updateDomainArticlesPosition();
                    scrollToDomainArticleIndex(domainArticlesCurrentIndex);
                    refreshDomainArticleHtmlPreview();
                  }}
                }}
              }});
          }});
        }}
        function refreshDomainArticleHtmlPreview() {{
          if (domainArticlesCurrentIndex >= 0 && domainArticlesCurrentIndex < domainArticlesItems.length) {{
            var it = domainArticlesItems[domainArticlesCurrentIndex];
            if (it && it.id) showDomainArticleHtml(it.id);
          }}
        }}
        if (domainArticlesPrevBtn) {{
          domainArticlesPrevBtn.addEventListener('click', function() {{
            if (domainArticlesCurrentIndex <= 0) return;
            domainArticlesCurrentIndex--;
            updateDomainArticlesPosition();
            scrollToDomainArticleIndex(domainArticlesCurrentIndex);
            refreshDomainArticleHtmlPreview();
          }});
        }}
        if (domainArticlesNextBtn) {{
          domainArticlesNextBtn.addEventListener('click', function() {{
            if (domainArticlesTotal === 0 || domainArticlesCurrentIndex >= domainArticlesTotal - 1) return;
            domainArticlesCurrentIndex++;
            if (domainArticlesCurrentIndex >= domainArticlesItems.length) {{
              loadMoreDomainArticles(function() {{
                updateDomainArticlesPosition();
                scrollToDomainArticleIndex(domainArticlesCurrentIndex);
                refreshDomainArticleHtmlPreview();
              }});
            }} else {{
              updateDomainArticlesPosition();
              scrollToDomainArticleIndex(domainArticlesCurrentIndex);
              refreshDomainArticleHtmlPreview();
            }}
          }});
        }}
        function showDomainArticleHtmlPlaceholder() {{
          var ph = document.getElementById('domainArticlesHtmlPlaceholder');
          var content = document.getElementById('domainArticlesHtmlContent');
          var meta = document.getElementById('domainArticlesHtmlMeta');
          if (ph) ph.style.display = '';
          if (content) {{ content.style.display = 'none'; content.innerHTML = ''; }}
          if (meta) meta.textContent = '';
        }}
        function showDomainArticleHtml(titleId) {{
          var content = document.getElementById('domainArticlesHtmlContent');
          var ph = document.getElementById('domainArticlesHtmlPlaceholder');
          var meta = document.getElementById('domainArticlesHtmlMeta');
          if (!content || !ph) return;
          ph.style.display = 'none';
          content.style.display = 'block';
          content.innerHTML = '<p class="text-muted small">Loading…</p>';
          var titleText = '';
          for (var i = 0; i < domainArticlesItems.length; i++) {{ if (domainArticlesItems[i].id == titleId) {{ titleText = (domainArticlesItems[i].title || '').trim(); break; }} }}
          if (meta) meta.textContent = (domainArticlesDomainUrl ? domainArticlesDomainUrl + ' · ' : '') + (titleId || '') + (titleText ? ' · ' + (titleText.length > 50 ? titleText.substring(0, 50) + '…' : titleText) : '');
          fetch('/api/article-content/' + titleId)
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              var html = (d.article_html || '').toString();
              var css = d.article_css || '';
              var transparentPixel = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
              html = html.replace(/href=["']([^"']*css\.css[^"']*)["']/gi, 'href="#"').replace(/src=["']([^"']*placeholder\.jpg[^"']*)["']/gi, 'src="'+transparentPixel+'"');
              /* Render inside an iframe to isolate article CSS from admin page */
              var iframeSrcdoc = '<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{{margin:0;padding:8px;font-family:sans-serif;}}' + (css || '') + '</style></head><body>' + (html || '<em>No content</em>') + '</body></html>';
              content.innerHTML = '<iframe id="domainArticlePreviewFrame" srcdoc="' + iframeSrcdoc.replace(/"/g,'&quot;') + '" style="width:100%;border:none;min-height:400px;" sandbox="allow-same-origin"></iframe>';
              /* Auto-resize iframe to content height */
              var ifr = content.querySelector('iframe');
              if (ifr) {{ ifr.onload = function() {{ try {{ var h = ifr.contentDocument.documentElement.scrollHeight; ifr.style.height = h + 'px'; }} catch(e){{}} }}; }}
            }})
            .catch(function() {{ content.innerHTML = '<p class="text-danger small">Failed to load article.</p>'; }});
        }}
        if (domainArticlesList) {{
          domainArticlesList.addEventListener('click', function(e) {{
            var btn = e.target.closest('button[data-sibling-id]');
            if (btn) {{
              e.preventDefault();
              e.stopPropagation();
              var sid = btn.getAttribute('data-sibling-id');
              if (sid) showDomainArticleHtml(sid);
              return;
            }}
            var li = e.target.closest('li[data-title-id]');
            if (!li) return;
            var titleId = li.getAttribute('data-title-id');
            var idx = parseInt(li.getAttribute('data-article-index'), 10);
            if (titleId && !isNaN(idx)) {{
              domainArticlesCurrentIndex = idx;
              updateDomainArticlesPosition();
              scrollToDomainArticleIndex(idx);
              showDomainArticleHtml(titleId);
            }}
          }});
        }}
        function startDomainArticlesAutoScroll() {{
          if (domainArticlesAutoScrollTimer) {{ cancelAnimationFrame(domainArticlesAutoScrollTimer); domainArticlesAutoScrollTimer = null; }}
          var sec = parseFloat(document.getElementById('domainArticlesAutoScrollSec').value) || 5;
          if (sec < 1) sec = 1;
          var wrap = document.getElementById('domainArticlesHtmlWrap');
          var checkEl = document.getElementById('domainArticlesAutoScrollCheck');
          if (!wrap || !checkEl) return;
          var duration = sec * 1000;
          var startTime = Date.now();
          var startScroll = wrap.scrollTop;
          var maxScroll = Math.max(0, wrap.scrollHeight - wrap.clientHeight);
          function tick() {{
            if (!checkEl.checked) {{ domainArticlesAutoScrollTimer = null; return; }}
            wrap = document.getElementById('domainArticlesHtmlWrap');
            if (!wrap || !wrap.parentNode) {{ domainArticlesAutoScrollTimer = null; return; }}
            var elapsed = Date.now() - startTime;
            var t = Math.min(1, elapsed / duration);
            var eased = t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t+2,2)/2;
            wrap.scrollTop = startScroll + (maxScroll - startScroll) * eased;
            if (t >= 1) {{ wrap.scrollTop = 0; startScroll = 0; startTime = Date.now(); maxScroll = Math.max(0, wrap.scrollHeight - wrap.clientHeight); }}
            domainArticlesAutoScrollTimer = requestAnimationFrame(tick);
          }}
          domainArticlesAutoScrollTimer = requestAnimationFrame(tick);
        }}
        function stopDomainArticlesAutoScroll() {{ if (domainArticlesAutoScrollTimer) {{ cancelAnimationFrame(domainArticlesAutoScrollTimer); domainArticlesAutoScrollTimer = null; }} }}
        var domainArticlesAutoScrollCheck = document.getElementById('domainArticlesAutoScrollCheck');
        var domainArticlesAutoScrollSecEl = document.getElementById('domainArticlesAutoScrollSec');
        if (domainArticlesAutoScrollCheck) domainArticlesAutoScrollCheck.addEventListener('change', function() {{ if (this.checked) startDomainArticlesAutoScroll(); else stopDomainArticlesAutoScroll(); }});
        if (domainArticlesAutoScrollSecEl) domainArticlesAutoScrollSecEl.addEventListener('change', function() {{ if (domainArticlesAutoScrollCheck && domainArticlesAutoScrollCheck.checked) startDomainArticlesAutoScroll(); }});
        if (domainArticlesModal) domainArticlesModal.addEventListener('hidden.bs.modal', function() {{ stopDomainArticlesAutoScroll(); }});
      }})();
      (function() {{
        var allArticlesModal = document.getElementById('allArticlesModal');
        var allArticlesList = document.getElementById('allArticlesList');
        var allArticlesListWrap = document.getElementById('allArticlesListWrap');
        var allArticlesListLoading = document.getElementById('allArticlesListLoading');
        var allArticlesPrevBtn = document.getElementById('allArticlesPrevBtn');
        var allArticlesNextBtn = document.getElementById('allArticlesNextBtn');
        var allArticlesPosition = document.getElementById('allArticlesPosition');
        var allArticlesItems = [];
        var allArticlesTotal = 0;
        var allArticlesCurrentIndex = 0;
        var allArticlesNextOffset = 0;
        var allArticlesLoading = false;
        var allArticlesAutoScrollTimer = null;
        var ALL_PAGE_SIZE = 30;
        function getAllArticlesValidatedFilter() {{ var el = document.querySelector('input[name="allArticlesValidatedFilter"]:checked'); return (el && el.value) ? el.value : '0'; }}
        function getAllArticlesDomainId() {{ var sel = document.getElementById('allArticlesDomainSelect'); return (sel && sel.value) ? sel.value : ''; }}
        function runAllArticlesTestContent() {{
          var vf = getAllArticlesValidatedFilter();
          var did = getAllArticlesDomainId();
          var data = {{ validated: vf, domain_id: did || '', async: 1 }};
          // Reuse single-action modal so user can pick AI provider & OpenRouter models (same UI as other content runs)
          if (typeof openSingleActionModal === 'function') {{
            openSingleActionModal('/api/all-articles-test-content', data, 'Test content');
          }}
        }}
        function viewTestContentResults(jobId) {{
          if (!jobId) return;
          fetch('/api/bulk-run-status?job_id=' + jobId).then(r=>r.json()).then(s=>{{
            var steps = s.steps || [];
            var progressSteps = steps.filter(function(st){{ return /R\d+.*:.*\[.*\].*[✓✗]/.test(st); }});
            var articles = [];
            progressSteps.forEach(function(st) {{
              var reason = '';
              var stBase = st;
              var pipeIdx = st.indexOf(' | ');
              if (pipeIdx >= 0) {{ reason = st.slice(pipeIdx + 3); stBase = st.slice(0, pipeIdx); }}
              var m = stBase.match(/:\s*\[(\d+)\]\s*(.+?)\s*[✓✗]/);
              if (m) {{
                var tid = m[1];
                var title = (m[2] || '').trim();
                var ok = /✓/.test(st);
                articles.push({{ tid: tid, title: title, ok: ok, reason: reason }});
              }}
            }});
            var html = '<div class="list-group">';
            articles.forEach(function(a) {{
              var titleEsc = a.title.replace(/</g,'&lt;').replace(/>/g,'&gt;');
              var reasonEsc = (a.reason||'').replace(/</g,'&lt;').replace(/>/g,'&gt;');
              var badge = a.ok ? '<span class="badge bg-success">Done</span>' : '<span class="badge bg-danger">Error</span>';
              var actions = a.ok ? '<button type="button" class="btn btn-sm btn-outline-secondary" onclick="viewDomainSingle('+a.tid+',\\'A\\')">View</button>' : '<button type="button" class="btn btn-sm btn-outline-danger" onclick="retryArticle('+a.tid+')">Retry</button>';
              html += '<div class="list-group-item d-flex align-items-start gap-2"><div class="flex-grow-1"><div class="fw-medium">[' + a.tid + '] ' + titleEsc + ' ' + badge + '</div>';
              if (reasonEsc) html += '<div class="text-muted small mt-1">' + reasonEsc + '</div>';
              html += '</div><div>' + actions + '</div></div>';
            }});
            html += '</div>';
            var modal = document.getElementById('testContentResultsModal');
            if (!modal) {{
              modal = document.createElement('div');
              modal.id = 'testContentResultsModal';
              modal.className = 'modal fade';
              modal.innerHTML = '<div class="modal-dialog modal-lg modal-dialog-scrollable"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Test Content Results</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body" id="testContentResultsBody"></div></div></div>';
              document.body.appendChild(modal);
            }}
            document.getElementById('testContentResultsBody').innerHTML = html;
            new bootstrap.Modal(modal).show();
          }}).catch(function(e){{ alert('Error: ' + e); }});
        }}
        function retryTestContentFailed(jobId) {{
          if (!jobId) return;
          fetch('/api/bulk-run-status?job_id=' + jobId).then(r=>r.json()).then(s=>{{
            var steps = s.steps || [];
            var progressSteps = steps.filter(function(st){{ return /R\d+.*:.*\[.*\].*[✓✗]/.test(st); }});
            var failedTids = [];
            progressSteps.forEach(function(st) {{
              var stBase = st.indexOf(' | ') >= 0 ? st.slice(0, st.indexOf(' | ')) : st;
              var m = stBase.match(/:\s*\[(\d+)\]\s*(.+?)\s*[✗]/);
              if (m) failedTids.push(m[1]);
            }});
            if (failedTids.length === 0) {{ alert('No failed articles to retry.'); return; }}
            var data = {{ title_ids: failedTids, async: 1 }};
            if (typeof openSingleActionModal === 'function') {{
              openSingleActionModal('/api/all-articles-test-content', data, 'Retry failed');
            }}
          }}).catch(function(e){{ alert('Error: ' + e); }});
        }}
        function retryArticle(tid) {{
          var data = {{ title_ids: [tid], async: 1 }};
          if (typeof openSingleActionModal === 'function') {{
            openSingleActionModal('/api/all-articles-test-content', data, 'Retry article');
          }}
        }}
        function updateAllArticlesPosition() {{
          if (!allArticlesPosition) return;
          allArticlesPosition.textContent = (allArticlesTotal === 0 ? '0 of 0' : (allArticlesCurrentIndex + 1) + ' of ' + allArticlesTotal);
          if (allArticlesPrevBtn) allArticlesPrevBtn.disabled = allArticlesTotal === 0 || allArticlesCurrentIndex <= 0;
          if (allArticlesNextBtn) allArticlesNextBtn.disabled = allArticlesTotal === 0 || allArticlesCurrentIndex >= allArticlesTotal - 1;
        }}
        function scrollToAllArticleIndex(index) {{
          if (!allArticlesList || index < 0 || index >= allArticlesItems.length) return;
          allArticlesList.querySelectorAll('[data-article-index]').forEach(function(el) {{ el.classList.remove('active'); }});
          var row = allArticlesList.querySelector('[data-article-index="'+index+'"]');
          if (row) {{ row.classList.add('active'); row.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }}); }}
        }}
        function showAllArticleHtmlPlaceholder() {{
          var ph = document.getElementById('allArticlesHtmlPlaceholder');
          var content = document.getElementById('allArticlesHtmlContent');
          var meta = document.getElementById('allArticlesHtmlMeta');
          if (ph) ph.style.display = '';
          if (content) {{ content.style.display = 'none'; content.innerHTML = ''; }}
          if (meta) meta.textContent = '';
        }}
        function showAllArticleHtml(titleId) {{
          var content = document.getElementById('allArticlesHtmlContent');
          var ph = document.getElementById('allArticlesHtmlPlaceholder');
          var meta = document.getElementById('allArticlesHtmlMeta');
          if (!content || !ph) return;
          ph.style.display = 'none';
          content.style.display = 'block';
          content.innerHTML = '<p class="text-muted small">Loading…</p>';
          var it = allArticlesItems.find(function(x) {{ return x.id == titleId; }});
          var domainUrl = (it && it.domain_url) ? it.domain_url : '';
          var generatorName = (it && it.generator) ? it.generator : '';
          var titleText = (it && it.title) ? (it.title.length > 50 ? it.title.substring(0, 50) + '…' : it.title) : '';
          var metaParts = [];
          if (domainUrl) metaParts.push(domainUrl);
          if (generatorName) metaParts.push(generatorName);
          if (titleId) metaParts.push(titleId);
          if (titleText) metaParts.push(titleText);
          if (meta) meta.textContent = metaParts.join(' · ');
          fetch('/api/article-content/' + titleId)
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              var html = (d.article_html || '').toString();
              var css = d.article_css || '';
              var transparentPixel = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
              html = html.replace(/href=["']([^"']*css\.css[^"']*)["']/gi, 'href="#"').replace(/src=["']([^"']*placeholder\.jpg[^"']*)["']/gi, 'src="'+transparentPixel+'"');
              /* Render inside an iframe to isolate article CSS from admin page */
              var iframeSrcdoc = '<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{{margin:0;padding:8px;font-family:sans-serif;}}' + (css || '') + '</style></head><body>' + (html || '<em>No content</em>') + '</body></html>';
              content.innerHTML = '<iframe id="allArticlePreviewFrame" srcdoc="' + iframeSrcdoc.replace(/"/g,'&quot;') + '" style="width:100%;border:none;min-height:400px;" sandbox="allow-same-origin"></iframe>';
              /* Auto-resize iframe to content height */
              var ifr = content.querySelector('iframe');
              if (ifr) {{ ifr.onload = function() {{ try {{ var h = ifr.contentDocument.documentElement.scrollHeight; ifr.style.height = h + 'px'; }} catch(e){{}} }}; }}
            }})
            .catch(function() {{ content.innerHTML = '<p class="text-danger small">Failed to load article.</p>'; }});
        }}
        function refetchAllArticlesList() {{
          allArticlesLoading = true;
          allArticlesItems = [];
          allArticlesNextOffset = 0;
          allArticlesCurrentIndex = 0;
          if (allArticlesList) allArticlesList.innerHTML = '';
          if (allArticlesListLoading) allArticlesListLoading.style.display = '';
          document.getElementById('allArticlesModalCount').textContent = 'Loading…';
          var vf = getAllArticlesValidatedFilter();
          var did = getAllArticlesDomainId();
          var url = '/api/articles-list?offset=0&limit='+ALL_PAGE_SIZE+'&validated='+encodeURIComponent(vf);
          if (did) url += '&domain_id='+encodeURIComponent(did);
          fetch(url)
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              allArticlesTotal = d.total || 0;
              document.getElementById('allArticlesModalCount').textContent = allArticlesTotal + ' article' + (allArticlesTotal !== 1 ? 's' : '');
              allArticlesNextOffset = (d.items || []).length;
              (d.items || []).forEach(function(it, i) {{
                var idx = allArticlesItems.length;
                allArticlesItems.push(it);
                var li = document.createElement('li');
                li.setAttribute('data-article-index', idx);
                li.setAttribute('data-title-id', it.id || '');
                li.style.cursor = 'pointer';
                var title = (it.title || '').trim();
                if (title.length > 80) title = title.substring(0, 80) + '…';
                var titleEsc = title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
                var genAt = (it.generated_at || '').trim();
                var modelUsed = (it.model_used || '').trim();
                if (modelUsed.length > 20) modelUsed = modelUsed.substring(0, 20) + '…';
                var meta = (genAt || modelUsed) ? '<span class="small text-muted me-2">' + (genAt ? genAt.substring(0,10) : '') + (genAt && modelUsed ? ' · ' : '') + (modelUsed ? modelUsed.replace(/</g,'&lt;') : '') + '</span>' : '';
                var sibs = it.siblings || {{}};
                var btnHtml = '';
                ['A','B','C','D'].forEach(function(l) {{ if (sibs[l]) {{ var isCur = sibs[l] == it.id; btnHtml += '<button type="button" class="btn btn-sm btn-domain-sibling ' + (isCur ? 'btn-primary' : 'btn-outline-secondary') + ' py-0 px-1 me-1" style="font-size:0.7rem" data-sibling-id="'+sibs[l]+'" title="'+(isCur ? 'Current' : 'View '+l+' HTML')+'">'+l+'</button>'; }} }});
                var sibWrap = btnHtml ? '<span class="d-inline-flex flex-nowrap flex-shrink-0 align-items-center">'+btnHtml+'</span>' : '';
                var validBadge = (it.validated ? '<span class="badge bg-success ms-1 flex-shrink-0">Validated</span>' : '<span class="text-muted small ms-1 flex-shrink-0">—</span>');
                var domainBadge = (it.domain_url ? '<span class="badge bg-secondary bg-opacity-50 ms-1 flex-shrink-0" title="'+((it.domain_url||'').replace(/"/g,'&quot;'))+'">'+((it.domain_url||'').length > 18 ? (it.domain_url||'').substring(0,18)+'…' : (it.domain_url||''))+'</span>' : '');
                var tid = it.id || '';
                var pillBtns = '';
                if (tid) {{
                  pillBtns = '<span class="pill-btns ms-1 mt-1 d-inline-flex flex-wrap gap-1">'
                    + '<button type="button" class="btn btn-success btn-sm py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-article-external\\',{{title_id:'+tid+'}},\\'Article A\\')" title="Article">Art</button>'
                    + '<button type="button" class="btn btn-info btn-sm text-white py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-main-image\\',{{title_id:'+tid+'}},\\'Main image\\')" title="Main image">M</button>'
                    + '<button type="button" class="btn btn-warning btn-sm text-dark py-0 px-1" onclick="event.stopPropagation(); openSingleActionModal(\\'/api/generate-ingredient-image\\',{{title_id:'+tid+'}},\\'Ingredient image\\')" title="Ingredient">I</button>'
                    + '<button type="button" class="btn btn-outline-primary btn-sm py-0 px-1" onclick="event.stopPropagation(); openPinPickerModal('+tid+')" title="Pin">P</button>'
                    + '<button type="button" class="btn btn-outline-secondary btn-sm py-0 px-1" onclick="event.stopPropagation(); viewDomainSingle('+tid+',\\'A\\')" title="View all">V</button>'
                    + '</span>';
                }}
                li.className = 'list-group-item list-group-item-action py-1 px-2 d-flex flex-wrap align-items-center';
                li.innerHTML = '<span class="text-muted small me-1 flex-shrink-0">'+(it.id||'')+'</span><span class="text-truncate me-1" style="min-width:0;max-width:120px" title="'+titleEsc+'">'+titleEsc+'</span>'+domainBadge+validBadge+meta+sibWrap+pillBtns;
                if (allArticlesList) allArticlesList.appendChild(li);
              }});
              updateAllArticlesPosition();
              if (allArticlesCurrentIndex < allArticlesItems.length) {{ scrollToAllArticleIndex(allArticlesCurrentIndex); showAllArticleHtml(allArticlesItems[allArticlesCurrentIndex].id); }} else showAllArticleHtmlPlaceholder();
            }})
            .catch(function() {{ document.getElementById('allArticlesModalCount').textContent = 'Error loading'; }})
            .finally(function() {{ allArticlesLoading = false; if (allArticlesListLoading) allArticlesListLoading.style.display = 'none'; }});
        }}
        window.openAllArticlesModal = function() {{
          var sel = document.getElementById('allArticlesDomainSelect');
          if (sel) {{
            sel.innerHTML = '<option value="">All domains</option>';
            (window.allDomainsForArticles || []).forEach(function(d) {{ var opt = document.createElement('option'); opt.value = d.id; opt.textContent = (d.domain_url || '').trim() || d.id; sel.appendChild(opt); }});
          }}
          document.querySelectorAll('input[name="allArticlesValidatedFilter"]').forEach(function(r) {{ if (r.value === '0') r.checked = true; }});
          showAllArticleHtmlPlaceholder();
          if (allArticlesModal && typeof bootstrap !== 'undefined') {{ var m = new bootstrap.Modal(allArticlesModal); m.show(); }}
          refetchAllArticlesList();
        }};
        var allArticlesTestContentBtn = document.getElementById('allArticlesTestContentBtn');
        if (allArticlesTestContentBtn) allArticlesTestContentBtn.addEventListener('click', runAllArticlesTestContent);
        document.getElementById('allArticlesDomainSelect').addEventListener('change', function() {{ refetchAllArticlesList(); }});
        document.querySelectorAll('input[name="allArticlesValidatedFilter"]').forEach(function(radio) {{ radio.addEventListener('change', function() {{ refetchAllArticlesList(); }}); }});
        if (allArticlesList) {{
          allArticlesList.addEventListener('click', function(e) {{
            var btn = e.target.closest('button[data-sibling-id]');
            if (btn) {{ e.preventDefault(); e.stopPropagation(); var sid = btn.getAttribute('data-sibling-id'); if (sid) showAllArticleHtml(sid); return; }}
            var li = e.target.closest('li[data-title-id]');
            if (!li) return;
            var titleId = li.getAttribute('data-title-id');
            var idx = parseInt(li.getAttribute('data-article-index'), 10);
            if (titleId && !isNaN(idx)) {{ allArticlesCurrentIndex = idx; updateAllArticlesPosition(); scrollToAllArticleIndex(idx); showAllArticleHtml(titleId); }}
          }});
        }}
        if (allArticlesPrevBtn) allArticlesPrevBtn.addEventListener('click', function() {{ if (allArticlesCurrentIndex <= 0) return; allArticlesCurrentIndex--; updateAllArticlesPosition(); scrollToAllArticleIndex(allArticlesCurrentIndex); showAllArticleHtml(allArticlesItems[allArticlesCurrentIndex].id); }});
        if (allArticlesNextBtn) allArticlesNextBtn.addEventListener('click', function() {{
          if (allArticlesTotal === 0 || allArticlesCurrentIndex >= allArticlesTotal - 1) return;
          allArticlesCurrentIndex++;
          if (allArticlesCurrentIndex >= allArticlesItems.length) {{
            var vf = getAllArticlesValidatedFilter();
            var did = getAllArticlesDomainId();
            var url = '/api/articles-list?offset='+allArticlesNextOffset+'&limit='+ALL_PAGE_SIZE+'&validated='+encodeURIComponent(vf);
            if (did) url += '&domain_id='+encodeURIComponent(did);
            fetch(url).then(function(r){{ return r.json(); }}).then(function(d) {{
              var items = d.items || [];
              allArticlesNextOffset += items.length;
              items.forEach(function(it) {{
                allArticlesItems.push(it);
                var li = document.createElement('li');
                li.setAttribute('data-article-index', allArticlesItems.length - 1);
                li.setAttribute('data-title-id', it.id || '');
                li.style.cursor = 'pointer';
                var title = (it.title || '').trim();
                if (title.length > 80) title = title.substring(0, 80) + '…';
                var titleEsc = title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
                var genAt = (it.generated_at || '').trim();
                var modelUsed = (it.model_used || '').trim();
                if (modelUsed.length > 20) modelUsed = modelUsed.substring(0, 20) + '…';
                var meta = (genAt || modelUsed) ? '<span class="small text-muted me-2">' + (genAt ? genAt.substring(0,10) : '') + (genAt && modelUsed ? ' · ' : '') + (modelUsed ? modelUsed.replace(/</g,'&lt;') : '') + '</span>' : '';
                var sibs = it.siblings || {{}};
                var btnHtml = '';
                ['A','B','C','D'].forEach(function(l) {{ if (sibs[l]) {{ var isCur = sibs[l]==it.id; btnHtml += '<button type="button" class="btn btn-sm btn-domain-sibling ' + (isCur?'btn-primary':'btn-outline-secondary') + ' py-0 px-1 me-1" style="font-size:0.7rem" data-sibling-id="'+sibs[l]+'">'+l+'</button>'; }} }});
                var sibWrap = btnHtml ? '<span class="d-inline-flex flex-nowrap flex-shrink-0">'+btnHtml+'</span>' : '';
                var validBadge = it.validated ? '<span class="badge bg-success ms-1 flex-shrink-0">Validated</span>' : '<span class="text-muted small ms-1 flex-shrink-0">—</span>';
                var domainBadge = (it.domain_url ? '<span class="badge bg-secondary bg-opacity-50 ms-1 flex-shrink-0">'+((it.domain_url||'').length>18?(it.domain_url||'').substring(0,18)+'…':(it.domain_url||''))+'</span>' : '');
                li.className = 'list-group-item list-group-item-action py-1 px-2 d-flex flex-wrap align-items-center';
                li.innerHTML = '<span class="text-muted small me-1 flex-shrink-0">'+(it.id||'')+'</span><span class="text-truncate me-1" style="min-width:0;max-width:120px">'+titleEsc+'</span>'+domainBadge+validBadge+meta+sibWrap;
                if (allArticlesList) allArticlesList.appendChild(li);
              }});
              updateAllArticlesPosition();
              scrollToAllArticleIndex(allArticlesCurrentIndex);
              showAllArticleHtml(allArticlesItems[allArticlesCurrentIndex].id);
            }});
          }} else {{
            updateAllArticlesPosition();
            scrollToAllArticleIndex(allArticlesCurrentIndex);
            showAllArticleHtml(allArticlesItems[allArticlesCurrentIndex].id);
          }}
        }});
        var allArticlesValidateNextBtn = document.getElementById('allArticlesValidateNextBtn');
        if (allArticlesValidateNextBtn) allArticlesValidateNextBtn.addEventListener('click', function() {{
          if (allArticlesCurrentIndex < 0 || allArticlesCurrentIndex >= allArticlesItems.length) return;
          var it = allArticlesItems[allArticlesCurrentIndex];
          var titleId = it && it.id;
          if (!titleId) return;
          fetch('/api/article-content/'+titleId+'/validated', {{ method: 'PUT', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ validated: true }}) }})
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              if (!d.success) return;
              refetchAllArticlesList();
            }});
        }});
        if (allArticlesListWrap) allArticlesListWrap.addEventListener('scroll', function() {{
          if (allArticlesLoading) return;
          var el = allArticlesListWrap;
          if (el.scrollHeight - el.scrollTop - el.clientHeight < 120) {{
            var vf = getAllArticlesValidatedFilter();
            var did = getAllArticlesDomainId();
            if (allArticlesNextOffset >= allArticlesTotal && allArticlesTotal > 0) return;
            allArticlesLoading = true;
            if (allArticlesListLoading) allArticlesListLoading.style.display = '';
            var url = '/api/articles-list?offset='+allArticlesNextOffset+'&limit='+ALL_PAGE_SIZE+'&validated='+encodeURIComponent(vf);
            if (did) url += '&domain_id='+encodeURIComponent(did);
            fetch(url).then(function(r){{return r.json();}}).then(function(d){{
              var items = d.items || [];
              allArticlesNextOffset += items.length;
              items.forEach(function(it){{
                var idx = allArticlesItems.length;
                allArticlesItems.push(it);
                var li = document.createElement('li');
                li.setAttribute('data-article-index', idx);
                li.setAttribute('data-title-id', it.id||'');
                li.style.cursor = 'pointer';
                var title = (it.title||'').trim();
                if (title.length > 80) title = title.substring(0,80)+'…';
                var titleEsc = title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
                var genAt = (it.generated_at||'').trim();
                var modelUsed = (it.model_used||'').trim();
                if (modelUsed.length > 20) modelUsed = modelUsed.substring(0,20)+'…';
                var meta = (genAt||modelUsed) ? '<span class="small text-muted me-2">'+(genAt?genAt.substring(0,10):'')+(genAt&&modelUsed?' · ':'')+(modelUsed?modelUsed.replace(/</g,'&lt;'):'')+'</span>' : '';
                var sibs = it.siblings || {{}};
                var btnHtml = '';
                ['A','B','C','D'].forEach(function(l) {{ if (sibs[l]) {{ var isCur = sibs[l]==it.id; btnHtml += '<button type="button" class="btn btn-sm btn-domain-sibling '+(isCur?'btn-primary':'btn-outline-secondary')+' py-0 px-1 me-1" style="font-size:0.7rem" data-sibling-id="'+sibs[l]+'">'+l+'</button>'; }} }});
                var sibWrap = btnHtml ? '<span class="d-inline-flex flex-nowrap flex-shrink-0">'+btnHtml+'</span>' : '';
                var validBadge = it.validated ? '<span class="badge bg-success ms-1 flex-shrink-0">Validated</span>' : '<span class="text-muted small ms-1 flex-shrink-0">—</span>';
                var domainBadge = (it.domain_url ? '<span class="badge bg-secondary bg-opacity-50 ms-1 flex-shrink-0">'+((it.domain_url||'').length>18?(it.domain_url||'').substring(0,18)+'…':(it.domain_url||''))+'</span>' : '');
                li.className = 'list-group-item list-group-item-action py-1 px-2 d-flex flex-wrap align-items-center';
                li.innerHTML = '<span class="text-muted small me-1 flex-shrink-0">'+(it.id||'')+'</span><span class="text-truncate me-1" style="min-width:0;max-width:120px">'+titleEsc+'</span>'+domainBadge+validBadge+meta+sibWrap;
                if (allArticlesList) allArticlesList.appendChild(li);
              }});
              allArticlesLoading = false;
              if (allArticlesListLoading) allArticlesListLoading.style.display = 'none';
            }});
          }}
        }});
        function startAllArticlesAutoScroll() {{
          if (allArticlesAutoScrollTimer) {{ cancelAnimationFrame(allArticlesAutoScrollTimer); allArticlesAutoScrollTimer = null; }}
          var sec = parseFloat(document.getElementById('allArticlesAutoScrollSec').value) || 5;
          if (sec < 1) sec = 1;
          var wrap = document.getElementById('allArticlesHtmlWrap');
          var checkEl = document.getElementById('allArticlesAutoScrollCheck');
          if (!wrap || !checkEl) return;
          var duration = sec * 1000;
          var startTime = Date.now();
          var startScroll = wrap.scrollTop;
          var maxScroll = Math.max(0, wrap.scrollHeight - wrap.clientHeight);
          function tick() {{
            if (!checkEl.checked) {{ allArticlesAutoScrollTimer = null; return; }}
            wrap = document.getElementById('allArticlesHtmlWrap');
            if (!wrap || !wrap.parentNode) {{ allArticlesAutoScrollTimer = null; return; }}
            var elapsed = Date.now() - startTime;
            var t = Math.min(1, elapsed / duration);
            var eased = t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t+2,2)/2;
            wrap.scrollTop = startScroll + (maxScroll - startScroll) * eased;
            if (t >= 1) {{ wrap.scrollTop = 0; startScroll = 0; startTime = Date.now(); maxScroll = Math.max(0, wrap.scrollHeight - wrap.clientHeight); }}
            allArticlesAutoScrollTimer = requestAnimationFrame(tick);
          }}
          allArticlesAutoScrollTimer = requestAnimationFrame(tick);
        }}
        function stopAllArticlesAutoScroll() {{ if (allArticlesAutoScrollTimer) {{ cancelAnimationFrame(allArticlesAutoScrollTimer); allArticlesAutoScrollTimer = null; }} }}
        var allArticlesAutoScrollCheck = document.getElementById('allArticlesAutoScrollCheck');
        var allArticlesAutoScrollSecEl = document.getElementById('allArticlesAutoScrollSec');
        if (allArticlesAutoScrollCheck) allArticlesAutoScrollCheck.addEventListener('change', function() {{ if (this.checked) startAllArticlesAutoScroll(); else stopAllArticlesAutoScroll(); }});
        if (allArticlesAutoScrollSecEl) allArticlesAutoScrollSecEl.addEventListener('change', function() {{ if (allArticlesAutoScrollCheck && allArticlesAutoScrollCheck.checked) startAllArticlesAutoScroll(); }});
        if (allArticlesModal) allArticlesModal.addEventListener('hidden.bs.modal', function() {{ stopAllArticlesAutoScroll(); }});
      }})();
      document.querySelectorAll('.font-heading-select, .font-body-select').forEach(function(sel) {{
        sel.addEventListener('change', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (!domainId) return;
          var saveBtn = document.querySelector('.btn-fonts-save[data-domain-id="'+domainId+'"]');
          if (saveBtn) saveBtn.style.display = '';
        }});
      }});
      document.querySelectorAll('.btn-fonts-save').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
          var domainId = this.getAttribute('data-domain-id');
          if (!domainId) return;
          var cell = document.querySelector('.fonts-cell[data-domain-id="'+domainId+'"]');
          if (!cell) return;
          var headingSel = cell.querySelector('.font-heading-select');
          var bodySel = cell.querySelector('.font-body-select');
          var fonts = {{ heading_family: headingSel ? headingSel.value : '', body_family: bodySel ? bodySel.value : '' }};
          btn.disabled = true;
          btn.textContent = '⏳';
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/'+domainId+'/fonts', {{ method: 'PUT', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{ fonts: fonts }}) }})
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
              if (d.success) {{
                btn.textContent = '✓';
                btn.style.display = 'none';
                setTimeout(function() {{ btn.textContent = '💾'; }}, 2000);
              }} else {{
                alert(d.error || 'Failed to save fonts');
                btn.textContent = '💾';
              }}
            }})
            .catch(function(e) {{ alert('Error: ' + e); btn.textContent = '💾'; }})
            .finally(function() {{
              btn.disabled = false;
              if (typeof hideGlobalLoading === 'function') hideGlobalLoading();
            }});
        }});
      }});
      window.refreshDomainsAfterPinEditor = function() {{ location.reload(); }};
      var FIELD_TO_KEY = {{ 'header_template': 'headers', 'footer_template': 'footers', 'side_article_template': 'side_articles', 'category_page_template': 'categories', 'writer_template': 'writers' }};
      function toBadgeLabel(field, val) {{
        if (!val) return '—';
        var s = val;
        if (field === 'header_template') s = s.replace(/^header_/i, 'H');
        else if (field === 'footer_template') s = s.replace(/^footer_/i, 'F');
        else if (field === 'side_article_template') s = s.replace(/^(sidebar_|side_article_)/i, 'S');
        else if (field === 'category_page_template') s = s.replace(/^category_/i, 'C');
        else if (field === 'writer_template') s = s.replace(/^writer_/i, 'W');
        return s.replace(/_/g, '') || '—';
      }};
      function closeThemeEdit(editDiv, badge) {{
        if (editDiv && editDiv.parentNode) editDiv.remove();
        if (badge) badge.style.display = '';
      }};
      document.querySelectorAll('.theme-badge').forEach(function(badge) {{
        badge.addEventListener('click', function(e) {{
          e.stopPropagation();
          var field = this.getAttribute('data-field');
          var domainId = this.getAttribute('data-domain-id');
          var current = this.getAttribute('data-current') || '';
          var key = FIELD_TO_KEY[field];
          var list = (window.SITE_TEMPLATES && window.SITE_TEMPLATES[key]) || [];
          var opts = '<option value="">—</option>';
          list.forEach(function(t) {{
            var n = t.name || t.label || '';
            var sel = n === current ? ' selected' : '';
            opts += '<option value="'+n.replace(/"/g,'&quot;')+'"'+sel+'>'+n.replace(/</g,'&lt;')+'</option>';
          }});
          this.style.display = 'none';
          var editDiv = document.createElement('div');
          editDiv.className = 'theme-badge-edit';
          editDiv.innerHTML = '<input type="text" class="form-control form-control-sm theme-filter" placeholder="Search..." style="width:60px;font-size:0.65rem;padding:1px 4px;">' +
            '<select class="form-select form-select-sm theme-select">'+opts+'</select>';
          this.parentNode.insertBefore(editDiv, this.nextSibling);
          var filterInput = editDiv.querySelector('.theme-filter');
          var sel = editDiv.querySelector('.theme-select');
          filterInput.oninput = function() {{
            var q = (this.value || '').toLowerCase();
            Array.from(sel.options).forEach(function(opt) {{
              opt.style.display = !q || (opt.text || '').toLowerCase().indexOf(q) >= 0 ? '' : 'none';
            }});
          }};
          var saveAndClose = function() {{
            var val = (sel.value || '').trim() || null;
            closeThemeEdit(editDiv, badge);
            if (val !== current) {{
              var body = {{}};
              body[field] = val;
              if (typeof showGlobalLoading === 'function') showGlobalLoading();
              fetch('/api/domains/'+domainId+'/site-templates', {{ method: 'PUT', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify(body) }})
                .then(function(r) {{ return r.json(); }})
                .then(function(d) {{
                  if (d.success) {{ badge.textContent = toBadgeLabel(field, val); badge.setAttribute('data-current', val || ''); }}
                  else {{ badge.textContent = toBadgeLabel(field, current); badge.setAttribute('data-current', current); }}
                }})
                .catch(function(err) {{ badge.textContent = toBadgeLabel(field, current); badge.setAttribute('data-current', current); }})
                .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
            }}
          }};
          sel.onchange = function() {{ document.removeEventListener('click', onDocClick); saveAndClose(); }};
          sel.focus();
          var onDocClick = function(ev) {{
            if (editDiv.parentNode && !editDiv.contains(ev.target) && ev.target !== badge) {{
              document.removeEventListener('click', onDocClick);
              saveAndClose();
            }}
          }};
          setTimeout(function() {{ document.addEventListener('click', onDocClick); }}, 10);
        }});
      }});
      var THEME_STEPS = [
        {{ part: 'header', field: 'header_template', key: 'headers', tabId: 'theme-step-1', gridId: 'themePreviewGrid1' }},
        {{ part: 'footer', field: 'footer_template', key: 'footers', tabId: 'theme-step-2', gridId: 'themePreviewGrid2' }},
        {{ part: 'sidebar', field: 'side_article_template', key: 'side_articles', tabId: 'theme-step-3', gridId: 'themePreviewGrid3' }},
        {{ part: 'category', field: 'category_page_template', key: 'categories', tabId: 'theme-step-4', gridId: 'themePreviewGrid4' }},
        {{ part: 'writer', field: 'writer_template', key: 'writers', tabId: 'theme-step-5', gridId: 'themePreviewGrid5' }}
      ];
      var themeStepperDomainId = null;
      var themeStepperSelections = {{}};
      var themeStepperCurrentIndex = 0;
      var themeStepperModal = document.getElementById('themeStepperModal');
      var themeStepperBsModal = themeStepperModal ? new bootstrap.Modal(themeStepperModal) : null;
      function themeStepperRenderStep(stepIndex) {{
        var step = THEME_STEPS[stepIndex];
        if (!step) return;
        var grid = document.getElementById(step.gridId);
        if (!grid || grid.dataset.built === '1') return;
        grid.dataset.built = '1';
        var list = (window.SITE_TEMPLATES && window.SITE_TEMPLATES[step.key]) || [];
        var currentVal = themeStepperSelections[step.field] || '';
        grid.innerHTML = '';
        list.forEach(function(t) {{
          var name = (t.name || t.label || '').trim();
          if (!name) return;
          var label = (t.label || t.name || name).replace(/_/g, ' ');
          var card = document.createElement('div');
          card.className = 'theme-preview-card' + (name === currentVal ? ' selected' : '');
          card.dataset.part = step.part;
          card.dataset.name = name;
          card.dataset.field = step.field;
          card.innerHTML = '<div class="theme-preview-label">' + (label.replace(/</g,'&lt;')) + '</div><div class="theme-preview-frame-wrap"><div class="theme-preview-loading">Loading…</div></div>';
          card.addEventListener('click', function() {{
            grid.querySelectorAll('.theme-preview-card').forEach(function(c) {{ c.classList.remove('selected'); }});
            card.classList.add('selected');
            themeStepperSelections[step.field] = name;
            var wrap = card.querySelector('.theme-preview-frame-wrap');
            if (card.dataset.loaded === '1') return;
            wrap.innerHTML = '<div class="theme-preview-loading">Loading…</div>';
            fetch('/api/domains/' + themeStepperDomainId + '/site-part-preview', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{ part: step.part, name: name }}) }})
              .then(function(r) {{ return r.json(); }})
              .then(function(d) {{
                if (!d.success) {{ wrap.innerHTML = '<div class="theme-preview-loading">Preview failed</div>'; return; }}
                var html = d.html || '';
                var css = d.css || '';
                var doc = '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>' + (css.replace(/<\\/style>/gi,'')) + '</style></head><body style="margin:0;padding:4px;">' + html + '</body></html>';
                var iframe = document.createElement('iframe');
                iframe.sandbox = 'allow-same-origin';
                iframe.style.cssText = 'width:100%;height:100%;border:0;transform:scale(0.5);transform-origin:0 0;';
                wrap.innerHTML = '';
                wrap.appendChild(iframe);
                try {{ iframe.srcdoc = doc; }} catch(e) {{ iframe.src = 'about:blank'; iframe.onload = function() {{ try {{ iframe.contentDocument.open(); iframe.contentDocument.write(doc); iframe.contentDocument.close(); }} catch(z) {{}} }}; }}
                card.dataset.loaded = '1';
              }})
              .catch(function() {{ wrap.innerHTML = '<div class="theme-preview-loading">Preview failed</div>'; }});
          }});
          grid.appendChild(card);
          (function(c, stepName, templateName) {{
            fetch('/api/domains/' + themeStepperDomainId + '/site-part-preview', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{ part: stepName, name: templateName }}) }})
              .then(function(r) {{ return r.json(); }})
              .then(function(d) {{
                if (!c.parentNode) return;
                var wrap = c.querySelector('.theme-preview-frame-wrap');
                if (!wrap) return;
                if (!d.success) {{ wrap.innerHTML = '<div class="theme-preview-loading">Preview failed</div>'; return; }}
                var html = d.html || '';
                var css = d.css || '';
                var doc = '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>' + (css.replace(/<\\/style>/gi,'')) + '</style></head><body style="margin:0;padding:4px;">' + html + '</body></html>';
                var iframe = document.createElement('iframe');
                iframe.sandbox = 'allow-same-origin';
                iframe.style.cssText = 'width:100%;height:100%;border:0;transform:scale(0.5);transform-origin:0 0;';
                wrap.innerHTML = '';
                wrap.appendChild(iframe);
                try {{ iframe.srcdoc = doc; }} catch(e) {{ iframe.src = 'about:blank'; iframe.onload = function() {{ try {{ iframe.contentDocument.open(); iframe.contentDocument.write(doc); iframe.contentDocument.close(); }} catch(z) {{}} }}; }}
                c.dataset.loaded = '1';
              }})
              .catch(function() {{ if (c.parentNode && c.querySelector('.theme-preview-frame-wrap')) c.querySelector('.theme-preview-frame-wrap').innerHTML = '<div class="theme-preview-loading">Preview failed</div>'; }});
          }})(card, step.part, name);
        }});
      }}
      function themeStepperUpdateButtons() {{
        document.getElementById('themeStepperBackBtn').disabled = themeStepperCurrentIndex === 0;
        document.getElementById('themeStepperNextBtn').style.display = themeStepperCurrentIndex >= THEME_STEPS.length - 1 ? 'none' : 'inline-block';
        document.getElementById('themeStepperSaveBtn').style.display = themeStepperCurrentIndex >= THEME_STEPS.length - 1 ? 'inline-block' : 'none';
      }}
      document.querySelectorAll('.theme-manage-btn').forEach(function(btn) {{
        btn.addEventListener('click', function(e) {{
          e.stopPropagation();
          var domainId = this.getAttribute('data-domain-id');
          if (!domainId) return;
          themeStepperDomainId = domainId;
          document.getElementById('themeStepperDomainId').value = domainId;
          themeStepperSelections = {{}};
          themeStepperCurrentIndex = 0;
          THEME_STEPS.forEach(function(s) {{ var g = document.getElementById(s.gridId); if (g) {{ g.dataset.built = ''; g.innerHTML = ''; }} }});
          if (typeof showGlobalLoading === 'function') showGlobalLoading();
          fetch('/api/domains/' + domainId + '/site-templates').then(function(r) {{ return r.json(); }}).then(function(d) {{
            if (d.success !== false && d.header_template !== undefined) {{
              themeStepperSelections.header_template = d.header_template || '';
              themeStepperSelections.footer_template = d.footer_template || '';
              themeStepperSelections.side_article_template = d.side_article_template || '';
              themeStepperSelections.category_page_template = d.category_page_template || '';
              themeStepperSelections.writer_template = d.writer_template || '';
            }}
            fetch('/api/domains/' + domainId).then(function(r2) {{ return r2.json(); }}).then(function(dom) {{
              document.getElementById('themeStepperDomainUrl').textContent = dom.domain_url || ('Domain ' + domainId);
            }}).catch(function() {{ document.getElementById('themeStepperDomainUrl').textContent = 'Domain ' + domainId; }});
            themeStepperRenderStep(0);
            themeStepperUpdateButtons();
            var tabEl = document.querySelector('#theme-step-1-tab');
            if (tabEl) tabEl.click();
          }}).catch(function() {{}}).finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
          if (themeStepperBsModal) themeStepperBsModal.show();
        }});
      }});
      document.getElementById('themeStepperBackBtn').addEventListener('click', function() {{
        if (themeStepperCurrentIndex <= 0) return;
        themeStepperCurrentIndex--;
        themeStepperRenderStep(themeStepperCurrentIndex);
        themeStepperUpdateButtons();
        document.querySelector('#themeStepperNav button[data-bs-target="#theme-step-' + (themeStepperCurrentIndex + 1) + '"]').click();
      }});
      document.getElementById('themeStepperNextBtn').addEventListener('click', function() {{
        if (themeStepperCurrentIndex >= THEME_STEPS.length - 1) return;
        themeStepperCurrentIndex++;
        themeStepperRenderStep(themeStepperCurrentIndex);
        themeStepperUpdateButtons();
        document.querySelector('#themeStepperNav button[data-bs-target="#theme-step-' + (themeStepperCurrentIndex + 1) + '"]').click();
      }});
      document.getElementById('themeStepperSaveBtn').addEventListener('click', function() {{
        if (!themeStepperDomainId) return;
        var body = {{}};
        THEME_STEPS.forEach(function(s) {{ body[s.field] = themeStepperSelections[s.field] || null; }});
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domains/' + themeStepperDomainId + '/site-templates', {{ method: 'PUT', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify(body) }})
          .then(function(r) {{ return r.json(); }})
          .then(function(d) {{
            if (d.success) {{
              if (themeStepperBsModal) themeStepperBsModal.hide();
              var bBtn = document.querySelector('button.theme-manage-btn[data-domain-id="' + themeStepperDomainId + '"]');
              if (bBtn) {{
                bBtn.innerHTML = 'Saved ✓';
                bBtn.classList.add('btn-success', 'text-white');
                setTimeout(function() {{ bBtn.classList.remove('btn-success', 'text-white'); bBtn.innerHTML = 'Theme'; }}, 2000);
              }}
            }} else {{ alert(d.error || 'Save failed'); }}
          }})
          .catch(function(e) {{ alert('Error: ' + e); }})
          .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }});
      themeStepperModal.addEventListener('show.bs.modal', function() {{
        themeStepperCurrentIndex = 0;
        themeStepperUpdateButtons();
      }});
      themeStepperModal.addEventListener('shown.bs.modal', function() {{
        var tab = document.querySelector('#themeStepperContent .tab-pane.active');
        if (tab) themeStepperRenderStep(themeStepperCurrentIndex);
      }});
    }});
    </script>
    """
    return base_layout(content, "Admin - Domains")


@app.route("/admin/domain-site-templates")
@login_required
def admin_domain_site_templates():
    """Assign header, footer, side_article, category templates per domain. Random distribute for 100+ domains."""
    templates = _list_site_templates()
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT d.id, d.domain_url, d.domain_name, d.header_template, d.footer_template,
            d.side_article_template, d.category_page_template, d.writer_template, d.index_template, d.article_card_template, g.name AS group_name
            FROM domains d LEFT JOIN `groups` g ON d.group_id = g.id ORDER BY d.id""")
        domains = [dict_row(r) for r in cur.fetchall()]
    def opt(name, sel):
        h = (sel or "").strip()
        return ' selected' if name == h else ''
    def opts(lst, current):
        s = '<option value="">—</option>'
        for t in lst:
            n, l = t.get("name", ""), t.get("label", t.get("name", ""))
            s += f'<option value="{html.escape(n)}"{opt(n, current)}>{html.escape(l)}</option>'
        return s
    rows = []
    for d in domains:
        did = d["id"]
        rows.append(
            f'<tr data-domain-id="{did}">'
            f'<td>{did}</td>'
            f'<td class="text-truncate" style="max-width:120px" title="{html.escape(d.get("domain_url") or "")}">{html.escape((d.get("domain_url") or "")[:40])}</td>'
            f'<td>{html.escape(d.get("domain_url") or "")}</td>'
            f'<td><select class="form-select form-select-sm site-tpl" data-field="header_template">{opts(templates["headers"], d.get("header_template"))}</select></td>'
            f'<td><select class="form-select form-select-sm site-tpl" data-field="footer_template">{opts(templates["footers"], d.get("footer_template"))}</select></td>'
            f'<td><select class="form-select form-select-sm site-tpl" data-field="side_article_template">{opts(templates["side_articles"], d.get("side_article_template"))}</select></td>'
            f'<td><select class="form-select form-select-sm site-tpl" data-field="category_page_template">{opts(templates["categories"], d.get("category_page_template"))}</select></td>'
            f'<td><select class="form-select form-select-sm site-tpl" data-field="writer_template">{opts(templates["writers"], d.get("writer_template"))}</select></td>'
            f'<td><select class="form-select form-select-sm site-tpl" data-field="index_template">{opts(templates["indexes"], d.get("index_template"))}</select></td>'
            f'<td><select class="form-select form-select-sm site-tpl" data-field="article_card_template">{opts(templates["article_cards"], d.get("article_card_template"))}</select></td>'
            f'</tr>'
        )
    rows_html = "".join(rows)
    content = f"""
    <h2>Site Templates (Header, Footer, Side, Category, Writer)</h2>
    <p class="text-muted">Each domain gets a header, footer, side article block, category page, writer byline, index, and article card template. Add domains in Domains, then use Random distribute for variety across 100+ domains.</p>
    <div class="mb-3">
      <button type="button" class="btn btn-primary" id="btnRandomDistribute">Random distribute (all domains)</button>
    </div>
    <div class="table-responsive">
    <table class="table table-bordered table-sm"><thead><tr><th>ID</th><th>URL</th><th>Name</th><th>Header</th><th>Footer</th><th>Side</th><th>Category</th><th>Writer</th><th>Index</th><th>Card</th></tr></thead><tbody>{rows_html}</tbody></table>
    </div>
    <script>
    document.getElementById('btnRandomDistribute').addEventListener('click', function() {{
      if (!confirm('Assign random header/footer/side/category/writer/index templates to ALL domains?')) return;
      if (typeof showGlobalLoading === 'function') showGlobalLoading();
      fetch('/api/domains/random-distribute-site-templates', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{ domain_ids: 'all' }}) }})
        .then(r => r.json())
        .then(d => {{ alert(d.success ? d.message : 'Error: ' + (d.error||'')); if (d.success) location.reload(); }})
        .catch(e => alert('Error: ' + e))
        .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
    }});
    document.querySelectorAll('.site-tpl').forEach(function(sel) {{
      sel.addEventListener('change', function() {{
        var tr = this.closest('tr');
        var domainId = tr.getAttribute('data-domain-id');
        var field = this.getAttribute('data-field');
        var val = this.value || null;
        var body = {{}};
        body[field] = val;
        if (typeof showGlobalLoading === 'function') showGlobalLoading();
        fetch('/api/domains/' + domainId + '/site-templates', {{ method: 'PUT', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify(body) }})
          .then(r => r.json())
          .then(d => {{ if (!d.success) alert('Save failed: ' + (d.error||'')); }})
          .catch(e => alert('Error: ' + e))
          .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
      }});
    }});
    </script>
    """
    return base_layout(content, "Site Templates")


def _assign_random_site_templates(conn, domain_id, user_id=None, domain_index=None):
    """Assign random header, footer, sidebar, category, writer templates, colors, fonts, categories, pins, and article generator to domain.
    When domain_index is provided (bulk add), themes 1-9 are distributed round-robin: first domain gets theme 1, second gets theme 2, etc."""
    import random
    
    # 1. Random site templates
    tpl = _list_site_templates()
    h = [x["name"] for x in tpl["headers"]] or ["header_1", "header_2", "header_3"]
    f = [x["name"] for x in tpl["footers"]] or ["footer_1", "footer_2", "footer_3"]
    s = [x["name"] for x in tpl["side_articles"]] or ["sidebar_1", "sidebar_2"]
    c = [x["name"] for x in tpl["categories"]] or ["category_1", "category_2"]
    w = [x["name"] for x in tpl["writers"]] or ["writer_1"]
    ac = [x["name"] for x in tpl.get("article_cards", [])] or ["article_card_1", "article_card_2"]
    idx = [x["name"] for x in tpl["indexes"]] or ["index_1"]
    
    # 2. Colors: bulk add = distinct palette per domain (round-robin); single add = random from list
    if domain_index is not None:
        palette = dict(GOOD_BULK_COLOR_PALETTES[domain_index % len(GOOD_BULK_COLOR_PALETTES)])
    else:
        palette = dict(random.choice(GOOD_BULK_COLOR_PALETTES))
    domain_colors_json = json.dumps(palette)
    
    # 3. Random fonts (good UX combinations)
    GOOD_FONT_COMBINATIONS = [
        {"heading_family": "Playfair Display", "body_family": "Inter"},
        {"heading_family": "Lora", "body_family": "Open Sans"},
        {"heading_family": "Merriweather", "body_family": "Lato"},
        {"heading_family": "Source Serif 4", "body_family": "Source Sans 3"},
        {"heading_family": "Fraunces", "body_family": "DM Sans"},
        {"heading_family": "Georgia", "body_family": "Arial"},
        {"heading_family": "Playfair Display", "body_family": "Source Sans 3"},
        {"heading_family": "Lora", "body_family": "Inter"},
    ]
    font_combo = random.choice(GOOD_FONT_COMBINATIONS)
    domain_fonts = {
        "heading_family": font_combo["heading_family"],
        "heading_h1": "2.5rem",
        "heading_h2": "1.875rem",
        "heading_h3": "1.5rem",
        "body_family": font_combo["body_family"],
        "body_size": "1rem",
        "body_line_height": "1.7",
    }
    domain_fonts_json = json.dumps(domain_fonts)
    
    # 4. Article generator (website_template): e.g. generator-1, generator-2. Used for /generate-article/{name}
    #    Round-robin when domain_index provided (bulk add), else random. Each domain gets a different generator.
    ARTICLE_GENERATORS = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    page_themes_list = _get_available_page_themes()
    if not page_themes_list:
        page_themes_list = [t[0] for t in DOMAIN_PAGE_THEMES_FALLBACK]

    if domain_index is not None:
        article_generator = ARTICLE_GENERATORS[domain_index % len(ARTICLE_GENERATORS)]
        page_theme = page_themes_list[domain_index % len(page_themes_list)]
    else:
        article_generator = random.choice(ARTICLE_GENERATORS)
        page_theme = random.choice(page_themes_list)

    # website_template = article generator name for /generate-article/{name} API (e.g. generator-1)
    website_template = f"generator-{article_generator}"
    
    article_template_config = {
        "generator": article_generator,
        "colors": palette,
        "fonts": domain_fonts
    }
    article_template_config_json = json.dumps(article_template_config)
    
    log.info(f"[assign_templates] Domain {domain_id}: Assigning generator {article_generator}, website_theme {website_template}, page_theme {page_theme}")
    
    # Update domain with all random settings
    db_execute(conn, """UPDATE domains SET 
        header_template=?, footer_template=?, side_article_template=?, category_page_template=?, 
        writer_template=?, index_template=?, article_card_template=?, 
        domain_colors=?, domain_fonts=?, website_template=?, article_template_config=?
        WHERE id=?""",
        (random.choice(h), random.choice(f), random.choice(s), random.choice(c), 
         random.choice(w), random.choice(idx), random.choice(ac),
         domain_colors_json, domain_fonts_json, website_template, article_template_config_json, domain_id))
    
    # 6. Persist page theme to domain_page_about_us so dropdown shows correct value
    db_execute(conn, "UPDATE domains SET domain_page_about_us = ? WHERE id = ?",
               (json.dumps({"theme": page_theme}), domain_id))
    
    # 7. Assign default categories from user profile
    if user_id:
        cur = db_execute(conn, "SELECT default_categories FROM user_api_keys WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            default_cats = dict_row(row).get("default_categories")
            if default_cats:
                categories = [line.strip() for line in default_cats.strip().split("\n") if line.strip()]
                if categories:
                    db_execute(conn, "UPDATE domains SET categories_list = ? WHERE id = ?", 
                             (json.dumps(categories), domain_id))
    
    # 8. Generate 2 pin templates for domain: fetch from Pin API, create via POST /api/domain-templates logic
    try:
        pin_base = (PIN_API_URL or "http://localhost:5000").rstrip("/")
        r = requests_lib.get(f"{pin_base}/templates", timeout=10)
        r.raise_for_status()
        data = r.json()
        pin_names = data.get("templates") or []
        if isinstance(pin_names, dict):
            pin_names = list(pin_names.keys()) if pin_names else []
        if not pin_names:
            log.info(f"[assign_templates] No pin templates from Pin API for domain {domain_id}")
        else:
            # Pick 2 templates: round-robin by domain_index if provided, else random
            if domain_index is not None:
                idx0 = (domain_index * 2) % len(pin_names)
                idx1 = (domain_index * 2 + 1) % len(pin_names)
                chosen = [pin_names[idx0], pin_names[idx1]] if len(pin_names) >= 2 else pin_names[:2]
            else:
                chosen = random.sample(pin_names, min(2, len(pin_names)))
            for sort_order, name in enumerate(chosen[:2]):
                try:
                    tr = requests_lib.get(f"{pin_base}/template/{name}", timeout=10)
                    tr.raise_for_status()
                    tpl_data = tr.json()
                    template_json = json.dumps(tpl_data) if isinstance(tpl_data, dict) else str(tpl_data)
                    cur = db_execute(conn, "INSERT INTO domain_templates (domain_id, name, template_json, sort_order) VALUES (?, ?, ?, ?)",
                                     (domain_id, name, template_json, sort_order))
                    tid = last_insert_id(cur)
                    if tid:
                        db_execute(conn, """INSERT INTO domain_template_assignments (domain_id, template_id, sort_order) VALUES (?, ?, ?)""",
                                  (domain_id, tid, sort_order))
                        # Generate preview image so Pins column shows thumbnails (use domain colors for styling)
                        try:
                            preview_url = _generate_domain_template_preview(template_json, domain_colors=palette)
                            if preview_url:
                                db_execute(conn, "UPDATE domain_templates SET preview_image_url = ? WHERE id = ?", (preview_url, tid))
                        except Exception as _e:
                            log.debug(f"[assign_templates] Preview generation skipped for template {name}: {_e}")
                except Exception as e:
                    log.warning(f"[assign_templates] Could not create pin template '{name}' for domain {domain_id}: {e}")
    except Exception as e:
        log.warning(f"[assign_templates] Error generating pin templates for domain {domain_id}: {e}")


@app.route("/admin/domains/random-templates/<int:domain_id>")
def admin_domains_random_templates(domain_id):
    """Assign random header/footer/sidebar/category to this domain, then redirect to domains list."""
    group_id = request.args.get("group_id")
    
    with get_connection() as conn:
        _assign_random_site_templates(conn, domain_id)
    
    redirect_url = url_for("admin_domains")
    if group_id:
        redirect_url += f"?group_id={group_id}"
    return redirect(redirect_url)


@app.route("/admin/domains/add", methods=["POST"])
@login_required
def admin_domains_add():
    user = get_current_user()
    user_id = user["id"]
    is_admin = bool(user.get("is_admin", 0))
    
    # Check if profile is complete
    if not is_profile_complete(user_id):
        return redirect(url_for("profile") + "?error=" + urllib.parse.quote("Please complete your profile settings before adding domains"))
    
    raw = request.form.get("domain_url", "").strip()
    url = _normalize_domain(raw)
    target_group_id_raw = request.form.get("target_group_id", "").strip()
    target_group_id = int(target_group_id_raw) if target_group_id_raw and target_group_id_raw.isdigit() else None
    
    if not url:
        return redirect(url_for("admin_domains") + "?add_error=" + urllib.parse.quote("Domain URL is required"))
    
    if not target_group_id:
        return redirect(url_for("admin_domains") + "?add_error=" + urllib.parse.quote("Please select a parent group"))
    
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM domains WHERE domain_url = ?", (url,))
        if cur.fetchone():
            return redirect(url_for("admin_domains") + "?add_error=" + urllib.parse.quote(f"'{url}' is already in the database"))
        
        # Get parent group name
        cur = db_execute(conn, "SELECT name FROM `groups` WHERE id = ?", (target_group_id,))
        parent_group = dict_row(cur.fetchone())
        if not parent_group:
            return redirect(url_for("admin_domains") + "?add_error=" + urllib.parse.quote("Invalid group"))
        parent_name = parent_group["name"]
        
        # Find a subgroup under this parent that has < 4 domains
        cur = db_execute(conn, """
            SELECT g.id, COUNT(d.id) as domain_count
            FROM `groups` g
            LEFT JOIN domains d ON d.group_id = g.id
            WHERE g.parent_group_id = ?
            GROUP BY g.id
            HAVING domain_count < 4
            ORDER BY domain_count, g.id
            LIMIT 1
        """, (target_group_id,))
        row = dict_row(cur.fetchone())
        
        if row:
            # Found a subgroup with space
            group_id = row["id"]
            domain_index = row.get("domain_count") or 0
        else:
            # No subgroup with space - create a new subgroup
            # Count existing subgroups to name it
            cur = db_execute(conn, "SELECT COUNT(*) as cnt FROM `groups` WHERE parent_group_id = ?", (target_group_id,))
            subgroup_count = dict_row(cur.fetchone())["cnt"]
            
            subgroup_name = f"{parent_name} - Group {subgroup_count + 1}"
            cur = db_execute(conn, "INSERT INTO `groups` (name, parent_group_id) VALUES (?, ?)", (subgroup_name, target_group_id))
            group_id = last_insert_id(cur)
            domain_index = 0
            
            # Assign new subgroup to user
            try:
                db_execute(conn, "INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)", (user_id, group_id))
                log.info(f"[add_domain] Created and assigned subgroup {group_id} to user {user_id}")
            except Exception as e:
                log.warning(f"[add_domain] Could not assign subgroup {group_id}: {e}")
        
        # Insert domain into the subgroup
        cur = db_execute(conn, "INSERT INTO domains (domain_url, domain_name, group_id, domain_index) VALUES (?, ?, ?, ?)", 
                        (url, url, group_id, domain_index))
        new_domain_id = last_insert_id(cur)
        _assign_random_site_templates(conn, new_domain_id, user_id)
        
        # Assign domain to current user
        try:
            db_execute(conn, "INSERT INTO user_domains (user_id, domain_id) VALUES (?, ?)", (user_id, new_domain_id))
            log.info(f"[admin_domains_add] Assigned domain {new_domain_id} to user {user_id}")
        except Exception as e:
            log.warning(f"[admin_domains_add] Could not assign domain {new_domain_id} to user {user_id}: {e}")
    
    # Redirect back to the parent group
    return redirect(url_for("admin_domains") + f"?group_id={target_group_id}")


@app.route("/admin/domains/group-by-4", methods=["POST"])
@login_required
def admin_domains_group_by_4():
    user = get_current_user()
    user_id = user["id"]
    
    # Get group_id from form or query parameter to redirect back
    group_id = request.form.get("group_id") or request.args.get("group_id")
    
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM domains WHERE group_id IS NULL ORDER BY id")
        domains = [dict_row(r) for r in cur.fetchall()]
        for i in range(0, len(domains), 4):
            chunk = domains[i : i + 4]
            cur = db_execute(conn, "INSERT INTO `groups` (name) VALUES (?)", (f"Group {i // 4 + 1}",))
            grp = last_insert_id(cur)
            
            # Assign group to current user
            try:
                db_execute(conn, "INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)", (user_id, grp))
                log.info(f"[group_by_4] Assigned group {grp} to user {user_id}")
            except Exception as e:
                log.warning(f"[group_by_4] Could not assign group {grp} to user {user_id}: {e}")
            
            for j, d in enumerate(chunk):
                db_execute(conn, "UPDATE domains SET group_id = ?, domain_index = ? WHERE id = ?", (grp, j, d["id"]))
    
    redirect_url = url_for("admin_domains")
    if group_id:
        redirect_url += f"?group_id={group_id}"
    return redirect(redirect_url)


@app.route("/admin/domains/bulk-add", methods=["POST"])
@login_required
def admin_domains_bulk_add():
    user = get_current_user()
    user_id = user["id"]
    
    # Check if profile is complete
    if not is_profile_complete(user_id):
        return redirect(url_for("profile") + "?error=" + urllib.parse.quote("Please complete your profile settings before adding domains"))
    
    text = request.form.get("domains", "")
    target_group_id_raw = request.form.get("target_group_id", "").strip()
    target_group_id = int(target_group_id_raw) if target_group_id_raw and target_group_id_raw.isdigit() else None
    
    added, skipped = [], []
    
    # Collect all valid URLs first
    urls_to_add = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        raw = line.split("|", 1)[0].strip() if "|" in line else line
        url = _normalize_domain(raw)
        if url:
            urls_to_add.append(url)
    
    with get_connection() as conn:
        # Check for duplicates
        for url in urls_to_add[:]:
            cur = db_execute(conn, "SELECT id FROM domains WHERE domain_url = ?", (url,))
            if cur.fetchone():
                skipped.append(url)
                urls_to_add.remove(url)
        
        if not urls_to_add:
            if skipped:
                msg = urllib.parse.quote(f"Skipped {len(skipped)} duplicate(s): {', '.join(skipped[:5])}" + (" ..." if len(skipped) > 5 else ""))
                redirect_url = url_for("admin_domains")
                if target_group_id:
                    redirect_url += f"?group_id={target_group_id}&add_error=" + msg
                else:
                    redirect_url += "?add_error=" + msg
                return redirect(redirect_url)
            redirect_url = url_for("admin_domains")
            if target_group_id:
                redirect_url += f"?group_id={target_group_id}"
            return redirect(redirect_url)
        
        # If target group specified, create subgroups with 4 domains each (A, B, C, D)
        if target_group_id:
            # Get parent group name for subgroup naming
            cur = db_execute(conn, "SELECT name FROM `groups` WHERE id = ?", (target_group_id,))
            parent_group = dict_row(cur.fetchone())
            parent_name = parent_group["name"] if parent_group else "Group"
            
            # Count existing domains in this group (for theme round-robin continuity)
            def get_group_descendant_ids(gid):
                result = [gid]
                cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
                for row in cur.fetchall():
                    result.extend(get_group_descendant_ids(dict_row(row)["id"]))
                return result
            group_ids = get_group_descendant_ids(target_group_id)
            placeholders = ",".join(["?"] * len(group_ids))
            cur = db_execute(conn, f"SELECT COUNT(*) as cnt FROM domains WHERE group_id IN ({placeholders})", tuple(group_ids))
            theme_start_index = dict_row(cur.fetchone()).get("cnt") or 0
            
            # Process domains in chunks of 4 (A, B, C, D per subgroup)
            for chunk_idx, i in enumerate(range(0, len(urls_to_add), 4)):
                chunk = urls_to_add[i:i+4]
                
                # Create a new subgroup for each 4 domains
                subgroup_name = f"{parent_name} - Batch {chunk_idx + 1}"
                cur = db_execute(conn, "INSERT INTO `groups` (name, parent_group_id) VALUES (?, ?)", (subgroup_name, target_group_id))
                new_group_id = last_insert_id(cur)
                
                # Assign subgroup to user
                try:
                    db_execute(conn, "INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)", (user_id, new_group_id))
                    log.info(f"[bulk_add] Assigned subgroup {new_group_id} to user {user_id}")
                except Exception as e:
                    log.warning(f"[bulk_add] Could not assign subgroup {new_group_id}: {e}")
                
                # Add domains to this subgroup with indexes 0, 1, 2, 3 (A, B, C, D)
                for domain_index, url in enumerate(chunk):
                    overall_index = theme_start_index + chunk_idx * 4 + domain_index
                    cur = db_execute(conn, "INSERT INTO domains (domain_url, domain_name, group_id, domain_index) VALUES (?, ?, ?, ?)", 
                                   (url, url, new_group_id, domain_index))
                    did = last_insert_id(cur)
                    if did:
                        _assign_random_site_templates(conn, did, user_id, domain_index=overall_index)
                        
                        # Assign domain to current user
                        try:
                            db_execute(conn, "INSERT INTO user_domains (user_id, domain_id) VALUES (?, ?)", (user_id, did))
                            log.info(f"[bulk_add] Assigned domain {did} to user {user_id}")
                        except Exception as e:
                            log.warning(f"[bulk_add] Could not assign domain {did} to user {user_id}: {e}")
                    
                    added.append(url)
        else:
            # No group - add as standalone (count existing domains for theme continuity)
            cur = db_execute(conn, "SELECT COUNT(*) as cnt FROM domains")
            theme_start_index = dict_row(cur.fetchone()).get("cnt") or 0
            
            for idx, url in enumerate(urls_to_add):
                cur = db_execute(conn, "INSERT INTO domains (domain_url, domain_name) VALUES (?, ?)", (url, url))
                did = last_insert_id(cur)
                if did:
                    _assign_random_site_templates(conn, did, user_id, domain_index=theme_start_index + idx)
                    
                    # Assign domain to current user
                    try:
                        db_execute(conn, "INSERT INTO user_domains (user_id, domain_id) VALUES (?, ?)", (user_id, did))
                        log.info(f"[bulk_add] Assigned domain {did} to user {user_id}")
                    except Exception as e:
                        log.warning(f"[bulk_add] Could not assign domain {did} to user {user_id}: {e}")
                
                added.append(url)
    
    redirect_url = url_for("admin_domains")
    if target_group_id:
        redirect_url += f"?group_id={target_group_id}"
    
    if skipped:
        msg = urllib.parse.quote(f"Skipped {len(skipped)} duplicate(s): {', '.join(skipped[:5])}" + (" ..." if len(skipped) > 5 else ""))
        if target_group_id:
            redirect_url += "&add_error=" + msg
        else:
            redirect_url += "?add_error=" + msg
        return redirect(redirect_url)
    
    return redirect(redirect_url)


@app.route("/admin/domains/<int:pk>/templates", methods=["GET"])
def admin_domain_templates(pk):
    """Manage pin templates for a domain: list + add (paste JSON from Pin Editor)."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, domain_url, domain_name FROM domains WHERE id = ?", (pk,))
        d = dict_row(cur.fetchone())
    if not d:
        return redirect(url_for("admin_domains"))
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, name, sort_order, created_at FROM domain_templates WHERE domain_id = ? ORDER BY sort_order, id", (pk,))
        templates = [dict_row(r) for r in cur.fetchall()]
    pin_editor_url = "/pin-editor?domain_id=" + str(pk)
    rows = "".join(
        f'<tr><td>{t["id"]}</td><td>{html.escape(t.get("name") or "")}</td><td>{html.escape(str(t.get("sort_order") or 0))}</td>'
        f'<td><button type="button" class="btn btn-sm btn-outline-secondary" onclick="editTemplate({t["id"]})">Edit</button> '
        f'<button type="button" class="btn btn-sm btn-danger" onclick="deleteTemplate({t["id"]})">Delete</button></td></tr>'
        for t in templates
    )
    content = f"""
    <h2>Pin templates — {html.escape(d.get("domain_url") or "")}</h2>
    <p><a href="{pin_editor_url}" target="_blank" class="btn btn-outline-primary">Open Pin Editor (edit &amp; preview)</a> — Create or edit a template in the editor, then use &quot;Save to domain&quot; there or paste the JSON below.</p>
    <div class="card mb-3">
      <div class="card-header">Add template</div>
      <div class="card-body">
        <div class="mb-2">
          <label class="form-label">Template name</label>
          <input type="text" id="newTemplateName" class="form-control" placeholder="e.g. Recipe Pin 1">
        </div>
        <div class="mb-2">
          <label class="form-label">Paste JSON from Pin Editor (Save JSON in editor, then paste here)</label>
          <textarea id="newTemplateJson" class="form-control font-monospace" rows="12" placeholder='{{"template_name": "template_1", "template_data": {{ ... }}}}'></textarea>
        </div>
        <button type="button" class="btn btn-primary" onclick="saveNewTemplate()">Save template to domain</button>
      </div>
    </div>
    <table class="table table-bordered"><thead><tr><th>ID</th><th>Name</th><th>Order</th><th></th></tr></thead><tbody>{rows or "<tr><td colspan='4' class='text-muted'>No templates yet.</td></tr>"}</tbody></table>
    <a href="/admin/domains" class="btn btn-secondary mt-2">Back to Domains</a>
    <div id="editModal" class="modal fade" tabindex="-1"><div class="modal-dialog modal-lg"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Edit template</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><input type="hidden" id="editId"><label class="form-label">Name</label><input type="text" id="editName" class="form-control mb-2"><label class="form-label">JSON</label><textarea id="editJson" class="form-control font-monospace" rows="12"></textarea></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button><button type="button" class="btn btn-primary" onclick="saveEditTemplate()">Save</button></div></div></div></div>
    <script>
    const domainId = {pk};
    function saveNewTemplate() {{
      const name = document.getElementById('newTemplateName').value.trim() || 'Unnamed';
      const json = document.getElementById('newTemplateJson').value.trim();
      if (!json) {{ alert('Paste JSON first'); return; }}
      fetch('/api/domain-templates', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ domain_id: domainId, name: name, template_json: json }}) }})
        .then(r => r.json()).then(d => {{ alert(d.success ? 'Saved' : (d.error || 'Error')); if (d.success) location.reload(); }}).catch(e => alert(e));
    }}
    function editTemplate(id) {{
      fetch('/api/domain-templates/' + id).then(r => r.json()).then(d => {{
        document.getElementById('editId').value = id;
        document.getElementById('editName').value = d.name || '';
        document.getElementById('editJson').value = typeof d.template_json === 'string' ? d.template_json : JSON.stringify(d.template_json, null, 2);
        new bootstrap.Modal(document.getElementById('editModal')).show();
      }});
    }}
    function saveEditTemplate() {{
      const id = document.getElementById('editId').value;
      const name = document.getElementById('editName').value.trim();
      const json = document.getElementById('editJson').value.trim();
      fetch('/api/domain-templates/' + id, {{ method: 'PUT', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ name: name, template_json: json }}) }})
        .then(r => r.json()).then(d => {{ alert(d.success ? 'Updated' : (d.error || 'Error')); if (d.success) {{ bootstrap.Modal.getInstance(document.getElementById('editModal')).hide(); location.reload(); }} }}).catch(e => alert(e));
    }}
    function deleteTemplate(id) {{
      if (!confirm('Delete this template?')) return;
      fetch('/api/domain-templates/' + id, {{ method: 'DELETE' }}).then(r => r.json()).then(d => {{ if (d.success) location.reload(); else alert(d.error || 'Error'); }}).catch(e => alert(e));
    }}
    </script>
    """
    return base_layout(content, "Pin templates")


@app.route("/api/domain-article-template/<int:domain_id>", methods=["GET", "PUT"])
def api_domain_article_template(domain_id):
    """GET: Return article_template_config for domain. PUT: Save config (body: {config: object} or {config_json: string})."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, domain_url, domain_name, website_template, article_template_config, article_template_preview_url, article_html_snippets, article_template_name FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Domain not found"}), 404
    if request.method == "GET":
        cfg_raw = row.get("article_template_config") or ""
        cfg = {}
        if cfg_raw:
            try:
                cfg = json.loads(cfg_raw) if isinstance(cfg_raw, str) else (cfg_raw or {})
            except json.JSONDecodeError:
                pass
        snippets_raw = row.get("article_html_snippets") or ""
        snippets = {}
        if snippets_raw:
            try:
                snippets = json.loads(snippets_raw) if isinstance(snippets_raw, str) else (snippets_raw or {})
            except json.JSONDecodeError:
                pass
        return jsonify({
            "domain_id": domain_id,
            "domain_name": row.get("domain_url") or row.get("domain_name") or "",
            "domain_url": row.get("domain_url") or "",
            "website_template": row.get("website_template") or "",
            "article_template_name": (row.get("article_template_name") or "").strip() or None,
            "article_template_config": cfg,
            "article_template_preview_url": (row.get("article_template_preview_url") or "").strip() or None,
            "article_html_snippets": snippets,
        })
    # PUT
    data = request.get_json(silent=True) or {}
    cfg = data.get("config") if "config" in data else None
    if cfg is None and "config_json" in data:
        try:
            cfg = json.loads(data["config_json"]) if isinstance(data["config_json"], str) else data["config_json"]
        except (json.JSONDecodeError, TypeError):
            return jsonify({"success": False, "error": "Invalid config_json"}), 400
    clear_config = "config" in data and data["config"] is None
    if not clear_config and cfg is None:
        return jsonify({"success": False, "error": "Missing config or config_json"}), 400
    config_json = json.dumps(cfg, ensure_ascii=False) if cfg is not None else None
    template_name = (data.get("article_template_name") or "").strip() or None
    website_template = (data.get("website_template") or "").strip() or None
    gen = website_template or row.get("website_template") or "generator-1"
    with get_connection() as conn:
        if website_template and clear_config:
            db_execute(conn, "UPDATE domains SET article_template_config = NULL, article_template_name = ?, website_template = ? WHERE id = ?", (template_name, website_template, domain_id))
        elif website_template:
            db_execute(conn, "UPDATE domains SET article_template_config = ?, article_template_name = ?, website_template = ? WHERE id = ?", (config_json, template_name, website_template, domain_id))
        elif clear_config:
            db_execute(conn, "UPDATE domains SET article_template_config = NULL, article_template_name = ? WHERE id = ?", (template_name, domain_id))
        else:
            db_execute(conn, "UPDATE domains SET article_template_config = ?, article_template_name = ? WHERE id = ?", (config_json, template_name, domain_id))

    # Apply new CSS to ALL existing articles in this domain (use {} when cleared so generator defaults apply)
    apply_cfg = cfg if cfg else {}
    updated = _apply_article_template_css_to_domain(domain_id, apply_cfg, gen)
    resp = {"success": True, "domain_id": domain_id}
    if updated is not None:
        resp["articles_updated"] = updated
    elif updated is None:
        resp["css_update_warning"] = "Config saved, but could not apply CSS to existing articles (generator may be unavailable)."
    return jsonify(resp)


@app.route("/api/domain-article-snippets/<int:domain_id>", methods=["GET", "PUT"])
def api_domain_article_snippets(domain_id):
    """GET: Return article_html_snippets for domain. PUT: Save snippets (body: { snippets: { head-end?, after-hero?, before-recipe?, article-end? } })."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, article_html_snippets FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"error": "Domain not found"}), 404
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        snippets = data.get("snippets")
        if snippets is None:
            snippets = {}
        if not isinstance(snippets, dict):
            return jsonify({"success": False, "error": "snippets must be object"}), 400
        snippets_json = json.dumps(snippets, ensure_ascii=False)
        with get_connection() as conn:
            db_execute(conn, "UPDATE domains SET article_html_snippets = ? WHERE id = ?", (snippets_json, domain_id))
        return jsonify({"success": True, "domain_id": domain_id})
    raw = row.get("article_html_snippets") or ""
    snippets = {}
    if raw:
        try:
            snippets = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError:
            pass
    return jsonify({"domain_id": domain_id, "snippets": snippets, "points": [p[0] for p in SNIPPET_POINTS]})


@app.route("/api/article-snippet-preview", methods=["POST"])
def api_article_snippet_preview():
    """Preview article HTML with snippets injected. Body: { article_html, article_css?, snippets }. Returns { html }."""
    data = request.get_json(silent=True) or {}
    html = (data.get("article_html") or "").strip()
    css = (data.get("article_css") or "").strip()
    snippets = data.get("snippets")
    if not html:
        return jsonify({"html": ""})
    if isinstance(snippets, dict):
        html = _inject_snippets_into_html(html, snippets)
    if css:
        html = re.sub(r'<link[^>]*href=["\']css\.css["\'][^>]*/?>', '<style>' + css + '</style>', html, count=1)
    return jsonify({"html": html})


@app.route("/api/domain-article-snippets/<int:domain_id>/apply", methods=["POST"])
def api_domain_article_snippets_apply(domain_id):
    """Apply domain snippets to ALL articles in this domain. Body: { category? } to filter by recipe course."""
    data = request.get_json(silent=True) or {}
    category = (data.get("category") or "").strip()
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT article_html_snippets FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
        if not row:
            return jsonify({"error": "Domain not found"}), 404
        cur = db_execute(conn, "SELECT t.id FROM titles t WHERE t.domain_id = ?", (domain_id,))
        title_ids = [r["id"] for r in cur.fetchall() if r and r.get("id")]
        if category:
            title_ids = _filter_title_ids_by_category(conn, title_ids, category)
    if not title_ids:
        return jsonify({"success": True, "updated": 0, "message": "No articles in domain" + (" (filtered by category)" if category else "")})
    snippets_json = row.get("article_html_snippets") or ""
    updated = 0
    with get_connection() as conn:
        for tid in title_ids:
            cur = db_execute(conn, "SELECT article_html FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
            r = dict_row(cur.fetchone())
            if not r or not (r.get("article_html") or "").strip():
                continue
            html_orig = (r.get("article_html") or "").strip()
            html_new = _inject_snippets_into_article_html(html_orig, snippets_json)
            if html_new != html_orig:
                db_execute(conn, "UPDATE article_content SET article_html = ? WHERE title_id = ? AND language_code = 'en'", (html_new, tid))
                updated += 1
    log.info("[snippets-apply] Domain %s: %s articles updated", domain_id, updated)
    return jsonify({"success": True, "updated": updated, "total": len(title_ids)})


def _filter_title_ids_by_category(conn, title_ids, category):
    """Filter title_ids to only those whose article_content.recipe has course matching category (case-insensitive)."""
    if not category or not title_ids:
        return title_ids
    cat = category.strip().lower()
    if not cat:
        return title_ids
    kept = []
    for tid in title_ids:
        cur = db_execute(conn, "SELECT recipe FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
        r = dict_row(cur.fetchone())
        if not r:
            continue
        recipe_raw = r.get("recipe") or ""
        try:
            recipe = json.loads(recipe_raw) if isinstance(recipe_raw, str) else recipe_raw
            course = (recipe.get("course") or recipe.get("categorie") or "").strip().lower()
            if course == cat:
                kept.append(tid)
        except (json.JSONDecodeError, TypeError):
            continue
    return kept


@app.route("/api/domain-article-snippets/apply-preview", methods=["GET"])
def api_domain_article_snippets_apply_preview():
    """Preview what will be impacted. Query: domain_id OR template, optional category."""
    domain_id = request.args.get("domain_id", type=int)
    template = (request.args.get("template") or "").strip()
    category = (request.args.get("category") or "").strip()
    if domain_id:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT domain_name, domain_url FROM domains WHERE id = ?", (domain_id,))
            row = dict_row(cur.fetchone())
            if not row:
                return jsonify({"error": "Domain not found"}), 404
            domain_name = (row.get("domain_url") or row.get("domain_name") or f"Domain {domain_id}").strip()
            cur = db_execute(conn, "SELECT t.id FROM titles t WHERE t.domain_id = ?", (domain_id,))
            title_ids = [r["id"] for r in cur.fetchall() if r and r.get("id")]
            if category:
                title_ids = _filter_title_ids_by_category(conn, title_ids, category)
        return jsonify({"domain_id": domain_id, "domain_name": domain_name, "article_count": len(title_ids), "category": category or None})
    if template:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id, domain_name, domain_url FROM domains WHERE website_template = ?", (template,))
            domains = [dict_row(r) for r in cur.fetchall() if r]
            domain_names = [(d.get("domain_url") or d.get("domain_name") or f"Domain {d['id']}").strip() for d in domains]
            all_tids = []
            for d in domains:
                cur = db_execute(conn, "SELECT t.id FROM titles t WHERE t.domain_id = ?", (d["id"],))
                all_tids.extend([r["id"] for r in cur.fetchall() if r and r.get("id")])
            if category:
                all_tids = _filter_title_ids_by_category(conn, all_tids, category)
        return jsonify({"template": template, "domain_names": domain_names, "domain_count": len(domains), "article_count": len(all_tids), "category": category or None})
    return jsonify({"error": "domain_id or template required"}), 400


@app.route("/api/article-categories", methods=["GET"])
def api_article_categories():
    """Return distinct course values from article_content.recipe (for snippet editor category filter)."""
    cats = set()
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT recipe FROM article_content WHERE recipe IS NOT NULL AND recipe != '' LIMIT 10000")
        for row in cur.fetchall():
            r = dict_row(row)
            recipe_raw = r.get("recipe") or ""
            try:
                recipe = json.loads(recipe_raw) if isinstance(recipe_raw, str) else recipe_raw
                c = (recipe.get("course") or recipe.get("categorie") or "").strip()
                if c:
                    cats.add(c)
            except (json.JSONDecodeError, TypeError):
                pass
    return jsonify({"categories": sorted(cats)})


@app.route("/api/website-templates", methods=["GET"])
def api_website_templates():
    """Return distinct website_template values from domains (for snippet editor template dropdown)."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT DISTINCT website_template FROM domains WHERE website_template IS NOT NULL AND TRIM(COALESCE(website_template,'')) != '' ORDER BY website_template")
        rows = [r.get("website_template", "").strip() for r in cur.fetchall() if r and (r.get("website_template") or "").strip()]
    return jsonify({"templates": rows})


def _list_site_templates():
    """List available site templates. Prefer website-parts-generator API; fallback to site_templates/ JSON."""
    out = {"headers": [], "footers": [], "categories": [], "side_articles": [], "writers": [], "indexes": [], "article_cards": []}
    # Try website-parts-generator API first
    base_url = (WEBSITE_PARTS_API_URL or "").rstrip("/")
    if base_url:
        try:
            req = urllib.request.Request(base_url + "/templates", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            tmpl = data.get("templates") or {}
            key_map = {"header": "headers", "footer": "footers", "category": "categories", "sidebar": "side_articles", "writer": "writers", "index": "indexes", "article_card": "article_cards"}
            for api_key, out_key in key_map.items():
                names = tmpl.get(api_key) or []
                for n in names:
                    out[out_key].append({"name": str(n), "label": str(n).replace("_", "-")})
            if any(out[k] for k in out):
                return out
        except Exception:
            pass
    # Fallback: site_templates/ JSON files
    base = SITE_TEMPLATES_DIR
    if os.path.isdir(base):
        folders = {"headers": "headers", "footers": "footers", "categories": "categories", "side_articles": "side_articles", "writers": "writers", "indexes": "indexes"}
        for key, subdir in folders.items():
            folder = os.path.join(base, subdir)
            if not os.path.isdir(folder):
                continue
            for f in sorted(os.listdir(folder)):
                if not f.endswith(".json"):
                    continue
                path = os.path.join(folder, f)
                try:
                    with open(path, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                    name = (data.get("name") or f.replace(".json", "")).strip()
                    label = (data.get("label") or name).strip()
                    out[key].append({"name": name, "label": label})
                except Exception:
                    pass
    # Final fallback: built-in names from website-parts-generator
    if not any(out[k] for k in out):
        out["headers"] = [{"name": "header_1", "label": "header-1"}, {"name": "header_2", "label": "header-2"}, {"name": "header_3", "label": "header-3"}]
        out["footers"] = [{"name": "footer_1", "label": "footer-1"}, {"name": "footer_2", "label": "footer-2"}, {"name": "footer_3", "label": "footer-3"}]
        out["categories"] = [{"name": "category_1", "label": "category-1"}, {"name": "category_2", "label": "category-2"}]
        out["side_articles"] = [{"name": "sidebar_1", "label": "sidebar-1"}, {"name": "sidebar_2", "label": "sidebar-2"}]
        out["writers"] = [{"name": "writer_1", "label": "writer-1"}]
        out["indexes"] = [{"name": "index_1", "label": "index-1"}]
        out["article_cards"] = [{"name": "article_card_1", "label": "article-card-1"}, {"name": "article_card_2", "label": "article-card-2"}]
    if "article_cards" not in out or not out["article_cards"]:
        out["article_cards"] = [{"name": "article_card_1", "label": "article-card-1"}, {"name": "article_card_2", "label": "article-card-2"}]
    return out


@app.route("/api/generate-site-part", methods=["POST"])
def api_generate_site_part():
    """Generate header, footer, category, or sidebar HTML+CSS via website-parts-generator. Body: { part: 'header'|'footer'|'category'|'sidebar', name: 'header_1', config: {...} }."""
    data = request.get_json(silent=True) or {}
    part = (data.get("part") or "").strip().lower()
    name = (data.get("name") or data.get("template") or "").strip()
    config = data.get("config") or {}
    if part not in ("header", "footer", "category", "sidebar", "writer", "index"):
        return jsonify({"success": False, "error": "part must be header, footer, category, sidebar, writer, or index"}), 400
    if not name:
        return jsonify({"success": False, "error": "name required"}), 400
    base = (WEBSITE_PARTS_API_URL or "").rstrip("/")
    if not base:
        return jsonify({"success": False, "error": "WEBSITE_PARTS_API_URL not set. Start website-parts-generator on port 8010."}), 500
    url = f"{base}/generate/{part}/{name}"
    try:
        req = urllib.request.Request(url, data=json.dumps(config).encode("utf-8"), method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            out = json.loads(resp.read().decode())
        return jsonify(out)
    except urllib.error.HTTPError as e:
        err = e.read().decode() if e.fp else str(e)
        return jsonify({"success": False, "error": err[:500], "hint": "Is website-parts-generator running on port 8010?"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/site-templates", methods=["GET"])
def api_site_templates():
    """List available header, footer, category, side_article templates for domain assignment."""
    return jsonify(_list_site_templates())


@app.route("/api/domains/<int:domain_id>/site-templates", methods=["GET", "PUT"])
def api_domain_site_templates(domain_id):
    """GET: Return domain's header/footer/side/category template assignments. PUT: Save assignments."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, header_template, footer_template, side_article_template, category_page_template, writer_template, index_template, article_card_template FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"success": False, "error": "Domain not found"}), 404
    if request.method == "GET":
        return jsonify({
            "success": True,
            "header_template": (row.get("header_template") or "").strip() or None,
            "footer_template": (row.get("footer_template") or "").strip() or None,
            "side_article_template": (row.get("side_article_template") or "").strip() or None,
            "category_page_template": (row.get("category_page_template") or "").strip() or None,
            "writer_template": (row.get("writer_template") or "").strip() or None,
            "index_template": (row.get("index_template") or "").strip() or None,
            "article_card_template": (row.get("article_card_template") or "").strip() or None,
        })
    data = request.get_json(silent=True) or {}
    updates = {}
    for k in ("header_template", "footer_template", "side_article_template", "category_page_template", "writer_template", "index_template", "article_card_template"):
        if k in data:
            v = (data.get(k) or "").strip() or None
            updates[k] = v
    if not updates:
        return jsonify({"success": False, "error": "No fields to update"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT header_template, footer_template, side_article_template, category_page_template, writer_template, index_template, article_card_template FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
        if not row:
            return jsonify({"success": False, "error": "Domain not found"}), 404
        header = (updates.get("header_template", row.get("header_template") or "") or "").strip() or None
        footer = (updates.get("footer_template", row.get("footer_template") or "") or "").strip() or None
        side = (updates.get("side_article_template", row.get("side_article_template") or "") or "").strip() or None
        category = (updates.get("category_page_template", row.get("category_page_template") or "") or "").strip() or None
        writer = (updates.get("writer_template", row.get("writer_template") or "") or "").strip() or None
        index_tpl = (updates.get("index_template", row.get("index_template") or "") or "").strip() or None
        ac_tpl = (updates.get("article_card_template", row.get("article_card_template") or "") or "").strip() or None
        db_execute(conn, "UPDATE domains SET header_template=?, footer_template=?, side_article_template=?, category_page_template=?, writer_template=?, index_template=?, article_card_template=? WHERE id=?",
                   (header, footer, side, category, writer, index_tpl, ac_tpl, domain_id))
    return jsonify({"success": True})


@app.route("/api/domains/<int:domain_id>/site-part-preview", methods=["POST"])
def api_domain_site_part_preview(domain_id):
    """Return HTML+CSS for a site part (header, footer, sidebar, category, writer, index) using domain's colors/fonts. Body: { part, name }."""
    data = request.get_json(silent=True) or {}
    part = (data.get("part") or "").strip().lower()
    name = (data.get("name") or data.get("template") or "").strip()
    if part not in ("header", "footer", "category", "sidebar", "writer", "index"):
        return jsonify({"success": False, "error": "part must be header, footer, category, sidebar, writer, or index"}), 400
    if not name:
        return jsonify({"success": False, "error": "name required"}), 400
    ctx = _get_domain_website_context(domain_id)
    if not ctx:
        return jsonify({"success": False, "error": "Domain not found"}), 404
    config = dict(ctx.get("config") or {})
    if part == "category":
        config.setdefault("category_name", "Recipes")
        config.setdefault("articles", [])
    elif part == "writer":
        config.setdefault("writer", {"name": "Sample Writer", "title": "Food Blogger", "bio": "Sample bio", "avatar": ""})
    elif part == "index":
        config.setdefault("articles", [])
        config.setdefault("categories", [])
    result = _fetch_site_part_internal(part, name, config)
    if result is None:
        return jsonify({"success": False, "error": "Failed to generate preview"}), 500
    return jsonify({"success": True, "html": result.get("html") or "", "css": result.get("css") or ""})


@app.route("/api/domains/random-distribute-site-templates", methods=["POST"])
def api_domains_random_distribute_site_templates():
    """Randomly assign header, footer, side_article, category templates to selected domains. Body: { domain_ids: [1,2,3] } or { domain_ids: "all" }."""
    import random
    data = request.get_json(silent=True) or {}
    domain_ids = data.get("domain_ids")
    if domain_ids == "all" or domain_ids == ["all"]:
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id FROM domains ORDER BY id")
            domain_ids = [r["id"] for r in cur.fetchall() if r and r.get("id")]
    elif not isinstance(domain_ids, list):
        return jsonify({"success": False, "error": "domain_ids must be array or 'all'"}), 400
    else:
        domain_ids = [int(x) for x in domain_ids if x is not None]
    if not domain_ids:
        return jsonify({"success": False, "error": "No domains"}), 400
    templates = _list_site_templates()
    headers = [t["name"] for t in templates["headers"]] or ["header_1", "header_2", "header_3"]
    footers = [t["name"] for t in templates["footers"]] or ["footer_1", "footer_2", "footer_3"]
    sides = [t["name"] for t in templates["side_articles"]] or ["sidebar_1", "sidebar_2"]
    categories = [t["name"] for t in templates["categories"]] or ["category_1", "category_2"]
    writers = [t["name"] for t in templates["writers"]] or ["writer_1"]
    indexes = [t["name"] for t in templates["indexes"]] or ["index_1"]
    article_cards = [t["name"] for t in templates.get("article_cards", [])] or ["article_card_1", "article_card_2"]
    updated = 0
    with get_connection() as conn:
        for did in domain_ids:
            h = random.choice(headers)
            f = random.choice(footers)
            s = random.choice(sides)
            c = random.choice(categories)
            w = random.choice(writers)
            idx = random.choice(indexes)
            ac = random.choice(article_cards)
            palette = random.choice(RANDOM_COLOR_PALETTES)
            domain_colors_json = json.dumps(palette)
            db_execute(conn, "UPDATE domains SET header_template=?, footer_template=?, side_article_template=?, category_page_template=?, writer_template=?, index_template=?, article_card_template=?, domain_colors=? WHERE id=?",
                       (h, f, s, c, w, idx, ac, domain_colors_json, did))
            updated += 1
    return jsonify({"success": True, "updated": updated, "message": f"Random templates assigned to {updated} domain(s)"})


# --- Full Website Preview ---
def _build_group_filter_alert(group_hierarchy_path, domain_count):
    """Build the group filter alert HTML without backslashes in f-string."""
    if not group_hierarchy_path:
        return ""
    path_str = " > ".join(bc['name'] for bc in group_hierarchy_path)
    close_onclick = 'window.location.href="/admin/domains"'
    return f"<div class='alert alert-info alert-dismissible'><strong>Filtered by group:</strong> {path_str} <span class='badge bg-primary'>{domain_count} domain(s)</span> <button type='button' class='btn-close' onclick='{close_onclick}'></button></div>"


def _get_domain_page_theme(domain_row):
    """Extract the active domain-page theme from any saved domain page JSON."""
    for slug in ("domain_page_about_us", "domain_page_terms_of_use", "domain_page_privacy_policy",
                 "domain_page_gdpr_policy", "domain_page_cookie_policy", "domain_page_copyright_policy",
                 "domain_page_disclaimer", "domain_page_contact_us"):
        raw = (domain_row.get(slug) or "").strip()
        if not raw:
            continue
        try:
            j = json.loads(raw)
            t = (j.get("theme") or "").strip()
            if t:
                return t
        except (json.JSONDecodeError, AttributeError):
            pass
    return ""


def _build_group_filter_alert(group_hierarchy_path, domain_count):
    """Build the group filter alert HTML without f-string backslashes."""
    if not group_hierarchy_path:
        return ""
    hierarchy_text = " > ".join(bc['name'] for bc in group_hierarchy_path)
    close_onclick = 'window.location.href="/admin/domains"'
    return (f"<div class='alert alert-info alert-dismissible'><strong>Filtered by group:</strong> {hierarchy_text} "
            f"<span class='badge bg-primary'>{domain_count} domain(s)</span> "
            f"<button type='button' class='btn-close' onclick='{close_onclick}'></button></div>")


def _get_customizations_script(domain_id):
    """Return script to apply saved visual customizations (respects scope: page/domain/template)."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT visual_customizations FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return ""
    
    raw = (row.get("visual_customizations") or "").strip()
    if not raw:
        return ""
    
    try:
        customizations = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        return ""
    
    if not isinstance(customizations, list) or not customizations:
        return ""
    
    # Get current page URL from request context
    current_page = request.path
    
    script_parts = ["<script>document.addEventListener('DOMContentLoaded', function() {"]
    script_parts.append(f"  var currentPage = '{current_page}';")
    
    for c in customizations:
        selector = (c.get("selector") or "").strip()
        if not selector:
            continue
        
        scope = c.get("scope", "domain")
        page_url = c.get("pageUrl", "")
        
        # Skip if scope=page and pageUrl doesn't match
        if scope == "page" and page_url and page_url != current_page:
            continue
        
        styles = (c.get("styles") or "").strip()
        text_override = c.get("textOverride")
        insert_after = (c.get("insertAfter") or "").strip()
        
        selector_escaped = selector.replace("'", "\\'").replace('"', '\\"')
        
        if styles or text_override is not None:
            script_parts.append(f"  var el = document.querySelector('{selector_escaped}');")
            script_parts.append(f"  if (el) {{")
            if styles:
                styles_escaped = styles.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
                script_parts.append(f"    el.style.cssText += '{styles_escaped}';")
            if text_override is not None:
                text_escaped = str(text_override).replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")
                script_parts.append(f"    if (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3) el.textContent = '{text_escaped}';")
            script_parts.append(f"  }}")
        
        if insert_after:
            insert_escaped = insert_after.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
            script_parts.append(f"  var afterEl = document.querySelector('{selector_escaped}');")
            script_parts.append(f"  if (afterEl) afterEl.insertAdjacentHTML('afterend', '{insert_escaped}');")
    
    script_parts.append("});</script>")
    return "\n".join(script_parts)


def _get_visual_editor_html(domain_id):
    """Return visual editor overlay HTML/CSS/JS for preview pages."""
    return f"""
<div id="visualEditorOverlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:999999;"></div>
<div id="visualEditorPanel" style="display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#fff;border-radius:12px;box-shadow:0 10px 40px rgba(0,0,0,0.3);z-index:1000000;max-width:500px;width:90%;max-height:80vh;overflow:auto;">
  <div style="padding:1rem;border-bottom:1px solid #ddd;display:flex;justify-content:space-between;align-items:center;">
    <h3 style="margin:0;font-size:1.1rem;">Edit Element</h3>
    <button id="veCloseBtn" style="background:none;border:none;font-size:1.5rem;cursor:pointer;padding:0;width:30px;height:30px;">&times;</button>
  </div>
  <div id="veContent" style="padding:1rem;"></div>
</div>
<button id="veToggleBtn" style="position:fixed;bottom:20px;right:20px;background:#6C8AE4;color:#fff;border:none;border-radius:50%;width:60px;height:60px;font-size:1.5rem;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.2);z-index:999998;">✏️</button>
<button id="dsToggleBtn" style="position:fixed;bottom:90px;right:20px;background:#22c55e;color:#fff;border:none;border-radius:50%;width:50px;height:50px;font-size:1.3rem;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.2);z-index:999998;" title="Domain Settings">⚙️</button>
<div id="dsOverlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:1000001;"></div>
<div id="dsPanel" style="display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#fff;border-radius:16px;box-shadow:0 12px 48px rgba(0,0,0,0.3);z-index:1000002;max-width:520px;width:94%;max-height:85vh;overflow:auto;font-family:Inter,system-ui,sans-serif;">
  <div style="padding:1.25rem 1.5rem;border-bottom:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;background:linear-gradient(135deg,#22c55e 0%,#16a34a 100%);border-radius:16px 16px 0 0;">
    <h3 style="margin:0;font-size:1.15rem;color:#fff;font-weight:700;">⚙️ Domain Settings</h3>
    <button id="dsCloseBtn" style="background:rgba(255,255,255,0.2);border:none;font-size:1.2rem;cursor:pointer;padding:0;width:32px;height:32px;border-radius:50%;color:#fff;line-height:1;">&times;</button>
  </div>
  <div id="dsBody" style="padding:1.5rem;">
    <p style="text-align:center;color:#6b7280;font-size:0.9rem;">Loading…</p>
  </div>
</div>
<script>
(function(){{
  const DS_ID = {domain_id};
  const FONT_OPTIONS = {json.dumps(FONT_FAMILY_OPTIONS)};
  const COLOR_KEYS = ['primary','secondary','background','text_primary','text_secondary','border'];
  const COLOR_LABELS = {{primary:'Primary',secondary:'Secondary',background:'Background',text_primary:'Text Primary',text_secondary:'Text Secondary',border:'Border'}};
  const dsBtn = document.getElementById('dsToggleBtn');
  const dsOverlay = document.getElementById('dsOverlay');
  const dsPanel = document.getElementById('dsPanel');
  const dsClose = document.getElementById('dsCloseBtn');
  const dsBody = document.getElementById('dsBody');
  let dsLoaded = false;

  function closeDsPanel(){{ dsOverlay.style.display='none'; dsPanel.style.display='none'; }}
  dsClose.addEventListener('click', closeDsPanel);
  dsOverlay.addEventListener('click', closeDsPanel);

  dsBtn.addEventListener('click', async function(){{
    dsOverlay.style.display='block'; dsPanel.style.display='block';
    if (dsLoaded) return;
    dsBody.innerHTML = '<p style="text-align:center;color:#6b7280;font-size:0.9rem;">Loading…</p>';
    try {{
      const [cRes, fRes] = await Promise.all([
        fetch('/api/domains/'+DS_ID+'/colors').then(r=>r.json()),
        fetch('/api/domains/'+DS_ID+'/fonts').then(r=>r.json())
      ]);
      const colors = cRes.colors || {{}};
      const fonts = fRes.fonts || {{}};
      renderDsForm(colors, fonts);
      dsLoaded = true;
    }} catch(e) {{
      dsBody.innerHTML = '<p style="color:#ef4444;">Error loading: '+e+'</p>';
    }}
  }});

  function renderDsForm(colors, fonts){{
    let colorsHtml = '<div style="margin-bottom:1.25rem;"><h4 style="font-size:0.95rem;font-weight:700;color:#111;margin:0 0 0.75rem;">🎨 Colors</h4><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.75rem;">';
    COLOR_KEYS.forEach(function(key){{
      const val = colors[key] || '#888888';
      const label = COLOR_LABELS[key] || key;
      colorsHtml += '<div style="text-align:center;"><label style="display:block;font-size:0.72rem;color:#6b7280;margin-bottom:0.3rem;font-weight:600;text-transform:uppercase;letter-spacing:0.03em;">'+label+'</label><input type="color" class="ds-color-input" data-key="'+key+'" value="'+val+'" style="width:100%;height:40px;border:2px solid #e5e7eb;border-radius:8px;cursor:pointer;padding:2px;transition:border-color 0.2s;"><span class="ds-color-hex" style="display:block;font-size:0.7rem;color:#9ca3af;margin-top:0.2rem;font-family:monospace;">'+val+'</span></div>';
    }});
    colorsHtml += '</div></div>';

    let fontsHtml = '<div style="margin-bottom:1.25rem;"><h4 style="font-size:0.95rem;font-weight:700;color:#111;margin:0 0 0.75rem;">🔤 Fonts</h4><div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">';
    // Heading font
    let hOpts = FONT_OPTIONS.map(function(f){{ return '<option value="'+f+'"'+(fonts.heading_family===f?' selected':'')+'>'+f+'</option>'; }}).join('');
    fontsHtml += '<div><label style="display:block;font-size:0.72rem;color:#6b7280;margin-bottom:0.3rem;font-weight:600;text-transform:uppercase;letter-spacing:0.03em;">Heading Font</label><select id="ds-heading-font" style="width:100%;padding:0.5rem;border:1px solid #e5e7eb;border-radius:8px;font-size:0.85rem;background:#fff;">'+hOpts+'</select></div>';
    // Body font
    let bOpts = FONT_OPTIONS.map(function(f){{ return '<option value="'+f+'"'+(fonts.body_family===f?' selected':'')+'>'+f+'</option>'; }}).join('');
    fontsHtml += '<div><label style="display:block;font-size:0.72rem;color:#6b7280;margin-bottom:0.3rem;font-weight:600;text-transform:uppercase;letter-spacing:0.03em;">Body Font</label><select id="ds-body-font" style="width:100%;padding:0.5rem;border:1px solid #e5e7eb;border-radius:8px;font-size:0.85rem;background:#fff;">'+bOpts+'</select></div>';
    fontsHtml += '</div></div>';

    // Info section
    let infoHtml = '<div style="margin-bottom:1.25rem;padding:0.75rem;background:#f0fdf4;border-radius:8px;border:1px solid #bbf7d0;"><p style="margin:0;font-size:0.8rem;color:#166534;">Domain ID: <strong>'+DS_ID+'</strong> &mdash; <a href="/admin/domains" target="_blank" style="color:#16a34a;text-decoration:underline;">Admin Panel</a></p></div>';

    let btnsHtml = '<div style="display:flex;gap:0.75rem;margin-top:0.5rem;">';
    btnsHtml += '<button id="dsSaveBtn" style="flex:1;padding:0.75rem;background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;border:none;border-radius:10px;font-weight:700;font-size:0.9rem;cursor:pointer;transition:opacity 0.2s;">💾 Save & Reload</button>';
    btnsHtml += '<button id="dsCancelBtn" style="flex:0 0 auto;padding:0.75rem 1.25rem;background:#f3f4f6;color:#374151;border:1px solid #d1d5db;border-radius:10px;font-weight:600;font-size:0.9rem;cursor:pointer;">Cancel</button>';
    btnsHtml += '</div>';

    dsBody.innerHTML = infoHtml + colorsHtml + fontsHtml + btnsHtml;

    // Update hex labels live
    dsBody.querySelectorAll('.ds-color-input').forEach(function(inp){{
      inp.addEventListener('input', function(){{
        const hexSpan = this.parentElement.querySelector('.ds-color-hex');
        if(hexSpan) hexSpan.textContent = this.value;
        this.style.borderColor = this.value;
      }});
      inp.style.borderColor = inp.value;
    }});

    document.getElementById('dsCancelBtn').addEventListener('click', closeDsPanel);
    document.getElementById('dsSaveBtn').addEventListener('click', async function(){{
      const btn = this;
      btn.disabled = true; btn.textContent = 'Saving…'; btn.style.opacity = '0.6';
      try {{
        // Collect colors
        const newColors = {{}};
        dsBody.querySelectorAll('.ds-color-input').forEach(function(inp){{
          newColors[inp.dataset.key] = inp.value;
        }});
        // Collect fonts
        const newFonts = {{
          heading_family: document.getElementById('ds-heading-font').value,
          body_family: document.getElementById('ds-body-font').value
        }};
        // Save colors
        await fetch('/api/domains/'+DS_ID+'/colors', {{
          method:'PUT',
          headers:{{'Content-Type':'application/json'}},
          body:JSON.stringify({{colors:newColors, update_articles:false}})
        }});
        // Save fonts
        await fetch('/api/domains/'+DS_ID+'/fonts', {{
          method:'PUT',
          headers:{{'Content-Type':'application/json'}},
          body:JSON.stringify({{fonts:newFonts, update_articles:false}})
        }});
        btn.textContent = '✓ Saved! Reloading…'; btn.style.background = '#16a34a';
        setTimeout(function(){{ window.location.reload(); }}, 600);
      }} catch(e) {{
        alert('Save failed: '+e);
        btn.disabled = false; btn.textContent = '💾 Save & Reload'; btn.style.opacity = '1';
      }}
    }});
  }}
}})();
</script>
<style>
.ve-highlight {{ outline:2px dashed #6C8AE4 !important; outline-offset:2px; cursor:pointer !important; }}
.ve-active {{ background:rgba(108,138,228,0.1) !important; }}
.ve-insert-point {{ position:relative; }}
.ve-insert-point::after {{ content:'+ Insert'; position:absolute; left:50%; transform:translateX(-50%); bottom:-20px; background:#22c55e; color:#fff; padding:4px 12px; border-radius:6px; font-size:0.75rem; opacity:0; transition:opacity 0.2s; pointer-events:none; }}
.ve-insert-point:hover::after {{ opacity:1; }}
#dsPanel::-webkit-scrollbar {{ width:6px; }} #dsPanel::-webkit-scrollbar-thumb {{ background:#d1d5db; border-radius:3px; }}
.ds-color-input:hover {{ border-color:#22c55e !important; box-shadow:0 0 0 3px rgba(34,197,94,0.15); }}
</style>
<script>
(function(){{
  let editMode = false;
  let selectedEl = null;
  let domainId = {domain_id};
  
  const overlay = document.getElementById('visualEditorOverlay');
  const panel = document.getElementById('visualEditorPanel');
  const toggleBtn = document.getElementById('veToggleBtn');
  const closeBtn = document.getElementById('veCloseBtn');
  const content = document.getElementById('veContent');
  
  toggleBtn.addEventListener('click', () => {{
    editMode = !editMode;
    toggleBtn.textContent = editMode ? '🔒' : '✏️';
    toggleBtn.title = editMode ? 'Exit edit mode' : 'Enter edit mode';
    if (!editMode) {{
      document.querySelectorAll('.ve-highlight').forEach(el => el.classList.remove('ve-highlight'));
      closePanel();
    }}
  }});
  
  closeBtn.addEventListener('click', closePanel);
  overlay.addEventListener('click', closePanel);
  
  function closePanel() {{
    overlay.style.display = 'none';
    panel.style.display = 'none';
    if (selectedEl) {{
      selectedEl.classList.remove('ve-active');
      selectedEl = null;
    }}
  }}
  
  document.body.addEventListener('click', (e) => {{
    if (!editMode) return;
    if (e.target.closest('#visualEditorPanel, #veToggleBtn')) return;
    
    e.preventDefault();
    e.stopPropagation();
    
    const target = e.target;
    if (target.classList.contains('ve-insert-point')) {{
      openInsertModal(target);
      return;
    }}
    
    document.querySelectorAll('.ve-active').forEach(el => el.classList.remove('ve-active'));
    target.classList.add('ve-active');
    selectedEl = target;
    
    openEditPanel(target);
  }}, true);
  
  document.body.addEventListener('mouseover', (e) => {{
    if (!editMode) return;
    if (e.target.closest('#visualEditorPanel, #veToggleBtn')) return;
    e.target.classList.add('ve-highlight');
  }}, true);
  
  document.body.addEventListener('mouseout', (e) => {{
    if (!editMode) return;
    e.target.classList.remove('ve-highlight');
  }}, true);
  
  function openEditPanel(el) {{
    const computed = window.getComputedStyle(el);
    const isText = el.childNodes.length === 1 && el.childNodes[0].nodeType === 3;
    const textContent = isText ? el.textContent.trim() : '';
    
    // Extract all colors from element
    const allColors = extractAllColors(el);
    
    // Check if element has gradient
    const hasGradient = computed.backgroundImage && computed.backgroundImage !== 'none' && computed.backgroundImage.includes('gradient');
    const gradientValue = hasGradient ? computed.backgroundImage : '';
    
    // Build color inputs HTML dynamically
    let colorsHtml = '';
    if (allColors.length > 0) {{
      colorsHtml = '<div><label style="display:block;font-weight:600;margin-bottom:0.5rem;">Colors Detected (' + allColors.length + ')</label><div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">';
      allColors.forEach((colorData, idx) => {{
        const inputId = 'veColor' + idx;
        const isGradient = colorData.isGradient || false;
        const isShadow = colorData.isShadow || false;
        const warningIcon = (isGradient || isShadow) ? '⚠️ ' : '';
        colorsHtml += `
          <div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
              <label style="font-size:0.85rem;color:#666;">${{warningIcon}}${{colorData.label}}</label>
              <button onclick="resetColor('${{inputId}}', '${{colorData.value}}')" style="font-size:0.7rem;padding:2px 6px;background:#e5e7eb;border:none;border-radius:4px;cursor:pointer;" title="Reset to default">Reset</button>
            </div>
            <input type="color" id="${{inputId}}" value="${{colorData.hex}}" data-property="${{colorData.property}}" style="width:100%;height:40px;border:1px solid #ddd;border-radius:6px;">
            <div style="font-size:0.7rem;color:#666;margin-top:0.25rem;">${{colorData.value}}</div>
          </div>
        `;
      }});
      colorsHtml += '</div>';
      if (hasGradient) {{
        colorsHtml += '<p style="font-size:0.75rem;color:#f59e0b;margin-top:0.5rem;">⚠️ Gradient detected. Edit full gradient in Custom CSS below.</p>';
      }}
      colorsHtml += '</div>';
    }}
    
    content.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:1rem;">
        <div>
          <label style="display:block;font-weight:600;margin-bottom:0.5rem;">Element</label>
          <input type="text" value="${{el.tagName.toLowerCase()}}" readonly style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;background:#f5f5f5;">
        </div>
        
        ${{isText ? `
        <div>
          <label style="display:block;font-weight:600;margin-bottom:0.5rem;">Text Content</label>
          <textarea id="veTextInput" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;min-height:80px;">${{textContent}}</textarea>
          <p style="font-size:0.75rem;color:#666;margin-top:0.25rem;">⚠️ Changes are static overrides (won't update from DB)</p>
        </div>
        ` : ''}}
        
        ${{colorsHtml}}
        
        <div>
          <label style="display:block;font-weight:600;margin-bottom:0.5rem;">Other CSS Properties</label>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
            <div>
              <label style="font-size:0.85rem;color:#666;">Font Size</label>
              <input type="text" id="veFontSize" value="${{computed.fontSize}}" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;">
            </div>
            <div>
              <label style="font-size:0.85rem;color:#666;">Width</label>
              <input type="text" id="veWidth" value="${{computed.width}}" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;">
            </div>
            <div>
              <label style="font-size:0.85rem;color:#666;">Height</label>
              <input type="text" id="veHeight" value="${{computed.height}}" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;">
            </div>
            <div>
              <label style="font-size:0.85rem;color:#666;">Padding</label>
              <input type="text" id="vePadding" value="${{computed.padding}}" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;">
            </div>
            <div>
              <label style="font-size:0.85rem;color:#666;">Margin</label>
              <input type="text" id="veMargin" value="${{computed.margin}}" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;">
            </div>
            <div>
              <label style="font-size:0.85rem;color:#666;">Border</label>
              <input type="text" id="veBorder" value="${{computed.border}}" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;">
            </div>
          </div>
        </div>
        
        <div>
          <label style="display:block;font-weight:600;margin-bottom:0.5rem;">Custom CSS</label>
          <textarea id="veCustomCss" placeholder="property: value;" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;min-height:60px;font-family:monospace;font-size:0.85rem;">${{hasGradient ? 'background-image: ' + gradientValue : ''}}</textarea>
          <p style="font-size:0.75rem;color:#666;margin-top:0.25rem;">💡 Edit any CSS property here (e.g., gradients, shadows, transforms)</p>
        </div>
        
        <div>
          <label style="display:block;font-weight:600;margin-bottom:0.5rem;">Apply Scope</label>
          <select id="veScopeSelect" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;background:#fff;">
            <option value="page">This page only</option>
            <option value="domain" selected>Entire domain (all articles)</option>
            <option value="template">All domains using this article template</option>
          </select>
          <p style="font-size:0.75rem;color:#666;margin-top:0.25rem;" id="veScopeHint">Changes will apply to all pages in this domain</p>
        </div>
        
        <div style="display:flex;gap:0.5rem;">
          <button id="veApplyBtn" style="flex:1;padding:0.75rem;background:#6C8AE4;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;">Apply Changes</button>
          <button id="veSaveBtn" style="flex:1;padding:0.75rem;background:#22c55e;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;">Save</button>
        </div>
        
        <div style="border-top:1px solid #ddd;padding-top:1rem;">
          <button id="veInsertBtn" style="width:100%;padding:0.75rem;background:#f59e0b;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;">Insert HTML/Script After This</button>
        </div>
      </div>
    `;
    
    overlay.style.display = 'block';
    panel.style.display = 'block';
    
    const scopeSelect = document.getElementById('veScopeSelect');
    const scopeHint = document.getElementById('veScopeHint');
    scopeSelect.addEventListener('change', () => {{
      const scope = scopeSelect.value;
      if (scope === 'page') scopeHint.textContent = 'Changes will apply only to this specific page';
      else if (scope === 'domain') scopeHint.textContent = 'Changes will apply to all pages in this domain';
      else if (scope === 'template') scopeHint.textContent = 'Changes will apply to all domains using this article template';
    }});
    
    document.getElementById('veApplyBtn').addEventListener('click', () => applyChanges(el));
    document.getElementById('veSaveBtn').addEventListener('click', () => saveChanges(el));
    document.getElementById('veInsertBtn').addEventListener('click', () => openInsertModal(el));
  }}
  
  function applyChanges(el) {{
    const isText = el.childNodes.length === 1 && el.childNodes[0].nodeType === 3;
    if (isText) {{
      const newText = document.getElementById('veTextInput')?.value;
      if (newText !== undefined) el.textContent = newText;
    }}
    
    // Apply all dynamic color inputs
    const colorInputs = document.querySelectorAll('[id^="veColor"]');
    colorInputs.forEach(input => {{
      const prop = input.dataset.property;
      const val = input.value;
      if (prop && val) {{
        if (prop === 'color') el.style.color = val;
        else if (prop === 'backgroundColor') el.style.backgroundColor = val;
        else if (prop === 'borderColor') el.style.borderColor = val;
        else if (prop === 'outlineColor') el.style.outlineColor = val;
        else if (prop.startsWith('background-gradient-')) {{
          // For gradients, we'll update via custom CSS
          const gradientNote = document.getElementById('veCustomCss');
          if (gradientNote) gradientNote.value += '\\n/* Gradient colors updated - edit full gradient in Custom CSS if needed */';
        }}
      }}
    }});
    
    // Apply other properties
    const fontSize = document.getElementById('veFontSize')?.value;
    const width = document.getElementById('veWidth')?.value;
    const height = document.getElementById('veHeight')?.value;
    const padding = document.getElementById('vePadding')?.value;
    const margin = document.getElementById('veMargin')?.value;
    const border = document.getElementById('veBorder')?.value;
    
    if (fontSize) el.style.fontSize = fontSize;
    if (width) el.style.width = width;
    if (height) el.style.height = height;
    if (padding) el.style.padding = padding;
    if (margin) el.style.margin = margin;
    if (border) el.style.border = border;
    
    const customCss = document.getElementById('veCustomCss')?.value.trim();
    if (customCss) {{
      customCss.split(';').forEach(rule => {{
        const [prop, val] = rule.split(':').map(s => s.trim());
        if (prop && val) el.style[prop] = val;
      }});
    }}
    
    alert('Changes applied! Click "Save" to persist.');
  }}
  
  async function saveChanges(el) {{
    const selector = getUniqueSelector(el);
    const styles = el.style.cssText;
    const isText = el.childNodes.length === 1 && el.childNodes[0].nodeType === 3;
    const textOverride = isText ? document.getElementById('veTextInput').value : null;
    const scope = document.getElementById('veScopeSelect').value;
    
    const scopeLabels = {{
      page: 'this page',
      domain: 'entire domain',
      template: 'all domains using this template'
    }};
    
    if (!confirm('Save changes to ' + scopeLabels[scope] + '?')) return;
    
    try {{
      const res = await fetch('/api/domains/' + domainId + '/visual-customizations', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ selector, styles, textOverride, scope, pageUrl: window.location.pathname }})
      }});
      const data = await res.json();
      if (data.success) {{
        alert('Saved to ' + scopeLabels[scope] + '! ' + (data.affected_domains || 1) + ' domain(s) updated. Reload to see changes.');
      }} else {{
        alert('Save failed: ' + (data.error || 'Unknown error'));
      }}
    }} catch (e) {{
      alert('Save failed: ' + e.message);
    }}
  }}
  
  function openInsertModal(afterEl) {{
    content.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:1rem;">
        <div>
          <label style="display:block;font-weight:600;margin-bottom:0.5rem;">Insert Position</label>
          <p style="font-size:0.85rem;color:#666;">Content will be inserted after the selected element.</p>
        </div>
        
        <div>
          <label style="display:block;font-weight:600;margin-bottom:0.5rem;">HTML/Script Content</label>
          <textarea id="veInsertHtml" placeholder="<div>Your HTML here</div>" style="width:100%;padding:0.5rem;border:1px solid #ddd;border-radius:6px;min-height:120px;font-family:monospace;font-size:0.85rem;"></textarea>
        </div>
        
        <div style="display:flex;gap:0.5rem;">
          <button id="veInsertApplyBtn" style="flex:1;padding:0.75rem;background:#6C8AE4;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;">Insert Now</button>
          <button id="veInsertSaveBtn" style="flex:1;padding:0.75rem;background:#22c55e;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;">Save to Domain</button>
        </div>
      </div>
    `;
    
    overlay.style.display = 'block';
    panel.style.display = 'block';
    
    document.getElementById('veInsertApplyBtn').addEventListener('click', () => {{
      const html = document.getElementById('veInsertHtml').value;
      afterEl.insertAdjacentHTML('afterend', html);
      alert('Content inserted! Click "Save to Domain" to persist.');
    }});
    
    document.getElementById('veInsertSaveBtn').addEventListener('click', async () => {{
      const html = document.getElementById('veInsertHtml').value;
      const selector = getUniqueSelector(afterEl);
      const scope = document.getElementById('veScopeSelect')?.value || 'domain';
      
      const scopeLabels = {{
        page: 'this page',
        domain: 'entire domain',
        template: 'all domains using this template'
      }};
      
      if (!confirm('Save insertion to ' + scopeLabels[scope] + '?')) return;
      
      try {{
        const res = await fetch('/api/domains/' + domainId + '/visual-customizations', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ selector, insertAfter: html, scope, pageUrl: window.location.pathname }})
        }});
        const data = await res.json();
        if (data.success) {{
          alert('Saved to ' + scopeLabels[scope] + '! ' + (data.affected_domains || 1) + ' domain(s) updated. Reload to see changes.');
        }} else {{
          alert('Save failed: ' + (data.error || 'Unknown error'));
        }}
      }} catch (e) {{
        alert('Save failed: ' + e.message);
      }}
    }});
  }}
  
  function getUniqueSelector(el) {{
    if (el.id) return '#' + el.id;
    let path = [];
    while (el && el.nodeType === Node.ELEMENT_NODE) {{
      let selector = el.nodeName.toLowerCase();
      if (el.className) {{
        const classes = el.className.split(' ').filter(c => c && !c.startsWith('ve-'));
        if (classes.length) selector += '.' + classes.join('.');
      }}
      path.unshift(selector);
      el = el.parentNode;
      if (path.length > 5) break;
    }}
    return path.join(' > ');
  }}
  
  function rgbToHex(rgb) {{
    if (!rgb || rgb === 'rgba(0, 0, 0, 0)' || rgb === 'transparent') return '#ffffff';
    const match = rgb.match(/\\d+/g);
    if (!match || match.length < 3) return '#000000';
    const r = parseInt(match[0]).toString(16).padStart(2, '0');
    const g = parseInt(match[1]).toString(16).padStart(2, '0');
    const b = parseInt(match[2]).toString(16).padStart(2, '0');
    return '#' + r + g + b;
  }}
  
  function extractAllColors(el) {{
    const computed = window.getComputedStyle(el);
    const colors = [];
    
    // Text color
    if (computed.color && computed.color !== 'rgba(0, 0, 0, 0)') {{
      colors.push({{ property: 'color', label: 'Text Color', value: computed.color, hex: rgbToHex(computed.color) }});
    }}
    
    // Background - check for gradients or solid
    const bg = computed.backgroundImage;
    if (bg && bg !== 'none') {{
      // Extract colors from gradient
      const gradientColors = bg.match(/rgba?\\([^)]+\\)/g) || [];
      gradientColors.forEach((c, i) => {{
        colors.push({{ property: 'background-gradient-' + i, label: 'Gradient Color ' + (i+1), value: c, hex: rgbToHex(c), isGradient: true }});
      }});
    }} else if (computed.backgroundColor && computed.backgroundColor !== 'rgba(0, 0, 0, 0)') {{
      colors.push({{ property: 'backgroundColor', label: 'Background', value: computed.backgroundColor, hex: rgbToHex(computed.backgroundColor) }});
    }}
    
    // Border color
    if (computed.borderColor && computed.borderColor !== 'rgba(0, 0, 0, 0)') {{
      colors.push({{ property: 'borderColor', label: 'Border', value: computed.borderColor, hex: rgbToHex(computed.borderColor) }});
    }}
    
    // Box shadow colors
    const shadow = computed.boxShadow;
    if (shadow && shadow !== 'none') {{
      const shadowColors = shadow.match(/rgba?\\([^)]+\\)/g) || [];
      shadowColors.forEach((c, i) => {{
        colors.push({{ property: 'shadow-' + i, label: 'Shadow Color ' + (i+1), value: c, hex: rgbToHex(c), isShadow: true }});
      }});
    }}
    
    // Outline color
    if (computed.outlineColor && computed.outlineColor !== 'rgba(0, 0, 0, 0)') {{
      colors.push({{ property: 'outlineColor', label: 'Outline', value: computed.outlineColor, hex: rgbToHex(computed.outlineColor) }});
    }}
    
    return colors;
  }}
  
  window.resetColor = function(inputId, originalColor) {{
    const input = document.getElementById(inputId);
    if (input) {{
      input.value = rgbToHex(originalColor);
    }}
  }}
}})();
</script>
"""


def _fetch_themed_part_internal(theme, slug, config):
    """Call the themed endpoint: POST /generate/domain_page/{theme}/{slug}."""
    base = (WEBSITE_PARTS_API_URL or "").rstrip("/")
    if not base or not theme:
        return None
    try:
        url = f"{base}/generate/domain_page/{theme}/{slug}"
        req = urllib.request.Request(url, data=json.dumps(config).encode("utf-8"), method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            out = json.loads(resp.read().decode())
        return {"html": out.get("html", ""), "css": out.get("css", "")}
    except Exception as e:
        log.warning("[fetch-themed-part] theme=%s slug=%s error=%s", theme, slug, e)
        return None


def _fetch_site_part_internal(part, name, config):
    """Call website-parts-generator and return {html, css} or None on error."""
    base = (WEBSITE_PARTS_API_URL or "").rstrip("/")
    if not base:
        return None
    try:
        url = f"{base}/generate/{part}/{name}"
        req = urllib.request.Request(url, data=json.dumps(config).encode("utf-8"), method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            out = json.loads(resp.read().decode())
        return {"html": out.get("html", ""), "css": out.get("css", "")}
    except urllib.error.HTTPError as e:
        err_msg = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
            try:
                j = json.loads(body)
                detail = j.get("detail", body)
                if isinstance(detail, list):
                    detail = " | ".join(str(x) for x in detail[:3])
                err_msg = str(detail)
                tb = j.get("traceback", [])
                if tb:
                    err_msg += " | TRACEBACK: " + " <- ".join(str(x).strip() for x in tb[-5:] if x.strip())
            except json.JSONDecodeError:
                err_msg = body[:800] if body else str(e)
        except Exception as ex:
            err_msg = str(ex)
        log.warning("[preview-website] fetch %s/%s failed (HTTP %s): %s", part, name, e.code, err_msg)
        return None
    except Exception as e:
        log.warning("[preview-website] fetch %s/%s failed: %s", part, name, e)
        return None


def _get_domain_website_context(domain_id):
    """Return domain data, style config, base_url for preview-website routes."""
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT d.id, d.domain_url, d.domain_name, d.header_template, d.footer_template,
            d.category_page_template, d.side_article_template, d.writer_template, d.index_template, d.article_template_config, d.categories_list, d.domain_colors, d.domain_fonts, d.article_card_template,
            d.domain_page_about_us, d.domain_page_terms_of_use, d.domain_page_privacy_policy, d.domain_page_gdpr_policy,
            d.domain_page_cookie_policy, d.domain_page_copyright_policy, d.domain_page_disclaimer, d.domain_page_contact_us
            FROM domains d WHERE d.id = ?""", (domain_id,))
        row = dict_row(cur.fetchone())
        if not row:
            return None
        if not (row.get("header_template") and row.get("footer_template")):
            _assign_random_site_templates(conn, domain_id)
            cur = db_execute(conn, "SELECT * FROM domains WHERE id = ?", (domain_id,))
            row = dict_row(cur.fetchone())
    cfg_raw = (row.get("article_template_config") or "").strip()
    config = {}
    if cfg_raw:
        try:
            config = json.loads(cfg_raw) if isinstance(cfg_raw, str) else cfg_raw
            if not isinstance(config, dict):
                config = {}
        except json.JSONDecodeError:
            pass
    # Merge domain_colors: each domain has primary, secondary, etc. Used by header, footer, sidebar, category, articles
    dc_raw = (row.get("domain_colors") or "").strip()
    if dc_raw:
        try:
            dc = json.loads(dc_raw) if isinstance(dc_raw, str) else dc_raw
            if isinstance(dc, dict):
                if "colors" not in config:
                    config["colors"] = dict(DEFAULT_DOMAIN_COLORS)
                for k, v in dc.items():
                    if v:
                        config["colors"][k] = v
        except json.JSONDecodeError:
            pass
    if "colors" not in config or not config["colors"]:
        config["colors"] = dict(DEFAULT_DOMAIN_COLORS)
    # Merge domain_fonts for header, footer, sidebar, category, articles
    df_raw = (row.get("domain_fonts") or "").strip()
    if df_raw:
        try:
            config["fonts"] = _domain_fonts_to_config(df_raw)
        except Exception:
            pass
    base_url = f"/preview-website/{domain_id}"
    config["domain_url"] = base_url
    config["domain_name"] = _domain_url_to_display_name(row.get("domain_url") or row.get("domain_name"))
    config["article_card_template"] = (row.get("article_card_template") or "article_card_1").strip() or "article_card_1"
    # Domain pages for footer links (about-us, terms-of-use, privacy-policy, etc.)
    config["domain_pages"] = [
        {"name": "About Us", "url": f"{base_url}/about-us", "slug": "about-us"},
        {"name": "Terms of Use", "url": f"{base_url}/terms-of-use", "slug": "terms-of-use"},
        {"name": "Privacy Policy", "url": f"{base_url}/privacy-policy", "slug": "privacy-policy"},
        {"name": "GDPR Policy", "url": f"{base_url}/gdpr-policy", "slug": "gdpr-policy"},
        {"name": "Cookie Policy", "url": f"{base_url}/cookie-policy", "slug": "cookie-policy"},
        {"name": "Copyright Policy", "url": f"{base_url}/copyright-policy", "slug": "copyright-policy"},
        {"name": "Disclaimer", "url": f"{base_url}/disclaimer", "slug": "disclaimer"},
        {"name": "Contact Us", "url": f"{base_url}/contact-us", "slug": "contact-us"},
    ]
    return {"domain": row, "config": config, "base_url": base_url}


def _get_domain_articles(conn, domain_id, offset=0, limit=12, category_slug=None):
    """Return list of {title, url, image, excerpt, title_id} for domain articles."""
    cat = (category_slug or "").strip().lower()
    if cat:
        cur = db_execute(conn, """SELECT t.id, t.title FROM titles t
            JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ? ORDER BY t.id DESC""", (domain_id,))
        rows = cur.fetchall()
        title_ids = [r["id"] for r in rows if r and r.get("id")]
        title_ids = _filter_title_ids_by_category(conn, title_ids, cat)
        total = len(title_ids)
        if not title_ids:
            return [], 0
        page_ids = title_ids[offset:offset + limit]
        placeholders = ",".join(["?"] * len(page_ids))
        cur = db_execute(conn, f"""SELECT t.id, t.title, ac.meta_description, ac.main_image, ac.ingredient_image
            FROM titles t JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.id IN ({placeholders}) ORDER BY t.id DESC""", tuple(page_ids))
        rows = cur.fetchall()
    else:
        cur = db_execute(conn, """SELECT t.id, t.title, ac.meta_description, ac.main_image
            FROM titles t JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ? ORDER BY t.id DESC""", (domain_id,))
        rows = cur.fetchall()
        total = len(rows)
        cur = db_execute(conn, """SELECT t.id, t.title, ac.meta_description, ac.main_image, ac.ingredient_image
            FROM titles t JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ? ORDER BY t.id DESC LIMIT ? OFFSET ?""", (domain_id, limit, offset))
        rows = cur.fetchall()
    articles = []
    for r in (rows or []):
        ro = dict_row(r)
        tid = ro.get("id")
        title = (ro.get("title") or "")[:200]
        excerpt = (ro.get("meta_description") or "")[:150]
        img = (ro.get("main_image") or ro.get("ingredient_image") or "").strip()
        articles.append({
            "title": title, "url": f"/preview-website/{domain_id}/article/{tid}",
            "image": img, "main_image": img, "excerpt": excerpt, "title_id": tid
        })
    if not cat:
        cur = db_execute(conn, """SELECT COUNT(*) AS c FROM titles t
            JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ?""", (domain_id,))
        total = (dict_row(cur.fetchone()) or {}).get("c", 0)
    return articles, total


def _get_categories_with_counts(conn, domain_id):
    """Return list of {slug, name, count} for domain. Uses categories_list or extracts from recipe.course."""
    cats_raw = None
    with get_connection() as c2:
        cur = db_execute(c2, "SELECT categories_list FROM domains WHERE id = ?", (domain_id,))
        r = dict_row(cur.fetchone())
        cats_raw = (r.get("categories_list") or "").strip()
    categories_list = []
    if cats_raw:
        try:
            categories_list = json.loads(cats_raw)
            if not isinstance(categories_list, list):
                categories_list = []
        except json.JSONDecodeError:
            pass
    if categories_list:
        result = []
        for c in categories_list:
            if isinstance(c, dict):
                name = (c.get("categorie") or c.get("name") or c.get("category") or "Other").strip()
            else:
                name = str(c).strip() or "Other"
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "other"
            cur = db_execute(conn, """SELECT t.id FROM titles t JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
                WHERE t.domain_id = ?""", (domain_id,))
            all_ids = [r["id"] for r in cur.fetchall() if r and r.get("id")]
            filtered = _filter_title_ids_by_category(conn, all_ids, slug) if slug != "other" else all_ids
            if slug == "other" and name.lower() != "other":
                filtered = _filter_title_ids_by_category(conn, all_ids, name)
            result.append({"slug": slug, "name": name, "count": len(filtered)})
        return result
    cur = db_execute(conn, """SELECT ac.recipe FROM titles t
        JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
        WHERE t.domain_id = ?""", (domain_id,))
    courses = set()
    for r in cur.fetchall():
        ro = dict_row(r)
        rec = ro.get("recipe") or ""
        if rec:
            try:
                rec = json.loads(rec) if isinstance(rec, str) else rec
                co = (rec.get("course") or "").strip()
                if co:
                    courses.add(co)
            except json.JSONDecodeError:
                pass
    result = []
    for co in sorted(courses):
        slug = re.sub(r"[^a-z0-9]+", "-", co.lower()).strip("-") or "other"
        cur = db_execute(conn, """SELECT t.id FROM titles t JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ?""", (domain_id,))
        all_ids = [r["id"] for r in cur.fetchall() if r and r.get("id")]
        filtered = _filter_title_ids_by_category(conn, all_ids, co)
        result.append({"slug": slug, "name": co, "count": len(filtered)})
    if not result:
        cur = db_execute(conn, """SELECT COUNT(*) AS c FROM titles t
            JOIN article_content ac ON ac.title_id = t.id AND ac.language_code = 'en'
            WHERE t.domain_id = ?""", (domain_id,))
        cnt = (dict_row(cur.fetchone()) or {}).get("c", 0)
        if cnt:
            result = [{"slug": "all", "name": "All Recipes", "count": cnt}]
    return result


def _build_pagination_html(base_url, page, total_pages, page_param="page"):
    """Build pagination nav HTML."""
    if total_pages <= 1:
        return ""
    parts = []
    sep = "&" if "?" in base_url else "?"
    for i in range(1, total_pages + 1):
        if i == page:
            parts.append(f'<span class="page-current">{i}</span>')
        else:
            u = f"{base_url}{sep}{page_param}={i}" if i > 1 else base_url.split("?")[0].rstrip("/")
            if page_param == "page" and "page/" in base_url:
                u = base_url.replace("/page/1", "").rstrip("/") if i == 1 else base_url.replace(f"/page/{page}", f"/page/{i}")
            parts.append(f'<a href="{html.escape(u)}" class="page-link">{i}</a>')
    prev_link = ""
    if page > 1:
        p = page - 1
        u = f"{base_url}{sep}{page_param}={p}" if p > 1 else base_url.split("?")[0].rstrip("/")
        if "page/" in base_url:
            u = base_url.replace(f"/page/{page}", f"/page/{p}")
        prev_link = f'<a href="{html.escape(u)}" class="page-prev">&laquo; Prev</a>'
    next_link = ""
    if page < total_pages:
        u = base_url.replace(f"/page/{page}", f"/page/{page + 1}") if "page/" in base_url else f"{base_url}{sep}{page_param}={page + 1}"
        next_link = f'<a href="{html.escape(u)}" class="page-next">Next &raquo;</a>'
    return f'<nav class="pagination-nav">{prev_link} <span class="page-numbers">{" ".join(parts)}</span> {next_link}</nav>'


def _get_sidebar_data(conn, domain_id, base_url):
    """Return {articles, categories} for sidebar."""
    articles, _ = _get_domain_articles(conn, domain_id, 0, 6, None)
    categories = _get_categories_with_counts(conn, domain_id)
    arts = [{"title": a["title"], "url": a["url"], "image": a.get("image", ""), "main_image": a.get("image", "")} for a in articles]
    cats = [{"name": c["name"], "url": f"{base_url}/category/{c['slug']}", "count": c["count"]} for c in categories]
    return {"articles": arts, "categories": cats}


def _render_preview_page(domain_id, main_html, main_css, page_title, ctx, include_sidebar=False, writer=None, override_theme=None):
    """Compose full page: header + (main + sidebar) + footer."""
    d = ctx["domain"]
    cfg = ctx["config"]
    base_url = ctx["base_url"]
    h_tpl = (d.get("header_template") or "header_1").strip() or "header_1"
    f_tpl = (d.get("footer_template") or "footer_1").strip() or "footer_1"
    s_tpl = (d.get("side_article_template") or "sidebar_1").strip() or "sidebar_1"
    w_tpl = (d.get("writer_template") or "").strip()
    page_theme = override_theme if override_theme else _get_domain_page_theme(d)
    h_cfg = dict(cfg)
    with get_connection() as conn:
        categories = _get_categories_with_counts(conn, domain_id)
        h_cfg["categories"] = [{"name": c["name"], "url": f"{base_url}/category/{c['slug']}", "slug": c["slug"], "count": c["count"]} for c in categories]
    header_data = None
    if page_theme:
        header_data = _fetch_themed_part_internal(page_theme, "header", h_cfg)
        if header_data:
            log.info("[render-preview-page] using themed header from %s", page_theme)
    if not header_data:
        header_data = _fetch_site_part_internal("header", h_tpl, h_cfg)
    f_cfg = dict(cfg)
    f_cfg["categories"] = h_cfg["categories"]
    footer_data = None
    if page_theme:
        footer_data = _fetch_themed_part_internal(page_theme, "footer", f_cfg)
        if footer_data:
            log.info("[render-preview-page] using themed footer from %s", page_theme)
    if not footer_data:
        footer_data = _fetch_site_part_internal("footer", f_tpl, f_cfg)
    header_html = (header_data or {}).get("html", f'<header><a href="{base_url}">{html.escape(cfg.get("domain_name","Home"))}</a></header>')
    header_css = (header_data or {}).get("css", "")
    footer_html = (footer_data or {}).get("html", f'<footer>&copy; {html.escape(cfg.get("domain_name",""))}</footer>')
    footer_css = (footer_data or {}).get("css", "")
    sidebar_html = ""
    sidebar_css = ""
    writer_css = ""
    if include_sidebar:
        with get_connection() as conn:
            sd = _get_sidebar_data(conn, domain_id, base_url)
        scfg = dict(cfg)
        scfg["articles"] = sd["articles"]
        scfg["categories"] = sd["categories"]
        if writer:
            scfg["writer"] = writer
        s_data = None
        if page_theme:
            s_data = _fetch_themed_part_internal(page_theme, "sidebar", scfg)
            if s_data:
                log.info("[render-preview-page] using themed sidebar from %s", page_theme)
        if not s_data:
            s_data = _fetch_site_part_internal("sidebar", s_tpl, scfg)
        if s_data:
            sidebar_html = s_data.get("html", "")
            sidebar_css = s_data.get("css", "")
            log.info(f"[render-preview-page] Sidebar generated: template={s_tpl}, html_len={len(sidebar_html)}, articles_count={len(scfg.get('articles', []))}")
        
        if not page_theme and w_tpl and writer:
            w_cfg = {"writer": writer, "colors": cfg.get("colors", {})}
            w_data = _fetch_site_part_internal("writer", w_tpl, w_cfg)
            if w_data:
                writer_html = w_data.get("html", "")
                writer_css = w_data.get("css", "")
                if writer_html:
                    sidebar_html = writer_html + "\n" + sidebar_html
                    log.info(f"[render-preview-page] Writer HTML injected into sidebar")
        
        # Debug: log sidebar structure
        sidebar_count = sidebar_html.count('<aside') + sidebar_html.count('sidebar-section')
        log.info(f"[render-preview-page] Sidebar structure check: {sidebar_count} sections found in sidebar_html")
        sidebar_section_count = sidebar_html.count('<div class="sidebar-section">')
        aside_count = sidebar_html.count('<aside')
        log.info(f"[render-preview-page] Sidebar stats: {sidebar_section_count} sections, {aside_count} aside tags")
        
        content_body = f'<div class="page-content-with-sidebar"><div class="main-area">{main_html}</div><div class="sidebar-area">{sidebar_html}</div></div>'
        layout_css = """
.page-content-with-sidebar { display: flex; gap: 2.5rem; max-width: 1280px; margin: 0 auto; padding: 2rem 1.5rem; align-items: flex-start; flex-direction: row; }
.main-area { flex: 1; min-width: 0; max-width: 780px; order: 1; }
.sidebar-area { flex-shrink: 0; width: 300px; max-width: 300px; order: 2; }
@media (max-width: 1024px) { .page-content-with-sidebar { gap: 2rem; } .sidebar-area { width: 280px; max-width: 280px; } }
@media (max-width: 900px) { .page-content-with-sidebar { flex-direction: column; gap: 3rem; } .sidebar-area { width: 100%; max-width: 780px; margin: 0 auto; order: 2; } .main-area { max-width: 100%; order: 1; } }
"""
    else:
        content_body = main_html
        layout_css = ""
    full_css = header_css + "\n" + footer_css + "\n" + (main_css or "") + "\n" + sidebar_css + "\n" + writer_css + "\n" + layout_css
    # Strip HTML tags that would close <style> early and leak pagination_css as visible text
    full_css = re.sub(r"</style>", "", full_css, flags=re.IGNORECASE)
    full_css = re.sub(r"</head>", "", full_css, flags=re.IGNORECASE)
    full_css = re.sub(r"</html>", "", full_css, flags=re.IGNORECASE)
    pagination_css = """
.pagination-nav { display: flex; align-items: center; justify-content: center; gap: 1rem; flex-wrap: wrap; margin: 2rem 0; }
.pagination-nav a, .pagination-nav .page-current { padding: 0.5rem 1rem; }
.pagination-nav a { color: var(--primary, #6C8AE4); text-decoration: none; }
.pagination-nav a:hover { text-decoration: underline; }
.pagination-nav .page-current { font-weight: bold; color: var(--text-primary); }
"""
    nav_script = """<script>document.querySelector('.nav-toggle')?.addEventListener('click',function(){document.querySelector('.main-nav')?.classList.toggle('is-open');});</script>"""
    
    # Always inject visual editor on preview pages
    editor_html = _get_visual_editor_html(domain_id)
    
    # Apply saved visual customizations
    customizations_script = _get_customizations_script(domain_id)
    
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(page_title)}</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600" rel="stylesheet">
<style>{full_css}
{pagination_css}</style></head>
<body>{header_html}
{content_body}
{footer_html}{nav_script}{customizations_script}{editor_html}</body></html>"""


@app.route("/preview-website/<int:domain_id>")
@app.route("/preview-website/<int:domain_id>/page/<int:page>")
def preview_website_index(domain_id, page=1):
    """Full website preview: index page with hero, article grid, pagination."""
    ctx = _get_domain_website_context(domain_id)
    if not ctx:
        return "Domain not found", 404
    base_url = ctx["base_url"]
    cfg = ctx["config"]
    per_page = 12
    offset = (page - 1) * per_page
    with get_connection() as conn:
        articles, total = _get_domain_articles(conn, domain_id, offset, per_page, None)
        categories = _get_categories_with_counts(conn, domain_id)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    name = cfg.get("domain_name", "Recipe Blog")

    # If "theme" is passed in querystring, override the page_theme temporarily for preview
    req_theme = request.args.get("theme")
    page_theme = req_theme if req_theme else _get_domain_page_theme(ctx["domain"])
    
    idx_tpl = (ctx["domain"].get("index_template") or "").strip()
    idx_cfg = dict(cfg)
    idx_cfg["base_url"] = base_url
    idx_cfg["articles"] = [{"title": a["title"], "url": a["url"], "image": a.get("main_image") or a.get("image", ""), "main_image": a.get("main_image") or a.get("image", ""), "excerpt": a.get("excerpt", "")} for a in articles]
    idx_cfg["categories"] = [{"name": c["name"], "url": f"{base_url}/category/{c['slug']}", "slug": c["slug"], "count": c["count"]} for c in categories]
    idx_cfg["total"] = total
    idx_cfg["total_pages"] = total_pages
    idx_cfg["current_page"] = page
    idx_cfg["per_page"] = per_page

    idx_data = None
    if page_theme:
        idx_data = _fetch_themed_part_internal(page_theme, "index", idx_cfg)
        if idx_data:
            log.info("[preview-index] using themed index from %s", page_theme)
    if not idx_data and idx_tpl:
        idx_data = _fetch_site_part_internal("index", idx_tpl, idx_cfg)
    if idx_data and idx_data.get("html"):
        main_html = idx_data["html"]
        main_css = idx_data.get("css", "")
        pagination_html = ""
        for i in range(1, total_pages + 1):
            u = f"{base_url}" if i == 1 else f"{base_url}/page/{i}"
            if i == page:
                pagination_html += f'<span class="page-current">{i}</span> '
            else:
                pagination_html += f'<a href="{u}" class="page-link">{i}</a> '
        prev_next = ""
        if page > 1:
            prev_next = f'<a href="{base_url}/page/{page-1}" class="page-prev">&laquo; Prev</a> '
        if page < total_pages:
            prev_next += f'<a href="{base_url}/page/{page+1}" class="page-next">Next &raquo;</a>'
        pagination_html = f'<nav class="pagination-nav">{prev_next}<span class="page-numbers">{pagination_html}</span></nav>'
        if '<div class="index-pagination-slot"></div>' in main_html:
            main_html = main_html.replace('<div class="index-pagination-slot"></div>', pagination_html if total_pages > 1 else "")
        else:
            main_html = main_html.replace("</main>", pagination_html + "\n</main>")
        return _render_preview_page(domain_id, main_html, main_css, f"{name} | Home", ctx, override_theme=req_theme)

    cards_html = ""
    for a in articles:
        ti = html.escape(a["title"])
        url = html.escape(a["url"])
        img = (a.get("main_image") or a.get("image") or "").strip()
        excerpt = html.escape((a.get("excerpt") or "")[:120])
        img_tag = f'<img src="{img}" alt="">' if img and img.startswith("http") else '<div class="idx-card-placeholder"></div>'
        cards_html += f'<article class="idx-card"><a href="{url}" class="idx-card-img">{img_tag}</a><div class="idx-card-body"><h3><a href="{url}">{ti}</a></h3><p>{excerpt}</p></div></article>'
    pagination_html = ""
    for i in range(1, total_pages + 1):
        u = f"{base_url}" if i == 1 else f"{base_url}/page/{i}"
        if i == page:
            pagination_html += f'<span class="page-current">{i}</span> '
        else:
            pagination_html += f'<a href="{u}" class="page-link">{i}</a> '
    prev_next = ""
    if page > 1:
        prev_next = f'<a href="{base_url}/page/{page-1}" class="page-prev">&laquo; Prev</a> '
    if page < total_pages:
        prev_next += f'<a href="{base_url}/page/{page+1}" class="page-next">Next &raquo;</a>'
    pagination_html = f'<nav class="pagination-nav">{prev_next}<span class="page-numbers">{pagination_html}</span></nav>'
    cat_links = "".join(f'<a href="{base_url}/category/{html.escape(c["slug"])}">{html.escape(c["name"])} ({c["count"]})</a>' for c in categories[:10])
    primary = cfg.get("colors") or {}
    primary = primary.get("primary", "#6C8AE4") if isinstance(primary, dict) else "#6C8AE4"
    main_html = f"""<main class="preview-index">
  <section class="hero">
    <h1>{html.escape(name)}</h1>
    <p class="hero-tagline">Delicious recipes for every occasion</p>
    <a href="{base_url}/categories" class="hero-cta">Browse Categories</a>
  </section>
  <section class="index-grid-wrap">
    <h2>Recent Recipes</h2>
    <div class="index-grid">{cards_html or '<p class="no-articles">No recipes yet. Add titles and generate articles.</p>'}</div>
    {f'<nav class="pagination-nav">{pagination_html}</nav>' if total_pages > 1 else ''}
  </section>
  <aside class="index-categories">
    <h3>Categories</h3>
    <div class="cat-links">{cat_links or '<p>No categories</p>'}</div>
  </aside>
</main>"""
    main_css = f"""
:root {{ --primary: {primary}; --text-primary: #2D2D2D; --text-secondary: #5A5A5A; --border: #E2E8FF; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
.preview-index {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
.hero {{ text-align: center; padding: 3rem 0; background: linear-gradient(135deg, rgba(108,138,228,.08) 0%, rgba(156,106,222,.08) 100%); border-radius: 12px; margin-bottom: 2rem; }}
.hero h1 {{ font-family: Playfair Display, serif; font-size: 2.5rem; color: var(--primary); margin-bottom: 0.5rem; }}
.hero-tagline {{ color: var(--text-secondary); margin-bottom: 1.5rem; }}
.hero-cta {{ display: inline-block; padding: 0.75rem 1.5rem; background: var(--primary); color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600; }}
.hero-cta:hover {{ opacity: 0.9; }}
.index-grid-wrap {{ margin-bottom: 2rem; }}
.index-grid-wrap h2 {{ font-size: 1.5rem; margin-bottom: 1.5rem; color: var(--text-primary); }}
.index-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1.5rem; }}
.idx-card {{ background: #fff; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
.idx-card .idx-card-img {{ display: block; aspect-ratio: 16/10; background: #eee; }}
.idx-card .idx-card-img img {{ width: 100%; height: 100%; object-fit: cover; }}
.idx-card-placeholder {{ width: 100%; height: 100%; background: linear-gradient(135deg, #eee 0%, #ddd 100%); }}
.idx-card-body {{ padding: 1.25rem; }}
.idx-card h3 {{ font-size: 1.1rem; margin-bottom: 0.5rem; }}
.idx-card h3 a {{ color: var(--text-primary); text-decoration: none; }}
.idx-card h3 a:hover {{ color: var(--primary); }}
.idx-card p {{ font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5; }}
.index-categories {{ margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border); }}
.index-categories h3 {{ font-size: 1.1rem; margin-bottom: 1rem; color: var(--primary); }}
.cat-links {{ display: flex; flex-wrap: wrap; gap: 0.75rem; }}
.cat-links a {{ color: var(--primary); text-decoration: none; font-weight: 500; }}
.cat-links a:hover {{ text-decoration: underline; }}
"""
    return _render_preview_page(domain_id, main_html, main_css, f"{name} | Home", ctx, override_theme=req_theme)

@app.route("/preview-website/<int:domain_id>/recipes")
@app.route("/preview-website/<int:domain_id>/recipes/page/<int:page>")
def preview_website_recipes(domain_id, page=1):
    """Redirect /recipes to index."""
    return redirect(url_for("preview_website_index", domain_id=domain_id, page=page), code=302)


@app.route("/preview-website/<int:domain_id>/about")
def preview_website_about(domain_id):
    """Redirect /about to /about-us."""
    return redirect(url_for("preview_website_domain_page", domain_id=domain_id, slug="about-us"), code=302)


@app.route("/preview-website/<int:domain_id>/about-us")
@app.route("/preview-website/<int:domain_id>/terms-of-use")
@app.route("/preview-website/<int:domain_id>/privacy-policy")
@app.route("/preview-website/<int:domain_id>/gdpr-policy")
@app.route("/preview-website/<int:domain_id>/cookie-policy")
@app.route("/preview-website/<int:domain_id>/copyright-policy")
@app.route("/preview-website/<int:domain_id>/disclaimer")
@app.route("/preview-website/<int:domain_id>/contact-us")
@app.route("/preview-website/<int:domain_id>/page/<slug>")
def preview_website_domain_page(domain_id, slug=None):
    """Serve generated domain pages: about-us, terms-of-use, privacy-policy, gdpr-policy, cookie-policy, copyright-policy, disclaimer, contact-us."""
    if slug is None:
        slug = request.path.rstrip("/").rsplit("/", 1)[-1]  # e.g. /preview-website/1/about-us -> about-us
    if slug not in DOMAIN_PAGE_SLUGS:
        return "Page not found", 404
    ctx = _get_domain_website_context(domain_id)
    if not ctx:
        return "Domain not found", 404
    name = ctx["config"].get("domain_name", "Recipe Blog")
    base_url = ctx["base_url"]
    col = PAGE_SLUG_TO_COLUMN.get(slug)
    if not col:
        return "Page not found", 404
    with get_connection() as conn:
        cur = db_execute(conn, f"SELECT {col} FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    raw = (row.get(col) or "").strip()
    page_data = None
    if raw:
        try:
            page_data = json.loads(raw)
            if not isinstance(page_data, dict):
                page_data = None
        except json.JSONDecodeError:
            page_data = None
    if page_data and page_data.get("main_html"):
        main_html = page_data["main_html"]
        main_css = page_data.get("main_css") or ""
        page_title = slug.replace("-", " ").title()
        return _render_preview_page(domain_id, main_html, main_css, f"{name} | {page_title}", ctx, override_theme=request.args.get("theme"))
    # Fallback simple content when not yet generated
    if slug == "about-us":
        main_html = f"""<main class="preview-about"><h1>About {html.escape(name)}</h1><p>Welcome to {html.escape(name)}! We share delicious recipes for every occasion.</p><p><a href="{base_url}">Back to Home</a></p></main>"""
        main_css = ".preview-about { max-width: 600px; margin: 0 auto; padding: 2rem; }"
        return _render_preview_page(domain_id, main_html, main_css, f"{name} | About", ctx, override_theme=request.args.get("theme"))
    main_html = f"""<main class="preview-page"><h1>{slug.replace("-", " ").title()}</h1><p>This page has not been generated yet. Use the <strong>Pages</strong> button in the Theme column to generate it.</p><p><a href="{base_url}">Back to Home</a></p></main>"""
    main_css = ".preview-page { max-width: 600px; margin: 0 auto; padding: 2rem; }"
    return _render_preview_page(domain_id, main_html, main_css, f"{name} | {slug.replace('-', ' ').title()}", ctx, override_theme=request.args.get("theme"))


@app.route("/preview-website/<int:domain_id>/categories")
def preview_website_categories(domain_id):
    """Categories listing page."""
    ctx = _get_domain_website_context(domain_id)
    if not ctx:
        return "Domain not found", 404
    base_url = ctx["base_url"]
    cfg = ctx["config"]
    with get_connection() as conn:
        categories = _get_categories_with_counts(conn, domain_id)
    name = cfg.get("domain_name", "Recipe Blog")
    items = "".join(f'<a href="{base_url}/category/{html.escape(c["slug"])}" class="cat-item"><span class="cat-name">{html.escape(c["name"])}</span><span class="cat-count">{c["count"]}</span></a>' for c in categories)
    main_html = f"""<main class="preview-cats">
  <h1>Categories</h1>
  <div class="cat-list">{items or '<p>No categories</p>'}</div>
</main>"""
    main_css = """
:root { --primary: #6C8AE4; --text-primary: #2D2D2D; --text-secondary: #5A5A5A; }
* { margin: 0; padding: 0; box-sizing: border-box; }
.preview-cats { max-width: 800px; margin: 0 auto; padding: 2rem; }
.preview-cats h1 { font-size: 2rem; margin-bottom: 1.5rem; color: var(--primary); }
.cat-list { display: flex; flex-direction: column; gap: 0.75rem; }
.cat-item { display: flex; justify-content: space-between; padding: 1rem; background: #fff; border: 1px solid #eee; border-radius: 8px; text-decoration: none; color: var(--text-primary); }
.cat-item:hover { border-color: var(--primary); }
.cat-count { color: var(--text-secondary); font-size: 0.9rem; }
"""
    return _render_preview_page(domain_id, main_html, main_css, f"{name} | Categories", ctx, override_theme=request.args.get("theme"))

@app.route("/preview-website/<int:domain_id>/category")
def preview_website_category_index(domain_id):
    """Redirect /category to /category/all."""
    return redirect(url_for("preview_website_category", domain_id=domain_id, slug="all"), code=302)


@app.route("/preview-website/<int:domain_id>/category/<slug>")
@app.route("/preview-website/<int:domain_id>/category/<slug>/page/<int:page>")
def preview_website_category(domain_id, slug, page=1):
    """Category page with article grid and pagination."""
    ctx = _get_domain_website_context(domain_id)
    if not ctx:
        return "Domain not found", 404
    base_url = ctx["base_url"]
    cfg = ctx["config"]
    per_page = 12
    offset = (page - 1) * per_page
    with get_connection() as conn:
        cat_info = next((c for c in _get_categories_with_counts(conn, domain_id) if c["slug"] == slug), None)
        cat_name = (cat_info["name"] if cat_info else slug.replace("-", " ").title())
        filter_by = None if (cat_info and cat_info.get("slug") == "all") else (cat_name if cat_info else slug)
        articles, total = _get_domain_articles(conn, domain_id, offset, per_page, filter_by)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    req_theme = request.args.get("theme")
    page_theme = req_theme if req_theme else _get_domain_page_theme(ctx["domain"])
    cat_tpl = (ctx["domain"].get("category_page_template") or "category_1").strip() or "category_1"
    log.info("[preview-category] domain_id=%s slug=%s template=%s theme=%s", domain_id, slug, cat_tpl, page_theme or "none")
    cat_cfg = dict(cfg)
    cat_cfg["category_name"] = cat_name
    cat_cfg["articles"] = [{"title": a["title"], "url": a["url"], "image": a.get("main_image") or a.get("image", ""), "main_image": a.get("main_image") or a.get("image", ""), "excerpt": a.get("excerpt", "")} for a in articles]
    cat_cfg["total"] = total
    cat_cfg["total_pages"] = total_pages
    cat_cfg["current_page"] = page
    cat_cfg["per_page"] = per_page
    cat_data = None
    if page_theme:
        cat_data = _fetch_themed_part_internal(page_theme, "category", cat_cfg)
        if cat_data:
            log.info("[preview-category] using themed category from %s", page_theme)
    if not cat_data:
        cat_data = _fetch_site_part_internal("category", cat_tpl, cat_cfg)
    if cat_data:
        used_label = page_theme or cat_tpl
        main_html = f"<!-- category template: {used_label} -->\n" + (cat_data["html"] or "")
        main_css = cat_data["css"] or ""
        log.info("[preview-category] using template %s (html_len=%d)", used_label, len(main_html or ""))
    else:
        log.warning("[preview-category] fetch failed for %s, using fallback", cat_tpl)
        def _card(a):
            img = (a.get("main_image") or a.get("image") or "").strip()
            img_tag = f'<img src="{html.escape(img)}" alt="" style="width:100%;height:180px;object-fit:cover;">' if img and img.startswith("http") else '<div style="width:100%;height:180px;background:#eee;"></div>'
            return f'<article class="cat-card"><a href="{html.escape(a["url"])}">{img_tag}<h3>{html.escape(a["title"])}</h3></a></article>'
        cards_html = "".join(_card(a) for a in articles)
        main_html = f'<main class="preview-cat"><h1>{html.escape(cat_name)}</h1><p class="preview-cat-count">{total} recipes</p><div class="cat-grid">{cards_html}</div></main>'
        main_css = ".preview-cat { max-width: 1200px; margin: 0 auto; padding: 2rem; } .preview-cat .cat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1.5rem; } .preview-cat .cat-card { border: 1px solid #eee; border-radius: 12px; overflow: hidden; } .preview-cat .cat-card a { text-decoration: none; color: inherit; display: block; } .preview-cat .cat-card h3 { padding: 1rem; font-size: 1.1rem; } .preview-cat-count { color: #666; margin-bottom: 1.5rem; }"
    pagination_html = ""
    for i in range(1, total_pages + 1):
        u = f"{base_url}/category/{slug}" if i == 1 else f"{base_url}/category/{slug}/page/{i}"
        if i == page:
            pagination_html += f'<span class="page-current">{i}</span> '
        else:
            pagination_html += f'<a href="{u}" class="page-link">{i}</a> '
    prev_next = ('<a href="' + base_url + '/category/' + slug + '/page/' + str(page-1) + '" class="page-prev">&laquo; Prev</a> ') if page > 1 else ""
    if page < total_pages:
        prev_next += f'<a href="{base_url}/category/{slug}/page/{page+1}" class="page-next">Next &raquo;</a>'
    pagination_html = f'<nav class="pagination-nav">{prev_next}<span class="page-numbers">{pagination_html}</span></nav>'
    main_html = main_html.replace("</main>", pagination_html + "\n</main>")
    return _render_preview_page(domain_id, main_html, main_css, f"{ctx['config'].get('domain_name','')} | {cat_name}", ctx, include_sidebar=False, override_theme=request.args.get("theme"))

@app.route("/preview-website/<int:domain_id>/article/<int:title_id>")
def preview_website_article(domain_id, title_id):
    """Single article page with header, sidebar, footer."""
    ctx = _get_domain_website_context(domain_id)
    if not ctx:
        return "Domain not found", 404
    base_url = ctx["base_url"]
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT t.id, t.title, t.domain_id FROM titles t WHERE t.id = ? AND t.domain_id = ?""", (title_id, domain_id))
        row = dict_row(cur.fetchone())
    if not row:
        return "Article not found", 404
    with get_connection() as conn:
        cur = db_execute(conn, """SELECT article_html, article_css, pin_image, writer, writer_avatar FROM article_content WHERE title_id = ? AND language_code = 'en'""", (title_id,))
        ac = dict_row(cur.fetchone())
    article_html = (ac.get("article_html") or "").strip()
    article_css = (ac.get("article_css") or "").strip()
    pin_image_url = (ac.get("pin_image") or "").strip()
    writer_json = ac.get("writer") or None
    writer_avatar = ac.get("writer_avatar") or None
    
    # Check if article_html has embedded sidebar (shouldn't have)
    has_sidebar_in_article = bool(re.search(r'sidebar-area|<aside|side-article', article_html, re.IGNORECASE))
    if has_sidebar_in_article:
        log.warning(f"[preview-website-article] Article {title_id} has embedded sidebar HTML in article_html - this should not happen!")
    
    # Parse writer JSON if available
    writer_data = None
    if writer_json:
        try:
            writer_data = json.loads(writer_json) if isinstance(writer_json, str) else writer_json
            # Update avatar URL if we have one saved
            if writer_avatar:
                writer_data["avatar"] = writer_avatar
        except:
            pass
    
    title_text = (row.get("title") or "").strip()
    pin_attr = f' data-pin-image="{pin_image_url}"' if pin_image_url else ""
    main_html = f'<main class="preview-article"><article class="article-content"{pin_attr}>{article_html or "<p>No content yet.</p>"}</article></main>'
    main_css = f".preview-article {{ padding: 0; }} .article-content {{ line-height: 1.7; max-width: 100%; }}\n{article_css}"
    return _render_preview_page(domain_id, main_html, main_css, f"{title_text} | {ctx['config'].get('domain_name','')}", ctx, include_sidebar=True, writer=writer_data, override_theme=request.args.get("theme"))

def _build_static_page_html(domain_id, ctx_static, page_type, **kwargs):
    """Build full HTML for a static page. ctx_static has base_url='.' for relative paths."""
    cfg = ctx_static["config"]
    base = ctx_static["base_url"]
    d = ctx_static["domain"]
    h_tpl = (d.get("header_template") or "header_1").strip() or "header_1"
    f_tpl = (d.get("footer_template") or "footer_1").strip() or "footer_1"
    s_tpl = (d.get("side_article_template") or "sidebar_1").strip() or "sidebar_1"
    page_theme = _get_domain_page_theme(d)
    h_cfg = dict(cfg)
    h_cfg["categories"] = kwargs.get("sidebar_categories", [])
    header_data = None
    if page_theme:
        header_data = _fetch_themed_part_internal(page_theme, "header", h_cfg)
    if not header_data:
        header_data = _fetch_site_part_internal("header", h_tpl, h_cfg)
    f_cfg = dict(cfg)
    f_cfg["categories"] = kwargs.get("sidebar_categories", [])
    footer_data = None
    if page_theme:
        footer_data = _fetch_themed_part_internal(page_theme, "footer", f_cfg)
    if not footer_data:
        footer_data = _fetch_site_part_internal("footer", f_tpl, f_cfg)
    header_html = (header_data or {}).get("html", "")
    footer_html = (footer_data or {}).get("html", "")
    header_css = (header_data or {}).get("css", "")
    footer_css = (footer_data or {}).get("css", "")
    name = cfg.get("domain_name", "Recipe Blog")
    include_sidebar = kwargs.get("include_sidebar", False)
    main_html = kwargs.get("main_html", "")
    main_css = kwargs.get("main_css", "")
    page_title = kwargs.get("page_title", name)
    writer_css_injected = ""
    if include_sidebar:
        scfg = dict(cfg)
        scfg["articles"] = kwargs.get("sidebar_articles", [])
        scfg["categories"] = kwargs.get("sidebar_categories", [])
        if kwargs.get("writer"):
            scfg["writer"] = kwargs["writer"]
        s_data = None
        if page_theme:
            s_data = _fetch_themed_part_internal(page_theme, "sidebar", scfg)
        if not s_data:
            s_data = _fetch_site_part_internal("sidebar", s_tpl, scfg)
        sidebar_html = (s_data or {}).get("html", "")
        sidebar_css = (s_data or {}).get("css", "")
        
        writer_html_injected = ""
        writer_css_injected = ""
        if not page_theme:
            w_tpl = d.get("writer_template") or ""
            if w_tpl.strip() and kwargs.get("writer"):
                w_cfg = {"writer": kwargs["writer"], "colors": cfg.get("colors", {})}
                w_data = _fetch_site_part_internal("writer", w_tpl, w_cfg)
                if w_data:
                    writer_html_injected = w_data.get("html", "")
                    writer_css_injected = w_data.get("css", "")
                    if writer_html_injected:
                        sidebar_html = writer_html_injected + "\n" + sidebar_html
                        log.info(f"[build-static-page] Writer HTML injected into sidebar")
        
        content_body = f'<div class="page-content-with-sidebar"><div class="main-area">{main_html}</div><div class="sidebar-area">{sidebar_html}</div></div>'
        layout_css = ".page-content-with-sidebar{display:flex;gap:2.5rem;max-width:1280px;margin:0 auto;padding:2rem 1.5rem;align-items:flex-start;flex-direction:row;}.main-area{flex:1;min-width:0;max-width:780px;order:1;}.sidebar-area{flex-shrink:0;width:300px;max-width:300px;order:2;}@media(max-width:1024px){.page-content-with-sidebar{gap:2rem;}.sidebar-area{width:280px;max-width:280px;}}@media(max-width:900px){.page-content-with-sidebar{flex-direction:column;gap:3rem;}.sidebar-area{width:100%;max-width:780px;margin:0 auto;order:2;}.main-area{max-width:100%;order:1;}}"
    else:
        content_body = main_html
        sidebar_css = layout_css = ""
    full_css = header_css + "\n" + footer_css + "\n" + main_css + "\n" + sidebar_css + "\n" + writer_css_injected + "\n" + layout_css
    pagination_css = ".pagination-nav{display:flex;align-items:center;justify-content:center;gap:1rem;flex-wrap:wrap;margin:2rem 0;}.pagination-nav a,.pagination-nav .page-current{padding:.5rem 1rem;}.pagination-nav a{color:var(--primary,#6C8AE4);text-decoration:none;}.pagination-nav .page-current{font-weight:bold;}"
    nav_script = "<script>document.querySelector('.nav-toggle')?.addEventListener('click',function(){document.querySelector('.main-nav')?.classList.toggle('is-open');});</script>"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(page_title)}</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600" rel="stylesheet">
<style>{full_css}{pagination_css}</style></head>
<body>{header_html}
{content_body}
{footer_html}{nav_script}</body></html>"""


def _write_static_file(out_dir, rel_path, content):
    """Write content to out_dir/rel_path, creating parent dirs as needed."""
    full = os.path.join(out_dir, rel_path.replace("/", os.sep))
    parent = os.path.dirname(full)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


@app.route("/api/domains/<int:domain_id>/generate-static-project", methods=["GET", "POST"])
def api_generate_static_project(domain_id):
    """Generate a static website (HTML files) to a directory."""
    ctx = _get_domain_website_context(domain_id)
    if not ctx:
        return jsonify({"success": False, "error": "Domain not found"}), 404
    output_path = request.args.get("output_path") or (request.get_json(silent=True) or {}).get("output_path")
    if not output_path:
        output_path = os.path.join(STATIC_PROJECT_OUTPUT_DIR, str(domain_id))
    output_path = os.path.normpath(os.path.abspath(output_path))
    ctx_static = dict(ctx)
    ctx_static["base_url"] = "."
    ctx_static["config"] = dict(ctx["config"])
    ctx_static["config"]["domain_url"] = "."
    base = "."
    name_safe = re.sub(r"[^a-zA-Z0-9-]", "-", (ctx["config"].get("domain_name") or "site")[:50]).strip("-") or "site"
    os.makedirs(output_path, exist_ok=True)
    with get_connection() as conn:
        categories = _get_categories_with_counts(conn, domain_id)
        articles_all, _ = _get_domain_articles(conn, domain_id, 0, 1000, None)
    arts = [{"title": a["title"], "url": f"article/{a['title_id']}.html", "image": a.get("image", ""), "main_image": a.get("image", "")} for a in articles_all[:8]]
    cats = [{"name": c["name"], "url": f"category/{c['slug']}/", "count": c["count"]} for c in categories]
    name = ctx["config"].get("domain_name", "Recipe Blog")
    primary = (ctx["config"].get("colors") or {}).get("primary", "#6C8AE4")
    if isinstance(primary, dict):
        primary = primary.get("primary", "#6C8AE4")
    cats_index = [{"name": c["name"], "url": f"category/{c['slug']}/", "count": c["count"]} for c in categories]
    cats_sub = [{"name": c["name"], "url": f"../category/{c['slug']}/", "count": c["count"]} for c in categories]
    static_page_theme = _get_domain_page_theme(ctx_static["domain"])
    idx_tpl = (ctx_static["domain"].get("index_template") or "").strip()
    idx_cfg = dict(ctx_static["config"])
    idx_cfg["base_url"] = "."
    idx_cfg["domain_url"] = "."
    idx_cfg["articles"] = [{"title": a["title"], "url": f"article/{a['title_id']}.html", "image": a.get("main_image") or a.get("image", ""), "main_image": a.get("main_image") or a.get("image", ""), "excerpt": a.get("excerpt", "")} for a in articles_all[:12]]
    idx_cfg["categories"] = [{"name": c["name"], "url": f"category/{c['slug']}/", "slug": c["slug"], "count": c["count"]} for c in categories]
    idx_cfg["total"] = len(articles_all)
    idx_cfg["total_pages"] = max(1, (len(articles_all) + 11) // 12)
    idx_cfg["current_page"] = 1
    idx_cfg["per_page"] = 12
    idx_data = None
    if static_page_theme:
        idx_data = _fetch_themed_part_internal(static_page_theme, "index", idx_cfg)
    if not idx_data and idx_tpl:
        idx_data = _fetch_site_part_internal("index", idx_tpl, idx_cfg)
    if idx_data and idx_data.get("html"):
        index_main = idx_data["html"].replace('<div class="index-pagination-slot"></div>', "")
        index_css = idx_data.get("css", "")
        index_html = _build_static_page_html(domain_id, ctx_static, "index", main_html=index_main, main_css=index_css, page_title=f"{name} | Home", sidebar_categories=cats_index)
        _write_static_file(output_path, "index.html", index_html)
        cfg_recipes = dict(ctx_static["config"])
        cfg_recipes["domain_url"] = ".."
        _write_static_file(output_path, "recipes/index.html", _build_static_page_html(domain_id, dict(ctx_static, config=cfg_recipes), "recipes", main_html=index_main, main_css=index_css, page_title=f"{name} | Recipes", sidebar_categories=cats_sub))
    else:
        idx_tpl = ""
    if not idx_tpl:
        index_main = f"""<main class="preview-index" style="max-width:1200px;margin:0 auto;padding:2rem;">
  <section class="hero" style="text-align:center;padding:3rem 0;background:linear-gradient(135deg,rgba(108,138,228,.08) 0%,rgba(156,106,222,.08) 100%);border-radius:12px;margin-bottom:2rem;">
    <h1 style="font-family:Playfair Display,serif;font-size:2.5rem;color:{primary};">{html.escape(name)}</h1>
    <p style="color:#5A5A5A;margin-bottom:1.5rem;">Delicious recipes for every occasion</p>
    <a href="categories/" style="display:inline-block;padding:.75rem 1.5rem;background:{primary};color:#fff;text-decoration:none;border-radius:8px;font-weight:600;">Browse Categories</a>
  </section>
  <section><h2 style="font-size:1.5rem;margin-bottom:1.5rem;">Recent Recipes</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.5rem;">"""
        for a in articles_all[:12]:
            url = f"article/{a['title_id']}.html"
            ti = html.escape(a["title"])
            excerpt = html.escape((a.get("excerpt") or "")[:120])
            img = (a.get("main_image") or a.get("image") or "").strip()
            img_tag = f'<img src="{img}" alt="" style="width:100%;height:100%;object-fit:cover;">' if img and img.startswith("http") else '<div style="width:100%;height:100%;background:linear-gradient(135deg,#eee 0%,#ddd 100%);"></div>'
            index_main += f'<article style="background:#fff;border:1px solid #E2E8FF;border-radius:12px;overflow:hidden;"><a href="{url}" style="display:block;aspect-ratio:16/10;background:#eee;">{img_tag}</a><div style="padding:1.25rem;"><h3 style="font-size:1.1rem;"><a href="{url}" style="color:#2D2D2D;text-decoration:none;">{ti}</a></h3><p style="font-size:.9rem;color:#5A5A5A;">{excerpt}</p></div></article>'
        index_main += "</div></section></main>"
        index_html = _build_static_page_html(domain_id, ctx_static, "index", main_html=index_main, main_css="", page_title=f"{name} | Home", sidebar_categories=cats_index)
        _write_static_file(output_path, "index.html", index_html)
    if not idx_tpl:
        cfg_recipes = dict(ctx_static["config"])
        cfg_recipes["domain_url"] = ".."
        _write_static_file(output_path, "recipes/index.html", _build_static_page_html(domain_id, dict(ctx_static, config=cfg_recipes), "recipes", main_html=index_main, main_css="", page_title=f"{name} | Recipes", sidebar_categories=cats_sub))
    cats_main = f'<main style="max-width:800px;margin:0 auto;padding:2rem;"><h1 style="font-size:2rem;margin-bottom:1.5rem;color:{primary};">Categories</h1><div style="display:flex;flex-direction:column;gap:.75rem;">'
    for c in categories:
        cats_main += f'<a href="category/{html.escape(c["slug"])}/" style="display:flex;justify-content:space-between;padding:1rem;background:#fff;border:1px solid #eee;border-radius:8px;text-decoration:none;color:#2D2D2D;"><span>{html.escape(c["name"])}</span><span style="color:#5A5A5A;">{c["count"]}</span></a>'
    cats_main += "</div></main>"
    cfg_cats = dict(ctx_static["config"])
    cfg_cats["domain_url"] = ".."
    _write_static_file(output_path, "categories/index.html", _build_static_page_html(domain_id, dict(ctx_static, config=cfg_cats), "categories", main_html=cats_main, main_css="", page_title=f"{name} | Categories", sidebar_categories=cats_sub))
    about_main = f'<main style="max-width:600px;margin:0 auto;padding:2rem;"><h1>About {html.escape(name)}</h1><p>Welcome! We share delicious recipes for every occasion.</p><p><a href="../">Back to Home</a></p></main>'
    _write_static_file(output_path, "about/index.html", _build_static_page_html(domain_id, dict(ctx_static, config=cfg_cats), "about", main_html=about_main, main_css="", page_title=f"{name} | About", sidebar_categories=cats_sub))
    per_page = 12
    for c in categories:
        slug = c["slug"]
        filter_by = None if slug == "all" else c["name"]
        with get_connection() as conn2:
            if slug == "all":
                arts_all_cat, total_cat = _get_domain_articles(conn2, domain_id, 0, 10000, None)
            else:
                arts_all_cat, total_cat = _get_domain_articles(conn2, domain_id, 0, 10000, filter_by)
        cat_name = c["name"]
        cat_tpl = (ctx_static["domain"].get("category_page_template") or "category_1").strip() or "category_1"
        total_pages_cat = max(1, (total_cat + per_page - 1) // per_page)

        def _art_to_dict(a, base_url):
            img = a.get("main_image") or a.get("image", "")
            return {"title": a["title"], "url": base_url, "image": img, "main_image": img, "excerpt": a.get("excerpt", ""), "title_id": a.get("title_id")}

        for page_num in range(1, total_pages_cat + 1):
            offset = (page_num - 1) * per_page
            arts_page = arts_all_cat[offset:offset + per_page]
            depth = "../../" if page_num == 1 else "../../../"
            arts_list = [_art_to_dict(a, f"../../article/{a['title_id']}.html") for a in arts_page]

            cat_cfg = dict(ctx_static["config"])
            cat_cfg["domain_url"] = "../.."
            cat_cfg["category_name"] = cat_name
            cat_cfg["articles"] = arts_list
            cat_cfg["total"] = total_cat
            cat_cfg["total_pages"] = total_pages_cat
            cat_cfg["current_page"] = page_num
            cat_cfg["per_page"] = per_page
            cat_data = None
            if static_page_theme:
                cat_data = _fetch_themed_part_internal(static_page_theme, "category", cat_cfg)
            if not cat_data:
                cat_data = _fetch_site_part_internal("category", cat_tpl, cat_cfg)

            if cat_data:
                prev_url = f"../" if page_num == 2 else f"../page/{page_num - 1}/" if page_num > 2 else None
                next_url = f"../page/{page_num + 1}/" if page_num < total_pages_cat else None
                pag_parts = []
                if prev_url:
                    pag_parts.append(f'<a href="{prev_url}" class="page-prev">&laquo; Prev</a> ')
                pag_parts.append('<span class="page-numbers">')
                for i in range(1, total_pages_cat + 1):
                    if i == page_num:
                        pag_parts.append(f'<span class="page-current">{i}</span> ')
                    else:
                        u = "../" if i == 1 else f"../page/{i}/"
                        pag_parts.append(f'<a href="{u}" class="page-link">{i}</a> ')
                pag_parts.append('</span>')
                if next_url:
                    pag_parts.append(f' <a href="{next_url}" class="page-next">Next &raquo;</a>')
                pag_html = f'<nav class="pagination-nav">{"".join(pag_parts)}</nav>'
                cat_main = cat_data["html"].replace("</main>", pag_html + "\n</main>")
                cat_html = _build_static_page_html(domain_id, dict(ctx_static, config=cat_cfg), "category", main_html=cat_main, main_css=cat_data.get("css", ""), page_title=f"{name} | {cat_name}" + (f" (Page {page_num})" if page_num > 1 else ""), include_sidebar=False)
            else:
                def _fallback_card(a):
                    img = (a.get("main_image") or a.get("image") or "").strip()
                    img_tag = f'<img src="{img}" alt="" style="width:100%;height:180px;object-fit:cover;">' if img and img.startswith("http") else '<div style="width:100%;height:180px;background:#eee;"></div>'
                    return f'<article><a href="../../article/{a["title_id"]}.html">{img_tag}<h3>{html.escape(a["title"])}</h3></a></article>'
                cat_main = f'<main><h1>{html.escape(cat_name)}</h1><p>{total_cat} recipes</p><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.5rem;">' + "".join(_fallback_card(a) for a in arts_page) + "</div></main>"
                cat_html = _build_static_page_html(domain_id, ctx_static, "category", main_html=cat_main, main_css="", page_title=f"{name} | {cat_name}", include_sidebar=False)

            if page_num == 1:
                _write_static_file(output_path, f"category/{slug}/index.html", cat_html)
            else:
                _write_static_file(output_path, f"category/{slug}/page/{page_num}/index.html", cat_html)
    with get_connection() as conn:
        for a in articles_all:
            tid = a["title_id"]
            cur = db_execute(conn, "SELECT article_html, article_css, pin_image, writer, writer_avatar FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
            ac = dict_row(cur.fetchone())
            art_html = (ac.get("article_html") or "").strip()
            art_css = (ac.get("article_css") or "").strip()
            art_pin_img = (ac.get("pin_image") or "").strip()
            writer_json = ac.get("writer")
            writer_avatar = ac.get("writer_avatar")

            writer_data = None
            if writer_json:
                try:
                    writer_data = json.loads(writer_json) if isinstance(writer_json, str) else writer_json
                    if writer_avatar:
                        writer_data["avatar"] = writer_avatar
                except:
                    pass

            title_text = a.get("title", "")
            art_pin_attr = f' data-pin-image="{art_pin_img}"' if art_pin_img else ""
            art_main = f'<main class="preview-article"><article class="article-content"{art_pin_attr}>{art_html or "<p>No content yet.</p>"}</article></main>'
            art_cfg = dict(ctx_static["config"])
            art_cfg["domain_url"] = "../.."
            depth = "../../"
            art_full = _build_static_page_html(domain_id, dict(ctx_static, config=art_cfg), "article", main_html=art_main, main_css=f".article-content{{line-height:1.7}}{art_css}", page_title=f"{title_text} | {name}", include_sidebar=True, sidebar_articles=[{"title": x["title"], "url": f"{depth}article/{x['title_id']}.html", "image": x.get("image", ""), "main_image": x.get("image", "")} for x in articles_all[:6] if x["title_id"] != tid], sidebar_categories=[{"name": cx["name"], "url": f"{depth}category/{cx['slug']}/", "count": cx["count"]} for cx in categories], writer=writer_data)
            _write_static_file(output_path, f"article/{tid}.html", art_full)
    return jsonify({"success": True, "output_path": output_path})


@app.route("/api/domains/<int:domain_id>/deploy-cloudflare", methods=["POST"])
def api_deploy_cloudflare(domain_id):
    """Generate static project and deploy to Cloudflare Pages via Wrangler (direct upload, no GitHub)."""
    try:
        return _do_deploy_cloudflare(domain_id)
    except Exception as e:
        log.exception("[deploy-cloudflare] Unexpected error")
        tb = traceback.format_exc()
        return jsonify({"success": False, "error": str(e), "traceback": tb}), 500


def _do_deploy_cloudflare(domain_id):
    """Inner deploy logic; raises on error."""
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return jsonify({
            "success": False,
            "error": "Cloudflare not configured. Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in .env"
        }), 400
    with app.test_request_context(path=f"/api/domains/{domain_id}/generate-static-project", method="POST"):
        resp = api_generate_static_project(domain_id)
        gen_data = resp.get_json() if resp else None
    if not gen_data or not gen_data.get("success"):
        return jsonify({"success": False, "error": gen_data.get("error", "Generation failed")}), 500
    output_path = gen_data["output_path"]
    if not os.path.isdir(output_path) or not os.path.isfile(os.path.join(output_path, "index.html")):
        return jsonify({"success": False, "error": "Generated project has no index.html"}), 500
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_url, domain_name FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone()) or {}
    domain_url = (row.get("domain_url") or "").strip()
    domain_name = (row.get("domain_url") or row.get("domain_name") or "site").strip()
    raw_name = domain_url or domain_name
    if raw_name and ("://" in raw_name or "/" in raw_name):
        raw_name = re.sub(r"^https?://", "", raw_name).split("/")[0].split("?")[0]
    project_name = re.sub(r"[^a-zA-Z0-9-]", "-", (raw_name or "site")[:50].replace(".", "-")).strip("-") or f"domain-{domain_id}"
    env = os.environ.copy()
    env["CLOUDFLARE_ACCOUNT_ID"] = CLOUDFLARE_ACCOUNT_ID
    env["CLOUDFLARE_API_TOKEN"] = CLOUDFLARE_API_TOKEN
    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    # Create project via Cloudflare API if it doesn't exist
    create_body = json.dumps({"name": project_name, "production_branch": "main"}).encode("utf-8")
    create_req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects",
        data=create_body,
        method="POST",
        headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(create_req, timeout=20) as _:
            log.info("[deploy-cloudflare] Created Pages project: %s", project_name)
    except urllib.error.HTTPError as e:
        body = (e.read().decode("utf-8", errors="replace") if e.fp else "") or ""
        if e.code in (409, 422) or "already" in body.lower() or "exists" in body.lower() or "8000013" in body:
            pass
        else:
            log.warning("[deploy-cloudflare] create project HTTP %s: %s", e.code, body[:400])
    fd_out, path_out = tempfile.mkstemp(suffix=".txt", text=True)
    fd_err, path_err = tempfile.mkstemp(suffix=".txt", text=True)
    try:
        try:
            with os.fdopen(fd_out, "w") as f_out:
                with os.fdopen(fd_err, "w") as f_err:
                    result = subprocess.run(
                        [npx_cmd, "wrangler", "pages", "deploy", output_path, "--project-name", project_name],
                        stdout=f_out,
                        stderr=f_err,
                        text=True,
                        timeout=600,
                        env=env,
                        shell=False,
                    )
        except FileNotFoundError:
            return jsonify({"success": False, "error": "npx not found. Install Node.js to use Wrangler."}), 500
        except subprocess.TimeoutExpired:
            return jsonify({"success": False, "error": "Deploy timed out after 10 minutes. Try again; first deploy can be slow."}), 500
        with open(path_out, "r", encoding="utf-8", errors="replace") as f:
            result_stdout = f.read()
        with open(path_err, "r", encoding="utf-8", errors="replace") as f:
            result_stderr = f.read()
    finally:
        try:
            os.unlink(path_out)
        except OSError:
            pass
        try:
            os.unlink(path_err)
        except OSError:
            pass
    if result.returncode != 0:
        err = (result_stderr or result_stdout or "Unknown error").strip()[-600:]
        if "8000007" in err or "Project not found" in err:
            err += (
                f"\n\nTo fix: Create the project manually first. Go to Cloudflare Dashboard > Workers & Pages > "
                f"Create > Pages > Direct Upload. Enter project name: {project_name}"
            )
        log.error("[deploy-cloudflare] wrangler failed: %s", err)
        return jsonify({"success": False, "error": f"Wrangler failed: {err}"}), 500
    url_match = re.search(r"https://[^\s\)\"]+\.pages\.dev", result_stdout or "")
    live_url = url_match.group(0) if url_match else None
    custom_domains_added = []
    hostname = raw_name.strip().lower() if raw_name else None
    if hostname and "." in hostname:
        domains_to_add = [hostname]
        if not hostname.startswith("www."):
            domains_to_add.append("www." + hostname)
        for dom in domains_to_add:
            try:
                domain_req = urllib.request.Request(
                    f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{project_name}/domains",
                    data=json.dumps({"name": dom}).encode("utf-8"),
                    method="POST",
                    headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
                )
                with urllib.request.urlopen(domain_req, timeout=15) as _:
                    custom_domains_added.append(dom)
                    log.info("[deploy-cloudflare] Added custom domain: %s", dom)
            except urllib.error.HTTPError as e:
                body = (e.read().decode("utf-8", errors="replace") if e.fp else "") or ""
                if "already" in body.lower() or "exists" in body.lower() or e.code in (409, 422):
                    custom_domains_added.append(dom)
                else:
                    log.warning("[deploy-cloudflare] add domain %s HTTP %s: %s", dom, e.code, body[:200])
            except Exception as ex:
                log.warning("[deploy-cloudflare] add domain %s failed: %s", dom, ex)
    resp_data = {"success": True, "output_path": output_path, "project_name": project_name, "url": live_url}
    if custom_domains_added:
        resp_data["custom_domains"] = custom_domains_added
    return jsonify(resp_data)


def _domain_to_project_name(domain_url, domain_name, domain_id):
    """Derive Cloudflare Pages project name from domain."""
    raw = (domain_url or domain_name or "").strip()
    if raw and ("://" in raw or "/" in raw):
        raw = re.sub(r"^https?://", "", raw).split("/")[0].split("?")[0]
    return re.sub(r"[^a-zA-Z0-9-]", "-", (raw or "site")[:50].replace(".", "-")).strip("-") or f"domain-{domain_id}"


def _check_url_up(url, timeout=10):
    """HEAD first, GET fallback; return (True, None) if up, else (False, reason)."""
    if not url or not url.startswith("http"):
        return False, "invalid url"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
    last_err = None
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if 200 <= resp.status < 400:
                    return True, None
                return False, f"HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}"
        except (urllib.error.URLError, OSError) as e:
            last_err = str(getattr(e, "reason", e) or e)
        except Exception as ex:
            last_err = str(ex)
    return False, last_err or "unknown"


@app.route("/api/domains/<int:domain_id>/cloudflare-info", methods=["POST", "GET"])
def api_domain_cloudflare_info(domain_id):
    """POST: fetch Cloudflare Pages project info, save to cloudflare_info, return JSON. GET: return saved info."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_url, domain_name, cloudflare_info FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"success": False, "error": "Domain not found"}), 404
    if request.method == "GET":
        raw = (row.get("cloudflare_info") or "").strip()
        info = {}
        if raw:
            try:
                info = json.loads(raw) if isinstance(raw, str) else raw
            except json.JSONDecodeError:
                pass
        return jsonify({"success": True, "cloudflare_info": info})
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return jsonify({"success": False, "error": "Cloudflare not configured"}), 400
    project_name = _domain_to_project_name(row.get("domain_url"), row.get("domain_name"), domain_id)
    domain_url = (row.get("domain_url") or "").strip()
    hostname = None
    if domain_url:
        hostname = re.sub(r"^https?://", "", domain_url).split("/")[0].split("?")[0].lower()
    result = {"domain_url": domain_url or hostname, "project_name": project_name, "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "status": "unknown", "up": False, "urls_checked": [], "project": None, "deployments": [], "domains": [], "dns_setup": False}
    try:
        req = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{project_name}",
            method="GET",
            headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            proj = data.get("result")
            if proj:
                result["project"] = {
                    "name": proj.get("name"),
                    "subdomain": proj.get("subdomain"),
                    "domains": proj.get("domains") or [],
                    "canonical_deployment": (proj.get("canonical_deployment") or {}).get("url") if proj.get("canonical_deployment") else None,
                }
                result["domains"] = proj.get("domains") or []
                _sub = (proj.get("subdomain") or "").strip().rstrip("/")
                if _sub.endswith(".pages.dev"):
                    pages_url = f"https://{_sub}" if _sub else None
                else:
                    pages_url = f"https://{_sub}.pages.dev" if _sub else None
                if pages_url:
                    result["urls_checked"].append(pages_url)
                    up, reason = _check_url_up(pages_url)
                    result["check_details"] = result.get("check_details") or []
                    result["check_details"].append({"url": pages_url, "up": up, "reason": reason})
                    if up:
                        result["up"] = True
                        result["status"] = "up"
                    else:
                        result["status"] = "down"
                        result["down_reason"] = reason
        req2 = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{project_name}/deployments",
            method="GET",
            headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"},
        )
        with urllib.request.urlopen(req2, timeout=15) as resp2:
            data2 = json.loads(resp2.read().decode())
            deploys = data2.get("result") or []
            for d in deploys[:5]:
                result["deployments"].append({
                    "id": d.get("id"),
                    "url": d.get("url"),
                    "status": d.get("latest_stage", {}).get("status") if d.get("latest_stage") else d.get("status"),
                    "created_on": d.get("created_on"),
                })
        if hostname:
            result["check_details"] = result.get("check_details") or []
            for scheme in ("https://", "http://"):
                u = scheme + hostname
                result["urls_checked"].append(u)
                up, reason = _check_url_up(u)
                result["check_details"].append({"url": u, "up": up, "reason": reason})
                if up:
                    result["up"] = True
                    result["status"] = "up"
                    result["custom_domain_up"] = u
                    break
            if not result["up"]:
                result["status"] = "down"
                if result.get("check_details"):
                    result["down_reason"] = "; ".join(
                        (d["reason"] or "ok") for d in result["check_details"] if not d.get("up", True)
                    )
        if hostname:
            try:
                zone_req = urllib.request.Request(
                    f"https://api.cloudflare.com/client/v4/zones?name={hostname}",
                    method="GET",
                    headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"},
                )
                with urllib.request.urlopen(zone_req, timeout=10) as zr:
                    zdata = json.loads(zr.read().decode())
                    zones = zdata.get("result") or []
                    result["dns_setup"] = bool(zones)
            except Exception:
                pass
    except urllib.error.HTTPError as e:
        body = (e.read().decode("utf-8", errors="replace") if e.fp else "") or ""
        result["error"] = f"HTTP {e.code}: {body[:300]}"
        result["status"] = "error"
    except Exception as ex:
        result["error"] = str(ex)
        result["status"] = "error"
    info_json = json.dumps(result, ensure_ascii=False)
    with get_connection() as conn:
        db_execute(conn, "UPDATE domains SET cloudflare_info = ? WHERE id = ?", (info_json, domain_id))
    return jsonify({"success": True, "cloudflare_info": result})


@app.route("/api/domains/<int:domain_id>/cloudflare-deployments", methods=["GET"])
def api_domain_cloudflare_deployments(domain_id):
    """Fetch all deployments from Cloudflare Pages for this domain's project."""
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return jsonify({"success": False, "error": "Cloudflare not configured"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_url, domain_name FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"success": False, "error": "Domain not found"}), 404
    project_name = _domain_to_project_name(row.get("domain_url"), row.get("domain_name"), domain_id)
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    # Fetch canonical (live) deployment id from project
    canonical_id = None
    try:
        req = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{project_name}",
            method="GET", headers=headers,
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            pdata = json.loads(resp.read().decode())
            canonical_id = ((pdata.get("result") or {}).get("canonical_deployment") or {}).get("id")
    except Exception:
        pass
    # Fetch deployments list
    try:
        req2 = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{project_name}/deployments?per_page=25",
            method="GET", headers=headers,
        )
        with urllib.request.urlopen(req2, timeout=15) as resp2:
            data = json.loads(resp2.read().decode())
            deploys = data.get("result") or []
            result = []
            for d in deploys:
                stage = d.get("latest_stage") or {}
                result.append({
                    "id": d.get("id"),
                    "url": d.get("url"),
                    "status": stage.get("status") or d.get("status"),
                    "created_on": d.get("created_on"),
                    "is_live": d.get("id") == canonical_id,
                })
            return jsonify({"success": True, "project_name": project_name, "deployments": result, "canonical_id": canonical_id})
    except urllib.error.HTTPError as e:
        body = (e.read().decode("utf-8", errors="replace") if e.fp else "") or ""
        return jsonify({"success": False, "error": f"HTTP {e.code}: {body[:300]}"}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500


@app.route("/api/domains/<int:domain_id>/cloudflare-rollback/<deployment_id>", methods=["POST"])
def api_domain_cloudflare_rollback(domain_id, deployment_id):
    """Promote (rollback to) a specific Cloudflare Pages deployment as the new live version."""
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return jsonify({"success": False, "error": "Cloudflare not configured"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_url, domain_name FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"success": False, "error": "Domain not found"}), 404
    project_name = _domain_to_project_name(row.get("domain_url"), row.get("domain_name"), domain_id)
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"}
    try:
        req = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{project_name}/deployments/{deployment_id}/rollback",
            data=b"{}",
            method="POST",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            d = data.get("result") or {}
            return jsonify({"success": True, "new_deployment_id": d.get("id"), "url": d.get("url")})
    except urllib.error.HTTPError as e:
        body = (e.read().decode("utf-8", errors="replace") if e.fp else "") or ""
        return jsonify({"success": False, "error": f"HTTP {e.code}: {body[:300]}"}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500


def _normalize_domain(value):
    """Strip protocol and www, return bare domain (e.g. 'example.com')."""
    v = (value or "").strip()
    if not v:
        return ""
    v = re.sub(r"^https?://", "", v, flags=re.IGNORECASE)
    v = v.split("/")[0].split("?")[0].strip().lower()
    if v.startswith("www."):
        v = v[4:]
    return v


def _domain_to_hostname(domain_url, domain_name):
    """Extract apex hostname (e.g. example.com) from domain_url."""
    raw = (domain_url or domain_name or "").strip()
    if not raw:
        return None
    raw = re.sub(r"^https?://", "", raw).split("/")[0].split("?")[0].lower()
    if raw.startswith("www."):
        raw = raw[4:]
    return raw if raw and "." in raw else None


@app.route("/api/domains/<int:domain_id>/cloudflare-setup-dns", methods=["POST"])
def api_domain_cloudflare_setup_dns(domain_id):
    """Add domain to Cloudflare Zone, get nameservers, add custom domain to Pages project."""
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return jsonify({"success": False, "error": "Cloudflare not configured. Add CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN to .env"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_url, domain_name FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"success": False, "error": "Domain not found"}), 404
    hostname = _domain_to_hostname(row.get("domain_url"), row.get("domain_name"))
    if not hostname:
        return jsonify({"success": False, "error": "Invalid domain URL. Use format https://example.com"}), 400
    project_name = _domain_to_project_name(row.get("domain_url"), row.get("domain_name"), domain_id)
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"}
    zone_id = None
    name_servers = []
    # 1. Create zone or get existing
    try:
        create_req = urllib.request.Request(
            "https://api.cloudflare.com/client/v4/zones",
            data=json.dumps({"name": hostname, "account": {"id": CLOUDFLARE_ACCOUNT_ID}, "jump_start": True}).encode(),
            method="POST",
            headers=headers,
        )
        with urllib.request.urlopen(create_req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            z = data.get("result")
            if z:
                zone_id = z.get("id")
                name_servers = z.get("name_servers") or []
    except urllib.error.HTTPError as e:
        body = (e.read().decode("utf-8", errors="replace") if e.fp else "") or ""
        if e.code == 409 or "already" in body.lower() or "exists" in body.lower():
            # Zone exists in this account, fetch it
            try:
                list_req = urllib.request.Request(
                    f"https://api.cloudflare.com/client/v4/zones?name={hostname}",
                    method="GET",
                    headers=headers,
                )
                with urllib.request.urlopen(list_req, timeout=15) as r2:
                    d2 = json.loads(r2.read().decode())
                    zones = d2.get("result") or []
                    if zones:
                        zone_id = zones[0].get("id")
                        name_servers = zones[0].get("name_servers") or []
            except Exception as ex2:
                return jsonify({"success": False, "error": f"Zone exists but could not fetch: {ex2}"}), 500
        else:
            return jsonify({"success": False, "error": f"HTTP {e.code}: {body[:400]}"}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500
    if not name_servers:
        return jsonify({"success": False, "error": "Could not get nameservers from Cloudflare"}), 500
    # 2. Add DNS records (CNAME @ and www -> Pages) - brief wait if zone was just created
    pages_target = f"{project_name}.pages.dev"
    records_added = []
    dns_errors = []
    if zone_id:
        time.sleep(2)
        for rec_name, rec_content in [("@", pages_target), ("www", pages_target)]:
            try:
                rec_body = json.dumps({
                    "type": "CNAME",
                    "name": rec_name,
                    "content": rec_content,
                    "ttl": 1,
                    "proxied": True,
                }).encode()
                rec_req = urllib.request.Request(
                    f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                    data=rec_body,
                    method="POST",
                    headers=headers,
                )
                with urllib.request.urlopen(rec_req, timeout=15) as _:
                    records_added.append(f"{rec_name} -> {rec_content}")
                    log.info("[cloudflare-setup-dns] Added DNS record: %s CNAME %s", rec_name, rec_content)
            except urllib.error.HTTPError as er:
                eb = (er.read().decode("utf-8", errors="replace") if er.fp else "") or ""
                if "already" in eb.lower() or "exists" in eb.lower() or er.code in (409, 422):
                    records_added.append(f"{rec_name} (exists)")
                else:
                    msg = f"{rec_name}: HTTP {er.code} — {eb[:200]}"
                    dns_errors.append(msg)
                    log.warning("[cloudflare-setup-dns] Add DNS %s: HTTP %s %s", rec_name, er.code, eb[:150])
            except Exception as exr:
                msg = f"{rec_name}: {exr}"
                dns_errors.append(msg)
                log.warning("[cloudflare-setup-dns] Add DNS %s failed: %s", rec_name, exr)
    # 3. Add custom domain + www to Pages project (project must exist - deploy first)
    domains_added = []
    for dom in [hostname, f"www.{hostname}"]:
        try:
            add_req = urllib.request.Request(
                f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{project_name}/domains",
                data=json.dumps({"name": dom}).encode(),
                method="POST",
                headers=headers,
            )
            with urllib.request.urlopen(add_req, timeout=15) as _:
                domains_added.append(dom)
                log.info("[cloudflare-setup-dns] Added Pages domain: %s", dom)
        except urllib.error.HTTPError as ea:
            b = (ea.read().decode("utf-8", errors="replace") if ea.fp else "") or ""
            if "already" in b.lower() or "exists" in b.lower() or ea.code in (409, 422):
                domains_added.append(dom)
            else:
                log.warning("[cloudflare-setup-dns] Add domain %s: HTTP %s %s", dom, ea.code, b[:150])
        except Exception as exa:
            log.warning("[cloudflare-setup-dns] Add domain %s failed: %s", dom, exa)
    return jsonify({
        "success": True,
        "hostname": hostname,
        "name_servers": name_servers,
        "zone_id": zone_id,
        "pages_project": project_name,
        "domains_added": domains_added,
        "dns_records_added": records_added,
        "dns_errors": dns_errors,
    })


@app.route("/api/domains/<int:domain_id>/cloudflare-add-dns-records", methods=["POST"])
def api_domain_cloudflare_add_dns_records(domain_id):
    """Add CNAME records (@ and www) to existing Cloudflare zone for Pages. Use when zone exists but has no records."""
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return jsonify({"success": False, "error": "Cloudflare not configured"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT domain_url, domain_name FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"success": False, "error": "Domain not found"}), 404
    hostname = _domain_to_hostname(row.get("domain_url"), row.get("domain_name"))
    if not hostname:
        return jsonify({"success": False, "error": "Invalid domain URL"}), 400
    project_name = _domain_to_project_name(row.get("domain_url"), row.get("domain_name"), domain_id)
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"}
    zone_id = None
    try:
        req = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/zones?name={hostname}",
            method="GET",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            zones = data.get("result") or []
            if zones:
                zone_id = zones[0].get("id")
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500
    if not zone_id:
        return jsonify({"success": False, "error": f"Zone for {hostname} not found. Run 'Check & Setup' first."}), 404
    pages_target = f"{project_name}.pages.dev"
    records_added = []
    for rec_name, rec_content in [("@", pages_target), ("www", pages_target)]:
        try:
            rec_body = json.dumps({
                "type": "CNAME",
                "name": rec_name,
                "content": rec_content,
                "ttl": 1,
                "proxied": True,
            }).encode()
            rec_req = urllib.request.Request(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                data=rec_body,
                method="POST",
                headers=headers,
            )
            with urllib.request.urlopen(rec_req, timeout=15) as _:
                records_added.append(f"{rec_name} -> {rec_content}")
                log.info("[cloudflare-add-dns-records] Added: %s CNAME %s", rec_name, rec_content)
        except urllib.error.HTTPError as er:
            eb = (er.read().decode("utf-8", errors="replace") if er.fp else "") or ""
            if "already" in eb.lower() or "exists" in eb.lower() or er.code in (409, 422):
                records_added.append(f"{rec_name} (exists)")
            else:
                return jsonify({"success": False, "error": f"Add DNS {rec_name}: HTTP {er.code} {eb[:200]}"}), 400
        except Exception as exr:
            return jsonify({"success": False, "error": f"Add DNS {rec_name}: {exr}"}), 500
    return jsonify({"success": True, "records_added": records_added})


def api_domain_article_snippets_apply_to_articles():
    """Apply snippets to specific articles. Body: { title_ids: [1,2,3], snippets: {...} }."""
    data = request.get_json(silent=True) or {}
    title_ids = data.get("title_ids")
    snippets = data.get("snippets")
    if not title_ids:
        return jsonify({"success": False, "error": "title_ids required (array)"}), 400
    if not isinstance(title_ids, list):
        title_ids = [int(x) for x in str(title_ids).split(",") if str(x).strip().isdigit()]
    else:
        title_ids = [int(x) for x in title_ids if x is not None]
    if snippets is None:
        snippets = {}
    if not isinstance(snippets, dict):
        return jsonify({"success": False, "error": "snippets must be object"}), 400
    snippets_json = json.dumps(snippets, ensure_ascii=False)
    updated = 0
    with get_connection() as conn:
        for tid in title_ids:
            cur = db_execute(conn, "SELECT article_html FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
            r = dict_row(cur.fetchone())
            if not r or not (r.get("article_html") or "").strip():
                continue
            html_orig = (r.get("article_html") or "").strip()
            html_new = _inject_snippets_into_article_html(html_orig, snippets_json)
            if html_new != html_orig:
                db_execute(conn, "UPDATE article_content SET article_html = ? WHERE title_id = ? AND language_code = 'en'", (html_new, tid))
                updated += 1
    log.info("[snippets-apply-to-articles] %s articles updated", updated)
    return jsonify({"success": True, "updated": updated, "total": len(title_ids)})


@app.route("/api/domain-article-snippets/apply-by-template", methods=["POST"])
def api_domain_article_snippets_apply_by_template():
    """Apply snippets to ALL articles in ALL domains with given template. Body: { template, snippets, category? }."""
    data = request.get_json(silent=True) or {}
    template = (data.get("template") or "").strip()
    snippets = data.get("snippets")
    category = (data.get("category") or "").strip()
    if not template:
        return jsonify({"success": False, "error": "template required"}), 400
    if snippets is None:
        snippets = {}
    if not isinstance(snippets, dict):
        return jsonify({"success": False, "error": "snippets must be object"}), 400
    snippets_json = json.dumps(snippets, ensure_ascii=False)
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id FROM domains WHERE website_template = ?", (template,))
        domain_ids = [r["id"] for r in cur.fetchall() if r and r.get("id")]
    if not domain_ids:
        return jsonify({"success": True, "updated": 0, "domains": 0, "message": "No domains with this template"})
    all_title_ids = []
    with get_connection() as conn:
        for did in domain_ids:
            cur = db_execute(conn, "SELECT t.id FROM titles t WHERE t.domain_id = ?", (did,))
            all_title_ids.extend([r["id"] for r in cur.fetchall() if r and r.get("id")])
        if category:
            all_title_ids = _filter_title_ids_by_category(conn, all_title_ids, category)
    updated = 0
    with get_connection() as conn:
        for tid in all_title_ids:
            cur = db_execute(conn, "SELECT article_html FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
            r = dict_row(cur.fetchone())
            if not r or not (r.get("article_html") or "").strip():
                continue
            html_orig = (r.get("article_html") or "").strip()
            html_new = _inject_snippets_into_article_html(html_orig, snippets_json)
            if html_new != html_orig:
                db_execute(conn, "UPDATE article_content SET article_html = ? WHERE title_id = ? AND language_code = 'en'", (html_new, tid))
                updated += 1
    log.info("[snippets-apply-by-template] Template %s: %s domains, %s articles updated", template, len(domain_ids), updated)
    return jsonify({"success": True, "updated": updated, "total": len(all_title_ids), "domains": len(domain_ids), "template": template})


@app.route("/api/domain-article-snippets/by-template/<template_name>", methods=["GET"])
def api_domain_article_snippets_by_template(template_name):
    """Get snippets from first domain that has this template. For loading into editor."""
    template = (template_name or "").strip()
    if not template:
        return jsonify({"error": "template required"}), 400
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, article_html_snippets FROM domains WHERE website_template = ? ORDER BY id LIMIT 1", (template,))
        row = dict_row(cur.fetchone())
    if not row:
        return jsonify({"domain_id": None, "snippets": {}, "message": "No domain with this template"})
    raw = row.get("article_html_snippets") or ""
    snippets = {}
    if raw:
        try:
            snippets = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError:
            pass
    return jsonify({"domain_id": row["id"], "snippets": snippets, "template": template})


@app.route("/api/domain-article-snippets/<int:domain_id>/apply-to-template", methods=["POST"])
def api_domain_article_snippets_apply_to_template(domain_id):
    """Apply this domain's snippets to ALL articles in ALL domains that use the same website_template (generator)."""
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT article_html_snippets, website_template FROM domains WHERE id = ?", (domain_id,))
        row = dict_row(cur.fetchone())
        if not row:
            return jsonify({"error": "Domain not found"}), 404
        template = (row.get("website_template") or "").strip()
        if not template:
            return jsonify({"success": False, "error": "Domain has no website_template set"}), 400
        snippets_json = row.get("article_html_snippets") or ""
        cur = db_execute(conn, "SELECT id FROM domains WHERE website_template = ?", (template,))
        domain_ids = [r["id"] for r in cur.fetchall() if r and r.get("id")]
    if not domain_ids:
        return jsonify({"success": True, "updated": 0, "domains": 0, "message": "No domains with this template"})
    all_title_ids = []
    with get_connection() as conn:
        for did in domain_ids:
            cur = db_execute(conn, "SELECT t.id FROM titles t WHERE t.domain_id = ?", (did,))
            all_title_ids.extend([r["id"] for r in cur.fetchall() if r and r.get("id")])
    updated = 0
    with get_connection() as conn:
        for tid in all_title_ids:
            cur = db_execute(conn, "SELECT article_html FROM article_content WHERE title_id = ? AND language_code = 'en'", (tid,))
            r = dict_row(cur.fetchone())
            if not r or not (r.get("article_html") or "").strip():
                continue
            html_orig = (r.get("article_html") or "").strip()
            html_new = _inject_snippets_into_article_html(html_orig, snippets_json)
            if html_new != html_orig:
                db_execute(conn, "UPDATE article_content SET article_html = ? WHERE title_id = ? AND language_code = 'en'", (html_new, tid))
                updated += 1
    log.info("[snippets-apply-template] Template %s: %s domains, %s articles updated", template, len(domain_ids), updated)
    return jsonify({"success": True, "updated": updated, "total": len(all_title_ids), "domains": len(domain_ids), "template": template})


PINTEREST_RED = "#E60023"
PINTEREST_RED_HOVER = "#FF1A3C"


def _enforce_pinterest_pin_color(cfg):
    """Force Pin Recipe button to always use Pinterest red. Mutates cfg in place."""
    if not isinstance(cfg, dict):
        return
    if "colors" not in cfg:
        cfg["colors"] = {}
    if isinstance(cfg["colors"], dict):
        cfg["colors"]["button_pin"] = PINTEREST_RED
        cfg["colors"]["button_hover_pin"] = PINTEREST_RED_HOVER
    return cfg


RESKIN_PROMPT_BASE = """You are a professional UI/UX designer for recipe blog articles. You receive the current HTML structure, CSS, and config. The config is INJECTED into the template to produce the HTML/CSS. Generate a NEW config that will produce a BETTER, noticeably DIFFERENT design when injected. Keep the EXACT same JSON keys and structure; only change VALUES.

{intensity_instructions}

Choose a contrasting aesthetic (e.g. if current is light and minimal → try dark mode or warm cozy; if warm pastels → try cool modern or bold). Do NOT keep similar colors or fonts — aim for a clearly different look.

CRITICAL — CONTRAST & READABILITY (must follow):
- Pick ONE theme: LIGHT (light backgrounds + dark text) OR DARK (dark backgrounds + light text). Be consistent.
- LIGHT theme: background #fff or #f8f9fa, container_bg #fff or light gray, text_primary #1a1a1a or #2d2d2d, text_secondary #4a4a4a or #555555 (dark gray — readable on white), recipe_card.bg light, pro_tips_box.bg_color light.
- DARK theme: background #1a1a1f or #0f0f12, container_bg #252530, text_primary #e8e8ed or #f5f5f5, text_secondary #b0b0b8 or #c8c8d0 (light gray — readable on dark), recipe_card.bg dark/medium, pro_tips_box.bg_color dark/medium.
- text_secondary: On LIGHT backgrounds use DARK gray (#4a4a4a, #555555, #5a5a5a). NEVER use light gray (#888, #999, #aaa) on white/light — that makes text unreadable. On DARK backgrounds use light gray (#b0b0b8, #c8c8d0).
- text_primary and text_secondary MUST have strong contrast against ALL backgrounds (page, container, cards, pro_tips_box). NEVER light-on-light or dark-on-dark.
- numbered_list: circle_bg and circle_color must contrast (e.g. #F4A261 circle + #fff number).
- button_pin and button_hover_pin: ALWAYS use Pinterest red #E60023 and #FF1A3C. Never change these — the Pin Recipe button must always match Pinterest brand.

CRITICAL — FONTS FOR READABILITY (must follow):
- body.family: Use high-legibility fonts: Inter, Source Sans 3, Open Sans, Lato, DM Sans, PT Sans, Work Sans. Avoid thin or decorative fonts for body text.
- body.size: At least 1rem (16px). Never smaller than 0.9375rem for body.
- body.line_height: 1.6 to 1.8 for comfortable reading.
- heading.family: Readable serif or sans: Playfair Display, Lora, Merriweather, Source Serif 4, Fraunces, DM Sans.

--- HTML STRUCTURE (abbreviated) ---
{html_snippet}

--- CSS (how config maps to styles: --primary, .recipe-card, .pro-tips-box, etc.) ---
{css_snippet}

--- CURRENT CONFIG (what you will transform) ---
{config}

SCHEMA (use these keys exactly, change only values):
- colors: primary, secondary, accent, background, container_bg, border, text_primary, text_secondary (text_secondary: dark #4a4a4a–#555 on light bg; light #b0b0b8–#c8c8d0 on dark bg), button_print, button_pin, button_hover_print, button_hover_pin, link, list_marker (hex: #RRGGBB)
- fonts: heading.family (Playfair Display, Lora, Merriweather, Source Serif 4, Fraunces), heading.sizes.h1/h2/h3, body.family (Inter, Source Sans 3, Open Sans, Lato, DM Sans — high legibility), body.size (min 1rem), body.line_height (1.6–1.8)
- layout: max_width, section_spacing, paragraph_spacing, list_spacing, container_padding, border_radius, box_shadow
- components: pro_tips_box (bg_color, border_color, border_left, padding); recipe_card (bg, border, border_radius, padding, meta_icon_color); numbered_list (circle_bg, circle_color, circle_size); bullet_list (color)

Return ONLY valid JSON config. No markdown, no ```, no explanation."""

RESKIN_INTENSITY = {
    "subtle": ("Refine colors and typography slightly for polish. Small improvements.", 0.4),
    "bold": ("Make BOLD changes: different color palette, different font personality, different overall feel. The result must look clearly different from the original.", 0.7),
    "complete": ("Complete makeover: transform to a totally different aesthetic. Change palette (e.g. light→dark or warm→cool), fonts, layout spacing, component styles. Output must strongly contrast with the original.", 0.85),
}


def _deep_merge_config(base, override):
    """Merge override into base. Only override non-null values. Preserves base structure."""
    if not isinstance(base, dict) or not isinstance(override, dict):
        return override if override is not None else base
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge_config(out[k], v)
        elif v is not None and v != "":
            out[k] = v
    return out


def _fetch_article_preview(config, generator):
    """Call article-preview API to get HTML and CSS for the given config."""
    payload = dict(config)
    if "title" not in payload or not payload.get("title"):
        payload["title"] = "Sample Recipe Title"
    if "categories_list" not in payload or not isinstance(payload.get("categories_list"), list):
        payload["categories_list"] = [{"id": 1, "categorie": "dessert"}]
    base = (GENERATE_ARTICLE_API_URL or "").rstrip("/")
    url = f"{base}/generate-article-preview/{generator}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        out = json.loads(resp.read().decode())
    return (
        (out.get("article_html") or "").strip(),
        (out.get("article_css") or "").strip(),
    )


def _reskin_article_template_config(config, generator, intensity="bold", user_id=None):
    """Use OpenAI to improve design. Fetches HTML+CSS from preview, sends to model, returns new config."""
    user_config = get_user_config_for_api(user_id) if user_id else {}
    openai_key = user_config.get("openai_api_key")
    openrouter_key = user_config.get("openrouter_api_key")
    
    if not openai_key and not openrouter_key:
        raise ValueError("OpenAI or OpenRouter API key not configured in your profile. Add it to use Reskin.")
        
    intensity = (intensity or "bold").lower().strip()
    if intensity not in RESKIN_INTENSITY:
        intensity = "bold"
    intensity_instructions, temperature = RESKIN_INTENSITY[intensity]
    try:
        html_full, css_full = _fetch_article_preview(config, generator)
    except Exception as e:
        raise ValueError(f"Could not fetch preview (is articles-website-generator running?): {e}")
    html_snippet = (html_full or "")[:3500]
    css_snippet = (css_full or "")[:5000]
    if not html_snippet and not css_snippet:
        raise ValueError("Preview returned no HTML or CSS.")
        
    if openrouter_key:
        import openai
        client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)
        ai_model = user_config.get("openrouter_model") or "openai/gpt-4o-mini"
    else:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        ai_model = user_config.get("openai_model") or "gpt-4o-mini"
    prompt = RESKIN_PROMPT_BASE.format(
        intensity_instructions=intensity_instructions,
        html_snippet=html_snippet,
        css_snippet=css_snippet,
        config=json.dumps(config, indent=2),
    )
    resp = client.chat.completions.create(
        model=ai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    text = (resp.choices[0].message.content or "").strip()
    # Extract JSON from response (may be wrapped in ```json ... ```)
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    text = text.strip()
    try:
        improved = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAI returned invalid JSON: {e}")
    # Deep-merge improved over original so we never lose keys; structure preserved
    merged = _deep_merge_config(config, improved)
    _enforce_pinterest_pin_color(merged)
    return merged


@app.route("/api/article-template-reskin", methods=["POST"])
def api_article_template_reskin():
    """Improve article template design via OpenAI. Fetches HTML+CSS from preview, sends to model, returns new config."""
    data = request.get_json(silent=True) or {}
    config = data.get("config")
    generator = (data.get("generator") or "generator-1").strip()
    intensity = (data.get("intensity") or "bold").strip().lower()
    if intensity not in ("subtle", "bold", "complete"):
        intensity = "bold"
    if not config or not isinstance(config, dict):
        return jsonify({"success": False, "error": "config (object) required in body"}), 400
    # Build full config for preview (needs title, categories)
    full_cfg = dict(config)
    if "title" not in full_cfg or not full_cfg.get("title"):
        full_cfg["title"] = "Sample Recipe Title"
    if "categories_list" not in full_cfg or not isinstance(full_cfg.get("categories_list"), list):
        full_cfg["categories_list"] = [{"id": 1, "categorie": "dessert"}]
    strip_keys = ("title", "categories_list", "structure_template", "images")
    cfg = {k: v for k, v in full_cfg.items() if k not in strip_keys}
    if not cfg:
        return jsonify({"success": False, "error": "Config has no design fields (colors, fonts, layout, components)"}), 400
        
    user = get_current_user()
    user_id = user["id"] if user else 1
        
    try:
        improved = _reskin_article_template_config(full_cfg, generator, intensity, user_id=user_id)
        return jsonify({"success": True, "config": improved})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        log.exception("Reskin failed")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/article-template-preview-upload", methods=["POST"])
def api_article_template_preview_upload():
    """Upload article template preview screenshot to Cloudflare R2; save URL to domain. Body: { domain_id, image_base64 }."""
    import base64
    data = request.get_json(silent=True) or {}
    domain_id = data.get("domain_id")
    b64 = data.get("image_base64") or ""
    if not domain_id or not b64:
        return jsonify({"success": False, "error": "domain_id and image_base64 required"}), 400
    domain_id = int(domain_id)
    if isinstance(b64, str) and "base64," in b64:
        b64 = b64.split("base64,", 1)[-1].strip()
    try:
        png_bytes = base64.b64decode(b64)
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid base64: " + str(e)}), 400
    if len(png_bytes) < 100:
        return jsonify({"success": False, "error": "Image too small"}), 400
    try:
        import r2_upload
        user = get_current_user()
        user_config = get_user_config_for_api(user["id"]) if user else {}
        url = r2_upload.upload_bytes_to_r2(png_bytes, "article_template_preview", "image/png", user_config=user_config)
    except Exception as e:
        log.warning("[article-template-preview-upload] R2 upload failed: %s", e)
        return jsonify({"success": False, "error": "Upload failed: " + str(e), "hint": "Check R2 config in .env"}), 500
    with get_connection() as conn:
        db_execute(conn, "UPDATE domains SET article_template_preview_url = ? WHERE id = ?", (url, domain_id))
    return jsonify({"success": True, "preview_url": url, "domain_id": domain_id})


@app.route("/admin/domains/edit/<int:pk>", methods=["GET", "POST"])
def admin_domains_edit(pk):
    group_id = request.args.get("group_id") or request.form.get("group_id")
    
    if request.method == "POST":
        template = request.form.get("website_template", "").strip()
        categories_list = request.form.get("categories_list", "").strip()
        domain_colors = request.form.get("domain_colors", "").strip()
        with get_connection() as conn:
            db_execute(conn, "UPDATE domains SET website_template = ?, categories_list = ?, domain_colors = ? WHERE id = ?", (template or None, categories_list or None, domain_colors or None, pk))
        
        redirect_url = url_for("admin_domains")
        if group_id:
            redirect_url += f"?group_id={group_id}"
        return redirect(redirect_url)
    
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT id, domain_url, domain_name, website_template, categories_list, domain_colors FROM domains WHERE id = ?", (pk,))
        d = dict_row(cur.fetchone())
    if not d:
        redirect_url = url_for("admin_domains")
        if group_id:
            redirect_url += f"?group_id={group_id}"
        return redirect(redirect_url)
    example_categories = '[{"id": 1, "categorie": "dessert"}]'
    example_colors = '{"primary": "#6C8AE4", "secondary": "#9C6ADE", "background": "#FFFFFF", "text_primary": "#2D2D2D", "text_secondary": "#5A5A5A", "border": "#E2E8FF"}'
    original_template = (d.get("website_template") or "").strip()
    content = f"""
    <h2>Edit Domain</h2>
    <p><strong>{html.escape(d.get("domain_url") or "")}</strong></p>
    <form method="post" class="mb-3" id="editDomainForm" data-original-template="{html.escape(original_template)}">
      <div class="mb-2">
        <label class="form-label">domain_colors (JSON — primary, secondary, background, text_primary, text_secondary, border)</label>
        <textarea name="domain_colors" class="form-control font-monospace" rows="4" placeholder="{html.escape(example_colors)}">{html.escape(d.get("domain_colors") or "")}</textarea>
        <div class="form-text">Used by header, footer, sidebar, category, and articles. Hex values e.g. #6C8AE4.</div>
      </div>
      <div class="mb-2">
        <label class="form-label">website_template (generator name for Article A, e.g. generator-1)</label>
        <input name="website_template" id="website_template" class="form-control" value="{html.escape(d.get("website_template") or "")}" placeholder="generator-1">
        <div class="form-text text-warning" id="generatorChangeWarning" style="display:none;">Changing the generator requires rewriting articles for this domain because the article structure is different.</div>
      </div>
      <div class="mb-2">
        <label class="form-label">categories_list (JSON array, e.g. {html.escape(example_categories)})</label>
        <textarea name="categories_list" class="form-control font-monospace" rows="3" placeholder="{html.escape(example_categories)}">{html.escape(d.get("categories_list") or "")}</textarea>
      </div>
      <p class="mb-2"><a href="/article-editor?domain_id={pk}" target="_blank" class="btn btn-outline-primary">Open Article Editor</a> — Edit article template (colors, fonts, layout) and save config to this domain.</p>
      <p class="mb-2"><a href="/article-snippet-editor?domain_id={pk}" target="_blank" class="btn btn-outline-secondary">Open Snippet Editor</a> — Add scripts, ads, HTML per section; bulk apply to all articles.</p>
      <button type="submit" class="btn btn-primary mt-2">Save</button>
      <a href="/admin/domains" class="btn btn-secondary mt-2">Cancel</a>
    </form>
    <script>
      document.getElementById('editDomainForm').addEventListener('submit', function(e) {{
        var orig = (this.dataset.originalTemplate || '').trim();
        var newVal = (document.getElementById('website_template').value || '').trim();
        if (orig !== newVal) {{
          if (!confirm('Changing the generator will require rewriting articles for this domain because the article structure is different. Do you want to continue?')) {{
            e.preventDefault();
          }}
        }}
      }});
      document.getElementById('website_template').addEventListener('change', function() {{
        var orig = (document.getElementById('editDomainForm').dataset.originalTemplate || '').trim();
        var newVal = (this.value || '').trim();
        document.getElementById('generatorChangeWarning').style.display = (orig !== newVal) ? 'block' : 'none';
      }});
    </script>
    """
    return base_layout(content, "Edit Domain")


@app.route("/admin/domains/delete/<int:pk>")
def admin_domains_delete(pk):
    # Get group_id from query parameter or referrer to redirect back to the same page
    group_id = request.args.get("group_id")
    
    with get_connection() as conn:
        # If no group_id in query, try to get it from the domain being deleted
        if not group_id:
            cur = db_execute(conn, "SELECT group_id FROM domains WHERE id = ?", (pk,))
            row = dict_row(cur.fetchone())
            if row and row.get("group_id"):
                # Get the top-level parent group
                current_group_id = row["group_id"]
                visited = set()
                while current_group_id and current_group_id not in visited:
                    visited.add(current_group_id)
                    cur = db_execute(conn, "SELECT parent_group_id FROM `groups` WHERE id = ?", (current_group_id,))
                    parent_row = dict_row(cur.fetchone())
                    if parent_row and parent_row.get("parent_group_id"):
                        current_group_id = parent_row["parent_group_id"]
                    else:
                        group_id = current_group_id
                        break
        
        db_execute(conn, "DELETE FROM domains WHERE id = ?", (pk,))
    
    redirect_url = url_for("admin_domains")
    if group_id:
        redirect_url += f"?group_id={group_id}"
    return redirect(redirect_url)


# --- Admin: Titles ---
@app.route("/admin/titles")
@login_required
def admin_titles():
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)
    
    # Get user's accessible domain and group IDs
    user_domain_ids = get_user_domain_ids(user_id, is_admin)
    user_group_ids = get_user_group_ids(user_id, is_admin)
    
    with get_connection() as conn:
        # Filter titles by user's domains
        if not is_admin and user_domain_ids:
            placeholders = ",".join(["?"] * len(user_domain_ids))
            cur = db_execute(conn, f"""
                SELECT t.*, d.domain_url, d.domain_name, g.name as group_name
                FROM titles t
                LEFT JOIN domains d ON t.domain_id = d.id
                LEFT JOIN `groups` g ON t.group_id = g.id
                WHERE t.domain_id IN ({placeholders})
                ORDER BY t.id
            """, tuple(user_domain_ids))
        else:
            cur = db_execute(conn, """
                SELECT t.*, d.domain_url, d.domain_name, g.name as group_name
                FROM titles t
                LEFT JOIN domains d ON t.domain_id = d.id
                LEFT JOIN `groups` g ON t.group_id = g.id
                ORDER BY t.id
            """)
        titles = [dict_row(r) for r in cur.fetchall()]
        
        # Filter domains by user
        if not is_admin and user_domain_ids:
            placeholders = ",".join(["?"] * len(user_domain_ids))
            cur = db_execute(conn, f"SELECT * FROM domains WHERE id IN ({placeholders}) ORDER BY id", tuple(user_domain_ids))
        else:
            cur = db_execute(conn, "SELECT * FROM domains ORDER BY id")
        domains = [dict_row(r) for r in cur.fetchall()]
        
        # Filter groups by user
        if not is_admin and user_group_ids:
            placeholders = ",".join(["?"] * len(user_group_ids))
            cur = db_execute(conn, f"SELECT id, name, parent_group_id FROM `groups` WHERE id IN ({placeholders}) ORDER BY id", tuple(user_group_ids))
        else:
            cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` ORDER BY id")
        groups = [dict_row(r) for r in cur.fetchall()]
        
        # Build complete hierarchy for each group
        def build_group_hierarchy(gid):
            if not gid:
                return None
            path = []
            current = gid
            visited = set()
            while current and current not in visited:
                visited.add(current)
                g = next((x for x in groups if x["id"] == current), None)
                if g:
                    path.insert(0, g["name"])
                    current = g.get("parent_group_id")
                else:
                    break
            return " > ".join(path) if path else None
        
        # Add hierarchy to each group
        for g in groups:
            g["hierarchy"] = build_group_hierarchy(g["id"])
    
    rows_html = "".join(
        f'<tr><td>{t["id"]}</td><td>{t["title"]}</td><td>{t.get("domain_url") or t.get("domain_name") or "-"}</td><td>{t.get("group_name") or "-"}</td>'
        f'<td><a href="/admin/titles/delete/{t["id"]}" class="btn btn-sm btn-danger">Delete</a></td></tr>'
        for t in titles
    )
    dom_opts = "".join(f'<option value="{d["id"]}">{(d.get("domain_url") or d.get("domain_name") or d["id"])}</option>' for d in domains)
    grp_opts = "".join(f'<option value="{g["id"]}">{g.get("hierarchy") or g["name"]}</option>' for g in groups)
    # Build domain→group mapping for autocomplete with hierarchy
    import json as _json
    domain_group_map = []
    for d in domains:
        dom_label = d.get("domain_url") or d.get("domain_name") or str(d["id"])
        dom_gid = d.get("group_id")
        if dom_gid:
            g = next((x for x in groups if x["id"] == dom_gid), None)
            if g:
                domain_group_map.append({
                    "label": dom_label, 
                    "group_id": int(dom_gid), 
                    "group_name": g.get("hierarchy") or g["name"]
                })
    domain_group_json = _json.dumps(domain_group_map)
    
    # Build group options with hierarchy and domain info
    group_domains_str = {}
    for d in domain_group_map:
        gid = d["group_id"]
        group_domains_str.setdefault(gid, []).append(d["label"])
    
    dist_grp_opts = ""
    for g in groups:
        gid = g["id"]
        hierarchy = g.get("hierarchy") or g["name"]
        doms = group_domains_str.get(gid, [])
        if doms:
            doms_str = " - ".join(doms[:3])
            if len(doms) > 3:
                doms_str += f" +{len(doms)-3} more"
            dist_grp_opts += f'<option value="{gid}">{hierarchy} ({doms_str})</option>'
        else:
            dist_grp_opts += f'<option value="{gid}">{hierarchy}</option>'
    content = f"""
    <h2>Titles</h2>


    <div class="card mb-3">
      <div class="card-header">🔗🔄 Distribute Titles to Groups</div>
      <div class="card-body">
        <div class="alert alert-info small mb-3">
          <strong>📁 Parent Group Selected:</strong> Distributes titles to <strong>all subgroups</strong> (and their domains) recursively. Round-robin across subgroups.
          <br><strong>🌐 Single Group Selected:</strong> All titles go to that group's 4 domains (A, B, C, D).
          <br><strong>⚡ All Groups:</strong> Round-robin distribution across all groups in the system.
        </div>
        <form method="post" action="/admin/titles/distribute">
          <div class="mb-3 position-relative">
            <label class="form-label fw-bold">🔍 Select Group or Find by Domain</label>
            <input type="hidden" name="group_id" id="hiddenGroupId" value="">
            <input type="text" id="comboSearch" class="form-control" placeholder="-- All Groups (round-robin) --  (Click to change)" autocomplete="off">
            <div id="comboDropdown" class="dropdown-menu w-100 shadow-sm" style="max-height: 300px; overflow-y: auto; display: none; position: absolute; top: 100%; left: 0; z-index: 1000;"></div>
            <div class="form-text" id="comboHint">No group selected — titles will round-robin across all groups</div>
          </div>
          <div class="mb-2">
            <label class="form-label fw-bold">Titles (one per line)</label>
            <textarea name="titles" class="form-control" rows="5" placeholder="Creamy Garlic Butter Chicken Skillet&#10;One-Pot Spicy Tomato Pasta&#10;..."></textarea>
          </div>
          <button type="submit" class="btn btn-primary">Distribute (A B C D)</button>
        </form>
      </div>
    </div>
    <script>
    (function(){{
      var domainMap = {domain_group_json};
      var theInput = document.getElementById('comboSearch');
      var hiddenInput = document.getElementById('hiddenGroupId');
      var dropDiv = document.getElementById('comboDropdown');
      var hintDiv = document.getElementById('comboHint');

      // Create a master list of groups
      // We'll extract unique groups from domainMap
      var groups = [];
      var seenGid = {{}};
      domainMap.forEach(function(m) {{
          if(!seenGid[m.group_id]) {{
              seenGid[m.group_id] = {{ id: m.group_id, name: m.group_name, domains: [] }};
              groups.push(seenGid[m.group_id]);
          }}
          seenGid[m.group_id].domains.push(m.label);
      }});

      function highlightMatch(text, query) {{
        if(!query) return text;
        var idx = text.toLowerCase().indexOf(query.toLowerCase());
        if(idx < 0) return text;
        return text.substring(0, idx) + '<mark style="background:#fff3cd;padding:0;font-weight:bold;">' + text.substring(idx, idx + query.length) + '</mark>' + text.substring(idx + query.length);
      }}
      
      function renderDropdown(query) {{
          var html = '';
          var q = (query || '').trim().toLowerCase();
          
          // Always show "All Groups" if query is empty or matches
          if(!q || "all groups".indexOf(q) >= 0 || "round robin".indexOf(q) >= 0) {{
              html += '<a class="dropdown-item border-bottom py-2 bg-light" href="javascript:void(0)" data-gid="" data-label="-- All Groups (round-robin) --">'
                   + '<strong>-- All Groups (round-robin) --</strong></a>';
          }}
          
          groups.forEach(function(g) {{
              // check if group name matches
              var gMatch = !q || g.name.toLowerCase().indexOf(q) >= 0;
              // check if any domains match
              var dMatches = !q ? g.domains : g.domains.filter(function(d){{ return d.toLowerCase().indexOf(q) >= 0; }});
              
              if(gMatch || dMatches.length > 0) {{
                  var dispName = gMatch ? highlightMatch(g.name, q) : g.name;
                  var domStr = dMatches.map(function(d){{ return highlightMatch(d, q); }}).join(' - ');
                  if(!domStr && g.domains.length > 0) {{
                      // if group matched but no specific domain matched, just show max 3 domains for context
                      domStr = g.domains.slice(0, 3).join(' - ') + (g.domains.length > 3 ? '...' : '');
                  }}
                  
                  html += '<a class="dropdown-item py-2" style="white-space:normal;" href="javascript:void(0)" '
                       + 'data-gid="' + g.id + '" data-label="' + g.name + '">'
                       + '<strong>' + dispName + '</strong>'
                       + (domStr ? '<br><small class="text-muted">' + domStr + '</small>' : '')
                       + '</a>';
              }}
          }});
          
          if(!html) {{
              html = '<div class="dropdown-item text-muted">No groups or domains found</div>';
          }}
          dropDiv.innerHTML = html;
          dropDiv.style.display = 'block';
          
          // Bind clicks
          dropDiv.querySelectorAll('[data-label]').forEach(function(el){{
            el.addEventListener('click', function(e){{
              e.preventDefault();
              var gid = this.getAttribute('data-gid');
              var label = this.getAttribute('data-label');
              
              hiddenInput.value = gid;
              theInput.value = label;
              dropDiv.style.display = 'none';
              
              if(gid) {{
                  hintDiv.innerHTML = '✅ All titles will go to <strong>' + label + '</strong>';
                  hintDiv.style.color = '#198754';
              }} else {{
                  hintDiv.textContent = 'No group selected — titles will round-robin across all groups';
                  hintDiv.style.color = '#6c757d';
              }}
            }});
          }});
      }}

      // Show dropdown on focus
      theInput.addEventListener('focus', function() {{
          renderDropdown(this.value);
      }});

      theInput.addEventListener('input', function(){{
          renderDropdown(this.value);
      }});

      document.addEventListener('click', function(e){{
        if(!theInput.contains(e.target) && !dropDiv.contains(e.target)) {{
          dropDiv.style.display = 'none';
          // if they typed something but didn't select, we should either revert or let it be (but value is still hidden)
          // letting it be is fine, the hidden value dictates the drop
        }}
      }});
    }})();
    </script>
    }})();
    </script>

    <table id="titlesTable" class="table table-bordered table-striped" style="width:100%">
      <thead><tr><th>ID</th><th>Title</th><th>Domain</th><th>Group</th><th>Actions</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    <script>
      $(document).ready(function() {{
          $('#titlesTable').DataTable({{
              "order": [[0, "desc"]],
              "pageLength": 50
          }});
      }});
    </script>
    """
    return base_layout(content, "Admin - Titles")




@app.route("/admin/titles/distribute", methods=["POST"])
def admin_titles_distribute():
    titles_text = request.form.get("titles", "")
    selected_group = request.form.get("group_id") or None
    titles = [t.strip() for t in titles_text.splitlines() if t.strip()]
    
    # Determine redirect URL based on where the request came from
    redirect_url = url_for("admin_titles")
    if selected_group:
        redirect_url = url_for("admin_domains") + f"?group_id={selected_group}"
    
    if not titles:
        return redirect(redirect_url)
    
    with get_connection() as conn:
        if selected_group:
            # Specific group selected — get all descendant groups recursively + their domains
            grp = int(selected_group)
            
            # Get all descendant groups (including selected group itself)
            def get_all_group_descendants(gid):
                result = [gid]
                cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
                children = [dict_row(r)["id"] for r in cur.fetchall()]
                for child_id in children:
                    result.extend(get_all_group_descendants(child_id))
                return result
            
            all_group_ids = get_all_group_descendants(grp)
            
            # Get all domains from these groups
            if all_group_ids:
                placeholders = ",".join(["?"] * len(all_group_ids))
                cur = db_execute(conn, f"SELECT id, group_id FROM domains WHERE group_id IN ({placeholders}) ORDER BY group_id, domain_index, id", tuple(all_group_ids))
                domain_rows = [dict_row(r) for r in cur.fetchall()]
            else:
                domain_rows = []
            
            if not domain_rows:
                return redirect(redirect_url)
            
            # Group domains by their group_id (each subgroup can have 1-4 domains)
            group_domains_map = {}
            for dr in domain_rows:
                gid = dr["group_id"]
                group_domains_map.setdefault(gid, []).append(dr["id"])
            
            # Filter to groups that have at least 1 domain
            valid_groups = {gid: doms for gid, doms in group_domains_map.items() if len(doms) >= 1}
            
            if not valid_groups:
                error_msg = f"No domains found in this group or its subgroups."
                return redirect(redirect_url + f"&error={urllib.parse.quote(error_msg)}")
            
            # Distribute titles round-robin across valid subgroups
            # Title 1 → Subgroup 1 (all domains), Title 2 → Subgroup 2 (all domains), etc.
            ordered_gids = sorted(valid_groups.keys())
            titles_distributed = 0
            total_domains = sum(len(doms) for doms in valid_groups.values())
            
            for i, title in enumerate(titles):
                target_gid = ordered_gids[i % len(ordered_gids)]
                for domain_id in valid_groups[target_gid]:
                    cur = db_execute(conn, "INSERT INTO titles (title, domain_id, group_id) VALUES (?, ?, ?)", (title, domain_id, target_gid))
                    tid = last_insert_id(cur)
                    if tid:
                        db_execute(conn, "INSERT INTO article_content (title_id, language_code) VALUES (?, 'en')", (tid,))
                titles_distributed += 1
            
            success_msg = f"Successfully distributed {titles_distributed} titles to {len(valid_groups)} subgroups ({total_domains} total domains)"
            return redirect(redirect_url + f"&success={urllib.parse.quote(success_msg)}")
        else:
            # No group selected — round-robin across all groups
            cur = db_execute(conn, "SELECT id FROM `groups` ORDER BY id")
            groups = [(r.get("id") if isinstance(r, dict) else r[0]) for r in cur.fetchall()]
            if not groups:
                return redirect(redirect_url)
            group_domains = {}
            for gid in groups:
                cur = db_execute(conn, "SELECT id FROM domains WHERE group_id = ? ORDER BY domain_index", (gid,))
                gdoms = [(r.get("id") if isinstance(r, dict) else r[0]) for r in cur.fetchall()]
                if len(gdoms) == 4:
                    group_domains[gid] = gdoms
            if not group_domains:
                return redirect(redirect_url)
            ordered_gids = [g for g in groups if g in group_domains]
            for i, title in enumerate(titles):
                gid = ordered_gids[i % len(ordered_gids)]
                for domain_id in group_domains[gid]:
                    cur = db_execute(conn, "INSERT INTO titles (title, domain_id, group_id) VALUES (?, ?, ?)", (title, domain_id, gid))
                    tid = last_insert_id(cur)
                    if tid:
                        db_execute(conn, "INSERT INTO article_content (title_id, language_code) VALUES (?, 'en')", (tid,))
    return redirect(redirect_url)


@app.route("/admin/titles/delete/<int:pk>")
def admin_titles_delete(pk):
    with get_connection() as conn:
        # Delete dependent rows first to satisfy MySQL FK constraints.
        # We discover FK children dynamically (safer across schema versions).
        try:
            cur = db_execute(conn, """
                SELECT TABLE_NAME AS table_name, COLUMN_NAME AS column_name
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE REFERENCED_TABLE_SCHEMA = DATABASE()
                  AND REFERENCED_TABLE_NAME = 'titles'
                  AND REFERENCED_COLUMN_NAME = 'id'
            """)
            fk_rows = cur.fetchall() or []
        except Exception:
            fk_rows = []

        import re
        ident_re = re.compile(r"^[A-Za-z0-9_]+$")

        for r in fk_rows:
            t = (r.get("table_name") if isinstance(r, dict) else None) or ""
            c = (r.get("column_name") if isinstance(r, dict) else None) or ""
            if not ident_re.match(t) or not ident_re.match(c):
                continue
            if t.lower() == "titles":
                continue
            try:
                db_execute(conn, f"DELETE FROM `{t}` WHERE `{c}` = ?", (pk,))
            except Exception:
                # If any child table delete fails, keep going and let the final title delete raise
                pass

        # Common soft-links (not necessarily FKs) we also clean up.
        try:
            db_execute(conn, "DELETE FROM app_logs WHERE title_id = ?", (pk,))
        except Exception:
            pass

        # Fallback for old schemas where information_schema is unavailable
        try:
            db_execute(conn, "DELETE FROM article_content WHERE title_id = ?", (pk,))
        except Exception:
            pass

        db_execute(conn, "DELETE FROM titles WHERE id = ?", (pk,))
    return redirect(url_for("admin_titles"))


# --- Admin: Groups ---
@app.route("/admin/groups")
@login_required
def admin_groups():
    user = get_current_user()
    user_id = user["id"]
    is_admin = bool(user.get("is_admin", 0))
    
    # Get user's accessible group IDs
    user_group_ids = get_user_group_ids(user_id, is_admin)
    
    parent_id = request.args.get("parent_id")
    parent_id = int(parent_id) if parent_id and parent_id.isdigit() else None
    search = (request.args.get("search") or "").strip()
    
    with get_connection() as conn:
        # Get current group info (if viewing a parent)
        parent_group = None
        breadcrumbs = []
        if parent_id:
            cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` WHERE id = ?", (parent_id,))
            parent_group = dict_row(cur.fetchone())
            if parent_group:
                # Build breadcrumb trail
                breadcrumbs = [{"id": parent_group["id"], "name": parent_group["name"]}]
                current_parent = parent_group.get("parent_group_id")
                while current_parent:
                    cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` WHERE id = ?", (current_parent,))
                    pg = dict_row(cur.fetchone())
                    if pg:
                        breadcrumbs.insert(0, {"id": pg["id"], "name": pg["name"]})
                        current_parent = pg.get("parent_group_id")
                    else:
                        break
        
        # Query groups (filtered by parent or search)
        # Build user group filter
        user_group_filter = ""
        user_group_params = []
        if not is_admin:
            if user_group_ids:
                user_group_placeholders = ",".join(["?"] * len(user_group_ids))
                user_group_filter = f" AND g.id IN ({user_group_placeholders})"
                user_group_params = user_group_ids
            else:
                # User has no groups - show nothing
                user_group_filter = " AND g.id = -1"
                user_group_params = []
        
        if search:
            # Search mode: find groups by name or domains by name
            cur = db_execute(conn, f"""
                SELECT DISTINCT g.id, g.name, g.parent_group_id,
                    (SELECT COUNT(*) FROM `groups` WHERE parent_group_id = g.id) as child_groups_count,
                    (SELECT COUNT(*) FROM domains WHERE group_id = g.id) as domains_count
                FROM `groups` g
                LEFT JOIN domains d ON d.group_id = g.id
                WHERE (g.name LIKE ? OR d.domain_url LIKE ? OR d.domain_name LIKE ?){user_group_filter}
                ORDER BY g.id
            """, (f"%{search}%", f"%{search}%", f"%{search}%") + tuple(user_group_params))
        else:
            # Normal mode: show groups under parent_id
            parent_filter = "g.parent_group_id = ?" if parent_id else "g.parent_group_id IS NULL"
            params = (parent_id,) if parent_id else ()
            cur = db_execute(conn, f"""
                SELECT g.id, g.name, g.parent_group_id,
                    (SELECT COUNT(*) FROM `groups` WHERE parent_group_id = g.id) as child_groups_count,
                    (SELECT COUNT(*) FROM domains WHERE group_id = g.id) as domains_count
                FROM `groups` g
                WHERE {parent_filter}{user_group_filter}
                ORDER BY g.id
            """, params + tuple(user_group_params))
        groups = [dict_row(r) for r in cur.fetchall()]
        
        # Get all groups for parent selector (filtered by user)
        if not is_admin:
            if user_group_ids:
                placeholders = ",".join(["?"] * len(user_group_ids))
                cur = db_execute(conn, f"SELECT id, name, parent_group_id FROM `groups` WHERE id IN ({placeholders}) ORDER BY name", tuple(user_group_ids))
                all_groups = [dict_row(r) for r in cur.fetchall()]
            else:
                all_groups = []
        else:
            cur = db_execute(conn, "SELECT id, name, parent_group_id FROM `groups` ORDER BY name")
            all_groups = [dict_row(r) for r in cur.fetchall()]
        
        # Get domains for domain selector (filtered by user)
        user_domain_ids = get_user_domain_ids(user_id, is_admin)
        if not is_admin:
            if user_domain_ids:
                placeholders = ",".join(["?"] * len(user_domain_ids))
                cur = db_execute(conn, f"SELECT id, domain_url, domain_name, group_id FROM domains WHERE id IN ({placeholders}) ORDER BY id", tuple(user_domain_ids))
                domains = [dict_row(r) for r in cur.fetchall()]
            else:
                domains = []
        else:
            cur = db_execute(conn, "SELECT id, domain_url, domain_name, group_id FROM domains ORDER BY id")
            domains = [dict_row(r) for r in cur.fetchall()]
    
    # Build breadcrumb HTML
    breadcrumb_html = '<nav aria-label="breadcrumb"><ol class="breadcrumb mb-3">'
    breadcrumb_html += '<li class="breadcrumb-item"><a href="/admin/groups">All Groups</a></li>'
    for bc in breadcrumbs:
        breadcrumb_html += f'<li class="breadcrumb-item"><a href="/admin/groups?parent_id={bc["id"]}">{bc["name"]}</a></li>'
    if parent_group:
        breadcrumb_html += f'<li class="breadcrumb-item active">{parent_group["name"]}</li>'
    breadcrumb_html += '</ol></nav>'
    
    # Build group options (exclude self and descendants to prevent circular refs)
    def get_descendants(gid, all_grps):
        desc = {gid}
        for g in all_grps:
            if g.get("parent_group_id") in desc:
                desc.add(g["id"])
        return desc
    
    excluded = get_descendants(parent_id, all_groups) if parent_id else set()
    group_opts = '<option value="">-- No Parent (Top Level) --</option>'
    for g in all_groups:
        if g["id"] not in excluded:
            indent = ""
            if g.get("parent_group_id"):
                indent = "→ "
            group_opts += f'<option value="{g["id"]}">{indent}{g["name"]}</option>'
    
    # Build domain options
    dom_opts = "".join(
        f'<option value="{d["id"]}" {"disabled" if d.get("group_id") else ""}>'
        f'{d.get("domain_url") or d.get("domain_name") or d["id"]}'
        f'{" (in group)" if d.get("group_id") else ""}</option>'
        for d in domains
    )
    
    # Build rows HTML with tree structure
    rows_html = ""
    for g in groups:
        child_count = g.get("child_groups_count") or 0
        dom_count = g.get("domains_count") or 0
        gname_esc = g["name"].replace("'", "&apos;")
        
        # Name column: clicking group name goes to domains page, badges for subgroups
        name_html = f'<div class="d-flex align-items-center gap-2">'
        name_html += f'<a href="/admin/domains?group_id={g["id"]}" class="fw-medium text-decoration-none">{g["name"]}</a>'
        if child_count > 0:
            name_html += f'<a href="/admin/groups?parent_id={g["id"]}" class="badge bg-secondary text-decoration-none" title="View subgroups">📁 {child_count}</a>'
        if dom_count > 0:
            name_html += f'<span class="badge bg-primary" title="Total domains">{dom_count}</span>'
        name_html += '</div>'
        
        info = []
        if child_count > 0:
            info.append(f'{child_count} subgroup(s)')
        if dom_count > 0:
            info.append(f'{dom_count} domain(s)')
        info_str = " · ".join(info) if info else "—"
        
        rows_html += f'<tr><td>{g["id"]}</td><td>{name_html}</td><td class="small text-muted">{info_str}</td>'
        rows_html += f'<td><button type="button" class="btn btn-sm btn-warning" onclick="editGroup({g["id"]}, \'{gname_esc}\', {g.get("parent_group_id") or "null"})">Edit</button> '
        rows_html += f'<a href="/admin/groups/delete/{g["id"]}" class="btn btn-sm btn-danger" onclick="return confirm(\'Delete group {g["id"]}?\')">Delete</a></td></tr>'
    
    search_val = search.replace('"', '&quot;') if search else ""
    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h2 class="mb-0">Groups Hierarchy</h2>
      <div class="d-flex gap-2">
        <button type="button" class="btn btn-outline-danger btn-sm" onclick="clearAllGroupsAndDomains()" title="Delete all groups and their domains">🗑️ Clear All Groups & Domains</button>
      </div>
    </div>
    {breadcrumb_html if parent_id else ""}
    <div class="mb-3 d-flex gap-2 align-items-center position-relative">
      <div class="position-relative" style="max-width:300px;flex:1">
        <input type="text" id="groupSearch" class="form-control" placeholder="Search groups or domains..." value="{search_val}" autocomplete="off">
        <div id="groupSearchSuggestions" class="position-absolute w-100 bg-white border rounded shadow-sm" style="display:none;max-height:300px;overflow-y:auto;z-index:1000;top:100%;margin-top:2px"></div>
      </div>
      <button type="button" class="btn btn-primary" onclick="searchGroups()">Search</button>
      <button type="button" class="btn btn-secondary" onclick="window.location.href='/admin/groups'">Clear</button>
    </div>
    <div class="mb-3">
      <button type="button" class="btn btn-success" onclick="showAddGroupModal()">+ Add Group</button>
      <button type="button" class="btn btn-info" onclick="showAssignDomainModal()">+ Assign Domain to Group</button>
    </div>
    <table class="table table-bordered table-hover">
      <thead><tr><th style="width:80px">ID</th><th>Name</th><th>Info</th><th style="width:200px">Actions</th></tr></thead>
      <tbody>{rows_html if rows_html else '<tr><td colspan="4" class="text-center text-muted">No groups found</td></tr>'}</tbody>
    </table>
    
    <div id="addGroupModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="addGroupModalTitle">Add Group</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form method="post" action="/admin/groups/add" id="addGroupForm">
            <div class="modal-body">
              <input type="hidden" name="parent_id" value="{parent_id or ''}">
              <input type="hidden" id="editGroupId" name="edit_id">
              <div class="mb-3">
                <label class="form-label">Group Name</label>
                <input name="name" id="groupNameInput" class="form-control" placeholder="Enter group name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Parent Group (optional)</label>
                <select name="parent_group_id" id="parentGroupSelect" class="form-select">{group_opts}</select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <div id="assignDomainModal" class="modal fade" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Assign Domain to Group</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form method="post" action="/admin/groups/assign-domain">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Domain</label>
                <select name="domain_id" class="form-select" required>{dom_opts}</select>
              </div>
              <div class="mb-3">
                <label class="form-label">Group</label>
                <select name="group_id" class="form-select" required>
                  <option value="">-- Select Group --</option>
                  {group_opts}
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">Assign</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <script>
    var groupSearchTimer = null;
    var groupSearchCache = null;
    
    function searchGroups() {{
      var val = document.getElementById('groupSearch').value.trim();
      window.location.href = '/admin/groups' + (val ? '?search=' + encodeURIComponent(val) : '');
    }}
    
    function fetchGroupSuggestions(query) {{
      if (!query || query.length < 2) {{
        document.getElementById('groupSearchSuggestions').style.display = 'none';
        return;
      }}
      
      fetch('/api/groups-search-suggestions?q=' + encodeURIComponent(query))
        .then(r => r.json())
        .then(data => {{
          var suggestions = data.suggestions || [];
          var suggestionsDiv = document.getElementById('groupSearchSuggestions');
          
          if (suggestions.length === 0) {{
            suggestionsDiv.style.display = 'none';
            return;
          }}
          
          var html = '';
          suggestions.forEach(function(s) {{
            var icon = s.type === 'group' ? '📁' : '🌐';
            var badge = s.type === 'group' ? '<span class="badge bg-secondary ms-2">Group</span>' : '<span class="badge bg-primary ms-2">Domain</span>';
            var path = s.path ? '<div class="small text-muted">' + s.path + '</div>' : '';
            html += '<div class="p-2 border-bottom suggestion-item" style="cursor:pointer" onclick="selectSuggestion(\\''+s.value.replace(/'/g, "\\\\'")+'\\','+s.group_id+')">';
            html += '<div>' + icon + ' <strong>' + s.label + '</strong>' + badge + '</div>' + path;
            html += '</div>';
          }});
          
          suggestionsDiv.innerHTML = html;
          suggestionsDiv.style.display = 'block';
        }})
        .catch(function() {{
          document.getElementById('groupSearchSuggestions').style.display = 'none';
        }});
    }}
    
    function selectSuggestion(value, groupId) {{
      if (groupId) {{
        window.location.href = '/admin/groups?parent_id=' + groupId;
      }} else {{
        document.getElementById('groupSearch').value = value;
        searchGroups();
      }}
    }}
    
    function showAddGroupModal() {{
      document.getElementById('addGroupModalTitle').textContent = 'Add Group';
      document.getElementById('addGroupForm').action = '/admin/groups/add';
      document.getElementById('editGroupId').value = '';
      document.getElementById('groupNameInput').value = '';
      document.getElementById('parentGroupSelect').value = '{parent_id or ""}';
      new bootstrap.Modal(document.getElementById('addGroupModal')).show();
    }}
    function editGroup(id, name, parentId) {{
      document.getElementById('addGroupModalTitle').textContent = 'Edit Group';
      document.getElementById('addGroupForm').action = '/admin/groups/edit';
      document.getElementById('editGroupId').value = id;
      document.getElementById('groupNameInput').value = name;
      document.getElementById('parentGroupSelect').value = parentId || '';
      new bootstrap.Modal(document.getElementById('addGroupModal')).show();
    }}
    function showAssignDomainModal() {{
      new bootstrap.Modal(document.getElementById('assignDomainModal')).show();
    }}
    
    var searchInput = document.getElementById('groupSearch');
    searchInput.addEventListener('input', function(e) {{
      clearTimeout(groupSearchTimer);
      groupSearchTimer = setTimeout(function() {{
        fetchGroupSuggestions(e.target.value);
      }}, 300);
    }});
    searchInput.addEventListener('keypress', function(e) {{
      if (e.key === 'Enter') {{
        document.getElementById('groupSearchSuggestions').style.display = 'none';
        searchGroups();
      }}
    }});
    searchInput.addEventListener('focus', function() {{
      if (this.value.length >= 2) fetchGroupSuggestions(this.value);
    }});
    document.addEventListener('click', function(e) {{
      if (!e.target.closest('#groupSearch') && !e.target.closest('#groupSearchSuggestions')) {{
        document.getElementById('groupSearchSuggestions').style.display = 'none';
      }}
    }});
    
    function clearAllGroupsAndDomains() {{
      if (!confirm('⚠️ WARNING: This will DELETE all groups and all domains permanently!\\n\\nAre you absolutely sure?')) return;
      if (!confirm('This action CANNOT be undone. All groups and domains will be deleted.\\n\\nContinue?')) return;
      
      if (typeof showGlobalLoading === 'function') showGlobalLoading();
      fetch('/api/groups/delete-all', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }}
      }})
        .then(function(r) {{ return r.json(); }})
        .then(function(data) {{
          if (data.success) {{
            alert('Deleted ' + (data.groups_count || 0) + ' groups and ' + (data.domains_count || 0) + ' domains');
            window.location.href = '/admin/groups';
          }} else {{
            alert(data.error || 'Failed to delete');
          }}
        }})
        .catch(function(err) {{ alert(err.message || 'Network error'); }})
        .finally(function() {{ if (typeof hideGlobalLoading === 'function') hideGlobalLoading(); }});
    }}
    </script>
    <style>
    .suggestion-item:hover {{
      background-color: #f8f9fa;
    }}
    #groupSearchSuggestions {{
      border-top: 2px solid #6C8AE4;
    }}
    </style>
    """
    return base_layout(content, "Admin - Groups")


@app.route("/admin/groups/add", methods=["POST"])
@login_required
def admin_groups_add():
    user = get_current_user()
    user_id = user["id"]
    
    name = request.form.get("name", "").strip()
    parent_group_id = request.form.get("parent_group_id", "").strip()
    parent_group_id = int(parent_group_id) if parent_group_id and parent_group_id.isdigit() else None
    parent_id_return = request.form.get("parent_id", "").strip()
    
    if name:
        with get_connection() as conn:
            # Insert group
            cur = db_execute(conn, "INSERT INTO `groups` (name, parent_group_id) VALUES (?, ?)", (name, parent_group_id))
            
            # Get the new group ID
            new_group_id = last_insert_id(cur)
            
            # Assign group to current user
            try:
                db_execute(conn, "INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)", (user_id, new_group_id))
                log.info(f"[admin_groups_add] Assigned group {new_group_id} to user {user_id}")
            except Exception as e:
                log.warning(f"[admin_groups_add] Could not assign group {new_group_id} to user {user_id}: {e}")
            
            # If this is a subgroup, also assign parent group to user (if not already)
            if parent_group_id:
                try:
                    db_execute(conn, "INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)", (user_id, parent_group_id))
                    log.info(f"[admin_groups_add] Assigned parent group {parent_group_id} to user {user_id}")
                except Exception as e:
                    log.debug(f"[admin_groups_add] Parent group {parent_group_id} already assigned to user {user_id}")
    
    return_url = f"/admin/groups?parent_id={parent_id_return}" if parent_id_return and parent_id_return.isdigit() else "/admin/groups"
    return redirect(return_url)


@app.route("/admin/groups/edit", methods=["POST"])
@login_required
def admin_groups_edit():
    edit_id = request.form.get("edit_id", "").strip()
    name = request.form.get("name", "").strip()
    parent_group_id = request.form.get("parent_group_id", "").strip()
    parent_group_id = int(parent_group_id) if parent_group_id and parent_group_id.isdigit() else None
    
    if edit_id and edit_id.isdigit() and name:
        edit_id = int(edit_id)
        # Prevent circular reference
        if parent_group_id == edit_id:
            return "Cannot set group as its own parent", 400
        
        with get_connection() as conn:
            # Check if parent_group_id would create a cycle
            if parent_group_id:
                cur = db_execute(conn, "SELECT id, parent_group_id FROM `groups`")
                all_groups = [dict_row(r) for r in cur.fetchall()]
                current = parent_group_id
                visited = {edit_id}
                while current:
                    if current in visited:
                        return "Cannot create circular group reference", 400
                    visited.add(current)
                    parent = next((g for g in all_groups if g["id"] == current), None)
                    current = parent.get("parent_group_id") if parent else None
            
            db_execute(conn, "UPDATE `groups` SET name = ?, parent_group_id = ? WHERE id = ?", (name, parent_group_id, edit_id))
    
    return redirect(url_for("admin_groups"))


@app.route("/admin/groups/assign-domain", methods=["POST"])
@login_required
def admin_groups_assign_domain():
    domain_id = request.form.get("domain_id", "").strip()
    group_id = request.form.get("group_id", "").strip()
    
    if domain_id and domain_id.isdigit() and group_id and group_id.isdigit():
        domain_id = int(domain_id)
        group_id = int(group_id)
        
        with get_connection() as conn:
            # Check if domain already in a group
            cur = db_execute(conn, "SELECT group_id FROM domains WHERE id = ?", (domain_id,))
            row = dict_row(cur.fetchone())
            if row and row.get("group_id"):
                return f"Domain is already in group {row['group_id']}. Remove it first.", 400
            
            db_execute(conn, "UPDATE domains SET group_id = ? WHERE id = ?", (group_id, domain_id))
    
    return redirect(url_for("admin_groups"))


@app.route("/api/groups/delete-all", methods=["POST"])
@login_required
def api_groups_delete_all():
    """Delete all groups and all domains (admin only for safety)."""
    user = get_current_user()
    user_id = user["id"]
    is_admin = user.get("is_admin", 0)
    
    if not is_admin:
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    with get_connection() as conn:
        # Count before deletion
        cur = db_execute(conn, "SELECT COUNT(*) as cnt FROM `groups`")
        groups_count = dict_row(cur.fetchone())["cnt"]
        
        cur = db_execute(conn, "SELECT COUNT(*) as cnt FROM domains")
        domains_count = dict_row(cur.fetchone())["cnt"]
        
        # Delete all titles first (FK constraint)
        db_execute(conn, "DELETE FROM titles")
        
        # Delete all article content
        db_execute(conn, "DELETE FROM article_content")
        
        # Delete all domains
        db_execute(conn, "DELETE FROM domains")
        
        # Delete all group assignments
        db_execute(conn, "DELETE FROM user_groups")
        
        # Delete all groups
        db_execute(conn, "DELETE FROM `groups`")
    
    return jsonify({"success": True, "groups_count": groups_count, "domains_count": domains_count})


@app.route("/admin/groups/delete/<int:pk>")
@login_required
def admin_groups_delete(pk):
    """Delete group with all its subgroups, domains, and articles (cascade)."""
    with get_connection() as conn:
        # Get all descendant groups recursively
        def get_all_group_descendants(gid):
            result = [gid]
            cur = db_execute(conn, "SELECT id FROM `groups` WHERE parent_group_id = ?", (gid,))
            children = [dict_row(r)["id"] for r in cur.fetchall()]
            for child_id in children:
                result.extend(get_all_group_descendants(child_id))
            return result
        
        all_group_ids = get_all_group_descendants(pk)
        
        # Get all domains in these groups
        if all_group_ids:
            placeholders = ",".join(["?"] * len(all_group_ids))
            cur = db_execute(conn, f"SELECT id FROM domains WHERE group_id IN ({placeholders})", tuple(all_group_ids))
            domain_ids = [dict_row(r)["id"] for r in cur.fetchall()]
            
            # Delete all titles for these domains (cascade will delete article_content)
            if domain_ids:
                placeholders = ",".join(["?"] * len(domain_ids))
                db_execute(conn, f"DELETE FROM titles WHERE domain_id IN ({placeholders})", tuple(domain_ids))
                
                # Delete all domains
                db_execute(conn, f"DELETE FROM domains WHERE id IN ({placeholders})", tuple(domain_ids))
            
            # Delete all groups (children first, then parent)
            for gid in reversed(all_group_ids):
                db_execute(conn, "DELETE FROM `groups` WHERE id = ?", (gid,))
        
    return redirect(url_for("admin_groups"))


@app.route("/api/groups-search-suggestions")
def api_groups_search_suggestions():
    """Return autocomplete suggestions for groups and domains search."""
    query = (request.args.get("q") or "").strip()
    if not query or len(query) < 2:
        return jsonify({"suggestions": []})
    
    suggestions = []
    with get_connection() as conn:
        # Search groups
        cur = db_execute(conn, """
            SELECT g.id, g.name, g.parent_group_id,
                (SELECT COUNT(*) FROM `groups` WHERE parent_group_id = g.id) as child_count,
                (SELECT COUNT(*) FROM domains WHERE group_id = g.id) as domain_count
            FROM `groups` g
            WHERE g.name LIKE ?
            ORDER BY g.name
            LIMIT 10
        """, (f"%{query}%",))
        groups = [dict_row(r) for r in cur.fetchall()]
        
        # Build group path for each result
        for g in groups:
            path_parts = []
            current_parent = g.get("parent_group_id")
            while current_parent:
                cur = db_execute(conn, "SELECT name, parent_group_id FROM `groups` WHERE id = ?", (current_parent,))
                parent = dict_row(cur.fetchone())
                if parent:
                    path_parts.insert(0, parent["name"])
                    current_parent = parent.get("parent_group_id")
                else:
                    break
            
            path = " > ".join(path_parts) if path_parts else None
            child_count = g.get("child_count") or 0
            domain_count = g.get("domain_count") or 0
            info = []
            if child_count > 0:
                info.append(f"{child_count} subgroups")
            if domain_count > 0:
                info.append(f"{domain_count} domains")
            
            suggestions.append({
                "type": "group",
                "label": g["name"] + (f" ({', '.join(info)})" if info else ""),
                "value": g["name"],
                "group_id": g["id"],
                "path": path
            })
        
        # Search domains
        cur = db_execute(conn, """
            SELECT d.id, d.domain_url, d.domain_name, d.group_id, g.name as group_name
            FROM domains d
            LEFT JOIN `groups` g ON g.id = d.group_id
            WHERE d.domain_url LIKE ? OR d.domain_name LIKE ?
            ORDER BY d.domain_url
            LIMIT 10
        """, (f"%{query}%", f"%{query}%"))
        domains = [dict_row(r) for r in cur.fetchall()]
        
        for d in domains:
            label = d.get("domain_url") or d.get("domain_name") or f"Domain {d['id']}"
            path = None
            if d.get("group_id") and d.get("group_name"):
                path = f"In group: {d['group_name']}"
            
            suggestions.append({
                "type": "domain",
                "label": label,
                "value": label,
                "group_id": d.get("group_id"),
                "path": path
            })
    
    return jsonify({"suggestions": suggestions[:15]})


@app.route("/api/domains-search-suggestions")
def api_domains_search_suggestions():
    """Return autocomplete suggestions for domains search with complete group hierarchy."""
    query = (request.args.get("q") or "").strip()
    if not query or len(query) < 2:
        return jsonify({"suggestions": []})
    
    def build_group_hierarchy(group_id, conn):
        """Build complete group path from root to current group."""
        if not group_id:
            return None
        path_parts = []
        current = group_id
        visited = set()
        while current and current not in visited:
            visited.add(current)
            cur = db_execute(conn, "SELECT name, parent_group_id FROM `groups` WHERE id = ?", (current,))
            g = dict_row(cur.fetchone())
            if g:
                path_parts.insert(0, g["name"])
                current = g.get("parent_group_id")
            else:
                break
        return " > ".join(path_parts) if path_parts else None
    
    suggestions = []
    with get_connection() as conn:
        # Search groups
        cur = db_execute(conn, """
            SELECT g.id, g.name, g.parent_group_id,
                (SELECT COUNT(*) FROM `groups` WHERE parent_group_id = g.id) as child_count,
                (SELECT COUNT(*) FROM domains WHERE group_id = g.id) as domain_count
            FROM `groups` g
            WHERE g.name LIKE ?
            ORDER BY g.name
            LIMIT 8
        """, (f"%{query}%",))
        groups = [dict_row(r) for r in cur.fetchall()]
        
        for g in groups:
            hierarchy = build_group_hierarchy(g.get("parent_group_id"), conn)
            child_count = g.get("child_count") or 0
            domain_count = g.get("domain_count") or 0
            info_parts = []
            if child_count > 0:
                info_parts.append(f"{child_count} subgroups")
            if domain_count > 0:
                info_parts.append(f"{domain_count} domains")
            
            suggestions.append({
                "type": "group",
                "label": g["name"],
                "domain_id": None,
                "group_id": g["id"],
                "group_path": hierarchy,
                "info": ", ".join(info_parts) if info_parts else None
            })
        
        # Search domains with complete group hierarchy
        cur = db_execute(conn, """
            SELECT d.id, d.domain_url, d.domain_name, d.group_id
            FROM domains d
            WHERE d.domain_url LIKE ? OR d.domain_name LIKE ?
            ORDER BY d.domain_url
            LIMIT 12
        """, (f"%{query}%", f"%{query}%"))
        domains = [dict_row(r) for r in cur.fetchall()]
        
        for d in domains:
            label = d.get("domain_url") or d.get("domain_name") or f"Domain {d['id']}"
            hierarchy = build_group_hierarchy(d.get("group_id"), conn) if d.get("group_id") else None
            
            suggestions.append({
                "type": "domain",
                "label": label,
                "domain_id": d["id"],
                "group_id": d.get("group_id"),
                "group_path": hierarchy,
                "info": None
            })
    
    return jsonify({"suggestions": suggestions[:15]})


@app.route("/")
@login_required
def index():
    user = get_current_user()
    if user:
        return redirect(url_for("admin_domains"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            return render_login_page("Username and password required")
        
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id, username, password_hash, is_admin, is_active FROM users WHERE username = ?", (username,))
            user = dict_row(cur.fetchone())
        
        if not user:
            return render_login_page("Invalid username or password")
        
        if not user.get("is_active"):
            return render_login_page("Account is inactive. Contact administrator.")
        
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if user.get("password_hash") != password_hash:
            return render_login_page("Invalid username or password")
        
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["is_admin"] = user.get("is_admin", 0)
        
        next_url = request.args.get("next") or url_for("admin_domains")
        return redirect(next_url)
    
    return render_login_page()


def render_login_page(error=None):
    error_html = f'<div class="alert alert-danger">{html.escape(error)}</div>' if error else ""
    content = f"""
    <div class="container" style="max-width:400px;margin-top:100px">
      <div class="card">
        <div class="card-body">
          <h3 class="card-title text-center mb-4">Login</h3>
          {error_html}
          <form method="post">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input type="text" name="username" class="form-control" required autofocus>
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
          </form>
          <div class="text-center mt-3">
            <a href="/register" class="text-muted small">Create new account</a>
          </div>
        </div>
      </div>
    </div>
    """
    return base_layout(content, "Login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin/users")
@login_required
def admin_users():
    user = get_current_user()
    if not user.get("is_admin"):
        return base_layout("<div class='alert alert-danger'>Admin access required</div>", "Access Denied")
    
    with get_connection() as conn:
        cur = db_execute(conn, """
            SELECT u.id, u.username, u.email, u.is_admin, u.is_active, u.created_at,
                   COUNT(DISTINCT ud.domain_id) as domain_count
            FROM users u
            LEFT JOIN user_domains ud ON ud.user_id = u.id
            GROUP BY u.id
            ORDER BY u.id DESC
        """)
        users = [dict_row(r) for r in cur.fetchall()]
        
        cur = db_execute(conn, "SELECT id, domain_url, domain_name FROM domains ORDER BY domain_name")
        all_domains = [dict_row(r) for r in cur.fetchall()]
    
    users_html = ""
    for u in users:
        status_badge = '<span class="badge bg-success">Active</span>' if u.get("is_active") else '<span class="badge bg-secondary">Inactive</span>'
        admin_badge = '<span class="badge bg-primary">Admin</span>' if u.get("is_admin") else ""
        users_html += f"""
        <tr>
            <td>{u["id"]}</td>
            <td><strong>{html.escape(u["username"])}</strong> {admin_badge} {status_badge}</td>
            <td>{html.escape(u.get("email") or "-")}</td>
            <td>{u.get("domain_count", 0)} domains</td>
            <td>{u.get("created_at", "")}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editUser({u['id']})">Edit</button>
                <button class="btn btn-sm btn-info" onclick="manageDomains({u['id']})">Domains</button>
                <button class="btn btn-sm btn-success" onclick="cloneProfile({u['id']})">Clone Profile</button>
                <button class="btn btn-sm btn-warning" onclick="toggleUserStatus({u['id']}, {1 if not u.get('is_active') else 0})">
                    {'Activate' if not u.get('is_active') else 'Deactivate'}
                </button>
            </td>
        </tr>
        """
    
    domain_options = "".join([f'<option value="{d["id"]}">{html.escape(d["domain_name"])} ({html.escape(d["domain_url"])})</option>' for d in all_domains])
    
    # Prepare users list for clone profile modal
    users_json = json.dumps([{"id": u["id"], "username": u["username"]} for u in users])
    
    content = f"""
    <h2>User Management</h2>
    <p class="text-muted">Manage users and their domain access</p>
    
    <table class="table table-hover">
        <thead>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Domains</th>
                <th>Created</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {users_html}
        </tbody>
    </table>
    
    <!-- Manage Domains Modal -->
    <div class="modal fade" id="manageDomainsModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Manage User Domains</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="userDomainsContent">Loading...</div>
                    <hr>
                    <h6>Add Domain</h6>
                    <form id="addDomainForm">
                        <input type="hidden" id="manageDomainUserId" name="user_id">
                        <div class="mb-3">
                            <select name="domain_id" class="form-select" required>
                                <option value="">-- Select Domain --</option>
                                {domain_options}
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary">Add Domain</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Clone Profile Modal -->
    <div class="modal fade" id="cloneProfileModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Clone Profile to <strong id="targetUsername"></strong></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p class="text-muted small mb-3">Select which user's profile settings to copy to <strong id="targetUsername2"></strong>.</p>
                    <form id="cloneProfileForm">
                        <input type="hidden" id="targetUserId" name="target_user_id">
                        <div class="mb-3">
                            <label class="form-label"><strong>Clone from:</strong> Source User</label>
                            <select name="source_user_id" id="sourceUserSelect" class="form-select" required>
                                <option value="">-- Select Source User --</option>
                            </select>
                            <div class="form-text">Source user must have their profile configured</div>
                        </div>
                        <div class="alert alert-warning small">
                            <strong>⚠️ Warning:</strong> This will copy all API keys and settings (OpenAI, Midjourney, R2, Cloudflare, etc.) to <strong id="targetUsername3"></strong>, overwriting any existing settings.
                        </div>
                        <button type="submit" class="btn btn-success">Clone Profile</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    const allUsers = {users_json};
    
    function editUser(userId) {
        alert("To edit a user's API keys or settings, please log in as that user and visit their /profile page. Admins can currently only activate/deactivate users or manage their domains from this screen.");
    }
    
    function cloneProfile(clickedUserId) {{
        const targetUser = allUsers.find(u => u.id === clickedUserId);
        const targetUsername = targetUser ? targetUser.username : 'User';
        
        // Set target user (the clicked user)
        document.getElementById('targetUserId').value = clickedUserId;
        document.getElementById('targetUsername').textContent = targetUsername;
        document.getElementById('targetUsername2').textContent = targetUsername;
        document.getElementById('targetUsername3').textContent = targetUsername;
        
        // Populate source dropdown with all users except the target
        const sourceSelect = document.getElementById('sourceUserSelect');
        sourceSelect.innerHTML = '<option value="">-- Select Source User --</option>';
        
        allUsers.forEach(u => {{
            if (u.id !== clickedUserId) {{
                const option = document.createElement('option');
                option.value = u.id;
                option.textContent = u.username;
                sourceSelect.appendChild(option);
            }}
        }});
        
        new bootstrap.Modal(document.getElementById('cloneProfileModal')).show();
    }}
    
    function manageDomains(userId) {{
        document.getElementById('manageDomainUserId').value = userId;
        fetch('/api/users/' + userId + '/domains')
            .then(r => r.json())
            .then(data => {{
                let html = '<ul class="list-group">';
                data.domains.forEach(d => {{
                    html += '<li class="list-group-item d-flex justify-content-between align-items-center">' +
                            d.domain_name + ' (' + d.domain_url + ')' +
                            '<button class="btn btn-sm btn-danger" onclick="removeDomain(' + userId + ', ' + d.id + ')">Remove</button>' +
                            '</li>';
                }});
                html += '</ul>';
                document.getElementById('userDomainsContent').innerHTML = html || '<p class="text-muted">No domains assigned</p>';
            }});
        new bootstrap.Modal(document.getElementById('manageDomainsModal')).show();
    }}
    
    function removeDomain(userId, domainId) {{
        if (!confirm('Remove this domain from user?')) return;
        fetch('/api/users/' + userId + '/domains/' + domainId, {{method: 'DELETE'}})
            .then(r => r.json())
            .then(data => {{
                if (data.success) {{
                    manageDomains(userId);
                }} else {{
                    alert(data.error || 'Failed');
                }}
            }});
    }}
    
    function toggleUserStatus(userId, activate) {{
        fetch('/api/users/' + userId + '/status', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{is_active: activate}})
        }})
        .then(r => r.json())
        .then(data => {{
            if (data.success) {{
                location.reload();
            }} else {{
                alert(data.error || 'Failed');
            }}
        }});
    }}
    
    document.getElementById('addDomainForm').addEventListener('submit', function(e) {{
        e.preventDefault();
        const formData = new FormData(this);
        fetch('/api/users/' + formData.get('user_id') + '/domains', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{domain_id: formData.get('domain_id')}})
        }})
        .then(r => r.json())
        .then(data => {{
            if (data.success) {{
                manageDomains(formData.get('user_id'));
                this.reset();
            }} else {{
                alert(data.error || 'Failed');
            }}
        }});
    }});
    
    document.getElementById('cloneProfileForm').addEventListener('submit', function(e) {{
        e.preventDefault();
        const formData = new FormData(this);
        const sourceUserId = formData.get('source_user_id');
        const targetUserId = formData.get('target_user_id');
        
        if (!sourceUserId) {{
            alert('Please select a source user.');
            return;
        }}
        
        const sourceUser = allUsers.find(u => u.id == sourceUserId);
        const sourceUsername = sourceUser ? sourceUser.username : 'User';
        const targetUsername = document.getElementById('targetUsername').textContent;
        
        if (!confirm(`Clone profile settings from "${{sourceUsername}}" to "${{targetUsername}}"?\\n\\nThis will overwrite all existing settings for ${{targetUsername}}.`)) {{
            return;
        }}
        
        fetch('/api/users/clone-profile', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                source_user_id: parseInt(sourceUserId),
                target_user_id: parseInt(targetUserId)
            }})
        }})
        .then(r => r.json())
        .then(data => {{
            if (data.success) {{
                alert(data.message || 'Profile cloned successfully!');
                bootstrap.Modal.getInstance(document.getElementById('cloneProfileModal')).hide();
            }} else {{
                alert(data.error || 'Failed to clone profile');
            }}
        }})
        .catch(err => {{
            alert('Error: ' + err.message);
        }});
    }});
    </script>
    """
    return base_layout(content, "User Management")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    user_id = user["id"]
    
    if request.method == "POST":
        # Update API keys
        with get_connection() as conn:
            # Check if user has API keys record
            cur = db_execute(conn, "SELECT id FROM user_api_keys WHERE user_id = ?", (user_id,))
            exists = cur.fetchone()
            
            keys_data = {
                "openai_api_key": request.form.get("openai_api_key", "").strip() or None,
                "openai_model": request.form.get("openai_model", "").strip() or None,
                "openrouter_api_key": request.form.get("openrouter_api_key", "").strip() or None,
                "openrouter_model": request.form.get("openrouter_model", "").strip() or None,
                "midjourney_api_token": request.form.get("midjourney_api_token", "").strip() or None,
                "midjourney_channel_id": request.form.get("midjourney_channel_id", "").strip() or None,
                "r2_account_id": request.form.get("r2_account_id", "").strip() or None,
                "r2_access_key_id": request.form.get("r2_access_key_id", "").strip() or None,
                "r2_secret_access_key": request.form.get("r2_secret_access_key", "").strip() or None,
                "r2_bucket_name": request.form.get("r2_bucket_name", "").strip() or None,
                "r2_public_url": request.form.get("r2_public_url", "").strip() or None,
                "cloudflare_account_id": request.form.get("cloudflare_account_id", "").strip() or None,
                "cloudflare_api_token": request.form.get("cloudflare_api_token", "").strip() or None,
                "local_api_url": request.form.get("local_api_url", "").strip() or None,
                "local_models": request.form.get("local_models", "").strip() or None,
                "default_categories": request.form.get("default_categories", "").strip() or None,
            }
            
            if exists:
                set_clause = ", ".join(f"{k} = ?" for k in keys_data.keys())
                db_execute(conn, f"UPDATE user_api_keys SET {set_clause} WHERE user_id = ?", 
                          tuple(keys_data.values()) + (user_id,))
            else:
                cols = ", ".join(keys_data.keys())
                placeholders = ", ".join(["?"] * len(keys_data))
                db_execute(conn, f"INSERT INTO user_api_keys (user_id, {cols}) VALUES (?, {placeholders})", 
                          (user_id,) + tuple(keys_data.values()))
        
        return redirect(url_for("profile") + "?saved=1")
    
    # GET - show form
    keys = get_user_api_keys(user_id)
    saved_msg = '<div class="alert alert-success">API keys saved successfully!</div>' if request.args.get("saved") else ""
    error_msg = f'<div class="alert alert-danger">{html.escape(request.args.get("error"))}</div>' if request.args.get("error") else ""
    
    # Check if profile is complete
    profile_complete = is_profile_complete(user_id)
    incomplete_warning = "" if profile_complete else '<div class="alert alert-warning"><strong>⚠️ Profile Incomplete!</strong><br>You must complete all required fields below before you can add domains. OpenRouter and Local (Ollama/LM Studio) settings are optional.</div>'
    
    def field(name, label, placeholder="", type_="text"):
        val = html.escape(str(keys.get(name) or ""))
        placeholder_attr = f'placeholder="{html.escape(placeholder)}"' if placeholder else ''
        return f'''
        <div class="mb-3">
          <label class="form-label">{label}</label>
          <input type="{type_}" name="{name}" class="form-control" {placeholder_attr} value="{val}">
        </div>
        '''
    
    # Default categories value (can't use backslash in f-string)
    default_cats = keys.get('default_categories') or 'Appetizers\nMain Courses\nDesserts\nBeverages\nSalads\nSoups\nSnacks\nBreakfast'
    default_cats_value = html.escape(str(default_cats))
    
    content = f"""
    <h2>User Profile</h2>
    <p><strong>Username:</strong> {html.escape(user['username'])}</p>
    <p><strong>Email:</strong> {html.escape(user.get('email') or '-')}</p>
    
    {incomplete_warning}
    
    <div class="card mb-4" style="max-width:800px">
      <div class="card-header">🔑 API Keys Configuration</div>
      <div class="card-body">
        {error_msg}
        {saved_msg}
        <p class="text-muted small mb-4">Configure your API keys below. These keys are stored securely and used only for your operations. <strong>All fields are required except OpenRouter and Local settings.</strong></p>
        <form method="post">
          <h5 class="mb-3">Default Settings <span class="badge bg-danger">Required</span></h5>
          <div class="mb-3">
            <label class="form-label">Default Categories (one per line)</label>
            <textarea name="default_categories" class="form-control" rows="8" placeholder="Appetizers&#10;Main Courses&#10;Desserts&#10;Beverages&#10;Salads&#10;Soups&#10;Snacks&#10;Breakfast">{default_cats_value}</textarea>
            <div class="form-text">These categories will be automatically assigned to new domains</div>
          </div>
          
          <h5 class="mb-3 mt-4">OpenAI <span class="badge bg-danger">Required</span></h5>
          {field("openai_api_key", "API Key", "sk-proj-xxxxxxxxxxxx")}
          {field("openai_model", "Model", "gpt-4o-mini")}
          
          <h5 class="mb-3 mt-4">Midjourney <span class="badge bg-danger">Required</span></h5>
          {field("midjourney_api_token", "API Token", "user:xxxx-xxxxxxxxxxxxxxx")}
          {field("midjourney_channel_id", "Channel ID", "1464695640058495123")}
          
          <h5 class="mb-3 mt-4">Cloudflare <span class="badge bg-danger">Required</span></h5>
          {field("cloudflare_account_id", "Account ID", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")}
          {field("cloudflare_api_token", "API Token", "••••••••••••••••••••••••••••••••", type_="password")}
          
          <h5 class="mb-3 mt-4">Cloudflare R2 <span class="badge bg-danger">Required</span></h5>
          {field("r2_account_id", "Account ID", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")}
          {field("r2_access_key_id", "Access Key ID", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")}
          {field("r2_secret_access_key", "Secret Access Key", "••••••••••••••••••••••••••••••••", type_="password")}
          {field("r2_bucket_name", "Bucket Name", "my-bucket")}
          {field("r2_public_url", "Public URL", "https://pub-xxxxxxxx.r2.dev")}
          
          <hr class="my-4">
          <h5 class="mb-3 text-muted">Optional Settings</h5>
          
          <h5 class="mb-3 mt-4">OpenRouter <span class="badge bg-secondary">Optional</span></h5>
          {field("openrouter_api_key", "API Key", "sk-or-v1-xxxxxxxxxxxx")}
          {field("openrouter_model", "Default Model", "openai/gpt-oss-120b")}
          
          <h5 class="mb-3 mt-4">Local (Ollama/LM Studio) <span class="badge bg-secondary">Optional</span></h5>
          {field("local_api_url", "API URL", "http://192.168.1.20:11434/api/generate")}
          {field("local_models", "Models (comma-separated)", "qwen3:8b,llama3.2:3b")}
          
          <button type="submit" class="btn btn-primary mt-3">💾 Save Settings</button>
        </form>
      </div>
    </div>
    
    <a href="/logout" class="btn btn-outline-secondary">Logout</a>
    """
    return base_layout(content, "Profile")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()
        
        if not username or not password:
            return render_register_page("Username and password required")
        
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with get_connection() as conn:
            cur = db_execute(conn, "SELECT id FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                return render_register_page("Username already exists")
            
            db_execute(conn, "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", (username, password_hash, email))
        
        return redirect(url_for("login"))
    
    return render_register_page()


def render_register_page(error=None):
    error_html = f'<div class="alert alert-danger">{html.escape(error)}</div>' if error else ""
    content = f"""
    <div class="container" style="max-width:400px;margin-top:100px">
      <div class="card">
        <div class="card-body">
          <h3 class="card-title text-center mb-4">Register</h3>
          {error_html}
          <form method="post">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input type="text" name="username" class="form-control" required autofocus>
            </div>
            <div class="mb-3">
              <label class="form-label">Email (optional)</label>
              <input type="email" name="email" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Register</button>
          </form>
          <div class="text-center mt-3">
            <a href="/login" class="text-muted small">Already have an account? Login</a>
          </div>
        </div>
      </div>
    </div>
    """
    return base_layout(content, "Register")


@app.route("/api/users/<int:user_id>/domains", methods=["GET", "POST"])
@login_required
def api_user_domains(user_id):
    user = get_current_user()
    if not user.get("is_admin"):
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    if request.method == "GET":
        with get_connection() as conn:
            cur = db_execute(conn, """
                SELECT d.id, d.domain_url, d.domain_name
                FROM user_domains ud
                JOIN domains d ON d.id = ud.domain_id
                WHERE ud.user_id = ?
                ORDER BY d.domain_name
            """, (user_id,))
            domains = [dict_row(r) for r in cur.fetchall()]
        return jsonify({"success": True, "domains": domains})
    
    elif request.method == "POST":
        data = request.get_json() or {}
        domain_id = data.get("domain_id")
        if not domain_id:
            return jsonify({"success": False, "error": "domain_id required"}), 400
        
        with get_connection() as conn:
            try:
                db_execute(conn, "INSERT INTO user_domains (user_id, domain_id) VALUES (?, ?)", (user_id, domain_id))
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/users/<int:user_id>/domains/<int:domain_id>", methods=["DELETE"])
@login_required
def api_user_domain_remove(user_id, domain_id):
    user = get_current_user()
    if not user.get("is_admin"):
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    with get_connection() as conn:
        db_execute(conn, "DELETE FROM user_domains WHERE user_id = ? AND domain_id = ?", (user_id, domain_id))
    return jsonify({"success": True})


@app.route("/api/users/<int:user_id>/status", methods=["POST"])
@login_required
def api_user_status(user_id):
    user = get_current_user()
    if not user.get("is_admin"):
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    data = request.get_json() or {}
    is_active = 1 if data.get("is_active") else 0
    
    with get_connection() as conn:
        db_execute(conn, "UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))
    return jsonify({"success": True})


@app.route("/api/users/clone-profile", methods=["POST"])
@login_required
def api_clone_profile():
    user = get_current_user()
    if not user.get("is_admin"):
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    data = request.get_json() or {}
    source_user_id = data.get("source_user_id")
    target_user_id = data.get("target_user_id")
    
    if not source_user_id or not target_user_id:
        return jsonify({"success": False, "error": "source_user_id and target_user_id required"}), 400
    
    if source_user_id == target_user_id:
        return jsonify({"success": False, "error": "Cannot clone to the same user"}), 400
    
    with get_connection() as conn:
        # Get source and target usernames for better error messages
        cur = db_execute(conn, "SELECT id, username FROM users WHERE id IN (?, ?)", (source_user_id, target_user_id))
        users_info = {dict_row(r)["id"]: dict_row(r)["username"] for r in cur.fetchall()}
        
        source_username = users_info.get(source_user_id, f"User {source_user_id}")
        target_username = users_info.get(target_user_id, f"User {target_user_id}")
        
        # Get source user's API keys
        cur = db_execute(conn, "SELECT * FROM user_api_keys WHERE user_id = ?", (source_user_id,))
        source_keys = dict_row(cur.fetchone())
        
        if not source_keys:
            return jsonify({"success": False, "error": f"Source user '{source_username}' has no profile settings configured. Please configure their profile first."}), 400
        
        # Remove id and user_id from source_keys
        source_keys.pop('id', None)
        source_keys.pop('user_id', None)
        
        # Check if target user has existing API keys
        cur = db_execute(conn, "SELECT id FROM user_api_keys WHERE user_id = ?", (target_user_id,))
        target_exists = cur.fetchone()
        
        if target_exists:
            # Update existing record
            set_clause = ", ".join(f"{k} = ?" for k in source_keys.keys())
            db_execute(conn, f"UPDATE user_api_keys SET {set_clause} WHERE user_id = ?", 
                      tuple(source_keys.values()) + (target_user_id,))
        else:
            # Insert new record
            cols = ", ".join(source_keys.keys())
            placeholders = ", ".join(["?"] * len(source_keys))
            db_execute(conn, f"INSERT INTO user_api_keys (user_id, {cols}) VALUES (?, {placeholders})", 
                      (target_user_id,) + tuple(source_keys.values()))
    
    return jsonify({"success": True, "message": f"Profile settings cloned from '{source_username}' to '{target_username}' successfully!"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
