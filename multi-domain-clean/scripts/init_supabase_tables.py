"""
Create Supabase tables for multi-domain-clean.

Option A - Direct Postgres (recommended):
  Set SUPABASE_DB_URL in .env, then run:
    python scripts/init_supabase_tables.py
  This runs supabase_schema.sql against your Supabase DB (same as app startup).

Option B - When direct connection fails (e.g. DNS):
  Set SUPABASE_URL and SUPABASE_KEY in .env (like excel.py).
  Run this script; it will test the client connection and tell you to run
  supabase_schema.sql in Supabase Dashboard → SQL Editor.
"""
import os
import sys

# Load .env from multi-domain-clean (parent of scripts/)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(_script_dir)
sys.path.insert(0, _app_dir)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_app_dir, ".env"))
except ImportError:
    pass

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()


def run_schema_via_direct():
    """Run supabase_schema.sql using SUPABASE_DB_URL (psycopg2)."""
    import psycopg2
    schema_path = os.path.join(_app_dir, "supabase_schema.sql")
    if not os.path.isfile(schema_path):
        print("ERROR: supabase_schema.sql not found in", _app_dir)
        return False
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    conn = psycopg2.connect(SUPABASE_DB_URL)
    conn.autocommit = True
    try:
        cur = conn.cursor()
        # Run each statement (split by semicolon, skip comments and empty)
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt or stmt.startswith("--"):
                continue
            try:
                cur.execute(stmt)
            except Exception as e:
                # Ignore "already exists" type errors
                if "already exists" in str(e).lower():
                    continue
                print("Warning:", e)
        cur.close()
        print("OK: Tables created/updated via SUPABASE_DB_URL.")
        return True
    finally:
        conn.close()


def test_client_connection():
    """Test connection using Supabase client (URL + key)."""
    try:
        from supabase import create_client
    except ImportError:
        print("Install supabase: pip install supabase")
        return False
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Try a simple query (table may not exist yet)
    try:
        client.table("users").select("id").limit(1).execute()
    except Exception as e:
        msg = str(e).lower()
        if "could not find the table" in msg or "pgrst" in msg or "schema" in msg:
            # Connected but table missing = connection OK
            return True
        if "connection" in msg or "network" in msg or "resolve" in msg:
            return False
        # Other (e.g. auth) might still mean we reached the API
        return True
    return True


def main():
    if SUPABASE_DB_URL:
        print("Using SUPABASE_DB_URL (direct Postgres)...")
        try:
            if run_schema_via_direct():
                return
        except Exception as e:
            print("Direct connection failed:", e)
            print()
            print("If you see DNS/connection errors, use Option B below.")
            print()

    if SUPABASE_URL and SUPABASE_KEY:
        print("Testing connection with SUPABASE_URL + SUPABASE_KEY (like excel.py)...")
        if test_client_connection():
            print("Connection OK.")
            print()
            print("The Supabase client (URL+key) cannot create tables.")
            print("To create tables:")
            print("  1. Open Supabase Dashboard → SQL Editor")
            print("  2. Copy the contents of: " + os.path.join(_app_dir, "supabase_schema.sql"))
            print("  3. Paste and Run")
            print()
            print("Then set SUPABASE_DB_URL in .env for the app (Dashboard → Project Settings → Database → Connection string).")
            return
        else:
            print("Client connection failed. Check SUPABASE_URL and SUPABASE_KEY.")

    print()
    print("Configure .env:")
    print("  SUPABASE_DB_URL = postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres")
    print("  (from Supabase Dashboard → Project Settings → Database)")
    print("  Or use SUPABASE_URL + SUPABASE_KEY and run supabase_schema.sql in Dashboard → SQL Editor.")


if __name__ == "__main__":
    main()
