"""Database connection and schema. MySQL only."""
import os
from contextlib import contextmanager

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "pinterest"),
    "charset": "utf8mb4",
    "autocommit": True,
}

# Pre-import cryptography to ensure pymysql can use it
try:
    import cryptography
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import serialization, hashes
except ImportError:
    pass


@contextmanager
def get_connection():
    conn = None
    try:
        import pymysql
        conn = pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)
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
    _init_mysql()


def _init_mysql():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
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
        
        # User API keys table
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_keys (user_id)
            )
        """)
        
        # User-domain associations
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
        
        # User-group associations (many-to-many: users can access multiple groups)
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
        # Migration: add columns if missing
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
        
        # Domain template assignments (pin templates assigned to domains)
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
        
        # Add user_id columns for multi-user support
        try:
            cursor.execute("ALTER TABLE `groups` ADD COLUMN user_id INT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE domains ADD COLUMN user_id INT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE titles ADD COLUMN user_id INT")
        except Exception:
            pass
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pinterest_schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title_id INT NOT NULL,
                scheduled_at DATETIME NOT NULL,
                status VARCHAR(32) DEFAULT 'pending',
                posted_at DATETIME,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_status (status),
                INDEX idx_scheduled_at (scheduled_at)
            )
        """)
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


def execute(conn, query, params=None):
    """Execute query. Use ? placeholders; they are converted to %s for MySQL."""
    q = query.replace("?", "%s")
    cur = conn.cursor()
    if params:
        cur.execute(q, params)
    else:
        cur.execute(q)
    return cur


def last_insert_id(cursor):
    """Return last insert ID. Pass the cursor that did the INSERT."""
    return cursor.lastrowid if cursor else None


def dict_row(row):
    """Convert row to dict."""
    if row is None:
        return None
    return dict(row) if not isinstance(row, dict) else row
