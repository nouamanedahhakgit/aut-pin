#!/usr/bin/env python3
"""
Test pool pin generate path.
Run from multi-domain-clean: python scripts/test_pin_generate_pool.py

If server is running on 5001, you can also test via curl and get traceback in JSON on failure:
  curl -s -X POST "http://localhost:5001/api/pin-generate?name=high_protein_white&template_only=1" -H "Content-Type: application/json" -d "{}" -b "session=YOUR_SESSION_COOKIE"
"""
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_app = os.path.dirname(_here)
sys.path.insert(0, _app)
os.chdir(_app)

def test():
    from app import _render_pool_template_to_html, _do_pin_generate_pool, get_connection, db_execute
    from db import dict_row

    name = "high_protein_white"
    body = {"variables": {"title": "Test", "domain": "example.com"}}

    with get_connection() as conn:
        cur = db_execute(conn, "SELECT name FROM pin_template_pool WHERE name = ?", (name,))
        if cur.fetchone() is None:
            print("Template not in pool. Insert first:")
            print("  python scripts/insert_pin_templates.py --from-js pin_templates/themes_from_ai/pin_theme_high_protein_white.js")
            return 1

    print("Calling _render_pool_template_to_html...")
    res = _render_pool_template_to_html(name, body, return_merged=True)
    res_list = list(res) if res else []
    print("  len(res) =", len(res_list))

    print("Calling _do_pin_generate_pool...")
    ok, out = _do_pin_generate_pool(name, body, user_id=None, template_only=True, pin_base=None)
    print("  ok =", ok, "keys =", list(out.keys()) if ok else "N/A")
    print("Passed.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(test())
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
