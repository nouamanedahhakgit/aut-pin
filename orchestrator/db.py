"""Database storage for orchestrator config. Uses MySQL or Supabase from wizard config."""
import json
import os


def _get_connection(cfg):
    """Open DB connection from config. Returns conn or None on error."""
    db = cfg.get("database", {})
    backend = db.get("backend", "mysql")
    try:
        if backend == "mysql":
            import pymysql
            return pymysql.connect(
                host=db.get("mysql_host", "localhost"),
                user=db.get("mysql_user", "root"),
                password=db.get("mysql_password", ""),
                database=db.get("mysql_database", "pinterest"),
                charset="utf8mb4",
                autocommit=True,
            )
        elif backend == "supabase":
            import psycopg2
            urls = [u for u in (db.get("supabase_pooler_url"), db.get("supabase_db_url")) if u]
            for url in urls:
                try:
                    return psycopg2.connect(
                        url,
                        connect_timeout=10,
                        options="-c client_encoding=UTF8",
                    )
                except Exception:
                    continue
            return None
    except Exception:
        return None


def _init_table(conn, backend):
    """Create orchestrator_config table if not exists."""
    cur = conn.cursor()
    if backend == "mysql":
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orchestrator_config (
                id INT PRIMARY KEY DEFAULT 1,
                config_json LONGTEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CHECK (id = 1)
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orchestrator_config (
                id INT PRIMARY KEY DEFAULT 1,
                config_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    cur.close()


def load_config_from_db(cfg):
    """Load config from database. Returns dict or None."""
    conn = _get_connection(cfg)
    if not conn:
        return None
    try:
        _init_table(conn, cfg.get("database", {}).get("backend", "mysql"))
        cur = conn.cursor()
        cur.execute("SELECT config_json FROM orchestrator_config WHERE id = 1")
        row = cur.fetchone()
        cur.close()
        if row and row[0]:
            return json.loads(row[0])
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return None


def save_config_to_db(cfg):
    """Save config to database. Returns True on success."""
    conn = _get_connection(cfg)
    if not conn:
        return False
    try:
        backend = cfg.get("database", {}).get("backend", "mysql")
        _init_table(conn, backend)
        cur = conn.cursor()
        config_json = json.dumps(cfg, indent=2)
        if backend == "mysql":
            cur.execute("""
                INSERT INTO orchestrator_config (id, config_json) VALUES (1, %s)
                ON DUPLICATE KEY UPDATE config_json = VALUES(config_json)
            """, (config_json,))
        else:
            cur.execute("""
                INSERT INTO orchestrator_config (id, config_json, updated_at) VALUES (1, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (id) DO UPDATE SET config_json = EXCLUDED.config_json, updated_at = CURRENT_TIMESTAMP
            """, (config_json,))
        cur.close()
        return True
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass
