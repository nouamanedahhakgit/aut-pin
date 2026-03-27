"""Database connection and schema. Supports MySQL or Supabase (PostgreSQL) via DB_BACKEND in .env."""
import os
import re
import time
from contextlib import contextmanager

try:
    from dotenv import load_dotenv
    # Load .env from this package directory so it's found when running from repo root
    _env_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(_env_dir, ".env"))
    # Also load from Docker volume mount (orchestrator-generated config)
    _docker_env = "/app/env-config/multi-domain-clean.env"
    if os.path.exists(_docker_env):
        load_dotenv(_docker_env, override=True)
except ImportError:
    pass

# DB_BACKEND: mysql | supabase
DB_BACKEND = os.getenv("DB_BACKEND", "mysql").lower().strip()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "pinterest"),
    "charset": "utf8mb4",
    "autocommit": True,
}

# If running inside Docker, automatically use host.docker.internal if MYSQL_HOST is localhost
if os.path.exists("/.dockerenv") and MYSQL_CONFIG["host"] == "localhost":
    MYSQL_CONFIG["host"] = "host.docker.internal"

# Supabase (PostgreSQL): direct URL. If you get "could not translate host name", use pooler URL instead (see below).
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")
# Optional: use when direct host fails (Dashboard → Project Settings → Database → Connection pooling → Session mode)
SUPABASE_POOLER_URL = os.getenv("SUPABASE_POOLER_URL", "")

# Pre-import cryptography for pymysql
try:
    import cryptography  # noqa: F401
except ImportError:
    pass


def _get_mysql_connection():
    import pymysql
    return pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)


def _get_supabase_connection():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    urls_to_try = [u for u in (SUPABASE_DB_URL, SUPABASE_POOLER_URL) if u and u.strip()]
    if not urls_to_try:
        raise ValueError(
            "DB_BACKEND=supabase requires SUPABASE_DB_URL (or SUPABASE_POOLER_URL) in .env. "
            "If direct host fails, use Connection pooling URL from Dashboard → Database."
        )
    last_error = None
    for url in urls_to_try:
        url = url.strip()
        for attempt in range(3):  # retry transient DNS/network failures
            try:
                return psycopg2.connect(url, cursor_factory=RealDictCursor)
            except Exception as e:
                last_error = e
                err_msg = str(e).lower()
                is_transient = (
                    "could not translate host name" in err_msg
                    or "resolve" in err_msg
                    or "connection refused" in err_msg
                    or "timed out" in err_msg
                )
                if is_transient and attempt < 2:
                    time.sleep(2 + attempt)  # 2s, 3s
                    continue
                if "could not translate host name" in err_msg or "resolve" in err_msg:
                    continue  # try next URL (e.g. direct vs pooler)
                raise
    # Log failure for diagnostics (avoid logging full URL with password)
    try:
        import logging
        _log = logging.getLogger(__name__)
        _host = "?"
        if urls_to_try:
            m = re.search(r"@([^:/]+)", urls_to_try[-1])
            if m:
                _host = m.group(1)
        _log.error("[Supabase] Connection failed to %s: %s", _host, last_error)
    except Exception:
        pass
    raise last_error


@contextmanager
def get_connection():
    conn = None
    try:
        if DB_BACKEND == "supabase":
            conn = _get_supabase_connection()
        else:
            conn = _get_mysql_connection()
        yield conn
        if conn:
            conn.commit()
    except RuntimeError as e:
        if "cryptography" in str(e).lower():
            raise RuntimeError(
                "MySQL requires the 'cryptography' package. Install it with: pip install cryptography\n"
                "Or double-click: install_cryptography.bat"
            ) from e
        raise
    except Exception:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Create tables if they do not exist."""
    if DB_BACKEND == "supabase":
        _init_supabase()
    else:
        _init_mysql()
    _ensure_default_admin()


def _ensure_default_admin():
    """Create default admin user (admin/123456) if no users exist. Change password after first login."""
    import hashlib
    default_hash = hashlib.sha256(b"123456").hexdigest()
    with get_connection() as conn:
        cur = execute(conn, "SELECT id FROM users LIMIT 1")
        if cur.fetchone():
            return
        execute(conn, """
            INSERT INTO users (username, password_hash, email, is_admin, is_active)
            VALUES (?, ?, ?, 1, 1)
        """, ("admin", default_hash, "admin@example.com"))


def _init_mysql():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                is_admin TINYINT DEFAULT 0,
                is_active TINYINT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_api_keys (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                openai_api_key TEXT,
                openai_model VARCHAR(255),
                openrouter_api_key TEXT,
                openrouter_model VARCHAR(255),
                midjourney_api_token TEXT,
                midjourney_channel_id VARCHAR(255),
                r2_account_id VARCHAR(255),
                r2_access_key_id VARCHAR(255),
                r2_secret_access_key TEXT,
                r2_bucket_name VARCHAR(255),
                r2_public_url TEXT,
                cloudflare_account_id VARCHAR(255),
                cloudflare_api_token TEXT,
                local_api_url TEXT,
                local_models TEXT,
                default_categories TEXT,
                bulk_max_concurrency INT DEFAULT 6,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_keys (user_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_domains (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                domain_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_domain (user_id, domain_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_groups (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                group_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_group (user_id, group_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `groups` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                parent_group_id INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_group_id) REFERENCES `groups`(id) ON DELETE SET NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INT AUTO_INCREMENT PRIMARY KEY,
                domain_url TEXT NOT NULL,
                domain_name VARCHAR(255) NOT NULL,
                group_id INT,
                domain_index INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES `groups`(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS titles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                domain_id INT,
                group_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (domain_id) REFERENCES domains(id),
                FOREIGN KEY (group_id) REFERENCES `groups`(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS article_content (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title_id INT NOT NULL,
                language_code VARCHAR(10) DEFAULT 'en',
                recipe TEXT,
                prompt TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (title_id) REFERENCES titles(id)
            )
        """)
        _run_mysql_migrations(cursor)
        _run_mysql_migrations_part2(cursor)


def _run_mysql_migrations(cursor):
    """MySQL-specific migrations."""
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN group_id INT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE `groups` ADD COLUMN parent_group_id INT DEFAULT NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE `groups` ADD CONSTRAINT fk_parent_group FOREIGN KEY (parent_group_id) REFERENCES `groups`(id) ON DELETE SET NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN domain_index INT")
    except Exception:
        pass
    for col in ("article", "prompt_image_ingredients", "recipe_title_pin", "pinterest_title", "pinterest_description",
                "pinterest_keywords", "focus_keyphrase", "meta_description", "keyphrase_synonyms", "main_image", "ingredient_image", "article_css"):
        try:
            cursor.execute(f"ALTER TABLE article_content ADD COLUMN {col} TEXT")
        except Exception:
            pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN website_template TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN categories_list TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN last_pin_template_index INT DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN article_template_config LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN article_template_preview_url VARCHAR(512)")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN article_html_snippets LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN article_template_name VARCHAR(255)")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN domain_colors LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN domain_fonts LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN writers LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN last_writer_index INT DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN pin_image TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN writer LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN writer_avatar TEXT")
    except Exception:
        pass
    for col in ("top_image", "bottom_image", "avatar_image", "article_html"):
        try:
            cursor.execute(f"ALTER TABLE article_content ADD COLUMN {col} TEXT")
        except Exception:
            pass
    for col in ("model_used",):
        try:
            cursor.execute(f"ALTER TABLE article_content ADD COLUMN {col} VARCHAR(255)")
        except Exception:
            pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN generated_at DATETIME")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN generation_time_seconds INT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN validated TINYINT(1) DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN generation_cost_usd DECIMAL(12,6)")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN usage_json TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN status_error TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE article_content ADD COLUMN pinterest_board_slug VARCHAR(128)")
    except Exception:
        pass


def _run_mysql_migrations_part2(cursor):
    """More MySQL migrations."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domain_templates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            domain_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            template_json LONGTEXT NOT NULL,
            sort_order INT DEFAULT 0,
            preview_image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (domain_id) REFERENCES domains(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domain_template_assignments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            domain_id INT NOT NULL,
            template_id INT NOT NULL,
            sort_order INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
            FOREIGN KEY (template_id) REFERENCES domain_templates(id) ON DELETE CASCADE,
            UNIQUE KEY unique_domain_template (domain_id, template_id)
        )
    """)
    try:
        cursor.execute("ALTER TABLE domain_templates ADD COLUMN preview_image_url TEXT")
    except Exception:
        pass
    for col in ("header_template", "footer_template", "side_article_template", "category_page_template", "writer_template", "index_template", "article_card_template"):
        try:
            cursor.execute(f"ALTER TABLE domains ADD COLUMN {col} VARCHAR(255)")
        except Exception:
            pass
    for col in ("domain_page_about_us", "domain_page_terms_of_use", "domain_page_privacy_policy",
                "domain_page_gdpr_policy", "domain_page_cookie_policy", "domain_page_copyright_policy",
                "domain_page_disclaimer", "domain_page_contact_us"):
        try:
            cursor.execute(f"ALTER TABLE domains ADD COLUMN {col} LONGTEXT")
        except Exception:
            pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN cloudflare_info LONGTEXT")
    except Exception:
        pass
    for col in ("user_id",):
        for tbl in ("groups", "domains", "titles"):
            try:
                cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} INT")
            except Exception:
                pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN cloned_from_user_id INT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN cloned_at TIMESTAMP NULL DEFAULT NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN bulk_max_concurrency INT DEFAULT 6")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN ai_provider VARCHAR(32) DEFAULT NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN llamacpp_manager_url TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN llamacpp_model_id INT DEFAULT NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN groq_api_key TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN groq_model VARCHAR(255)")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN image_request_delay_sec INT DEFAULT 15")
    except Exception:
        pass  # column may already exist
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN pinterest_board_id VARCHAR(255)")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN pinterest_access_token TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN pinterest_refresh_token TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN pinterest_app_id VARCHAR(255)")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN pinterest_app_secret TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN visual_customizations LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN pinterest_mode VARCHAR(32) DEFAULT NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN pinterest_domain_verify VARCHAR(128) DEFAULT NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE domains ADD COLUMN pinterest_boards TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN rss_base_url VARCHAR(512) DEFAULT NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN skip_cf_status_check TINYINT DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN pin_generator_type VARCHAR(32) DEFAULT 'python'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN active_themes LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN active_pin_templates LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN active_article_generators LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN ui_poll_running_tasks TINYINT DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN ui_cf_auto_refresh_domains TINYINT DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE user_api_keys ADD COLUMN ai_prompts_json LONGTEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE `groups` ADD COLUMN ai_prompt_overrides_json LONGTEXT")
    except Exception:
        pass
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            log_type VARCHAR(64) NOT NULL,
            application VARCHAR(64) DEFAULT 'multi-domain',
            success TINYINT(1) DEFAULT 0,
            title_id INT,
            domain_id INT,
            group_id INT,
            job_id VARCHAR(128),
            message TEXT,
            reason TEXT,
            details LONGTEXT,
            INDEX idx_log_type (log_type),
            INDEX idx_application (application),
            INDEX idx_success (success),
            INDEX idx_title_id (title_id),
            INDEX idx_domain_id (domain_id),
            INDEX idx_job_id (job_id),
            INDEX idx_created_at (created_at)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS writers_pool (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(255) NOT NULL DEFAULT '',
            title VARCHAR(255) NOT NULL DEFAULT '',
            bio TEXT,
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_writers_pool_user (user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pin_template_pool (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            template_json LONGTEXT NOT NULL,
            preview_image_url TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_pin_template_pool_name (name)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_provider_models (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provider VARCHAR(32) NOT NULL,
            model_id VARCHAR(255) NOT NULL,
            label VARCHAR(512),
            is_free TINYINT DEFAULT 0,
            sort_order INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_ai_provider_models_provider (provider)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_provider_models (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provider VARCHAR(32) NOT NULL,
            model_id VARCHAR(255) NOT NULL,
            label VARCHAR(512),
            is_free TINYINT(1) DEFAULT 0,
            sort_order INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_ai_provider_models_provider (provider)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pin_url_submissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            url TEXT NOT NULL,
            `generated` TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_pin_url_user (user_id),
            INDEX idx_pin_url_generated (`generated`),
            INDEX idx_pin_url_created (created_at)
        )
    """)


def _safe_execute(conn, cur, sql, *args):
    """Execute SQL; on error, rollback so transaction can continue (PostgreSQL requirement)."""
    try:
        cur.execute(sql, *args)
    except Exception:
        conn.rollback()


def _init_supabase():
    """PostgreSQL schema for Supabase."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                is_admin SMALLINT DEFAULT 0,
                is_active SMALLINT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "groups" (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                parent_group_id INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT,
                FOREIGN KEY (parent_group_id) REFERENCES "groups"(id) ON DELETE SET NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id SERIAL PRIMARY KEY,
                domain_url TEXT NOT NULL,
                domain_name VARCHAR(255) NOT NULL,
                group_id INT,
                domain_index INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT,
                FOREIGN KEY (group_id) REFERENCES "groups"(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_api_keys (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                openai_api_key TEXT,
                openai_model VARCHAR(255),
                openrouter_api_key TEXT,
                openrouter_model VARCHAR(255),
                midjourney_api_token TEXT,
                midjourney_channel_id VARCHAR(255),
                r2_account_id VARCHAR(255),
                r2_access_key_id VARCHAR(255),
                r2_secret_access_key TEXT,
                r2_bucket_name VARCHAR(255),
                r2_public_url TEXT,
                cloudflare_account_id VARCHAR(255),
                cloudflare_api_token TEXT,
                local_api_url TEXT,
                local_models TEXT,
                default_categories TEXT,
                bulk_max_concurrency INT DEFAULT 6,
                cloned_from_user_id INT,
                cloned_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id)
            )
        """)
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS bulk_max_concurrency INT DEFAULT 6")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(32) DEFAULT NULL")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS llamacpp_manager_url TEXT")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS llamacpp_model_id INT DEFAULT NULL")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS groq_api_key TEXT")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS groq_model VARCHAR(255)")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS image_request_delay_sec INT DEFAULT 15")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS rss_base_url VARCHAR(512) DEFAULT NULL")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS skip_cf_status_check SMALLINT DEFAULT 0")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS pin_generator_type VARCHAR(32) DEFAULT 'python'")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS active_themes TEXT")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS active_pin_templates TEXT")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS active_article_generators TEXT")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS ui_poll_running_tasks SMALLINT DEFAULT 0")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS ui_cf_auto_refresh_domains SMALLINT DEFAULT 0")
        _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS ai_prompts_json TEXT")
        _safe_execute(conn, cur, 'ALTER TABLE "groups" ADD COLUMN IF NOT EXISTS ai_prompt_overrides_json TEXT')
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_domains (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                domain_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
                UNIQUE (user_id, domain_id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_groups (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                group_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES "groups"(id) ON DELETE CASCADE,
                UNIQUE (user_id, group_id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS titles (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                domain_id INT,
                group_id INT,
                user_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (domain_id) REFERENCES domains(id),
                FOREIGN KEY (group_id) REFERENCES "groups"(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS article_content (
                id SERIAL PRIMARY KEY,
                title_id INT NOT NULL,
                language_code VARCHAR(10) DEFAULT 'en',
                recipe TEXT,
                prompt TEXT,
                content TEXT,
                article TEXT,
                prompt_image_ingredients TEXT,
                recipe_title_pin TEXT,
                pinterest_title TEXT,
                pinterest_description TEXT,
                pinterest_keywords TEXT,
                focus_keyphrase TEXT,
                meta_description TEXT,
                keyphrase_synonyms TEXT,
                main_image TEXT,
                ingredient_image TEXT,
                article_css TEXT,
                pin_image TEXT,
                writer TEXT,
                writer_avatar TEXT,
                top_image TEXT,
                bottom_image TEXT,
                avatar_image TEXT,
                article_html TEXT,
                model_used VARCHAR(255),
                generated_at TIMESTAMP,
                generation_time_seconds INT,
                validated SMALLINT DEFAULT 0,
                generation_cost_usd NUMERIC(12,6),
                usage_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (title_id) REFERENCES titles(id)
            )
        """)
        _safe_execute(conn, cur, "ALTER TABLE article_content ADD COLUMN IF NOT EXISTS generation_cost_usd NUMERIC(12,6)")
        _safe_execute(conn, cur, "ALTER TABLE article_content ADD COLUMN IF NOT EXISTS usage_json TEXT")
        _safe_execute(conn, cur, "ALTER TABLE article_content ADD COLUMN IF NOT EXISTS status_error TEXT")
        _safe_execute(conn, cur, "ALTER TABLE article_content ADD COLUMN IF NOT EXISTS pinterest_board_slug VARCHAR(128)")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS domain_templates (
                id SERIAL PRIMARY KEY,
                domain_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                template_json TEXT NOT NULL,
                sort_order INT DEFAULT 0,
                preview_image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (domain_id) REFERENCES domains(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS domain_template_assignments (
                id SERIAL PRIMARY KEY,
                domain_id INT NOT NULL,
                template_id INT NOT NULL,
                sort_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
                FOREIGN KEY (template_id) REFERENCES domain_templates(id) ON DELETE CASCADE,
                UNIQUE (domain_id, template_id)
            )
        """)
        for col in ("website_template", "categories_list", "last_pin_template_index", "article_template_config",
                    "article_template_preview_url", "article_html_snippets", "article_template_name",
                    "domain_colors", "domain_fonts", "writers", "last_writer_index",
                    "header_template", "footer_template", "side_article_template", "category_page_template",
                    "writer_template", "index_template", "article_card_template",
                    "domain_page_about_us", "domain_page_terms_of_use", "domain_page_privacy_policy",
                    "domain_page_gdpr_policy", "domain_page_cookie_policy", "domain_page_copyright_policy",
                    "domain_page_disclaimer", "domain_page_contact_us",
                    "cloudflare_info", "pinterest_board_id", "pinterest_boards", "pinterest_access_token", "pinterest_refresh_token",
                    "pinterest_app_id", "pinterest_app_secret", "visual_customizations", "pinterest_mode", "pinterest_domain_verify"):
            _safe_execute(conn, cur, f'ALTER TABLE domains ADD COLUMN IF NOT EXISTS {col} TEXT')
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_logs (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                log_type VARCHAR(64) NOT NULL,
                application VARCHAR(64) DEFAULT 'multi-domain',
                success SMALLINT DEFAULT 0,
                title_id INT,
                domain_id INT,
                group_id INT,
                job_id VARCHAR(128),
                message TEXT,
                reason TEXT,
                details TEXT
            )
        """)
        for idx in ("idx_log_type", "idx_application", "idx_success", "idx_title_id", "idx_domain_id", "idx_job_id", "idx_created_at"):
            col = idx.replace("idx_", "")
            _safe_execute(conn, cur, f"CREATE INDEX IF NOT EXISTS {idx} ON app_logs({col})")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS writers_pool (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL DEFAULT '',
                title VARCHAR(255) NOT NULL DEFAULT '',
                bio TEXT,
                avatar TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        _safe_execute(conn, cur, "CREATE INDEX IF NOT EXISTS idx_writers_pool_user ON writers_pool(user_id)")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pin_template_pool (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                template_json TEXT NOT NULL,
                preview_image_url TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ai_provider_models (
                id SERIAL PRIMARY KEY,
                provider VARCHAR(32) NOT NULL,
                model_id VARCHAR(255) NOT NULL,
                label VARCHAR(512),
                is_free SMALLINT DEFAULT 0,
                sort_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ai_provider_models_provider ON ai_provider_models(provider)")
        _safe_execute(conn, cur, "CREATE INDEX IF NOT EXISTS idx_pin_template_pool_name ON pin_template_pool(name)")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pin_url_submissions (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                url TEXT NOT NULL,
                generated SMALLINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        _safe_execute(conn, cur, "CREATE INDEX IF NOT EXISTS idx_pin_url_user ON pin_url_submissions(user_id)")
        _safe_execute(conn, cur, "CREATE INDEX IF NOT EXISTS idx_pin_url_generated ON pin_url_submissions(generated)")
        _safe_execute(conn, cur, "CREATE INDEX IF NOT EXISTS idx_pin_url_created ON pin_url_submissions(created_at)")
        _run_supabase_migrations(conn, cur)


def _run_supabase_migrations(conn, cur):
    """Add any columns that MySQL has, so Supabase schema stays in sync."""
    for col in ("pinterest_boards",):
        _safe_execute(conn, cur, f'ALTER TABLE domains ADD COLUMN IF NOT EXISTS {col} TEXT')
    _safe_execute(conn, cur, "ALTER TABLE user_api_keys ADD COLUMN IF NOT EXISTS ai_prompts_json TEXT")
    _safe_execute(conn, cur, 'ALTER TABLE "groups" ADD COLUMN IF NOT EXISTS ai_prompt_overrides_json TEXT')


def _pg_compat_query(q):
    """Convert MySQL-specific SQL to PostgreSQL-compatible form."""
    q = q.replace("`", '"')
    # IFNULL(a,b) -> COALESCE(a,b) — PostgreSQL doesn't have IFNULL
    q = re.sub(r"\bIFNULL\s*\(", "COALESCE(", q, flags=re.IGNORECASE)
    return q


def execute(conn, query, params=None):
    """Execute query. Use ? placeholders; they are converted to %s. For Supabase, backticks become double-quotes.
    For Supabase INSERT, appends RETURNING id so last_insert_id works with connection pooling."""
    q = query.replace("?", "%s")
    if DB_BACKEND == "supabase":
        q = _pg_compat_query(q)
        # Append RETURNING id for simple INSERT (more reliable than lastval() with connection pooling)
        if re.match(r"^\s*INSERT\s+INTO\s+", q, re.IGNORECASE) and " RETURNING " not in q.upper():
            q = q.rstrip("; \n") + " RETURNING id"
    cur = conn.cursor()
    if params:
        cur.execute(q, params)
    else:
        cur.execute(q)
    return cur


def last_insert_id(cursor):
    """Return last insert ID. Pass the cursor that did the INSERT."""
    if cursor is None:
        return None
    if hasattr(cursor, "lastrowid") and cursor.lastrowid is not None:
        return cursor.lastrowid
    if DB_BACKEND == "supabase":
        # Prefer result from RETURNING id (set by execute for INSERT)
        if cursor.description:
            row = cursor.fetchone()
            if row:
                # RealDictCursor: row['id']; tuple: row[0]; try common variations
                for key in ("id", "ID"):
                    if hasattr(row, "get") and row.get(key) is not None:
                        val = row[key]
                        return val if val else None  # 0 is invalid for auto-increment
                try:
                    val = row[0] if len(row) else None
                    return val if val else None
                except (TypeError, IndexError, KeyError):
                    pass
        try:
            cursor.execute("SELECT lastval()")
            row = cursor.fetchone()
            val = list(row.values())[0] if row and hasattr(row, "values") else (row[0] if row else None)
            return val if val else None  # 0 is invalid for auto-increment
        except Exception:
            return None
    return None


def get_fk_children(conn, table_name, pk_column):
    """Return list of (child_table, child_column) referencing table_name.pk_column. Works for MySQL and PostgreSQL."""
    if DB_BACKEND == "supabase":
        cur = conn.cursor()
        cur.execute("""
            SELECT tc.table_name AS table_name, kcu.column_name AS column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = current_schema()
              AND ccu.table_name = %s AND ccu.column_name = %s
        """, (table_name, pk_column))
    else:
        cur = execute(conn, """
            SELECT TABLE_NAME AS table_name, COLUMN_NAME AS column_name
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_SCHEMA = DATABASE()
              AND REFERENCED_TABLE_NAME = %s
              AND REFERENCED_COLUMN_NAME = %s
        """, (table_name, pk_column))
    rows = cur.fetchall() or []
    return [(r.get("table_name", ""), r.get("column_name", "")) for r in rows if r.get("table_name") and r.get("column_name")]


def dict_row(row):
    """Convert row to dict."""
    if row is None:
        return None
    return dict(row) if not isinstance(row, dict) else row
