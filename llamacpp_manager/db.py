"""Database connection and schema for llama.cpp manager. Uses SQLite (local file, no external server)."""
import logging
import os
import sqlite3
from contextlib import contextmanager

from .config import LLAMACPP_DB_PATH

log = logging.getLogger(__name__)


def _dict_row(cursor, row):
    """Row factory: return rows as dicts."""
    return {cursor.description[i][0]: row[i] for i in range(len(row))}


def _get_connection():
    conn = sqlite3.connect(LLAMACPP_DB_PATH)
    conn.row_factory = _dict_row
    return conn


@contextmanager
def get_connection():
    conn = None
    try:
        conn = _get_connection()
        yield conn
        if conn:
            conn.commit()
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
    db_dir = os.path.dirname(LLAMACPP_DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                model_path VARCHAR(1024) NOT NULL,
                port INTEGER NOT NULL UNIQUE,
                status VARCHAR(32) DEFAULT 'stopped',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER NOT NULL,
                ctx INTEGER DEFAULT 4096,
                threads INTEGER DEFAULT 0,
                gpu_layers INTEGER DEFAULT -1,
                temperature REAL DEFAULT 0.7,
                top_p REAL DEFAULT 0.9,
                top_k INTEGER DEFAULT 40,
                repeat_penalty REAL DEFAULT 1.1,
                max_tokens INTEGER DEFAULT 1024,
                stop_words TEXT,
                seed INTEGER DEFAULT -1,
                mirostat INTEGER DEFAULT 0,
                mirostat_eta REAL DEFAULT 0.1,
                mirostat_tau REAL DEFAULT 5.0,
                FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY,
                max_threads INTEGER DEFAULT 8,
                auto_threads INTEGER DEFAULT 1,
                max_ram_usage VARCHAR(64) DEFAULT '4G'
            )
        """)
        cursor.execute(
            "INSERT OR IGNORE INTO system_config (id, max_threads, auto_threads, max_ram_usage) VALUES (1, 8, 1, '4G')"
        )

    log.info("[llamacpp_manager] Database initialized (SQLite: %s)", LLAMACPP_DB_PATH)
