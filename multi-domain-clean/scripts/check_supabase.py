#!/usr/bin/env python3
"""Diagnose Supabase database connectivity. Run from multi-domain-clean or repo root.

  cd multi-domain-clean && python scripts/check_supabase.py

Checks: DNS resolution, connection, basic query. Reports clear errors."""
import os
import re
import socket
import sys
from pathlib import Path

# Load .env from multi-domain-clean
_script_dir = Path(__file__).resolve().parent
_env_dir = _script_dir.parent
_env_file = _env_dir / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "").strip()
SUPABASE_POOLER_URL = os.getenv("SUPABASE_POOLER_URL", "").strip()
DB_BACKEND = os.getenv("DB_BACKEND", "mysql").lower().strip()


def _mask_url(url):
    """Mask password in connection URL for safe display."""
    if not url:
        return "(empty)"
    # postgresql://user:password@host:port/db -> postgresql://user:***@host:port/db
    return re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)


def _host_from_url(url):
    m = re.search(r"@([^:/]+)(?::(\d+))?", url)
    return m.group(1) if m else None


def check_dns(host):
    """Resolve hostname to IP. Returns (ok, message)."""
    try:
        addrs = socket.getaddrinfo(host, None)
        ips = sorted({a[4][0] for a in addrs})
        return True, f"OK — resolves to: {', '.join(ips[:4])}{'...' if len(ips) > 4 else ''}"
    except socket.gaierror as e:
        return False, f"FAIL — DNS error: {e}"


def check_connect(url):
    """Try psycopg2 connect. Returns (ok, message)."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("SELECT 1 AS ok")
        cur.fetchone()
        cur.close()
        conn.close()
        return True, "OK — connected and query works"
    except ImportError:
        return False, "FAIL — psycopg2 not installed. Run: pip install psycopg2-binary"
    except Exception as e:
        msg = str(e).strip()
        if "could not translate host name" in msg.lower() or "name or service not known" in msg.lower():
            return False, f"FAIL — DNS: {msg[:200]}"
        if "password authentication failed" in msg.lower():
            return False, f"FAIL — wrong password or user: {msg[:200]}"
        if "timeout" in msg.lower() or "timed out" in msg.lower():
            return False, f"FAIL — connection timeout: {msg[:200]}"
        if "connection refused" in msg.lower():
            return False, f"FAIL — connection refused (port/firewall): {msg[:200]}"
        return False, f"FAIL — {msg[:300]}"


def main():
    urls = [u for u in (SUPABASE_DB_URL, SUPABASE_POOLER_URL) if u]
    if not urls:
        print("No SUPABASE_DB_URL or SUPABASE_POOLER_URL in .env")
        print("Set one in multi-domain-clean/.env — Supabase Dashboard → Project Settings → Database")
        return 1

    print("Supabase connectivity check")
    print("=" * 50)
    print("DB_BACKEND:", DB_BACKEND)
    print()

    all_ok = True
    for i, url in enumerate(urls):
        label = "SUPABASE_DB_URL (direct)" if url == SUPABASE_DB_URL and url else "SUPABASE_POOLER_URL"
        if SUPABASE_DB_URL and SUPABASE_POOLER_URL and url == SUPABASE_POOLER_URL:
            label = "SUPABASE_POOLER_URL"
        elif url == SUPABASE_DB_URL:
            label = "SUPABASE_DB_URL"

        print(f"[{i+1}] {label}")
        print("    URL:", _mask_url(url))
        host = _host_from_url(url)
        if host:
            ok_dns, msg_dns = check_dns(host)
            print("    DNS:", msg_dns)
            if not ok_dns:
                all_ok = False
        ok_conn, msg_conn = check_connect(url)
        print("    Connect:", msg_conn)
        if not ok_conn:
            all_ok = False
        print()

    if all_ok:
        print("All checks passed. Supabase is reachable.")
        return 0

    print("Some checks failed. Common fixes:")
    print("  • DNS: ipconfig /flushdns (Windows) or check network")
    print("  • Auth: verify password in Supabase Dashboard → Project Settings → Database")
    print("  • Firewall: ensure outbound to port 5432 or 6543")
    print("  • Status: https://status.supabase.com")
    return 1


if __name__ == "__main__":
    sys.exit(main())
